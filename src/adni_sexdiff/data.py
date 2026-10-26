"""Pipeline steps of adni_sexdiff.

``clean`` (change ``adni-metabolomics-clean``) and ``cohort`` (change
``adni-cohort``) are implemented. Every other step is a stub: its docstring
states the inputs it reads, the files it writes and the contract of those
files, and its body raises ``NotImplementedError`` until an OpenSpec change
implements it. The statistical choices the remaining steps need (feature
rule, permutations, seed, rank floor, diagnostic variables, reading rules)
are undecided and enter only through a proposal (see ``constants``).

The raw-input helpers (``require_raw_files``, ``hash_raw_file``,
``check_known_repairs``) and the manifest and output-directory helpers
(``_git_revision``, ``_software_versions``, ``_write_manifest``,
``_finalize_output_dir``) are shared by every step.

ADNI is controlled-access. Every table keyed by ``RID`` is participant-level:
it stays under the ignored paths of ``constants.PARTICIPANT_LEVEL_PATTERNS``,
is never printed, never synced and never quoted. Progress output names
counts and files, never participants.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Generator, Iterable
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import pandas as pd

from .constants import (
    ANALYSIS_COVARIATES,
    CLEAN_EXPECTED_COUNTS,
    CLEAN_FASTING_FILE,
    CLEAN_INPUT_FILES,
    CLEAN_LOG,
    CLEAN_MANIFEST,
    CLEAN_MEDICATION_FILE,
    CLEAN_OPTIONS,
    CLEAN_RUNS_TABLE,
    CLEAN_TABLES,
    CLEANED_DIR,
    COHORT_CLINICAL_FILE,
    COHORT_COLUMNS,
    COHORT_COUNTS,
    COHORT_DIR,
    COHORT_EXPECTED_COUNTS,
    COHORT_MANIFEST,
    COHORT_RULE,
    COHORT_TABLE,
    DATA_ROOT_ENV,
    DEFAULT_DATA_ROOT,
    GROUP_COLUMN,
    GROUP_VALUES,
    KNOWN_RAW_FILE_REPAIRS,
    METABO_ADNI_VERSION,
    PARTICIPANT_ID_COLUMN,
    PLATFORMS,
    RAW_INPUT_SHA256,
    SAMPLE_COLUMN,
    STAGE_COLUMN,
    STAGE_LABELS,
    STAGE_RULE,
)

#: metabo_adni's ``RID`` of the p180 QC pool rows (``cross_plate_correction``).
_P180_QC_POOL_RID = 999999
#: The flags of metabo_adni's command line that ``clean`` leaves off, in the
#: order its ``main`` applies them (``merge`` sits between ``log2`` and
#: ``zscore`` there and is on).
_CLEAN_TRANSFORMS = ("log2", "zscore", "winsorize", "remove_moutliers", "residualize_meds")
#: Packages whose versions every manifest records.
_MANIFEST_PACKAGES = ("adni-sexdiff", "metabo_adni", "pandas", "numpy", "scipy", "pingouin", "statsmodels", "openpyxl")


def resolve_data_root(data_root: str | Path | None = None) -> Path:
    """Resolve the data root: explicit value → ``ADNI_DATA_ROOT`` → ``data/``.

    Parameters
    ----------
    data_root:
        Explicit data root (a CLI flag), or ``None``.

    Returns
    -------
    Path
        The resolved data root. It is not created and not checked: the raw
        ADNI files are uploaded by hand (LONI needs a login; there is no
        download step), so a missing file is reported by the step that
        needs it.
    """
    if data_root is not None:
        return Path(data_root)
    return Path(os.environ.get(DATA_ROOT_ENV, DEFAULT_DATA_ROOT))


# --- raw inputs --------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def require_raw_files(root: str | Path, names: Iterable[str]) -> None:
    """Check that every raw file a step needs is in the data root.

    Parameters
    ----------
    root:
        The data root.
    names:
        The exact names the step reads from the top level of ``root``.

    Raises
    ------
    FileNotFoundError
        One or more names are absent (or are dangling symlinks); the message
        names every missing one. Called before any file is read or any
        output directory is created, so a step never relies on a reader's
        own handling of an absent file (metabo_adni skips an absent
        concentration file silently).
    """
    root = Path(root)
    missing = [n for n in names if not (root / n).is_file()]
    if missing:
        raise FileNotFoundError(
            f"{len(missing)} raw file(s) missing from the data root {root}: "
            + ", ".join(repr(n) for n in missing)
        )


def hash_raw_file(path: str | Path, *, root: str | Path | None = None) -> dict:
    """Hash a raw file's content through its symlink and describe it.

    Parameters
    ----------
    path:
        The file under its expected name in the data root.
    root:
        The data root the symlink target is reported relative to (default:
        the file's directory).

    Returns
    -------
    dict
        ``name`` (the expected name), ``target`` (the symlink target relative
        to the root, or the absolute resolved path when it lies outside the
        root; ``None`` for a regular file), ``bytes`` and ``sha256`` of the
        resolved content. The file is only read.
    """
    path = Path(path)
    root = Path(root) if root is not None else path.parent
    target = None
    if path.is_symlink():
        resolved = path.resolve()
        try:
            target = resolved.relative_to(root.resolve()).as_posix()
        except ValueError:
            target = str(resolved)
    return {"name": path.name, "target": target, "bytes": path.stat().st_size, "sha256": _sha256_file(path)}


def check_known_repairs(hashes: Iterable[dict]) -> list[str]:
    """Match raw-file hashes against the predeclared hashes and the repair registry.

    Parameters
    ----------
    hashes:
        Records from ``hash_raw_file``. Each is annotated in place with
        ``predeclared`` (the hash equals ``constants.RAW_INPUT_SHA256``) and
        ``repair`` (the registry's defect, repair and date when the hash is
        the repaired one, else ``None``).

    Returns
    -------
    list[str]
        One finding per file whose hash matches neither its predeclared hash
        nor a registry entry (a fresh LONI download), naming the file and
        the hash.

    Raises
    ------
    RuntimeError
        A file's hash is LONI's unrepaired bytes of a registry entry
        (``constants.KNOWN_RAW_FILE_REPAIRS``): the message names the file,
        the defect and the repair its archive copy must carry. No file is
        repaired here.
    """
    findings = []
    for rec in hashes:
        name, sha = rec["name"], rec["sha256"]
        entry = KNOWN_RAW_FILE_REPAIRS.get(name)
        if entry is not None and sha == entry["loni_sha256"]:
            raise RuntimeError(
                f"{name} in the data root is LONI's unrepaired export (sha256 {sha}): {entry['defect']}. "
                f"Its archive copy must carry the repair: {entry['repair']}. "
                "No step edits the archive or a working copy; repair the archive copy by hand and rerun."
            )
        rec["predeclared"] = sha == RAW_INPUT_SHA256.get(name)
        rec["repair"] = None
        if entry is not None and sha == entry["repaired_sha256"]:
            rec["repair"] = {k: entry[k] for k in ("defect", "repair", "repaired_on")}
        elif not rec["predeclared"]:
            findings.append(
                f"{name}: sha256 {sha} matches neither the predeclared hash nor a known repair "
                "(a fresh LONI download?); predeclared counts hold for the predeclared bytes only"
            )
    return findings


def check_metabo_adni_version() -> str:
    """Return the installed metabo_adni version after checking the pin.

    Returns
    -------
    str
        The installed version, equal to ``constants.METABO_ADNI_VERSION``.

    Raises
    ------
    RuntimeError
        The installed version differs from the pin (the lock and the
        constant moved apart), or metabo_adni is not installed.
    """
    try:
        installed = version("metabo_adni")
    except PackageNotFoundError as e:
        raise RuntimeError(f"metabo_adni is not installed; the pin is {METABO_ADNI_VERSION}") from e
    if installed != METABO_ADNI_VERSION:
        raise RuntimeError(
            f"metabo_adni {installed} is installed but the pin is {METABO_ADNI_VERSION}; "
            "a pin move is its own change (AGENTS.md constraint 3)"
        )
    return installed


# --- manifests and output directories ---------------------------------------


def _git_revision() -> dict:
    here = Path(__file__).resolve().parent
    try:
        rev = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=here, capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=here, capture_output=True, text=True, check=True,
        ).stdout.strip() != ""
        return {"commit": rev, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def _software_versions(names: Iterable[str] = _MANIFEST_PACKAGES) -> dict:
    out: dict[str, str | None] = {"python": sys.version.split()[0]}
    for pkg in names:
        try:
            out[pkg] = version(pkg)
        except PackageNotFoundError:
            out[pkg] = None
    return out


def _json_default(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"{type(obj).__name__} is not JSON serializable")


def _write_manifest(path: str | Path, manifest: dict) -> None:
    Path(path).write_text(json.dumps(manifest, indent=2, sort_keys=True, default=_json_default) + "\n")


@contextlib.contextmanager
def _finalize_output_dir(final: str | Path, *, force: bool) -> Generator[Path, None, None]:
    """Stage a step's output in ``<final>.tmp/`` and rename it to ``final`` when complete.

    Parameters
    ----------
    final:
        The output directory the step promises.
    force:
        Replace an existing ``final``.

    Yields
    ------
    Path
        The empty staging directory ``<final>.tmp/``.

    Notes
    -----
    On entry an existing ``final`` stops the step unless ``force`` is given,
    and a stale ``<final>.tmp/`` from an earlier run is removed. When the
    block completes, ``final`` (under ``force``) is replaced by the staging
    directory; when it raises, ``final`` is untouched and ``<final>.tmp/``
    keeps whatever was written, for inspection.
    """
    final = Path(final)
    tmp = final.with_name(final.name + ".tmp")
    if final.exists() and not force:
        raise FileExistsError(f"{final} exists; pass --force to replace it")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    yield tmp
    if final.exists():
        if not force:
            raise FileExistsError(f"{final} appeared during the run; {tmp} is kept")
        shutil.rmtree(final)
    os.replace(tmp, final)


def check_motco_version() -> str:
    """Return the installed MOTCO version after checking the minimum.

    Returns
    -------
    str
        The installed version, at least ``constants.ANALYSIS_MOTCO_MIN_VERSION``.

    Raises
    ------
    RuntimeError
        The installed MOTCO is older than the minimum.
    """
    raise NotImplementedError("check_motco_version is a stub; implemented by the analyze change")


def run_clean(
    *,
    platform: str = "all",
    data_root: str | Path | None = None,
    out_dir: str | Path | None = None,
    force: bool = False,
) -> dict:
    """Clean the raw ADNI metabolomics files per platform through metabo_adni.

    Parameters
    ----------
    platform:
        ``"p180"``, ``"nmr"`` or ``"all"`` (``constants.PLATFORMS``, run one
        after the other, each in its own directory).
    data_root:
        Directory holding, flat at its top level, the raw files of
        ``constants.CLEAN_INPUT_FILES`` under the names metabo_adni expects
        (symlinks to the dated LONI downloads under ``<root>/Metabolomics/``;
        p180: the four concentration files, the four LOD workbooks and the
        fasting file ``BIOMARK.csv``; NMR: ``ADNINIGHTINGALE2.csv`` and the
        fasting file). No other file is read. Resolved by
        ``resolve_data_root``.
    out_dir:
        Cleaned root (default ``constants.CLEANED_DIR``); each platform goes
        to ``<out_dir>/<platform>/``.
    force:
        Replace an existing platform directory (after the new one is
        complete).

    Returns
    -------
    dict
        Platform → ``{"dir": Path, "files": {name: Path}, "manifest": dict}``.

    Notes
    -----
    Cleaning is metabo_adni's (``metabo_adni==0.5.8``, pinned; checked by
    ``check_metabo_adni_version`` before any file is read) and is never
    reimplemented here. metabo_adni has no library entry point: its command
    line ``clean_files`` (``metabo_adni.__main__.main``) calls its QC
    functions in a fixed order. This step calls the same functions in the
    same order, in-process, with ``constants.CLEAN_OPTIONS`` (QC at the
    default cutoffs, ``--merge``, no transform), so that it can count the
    participants and metabolites after each; the manifest records the
    equivalent ``clean_files`` command line. metabo_adni changes into the
    directory it reads and writes there, so the inputs are copied (through
    the data root's symlinks) into ``<platform>.tmp/work/``; the data root
    is never written. Before any copy, every input is hashed: the repaired
    UPLC ADNI-GO/2 file is recognised, LONI's unrepaired bytes stop the step
    (``check_known_repairs``), and an unknown hash is a finding.
    metabo_adni prints participant identifiers; everything it prints goes to
    the log, never to the terminal.

    Output contract per platform: ``P180.csv`` / ``NMR.csv`` (the merged
    table under the name metabo_adni's command line gives it, participant ×
    metabolite, keyed by ``RID``, on the scale the platform delivers;
    participant-level), for p180 ``p180_runs.csv`` (``RID``, ``run`` ∈
    {``ADNI1``, ``ADNI2GO``}, from the raw files' participant rows;
    participant-level), ``logs/metabo_adni.log`` (participant-level) and
    ``clean_manifest.json`` (versions, git revision, data root, options and
    ``cli_equivalent``, inputs with target, size, sha256 and known repair,
    raw inventory, cells after every step, imputed points, value summary,
    runs, output hashes, expected and observed counts with deviations,
    findings, upstream behaviours; aggregate, no ``RID``, the only file
    under ``results/cleaned/`` that is committed and synced). Observed
    counts are compared with ``constants.CLEAN_EXPECTED_COUNTS``; each
    deviation is a finding, printed and recorded, and never stops the step.
    Each platform is written to ``<platform>.tmp/`` and renamed when
    complete.
    """
    if platform not in (*PLATFORMS, "all"):
        raise ValueError(f"platform must be one of {[*PLATFORMS, 'all']}, not {platform!r}")
    platforms = list(PLATFORMS) if platform == "all" else [platform]
    installed = check_metabo_adni_version()
    print(f"[clean] metabo_adni {installed} (pinned)")
    for p in platforms:
        _check_clean_options(p)
    root = resolve_data_root(data_root)
    out_root = Path(out_dir) if out_dir is not None else Path(CLEANED_DIR)
    for p in platforms:
        if (out_root / p).exists() and not force:
            raise FileExistsError(f"{out_root / p} exists; pass --force to replace it")

    names = list(dict.fromkeys(n for p in platforms for n in CLEAN_INPUT_FILES[p]))
    require_raw_files(root, names)
    records = {n: hash_raw_file(root / n, root=root) for n in names}
    check_known_repairs(records.values())
    for rec in records.values():
        state = "predeclared" if rec["predeclared"] else "NOT predeclared"
        if rec["repair"] is not None:
            state += f", repaired archive copy ({rec['repair']['repaired_on']})"
        print(f"[clean] input {rec['name']}: sha256 {rec['sha256'][:16]}… ({state})")

    out = {}
    for p in platforms:
        out[p] = _clean_platform(
            p, root=root, final=out_root / p, force=force, inputs=[dict(records[n]) for n in CLEAN_INPUT_FILES[p]]
        )
    return out


def _check_clean_options(platform: str) -> None:
    options = CLEAN_OPTIONS[platform]
    on = [t for t in _CLEAN_TRANSFORMS if options.get(t)]
    if not options.get("merge") or on:
        raise NotImplementedError(
            f"clean implements CLEAN_OPTIONS[{platform!r}] with --merge on and every transform off; "
            f"merge={options.get('merge')!r}, transforms on: {on}. Another setting needs its own change."
        )


def _clean_cli_equivalent(platform: str) -> str:
    options = CLEAN_OPTIONS[platform]
    parts = ["clean_files", "-D", "<work>", "-P", platform, "-F", CLEAN_FASTING_FILE]
    if platform == "p180":
        parts += ["-L", "<work>"]
    for opt in ("mmc", "mpc", "cv", "icc"):
        if opt in options:
            parts += [f"--{opt}", str(options[opt])]
    for flag in ("log2", "merge", "zscore", "winsorize", "remove_moutliers", "residualize_meds"):
        if options.get(flag):
            parts.append("--" + flag.replace("_", "-"))
    return " ".join(parts)


def _cells(files: dict, platform: str) -> dict[str, list[int]]:
    """Unique participants × metabolites per metabo_adni table (the spike's count)."""
    from metabo_adni.data import load

    out = {}
    for key, df in files.items():
        idx = load._get_data_indices(df, platform)
        out[key] = [int(df.loc[idx].index.nunique()), len(load._get_metabo_col_names(df, key))]
    return out


def _participant_ids(df: pd.DataFrame, platform: str) -> set[int]:
    from metabo_adni.data import load

    return {int(r) for r in df.index[load._get_data_indices(df, platform)]}


def _raw_inventory(files: dict, platform: str) -> dict:
    """Records, QC-pool records, participants, replicates, plates and visit codes per table, as read."""
    from metabo_adni.data import load

    out = {}
    for key, df in files.items():
        part = df.loc[load._get_data_indices(df, platform)]
        per_participant = part.index.value_counts()
        visit_col = next((c for c in ("VISCODE2", "VISCODE") if c in df.columns), None)
        visits = None
        if visit_col is not None:
            visits = {str(k): int(v) for k, v in part[visit_col].astype(str).value_counts().sort_index().items()}
        out[key] = {
            "records": int(len(df)),
            "qc_pool_records": int((df.index == _P180_QC_POOL_RID).sum()),
            "participant_records": int(len(part)),
            "participants": int(part.index.nunique()),
            "participants_with_replicates": int((per_participant > 1).sum()),
            "plates": int(part["Plate.Bar.Code"].nunique()) if "Plate.Bar.Code" in df.columns else None,
            "visit_column": visit_col,
            "visit_codes": visits,
            "non_baseline_records": None if visits is None else int(sum(v for k, v in visits.items() if k != "bl")),
        }
    return out


def _missing_before_imputation(files: dict, platform: str) -> dict:
    """Missing points per table before imputation, the merge-kept share and the multi-plate count."""
    from metabo_adni.data import load

    kept_cols: dict[str, set] = {}
    if platform == "p180":
        for kit in ("UPLC", "FIA"):
            a = set(load._get_metabo_col_names(files[f"ADNI1-{kit}"], f"ADNI1-{kit}"))
            b = set(load._get_metabo_col_names(files[f"ADNI2GO-{kit}"], f"ADNI2GO-{kit}"))
            kept_cols[f"ADNI1-{kit}"] = kept_cols[f"ADNI2GO-{kit}"] = a & b
    points, metabolites, points_kept = {}, {}, {}
    mp_metabolites, mp_points = 0, 0
    for key, df in files.items():
        mets = load._get_metabo_col_names(df, key)
        idx = load._get_data_indices(df, platform)
        na = df.loc[idx, list(mets)].isna()
        points[key] = int(na.to_numpy().sum())
        metabolites[key] = int(na.any().sum())
        kept = [m for m in mets if m in kept_cols.get(key, set(mets))]
        points_kept[key] = int(na[kept].to_numpy().sum())
        if platform == "p180":
            plates = df.loc[idx, "Plate.Bar.Code"]
            for m in mets[na.any().to_numpy()]:
                if plates[na[m].to_numpy()].nunique() > 1:
                    mp_metabolites += 1
                    mp_points += int(na[m].sum())
    return {
        "points": {**points, "total": int(sum(points.values()))},
        "metabolites": metabolites,
        "points_in_merged_metabolites": points_kept,
        "multi_plate": {"metabolites": mp_metabolites, "points": mp_points},
    }


def _value_summary(table: pd.DataFrame) -> dict:
    vals = table.to_numpy(dtype=float)
    finite = vals[~np.isnan(vals)]
    positive = finite[finite > 0]
    return {
        "values": int(vals.size),
        "missing": int(np.isnan(vals).sum()),
        "negative": int((finite < 0).sum()),
        "zeros": int((finite == 0).sum()),
        "zero_metabolites": [str(c) for c in table.columns[(table == 0).any().to_numpy()]],
        "below_one": int((finite < 1).sum()),
        "share_below_one": float((finite < 1).mean()),
        "smallest_positive": float(positive.min()) if positive.size else None,
        "median": float(np.median(finite)),
        "metabolites_with_median_below_one": int((table.median() < 1).sum()),
    }


def _count_deviations(expected, observed, label: str) -> list[str]:
    if isinstance(expected, dict) and isinstance(observed, dict):
        out = []
        for k in [*expected, *(k for k in observed if k not in expected)]:
            out += _count_deviations(expected.get(k), observed.get(k), f"{label} {k}")
        return out
    return [] if expected == observed else [f"{label}: expected {expected}, observed {observed}"]


def _clean_platform(platform: str, *, root: Path, final: Path, force: bool, inputs: list[dict]) -> dict:
    """Run metabo_adni's pipeline for one platform in a working copy and write its directory."""
    from metabo_adni.data import load
    from metabo_adni.qc import metabolites, participants, transformations

    options = CLEAN_OPTIONS[platform]
    findings = check_known_repairs(inputs)
    prefix = f"[clean] {platform}"
    with _finalize_output_dir(final, force=force) as tmp:
        # Absolute: metabo_adni changes into the working copy, and the paths
        # passed to it later (fasting file, LOD directory) must still resolve.
        work = tmp.resolve() / "work"
        work.mkdir()
        for rec in inputs:
            shutil.copyfile(root / rec["name"], work / rec["name"])
            if _sha256_file(work / rec["name"]) != rec["sha256"]:
                raise RuntimeError(f"{rec['name']}: the working copy differs from the data root (changed during the copy?)")
        print(f"{prefix}: working copy of {len(inputs)} input(s) in {work}")
        log_path = tmp / CLEAN_LOG
        log_path.parent.mkdir(parents=True)

        cells: dict[str, dict[str, list[int]]] = {}
        cwd = os.getcwd()
        try:
            with log_path.open("w", encoding="utf-8") as log:

                def call(step: str, fn, *args):
                    # metabo_adni prints participant identifiers: stdout and
                    # stderr (warnings) of every call go to the log only.
                    log.write(f"\n##### [clean] {platform}: {step} #####\n")
                    log.flush()
                    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                        result = fn(*args)
                    log.flush()
                    cells[step] = _cells(result, platform)
                    print(f"{prefix}: {step}: " + "; ".join(f"{k} {n} × {m}" for k, (n, m) in cells[step].items()))
                    return result

                # The order of metabo_adni.__main__.main (clean_files).
                files = call("read_files", load.read_files, str(work), platform)
                inventory = _raw_inventory(files, platform)
                raw_ids = {}
                if platform == "p180":
                    raw_ids = {run: set() for run in ("ADNI1", "ADNI2GO")}
                    for key, df in files.items():
                        raw_ids[key.split("-")[0]] |= _participant_ids(df, platform)
                files = call("remove_missing_metabolites", metabolites.remove_missing, files, platform, options["mmc"])
                if platform == "p180":
                    files = call("cross_plate_correction", metabolites.cross_plate_correction, files, platform)
                    files = call("remove_cv", metabolites.remove_cv, files, platform, options["cv"])
                    files = call("remove_icc", metabolites.remove_icc, files, platform, options["icc"])
                files = call("remove_missing_participants", participants.remove_missing, files, platform, options["mpc"])
                files = call("consolidate_replicates", participants.consolidate_replicates, files, platform)
                files = call("remove_non_fasters", participants.remove_non_fasters, files, str(work / CLEAN_FASTING_FILE))
                files = call("remove_bad_qc_tags", participants.remove_bad_qc_tags, files, platform)
                missing = _missing_before_imputation(files, platform)
                files = call(
                    "imputation", transformations.imputation, files, platform, str(work) if platform == "p180" else None
                )
                merged_ids = {}
                if platform == "p180":
                    merged_ids = {
                        run: _participant_ids(files[f"{run}-FIA"], platform) & _participant_ids(files[f"{run}-UPLC"], platform)
                        for run in raw_ids
                    }
                files = call("merge", transformations.merge, files, platform)
        finally:
            os.chdir(cwd)

        # The cleaned table, as metabo_adni's command line writes it.
        ((key, table),) = files.items()
        table_name = f"{key}.csv"
        if table_name != CLEAN_TABLES[platform]:
            raise RuntimeError(f"metabo_adni returned {table_name}, expected {CLEAN_TABLES[platform]}")
        n_dup = int(table.index.duplicated().sum())
        if n_dup:
            raise RuntimeError(f"{table_name}: {n_dup} duplicated participant identifier(s) after the merge")
        table.to_csv(tmp / table_name)
        outputs = [table_name]

        runs = None
        if platform == "p180":
            in_both = raw_ids["ADNI1"] & raw_ids["ADNI2GO"]
            if in_both:
                findings.append(
                    f"p180: {len(in_both)} participant(s) appear in both runs' raw files; each is labelled "
                    "by the run whose tables the merge stacked"
                )

            def run_of(rid: int) -> str:
                hits = [r for r in raw_ids if rid in raw_ids[r]]
                if len(hits) > 1:
                    hits = [r for r in hits if rid in merged_ids[r]]
                if len(hits) != 1:
                    raise RuntimeError("a P180 participant cannot be assigned to exactly one run")
                return hits[0]

            runs_df = pd.DataFrame(
                {PARTICIPANT_ID_COLUMN: table.index.astype(int), "run": [run_of(int(r)) for r in table.index]}
            )
            runs_df.to_csv(tmp / CLEAN_RUNS_TABLE, index=False)
            outputs.append(CLEAN_RUNS_TABLE)
            runs = {r: int((runs_df["run"] == r).sum()) for r in raw_ids}
        outputs.append(CLEAN_LOG)
        shutil.rmtree(work)

        values = _value_summary(table)
        observed = {
            "cells": cells,
            "imputed_points": missing["points"],
            "final": {"participants": int(table.index.nunique()), "metabolites": int(table.shape[1])},
            "duplicated_participants": n_dup,
            "zeros": {"values": values["zeros"], "metabolites": len(values["zero_metabolites"])},
        }
        if platform == "p180":
            observed["runs"] = runs
            observed["multi_plate_lod"] = missing["multi_plate"]
        else:
            observed["non_baseline_records"] = inventory["NMR"]["non_baseline_records"]
        expected = json.loads(json.dumps(CLEAN_EXPECTED_COUNTS[platform]))
        deviations = _count_deviations(expected, observed, platform)
        findings += deviations

        upstream = {
            "medication_reader_baseline": {
                "description": (
                    "load.read_meds_file keeps the medication table's VISCODE2 == 'bl' rows, where most rows "
                    "carry no class (classes are filled at 'sc'); --residualize-meds is off and clean does not "
                    "read the medication table, so it does not apply here"
                ),
                "applies": False,
            },
            "replicates_averaged_across_visits": {
                "description": (
                    "participants.consolidate_replicates averages every record of a participant, whatever its "
                    "visit code; records at visits other than 'bl' per table, as read (None: no visit column)"
                ),
                "non_baseline_records": {k: v["non_baseline_records"] for k, v in inventory.items()},
            },
        }
        if platform == "p180":
            upstream["multi_plate_lod_imputation"] = {
                "description": (
                    "transformations.imputation loops over the plates of a metabolite's missing values and "
                    "assigns each plate's LOD/2 to all of them, so every missing value of a metabolite whose "
                    "missing values span more than one plate receives the last plate's LOD/2; counted over "
                    "the four p180 tables before imputation"
                ),
                **missing["multi_plate"],
            }
            upstream["adni2go_uplc_lod_not_halved"] = {
                "description": (
                    "transformations.imputation assigns ADNI2GO-UPLC missing values the LOD itself (the "
                    "workbook's single row), not LOD/2"
                ),
                "metabolites": missing["metabolites"]["ADNI2GO-UPLC"],
                "points": missing["points"]["ADNI2GO-UPLC"],
                "points_in_merged_metabolites": missing["points_in_merged_metabolites"]["ADNI2GO-UPLC"],
            }

        manifest = {
            "step": "clean",
            "platform": platform,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "versions": _software_versions(),
            "git_revision": _git_revision(),
            "data_root": str(root.resolve()),
            "inputs": inputs,
            "settings": {
                "options": options,
                "fasting_file": CLEAN_FASTING_FILE,
                "lod_directory": "<work>" if platform == "p180" else None,
                "metabo_adni_steps": list(cells),
                "cli_equivalent": _clean_cli_equivalent(platform),
                "cli_note": (
                    "<work> is a directory holding copies of the inputs listed under 'inputs'; clean_files "
                    f"writes {table_name} there"
                ),
            },
            "raw_inventory": inventory,
            "imputation": {
                "points_in_merged_metabolites": missing["points_in_merged_metabolites"],
                "metabolites": missing["metabolites"],
            },
            "value_summary": values,
            "outputs": {
                name: {"sha256": _sha256_file(tmp / name), "bytes": (tmp / name).stat().st_size, "participant_level": True}
                for name in outputs
            },
            "counts": {
                "expected": expected,
                "observed": observed,
                "deviations": deviations,
                "reproduced": not deviations,
            },
            "findings": findings,
            "upstream_behaviours": upstream,
        }
        _write_manifest(tmp / CLEAN_MANIFEST, manifest)

    final_files = {name: final / name for name in [*outputs, CLEAN_MANIFEST]}
    print(
        f"{prefix}: wrote {final}/ ({table_name}: {observed['final']['participants']} participants × "
        f"{observed['final']['metabolites']} metabolites"
        + (f"; runs {runs}" if runs else "")
        + f"; {missing['points']['total']} points imputed)"
    )
    if deviations:
        print(f"{prefix}: {len(deviations)} count deviation(s) from the predeclared counts")
    else:
        print(f"{prefix}: counts reproduce the predeclared ones")
    for msg in findings:
        print(f"{prefix}: FINDING: {msg}")
    return {"dir": final, "files": final_files, "manifest": manifest}


#: The ADNIMERGE columns ``cohort`` reads besides those the scientific
#: constants name: the visit, sex (values ``GROUP_VALUES``), the protocol
#: (written beside ``phase``) and the diagnosis at the visit (read for the
#: stage-source agreement only).
_CLINICAL_VISIT_COLUMN = "VISCODE"
_CLINICAL_SEX_COLUMN = "PTGENDER"
_CLINICAL_PROTOCOL_COLUMN = "ORIGPROT"
_CLINICAL_DX_COLUMN = "DX"
#: The medication table's visit column.
_MEDICATION_VISIT_COLUMN = "VISCODE2"
#: ``DX`` read as the diagnosis at the visit, onto ``STAGE_LABELS``; a recorded
#: change "X to Y" counts as Y. Used for the stage-source agreement only.
_DX_AT_VISIT = {"NL": "CN", "MCI": "MCI", "Dementia": "AD"}
#: The visit-set label of a p180 run whose raw files carry no visit column.
_NO_VISIT_COLUMN = "no visit column"
#: The visit-set label of a cleaned participant without a raw record.
_NO_RECORD = "no record"


def _check_clean_outputs(cleaned: Path) -> dict:
    """Hash every clean output ``cohort`` reads against its ``clean_manifest.json``.

    Stops (before anything is written) on an absent manifest or output and on
    a hash that differs from the recorded one, naming ``<platform>/<file>``.
    """
    out = {}
    for platform in COHORT_RULE["platforms"]:
        manifest_path = cleaned / platform / CLEAN_MANIFEST
        if not manifest_path.is_file():
            raise FileNotFoundError(f"{platform}/{CLEAN_MANIFEST} is absent from {cleaned}; run clean first")
        recorded = json.loads(manifest_path.read_text())["outputs"]
        entry = {
            "manifest": {"name": f"{platform}/{CLEAN_MANIFEST}", "sha256": _sha256_file(manifest_path)},
            "outputs": {},
        }
        names = [CLEAN_TABLES[platform], *([CLEAN_RUNS_TABLE] if platform == "p180" else [])]
        for name in names:
            label, path = f"{platform}/{name}", cleaned / platform / name
            if not path.is_file():
                raise FileNotFoundError(f"{label} is absent from {cleaned}; run clean first")
            if name not in recorded:
                raise RuntimeError(f"{label}: {platform}/{CLEAN_MANIFEST} records no hash for it")
            sha = _sha256_file(path)
            if sha != recorded[name]["sha256"]:
                raise RuntimeError(
                    f"{label}: sha256 {sha} differs from the hash {platform}/{CLEAN_MANIFEST} records "
                    f"({recorded[name]['sha256']}); the cleaned output changed after clean, rerun clean"
                )
            entry["outputs"][name] = {"sha256": sha, "equals_clean_manifest": True}
        out[platform] = entry
    return out


def _read_columns(path: Path, columns: Iterable[str], **kwargs) -> pd.DataFrame:
    """Read ``columns`` of a CSV, stopping on an absent column (named) before reading the rows."""
    columns = list(dict.fromkeys(columns))
    header = pd.read_csv(path, nrows=0).columns
    absent = [c for c in columns if c not in header]
    if absent:
        raise ValueError(f"{path.name}: column(s) absent: {', '.join(repr(c) for c in absent)}")
    return pd.read_csv(path, usecols=columns, low_memory=False, **kwargs)


def _value_counts_text(values: pd.Series) -> str:
    """``'value' (n)`` per distinct value, then ``missing (n)``; values are codes, never identifiers."""
    parts = [f"'{v}' ({int(n)})" for v, n in values.dropna().value_counts().sort_index().items()]
    n_missing = int(values.isna().sum())
    if n_missing:
        parts.append(f"missing ({n_missing})")
    return ", ".join(parts)


def _int_counts(values: pd.Series, order: Iterable | None = None) -> dict[str, int]:
    vc = values.value_counts()
    keys = list(order) if order is not None else sorted(vc.index)
    return {str(k): int(vc.get(k, 0)) for k in keys}


def _sex_stage(frame: pd.DataFrame) -> dict[str, dict[str, int]]:
    return {
        sex: _int_counts(frame.loc[frame[GROUP_COLUMN] == sex, STAGE_COLUMN], STAGE_LABELS) for sex in GROUP_VALUES
    }


def _crosstab(frame: pd.DataFrame, row: str, col: str) -> dict[str, dict[str, int]]:
    """Nonzero cells of ``row`` × ``col`` as nested counts."""
    t = pd.crosstab(frame[row], frame[col])
    return {str(r): {str(c): int(t.loc[r, c]) for c in t.columns if t.loc[r, c]} for r in t.index}


def _stage_counts_table(sets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """``stage_counts.csv``: sex × stage with margins per set, and the intersection's composition cells."""
    phases = ANALYSIS_COVARIATES["phase"]["levels"]
    rows = []
    for name, frame in sets.items():
        for sex in (*GROUP_VALUES, "all"):
            s = frame if sex == "all" else frame[frame[GROUP_COLUMN] == sex]
            for stage in (*STAGE_LABELS, "all"):
                st = s if stage == "all" else s[s[STAGE_COLUMN] == stage]
                if name == "intersection" and "all" not in (sex, stage):
                    for dx in (d for d, mapped in STAGE_RULE["map"].items() if mapped == stage):
                        for phase in phases:
                            n = int(((st["dx_bl"] == dx) & (st["phase"] == phase)).sum())
                            if n:
                                rows.append((name, sex, stage, dx, phase, n))
                rows.append((name, sex, stage, "all", "all", len(st)))
    return pd.DataFrame(rows, columns=["set", GROUP_COLUMN, STAGE_COLUMN, "dx_bl", "phase", "n"])


def run_cohort(
    *,
    cleaned_dir: str | Path | None = None,
    data_root: str | Path | None = None,
    out_dir: str | Path | None = None,
    force: bool = False,
) -> dict:
    """Build the analysis cohort: one baseline row per participant with sex, stage and covariates.

    Parameters
    ----------
    cleaned_dir:
        Output root of ``clean`` (default ``constants.CLEANED_DIR``). Read:
        ``p180/P180.csv``, ``p180/p180_runs.csv`` and ``nmr/NMR.csv`` (the
        ``RID`` column and the run only), each checked against the sha256 its
        platform's ``clean_manifest.json`` records.
    data_root:
        Directory holding, flat at its top level, the five files the cohort
        reads (symlinks into ``<root>/Clinical/`` and ``<root>/Metabolomics/``):
        the clinical table ``ADNI_adnimerge_20170629_QT-freeze.csv``
        (``constants.COHORT_CLINICAL_FILE``), the medication table
        ``ADMCPATIENTDRUGCLASSES_20170512.csv`` (its statin column) and the
        visit columns of ``ADMCDUKEP180UPLCADNI2GO.csv``,
        ``ADMCDUKEP180FIAADNI2GO.csv`` and ``ADNINIGHTINGALE2.csv``
        (``COHORT_RULE["sample_visit_columns"]``). No other file is read.
        Resolved by ``resolve_data_root``.
    out_dir:
        Cohort directory (default ``constants.COHORT_DIR``).
    force:
        Replace an existing cohort directory (after the new one is complete).

    Returns
    -------
    dict
        ``{"dir": Path, "counts": DataFrame, "manifest": dict, "findings": [...]}``;
        ``counts`` is ``stage_counts.csv``.

    Notes
    -----
    Applies the constants decided by the change ``adni-cohort``.
    ``COHORT_RULE``: a cleaned participant enters a platform's set when every
    raw record of the participant on that platform has visit ``bl`` (the
    ADNI-1 p180 run, whose files carry no visit column, counts as baseline)
    and the clinical table has its ``bl`` row; the analysis cohort is the
    intersection of the two sets. ``STAGE_RULE``: ``DX.bl`` onto CN / MCI /
    AD (SMC into CN, EMCI and LMCI into MCI). ``ANALYSIS_COVARIATES``: age,
    education, APOE4 (0/1/2), phase (``ORIGPROT``: ADNI1 vs ADNI-GO/2) from
    the ``bl`` row and statin use from the medication table's ``sc`` row
    (filled 1, empty 0). Sex is ``PTGENDER``.

    The only exclusions are the sample rule and a missing ``bl`` row, counted
    in the cascade. Every other irregularity stops the step before anything
    is written, naming the file or column and a count, never a participant:
    a missing data-root file, LONI's unrepaired bytes of a known-defective
    file, an absent clean manifest or output, a clean output whose hash
    differs from its manifest, an absent column, more than one ``bl`` row
    for a participant, more than one ``sc`` medication row for a participant
    of the platform sets, and among those participants a ``DX.bl`` outside
    the stage map, a ``PTGENDER`` outside ``GROUP_VALUES``, an ``ORIGPROT``
    outside the phase map, a value outside a covariate's levels or a missing
    covariate value (including no ``sc`` medication row). Nothing is
    imputed.

    Output contract: ``cohort.csv`` (one row per participant of either
    platform set, sorted by ``rid``, columns ``COHORT_COLUMNS``: ``rid``,
    ``sex``, ``stage``, ``dx_bl``, ``protocol``, the covariates in declared
    order, ``visit`` and a flag per platform; the intersection is the rows
    with both flags; participant-level and gitignored), ``stage_counts.csv``
    (``set``, ``sex``, ``stage``, ``dx_bl``, ``phase``, ``n``: sex × stage
    with margins for the p180 set, the NMR set and the intersection, and the
    intersection's nonzero sex × stage × ``DX.bl`` × phase cells; aggregate,
    the only committed table) and ``cohort_manifest.json`` (versions, git
    revision, data root, the data-root inputs with target, size, sha256 and
    known repair, the clean manifests and outputs with their hashes, the
    three constants as applied, the counts: visit sets, cascade and sex ×
    stage per set, composition, stage-source agreement, phase against the
    p180 run; descriptives by sex × stage, expected and observed counts with
    deviations, output hashes, findings; aggregate, no ``RID``). Observed
    counts are compared with ``constants.COHORT_EXPECTED_COUNTS``; each
    deviation is a finding, printed and recorded, and never stops the step.
    An unknown input hash and a phase that differs from the p180 run are
    findings too. The directory is written as ``cohort.tmp/`` and renamed
    when complete.
    """
    root = resolve_data_root(data_root)
    cleaned = Path(cleaned_dir) if cleaned_dir is not None else Path(CLEANED_DIR)
    final = Path(out_dir) if out_dir is not None else Path(COHORT_DIR)
    if final.exists() and not force:
        raise FileExistsError(f"{final} exists; pass --force to replace it")
    platforms = COHORT_RULE["platforms"]
    sample_visit, baseline_visit = COHORT_RULE["sample_visit"], COHORT_RULE["baseline_visit"]

    # --- inputs: data-root names and hashes, then the clean outputs --------
    names = [COHORT_CLINICAL_FILE, CLEAN_MEDICATION_FILE, *COHORT_RULE["sample_visit_columns"]]
    require_raw_files(root, names)
    raw = [hash_raw_file(root / n, root=root) for n in names]
    findings = check_known_repairs(raw)
    for rec in raw:
        state = "predeclared" if rec["predeclared"] else "NOT predeclared"
        if rec["repair"] is not None:
            state += f", repaired archive copy ({rec['repair']['repaired_on']})"
        print(f"[cohort] input {rec['name']}: sha256 {rec['sha256'][:16]}… ({state})")
    clean_inputs = _check_clean_outputs(cleaned)
    for platform, entry in clean_inputs.items():
        for name, rec in entry["outputs"].items():
            print(f"[cohort] clean {platform}/{name}: sha256 {rec['sha256'][:16]}… equals {entry['manifest']['name']}")

    cleaned_ids = {
        p: pd.Index(
            _read_columns(cleaned / p / CLEAN_TABLES[p], [PARTICIPANT_ID_COLUMN])[PARTICIPANT_ID_COLUMN].astype(int)
        ).sort_values()
        for p in platforms
    }
    for p, ids in cleaned_ids.items():
        if ids.has_duplicates:
            raise RuntimeError(f"{p}/{CLEAN_TABLES[p]}: {int(ids.duplicated().sum())} duplicated participant(s)")
    runs = _read_columns(cleaned / "p180" / CLEAN_RUNS_TABLE, [PARTICIPANT_ID_COLUMN, "run"])
    runs = runs.set_index(runs[PARTICIPANT_ID_COLUMN].astype(int))["run"]
    if not runs.index.sort_values().equals(cleaned_ids["p180"]):
        raise RuntimeError(f"p180/{CLEAN_RUNS_TABLE} and p180/{CLEAN_TABLES['p180']} hold different participants")

    # --- the visit of each platform's sample (raw visit columns) ----------
    records: dict[str, list[pd.DataFrame]] = {p: [] for p in platforms}
    for name, col in COHORT_RULE["sample_visit_columns"].items():
        (platform,) = [p for p in platforms if name in CLEAN_INPUT_FILES[p]]
        df = _read_columns(root / name, [PARTICIPANT_ID_COLUMN, col])
        records[platform].append(df.rename(columns={col: "visit"}))
    sample_ok, sample_visits = {}, {}
    for p in platforms:
        ids = cleaned_ids[p]
        recs = pd.concat(records[p]) if records[p] else pd.DataFrame(columns=[PARTICIPANT_ID_COLUMN, "visit"])
        labels = recs.groupby(PARTICIPANT_ID_COLUMN)["visit"].agg(lambda s: "+".join(sorted(set(s.astype(str)))))
        labels = labels.reindex(ids).fillna(_NO_RECORD)
        if p == "p180":
            run = runs.reindex(ids)
            no_visit = run.isin(COHORT_RULE["runs_without_visit"])
            labels[no_visit] = _NO_VISIT_COLUMN
            sample_ok[p] = no_visit | (labels == sample_visit)
            sample_visits[p] = {str(r): _int_counts(labels[run == r]) for r in sorted(run.unique())}
        else:
            sample_ok[p] = labels == sample_visit
            sample_visits[p] = _int_counts(labels)

    # --- the clinical table's baseline rows --------------------------------
    clinical_columns = [
        PARTICIPANT_ID_COLUMN,
        _CLINICAL_VISIT_COLUMN,
        _CLINICAL_SEX_COLUMN,
        STAGE_RULE["source"],
        _CLINICAL_DX_COLUMN,
        _CLINICAL_PROTOCOL_COLUMN,
        *(cfg["column"] for cfg in ANALYSIS_COVARIATES.values() if cfg["file"] == "clinical"),
    ]
    clinical = _read_columns(root / COHORT_CLINICAL_FILE, clinical_columns)
    bl = clinical[clinical[_CLINICAL_VISIT_COLUMN] == baseline_visit]
    n_dup = int(bl.loc[bl[PARTICIPANT_ID_COLUMN].duplicated(keep=False), PARTICIPANT_ID_COLUMN].nunique())
    if n_dup:
        raise RuntimeError(
            f"{COHORT_CLINICAL_FILE}: {n_dup} participant(s) with more than one {_CLINICAL_VISIT_COLUMN} "
            f"'{baseline_visit}' row"
        )
    bl = bl.set_index(PARTICIPANT_ID_COLUMN)

    # --- platform sets: the sample rule, then the baseline row -------------
    sets_ids, cascade = {}, {}
    for p in platforms:
        ids = cleaned_ids[p]
        at_bl = ids[sample_ok[p].to_numpy()]
        with_row = at_bl[at_bl.isin(bl.index)]
        cascade[p] = {
            "cleaned": len(ids),
            "excluded_sample_not_bl": len(ids) - len(at_bl),
            "excluded_no_clinical_bl_row": len(at_bl) - len(with_row),
            "set": len(with_row),
        }
        sets_ids[p] = set(with_row)
        print(
            f"[cohort] {p}: {len(ids)} cleaned → {len(at_bl)} with every sample at '{sample_visit}' → "
            f"{len(with_row)} with a '{baseline_visit}' row in {COHORT_CLINICAL_FILE}"
        )
    union = sorted(set().union(*sets_ids.values()))
    c = bl.loc[union]

    # --- the medication table's rows at each medication covariate's visit --
    med_covariates = {n: cfg for n, cfg in ANALYSIS_COVARIATES.items() if cfg["file"] == "medication"}
    medication: dict[str, pd.Series] = {}
    med_counts: dict[str, dict] = {}
    if med_covariates:
        meds = _read_columns(
            root / CLEAN_MEDICATION_FILE,
            [PARTICIPANT_ID_COLUMN, _MEDICATION_VISIT_COLUMN, *(cfg["column"] for cfg in med_covariates.values())],
            dtype=str,
        )
        for name, cfg in med_covariates.items():
            rows = meds[meds[_MEDICATION_VISIT_COLUMN] == cfg["visit"]]
            rows = rows.set_index(rows[PARTICIPANT_ID_COLUMN].astype(int))
            in_sets = rows[rows.index.isin(union)]
            n_dup = int(in_sets.index[in_sets.index.duplicated(keep=False)].nunique())
            if n_dup:
                raise RuntimeError(
                    f"{CLEAN_MEDICATION_FILE}: {n_dup} participant(s) of the platform sets with more than one "
                    f"{_MEDICATION_VISIT_COLUMN} '{cfg['visit']}' row"
                )
            cell = in_sets[cfg["column"]]
            # A filled cell is use, an empty cell on an existing row no use; no row is missing.
            medication[name] = (cell.notna() & cell.str.strip().ne("")).astype(int).reindex(union)
            med_counts[name] = {"visit": cfg["visit"], "visit_rows": len(rows)}

    # --- stage, sex and covariates: stop on any value outside the rules -----
    problems = []
    dx_bl = c[STAGE_RULE["source"]]
    stage = dx_bl.map(STAGE_RULE["map"])
    if stage.isna().any():
        problems.append(
            f"{STAGE_RULE['source']}: values outside STAGE_RULE['map'] among the platform sets' participants: "
            + _value_counts_text(dx_bl[stage.isna()])
        )
    sex = c[_CLINICAL_SEX_COLUMN]
    if (~sex.isin(GROUP_VALUES)).any():
        problems.append(
            f"{_CLINICAL_SEX_COLUMN}: values outside GROUP_VALUES among the platform sets' participants: "
            + _value_counts_text(sex[~sex.isin(GROUP_VALUES)])
        )
    covariates: dict[str, pd.Series] = {}
    for name, cfg in ANALYSIS_COVARIATES.items():
        if cfg["file"] == "medication":
            values = medication[name]
            source = f"{cfg['column']} at '{cfg['visit']}' in {CLEAN_MEDICATION_FILE}"
            if values.isna().any():
                problems.append(
                    f"{name} ({source}): {int(values.isna().sum())} participant(s) of the platform sets without a "
                    f"'{cfg['visit']}' row; nothing is imputed (missing policy error)"
                )
        else:
            values = c[cfg["column"]]
            source = cfg["column"]
            if values.isna().any():
                problems.append(
                    f"{name} ({source}): {int(values.isna().sum())} participant(s) of the platform sets missing; "
                    "nothing is imputed (missing policy error)"
                )
        present = values.dropna()
        if "map" in cfg:
            outside = ~present.isin(list(cfg["map"]))
            if outside.any():
                problems.append(
                    f"{name} ({source}): values outside ANALYSIS_COVARIATES['{name}']['map']: "
                    + _value_counts_text(present[outside])
                )
            values = values.map(cfg["map"])
            present = values.dropna()
        if cfg["coding"] == "numeric":
            numeric = pd.to_numeric(present, errors="coerce")
            if numeric.isna().any():
                problems.append(f"{name} ({source}): {int(numeric.isna().sum())} non-numeric value(s)")
        elif (~present.isin(list(cfg["levels"]))).any():
            problems.append(
                f"{name} ({source}): values outside the levels {list(cfg['levels'])}: "
                + _value_counts_text(present[~present.isin(list(cfg["levels"]))])
            )
        covariates[name] = values
    if problems:
        raise ValueError(
            "cohort stops before writing anything (a value outside the declared rules needs a proposal, "
            "not a silent drop): " + "; ".join(problems)
        )
    for name, cfg in ANALYSIS_COVARIATES.items():
        if cfg["coding"] == "numeric":
            covariates[name] = pd.to_numeric(covariates[name])
        elif all(isinstance(v, int) for v in cfg["levels"]):
            covariates[name] = covariates[name].astype(int)

    # --- the participant table ----------------------------------------------
    cohort = pd.DataFrame(
        {
            SAMPLE_COLUMN: union,
            GROUP_COLUMN: sex.to_numpy(),
            STAGE_COLUMN: stage.to_numpy(),
            "dx_bl": dx_bl.to_numpy(),
            "protocol": c[_CLINICAL_PROTOCOL_COLUMN].to_numpy(),
            **{name: values.to_numpy() for name, values in covariates.items()},
            "visit": baseline_visit,
            **{p: [rid in sets_ids[p] for rid in union] for p in platforms},
        }
    )[list(COHORT_COLUMNS)]
    in_all = cohort[list(platforms)].all(axis=1)
    sets = {p: cohort[cohort[p]] for p in platforms}
    sets["intersection"] = inter = cohort[in_all]

    # --- counts ---------------------------------------------------------------
    counts: dict = {
        p: {"sample_visits": sample_visits[p], "cascade": cascade[p], "sex_stage": _sex_stage(sets[p])}
        for p in platforms
    }
    composition: dict[str, dict] = {}
    for sex_ in GROUP_VALUES:
        for dx_ in STAGE_RULE["map"]:
            phases = inter.loc[(inter[GROUP_COLUMN] == sex_) & (inter["dx_bl"] == dx_), "phase"].value_counts()
            cells = {str(ph): int(phases[ph]) for ph in ANALYSIS_COVARIATES["phase"]["levels"] if phases.get(ph, 0)}
            if cells:
                composition.setdefault(sex_, {})[dx_] = cells
    dx = c.loc[inter[SAMPLE_COLUMN], _CLINICAL_DX_COLUMN]
    at_visit = dx.str.split(" to ").str[-1].map(_DX_AT_VISIT)
    inter_stage = inter.set_index(SAMPLE_COLUMN)[STAGE_COLUMN]
    unread = int((dx.notna() & at_visit.isna()).sum())
    if unread:
        findings.append(
            f"{_CLINICAL_DX_COLUMN}: {unread} intersection participant(s) with a value outside "
            f"{sorted(_DX_AT_VISIT)} (or a change 'X to Y' between them); counted as differing from the stage"
        )
    phase_vs_run = {}
    for name in ("p180", "intersection"):
        frame = sets[name].set_index(SAMPLE_COLUMN)
        frame = frame.assign(run=runs.reindex(frame.index))
        phase_vs_run[name] = {
            "table": _crosstab(frame, "phase", "run"),
            "disagreements": int((frame["phase"] != frame["run"]).sum()),
        }
    if phase_vs_run["p180"]["disagreements"]:
        findings.append(
            f"phase against the p180 run: {phase_vs_run['p180']['disagreements']} participant(s) of the p180 set "
            f"whose phase ({ANALYSIS_COVARIATES['phase']['column']}) differs from their run in {CLEAN_RUNS_TABLE}"
        )
    counts["intersection"] = {
        "cascade": {
            "cleaned_on_both": len(set.intersection(*(set(cleaned_ids[p]) for p in platforms))),
            "set": len(inter),
        },
        "sex_stage": _sex_stage(inter),
        "composition": composition,
        "stage_source": {
            "agree": int((at_visit == inter_stage).sum()),
            "differ": int((dx.notna() & (at_visit != inter_stage)).sum()),
            "missing": int(dx.isna().sum()),
        },
        "phase_vs_run_disagreements": phase_vs_run["intersection"]["disagreements"],
        "statin_users": int(inter["statin"].sum()),
        "missing_covariate_values": int(inter[list(ANALYSIS_COVARIATES)].isna().sum().sum()),
    }
    counts["union"] = {
        "participants": len(cohort),
        "both": int(in_all.sum()),
        **{
            f"{p}_only": int((cohort[p] & ~cohort[[q for q in platforms if q != p]].any(axis=1)).sum())
            for p in platforms
        },
    }
    counts["phase_vs_run"] = phase_vs_run
    counts["stage_source_detail"] = _crosstab(
        pd.DataFrame({"dx_bl": inter["dx_bl"].to_numpy(), "dx": dx.fillna("(missing)").to_numpy()}), "dx_bl", "dx"
    )
    counts["inventory"] = {
        "clinical": {"rows": len(clinical), "baseline_rows": len(bl)},
        "medication": med_counts,
    }

    descriptives = {}
    for sex_ in GROUP_VALUES:
        descriptives[sex_] = {}
        for st in STAGE_LABELS:
            cell = inter[(inter[GROUP_COLUMN] == sex_) & (inter[STAGE_COLUMN] == st)]
            d: dict = {"n": len(cell)}
            for name, cfg in ANALYSIS_COVARIATES.items():
                if cfg["coding"] == "numeric":
                    d[name] = {"mean": float(cell[name].mean()), "sd": float(cell[name].std())}
                else:
                    d[name] = _int_counts(cell[name], cfg["levels"])
            descriptives[sex_][st] = d

    expected = json.loads(json.dumps(COHORT_EXPECTED_COUNTS))
    deviations = [msg for key in expected for msg in _count_deviations(expected[key], counts.get(key), key)]
    findings += deviations
    stage_counts = _stage_counts_table(sets)

    manifest = {
        "step": "cohort",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": _software_versions(),
        "git_revision": _git_revision(),
        "data_root": str(root.resolve()),
        "inputs": {"clean": clean_inputs, "raw": raw},
        "settings": {
            "COHORT_RULE": COHORT_RULE,
            "STAGE_RULE": STAGE_RULE,
            "ANALYSIS_COVARIATES": ANALYSIS_COVARIATES,
            "GROUP_VALUES": GROUP_VALUES,
            "COHORT_COLUMNS": COHORT_COLUMNS,
            "stage_source_reading": {
                "column": _CLINICAL_DX_COLUMN,
                "map": _DX_AT_VISIT,
                "note": "a recorded change 'X to Y' counts as Y; read for the agreement count only",
            },
        },
        "counts": counts,
        "descriptives": {"set": "intersection", "cells": descriptives},
        "expected": expected,
        "deviations": deviations,
        "findings": findings,
    }

    # --- outputs ----------------------------------------------------------------
    with _finalize_output_dir(final, force=force) as tmp:
        cohort.to_csv(tmp / COHORT_TABLE, index=False)
        stage_counts.to_csv(tmp / COHORT_COUNTS, index=False)
        manifest["outputs"] = {
            name: {
                "sha256": _sha256_file(tmp / name),
                "bytes": (tmp / name).stat().st_size,
                "participant_level": name == COHORT_TABLE,
            }
            for name in (COHORT_TABLE, COHORT_COUNTS)
        }
        _write_manifest(tmp / COHORT_MANIFEST, manifest)

    sex_stage = counts["intersection"]["sex_stage"]
    cells = "; ".join(
        f"{sex_} {'/'.join(STAGE_LABELS)} " + "/".join(str(n) for n in sex_stage[sex_].values())
        for sex_ in GROUP_VALUES
    )
    print(f"[cohort] intersection: {len(inter)} ({cells})")
    print(
        f"[cohort] wrote {final}/ ({COHORT_TABLE}: {len(cohort)} participants, {len(inter)} in every platform set; "
        f"{COHORT_COUNTS}: {len(stage_counts)} rows)"
    )
    if deviations:
        print(f"[cohort] {len(deviations)} count deviation(s) from the predeclared counts")
    else:
        print("[cohort] counts reproduce the predeclared ones")
    for msg in findings:
        print(f"[cohort] FINDING: {msg}")
    return {"dir": final, "counts": stage_counts, "manifest": manifest, "findings": findings}


def run_export(
    *,
    cleaned_dir: str | Path | None = None,
    cohort_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    force: bool = False,
) -> dict:
    """Export the MOTCO blocks and metadata from the cleaned matrices and the cohort.

    Parameters
    ----------
    cleaned_dir:
        Output root of ``clean`` (default ``constants.CLEANED_DIR``).
    cohort_dir:
        Output directory of ``cohort`` (default ``constants.COHORT_DIR``).
    out_dir:
        MOTCO input directory (default ``constants.MOTCO_INPUT_DIR``).
    force:
        Replace an existing export.

    Returns
    -------
    dict
        ``{"dir": Path, "blocks": {platform: shape}, "manifest": dict, "findings": [...]}``.

    Notes
    -----
    Restricts every block to the cohort's participants in ``cohort.csv``
    order and applies the (undecided) constant ``EXPORT_FEATURE_RULE``
    (which cleaned metabolites enter each block and on which scale).
    Covariates are exported, not applied: adjustment is MOTCO's. No step
    before ``analyze`` uses sex or stage to select features. Output
    contract: one block per platform, ``<platform>.csv`` (participant ×
    metabolite, ``rid`` index), ``metadata.csv`` (``rid``, ``sex``,
    ``stage``, in that order), ``covariates.csv`` (``rid`` plus the
    covariate columns), all participant-level and gitignored;
    ``features_<platform>.csv`` (one row per cleaned metabolite with its
    status under the rule; gitignored with the other CSVs, regenerable) and
    ``manifest.json`` (input hashes incl. the cohort and clean manifests, the
    rule as applied, n per sex × stage cell, feature counts per status,
    every output file's sha256, software, git revision, findings; the only
    committed file). The directory is written as ``motco_input.tmp/`` and
    renamed when complete.
    """
    raise NotImplementedError("run_export is a stub; implemented by the export change")


def run_analysis(
    *,
    input_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    n_jobs: int = 1,
    force: bool = False,
) -> dict:
    """Run the covariate-adjusted MOTCO sex × stage trajectory comparison.

    Parameters
    ----------
    input_dir:
        Output directory of ``export`` (default ``constants.MOTCO_INPUT_DIR``).
    out_dir:
        Analysis directory (default ``constants.MOTCO_ANALYSIS_DIR``).
    n_jobs:
        Parallel jobs for MOTCO's CV and RRPP. MOTCO seeds one RRPP stream
        per worker, so values other than 1 change the permutation draws
        (p-values, null summaries) but not the statistics, rank or latent
        space; reported runs use ``constants.REPORTED_N_JOBS`` (1) and
        another value is recorded as a finding.
    force:
        Replace an existing analysis directory.

    Returns
    -------
    dict
        ``{"dir": Path, "record": dict, "manifest": dict, "findings": [...]}``.

    Notes
    -----
    One call of ``motco.analysis.analyze_trajectories`` (MOTCO at least
    ``constants.ANALYSIS_MOTCO_MIN_VERSION``, checked by
    ``check_motco_version``; never assembled from ``motco plsr`` +
    ``motco de``) on the exported blocks, group ``sex``, stage ``stage`` in
    ``STAGE_LABELS`` order, with ``ANALYSIS_COVARIATES`` (decided by
    ``adni-cohort``; its codings declared to MOTCO, missing policy
    ``error``, nothing imputed) and the (undecided) constants
    ``ANALYSIS_PERMUTATIONS``, ``ANALYSIS_SEED`` and ``ANALYSIS_RANK_FLOOR``
    (passed explicitly and checked against MOTCO's default before any input
    is read); MOTCO's other defaults are not overridden. Output contract:
    MOTCO's artifact written by ``write_analysis_outputs`` (``result.json``,
    ``latent_scores.csv``, ``pls_loadings.csv``, ``stage_means.csv``) plus
    ``analysis_metadata.csv`` (the table the model saw, parsed back exactly
    as ``motco analyze --metadata`` would), ``analysis_manifest.json``
    (input file hashes and the export manifest hash, the covariate set and
    coding, the measurement settings incl. ``min_components`` and
    ``n_jobs``, a ``cli_equivalent`` that reproduces the run with MOTCO's
    CLI, MOTCO and software versions, git revision, findings) and
    ``summary.md`` (the statistics, p-values, CV-selected rank, null
    summaries and the covariate block, generated from the record).
    ``latent_scores.csv`` and ``analysis_metadata.csv`` are participant-level
    and gitignored; the rest is aggregate. Written as
    ``motco_analysis.tmp/`` and renamed when complete.
    """
    raise NotImplementedError("run_analysis is a stub; implemented by the analyze change")


def run_axis_diagnostics(
    *,
    input_dir: str | Path | None = None,
    analysis_dir: str | Path | None = None,
    cohort_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    force: bool = False,
) -> dict:
    """Measure what the MOTCO latent axes and the block axes correlate with.

    Parameters
    ----------
    input_dir:
        Output directory of ``export``; the blocks, metadata, covariates and
        manifest are read.
    analysis_dir:
        Output directory of ``analyze``; read and checked (its manifest's
        input hashes against the export files), never written.
    cohort_dir:
        Output directory of ``cohort``; the source of the predeclared
        diagnostic variables that are not export columns.
    out_dir:
        Diagnostics directory (default ``constants.DIAGNOSTICS_DIR``).
    force:
        Replace an existing diagnostics directory.

    Returns
    -------
    dict
        ``{"dir": Path, "tables": {name: DataFrame}, "manifest": dict, "findings": [...]}``.

    Notes
    -----
    For every latent component of the analysis: the Spearman and
    covariate-partial Spearman correlations with the (undecided)
    ``DIAGNOSTIC_VARIABLES``, the same for the first PCs of each z-scored
    block, and the geometry shares along each component from
    ``stage_means.csv``; rows at or above ``DIAGNOSTIC_CORRELATION_THRESHOLD``
    are flagged, with no p-value. The diagnostic reads sex and stage, so it
    is never a filter: its outputs are read by no ``export`` or ``analyze``
    run, and no variant is derived from a diagnostic value. Output contract:
    ``axis_correlations.csv``, ``block_pcs.csv``, ``geometry_shares.csv``
    (per component × variable; aggregate), ``diagnostics.md`` (flagged rows
    first) and ``diagnostics_manifest.json`` (input hashes, variables and
    their sources, threshold, software, git revision, findings). Nothing
    participant-level is written.
    """
    raise NotImplementedError("run_axis_diagnostics is a stub; implemented by the axis-diagnostics change")


def run_report(
    *,
    analysis_dir: str | Path | None = None,
    cohort_dir: str | Path | None = None,
    diagnostics_dir: str | Path | None = None,
    out: str | Path | None = None,
    check: bool = False,
) -> dict:
    """Write the case-study report from the generated files, or check one against them.

    Parameters
    ----------
    analysis_dir:
        Output directory of ``analyze``; ``result.json``, ``summary.md`` and
        ``analysis_manifest.json`` are read.
    cohort_dir:
        Output directory of ``cohort``; ``stage_counts.csv`` is read.
    diagnostics_dir:
        Output directory of ``axis-diagnostics``, when present.
    out:
        Report path (default ``reports/motco-adni-<date>.md``).
    check:
        Instead of writing, read the report at ``out`` and compare every
        number in its generated tables with the generated files; a mismatch
        is an error naming the cell.

    Returns
    -------
    dict
        ``{"path": Path, "tables": {name: DataFrame}, "checked": bool, "mismatches": [...]}``.

    Notes
    -----
    Report numbers are pasted from the generated files and checked by this
    step, never retyped. The report carries the design cells, the statistics
    with their p-values and null summaries, the CV-selected rank beside
    ``angle``, the covariate block, the feature counts, the diagnostics'
    flagged rows and the (undecided) ``READING_RULES``; it quotes only
    aggregate values and reads no participant-level file. The report is
    committed under ``reports/`` after ``--check`` passes.
    """
    raise NotImplementedError("run_report is a stub; implemented by the report change")


__all__ = [
    "PLATFORMS",
    "resolve_data_root",
    "require_raw_files",
    "hash_raw_file",
    "check_known_repairs",
    "check_metabo_adni_version",
    "check_motco_version",
    "run_clean",
    "run_cohort",
    "run_export",
    "run_analysis",
    "run_axis_diagnostics",
    "run_report",
]
