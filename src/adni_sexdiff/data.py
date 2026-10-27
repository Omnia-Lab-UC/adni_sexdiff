"""Pipeline steps of adni_sexdiff.

``clean`` (change ``adni-metabolomics-clean``), ``cohort`` (change
``adni-cohort``), ``export`` (change ``adni-export``) and ``analyze``
(change ``adni-analyze``) are implemented. Every other step is a stub: its
docstring states the inputs it reads, the files it writes and the contract
of those files, and its body raises ``NotImplementedError`` until an
OpenSpec change implements it. The statistical choices the remaining steps
need (the diagnostic variables and threshold) are undecided and enter only
through a proposal (see ``constants``).

The raw-input helpers (``require_raw_files``, ``hash_raw_file``,
``check_known_repairs``), the version gates (``check_metabo_adni_version``,
``check_motco_version``, ``check_motco_rank_floor``) and the manifest and
output-directory helpers (``_git_revision``, ``_software_versions``,
``_write_manifest``, ``_finalize_output_dir``) are shared by every step.

ADNI is controlled-access. Every table keyed by ``RID`` is participant-level:
it stays under the ignored paths of ``constants.PARTICIPANT_LEVEL_PATTERNS``,
is never printed, never synced and never quoted. Progress output names
counts and files, never participants.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
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
    ANALYSIS_ALPHA,
    ANALYSIS_CATEGORICAL_COVARIATES,
    ANALYSIS_COVARIATES,
    ANALYSIS_EXPECTED_COUNTS,
    ANALYSIS_INPUT_FILES,
    ANALYSIS_LATENT_ADJUSTMENT,
    ANALYSIS_LATENT_SCORES,
    ANALYSIS_MANIFEST,
    ANALYSIS_METADATA,
    ANALYSIS_MISSING_COVARIATES,
    ANALYSIS_MOTCO_MIN_VERSION,
    ANALYSIS_PERMUTATIONS,
    ANALYSIS_PREDECLARED_LATENT_SENSITIVITY,
    ANALYSIS_RANK_FLOOR,
    ANALYSIS_REJECTION_RULE,
    ANALYSIS_SEED,
    ANALYSIS_STATISTICS,
    ANALYSIS_SUMMARY,
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
    EXPORT_BLOCKS,
    EXPORT_COVARIATE_COLUMNS,
    EXPORT_COVARIATES,
    EXPORT_EXPECTED_COUNTS,
    EXPORT_FEATURE_RULE,
    EXPORT_FEATURES,
    EXPORT_MANIFEST,
    EXPORT_METADATA,
    GROUP_COLUMN,
    GROUP_VALUES,
    KNOWN_RAW_FILE_REPAIRS,
    METABO_ADNI_VERSION,
    MOTCO_ANALYSIS_DIR,
    MOTCO_INPUT_DIR,
    PARTICIPANT_ID_COLUMN,
    PLATFORMS,
    RAW_INPUT_SHA256,
    READING_RULES,
    REPORTED_N_JOBS,
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


def _check_clean_outputs(cleaned: Path, *, platforms: Iterable[str] = COHORT_RULE["platforms"], runs: bool = True) -> dict:
    """Hash every clean output a step reads against its ``clean_manifest.json``.

    ``platforms`` names the cleaned tables read; ``runs`` adds the p180 run
    table (``cohort`` reads it, ``export`` does not). Stops (before anything
    is written) on an absent manifest or output and on a hash that differs
    from the recorded one, naming ``<platform>/<file>``.
    """
    out = {}
    for platform in platforms:
        manifest_path = cleaned / platform / CLEAN_MANIFEST
        if not manifest_path.is_file():
            raise FileNotFoundError(f"{platform}/{CLEAN_MANIFEST} is absent from {cleaned}; run clean first")
        recorded = json.loads(manifest_path.read_text())["outputs"]
        entry = {
            "manifest": {"name": f"{platform}/{CLEAN_MANIFEST}", "sha256": _sha256_file(manifest_path)},
            "outputs": {},
        }
        names = [CLEAN_TABLES[platform], *([CLEAN_RUNS_TABLE] if platform == "p180" and runs else [])]
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


#: How a name mark of ``EXPORT_FEATURE_RULE["membership"][<platform>]["derived"]``
#: is tested against a cleaned column name.
_NAME_MARK_TESTS = {
    "endswith": lambda column, mark: column.endswith(mark),
    "contains": lambda column, mark: mark in column,
    "equals": lambda column, mark: column == mark,
}
#: The family of a kept column (a measured concentration).
_KEPT_FAMILY = "concentration"
#: The derived families of the rule, over every platform, in the rule's order.
_DERIVED_FAMILIES: tuple[str, ...] = tuple(
    dict.fromkeys(f for m in EXPORT_FEATURE_RULE["membership"].values() for f in m["derived"])
)
#: The columns of ``features_<platform>.csv``; the last five are on the
#: transformed scale and stay empty for derived rows.
_FEATURE_COLUMNS = (
    "feature", "family", "status", "zero_cells", "median", "floor", "floor_over_median",
    "skew_raw", "skew_transformed", "max_abs_z_transformed", "phase_d",
)
#: Singular values below this fraction of the largest count as zero in the
#: numerical rank of a standardized block.
_RANK_TOLERANCE = 1e-8


def _feature_family(column: str, derived: dict[str, tuple[str, str]]) -> str | None:
    """The derived family of a cleaned column under the name marks (first match), or ``None`` when kept."""
    for family, (test, mark) in derived.items():
        if _NAME_MARK_TESTS[test](column, mark):
            return family
    return None


def _check_cohort_outputs(cohort_dir: Path, clean_inputs: dict) -> tuple[dict, dict, dict]:
    """Hash ``cohort.csv`` against ``cohort_manifest.json`` and check the manifest's clean hashes.

    Returns the cohort manifest, the manifest's ``inputs.cohort`` entry and
    the chain check (``<platform>/<table>`` → ``True``). Stops, before
    anything is written, on an absent manifest or table, a ``cohort.csv``
    whose hash differs from the recorded one, and a recorded clean hash that
    differs from the clean manifest's (the cohort was built from an earlier
    clean), naming the file and the ``cohort`` command.
    """
    manifest_path = cohort_dir / COHORT_MANIFEST
    if not manifest_path.is_file():
        raise FileNotFoundError(f"{COHORT_MANIFEST} is absent from {cohort_dir}; run cohort first")
    cohort_manifest = json.loads(manifest_path.read_text())
    table_path = cohort_dir / COHORT_TABLE
    if not table_path.is_file():
        raise FileNotFoundError(f"{COHORT_TABLE} is absent from {cohort_dir}; run cohort first")
    recorded = cohort_manifest.get("outputs", {})
    if COHORT_TABLE not in recorded:
        raise RuntimeError(f"{COHORT_TABLE}: {COHORT_MANIFEST} records no hash for it; rerun cohort")
    sha = _sha256_file(table_path)
    if sha != recorded[COHORT_TABLE]["sha256"]:
        raise RuntimeError(
            f"{COHORT_TABLE}: sha256 {sha} differs from the hash {COHORT_MANIFEST} records "
            f"({recorded[COHORT_TABLE]['sha256']}); the cohort output changed after cohort, rerun cohort"
        )
    chain = {}
    recorded_clean = cohort_manifest.get("inputs", {}).get("clean", {})
    for platform, entry in clean_inputs.items():
        for name, rec in entry["outputs"].items():
            try:
                seen = recorded_clean[platform]["outputs"][name]["sha256"]
            except (KeyError, TypeError):
                raise RuntimeError(f"{name}: {COHORT_MANIFEST} records no hash for {platform}/{name}; rerun cohort") from None
            if seen != rec["sha256"]:
                raise RuntimeError(
                    f"{name}: the hash {COHORT_MANIFEST} records for {platform}/{name} ({seen}) differs from the one "
                    f"{platform}/{CLEAN_MANIFEST} records ({rec['sha256']}); the cohort was built from an earlier "
                    "clean output, rerun cohort"
                )
            chain[f"{platform}/{name}"] = True
    inputs = {
        "manifest": {"name": COHORT_MANIFEST, "sha256": _sha256_file(manifest_path)},
        "outputs": {COHORT_TABLE: {"sha256": sha, "equals_cohort_manifest": True}},
    }
    return cohort_manifest, inputs, chain


def _standardize(M: np.ndarray) -> np.ndarray:
    return (M - M.mean(axis=0)) / M.std(axis=0)


def _shape_counts(M: np.ndarray) -> dict:
    """Skew (pandas, bias-corrected) and largest |z| (population sd) per feature, counted over features."""
    df = pd.DataFrame(M)
    skew = df.skew().to_numpy()
    z = ((df - df.mean()) / df.std(ddof=0)).abs().max().to_numpy()
    return {
        "abs_skew_gt_1": int((np.abs(skew) > 1).sum()),
        "skew_lt_minus_1": int((skew < -1).sum()),
        "median_abs_skew": float(np.median(np.abs(skew))),
        "max_abs_z_gt_5": int((z > 5).sum()),
        "max_abs_z_gt_8": int((z > 8).sum()),
        "max_abs_z_gt_15": int((z > 15).sum()),
    }


def _spectrum(M: np.ndarray) -> dict:
    """Variance shares of the leading principal components of the standardized block, and its ranks."""
    s = np.linalg.svd(_standardize(M), compute_uv=False)
    ev = s**2 / (s**2).sum()
    return {
        "features": int(M.shape[1]),
        "pc1_share": float(ev[0]),
        "pc1_3_share": float(ev[:3].sum()),
        "pc1_10_share": float(ev[:10].sum()),
        "effective_rank": float(1 / np.sum(ev**2)),
        "numerical_rank": int((s / s[0] > _RANK_TOLERANCE).sum()),
        "numerical_rank_tolerance": _RANK_TOLERANCE,
    }


def _phase_offset(M: np.ndarray, phase: np.ndarray, levels: tuple[str, str]) -> tuple[np.ndarray, dict]:
    """Standardized mean difference per feature between the two phases, and the PC correlations with phase."""
    a, b = M[phase == levels[0]], M[phase == levels[1]]
    d = (a.mean(axis=0) - b.mean(axis=0)) / np.sqrt((a.var(axis=0) + b.var(axis=0)) / 2)
    u, _, _ = np.linalg.svd(_standardize(M), full_matrices=False)
    g = (phase == levels[0]).astype(float)
    return d, {
        "contrast": f"{levels[0]} minus {levels[1]}, pooled within-phase sd",
        "median_abs_d": float(np.median(np.abs(d))),
        "max_abs_d": float(np.abs(d).max()),
        "abs_d_gt_0_5": int((np.abs(d) > 0.5).sum()),
        "abs_d_gt_1": int((np.abs(d) > 1).sum()),
        "abs_corr_pc1_phase": float(abs(np.corrcoef(u[:, 0], g)[0, 1])),
        "abs_corr_pc2_phase": float(abs(np.corrcoef(u[:, 1], g)[0, 1])),
    }


def _project(observed, expected):
    """``observed`` restricted, recursively, to the keys ``expected`` holds (an absent key stays absent)."""
    if isinstance(expected, dict) and isinstance(observed, dict):
        return {k: _project(observed[k], v) for k, v in expected.items() if k in observed}
    return observed


def run_export(
    *,
    cleaned_dir: str | Path | None = None,
    cohort_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    force: bool = False,
) -> dict:
    """Export the MOTCO blocks, metadata and covariates of the analysis cohort under the feature rule.

    Parameters
    ----------
    cleaned_dir:
        Output root of ``clean`` (default ``constants.CLEANED_DIR``). Read:
        ``p180/P180.csv`` and ``nmr/NMR.csv``, each checked against the
        sha256 its platform's ``clean_manifest.json`` records.
    cohort_dir:
        Output directory of ``cohort`` (default ``constants.COHORT_DIR``).
        Read: ``cohort.csv``, checked against the sha256
        ``cohort_manifest.json`` records, and the manifest itself, whose
        recorded clean hashes must equal the clean manifests' (the chain
        check: a cohort built from an earlier clean output stops the step,
        naming the file and the ``cohort`` command). No data-root file and
        no other file is read.
    out_dir:
        MOTCO input directory (default ``constants.MOTCO_INPUT_DIR``).
    force:
        Replace an existing export (after the new one is complete).

    Returns
    -------
    dict
        ``{"dir": Path, "blocks": {platform: (participants, metabolites)},
        "manifest": dict, "findings": [...]}``.

    Notes
    -----
    Applies ``EXPORT_FEATURE_RULE``, decided by the change ``adni-export``.
    The exported participants are the rows of ``cohort.csv`` that carry
    every platform flag, in ``cohort.csv`` order (ascending ``rid``).
    Membership: every cleaned p180 metabolite enters its block; a cleaned
    NMR column enters unless its name carries a derived mark (percentage
    ``_PCT``, ratio ``_BY_``, degree ``UNSATURATION``, size ``_SIZE``), in
    which case it is listed with status ``derived`` and its family. Scale:
    every kept value is exported as ``log2(x + floor)``, the floor of a
    metabolite being its 5 % quantile over the exported participants
    (linear interpolation), computed without sex, stage or a covariate and
    recorded per feature. Nothing is imputed, replaced, winsorized or
    removed; nothing is centred per run or phase. Covariates are copied,
    not applied: adjustment is MOTCO's. Sex and stage are read only to
    write ``metadata.csv`` and to count cells; ``phase`` only to write
    ``covariates.csv`` and to describe the p180 run offset, which the
    manifest records and the step does not correct.

    Stops, before anything is written, naming the file, column or platform
    and a count, never a participant: an absent input or manifest, a hash
    that differs from its manifest, a chain mismatch, an absent column, a
    duplicated ``rid``, a ``sex`` outside ``GROUP_VALUES``, a ``stage``
    outside ``STAGE_LABELS``, a missing covariate value, a cohort
    participant absent from a cleaned table, a missing cleaned cell, a
    non-positive floor, a non-finite exported cell, and an existing output
    directory without ``force``.

    Output contract: ``p180.csv`` and ``nmr.csv`` (first column ``rid``,
    then the kept metabolites under their cleaned names in cleaned-column
    order, on the rule's scale), ``metadata.csv`` (``rid``, ``sex``,
    ``stage``) and ``covariates.csv`` (``rid``, then
    ``EXPORT_COVARIATE_COLUMNS`` copied from ``cohort.csv`` unchanged), all
    with the same ``rid`` column in the same order, participant-level and
    gitignored; ``features_p180.csv`` and ``features_nmr.csv`` (one row per
    cleaned column: family, status, zero cells, median, floor, floor over
    median, skew raw and transformed, largest |z| transformed, phase ``d``;
    the transformed-scale columns empty for derived rows; aggregate per
    feature, gitignored with the other CSVs, regenerable); and
    ``manifest.json`` (versions, git revision, the inputs with their hashes
    and the chain check, the rule as applied, block order and columns,
    group and stage values, the covariate codings copied from the cohort
    manifest, ``covariates_applied`` false, the counts: participants, sex ×
    stage, features per status and family, zero cells, floors not
    positive, non-finite cells, missing covariate values, block shares, and
    per block the distribution-shape counts, the spectrum and the phase
    offset; expected and observed counts with deviations, output hashes,
    findings; aggregate, no participant identifier, the only committed
    file). Observed counts are compared with
    ``constants.EXPORT_EXPECTED_COUNTS``; each deviation is a finding,
    printed and recorded, and never stops the step. The directory is
    written as ``motco_input.tmp/`` and renamed when complete. Reruns on
    the same inputs are byte-identical.
    """
    cleaned = Path(cleaned_dir) if cleaned_dir is not None else Path(CLEANED_DIR)
    cohort_path = Path(cohort_dir) if cohort_dir is not None else Path(COHORT_DIR)
    final = Path(out_dir) if out_dir is not None else Path(MOTCO_INPUT_DIR)
    if final.exists() and not force:
        raise FileExistsError(f"{final} exists; pass --force to replace it")
    rule = EXPORT_FEATURE_RULE
    scale = rule["scale"]
    findings: list[str] = []

    # --- inputs: the clean outputs, the cohort output and the chain ---------
    clean_inputs = _check_clean_outputs(cleaned, platforms=EXPORT_BLOCKS, runs=False)
    cohort_manifest, cohort_inputs, chain = _check_cohort_outputs(cohort_path, clean_inputs)
    for platform, entry in clean_inputs.items():
        for name, rec in entry["outputs"].items():
            print(f"[export] clean {platform}/{name}: sha256 {rec['sha256'][:16]}… equals {entry['manifest']['name']}")
    print(
        f"[export] cohort {COHORT_TABLE}: sha256 {cohort_inputs['outputs'][COHORT_TABLE]['sha256'][:16]}… equals "
        f"{COHORT_MANIFEST}; its recorded clean hashes equal the clean manifests' ({len(chain)} file(s))"
    )
    try:
        covariate_codings = cohort_manifest["settings"]["ANALYSIS_COVARIATES"]
    except KeyError:
        raise RuntimeError(f"{COHORT_MANIFEST} records no ANALYSIS_COVARIATES under settings; rerun cohort") from None
    if covariate_codings != json.loads(json.dumps(ANALYSIS_COVARIATES)):
        findings.append(
            f"{COHORT_MANIFEST} records ANALYSIS_COVARIATES that differ from constants.ANALYSIS_COVARIATES; "
            "the export copies the cohort's codings"
        )

    # --- the exported participants: every platform flag, cohort order -------
    cohort = pd.read_csv(cohort_path / COHORT_TABLE)
    required = [SAMPLE_COLUMN, GROUP_COLUMN, STAGE_COLUMN, *EXPORT_COVARIATE_COLUMNS, *EXPORT_BLOCKS]
    absent = [c for c in required if c not in cohort.columns]
    if absent:
        raise ValueError(f"{COHORT_TABLE}: column(s) absent: {', '.join(repr(c) for c in absent)}")
    both = cohort[cohort[list(EXPORT_BLOCKS)].astype(bool).all(axis=1)].reset_index(drop=True)
    problems = []
    n_dup = int(both[SAMPLE_COLUMN].duplicated().sum())
    if n_dup:
        problems.append(f"{SAMPLE_COLUMN}: {n_dup} duplicated value(s)")
    outside = ~both[GROUP_COLUMN].isin(GROUP_VALUES)
    if outside.any():
        problems.append(f"{GROUP_COLUMN}: values outside GROUP_VALUES: " + _value_counts_text(both.loc[outside, GROUP_COLUMN]))
    outside = ~both[STAGE_COLUMN].isin(STAGE_LABELS)
    if outside.any():
        problems.append(f"{STAGE_COLUMN}: values outside STAGE_LABELS: " + _value_counts_text(both.loc[outside, STAGE_COLUMN]))
    for name, n_missing in both[list(EXPORT_COVARIATE_COLUMNS)].isna().sum().items():
        if n_missing:
            problems.append(f"{name}: {int(n_missing)} missing value(s); nothing is imputed")
    if problems:
        raise ValueError(f"export stops before writing anything ({COHORT_TABLE}, rows with every platform flag): " + "; ".join(problems))
    rids = both[SAMPLE_COLUMN].to_numpy()
    sex_stage = _sex_stage(both)
    cells = "; ".join(
        f"{sex_} {'/'.join(STAGE_LABELS)} " + "/".join(str(n) for n in sex_stage[sex_].values()) for sex_ in GROUP_VALUES
    )
    print(f"[export] participants: {len(both)} of the {len(cohort)} rows of {COHORT_TABLE} carry every platform flag ({cells})")

    # --- the cleaned tables aligned to the participants ----------------------
    blocks: dict[str, pd.DataFrame] = {}
    for platform in EXPORT_BLOCKS:
        name = CLEAN_TABLES[platform]
        table = pd.read_csv(cleaned / platform / name, index_col=PARTICIPANT_ID_COLUMN)
        n_dup = int(table.index.duplicated().sum())
        if n_dup:
            raise RuntimeError(f"{platform}/{name}: {n_dup} duplicated participant(s)")
        n_absent = int((~pd.Index(rids).isin(table.index)).sum())
        if n_absent:
            raise RuntimeError(
                f"{platform}: {n_absent} cohort participant(s) absent from {name}; the cohort was built from "
                "another clean output, rerun cohort"
            )
        blocks[platform] = table.loc[rids]
        print(f"[export] {platform}/{name}: {table.shape[0]} × {table.shape[1]} cleaned → {len(rids)} × {table.shape[1]} exported participants")

    # --- membership by family, the floor and the scale ------------------------
    phase_levels = tuple(ANALYSIS_COVARIATES["phase"]["levels"])
    phase = both["phase"].to_numpy()  # read only to describe the run offset
    exported: dict[str, pd.DataFrame] = {}
    feature_tables: dict[str, pd.DataFrame] = {}
    counts: dict = {
        "participants": len(both),
        "sex_stage": sex_stage,
        "features": {},
        "zero_cells": {},
        "metabolites_with_zeros": {},
        "floors_not_positive": {},
        "non_finite": {},
        "missing_covariate_values": int(both[list(EXPORT_COVARIATE_COLUMNS)].isna().sum().sum()),
        "block_shares": {},
        "joint_features": 0,
        "shape": {},
        "spectrum": {},
        "phase_offset": {},
    }
    for platform in EXPORT_BLOCKS:
        table = blocks[platform]
        name = CLEAN_TABLES[platform]
        derived_marks = rule["membership"][platform]["derived"]
        families = {c: _feature_family(str(c), derived_marks) for c in table.columns}
        kept = [c for c in table.columns if families[c] is None]
        kept_pos = {c: j for j, c in enumerate(kept)}
        counts["features"][platform] = {
            "cleaned": int(table.shape[1]),
            "kept": len(kept),
            "derived": {fam: sum(1 for f in families.values() if f == fam) for fam in _DERIVED_FAMILIES},
        }
        X = table.to_numpy(dtype=float)
        n_missing = int(np.isnan(X).sum())
        if n_missing:
            raise RuntimeError(f"{platform}/{name}: {n_missing} missing cell(s) among the exported participants")
        Xk = table[kept].to_numpy(dtype=float)
        floor = np.quantile(Xk, scale["floor_quantile"], axis=0, method=scale["floor_method"])
        counts["floors_not_positive"][platform] = n_bad = int((~(floor > 0)).sum())
        if n_bad:
            raise RuntimeError(
                f"{platform}: {n_bad} kept metabolite(s) with a non-positive floor ({scale['floor_quantile']:.0%} "
                "quantile over the exported participants); the rule needs a proposal, not a patch"
            )
        T = np.log2(Xk + floor)
        counts["non_finite"][platform] = n_bad = int((~np.isfinite(T)).sum())
        if n_bad:
            raise RuntimeError(f"{platform}: {n_bad} non-finite cell(s) after {scale['transform']}")
        zeros = (X == 0).sum(axis=0)
        zeros_kept = (Xk == 0).sum(axis=0)
        counts["zero_cells"][platform] = int(zeros_kept.sum())
        counts["metabolites_with_zeros"][platform] = int((zeros_kept > 0).sum())
        median = np.median(X, axis=0)
        skew_raw = pd.DataFrame(X).skew().to_numpy()
        Tdf = pd.DataFrame(T)
        skew_t = Tdf.skew().to_numpy()
        max_abs_z = ((Tdf - Tdf.mean()) / Tdf.std(ddof=0)).abs().max().to_numpy()
        d, offset = _phase_offset(T, phase, phase_levels)
        rows = []
        for i, c in enumerate(table.columns):
            fam = families[c]
            row = {
                "feature": c,
                "family": fam or _KEPT_FAMILY,
                "status": "derived" if fam else "kept",
                "zero_cells": int(zeros[i]),
                "median": median[i],
                "skew_raw": skew_raw[i],
            }
            if fam is None:
                j = kept_pos[c]
                row.update(
                    floor=floor[j],
                    floor_over_median=floor[j] / median[i],
                    skew_transformed=skew_t[j],
                    max_abs_z_transformed=max_abs_z[j],
                    phase_d=d[j],
                )
            rows.append(row)
        feature_tables[platform] = pd.DataFrame(rows, columns=list(_FEATURE_COLUMNS))
        block = pd.DataFrame(T, columns=kept)
        block.insert(0, SAMPLE_COLUMN, rids)
        exported[platform] = block
        counts["shape"][platform] = _shape_counts(T)
        counts["spectrum"][platform] = _spectrum(T)
        counts["phase_offset"][platform] = offset
        derived_text = ", ".join(f"{fam} {n}" for fam, n in counts["features"][platform]["derived"].items() if n)
        print(
            f"[export] {platform}: {len(kept)} of {table.shape[1]} cleaned column(s) kept"
            + (f" ({derived_text} derived)" if derived_text else "")
            + f"; zero cells {counts['zero_cells'][platform]} in {counts['metabolites_with_zeros'][platform]} metabolite(s); "
            f"{scale['transform']} with floor at the {scale['floor_quantile']:.0%} quantile; "
            f"phase |d| > 1 for {offset['abs_d_gt_1']} metabolite(s), median |d| {offset['median_abs_d']:.2f}"
        )
    total = sum(counts["features"][p]["kept"] for p in EXPORT_BLOCKS)
    counts["joint_features"] = total
    counts["block_shares"] = {p: counts["features"][p]["kept"] / total for p in EXPORT_BLOCKS}

    # --- the predeclared counts ------------------------------------------------
    expected = json.loads(json.dumps(EXPORT_EXPECTED_COUNTS))
    observed = _project(json.loads(json.dumps(counts, default=_json_default)), expected)
    deviations = [msg for key in expected for msg in _count_deviations(expected[key], observed.get(key), key)]
    findings += deviations

    manifest = {
        "step": "export",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": _software_versions(),
        "git_revision": _git_revision(),
        "inputs": {"clean": clean_inputs, "cohort": cohort_inputs, "chain": chain},
        "settings": {
            "EXPORT_FEATURE_RULE": rule,
            "blocks": EXPORT_BLOCKS,
            "block_columns": {p: [str(c) for c in exported[p].columns if c != SAMPLE_COLUMN] for p in EXPORT_BLOCKS},
            "sample_column": SAMPLE_COLUMN,
            "group_column": GROUP_COLUMN,
            "group_values": GROUP_VALUES,
            "stage_column": STAGE_COLUMN,
            "stage_order": STAGE_LABELS,
            "covariate_columns": EXPORT_COVARIATE_COLUMNS,
            "covariates": covariate_codings,
            "covariates_applied": False,
            "motco_transform": scale["motco_transform"],
            "units": scale["transform"],
        },
        "counts": counts,
        "expected": expected,
        "deviations": deviations,
        "findings": findings,
    }

    # --- outputs -------------------------------------------------------------------
    names = [f"{p}.csv" for p in EXPORT_BLOCKS] + [EXPORT_METADATA, EXPORT_COVARIATES]
    with _finalize_output_dir(final, force=force) as tmp:
        for platform in EXPORT_BLOCKS:
            exported[platform].to_csv(tmp / f"{platform}.csv", index=False)
        both[[SAMPLE_COLUMN, GROUP_COLUMN, STAGE_COLUMN]].to_csv(tmp / EXPORT_METADATA, index=False)
        both[[SAMPLE_COLUMN, *EXPORT_COVARIATE_COLUMNS]].to_csv(tmp / EXPORT_COVARIATES, index=False)
        for platform in EXPORT_BLOCKS:
            feature_name = EXPORT_FEATURES.format(platform=platform)
            feature_tables[platform].to_csv(tmp / feature_name, index=False)
            names.append(feature_name)
        manifest["outputs"] = {
            name: {
                "sha256": _sha256_file(tmp / name),
                "bytes": (tmp / name).stat().st_size,
                "participant_level": not name.startswith("features_"),
            }
            for name in names
        }
        _write_manifest(tmp / EXPORT_MANIFEST, manifest)

    shapes = {p: (len(rids), counts["features"][p]["kept"]) for p in EXPORT_BLOCKS}
    print(
        f"[export] wrote {final}/ ("
        + ", ".join(f"{p}.csv {n} × {m}" for p, (n, m) in shapes.items())
        + f", {EXPORT_METADATA}, {EXPORT_COVARIATES}, "
        + ", ".join(EXPORT_FEATURES.format(platform=p) for p in EXPORT_BLOCKS)
        + f", {EXPORT_MANIFEST})"
    )
    if deviations:
        print(f"[export] {len(deviations)} count deviation(s) from the predeclared counts")
    else:
        print("[export] counts reproduce the predeclared ones")
    for msg in findings:
        print(f"[export] FINDING: {msg}")
    return {"dir": final, "blocks": shapes, "manifest": manifest, "findings": findings}


# --- analyze ------------------------------------------------------------------

#: MOTCO settings the proposal of ``adni-analyze`` states as not overridden.
#: The record's ``params`` are compared with these; a difference is a finding
#: (a moved MOTCO default), never a silent change of the primary.
_MOTCO_DEFAULTS_STATED: dict = {
    "orientation_estimator": "net_displacement",
    "forced_components": None,
    "cv1_splits": 3,
    "cv2_splits": 4,
    "n_repeats": 5,
    "max_components": 20,
    "random_state": 1203,
}
#: The CV settings MOTCO may clamp to the design (``latent.integration_params``
#: against ``params``); a clamped value is a finding.
_MOTCO_CV_KEYS = ("cv1_splits", "cv2_splits", "n_repeats", "max_components", "random_state")


def check_motco_version() -> str:
    """Return the installed MOTCO version after checking the minimum.

    Returns
    -------
    str
        The installed version (``motco.__version__``), at least
        ``constants.ANALYSIS_MOTCO_MIN_VERSION``.

    Raises
    ------
    RuntimeError
        The installed MOTCO is older than the minimum; the message names
        both versions. Called before any input is read, so nothing is read
        or written.
    """
    import motco

    installed = str(motco.__version__)
    required = ANALYSIS_MOTCO_MIN_VERSION
    try:
        from packaging.version import Version

        too_old = Version(installed) < Version(required)
    except ImportError:  # pragma: no cover - packaging is in the lock

        def key(v: str) -> tuple[int, ...]:
            return tuple(int(part) for part in re.findall(r"\d+", v)[:3])

        too_old = key(installed) < key(required)
    if too_old:
        raise RuntimeError(
            f"MOTCO {installed} is installed but analyze needs MOTCO >= {required} (the release with the "
            "validated rank floor; AGENTS.md constraint 4); run `uv sync --locked`; nothing was read or written"
        )
    return installed


def check_motco_rank_floor() -> int:
    """Return ``ANALYSIS_RANK_FLOOR`` after checking it equals MOTCO's default.

    Returns
    -------
    int
        ``constants.ANALYSIS_RANK_FLOOR``.

    Raises
    ------
    RuntimeError
        MOTCO's default rank floor (``TrajectoryAnalysisParams().min_components``;
        MOTCO holds a floor of 1 as ``None``) differs from
        ``ANALYSIS_RANK_FLOOR``; the message names both values. The floor is
        MOTCO's validated default, passed explicitly, so a MOTCO whose default
        moved stops the run instead of changing the primary. Called before any
        input is read.
    """
    from motco.analysis import TrajectoryAnalysisParams

    default = TrajectoryAnalysisParams().min_components
    default = 1 if default is None else int(default)
    if default != ANALYSIS_RANK_FLOOR:
        raise RuntimeError(
            f"MOTCO's default rank floor (TrajectoryAnalysisParams().min_components) is {default} but "
            f"ANALYSIS_RANK_FLOOR is {ANALYSIS_RANK_FLOOR}; the floor is MOTCO's validated default, so a change "
            "of either is a proposal, not a run; nothing was read or written"
        )
    return ANALYSIS_RANK_FLOOR


def _load_analysis_inputs(input_dir: Path) -> dict:
    """Read the export outputs, check them against the export manifest and build the model's metadata table.

    Returns ``blocks`` (platform → participants × features, indexed by
    ``rid``, read as ``motco analyze --block`` reads a block), ``metadata``
    (``rid``, ``sex``, ``stage``, then ``ANALYSIS_COVARIATES``, one row per
    exported participant in export order), ``export_manifest``, ``inputs``
    (file → observed sha256 and bytes, with the recorded hash for the CSVs)
    and ``findings``. Stops, before anything is written, naming the file or
    column and a count, never a participant: an absent export directory or
    file, a CSV whose sha256 differs from the one the export manifest
    records, a column set that differs from the contract, tables whose
    ``rid`` columns differ or are in another order, a duplicated ``rid``, a
    ``sex`` outside ``GROUP_VALUES``, a ``stage`` outside ``STAGE_LABELS``, a
    categorical covariate outside its levels, a non-finite numeric covariate,
    a missing covariate value, a non-numeric or non-finite block cell.
    """
    if not input_dir.is_dir():
        raise FileNotFoundError(f"{input_dir} does not exist; run `adni-sexdiff export` first")
    absent = [n for n in ANALYSIS_INPUT_FILES if not (input_dir / n).is_file()]
    if absent:
        raise FileNotFoundError(
            f"{len(absent)} export file(s) absent from {input_dir}: " + ", ".join(repr(n) for n in absent)
            + "; run `adni-sexdiff export` first"
        )
    manifest = json.loads((input_dir / EXPORT_MANIFEST).read_text())
    recorded = manifest.get("outputs", {})
    inputs: dict[str, dict] = {}
    for name in ANALYSIS_INPUT_FILES:
        path = input_dir / name
        sha = _sha256_file(path)
        entry: dict = {"sha256": sha, "bytes": path.stat().st_size}
        if name != EXPORT_MANIFEST:
            rec = recorded.get(name, {}).get("sha256")
            if rec is None:
                raise RuntimeError(f"{name}: {EXPORT_MANIFEST} records no hash for it; rerun export")
            if sha != rec:
                raise RuntimeError(
                    f"{name}: sha256 {sha} differs from the hash {EXPORT_MANIFEST} records ({rec}); "
                    "the export changed after export, rerun export"
                )
            entry.update(recorded=rec, equals_export_manifest=True)
        inputs[name] = entry
    findings: list[str] = []
    settings = manifest.get("settings", {})
    codings = settings.get("covariates")
    if not isinstance(codings, dict):
        raise RuntimeError(f"{EXPORT_MANIFEST} records no covariate codings under settings.covariates; rerun export")
    if codings != json.loads(json.dumps(ANALYSIS_COVARIATES)):
        findings.append(
            f"{EXPORT_MANIFEST} records covariate codings that differ from constants.ANALYSIS_COVARIATES; the "
            "analysis declares the constant's codings and checks the levels the manifest records"
        )
    block_columns = settings.get("block_columns")
    if not isinstance(block_columns, dict):
        raise RuntimeError(f"{EXPORT_MANIFEST} records no block_columns under settings; rerun export")

    # Read as `motco analyze` reads `--metadata` and `--block` (pandas' default
    # parsing; the first block column is the index).
    meta = pd.read_csv(input_dir / EXPORT_METADATA)
    cov = pd.read_csv(input_dir / EXPORT_COVARIATES)
    blocks: dict[str, pd.DataFrame] = {}
    for platform in EXPORT_BLOCKS:
        blocks[platform] = pd.read_csv(input_dir / f"{platform}.csv", index_col=0)

    problems: list[str] = []
    if list(meta.columns) != [SAMPLE_COLUMN, GROUP_COLUMN, STAGE_COLUMN]:
        problems.append(
            f"{EXPORT_METADATA}: columns {list(meta.columns)} differ from [{SAMPLE_COLUMN}, {GROUP_COLUMN}, {STAGE_COLUMN}]"
        )
    if list(cov.columns) != [SAMPLE_COLUMN, *ANALYSIS_COVARIATES]:
        problems.append(
            f"{EXPORT_COVARIATES}: columns {list(cov.columns)} differ from [{SAMPLE_COLUMN}, "
            + ", ".join(ANALYSIS_COVARIATES) + "] (ANALYSIS_COVARIATES)"
        )
    for platform, table in blocks.items():
        name = f"{platform}.csv"
        if table.index.name != SAMPLE_COLUMN:
            problems.append(f"{name}: first column is {table.index.name!r}, not {SAMPLE_COLUMN!r}")
        expected_cols = block_columns.get(platform)
        if expected_cols is None:
            problems.append(f"{name}: {EXPORT_MANIFEST} records no block_columns for {platform}")
        elif [str(c) for c in table.columns] != [str(c) for c in expected_cols]:
            problems.append(
                f"{name}: {table.shape[1]} column(s) differ from the {len(expected_cols)} block_columns "
                f"{EXPORT_MANIFEST} records for {platform}"
            )
    if problems:
        raise ValueError("analyze stops before writing anything: " + "; ".join(problems))

    ids = {
        EXPORT_METADATA: meta[SAMPLE_COLUMN].tolist(),
        EXPORT_COVARIATES: cov[SAMPLE_COLUMN].tolist(),
        **{f"{p}.csv": t.index.tolist() for p, t in blocks.items()},
    }
    for name, values in ids.items():
        n_dup = len(values) - len(set(values))
        if n_dup:
            problems.append(f"{name}: {n_dup} duplicated {SAMPLE_COLUMN} value(s)")
    if problems:
        raise ValueError("analyze stops before writing anything: " + "; ".join(problems))
    reference = ids[EXPORT_METADATA]
    reference_set = set(reference)
    for name, values in ids.items():
        if name == EXPORT_METADATA or values == reference:
            continue
        only_reference = len(reference_set - set(values))
        only_other = len(set(values) - reference_set)
        if only_reference or only_other:
            problems.append(
                f"{EXPORT_METADATA} and {name} list different participants ({only_reference} only in "
                f"{EXPORT_METADATA}, {only_other} only in {name})"
            )
        else:
            problems.append(f"{EXPORT_METADATA} and {name} list the same participants in a different order")
    if problems:
        raise ValueError("analyze stops before writing anything: " + "; ".join(problems))

    for column, allowed in ((GROUP_COLUMN, GROUP_VALUES), (STAGE_COLUMN, STAGE_LABELS)):
        outside = ~meta[column].isin(allowed)
        if outside.any():
            problems.append(
                f"{EXPORT_METADATA} {column}: {int(outside.sum())} value(s) outside {list(allowed)}: "
                + _value_counts_text(meta.loc[outside, column])
            )
    for name, spec in ANALYSIS_COVARIATES.items():
        n_missing = int(cov[name].isna().sum())
        if n_missing:
            problems.append(
                f"{EXPORT_COVARIATES} {name}: {n_missing} missing value(s); nothing is imputed "
                f"(missing policy {ANALYSIS_MISSING_COVARIATES!r})"
            )
            continue
        if spec["coding"] == "categorical":
            levels = [str(level) for level in codings.get(name, spec).get("levels", spec["levels"])]
            outside = ~cov[name].astype(str).isin(levels)
            if outside.any():
                problems.append(f"{EXPORT_COVARIATES} {name}: {int(outside.sum())} value(s) outside its levels {levels}")
        else:
            numeric = pd.to_numeric(cov[name], errors="coerce")
            n_bad = int((~np.isfinite(numeric.to_numpy(dtype=float))).sum())
            if n_bad:
                problems.append(f"{EXPORT_COVARIATES} {name}: {n_bad} non-numeric or non-finite value(s)")
    for platform, table in blocks.items():
        try:
            matrix = table.to_numpy(dtype=float)
        except (TypeError, ValueError):
            problems.append(f"{platform}.csv: non-numeric cell(s)")
            continue
        n_bad = int((~np.isfinite(matrix)).sum())
        if n_bad:
            problems.append(f"{platform}.csv: {n_bad} missing or non-finite cell(s); nothing is imputed")
    if problems:
        raise ValueError("analyze stops before writing anything: " + "; ".join(problems))

    merged = meta.merge(cov, on=SAMPLE_COLUMN, how="inner", validate="one_to_one")
    merged = merged[[SAMPLE_COLUMN, GROUP_COLUMN, STAGE_COLUMN, *ANALYSIS_COVARIATES]]
    return {"blocks": blocks, "metadata": merged, "export_manifest": manifest, "inputs": inputs, "findings": findings}


def _rejected(p: float | None, alpha: float = ANALYSIS_ALPHA) -> bool | None:
    """``ANALYSIS_REJECTION_RULE`` (``p <= alpha``); ``None`` when there is no p-value."""
    return None if p is None else bool(p <= alpha)


def _fmt(value, spec: str = ".6g") -> str:
    """Format a number for ``summary.md`` (six significant digits); ``n/a`` for ``None``."""
    return "n/a" if value is None else format(value, spec)


def _analysis_cli_equivalent(input_dir: Path, metadata_path: Path, params, n_jobs: int) -> dict:
    """The ``motco analyze`` command that reproduces the analysis directory from its inputs.

    Covariate flags are emitted in ``ANALYSIS_COVARIATES`` order, ``--covariate``
    for a numeric covariate and ``--categorical-covariate`` for a categorical
    one (MOTCO's CLI keeps the declaration order across both flags). Only the
    settings the step passes appear; the rest are MOTCO's defaults.
    """
    import shlex

    argv = ["motco", "analyze"]
    for platform in EXPORT_BLOCKS:
        argv += ["--block", f"{platform}={input_dir / f'{platform}.csv'}"]
    argv += [
        "--metadata", str(metadata_path),
        "--sample-col", SAMPLE_COLUMN, "--group-col", GROUP_COLUMN, "--stage-col", STAGE_COLUMN,
        "--stage-order", ",".join(STAGE_LABELS), "--group-order", ",".join(GROUP_VALUES),
    ]
    for name in ANALYSIS_COVARIATES:
        argv += ["--categorical-covariate" if name in ANALYSIS_CATEGORICAL_COVARIATES else "--covariate", name]
    argv += ["--missing-covariates", ANALYSIS_MISSING_COVARIATES]
    if params.covariate_latent_adjustment is not None:
        argv += ["--latent-adjustment", params.covariate_latent_adjustment]
    argv += [
        "--permutations", str(params.permutations), "--seed", str(params.seed), "--n-jobs", str(n_jobs),
        "--min-components", str(params.resolved_min_components), "--out-dir", "OUT_DIR",
    ]
    return {
        "command": shlex.join(argv),
        "argv": argv,
        "note": "replace OUT_DIR with a new directory; paths are relative to the directory analyze ran in",
    }


def render_analysis_summary(
    record: dict,
    *,
    export_manifest: dict,
    n_jobs: int,
    alpha: float = ANALYSIS_ALPHA,
    rank_floor: int = ANALYSIS_RANK_FLOOR,
) -> str:
    """Render ``summary.md`` from a MOTCO analysis record (``result.json``).

    Parameters
    ----------
    record:
        The parsed ``result.json``.
    export_manifest:
        The export manifest, for the export context (block shares, the
        phase offset per block, the feature rule).
    n_jobs:
        The run's ``n_jobs``, shown in the header.
    alpha, rank_floor:
        ``ANALYSIS_ALPHA`` and ``ANALYSIS_RANK_FLOOR``.

    Returns
    -------
    str
        Markdown: the header, the statistics table (observed, p, rejected
        under ``ANALYSIS_REJECTION_RULE``, null mean, sd and q95; the
        ``angle`` row with the CV-selected rank, the floor, the pooled
        eigengap and a note when the floor binds), the reading of each
        statistic's status, the cell sizes, the latent block, the covariate
        block with the reference-row table, the export context and
        ``READING_RULES`` verbatim. Numbers carry six significant digits.
    """
    design, meas, latent = record["design"], record["measurement"], record["latent"]
    stages, groups = design["stage_levels"], design["group_levels"]
    selected = latent["selected_lv"]
    floor_binding = latent["component_selection"] == "cv" and selected == rank_floor
    eigengap = (record.get("config_spectrum", {}).get("pooled") or {}).get("relative_eigengap")
    blocks_text = ", ".join(f"{b['name']} ({b['n_features']} features, {b['transform']})" for b in record["blocks"])
    lines = [
        "# MOTCO trajectory analysis: ADNI serum metabolomics, sex × stage",
        "",
        f"MOTCO {record['software']['motco']}; n = {design['n_samples']}; groups {' vs '.join(groups)} "
        f"(`{design['group_col']}`); stages {' → '.join(stages)} (`{design['stage_col']}`); blocks {blocks_text}; "
        f"orientation `{meas['orientation_estimator']}`; {meas['permutations']} RRPP permutations, seed "
        f"{meas['seed']}; α = {alpha}, rejected when {ANALYSIS_REJECTION_RULE} (`ANALYSIS_REJECTION_RULE`); "
        f"n_jobs {n_jobs}"
        + ("" if n_jobs == REPORTED_N_JOBS else f" (not a reported run: reported runs use n_jobs = {REPORTED_N_JOBS})")
        + "; latent adjustment: none (the primary; the `stage`-conditioned arm is the predeclared sensitivity "
        f"of `{ANALYSIS_PREDECLARED_LATENT_SENSITIVITY['change']}`).",
        "",
        "## Statistics",
        "",
        "| statistic | observed | p (RRPP) | rejected | null mean | null sd | null q95 | note |",
        "|---|---:|---:|:---:|---:|---:|---:|---|",
    ]
    status: dict[str, bool | None] = {}
    for s in ANALYSIS_STATISTICS:
        p = record["p_values"].get(s)
        null = record["null_summary"].get(s, {})
        status[s] = _rejected(p, alpha)
        rejected = "n/a" if status[s] is None else ("yes" if status[s] else "no")
        note = ""
        if s == "angle":
            note = (
                f"degrees, endpoint stages {stages[0]} and {stages[-1]}; CV-selected rank {selected} "
                f"(rank floor {rank_floor}); pooled relative eigengap {_fmt(eigengap)}"
            )
            if floor_binding:
                note += "; the floor is binding: the CV selected the floor rank"
        elif s == "shape":
            note = "not available at fewer than three stages" if not meas.get("shape_available", True) else ""
        lines.append(
            f"| {s} | {_fmt(record['statistics'].get(s))} | {_fmt(p)} | {rejected} | "
            f"{_fmt(null.get('mean'))} | {_fmt(null.get('sd'))} | {_fmt(null.get('q95'))} | {note} |"
        )
    readings = {
        "delta": (
            "`delta` is rejected: evidence that the sexes' trajectories differ, not specifically that they "
            "differ in size (reading rule 4).",
            "`delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design.",
        ),
        "angle": (
            f"`angle` is rejected: evidence that the sexes' net displacements ({stages[0]} to {stages[-1]}) differ "
            "in orientation, with Type I controlled at the validated designs (reading rule 3).",
            "`angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions "
            "agree (reading rule 3: no power statement exists at this design).",
        ),
        "shape": (
            "`shape` is rejected: evidence that the sexes' trajectories differ in shape, with Type I controlled "
            "at the validated designs (reading rule 3).",
            "`shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes "
            "agree (reading rule 3: no power statement exists at this design).",
        ),
    }
    lines += ["", "Reading, under the rules below:", ""]
    for s in ANALYSIS_STATISTICS:
        if status[s] is None:
            lines.append(f"- `{s}`: no p-value in the record.")
        else:
            lines.append("- " + readings[s][0 if status[s] else 1])
    lines += [
        "",
        "## Cell sizes",
        "",
        "| group | " + " | ".join(f"stage {s}" for s in stages) + " | total |",
        "|---|" + "---:|" * (len(stages) + 1),
    ]
    for g in groups:
        cells = design["cell_sizes"][g]
        lines.append(f"| {g} | " + " | ".join(str(cells[s]) for s in stages) + f" | {sum(cells.values())} |")
    cv = latent.get("integration_params", {})
    permuted = record.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {}
    lines += [
        "",
        "## Latent space",
        "",
        f"- PLS-DA rank: {selected} (`{latent['component_selection']}`); rank floor {rank_floor}"
        + ("; the floor is binding: the CV selected the floor rank" if floor_binding else ""),
        f"- pooled relative eigengap of the stage-mean configuration: {_fmt(eigengap)}"
        + (
            f" (permutation null q05 / q50 / q95: {_fmt(permuted.get('q05'))} / {_fmt(permuted.get('q50'))} / "
            f"{_fmt(permuted.get('q95'))})"
            if permuted else ""
        ),
        f"- cv_mean_auroc: {_fmt(latent.get('cv_mean_auroc'))}",
        f"- CV: cv2_splits {cv.get('cv2_splits')}, cv1_splits {cv.get('cv1_splits')}, n_repeats {cv.get('n_repeats')} "
        f"({latent.get('cv_repeats_completed')} completed), max_components {cv.get('max_components')}, "
        f"rank floor {cv.get('min_components', 1)}, random_state {cv.get('random_state')}",
        f"- blocks: {blocks_text}; features are z-scored by MOTCO (pooled per-feature scalers)",
    ]
    cov = record.get("covariates")
    lines += ["", "## Covariates", ""]
    if cov is None:
        lines.append("None entered.")
    else:
        lines += [
            "- entered (in order, additively): " + ", ".join(f"`{c}` ({cov['kinds'][c]})" for c in cov["columns"]),
            f"- design columns: {len(cov['design_columns'])} (" + ", ".join(cov["design_columns"]) + ")",
            "- reference levels: " + ", ".join(f"`{c}` {lvl}" for c, lvl in cov["reference_levels"].items()),
            f"- missing policy: `{cov['missing_policy']}`; dropped participants: {cov['n_dropped']}",
            f"- LS-means evaluated at the reference row (`{cov['lsmean_reference']}`); no sex × covariate or "
            "stage × covariate term:",
            "",
            "| design column | reference value |",
            "|---|---:|",
        ]
        lines += [f"| {c} | {_fmt(v)} |" for c, v in cov["reference_row"].items()]
    counts = export_manifest.get("counts", {})
    settings = export_manifest.get("settings", {})
    features = counts.get("features", {})
    shares = counts.get("block_shares", {})
    offsets = counts.get("phase_offset", {})
    lines += [
        "",
        "## Export context",
        "",
        f"- feature rule (`EXPORT_FEATURE_RULE`): units `{settings.get('units')}`, MOTCO transform "
        f"`{settings.get('motco_transform')}`; kept / cleaned columns: "
        + ", ".join(f"{p} {features.get(p, {}).get('kept')} / {features.get(p, {}).get('cleaned')}" for p in EXPORT_BLOCKS)
        + f"; joint features {counts.get('joint_features')}",
        "- block shares (unweighted in MOTCO): " + ", ".join(f"{p} {_fmt(shares.get(p), '.3f')}" for p in EXPORT_BLOCKS),
        "- p180 run offset (`phase`, ADNI1 against ADNI2GO, recorded by export and not corrected): "
        + "; ".join(
            f"{p} median |d| {_fmt(offsets.get(p, {}).get('median_abs_d'), '.2f')}, |d| > 1 for "
            f"{offsets.get(p, {}).get('abs_d_gt_1')} metabolite(s), |corr(PC1, phase)| "
            f"{_fmt(offsets.get(p, {}).get('abs_corr_pc1_phase'), '.2f')}"
            for p in EXPORT_BLOCKS
        ),
        "- `phase` enters as a covariate of the stage means (above); the `stage`-conditioned latent adjustment "
        f"is the predeclared sensitivity arm of `{ANALYSIS_PREDECLARED_LATENT_SENSITIVITY['change']}`",
        "",
        "## Reading rules",
        "",
        "Binding for every reader of this result (`READING_RULES`, written before the first run):",
        "",
    ]
    lines += [f"{i}. {rule}" for i, rule in enumerate(READING_RULES, 1)]
    return "\n".join(lines) + "\n"


def run_analysis(
    *,
    input_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    n_jobs: int = REPORTED_N_JOBS,
    force: bool = False,
) -> dict:
    """Run the covariate-adjusted MOTCO sex × stage trajectory comparison.

    Parameters
    ----------
    input_dir:
        Output directory of ``export`` (default ``constants.MOTCO_INPUT_DIR``).
        Read: ``p180.csv``, ``nmr.csv``, ``metadata.csv``, ``covariates.csv``
        (each checked against the sha256 ``manifest.json`` records) and
        ``manifest.json`` (block columns, covariate codings, counts). No
        data-root file, no cohort file, no cleaned table.
    out_dir:
        Analysis directory (default ``constants.MOTCO_ANALYSIS_DIR``).
    n_jobs:
        Parallel jobs for MOTCO's CV and RRPP. MOTCO seeds one RRPP stream
        per worker, so a value other than 1 changes the permutation draws
        (p-values, null summaries) but not the statistics, rank or latent
        space; reported runs use ``constants.REPORTED_N_JOBS`` (1) and
        another value is recorded as a finding and not reported.
    force:
        Replace an existing analysis directory (after the new one is
        complete).

    Returns
    -------
    dict
        ``{"dir": Path, "record": dict, "manifest": dict, "findings": [...]}``.

    Notes
    -----
    Gates, before any input is read: ``check_motco_version`` (MOTCO at
    least ``ANALYSIS_MOTCO_MIN_VERSION``) and ``check_motco_rank_floor``
    (MOTCO's default ``min_components`` equals ``ANALYSIS_RANK_FLOOR``);
    then an existing output directory without ``force``. The inputs are
    then checked (``_load_analysis_inputs``): the export directory and the
    five files exist, each CSV hashes to the value the export manifest
    records, the four tables carry the same ``rid`` column in the same
    order, the column sets match the contract and the manifest's
    ``block_columns``, ``sex`` is in ``GROUP_VALUES``, ``stage`` in
    ``STAGE_LABELS``, each categorical covariate within its levels, no
    covariate value or block cell missing. A failure stops the step naming
    the file or column and a count, never a participant, and nothing is
    written.

    One call of ``motco.analysis.analyze_trajectories`` (never assembled
    from ``motco plsr`` + ``motco de``) on the blocks in ``EXPORT_BLOCKS``
    order (transform ``identity``, MOTCO z-scores every feature itself),
    group ``sex`` in ``GROUP_VALUES`` order, stage ``stage`` in
    ``STAGE_LABELS`` order, the ``ANALYSIS_COVARIATES`` entered additively
    in their order with ``ANALYSIS_CATEGORICAL_COVARIATES`` declared
    categorical (drop-first indicators, the first level the reference;
    LS-means at the pooled covariate mean), missing policy
    ``ANALYSIS_MISSING_COVARIATES``, and
    ``TrajectoryAnalysisParams(permutations=ANALYSIS_PERMUTATIONS,
    seed=ANALYSIS_SEED, n_jobs=n_jobs, min_components=ANALYSIS_RANK_FLOOR,
    covariate_latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT)`` and nothing
    else: MOTCO's orientation estimator, CV settings and attribution stay
    its defaults and are read back from the record. The metadata table the
    model sees is ``analysis_metadata.csv`` parsed back as ``motco analyze
    --metadata`` parses it, so the manifest's ``cli_equivalent`` reproduces
    the run. ``phase`` enters as a covariate of the stage means; the run
    offset is not corrected, and the ``stage``-conditioned latent
    adjustment is the predeclared sensitivity arm of a following change.

    Output contract (``results/motco_analysis/``, written as
    ``motco_analysis.tmp/`` and renamed when complete): MOTCO's artifact
    from ``write_analysis_outputs`` (``result.json``, ``latent_scores.csv``,
    ``pls_loadings.csv``, ``stage_means.csv``), ``analysis_metadata.csv``
    (``rid``, ``sex``, ``stage``, the five covariates, one row per exported
    participant in export order), ``analysis_manifest.json`` (versions with
    MOTCO and scikit-learn, git revision, the inputs with observed and
    recorded hashes and the export manifest's hash and revision, every
    setting by constant name, ``n_jobs``, the blocks, the covariate block
    from the record, the MOTCO defaults used, the latent adjustment with
    the predeclared arm, ``cli_equivalent``, the counts, the predeclared
    ``ANALYSIS_EXPECTED_COUNTS`` beside them with deviations, output hashes
    with a participant-level flag, findings) and ``summary.md``
    (``render_analysis_summary``: the statistics with p-values, rejection
    under ``ANALYSIS_REJECTION_RULE`` and null summaries, the CV-selected
    rank, floor and eigengap beside ``angle``, the cell sizes, the latent
    and covariate blocks, the export context and ``READING_RULES``).
    ``latent_scores.csv`` and ``analysis_metadata.csv`` are
    participant-level and gitignored; the other five files are aggregate
    and the committed ones.

    Findings, recorded and printed, never a stop: a deviation from the
    predeclared counts; ``n_jobs`` other than 1 (the run is not reported);
    a CV-selected rank equal to the floor (the floor is binding); fewer CV
    repeats completed than requested; a non-finite statistic or p-value; a
    MOTCO default that differs from the one the proposal states; a CV
    setting MOTCO clamped; covariate codings in the export manifest that
    differ from the constant. No finding names a participant.
    """
    motco_version = check_motco_version()
    rank_floor = check_motco_rank_floor()
    from motco.analysis import (
        OmicsBlock,
        TrajectoryAnalysisParams,
        TrajectoryDataset,
        analyze_trajectories,
        write_analysis_outputs,
    )

    input_dir = Path(input_dir) if input_dir is not None else Path(MOTCO_INPUT_DIR)
    final = Path(out_dir) if out_dir is not None else Path(MOTCO_ANALYSIS_DIR)
    if final.exists() and not force:
        raise FileExistsError(f"{final} exists; pass --force to replace it")
    print(f"[analyze] MOTCO {motco_version}; rank floor {rank_floor} equals MOTCO's default")

    # --- inputs ---------------------------------------------------------------
    loaded = _load_analysis_inputs(input_dir)
    findings: list[str] = list(loaded["findings"])
    blocks, frame, export_manifest = loaded["blocks"], loaded["metadata"], loaded["export_manifest"]
    for name, rec in loaded["inputs"].items():
        print(f"[analyze] {name}: sha256 {rec['sha256'][:16]}…" + (f" equals {EXPORT_MANIFEST}" if "recorded" in rec else ""))
    sex_stage = _sex_stage(frame)
    cells = "; ".join(
        f"{sex_} {'/'.join(STAGE_LABELS)} " + "/".join(str(n) for n in sex_stage[sex_].values()) for sex_ in GROUP_VALUES
    )
    n_features = {p: int(blocks[p].shape[1]) for p in EXPORT_BLOCKS}
    print(
        f"[analyze] participants: {len(frame)} ({cells}); features "
        + " + ".join(f"{n_features[p]} {p}" for p in EXPORT_BLOCKS) + f" = {sum(n_features.values())}; covariates "
        + ", ".join(f"{c} ({ANALYSIS_COVARIATES[c]['coding']})" for c in ANALYSIS_COVARIATES)
    )

    # --- the dataset: the metadata table parsed back as `motco analyze` parses it
    metadata_csv = frame.to_csv(index=False)
    metadata = pd.read_csv(io.StringIO(metadata_csv))
    metadata[SAMPLE_COLUMN] = metadata[SAMPLE_COLUMN].astype(str)
    transform = EXPORT_FEATURE_RULE["scale"]["motco_transform"]
    motco_blocks = []
    for platform in EXPORT_BLOCKS:
        values = blocks[platform].copy()
        values.index = values.index.astype(str)
        motco_blocks.append(OmicsBlock(platform, values, transform))
    dataset = TrajectoryDataset(
        blocks=motco_blocks,
        metadata=metadata,
        sample_col=SAMPLE_COLUMN,
        group_col=GROUP_COLUMN,
        stage_col=STAGE_COLUMN,
        stage_order=STAGE_LABELS,
        group_order=GROUP_VALUES,
        covariate_cols=tuple(ANALYSIS_COVARIATES),
        categorical_covariates=ANALYSIS_CATEGORICAL_COVARIATES,
        missing_covariates=ANALYSIS_MISSING_COVARIATES,
    )
    params = TrajectoryAnalysisParams(
        permutations=ANALYSIS_PERMUTATIONS,
        seed=ANALYSIS_SEED,
        n_jobs=n_jobs,
        min_components=ANALYSIS_RANK_FLOOR,
        covariate_latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT,
    )
    design = dataset.covariate_design
    print(f"[analyze] design columns: {len(design.column_names)} (" + ", ".join(design.column_names) + ")")
    print(
        f"[analyze] CV rank selection (floor {params.resolved_min_components}) + {params.permutations} RRPP "
        f"permutations, seed {params.seed}, n_jobs {n_jobs}, latent adjustment {params.covariate_latent_adjustment}…"
    )

    # --- the one call -------------------------------------------------------------
    result = analyze_trajectories(dataset, params)
    record = result.record
    latent, meas = record["latent"], record["measurement"]
    print(
        f"[analyze] rank {latent['selected_lv']} ({latent['component_selection']}), cv_mean_auroc "
        f"{_fmt(latent.get('cv_mean_auroc'), '.4f')}, {latent.get('cv_repeats_completed')} CV repeat(s), "
        f"{meas['runtime_seconds']:.1f} s"
    )
    rejected = {s: _rejected(record["p_values"].get(s)) for s in ANALYSIS_STATISTICS}
    for s in ANALYSIS_STATISTICS:
        verdict = "no p-value" if rejected[s] is None else ("rejected" if rejected[s] else "not rejected")
        print(f"[analyze] {s}: {_fmt(record['statistics'].get(s))} (p {_fmt(record['p_values'].get(s))}, {verdict} at α = {ANALYSIS_ALPHA})")

    # --- counts, expected, findings ----------------------------------------------------
    cov_record = record["covariates"]
    counts: dict = {
        "participants": record["design"]["n_samples"],
        "sex_stage": record["design"]["cell_sizes"],
        "features": {**n_features, "joint": sum(n_features.values())},
        "design_columns": list(cov_record["design_columns"]),
        "covariate_levels": {
            name: {level: int((metadata[name].astype(str) == level).sum()) for level in cov_record["levels"][name]}
            for name in ANALYSIS_CATEGORICAL_COVARIATES
        },
        "dropped": cov_record["n_dropped"],
        "component_selection": latent["component_selection"],
        "min_components": params.resolved_min_components,
        "permutations": meas["permutations"],
        "selected_rank": latent["selected_lv"],
        "cv_mean_auroc": latent.get("cv_mean_auroc"),
        "cv_repeats_completed": latent.get("cv_repeats_completed"),
        "eigengap": (record.get("config_spectrum", {}).get("pooled") or {}).get("relative_eigengap"),
        "statistics": record["statistics"],
        "p_values": record["p_values"],
        "rejected": rejected,
        "runtime_seconds": meas["runtime_seconds"],
    }
    expected = json.loads(json.dumps(ANALYSIS_EXPECTED_COUNTS))
    observed = _project(json.loads(json.dumps(counts, default=_json_default)), expected)
    deviations = [msg for key in expected for msg in _count_deviations(expected[key], observed.get(key), key)]
    findings += deviations
    if n_jobs != REPORTED_N_JOBS:
        findings.append(
            f"n_jobs = {n_jobs}: MOTCO seeds one RRPP stream per worker, so the permutation draws, p-values and "
            f"null summaries differ from an n_jobs = {REPORTED_N_JOBS} run (statistics, rank, latent scores and "
            f"loadings do not); the run is not reported (REPORTED_N_JOBS = {REPORTED_N_JOBS})"
        )
    if latent["component_selection"] == "cv" and latent["selected_lv"] == rank_floor:
        findings.append(
            f"CV selected rank {latent['selected_lv']}, equal to the rank floor ANALYSIS_RANK_FLOOR = {rank_floor}: "
            "the floor is binding; angle and shape are measured in the two floor dimensions (the floor guarantees "
            "two dimensions, not a second axis with signal)"
        )
    n_repeats = params.n_repeats
    if latent.get("cv_repeats_completed") is not None and latent["cv_repeats_completed"] < n_repeats:
        findings.append(f"cross-validation completed {latent['cv_repeats_completed']} of {n_repeats} repeat(s)")
    for s in ANALYSIS_STATISTICS:
        value = record["statistics"].get(s)
        if value is None or not np.isfinite(value):
            findings.append(f"{s}: the statistic is not finite ({value})")
        p = record["p_values"].get(s)
        if p is None or not np.isfinite(p):
            findings.append(f"{s}: no finite p-value in the record ({p})")
    for key, stated in _MOTCO_DEFAULTS_STATED.items():
        used = record["params"].get(key)
        if used != stated:
            findings.append(f"MOTCO default {key} is {used!r} in the record but the proposal states {stated!r}")
    cv_used = latent.get("integration_params", {})
    for key in _MOTCO_CV_KEYS:
        if key in cv_used and cv_used[key] != record["params"].get(key):
            findings.append(f"MOTCO clamped the CV setting {key} from {record['params'].get(key)!r} to {cv_used[key]!r}")
    if (cv_used.get("min_components", 1)) != rank_floor:
        findings.append(f"the CV ran with rank floor {cv_used.get('min_components', 1)}, not ANALYSIS_RANK_FLOOR = {rank_floor}")

    versions = _software_versions((*_MANIFEST_PACKAGES, "motco", "scikit-learn"))
    manifest = {
        "step": "analyze",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": versions,
        "motco_software": record.get("software"),
        "git_revision": _git_revision(),
        "inputs": {
            "dir": str(input_dir),
            "files": loaded["inputs"],
            "export_manifest": {"name": EXPORT_MANIFEST, "sha256": loaded["inputs"][EXPORT_MANIFEST]["sha256"]},
            "export_git_revision": export_manifest.get("git_revision"),
            "export_created_at": export_manifest.get("created_at"),
            "export_findings": export_manifest.get("findings", []),
        },
        "settings": {
            "entry_point": "motco.analysis.analyze_trajectories",
            "ANALYSIS_PERMUTATIONS": ANALYSIS_PERMUTATIONS,
            "ANALYSIS_SEED": ANALYSIS_SEED,
            "ANALYSIS_ALPHA": ANALYSIS_ALPHA,
            "ANALYSIS_REJECTION_RULE": ANALYSIS_REJECTION_RULE,
            "ANALYSIS_RANK_FLOOR": ANALYSIS_RANK_FLOOR,
            "ANALYSIS_LATENT_ADJUSTMENT": ANALYSIS_LATENT_ADJUSTMENT,
            "ANALYSIS_STATISTICS": ANALYSIS_STATISTICS,
            "ANALYSIS_MISSING_COVARIATES": ANALYSIS_MISSING_COVARIATES,
            "ANALYSIS_COVARIATES": ANALYSIS_COVARIATES,
            "ANALYSIS_CATEGORICAL_COVARIATES": ANALYSIS_CATEGORICAL_COVARIATES,
            "n_jobs": n_jobs,
            "n_jobs_note": "RRPP draws depend on n_jobs (one seed stream per worker); reported runs use REPORTED_N_JOBS",
            "REPORTED_N_JOBS": REPORTED_N_JOBS,
            "blocks": [
                {"name": p, "file": f"{p}.csv", "transform": transform, "units": export_manifest.get("settings", {}).get("units"), "n_features": n_features[p]}
                for p in EXPORT_BLOCKS
            ],
            "metadata_file": ANALYSIS_METADATA,
            "sample_column": SAMPLE_COLUMN,
            "group_column": GROUP_COLUMN,
            "group_order": GROUP_VALUES,
            "stage_column": STAGE_COLUMN,
            "stage_order": STAGE_LABELS,
            "covariates": {
                key: cov_record[key]
                for key in ("columns", "kinds", "levels", "reference_levels", "design_columns", "reference_row", "lsmean_reference", "missing_policy", "n_dropped")
            },
            "covariates_imputed": False,
            "interactions": None,
            "min_components": params.resolved_min_components,
            "motco_defaults_used": {
                **{key: record["params"].get(key) for key in _MOTCO_DEFAULTS_STATED},
                "cv_as_run": cv_used,
                "attribution": False,
                "stated_by_proposal": _MOTCO_DEFAULTS_STATED,
            },
            "latent_adjustment": ANALYSIS_LATENT_ADJUSTMENT,
            "predeclared_sensitivity": ANALYSIS_PREDECLARED_LATENT_SENSITIVITY,
            "cli_equivalent": _analysis_cli_equivalent(input_dir, final / ANALYSIS_METADATA, params, n_jobs),
        },
        "counts": counts,
        "expected": expected,
        "deviations": deviations,
        "findings": findings,
    }

    # --- outputs ----------------------------------------------------------------------
    participant_level = {ANALYSIS_LATENT_SCORES, ANALYSIS_METADATA}
    with _finalize_output_dir(final, force=force) as tmp:
        written = write_analysis_outputs(result, tmp)
        (tmp / ANALYSIS_METADATA).write_text(metadata_csv)
        (tmp / ANALYSIS_SUMMARY).write_text(render_analysis_summary(record, export_manifest=export_manifest, n_jobs=n_jobs))
        names = sorted({p.name for p in written.values()} | {ANALYSIS_METADATA, ANALYSIS_SUMMARY})
        manifest["outputs"] = {
            name: {
                "sha256": _sha256_file(tmp / name),
                "bytes": (tmp / name).stat().st_size,
                "participant_level": name in participant_level,
            }
            for name in names
        }
        _write_manifest(tmp / ANALYSIS_MANIFEST, manifest)

    print(f"[analyze] wrote {final}/ (" + ", ".join([*names, ANALYSIS_MANIFEST]) + ")")
    if deviations:
        print(f"[analyze] {len(deviations)} count deviation(s) from the predeclared counts")
    else:
        print("[analyze] counts reproduce the predeclared ones")
    for msg in findings:
        print(f"[analyze] FINDING: {msg}")
    return {"dir": final, "record": record, "manifest": manifest, "findings": findings}


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
    flagged rows and ``READING_RULES`` (decided by ``adni-analyze``); it quotes only
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
    "check_motco_rank_floor",
    "render_analysis_summary",
    "run_clean",
    "run_cohort",
    "run_export",
    "run_analysis",
    "run_axis_diagnostics",
    "run_report",
]
