"""Pipeline steps of adni_sexdiff.

``clean`` (change ``adni-metabolomics-clean``), ``cohort`` (change
``adni-cohort``), ``export`` (change ``adni-export``), ``analyze`` (change
``adni-analyze``) and ``axis-diagnostics`` (change
``adni-axis-diagnostics``) and ``report`` (changes ``adni-report``,
``adni-report-variants`` and ``adni-report-stage-arm``: the case-study
report generated in full from the kept aggregate outputs, the primary
beside every sensitivity, and its cell-by-cell check) are implemented, and
so are the sensitivity steps ``latent-sensitivity`` (change
``adni-latent-sensitivity``: the predeclared ``stage``-conditioned
latent-adjustment arm), ``export-sensitivity`` (change
``adni-nist-bridge``: the predeclared export variants of the p180 run
handling, a NIST SRM 1950 bridge and per-run standardization; change
``adni-nmr-all-columns``: the NMR membership variant, every cleaned NMR
column in the block),
``stage-sensitivity`` (change ``adni-stage-sensitivity``: the predeclared
CN / LMCI / AD arm) and ``rank-sensitivity`` (change
``adni-rank-sensitivity``: the predeclared forced-rank ladder after an
anchor run at the primary's rank), each read beside the primary and never
replacing it. Every scientific constant
the steps need is decided and lives in ``constants``; a variant or arm
enters only through a proposal.

The raw-input helpers (``require_raw_files``, ``hash_raw_file``,
``check_known_repairs``), the version gates (``check_metabo_adni_version``,
``check_motco_version``, ``check_motco_rank_floor``), the shared export
function (``_run_export``, the body of ``export`` that a variant calls with
its one hook), the shared analysis function
(``_run_trajectory_analysis``, the body of ``analyze`` that the arms, the
variants and the ranks of the sweep call with their one differing input or
setting), the shared reading sentences
(``_statistic_reading_line``, ``_arm_status_line``,
``_export_variant_status_line``, ``_stage_arm_status_line``,
``_rank_status_line``: the code of
``summary.md``, the comparison documents and the report; a variant's words
come from ``_variant_words``) and the manifest
and output-directory helpers (``_git_revision``, ``_software_versions``,
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
import platform as _platform
import re
import shutil
import subprocess
import sys
import zipfile
from collections.abc import Callable, Generator, Iterable, Sequence
from datetime import date as date_type
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import pandas as pd

from . import constants
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
    ANALYSIS_PLS_LOADINGS,
    ANALYSIS_PREDECLARED_LATENT_SENSITIVITY,
    ANALYSIS_RANK_FLOOR,
    ANALYSIS_REJECTION_RULE,
    ANALYSIS_RESULT,
    ANALYSIS_SEED,
    ANALYSIS_STAGE_MEANS,
    ANALYSIS_STATISTICS,
    ANALYSIS_SUMMARY,
    CLEAN_EXPECTED_COUNTS,
    CLEAN_FASTING_FILE,
    CLEAN_INPUT_FILES,
    CLEAN_LOG,
    CLEAN_MANIFEST,
    CLEAN_MEDICATION_FILE,
    CLEAN_OPTIONS,
    CLEAN_P180_FILES,
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
    DIAGNOSTIC_CONDITIONING_COLUMNS,
    DIAGNOSTIC_CORRELATION_THRESHOLD,
    DIAGNOSTIC_N_BLOCK_PCS,
    DIAGNOSTIC_VARIABLES,
    DIAGNOSTICS_ANALYSIS_FILES,
    DIAGNOSTICS_AXIS_CORRELATIONS,
    DIAGNOSTICS_BLOCK_PCS,
    DIAGNOSTICS_COMPONENTS,
    DIAGNOSTICS_DIR,
    DIAGNOSTICS_EXPECTED_COUNTS,
    DIAGNOSTICS_GEOMETRY_QUANTITIES,
    DIAGNOSTICS_GEOMETRY_SHARES,
    DIAGNOSTICS_MANIFEST,
    DIAGNOSTICS_RANK_INDEPENDENT_KEYS,
    DIAGNOSTICS_SUMMARY,
    EXPORT_BLOCKS,
    EXPORT_COVARIATE_COLUMNS,
    EXPORT_COVARIATES,
    EXPORT_EXPECTED_COUNTS,
    EXPORT_FEATURE_RULE,
    EXPORT_FEATURES,
    EXPORT_MANIFEST,
    EXPORT_METADATA,
    EXPORT_SENSITIVITY_BRIDGE_TABLE,
    EXPORT_SENSITIVITY_DIR,
    EXPORT_SENSITIVITY_MANIFEST,
    EXPORT_SENSITIVITY_SUBDIRS,
    EXPORT_SENSITIVITY_SUMMARY,
    EXPORT_SENSITIVITY_TABLE,
    EXPORT_VARIANT_EXPECTED_COUNTS,
    EXPORT_VARIANT_RULE_SETS,
    EXPORT_VARIANTS,
    GROUP_COLUMN,
    GROUP_VALUES,
    KNOWN_RAW_FILE_REPAIRS,
    LATENT_SENSITIVITY_ARM,
    LATENT_SENSITIVITY_COVARIATE_ROLES,
    LATENT_SENSITIVITY_DIR,
    LATENT_SENSITIVITY_EXPECTED_COUNTS,
    LATENT_SENSITIVITY_MANIFEST,
    LATENT_SENSITIVITY_READING_RULES,
    LATENT_SENSITIVITY_SUBDIRS,
    LATENT_SENSITIVITY_SUMMARY,
    LATENT_SENSITIVITY_TABLE,
    METABO_ADNI_VERSION,
    MOTCO_ANALYSIS_DIR,
    MOTCO_INPUT_DIR,
    NIST_BRIDGE_RULE,
    NIST_BRIDGE_WORKBOOK_SHA256,
    NUMERIC_SETTINGS,
    PARTICIPANT_ID_COLUMN,
    PLATFORMS,
    RANK_SENSITIVITY_DIR,
    RANK_SENSITIVITY_EXPECTED_COUNTS,
    RANK_SENSITIVITY_LADDER,
    RANK_SENSITIVITY_MANIFEST,
    RANK_SENSITIVITY_RANK_DIR,
    RANK_SENSITIVITY_READING_RULES,
    RANK_SENSITIVITY_SUBDIRS,
    RANK_SENSITIVITY_SUMMARY,
    RANK_SENSITIVITY_TABLE,
    RAW_INPUT_SHA256,
    READING_RULES,
    REPORT_EXPORT_VARIANTS,
    REPORT_INPUT_FILES,
    REPORT_NAME,
    REPORT_SECTIONS,
    REPORTED_N_JOBS,
    REPORTS_DIR,
    SAMPLE_COLUMN,
    STAGE_COLUMN,
    STAGE_LABELS,
    STAGE_RULE,
    STAGE_SENSITIVITY_ARM,
    STAGE_SENSITIVITY_DIR,
    STAGE_SENSITIVITY_EXPECTED_COUNTS,
    STAGE_SENSITIVITY_MANIFEST,
    STAGE_SENSITIVITY_READING_RULES,
    STAGE_SENSITIVITY_SUBDIRS,
    STAGE_SENSITIVITY_SUMMARY,
    STAGE_SENSITIVITY_TABLE,
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


#: The OpenBLAS kernel and thread count of a pinned run (``NUMERIC_SETTINGS``).
_PINNED_OPENBLAS = (NUMERIC_SETTINGS["OPENBLAS_CORETYPE"], int(NUMERIC_SETTINGS["OPENBLAS_NUM_THREADS"]))


def _cpu_model() -> str | None:
    """The CPU model name (``/proc/cpuinfo`` on Linux, else ``platform.processor()``), or ``None``."""
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return _platform.processor() or None


def _numerics_record() -> dict:
    """The numeric environment this process actually has, for every manifest's ``numerics``.

    Returns
    -------
    dict
        ``host``, ``cpu_model``, ``cpus_available`` (the CPUs the process may
        use, which cap OpenBLAS's threads), ``requested``
        (``NUMERIC_SETTINGS``), ``environment`` (the four variables as the
        process sees them), ``numpy_log2_float64`` (the target numpy's
        ``float64`` ``log2`` dispatches to, from the public
        ``numpy.lib.introspect.opt_func_info``), ``blas`` (per loaded BLAS
        library, sorted by file name: ``api``, ``version``, ``architecture``,
        ``num_threads``, ``library`` as a base name, from ``threadpoolctl``)
        and ``pinned``.

    Notes
    -----
    Call it after a step's work, so every library the step loaded (scipy's
    OpenBLAS among them) is listed. ``pinned`` is decided from what the
    process observes, not from what was requested: the variables equal
    ``NUMERIC_SETTINGS``, ``log2`` runs numpy's baseline target, and every
    loaded BLAS is OpenBLAS at the pinned kernel and thread count. A field
    that cannot be read is ``None`` and makes ``pinned`` false. No path, no
    data and no participant enters the record.
    """
    try:
        from numpy.lib.introspect import opt_func_info

        log2 = opt_func_info(func_name="^log2$", signature="float64").get("log2", {}).get("dd", {}).get("current")
    except (ImportError, AttributeError, TypeError, ValueError):
        log2 = None
    try:
        import threadpoolctl

        blas = sorted(
            (
                {
                    "api": info.get("internal_api"),
                    "version": info.get("version"),
                    "architecture": info.get("architecture"),
                    "num_threads": info.get("num_threads"),
                    "library": Path(info.get("filepath") or "").name,
                }
                for info in threadpoolctl.threadpool_info()
                if info.get("user_api") == "blas"
            ),
            key=lambda entry: entry["library"],
        )
    except ImportError:
        blas = None
    try:
        cpus = len(os.sched_getaffinity(0))
    except AttributeError:
        cpus = os.cpu_count()
    record = {
        "host": _platform.node() or None,
        "cpu_model": _cpu_model(),
        "cpus_available": cpus,
        "requested": dict(NUMERIC_SETTINGS),
        "environment": {name: os.environ.get(name) for name in NUMERIC_SETTINGS},
        "numpy_log2_float64": log2,
        "blas": blas,
    }
    record["pinned"] = _numerics_problems(record) == []
    return record


def _numerics_problems(record: dict) -> list[str]:
    """Each way the observed state of ``record`` differs from the pinned one (empty when pinned)."""
    problems = [
        f"{name} is {seen!r} (pinned: {record['requested'][name]!r})"
        for name, seen in record["environment"].items()
        if seen != record["requested"][name]
    ]
    log2 = record["numpy_log2_float64"]
    if log2 is None:
        problems.append("numpy's log2 dispatch target could not be read (pinned: baseline)")
    elif not str(log2).startswith("baseline"):
        problems.append(f"numpy log2 runs {log2} (pinned: baseline)")
    arch, threads = _PINNED_OPENBLAS
    if not record["blas"]:
        problems.append(f"no BLAS library could be read (pinned: OpenBLAS {arch} × {threads} thread)")
    for lib in record["blas"] or []:
        if lib["api"] != "openblas":
            problems.append(f"BLAS {lib['api']} ({lib['library']}) cannot be pinned (pinned: OpenBLAS)")
            continue
        if lib["architecture"] != arch:
            problems.append(f"OpenBLAS {lib['library']} reports {lib['architecture']} (pinned: {arch})")
        if lib["num_threads"] != threads:
            problems.append(f"OpenBLAS {lib['library']} runs {lib['num_threads']} thread(s) (pinned: {threads})")
    return problems


def _numerics_finding(record: dict) -> str | None:
    """The finding for a run that is not pinned, naming what differs; ``None`` when pinned."""
    problems = _numerics_problems(record)
    if not problems:
        return None
    return (
        "numerics not pinned: " + "; ".join(problems) + "; outputs may differ from another machine's at rounding "
        "level and the hash chain may not reproduce; do not commit this output (NUMERIC_SETTINGS, change "
        "adni-portable-numerics: import adni_sexdiff before numpy)"
    )


def _numerics(prefix: str) -> tuple[dict, list[str]]:
    """Record the numeric state for a step's manifest, print it, and return it with its finding, if any.

    Parameters
    ----------
    prefix:
        The step's printed progress prefix (``[cohort]``, ``[clean] p180:``).

    Returns
    -------
    tuple
        ``(record, findings)``: the ``numerics`` block (``_numerics_record``)
        and a list holding the not-pinned finding, or empty.
    """
    record = _numerics_record()
    finding = _numerics_finding(record)
    if finding is None:
        arch, threads = _PINNED_OPENBLAS
        print(
            f"{prefix} numerics: pinned (log2 {record['numpy_log2_float64']}, OpenBLAS {arch} × {threads} thread, "
            f"host {record['host']})"
        )
        return record, []
    print(f"{prefix} numerics: NOT pinned (see the finding)")
    return record, [finding]


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
    keeps whatever was written, for inspection (an empty staging directory,
    with nothing to inspect, is removed, so a run that fails before writing
    leaves no ``.tmp/``).
    """
    final = Path(final)
    tmp = final.with_name(final.name + ".tmp")
    if final.exists() and not force:
        raise FileExistsError(f"{final} exists; pass --force to replace it")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    try:
        yield tmp
    except BaseException:
        if tmp.is_dir() and not any(tmp.iterdir()):
            tmp.rmdir()
        raise
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

    The manifest's ``numerics`` block records the numeric environment the run
    actually had (``_numerics_record``: host, CPU, the ``NUMERIC_SETTINGS``
    variables, numpy's ``log2`` target, each BLAS library's kernel and
    threads, ``pinned``); a run that is not pinned is a finding, never a
    stop, and its outputs are not committed.
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

        numerics, numerics_findings = _numerics(f"{prefix}:")
        findings += numerics_findings
        manifest = {
            "step": "clean",
            "platform": platform,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "versions": _software_versions(),
            "numerics": numerics,
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

    The manifest's ``numerics`` block records the numeric environment the run
    actually had (``_numerics_record``: host, CPU, the ``NUMERIC_SETTINGS``
    variables, numpy's ``log2`` target, each BLAS library's kernel and
    threads, ``pinned``); a run that is not pinned is a finding, never a
    stop, and its outputs are not committed.
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
    numerics, numerics_findings = _numerics("[cohort]")
    findings += numerics_findings

    manifest = {
        "step": "cohort",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": _software_versions(),
        "numerics": numerics,
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

    The manifest's ``numerics`` block records the numeric environment the run
    actually had (``_numerics_record``: host, CPU, the ``NUMERIC_SETTINGS``
    variables, numpy's ``log2`` target, each BLAS library's kernel and
    threads, ``pinned``); a run that is not pinned is a finding, never a
    stop, and its outputs are not committed.

    The body is ``_run_export`` with no variant; the ``export-sensitivity``
    step (change ``adni-nist-bridge``) calls the same function with one hook
    of ``EXPORT_VARIANTS`` set (a p180 hook, or ``membership`` on the NMR
    block, change ``adni-nmr-all-columns``), and the primary's outputs are
    its byte gate.
    """
    cleaned = Path(cleaned_dir) if cleaned_dir is not None else Path(CLEANED_DIR)
    cohort_path = Path(cohort_dir) if cohort_dir is not None else Path(COHORT_DIR)
    final = Path(out_dir) if out_dir is not None else Path(MOTCO_INPUT_DIR)
    return _run_export(cleaned=cleaned, cohort_path=cohort_path, final=final, force=force)


#: The p180 assay runs as ``p180_runs.csv`` names them (the prefixes of the
#: keys of ``CLEAN_P180_FILES``), in run order.
_P180_RUNS: tuple[str, ...] = tuple(dict.fromkeys(key.split("-")[0] for key in CLEAN_P180_FILES))


def _apply_run_factors(table: pd.DataFrame, run: np.ndarray, factors: dict[str, float]) -> pd.DataFrame:
    """Multiply the ``NIST_BRIDGE_RULE["bridged_run"]`` rows of ``table`` by 2^factor of each column (factor 0, ×1, when absent)."""
    multiplier = np.array([2.0 ** factors.get(str(c), 0.0) for c in table.columns])
    values = table.to_numpy(dtype=float, copy=True)
    values[run == NIST_BRIDGE_RULE["bridged_run"]] *= multiplier
    return pd.DataFrame(values, index=table.index, columns=table.columns)


def _standardize_by_run(T: np.ndarray, run: np.ndarray) -> np.ndarray:
    """Centre every column of ``T`` and divide it by its population SD within each run of ``_P180_RUNS``."""
    out = np.empty_like(T)
    for r in _P180_RUNS:
        rows = run == r
        if rows.any():
            out[rows] = (T[rows] - T[rows].mean(axis=0)) / T[rows].std(axis=0)
    return out


def _run_export(
    *,
    cleaned: Path,
    cohort_path: Path,
    final: Path,
    force: bool,
    variant: str | None = None,
    factors: dict[str, float] | None = None,
    reference: dict | None = None,
    manifest_extra: dict | None = None,
    staging: Path | None = None,
) -> dict:
    """The export, shared by ``export`` (the primary) and ``export-sensitivity`` (one variant of ``EXPORT_VARIANTS``).

    Parameters
    ----------
    cleaned, cohort_path, final:
        The clean output root, the cohort directory and the export directory
        the step promises.
    force:
        Replace an existing ``final`` (when ``staging`` is ``None``).
    variant:
        ``None`` for the primary, or a name of ``EXPORT_VARIANTS``: the step
        is then ``export-sensitivity``, ``p180_runs.csv`` is read (its hash
        against ``clean_manifest.json``) for the assay run of each exported
        participant, and the variant's hook changes its ``block``:
        ``factors`` multiplies the cleaned concentrations of the
        ``NIST_BRIDGE_RULE["bridged_run"]`` rows by 2^factor before the
        floors; ``standardize_by_run`` centres and scales each metabolite on
        the rule's scale within each run, after the floors and the log;
        ``membership`` (change ``adni-nmr-all-columns``) keeps every cleaned
        column of the block in cleaned order, the derived ones among them,
        each on the rule's scale with its own floor (the counts record
        ``derived`` 0 per family and ``derived_kept``; every row of the
        feature table is ``kept`` with its family), and compares the
        columns the rule keeps with the primary's ``<block>.csv`` (read
        from ``reference["dir"]`` with ``float_precision="round_trip"``):
        names, order and every cell, recorded as
        ``counts.rule_columns_equal_primary``, a difference a finding naming
        the block and the count of columns.
    factors:
        The log2 factor per metabolite of the block (hook ``factors``; from
        ``nist_bridge``); a metabolite without one keeps factor 1.
    reference:
        The primary export as the variant's reference: ``dir``, ``manifest``
        (name and sha256), ``outputs`` (the hashes its manifest records),
        ``phase_offset``; the variant's unchanged files are compared with
        ``outputs`` and every difference is a finding.
    manifest_extra:
        Top-level keys added to the manifest; its ``findings`` come first in
        the findings, its ``counts`` join the counts and its ``inputs`` the
        inputs.
    staging:
        An existing, empty directory to write into when the caller stages
        the directory itself; ``None`` stages ``<final>.tmp/`` here.

    Returns
    -------
    dict
        ``{"dir": Path, "blocks": {platform: (participants, metabolites)}, "manifest": dict, "findings": [...]}``.

    Notes
    -----
    With ``variant=None`` every byte is the primary's (``run_export``
    documents it). A variant reads no sex, stage or covariate to compute a
    value: the run comes from ``p180_runs.csv`` and the floors are the
    rule's, over the exported participants; ``phase`` is read to count the
    participants whose run differs from it (a finding) and, as in the
    primary, to describe the run offset. Its expected counts are
    ``EXPORT_VARIANT_EXPECTED_COUNTS[variant]`` without ``analysis`` and
    ``diagnostics``.
    """
    spec = EXPORT_VARIANTS[variant] if variant is not None else None
    step = "export" if spec is None else "export-sensitivity"
    log = "[export]" if spec is None else f"[export-sensitivity] {variant}:"
    if staging is None and final.exists() and not force:
        raise FileExistsError(f"{final} exists; pass --force to replace it")
    rule = EXPORT_FEATURE_RULE
    scale = rule["scale"]
    extra = dict(manifest_extra or {})
    findings: list[str] = list(extra.pop("findings", []))
    extra_counts = dict(extra.pop("counts", {}))
    extra_inputs = dict(extra.pop("inputs", {}))

    # --- inputs: the clean outputs, the cohort output and the chain ---------
    clean_inputs = _check_clean_outputs(cleaned, platforms=EXPORT_BLOCKS, runs=spec is not None)
    cohort_manifest, cohort_inputs, chain = _check_cohort_outputs(cohort_path, clean_inputs)
    for platform, entry in clean_inputs.items():
        for name, rec in entry["outputs"].items():
            print(f"{log} clean {platform}/{name}: sha256 {rec['sha256'][:16]}… equals {entry['manifest']['name']}")
    print(
        f"{log} cohort {COHORT_TABLE}: sha256 {cohort_inputs['outputs'][COHORT_TABLE]['sha256'][:16]}… equals "
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
        raise ValueError(f"{step} stops before writing anything ({COHORT_TABLE}, rows with every platform flag): " + "; ".join(problems))
    rids = both[SAMPLE_COLUMN].to_numpy()
    sex_stage = _sex_stage(both)
    cells = "; ".join(
        f"{sex_} {'/'.join(STAGE_LABELS)} " + "/".join(str(n) for n in sex_stage[sex_].values()) for sex_ in GROUP_VALUES
    )
    print(f"{log} participants: {len(both)} of the {len(cohort)} rows of {COHORT_TABLE} carry every platform flag ({cells})")

    # --- a variant: the assay run of each exported participant ------------------
    run = None
    if spec is not None:
        label = f"p180/{CLEAN_RUNS_TABLE}"
        runs = pd.read_csv(cleaned / "p180" / CLEAN_RUNS_TABLE, index_col=PARTICIPANT_ID_COLUMN)
        n_dup = int(runs.index.duplicated().sum())
        if n_dup:
            raise RuntimeError(f"{label}: {n_dup} duplicated participant(s); rerun clean")
        n_absent = int((~pd.Index(rids).isin(runs.index)).sum())
        if n_absent:
            raise RuntimeError(f"{label}: {n_absent} exported participant(s) absent; rerun clean, then cohort")
        run = runs.loc[rids, "run"].astype(str).to_numpy()
        outside = ~np.isin(run, _P180_RUNS)
        if outside.any():
            raise ValueError(f"{label}: {int(outside.sum())} run value(s) outside {list(_P180_RUNS)}: " + _value_counts_text(pd.Series(run[outside])))
        n_differ = int((run != both["phase"].astype(str).to_numpy()).sum())
        if n_differ:
            findings.append(
                f"{n_differ} exported participant(s) whose run in {label} differs from their phase in {COHORT_TABLE}: "
                "the variant handles the assay run (the batch) and phase stays the covariate of the stage means"
            )
        extra_counts.update(
            runs=_int_counts(pd.Series(run), _P180_RUNS), runs_differing_from_phase=n_differ
        )
        print(
            f"{log} run ({label}): " + ", ".join(f"{r} {n}" for r, n in extra_counts["runs"].items())
            + f"; {n_differ} differ from phase; hook {spec['hook']} on {spec['block']}"
        )

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
        print(f"{log} {platform}/{name}: {table.shape[0]} × {table.shape[1]} cleaned → {len(rids)} × {table.shape[1]} exported participants")
        if spec is not None and spec["hook"] == "factors" and platform == spec["block"]:
            blocks[platform] = _apply_run_factors(blocks[platform], run, factors or {})
            n_bridged = sum(1 for c in table.columns if (factors or {}).get(str(c), 0.0) != 0.0)
            print(
                f"{log} {platform}: the {int((run == NIST_BRIDGE_RULE['bridged_run']).sum())} "
                f"{NIST_BRIDGE_RULE['bridged_run']} row(s) multiplied by 2^b for {n_bridged} of {table.shape[1]} "
                "metabolite(s) before the floors (NIST_BRIDGE_RULE)"
            )

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
        # hook ``membership`` (``nmr_all_columns``): every cleaned column of the block, the derived ones among them
        membership = spec is not None and spec["hook"] == "membership" and platform == spec["block"]
        kept = list(table.columns) if membership else [c for c in table.columns if families[c] is None]
        kept_pos = {c: j for j, c in enumerate(kept)}
        counts["features"][platform] = {
            "cleaned": int(table.shape[1]),
            "kept": len(kept),
            "derived": {
                fam: sum(1 for c, f in families.items() if f == fam and c not in kept_pos) for fam in _DERIVED_FAMILIES
            },
        }
        if membership:
            counts["features"][platform]["derived_kept"] = {
                fam: sum(1 for c, f in families.items() if f == fam and c in kept_pos) for fam in _DERIVED_FAMILIES
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
        standardized = spec is not None and spec["hook"] == "standardize_by_run" and platform == spec["block"]
        if standardized:
            T = _standardize_by_run(T, run)
        counts["non_finite"][platform] = n_bad = int((~np.isfinite(T)).sum())
        if n_bad:
            raise RuntimeError(
                f"{platform}: {n_bad} non-finite cell(s) after {scale['transform']}"
                + (" and the per-run standardization (a metabolite constant within a run?)" if standardized else "")
            )
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
                "status": "kept" if c in kept_pos else "derived",
                "zero_cells": int(zeros[i]),
                "median": median[i],
                "skew_raw": skew_raw[i],
            }
            if c in kept_pos:
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
        if membership:
            # The columns the rule keeps must be the primary's: names, order and every cell (design D2).
            rule_columns = [c for c in kept if families[c] is None]
            primary_path = Path((reference or {}).get("dir", MOTCO_INPUT_DIR)) / f"{platform}.csv"
            primary_block = pd.read_csv(primary_path, float_precision="round_trip")
            same_rows = SAMPLE_COLUMN in primary_block.columns and np.array_equal(
                primary_block[SAMPLE_COLUMN].astype(str).to_numpy(), np.asarray(rids).astype(str)
            )
            primary_columns = [str(c) for c in primary_block.columns if c != SAMPLE_COLUMN]
            n_differ = len(set(primary_columns) ^ {str(c) for c in rule_columns})
            for c in rule_columns:
                if str(c) not in primary_block.columns:
                    continue
                ours = np.ascontiguousarray(T[:, kept_pos[c]], dtype=float)
                theirs = np.ascontiguousarray(primary_block[str(c)].to_numpy(dtype=float))
                n_differ += int(not (same_rows and ours.tobytes() == theirs.tobytes()))
            in_order = primary_columns == [str(c) for c in rule_columns]
            counts["rule_columns_equal_primary"] = equal = n_differ == 0 and in_order
            if not equal:
                findings.append(
                    f"{platform}: {n_differ} of the {len(rule_columns)} column(s) EXPORT_FEATURE_RULE keeps differ from the "
                    f"primary {platform}.csv ({primary_path.parent}) in name or cells"
                    + ("" if in_order else ", and their order differs")
                    + f"; the variant changes {_variant_words(variant)['changes']} only"
                )
            print(
                f"{log} {platform}: the {len(rule_columns)} column(s) EXPORT_FEATURE_RULE keeps "
                + ("equal" if equal else "differ from")
                + f" the primary {platform}.csv, column for column and cell for cell ({n_differ} differ)"
            )
        derived_text = ", ".join(f"{fam} {n}" for fam, n in counts["features"][platform]["derived"].items() if n)
        kept_text = ", ".join(f"{fam} {n}" for fam, n in counts["features"][platform].get("derived_kept", {}).items() if n)
        print(
            f"{log} {platform}: {len(kept)} of {table.shape[1]} cleaned column(s) kept"
            + (f" ({derived_text} derived)" if derived_text else "")
            + (f" (every column, derived ones among them: {kept_text}; hook membership)" if kept_text else "")
            + f"; zero cells {counts['zero_cells'][platform]} in {counts['metabolites_with_zeros'][platform]} metabolite(s); "
            f"{scale['transform']} with floor at the {scale['floor_quantile']:.0%} quantile"
            + ("; standardized within run" if standardized else "")
            + f"; phase |d| > 1 for {offset['abs_d_gt_1']} metabolite(s), median |d| {offset['median_abs_d']:.2f}"
        )
    total = sum(counts["features"][p]["kept"] for p in EXPORT_BLOCKS)
    counts["joint_features"] = total
    counts["block_shares"] = {p: counts["features"][p]["kept"] / total for p in EXPORT_BLOCKS}
    counts.update(extra_counts)

    # --- the predeclared counts ------------------------------------------------
    # A variant's unchanged files are compared with the primary's after they are written (below).
    if spec is None:
        expected = json.loads(json.dumps(EXPORT_EXPECTED_COUNTS))
    else:
        expected = json.loads(json.dumps(
            {k: v for k, v in EXPORT_VARIANT_EXPECTED_COUNTS[variant].items() if k not in ("analysis", "diagnostics")}
        ))
    observed = _project(json.loads(json.dumps(counts, default=_json_default)), expected)
    deviations = [
        msg for key in expected if key != "unchanged_equal_primary"
        for msg in _count_deviations(expected[key], observed.get(key), key)
    ]
    findings += deviations
    numerics, numerics_findings = _numerics(log)
    findings += numerics_findings

    manifest = {
        "step": step,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": _software_versions(),
        "numerics": numerics,
        "git_revision": _git_revision(),
        "inputs": {"clean": clean_inputs, "cohort": cohort_inputs, "chain": chain, **extra_inputs},
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
        **extra,
    }

    # --- outputs -------------------------------------------------------------------
    names = [f"{p}.csv" for p in EXPORT_BLOCKS] + [EXPORT_METADATA, EXPORT_COVARIATES]

    def write(tmp: Path) -> None:
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
        if spec is not None:
            # The files a variant does not change must be the primary's, byte for byte.
            recorded = (reference or {}).get("outputs", {})
            unchanged = {
                name: manifest["outputs"][name]["sha256"] == recorded.get(name, {}).get("sha256")
                for name in [*(f"{p}.csv" for p in EXPORT_BLOCKS if p != spec["block"]), EXPORT_METADATA, EXPORT_COVARIATES]
            }
            counts["unchanged_equal_primary"] = unchanged
            new = _count_deviations(expected.get("unchanged_equal_primary"), unchanged, "unchanged_equal_primary")
            deviations.extend(new)
            findings.extend(new)
            differ = [name for name, same in unchanged.items() if not same]
            if differ:
                findings.append(
                    f"{', '.join(differ)}: sha256 differs from the hash the primary export manifest records "
                    f"({(reference or {}).get('dir')}); a variant changes {_variant_words(variant)['changes']} only"
                )
        _write_manifest(tmp / EXPORT_MANIFEST, manifest)

    if staging is None:
        with _finalize_output_dir(final, force=force) as tmp:
            write(tmp)
        where = final
    else:
        write(staging)
        where = staging

    shapes = {p: (len(rids), counts["features"][p]["kept"]) for p in EXPORT_BLOCKS}
    print(
        f"{log} wrote {where}/ ("
        + ", ".join(f"{p}.csv {n} × {m}" for p, (n, m) in shapes.items())
        + f", {EXPORT_METADATA}, {EXPORT_COVARIATES}, "
        + ", ".join(EXPORT_FEATURES.format(platform=p) for p in EXPORT_BLOCKS)
        + f", {EXPORT_MANIFEST})"
    )
    if deviations:
        print(f"{log} {len(deviations)} count deviation(s) from the predeclared counts")
    else:
        print(f"{log} counts reproduce the predeclared ones")
    for msg in findings:
        print(f"{log} FINDING: {msg}")
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


def _load_analysis_inputs(input_dir: Path, *, step: str = "analyze") -> dict:
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
    ``step`` names the calling step in those messages (``analyze``, or
    ``axis-diagnostics``, which reads the same export).
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
        raise ValueError(f"{step} stops before writing anything: " + "; ".join(problems))

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
        raise ValueError(f"{step} stops before writing anything: " + "; ".join(problems))
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
        raise ValueError(f"{step} stops before writing anything: " + "; ".join(problems))

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
        raise ValueError(f"{step} stops before writing anything: " + "; ".join(problems))

    merged = meta.merge(cov, on=SAMPLE_COLUMN, how="inner", validate="one_to_one")
    merged = merged[[SAMPLE_COLUMN, GROUP_COLUMN, STAGE_COLUMN, *ANALYSIS_COVARIATES]]
    return {"blocks": blocks, "metadata": merged, "export_manifest": manifest, "inputs": inputs, "findings": findings}


def _rejected(p: float | None, alpha: float = ANALYSIS_ALPHA) -> bool | None:
    """``ANALYSIS_REJECTION_RULE`` (``p <= alpha``); ``None`` when there is no p-value."""
    return None if p is None else bool(p <= alpha)


def _fmt(value, spec: str = ".6g") -> str:
    """Format a number for ``summary.md`` (six significant digits); ``n/a`` for ``None``."""
    return "n/a" if value is None else format(value, spec)


def _analysis_cli_equivalent(
    input_dir: Path, metadata_path: Path, params, n_jobs: int, *, forced_components: int | None = None
) -> dict:
    """The ``motco analyze`` command that reproduces the analysis directory from its inputs.

    Covariate flags are emitted in ``ANALYSIS_COVARIATES`` order, ``--covariate``
    for a numeric covariate and ``--categorical-covariate`` for a categorical
    one (MOTCO's CLI keeps the declaration order across both flags). Only the
    settings the step passes appear; the rest are MOTCO's defaults.
    ``--forced-components`` appears only for a forced rank (``forced_components``
    not ``None``: a rank of the ``rank-sensitivity`` sweep, change
    ``adni-rank-sensitivity``), so every other command is unchanged.
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
        "--min-components", str(params.resolved_min_components),
    ]
    if forced_components is not None:
        argv += ["--forced-components", str(forced_components)]
    argv += ["--out-dir", "OUT_DIR"]
    return {
        "command": shlex.join(argv),
        "argv": argv,
        "note": "replace OUT_DIR with a new directory; paths are relative to the directory analyze ran in",
    }


def _statistic_reading_line(
    statistic: str,
    rejected: bool | None,
    *,
    stages: list,
    arm: bool = False,
    variant: str | None = None,
    stage_arm: bool = False,
    rank_sweep: bool = False,
) -> str:
    """The reading sentence of one statistic's status, shared by ``summary.md`` and the report (design D5 of ``adni-report``).

    Parameters
    ----------
    statistic:
        ``delta``, ``angle`` or ``shape``.
    rejected:
        The status under ``ANALYSIS_REJECTION_RULE`` (``_rejected``); ``None``
        when the record holds no p-value.
    stages:
        The record's stage levels (``angle`` names the endpoint stages).
    arm:
        ``True`` for the latent-adjustment arm: the sentence carries the
        arm's note (a rejection the primary does not make is basis
        dependence, a non-rejection is weaker than the primary's).
    variant:
        The name of an export variant (``EXPORT_VARIANTS``, change
        ``adni-nist-bridge``): the sentence carries the variant's note (a
        rejection the primary does not make is dependence on what the variant
        changes, a non-rejection is no more informative than the primary's),
        in the words and rule citations of the variant's rule set
        (``EXPORT_VARIANT_RULE_SETS``, change ``adni-nmr-all-columns``);
        ``None`` otherwise.
    stage_arm:
        ``True`` for the CN / LMCI / AD arm (``STAGE_SENSITIVITY_ARM``, change
        ``adni-stage-sensitivity``): the sentence carries the arm's note (a
        rejection the primary does not make is dependence on the stage
        definition and the sample, a non-rejection is no more informative
        than the primary's). The default leaves every other sentence as it
        was.
    rank_sweep:
        ``True`` for a forced rank of the rank sweep
        (``RANK_SENSITIVITY_LADDER``, change ``adni-rank-sensitivity``): the
        sentence carries the sweep's note (a rejection the primary does not
        make is rank dependence, not a result at that rank; a non-rejection
        is no more informative than the primary's). The default leaves every
        other sentence as it was.

    Returns
    -------
    str
        The sentence without its list marker, string-equal wherever it is
        printed (``summary.md`` of the primary, the arms, a variant and a
        rank, ``export_sensitivity.md``, ``stage_sensitivity.md``,
        ``rank_sensitivity.md``, the report).
    """
    if rejected is None:
        return f"`{statistic}`: no p-value in the record."
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
    line = readings[statistic][0 if rejected else 1]
    if arm and rejected:
        line += (
            " In the arm, a rejection the primary does not make is basis dependence, not a result of the arm (arm "
            "rule 2" + ("; an arm-only `angle` rejection is read against MOTCO's controls, arm rule 4)." if statistic == "angle" else ").")
        )
    elif arm:
        line += " In the arm this non-rejection is weaker than the primary's (arm rule 5)."
    elif variant is not None and rejected:
        words = _variant_words(variant)
        line += (
            f" In the variant, a rejection the primary does not make is dependence on {words['source']}, not a result "
            f"of the variant, and is read beside the variant's rank and null summary ({words['cite']}s 2 and 6)."
        )
    elif variant is not None:
        line += f" In the variant this non-rejection is no more informative than the primary's ({_variant_words(variant)['cite']} 6)."
    elif stage_arm and rejected:
        line += (
            " In the CN / LMCI / AD arm, a rejection the primary does not make is dependence on the stage definition "
            "and the sample, not a result of the arm, and is read beside the arm's rank and null summary (stage-arm "
            "rules 2 and 6)."
        )
    elif stage_arm:
        line += (
            " In the CN / LMCI / AD arm this non-rejection is no more informative than the primary's (stage-arm rule 6)."
        )
    elif rank_sweep and rejected:
        line += (
            " At a forced rank, a rejection the primary does not make is rank dependence, not a result at that rank, "
            "and is read beside the rank's null summary (sweep rules 2 and 5)."
        )
    elif rank_sweep:
        line += " At a forced rank this non-rejection is no more informative than the primary's (sweep rule 5)."
    return line


def render_analysis_summary(
    record: dict,
    *,
    export_manifest: dict,
    n_jobs: int,
    alpha: float = ANALYSIS_ALPHA,
    rank_floor: int = ANALYSIS_RANK_FLOOR,
    rank_sweep: dict | None = None,
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
    rank_sweep:
        For a forced rank of the rank sweep (change
        ``adni-rank-sensitivity``): ``ladder`` (``RANK_SENSITIVITY_LADDER``
        with its constant name), ``forced_rank``, ``primary_rank`` and
        ``anchor`` (the anchor gate's record, ``None`` on the anchor run
        itself); ``None`` otherwise (see Notes).

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

    Notes
    -----
    The renderer keys on ``record.get("latent_adjustment")``. Without the
    block (the primary) every line is the one above. With it (the
    ``stage``-conditioned arm of ``latent-sensitivity``, change
    ``adni-latent-sensitivity``) the title and header name the arm, a
    "Latent adjustment" section follows "Latent space" (conditioning,
    covariates, the residualization design columns with ``stage[1]`` and
    ``stage[2]`` named, residual df, smallest CV training df, feature scale,
    the ``feature_r2`` quantiles and mean), each reading line carries the
    arm's note (a non-rejection is weaker than the primary's, a rejection the
    primary does not make is basis dependence) and
    ``LATENT_SENSITIVITY_READING_RULES`` follows ``READING_RULES`` under its
    own heading.

    It also keys on ``export_manifest.get("variant")`` (change
    ``adni-nist-bridge``). With the block (an export variant of
    ``export-sensitivity``) the title and header name the variant, an "Export
    variant" section follows "Latent space" (``_export_variant_lines``: the
    variant's setting, the blocks it keeps, the runs, for ``nist_bridge`` the
    bridge summary and table, for ``nmr_all_columns`` the NMR membership, the
    rule's columns equal, the block shares and the NMR shape counts, the run
    offset per block of the primary export beside the variant's), each
    reading line carries the variant's note, the export context names the
    variant's run offset and what it changes (``_export_variant_phase_line``),
    and the variant's rule set (``EXPORT_VARIANT_RULE_SETS``:
    ``EXPORT_VARIANT_READING_RULES`` for the p180 variants,
    ``NMR_MEMBERSHIP_READING_RULES`` for ``nmr_all_columns``, change
    ``adni-nmr-all-columns``) follows ``READING_RULES`` under its own heading;
    otherwise every byte is unchanged.

    And it keys on ``export_manifest.get("stage_arm")`` (change
    ``adni-stage-sensitivity``). With the block (the CN / LMCI / AD arm of
    ``stage-sensitivity``) the title and header name the arm, an "Arm"
    section follows "Latent space" (``_stage_arm_lines``: the participants
    kept and dropped by ``dx_bl`` × sex, the cells, the runs within stage and
    the covariate levels of the primary and the arm, the run offset per block
    of both), each reading line carries the arm's note, the export context
    names the run offset on the arm's rows and
    ``STAGE_SENSITIVITY_READING_RULES`` follows ``READING_RULES`` under its own
    heading; otherwise every byte is unchanged.

    And on ``rank_sweep`` (change ``adni-rank-sensitivity``). With it (a
    forced rank of ``rank-sensitivity``) the title and header name the
    forced rank and the ladder, the ``angle`` note reads "forced rank k"
    instead of the CV-selected rank, the CV line of "Latent space" says that
    MOTCO skips the cross-validation, a "Rank sweep" section follows "Latent
    space" (``_rank_sweep_lines``: the ladder, this rank's place in it, the
    nesting relative to the primary's rank, the anchor and the
    rank-specific loadings), each reading line carries the sweep's note and
    ``RANK_SENSITIVITY_READING_RULES`` follows ``READING_RULES`` under its own
    heading; without it every byte is unchanged.
    """
    design, meas, latent = record["design"], record["measurement"], record["latent"]
    stages, groups = design["stage_levels"], design["group_levels"]
    selected = latent["selected_lv"]
    floor_binding = latent["component_selection"] == "cv" and selected == rank_floor
    eigengap = (record.get("config_spectrum", {}).get("pooled") or {}).get("relative_eigengap")
    blocks_text = ", ".join(f"{b['name']} ({b['n_features']} features, {b['transform']})" for b in record["blocks"])
    adjustment = record.get("latent_adjustment")
    variant = export_manifest.get("variant") or None
    variant_name = variant["name"] if variant else None
    stage_arm = export_manifest.get("stage_arm") or None
    sweep = rank_sweep or None
    title = "# MOTCO trajectory analysis: ADNI serum metabolomics, sex × stage"
    if adjustment:
        title += f" — `{adjustment['conditioning']}`-conditioned latent-adjustment arm"
        latent_clause = (
            f"; latent adjustment: `{adjustment['conditioning']}` (the sensitivity arm "
            f"`{LATENT_SENSITIVITY_ARM['name']}`, `LATENT_SENSITIVITY_ARM` of `{LATENT_SENSITIVITY_ARM['change']}`: "
            "the latent basis is fitted on the features with the covariates regressed out within stage and the raw "
            "features are measured in it; read beside the primary, never replacing it)."
        )
    elif variant_name:
        title += f" — export variant `{variant_name}`"
        latent_clause = (
            f"; latent adjustment: none, as the primary's; export variant `{variant_name}` (`EXPORT_VARIANTS`, change "
            f"`{variant['change']}`: {variant['setting']}; every other export and analysis setting the primary's; read "
            "beside the primary, never replacing it)."
        )
    elif stage_arm:
        title += f" — CN / LMCI / AD arm `{stage_arm['name']}`"
        latent_clause = (
            f"; latent adjustment: none, as the primary's; CN / LMCI / AD arm `{stage_arm['name']}` "
            f"(`STAGE_SENSITIVITY_ARM`, change `{stage_arm['change']}`: {_stage_arm_definition(stage_arm)}; every "
            "other export and analysis setting the primary's; read beside the primary, never replacing it)."
        )
    elif sweep:
        ladder = sweep["ladder"]
        title += f" — forced rank {sweep['forced_rank']} (rank sweep)"
        latent_clause = (
            f"; latent adjustment: none, as the primary's; forced rank {sweep['forced_rank']} of the rank sweep "
            f"`{ladder['name']}` (`RANK_SENSITIVITY_LADDER`, change `{ladder['change']}`: `{ladder['setting']}` = "
            f"{sweep['forced_rank']}, which fixes the rank and skips MOTCO's cross-validation; every other export and "
            "analysis setting the primary's; read beside the primary, never replacing it)."
        )
    else:
        latent_clause = (
            "; latent adjustment: none (the primary; the `stage`-conditioned arm is the predeclared sensitivity "
            f"of `{ANALYSIS_PREDECLARED_LATENT_SENSITIVITY['change']}`)."
        )
    lines = [
        title,
        "",
        f"MOTCO {record['software']['motco']}; n = {design['n_samples']}; groups {' vs '.join(groups)} "
        f"(`{design['group_col']}`); stages {' → '.join(stages)} (`{design['stage_col']}`); blocks {blocks_text}; "
        f"orientation `{meas['orientation_estimator']}`; {meas['permutations']} RRPP permutations, seed "
        f"{meas['seed']}; α = {alpha}, rejected when {ANALYSIS_REJECTION_RULE} (`ANALYSIS_REJECTION_RULE`); "
        f"n_jobs {n_jobs}"
        + ("" if n_jobs == REPORTED_N_JOBS else f" (not a reported run: reported runs use n_jobs = {REPORTED_N_JOBS})")
        + latent_clause,
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
                f"degrees, endpoint stages {stages[0]} and {stages[-1]}; "
                + (f"forced rank {selected}" if sweep else f"CV-selected rank {selected}")
                + f" (rank floor {rank_floor}); pooled relative eigengap {_fmt(eigengap)}"
            )
            if floor_binding:
                note += "; the floor is binding: the CV selected the floor rank"
        elif s == "shape":
            note = "not available at fewer than three stages" if not meas.get("shape_available", True) else ""
        lines.append(
            f"| {s} | {_fmt(record['statistics'].get(s))} | {_fmt(p)} | {rejected} | "
            f"{_fmt(null.get('mean'))} | {_fmt(null.get('sd'))} | {_fmt(null.get('q95'))} | {note} |"
        )
    lines += ["", "Reading, under the rules below:", ""]
    lines += [
        "- " + _statistic_reading_line(
            s, status[s], stages=stages, arm=bool(adjustment), variant=variant_name, stage_arm=bool(stage_arm),
            rank_sweep=bool(sweep),
        )
        for s in ANALYSIS_STATISTICS
    ]
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
        (
            f"- CV: none (MOTCO skips the cross-validation at a forced rank; {latent.get('cv_repeats_completed')} "
            "repeats completed)"
            if sweep
            else f"- CV: cv2_splits {cv.get('cv2_splits')}, cv1_splits {cv.get('cv1_splits')}, n_repeats "
            f"{cv.get('n_repeats')} ({latent.get('cv_repeats_completed')} completed), max_components "
            f"{cv.get('max_components')}, rank floor {cv.get('min_components', 1)}, random_state {cv.get('random_state')}"
        ),
        f"- blocks: {blocks_text}; features are z-scored by MOTCO (pooled per-feature scalers)",
    ]
    if adjustment:
        design_cols = [str(c) for c in adjustment["design_columns"]]
        stage_names = {f"stage[{k}]": st for k, st in enumerate(stages)}
        n_cond = sum(c in stage_names for c in design_cols)
        r2 = adjustment.get("feature_r2", {})
        lines += [
            "",
            "## Latent adjustment",
            "",
            f"- conditioning: `{adjustment['conditioning']}` (`covariate_latent_adjustment`, `LATENT_SENSITIVITY_ARM`): "
            "the basis is fitted on the pooled-standardized features with the covariates regressed out given the "
            "intercept and the stage indicators, per CV training set and on the full sample; the raw features are "
            "projected onto it; the trajectory model, LS-means and RRPP are the primary's",
            "- covariates residualized (in order): " + ", ".join(f"`{c}`" for c in adjustment["covariates"]),
            f"- residualization design columns: {len(design_cols)} ("
            + ", ".join(f"{c} = {stage_names[c]}" if c in stage_names else c for c in design_cols) + ")",
            f"- samples {adjustment['n_samples']}; residual df {adjustment['residual_df']} (n − 1 − {n_cond} stage "
            f"indicator(s) − {len(design_cols) - n_cond} design column(s)); smallest CV training df "
            f"{adjustment.get('cv_min_training_df')}",
            f"- feature scale: `{adjustment['feature_scale']}`",
            "- feature R² of the covariates given the intercept and the stage indicators (the share of each feature's "
            "variance the residualization removed): q05 / q25 / q50 / q75 / q95 "
            + " / ".join(_fmt(r2.get(q), ".3f") for q in ("q05", "q25", "q50", "q75", "q95"))
            + f"; mean {_fmt(r2.get('mean'), '.3f')}; fraction above 0.5 {_fmt(r2.get('fraction_above_0.5'), '.3f')}",
        ]
    if variant_name:
        lines += ["", "## Export variant", "", *_export_variant_lines(export_manifest)]
    if stage_arm:
        lines += ["", "## Arm", "", *_stage_arm_lines(export_manifest)]
    if sweep:
        lines += ["", "## Rank sweep", "", *_rank_sweep_lines(sweep)]
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
        (
            f"- feature rule (`EXPORT_FEATURE_RULE`, the primary export's floors and scale: the arm's rows are the "
            f"primary export's rows): units `{settings.get('units')}`, MOTCO transform `{settings.get('motco_transform')}`; "
            "features: " + ", ".join(f"{p} {features.get(p)}" for p in EXPORT_BLOCKS)
            if stage_arm
            else f"- feature rule (`EXPORT_FEATURE_RULE`): units `{settings.get('units')}`, MOTCO transform "
            f"`{settings.get('motco_transform')}`; kept / cleaned columns: "
            + ", ".join(f"{p} {features.get(p, {}).get('kept')} / {features.get(p, {}).get('cleaned')}" for p in EXPORT_BLOCKS)
        )
        + f"; joint features {counts.get('joint_features')}",
        "- block shares (unweighted in MOTCO): " + ", ".join(f"{p} {_fmt(shares.get(p), '.3f')}" for p in EXPORT_BLOCKS),
        (
            f"- run offset of this export (`phase`, ADNI1 against ADNI2GO; the variant `{variant_name}` "
            f"{_variant_words(variant_name)['does']} and the primary's offset is beside it above): "
            if variant_name
            else "- run offset on the arm's rows (`phase`, ADNI1 against ADNI2GO, measured by stage-sensitivity and not "
            "corrected; the primary's is beside it above): "
            if stage_arm
            else "- p180 run offset (`phase`, ADNI1 against ADNI2GO, recorded by export and not corrected): "
        )
        + "; ".join(
            f"{p} median |d| {_fmt(offsets.get(p, {}).get('median_abs_d'), '.2f')}, |d| > 1 for "
            f"{offsets.get(p, {}).get('abs_d_gt_1')} metabolite(s), |corr(PC1, phase)| "
            f"{_fmt(offsets.get(p, {}).get('abs_corr_pc1_phase'), '.2f')}"
            for p in EXPORT_BLOCKS
        ),
        (
            "- `phase` enters as a covariate of the stage means (above) and, in this arm, is among the covariates "
            "regressed out of the features within stage before the basis is fitted; the primary's latent space is "
            "built without it"
            if adjustment
            else _export_variant_phase_line(variant_name)
            if variant_name
            else "- `phase` enters as a covariate of the stage means (above), as in the primary; in the arm each stage "
            "holds one `DX.bl` category in both runs, so its coefficient is estimated from contrasts within one "
            "diagnosis, and the run offset stays (stage-arm rule 4)"
            if stage_arm
            else "- `phase` enters as a covariate of the stage means (above), as in the primary; the rank sweep changes "
            "the latent rank only (sweep rule 2), and a component above the primary's rank that tracks `phase` is a "
            "measurement-space finding (sweep rule 7)"
            if sweep
            else "- `phase` enters as a covariate of the stage means (above); the `stage`-conditioned latent adjustment "
            f"is the predeclared sensitivity arm of `{ANALYSIS_PREDECLARED_LATENT_SENSITIVITY['change']}`"
        ),
        "",
        "## Reading rules",
        "",
        "Binding for every reader of this result (`READING_RULES`, written before the first run):",
        "",
    ]
    lines += [f"{i}. {rule}" for i, rule in enumerate(READING_RULES, 1)]
    if adjustment:
        lines += [
            "",
            "## Reading rules of the arm",
            "",
            f"Binding for every reader of the arm (`LATENT_SENSITIVITY_READING_RULES`, decided by "
            f"`{LATENT_SENSITIVITY_ARM['change']}` before any run), after `READING_RULES`:",
            "",
        ]
        lines += [f"{i}. {rule}" for i, rule in enumerate(LATENT_SENSITIVITY_READING_RULES, 1)]
    if variant_name:
        lines += ["", *_export_variant_rules_lines(variant_name)]
    if stage_arm:
        lines += ["", *_stage_arm_rules_heading(), ""]
        lines += [f"{i}. {rule}" for i, rule in enumerate(STAGE_SENSITIVITY_READING_RULES, 1)]
    if sweep:
        lines += ["", *_rank_sweep_rules_heading(), ""]
        lines += [f"{i}. {rule}" for i, rule in enumerate(RANK_SENSITIVITY_READING_RULES, 1)]
    return "\n".join(lines) + "\n"


def _rank_sweep_rules_heading() -> list[str]:
    """The heading and lead line of ``RANK_SENSITIVITY_READING_RULES``, shared by every reader of the rank sweep."""
    return [
        "## Reading rules of the rank sweep",
        "",
        "Binding for every reader of the rank sweep (`RANK_SENSITIVITY_READING_RULES`, decided by "
        f"`{RANK_SENSITIVITY_LADDER['change']}` before any run), after `READING_RULES`:",
    ]


def _anchor_text(anchor: dict) -> str:
    """The anchor gate's result in one clause, from its record (``_check_anchor``): the rank, what was compared and found equal, and what was not compared.

    The compared fields are listed in the gate's order (``_ANCHOR_FIELD_ORDER``),
    whatever the order of ``anchor["fields"]``: a manifest stores the record
    with sorted keys, and the clause read back from it must equal the one the
    step printed (design D5 of ``adni-report-rank-sweep``).
    """
    names = [*(n for n in _ANCHOR_FIELD_ORDER if n in anchor["fields"]), *(n for n in anchor["fields"] if n not in _ANCHOR_FIELD_ORDER)]
    fields = ", ".join(f"`{name}`" for name in names)
    files = ", ".join(f"`{name}`" for name in anchor["files"])
    text = (
        f"a forced run at the primary's rank {anchor['rank']} reproduced the primary before any rank ran: {fields} equal "
        f"to the primary record's, and {files} hash to the values the primary manifest records"
    )
    if anchor["not_compared"]:
        text += (
            f" (at n_jobs = {anchor['n_jobs']} the permutation draws are not the primary's, so "
            + ", ".join(f"`{name}`" for name in anchor["not_compared"]) + " were not compared)"
        )
    return text


def _rank_sweep_lines(sweep: dict) -> list[str]:
    """The "Rank sweep" lines of a forced rank's ``summary.md``, from the ``rank_sweep`` block its manifest records (design D6 of ``adni-rank-sensitivity``).

    The ladder (``RANK_SENSITIVITY_LADDER``), this rank's place in it, the
    nesting of its latent space relative to the primary's CV-selected rank
    (the primary's first k components, the primary's itself, or the primary's
    plus components the cross-validation did not select), the anchor gate's
    result and the rank-specific loadings. No statistic is computed here.
    """
    ladder, k, r = sweep["ladder"], int(sweep["forced_rank"]), int(sweep["primary_rank"])
    ranks = [int(x) for x in ladder["ranks"]]
    if k < r:
        nesting = (
            f"at rank {k}, below the primary's rank {r} (selected by its cross-validation), the latent space is spanned "
            f"by the primary's first {k} components"
        )
    elif k == r:
        nesting = f"at rank {k}, the primary's rank (selected by its cross-validation), the latent space is the primary's"
    else:
        nesting = (
            f"at rank {k}, above the primary's rank {r} (selected by its cross-validation), the latent space holds the "
            f"primary's {r} components and {k - r} component(s) the cross-validation did not select"
        )
    anchor = sweep.get("anchor")
    step = f"step {ranks.index(k) + 1} of {len(ranks)} of the ladder" if k in ranks else "the anchor, not a step of the ladder"
    return [
        f"- ladder: `{ladder['name']}` (`RANK_SENSITIVITY_LADDER`, change `{ladder['change']}`): ranks "
        + ", ".join(str(x) for x in ranks) + f"; the one setting `{ladder['setting']}`; {ladder['draws']}",
        f"- this rank: {k}, {step}; the primary's rank {r} is the anchor"
        + ("" if r in ranks else ", not a step of the ladder"),
        f"- nesting (sweep rule 3): PLS-DA components are nested; {nesting}; the comparison manifest records the check "
        "of every rank's scores against the top rank's and the anchor's",
        "- anchor (sweep rule 3): " + (_anchor_text(anchor) if anchor else "this run is the anchor itself, compared with "
                                       "the primary and then removed"),
        "- loadings: `pls_loadings.csv` (MOTCO's rotations) depends on the rank and is not nested; its columns are "
        "this rank's own and are never read against another rank's",
    ]


def _stage_arm_rules_heading() -> list[str]:
    """The heading and lead line of ``STAGE_SENSITIVITY_READING_RULES``, shared by every reader of the CN / LMCI / AD arm."""
    return [
        "## Reading rules of the CN / LMCI / AD arm",
        "",
        "Binding for every reader of the CN / LMCI / AD arm (`STAGE_SENSITIVITY_READING_RULES`, decided by "
        f"`{STAGE_SENSITIVITY_ARM['change']}` before any run), after `READING_RULES`:",
    ]


def _stage_arm_definition(arm: dict) -> str:
    """The arm's participants and stages in one clause, from its constant as a manifest records it (``stage_arm``)."""
    keep, drop = [str(dx) for dx in arm["keep"]], [str(dx) for dx in arm["drop"]]
    return (
        f"the primary export's rows of the participants whose `DX.bl` is {', '.join(keep[:-1])} or {keep[-1]}, staged "
        "by `STAGE_RULE`'s map (" + ", ".join(f"{dx} → {arm['stage_map'][dx]}" for dx in keep) + "), "
        + " and ".join(drop) + " dropped"
    )


def _stage_arm_tables(export_manifest: dict) -> list[tuple[list[str], str, list[list[str]]]]:
    """The four tables of the arm's definition, each as (header, alignment, rows of cells), every value read from the arm export manifest.

    In order: the exported participants by ``dx_bl`` × sex with the
    categories the arm keeps (``counts.dx_bl``), the sex × stage cells, the
    runs within each stage and the covariate levels of the primary
    (``reference``) and of the arm (``counts``). The alignment holds one
    ``l``, ``r`` or ``c`` per column. ``_stage_arm_lines`` prints them under
    its lead lines (the arm's ``summary.md`` and ``stage_sensitivity.md``)
    and the report under its own level-3 headings (design D5 of
    ``adni-report-stage-arm``), so the rows are string-equal across the
    documents. Keys are taken in the constants' orders (``STAGE_RULE``,
    ``GROUP_VALUES``, ``STAGE_LABELS``, the covariate levels), never in the
    manifest's, which is written with sorted keys.
    """
    arm, reference = export_manifest["stage_arm"], export_manifest.get("reference", {})
    counts = export_manifest.get("counts", {})
    keep = [str(dx) for dx in arm["keep"]]
    phase_levels = [str(level) for level in ANALYSIS_COVARIATES["phase"]["levels"]]
    by_dx = counts.get("dx_bl", {})
    dx_rows = []
    for dx, stage in STAGE_RULE["map"].items():
        cells = by_dx.get(dx, {})
        dx_rows.append([
            dx, stage, "yes" if dx in keep else "no", *(str(cells.get(g, 0)) for g in GROUP_VALUES),
            str(sum(cells.get(g, 0) for g in GROUP_VALUES)),
        ])
    p_cells, a_cells = reference.get("sex_stage", {}), counts.get("sex_stage", {})
    p_runs, a_runs = reference.get("phase_by_stage", {}), counts.get("phase_by_stage", {})
    p_levels, a_levels = reference.get("covariate_levels", {}), counts.get("covariate_levels", {})
    return [
        (["`dx_bl`", "stage", "in the arm", *GROUP_VALUES, "total"], "llc" + "r" * (len(GROUP_VALUES) + 1), dx_rows),
        (
            ["sex", *(f"{st} primary" for st in STAGE_LABELS), *(f"{st} arm" for st in STAGE_LABELS)],
            "l" + "r" * (2 * len(STAGE_LABELS)),
            [
                [g, *(str(p_cells.get(g, {}).get(st)) for st in STAGE_LABELS), *(str(a_cells.get(g, {}).get(st)) for st in STAGE_LABELS)]
                for g in GROUP_VALUES
            ],
        ),
        (
            ["stage", *(f"{r} primary" for r in phase_levels), *(f"{r} arm" for r in phase_levels)],
            "l" + "r" * (2 * len(phase_levels)),
            [
                [st, *(str(p_runs.get(st, {}).get(r)) for r in phase_levels), *(str(a_runs.get(st, {}).get(r)) for r in phase_levels)]
                for st in STAGE_LABELS
            ],
        ),
        (
            ["covariate", "level", "primary", "arm"],
            "llrr",
            [
                [f"`{name}`", level, str(p_levels.get(name, {}).get(level)), str(a_levels.get(name, {}).get(level))]
                for name in ANALYSIS_CATEGORICAL_COVARIATES
                for level in (str(v) for v in ANALYSIS_COVARIATES[name]["levels"])
            ],
        ),
    ]


def _stage_arm_lines(export_manifest: dict) -> list[str]:
    """The "Arm" lines of the arm's ``summary.md`` and of ``stage_sensitivity.md``, every value read from the arm export manifest.

    The arm (``stage_arm``), the primary export it is a row subset of
    (``reference``), the rows equal to the primary's
    (``counts.rows_equal_primary``), the four tables of
    ``_stage_arm_tables`` each under its lead line, and the run offset per
    block of both. Keys are taken in the constants' orders
    (``EXPORT_BLOCKS`` for the blocks), never in the manifest's, which is
    written with sorted keys.
    """
    arm, reference = export_manifest["stage_arm"], export_manifest.get("reference", {})
    counts = export_manifest.get("counts", {})
    rows_equal = counts.get("rows_equal_primary", {})
    files = [*(f"{p}.csv" for p in EXPORT_BLOCKS), EXPORT_METADATA, EXPORT_COVARIATES]
    tables = reference.get("feature_tables", {})
    lines = [
        f"- arm: `{arm['name']}` (`STAGE_SENSITIVITY_ARM`, change `{arm['change']}`): {_stage_arm_definition(arm)}",
        f"- read beside the primary export `{reference.get('dir')}` (`{EXPORT_MANIFEST}` sha256 "
        f"`{(reference.get('manifest') or {}).get('sha256')}`): the arm's rows are its rows, every cell unchanged, so the "
        "floors are the primary's (" + ", ".join(
            f"`{name}` sha256 `{(tables.get(name) or {}).get('sha256')}`" for name in sorted(tables)
        ) + "); rows equal to the primary's: " + ", ".join(
            f"{name} {'yes' if rows_equal.get(name) else 'no'}" for name in files
        ),
        f"- participants: {counts.get('participants')} of the primary's {reference.get('participants')}; dropped: "
        + ", ".join(f"{dx} {counts.get('dropped', {}).get(dx)}" for dx in arm["drop"]),
    ]
    leads = [
        f"Exported participants by `{arm['source']}` (`STAGE_RULE` maps it onto the stage):",
        "Sex × stage cells:",
        "Runs within each stage (`phase`):",
        "Covariate levels:",
    ]
    separator = {"l": "---|", "r": "---:|", "c": ":---:|"}
    for lead, (header, align, rows) in zip(leads, _stage_arm_tables(export_manifest)):
        lines += [
            "",
            lead,
            "",
            "| " + " | ".join(header) + " |",
            "|" + "".join(separator[a] for a in align),
            *("| " + " | ".join(row) + " |" for row in rows),
        ]
    primary_offset, offsets = reference.get("phase_offset", {}), counts.get("phase_offset", {})
    lines.append("")
    for p in EXPORT_BLOCKS:
        lines.append(
            f"- {p} run offset (`phase`, ADNI1 against ADNI2GO): primary {_offset_text(primary_offset.get(p, {}))}; "
            f"arm {_offset_text(offsets.get(p, {}))}"
        )
    return lines


#: The name of each block in the sentences of a variant's readers (design D4
#: of ``adni-nmr-all-columns``).
_BLOCK_TEXT: dict[str, str] = {"p180": "p180", "nmr": "NMR"}


def _variant_words(variant: str) -> dict:
    """The words every reader of a variant prints (designs D3 and D4 of ``adni-nmr-all-columns``).

    The variant's entry of ``EXPORT_VARIANT_RULE_SETS`` (``rules``, ``change``,
    ``cite``, ``dependence``, ``source``, ``heading``, ``reader``), with
    ``rule_tuple`` (the rules themselves), ``differs`` (the status of a
    statistic whose rejection differs from the primary's) and, from the
    variant's block and hook in ``EXPORT_VARIANTS``: ``kept`` (the blocks it
    keeps), ``changes`` (what it changes, as its rule 2 says it), ``does`` and
    ``whose``. A variant of the p180 run keeps the words its committed
    outputs print.
    """
    spec, entry = EXPORT_VARIANTS[variant], EXPORT_VARIANT_RULE_SETS[variant]
    block = _BLOCK_TEXT[spec["block"]]
    if spec["hook"] == "membership":
        changes, does, whose = f"the {block} block's membership", f"changes the {block} block's membership", f"{block} block membership"
    else:
        changes, does, whose = f"the {block} values", f"handles the {block} run", f"{block} run handling"
    return {
        **entry,
        "rule_tuple": getattr(constants, entry["rules"]),
        "differs": f"differs ({entry['dependence']})",
        "kept": ", ".join(f"the {_BLOCK_TEXT[p]} block" for p in EXPORT_BLOCKS if p != spec["block"]),
        "changes": changes,
        "does": does,
        "whose": whose,
    }


def _export_variant_status_differs(variant: str) -> str:
    """The status of a statistic whose rejection differs between the primary and the variant: ``differs (<dependence>)``."""
    return _variant_words(variant)["differs"]


def _export_variant_rules_heading(variant: str) -> list[str]:
    """The heading and lead line of a variant's reading rules (``EXPORT_VARIANT_RULE_SETS``), shared by every reader of the variant."""
    words = _variant_words(variant)
    return [
        f"## {words['heading']}",
        "",
        f"Binding for every reader of {words['reader']} (`{words['rules']}`, decided by `{words['change']}` before any "
        "run), after `READING_RULES`:",
    ]


def _export_variant_rules_lines(variant: str) -> list[str]:
    """The heading, lead line and numbered rules of a variant's rule set, printed after ``READING_RULES``."""
    return [*_export_variant_rules_heading(variant), "", *(f"{i}. {rule}" for i, rule in enumerate(_variant_words(variant)["rule_tuple"], 1))]


def _export_variant_phase_line(variant: str) -> str:
    """The ``phase`` line of a variant's export context in ``summary.md`` (design D4 of ``adni-nmr-all-columns``)."""
    spec, words = EXPORT_VARIANTS[variant], _variant_words(variant)
    lead = "- `phase` enters as a covariate of the stage means (above), as in the primary; "
    if spec["hook"] == "membership":
        return (
            lead + f"the variant changes the {_BLOCK_TEXT[spec['block']]} membership only ({words['cite']} 2) and `phase` "
            "carries the run difference, as in the primary"
        )
    return lead + f"the variant changes {words['changes']} only ({words['cite']} 2) and `phase` carries what remains of the run difference"


def _offset_text(offset: dict) -> str:
    """One block's run offset as the export manifest records it (``counts.phase_offset``)."""
    return (
        f"median |d| {_fmt(offset.get('median_abs_d'), '.2f')}, |d| > 0.5 for {offset.get('abs_d_gt_0_5')} and > 1 for "
        f"{offset.get('abs_d_gt_1')} metabolite(s), |corr(PC1, phase)| {_fmt(offset.get('abs_corr_pc1_phase'), '.2f')}, "
        f"|corr(PC2, phase)| {_fmt(offset.get('abs_corr_pc2_phase'), '.2f')}"
    )


def _export_variant_lines(export_manifest: dict) -> list[str]:
    """The "Export variant" lines of a variant's ``summary.md``, every value read from the variant export manifest.

    The variant (``variant``), the primary export it is read beside
    (``reference``) with the blocks the variant keeps, the assay runs of the
    exported participants (``counts.runs``), for ``nist_bridge`` the bridge
    summary and table (``bridge``), for a variant with hook ``membership``
    (``nmr_all_columns``, design D4 of ``adni-nmr-all-columns``) the block's
    membership with the derived columns kept, the rule's columns equal to
    the primary's (``counts.rule_columns_equal_primary``), the joint
    features, the block shares and the block's shape counts, and the run
    offset per block, the primary's (copied into ``reference.phase_offset``)
    then the variant's (``counts.phase_offset``). Keys are taken in the
    constants' orders, never in the manifest's, which is written with sorted
    keys.
    """
    variant, reference = export_manifest["variant"], export_manifest.get("reference", {})
    counts = export_manifest.get("counts", {})
    runs = counts.get("runs", {})
    lines = [
        f"- variant: `{variant['name']}` (`EXPORT_VARIANTS`, change `{variant['change']}`): {variant['setting']}",
        f"- read beside the primary export `{reference.get('dir')}` (`{EXPORT_MANIFEST}` sha256 "
        f"`{(reference.get('manifest') or {}).get('sha256')}`); the participants, {_variant_words(variant['name'])['kept']}, "
        "the metadata and the covariates are the primary's",
        f"- assay run of the exported participants (`{CLEAN_RUNS_TABLE}`): " + ", ".join(f"{r} {n}" for r, n in runs.items())
        + f"; {counts.get('runs_differing_from_phase')} differ from `phase`",
    ]
    if variant["hook"] == "membership":
        block = variant["block"]
        features = counts.get("features", {}).get(block, {})
        derived_kept = features.get("derived_kept", {})
        n_rule = features.get("kept", 0) - sum(derived_kept.get(fam, 0) for fam in _DERIVED_FAMILIES)
        shape = counts.get("shape", {}).get(block, {})
        shares = counts.get("block_shares", {})
        equal = counts.get("rule_columns_equal_primary")
        lines += [
            f"- {block} membership (hook `membership`): {features.get('kept')} of {features.get('cleaned')} cleaned "
            f"column(s), the {n_rule} `EXPORT_FEATURE_RULE` keeps and the derived ones it excludes ("
            + ", ".join(f"{fam} {derived_kept.get(fam, 0)}" for fam in _DERIVED_FAMILIES)
            + "), each on the rule's scale with its own floor; the rule's columns equal the primary "
            f"`{block}.csv`'s, column for column and cell for cell: {'n/a' if equal is None else ('yes' if equal else 'no')}",
            f"- joint features {counts.get('joint_features')}; block shares (unweighted in MOTCO): "
            + ", ".join(f"{p} {_fmt(shares.get(p), '.3f')}" for p in EXPORT_BLOCKS),
            f"- {block} block shape on the rule's scale: |skew| > 1 for {shape.get('abs_skew_gt_1')} column(s), largest "
            f"|z| > 8 for {shape.get('max_abs_z_gt_8')}",
        ]
    bridge = export_manifest.get("bridge")
    if bridge:
        summary, table = bridge["summary"], bridge["table"]
        q = summary.get("factor_log2_bridged") or {}
        bridged = summary["p180_bridged"]
        lines += [
            f"- NIST SRM 1950 bridge (`NIST_BRIDGE_RULE`): {summary['metabolites']} p180 metabolite(s), bridged "
            + ", ".join(f"{k} {n}" for k, n in bridged.items() if k != "not_bridged")
            + f", not bridged {bridged['not_bridged']} (factor 1: " + (", ".join(f"`{m}`" for m in summary['not_bridged']) or "none")
            + "); no NIST column: " + (", ".join(f"`{m}`" for m in summary["unmatched"]) or "none"),
            "- log2 factor b over the bridged metabolites (ADNI1 minus ADNI2GO; ADNI2GO concentrations multiplied by "
            "2^b): q05 / q25 / q50 / q75 / q95 " + " / ".join(_fmt(q.get(k), "+.3f") for k in ("q05", "q25", "q50", "q75", "q95"))
            + f"; median |b| {_fmt(q.get('median_abs'), '.3f')}; b > 0 for {q.get('positive')}",
            f"- bridge table `{table['name']}` (sha256 `{table['sha256']}`): per metabolite the replicates, valid "
            "replicates, ISTD flags, run means and plate-clustered SEs, b and whether it is bridged",
        ]
    primary_offset = reference.get("phase_offset", {})
    offsets = counts.get("phase_offset", {})
    for p in EXPORT_BLOCKS:
        lines.append(
            f"- {p} run offset (`phase`, ADNI1 against ADNI2GO): primary {_offset_text(primary_offset.get(p, {}))}; "
            f"variant {_offset_text(offsets.get(p, {}))}"
        )
    return lines


def _run_trajectory_analysis(
    *,
    input_dir: Path,
    final: Path,
    n_jobs: int,
    force: bool,
    step: str,
    latent_adjustment: str | None,
    expected: dict,
    manifest_extra: dict | Callable[[dict], dict] | None = None,
    loaded: dict | None = None,
    staging: Path | None = None,
    log: str | None = None,
    forced_components: int | None = None,
    rank_sweep: dict | None = None,
) -> dict:
    """One ``analyze_trajectories`` call written as an analysis directory, shared by ``analyze`` and the four sensitivity steps.

    Parameters
    ----------
    input_dir, final:
        The export directory and the analysis directory the step promises.
    n_jobs, force:
        The caller's flags (``n_jobs``: MOTCO's CV and RRPP workers; ``force``:
        replace an existing ``final``).
    step:
        The calling step, ``analyze``, ``latent-sensitivity``,
        ``export-sensitivity``, ``stage-sensitivity`` or ``rank-sensitivity``:
        the printed prefix, the manifest's ``step`` and the name in the
        loader's messages.
    latent_adjustment:
        ``TrajectoryAnalysisParams.covariate_latent_adjustment``:
        ``ANALYSIS_LATENT_ADJUSTMENT`` (``None``) for the primary,
        ``LATENT_SENSITIVITY_ARM["conditioning"]`` (``stage``) for the arm.
        The only setting that differs between the two callers.
    expected:
        The predeclared counts the record is compared with
        (``ANALYSIS_EXPECTED_COUNTS`` or ``LATENT_SENSITIVITY_EXPECTED_COUNTS``);
        every deviation is a finding.
    manifest_extra:
        Top-level keys added to the manifest: a dict, or a callable of the
        record (after the call) returning one. Its ``findings`` entry, if any,
        is appended to the findings after those of the analysis and before the
        numeric state is recorded.
    loaded:
        ``_load_analysis_inputs(input_dir, step=step)`` when the caller has
        already read and checked the export, which is then not read twice;
        ``None`` reads it here.
    staging:
        An existing, empty directory to write the outputs into when the
        caller stages the directory itself (``latent-sensitivity`` renames
        ``analysis.tmp/`` and ``comparison.tmp/`` together); ``None`` stages
        ``<final>.tmp/`` here and renames it when complete.
    log:
        The printed prefix when it is not ``[<step>]`` (``export-sensitivity``
        names the variant).
    forced_components:
        ``TrajectoryAnalysisParams.forced_components``: ``None`` (the
        default, MOTCO's double-CV rank selection) for every caller but
        ``rank-sensitivity``, which passes one rank of
        ``RANK_SENSITIVITY_LADDER`` (or the primary's rank, for the anchor;
        change ``adni-rank-sensitivity``). A forced rank skips MOTCO's
        cross-validation; the manifest then records
        ``settings.forced_components``, ``cli_equivalent`` carries
        ``--forced-components`` and the three findings that read the
        cross-validation are not raised (see Notes). The default leaves every
        byte as it was.
    rank_sweep:
        For a forced rank of ``rank-sensitivity``: the ladder
        (``RANK_SENSITIVITY_LADDER`` with its constant name), the forced rank,
        the primary's rank and the anchor gate's record, recorded in the
        manifest under ``rank_sweep`` and passed to
        ``render_analysis_summary``, which then renders the sweep's sections;
        ``None`` (the default) for every other caller, whose bytes are
        unchanged.

    Returns
    -------
    dict
        ``{"dir": Path, "record": dict, "manifest": dict, "findings": [...], "names": [...]}``
        (``names``: the files written, without the manifest).

    Notes
    -----
    Everything but ``latent_adjustment`` and ``forced_components`` is fixed
    here: the gates, the loader,
    the dataset (blocks in ``EXPORT_BLOCKS`` order, transform
    ``EXPORT_FEATURE_RULE``'s, the ``ANALYSIS_COVARIATES`` with
    ``ANALYSIS_CATEGORICAL_COVARIATES`` categorical, missing policy
    ``ANALYSIS_MISSING_COVARIATES``), ``TrajectoryAnalysisParams(
    permutations=ANALYSIS_PERMUTATIONS, seed=ANALYSIS_SEED, n_jobs,
    min_components=ANALYSIS_RANK_FLOOR, covariate_latent_adjustment=
    latent_adjustment)``, the counts, the findings, the manifest, the summary
    and the output directory, as ``run_analysis`` documents them. With
    ``step="analyze"``, ``latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT`` and
    ``expected=ANALYSIS_EXPECTED_COUNTS`` it is ``run_analysis``, whose
    outputs it reproduces byte for byte (the gate of
    ``adni-latent-sensitivity``). When the record carries a
    ``latent_adjustment`` block, the counts gain it (conditioning,
    covariates, design columns, samples, residual df, smallest CV training df,
    feature scale, ``feature_r2``) and ``render_analysis_summary`` renders the
    arm's sections; otherwise every byte is the primary's.

    On a forced record (``latent.component_selection`` ``forced``) MOTCO
    skips the cross-validation, so ``cv_repeats_completed`` is 0 and
    ``integration_params`` holds no CV key and no ``min_components``: the
    fewer-CV-repeats finding and the CV-floor finding are not raised (the
    floor is recorded in the counts and does not bind a forced run), and the
    moved-default check of ``forced_components`` expects the rank passed
    instead of ``None``, so a record whose ``forced_components`` differs
    from it is still a finding. Every other finding is unchanged.
    """
    log = log or f"[{step}]"
    motco_version = check_motco_version()
    rank_floor = check_motco_rank_floor()
    from motco.analysis import (
        OmicsBlock,
        TrajectoryAnalysisParams,
        TrajectoryDataset,
        analyze_trajectories,
        write_analysis_outputs,
    )

    if final.exists() and not force:
        raise FileExistsError(f"{final} exists; pass --force to replace it")
    print(f"{log} MOTCO {motco_version}; rank floor {rank_floor} equals MOTCO's default")

    # --- inputs ---------------------------------------------------------------
    if loaded is None:
        loaded = _load_analysis_inputs(input_dir, step=step)
    findings: list[str] = list(loaded["findings"])
    blocks, frame, export_manifest = loaded["blocks"], loaded["metadata"], loaded["export_manifest"]
    for name, rec in loaded["inputs"].items():
        print(f"{log} {name}: sha256 {rec['sha256'][:16]}…" + (f" equals {EXPORT_MANIFEST}" if "recorded" in rec else ""))
    sex_stage = _sex_stage(frame)
    cells = "; ".join(
        f"{sex_} {'/'.join(STAGE_LABELS)} " + "/".join(str(n) for n in sex_stage[sex_].values()) for sex_ in GROUP_VALUES
    )
    n_features = {p: int(blocks[p].shape[1]) for p in EXPORT_BLOCKS}
    print(
        f"{log} participants: {len(frame)} ({cells}); features "
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
        covariate_latent_adjustment=latent_adjustment,
        forced_components=forced_components,
    )
    design = dataset.covariate_design
    print(f"{log} design columns: {len(design.column_names)} (" + ", ".join(design.column_names) + ")")
    selection = (
        f"CV rank selection (floor {params.resolved_min_components})" if forced_components is None
        else f"forced rank {forced_components} (no cross-validation)"
    )
    print(
        f"{log} {selection} + {params.permutations} RRPP "
        f"permutations, seed {params.seed}, n_jobs {n_jobs}, latent adjustment {params.covariate_latent_adjustment}…"
    )

    # --- the one call -------------------------------------------------------------
    result = analyze_trajectories(dataset, params)
    record = result.record
    latent, meas = record["latent"], record["measurement"]
    print(
        f"{log} rank {latent['selected_lv']} ({latent['component_selection']}), cv_mean_auroc "
        f"{_fmt(latent.get('cv_mean_auroc'), '.4f')}, {latent.get('cv_repeats_completed')} CV repeat(s), "
        f"{meas['runtime_seconds']:.1f} s"
    )
    rejected = {s: _rejected(record["p_values"].get(s)) for s in ANALYSIS_STATISTICS}
    for s in ANALYSIS_STATISTICS:
        verdict = "no p-value" if rejected[s] is None else ("rejected" if rejected[s] else "not rejected")
        print(f"{log} {s}: {_fmt(record['statistics'].get(s))} (p {_fmt(record['p_values'].get(s))}, {verdict} at α = {ANALYSIS_ALPHA})")
    adjustment = record.get("latent_adjustment")
    if adjustment:
        print(
            f"{log} latent adjustment: conditioning {adjustment['conditioning']}, residualization design "
            f"{len(adjustment['design_columns'])} column(s), residual df {adjustment['residual_df']}, smallest CV "
            f"training df {adjustment.get('cv_min_training_df')}, feature R² median {_fmt(adjustment['feature_r2'].get('q50'), '.3f')}"
        )

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
    if adjustment:
        counts["latent_adjustment"] = {
            key: adjustment.get(key)
            for key in ("conditioning", "covariates", "design_columns", "n_samples", "residual_df",
                        "cv_min_training_df", "feature_scale", "feature_r2")
        }
    expected = json.loads(json.dumps(expected))
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
    # A forced rank skips the cross-validation: its repeats and floor are not findings (design D5 of adni-rank-sensitivity).
    forced = latent["component_selection"] == "forced"
    n_repeats = params.n_repeats
    if not forced and latent.get("cv_repeats_completed") is not None and latent["cv_repeats_completed"] < n_repeats:
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
        if key == "forced_components" and forced_components is not None:
            if used != forced_components:
                findings.append(
                    f"MOTCO default {key} is {used!r} in the record but the run passed {forced_components!r} (the forced rank)"
                )
        elif used != stated:
            findings.append(f"MOTCO default {key} is {used!r} in the record but the proposal states {stated!r}")
    cv_used = latent.get("integration_params", {})
    for key in _MOTCO_CV_KEYS:
        if key in cv_used and cv_used[key] != record["params"].get(key):
            findings.append(f"MOTCO clamped the CV setting {key} from {record['params'].get(key)!r} to {cv_used[key]!r}")
    if not forced and (cv_used.get("min_components", 1)) != rank_floor:
        findings.append(f"the CV ran with rank floor {cv_used.get('min_components', 1)}, not ANALYSIS_RANK_FLOOR = {rank_floor}")
    extra = dict(manifest_extra(record) if callable(manifest_extra) else (manifest_extra or {}))
    findings += list(extra.pop("findings", []))

    numerics, numerics_findings = _numerics(log)
    findings += numerics_findings
    versions = _software_versions((*_MANIFEST_PACKAGES, "motco", "scikit-learn"))
    manifest = {
        "step": step,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": versions,
        "numerics": numerics,
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
            "latent_adjustment": latent_adjustment,
            "predeclared_sensitivity": ANALYSIS_PREDECLARED_LATENT_SENSITIVITY,
            "cli_equivalent": _analysis_cli_equivalent(
                input_dir, final / ANALYSIS_METADATA, params, n_jobs, forced_components=forced_components
            ),
        },
        "counts": counts,
        "expected": expected,
        "deviations": deviations,
        "findings": findings,
        **extra,
    }
    if forced_components is not None:
        manifest["settings"]["forced_components"] = forced_components
    if rank_sweep is not None:
        manifest["rank_sweep"] = rank_sweep

    # --- outputs ----------------------------------------------------------------------
    participant_level = {ANALYSIS_LATENT_SCORES, ANALYSIS_METADATA}

    def write(tmp: Path) -> list[str]:
        written = write_analysis_outputs(result, tmp)
        (tmp / ANALYSIS_METADATA).write_text(metadata_csv)
        (tmp / ANALYSIS_SUMMARY).write_text(
            render_analysis_summary(record, export_manifest=export_manifest, n_jobs=n_jobs, rank_sweep=rank_sweep)
        )
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
        return names

    if staging is None:
        with _finalize_output_dir(final, force=force) as tmp:
            names = write(tmp)
        where = final
    else:
        names = write(staging)
        where = staging

    print(f"{log} wrote {where}/ (" + ", ".join([*names, ANALYSIS_MANIFEST]) + ")")
    if deviations:
        print(f"{log} {len(deviations)} count deviation(s) from the predeclared counts")
    else:
        print(f"{log} counts reproduce the predeclared ones")
    for msg in findings:
        print(f"{log} FINDING: {msg}")
    return {"dir": final, "record": record, "manifest": manifest, "findings": findings, "names": names}


def run_analysis(
    *,
    input_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    n_jobs: int = REPORTED_N_JOBS,
    force: bool = False,
) -> dict:
    """Run the covariate-adjusted MOTCO sex × stage trajectory comparison (the primary analysis).

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
    The body is ``_run_trajectory_analysis`` with ``step="analyze"``,
    ``latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT`` and
    ``expected=ANALYSIS_EXPECTED_COUNTS``; the ``latent-sensitivity`` step
    calls the same function with the arm's setting (change
    ``adni-latent-sensitivity``), and the primary's outputs are its byte
    gate.

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
    adjustment is the predeclared sensitivity arm, run by
    ``latent-sensitivity`` beside this primary and never replacing it.

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

    The manifest's ``numerics`` block records the numeric environment the run
    actually had (``_numerics_record``: host, CPU, the ``NUMERIC_SETTINGS``
    variables, numpy's ``log2`` target, each BLAS library's kernel and
    threads, ``pinned``); a run that is not pinned is a finding, never a
    stop, and its outputs are not committed.
    """
    input_dir = Path(input_dir) if input_dir is not None else Path(MOTCO_INPUT_DIR)
    final = Path(out_dir) if out_dir is not None else Path(MOTCO_ANALYSIS_DIR)
    out = _run_trajectory_analysis(
        input_dir=input_dir,
        final=final,
        n_jobs=n_jobs,
        force=force,
        step="analyze",
        latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT,
        expected=ANALYSIS_EXPECTED_COUNTS,
    )
    return {key: out[key] for key in ("dir", "record", "manifest", "findings")}


# --- axis-diagnostics -----------------------------------------------------------

#: The columns of the four diagnostic tables, in order.
_DIAGNOSTICS_AXIS_COLUMNS: tuple[str, ...] = (
    "component", "component_sd", "variable", "source", "n", "spearman", "n_partial", "partial_spearman",
    "flag_raw", "flag_partial",
)
_DIAGNOSTICS_PC_COLUMNS: tuple[str, ...] = (
    "block", "component", "variance_share", "variable", "source", "n", "spearman", "n_partial",
    "partial_spearman", "flag_raw", "flag_partial",
)
_DIAGNOSTICS_GEOMETRY_COLUMNS: tuple[str, ...] = ("quantity", "component", "value", "along", "total", "share")
_DIAGNOSTICS_COMPONENT_COLUMNS: tuple[str, ...] = (
    "component", "sd", *(f"loading_share_{p}" for p in EXPORT_BLOCKS), "n_flagged_raw", "n_flagged_partial",
    "top_variable", "top_spearman",
)
#: The definition of every statistic the diagnostic writes, recorded in its manifest.
_DIAGNOSTICS_DEFINITIONS: dict[str, str | dict] = {
    "spearman": "scipy.stats.spearmanr over the participants with both values finite (n recorded); undefined "
    "(empty) with fewer than three such rows or a constant",
    "partial_spearman": "Spearman correlation of the OLS residuals of the component and the variable on an intercept "
    f"and the {len(DIAGNOSTIC_CONDITIONING_COLUMNS)} design columns of the record, over the participants complete in "
    "all; undefined (empty) for a variable in the span of the conditioning set, as each analysis covariate is",
    "component_sd": "sample SD (ddof 1) of the component's latent scores over the exported participants",
    "flag": f"|rho| >= DIAGNOSTIC_CORRELATION_THRESHOLD ({DIAGNOSTIC_CORRELATION_THRESHOLD}), raw and partial "
    "separately; a reporting threshold, not an adoption rule; no p-value",
    "block_pcs": f"SVD of the block z-scored with the population SD; the first {DIAGNOSTIC_N_BLOCK_PCS} components' "
    "scores U S, each sign fixed so that its largest-magnitude loading is positive; variance_share = s^2 / sum s^2 "
    "over all components",
    "pc1_phase": "Spearman correlation of each block's pc1 with the phase variable, recorded beside the export "
    "manifest's abs_corr_pc1_phase (Pearson, first left-singular vector against the ADNI1 indicator) as a "
    "cross-check with no agreement threshold",
    "geometry": DIAGNOSTICS_GEOMETRY_QUANTITIES,
    "geometry_share": "squared length along the component over the squared length over all components, from "
    "stage_means.csv",
    "loading_share": "per component, the sum of the squared pls_loadings.csv entries (MOTCO's x_rotations_ on the "
    "z-scored joint features) over a block's rows, over the sum over all rows; the blocks enter MOTCO unweighted",
}


def spearman(x, y) -> tuple[float, int]:
    """Spearman correlation over the pairwise-complete values.

    Parameters
    ----------
    x, y:
        The two variables, one value per participant.

    Returns
    -------
    (float, int)
        The correlation and the number of rows finite in both; NaN with
        fewer than three such rows or a constant.
    """
    import warnings

    from scipy.stats import spearmanr

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    n = int(ok.sum())
    if n < 3 or np.ptp(x[ok]) == 0 or np.ptp(y[ok]) == 0:
        return float("nan"), n
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rho = spearmanr(x[ok], y[ok]).statistic
    return float(rho), n


def partial_spearman(x, y, z) -> tuple[float, int]:
    """Spearman correlation of the OLS residuals of ``x`` and ``y`` on an intercept and ``z``.

    Parameters
    ----------
    x, y:
        The two variables.
    z:
        Conditioning variables, participants × columns.

    Returns
    -------
    (float, int)
        The partial correlation and the number of rows complete in all
        three; NaN when fewer than ``z.shape[1] + 3`` rows are complete or
        when a variable lies in the span of the conditioning set (its
        residual is numerically zero, as for an analysis covariate itself).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)
    if z.ndim == 1:
        z = z[:, None]
    ok = np.isfinite(x) & np.isfinite(y) & np.all(np.isfinite(z), axis=1)
    n = int(ok.sum())
    if n < z.shape[1] + 3:
        return float("nan"), n
    design = np.column_stack([np.ones(n), z[ok]])
    residuals = []
    for v in (x[ok], y[ok]):
        beta = np.linalg.lstsq(design, v, rcond=None)[0]
        r = v - design @ beta
        if np.std(r) <= 1e-8 * max(np.std(v), np.finfo(float).tiny):
            return float("nan"), n
        residuals.append(r)
    return spearman(residuals[0], residuals[1])[0], n


def block_principal_components(values: pd.DataFrame, *, n_components: int = DIAGNOSTIC_N_BLOCK_PCS) -> dict:
    """Principal components of a z-scored block (population SD).

    Parameters
    ----------
    values:
        Participants × features (one exported block).
    n_components:
        Components returned.

    Returns
    -------
    dict
        ``scores`` (participants × ``pc1..``, the SVD scores ``U S``),
        ``loadings`` (features × ``pc1..``, the right-singular vectors),
        ``variance_share`` per component (``s² / Σ s²`` over all
        components) and ``n_features``. Each component's sign is fixed so
        that its largest-magnitude loading is positive. A constant feature
        is left at zero.
    """
    x = np.asarray(values, dtype=float)
    mu = x.mean(axis=0)
    sd = x.std(axis=0, ddof=0)
    sd = np.where(sd > 0, sd, 1.0)
    zed = (x - mu) / sd
    u, s, vt = np.linalg.svd(zed, full_matrices=False)
    k = min(n_components, s.size)
    scores = u[:, :k] * s[:k]
    loadings = vt[:k].T.copy()
    for j in range(k):
        lead = np.argmax(np.abs(loadings[:, j]))
        if loadings[lead, j] < 0:
            scores[:, j] = -scores[:, j]
            loadings[:, j] = -loadings[:, j]
    share = (s**2) / float((s**2).sum()) if s.size else np.array([])
    cols = [f"pc{j + 1}" for j in range(k)]
    return {
        "scores": pd.DataFrame(scores, index=values.index, columns=cols),
        "loadings": pd.DataFrame(loadings, index=values.columns, columns=cols),
        "variance_share": {c: float(share[j]) for j, c in enumerate(cols)},
        "n_features": int(x.shape[1]),
    }


def _pls_columns(frame: pd.DataFrame) -> list[str]:
    """The ``pls_k`` columns of a MOTCO table, in component order."""
    comps = [str(c) for c in frame.columns if re.fullmatch(r"pls_\d+", str(c))]
    return sorted(comps, key=lambda c: int(c.split("_")[1]))


def geometry_shares(stage_means: pd.DataFrame, *, groups: Iterable[str], stages: Iterable[str]) -> list[dict]:
    """Share of each trajectory-geometry vector's squared length along each latent component.

    Parameters
    ----------
    stage_means:
        MOTCO's ``stage_means.csv`` (``group``, ``stage``, ``pls_k`` columns).
    groups, stages:
        The group and stage levels in order (the record's ``design``).

    Returns
    -------
    list[dict]
        One row per quantity and component (``DIAGNOSTICS_GEOMETRY_QUANTITIES``:
        ``net_displacement_<group>`` per group, ``sex_difference_by_stage``,
        ``sex_difference_centred``): ``quantity``, ``component``, ``value``
        (the signed component of a single vector; NaN for the summed
        quantities), ``along`` (the squared length along the component),
        ``total`` (the squared length over all components) and ``share`` =
        ``along / total``. The shares of one quantity sum to 1.
    """
    groups, stages = [str(g) for g in groups], [str(s) for s in stages]
    comps = _pls_columns(stage_means)
    sm = stage_means.copy()
    sm["group"] = sm["group"].astype(str)
    sm["stage"] = sm["stage"].astype(str)
    means = {}
    for g in groups:
        for st in stages:
            rows = sm.loc[(sm["group"] == g) & (sm["stage"] == st), comps]
            if len(rows) != 1:
                raise ValueError(f"{ANALYSIS_STAGE_MEANS}: {len(rows)} row(s) for group {g!r}, stage {st!r}, expected 1")
            means[(g, st)] = rows.to_numpy(dtype=float).ravel()
    quantities: dict[str, list[np.ndarray]] = {}
    for g in groups:
        quantities[f"net_displacement_{g}"] = [means[(g, stages[-1])] - means[(g, stages[0])]]
    diffs = [means[(groups[0], st)] - means[(groups[1], st)] for st in stages]
    quantities["sex_difference_by_stage"] = diffs
    centre = np.mean(diffs, axis=0)
    quantities["sex_difference_centred"] = [d - centre for d in diffs]
    rows = []
    for name, vectors in quantities.items():
        total = float(sum((v**2).sum() for v in vectors))
        for j, c in enumerate(comps):
            along = float(sum(v[j] ** 2 for v in vectors))
            rows.append({
                "quantity": name,
                "component": c,
                "value": float(vectors[0][j]) if len(vectors) == 1 else float("nan"),
                "along": along,
                "total": total,
                "share": along / total if total > 0 else float("nan"),
            })
    return rows


def block_loading_shares(loadings: pd.DataFrame, blocks: Iterable[str]) -> dict[str, dict[str, float]]:
    """Share of each component's squared ``pls_loadings.csv`` entries held by each block.

    Parameters
    ----------
    loadings:
        MOTCO's ``pls_loadings.csv`` (``block``, ``feature``, ``pls_k``
        columns: ``x_rotations_`` on the z-scored joint features).
    blocks:
        The block names in order.

    Returns
    -------
    dict
        ``pls_k`` → ``{block: share}``, the sum of the squared entries over
        the block's rows over the sum over all rows; the shares of one
        component sum to 1.
    """
    comps = _pls_columns(loadings)
    sq = loadings[comps].to_numpy(dtype=float) ** 2
    which = loadings["block"].astype(str).to_numpy()
    totals = sq.sum(axis=0)
    return {
        c: {
            b: float(sq[which == b, j].sum() / totals[j]) if totals[j] > 0 else float("nan")
            for b in blocks
        }
        for j, c in enumerate(comps)
    }


def _diagnostic_variables(frame: pd.DataFrame, spec: dict[str, dict] = DIAGNOSTIC_VARIABLES) -> pd.DataFrame:
    """The participants × variables table under ``DIAGNOSTIC_VARIABLES``.

    ``frame`` holds one row per exported participant in export order with
    every source column the variables name (the loader's merged frame joined
    with ``dx_bl``). A variable is its column as is (numeric) when the entry
    has no ``levels``, and the 0-based index of the value in ``levels`` when
    it has. A value outside the levels, or an absent column, stops the step
    naming the column and a count, never a participant.
    """
    problems: list[str] = []
    out: dict[str, np.ndarray] = {}
    for name, entry in spec.items():
        column = entry["column"]
        if column not in frame.columns:
            problems.append(f"{entry['file']}: column {column!r} absent (variable {name})")
            continue
        values = frame[column]
        if "levels" in entry:
            levels = [str(level) for level in entry["levels"]]
            text = values.astype(str).where(values.notna(), other=None)
            outside = ~text.isin(levels)
            if outside.any():
                problems.append(
                    f"{entry['file']} {column}: {int(outside.sum())} value(s) outside its levels {levels}: "
                    + _value_counts_text(values[outside])
                )
                continue
            out[name] = text.map({level: float(i) for i, level in enumerate(levels)}).to_numpy(dtype=float)
        else:
            out[name] = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    if problems:
        raise ValueError("axis-diagnostics stops before writing anything: " + "; ".join(problems))
    return pd.DataFrame(out, columns=list(spec))


def _conditioning_design(
    frame: pd.DataFrame,
    codings: dict[str, dict],
    *,
    expected_columns: Iterable[str] = DIAGNOSTIC_CONDITIONING_COLUMNS,
    record_columns: Iterable[str] | None = None,
    reference_row: dict[str, float] | None = None,
    tolerance: float = 1e-9,
) -> pd.DataFrame:
    """The design columns of the stage-means model, built from the covariate columns of ``frame``.

    A numeric covariate enters as is; a categorical one as drop-first
    indicators in level order, named ``<name>[<level>]``, the first level
    the reference (MOTCO's coding); the covariates are taken in the order
    of ``codings`` (the caller passes them in ``ANALYSIS_COVARIATES``
    order: the export manifest records them with sorted keys). The column
    names must equal
    ``expected_columns`` (``DIAGNOSTIC_CONDITIONING_COLUMNS``) and, when
    given, ``record_columns`` (the record's ``design_columns``); each
    column's mean must equal ``reference_row``'s entry (the record's pooled
    mean) within ``tolerance``. Either difference stops the step naming the
    column: the conditioning set is then the model's design, not a
    reimplementation of it.
    """
    columns: dict[str, np.ndarray] = {}
    for name, spec in codings.items():
        values = frame[name]
        if spec["coding"] == "categorical":
            levels = [str(level) for level in spec["levels"]]
            text = values.astype(str)
            for level in levels[1:]:
                columns[f"{name}[{level}]"] = (text == level).to_numpy(dtype=float)
        else:
            columns[name] = pd.to_numeric(values).to_numpy(dtype=float)
    design = pd.DataFrame(columns)
    names = list(design.columns)
    for label, expected in (("DIAGNOSTIC_CONDITIONING_COLUMNS", expected_columns), ("the record's design_columns", record_columns)):
        if expected is not None and names != [str(c) for c in expected]:
            raise RuntimeError(
                f"the conditioning design's columns {names} differ from {label} {[str(c) for c in expected]}; "
                "the partial correlations condition on the model's design, so a differing design is a stop"
            )
    if reference_row is not None:
        for col in names:
            ref = reference_row.get(col)
            mean = float(design[col].mean())
            if ref is None or not np.isfinite(ref) or abs(mean - float(ref)) > tolerance:
                raise RuntimeError(
                    f"conditioning column {col}: mean {mean!r} differs from the record's reference_row entry {ref!r} "
                    f"by more than {tolerance}; the design built from {EXPORT_COVARIATES} is not the model's"
                )
    return design


#: The steps that write an analysis directory, by the ``step`` their manifest records.
_ANALYSIS_STEPS: tuple[str, ...] = (
    "analyze", "latent-sensitivity", "export-sensitivity", "stage-sensitivity", "rank-sensitivity",
)
#: Every command that writes an analysis directory, for a hint whose analysis manifest cannot be read.
_EVERY_ANALYSIS_COMMAND = (
    "`adni-sexdiff analyze` (the primary), `adni-sexdiff latent-sensitivity` (the latent arm), `adni-sexdiff "
    "export-sensitivity` (an export variant), `adni-sexdiff stage-sensitivity` (the CN / LMCI / AD arm) or "
    "`adni-sexdiff rank-sensitivity` (a rank of the sweep)"
)


def _analysis_command(analysis_dir: Path, manifest: dict | None = None) -> str:
    """The command that wrote ``analysis_dir``, for the diagnostic's hints: ``adni-sexdiff <step>`` from the manifest's ``step`` (with ``--variant`` for an export variant, ``--force`` for a rank of the sweep), or every such command when it cannot be read."""
    both = _EVERY_ANALYSIS_COMMAND
    if manifest is None:
        try:
            manifest = json.loads((analysis_dir / ANALYSIS_MANIFEST).read_text())
        except (OSError, ValueError):
            return both
    step = manifest.get("step") if isinstance(manifest, dict) else None
    if step == "export-sensitivity":
        variant = (manifest.get("variant") or {}).get("name")
        return f"`adni-sexdiff export-sensitivity --variant {variant} --force`" if variant else f"`adni-sexdiff {step}`"
    if step == "rank-sensitivity":
        return f"`adni-sexdiff {step} --force`"
    return f"`adni-sexdiff {step}`" if step in _ANALYSIS_STEPS else both


def _check_analysis_inputs(input_dir: Path, analysis_dir: Path, loaded: dict) -> dict:
    """Read the analysis directory and chain it to the export the loader read.

    Parameters
    ----------
    input_dir, analysis_dir:
        The export and analysis directories.
    loaded:
        ``_load_analysis_inputs(input_dir)``: the export files' observed
        hashes, the merged metadata frame and the export manifest.

    Returns
    -------
    dict
        ``dir``, ``record`` (``result.json``), ``manifest``
        (``analysis_manifest.json``), ``files`` (sha256 and bytes of each
        ``DIAGNOSTICS_ANALYSIS_FILES`` entry), ``chain`` (export file →
        ``True``), ``export_manifest_equals`` (``True``), ``rank``,
        ``components`` (``pls_0`` … in order), ``scores`` (participants ×
        components, indexed by ``rid`` as text, in export order),
        ``stage_means`` and ``loadings`` as read.

    Notes
    -----
    Stops, before anything is written and naming the file and both hashes or
    both counts, never a participant: an absent directory or file (naming
    the commands that write an analysis directory, ``adni-sexdiff analyze``
    for the primary, ``adni-sexdiff latent-sensitivity`` for the latent arm,
    ``adni-sexdiff export-sensitivity`` for an export variant,
    ``adni-sexdiff stage-sensitivity`` for the CN / LMCI / AD arm and
    ``adni-sexdiff rank-sensitivity`` for a rank of the sweep, or the one
    the manifest's ``step`` names when the manifest is readable); an
    input hash the analysis manifest records that differs from the export
    file's sha256 now, or an export-manifest hash that differs (the export
    was regenerated after the analysis; the hint names the manifest's
    step); a ``pls_`` column count in ``latent_scores.csv``,
    ``stage_means.csv`` or ``pls_loadings.csv`` that differs from the
    record's selected rank; a ``stage_means.csv`` without exactly one row
    per group × stage of the record's design; a ``pls_loadings.csv`` whose
    (block, feature) rows are not the export manifest's ``block_columns``,
    each once; a ``latent_scores.csv`` whose ``rid`` set differs from the
    export's.
    """
    both = _EVERY_ANALYSIS_COMMAND
    if not analysis_dir.is_dir():
        raise FileNotFoundError(f"{analysis_dir} does not exist; run {both} first")
    absent = [n for n in DIAGNOSTICS_ANALYSIS_FILES if not (analysis_dir / n).is_file()]
    if absent:
        raise FileNotFoundError(
            f"{len(absent)} analysis file(s) absent from {analysis_dir}: " + ", ".join(repr(n) for n in absent)
            + f"; run {_analysis_command(analysis_dir)} first"
        )
    manifest = json.loads((analysis_dir / ANALYSIS_MANIFEST).read_text())
    record = json.loads((analysis_dir / ANALYSIS_RESULT).read_text())
    command = _analysis_command(analysis_dir, manifest)
    recorded = manifest.get("inputs", {}).get("files", {})
    chain: dict[str, bool] = {}
    for name, entry in loaded["inputs"].items():
        if name == EXPORT_MANIFEST:
            continue
        rec = recorded.get(name, {}).get("sha256")
        if rec is None:
            raise RuntimeError(f"{name}: {ANALYSIS_MANIFEST} records no input hash for it; rerun {command}")
        if rec != entry["sha256"]:
            raise RuntimeError(
                f"{name}: sha256 {entry['sha256']} now differs from the hash {ANALYSIS_MANIFEST} records ({rec}); the "
                f"export was regenerated after the analysis, rerun {command}"
            )
        chain[name] = True
    rec_manifest = manifest.get("inputs", {}).get("export_manifest", {}).get("sha256")
    now_manifest = loaded["inputs"][EXPORT_MANIFEST]["sha256"]
    if rec_manifest != now_manifest:
        raise RuntimeError(
            f"{EXPORT_MANIFEST}: sha256 {now_manifest} now differs from the hash {ANALYSIS_MANIFEST} records "
            f"({rec_manifest}); the export was regenerated after the analysis, rerun {command}"
        )

    rank = int(record["latent"]["selected_lv"])
    scores = pd.read_csv(analysis_dir / ANALYSIS_LATENT_SCORES)
    stage_means = pd.read_csv(analysis_dir / ANALYSIS_STAGE_MEANS)
    loadings = pd.read_csv(analysis_dir / ANALYSIS_PLS_LOADINGS)
    problems: list[str] = []
    components = [f"pls_{k}" for k in range(rank)]
    for name, table in ((ANALYSIS_LATENT_SCORES, scores), (ANALYSIS_STAGE_MEANS, stage_means), (ANALYSIS_PLS_LOADINGS, loadings)):
        comps = _pls_columns(table)
        if comps != components:
            problems.append(f"{name}: {len(comps)} pls_ column(s) but {ANALYSIS_RESULT} records selected rank {rank}")
    design = record["design"]
    groups = [str(g) for g in design["group_levels"]]
    stages = [str(st) for st in design["stage_levels"]]
    expected_rows = {(g, st) for g in groups for st in stages}
    if {"group", "stage"} <= set(stage_means.columns):
        seen_rows = list(zip(stage_means["group"].astype(str), stage_means["stage"].astype(str)))
        n_missing = len(expected_rows - set(seen_rows))
        if len(seen_rows) != len(expected_rows) or n_missing:
            problems.append(
                f"{ANALYSIS_STAGE_MEANS}: {len(seen_rows)} row(s), expected {len(expected_rows)} (one per group × stage of "
                f"the record's design), {n_missing} cell(s) missing"
            )
    else:
        problems.append(f"{ANALYSIS_STAGE_MEANS}: columns group and stage absent")
    block_columns = loaded["export_manifest"].get("settings", {}).get("block_columns", {})
    expected_feats = [(p, str(f)) for p in EXPORT_BLOCKS for f in block_columns.get(p, [])]
    if {"block", "feature"} <= set(loadings.columns):
        seen_feats = list(zip(loadings["block"].astype(str), loadings["feature"].astype(str)))
        n_dup = len(seen_feats) - len(set(seen_feats))
        only_loadings = len(set(seen_feats) - set(expected_feats))
        only_export = len(set(expected_feats) - set(seen_feats))
        if n_dup or only_loadings or only_export:
            problems.append(
                f"{ANALYSIS_PLS_LOADINGS}: {len(seen_feats)} (block, feature) row(s) differ from the {len(expected_feats)} "
                f"block_columns {EXPORT_MANIFEST} records ({only_export} only in the export, {only_loadings} only in "
                f"{ANALYSIS_PLS_LOADINGS}, {n_dup} duplicated)"
            )
    else:
        problems.append(f"{ANALYSIS_PLS_LOADINGS}: columns block and feature absent")
    rids = [str(r) for r in loaded["metadata"][SAMPLE_COLUMN]]
    if SAMPLE_COLUMN in scores.columns:
        seen_rids = [str(r) for r in scores[SAMPLE_COLUMN]]
        n_dup = len(seen_rids) - len(set(seen_rids))
        only_scores = len(set(seen_rids) - set(rids))
        only_export = len(set(rids) - set(seen_rids))
        if n_dup or only_scores or only_export:
            problems.append(
                f"{ANALYSIS_LATENT_SCORES}: {len(seen_rids)} participant(s) differ from the {len(rids)} of "
                f"{EXPORT_METADATA} ({only_export} only in the export, {only_scores} only in {ANALYSIS_LATENT_SCORES}, "
                f"{n_dup} duplicated)"
            )
    else:
        problems.append(f"{ANALYSIS_LATENT_SCORES}: column {SAMPLE_COLUMN!r} absent")
    if problems:
        raise RuntimeError(
            "axis-diagnostics stops before writing anything: " + "; ".join(problems)
            + f"; the analysis directory is not the one {command} wrote for this export, rerun it"
        )
    scores = scores.set_index(scores[SAMPLE_COLUMN].astype(str))[components].loc[rids]
    files = {
        name: {"sha256": _sha256_file(analysis_dir / name), "bytes": (analysis_dir / name).stat().st_size}
        for name in DIAGNOSTICS_ANALYSIS_FILES
    }
    return {
        "dir": analysis_dir,
        "record": record,
        "manifest": manifest,
        "files": files,
        "chain": chain,
        "export_manifest_equals": True,
        "rank": rank,
        "components": components,
        "scores": scores,
        "stage_means": stage_means,
        "loadings": loadings,
    }


def _check_cohort_chain(cohort_dir: Path, export_manifest: dict, rids: list[str]) -> dict:
    """Check ``cohort.csv`` against its manifest, the manifest against the export's record, and the rows against the export.

    Returns ``cohort`` (the rows with every platform flag, in file order),
    ``manifest`` (the cohort manifest) and ``files`` (``cohort.csv`` with its
    sha256 and ``equals_cohort_manifest``, ``cohort_manifest.json`` with its
    sha256 and ``equals_export_manifest``). Stops, before anything is
    written, on a ``cohort.csv`` whose hash differs from its manifest's
    record (``_check_cohort_outputs``), a ``cohort_manifest.json`` whose
    sha256 differs from the one the export manifest records (the cohort was
    rerun after the export; names ``export``), and both-flag rows that are
    not the exported participants in export order (counts only).

    On the CN / LMCI / AD arm's export (an export manifest that records
    ``stage_arm``, change ``adni-stage-sensitivity``) the rows compared, and
    returned, are the both-flag rows whose ``dx_bl`` the arm keeps, and a
    stop names ``stage-sensitivity`` (the step that wrote the arm's export)
    instead of ``export``.
    """
    stage_arm = export_manifest.get("stage_arm") or None
    rerun = (
        "rerun `adni-sexdiff stage-sensitivity --force` (then axis-diagnostics on the arm)" if stage_arm
        else "rerun `adni-sexdiff export` (then analyze)"
    )
    cohort_manifest, inputs, _ = _check_cohort_outputs(cohort_dir, {})
    recorded = export_manifest.get("inputs", {}).get("cohort", {}).get("manifest", {}).get("sha256")
    now = inputs["manifest"]["sha256"]
    if recorded is None:
        raise RuntimeError(
            f"{EXPORT_MANIFEST} records no hash for {COHORT_MANIFEST}; "
            + (rerun if stage_arm else "rerun `adni-sexdiff export`")
        )
    if recorded != now:
        raise RuntimeError(
            f"{COHORT_MANIFEST}: sha256 {now} now differs from the hash {EXPORT_MANIFEST} records ({recorded}); the "
            f"cohort was rerun after the export, {rerun}"
        )
    cohort = pd.read_csv(cohort_dir / COHORT_TABLE)
    absent = [c for c in (SAMPLE_COLUMN, *EXPORT_BLOCKS, *([stage_arm["source"]] if stage_arm else [])) if c not in cohort.columns]
    if absent:
        raise ValueError(f"{COHORT_TABLE}: column(s) absent: {', '.join(repr(c) for c in absent)}")
    both = cohort[cohort[list(EXPORT_BLOCKS)].astype(bool).all(axis=1)].reset_index(drop=True)
    which = "with every platform flag"
    if stage_arm:
        both = both[both[stage_arm["source"]].isin(list(stage_arm["keep"]))].reset_index(drop=True)
        which += f" whose {stage_arm['source']} the arm {stage_arm['name']} keeps"
    seen = [str(r) for r in both[SAMPLE_COLUMN]]
    if seen != rids:
        only_cohort = len(set(seen) - set(rids))
        only_export = len(set(rids) - set(seen))
        detail = (
            "the same participants in another order" if not only_cohort and not only_export and len(seen) == len(rids)
            else f"{only_export} only in the export, {only_cohort} only in the cohort"
        )
        raise RuntimeError(
            f"{COHORT_TABLE}: the {len(seen)} row(s) {which} differ from the {len(rids)} exported "
            f"participants of {EXPORT_METADATA} ({detail}); {rerun}"
        )
    files = {
        COHORT_TABLE: inputs["outputs"][COHORT_TABLE],
        COHORT_MANIFEST: {"sha256": now, "equals_export_manifest": True},
    }
    return {"cohort": both, "manifest": cohort_manifest, "files": files}


def _correlation_rows(scores: pd.DataFrame, variables: pd.DataFrame, z: np.ndarray, *, threshold: float) -> list[dict]:
    """Raw and partial Spearman rows of every score column against every variable (declared order)."""
    rows = []
    for comp in scores.columns:
        s = scores[comp].to_numpy(dtype=float)
        sd = float(np.std(s, ddof=1)) if s.size > 1 else float("nan")
        for var in variables.columns:
            v = variables[var].to_numpy(dtype=float)
            rho, n = spearman(s, v)
            prho, n_partial = partial_spearman(s, v, z)
            rows.append({
                "component": str(comp),
                "component_sd": sd,
                "variable": str(var),
                "n": n,
                "spearman": rho,
                "n_partial": n_partial,
                "partial_spearman": prho,
                "flag_raw": bool(np.isfinite(rho) and abs(rho) >= threshold),
                "flag_partial": bool(np.isfinite(prho) and abs(prho) >= threshold),
            })
    return rows


def _fmt_nan(value, spec: str = ".6g") -> str:
    """``_fmt`` that also renders NaN as ``n/a``."""
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return "n/a"
    return format(value, spec)


def _finite_or_none(value) -> float | None:
    """A float for the manifest; ``None`` for NaN or infinity (JSON holds no NaN)."""
    if value is None:
        return None
    value = float(value)
    return value if np.isfinite(value) else None


def render_axis_diagnostics(
    tables: dict[str, pd.DataFrame],
    *,
    analysis: dict,
    variables: dict[str, dict],
    blocks: dict[str, dict],
    findings: list[str],
    threshold: float = DIAGNOSTIC_CORRELATION_THRESHOLD,
) -> str:
    """Render ``diagnostics.md`` from the four diagnostic tables.

    Parameters
    ----------
    tables:
        ``axis``, ``block_pcs``, ``geometry``, ``components`` as written to
        the CSVs.
    analysis:
        The analysis read: ``dir``, ``rank``, ``selection``,
        ``latent_adjustment``, ``n_jobs``, ``is_primary``, ``participants``,
        ``export_variant`` (the variant's name when the analysis is an
        export variant of ``export-sensitivity``; absent or ``None``
        otherwise), ``stage_arm`` (the arm's name when the analysis is the
        CN / LMCI / AD arm of ``stage-sensitivity``; absent or ``None``
        otherwise) and ``rank_sweep`` (``forced_rank`` and ``primary_rank``
        when the analysis is a rank of the ``rank-sensitivity`` sweep; absent
        or ``None`` otherwise).
    variables:
        ``DIAGNOSTIC_VARIABLES`` (name → ``file``, ``derivation``), in table
        order.
    blocks:
        Per block (``EXPORT_BLOCKS`` order): ``features``,
        ``variance_shares`` (per PC) and ``pc1_phase`` (``spearman`` here,
        ``export_abs_corr_pearson`` as the export manifest recorded it).
    findings:
        The run's findings, listed before the reading rules.
    threshold:
        ``DIAGNOSTIC_CORRELATION_THRESHOLD``, named in the header.

    Returns
    -------
    str
        Markdown: a header stating what the tables are and are not; the
        flagged correlations first (latent components, then block PCs, each
        by |rho| descending); the component summary; the variable ×
        component table with ``*`` on the flagged cells; one block-PC table
        per block with the export's recorded PC1 phase correlation beside
        the diagnostic's in the heading; the geometry shares; the analysis
        read; the findings; ``READING_RULES`` verbatim. Correlations and
        shares carry three decimals, SDs four significant digits.

    Notes
    -----
    The renderer keys on ``analysis["latent_adjustment"]`` (change
    ``adni-latent-sensitivity``). When it is not null the opening paragraph
    names the ``stage``-conditioned sensitivity arm and its directory, a
    flagged row is a finding about the measurement space of the arm (the
    primary stays primary), the analysis-read section names the arm's
    constant and ``LATENT_SENSITIVITY_READING_RULES`` follows
    ``READING_RULES`` under its own heading. It also keys on
    ``analysis.get("export_variant")`` (change ``adni-nist-bridge``): for an
    export variant the opening paragraph names the variant and the block it
    changes, a flagged row is a finding about the variant's measurement space
    (the primary stays primary), the analysis-read section names the variant
    under its rule 7 and the variant's rule set (``EXPORT_VARIANT_RULE_SETS``,
    change ``adni-nmr-all-columns``: ``EXPORT_VARIANT_READING_RULES`` for the
    p180 variants, ``NMR_MEMBERSHIP_READING_RULES`` for ``nmr_all_columns``)
    follows ``READING_RULES`` under its own heading. And on
    ``analysis.get("stage_arm")`` (change
    ``adni-stage-sensitivity``): for the CN / LMCI / AD arm the opening
    paragraph names the arm, a flagged row is a finding about the arm's
    measurement space (the primary stays primary), the analysis-read section
    names the arm and ``STAGE_SENSITIVITY_READING_RULES`` follows
    ``READING_RULES`` under its own heading. And on
    ``analysis.get("rank_sweep")`` (change ``adni-rank-sensitivity``): for a
    forced rank of the sweep the opening paragraph names the sweep, the
    forced rank and its directory and states that its first components (up
    to the primary's rank) are the primary's, a flagged row is a finding
    about the measurement space at that rank (the primary stays primary),
    the analysis-read section names the sweep and
    ``RANK_SENSITIVITY_READING_RULES`` follows ``READING_RULES`` under its own
    heading. On the primary, the latent arm, the variants and the
    CN / LMCI / AD arm every byte is unchanged.
    """
    axis, pcs, geo, comps_table = tables["axis"], tables["block_pcs"], tables["geometry"], tables["components"]
    comps = _pls_columns(pd.DataFrame(columns=list(dict.fromkeys(axis["component"])))) if len(axis) else []
    var_order = list(variables)
    n_pcs = max((len(b.get("variance_shares", {})) for b in blocks.values()), default=0)
    latent_adjustment = analysis.get("latent_adjustment")
    export_variant = analysis.get("export_variant")
    stage_arm = analysis.get("stage_arm")
    rank_sweep = analysis.get("rank_sweep")
    read = f"{analysis['selection']}-selected rank {analysis['rank']}"
    if latent_adjustment is not None:
        which = (
            f"the `{latent_adjustment}`-conditioned latent-adjustment sensitivity arm `{LATENT_SENSITIVITY_ARM['name']}` "
            f"(`LATENT_SENSITIVITY_ARM`, change `{LATENT_SENSITIVITY_ARM['change']}`; not the primary)"
        )
        whose = "this arm (the primary stays primary)"
    elif export_variant is not None:
        which = (
            f"the export variant `{export_variant}` (`EXPORT_VARIANTS`, change "
            f"`{EXPORT_VARIANTS[export_variant]['change']}`: the primary's settings on an export whose "
            f"{_variant_words(export_variant)['whose']} differs; not the primary)"
        )
        whose = "this export variant (the primary stays primary)"
    elif stage_arm is not None:
        which = (
            f"the CN / LMCI / AD arm `{stage_arm}` (`STAGE_SENSITIVITY_ARM`, change "
            f"`{STAGE_SENSITIVITY_ARM['change']}`: the primary's settings on the primary export's rows of the "
            "participants whose `DX.bl` is " + ", ".join(STAGE_SENSITIVITY_ARM["keep"][:-1])
            + f" or {STAGE_SENSITIVITY_ARM['keep'][-1]}; not the primary)"
        )
        whose = "this arm (the primary stays primary)"
    elif rank_sweep is not None:
        k, r = int(rank_sweep["forced_rank"]), int(rank_sweep["primary_rank"])
        which = (
            f"forced rank {k} of the rank sweep `{RANK_SENSITIVITY_LADDER['name']}` (`RANK_SENSITIVITY_LADDER`, change "
            f"`{RANK_SENSITIVITY_LADDER['change']}`: the primary's analysis with `{RANK_SENSITIVITY_LADDER['setting']}` = "
            f"{k}; PLS-DA components are nested, so its components `pls_0` to `pls_{min(k, r) - 1}` are the primary's, "
            f"with the primary's correlations; not the primary)"
        )
        whose = f"the rank sweep at rank {k} (the primary stays primary)"
        read = f"forced rank {k}"
    else:
        which = "the primary" if analysis["is_primary"] else "an arm (not the primary)"
        whose = "the primary analysis"
    lines = [
        "# MOTCO axis diagnostics: ADNI serum metabolomics, sex × stage",
        "",
        f"Descriptive measurement-space diagnostics of {which} covariate-adjusted trajectory analysis "
        f"(`{analysis['dir']}`, {read}, n = {analysis['participants']}): "
        f"Spearman correlations of every latent component with the {len(var_order)} predeclared variables "
        "(`DIAGNOSTIC_VARIABLES`: the five analysis covariates as the model codes them, the design's stage and sex, "
        "and the enrollment category `dx_bl` the stage rule merged), the partial Spearman correlations given the "
        f"{len(DIAGNOSTIC_CONDITIONING_COLUMNS)} design columns of the record (the Spearman correlation of the OLS "
        "residuals of both on an intercept and the design; undefined for a covariate itself), the same for the first "
        f"{n_pcs} principal components of each z-scored block, the share of the sex × stage geometry along each "
        f"component and the block composition of each component. Rows with |rho| ≥ {threshold} are flagged and "
        "listed first; the flag is a reporting threshold, not an adoption rule. No p-value is attached to any "
        "correlation and the tables support no inferential claim. Nothing here chooses a variant or an arm: an axis "
        f"correlated with a variable is a finding about the measurement space of {whose}, not a "
        "reinterpretation of its statistics or p-values (`delta`, `angle` and `shape` keep their recorded status), and "
        "the primary analysis stays primary under the reading rules below.",
        "",
        "## Flagged correlations",
        "",
        "Each flagged row is a measurement-space finding about the analysis read, not a change of its statistics.",
        "",
        "Latent components (by |rho|):",
        "",
    ]

    def flag_text(r) -> str:
        return "+".join(f for f, on in (("raw", r.flag_raw), ("partial", r.flag_partial)) if on)

    flagged = axis[axis["flag_raw"] | axis["flag_partial"]].copy()
    if len(flagged):
        flagged["abs"] = flagged["spearman"].abs().fillna(flagged["partial_spearman"].abs())
        flagged["c"] = flagged["component"].map({c: i for i, c in enumerate(comps)})
        flagged["v"] = flagged["variable"].map({v: i for i, v in enumerate(var_order)})
        flagged = flagged.sort_values(["abs", "c", "v"], ascending=[False, True, True])
        lines += [
            "| component | sd | variable | source | n | rho | rho \\| design | flag |",
            "|---|---:|---|---|---:|---:|---:|---|",
        ]
        for r in flagged.itertuples(index=False):
            lines.append(
                f"| {r.component} | {_fmt(r.component_sd, '.4g')} | `{r.variable}` | {r.source} | {r.n} | "
                f"{_fmt_nan(r.spearman, '.3f')} | {_fmt_nan(r.partial_spearman, '.3f')} | {flag_text(r)} |"
            )
    else:
        lines.append(f"No latent-component correlation reaches |rho| ≥ {threshold}.")
    lines += ["", "Block principal components (by |rho|):", ""]
    pflag = pcs[pcs["flag_raw"] | pcs["flag_partial"]].copy()
    if len(pflag):
        pflag["abs"] = pflag["spearman"].abs().fillna(pflag["partial_spearman"].abs())
        pflag["b"] = pflag["block"].map({b: i for i, b in enumerate(blocks)})
        pflag["v"] = pflag["variable"].map({v: i for i, v in enumerate(var_order)})
        pflag = pflag.sort_values(["abs", "b", "component", "v"], ascending=[False, True, True, True])
        lines += [
            "| block | component | variance share | variable | source | n | rho | rho \\| design | flag |",
            "|---|---|---:|---|---|---:|---:|---:|---|",
        ]
        for r in pflag.itertuples(index=False):
            lines.append(
                f"| {r.block} | {r.component} | {_fmt(r.variance_share, '.3f')} | `{r.variable}` | {r.source} | {r.n} | "
                f"{_fmt_nan(r.spearman, '.3f')} | {_fmt_nan(r.partial_spearman, '.3f')} | {flag_text(r)} |"
            )
    else:
        lines.append(f"No block principal component correlation reaches |rho| ≥ {threshold}.")

    # Components
    share_cols = [c for c in comps_table.columns if c.startswith("loading_share_")]
    lines += [
        "",
        "## Components",
        "",
        "Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation "
        "weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables "
        "flagged on the raw and on the partial correlation, and the variable with the largest |rho|.",
        "",
        "| component | sd | " + " | ".join(f"share {c.removeprefix('loading_share_')}" for c in share_cols)
        + " | flagged raw | flagged partial | top variable | top rho |",
        "|---|---:|" + "---:|" * len(share_cols) + "---:|---:|---|---:|",
    ]
    for r in comps_table.to_dict("records"):
        lines.append(
            f"| {r['component']} | {_fmt(r['sd'], '.4g')} | " + " | ".join(_fmt_nan(r[c], ".3f") for c in share_cols)
            + f" | {r['n_flagged_raw']} | {r['n_flagged_partial']} | "
            + (f"`{r['top_variable']}`" if isinstance(r["top_variable"], str) else "n/a")
            + f" | {_fmt_nan(r['top_spearman'], '.3f')} |"
        )

    # Variables × components
    lines += [
        "",
        "## Correlations of the latent components",
        "",
        "Component score SD: " + ", ".join(
            f"{c} {_fmt(axis.loc[axis['component'] == c, 'component_sd'].iloc[0], '.4g')}" for c in comps
        ) + ". Columns per component: Spearman rho, then rho given the design columns (n/a for a covariate itself). "
        "Variables in declared order; `n` is the pairwise-complete count.",
        "",
        "| variable | source | n | " + " | ".join(f"{c} rho | {c} rho \\| design" for c in comps) + " |",
        "|---|---|---:|" + "---:|---:|" * len(comps),
    ]
    for var in var_order:
        sub = axis[axis["variable"] == var].set_index("component")
        cells = []
        for c in comps:
            r = sub.loc[c]
            cells.append(f"{_fmt_nan(r['spearman'], '.3f')}{'*' if r['flag_raw'] else ''}")
            cells.append(f"{_fmt_nan(r['partial_spearman'], '.3f')}{'*' if r['flag_partial'] else ''}")
        lines.append(f"| `{var}` | {variables[var]['file']} | {int(sub['n'].iloc[0])} | " + " | ".join(cells) + " |")
    lines += ["", f"`*` marks |rho| ≥ {threshold}."]

    # Block principal components
    lines += ["", "## Block principal components", ""]
    for block, info in blocks.items():
        sub = pcs[pcs["block"] == block]
        bcomps = list(info.get("variance_shares", {}))
        shares = ", ".join(f"{c} {_fmt(info['variance_shares'][c], '.3f')}" for c in bcomps)
        pc1 = info.get("pc1_phase", {})
        lines += [
            f"### {block} ({info.get('features')} features; variance share {shares}; pc1 against `phase`: Spearman "
            f"{_fmt_nan(pc1.get('spearman'), '.3f')} here, |Pearson| {_fmt_nan(pc1.get('export_abs_corr_pearson'), '.3f')} "
            "recorded by export)",
            "",
            "| variable | n | " + " | ".join(f"{c} rho | {c} rho \\| design" for c in bcomps) + " |",
            "|---|---:|" + "---:|---:|" * len(bcomps),
        ]
        for var in var_order:
            vs = sub[sub["variable"] == var].set_index("component")
            cells = []
            for c in bcomps:
                r = vs.loc[c]
                cells.append(f"{_fmt_nan(r['spearman'], '.3f')}{'*' if r['flag_raw'] else ''}")
                cells.append(f"{_fmt_nan(r['partial_spearman'], '.3f')}{'*' if r['flag_partial'] else ''}")
            lines.append(f"| `{var}` | {int(vs['n'].iloc[0])} | " + " | ".join(cells) + " |")
        lines.append("")

    # Geometry shares
    lines += [
        "## Geometry shares",
        "",
        "Share of the squared length of each vector of the trajectory geometry (from `stage_means.csv`) that lies "
        "along each component: each sex's net displacement (last stage minus first, what `angle` reads), the "
        "per-stage sex-difference vectors (Female minus Male) and the stage-centred ones. `value` is the signed "
        "component of a single vector (the net displacements), empty for the summed quantities.",
        "",
        "| quantity | component | value | along | total | share |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in geo.itertuples(index=False):
        lines.append(
            f"| {r.quantity} | {r.component} | {_fmt_nan(r.value, '.4g')} | {_fmt(r.along, '.4g')} | "
            f"{_fmt(r.total, '.4g')} | {_fmt_nan(r.share, '.3f')} |"
        )

    # Analysis read
    n_jobs = analysis.get("n_jobs")
    lines += [
        "",
        "## Analysis read",
        "",
        f"- directory: `{analysis['dir']}`",
        f"- rank: {analysis['rank']} (`{analysis['selection']}`)",
        f"- latent adjustment: {analysis['latent_adjustment'] if analysis['latent_adjustment'] is not None else 'none'}",
        f"- n_jobs: {n_jobs}" + ("" if n_jobs == REPORTED_N_JOBS else f" (not a reported run: reported runs use n_jobs = {REPORTED_N_JOBS})"),
        f"- primary: {'yes' if analysis['is_primary'] else 'no (the primary rank and row counts are not expected)'}",
    ]
    if latent_adjustment is not None:
        lines.append(
            f"- arm: `{LATENT_SENSITIVITY_ARM['name']}` (`LATENT_SENSITIVITY_ARM`): a component of the arm that tracks a "
            "variable here is a measurement-space finding about the arm; it never reinterprets either analysis' "
            "statistics and is never grounds to adopt the arm (arm rule 9)"
        )
    if export_variant is not None:
        lines.append(
            f"- export variant: `{export_variant}` (`EXPORT_VARIANTS`): a component of the variant that tracks a variable "
            "here is a measurement-space finding about the variant; it never reinterprets either analysis' statistics "
            f"and is never grounds to adopt the variant ({_variant_words(export_variant)['cite']} 7)"
        )
    if stage_arm is not None:
        lines.append(
            f"- CN / LMCI / AD arm: `{stage_arm}` (`STAGE_SENSITIVITY_ARM`): a component of the arm that tracks a "
            "variable here is a measurement-space finding about the arm and never grounds to adopt it; in the arm "
            "`dx_bl` orders the participants as `stage` does, so their correlations coincide (stage-arm rule 7)"
        )
    if rank_sweep is not None:
        k, r = int(rank_sweep["forced_rank"]), int(rank_sweep["primary_rank"])
        lines.append(
            f"- rank sweep: forced rank {k} of `{RANK_SENSITIVITY_LADDER['name']}` (`RANK_SENSITIVITY_LADDER`); "
            f"`pls_0` to `pls_{min(k, r) - 1}` are the primary's components (nesting) and keep its correlations; "
            + (
                f"a component above the primary's rank {r} that tracks a variable, `phase` in particular, is a "
                "measurement-space finding about the higher ranks and never grounds to choose a rank (sweep rule 7)"
                if k > r else "a flagged row here is the primary's own, at a lower rank (sweep rule 7)"
            )
        )
    lines += [
        "",
        "## Findings",
        "",
    ]
    lines += [f"- {msg}" for msg in findings] or ["None."]
    lines += [
        "",
        "## Reading rules",
        "",
        "Binding for every reader of the result (`READING_RULES`, decided by `adni-analyze` before any run):",
        "",
    ]
    lines += [f"{i}. {rule}" for i, rule in enumerate(READING_RULES, 1)]
    if latent_adjustment is not None:
        lines += [
            "",
            "## Reading rules of the arm",
            "",
            f"Binding for every reader of the arm (`LATENT_SENSITIVITY_READING_RULES`, decided by "
            f"`{LATENT_SENSITIVITY_ARM['change']}` before any run), after `READING_RULES`:",
            "",
        ]
        lines += [f"{i}. {rule}" for i, rule in enumerate(LATENT_SENSITIVITY_READING_RULES, 1)]
    if export_variant is not None:
        lines += ["", *_export_variant_rules_lines(export_variant)]
    if stage_arm is not None:
        lines += ["", *_stage_arm_rules_heading(), ""]
        lines += [f"{i}. {rule}" for i, rule in enumerate(STAGE_SENSITIVITY_READING_RULES, 1)]
    if rank_sweep is not None:
        lines += ["", *_rank_sweep_rules_heading(), ""]
        lines += [f"{i}. {rule}" for i, rule in enumerate(RANK_SENSITIVITY_READING_RULES, 1)]
    return "\n".join(lines) + "\n"


def run_axis_diagnostics(
    *,
    input_dir: str | Path | None = None,
    analysis_dir: str | Path | None = None,
    cohort_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    force: bool = False,
) -> dict:
    """Measure what the MOTCO latent components and the block axes correlate with.

    Parameters
    ----------
    input_dir:
        Output directory of ``export`` (default ``constants.MOTCO_INPUT_DIR``).
        Read: ``p180.csv``, ``nmr.csv``, ``metadata.csv``, ``covariates.csv``
        (each checked against the sha256 ``manifest.json`` records) and
        ``manifest.json`` (block columns, covariate codings, the recorded
        phase offset).
    analysis_dir:
        Output directory of ``analyze`` (default
        ``constants.MOTCO_ANALYSIS_DIR``); ``DIAGNOSTICS_ANALYSIS_FILES``
        (``result.json``, ``latent_scores.csv``, ``stage_means.csv``,
        ``pls_loadings.csv``, ``analysis_manifest.json``) are read and
        checked, never written. Another directory is an arm: the manifest
        records it as not the primary (see Notes).
    cohort_dir:
        Output directory of ``cohort`` (default ``constants.COHORT_DIR``);
        ``cohort.csv`` (checked against ``cohort_manifest.json``) is the
        source of ``dx_bl``.
    out_dir:
        Diagnostics directory (default ``constants.DIAGNOSTICS_DIR``).
    force:
        Replace an existing diagnostics directory (after the new one is
        complete).

    Returns
    -------
    dict
        ``{"dir": Path, "tables": {"axis", "block_pcs", "geometry", "components"}, "manifest": dict, "findings": [...]}``.

    Notes
    -----
    Checks, in this order, before anything is written: an existing output
    directory without ``force``; the export (``_load_analysis_inputs``: the
    five files, each CSV against the export manifest's hash, the column
    sets, the ``rid`` alignment, the value and missing checks); the analysis
    (``_check_analysis_inputs``: the five files, every input hash the
    analysis manifest records against the export file now, the export
    manifest's hash, the ``pls_`` column count of the three tables against
    the record's selected rank, one ``stage_means.csv`` row per group ×
    stage, the ``pls_loadings.csv`` rows against the export's
    ``block_columns``, the ``rid`` set of ``latent_scores.csv``); the cohort
    (``_check_cohort_chain``: ``cohort.csv`` against its manifest, the
    cohort manifest's hash against the export manifest's record, the rows
    with both platform flags against the exported participants in order);
    the variable table (``_diagnostic_variables``: a value outside its
    levels) and the conditioning design (``_conditioning_design``: the six
    design columns by name and by column mean against the record). A
    failure stops the step naming the file or column and a count or both
    hashes, never a participant, and nothing is written.

    The variables are ``DIAGNOSTIC_VARIABLES`` (``age``, ``education``,
    ``apoe4``, ``phase``, ``statin`` from ``covariates.csv`` as the model
    codes them; ``stage`` and ``male`` from ``metadata.csv``; ``dx_bl`` from
    ``cohort.csv``), each as is or as the 0-based index in its levels. The
    statistics: ``spearman`` (pairwise-complete), ``partial_spearman`` given
    the record's six design columns (``DIAGNOSTIC_CONDITIONING_COLUMNS``,
    built from ``covariates.csv`` with the export's codings; undefined for
    a covariate itself), ``block_principal_components`` (the first
    ``DIAGNOSTIC_N_BLOCK_PCS`` PCs of each z-scored block, population SD,
    signs fixed by the largest loading, with their variance shares and
    pc1's Spearman with ``phase`` beside the export's recorded Pearson
    value), ``geometry_shares`` (from ``stage_means.csv``,
    ``DIAGNOSTICS_GEOMETRY_QUANTITIES``) and ``block_loading_shares`` (the
    share of each component's squared ``pls_loadings.csv`` entries per
    block). A correlation is flagged when |rho| is at least
    ``DIAGNOSTIC_CORRELATION_THRESHOLD``; no p-value is attached.

    Output contract (``results/motco_diagnostics/``, written as
    ``motco_diagnostics.tmp/`` and renamed when complete), every file
    per component, per block or per variable, no ``rid``, all committed:
    ``axis_correlations.csv`` (``component``, ``component_sd``,
    ``variable``, ``source``, ``n``, ``spearman``, ``n_partial``,
    ``partial_spearman``, ``flag_raw``, ``flag_partial``; rows by
    component, then variable order), ``block_pcs.csv`` (``block``,
    ``component``, ``variance_share``, then the same columns; rows by
    block, PC, variable), ``geometry_shares.csv`` (``quantity``,
    ``component``, ``value``, ``along``, ``total``, ``share``),
    ``components.csv`` (``component``, ``sd``, ``loading_share_<block>``
    per block, ``n_flagged_raw``, ``n_flagged_partial``, ``top_variable``,
    ``top_spearman``), ``diagnostics.md`` (``render_axis_diagnostics``:
    the flagged rows first, the tables, the analysis read, the findings and
    ``READING_RULES`` verbatim) and ``diagnostics_manifest.json``
    (versions, git revision, the twelve inputs with sha256 and the chain
    checks, the analysis read with ``is_primary``, the variables with
    sources and derivations, the threshold, the conditioning columns, the
    definition of every statistic, the counts, the predeclared
    ``DIAGNOSTICS_EXPECTED_COUNTS`` beside them with deviations, output
    hashes, findings).

    Findings, recorded and printed, never a stop: a deviation from the
    predeclared counts; an analysis read whose ``n_jobs`` is not
    ``REPORTED_N_JOBS``; an analysis that is not the primary (a non-default
    ``analysis_dir`` or a recorded latent adjustment: the ``primary`` and
    ``rows`` expectations are then skipped and the manifest says so, the
    arm path of ``adni-latent-sensitivity``; an export variant of
    ``export-sensitivity``, read with ``--input-dir <variant>/motco_input
    --analysis-dir <variant>/analysis``, is not the primary either and its
    ``diagnostics.md`` names it and the block it changes and carries the
    variant's rule set (``EXPORT_VARIANT_RULE_SETS``), change
    ``adni-nist-bridge``; its expected counts are the variant's own
    ``EXPORT_VARIANT_EXPECTED_COUNTS[<variant>]["diagnostics"]`` when the
    entry holds them (``nmr_all_columns``: the rank-independent keys with 245
    NMR features, change ``adni-nmr-all-columns``) and the rank-independent
    keys otherwise; so is the CN / LMCI / AD arm of
    ``stage-sensitivity``, read with ``--input-dir
    results/motco_stage_sensitivity/motco_input --analysis-dir
    results/motco_stage_sensitivity/analysis``: its cohort check compares the
    both-flag rows whose ``dx_bl`` the arm keeps, its expected participants and
    cells are ``STAGE_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]``, the
    manifest records ``stage_arm`` and ``diagnostics.md`` names the arm and
    carries ``STAGE_SENSITIVITY_READING_RULES``, change
    ``adni-stage-sensitivity``; so is a forced rank of the rank sweep, read
    with ``--analysis-dir results/motco_rank_sensitivity/rank_<kk>`` and the
    primary export: an analysis manifest with step ``rank-sensitivity``,
    whose forced rank and primary rank the manifest records under
    ``inputs.analysis.rank_sweep`` (``null`` on every other read); on the top
    rank (``RANK_SENSITIVITY_LADDER["diagnosed_rank"]``) the expected counts
    are ``RANK_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]`` (the
    rank-independent keys, the read and the rows at that rank), on another
    rank the rank-independent keys with a finding that the sweep's
    predeclared diagnostic is the top rank's, and ``diagnostics.md`` names the
    sweep and the forced rank and carries ``RANK_SENSITIVITY_READING_RULES``,
    change ``adni-rank-sensitivity``); a variable that is constant
    or has fewer than three complete rows; per component, the flagged
    variables as counts and names. The diagnostic reads sex and stage, so
    it is never a filter: no ``export``, ``analyze`` or sensitivity run reads
    its outputs, and arms, variants and the rank ladder are predeclared in a
    proposal, never derived from a diagnostic value.

    The manifest's ``numerics`` block records the numeric environment the run
    actually had (``_numerics_record``: host, CPU, the ``NUMERIC_SETTINGS``
    variables, numpy's ``log2`` target, each BLAS library's kernel and
    threads, ``pinned``); a run that is not pinned is a finding, never a
    stop, and its outputs are not committed.
    """
    log = "axis-diagnostics"
    threshold = DIAGNOSTIC_CORRELATION_THRESHOLD
    input_dir = Path(input_dir) if input_dir is not None else Path(MOTCO_INPUT_DIR)
    analysis_path = Path(analysis_dir) if analysis_dir is not None else Path(MOTCO_ANALYSIS_DIR)
    cohort_path = Path(cohort_dir) if cohort_dir is not None else Path(COHORT_DIR)
    final = Path(out_dir) if out_dir is not None else Path(DIAGNOSTICS_DIR)
    if final.exists() and not force:
        raise FileExistsError(f"{final} exists; pass --force to replace it")

    # --- the export ---------------------------------------------------------------
    loaded = _load_analysis_inputs(input_dir, step=log)
    findings: list[str] = list(loaded["findings"])
    blocks, frame, export_manifest = loaded["blocks"], loaded["metadata"], loaded["export_manifest"]
    rids = [str(r) for r in frame[SAMPLE_COLUMN]]
    for name, rec in loaded["inputs"].items():
        print(f"[{log}] {input_dir / name}: sha256 {rec['sha256'][:16]}…" + (f" equals {EXPORT_MANIFEST}" if "recorded" in rec else ""))

    # --- the analysis, chained to the export ----------------------------------------
    analysis = _check_analysis_inputs(input_dir, analysis_path, loaded)
    record, a_manifest = analysis["record"], analysis["manifest"]
    rank, components, scores = analysis["rank"], analysis["components"], analysis["scores"]
    a_settings = a_manifest.get("settings", {})
    latent_adjustment = a_settings.get("latent_adjustment")
    n_jobs = a_settings.get("n_jobs")
    selection = record["latent"]["component_selection"]
    export_variant = (a_manifest.get("variant") or {}).get("name") if a_manifest.get("step") == "export-sensitivity" else None
    stage_arm = (a_manifest.get("stage_arm") or {}).get("name") if a_manifest.get("step") == "stage-sensitivity" else None
    rank_sweep = None
    if a_manifest.get("step") == "rank-sensitivity":
        # a forced rank of the sweep (change adni-rank-sensitivity): its forced rank and the primary's rank
        recorded_sweep = a_manifest.get("rank_sweep") or {}
        rank_sweep = {
            "forced_rank": recorded_sweep.get("forced_rank", a_settings.get("forced_components")),
            "primary_rank": recorded_sweep.get("primary_rank"),
        }
    diagnosed = rank_sweep is not None and rank_sweep["forced_rank"] == RANK_SENSITIVITY_LADDER["diagnosed_rank"]
    is_primary = (
        analysis_path.resolve() == Path(MOTCO_ANALYSIS_DIR).resolve()
        and latent_adjustment is None and export_variant is None and stage_arm is None and rank_sweep is None
    )
    print(
        f"[{log}] {analysis_path}: {len(analysis['files'])} files read; the recorded hashes of {len(analysis['chain'])} "
        f"export files and of {EXPORT_MANIFEST} equal the files now; rank {rank} ({selection}), latent adjustment "
        f"{latent_adjustment}" + (f", export variant {export_variant}" if export_variant else "")
        + (f", stage arm {stage_arm}" if stage_arm else "")
        + (f", rank sweep forced rank {rank_sweep['forced_rank']}" if rank_sweep else "")
        + f", n_jobs {n_jobs}, primary {is_primary}"
    )

    # --- the cohort, chained to the export ------------------------------------------
    cohort = _check_cohort_chain(cohort_path, export_manifest, rids)
    print(
        f"[{log}] {cohort_path / COHORT_TABLE}: equals {COHORT_MANIFEST}, which equals the export's record; "
        f"{len(cohort['cohort'])} rows with every platform flag"
        + (" whose dx_bl the arm keeps" if export_manifest.get("stage_arm") else "")
        + " are the exported participants in order"
    )

    # --- the variables and the conditioning design -----------------------------------
    extra = cohort["cohort"][[SAMPLE_COLUMN, "dx_bl"]].copy() if "dx_bl" in cohort["cohort"].columns else cohort["cohort"][[SAMPLE_COLUMN]].copy()
    extra["_rid"] = extra[SAMPLE_COLUMN].astype(str)
    merged = frame.copy()
    merged["_rid"] = rids
    merged = merged.merge(extra.drop(columns=[SAMPLE_COLUMN]), on="_rid", how="left", validate="one_to_one").drop(columns=["_rid"])
    variables = _diagnostic_variables(merged)
    # The export manifest is written with sorted keys: take its codings in the model's (ANALYSIS_COVARIATES) order.
    recorded_codings = export_manifest["settings"]["covariates"]
    codings = {name: recorded_codings.get(name, spec) for name, spec in ANALYSIS_COVARIATES.items()}
    cov_record = record.get("covariates") or {}
    design = _conditioning_design(
        frame, codings, record_columns=cov_record.get("design_columns"), reference_row=cov_record.get("reference_row")
    )
    z = design.to_numpy(dtype=float)
    sources = {name: entry["file"] for name, entry in DIAGNOSTIC_VARIABLES.items()}
    n_missing: dict[str, int] = {}
    for name in variables.columns:
        v = variables[name].to_numpy(dtype=float)
        ok = np.isfinite(v)
        if (~ok).any():
            n_missing[name] = int((~ok).sum())
        if ok.sum() < 3:
            findings.append(f"variable {name}: {int(ok.sum())} complete row(s), fewer than three; its correlations are undefined")
        elif np.ptp(v[ok]) == 0:
            findings.append(f"variable {name}: constant over the complete rows; its correlations are undefined")
    if n_missing:
        findings.append(f"variables with missing values (pairwise-complete correlations): {n_missing}")
    sex_stage = _sex_stage(frame)
    cells = "; ".join(
        f"{sex_} {'/'.join(STAGE_LABELS)} " + "/".join(str(n) for n in sex_stage[sex_].values()) for sex_ in GROUP_VALUES
    )
    print(
        f"[{log}] participants: {len(frame)} ({cells}); {len(variables.columns)} variables ("
        + ", ".join(variables.columns) + f"); conditioning on {len(design.columns)} design columns ("
        + ", ".join(design.columns) + "), means equal to the record's reference row"
    )

    # --- axis correlations ------------------------------------------------------------
    axis_rows = [{**row, "source": sources[row["variable"]]} for row in _correlation_rows(scores, variables, z, threshold=threshold)]
    axis = pd.DataFrame(axis_rows, columns=list(_DIAGNOSTICS_AXIS_COLUMNS))

    # --- block principal components ------------------------------------------------
    export_offsets = export_manifest.get("counts", {}).get("phase_offset", {})
    phase_values = variables["phase"].to_numpy(dtype=float) if "phase" in variables.columns else None
    pc_rows: list[dict] = []
    block_info: dict[str, dict] = {}
    for platform in EXPORT_BLOCKS:
        pcs = block_principal_components(blocks[platform])
        pc1_phase = spearman(pcs["scores"]["pc1"], phase_values)[0] if phase_values is not None else float("nan")
        block_info[platform] = {
            "features": pcs["n_features"],
            "pcs": len(pcs["variance_share"]),
            "variance_shares": pcs["variance_share"],
            "pc1_phase": {
                "spearman": _finite_or_none(pc1_phase),
                "export_abs_corr_pearson": export_offsets.get(platform, {}).get("abs_corr_pc1_phase"),
            },
        }
        for row in _correlation_rows(pcs["scores"], variables, z, threshold=threshold):
            pc_rows.append({
                "block": platform,
                **{k: v for k, v in row.items() if k != "component_sd"},
                "variance_share": pcs["variance_share"][row["component"]],
                "source": sources[row["variable"]],
            })
        print(
            f"[{log}] {platform}: {pcs['n_features']} features; PC variance shares "
            + ", ".join(f"{k} {v:.3f}" for k, v in pcs["variance_share"].items())
            + f"; pc1 against phase: Spearman {_fmt_nan(pc1_phase, '.3f')} (export recorded |Pearson| "
            f"{_fmt_nan(export_offsets.get(platform, {}).get('abs_corr_pc1_phase'), '.3f')})"
        )
    block_pcs = pd.DataFrame(pc_rows, columns=list(_DIAGNOSTICS_PC_COLUMNS))

    # --- geometry shares and block composition ----------------------------------------
    groups = [str(g) for g in record["design"]["group_levels"]]
    stages = [str(st) for st in record["design"]["stage_levels"]]
    geometry = pd.DataFrame(geometry_shares(analysis["stage_means"], groups=groups, stages=stages), columns=list(_DIAGNOSTICS_GEOMETRY_COLUMNS))
    loading_shares = block_loading_shares(analysis["loadings"], EXPORT_BLOCKS)
    comp_rows: list[dict] = []
    per_component: dict[str, dict] = {}
    for c in components:
        sub = axis[axis["component"] == c]
        finite = sub[sub["spearman"].notna()]
        top = finite.loc[finite["spearman"].abs().idxmax()] if len(finite) else None
        flagged = sub[sub["flag_raw"] | sub["flag_partial"]]
        row = {
            "component": c,
            "sd": float(sub["component_sd"].iloc[0]),
            **{f"loading_share_{p}": loading_shares[c][p] for p in EXPORT_BLOCKS},
            "n_flagged_raw": int(sub["flag_raw"].sum()),
            "n_flagged_partial": int(sub["flag_partial"].sum()),
            "top_variable": None if top is None else str(top["variable"]),
            "top_spearman": float("nan") if top is None else float(top["spearman"]),
        }
        comp_rows.append(row)
        per_component[c] = {
            **{k: (_finite_or_none(v) if isinstance(v, float) else v) for k, v in row.items() if k != "component"},
            "flagged_variables": flagged["variable"].tolist(),
        }
        if len(flagged):
            ordered = flagged.assign(_abs=flagged["spearman"].abs().fillna(flagged["partial_spearman"].abs())).sort_values("_abs", ascending=False)
            findings.append(
                f"{c}: {len(flagged)} of {len(variables.columns)} variables flagged at |rho| >= {threshold} (raw or "
                "partial): " + ", ".join(
                    f"{r.variable} ({_fmt_nan(r.spearman, '.2f')}; partial {_fmt_nan(r.partial_spearman, '.2f')})"
                    for r in ordered.itertuples(index=False)
                )
            )
    comps_table = pd.DataFrame(comp_rows, columns=list(_DIAGNOSTICS_COMPONENT_COLUMNS))
    print(
        f"[{log}] components: " + "; ".join(
            f"{r['component']} sd {r['sd']:.4g}, " + "/".join(f"{r[f'loading_share_{p}']:.2f}" for p in EXPORT_BLOCKS)
            + f" {'/'.join(EXPORT_BLOCKS)}, {r['n_flagged_raw']} flagged" for r in comp_rows
        )
    )

    # --- counts, expected, findings -----------------------------------------------------
    counts: dict = {
        "participants": int(len(frame)),
        "sex_stage": sex_stage,
        "components": rank,
        "variables": list(variables.columns),
        "conditioning_columns": list(design.columns),
        "blocks": block_info,
        "primary": {"selected_rank": rank, "component_selection": selection, "latent_adjustment": latent_adjustment, "n_jobs": n_jobs},
        "rows": {
            "axis_correlations": int(len(axis)),
            "block_pcs": int(len(block_pcs)),
            "geometry_shares": int(len(geometry)),
            "components": int(len(comps_table)),
        },
        "flagged": {
            "axis_raw": int(axis["flag_raw"].sum()),
            "axis_partial": int(axis["flag_partial"].sum()),
            "block_pcs_raw": int(block_pcs["flag_raw"].sum()),
            "block_pcs_partial": int(block_pcs["flag_partial"].sum()),
        },
        "per_component": per_component,
        "variables_missing": n_missing,
    }
    expected_full = json.loads(json.dumps(DIAGNOSTICS_EXPECTED_COUNTS))
    variant_expected = (EXPORT_VARIANT_EXPECTED_COUNTS.get(export_variant) or {}).get("diagnostics") if export_variant else None
    if stage_arm is not None:
        # the arm's participants and cells, with the rank-independent keys (change adni-stage-sensitivity)
        expected = json.loads(json.dumps(STAGE_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]))
    elif diagnosed:
        # the sweep's predeclared diagnostic: its top rank's read and rows (change adni-rank-sensitivity)
        expected = json.loads(json.dumps(RANK_SENSITIVITY_EXPECTED_COUNTS["diagnostics"]))
    elif variant_expected is not None:
        # a variant's own block features, with the rank-independent keys (change adni-nmr-all-columns)
        expected = json.loads(json.dumps(variant_expected))
    else:
        expected = expected_full if is_primary else {k: expected_full[k] for k in DIAGNOSTICS_RANK_INDEPENDENT_KEYS}
    observed = _project(json.loads(json.dumps(counts, default=_json_default)), expected)
    deviations = [msg for key in expected for msg in _count_deviations(expected[key], observed.get(key), key)]
    findings += deviations
    if n_jobs != REPORTED_N_JOBS:
        findings.append(
            f"the analysis read ran with n_jobs = {n_jobs}: its permutation draws are not the reported ones "
            f"(REPORTED_N_JOBS = {REPORTED_N_JOBS}); the latent scores, stage means and loadings read here do not "
            "depend on n_jobs"
        )
    if rank_sweep is not None:
        findings.append(
            f"the analysis read is not the primary (directory {analysis_path}, forced rank {rank_sweep['forced_rank']} of "
            "the rank sweep): the primary's rank and row counts are not expected; "
            + (
                "the top rank's read and rows are (RANK_SENSITIVITY_EXPECTED_COUNTS), with the rank-independent counts"
                if diagnosed
                else "the rank-independent counts are, and the sweep's predeclared diagnostic is its top rank's (rank "
                f"{RANK_SENSITIVITY_LADDER['diagnosed_rank']}, RANK_SENSITIVITY_EXPECTED_COUNTS)"
            )
        )
    elif not is_primary:
        findings.append(
            f"the analysis read is not the primary (directory {analysis_path}, latent adjustment {latent_adjustment!r}"
            + (f", export variant {export_variant!r}" if export_variant else "")
            + (f", stage arm {stage_arm!r}" if stage_arm else "")
            + "): the primary's rank and the row counts are not expected; the rank-independent counts are"
            + (" (with the arm's participants and cells, STAGE_SENSITIVITY_EXPECTED_COUNTS)" if stage_arm else "")
            + (" (with the variant's block features, EXPORT_VARIANT_EXPECTED_COUNTS)" if variant_expected is not None else "")
        )

    numerics, numerics_findings = _numerics(f"[{log}]")
    findings += numerics_findings
    versions = _software_versions((*_MANIFEST_PACKAGES, "motco", "scikit-learn"))
    manifest = {
        "step": log,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": versions,
        "numerics": numerics,
        "git_revision": _git_revision(),
        "inputs": {
            "export": {
                "dir": str(input_dir),
                "files": loaded["inputs"],
                "export_manifest": {"name": EXPORT_MANIFEST, "sha256": loaded["inputs"][EXPORT_MANIFEST]["sha256"]},
                "export_git_revision": export_manifest.get("git_revision"),
                "export_created_at": export_manifest.get("created_at"),
            },
            "analysis": {
                "dir": str(analysis_path),
                "files": analysis["files"],
                "chain": analysis["chain"],
                "export_manifest_equals": analysis["export_manifest_equals"],
                "analysis_manifest": {"name": ANALYSIS_MANIFEST, "sha256": analysis["files"][ANALYSIS_MANIFEST]["sha256"]},
                "latent_adjustment": latent_adjustment,
                "n_jobs": n_jobs,
                "selected_rank": rank,
                "component_selection": selection,
                "is_primary": is_primary,
                **({"export_variant": export_variant} if export_variant else {}),
                **({"stage_arm": stage_arm} if stage_arm else {}),
                "rank_sweep": rank_sweep,
                "analysis_git_revision": a_manifest.get("git_revision"),
                "analysis_created_at": a_manifest.get("created_at"),
                "analysis_findings": a_manifest.get("findings", []),
            },
            "cohort": {"dir": str(cohort_path), "files": cohort["files"]},
        },
        "settings": {
            "DIAGNOSTIC_VARIABLES": [
                {
                    "name": name,
                    "file": entry["file"],
                    "column": entry["column"],
                    "derivation": entry["derivation"],
                    "levels": list(entry["levels"]) if "levels" in entry else None,
                }
                for name, entry in DIAGNOSTIC_VARIABLES.items()
            ],
            "DIAGNOSTIC_CORRELATION_THRESHOLD": threshold,
            "threshold_note": "a reporting flag on |rho|, raw and partial, not an adoption rule; no p-value is attached to any correlation",
            "DIAGNOSTIC_N_BLOCK_PCS": DIAGNOSTIC_N_BLOCK_PCS,
            "conditioning_columns": list(design.columns),
            "conditioning_source": (
                f"the ANALYSIS_COVARIATES columns of {EXPORT_COVARIATES} under the codings the export manifest records "
                "(numeric as is, drop-first indicators for the categorical ones), checked by name against "
                "DIAGNOSTIC_CONDITIONING_COLUMNS and the record's design_columns and by column mean against the "
                "record's reference_row"
            ),
            "definitions": _DIAGNOSTICS_DEFINITIONS,
            "downstream": "read by no export or analyze run; arms and variants are predeclared in a change proposal, never derived from a diagnostic value",
            "predeclared_sensitivity": ANALYSIS_PREDECLARED_LATENT_SENSITIVITY,
        },
        "counts": counts,
        "expected": expected,
        "primary_expectations_checked": is_primary,
        "deviations": deviations,
        "findings": findings,
    }

    # --- outputs ----------------------------------------------------------------------------
    tables = {"axis": axis, "block_pcs": block_pcs, "geometry": geometry, "components": comps_table}
    names = {
        "axis": DIAGNOSTICS_AXIS_CORRELATIONS,
        "block_pcs": DIAGNOSTICS_BLOCK_PCS,
        "geometry": DIAGNOSTICS_GEOMETRY_SHARES,
        "components": DIAGNOSTICS_COMPONENTS,
    }
    analysis_info = {
        "dir": str(analysis_path), "rank": rank, "selection": selection, "latent_adjustment": latent_adjustment,
        "n_jobs": n_jobs, "is_primary": is_primary, "participants": int(len(frame)), "export_variant": export_variant,
        "stage_arm": stage_arm, "rank_sweep": rank_sweep,
    }
    with _finalize_output_dir(final, force=force) as tmp:
        for key, name in names.items():
            tables[key].to_csv(tmp / name, index=False)
        (tmp / DIAGNOSTICS_SUMMARY).write_text(
            render_axis_diagnostics(
                tables, analysis=analysis_info, variables=DIAGNOSTIC_VARIABLES, blocks=block_info,
                findings=findings, threshold=threshold,
            )
        )
        written = [*names.values(), DIAGNOSTICS_SUMMARY]
        manifest["outputs"] = {
            name: {"sha256": _sha256_file(tmp / name), "bytes": (tmp / name).stat().st_size, "participant_level": False}
            for name in written
        }
        _write_manifest(tmp / DIAGNOSTICS_MANIFEST, manifest)

    print(f"[{log}] wrote {final}/ (" + ", ".join([*written, DIAGNOSTICS_MANIFEST]) + ")")
    print(
        f"[{log}] rows: " + ", ".join(f"{k} {v}" for k, v in counts["rows"].items()) + "; flagged: "
        + ", ".join(f"{k} {v}" for k, v in counts["flagged"].items())
    )
    if deviations:
        print(f"[{log}] {len(deviations)} count deviation(s) from the predeclared counts")
    else:
        print(
            f"[{log}] counts reproduce the predeclared ones"
            + (
                "" if is_primary
                else " (the top rank of the sweep: RANK_SENSITIVITY_EXPECTED_COUNTS)" if diagnosed
                else " (rank-independent keys only: not the primary)"
            )
        )
    for msg in findings:
        print(f"[{log}] FINDING: {msg}")
    return {"dir": final, "tables": tables, "manifest": manifest, "findings": findings}


# --- latent-sensitivity ------------------------------------------------------------

#: The columns of ``latent_sensitivity.csv``, in order (design D6 of
#: ``adni-latent-sensitivity``): the analysis, then the latent space, then per
#: statistic the observed value, p, rejection, null mean, SD and q95, then the
#: arm's latent-adjustment summary (empty for the primary).
_LATENT_SENSITIVITY_R2_KEYS: tuple[str, ...] = ("q05", "q25", "q50", "q75", "q95", "mean")
_LATENT_SENSITIVITY_COLUMNS: tuple[str, ...] = (
    "analysis", "directory", "latent_adjustment",
    "selected_rank", "component_selection", "cv_mean_auroc", "cv_repeats_completed", "eigengap",
    *(f"{s}_{k}" for s in ANALYSIS_STATISTICS for k in ("observed", "p", "rejected", "null_mean", "null_sd", "null_q95")),
    "residual_df", "cv_min_training_df",
    *(f"feature_r2_{q}" for q in _LATENT_SENSITIVITY_R2_KEYS),
)
#: The status of a statistic in the comparison: the primary's rejection under
#: ``ANALYSIS_REJECTION_RULE`` against the arm's.
_LATENT_SENSITIVITY_STATUS_SAME = "same"
_LATENT_SENSITIVITY_STATUS_DIFFERS = "differs (basis dependence)"
#: MOTCO's two latent-adjustment decisions, quoted in ``latent_sensitivity.md``
#: with their report paths (the proposal's "Why"); no number here is from a
#: run of the arm.
_MOTCO_LATENT_ADJUSTMENT_DECISIONS: tuple[dict[str, str], ...] = (
    {
        "report": "../MOTCO/docs/reports/latent-adjustment-type-i-2026-10-20.md",
        "decision": "adopt_stage",
        "reading": (
            "the `stage`-conditioned adjustment holds Type I at the validated design under conditions this change "
            "meets: the case study's own proposal justifies the covariate set (`LATENT_SENSITIVITY_COVARIATE_ROLES`), "
            "`group_stage` is not used, the record's `latent_adjustment` and `covariates` blocks are reported beside "
            "the results, no categorical level is rare enough to drop out of a CV training set, and the earlier "
            "binding statements stand; `angle` held the 0.0706 bound by 0.004 (0.067)"
        ),
    },
    {
        "report": "../MOTCO/docs/reports/latent-adjustment-power-2026-10-20.md",
        "decision": "candidate_fails",
        "reading": (
            "the adjustment loses `shape` power with a covariate-aligned nuisance axis (0.243 against 0.428) and "
            "small-magnitude `delta` power without one (0.400 against 0.520 at e = 0.1), so it is a sensitivity "
            "read beside the covariate-blind primary, never a replacement of it"
        ),
    },
)


def _check_primary_reference(analysis_dir: Path, loaded: dict, *, motco_version: str, step: str = "latent-sensitivity") -> dict:
    """Read the primary analysis as a chained, read-only reference (design D4 of ``adni-latent-sensitivity``).

    Parameters
    ----------
    analysis_dir:
        The primary's analysis directory (``results/motco_analysis``).
    loaded:
        ``_load_analysis_inputs(input_dir, step="latent-sensitivity")``: the
        export files' observed hashes.
    motco_version:
        The installed MOTCO version (``check_motco_version``).
    step:
        The step that reads the reference, ``latent-sensitivity`` (the arm),
        ``export-sensitivity`` (an export variant, change
        ``adni-nist-bridge``), ``stage-sensitivity`` (the CN / LMCI / AD arm,
        change ``adni-stage-sensitivity``) or ``rank-sensitivity`` (the rank
        sweep, change ``adni-rank-sensitivity``), named in the messages.

    Returns
    -------
    dict
        ``dir``, ``record`` (``result.json``), ``manifest``
        (``analysis_manifest.json``), ``files`` (the two files with sha256
        and bytes), ``chain`` (export file → ``True``),
        ``export_manifest_equals`` (``True``), ``rank``, ``n_jobs``,
        ``motco`` (the version the manifest records).

    Notes
    -----
    Reads only the two JSON files: no primary CSV, nothing participant-level.
    Stops, before anything is written and naming the file or setting, both
    values and the command to rerun: an absent directory or file (naming
    ``adni-sexdiff analyze``); an ``inputs.files`` hash or the
    ``inputs.export_manifest`` hash that differs from the export file now
    (the export was regenerated after the primary); a recorded
    ``settings.latent_adjustment`` that is not null or a record with a
    ``latent_adjustment`` block (the directory is not the primary); a
    recorded MOTCO version other than the installed one; a recorded
    ``ANALYSIS_SEED`` or ``ANALYSIS_PERMUTATIONS`` other than the constant.
    It does not require a ``numerics`` block: the committed primary manifest
    predates ``adni-portable-numerics``, and the primary's bytes are checked
    by that change's exact gate instead.
    """
    what = {"export-sensitivity": "the variant", "rank-sensitivity": "the sweep"}.get(step, "the arm")
    rerun = f"rerun `adni-sexdiff analyze` (then {step}); nothing was written"
    if not analysis_dir.is_dir():
        raise FileNotFoundError(
            f"{analysis_dir} does not exist: the primary analysis is {what}'s reference; run `adni-sexdiff analyze` "
            "first; nothing was written"
        )
    absent = [n for n in (ANALYSIS_RESULT, ANALYSIS_MANIFEST) if not (analysis_dir / n).is_file()]
    if absent:
        raise FileNotFoundError(
            f"{len(absent)} primary file(s) absent from {analysis_dir}: " + ", ".join(repr(n) for n in absent)
            + "; run `adni-sexdiff analyze` first; nothing was written"
        )
    manifest = json.loads((analysis_dir / ANALYSIS_MANIFEST).read_text())
    record = json.loads((analysis_dir / ANALYSIS_RESULT).read_text())
    recorded = manifest.get("inputs", {}).get("files", {})
    chain: dict[str, bool] = {}
    for name, entry in loaded["inputs"].items():
        if name == EXPORT_MANIFEST:
            continue
        rec = recorded.get(name, {}).get("sha256")
        if rec is None:
            raise RuntimeError(f"{name}: the primary's {ANALYSIS_MANIFEST} records no input hash for it; {rerun}")
        if rec != entry["sha256"]:
            raise RuntimeError(
                f"{name}: sha256 {entry['sha256']} now differs from the hash the primary's {ANALYSIS_MANIFEST} records "
                f"({rec}); the export was regenerated after the primary, {rerun}"
            )
        chain[name] = True
    rec_manifest = manifest.get("inputs", {}).get("export_manifest", {}).get("sha256")
    now_manifest = loaded["inputs"][EXPORT_MANIFEST]["sha256"]
    if rec_manifest != now_manifest:
        raise RuntimeError(
            f"{EXPORT_MANIFEST}: sha256 {now_manifest} now differs from the hash the primary's {ANALYSIS_MANIFEST} "
            f"records ({rec_manifest}); the export was regenerated after the primary, {rerun}"
        )
    settings = manifest.get("settings", {})
    latent_adjustment = settings.get("latent_adjustment")
    if latent_adjustment is not None or "latent_adjustment" in record:
        raise RuntimeError(
            f"{analysis_dir} is not the primary: {ANALYSIS_MANIFEST} records latent adjustment {latent_adjustment!r}"
            + (f" and {ANALYSIS_RESULT} carries a latent_adjustment block" if "latent_adjustment" in record else "")
            + " (the primary records None); point --analysis-dir at the primary (`adni-sexdiff analyze`); nothing was written"
        )
    recorded_motco = manifest.get("versions", {}).get("motco")
    if recorded_motco != motco_version:
        raise RuntimeError(
            f"the primary was made under MOTCO {recorded_motco} but MOTCO {motco_version} is installed; {what} "
            f"must share the primary's release (AGENTS.md constraint 4), {rerun}"
        )
    for name, constant in (("ANALYSIS_SEED", ANALYSIS_SEED), ("ANALYSIS_PERMUTATIONS", ANALYSIS_PERMUTATIONS)):
        seen = settings.get(name)
        if seen != constant:
            raise RuntimeError(
                f"the primary's {ANALYSIS_MANIFEST} records {name} = {seen!r} but the constant is {constant!r}; "
                f"{what} must share the primary's seed and permutations, {rerun}"
            )
    files = {
        name: {"sha256": _sha256_file(analysis_dir / name), "bytes": (analysis_dir / name).stat().st_size}
        for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST)
    }
    return {
        "dir": analysis_dir,
        "record": record,
        "manifest": manifest,
        "files": files,
        "chain": chain,
        "export_manifest_equals": True,
        "rank": int(record["latent"]["selected_lv"]),
        "n_jobs": settings.get("n_jobs"),
        "motco": recorded_motco,
    }


def _check_cohort_manifest(cohort_dir: Path, export_manifest: dict) -> dict:
    """Check ``cohort_manifest.json`` against the export manifest's record and read its descriptives (design D4).

    Returns ``manifest`` (the cohort manifest), ``descriptives`` (its
    ``descriptives`` block: per sex × stage cell of the intersection set,
    ``n``, age and education mean and sd, counts per level of ``apoe4``,
    ``phase`` and ``statin``) and ``files`` (``cohort_manifest.json`` with
    its sha256, bytes and ``equals_export_manifest``). Reads no
    ``cohort.csv``. Stops, before anything is written, on an absent manifest
    (naming ``adni-sexdiff cohort``), an export manifest that records no
    cohort-manifest hash, and a hash that differs (the cohort was rerun after
    the export; names ``export`` and ``analyze``).
    """
    path = cohort_dir / COHORT_MANIFEST
    if not path.is_file():
        raise FileNotFoundError(
            f"{COHORT_MANIFEST} is absent from {cohort_dir}; run `adni-sexdiff cohort` (then export, analyze) first; "
            "nothing was written"
        )
    recorded = export_manifest.get("inputs", {}).get("cohort", {}).get("manifest", {}).get("sha256")
    if recorded is None:
        raise RuntimeError(f"{EXPORT_MANIFEST} records no hash for {COHORT_MANIFEST}; rerun `adni-sexdiff export` (then analyze); nothing was written")
    now = _sha256_file(path)
    if recorded != now:
        raise RuntimeError(
            f"{COHORT_MANIFEST}: sha256 {now} now differs from the hash {EXPORT_MANIFEST} records ({recorded}); the "
            "cohort was rerun after the export, rerun `adni-sexdiff export` (then analyze, then latent-sensitivity); "
            "nothing was written"
        )
    manifest = json.loads(path.read_text())
    return {
        "manifest": manifest,
        "descriptives": manifest.get("descriptives"),
        "files": {COHORT_MANIFEST: {"sha256": now, "bytes": path.stat().st_size, "equals_export_manifest": True}},
    }


def _comparison_row(name: str, directory: Path, record: dict) -> dict:
    """One row of ``latent_sensitivity.csv`` (``_LATENT_SENSITIVITY_COLUMNS``), every value read from ``record``.

    ``directory`` is the primary's directory as read, and for the arm its
    subdirectory name under the step's output root (``analysis``), so that
    the table does not depend on where the root is and two runs into
    different roots stay byte-identical; the manifests record the full paths.
    """
    latent = record["latent"]
    adjustment = record.get("latent_adjustment") or {}
    row: dict = {
        "analysis": name,
        "directory": str(directory),
        "latent_adjustment": adjustment.get("conditioning"),
        "selected_rank": latent["selected_lv"],
        "component_selection": latent["component_selection"],
        "cv_mean_auroc": latent.get("cv_mean_auroc"),
        "cv_repeats_completed": latent.get("cv_repeats_completed"),
        "eigengap": (record.get("config_spectrum", {}).get("pooled") or {}).get("relative_eigengap"),
    }
    for s in ANALYSIS_STATISTICS:
        null = record["null_summary"].get(s, {})
        p = record["p_values"].get(s)
        row.update({
            f"{s}_observed": record["statistics"].get(s),
            f"{s}_p": p,
            f"{s}_rejected": _rejected(p),
            f"{s}_null_mean": null.get("mean"),
            f"{s}_null_sd": null.get("sd"),
            f"{s}_null_q95": null.get("q95"),
        })
    r2 = adjustment.get("feature_r2", {})
    row.update({
        "residual_df": adjustment.get("residual_df"),
        "cv_min_training_df": adjustment.get("cv_min_training_df"),
        **{f"feature_r2_{q}": r2.get(q) for q in _LATENT_SENSITIVITY_R2_KEYS},
    })
    return row


def _comparison_statuses(primary_row: dict, arm_row: dict, *, differs: str = _LATENT_SENSITIVITY_STATUS_DIFFERS) -> dict[str, str]:
    """``same`` when both rejections under ``ANALYSIS_REJECTION_RULE`` are equal, else ``differs`` (``differs (basis dependence)`` for the arm)."""
    return {
        s: _LATENT_SENSITIVITY_STATUS_SAME if primary_row[f"{s}_rejected"] == arm_row[f"{s}_rejected"]
        else differs
        for s in ANALYSIS_STATISTICS
    }


def _cohort_cell_findings(descriptives: dict | None, cell_sizes: dict) -> list[str]:
    """A finding per sex × stage cell whose cohort-manifest ``n`` differs from the record's cell size (design D9)."""
    cells = (descriptives or {}).get("cells", {})
    findings = []
    for g in GROUP_VALUES:
        for st in STAGE_LABELS:
            n_cohort = cells.get(g, {}).get(st, {}).get("n")
            n_record = cell_sizes.get(g, {}).get(st)
            if n_cohort != n_record:
                findings.append(
                    f"cohort manifest descriptives {g} {st}: n {n_cohort} differs from the record's cell size {n_record}; "
                    "the covariate-roles table shows the cohort manifest's cells, the analysis the record's"
                )
    return findings


def _rejection_text(value: bool | None) -> str:
    return "no p-value" if value is None else ("rejected" if value else "not rejected")


def _latent_sensitivity_findings(primary: dict, record: dict) -> list[str]:
    """The findings of design D9 that read the arm's record: a rank that differs from the primary's, a status that differs."""
    findings: list[str] = []
    rank_p, rank_a = int(primary["latent"]["selected_lv"]), int(record["latent"]["selected_lv"])
    if rank_a != rank_p:
        findings.append(
            f"the arm's CV-selected rank {rank_a} differs from the primary's {rank_p}: reported beside angle, not "
            "ranked as better or worse (arm rule 3)"
        )
    for s in ANALYSIS_STATISTICS:
        rp, ra = _rejected(primary["p_values"].get(s)), _rejected(record["p_values"].get(s))
        if rp != ra:
            findings.append(
                f"{s}: the arm's status ({_rejection_text(ra)}) differs from the primary's ({_rejection_text(rp)}) "
                f"at α = {ANALYSIS_ALPHA}: basis dependence, not a result of the arm; the primary's status stays "
                "the result (arm rule 2)"
            )
    return findings


def _arm_status_line(statistic: str, status: str, rejected_primary: bool | None, rejected_arm: bool | None) -> str:
    """The status sentence of one statistic in the comparison, shared by ``latent_sensitivity.md`` and the report (design D5 of ``adni-report``).

    Parameters
    ----------
    statistic:
        ``delta``, ``angle`` or ``shape``.
    status:
        ``_comparison_statuses`` for the statistic: ``same`` or
        ``differs (basis dependence)``.
    rejected_primary, rejected_arm:
        The two statuses under ``ANALYSIS_REJECTION_RULE`` (``_rejected``);
        ``None`` when a record holds no p-value.

    Returns
    -------
    str
        The sentence without its list marker: the status with both
        rejection texts, then the reading the pair implies (both
        non-rejections, the arm's weaker; both rejections; the arm rejects
        where the primary does not, basis dependence; or the reverse), the
        primary's status the result in every case. String-equal wherever it
        is printed.
    """
    arm_name = LATENT_SENSITIVITY_ARM["name"]
    rp, ra = rejected_primary, rejected_arm
    text = f"`{statistic}`: {status} (primary {_rejection_text(rp)}, {arm_name} {_rejection_text(ra)}). "
    if rp is None or ra is None:
        text += "A missing p-value is recorded as a finding."
    elif status == _LATENT_SENSITIVITY_STATUS_SAME and not rp:
        text += (
            "Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence "
            "that the sexes' trajectories agree"
            + (" in this respect (reading rule 3: no power statement exists at this design)." if statistic != "delta" else
               " (no power statement exists at this design).")
        )
    elif status == _LATENT_SENSITIVITY_STATUS_SAME:
        text += (
            "Both are rejections: evidence that the trajectories differ in this respect, with Type I controlled at "
            "the validated designs (reading rules 3 and 4); the arm adds no claim of its own (arm rule 8)."
        )
    elif ra and not rp:
        text += (
            "The arm rejects where the primary does not: basis dependence, not a result of the arm; the primary's "
            "non-rejection stays the result (arm rule 2)"
            + (", and an arm-only `angle` rejection is read against MOTCO's translation control (arm rule 4)." if statistic == "angle" else ".")
        )
    else:
        text += (
            "The primary rejects where the arm does not: the primary's rejection stays the result (reading rule 1); "
            "the arm's non-rejection is weaker than the primary's (arm rule 5)."
        )
    return text


def render_latent_sensitivity(
    rows: list[dict],
    *,
    statuses: dict[str, str],
    primary: dict,
    arm: dict,
    reference: dict,
    arm_info: dict,
    descriptives: dict | None,
    findings: list[str],
    n_jobs: int,
    alpha: float = ANALYSIS_ALPHA,
    rank_floor: int = ANALYSIS_RANK_FLOOR,
) -> str:
    """Render ``latent_sensitivity.md`` from the two records (design D6 of ``adni-latent-sensitivity``).

    Parameters
    ----------
    rows:
        The two rows of ``latent_sensitivity.csv`` (``_comparison_row``), the
        primary first.
    statuses:
        Per statistic, ``_comparison_statuses``.
    primary, arm:
        The two parsed ``result.json`` records.
    reference, arm_info:
        Per analysis: ``dir`` and ``files`` (``result.json`` with its sha256).
    descriptives:
        The cohort manifest's ``descriptives`` block, copied, not recomputed.
    findings:
        The comparison's findings.
    n_jobs:
        This run's ``n_jobs``.
    alpha, rank_floor:
        ``ANALYSIS_ALPHA`` and ``ANALYSIS_RANK_FLOOR``.

    Returns
    -------
    str
        Markdown, in this order: the header (both directories with their
        ``result.json`` sha256, the arm by constant name, ``n_jobs``); the
        statistics table (primary row, arm row, status) with both ranks,
        floors, eigengaps and null summaries beside ``angle``; the
        latent-space table; the arm's latent-adjustment block; the covariate
        roles beside the cohort manifest's per-cell descriptives; MOTCO's two
        latent-adjustment decisions; the findings; ``READING_RULES`` then
        ``LATENT_SENSITIVITY_READING_RULES``, both verbatim. Numbers carry
        six significant digits.
    """
    p_row, a_row = rows[0], rows[1]
    design = arm["design"]
    stages = [str(st) for st in design["stage_levels"]]
    groups = [str(g) for g in design["group_levels"]]
    arm_name = LATENT_SENSITIVITY_ARM["name"]
    adjustment = arm["latent_adjustment"]
    lines = [
        "# MOTCO latent-adjustment sensitivity: ADNI serum metabolomics, sex × stage",
        "",
        f"The primary analysis (`{reference['dir']}`, `result.json` sha256 `{reference['files'][ANALYSIS_RESULT]['sha256']}`) "
        f"beside its predeclared sensitivity arm `{arm_name}` (`LATENT_SENSITIVITY_ARM`, change "
        f"`{LATENT_SENSITIVITY_ARM['change']}`: `{LATENT_SENSITIVITY_ARM['setting']}` = `{adjustment['conditioning']}`, "
        f"the same five covariates, every other setting the primary's; `{arm_info['dir']}`, `result.json` sha256 "
        f"`{arm_info['files'][ANALYSIS_RESULT]['sha256']}`). MOTCO {arm['software']['motco']}; n = {design['n_samples']}; "
        f"{arm['measurement']['permutations']} RRPP permutations, seed {arm['measurement']['seed']}; α = {alpha}, rejected "
        f"when {ANALYSIS_REJECTION_RULE} (`ANALYSIS_REJECTION_RULE`); n_jobs {n_jobs}"
        + ("" if n_jobs == REPORTED_N_JOBS else f" (not a reported run: reported runs use n_jobs = {REPORTED_N_JOBS})")
        + ". The primary row comes first and its status is the result; the arm is read beside it and never replaces "
        "it (arm rule 1). A status that differs is basis dependence, not a result of the arm (arm rule 2). Every value "
        "below is read from the two `result.json` records.",
        "",
        "## Statistics",
        "",
        "| statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |",
        "|---|---|---:|---:|:---:|---:|---:|---:|---|",
    ]
    for s in ANALYSIS_STATISTICS:
        for label, row in (("primary", p_row), (arm_name, a_row)):
            rejected = row[f"{s}_rejected"]
            lines.append(
                f"| {s} | {label} | {_fmt(row[f'{s}_observed'])} | {_fmt(row[f'{s}_p'])} | "
                f"{'n/a' if rejected is None else ('yes' if rejected else 'no')} | {_fmt(row[f'{s}_null_mean'])} | "
                f"{_fmt(row[f'{s}_null_sd'])} | {_fmt(row[f'{s}_null_q95'])} | {statuses[s]} |"
            )
    lines += [
        "",
        f"`angle` (degrees, endpoint stages {stages[0]} and {stages[-1]}) is read beside each analysis' CV-selected "
        f"rank, floor, eigengap and null summary (reading rule 2, arm rule 3): primary rank {p_row['selected_rank']} "
        f"(floor {rank_floor}, pooled relative eigengap {_fmt(p_row['eigengap'])}); {arm_name} rank "
        f"{a_row['selected_rank']} (floor {rank_floor}, eigengap {_fmt(a_row['eigengap'])})"
        + (
            "; the ranks differ, which is reported, not ranked as better or worse (arm rule 3)."
            if p_row["selected_rank"] != a_row["selected_rank"] else "; the ranks are equal."
        ),
        "",
        "Status per statistic:",
        "",
    ]
    lines += [
        "- " + _arm_status_line(s, statuses[s], p_row[f"{s}_rejected"], a_row[f"{s}_rejected"]) for s in ANALYSIS_STATISTICS
    ]
    p_perm = (primary.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {})
    a_perm = (arm.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {})
    lines += [
        "",
        "## Latent space",
        "",
        f"| quantity | primary | {arm_name} |",
        "|---|---:|---:|",
        f"| PLS-DA rank (selection) | {p_row['selected_rank']} (`{p_row['component_selection']}`) | {a_row['selected_rank']} (`{a_row['component_selection']}`) |",
        f"| rank floor (`ANALYSIS_RANK_FLOOR`) | {rank_floor} | {rank_floor} |",
        f"| cv_mean_auroc | {_fmt(p_row['cv_mean_auroc'])} | {_fmt(a_row['cv_mean_auroc'])} |",
        f"| CV repeats completed | {p_row['cv_repeats_completed']} | {a_row['cv_repeats_completed']} |",
        f"| pooled relative eigengap | {_fmt(p_row['eigengap'])} | {_fmt(a_row['eigengap'])} |",
        f"| eigengap permutation null q05 / q50 / q95 | {_fmt(p_perm.get('q05'))} / {_fmt(p_perm.get('q50'))} / {_fmt(p_perm.get('q95'))} "
        f"| {_fmt(a_perm.get('q05'))} / {_fmt(a_perm.get('q50'))} / {_fmt(a_perm.get('q95'))} |",
        "",
        "The two analyses share the export, the covariates and their design, the cells, the CV folds (stratified on "
        "the stage, as the primary's), the seed and the permutations; they differ only in the latent basis and the "
        "CV-selected rank (arm rule 2).",
    ]
    design_cols = [str(c) for c in adjustment["design_columns"]]
    stage_names = {f"stage[{k}]": st for k, st in enumerate(stages)}
    n_cond = sum(c in stage_names for c in design_cols)
    r2 = adjustment.get("feature_r2", {})
    lines += [
        "",
        f"## Latent adjustment of the arm",
        "",
        f"- conditioning: `{adjustment['conditioning']}` (`{LATENT_SENSITIVITY_ARM['setting']}`): the basis is fitted on "
        "the pooled-standardized features with the covariates regressed out given the intercept and the stage "
        "indicators, per CV training set and on the full sample; the raw features are projected onto it; the "
        "trajectory model, LS-means and RRPP are the primary's",
        "- covariates residualized (in order): " + ", ".join(f"`{c}`" for c in adjustment["covariates"]),
        f"- residualization design columns: {len(design_cols)} ("
        + ", ".join(f"{c} = {stage_names[c]}" if c in stage_names else c for c in design_cols) + ")",
        f"- samples {adjustment['n_samples']}; residual df {adjustment['residual_df']} (n − 1 − {n_cond} stage "
        f"indicator(s) − {len(design_cols) - n_cond} design column(s)); smallest CV training df "
        f"{adjustment.get('cv_min_training_df')}",
        f"- feature scale: `{adjustment['feature_scale']}`",
        "- feature R² of the covariates given the intercept and the stage indicators (the share of each feature's "
        "variance the residualization removed; arm rule 6): q05 / q25 / q50 / q75 / q95 "
        + " / ".join(_fmt(r2.get(q), ".3f") for q in ("q05", "q25", "q50", "q75", "q95"))
        + f"; mean {_fmt(r2.get('mean'), '.3f')}; fraction above 0.5 {_fmt(r2.get('fraction_above_0.5'), '.3f')}",
        "",
        "## Covariates residualized by the arm",
        "",
        "Each covariate's relation to the stage effect (`LATENT_SENSITIVITY_COVARIATE_ROLES`, decided before any run; "
        "no statistic or threshold is computed for it and nothing changes because of it). Residualizing a covariate "
        "that mediates the stage effect removes real stage signal, and no data can tell a confounder from a mediator "
        "(arm rule 7).",
        "",
        "| covariate | role | variable | justification |",
        "|---|---|---|---|",
    ]
    for name, role in LATENT_SENSITIVITY_COVARIATE_ROLES.items():
        lines.append(f"| `{name}` | {role['role']} | {role['variable']} | {role['justification']} |")
    mediators = [name for name, role in LATENT_SENSITIVITY_COVARIATE_ROLES.items() if role["role"] == "mediator candidate"]
    lines += [
        "",
        "The mediator candidate is " + ", ".join(f"`{m}`" for m in mediators) + ": a treatment that may follow "
        "diagnosis, so the arm's basis may have removed stage signal that runs through treatment (arm rule 7). It "
        "stays in the arm because the arm was predeclared with the five covariates.",
        "",
        "Per sex × stage cell of the analysis cohort, copied from `cohort_manifest.json` (`descriptives`, set "
        f"`{(descriptives or {}).get('set')}`), not recomputed: n, age and education mean (sd), and counts per level "
        "of `apoe4` (0 / 1 / 2), `phase` (ADNI1 / ADNI2GO) and `statin` (0 / 1).",
        "",
        "| sex | stage | n | age mean (sd) | education mean (sd) | apoe4 0 / 1 / 2 | phase ADNI1 / ADNI2GO | statin 0 / 1 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    cells = (descriptives or {}).get("cells", {})
    for g in groups:
        for st in stages:
            c = cells.get(g, {}).get(st)
            if not c:
                lines.append(f"| {g} | {st} | n/a | n/a | n/a | n/a | n/a | n/a |")
                continue
            lines.append(
                f"| {g} | {st} | {c.get('n')} | {_fmt(c.get('age', {}).get('mean'))} ({_fmt(c.get('age', {}).get('sd'))}) | "
                f"{_fmt(c.get('education', {}).get('mean'))} ({_fmt(c.get('education', {}).get('sd'))}) | "
                + " / ".join(str(c.get("apoe4", {}).get(k, "n/a")) for k in ("0", "1", "2")) + " | "
                + " / ".join(str(c.get("phase", {}).get(k, "n/a")) for k in ("ADNI1", "ADNI2GO")) + " | "
                + " / ".join(str(c.get("statin", {}).get(k, "n/a")) for k in ("0", "1")) + " |"
            )
    lines += [
        "",
        "## MOTCO's latent-adjustment decisions",
        "",
        "Measured at one design (n = 80, the SEA-AD MTG structure, 498 features, eight covariates in nine design "
        "columns), none at this one; the arm carries no Type I or power claim of its own (arm rule 8).",
        "",
    ]
    for decision in _MOTCO_LATENT_ADJUSTMENT_DECISIONS:
        lines.append(f"- `{decision['decision']}` (`{decision['report']}`): {decision['reading']}.")
    lines += ["", "## Findings", ""]
    lines += [f"- {msg}" for msg in findings] or ["None."]
    lines += [
        "",
        "## Reading rules",
        "",
        "Binding for every reader of the result (`READING_RULES`, decided by `adni-analyze` before any run):",
        "",
    ]
    lines += [f"{i}. {rule}" for i, rule in enumerate(READING_RULES, 1)]
    lines += [
        "",
        "## Reading rules of the arm",
        "",
        f"Binding for every reader of the arm (`LATENT_SENSITIVITY_READING_RULES`, decided by "
        f"`{LATENT_SENSITIVITY_ARM['change']}` before any run), after `READING_RULES`:",
        "",
    ]
    lines += [f"{i}. {rule}" for i, rule in enumerate(LATENT_SENSITIVITY_READING_RULES, 1)]
    return "\n".join(lines) + "\n"


def run_latent_sensitivity(
    *,
    input_dir: str | Path | None = None,
    analysis_dir: str | Path | None = None,
    cohort_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    n_jobs: int = REPORTED_N_JOBS,
    force: bool = False,
) -> dict:
    """Run the predeclared ``stage``-conditioned latent-adjustment arm beside the primary analysis.

    Parameters
    ----------
    input_dir:
        Output directory of ``export`` (default ``constants.MOTCO_INPUT_DIR``).
        Read as ``analyze`` reads it: ``p180.csv``, ``nmr.csv``,
        ``metadata.csv``, ``covariates.csv`` (each checked against the sha256
        ``manifest.json`` records) and ``manifest.json``.
    analysis_dir:
        The primary's analysis directory (default
        ``constants.MOTCO_ANALYSIS_DIR``); only ``result.json`` and
        ``analysis_manifest.json`` are read, never written.
    cohort_dir:
        Output directory of ``cohort`` (default ``constants.COHORT_DIR``);
        only ``cohort_manifest.json`` is read (its hash and its per-cell
        descriptives), no ``cohort.csv``.
    out_dir:
        The output root (default ``constants.LATENT_SENSITIVITY_DIR``), with
        the subdirectories ``LATENT_SENSITIVITY_SUBDIRS``: ``analysis/`` and
        ``comparison/`` are written here; ``diagnostics/`` never is.
    n_jobs:
        MOTCO's CV and RRPP workers, as for ``analyze``; reported runs use
        ``constants.REPORTED_N_JOBS`` (1) and another value is a finding.
    force:
        Replace existing ``analysis/`` and ``comparison/`` directories (after
        both are complete).

    Returns
    -------
    dict
        ``{"dir": Path, "analysis": {...}, "comparison": {"rows": [...], "statuses": {...}, "manifest": dict}, "findings": [...]}``.

    Notes
    -----
    The arm (``LATENT_SENSITIVITY_ARM``, decided by ``adni-latent-sensitivity``
    and equal to the arm ``adni-analyze`` predeclared): one
    ``analyze_trajectories`` call through ``_run_trajectory_analysis`` at the
    primary's settings plus ``covariate_latent_adjustment = "stage"``, the
    same five covariates, never assembled from MOTCO's primitives. The
    primary is never rerun or written; it is read beside the arm as a
    sensitivity, never replaced (MOTCO's power comparison returned
    ``candidate_fails``). ``group_stage`` does not run; the arm and its
    settings are constants, never flags.

    Checks, in this order, before anything is written: the gates of
    ``analyze`` (``check_motco_version``, ``check_motco_rank_floor``);
    ``analysis/`` or ``comparison/`` existing without ``force``; the export
    (``_load_analysis_inputs``); the primary as a chained, read-only
    reference (``_check_primary_reference``: the directory and its two JSON
    files exist, every ``inputs.files`` hash and the export-manifest hash
    equal the export files now, no latent adjustment is recorded, the
    recorded MOTCO version equals the installed one, ``ANALYSIS_SEED`` and
    ``ANALYSIS_PERMUTATIONS`` equal the constants); the cohort manifest
    against the export manifest's record (``_check_cohort_manifest``). A
    failure stops the step naming the file or setting, both values and the
    command to rerun, never a participant, and nothing is written. The
    rare-level condition is MOTCO's: a residualization design that is not of
    full rank, on the full sample or in a CV training set, stops the step
    with MOTCO's message (naming the repeat and fold) and nothing written;
    no level is merged and no setting changed.

    Output contract (``results/motco_latent_sensitivity/``): ``analysis/``
    (staged as ``analysis.tmp/``), the seven files ``analyze`` writes, laid
    out as the primary's so that ``axis-diagnostics --analysis-dir`` reads
    it unchanged: MOTCO's ``result.json`` (with its ``latent_adjustment``
    block), ``latent_scores.csv``, ``pls_loadings.csv``, ``stage_means.csv``,
    ``analysis_metadata.csv``, ``analysis_manifest.json`` (``step``
    ``latent-sensitivity``; the five export files as its inputs; ``arm``,
    the constant by name; ``reference``, the primary's directory, its two
    hashes, rank, MOTCO version and ``n_jobs``; every setting as passed with
    ``latent_adjustment`` ``stage``; ``cli_equivalent`` naming
    ``--latent-adjustment stage``; the ``numerics`` block; the predeclared
    ``LATENT_SENSITIVITY_EXPECTED_COUNTS`` beside the observed ones with
    deviations; output hashes with a participant-level flag; findings) and
    ``summary.md`` (``render_analysis_summary`` with the latent-adjustment
    section and both sets of reading rules). ``comparison/`` (staged as
    ``comparison.tmp/``): ``latent_sensitivity.csv`` (two rows, the primary
    then the arm; ``_LATENT_SENSITIVITY_COLUMNS``: the latent adjustment,
    the selected rank and selection mode, ``cv_mean_auroc``, CV repeats,
    the eigengap, per statistic the observed value, p, rejection under
    ``ANALYSIS_REJECTION_RULE`` and the null mean, SD and q95, and for the
    arm the residual df, the smallest CV training df and the ``feature_r2``
    quantiles and mean; every value read from the two records, no runtime
    column, so a rerun is byte-identical), ``latent_sensitivity.md``
    (``render_latent_sensitivity``) and ``latent_sensitivity_manifest.json``
    (versions, ``numerics``, git revision; the eight inputs with sha256 and
    the chain results; ``LATENT_SENSITIVITY_ARM``,
    ``LATENT_SENSITIVITY_COVARIATE_ROLES``, ``ANALYSIS_ALPHA`` with the
    rule, ``n_jobs``; ``reference`` and ``arm``; the counts: statuses,
    ranks, CV AUROC, the latent-adjustment block, the cohort manifest's
    cells against the record's; the arm's ``expected`` and ``deviations``,
    copied; output hashes; findings). Both directories are renamed together
    when both are complete; a failure leaves both as they were.
    ``analysis/latent_scores.csv`` and ``analysis/analysis_metadata.csv``
    are participant-level (matched by the existing ``results/**`` ignore
    patterns); every other file is aggregate and committed.
    ``diagnostics/`` is never touched: when ``analysis/`` is replaced while
    it exists, a finding says the arm diagnostic must be rerun; the step
    tests the directory's existence and opens nothing under it.

    Findings, recorded and printed, never a stop: every finding condition
    of ``analyze`` (count deviations, ``n_jobs`` not 1, a rank at the floor,
    fewer CV repeats, a non-finite statistic or p-value, a moved MOTCO
    default, a clamped CV setting, a run that is not pinned); an arm rank
    that differs from the primary's (both named); a statistic whose
    rejection status differs from the primary's, named as basis dependence;
    a primary read with ``n_jobs`` not 1; cohort-manifest cells that differ
    from the record's cell sizes; a replaced arm whose ``diagnostics/``
    exists. No finding names a participant. No arm value changes a
    constant, selects a covariate, reruns the primary or defines a variant.
    """
    step = "latent-sensitivity"
    log = f"[{step}]"
    conditioning = LATENT_SENSITIVITY_ARM["conditioning"]
    motco_version = check_motco_version()
    rank_floor = check_motco_rank_floor()
    input_dir = Path(input_dir) if input_dir is not None else Path(MOTCO_INPUT_DIR)
    primary_dir = Path(analysis_dir) if analysis_dir is not None else Path(MOTCO_ANALYSIS_DIR)
    cohort_path = Path(cohort_dir) if cohort_dir is not None else Path(COHORT_DIR)
    root = Path(out_dir) if out_dir is not None else Path(LATENT_SENSITIVITY_DIR)
    analysis_final = root / LATENT_SENSITIVITY_SUBDIRS["analysis"]
    comparison_final = root / LATENT_SENSITIVITY_SUBDIRS["comparison"]
    diagnostics_final = root / LATENT_SENSITIVITY_SUBDIRS["diagnostics"]
    existing = [str(d) for d in (analysis_final, comparison_final) if d.exists()]
    if existing and not force:
        raise FileExistsError(
            " and ".join(existing) + (" exist" if len(existing) > 1 else " exists")
            + f"; pass --force to replace the arm and its comparison ({diagnostics_final} is never touched)"
        )
    print(
        f"{log} MOTCO {motco_version}; rank floor {rank_floor} equals MOTCO's default; arm "
        f"{LATENT_SENSITIVITY_ARM['name']} (LATENT_SENSITIVITY_ARM: {LATENT_SENSITIVITY_ARM['setting']} = "
        f"{conditioning!r}, the primary's five covariates and settings), read beside the primary"
    )

    # --- the export, the primary as a reference, the cohort manifest -------------------
    loaded = _load_analysis_inputs(input_dir, step=step)
    reference = _check_primary_reference(primary_dir, loaded, motco_version=motco_version)
    primary, p_manifest = reference["record"], reference["manifest"]
    primary_n_jobs = reference["n_jobs"]
    print(
        f"{log} {primary_dir}: the primary (rank {reference['rank']}, latent adjustment none, n_jobs {primary_n_jobs}, "
        f"MOTCO {reference['motco']}); the hashes it records for {len(reference['chain'])} export files and "
        f"{EXPORT_MANIFEST} equal the files now; its {ANALYSIS_RESULT} and {ANALYSIS_MANIFEST} are read, never written"
    )
    cohort = _check_cohort_manifest(cohort_path, loaded["export_manifest"])
    cells = (cohort["descriptives"] or {}).get("cells", {})
    n_cells = sum(len(v) for v in cells.values()) if isinstance(cells, dict) else 0
    print(
        f"{log} {cohort_path / COHORT_MANIFEST}: equals the hash {EXPORT_MANIFEST} records; descriptives for "
        f"{n_cells} sex × stage cells read (no {COHORT_TABLE})"
    )

    # --- the findings that do not depend on the arm's record (design D9) --------------------
    static_findings: list[str] = []
    if primary_n_jobs != REPORTED_N_JOBS:
        static_findings.append(
            f"the primary read ran with n_jobs = {primary_n_jobs}: its permutation draws are not the reported ones "
            f"(REPORTED_N_JOBS = {REPORTED_N_JOBS}), so the reference is not a reported run"
        )
    if analysis_final.exists() and diagnostics_final.exists():
        static_findings.append(
            f"{diagnostics_final} exists and was computed from the arm this run replaces; rerun `adni-sexdiff "
            f"axis-diagnostics --analysis-dir {analysis_final} --out-dir {diagnostics_final} --force` (the directory "
            "is neither read nor written here)"
        )

    def arm_extra(record: dict) -> dict:
        return {
            "arm": {"constant": "LATENT_SENSITIVITY_ARM", **LATENT_SENSITIVITY_ARM},
            "reference": {
                "dir": str(primary_dir),
                "files": reference["files"],
                "selected_rank": reference["rank"],
                "latent_adjustment": None,
                "n_jobs": primary_n_jobs,
                "motco": reference["motco"],
                "git_revision": p_manifest.get("git_revision"),
                "created_at": p_manifest.get("created_at"),
            },
            "findings": [*static_findings, *_latent_sensitivity_findings(primary, record)],
        }

    # --- the arm, then the comparison, staged together (design D5) ------------------------
    root_existed = root.exists()
    try:
        return _run_latent_sensitivity_outputs(
            log=log, step=step, conditioning=conditioning, n_jobs=n_jobs, force=force, input_dir=input_dir,
            primary_dir=primary_dir, cohort_path=cohort_path, root=root, analysis_final=analysis_final,
            comparison_final=comparison_final, diagnostics_final=diagnostics_final, loaded=loaded,
            reference=reference, cohort=cohort, arm_extra=arm_extra,
        )
    except BaseException:
        # a run that fails before writing leaves no output root behind (nothing is kept for inspection in an empty one)
        if not root_existed and root.is_dir() and not any(root.iterdir()):
            root.rmdir()
        raise


def _run_latent_sensitivity_outputs(
    *,
    log: str,
    step: str,
    conditioning: str,
    n_jobs: int,
    force: bool,
    input_dir: Path,
    primary_dir: Path,
    cohort_path: Path,
    root: Path,
    analysis_final: Path,
    comparison_final: Path,
    diagnostics_final: Path,
    loaded: dict,
    reference: dict,
    cohort: dict,
    arm_extra: Callable[[dict], dict],
) -> dict:
    """The arm and the comparison of ``run_latent_sensitivity``, staged as ``analysis.tmp/`` and ``comparison.tmp/`` and renamed together."""
    primary, p_manifest = reference["record"], reference["manifest"]
    primary_n_jobs = reference["n_jobs"]
    cells = (cohort["descriptives"] or {}).get("cells", {})
    with _finalize_output_dir(analysis_final, force=force) as a_tmp:
        arm = _run_trajectory_analysis(
            input_dir=input_dir,
            final=analysis_final,
            n_jobs=n_jobs,
            force=force,
            step=step,
            latent_adjustment=conditioning,
            expected=LATENT_SENSITIVITY_EXPECTED_COUNTS,
            manifest_extra=arm_extra,
            loaded=loaded,
            staging=a_tmp,
        )
        record, a_manifest = arm["record"], arm["manifest"]
        rows = [
            _comparison_row("primary", primary_dir, primary),
            _comparison_row(LATENT_SENSITIVITY_ARM["name"], Path(LATENT_SENSITIVITY_SUBDIRS["analysis"]), record),
        ]
        statuses = _comparison_statuses(rows[0], rows[1])
        table = pd.DataFrame(rows, columns=list(_LATENT_SENSITIVITY_COLUMNS), dtype=object)
        cell_findings = _cohort_cell_findings(cohort["descriptives"], record["design"]["cell_sizes"])
        findings: list[str] = [*arm_extra(record)["findings"], *cell_findings]
        if n_jobs != REPORTED_N_JOBS:
            findings.append(
                f"n_jobs = {n_jobs}: MOTCO seeds one RRPP stream per worker, so the arm's permutation draws, p-values "
                f"and null summaries differ from an n_jobs = {REPORTED_N_JOBS} run; the arm is not reported "
                f"(REPORTED_N_JOBS = {REPORTED_N_JOBS})"
            )
        for s in ANALYSIS_STATISTICS:
            print(
                f"{log} {s}: primary {_fmt(rows[0][f'{s}_observed'])} (p {_fmt(rows[0][f'{s}_p'])}, "
                f"{_rejection_text(rows[0][f'{s}_rejected'])}); {LATENT_SENSITIVITY_ARM['name']} "
                f"{_fmt(rows[1][f'{s}_observed'])} (p {_fmt(rows[1][f'{s}_p'])}, {_rejection_text(rows[1][f'{s}_rejected'])}); "
                f"status {statuses[s]}"
            )
        print(
            f"{log} rank: primary {rows[0]['selected_rank']}, {LATENT_SENSITIVITY_ARM['name']} {rows[1]['selected_rank']}; "
            f"cv_mean_auroc {_fmt(rows[0]['cv_mean_auroc'], '.4f')} / {_fmt(rows[1]['cv_mean_auroc'], '.4f')}; eigengap "
            f"{_fmt(rows[0]['eigengap'], '.4f')} / {_fmt(rows[1]['eigengap'], '.4f')}"
        )
        numerics, numerics_findings = _numerics(log)
        findings += numerics_findings
        arm_files = {
            name: {"sha256": _sha256_file(a_tmp / name), "bytes": (a_tmp / name).stat().st_size}
            for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST)
        }
        arm_info = {
            "dir": str(analysis_final),
            "files": arm_files,
            "constant": "LATENT_SENSITIVITY_ARM",
            "name": LATENT_SENSITIVITY_ARM["name"],
            "latent_adjustment": conditioning,
            "selected_rank": int(record["latent"]["selected_lv"]),
            "n_jobs": n_jobs,
            "findings": a_manifest["findings"],
        }
        versions = _software_versions((*_MANIFEST_PACKAGES, "motco", "scikit-learn"))
        manifest = {
            "step": step,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "versions": versions,
            "numerics": numerics,
            "git_revision": _git_revision(),
            "inputs": {
                "export": {
                    "dir": str(input_dir),
                    "files": loaded["inputs"],
                    "export_manifest": {"name": EXPORT_MANIFEST, "sha256": loaded["inputs"][EXPORT_MANIFEST]["sha256"]},
                    "export_git_revision": loaded["export_manifest"].get("git_revision"),
                    "export_created_at": loaded["export_manifest"].get("created_at"),
                },
                "primary": {
                    "dir": str(primary_dir),
                    "files": reference["files"],
                    "chain": reference["chain"],
                    "export_manifest_equals": reference["export_manifest_equals"],
                    "primary_records_export": True,
                    "latent_adjustment": None,
                    "n_jobs": primary_n_jobs,
                    "selected_rank": reference["rank"],
                    "motco": reference["motco"],
                    "seed_and_permutations_equal_constants": True,
                    "git_revision": p_manifest.get("git_revision"),
                    "created_at": p_manifest.get("created_at"),
                },
                "cohort": {
                    "dir": str(cohort_path),
                    "files": cohort["files"],
                    "cohort_manifest_equals_export_record": True,
                    "descriptives_set": (cohort["descriptives"] or {}).get("set"),
                },
            },
            "settings": {
                "LATENT_SENSITIVITY_ARM": LATENT_SENSITIVITY_ARM,
                "LATENT_SENSITIVITY_COVARIATE_ROLES": LATENT_SENSITIVITY_COVARIATE_ROLES,
                "ANALYSIS_ALPHA": ANALYSIS_ALPHA,
                "ANALYSIS_REJECTION_RULE": ANALYSIS_REJECTION_RULE,
                "ANALYSIS_RANK_FLOOR": ANALYSIS_RANK_FLOOR,
                "n_jobs": n_jobs,
                "REPORTED_N_JOBS": REPORTED_N_JOBS,
                "status_rule": (
                    f"{_LATENT_SENSITIVITY_STATUS_SAME!r} when both rejections under ANALYSIS_REJECTION_RULE are "
                    f"equal, else {_LATENT_SENSITIVITY_STATUS_DIFFERS!r}; the primary's status is the result either way"
                ),
                "columns": list(_LATENT_SENSITIVITY_COLUMNS),
                "motco_latent_adjustment_decisions": list(_MOTCO_LATENT_ADJUSTMENT_DECISIONS),
            },
            "reference": arm_extra(record)["reference"],
            "arm": arm_info,
            "counts": {
                "rows": len(rows),
                "statuses": statuses,
                "ranks": {"primary": rows[0]["selected_rank"], LATENT_SENSITIVITY_ARM["name"]: rows[1]["selected_rank"]},
                "cv_mean_auroc": {"primary": rows[0]["cv_mean_auroc"], LATENT_SENSITIVITY_ARM["name"]: rows[1]["cv_mean_auroc"]},
                "eigengap": {"primary": rows[0]["eigengap"], LATENT_SENSITIVITY_ARM["name"]: rows[1]["eigengap"]},
                "rejected": {
                    "primary": {s: rows[0][f"{s}_rejected"] for s in ANALYSIS_STATISTICS},
                    LATENT_SENSITIVITY_ARM["name"]: {s: rows[1][f"{s}_rejected"] for s in ANALYSIS_STATISTICS},
                },
                "latent_adjustment": record["latent_adjustment"],
                "cohort_cells": cells,
                "record_cells": record["design"]["cell_sizes"],
                "cohort_cells_equal_record": not cell_findings,
            },
            "expected": a_manifest["expected"],
            "deviations": a_manifest["deviations"],
            "findings": findings,
        }
        with _finalize_output_dir(comparison_final, force=force) as c_tmp:
            table.to_csv(c_tmp / LATENT_SENSITIVITY_TABLE, index=False)
            (c_tmp / LATENT_SENSITIVITY_SUMMARY).write_text(
                render_latent_sensitivity(
                    rows, statuses=statuses, primary=primary, arm=record,
                    reference={"dir": str(primary_dir), "files": reference["files"]}, arm_info=arm_info,
                    descriptives=cohort["descriptives"], findings=findings, n_jobs=n_jobs,
                )
            )
            written = [LATENT_SENSITIVITY_TABLE, LATENT_SENSITIVITY_SUMMARY]
            manifest["outputs"] = {
                name: {"sha256": _sha256_file(c_tmp / name), "bytes": (c_tmp / name).stat().st_size, "participant_level": False}
                for name in written
            }
            _write_manifest(c_tmp / LATENT_SENSITIVITY_MANIFEST, manifest)

    print(f"{log} wrote {analysis_final}/ ({', '.join([*arm['names'], ANALYSIS_MANIFEST])})")
    print(f"{log} wrote {comparison_final}/ ({', '.join([*written, LATENT_SENSITIVITY_MANIFEST])})")
    if a_manifest["deviations"]:
        print(f"{log} {len(a_manifest['deviations'])} count deviation(s) from the predeclared counts (see the arm's findings above)")
    else:
        print(f"{log} counts reproduce the predeclared ones")
    for msg in findings:
        print(f"{log} FINDING: {msg}")
    print(
        f"{log} the primary stays primary; next: `adni-sexdiff axis-diagnostics --analysis-dir {analysis_final} "
        f"--out-dir {diagnostics_final}`"
    )
    return {
        "dir": root,
        "analysis": arm,
        "comparison": {"rows": rows, "statuses": statuses, "manifest": manifest},
        "findings": findings,
    }


# --- export-sensitivity: the NIST SRM 1950 bridge ---------------------------------

#: The columns of ``bridge/nist_bridge.csv``, in order: per exported p180
#: metabolite its kit and NIST column, per run the replicates, the valid ones,
#: the cells with the excluded status, the mean log2 of the valid replicates
#: and its plate-clustered SE, then ``b``, its SE, the inclusion and the log2
#: factor applied (``b`` when bridged, 0 otherwise).
_NIST_BRIDGE_COLUMNS: tuple[str, ...] = (
    "metabolite", "kit", "nist_column",
    *(
        f"{quantity}_{run}"
        for run in (NIST_BRIDGE_RULE["reference_run"], NIST_BRIDGE_RULE["bridged_run"])
        for quantity in ("replicates", "valid", "istd_flags", "mean_log2", "se")
    ),
    "b", "se_b", "bridged", "factor_log2",
)


def _nist_key(name) -> str:
    """A metabolite name with case and punctuation dropped (``NIST_BRIDGE_RULE["name_matching"]``): ``C6 (C4:1-DC)`` and ``C6..C4.1.DC.`` both give ``c6c41dc``."""
    return re.sub(r"[^0-9a-z]", "", str(name).lower())


def read_nist_workbook(content: bytes, *, member: str, rule: dict = NIST_BRIDGE_RULE) -> dict:
    """Read the NIST SRM 1950 replicates of one p180 QC workbook, given as the bytes of its archive member.

    Parameters
    ----------
    content:
        The workbook's bytes (read in place from its archive).
    member:
        The member name, for the messages.
    rule:
        ``NIST_BRIDGE_RULE``: the sheet, its header row, the label column and
        label, the plate column, the column after which the metabolites
        start, the status suffix and the excluded status.

    Returns
    -------
    dict
        ``names`` (key → the sheet's column name, keys by ``_nist_key``),
        ``numbers`` (replicates × keys: the cell as a number, NaN for text),
        ``valid`` (replicates × keys: a positive number whose status, where
        the sheet has a status column, is not the excluded one), ``istd``
        (replicates × keys: the excluded status), ``plates`` (the plate of
        each replicate), ``replicates``, ``plates_n``, ``metabolite_columns``,
        ``status_columns`` (whether the sheet has any), ``text_cells`` (text
        cells among the replicates) and ``statuses`` (status value → cells).

    Notes
    -----
    Only the rows whose label column reads ``rule["label"]`` are replicates;
    every other row of the sheet (class labels, other materials) is ignored.
    Stops naming the member and the column on an absent sheet or column, no
    labelled row, and two metabolite columns with the same key.
    """
    try:
        df = pd.read_excel(io.BytesIO(content), sheet_name=rule["sheet"], header=rule["header_row"])
    except ValueError as e:
        raise ValueError(f"{member}: cannot read the sheet {rule['sheet']!r} ({e})") from None
    absent = [c for c in (rule["label_column"], rule["plate_column"], rule["metabolites_after"]) if c not in df.columns]
    if absent:
        raise ValueError(f"{member}: sheet {rule['sheet']!r} lacks the column(s) " + ", ".join(repr(c) for c in absent))
    rows = df[df[rule["label_column"]].astype(str).str.strip() == rule["label"]].reset_index(drop=True)
    if rows.empty:
        raise ValueError(f"{member}: no row of the sheet {rule['sheet']!r} is labelled {rule['label']!r}")
    start = list(df.columns).index(rule["metabolites_after"]) + 1
    suffix = rule["status_suffix"]
    metabolites = [c for c in df.columns[start:] if not str(c).endswith(suffix)]
    keys = [_nist_key(c) for c in metabolites]
    duplicated = sorted({k for k in keys if keys.count(k) > 1})
    if duplicated:
        raise ValueError(f"{member}: metabolite columns share a key with case and punctuation dropped: {duplicated}")
    raw = rows[metabolites]
    numbers = raw.apply(pd.to_numeric, errors="coerce")
    text = raw.map(lambda v: isinstance(v, str))
    istd = pd.DataFrame(False, index=rows.index, columns=metabolites)
    statuses: dict[str, int] = {}
    has_status = False
    for c in metabolites:
        status_column = f"{c}{suffix}"
        if status_column in rows.columns:
            has_status = True
            status = rows[status_column].astype(str).str.strip()
            istd[c] = (status == rule["excluded_status"]).to_numpy()
            for value, n in status.value_counts().items():
                statuses[value] = statuses.get(value, 0) + int(n)
    valid = (numbers > 0) & ~istd
    numbers.columns = valid.columns = istd.columns = keys
    plates = rows[rule["plate_column"]].astype(str).str.strip().to_numpy()
    return {
        "names": dict(zip(keys, (str(c) for c in metabolites))),
        "numbers": numbers,
        "valid": valid,
        "istd": istd,
        "plates": plates,
        "replicates": int(len(rows)),
        "plates_n": int(len(set(plates))),
        "metabolite_columns": len(metabolites),
        "status_columns": has_status,
        "text_cells": int(text.to_numpy().sum()),
        "statuses": dict(sorted(statuses.items())),
    }


def _nist_run_level(values: np.ndarray, valid: np.ndarray, plates: np.ndarray) -> tuple[float, float, int]:
    """Mean log2 of the valid replicates, its plate-clustered SE (SD of the plate means over √plates) and the valid count."""
    n_valid = int(valid.sum())
    if n_valid == 0:
        return float("nan"), float("nan"), 0
    log2 = np.log2(values[valid])
    plate_means = pd.Series(log2).groupby(plates[valid]).mean()
    se = float(plate_means.std(ddof=1) / np.sqrt(len(plate_means))) if len(plate_means) > 1 else float("nan")
    return float(log2.mean()), se, n_valid


def nist_bridge(workbooks: dict[str, dict[str, dict]], metabolites: Sequence[str], *, rule: dict = NIST_BRIDGE_RULE) -> dict:
    """The NIST SRM 1950 bridge factor of every exported p180 metabolite under ``NIST_BRIDGE_RULE``.

    Parameters
    ----------
    workbooks:
        Run → kit → ``read_nist_workbook`` of the rule's workbooks.
    metabolites:
        The exported p180 metabolites, in block order (their cleaned names).
    rule:
        ``NIST_BRIDGE_RULE``.

    Returns
    -------
    dict
        ``table`` (one row per metabolite, ``_NIST_BRIDGE_COLUMNS``),
        ``factors`` (metabolite → the log2 factor applied: ``b`` when
        bridged, 0 otherwise), ``summary`` (bridged per kit, the unbridged
        and the unmatched metabolites, the quantiles of the applied factor
        over the bridged ones) and ``findings`` (an unmatched metabolite).

    Notes
    -----
    Reads the NIST replicates only: no participant row, label or covariate.
    A metabolite matches the first kit of ``rule["kits"]`` whose sheets hold
    its key in both runs (``_nist_key``); one without a match keeps factor 1
    and is a finding. It is bridged when at least ``rule["inclusion_share"]``
    of its replicates are valid in each run; ``b`` is the mean log2 of its
    valid ``reference_run`` replicates minus that of its valid
    ``bridged_run`` replicates, without plate correction. The SEs are
    recorded beside ``b`` and never used by the rule.
    """
    ref, brd = rule["reference_run"], rule["bridged_run"]
    share = rule["inclusion_share"]
    rows: list[dict] = []
    factors: dict[str, float] = {}
    unmatched: list[str] = []
    for name in metabolites:
        key = _nist_key(name)
        kit = next((k for k in rule["kits"] if all(key in workbooks[r][k]["names"] for r in (ref, brd))), None)
        row: dict = {"metabolite": str(name), "kit": kit, "nist_column": None}
        if kit is None:
            unmatched.append(str(name))
            row.update(bridged=False, factor_log2=0.0)
            rows.append(row)
            factors[str(name)] = 0.0
            continue
        row["nist_column"] = workbooks[ref][kit]["names"][key]
        level: dict[str, tuple[float, float, int]] = {}
        enough = True
        for r in (ref, brd):
            wb = workbooks[r][kit]
            valid = wb["valid"][key].to_numpy()
            level[r] = _nist_run_level(wb["numbers"][key].to_numpy(dtype=float), valid, wb["plates"])
            row.update({
                f"replicates_{r}": wb["replicates"],
                f"valid_{r}": level[r][2],
                f"istd_flags_{r}": int(wb["istd"][key].sum()),
                f"mean_log2_{r}": level[r][0],
                f"se_{r}": level[r][1],
            })
            enough = enough and level[r][2] >= share * wb["replicates"]
        b = level[ref][0] - level[brd][0]
        row.update(b=b, se_b=float(np.hypot(level[ref][1], level[brd][1])), bridged=bool(enough))
        row["factor_log2"] = float(b) if enough else 0.0
        factors[str(name)] = row["factor_log2"]
        rows.append(row)
    table = pd.DataFrame(rows, columns=list(_NIST_BRIDGE_COLUMNS))
    bridged = table[table["bridged"].astype(bool)]
    applied = bridged["factor_log2"].to_numpy(dtype=float)
    summary = {
        "metabolites": int(len(table)),
        "p180_bridged": {
            **{kit: int((bridged["kit"] == kit).sum()) for kit in rule["kits"]},
            "not_bridged": int(len(table) - len(bridged)),
        },
        "not_bridged": table.loc[~table["bridged"].astype(bool), "metabolite"].tolist(),
        "unmatched": unmatched,
        "factor_log2_bridged": (
            {
                "min": float(applied.min()),
                **{f"q{int(q * 100):02d}": float(np.quantile(applied, q)) for q in (0.05, 0.25, 0.5, 0.75, 0.95)},
                "max": float(applied.max()),
                "median_abs": float(np.median(np.abs(applied))),
                "positive": int((applied > 0).sum()),
            }
            if applied.size else None
        ),
    }
    findings = []
    if unmatched:
        findings.append(
            f"{len(unmatched)} exported p180 metabolite(s) match no NIST column in either kit and keep factor 1: "
            + ", ".join(unmatched)
        )
    return {"table": table, "factors": factors, "summary": summary, "findings": findings}


def _read_nist_archives(root: Path, *, rule: dict = NIST_BRIDGE_RULE) -> dict:
    """Hash the QC archives of the data root and read their four workbooks in place.

    Returns ``workbooks`` (run → kit → ``read_nist_workbook``), ``qc`` (the
    archives as ``hash_raw_file`` records them, with ``predeclared`` and
    ``predeclared_sha256`` from ``RAW_INPUT_SHA256``; each workbook's member
    name, bytes and sha256 beside ``NIST_BRIDGE_WORKBOOK_SHA256`` and what
    the reader saw: replicates, plates, metabolite columns, status columns,
    text cells and statuses) and ``findings`` (an archive or workbook hash
    that differs from the predeclared one). Stops before anything is read
    when an archive is absent from the top level of the data root
    (``require_raw_files``, naming every missing one), and before any
    workbook is parsed when a present archive lacks a member (naming the
    archive and the member). Nothing is extracted and nothing is written.
    """
    archives = list(dict.fromkeys(spec["archive"] for spec in rule["workbooks"].values()))
    require_raw_files(root, archives)
    hashes = [hash_raw_file(root / name, root=root) for name in archives]
    findings = check_known_repairs(hashes)
    for rec in hashes:
        rec["predeclared_sha256"] = RAW_INPUT_SHA256.get(rec["name"])
    contents: dict[tuple[str, str], bytes] = {}
    for run, spec in rule["workbooks"].items():
        with zipfile.ZipFile(root / spec["archive"]) as zf:
            present = set(zf.namelist())
            missing = [m for m in spec["members"].values() if m not in present]
            if missing:
                raise FileNotFoundError(
                    f"{spec['archive']} in the data root {root} holds no member " + ", ".join(repr(m) for m in missing)
                    + " (NIST_BRIDGE_RULE); the archive is read in place, never extracted: restore LONI's download"
                )
            for kit, member in spec["members"].items():
                contents[(run, kit)] = zf.read(member)
    workbooks: dict[str, dict[str, dict]] = {}
    records = []
    for (run, kit), content in contents.items():
        spec = rule["workbooks"][run]
        member = spec["members"][kit]
        sha = hashlib.sha256(content).hexdigest()
        predeclared = NIST_BRIDGE_WORKBOOK_SHA256.get(member)
        if sha != predeclared:
            findings.append(
                f"{spec['archive']} member {member}: sha256 {sha} differs from the predeclared hash ({predeclared}); "
                "the predeclared counts hold for the predeclared bytes only"
            )
        wb = read_nist_workbook(content, member=member, rule=rule)
        workbooks.setdefault(run, {})[kit] = wb
        records.append({
            "run": run, "kit": kit, "archive": spec["archive"], "member": member, "bytes": len(content), "sha256": sha,
            "predeclared_sha256": predeclared, "predeclared": sha == predeclared,
            "replicates": wb["replicates"], "plates": wb["plates_n"], "metabolite_columns": wb["metabolite_columns"],
            "status_columns": wb["status_columns"], "text_cells": wb["text_cells"], "statuses": wb["statuses"],
        })
    return {"workbooks": workbooks, "qc": {"archives": hashes, "workbooks": records}, "findings": findings}


# --- export-sensitivity: the step ---------------------------------------------------

#: The columns of ``export_sensitivity.csv``, in order (design D10 of
#: ``adni-nist-bridge``): the analysis and its export variant (empty for the
#: primary), the latent space, then per statistic the observed value, p,
#: rejection, null mean, SD and q95; every value read from a record.
_EXPORT_SENSITIVITY_COLUMNS: tuple[str, ...] = (
    "analysis", "directory", "export_variant",
    "selected_rank", "component_selection", "cv_mean_auroc", "cv_repeats_completed", "eigengap",
    *(f"{s}_{k}" for s in ANALYSIS_STATISTICS for k in ("observed", "p", "rejected", "null_mean", "null_sd", "null_q95")),
)
def _export_comparison_row(name: str, directory: Path, record: dict, variant: str | None) -> dict:
    """One row of ``export_sensitivity.csv`` (``_EXPORT_SENSITIVITY_COLUMNS``), every value read from ``record`` (``_comparison_row``)."""
    row = {**_comparison_row(name, directory, record), "export_variant": variant}
    return {column: row[column] for column in _EXPORT_SENSITIVITY_COLUMNS}


def _export_variant_findings(primary: dict, record: dict, variant: str) -> list[str]:
    """The findings that read a variant's record, under the variant's rule set: a rank that differs from the primary's, a status that differs.

    A status that differs cites the variant's rule 2, and rule 6 too when
    the variant rejects where the primary does not.
    """
    words = _variant_words(variant)
    findings: list[str] = []
    rank_p, rank_v = int(primary["latent"]["selected_lv"]), int(record["latent"]["selected_lv"])
    if rank_v != rank_p:
        findings.append(
            f"the variant {variant}'s CV-selected rank {rank_v} differs from the primary's {rank_p}: reported beside "
            f"angle, not ranked ({words['cite']} 3)"
        )
    for s in ANALYSIS_STATISTICS:
        rp, rv = _rejected(primary["p_values"].get(s)), _rejected(record["p_values"].get(s))
        if rp != rv:
            findings.append(
                f"{s}: the variant {variant}'s status ({_rejection_text(rv)}) differs from the primary's "
                f"({_rejection_text(rp)}) at α = {ANALYSIS_ALPHA}: dependence on {words['source']}, not a result of "
                f"the variant; the primary's status stays the result ("
                + (f"{words['cite']}s 2 and 6)" if rv and not rp else f"{words['cite']} 2)")
            )
    return findings


def _export_variant_status_line(
    statistic: str, status: str, rejected_primary: bool | None, rejected_variant: bool | None, variant: str
) -> str:
    """The status sentence of one statistic in ``export_sensitivity.md``: the wording of ``_arm_status_line`` under the variant's rule set.

    Parameters
    ----------
    statistic:
        ``delta``, ``angle`` or ``shape``.
    status:
        ``same`` or ``differs (<dependence>)``, the variant's dependence label
        (``EXPORT_VARIANT_RULE_SETS``).
    rejected_primary, rejected_variant:
        The two statuses under ``ANALYSIS_REJECTION_RULE``; ``None`` when a
        record holds no p-value.
    variant:
        The variant's name; its rule set gives the citation word and what a
        differing status depends on.

    Returns
    -------
    str
        The status with both rejection texts, then the reading the pair
        implies, the primary's status the result in every case.
    """
    rp, rv = rejected_primary, rejected_variant
    words = _variant_words(variant)
    cite, source = words["cite"], words["source"]
    text = f"`{statistic}`: {status} (primary {_rejection_text(rp)}, {variant} {_rejection_text(rv)}). "
    if rp is None or rv is None:
        text += "A missing p-value is recorded as a finding."
    elif status == _LATENT_SENSITIVITY_STATUS_SAME and not rp:
        text += (
            f"Both are non-rejections; the variant's is no more informative than the primary's ({cite} 6), and "
            "neither is evidence that the sexes' trajectories agree"
            + (" in this respect (reading rule 3: no power statement exists at this design)." if statistic != "delta" else
               " (no power statement exists at this design).")
        )
    elif status == _LATENT_SENSITIVITY_STATUS_SAME:
        text += (
            "Both are rejections: evidence that the trajectories differ in this respect, with Type I controlled at "
            f"the validated designs (reading rules 3 and 4); the variant adds no claim of its own ({cite} 1)."
        )
    elif rv and not rp:
        text += (
            f"The variant rejects where the primary does not: dependence on {source}, not a result of the variant, "
            "read beside the variant's rank and null summary; the primary's non-rejection stays the result "
            f"({cite}s 2 and 6)."
        )
    else:
        text += (
            "The primary rejects where the variant does not: the primary's rejection stays the result (reading rule 1); "
            f"the difference is dependence on {source} ({cite} 2)."
        )
    return text


def render_export_sensitivity(
    rows: list[dict],
    *,
    statuses: dict[str, str],
    variant: str,
    primary: dict,
    record: dict,
    reference: dict,
    variant_info: dict,
    variant_export_manifest: dict,
    findings: list[str],
    n_jobs: int,
    alpha: float = ANALYSIS_ALPHA,
    rank_floor: int = ANALYSIS_RANK_FLOOR,
) -> str:
    """Render ``export_sensitivity.md`` from the two records and the variant's export manifest (design D10 of ``adni-nist-bridge``).

    Parameters
    ----------
    rows:
        The two rows of ``export_sensitivity.csv``, the primary first.
    statuses:
        Per statistic, ``same`` or ``differs (<dependence>)`` with the
        variant's dependence label (``EXPORT_VARIANT_RULE_SETS``).
    variant:
        The variant's name (``EXPORT_VARIANTS``); its rule set gives every
        variant-specific word (change ``adni-nmr-all-columns``).
    primary, record:
        The primary's and the variant's ``result.json``.
    reference, variant_info:
        Per analysis: ``dir`` and ``files`` (``result.json`` with its sha256).
        Only the primary's hash is printed: the primary is never rerun here,
        while the variant's ``result.json`` carries MOTCO's runtime, so its
        hash would change on every rerun (the manifest records it).
    variant_export_manifest:
        The variant's export manifest: the variant, the primary export it
        was read beside, the runs, the bridge and both run offsets.
    findings:
        Every finding of the variant's export, analysis and comparison.
    n_jobs:
        This run's ``n_jobs``.
    alpha, rank_floor:
        ``ANALYSIS_ALPHA`` and ``ANALYSIS_RANK_FLOOR``.

    Returns
    -------
    str
        Markdown, in this order: the header; the statistics table (primary
        row, variant row, status) with both ranks, floors, eigengaps beside
        ``angle``; the status lines (``_export_variant_status_line``) and the
        variant's reading lines (``_statistic_reading_line``, string-equal to
        its ``summary.md``); the latent-space table; the export variant (its
        setting, the runs, the bridge for ``nist_bridge``, the membership,
        block shares and NMR shape counts for ``nmr_all_columns``, the run
        offset per block of both exports: ``_export_variant_lines``); the
        findings; ``READING_RULES`` then the variant's rule set
        (``EXPORT_VARIANT_RULE_SETS``), verbatim. No statistic is computed
        here.
    """
    p_row, v_row = rows[0], rows[1]
    design = record["design"]
    stages = [str(st) for st in design["stage_levels"]]
    spec, words = EXPORT_VARIANTS[variant], _variant_words(variant)
    cite = words["cite"]
    lines = [
        f"# MOTCO export sensitivity: ADNI serum metabolomics, sex × stage — `{variant}`",
        "",
        f"The primary analysis (`{reference['dir']}`, `result.json` sha256 `{reference['files'][ANALYSIS_RESULT]['sha256']}`) "
        f"beside the export variant `{variant}` (`EXPORT_VARIANTS`, change `{spec['change']}`: {spec['setting']}; "
        f"every other export and analysis setting the primary's; `{variant_info['dir']}`, whose `result.json` carries "
        f"MOTCO's runtime, so its hash is in `{EXPORT_SENSITIVITY_MANIFEST}`). MOTCO {record['software']['motco']}; n = "
        f"{design['n_samples']}; {record['measurement']['permutations']} RRPP permutations, seed "
        f"{record['measurement']['seed']}; α = {alpha}, rejected when {ANALYSIS_REJECTION_RULE} (`ANALYSIS_REJECTION_RULE`); "
        f"n_jobs {n_jobs}"
        + ("" if n_jobs == REPORTED_N_JOBS else f" (not a reported run: reported runs use n_jobs = {REPORTED_N_JOBS})")
        + ". The primary row comes first and its status is the result; the variant is read beside it and never "
        f"replaces it ({cite} 1). A status that differs is dependence on {words['source']}, not a result of the "
        f"variant ({cite} 2). Every value below is read from the two `result.json` records and the variant's export "
        "manifest.",
        "",
        "## Statistics",
        "",
        "| statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |",
        "|---|---|---:|---:|:---:|---:|---:|---:|---|",
    ]
    for s in ANALYSIS_STATISTICS:
        for label, row in (("primary", p_row), (variant, v_row)):
            rejected = row[f"{s}_rejected"]
            lines.append(
                f"| {s} | {label} | {_fmt(row[f'{s}_observed'])} | {_fmt(row[f'{s}_p'])} | "
                f"{'n/a' if rejected is None else ('yes' if rejected else 'no')} | {_fmt(row[f'{s}_null_mean'])} | "
                f"{_fmt(row[f'{s}_null_sd'])} | {_fmt(row[f'{s}_null_q95'])} | {statuses[s]} |"
            )
    lines += [
        "",
        f"`angle` (degrees, endpoint stages {stages[0]} and {stages[-1]}) is read beside each analysis' CV-selected "
        f"rank, floor, eigengap and null summary (reading rule 2, {cite} 3): primary rank {p_row['selected_rank']} "
        f"(floor {rank_floor}, pooled relative eigengap {_fmt(p_row['eigengap'])}); {variant} rank "
        f"{v_row['selected_rank']} (floor {rank_floor}, eigengap {_fmt(v_row['eigengap'])})"
        + (
            f"; the ranks differ, which is reported, not ranked ({cite} 3)."
            if p_row["selected_rank"] != v_row["selected_rank"] else "; the ranks are equal."
        ),
        "",
        "Status per statistic:",
        "",
    ]
    lines += [
        "- " + _export_variant_status_line(s, statuses[s], p_row[f"{s}_rejected"], v_row[f"{s}_rejected"], variant)
        for s in ANALYSIS_STATISTICS
    ]
    lines += ["", f"Reading of the variant's statistics, as its `{ANALYSIS_SUMMARY}` prints it:", ""]
    lines += [
        "- " + _statistic_reading_line(s, v_row[f"{s}_rejected"], stages=stages, variant=variant) for s in ANALYSIS_STATISTICS
    ]
    p_perm = (primary.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {})
    v_perm = (record.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {})
    lines += [
        "",
        "## Latent space",
        "",
        f"| quantity | primary | {variant} |",
        "|---|---:|---:|",
        f"| PLS-DA rank (selection) | {p_row['selected_rank']} (`{p_row['component_selection']}`) | {v_row['selected_rank']} (`{v_row['component_selection']}`) |",
        f"| rank floor (`ANALYSIS_RANK_FLOOR`) | {rank_floor} | {rank_floor} |",
        f"| cv_mean_auroc | {_fmt(p_row['cv_mean_auroc'])} | {_fmt(v_row['cv_mean_auroc'])} |",
        f"| CV repeats completed | {p_row['cv_repeats_completed']} | {v_row['cv_repeats_completed']} |",
        f"| pooled relative eigengap | {_fmt(p_row['eigengap'])} | {_fmt(v_row['eigengap'])} |",
        f"| eigengap permutation null q05 / q50 / q95 | {_fmt(p_perm.get('q05'))} / {_fmt(p_perm.get('q50'))} / {_fmt(p_perm.get('q95'))} "
        f"| {_fmt(v_perm.get('q05'))} / {_fmt(v_perm.get('q50'))} / {_fmt(v_perm.get('q95'))} |",
        "",
        f"The two analyses share the cleaned tables, the participants, {words['kept']}, the covariates and their design, "
        f"the cells, the settings, the CV folds, the seed and the permutations; they differ only in {words['changes']} "
        f"({cite} 2).",
        "",
        "## Export variant",
        "",
        *_export_variant_lines(variant_export_manifest),
        "",
        "## Findings",
        "",
    ]
    lines += [f"- {msg}" for msg in findings] or ["None."]
    lines += [
        "",
        "## Reading rules",
        "",
        "Binding for every reader of the result (`READING_RULES`, decided by `adni-analyze` before any run):",
        "",
    ]
    lines += [f"{i}. {rule}" for i, rule in enumerate(READING_RULES, 1)]
    lines += ["", *_export_variant_rules_lines(variant)]
    return "\n".join(lines) + "\n"


def _check_primary_export_chain(export_manifest: dict, input_dir: Path, clean_inputs: dict, cohort_inputs: dict) -> dict:
    """Check that the primary export was made from the clean and cohort outputs now on disk.

    Returns the chain (``<platform>/<file>`` and the two cohort files →
    ``True``). Stops, before anything is written, naming the file, both
    hashes and the command to rerun, when a clean output or cohort file the
    primary export manifest records differs from the one now on disk: the
    variant must share the primary's cleaned tables and participants.
    """
    rerun = "rerun `adni-sexdiff export` (then analyze); nothing was written"
    where = input_dir / EXPORT_MANIFEST
    recorded = export_manifest.get("inputs", {})
    chain: dict[str, bool] = {}
    for platform, entry in (recorded.get("clean") or {}).items():
        for name, rec in (entry.get("outputs") or {}).items():
            now = clean_inputs.get(platform, {}).get("outputs", {}).get(name, {}).get("sha256")
            if rec.get("sha256") != now:
                raise RuntimeError(
                    f"{platform}/{name}: {where} records sha256 {rec.get('sha256')} but the cleaned file hashes to {now} "
                    f"now; the primary export was made from another clean output, {rerun}"
                )
            chain[f"{platform}/{name}"] = True
    cohort = recorded.get("cohort") or {}
    for name, rec, now in (
        (COHORT_TABLE, (cohort.get("outputs") or {}).get(COHORT_TABLE) or {}, cohort_inputs["outputs"][COHORT_TABLE]["sha256"]),
        (COHORT_MANIFEST, cohort.get("manifest") or {}, cohort_inputs["manifest"]["sha256"]),
    ):
        if rec.get("sha256") != now:
            raise RuntimeError(
                f"{name}: {where} records sha256 {rec.get('sha256')} but the cohort file hashes to {now} now; the primary "
                f"export was made from another cohort output, {rerun}"
            )
        chain[name] = True
    return chain


def _dedupe(messages: Iterable[str]) -> list[str]:
    """The messages in order, each once."""
    return list(dict.fromkeys(messages))


def run_export_sensitivity(
    *,
    variant: str,
    data_root: str | Path | None = None,
    cleaned_dir: str | Path | None = None,
    cohort_dir: str | Path | None = None,
    input_dir: str | Path | None = None,
    analysis_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    n_jobs: int = REPORTED_N_JOBS,
    force: bool = False,
) -> dict:
    """Run predeclared export variants beside the primary: the variant export, its analysis and the comparison.

    Parameters
    ----------
    variant:
        A name of ``EXPORT_VARIANTS`` (``nist_bridge``,
        ``per_run_standardized``, ``nmr_all_columns``) or ``all`` (every
        variant, in registry order, each into its own directory; with the
        outputs of a variant present it stops at the existing-variant gate
        unless ``force``). Another name stops the step naming the registered
        variants, before anything is read.
    data_root:
        The data root (``--data-root`` → ``ADNI_DATA_ROOT`` → ``data/``); read
        by ``nist_bridge`` only: the two QC archives of ``NIST_BRIDGE_RULE``
        at its top level.
    cleaned_dir:
        Output root of ``clean`` (default ``constants.CLEANED_DIR``): ``P180.csv``,
        ``p180_runs.csv``, ``NMR.csv``, each against its ``clean_manifest.json``.
    cohort_dir:
        Output directory of ``cohort`` (default ``constants.COHORT_DIR``):
        ``cohort.csv`` and ``cohort_manifest.json``.
    input_dir:
        The primary export (default ``constants.MOTCO_INPUT_DIR``), read as
        the reference, never written.
    analysis_dir:
        The primary analysis (default ``constants.MOTCO_ANALYSIS_DIR``):
        ``result.json`` and ``analysis_manifest.json``, read as the
        reference, never written.
    out_dir:
        The output root (default ``constants.EXPORT_SENSITIVITY_DIR``); each
        variant writes ``<out_dir>/<variant>/`` with the subdirectories of
        ``EXPORT_SENSITIVITY_SUBDIRS`` but ``diagnostics/``.
    n_jobs:
        MOTCO's CV and RRPP workers, as for ``analyze``; reported runs use
        ``constants.REPORTED_N_JOBS`` (1) and another value is a finding.
    force:
        Replace an existing variant (after the new one is complete).

    Returns
    -------
    dict
        ``{"dir": Path, "variants": {name: {"dir", "export", "analysis", "comparison", "findings"}}}``.

    Notes
    -----
    The variants, the bridge rule and every analysis setting are constants
    (``EXPORT_VARIANTS``, ``NIST_BRIDGE_RULE``, the ``ANALYSIS_*``), never
    flags. A variant reruns the export through ``_run_export`` with its one
    hook (``nist_bridge``: the ADNI-GO/2 concentrations multiplied by 2^b
    before the floors; ``per_run_standardized``: each p180 metabolite
    standardized within its run on the rule's scale; ``nmr_all_columns``,
    change ``adni-nmr-all-columns``: every cleaned NMR column kept, each on
    the rule's scale with its own floor, no bridge and no data root) and
    analyses it through
    ``_run_trajectory_analysis`` at the primary's settings
    (``ANALYSIS_LATENT_ADJUSTMENT``, one ``analyze_trajectories`` call). The
    primary export and analysis are read beside it and never written or
    rerun; no diagnostics output is read.

    Checks, in this order, before anything is written: the variant name;
    the gates of ``analyze`` (``check_motco_version``,
    ``check_motco_rank_floor``); an existing variant directory without
    ``force``; the clean outputs with the run table (``_check_clean_outputs``)
    and the cohort chain (``_check_cohort_outputs``); the primary export
    (``_load_analysis_inputs``: each file against its manifest) and its
    chain to the clean and cohort files now on disk
    (``_check_primary_export_chain``); the primary analysis
    (``_check_primary_reference``: its recorded export hashes, no latent
    adjustment, the installed MOTCO, ``ANALYSIS_SEED`` and
    ``ANALYSIS_PERMUTATIONS``); for ``nist_bridge``, the two archives at the
    top of the data root and their four members (``_read_nist_archives``).
    A failure stops the step naming the file or setting, both values and
    the command to rerun, never a participant, and nothing is written.

    Output contract (``<out_dir>/<variant>/``, each subdirectory staged as
    ``<sub>.tmp/`` and the set renamed together when complete):
    ``bridge/nist_bridge.csv`` (``nist_bridge`` only; one row per exported
    p180 metabolite: kit, NIST column, per run the replicates, the valid
    ones, the ISTD flags, the mean log2 and its plate-clustered SE, then
    ``b``, its SE, ``bridged`` and the applied ``factor_log2``; reference
    material only, aggregate); ``motco_input/`` (laid out as the primary
    export; its CSVs participant-level; ``manifest.json`` with step
    ``export-sensitivity``, the variant, the primary export as
    ``reference`` with its output hashes and run offset, for
    ``nist_bridge`` the QC archives and members with their hashes beside the
    predeclared ones, the bridge table's hash, summary and factor per
    metabolite, and the predeclared ``EXPORT_VARIANT_EXPECTED_COUNTS``
    beside the observed counts); ``analysis/`` (the seven files ``analyze``
    writes; the manifest records step ``export-sensitivity``, the variant,
    the primary analysis as ``reference`` with its two hashes and the
    variant's ``analysis`` expected counts; ``summary.md`` with the export
    variant section and both sets of reading rules); ``comparison/``
    (``export_sensitivity.csv``: the primary row then the variant row,
    ``_EXPORT_SENSITIVITY_COLUMNS``, every value read from the records;
    ``export_sensitivity.md``: ``render_export_sensitivity``;
    ``export_sensitivity_manifest.json``). ``diagnostics/`` is
    ``axis-diagnostics --input-dir <variant>/motco_input --analysis-dir
    <variant>/analysis --out-dir <variant>/diagnostics`` and never touched
    here: replacing a variant whose ``diagnostics/`` exists is a finding.

    Findings, recorded and printed, never a stop: every finding of
    ``export`` and ``analyze``; a deviation from the predeclared counts; a
    QC archive or workbook hash that differs from its predeclared value; an
    exported metabolite without a NIST column; a participant whose run
    differs from its ``phase``; an unchanged file whose hash differs from the
    primary's; for ``nmr_all_columns`` the rule's NMR columns differing from
    the primary's; a variant rank that differs from the primary's; a
    statistic whose status differs (the variant's dependence label of
    ``EXPORT_VARIANT_RULE_SETS``: run-handling dependence for the p180
    variants, feature-membership dependence for ``nmr_all_columns``); a
    primary read with ``n_jobs`` not 1; stale diagnostics. Each finding that
    reads a rule cites the variant's rule set. No finding names a participant. No
    variant value changes a constant, selects a metabolite or covariate,
    reruns the primary or defines a new variant.
    """
    step = "export-sensitivity"
    log = f"[{step}]"
    if variant != "all" and variant not in EXPORT_VARIANTS:
        raise ValueError(
            f"unknown export variant {variant!r}; the registered variants (EXPORT_VARIANTS) are "
            + ", ".join(repr(v) for v in EXPORT_VARIANTS) + ", or 'all'; nothing was read or written"
        )
    names = list(EXPORT_VARIANTS) if variant == "all" else [variant]
    motco_version = check_motco_version()
    rank_floor = check_motco_rank_floor()
    cleaned = Path(cleaned_dir) if cleaned_dir is not None else Path(CLEANED_DIR)
    cohort_path = Path(cohort_dir) if cohort_dir is not None else Path(COHORT_DIR)
    primary_input = Path(input_dir) if input_dir is not None else Path(MOTCO_INPUT_DIR)
    primary_dir = Path(analysis_dir) if analysis_dir is not None else Path(MOTCO_ANALYSIS_DIR)
    root = Path(out_dir) if out_dir is not None else Path(EXPORT_SENSITIVITY_DIR)
    written = ("bridge", "export", "analysis", "comparison")
    existing = [str(root / n / EXPORT_SENSITIVITY_SUBDIRS[k]) for n in names for k in written if (root / n / EXPORT_SENSITIVITY_SUBDIRS[k]).exists()]
    if existing and not force:
        raise FileExistsError(
            ", ".join(existing) + (" exist" if len(existing) > 1 else " exists")
            + f"; pass --force to replace the variant (its {EXPORT_SENSITIVITY_SUBDIRS['diagnostics']}/ is never touched)"
        )
    print(
        f"{log} MOTCO {motco_version}; rank floor {rank_floor} equals MOTCO's default; variant(s) {', '.join(names)} "
        "(EXPORT_VARIANTS), each read beside the primary"
    )

    # --- the clean and cohort outputs, the primary export and analysis as references ----------
    clean_inputs = _check_clean_outputs(cleaned, platforms=EXPORT_BLOCKS, runs=True)
    _, cohort_inputs, chain = _check_cohort_outputs(cohort_path, clean_inputs)
    print(
        f"{log} clean: " + ", ".join(f"{p}/{n}" for p, e in clean_inputs.items() for n in e["outputs"])
        + f" equal their manifests; {cohort_path / COHORT_TABLE} equals {COHORT_MANIFEST}, which records them ({len(chain)} file(s))"
    )
    primary_loaded = _load_analysis_inputs(primary_input, step=step)
    primary_chain = _check_primary_export_chain(primary_loaded["export_manifest"], primary_input, clean_inputs, cohort_inputs)
    reference = _check_primary_reference(primary_dir, primary_loaded, motco_version=motco_version, step=step)
    print(
        f"{log} {primary_input}: the primary export ({len(primary_loaded['inputs']) - 1} files equal its manifest, made from "
        f"the {len(primary_chain)} clean and cohort files now on disk); {primary_dir}: the primary (rank "
        f"{reference['rank']}, latent adjustment none, n_jobs {reference['n_jobs']}, MOTCO {reference['motco']}); both "
        "are read, never written"
    )
    shared = {
        "step": step, "log": log, "cleaned": cleaned, "cohort_path": cohort_path, "primary_input": primary_input,
        "primary_dir": primary_dir, "root": root, "n_jobs": n_jobs, "force": force, "data_root": data_root,
        "primary_loaded": primary_loaded, "primary_chain": primary_chain, "reference": reference,
    }
    results = {name: _run_export_variant(name, **shared) for name in names}
    for name in names:
        d = {k: root / name / sub for k, sub in EXPORT_SENSITIVITY_SUBDIRS.items()}
        print(
            f"{log} {name}: the primary stays primary; next: `adni-sexdiff axis-diagnostics --input-dir {d['export']} "
            f"--analysis-dir {d['analysis']} --out-dir {d['diagnostics']}`"
        )
    return {"dir": root, "variants": results}


def _run_export_variant(
    name: str,
    *,
    step: str,
    log: str,
    cleaned: Path,
    cohort_path: Path,
    primary_input: Path,
    primary_dir: Path,
    root: Path,
    n_jobs: int,
    force: bool,
    data_root: str | Path | None,
    primary_loaded: dict,
    primary_chain: dict,
    reference: dict,
) -> dict:
    """One variant of ``run_export_sensitivity``: the bridge (``nist_bridge``), the export, the analysis and the comparison, staged and renamed together."""
    spec = EXPORT_VARIANTS[name]
    vlog = f"{log} {name}:"
    dirs = {key: root / name / sub for key, sub in EXPORT_SENSITIVITY_SUBDIRS.items()}
    p_export = primary_loaded["export_manifest"]
    primary, p_manifest = reference["record"], reference["manifest"]

    # --- the bridge, from the QC archives alone (before any output directory exists) -------------
    bridge, read = None, None
    pre_findings: list[str] = []
    if spec["hook"] == "factors":
        qc_root = resolve_data_root(data_root)
        read = _read_nist_archives(qc_root)
        bridge = nist_bridge(read["workbooks"], p_export["settings"]["block_columns"][spec["block"]])
        pre_findings += [*read["findings"], *bridge["findings"]]
        s = bridge["summary"]
        print(
            f"{vlog} {', '.join(a['name'] for a in read['qc']['archives'])} read in place from {qc_root} ("
            + ", ".join(f"{w['run']} {w['kit']} {w['replicates']} replicates" for w in read["qc"]["workbooks"])
            + "); bridged " + ", ".join(f"{k} {n}" for k, n in s["p180_bridged"].items())
            + f"; unmatched {len(s['unmatched'])}"
        )

    ref = {
        "dir": str(primary_input),
        "manifest": {"name": EXPORT_MANIFEST, "sha256": primary_loaded["inputs"][EXPORT_MANIFEST]["sha256"]},
        "outputs": {n: {"sha256": r["sha256"]} for n, r in p_export.get("outputs", {}).items()},
        "phase_offset": p_export.get("counts", {}).get("phase_offset"),
        "chain": primary_chain,
        "git_revision": p_export.get("git_revision"),
        "created_at": p_export.get("created_at"),
    }
    static_findings: list[str] = []
    if reference["n_jobs"] != REPORTED_N_JOBS:
        static_findings.append(
            f"the primary read ran with n_jobs = {reference['n_jobs']}: its permutation draws are not the reported ones "
            f"(REPORTED_N_JOBS = {REPORTED_N_JOBS}), so the reference is not a reported run"
        )
    if dirs["diagnostics"].exists() and any(dirs[k].exists() for k in ("export", "analysis")):
        static_findings.append(
            f"{dirs['diagnostics']} exists and was computed from the variant this run replaces; rerun `adni-sexdiff "
            f"axis-diagnostics --input-dir {dirs['export']} --analysis-dir {dirs['analysis']} --out-dir "
            f"{dirs['diagnostics']} --force` (the directory is neither read nor written here)"
        )
    variant_block = {"name": name, "constant": "EXPORT_VARIANTS", **spec}

    root_existed, variant_existed = root.exists(), (root / name).exists()
    try:
        with contextlib.ExitStack() as stack:
            b_tmp = stack.enter_context(_finalize_output_dir(dirs["bridge"], force=force)) if bridge else None
            e_tmp = stack.enter_context(_finalize_output_dir(dirs["export"], force=force))
            a_tmp = stack.enter_context(_finalize_output_dir(dirs["analysis"], force=force))
            c_tmp = stack.enter_context(_finalize_output_dir(dirs["comparison"], force=force))

            # --- the bridge table -------------------------------------------------------------------
            extra: dict = {"variant": variant_block, "reference": ref, "findings": [*pre_findings]}
            bridge_table = None
            if bridge is not None:
                bridge["table"].to_csv(b_tmp / EXPORT_SENSITIVITY_BRIDGE_TABLE, index=False)
                bridge_table = {
                    "name": f"{EXPORT_SENSITIVITY_SUBDIRS['bridge']}/{EXPORT_SENSITIVITY_BRIDGE_TABLE}",
                    "sha256": _sha256_file(b_tmp / EXPORT_SENSITIVITY_BRIDGE_TABLE),
                    "bytes": (b_tmp / EXPORT_SENSITIVITY_BRIDGE_TABLE).stat().st_size,
                    "rows": int(len(bridge["table"])),
                    "participant_level": False,
                }
                extra.update(
                    bridge={
                        "constant": "NIST_BRIDGE_RULE",
                        "rule": NIST_BRIDGE_RULE,
                        "table": bridge_table,
                        "summary": bridge["summary"],
                        "factors_log2": bridge["factors"],
                    },
                    inputs={"qc": read["qc"]},
                    counts={
                        "p180_bridged": bridge["summary"]["p180_bridged"],
                        "p180_unmatched": len(bridge["summary"]["unmatched"]),
                    },
                )
                print(f"{vlog} wrote {b_tmp}/{EXPORT_SENSITIVITY_BRIDGE_TABLE} ({bridge_table['rows']} metabolites, no participant value)")

            # --- the variant export ---------------------------------------------------------------------
            export = _run_export(
                cleaned=cleaned, cohort_path=cohort_path, final=dirs["export"], force=force, variant=name,
                factors=bridge["factors"] if bridge is not None else None, reference=ref, manifest_extra=extra,
                staging=e_tmp,
            )

            # --- the variant analysis, at the primary's settings ---------------------------------------
            loaded = _load_analysis_inputs(e_tmp, step=step)

            def variant_extra(record: dict) -> dict:
                return {
                    "variant": variant_block,
                    "reference": {
                        "dir": str(primary_dir),
                        "files": reference["files"],
                        "selected_rank": reference["rank"],
                        "latent_adjustment": None,
                        "n_jobs": reference["n_jobs"],
                        "motco": reference["motco"],
                        "git_revision": p_manifest.get("git_revision"),
                        "created_at": p_manifest.get("created_at"),
                        "export": {"dir": str(primary_input), "manifest": ref["manifest"]},
                    },
                    "findings": [*static_findings, *_export_variant_findings(primary, record, name)],
                }

            analysis = _run_trajectory_analysis(
                input_dir=dirs["export"], final=dirs["analysis"], n_jobs=n_jobs, force=force, step=step,
                latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT, expected=EXPORT_VARIANT_EXPECTED_COUNTS[name]["analysis"],
                manifest_extra=variant_extra, loaded=loaded, staging=a_tmp, log=vlog,
            )
            record, a_manifest, e_manifest = analysis["record"], analysis["manifest"], export["manifest"]

            # --- the comparison ---------------------------------------------------------------------------
            rows = [
                _export_comparison_row("primary", primary_dir, primary, None),
                _export_comparison_row(name, Path(EXPORT_SENSITIVITY_SUBDIRS["analysis"]), record, name),
            ]
            statuses = _comparison_statuses(rows[0], rows[1], differs=_export_variant_status_differs(name))
            table = pd.DataFrame(rows, columns=list(_EXPORT_SENSITIVITY_COLUMNS), dtype=object)
            for s in ANALYSIS_STATISTICS:
                print(
                    f"{vlog} {s}: primary {_fmt(rows[0][f'{s}_observed'])} (p {_fmt(rows[0][f'{s}_p'])}, "
                    f"{_rejection_text(rows[0][f'{s}_rejected'])}); {name} {_fmt(rows[1][f'{s}_observed'])} "
                    f"(p {_fmt(rows[1][f'{s}_p'])}, {_rejection_text(rows[1][f'{s}_rejected'])}); status {statuses[s]}"
                )
            print(
                f"{vlog} rank: primary {rows[0]['selected_rank']}, {name} {rows[1]['selected_rank']}; cv_mean_auroc "
                f"{_fmt(rows[0]['cv_mean_auroc'], '.4f')} / {_fmt(rows[1]['cv_mean_auroc'], '.4f')}"
            )
            numerics, numerics_findings = _numerics(vlog)
            findings = _dedupe([*e_manifest["findings"], *a_manifest["findings"], *numerics_findings])
            variant_files = {
                n: {"sha256": _sha256_file(a_tmp / n), "bytes": (a_tmp / n).stat().st_size}
                for n in (ANALYSIS_RESULT, ANALYSIS_MANIFEST)
            }
            variant_info = {
                "dir": str(dirs["analysis"]),
                "files": variant_files,
                "selected_rank": int(record["latent"]["selected_lv"]),
                "n_jobs": n_jobs,
            }
            versions = _software_versions((*_MANIFEST_PACKAGES, "motco", "scikit-learn"))
            manifest = {
                "step": step,
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "versions": versions,
                "numerics": numerics,
                "git_revision": _git_revision(),
                "inputs": {
                    "primary": {
                        "export": {
                            "dir": str(primary_input),
                            "manifest": ref["manifest"],
                            "files": primary_loaded["inputs"],
                            "chain": primary_chain,
                        },
                        "analysis": {
                            "dir": str(primary_dir),
                            "files": reference["files"],
                            "chain": reference["chain"],
                            "primary_records_export": True,
                            "latent_adjustment": None,
                            "n_jobs": reference["n_jobs"],
                            "selected_rank": reference["rank"],
                            "motco": reference["motco"],
                            "seed_and_permutations_equal_constants": True,
                            "git_revision": p_manifest.get("git_revision"),
                            "created_at": p_manifest.get("created_at"),
                        },
                    },
                    "variant": {
                        "export": {
                            "dir": str(dirs["export"]),
                            "manifest": {"name": EXPORT_MANIFEST, "sha256": loaded["inputs"][EXPORT_MANIFEST]["sha256"]},
                            "files": loaded["inputs"],
                        },
                        "analysis": variant_info,
                        "bridge": bridge_table,
                    },
                    **({"qc": read["qc"]} if read is not None else {}),
                },
                "settings": {
                    "EXPORT_VARIANTS": {name: spec},
                    **({"NIST_BRIDGE_RULE": NIST_BRIDGE_RULE} if bridge is not None else {}),
                    "ANALYSIS_ALPHA": ANALYSIS_ALPHA,
                    "ANALYSIS_REJECTION_RULE": ANALYSIS_REJECTION_RULE,
                    "ANALYSIS_RANK_FLOOR": ANALYSIS_RANK_FLOOR,
                    "n_jobs": n_jobs,
                    "REPORTED_N_JOBS": REPORTED_N_JOBS,
                    "status_rule": (
                        f"{_LATENT_SENSITIVITY_STATUS_SAME!r} when both rejections under ANALYSIS_REJECTION_RULE are "
                        f"equal, else {_export_variant_status_differs(name)!r}; the primary's status is the result either way"
                    ),
                    "columns": list(_EXPORT_SENSITIVITY_COLUMNS),
                },
                "variant": variant_block,
                "reference": a_manifest["reference"],
                "counts": {
                    "rows": len(rows),
                    "statuses": statuses,
                    "ranks": {"primary": rows[0]["selected_rank"], name: rows[1]["selected_rank"]},
                    "cv_mean_auroc": {"primary": rows[0]["cv_mean_auroc"], name: rows[1]["cv_mean_auroc"]},
                    "eigengap": {"primary": rows[0]["eigengap"], name: rows[1]["eigengap"]},
                    "rejected": {
                        "primary": {s: rows[0][f"{s}_rejected"] for s in ANALYSIS_STATISTICS},
                        name: {s: rows[1][f"{s}_rejected"] for s in ANALYSIS_STATISTICS},
                    },
                    "phase_offset": {"primary": ref["phase_offset"], name: e_manifest["counts"]["phase_offset"]},
                    "runs": e_manifest["counts"].get("runs"),
                    **({"p180_bridged": bridge["summary"]["p180_bridged"]} if bridge is not None else {}),
                },
                "expected": {"export": e_manifest["expected"], "analysis": a_manifest["expected"]},
                "deviations": [*e_manifest["deviations"], *a_manifest["deviations"]],
                "findings": findings,
            }
            table.to_csv(c_tmp / EXPORT_SENSITIVITY_TABLE, index=False)
            (c_tmp / EXPORT_SENSITIVITY_SUMMARY).write_text(
                render_export_sensitivity(
                    rows, statuses=statuses, variant=name, primary=primary, record=record,
                    reference={"dir": str(primary_dir), "files": reference["files"]}, variant_info=variant_info,
                    variant_export_manifest=e_manifest, findings=findings, n_jobs=n_jobs,
                )
            )
            comparison_names = [EXPORT_SENSITIVITY_TABLE, EXPORT_SENSITIVITY_SUMMARY]
            manifest["outputs"] = {
                n: {"sha256": _sha256_file(c_tmp / n), "bytes": (c_tmp / n).stat().st_size, "participant_level": False}
                for n in comparison_names
            }
            _write_manifest(c_tmp / EXPORT_SENSITIVITY_MANIFEST, manifest)
    except BaseException:
        # a run that fails before writing leaves no empty variant or output root behind
        for d, existed in ((root / name, variant_existed), (root, root_existed)):
            if not existed and d.is_dir() and not any(d.iterdir()):
                d.rmdir()
        raise

    for key in ("bridge", "export", "analysis", "comparison"):
        if key != "bridge" or bridge is not None:
            print(f"{vlog} wrote {dirs[key]}/")
    n_dev = len(manifest["deviations"])
    print(f"{vlog} " + (f"{n_dev} count deviation(s) from the predeclared counts" if n_dev else "counts reproduce the predeclared ones"))
    for msg in findings:
        print(f"{vlog} FINDING: {msg}")
    return {
        "dir": root / name,
        "export": export,
        "analysis": analysis,
        "comparison": {"rows": rows, "statuses": statuses, "manifest": manifest},
        "findings": findings,
    }


# --- stage-sensitivity ---------------------------------------------------------------

#: The columns of ``stage_sensitivity.csv``, in order (design D7 of
#: ``adni-stage-sensitivity``): the analysis and its stage arm (empty for the
#: primary), the participants, the latent space, then per statistic the
#: observed value, p, rejection, null mean, SD and q95; every value read from
#: a record.
_STAGE_SENSITIVITY_COLUMNS: tuple[str, ...] = (
    "analysis", "directory", "stage_arm", "participants",
    "selected_rank", "component_selection", "cv_mean_auroc", "cv_repeats_completed", "eigengap",
    *(f"{s}_{k}" for s in ANALYSIS_STATISTICS for k in ("observed", "p", "rejected", "null_mean", "null_sd", "null_q95")),
)
#: The status of a statistic whose rejection differs between the primary and the CN / LMCI / AD arm.
_STAGE_SENSITIVITY_STATUS_DIFFERS = "differs (stage-definition dependence)"
#: The export files whose rows the arm copies, in the order the loader lists them.
_STAGE_ARM_FILES: tuple[str, ...] = (*(f"{p}.csv" for p in EXPORT_BLOCKS), EXPORT_METADATA, EXPORT_COVARIATES)


def _stage_comparison_row(name: str, directory: Path, record: dict, stage_arm: str | None) -> dict:
    """One row of ``stage_sensitivity.csv`` (``_STAGE_SENSITIVITY_COLUMNS``), every value read from ``record`` (``_comparison_row``)."""
    row = {**_comparison_row(name, directory, record), "stage_arm": stage_arm, "participants": record["design"]["n_samples"]}
    return {column: row[column] for column in _STAGE_SENSITIVITY_COLUMNS}


def _stage_arm_findings(primary: dict, record: dict) -> list[str]:
    """The findings that read the arm's record: a rank that differs from the primary's, a status that differs."""
    name = STAGE_SENSITIVITY_ARM["name"]
    findings: list[str] = []
    rank_p, rank_a = int(primary["latent"]["selected_lv"]), int(record["latent"]["selected_lv"])
    if rank_a != rank_p:
        findings.append(
            f"the arm {name}'s CV-selected rank {rank_a} differs from the primary's {rank_p}: reported beside angle, "
            "not ranked (stage-arm rule 3)"
        )
    for s in ANALYSIS_STATISTICS:
        rp, ra = _rejected(primary["p_values"].get(s)), _rejected(record["p_values"].get(s))
        if rp != ra:
            findings.append(
                f"{s}: the arm {name}'s status ({_rejection_text(ra)}) differs from the primary's ({_rejection_text(rp)}) "
                f"at α = {ANALYSIS_ALPHA}: dependence on the stage definition and the sample, not a result of the arm; "
                "the primary's status stays the result (stage-arm rules 1 and 2)"
            )
    return findings


def _stage_arm_status_line(statistic: str, status: str, rejected_primary: bool | None, rejected_arm: bool | None) -> str:
    """The status sentence of one statistic in ``stage_sensitivity.md``: the wording of ``_arm_status_line`` under the stage-arm rules.

    Parameters
    ----------
    statistic:
        ``delta``, ``angle`` or ``shape``.
    status:
        ``same`` or ``differs (stage-definition dependence)``.
    rejected_primary, rejected_arm:
        The two statuses under ``ANALYSIS_REJECTION_RULE``; ``None`` when a
        record holds no p-value.

    Returns
    -------
    str
        The status with both rejection texts, then the reading the pair
        implies, the primary's status the result in every case; a differing
        status carries what the arm's stage definition changes for the
        statistic (stage-arm rule 5). String-equal wherever it is printed
        (``stage_sensitivity.md``, and the report once it quotes the arm).
    """
    name = STAGE_SENSITIVITY_ARM["name"]
    rp, ra = rejected_primary, rejected_arm
    text = f"`{statistic}`: {status} (primary {_rejection_text(rp)}, {name} {_rejection_text(ra)}). "
    definition = (
        " `angle` reads only the endpoint stages: the arm's AD cells are the primary's and its CN cells lose the SMC "
        "participants (stage-arm rule 5)."
        if statistic == "angle"
        else " A difference that involves the middle stage is a difference of stage definition: the arm's MCI is LMCI "
        "only (stage-arm rule 5)."
    )
    if rp is None or ra is None:
        text += "A missing p-value is recorded as a finding."
    elif status == _LATENT_SENSITIVITY_STATUS_SAME and not rp:
        text += (
            "Both are non-rejections; the arm's is no more informative than the primary's (stage-arm rule 6), and "
            "neither is evidence that the sexes' trajectories agree"
            + (" in this respect (reading rule 3: no power statement exists at this design)." if statistic != "delta" else
               " (no power statement exists at this design).")
        )
    elif status == _LATENT_SENSITIVITY_STATUS_SAME:
        text += (
            "Both are rejections: evidence that the trajectories differ in this respect, with Type I controlled at "
            "the validated designs (reading rules 3 and 4); the arm adds no claim of its own (stage-arm rule 1)."
        )
    elif ra and not rp:
        text += (
            "The arm rejects where the primary does not: dependence on the stage definition and the sample, not a "
            "result of the arm, read beside the arm's rank and null summary; the primary's non-rejection stays the "
            "result (stage-arm rules 2 and 6)." + definition
        )
    else:
        text += (
            "The primary rejects where the arm does not: the primary's rejection stays the result (reading rule 1); "
            "the difference is dependence on the stage definition and the sample (stage-arm rule 2)." + definition
        )
    return text


def render_stage_sensitivity(
    rows: list[dict],
    *,
    statuses: dict[str, str],
    primary: dict,
    record: dict,
    reference: dict,
    arm_info: dict,
    arm_export_manifest: dict,
    findings: list[str],
    n_jobs: int,
    alpha: float = ANALYSIS_ALPHA,
    rank_floor: int = ANALYSIS_RANK_FLOOR,
) -> str:
    """Render ``stage_sensitivity.md`` from the two records and the arm's export manifest (design D7 of ``adni-stage-sensitivity``).

    Parameters
    ----------
    rows:
        The two rows of ``stage_sensitivity.csv``, the primary first.
    statuses:
        Per statistic, ``same`` or ``differs (stage-definition dependence)``.
    primary, record:
        The primary's and the arm's ``result.json``.
    reference, arm_info:
        Per analysis: ``dir`` and ``files`` (``result.json`` with its sha256).
        Only the primary's hash is printed: the primary is never rerun here,
        while the arm's ``result.json`` carries MOTCO's runtime, so its hash
        would change on every rerun (the manifest records it).
    arm_export_manifest:
        The arm's export manifest, as the loader read it: the arm, the
        primary export it is a row subset of, the participants, cells, runs
        within stage, covariate levels and run offsets of both.
    findings:
        Every finding of the arm's export, analysis and comparison.
    n_jobs:
        This run's ``n_jobs``.
    alpha, rank_floor:
        ``ANALYSIS_ALPHA`` and ``ANALYSIS_RANK_FLOOR``.

    Returns
    -------
    str
        Markdown, in this order: the header; the statistics table (primary
        row, arm row, status) with both ranks, floors and eigengaps beside
        ``angle``; the status lines (``_stage_arm_status_line``) and the arm's
        reading lines (``_statistic_reading_line``, string-equal to its
        ``summary.md``); the latent-space table; the arm (``_stage_arm_lines``:
        the participants kept and dropped by ``dx_bl`` × sex, the cells, the
        runs within stage and the covariate levels of both, the run offset per
        block of both exports); the findings; ``READING_RULES`` then
        ``STAGE_SENSITIVITY_READING_RULES``, verbatim. No statistic is
        computed here.
    """
    p_row, a_row = rows[0], rows[1]
    design = record["design"]
    stages = [str(st) for st in design["stage_levels"]]
    name = STAGE_SENSITIVITY_ARM["name"]
    lines = [
        f"# MOTCO stage sensitivity: ADNI serum metabolomics, sex × stage — CN / LMCI / AD arm `{name}`",
        "",
        f"The primary analysis (`{reference['dir']}`, `result.json` sha256 `{reference['files'][ANALYSIS_RESULT]['sha256']}`) "
        f"beside the CN / LMCI / AD arm `{name}` (`STAGE_SENSITIVITY_ARM`, change `{STAGE_SENSITIVITY_ARM['change']}`: "
        f"{_stage_arm_definition(STAGE_SENSITIVITY_ARM)}; every other export and analysis setting the primary's; "
        f"`{arm_info['dir']}`, whose `result.json` carries MOTCO's runtime, so its hash is in "
        f"`{STAGE_SENSITIVITY_MANIFEST}`). MOTCO {record['software']['motco']}; n = {p_row['participants']} (primary) "
        f"and {a_row['participants']} (arm); {record['measurement']['permutations']} RRPP permutations, seed "
        f"{record['measurement']['seed']}; α = {alpha}, rejected when {ANALYSIS_REJECTION_RULE} (`ANALYSIS_REJECTION_RULE`); "
        f"n_jobs {n_jobs}"
        + ("" if n_jobs == REPORTED_N_JOBS else f" (not a reported run: reported runs use n_jobs = {REPORTED_N_JOBS})")
        + ". The primary row comes first and its status is the result; the arm is read beside it and never replaces "
        "it (stage-arm rule 1). A status that differs is dependence on the stage definition and the sample, not a "
        "result of the arm (stage-arm rule 2). Every value below is read from the two `result.json` records and the "
        "arm's export manifest.",
        "",
        "## Statistics",
        "",
        "| statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |",
        "|---|---|---:|---:|:---:|---:|---:|---:|---|",
    ]
    for s in ANALYSIS_STATISTICS:
        for label, row in (("primary", p_row), (name, a_row)):
            rejected = row[f"{s}_rejected"]
            lines.append(
                f"| {s} | {label} | {_fmt(row[f'{s}_observed'])} | {_fmt(row[f'{s}_p'])} | "
                f"{'n/a' if rejected is None else ('yes' if rejected else 'no')} | {_fmt(row[f'{s}_null_mean'])} | "
                f"{_fmt(row[f'{s}_null_sd'])} | {_fmt(row[f'{s}_null_q95'])} | {statuses[s]} |"
            )
    lines += [
        "",
        f"`angle` (degrees, endpoint stages {stages[0]} and {stages[-1]}) is read beside each analysis' CV-selected "
        f"rank, floor, eigengap and null summary (reading rule 2, stage-arm rule 3): primary rank {p_row['selected_rank']} "
        f"(floor {rank_floor}, pooled relative eigengap {_fmt(p_row['eigengap'])}); {name} rank "
        f"{a_row['selected_rank']} (floor {rank_floor}, eigengap {_fmt(a_row['eigengap'])})"
        + (
            "; the ranks differ, which is reported, not ranked (stage-arm rule 3)."
            if p_row["selected_rank"] != a_row["selected_rank"] else "; the ranks are equal."
        ),
        "",
        "Status per statistic:",
        "",
    ]
    lines += [
        "- " + _stage_arm_status_line(s, statuses[s], p_row[f"{s}_rejected"], a_row[f"{s}_rejected"])
        for s in ANALYSIS_STATISTICS
    ]
    lines += ["", f"Reading of the arm's statistics, as its `{ANALYSIS_SUMMARY}` prints it:", ""]
    lines += [
        "- " + _statistic_reading_line(s, a_row[f"{s}_rejected"], stages=stages, stage_arm=True) for s in ANALYSIS_STATISTICS
    ]
    p_perm = (primary.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {})
    a_perm = (record.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {})
    lines += [
        "",
        "## Latent space",
        "",
        f"| quantity | primary | {name} |",
        "|---|---:|---:|",
        f"| participants | {p_row['participants']} | {a_row['participants']} |",
        f"| PLS-DA rank (selection) | {p_row['selected_rank']} (`{p_row['component_selection']}`) | {a_row['selected_rank']} (`{a_row['component_selection']}`) |",
        f"| rank floor (`ANALYSIS_RANK_FLOOR`) | {rank_floor} | {rank_floor} |",
        f"| cv_mean_auroc | {_fmt(p_row['cv_mean_auroc'])} | {_fmt(a_row['cv_mean_auroc'])} |",
        f"| CV repeats completed | {p_row['cv_repeats_completed']} | {a_row['cv_repeats_completed']} |",
        f"| pooled relative eigengap | {_fmt(p_row['eigengap'])} | {_fmt(a_row['eigengap'])} |",
        f"| eigengap permutation null q05 / q50 / q95 | {_fmt(p_perm.get('q05'))} / {_fmt(p_perm.get('q50'))} / {_fmt(p_perm.get('q95'))} "
        f"| {_fmt(a_perm.get('q05'))} / {_fmt(a_perm.get('q50'))} / {_fmt(a_perm.get('q95'))} |",
        "",
        "The two analyses share the primary export's cells of the kept participants, the covariates and their coding "
        "and every setting; they differ in the participants (SMC and EMCI dropped), and so in their z-scoring, CV "
        "folds, latent basis, rank, covariate reference row and permutation draws (stage-arm rule 2).",
        "",
        "## Arm",
        "",
        *_stage_arm_lines(arm_export_manifest),
        "",
        "## Findings",
        "",
    ]
    lines += [f"- {msg}" for msg in findings] or ["None."]
    lines += [
        "",
        "## Reading rules",
        "",
        "Binding for every reader of the result (`READING_RULES`, decided by `adni-analyze` before any run):",
        "",
    ]
    lines += [f"{i}. {rule}" for i, rule in enumerate(READING_RULES, 1)]
    lines += ["", *_stage_arm_rules_heading(), ""]
    lines += [f"{i}. {rule}" for i, rule in enumerate(STAGE_SENSITIVITY_READING_RULES, 1)]
    return "\n".join(lines) + "\n"


def _phase_by_stage(frame: pd.DataFrame) -> dict[str, dict[str, int]]:
    """Participants per stage (``STAGE_LABELS``) and ``phase`` level, from the loader's merged frame."""
    levels = [str(level) for level in ANALYSIS_COVARIATES["phase"]["levels"]]
    return {
        st: _int_counts(frame.loc[frame[STAGE_COLUMN] == st, "phase"].astype(str), levels) for st in STAGE_LABELS
    }


def _covariate_level_counts(frame: pd.DataFrame) -> dict[str, dict[str, int]]:
    """Participants per level of each categorical covariate, levels as text, as ``analyze`` counts them."""
    return {
        name: _int_counts(frame[name].astype(str), [str(level) for level in ANALYSIS_COVARIATES[name]["levels"]])
        for name in ANALYSIS_CATEGORICAL_COVARIATES
    }


def _stage_arm_export(
    *,
    log: str,
    input_dir: Path,
    staging: Path,
    loaded: dict,
    keep: np.ndarray,
    dx_bl: pd.Series,
    cohort_path: Path,
    cohort: dict,
) -> dict:
    """Write the arm's export into ``staging``: the primary export's rows of the kept participants, copied as bytes (design D2, D5).

    Parameters
    ----------
    log:
        The printed prefix.
    input_dir:
        The primary export, read as bytes, never written.
    staging:
        The empty staging directory of the arm's ``motco_input/``.
    loaded:
        ``_load_analysis_inputs(input_dir)``: the primary export as the
        loader read it (blocks, merged metadata, manifest, file hashes).
    keep:
        Per exported participant, in export order, whether the arm keeps it.
    dx_bl:
        The exported participants' ``dx_bl`` (``cohort.csv``), in export
        order; only counted, never written.
    cohort_path, cohort:
        The cohort directory and ``_check_cohort_chain``'s result, recorded
        as the arm's cohort input (so the chain check reads the arm's
        manifest as it reads the primary's).

    Returns
    -------
    dict
        ``{"manifest": dict, "findings": [...], "deviations": [...]}``.

    Notes
    -----
    For each of ``p180.csv``, ``nmr.csv``, ``metadata.csv`` and
    ``covariates.csv`` the header line and the lines of the kept
    participants, in file order, are written unchanged, so every row is the
    primary's byte for byte whatever pandas' float parser or writer does.
    Stops, before the manifest is written, when a file does not end with a
    newline, holds another number of record lines than ``metadata.csv`` holds
    participants, or has a line whose first field is not the participant's
    ``rid`` (counts only). After writing, each file read as the loader reads
    it is compared with the primary frame restricted to the kept rows; the
    result is ``rows_equal_primary``, predeclared true (a deviation is a
    finding). The manifest carries the export-manifest contract every reader
    relies on (``outputs``, ``settings`` copied from the primary with
    ``block_columns`` and ``covariates``, ``inputs.cohort.manifest``,
    ``counts`` with ``phase_offset``) and the arm's own keys
    (``stage_arm``, ``reference``, the counts of
    ``STAGE_SENSITIVITY_EXPECTED_COUNTS["export"]`` beside the expected ones).
    No floor is recomputed and no value transformed; the run offset, the
    spectrum and the shape counts are measured on the arm's rows as the
    loader parses them.
    """
    arm = STAGE_SENSITIVITY_ARM
    p_export, frame = loaded["export_manifest"], loaded["metadata"]
    rids = [str(r) for r in frame[SAMPLE_COLUMN]]
    rows = np.flatnonzero(keep)
    rerun = "the primary export is not the one its manifest records; rerun `adni-sexdiff export`; nothing was written"

    # --- the header and the kept lines, copied as bytes -------------------------------------
    for name in _STAGE_ARM_FILES:
        content = (input_dir / name).read_bytes()
        if not content.endswith(b"\n"):
            raise RuntimeError(f"{input_dir / name}: the file does not end with a newline; {rerun}")
        lines = content[:-1].split(b"\n")
        header, records = lines[0], lines[1:]
        if len(records) != len(rids):
            raise RuntimeError(
                f"{input_dir / name}: {len(records)} record line(s) but {EXPORT_METADATA} lists {len(rids)} participants; {rerun}"
            )
        n_bad = sum(rec.split(b",", 1)[0].decode() != rid for rec, rid in zip(records, rids))
        if n_bad:
            raise RuntimeError(
                f"{input_dir / name}: {n_bad} line(s) whose first field is not the {SAMPLE_COLUMN} of {EXPORT_METADATA} "
                f"at that position; {rerun}"
            )
        (staging / name).write_bytes(b"".join(line + b"\n" for line in (header, *(records[i] for i in rows))))

    # --- read back as the loader reads it: equal to the primary frame on the kept rows --------
    rows_equal: dict[str, bool] = {}
    for platform in EXPORT_BLOCKS:
        name = f"{platform}.csv"
        rows_equal[name] = bool(pd.read_csv(staging / name, index_col=0).equals(loaded["blocks"][platform].iloc[rows]))
    for name in (EXPORT_METADATA, EXPORT_COVARIATES):
        primary_frame = pd.read_csv(input_dir / name).iloc[rows].reset_index(drop=True)
        rows_equal[name] = bool(pd.read_csv(staging / name).equals(primary_frame))

    # --- counts on the arm's rows ---------------------------------------------------------------
    arm_frame = frame.iloc[rows].reset_index(drop=True)
    phase_levels = tuple(ANALYSIS_COVARIATES["phase"]["levels"])
    phase = arm_frame["phase"].astype(str).to_numpy()
    sexes = frame[GROUP_COLUMN].astype(str).to_numpy()
    dx = dx_bl.astype(str).to_numpy()
    block_columns = p_export["settings"]["block_columns"]
    total = sum(len(block_columns[p]) for p in EXPORT_BLOCKS)
    counts: dict = {
        "participants": int(len(rows)),
        "dropped": {d: int((dx == d).sum()) for d in arm["drop"]},
        "dx_bl": {d: {g: int(((dx == d) & (sexes == g)).sum()) for g in GROUP_VALUES} for d in STAGE_RULE["map"]},
        "sex_stage": _sex_stage(arm_frame),
        "phase_by_stage": _phase_by_stage(arm_frame),
        "covariate_levels": _covariate_level_counts(arm_frame),
        "features": {p: len(block_columns[p]) for p in EXPORT_BLOCKS},
        "joint_features": total,
        "block_shares": {p: len(block_columns[p]) / total for p in EXPORT_BLOCKS},
        "missing_covariate_values": int(arm_frame[list(ANALYSIS_COVARIATES)].isna().sum().sum()),
        "non_finite": {},
        "rows_equal_primary": rows_equal,
        "shape": {},
        "spectrum": {},
        "phase_offset": {},
    }
    for platform in EXPORT_BLOCKS:
        M = loaded["blocks"][platform].iloc[rows].to_numpy(dtype=float)
        counts["non_finite"][platform] = int((~np.isfinite(M)).sum())
        counts["shape"][platform] = _shape_counts(M)
        counts["spectrum"][platform] = _spectrum(M)
        counts["phase_offset"][platform] = _phase_offset(M, phase, phase_levels)[1]
    expected = json.loads(json.dumps(STAGE_SENSITIVITY_EXPECTED_COUNTS["export"]))
    observed = _project(json.loads(json.dumps(counts, default=_json_default)), expected)
    deviations = [msg for key in expected for msg in _count_deviations(expected[key], observed.get(key), key)]
    findings = list(deviations)
    differ = [name for name, same in rows_equal.items() if not same]
    if differ:
        findings.append(
            f"{', '.join(differ)}: read back, the arm's rows differ from the primary export's rows of the kept "
            "participants; the arm copies the primary's lines unchanged, so the parse of a subset differs"
        )
    numerics, numerics_findings = _numerics(log)
    findings += numerics_findings
    print(
        f"{log} arm export: {counts['participants']} of {len(rids)} participants kept ("
        + ", ".join(f"{d} {counts['dropped'][d]} dropped" for d in arm["drop"])
        + "); the header and the kept lines of " + ", ".join(_STAGE_ARM_FILES) + " copied as bytes; read back equal to "
        "the primary's rows: " + ", ".join(f"{n} {rows_equal[n]}" for n in _STAGE_ARM_FILES)
        + f"; p180 phase |d| > 1 for {counts['phase_offset']['p180']['abs_d_gt_1']} metabolite(s), median |d| "
        f"{counts['phase_offset']['p180']['median_abs_d']:.2f}"
    )

    p_outputs = p_export.get("outputs", {})
    feature_tables = {
        EXPORT_FEATURES.format(platform=p): {"sha256": (p_outputs.get(EXPORT_FEATURES.format(platform=p)) or {}).get("sha256")}
        for p in EXPORT_BLOCKS
    }
    manifest = {
        "step": "stage-sensitivity",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versions": _software_versions(),
        "numerics": numerics,
        "git_revision": _git_revision(),
        "stage_arm": {"constant": "STAGE_SENSITIVITY_ARM", **arm},
        "reference": {
            "dir": str(input_dir),
            "manifest": {"name": EXPORT_MANIFEST, "sha256": loaded["inputs"][EXPORT_MANIFEST]["sha256"]},
            "outputs": {name: {"sha256": loaded["inputs"][name]["sha256"]} for name in _STAGE_ARM_FILES},
            "feature_tables": feature_tables,
            "floors_note": "the arm's rows are the primary export's rows: its floors are the primary's, recorded in these feature tables",
            "participants": int(len(frame)),
            "sex_stage": _sex_stage(frame),
            "phase_by_stage": _phase_by_stage(frame),
            "covariate_levels": _covariate_level_counts(frame),
            "phase_offset": p_export.get("counts", {}).get("phase_offset"),
            "git_revision": p_export.get("git_revision"),
            "created_at": p_export.get("created_at"),
        },
        "inputs": {
            "primary_export": {
                "dir": str(input_dir),
                "manifest": {"name": EXPORT_MANIFEST, "sha256": loaded["inputs"][EXPORT_MANIFEST]["sha256"]},
                "files": loaded["inputs"],
            },
            "cohort": {
                "dir": str(cohort_path),
                "manifest": {"name": COHORT_MANIFEST, "sha256": cohort["files"][COHORT_MANIFEST]["sha256"]},
                "outputs": {COHORT_TABLE: cohort["files"][COHORT_TABLE]},
                "manifest_equals_primary_export_record": True,
                "rows_equal_exported_participants": True,
            },
        },
        "settings": {
            **p_export.get("settings", {}),
            "STAGE_SENSITIVITY_ARM": arm,
            "rows": (
                "the primary export's header and the lines of the kept participants, in export order, copied as bytes; "
                "no floor recomputed, no value transformed, no dx_bl written"
            ),
        },
        "counts": counts,
        "expected": expected,
        "deviations": deviations,
        "findings": findings,
    }
    manifest["outputs"] = {
        name: {"sha256": _sha256_file(staging / name), "bytes": (staging / name).stat().st_size, "participant_level": True}
        for name in _STAGE_ARM_FILES
    }
    _write_manifest(staging / EXPORT_MANIFEST, manifest)
    return {"manifest": manifest, "findings": findings, "deviations": deviations}


def run_stage_sensitivity(
    *,
    input_dir: str | Path | None = None,
    analysis_dir: str | Path | None = None,
    cohort_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    n_jobs: int = REPORTED_N_JOBS,
    force: bool = False,
) -> dict:
    """Run the predeclared CN / LMCI / AD arm beside the primary: the arm export, its analysis and the comparison.

    Parameters
    ----------
    input_dir:
        The primary export (default ``constants.MOTCO_INPUT_DIR``), read as
        ``analyze`` reads it (``p180.csv``, ``nmr.csv``, ``metadata.csv``,
        ``covariates.csv``, each against the sha256 ``manifest.json``
        records, and ``manifest.json``) and as bytes for the copy; never
        written. No feature table is read.
    analysis_dir:
        The primary analysis (default ``constants.MOTCO_ANALYSIS_DIR``):
        ``result.json`` and ``analysis_manifest.json``, read as the
        reference, never written.
    cohort_dir:
        Output directory of ``cohort`` (default ``constants.COHORT_DIR``):
        ``cohort.csv`` (the source of ``dx_bl``) and ``cohort_manifest.json``.
    out_dir:
        The output root (default ``constants.STAGE_SENSITIVITY_DIR``), with the
        subdirectories ``STAGE_SENSITIVITY_SUBDIRS``: ``motco_input/``,
        ``analysis/`` and ``comparison/`` are written here; ``diagnostics/``
        never is.
    n_jobs:
        MOTCO's CV and RRPP workers, as for ``analyze``; reported runs use
        ``constants.REPORTED_N_JOBS`` (1) and another value is a finding.
    force:
        Replace the existing arm (after the new one is complete).

    Returns
    -------
    dict
        ``{"dir": Path, "export": {...}, "analysis": {...}, "comparison": {"rows": [...], "statuses": {...}, "manifest": dict}, "findings": [...]}``.

    Notes
    -----
    The arm (``STAGE_SENSITIVITY_ARM``, decided by ``adni-stage-sensitivity``):
    the exported participants whose ``dx_bl`` is CN, LMCI or AD, staged by
    ``STAGE_RULE``'s own map; SMC and EMCI, enrolled only in ADNI-GO/2,
    dropped. Its export is the primary export's rows of those participants,
    copied as bytes (no floor recomputed, nothing re-exported, no cleaned
    table or data-root file read); its analysis is one
    ``analyze_trajectories`` call through ``_run_trajectory_analysis`` at
    the primary's settings (``ANALYSIS_LATENT_ADJUSTMENT``, never assembled
    from MOTCO's primitives). The primary export and analysis are read
    beside it and never written or rerun; nothing under a diagnostics
    directory is read. The arm and its rule are constants, never flags, and
    the arm is not crossed with the latent adjustment or an export variant.

    Checks, in this order, before anything is written: the gates of
    ``analyze`` (``check_motco_version``, ``check_motco_rank_floor``); the
    arm's ``motco_input/``, ``analysis/`` or ``comparison/`` existing
    without ``force``; the primary export (``_load_analysis_inputs``: each
    file against its manifest) and that it is the primary (no
    ``stage_arm`` or ``variant`` recorded); the primary analysis as a
    chained reference (``_check_primary_reference``: its recorded export
    hashes, no latent adjustment, the installed MOTCO, ``ANALYSIS_SEED`` and
    ``ANALYSIS_PERMUTATIONS``); the cohort (``_check_cohort_chain``:
    ``cohort.csv`` against its manifest, the manifest against the export
    manifest's record, the both-flag rows the exported participants in
    order), the both-flag rows' sex and stage equal to ``metadata.csv``, every
    ``dx_bl`` in ``STAGE_RULE``'s map, and every kept row's stage equal to
    the arm's map of its ``dx_bl``. A failure stops the step naming the file
    or setting, both values or counts and the command to rerun, never a
    participant, and nothing is written.

    Output contract (``results/motco_stage_sensitivity/``, each subdirectory
    staged as ``<sub>.tmp/`` and the three renamed together when complete):
    ``motco_input/`` (``_stage_arm_export``: the four CSVs, participant-level,
    and ``manifest.json`` with step ``stage-sensitivity``, ``stage_arm``, the
    primary export as ``reference`` with its feature tables' hashes as the
    source of the floors, the cohort chain, the primary's settings, the
    counts beside ``STAGE_SENSITIVITY_EXPECTED_COUNTS["export"]``);
    ``analysis/`` (the seven files ``analyze`` writes; the manifest records
    step ``stage-sensitivity``, ``stage_arm``, the primary analysis as
    ``reference`` with its two hashes and the arm's ``analysis`` expected
    counts; ``summary.md`` with the "Arm" section and both sets of reading
    rules); ``comparison/`` (``stage_sensitivity.csv``: the primary row then
    the arm row, ``_STAGE_SENSITIVITY_COLUMNS``, every value read from the
    records; ``stage_sensitivity.md``: ``render_stage_sensitivity``;
    ``stage_sensitivity_manifest.json``: the nine inputs with sha256 and the
    chain results, the arm, both analyses, statuses, ranks, cells, levels,
    runs within stage, run offsets, the expected counts and deviations of
    the export and the analysis, output hashes, findings).
    ``diagnostics/`` is ``axis-diagnostics --input-dir
    <root>/motco_input --analysis-dir <root>/analysis --out-dir
    <root>/diagnostics`` and never touched here: replacing the arm while it
    exists is a finding. ``motco_input/*.csv``,
    ``analysis/latent_scores.csv`` and ``analysis/analysis_metadata.csv``
    are participant-level; every other file is aggregate.

    Findings, recorded and printed, never a stop: every finding of
    ``analyze``; a deviation from the predeclared counts; rows read back that
    differ from the primary's; an arm rank that differs from the primary's;
    a statistic whose status differs (stage-definition dependence); a
    primary read with ``n_jobs`` not 1; stale diagnostics. No finding names a
    participant. No arm value changes a constant, ``STAGE_RULE`` or
    ``COHORT_RULE``, selects a participant or setting, reruns the primary or
    defines another arm.
    """
    step = "stage-sensitivity"
    log = f"[{step}]"
    arm = STAGE_SENSITIVITY_ARM
    motco_version = check_motco_version()
    rank_floor = check_motco_rank_floor()
    input_dir = Path(input_dir) if input_dir is not None else Path(MOTCO_INPUT_DIR)
    primary_dir = Path(analysis_dir) if analysis_dir is not None else Path(MOTCO_ANALYSIS_DIR)
    cohort_path = Path(cohort_dir) if cohort_dir is not None else Path(COHORT_DIR)
    root = Path(out_dir) if out_dir is not None else Path(STAGE_SENSITIVITY_DIR)
    dirs = {key: root / sub for key, sub in STAGE_SENSITIVITY_SUBDIRS.items()}
    written = ("export", "analysis", "comparison")
    existing = [str(dirs[k]) for k in written if dirs[k].exists()]
    if existing and not force:
        raise FileExistsError(
            ", ".join(existing) + (" exist" if len(existing) > 1 else " exists")
            + f"; pass --force to replace the arm ({dirs['diagnostics']} is never touched)"
        )
    print(
        f"{log} MOTCO {motco_version}; rank floor {rank_floor} equals MOTCO's default; arm {arm['name']} "
        f"(STAGE_SENSITIVITY_ARM: {arm['source']} in {', '.join(arm['keep'])}, {' and '.join(arm['drop'])} dropped; "
        "the primary's rows, floors and settings), read beside the primary"
    )

    # --- the primary export, the primary analysis as a reference, the cohort ------------------
    loaded = _load_analysis_inputs(input_dir, step=step)
    p_export = loaded["export_manifest"]
    for key in ("stage_arm", "variant"):
        if p_export.get(key):
            raise RuntimeError(
                f"{input_dir / EXPORT_MANIFEST} records {key} {p_export[key].get('name')!r}: the arm is a row subset of "
                "the primary export only; point --input-dir at the primary export (`adni-sexdiff export`); nothing was written"
            )
    reference = _check_primary_reference(primary_dir, loaded, motco_version=motco_version, step=step)
    primary, p_manifest = reference["record"], reference["manifest"]
    print(
        f"{log} {input_dir}: the primary export ({len(loaded['inputs']) - 1} files equal its manifest); {primary_dir}: "
        f"the primary (rank {reference['rank']}, latent adjustment none, n_jobs {reference['n_jobs']}, MOTCO "
        f"{reference['motco']}); both are read, never written"
    )
    frame = loaded["metadata"]
    rids = [str(r) for r in frame[SAMPLE_COLUMN]]
    cohort = _check_cohort_chain(cohort_path, p_export, rids)
    both = cohort["cohort"]
    source = arm["source"]
    absent = [c for c in (GROUP_COLUMN, STAGE_COLUMN, source) if c not in both.columns]
    if absent:
        raise ValueError(f"{COHORT_TABLE}: column(s) absent: {', '.join(repr(c) for c in absent)}; rerun `adni-sexdiff cohort`")
    problems = []
    for column in (GROUP_COLUMN, STAGE_COLUMN):
        n_differ = int((both[column].astype(str).to_numpy() != frame[column].astype(str).to_numpy()).sum())
        if n_differ:
            problems.append(f"{column}: {n_differ} participant(s) whose {COHORT_TABLE} value differs from {EXPORT_METADATA}")
    if problems:
        raise RuntimeError(
            f"{step} stops before writing anything: " + "; ".join(problems)
            + "; the export was not made from this cohort, rerun `adni-sexdiff export` (then analyze)"
        )
    outside = ~both[source].isin(list(STAGE_RULE["map"]))
    if outside.any():
        raise ValueError(
            f"{step} stops before writing anything: {COHORT_TABLE} {source}: {int(outside.sum())} value(s) of the "
            f"exported participants outside STAGE_RULE's map {list(STAGE_RULE['map'])}: "
            + _value_counts_text(both.loc[outside, source]) + "; rerun `adni-sexdiff cohort`"
        )
    keep = both[source].isin(list(arm["keep"])).to_numpy()
    mapped = both.loc[keep, source].map(arm["stage_map"]).to_numpy()
    n_differ = int((frame.loc[keep, STAGE_COLUMN].astype(str).to_numpy() != mapped).sum())
    if n_differ:
        raise RuntimeError(
            f"{step} stops before writing anything: {n_differ} kept participant(s) whose {STAGE_COLUMN} in "
            f"{EXPORT_METADATA} differs from the arm's map of their {source} (STAGE_RULE's map); the cohort broke "
            "STAGE_RULE, rerun `adni-sexdiff cohort` (then export, analyze)"
        )
    print(
        f"{log} {cohort_path / COHORT_TABLE}: equals {COHORT_MANIFEST}, which equals the export's record; its "
        f"{len(both)} rows with every platform flag are the exported participants in order, sex and stage equal; "
        f"{int(keep.sum())} kept by {source} (" + ", ".join(f"{d} {int((both[source] == d).sum())}" for d in arm["keep"])
        + "), " + ", ".join(f"{d} {int((both[source] == d).sum())}" for d in arm["drop"]) + " dropped"
    )

    # --- the findings that do not depend on the arm's record --------------------------------
    static_findings: list[str] = []
    if reference["n_jobs"] != REPORTED_N_JOBS:
        static_findings.append(
            f"the primary read ran with n_jobs = {reference['n_jobs']}: its permutation draws are not the reported ones "
            f"(REPORTED_N_JOBS = {REPORTED_N_JOBS}), so the reference is not a reported run"
        )
    if dirs["diagnostics"].exists() and any(dirs[k].exists() for k in ("export", "analysis")):
        static_findings.append(
            f"{dirs['diagnostics']} exists and was computed from the arm this run replaces; rerun `adni-sexdiff "
            f"axis-diagnostics --input-dir {dirs['export']} --analysis-dir {dirs['analysis']} --out-dir "
            f"{dirs['diagnostics']} --force` (the directory is neither read nor written here)"
        )
    arm_block = {"constant": "STAGE_SENSITIVITY_ARM", **arm}
    p_ref_manifest = {"name": EXPORT_MANIFEST, "sha256": loaded["inputs"][EXPORT_MANIFEST]["sha256"]}

    root_existed = root.exists()
    try:
        with contextlib.ExitStack() as stack:
            e_tmp = stack.enter_context(_finalize_output_dir(dirs["export"], force=force))
            a_tmp = stack.enter_context(_finalize_output_dir(dirs["analysis"], force=force))
            c_tmp = stack.enter_context(_finalize_output_dir(dirs["comparison"], force=force))

            # --- the arm export: the primary's rows of the kept participants ---------------------
            export = _stage_arm_export(
                log=log, input_dir=input_dir, staging=e_tmp, loaded=loaded, keep=keep, dx_bl=both[source],
                cohort_path=cohort_path, cohort=cohort,
            )

            # --- the arm analysis, at the primary's settings ----------------------------------------
            arm_loaded = _load_analysis_inputs(e_tmp, step=step)

            def arm_extra(record: dict) -> dict:
                return {
                    "stage_arm": arm_block,
                    "reference": {
                        "dir": str(primary_dir),
                        "files": reference["files"],
                        "selected_rank": reference["rank"],
                        "latent_adjustment": None,
                        "n_jobs": reference["n_jobs"],
                        "motco": reference["motco"],
                        "git_revision": p_manifest.get("git_revision"),
                        "created_at": p_manifest.get("created_at"),
                        "export": {"dir": str(input_dir), "manifest": p_ref_manifest},
                    },
                    "findings": [*static_findings, *_stage_arm_findings(primary, record)],
                }

            analysis = _run_trajectory_analysis(
                input_dir=dirs["export"], final=dirs["analysis"], n_jobs=n_jobs, force=force, step=step,
                latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT, expected=STAGE_SENSITIVITY_EXPECTED_COUNTS["analysis"],
                manifest_extra=arm_extra, loaded=arm_loaded, staging=a_tmp,
            )
            record, a_manifest = analysis["record"], analysis["manifest"]
            e_manifest = arm_loaded["export_manifest"]

            # --- the comparison ---------------------------------------------------------------------
            rows = [
                _stage_comparison_row("primary", primary_dir, primary, None),
                _stage_comparison_row(arm["name"], Path(STAGE_SENSITIVITY_SUBDIRS["analysis"]), record, arm["name"]),
            ]
            statuses = _comparison_statuses(rows[0], rows[1], differs=_STAGE_SENSITIVITY_STATUS_DIFFERS)
            table = pd.DataFrame(rows, columns=list(_STAGE_SENSITIVITY_COLUMNS), dtype=object)
            for s in ANALYSIS_STATISTICS:
                print(
                    f"{log} {s}: primary {_fmt(rows[0][f'{s}_observed'])} (p {_fmt(rows[0][f'{s}_p'])}, "
                    f"{_rejection_text(rows[0][f'{s}_rejected'])}); {arm['name']} {_fmt(rows[1][f'{s}_observed'])} "
                    f"(p {_fmt(rows[1][f'{s}_p'])}, {_rejection_text(rows[1][f'{s}_rejected'])}); status {statuses[s]}"
                )
            print(
                f"{log} rank: primary {rows[0]['selected_rank']}, {arm['name']} {rows[1]['selected_rank']}; cv_mean_auroc "
                f"{_fmt(rows[0]['cv_mean_auroc'], '.4f')} / {_fmt(rows[1]['cv_mean_auroc'], '.4f')}"
            )
            numerics, numerics_findings = _numerics(log)
            findings = _dedupe([*export["findings"], *a_manifest["findings"], *numerics_findings])
            arm_files = {
                n: {"sha256": _sha256_file(a_tmp / n), "bytes": (a_tmp / n).stat().st_size}
                for n in (ANALYSIS_RESULT, ANALYSIS_MANIFEST)
            }
            arm_info = {
                "dir": str(dirs["analysis"]),
                "files": arm_files,
                "constant": "STAGE_SENSITIVITY_ARM",
                "name": arm["name"],
                "latent_adjustment": None,
                "selected_rank": int(record["latent"]["selected_lv"]),
                "n_jobs": n_jobs,
                "findings": a_manifest["findings"],
            }
            p_counts, a_counts = p_manifest.get("counts", {}), a_manifest["counts"]
            versions = _software_versions((*_MANIFEST_PACKAGES, "motco", "scikit-learn"))
            manifest = {
                "step": step,
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "versions": versions,
                "numerics": numerics,
                "git_revision": _git_revision(),
                "inputs": {
                    "primary": {
                        "export": {"dir": str(input_dir), "manifest": p_ref_manifest, "files": loaded["inputs"]},
                        "analysis": {
                            "dir": str(primary_dir),
                            "files": reference["files"],
                            "chain": reference["chain"],
                            "primary_records_export": True,
                            "latent_adjustment": None,
                            "n_jobs": reference["n_jobs"],
                            "selected_rank": reference["rank"],
                            "motco": reference["motco"],
                            "seed_and_permutations_equal_constants": True,
                            "git_revision": p_manifest.get("git_revision"),
                            "created_at": p_manifest.get("created_at"),
                        },
                    },
                    "cohort": {
                        "dir": str(cohort_path),
                        "files": cohort["files"],
                        "cohort_manifest_equals_export_record": True,
                        "rows_equal_exported_participants": True,
                        "sex_and_stage_equal_metadata": True,
                    },
                },
                "settings": {
                    "STAGE_SENSITIVITY_ARM": arm,
                    "ANALYSIS_ALPHA": ANALYSIS_ALPHA,
                    "ANALYSIS_REJECTION_RULE": ANALYSIS_REJECTION_RULE,
                    "ANALYSIS_RANK_FLOOR": ANALYSIS_RANK_FLOOR,
                    "n_jobs": n_jobs,
                    "REPORTED_N_JOBS": REPORTED_N_JOBS,
                    "status_rule": (
                        f"{_LATENT_SENSITIVITY_STATUS_SAME!r} when both rejections under ANALYSIS_REJECTION_RULE are "
                        f"equal, else {_STAGE_SENSITIVITY_STATUS_DIFFERS!r}; the primary's status is the result either way"
                    ),
                    "columns": list(_STAGE_SENSITIVITY_COLUMNS),
                },
                "stage_arm": arm_block,
                "reference": a_manifest["reference"],
                "arm": {
                    **arm_info,
                    "export": {
                        "dir": str(dirs["export"]),
                        "manifest": {"name": EXPORT_MANIFEST, "sha256": arm_loaded["inputs"][EXPORT_MANIFEST]["sha256"]},
                        "files": arm_loaded["inputs"],
                    },
                },
                "counts": {
                    "rows": len(rows),
                    "statuses": statuses,
                    "participants": {"primary": rows[0]["participants"], arm["name"]: rows[1]["participants"]},
                    "ranks": {"primary": rows[0]["selected_rank"], arm["name"]: rows[1]["selected_rank"]},
                    "cv_mean_auroc": {"primary": rows[0]["cv_mean_auroc"], arm["name"]: rows[1]["cv_mean_auroc"]},
                    "eigengap": {"primary": rows[0]["eigengap"], arm["name"]: rows[1]["eigengap"]},
                    "rejected": {
                        "primary": {s: rows[0][f"{s}_rejected"] for s in ANALYSIS_STATISTICS},
                        arm["name"]: {s: rows[1][f"{s}_rejected"] for s in ANALYSIS_STATISTICS},
                    },
                    "sex_stage": {"primary": primary["design"]["cell_sizes"], arm["name"]: record["design"]["cell_sizes"]},
                    "covariate_levels": {
                        "primary": p_counts.get("covariate_levels"), arm["name"]: a_counts.get("covariate_levels"),
                    },
                    "phase_by_stage": {
                        "primary": e_manifest["reference"]["phase_by_stage"], arm["name"]: e_manifest["counts"]["phase_by_stage"],
                    },
                    "phase_offset": {
                        "primary": e_manifest["reference"]["phase_offset"], arm["name"]: e_manifest["counts"]["phase_offset"],
                    },
                    "dropped": e_manifest["counts"]["dropped"],
                },
                "expected": {"export": e_manifest["expected"], "analysis": a_manifest["expected"]},
                "deviations": [*e_manifest["deviations"], *a_manifest["deviations"]],
                "findings": findings,
            }
            table.to_csv(c_tmp / STAGE_SENSITIVITY_TABLE, index=False)
            (c_tmp / STAGE_SENSITIVITY_SUMMARY).write_text(
                render_stage_sensitivity(
                    rows, statuses=statuses, primary=primary, record=record,
                    reference={"dir": str(primary_dir), "files": reference["files"]}, arm_info=arm_info,
                    arm_export_manifest=e_manifest, findings=findings, n_jobs=n_jobs,
                )
            )
            comparison_names = [STAGE_SENSITIVITY_TABLE, STAGE_SENSITIVITY_SUMMARY]
            manifest["outputs"] = {
                n: {"sha256": _sha256_file(c_tmp / n), "bytes": (c_tmp / n).stat().st_size, "participant_level": False}
                for n in comparison_names
            }
            _write_manifest(c_tmp / STAGE_SENSITIVITY_MANIFEST, manifest)
    except BaseException:
        # a run that fails before writing leaves no empty output root behind
        if not root_existed and root.is_dir() and not any(root.iterdir()):
            root.rmdir()
        raise

    for key in written:
        print(f"{log} wrote {dirs[key]}/")
    n_dev = len(manifest["deviations"])
    print(f"{log} " + (f"{n_dev} count deviation(s) from the predeclared counts" if n_dev else "counts reproduce the predeclared ones"))
    for msg in findings:
        print(f"{log} FINDING: {msg}")
    print(
        f"{log} the primary stays primary; next: `adni-sexdiff axis-diagnostics --input-dir {dirs['export']} "
        f"--analysis-dir {dirs['analysis']} --out-dir {dirs['diagnostics']}`"
    )
    return {
        "dir": root,
        "export": export,
        "analysis": analysis,
        "comparison": {"rows": rows, "statuses": statuses, "manifest": manifest},
        "findings": findings,
    }


# --- rank-sensitivity ----------------------------------------------------------------

#: The columns of ``rank_sensitivity.csv``, in order (design D7 of
#: ``adni-rank-sensitivity``): the analysis, the latent space, then per
#: statistic the observed value, p, rejection, null mean, SD and q95; every
#: value read from a record.
_RANK_SENSITIVITY_COLUMNS: tuple[str, ...] = (
    "analysis", "directory",
    "selected_rank", "component_selection", "cv_mean_auroc", "cv_repeats_completed", "eigengap",
    *(f"{s}_{k}" for s in ANALYSIS_STATISTICS for k in ("observed", "p", "rejected", "null_mean", "null_sd", "null_q95")),
)
#: The status of a statistic whose rejection differs between the primary and a forced rank.
_RANK_SENSITIVITY_STATUS_DIFFERS = "differs (rank dependence)"
#: The analysis files the anchor gate compares, by sha256, with the primary manifest's record.
_ANCHOR_FILES: tuple[str, ...] = (ANALYSIS_LATENT_SCORES, ANALYSIS_PLS_LOADINGS, ANALYSIS_STAGE_MEANS)
#: The record fields the anchor gate compares, in the order ``_check_anchor`` compares them (the full shape, then
#: ``config_spectrum.pooled`` of the n_jobs ≠ 1 shape); ``_anchor_text`` lists them in this order.
_ANCHOR_FIELD_ORDER: tuple[str, ...] = (
    "statistics", "p_values", "null_summary", "config_spectrum", "config_spectrum.pooled", "selected_lv",
)
#: The staging directory of the anchor run under the sweep's output root (removed when the gate passes).
_ANCHOR_STAGING = "anchor.tmp"


def _rank_dir_name(rank: int) -> str:
    """The directory of one rank under ``RANK_SENSITIVITY_DIR`` (``rank_02`` … ``rank_12``)."""
    return RANK_SENSITIVITY_RANK_DIR.format(rank=int(rank))


def _rank_comparison_row(name: str, directory: Path, record: dict) -> dict:
    """One row of ``rank_sensitivity.csv`` (``_RANK_SENSITIVITY_COLUMNS``), every value read from ``record`` (``_comparison_row``)."""
    row = _comparison_row(name, directory, record)
    return {column: row[column] for column in _RANK_SENSITIVITY_COLUMNS}


def _check_anchor(anchor_dir: Path, reference: dict, *, n_jobs: int) -> tuple[dict, list[str]]:
    """Compare the anchor run with the primary (design D3 of ``adni-rank-sensitivity``).

    Parameters
    ----------
    anchor_dir:
        The anchor's staged analysis directory (``anchor.tmp/``), as
        ``_run_trajectory_analysis`` wrote it.
    reference:
        ``_check_primary_reference``: the primary's record, manifest and
        ``n_jobs``.
    n_jobs:
        This run's ``n_jobs``.

    Returns
    -------
    tuple
        ``(anchor, differences)``: the anchor record (``rank``, ``n_jobs``,
        ``primary_n_jobs``, ``fields``: compared field → equal, ``files``:
        per file the anchor's and the primary manifest's sha256 and
        ``equal``, ``not_compared``, ``equal``) and one message per
        difference (empty when the gate passes).

    Notes
    -----
    The record fields are read back from the anchor's ``result.json`` and
    compared with the primary's ``result.json`` exactly (pinned numerics):
    ``statistics``, ``p_values``, ``null_summary``, ``config_spectrum`` and
    ``latent.selected_lv``. When this run's ``n_jobs`` is not
    ``REPORTED_N_JOBS`` or not the primary's, the permutation draws differ
    from the primary's, so only ``statistics``, ``config_spectrum.pooled``
    and ``selected_lv`` are compared and ``p_values``, ``null_summary`` and
    ``config_spectrum.permutation_pooled_eigengap`` are recorded as not
    compared. The files are ``latent_scores.csv``, ``pls_loadings.csv`` and
    ``stage_means.csv``, against the hashes the primary manifest's
    ``outputs`` record, so no primary participant-level file is opened. A
    message names the field and its differing entries with both values, or
    the file with both hashes; never a participant.
    """
    primary, p_manifest = reference["record"], reference["manifest"]
    record = json.loads((anchor_dir / ANALYSIS_RESULT).read_text())
    full = n_jobs == REPORTED_N_JOBS and reference["n_jobs"] == n_jobs
    getters: dict[str, Callable[[dict], object]] = {"statistics": lambda r: r.get("statistics")}
    if full:
        getters.update({
            "p_values": lambda r: r.get("p_values"),
            "null_summary": lambda r: r.get("null_summary"),
            "config_spectrum": lambda r: r.get("config_spectrum"),
        })
        not_compared: list[str] = []
    else:
        getters["config_spectrum.pooled"] = lambda r: (r.get("config_spectrum") or {}).get("pooled")
        not_compared = ["p_values", "null_summary", "config_spectrum.permutation_pooled_eigengap"]
    getters["selected_lv"] = lambda r: r["latent"]["selected_lv"]
    differences: list[str] = []
    fields: dict[str, bool] = {}
    for name, get in getters.items():
        seen, recorded = get(record), get(primary)
        equal = json.dumps(seen, sort_keys=True, default=_json_default) == json.dumps(recorded, sort_keys=True, default=_json_default)
        fields[name] = equal
        if not equal:
            a = _flatten(seen) if isinstance(seen, dict) else {name: seen}
            b = _flatten(recorded) if isinstance(recorded, dict) else {name: recorded}
            keys = [k for k in dict.fromkeys([*a, *b]) if repr(a.get(k)) != repr(b.get(k))]
            differences.append(
                f"`{name}` differs from the primary record's at " + "; ".join(
                    f"{k}: anchor {a.get(k)!r}, primary {b.get(k)!r}" for k in keys[:6]
                ) + (f" (and {len(keys) - 6} more)" if len(keys) > 6 else "")
            )
    files: dict[str, dict] = {}
    recorded_outputs = p_manifest.get("outputs") or {}
    for name in _ANCHOR_FILES:
        sha = _sha256_file(anchor_dir / name)
        rec = (recorded_outputs.get(name) or {}).get("sha256")
        files[name] = {"sha256": sha, "primary_sha256": rec, "equal": sha == rec}
        if sha != rec:
            differences.append(f"{name}: sha256 {sha} (anchor) differs from the hash the primary's {ANALYSIS_MANIFEST} records ({rec})")
    anchor = {
        "rank": int(primary["latent"]["selected_lv"]),
        "n_jobs": n_jobs,
        "primary_n_jobs": reference["n_jobs"],
        "fields": fields,
        "files": files,
        "not_compared": not_compared,
        "equal": not differences,
    }
    return anchor, differences


def _rank_findings(primary: dict, record: dict, rank: int) -> list[str]:
    """The findings that read a rank's record: a statistic whose rejection status differs from the primary's (rank dependence)."""
    findings: list[str] = []
    for s in ANALYSIS_STATISTICS:
        rp, rk = _rejected(primary["p_values"].get(s)), _rejected(record["p_values"].get(s))
        if rp != rk:
            findings.append(
                f"{s}: forced rank {rank}'s status ({_rejection_text(rk)}) differs from the primary's "
                f"({_rejection_text(rp)}) at α = {ANALYSIS_ALPHA}: rank dependence, not a result at that rank; the "
                "primary's status stays the result (sweep rules 1 and 2)"
            )
    return findings


def _ranks_text(ranks: Sequence[int]) -> str:
    """``rank 2``, ``ranks 2 and 9`` or ``ranks 2, 3 and 9``."""
    ranks = [str(k) for k in ranks]
    if len(ranks) == 1:
        return f"rank {ranks[0]}"
    return "ranks " + ", ".join(ranks[:-1]) + f" and {ranks[-1]}"


def _rank_status_line(statistic: str, primary_rejected: bool | None, statuses: dict[int, tuple[str, bool | None]]) -> str:
    """The status sentence of one statistic across the sweep, shared by ``rank_sensitivity.md`` and the report (change ``adni-report-rank-sweep``).

    Parameters
    ----------
    statistic:
        ``delta``, ``angle`` or ``shape``.
    primary_rejected:
        The primary's status under ``ANALYSIS_REJECTION_RULE``; ``None`` when
        its record holds no p-value.
    statuses:
        Per forced rank, in ladder order: its status against the primary
        (``same`` or ``differs (rank dependence)``) and its own rejection.

    Returns
    -------
    str
        One sentence, without its list marker: the ranks whose status
        differs (or ``same at every rank``) with the rejection texts, then
        the reading the pattern implies, the primary's status the result in
        every case and no rule combining the ranks (sweep rules 1, 2, 5 and
        6); for ``angle`` the rank-specific null (sweep rule 4). Shaped like
        ``_stage_arm_status_line`` and string-equal wherever it is printed.
    """
    rp = primary_rejected
    if rp is None or any(rejected is None for _, rejected in statuses.values()):
        return (
            f"`{statistic}`: primary {_rejection_text(rp)}; "
            + ", ".join(f"rank {k} {_rejection_text(rejected)}" for k, (_, rejected) in statuses.items())
            + ". A missing p-value is recorded as a finding."
        )
    differ = [k for k, (status, _) in statuses.items() if status != _LATENT_SENSITIVITY_STATUS_SAME]
    same = [k for k in statuses if k not in differ]
    angle = " Each `angle` is read against its own null, never against another rank's (sweep rule 4)." if statistic == "angle" else ""
    if not differ:
        text = f"`{statistic}`: same at every rank (primary {_rejection_text(rp)}; {_ranks_text(same)} {_rejection_text(rp)}). "
        if not rp:
            return text + (
                "No forced rank rejects where the primary does not; each non-rejection is no more informative than the "
                "primary's (sweep rule 5), and none is evidence that the sexes' trajectories agree"
                + (" in this respect (reading rule 3: no power statement exists at this design)." if statistic != "delta" else
                   " (no power statement exists at this design).")
            )
        return text + (
            "Every forced rank rejects as the primary does; the primary's rejection stays the result, and the sweep adds "
            "no claim of its own, since no rule counts the ranks that reject (sweep rules 1 and 6)." + angle
        )
    text = (
        f"`{statistic}`: {_RANK_SENSITIVITY_STATUS_DIFFERS} at {_ranks_text(differ)}"
        + (f", same at {_ranks_text(same)}" if same else "")
        + f" (primary {_rejection_text(rp)}; {_ranks_text(differ)} {_rejection_text(not rp)}). "
    )
    if not rp:
        return text + (
            "A rejection at a forced rank only is rank dependence, not a result at that rank, read beside that rank's "
            "null summary; the primary's non-rejection stays the result, and no rule counts the ranks that reject "
            "(sweep rules 2, 5 and 6)." + angle
        )
    return text + (
        "The primary's rejection stays the result (reading rule 1); a forced rank that does not reject is rank "
        "dependence, and no rule combines the ranks (sweep rules 2 and 6)." + angle
    )


def _rank_anchor_lines(anchor: dict, *, top: int, primary_rank: int) -> list[str]:
    """The anchor and nesting bullets of ``rank_sensitivity.md``, without their list marker (design D5 of ``adni-report-rank-sweep``).

    ``anchor`` is the anchor gate's record with its predeclared rank
    (``expected_rank``), as the step holds it or as the comparison manifest
    records it; ``top`` the ladder's top rank and ``primary_rank`` the
    primary record's rank. ``render_rank_sensitivity`` and the report print
    them, so they are string-equal across the documents.
    """
    return [
        f"anchor (sweep rule 3): {_anchor_text(anchor)}; its directory was removed. Predeclared anchor rank "
        f"{anchor.get('expected_rank')} (`RANK_SENSITIVITY_EXPECTED_COUNTS`); the primary record's {anchor['rank']}.",
        f"nesting (sweep rule 3): PLS-DA components are nested, so each rank's latent scores are the first columns of "
        f"rank {top}'s, and the ranks at or below the primary's {primary_rank} are the primary's first components "
        "(through the anchor, equal to the primary by the gate). The check compares the scores in memory; no score is "
        "printed or written by it.",
    ]


def _rank_nesting_table(nesting: dict[str, dict], ranks: Sequence[int], *, top: int) -> tuple[list[str], str, list[list[str]]]:
    """The nesting table of ``rank_sensitivity.md`` as (header, alignment, rows of cells), one row per rank in ladder order.

    ``nesting`` is keyed by rank directory (``_rank_dir_name``), as the step
    holds it or as the comparison manifest records it (``counts.nesting``).
    The alignment holds one ``l``, ``r`` or ``c`` per column.
    ``render_rank_sensitivity`` and the report print it (design D5 of
    ``adni-report-rank-sweep``), so the rows are string-equal across the
    documents.
    """
    rows = []
    for k in ranks:
        n = nesting[_rank_dir_name(k)]
        rows.append([
            _rank_dir_name(k), _yes_no(n["first_columns_of_top"]), str(n["anchor_columns"]), _yes_no(n["first_columns_of_anchor"]),
        ])
    header = ["rank", f"first columns of rank {top}'s", "columns compared with the anchor's", "equal to the anchor's"]
    return header, "lcrc", rows


def render_rank_sensitivity(
    rows: list[dict],
    *,
    statuses: dict[int, dict[str, str]],
    primary: dict,
    records: dict[int, dict],
    reference: dict,
    anchor: dict,
    nesting: dict[str, dict],
    findings: list[str],
    n_jobs: int,
    alpha: float = ANALYSIS_ALPHA,
    rank_floor: int = ANALYSIS_RANK_FLOOR,
) -> str:
    """Render ``rank_sensitivity.md`` from the primary's and the ranks' records (design D7 of ``adni-rank-sensitivity``).

    Parameters
    ----------
    rows:
        The rows of ``rank_sensitivity.csv``: the primary, then one per rank
        in ladder order.
    statuses:
        Per rank, per statistic: ``same`` or ``differs (rank dependence)``.
    primary, records:
        The primary's ``result.json`` and each rank's, by rank.
    reference:
        The primary: ``dir`` and ``files`` (``result.json`` with its sha256).
        The ranks' ``result.json`` carry MOTCO's runtime, so their hashes are
        in the manifest only.
    anchor:
        The anchor gate's record (``_check_anchor``) with its predeclared
        rank (``expected_rank``).
    nesting:
        Per rank directory: the nesting check (``first_columns_of_top``,
        ``anchor_columns``, ``first_columns_of_anchor``).
    findings:
        The comparison's findings.
    n_jobs:
        This run's ``n_jobs``.
    alpha, rank_floor:
        ``ANALYSIS_ALPHA`` and ``ANALYSIS_RANK_FLOOR``.

    Returns
    -------
    str
        Markdown, in this order: the header (the primary's directory and
        ``result.json`` sha256, the ladder by constant name, MOTCO and
        ``n_jobs``); the statistics table (per statistic the primary row,
        whose status is the result, then the ranks, each with its status);
        the status sentences (``_rank_status_line``) and each rank's reading
        lines (``_statistic_reading_line``, string-equal to its
        ``summary.md``); the latent spaces (rank, mode, floor, eigengap with
        its permutation quantiles, the ``angle`` null summary); the anchor
        check and the nesting; the findings; ``READING_RULES`` then
        ``RANK_SENSITIVITY_READING_RULES``, verbatim. Numbers carry six
        significant digits; no runtime is printed, so a rerun is
        byte-identical. No statistic is computed here.
    """
    ladder = RANK_SENSITIVITY_LADDER
    ranks = [int(k) for k in records]
    p_row, by_rank = rows[0], dict(zip(ranks, rows[1:]))
    design = primary["design"]
    stages = [str(st) for st in design["stage_levels"]]
    r = int(primary["latent"]["selected_lv"])
    top = max(ranks)
    first = records[ranks[0]]
    lines = [
        f"# MOTCO rank sensitivity: ADNI serum metabolomics, sex × stage — forced-rank ladder `{ladder['name']}`",
        "",
        f"The primary analysis (`{reference['dir']}`, `result.json` sha256 `{reference['files'][ANALYSIS_RESULT]['sha256']}`, "
        f"rank {r} selected by its cross-validation) beside the rank sweep `{ladder['name']}` (`RANK_SENSITIVITY_LADDER`, "
        f"change `{ladder['change']}`: the primary's analysis at each forced rank " + ", ".join(str(k) for k in ranks)
        + f", `{ladder['setting']}` set to the rank and MOTCO's cross-validation skipped; every other export and analysis "
        "setting the primary's; the ranks' `result.json` carry MOTCO's runtime, so their hashes are in "
        f"`{RANK_SENSITIVITY_MANIFEST}`). MOTCO {first['software']['motco']}; n = {design['n_samples']}; "
        f"{first['measurement']['permutations']} RRPP permutations, seed {first['measurement']['seed']} at every rank; "
        f"α = {alpha}, rejected when {ANALYSIS_REJECTION_RULE} (`ANALYSIS_REJECTION_RULE`); n_jobs {n_jobs}"
        + ("" if n_jobs == REPORTED_N_JOBS else f" (not a reported run: reported runs use n_jobs = {REPORTED_N_JOBS})")
        + ". The primary row comes first and its status is the result; the sweep is read beside it and never replaces "
        "it, and no rank is chosen, adopted or ranked (sweep rule 1). A status that differs is rank dependence, not a "
        "result at that rank (sweep rule 2). Every value below is read from the `result.json` records.",
        "",
        "## Statistics",
        "",
        "| statistic | analysis | rank | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |",
        "|---|---|---:|---:|---:|:---:|---:|---:|---:|---|",
    ]
    for s in ANALYSIS_STATISTICS:
        for label, row, status in (
            ("primary", p_row, "the result"),
            *((_rank_dir_name(k), by_rank[k], statuses[k][s]) for k in ranks),
        ):
            rejected = row[f"{s}_rejected"]
            lines.append(
                f"| {s} | {label} | {row['selected_rank']} | {_fmt(row[f'{s}_observed'])} | {_fmt(row[f'{s}_p'])} | "
                f"{'n/a' if rejected is None else ('yes' if rejected else 'no')} | {_fmt(row[f'{s}_null_mean'])} | "
                f"{_fmt(row[f'{s}_null_sd'])} | {_fmt(row[f'{s}_null_q95'])} | {status} |"
            )
    lines += [
        "",
        f"`angle` (degrees, endpoint stages {stages[0]} and {stages[-1]}) is read beside each analysis' rank, floor "
        f"({rank_floor}), eigengap and its own null summary (reading rule 2, sweep rule 4; the latent spaces below), "
        "never against the `angle` of another rank.",
        "",
        "Status per statistic:",
        "",
    ]
    lines += [
        "- " + _rank_status_line(
            s, p_row[f"{s}_rejected"], {k: (statuses[k][s], by_rank[k][f"{s}_rejected"]) for k in ranks}
        )
        for s in ANALYSIS_STATISTICS
    ]
    lines += ["", f"Reading of each rank's statistics, as its `{ANALYSIS_SUMMARY}` prints it:", ""]
    for s in ANALYSIS_STATISTICS:
        groups: dict[bool | None, list[int]] = {}
        for k in ranks:
            groups.setdefault(by_rank[k][f"{s}_rejected"], []).append(k)
        for rejected, ks in groups.items():
            lines.append(
                f"- {_ranks_text(ks)}: " + _statistic_reading_line(s, rejected, stages=stages, rank_sweep=True)
            )
    lines += [
        "",
        "## Latent spaces",
        "",
        "| analysis | rank (selection) | rank floor | cv_mean_auroc | CV repeats completed | pooled relative eigengap | "
        "eigengap null q05 / q50 / q95 | `angle` null mean / sd / q95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, row, rec in (("primary", p_row, primary), *((_rank_dir_name(k), by_rank[k], records[k]) for k in ranks)):
        perm = (rec.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {})
        lines.append(
            f"| {label} | {row['selected_rank']} (`{row['component_selection']}`) | {rank_floor} | "
            f"{_fmt(row['cv_mean_auroc'])} | {row['cv_repeats_completed']} | {_fmt(row['eigengap'])} | "
            f"{_fmt(perm.get('q05'))} / {_fmt(perm.get('q50'))} / {_fmt(perm.get('q95'))} | "
            f"{_fmt(row['angle_null_mean'])} / {_fmt(row['angle_null_sd'])} / {_fmt(row['angle_null_q95'])} |"
        )
    lines += [
        "",
        "The ranks share the primary export, the covariates and their design, the cells, the seed and the permutations; "
        f"at n_jobs = {REPORTED_N_JOBS} every rank permutes the same residual indices (sweep rule 2). They differ only in "
        "the latent rank: MOTCO skips the cross-validation at a forced rank, so `cv_mean_auroc` is not available and no "
        "CV repeat runs. Each rank's `pls_loadings.csv` (MOTCO's rotations) is its own and is not nested.",
        "",
        "## Anchor and nesting",
        "",
        *(f"- {line}" for line in _rank_anchor_lines(anchor, top=top, primary_rank=r)),
    ]
    header, align, nesting_rows = _rank_nesting_table(nesting, ranks, top=top)
    separator = {"l": "---|", "r": "---:|", "c": ":---:|"}
    lines += [
        "",
        "| " + " | ".join(header) + " |",
        "|" + "".join(separator[a] for a in align),
        *("| " + " | ".join(row) + " |" for row in nesting_rows),
    ]
    lines += ["", "## Findings", ""]
    lines += [f"- {msg}" for msg in findings] or ["None."]
    lines += [
        "",
        "## Reading rules",
        "",
        "Binding for every reader of the result (`READING_RULES`, decided by `adni-analyze` before any run):",
        "",
    ]
    lines += [f"{i}. {rule}" for i, rule in enumerate(READING_RULES, 1)]
    lines += ["", *_rank_sweep_rules_heading(), ""]
    lines += [f"{i}. {rule}" for i, rule in enumerate(RANK_SENSITIVITY_READING_RULES, 1)]
    return "\n".join(lines) + "\n"


def run_rank_sensitivity(
    *,
    input_dir: str | Path | None = None,
    analysis_dir: str | Path | None = None,
    out_dir: str | Path | None = None,
    n_jobs: int = REPORTED_N_JOBS,
    force: bool = False,
) -> dict:
    """Run the predeclared rank sweep beside the primary: the anchor gate, one analysis per forced rank and the comparison.

    Parameters
    ----------
    input_dir:
        The primary export (default ``constants.MOTCO_INPUT_DIR``), read as
        ``analyze`` reads it (``p180.csv``, ``nmr.csv``, ``metadata.csv``,
        ``covariates.csv``, each against the sha256 ``manifest.json``
        records, and ``manifest.json``); never written.
    analysis_dir:
        The primary analysis (default ``constants.MOTCO_ANALYSIS_DIR``):
        ``result.json`` and ``analysis_manifest.json``, read as the
        reference, never written. No primary CSV is opened.
    out_dir:
        The output root (default ``constants.RANK_SENSITIVITY_DIR``): one
        directory per rank (``RANK_SENSITIVITY_RANK_DIR``) and
        ``comparison/`` are written here; ``diagnostics/`` never is.
    n_jobs:
        MOTCO's RRPP workers, as for ``analyze``; reported runs use
        ``constants.REPORTED_N_JOBS`` (1) and another value is a finding.
    force:
        Replace the existing sweep (after the new one is complete).

    Returns
    -------
    dict
        ``{"dir": Path, "anchor": dict, "ranks": {rank: {...}}, "comparison": {"rows": [...], "statuses": {...}, "nesting": {...}, "manifest": dict}, "findings": [...]}``.

    Notes
    -----
    The sweep (``RANK_SENSITIVITY_LADDER``, decided by
    ``adni-rank-sensitivity``): the primary's analysis rerun at each forced
    rank of the ladder (2, 3, 4, 6, 9, 12), one ``analyze_trajectories``
    call per rank through ``_run_trajectory_analysis`` with
    ``forced_components`` set to the rank and every other setting the
    primary's (``ANALYSIS_LATENT_ADJUSTMENT``, ``ANALYSIS_SEED`` and
    ``ANALYSIS_PERMUTATIONS`` at every rank), never assembled from MOTCO's
    primitives. The primary is read beside the sweep and never written or
    rerun; nothing under a diagnostics directory, no cohort table and no
    data-root file is read. The ladder is a constant, never a flag, and the
    sweep is not crossed with the latent adjustment, an export variant or
    the CN / LMCI / AD arm.

    Checks, in this order, before anything is written: the gates of
    ``analyze`` (``check_motco_version``, ``check_motco_rank_floor``); a rank
    directory or ``comparison/`` existing without ``force``; the primary
    export (``_load_analysis_inputs``: each file against its manifest) and
    that it is the primary (no ``stage_arm`` or ``variant`` recorded); the
    primary analysis as a chained reference (``_check_primary_reference``:
    its recorded export hashes, no latent adjustment, the installed MOTCO,
    ``ANALYSIS_SEED`` and ``ANALYSIS_PERMUTATIONS``), written by ``analyze``
    with a CV-selected rank, its ``result.json`` hashing to the value its
    manifest records. A failure stops the step naming the file or setting,
    both values and the command to rerun, never a participant, and nothing
    is written.

    The anchor gate (design D3), before any rank runs: one forced run at
    the primary record's rank, staged in ``<out_dir>/anchor.tmp/`` through
    the path every rank takes, and compared with the primary
    (``_check_anchor``: its statistics, p-values, null summaries,
    ``config_spectrum`` and rank against the primary's ``result.json``, its
    ``latent_scores.csv``, ``pls_loadings.csv`` and ``stage_means.csv``
    against the hashes the primary manifest records; at ``n_jobs`` other
    than 1, only what the draws do not change). A difference stops the step
    naming the field or file, both values and the numerics state when it is
    not pinned, with ``anchor.tmp/`` kept for inspection (it is ignored);
    on equality ``anchor.tmp/`` is removed and every rank manifest and the
    comparison manifest record the anchor.

    Output contract (``results/motco_rank_sensitivity/``, each directory
    staged as ``<dir>.tmp/`` and all renamed together when complete): one
    analysis directory per rank (``rank_02`` … ``rank_12``), the seven files
    ``analyze`` writes laid out as the primary's (the manifest records step
    ``rank-sensitivity``, ``settings.forced_components``, ``rank_sweep``: the
    ladder by constant name, the forced rank, the primary's rank and the
    anchor; the primary as ``reference`` with its two hashes; the counts
    beside ``RANK_SENSITIVITY_EXPECTED_COUNTS["analysis"][rank]``;
    ``summary.md`` with the "Rank sweep" section and both sets of reading
    rules); ``comparison/`` (``rank_sensitivity.csv``: the primary row then
    one row per rank, ``_RANK_SENSITIVITY_COLUMNS``, every value read from
    the records; ``rank_sensitivity.md``: ``render_rank_sensitivity``;
    ``rank_sensitivity_manifest.json``: the seven inputs with sha256 and the
    chain results, the ladder, the reference, the anchor, the ranks with
    their two hashes, statuses, the nesting, the counts beside
    ``RANK_SENSITIVITY_EXPECTED_COUNTS["comparison"]``, output hashes,
    findings). Before the renames each rank's latent scores are compared in
    memory with the first columns of the top rank's and of the anchor's (the
    nesting; a false value is a finding, never a stop). ``diagnostics/`` is
    ``axis-diagnostics --analysis-dir <root>/rank_12 --out-dir
    <root>/diagnostics`` and never touched here: replacing the sweep while
    it exists is a finding. Each rank's ``latent_scores.csv`` and
    ``analysis_metadata.csv`` are participant-level (matched by the existing
    ``results/**`` ignore patterns); every other file is aggregate.

    Findings, recorded and printed, never a stop: every finding of
    ``analyze`` that applies to a forced run (count deviations, ``n_jobs``
    not 1, a non-finite statistic or p-value, a moved MOTCO default, a run
    that is not pinned; not the conditions of the cross-validation); a
    primary rank other than the predeclared anchor rank; a statistic whose
    status at a rank differs from the primary's (rank dependence); a
    nesting check that fails; a primary read with ``n_jobs`` not 1; stale
    diagnostics. No finding names a participant. No sweep value changes a
    constant, selects a rank or setting, reruns the primary or defines an
    arm.
    """
    step = "rank-sensitivity"
    log = f"[{step}]"
    ladder = RANK_SENSITIVITY_LADDER
    ranks = tuple(int(k) for k in ladder["ranks"])
    top = max(ranks)
    motco_version = check_motco_version()
    rank_floor = check_motco_rank_floor()
    input_dir = Path(input_dir) if input_dir is not None else Path(MOTCO_INPUT_DIR)
    primary_dir = Path(analysis_dir) if analysis_dir is not None else Path(MOTCO_ANALYSIS_DIR)
    root = Path(out_dir) if out_dir is not None else Path(RANK_SENSITIVITY_DIR)
    rank_dirs = {k: root / _rank_dir_name(k) for k in ranks}
    comparison_final = root / RANK_SENSITIVITY_SUBDIRS["comparison"]
    diagnostics_final = root / RANK_SENSITIVITY_SUBDIRS["diagnostics"]
    anchor_tmp = root / _ANCHOR_STAGING
    existing = [str(d) for d in (*rank_dirs.values(), comparison_final) if d.exists()]
    if existing and not force:
        raise FileExistsError(
            ", ".join(existing) + (" exist" if len(existing) > 1 else " exists")
            + f"; pass --force to replace the sweep ({diagnostics_final} is never touched)"
        )
    print(
        f"{log} MOTCO {motco_version}; rank floor {rank_floor} equals MOTCO's default; ladder {ladder['name']} "
        f"(RANK_SENSITIVITY_LADDER: {ladder['setting']} at ranks " + ", ".join(str(k) for k in ranks)
        + "; the primary's export, seed, permutations and settings), read beside the primary"
    )

    # --- the primary export and the primary analysis as a reference ----------------------
    loaded = _load_analysis_inputs(input_dir, step=step)
    p_export = loaded["export_manifest"]
    for key in ("stage_arm", "variant"):
        if p_export.get(key):
            raise RuntimeError(
                f"{input_dir / EXPORT_MANIFEST} records {key} {p_export[key].get('name')!r}: the sweep runs on the "
                "primary export only (sweep rule 8); point --input-dir at the primary export (`adni-sexdiff export`); "
                "nothing was written"
            )
    reference = _check_primary_reference(primary_dir, loaded, motco_version=motco_version, step=step)
    primary, p_manifest = reference["record"], reference["manifest"]
    selection = primary["latent"]["component_selection"]
    if p_manifest.get("step") != "analyze" or selection != "cv":
        raise RuntimeError(
            f"{primary_dir} is not the primary: {ANALYSIS_MANIFEST} records step {p_manifest.get('step')!r} and "
            f"{ANALYSIS_RESULT} rank selection {selection!r} (the primary is `analyze`'s, its rank selected by "
            "cross-validation); point --analysis-dir at the primary (`adni-sexdiff analyze`); nothing was written"
        )
    recorded_result = ((p_manifest.get("outputs") or {}).get(ANALYSIS_RESULT) or {}).get("sha256")
    now_result = reference["files"][ANALYSIS_RESULT]["sha256"]
    if recorded_result != now_result:
        raise RuntimeError(
            f"{ANALYSIS_RESULT}: sha256 {now_result} differs from the hash the primary's {ANALYSIS_MANIFEST} records "
            f"({recorded_result}); the primary changed after analyze, rerun `adni-sexdiff analyze` (then {step}); "
            "nothing was written"
        )
    r = reference["rank"]
    print(
        f"{log} {input_dir}: the primary export ({len(loaded['inputs']) - 1} files equal its manifest); {primary_dir}: "
        f"the primary (rank {r}, cv, latent adjustment none, n_jobs {reference['n_jobs']}, MOTCO {reference['motco']}; "
        f"{ANALYSIS_RESULT} equals its manifest); both are read, never written"
    )

    # --- the findings that do not depend on a rank's record -----------------------------------
    expected_anchor = RANK_SENSITIVITY_EXPECTED_COUNTS["anchor"]
    anchor_deviations = _count_deviations(expected_anchor, {"rank": r}, "anchor")
    static_findings: list[str] = list(anchor_deviations)
    if reference["n_jobs"] != REPORTED_N_JOBS:
        static_findings.append(
            f"the primary read ran with n_jobs = {reference['n_jobs']}: its permutation draws are not the reported ones "
            f"(REPORTED_N_JOBS = {REPORTED_N_JOBS}), so the reference is not a reported run"
        )
    if diagnostics_final.exists() and any(d.exists() for d in rank_dirs.values()):
        static_findings.append(
            f"{diagnostics_final} exists and was computed from the sweep this run replaces; rerun `adni-sexdiff "
            f"axis-diagnostics --analysis-dir {rank_dirs[top]} --out-dir {diagnostics_final} --force` (the directory "
            "is neither read nor written here)"
        )
    ladder_block = {"constant": "RANK_SENSITIVITY_LADDER", **ladder}
    reference_block = {
        "dir": str(primary_dir),
        "files": reference["files"],
        "selected_rank": r,
        "component_selection": selection,
        "latent_adjustment": None,
        "n_jobs": reference["n_jobs"],
        "motco": reference["motco"],
        "git_revision": p_manifest.get("git_revision"),
        "created_at": p_manifest.get("created_at"),
        "export": {"dir": str(input_dir), "manifest": {"name": EXPORT_MANIFEST, "sha256": loaded["inputs"][EXPORT_MANIFEST]["sha256"]}},
    }

    root_existed = root.exists()
    try:
        # --- the anchor gate: a forced run at the primary's rank, through the path every rank takes ---
        if anchor_tmp.exists():
            shutil.rmtree(anchor_tmp)
        anchor_tmp.mkdir(parents=True)
        _run_trajectory_analysis(
            input_dir=input_dir, final=root / "anchor", n_jobs=n_jobs, force=force, step=step,
            latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT,
            expected={**ANALYSIS_EXPECTED_COUNTS, "component_selection": "forced", "selected_rank": r, "cv_repeats_completed": 0},
            loaded=loaded, staging=anchor_tmp, log=f"{log} anchor (rank {r}):", forced_components=r,
            rank_sweep={"ladder": ladder_block, "forced_rank": r, "primary_rank": r, "anchor": None},
        )
        anchor, differences = _check_anchor(anchor_tmp, reference, n_jobs=n_jobs)
        if differences:
            numerics = _numerics_finding(_numerics_record())
            raise RuntimeError(
                f"{step} stops before any rank runs: the anchor (a forced run at the primary's rank {r}) differs from the "
                "primary: " + "; ".join(differences) + (f"; {numerics}" if numerics else "; the numerics are pinned")
                + f"; the sweep must reproduce the primary at its own rank: rerun `adni-sexdiff analyze` pinned on this "
                f"machine (then {step}); {anchor_tmp} is kept for inspection (it is ignored) and no rank directory or "
                "comparison was written"
            )
        anchor_scores = pd.read_csv(anchor_tmp / ANALYSIS_LATENT_SCORES)  # in memory only, for the nesting check
        shutil.rmtree(anchor_tmp)
        anchor_block = {**anchor, "expected_rank": expected_anchor["rank"]}
        print(
            f"{log} anchor: the forced run at rank {r} equals the primary ("
            + ", ".join(anchor["fields"]) + "; " + ", ".join(anchor["files"]) + ")"
            + (f"; not compared at n_jobs {n_jobs}: " + ", ".join(anchor["not_compared"]) if anchor["not_compared"] else "")
            + f"; {anchor_tmp} removed"
        )

        # --- the ranks and the comparison, staged together -------------------------------------
        with contextlib.ExitStack() as stack:
            tmps = {k: stack.enter_context(_finalize_output_dir(rank_dirs[k], force=force)) for k in ranks}
            c_tmp = stack.enter_context(_finalize_output_dir(comparison_final, force=force))
            results: dict[int, dict] = {}
            for k in ranks:

                def rank_extra(record: dict, k: int = k) -> dict:
                    return {"reference": reference_block, "findings": [*static_findings, *_rank_findings(primary, record, k)]}

                results[k] = _run_trajectory_analysis(
                    input_dir=input_dir, final=rank_dirs[k], n_jobs=n_jobs, force=force, step=step,
                    latent_adjustment=ANALYSIS_LATENT_ADJUSTMENT, expected=RANK_SENSITIVITY_EXPECTED_COUNTS["analysis"][k],
                    manifest_extra=rank_extra, loaded=loaded, staging=tmps[k], log=f"{log} rank {k}:",
                    forced_components=k,
                    rank_sweep={"ladder": ladder_block, "forced_rank": k, "primary_rank": r, "anchor": anchor_block},
                )

            # --- the nesting, in memory: no score is printed or written --------------------------
            scores = {k: pd.read_csv(tmps[k] / ANALYSIS_LATENT_SCORES) for k in ranks}
            nesting: dict[str, dict] = {}
            for k in ranks:
                columns = [f"pls_{j}" for j in range(k)]
                m = min(k, r)
                shared = [f"pls_{j}" for j in range(m)]
                same_rows_top = scores[k][SAMPLE_COLUMN].astype(str).equals(scores[top][SAMPLE_COLUMN].astype(str))
                same_rows_anchor = scores[k][SAMPLE_COLUMN].astype(str).equals(anchor_scores[SAMPLE_COLUMN].astype(str))
                nesting[_rank_dir_name(k)] = {
                    "rank": k,
                    "first_columns_of_top": bool(
                        same_rows_top and np.array_equal(scores[k][columns].to_numpy(), scores[top][columns].to_numpy())
                    ),
                    "anchor_columns": m,
                    "first_columns_of_anchor": bool(
                        same_rows_anchor and np.array_equal(scores[k][shared].to_numpy(), anchor_scores[shared].to_numpy())
                    ),
                }
            del scores, anchor_scores
            nesting_findings = [
                f"{name}: its latent scores are not the first {n['rank']} column(s) of rank {top}'s"
                + ("" if n["first_columns_of_anchor"] else f" nor match the anchor's first {n['anchor_columns']}")
                + " (nesting, sweep rule 3); this contradicts the spike of adni-rank-sensitivity and is reported, never a stop"
                if not n["first_columns_of_top"]
                else f"{name}: its first {n['anchor_columns']} latent score column(s) differ from the anchor's (nesting, "
                "sweep rule 3); this contradicts the spike of adni-rank-sensitivity and is reported, never a stop"
                for name, n in nesting.items()
                if not (n["first_columns_of_top"] and n["first_columns_of_anchor"])
            ]
            print(
                f"{log} nesting: " + ", ".join(
                    f"{name} {'yes' if n['first_columns_of_top'] and n['first_columns_of_anchor'] else 'NO'}"
                    for name, n in nesting.items()
                ) + f" (the first columns of rank {top}'s and of the anchor's)"
            )

            # --- the comparison ---------------------------------------------------------------------
            rows = [_rank_comparison_row("primary", primary_dir, primary)] + [
                _rank_comparison_row(_rank_dir_name(k), Path(_rank_dir_name(k)), results[k]["record"]) for k in ranks
            ]
            statuses = {
                k: _comparison_statuses(rows[0], row, differs=_RANK_SENSITIVITY_STATUS_DIFFERS)
                for k, row in zip(ranks, rows[1:])
            }
            table = pd.DataFrame(rows, columns=list(_RANK_SENSITIVITY_COLUMNS), dtype=object)
            for s in ANALYSIS_STATISTICS:
                print(
                    f"{log} {s}: primary {_fmt(rows[0][f'{s}_observed'])} (p {_fmt(rows[0][f'{s}_p'])}, "
                    f"{_rejection_text(rows[0][f'{s}_rejected'])}); " + "; ".join(
                        f"rank {k} {_fmt(row[f'{s}_observed'])} (p {_fmt(row[f'{s}_p'])}, {statuses[k][s]})"
                        for k, row in zip(ranks, rows[1:])
                    )
                )
            counts = {
                "rows": len(rows),
                "statuses": {_rank_dir_name(k): statuses[k] for k in ranks},
                "ranks": {"primary": r, **{_rank_dir_name(k): int(results[k]["record"]["latent"]["selected_lv"]) for k in ranks}},
                "component_selection": {
                    "primary": selection,
                    **{_rank_dir_name(k): results[k]["record"]["latent"]["component_selection"] for k in ranks},
                },
                "eigengap": {row["analysis"]: row["eigengap"] for row in rows},
                "rejected": {row["analysis"]: {s: row[f"{s}_rejected"] for s in ANALYSIS_STATISTICS} for row in rows},
                "nesting": nesting,
                "nesting_holds": all(n["first_columns_of_top"] and n["first_columns_of_anchor"] for n in nesting.values()),
            }
            expected = {"anchor": expected_anchor, "comparison": RANK_SENSITIVITY_EXPECTED_COUNTS["comparison"]}
            comparison_deviations = _count_deviations(expected["comparison"], {"rows": counts["rows"]}, "comparison")
            rank_deviations = _dedupe(msg for k in ranks for msg in results[k]["manifest"]["deviations"])
            numerics, numerics_findings = _numerics(log)
            findings = _dedupe([
                *static_findings,
                *(msg for k in ranks for msg in results[k]["findings"]),
                *nesting_findings,
                *comparison_deviations,
                *(
                    [
                        f"n_jobs = {n_jobs}: MOTCO seeds one RRPP stream per worker, so the ranks' permutation draws, "
                        f"p-values and null summaries differ from an n_jobs = {REPORTED_N_JOBS} run; the sweep is not "
                        f"reported (REPORTED_N_JOBS = {REPORTED_N_JOBS})"
                    ]
                    if n_jobs != REPORTED_N_JOBS else []
                ),
                *numerics_findings,
            ])
            ranks_block = {
                _rank_dir_name(k): {
                    "dir": str(rank_dirs[k]),
                    "rank": k,
                    "files": {
                        n: {"sha256": _sha256_file(tmps[k] / n), "bytes": (tmps[k] / n).stat().st_size}
                        for n in (ANALYSIS_RESULT, ANALYSIS_MANIFEST)
                    },
                    "deviations": results[k]["manifest"]["deviations"],
                    "findings": results[k]["findings"],
                }
                for k in ranks
            }
            manifest = {
                "step": step,
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "versions": _software_versions((*_MANIFEST_PACKAGES, "motco", "scikit-learn")),
                "numerics": numerics,
                "git_revision": _git_revision(),
                "inputs": {
                    "export": {
                        "dir": str(input_dir),
                        "files": loaded["inputs"],
                        "export_manifest": {"name": EXPORT_MANIFEST, "sha256": loaded["inputs"][EXPORT_MANIFEST]["sha256"]},
                        "export_git_revision": p_export.get("git_revision"),
                        "export_created_at": p_export.get("created_at"),
                    },
                    "primary": {
                        "dir": str(primary_dir),
                        "files": reference["files"],
                        "chain": reference["chain"],
                        "export_manifest_equals": reference["export_manifest_equals"],
                        "primary_records_export": True,
                        "result_equals_primary_manifest": True,
                        "step": p_manifest.get("step"),
                        "component_selection": selection,
                        "latent_adjustment": None,
                        "n_jobs": reference["n_jobs"],
                        "selected_rank": r,
                        "motco": reference["motco"],
                        "seed_and_permutations_equal_constants": True,
                        "git_revision": p_manifest.get("git_revision"),
                        "created_at": p_manifest.get("created_at"),
                    },
                },
                "settings": {
                    "RANK_SENSITIVITY_LADDER": ladder,
                    "ANALYSIS_ALPHA": ANALYSIS_ALPHA,
                    "ANALYSIS_REJECTION_RULE": ANALYSIS_REJECTION_RULE,
                    "ANALYSIS_RANK_FLOOR": ANALYSIS_RANK_FLOOR,
                    "n_jobs": n_jobs,
                    "REPORTED_N_JOBS": REPORTED_N_JOBS,
                    "status_rule": (
                        f"{_LATENT_SENSITIVITY_STATUS_SAME!r} when both rejections under ANALYSIS_REJECTION_RULE are "
                        f"equal, else {_RANK_SENSITIVITY_STATUS_DIFFERS!r}; the primary's status is the result either way"
                    ),
                    "columns": list(_RANK_SENSITIVITY_COLUMNS),
                },
                "reference": reference_block,
                "anchor": anchor_block,
                "ranks": ranks_block,
                "counts": counts,
                "expected": expected,
                "deviations": [*anchor_deviations, *comparison_deviations, *rank_deviations],
                "findings": findings,
            }
            table.to_csv(c_tmp / RANK_SENSITIVITY_TABLE, index=False)
            (c_tmp / RANK_SENSITIVITY_SUMMARY).write_text(
                render_rank_sensitivity(
                    rows, statuses=statuses, primary=primary, records={k: results[k]["record"] for k in ranks},
                    reference={"dir": str(primary_dir), "files": reference["files"]}, anchor=anchor_block,
                    nesting=nesting, findings=findings, n_jobs=n_jobs,
                )
            )
            comparison_names = [RANK_SENSITIVITY_TABLE, RANK_SENSITIVITY_SUMMARY]
            manifest["outputs"] = {
                n: {"sha256": _sha256_file(c_tmp / n), "bytes": (c_tmp / n).stat().st_size, "participant_level": False}
                for n in comparison_names
            }
            _write_manifest(c_tmp / RANK_SENSITIVITY_MANIFEST, manifest)
    except BaseException:
        # a run that fails before writing leaves no empty output root behind (a failed anchor keeps anchor.tmp/)
        if not root_existed and root.is_dir() and not any(root.iterdir()):
            root.rmdir()
        raise

    for k in ranks:
        print(f"{log} wrote {rank_dirs[k]}/ ({', '.join([*results[k]['names'], ANALYSIS_MANIFEST])})")
    print(f"{log} wrote {comparison_final}/ ({', '.join([*comparison_names, RANK_SENSITIVITY_MANIFEST])})")
    n_dev = len(manifest["deviations"])
    print(f"{log} " + (f"{n_dev} count deviation(s) from the predeclared counts" if n_dev else "counts reproduce the predeclared ones"))
    for msg in findings:
        print(f"{log} FINDING: {msg}")
    print(
        f"{log} the primary stays primary; next: `adni-sexdiff axis-diagnostics --analysis-dir {rank_dirs[top]} "
        f"--out-dir {diagnostics_final}`"
    )
    return {
        "dir": root,
        "anchor": anchor_block,
        "ranks": results,
        "comparison": {"rows": rows, "statuses": statuses, "nesting": nesting, "manifest": manifest},
        "findings": findings,
    }


# --- report ----------------------------------------------------------------------

#: The report's title; the date of the file name follows it (design D2 of ``adni-report``).
_REPORT_TITLE = "MOTCO case-study report: ADNI serum metabolomics, sex × stage"
#: ``REPORT_NAME`` as a pattern on the file name, the date captured.
_REPORT_NAME_RE = re.compile(
    "^" + re.escape(REPORT_NAME.split("{date}")[0]) + r"(\d{4}-\d{2}-\d{2})" + re.escape(REPORT_NAME.split("{date}")[1]) + "$"
)
def _variant_role(variant: str, key: str) -> str:
    """The role of ``REPORT_INPUT_FILES`` of a variant's subdirectory, by its key in ``EXPORT_SENSITIVITY_SUBDIRS``."""
    return f"export-sensitivity/{variant}/{EXPORT_SENSITIVITY_SUBDIRS[key]}"


def _variant_labels(variant: str) -> dict[str, str]:
    """The labels of a variant's four manifests, in pipeline order (design D2 of ``adni-report-variants``)."""
    return {
        "export": f"export-sensitivity {variant} (export)",
        "analysis": f"export-sensitivity {variant} (analysis)",
        "comparison": f"export-sensitivity {variant} (comparison)",
        "diagnostics": f"axis-diagnostics ({variant})",
    }


def _stage_arm_role(key: str) -> str:
    """The role of ``REPORT_INPUT_FILES`` of a subdirectory of the CN / LMCI / AD arm, by its key in ``STAGE_SENSITIVITY_SUBDIRS``."""
    return f"stage-sensitivity/{STAGE_SENSITIVITY_SUBDIRS[key]}"


#: The labels of the CN / LMCI / AD arm's four manifests, in pipeline order
#: (design D2 of ``adni-report-stage-arm``); the latent arm keeps its labels.
_STAGE_ARM_LABELS: dict[str, str] = {
    "export": "stage-sensitivity (export)",
    "analysis": "stage-sensitivity (analysis)",
    "comparison": "stage-sensitivity (comparison)",
    "diagnostics": f"axis-diagnostics ({STAGE_SENSITIVITY_ARM['name']})",
}


def _rank_sweep_role(key: int | str) -> str:
    """The role of ``REPORT_INPUT_FILES`` of a directory of the rank sweep: a rank's (``key`` the rank) or a subdirectory's (``key`` of ``RANK_SENSITIVITY_SUBDIRS``)."""
    sub = RANK_SENSITIVITY_SUBDIRS[key] if isinstance(key, str) else _rank_dir_name(key)
    return f"rank-sensitivity/{sub}"


#: The labels of the rank sweep's eight manifests, in pipeline order (design
#: D2 of ``adni-report-rank-sweep``): one per rank of the ladder (keyed by the
#: rank), the comparison and the top rank's diagnostics.
_RANK_SWEEP_LABELS: dict[int | str, str] = {
    **{int(rank): f"rank-sensitivity ({_rank_dir_name(rank)})" for rank in RANK_SENSITIVITY_LADDER["ranks"]},
    "comparison": "rank-sensitivity (comparison)",
    "diagnostics": f"axis-diagnostics ({_rank_dir_name(RANK_SENSITIVITY_LADDER['diagnosed_rank'])})",
}


#: The 33 manifests the report reads, in pipeline order: (label, role in
#: ``REPORT_INPUT_FILES``, file name in that role); the primary's and the
#: arm's nine, then four per variant of ``REPORT_EXPORT_VARIANTS`` in
#: registry order, then the CN / LMCI / AD arm's four, then the rank sweep's eight
#: (one per rank in ladder order, the comparison, the top rank's
#: diagnostics). The label names the step in every provenance table and
#: under "Findings".
_REPORT_MANIFESTS: tuple[tuple[str, str, str], ...] = (
    *((f"clean {platform}", "cleaned", f"{platform}/{CLEAN_MANIFEST}") for platform in PLATFORMS),
    ("cohort", "cohort", COHORT_MANIFEST),
    ("export", "export", EXPORT_MANIFEST),
    ("analyze", "analysis", ANALYSIS_MANIFEST),
    ("axis-diagnostics", "diagnostics", DIAGNOSTICS_MANIFEST),
    ("latent-sensitivity (analysis)", f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['analysis']}", ANALYSIS_MANIFEST),
    ("latent-sensitivity (comparison)", f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['comparison']}", LATENT_SENSITIVITY_MANIFEST),
    ("axis-diagnostics (arm)", f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['diagnostics']}", DIAGNOSTICS_MANIFEST),
    *(
        (_variant_labels(variant)[key], _variant_role(variant, key), name)
        for variant in REPORT_EXPORT_VARIANTS
        for key, name in (("export", EXPORT_MANIFEST), ("analysis", ANALYSIS_MANIFEST),
                          ("comparison", EXPORT_SENSITIVITY_MANIFEST), ("diagnostics", DIAGNOSTICS_MANIFEST))
    ),
    *(
        (_STAGE_ARM_LABELS[key], _stage_arm_role(key), name)
        for key, name in (("export", EXPORT_MANIFEST), ("analysis", ANALYSIS_MANIFEST),
                          ("comparison", STAGE_SENSITIVITY_MANIFEST), ("diagnostics", DIAGNOSTICS_MANIFEST))
    ),
    *(
        (_RANK_SWEEP_LABELS[key], _rank_sweep_role(key), name)
        for key, name in (
            *((int(rank), ANALYSIS_MANIFEST) for rank in RANK_SENSITIVITY_LADDER["ranks"]),
            ("comparison", RANK_SENSITIVITY_MANIFEST), ("diagnostics", DIAGNOSTICS_MANIFEST),
        )
    ),
)
#: The packages whose versions every manifest that records them must agree on.
_REPORT_PINNED_PACKAGES: tuple[str, ...] = ("motco", "scikit-learn", "metabo_adni")
#: The packages of the versions table, in order.
_REPORT_VERSION_PACKAGES: tuple[str, ...] = (
    "python", "adni-sexdiff", "metabo_adni", "motco", "scikit-learn", "numpy", "scipy", "pandas", "statsmodels",
    "pingouin", "openpyxl",
)
_REPORT_NO_NUMERICS = "no block (written before `adni-portable-numerics`)"


def _report_date(path: Path) -> str:
    """The date in a report's file name (``REPORT_NAME``); stops naming the file and the pattern otherwise."""
    m = _REPORT_NAME_RE.match(Path(path).name)
    if m is None:
        raise ValueError(f"{path}: the report's name must match {REPORT_NAME.format(date='<YYYY-MM-DD>')} (the date is read from it)")
    return m.group(1)


def _report_dirs(
    cleaned_dir, cohort_dir, input_dir, analysis_dir, diagnostics_dir, sensitivity_dir, export_sensitivity_dir,
    stage_sensitivity_dir, rank_sensitivity_dir,
) -> dict[str, Path]:
    """The directory of every role of ``REPORT_INPUT_FILES`` from the nine directory flags (design D7)."""
    sensitivity = Path(sensitivity_dir) if sensitivity_dir is not None else Path(LATENT_SENSITIVITY_DIR)
    variants = Path(export_sensitivity_dir) if export_sensitivity_dir is not None else Path(EXPORT_SENSITIVITY_DIR)
    stage = Path(stage_sensitivity_dir) if stage_sensitivity_dir is not None else Path(STAGE_SENSITIVITY_DIR)
    sweep = Path(rank_sensitivity_dir) if rank_sensitivity_dir is not None else Path(RANK_SENSITIVITY_DIR)
    dirs = {
        "cleaned": Path(cleaned_dir) if cleaned_dir is not None else Path(CLEANED_DIR),
        "cohort": Path(cohort_dir) if cohort_dir is not None else Path(COHORT_DIR),
        "export": Path(input_dir) if input_dir is not None else Path(MOTCO_INPUT_DIR),
        "analysis": Path(analysis_dir) if analysis_dir is not None else Path(MOTCO_ANALYSIS_DIR),
        "diagnostics": Path(diagnostics_dir) if diagnostics_dir is not None else Path(DIAGNOSTICS_DIR),
    }
    for sub in LATENT_SENSITIVITY_SUBDIRS.values():
        dirs[f"sensitivity/{sub}"] = sensitivity / sub
    for variant in REPORT_EXPORT_VARIANTS:
        for key, sub in EXPORT_SENSITIVITY_SUBDIRS.items():
            dirs[_variant_role(variant, key)] = variants / variant / sub
    for key, sub in STAGE_SENSITIVITY_SUBDIRS.items():
        dirs[_stage_arm_role(key)] = stage / sub
    for rank in RANK_SENSITIVITY_LADDER["ranks"]:
        dirs[_rank_sweep_role(rank)] = sweep / _rank_dir_name(rank)
    for key, sub in RANK_SENSITIVITY_SUBDIRS.items():
        dirs[_rank_sweep_role(key)] = sweep / sub
    return dirs


def _report_rerun(role: str, name: str, dirs: dict[str, Path]) -> str:
    """The command that writes a file of ``role`` (the hint of every gate message)."""
    if role == "cleaned":
        return f"`adni-sexdiff clean --platform {name.split('/')[0]}`"
    if role == "cohort":
        return "`adni-sexdiff cohort`"
    if role == "export":
        return "`adni-sexdiff export`"
    if role == "analysis":
        return "`adni-sexdiff analyze`"
    if role == "diagnostics":
        return "`adni-sexdiff axis-diagnostics`"
    if role == f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['diagnostics']}":
        return (
            f"`adni-sexdiff axis-diagnostics --analysis-dir {dirs[f'sensitivity/{LATENT_SENSITIVITY_SUBDIRS['analysis']}']} "
            f"--out-dir {dirs[role]}`"
        )
    if role.startswith("export-sensitivity/"):
        variant = role.split("/")[1]
        if role == _variant_role(variant, "diagnostics"):
            return (
                f"`adni-sexdiff axis-diagnostics --input-dir {dirs[_variant_role(variant, 'export')]} --analysis-dir "
                f"{dirs[_variant_role(variant, 'analysis')]} --out-dir {dirs[role]}`"
            )
        return f"`adni-sexdiff export-sensitivity --variant {variant} --force`, then the variant's `axis-diagnostics`"
    if role.startswith("stage-sensitivity/"):
        if role == _stage_arm_role("diagnostics"):
            return (
                f"`adni-sexdiff axis-diagnostics --input-dir {dirs[_stage_arm_role('export')]} --analysis-dir "
                f"{dirs[_stage_arm_role('analysis')]} --out-dir {dirs[role]}`"
            )
        return "`adni-sexdiff stage-sensitivity --force`, then the arm's `axis-diagnostics`"
    if role.startswith("rank-sensitivity/"):
        if role == _rank_sweep_role("diagnostics"):
            return (
                f"`adni-sexdiff axis-diagnostics --analysis-dir "
                f"{dirs[_rank_sweep_role(int(RANK_SENSITIVITY_LADDER['diagnosed_rank']))]} --out-dir {dirs[role]}`"
            )
        return "`adni-sexdiff rank-sensitivity --force`, then the sweep's `axis-diagnostics`"
    return "`adni-sexdiff latent-sensitivity`"


def _get(manifest: dict, keys: str | Sequence[str], *, where: str):
    """A nested manifest value by its keys (a dotted string, or a sequence when a key holds a dot); stops naming the manifest and the key when it is absent."""
    keys = keys.split(".") if isinstance(keys, str) else list(keys)
    node = manifest
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            raise RuntimeError(
                f"{where} has no key {'.'.join(keys)!r}: the chain map of `report` (change adni-report) expects it; a later step "
                "change moved it and the report change that follows updates the map; nothing was written"
            )
        node = node[key]
    return node


def _load_report_inputs(
    *,
    cleaned_dir=None,
    cohort_dir=None,
    input_dir=None,
    analysis_dir=None,
    diagnostics_dir=None,
    sensitivity_dir=None,
    export_sensitivity_dir=None,
    stage_sensitivity_dir=None,
    rank_sensitivity_dir=None,
    log: str = "[report]",
) -> dict:
    """Read and gate every input of ``report`` (design D3 of ``adni-report``, ``adni-report-variants``, ``adni-report-stage-arm`` and ``adni-report-rank-sweep``), before anything is written.

    Parameters
    ----------
    cleaned_dir, cohort_dir, input_dir, analysis_dir, diagnostics_dir, sensitivity_dir, export_sensitivity_dir, stage_sensitivity_dir, rank_sensitivity_dir:
        The nine directories (``_report_dirs``); ``None`` is the pipeline's.
    log:
        The progress prefix.

    Returns
    -------
    dict
        ``dirs`` (role → directory), ``files`` (role → name → ``path``,
        ``sha256``, ``bytes``), ``manifests`` and ``manifest_paths`` (label →
        parsed manifest and its path, in ``_REPORT_MANIFESTS`` order),
        ``records`` (``primary`` and ``arm``: the two ``result.json``;
        ``variants``: variant → its ``result.json``; ``stage_arm``: the CN /
        LMCI / AD arm's ``result.json``; ``ranks``: forced rank → its
        ``result.json``, in ladder order), ``tables``
        (``stage_counts``, ``comparison``, ``diagnostics`` and
        ``arm_diagnostics``; ``variants``: variant → ``comparison``,
        ``bridge`` (``None`` without a bridge role) and ``diagnostics``;
        ``stage_arm`` and ``rank_sweep``: ``comparison`` and
        ``diagnostics``; each CSV read as text), ``provenance`` (one row
        per input file: path, sha256, bytes, where it is recorded),
        ``chain`` (one row per link: the manifest key, the upstream value,
        the hash, ``ok``, the step to rerun), ``versions`` (the consistent
        versions of ``_REPORT_PINNED_PACKAGES``) and ``findings`` (design
        D8: dirty revisions, manifests without ``numerics``).

    Notes
    -----
    Gates, in this order, each stopping before anything is written and
    naming the file or setting, both values where there are two and the
    step to rerun, never a participant: (1) every file of
    ``REPORT_INPUT_FILES`` present; (2) every aggregate file hashes to the
    value its own manifest records under ``outputs`` (manifests are hashed
    for the chain, not checked against themselves); (3) the primary is the
    primary (no latent adjustment recorded or in the record, ``is_primary``
    in its diagnostics), the arm is ``LATENT_SENSITIVITY_ARM`` (its
    conditioning and name, ``is_primary`` false in its diagnostics) and each
    directory of ``REPORT_EXPORT_VARIANTS`` holds that variant (its export, analysis
    and comparison manifests name it, its export manifest's ``variant``
    block equals the registry entry, its analysis records no latent
    adjustment, its diagnostics record ``is_primary`` false and its name);
    the bridge table of a variant with hook ``factors`` is then checked
    against ``bridge.table.sha256`` of its export manifest, the one place
    the step records it; the CN / LMCI / AD arm is ``STAGE_SENSITIVITY_ARM``
    (its export manifest records step ``stage-sensitivity``, every field of
    the constant in its ``stage_arm`` block and no ``variant`` block, its
    analysis and comparison manifests name the arm, its analysis records no
    latent adjustment, its diagnostics record ``is_primary`` false and the
    arm); the rank sweep is ``RANK_SENSITIVITY_LADDER`` (each rank directory
    holds its rank: step ``rank-sensitivity``, ``settings.forced_components``
    and ``rank_sweep.forced_rank`` the rank, its record's
    ``latent.selected_lv`` the rank with selection ``forced``; every field of
    the constant in its ``rank_sweep.ladder``; ``rank_sweep.primary_rank``
    the primary record's rank; no latent adjustment and no ``variant`` or
    ``stage_arm`` block; the comparison records step ``rank-sensitivity``,
    the constant, exactly the ladder's directories and an anchor equal at the
    primary record's rank; the diagnostics record ``is_primary`` false and
    the forced rank ``diagnosed_rank``); (4) reported runs: the primary, the
    arm, every variant analysis, the CN / LMCI / AD arm's analysis and every
    rank record ``n_jobs = REPORTED_N_JOBS`` in manifest and record, every
    ``numerics`` block present records ``pinned`` true, and every manifest
    that records MOTCO, scikit-learn or metabo_adni records the same
    version; (5) the chain, link by link from the clean manifests to the
    arm's, every variant's, the CN / LMCI / AD arm's and the rank sweep's
    diagnostics, the primary feature tables the arm export names as the
    source of its floors included. The identity and reported-run gates read
    a manifest's own content, so they run before the chain: an arm given as
    the primary, swapped variant or rank directories, a crossed CN / LMCI /
    AD arm or rank, an unanchored sweep, an unreported run or an unpinned
    manifest is named as such, not as a broken link. No participant-level
    file is opened or hashed: the hashes of ``cohort.csv``, the export CSVs
    of the primary, of every variant and of the CN / LMCI / AD arm,
    ``latent_scores.csv`` and ``analysis_metadata.csv`` are the ones the
    manifests recorded (``equals_*`` flags are read, not recomputed).
    """
    dirs = _report_dirs(
        cleaned_dir, cohort_dir, input_dir, analysis_dir, diagnostics_dir, sensitivity_dir, export_sensitivity_dir,
        stage_sensitivity_dir, rank_sensitivity_dir,
    )

    # (1) every input present
    absent = []
    for role, names in REPORT_INPUT_FILES.items():
        for name in names:
            if not (dirs[role] / name).is_file():
                absent.append(f"{dirs[role] / name} (run {_report_rerun(role, name, dirs)})")
    if absent:
        raise FileNotFoundError(
            f"{len(absent)} report input(s) absent: " + "; ".join(absent) + "; nothing was written"
        )

    # hashes, parsed manifests, records and tables
    files: dict[str, dict[str, dict]] = {}
    for role, names in REPORT_INPUT_FILES.items():
        files[role] = {}
        for name in names:
            path = dirs[role] / name
            files[role][name] = {"path": path, "sha256": _sha256_file(path), "bytes": path.stat().st_size}
    manifests: dict[str, dict] = {}
    manifest_paths: dict[str, Path] = {}
    manifest_of_role: dict[str, dict[str, str]] = {}
    for label, role, name in _REPORT_MANIFESTS:
        manifest_paths[label] = files[role][name]["path"]
        manifests[label] = json.loads(manifest_paths[label].read_text())
        manifest_of_role.setdefault(role, {})[name] = label
    n_files = sum(len(v) for v in files.values())
    print(f"{log} inputs: {n_files} files hashed under {len(files)} directories; {len(manifests)} manifests read")

    # (2) every aggregate file against its own manifest
    provenance: list[dict] = []
    checked = 0
    for role, names in REPORT_INPUT_FILES.items():
        role_manifests = manifest_of_role.get(role, {})
        for name in names:
            entry = files[role][name]
            if name in role_manifests:
                provenance.append({**entry, "role": role, "name": name, "recorded_in": "hashed for the chain (recorded by the manifests downstream)"})
                continue
            if not role_manifests:
                # a bridge table: recorded by its variant's export manifest, checked once that manifest is identified (gate 3)
                label = _variant_labels(role.split("/")[1])["export"]
                provenance.append({**entry, "role": role, "name": name, "recorded_in": f"{label}: bridge.table.sha256"})
                continue
            (label,) = role_manifests.values()
            recorded = manifests[label].get("outputs", {}).get(name, {}).get("sha256")
            if recorded is None:
                raise RuntimeError(
                    f"{manifest_paths[label]} records no hash for {name} under outputs; rerun "
                    f"{_report_rerun(role, name, dirs)}; nothing was written"
                )
            if recorded != entry["sha256"]:
                raise RuntimeError(
                    f"{entry['path']}: sha256 {entry['sha256']} differs from the hash {manifest_paths[label]} records "
                    f"({recorded}); rerun {_report_rerun(role, name, dirs)} (then every step after it); nothing was written"
                )
            checked += 1
            provenance.append({**entry, "role": role, "name": name, "recorded_in": f"{label}: outputs.{name}.sha256"})
    print(
        f"{log} {checked} aggregate files hash to the values their manifests record under outputs; {len(manifests)} "
        "manifests hashed for the chain"
    )

    a_role = "analysis"
    s_role = f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['analysis']}"
    primary = json.loads(files[a_role][ANALYSIS_RESULT]["path"].read_text())
    arm = json.loads(files[s_role][ANALYSIS_RESULT]["path"].read_text())
    p_manifest, d_manifest = manifests["analyze"], manifests["axis-diagnostics"]
    a_manifest, c_manifest, ad_manifest = (
        manifests["latent-sensitivity (analysis)"], manifests["latent-sensitivity (comparison)"], manifests["axis-diagnostics (arm)"]
    )

    # (3) identity: the primary is the primary, the arm is the predeclared arm
    latent = p_manifest.get("settings", {}).get("latent_adjustment")
    if latent is not None or "latent_adjustment" in primary:
        raise RuntimeError(
            f"{dirs[a_role]} is not the primary: {ANALYSIS_MANIFEST} records latent adjustment {latent!r}"
            + (f" and {ANALYSIS_RESULT} carries a latent_adjustment block" if "latent_adjustment" in primary else "")
            + " (the primary records None); point --analysis-dir at the primary (`adni-sexdiff analyze`); nothing was written"
        )
    if _get(d_manifest, "inputs.analysis.is_primary", where=str(manifest_paths["axis-diagnostics"])) is not True:
        raise RuntimeError(
            f"{manifest_paths['axis-diagnostics']} records inputs.analysis.is_primary false: --diagnostics-dir must name the "
            "primary's diagnostics (`adni-sexdiff axis-diagnostics`); nothing was written"
        )
    conditioning = (arm.get("latent_adjustment") or {}).get("conditioning")
    arm_name = a_manifest.get("arm", {}).get("name")
    if conditioning != LATENT_SENSITIVITY_ARM["conditioning"] or arm_name != LATENT_SENSITIVITY_ARM["name"]:
        raise RuntimeError(
            f"{dirs[s_role]} is not the predeclared arm: {ANALYSIS_RESULT} records latent adjustment {conditioning!r} and "
            f"{ANALYSIS_MANIFEST} the arm {arm_name!r}, but LATENT_SENSITIVITY_ARM is {LATENT_SENSITIVITY_ARM['name']!r} "
            f"({LATENT_SENSITIVITY_ARM['setting']} = {LATENT_SENSITIVITY_ARM['conditioning']!r}); rerun "
            "`adni-sexdiff latent-sensitivity`; nothing was written"
        )
    if _get(ad_manifest, "inputs.analysis.is_primary", where=str(manifest_paths["axis-diagnostics (arm)"])) is not False:
        raise RuntimeError(
            f"{manifest_paths['axis-diagnostics (arm)']} records inputs.analysis.is_primary true: the arm's diagnostics must "
            f"read the arm ({_report_rerun(f'sensitivity/{LATENT_SENSITIVITY_SUBDIRS['diagnostics']}', '', dirs)}); nothing was written"
        )
    print(
        f"{log} primary: {dirs[a_role]} (rank {primary['latent']['selected_lv']}, latent adjustment none); arm: "
        f"{dirs[s_role]} ({arm_name}, `{conditioning}`-conditioned, rank {arm['latent']['selected_lv']})"
    )
    variant_records: dict[str, dict] = {}
    for variant in REPORT_EXPORT_VARIANTS:
        spec = EXPORT_VARIANTS[variant]
        labels = _variant_labels(variant)
        e_role, va_role, b_role = (_variant_role(variant, k) for k in ("export", "analysis", "bridge"))
        rerun = _report_rerun(e_role, "", dirs)
        v_dir = dirs[e_role].parent
        for key in ("export", "analysis", "comparison"):
            recorded = (manifests[labels[key]].get("variant") or {}).get("name")
            if recorded != variant:
                raise RuntimeError(
                    f"{v_dir} is not the variant {variant!r}: {manifest_paths[labels[key]]} records the variant {recorded!r}; "
                    f"point --export-sensitivity-dir at the root whose {variant}/ holds that variant's outputs, or rerun "
                    f"{rerun}; nothing was written"
                )
        recorded_spec = manifests[labels["export"]]["variant"]
        for field in ("block", "hook", "rule", "setting", "change"):
            if recorded_spec.get(field) != spec.get(field):
                raise RuntimeError(
                    f"{manifest_paths[labels['export']]} records the variant {variant!r} with {field} "
                    f"{recorded_spec.get(field)!r}, but EXPORT_VARIANTS[{variant!r}][{field!r}] is {spec.get(field)!r}: the "
                    f"registry entry moved after the run; rerun {rerun}; nothing was written"
                )
        record = json.loads(files[va_role][ANALYSIS_RESULT]["path"].read_text())
        latent = manifests[labels["analysis"]].get("settings", {}).get("latent_adjustment")
        if latent is not None or "latent_adjustment" in record:
            raise RuntimeError(
                f"{dirs[va_role]} is not the variant's analysis: {ANALYSIS_MANIFEST} records latent adjustment {latent!r}"
                + (f" and {ANALYSIS_RESULT} carries a latent_adjustment block" if "latent_adjustment" in record else "")
                + f" (a variant records None, the primary's setting); rerun {rerun}; nothing was written"
            )
        diag_where = str(manifest_paths[labels["diagnostics"]])
        is_primary = _get(manifests[labels["diagnostics"]], "inputs.analysis.is_primary", where=diag_where)
        read_variant = _get(manifests[labels["diagnostics"]], "inputs.analysis.export_variant", where=diag_where)
        if is_primary is not False or read_variant != variant:
            raise RuntimeError(
                f"{diag_where} records inputs.analysis.is_primary {is_primary!r} and export_variant {read_variant!r}: the "
                f"diagnostics of {variant!r} must read that variant (is_primary false, export_variant {variant!r}); rerun "
                f"{_report_rerun(_variant_role(variant, 'diagnostics'), '', dirs)}; nothing was written"
            )
        if b_role in files:
            name = EXPORT_SENSITIVITY_BRIDGE_TABLE
            entry = files[b_role][name]
            recorded = _get(manifests[labels["export"]], "bridge.table.sha256", where=str(manifest_paths[labels["export"]]))
            if recorded != entry["sha256"]:
                raise RuntimeError(
                    f"{entry['path']}: sha256 {entry['sha256']} differs from the hash {manifest_paths[labels['export']]} "
                    f"records under bridge.table.sha256 ({recorded}); rerun {rerun}; nothing was written"
                )
        variant_records[variant] = record
    print(
        f"{log} variants ({', '.join(f'`{v}`' for v in REPORT_EXPORT_VARIANTS)}, `REPORT_EXPORT_VARIANTS`): "
        + "; ".join(
            f"{variant}: {dirs[_variant_role(variant, 'analysis')].parent} (rank {record['latent']['selected_lv']}, latent "
            "adjustment none" + (", bridge table as recorded" if _variant_role(variant, "bridge") in files else "") + ")"
            for variant, record in variant_records.items()
        )
    )
    st_name = STAGE_SENSITIVITY_ARM["name"]
    st_labels = _STAGE_ARM_LABELS
    st_e_role, st_a_role, st_d_role = (_stage_arm_role(k) for k in ("export", "analysis", "diagnostics"))
    st_rerun = _report_rerun(st_e_role, "", dirs)
    st_export = manifests[st_labels["export"]]
    st_export_path = manifest_paths[st_labels["export"]]
    recorded_arm = st_export.get("stage_arm") or {}
    if st_export.get("step") != "stage-sensitivity" or recorded_arm.get("constant") != "STAGE_SENSITIVITY_ARM":
        raise RuntimeError(
            f"{dirs[st_e_role]} is not the CN / LMCI / AD arm's export: {st_export_path} records step "
            f"{st_export.get('step')!r} and stage_arm.constant {recorded_arm.get('constant')!r} (the arm records "
            f"'stage-sensitivity' and 'STAGE_SENSITIVITY_ARM'); point --stage-sensitivity-dir at the root of "
            f"`stage-sensitivity`, or rerun {st_rerun}; nothing was written"
        )
    for field, value in STAGE_SENSITIVITY_ARM.items():
        expected = list(value) if isinstance(value, tuple) else value
        if recorded_arm.get(field) != expected:
            raise RuntimeError(
                f"{st_export_path} records the arm {recorded_arm.get('name')!r} with {field} {recorded_arm.get(field)!r}, "
                f"but STAGE_SENSITIVITY_ARM[{field!r}] is {value!r}: the constant moved after the run; rerun {st_rerun}; "
                "nothing was written"
            )
    if st_export.get("variant") is not None:
        raise RuntimeError(
            f"{st_export_path} records the export variant {(st_export.get('variant') or {}).get('name')!r}: the CN / LMCI / "
            f"AD arm takes the primary export's rows and is not crossed with an export variant; rerun {st_rerun}; nothing "
            "was written"
        )
    st_record = json.loads(files[st_a_role][ANALYSIS_RESULT]["path"].read_text())
    st_analysis = manifests[st_labels["analysis"]]
    recorded = (st_analysis.get("stage_arm") or {}).get("name")
    latent = st_analysis.get("settings", {}).get("latent_adjustment")
    if recorded != st_name or latent is not None or "latent_adjustment" in st_record:
        raise RuntimeError(
            f"{dirs[st_a_role]} is not the CN / LMCI / AD arm's analysis: {ANALYSIS_MANIFEST} records the arm {recorded!r} "
            f"and latent adjustment {latent!r}"
            + (f", and {ANALYSIS_RESULT} carries a latent_adjustment block" if "latent_adjustment" in st_record else "")
            + f" (the arm records {st_name!r} and None: it is not crossed with the latent adjustment); point "
            f"--stage-sensitivity-dir at the root of `stage-sensitivity`, or rerun {st_rerun}; nothing was written"
        )
    st_comparison = manifests[st_labels["comparison"]]
    for where, value in (("stage_arm.name", (st_comparison.get("stage_arm") or {}).get("name")),
                         ("arm.name", (st_comparison.get("arm") or {}).get("name"))):
        if value != st_name:
            raise RuntimeError(
                f"{manifest_paths[st_labels['comparison']]} records {where} {value!r}, but STAGE_SENSITIVITY_ARM is "
                f"{st_name!r}; point --stage-sensitivity-dir at the root of `stage-sensitivity`, or rerun {st_rerun}; "
                "nothing was written"
            )
    st_diag_where = str(manifest_paths[st_labels["diagnostics"]])
    is_primary = _get(manifests[st_labels["diagnostics"]], "inputs.analysis.is_primary", where=st_diag_where)
    read_arm = (manifests[st_labels["diagnostics"]].get("inputs", {}).get("analysis") or {}).get("stage_arm")
    if is_primary is not False or read_arm != st_name:
        raise RuntimeError(
            f"{st_diag_where} records inputs.analysis.is_primary {is_primary!r} and stage_arm {read_arm!r}: the diagnostics "
            f"of the CN / LMCI / AD arm must read the arm (is_primary false, stage_arm {st_name!r}); rerun "
            f"{_report_rerun(st_d_role, '', dirs)}; nothing was written"
        )
    print(
        f"{log} CN / LMCI / AD arm (`STAGE_SENSITIVITY_ARM`): {dirs[st_a_role].parent} ({st_name}, rank "
        f"{st_record['latent']['selected_lv']}, latent adjustment none, no export variant)"
    )
    ladder = RANK_SENSITIVITY_LADDER
    ranks = [int(k) for k in ladder["ranks"]]
    p_rank = primary["latent"]["selected_lv"]
    rk_rerun = _report_rerun(_rank_sweep_role(ranks[0]), "", dirs)
    rk_c_role, rk_d_role = _rank_sweep_role("comparison"), _rank_sweep_role("diagnostics")

    def ladder_fields(recorded: dict | None, where: str) -> None:
        recorded = recorded or {}
        for field, value in ladder.items():
            expected = list(value) if isinstance(value, tuple) else value
            if recorded.get(field) != expected:
                raise RuntimeError(
                    f"{where} records the ladder {recorded.get('name')!r} with {field} {recorded.get(field)!r}, but "
                    f"RANK_SENSITIVITY_LADDER[{field!r}] is {value!r}: the constant moved after the run; rerun {rk_rerun}; "
                    "nothing was written"
                )

    rank_records: dict[int, dict] = {}
    for k in ranks:
        role, label = _rank_sweep_role(k), _RANK_SWEEP_LABELS[k]
        m, where = manifests[label], manifest_paths[label]
        record = json.loads(files[role][ANALYSIS_RESULT]["path"].read_text())
        latent = m.get("settings", {}).get("latent_adjustment")
        if latent is not None or "latent_adjustment" in record:
            raise RuntimeError(
                f"{dirs[role]} is not forced rank {k} of the rank sweep: {ANALYSIS_MANIFEST} records latent adjustment "
                f"{latent!r}" + (f" and {ANALYSIS_RESULT} carries a latent_adjustment block" if "latent_adjustment" in record else "")
                + " (a rank records None: the sweep is not crossed with the latent adjustment); point --rank-sensitivity-dir "
                f"at the root of `rank-sensitivity`, or rerun {rk_rerun}; nothing was written"
            )
        sweep = m.get("rank_sweep") or {}
        held = {
            "step": m.get("step"),
            "settings.forced_components": m.get("settings", {}).get("forced_components"),
            "rank_sweep.forced_rank": sweep.get("forced_rank"),
            f"{ANALYSIS_RESULT} latent.selected_lv": record.get("latent", {}).get("selected_lv"),
            f"{ANALYSIS_RESULT} latent.component_selection": record.get("latent", {}).get("component_selection"),
        }
        expected = {
            "step": "rank-sensitivity", "settings.forced_components": k, "rank_sweep.forced_rank": k,
            f"{ANALYSIS_RESULT} latent.selected_lv": k, f"{ANALYSIS_RESULT} latent.component_selection": "forced",
        }
        if held != expected:
            raise RuntimeError(
                f"{dirs[role]} does not hold forced rank {k} of the rank sweep: {where} and its {ANALYSIS_RESULT} record "
                + ", ".join(f"{key} {value!r}" for key, value in held.items())
                + f" (forced rank {k} records " + ", ".join(f"{key} {value!r}" for key, value in expected.items())
                + f"); the directory holds rank {held[f'{ANALYSIS_RESULT} latent.selected_lv']!r}, not {k}; point "
                f"--rank-sensitivity-dir at the root of `rank-sensitivity`, or rerun {rk_rerun}; nothing was written"
            )
        if sweep.get("ladder", {}).get("constant") != "RANK_SENSITIVITY_LADDER":
            raise RuntimeError(
                f"{where} records rank_sweep.ladder.constant {sweep.get('ladder', {}).get('constant')!r} (the sweep records "
                f"'RANK_SENSITIVITY_LADDER'); rerun {rk_rerun}; nothing was written"
            )
        ladder_fields(sweep.get("ladder"), f"{where} (rank_sweep.ladder)")
        if sweep.get("primary_rank") != p_rank:
            raise RuntimeError(
                f"{where} records rank_sweep.primary_rank {sweep.get('primary_rank')!r}, but the primary record's rank is "
                f"{p_rank} ({dirs[a_role] / ANALYSIS_RESULT}): the sweep was run beside another primary; rerun {rk_rerun}; "
                "nothing was written"
            )
        for key in ("variant", "stage_arm"):
            if m.get(key) is not None:
                raise RuntimeError(
                    f"{where} records the {key} {(m.get(key) or {}).get('name')!r}: the rank sweep runs on the primary export "
                    f"and is not crossed with an export variant or the CN / LMCI / AD arm (sweep rule 8); rerun {rk_rerun}; "
                    "nothing was written"
                )
        rank_records[k] = record
    rk_c_label = _RANK_SWEEP_LABELS["comparison"]
    rk_comparison, rk_c_where = manifests[rk_c_label], manifest_paths[rk_c_label]
    if rk_comparison.get("step") != "rank-sensitivity":
        raise RuntimeError(
            f"{dirs[rk_c_role]} is not the rank sweep's comparison: {rk_c_where} records step {rk_comparison.get('step')!r} "
            f"(the sweep records 'rank-sensitivity'); point --rank-sensitivity-dir at the root of `rank-sensitivity`, or "
            f"rerun {rk_rerun}; nothing was written"
        )
    ladder_fields(rk_comparison.get("settings", {}).get("RANK_SENSITIVITY_LADDER"), f"{rk_c_where} (settings.RANK_SENSITIVITY_LADDER)")
    recorded_ranks = rk_comparison.get("ranks") or {}
    expected_ranks = {_rank_dir_name(k): k for k in ranks}
    held_ranks = {name: (entry or {}).get("rank") for name, entry in recorded_ranks.items()}
    if held_ranks != expected_ranks:
        raise RuntimeError(
            f"{rk_c_where} records the ranks {held_ranks}, but RANK_SENSITIVITY_LADDER's directories are {expected_ranks}; "
            f"rerun {rk_rerun}; nothing was written"
        )
    anchor = rk_comparison.get("anchor") or {}
    if anchor.get("equal") is not True or anchor.get("rank") != p_rank:
        raise RuntimeError(
            f"{rk_c_where} records the anchor at rank {anchor.get('rank')!r} with equal {anchor.get('equal')!r}, but the "
            f"sweep is reported only when its anchor at the primary record's rank {p_rank} equals the primary (sweep rule 3; "
            "a failed anchor writes no comparison, so this manifest was edited or comes from another sweep); rerun "
            f"{rk_rerun}; nothing was written"
        )
    rk_d_label = _RANK_SWEEP_LABELS["diagnostics"]
    rk_d_where = str(manifest_paths[rk_d_label])
    rk_d_analysis = manifests[rk_d_label].get("inputs", {}).get("analysis") or {}
    is_primary = _get(manifests[rk_d_label], "inputs.analysis.is_primary", where=rk_d_where)
    read_sweep = rk_d_analysis.get("rank_sweep") or {}
    if (is_primary is not False or read_sweep.get("forced_rank") != ladder["diagnosed_rank"]
            or read_sweep.get("primary_rank") != p_rank):
        raise RuntimeError(
            f"{rk_d_where} records inputs.analysis.is_primary {is_primary!r} and rank_sweep {read_sweep or None!r}: the "
            f"diagnostics of the rank sweep must read its top rank (is_primary false, forced_rank "
            f"{ladder['diagnosed_rank']}, primary_rank {p_rank}); rerun {_report_rerun(rk_d_role, '', dirs)}; nothing was "
            "written"
        )
    print(
        f"{log} rank sweep (`RANK_SENSITIVITY_LADDER`): {dirs[rk_c_role].parent} ({ladder['name']}, forced ranks "
        + ", ".join(str(k) for k in ranks) + f"; anchor equal at the primary's rank {p_rank}; latent adjustment none, "
        f"no export variant or arm; diagnostics of rank {ladder['diagnosed_rank']})"
    )

    # (4) reported runs: n_jobs, pinned numerics, consistent versions
    arm_rerun = "`adni-sexdiff latent-sensitivity`"
    reported = [("analyze", primary, "`adni-sexdiff analyze`"), ("latent-sensitivity (analysis)", arm, arm_rerun)]
    reported += [
        (_variant_labels(v)["analysis"], record, f"`adni-sexdiff export-sensitivity --variant {v} --force`")
        for v, record in variant_records.items()
    ]
    reported.append((st_labels["analysis"], st_record, "`adni-sexdiff stage-sensitivity --force`"))
    reported += [(_RANK_SWEEP_LABELS[k], rank_records[k], "`adni-sexdiff rank-sensitivity --force`") for k in ranks]
    for label, record, rerun in reported:
        for where, value in ((f"{manifest_paths[label]} (settings.n_jobs)", manifests[label].get("settings", {}).get("n_jobs")),
                             (f"{manifest_paths[label].parent / ANALYSIS_RESULT} (measurement.n_jobs)", record.get("measurement", {}).get("n_jobs"))):
            if value != REPORTED_N_JOBS:
                raise RuntimeError(
                    f"{where} records n_jobs = {value}: not a reported run (reported runs use n_jobs = {REPORTED_N_JOBS}, "
                    f"REPORTED_N_JOBS); rerun {rerun} without --n-jobs; nothing was written"
                )
    numerics_absent = []
    for label, manifest in manifests.items():
        numerics = manifest.get("numerics")
        if numerics is None:
            numerics_absent.append(label)
        elif numerics.get("pinned") is not True:
            raise RuntimeError(
                f"{manifest_paths[label]} records numerics.pinned {numerics.get('pinned')!r}: the run is not pinned "
                "(constants.NUMERIC_SETTINGS) and is not reported; rerun the step under the pinned environment; nothing was written"
            )
    versions: dict[str, str] = {}
    for pkg in _REPORT_PINNED_PACKAGES:
        first: tuple[str, str] | None = None
        for label, manifest in manifests.items():
            seen = manifest.get("versions", {}).get(pkg)
            if seen is None:
                continue
            if first is None:
                first = (label, seen)
            elif seen != first[1]:
                raise RuntimeError(
                    f"versions.{pkg} differs between {manifest_paths[first[0]]} ({first[1]}) and {manifest_paths[label]} "
                    f"({seen}); the pipeline must be rerun from the step whose pin moved (AGENTS.md constraints 3 and 4); "
                    "nothing was written"
                )
        if first is not None:
            versions[pkg] = first[1]
    print(
        f"{log} reported runs: primary, arm, {len(variant_records)} variants, the CN / LMCI / AD arm and "
        f"{len(rank_records)} ranks n_jobs {REPORTED_N_JOBS}; numerics pinned in "
        f"{len(manifests) - len(numerics_absent)} "
        f"manifests, absent in {len(numerics_absent)}; versions consistent ("
        + ", ".join(f"{k} {v}" for k, v in versions.items()) + ")"
    )

    # (5) the chain, link by link
    sha = {role: {name: entry["sha256"] for name, entry in names.items()} for role, names in files.items()}
    c_role = f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['comparison']}"
    ad_role = f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['diagnostics']}"
    export_sha = sha["export"][EXPORT_MANIFEST]
    cohort_sha = sha["cohort"][COHORT_MANIFEST]
    primary_sha = {ANALYSIS_RESULT: sha[a_role][ANALYSIS_RESULT], ANALYSIS_MANIFEST: sha[a_role][ANALYSIS_MANIFEST]}
    arm_sha = {ANALYSIS_RESULT: sha[s_role][ANALYSIS_RESULT], ANALYSIS_MANIFEST: sha[s_role][ANALYSIS_MANIFEST]}
    chain: list[dict] = []

    def link(label: str, keys: list[str], upstream: str, now: str, rerun: str) -> None:
        recorded = _get(manifests[label], keys, where=str(manifest_paths[label]))
        chain.append({"link": f"{label}: {'.'.join(keys)}", "upstream": upstream, "sha256": now, "recorded": recorded, "ok": recorded == now, "rerun": rerun})

    def export_file_links(label: str, rerun: str, *, export_role: str = "export", export_label: str = "export") -> None:
        outputs = manifests[export_label].get("outputs", {})
        link(label, ["inputs", "export_manifest", "sha256"], f"sha256({files[export_role][EXPORT_MANIFEST]['path']})", sha[export_role][EXPORT_MANIFEST], rerun)
        for name in ANALYSIS_INPUT_FILES:
            if name == EXPORT_MANIFEST:
                continue
            link(label, ["inputs", "files", name, "recorded"], f"{export_label}: outputs.{name}.sha256", outputs.get(name, {}).get("sha256"), rerun)

    def diagnostics_links(label: str, analysis_label: str, analysis_sha: dict, rerun: str, *, export_role: str = "export") -> None:
        link(label, ["inputs", "analysis", "analysis_manifest", "sha256"], f"sha256({manifest_paths[analysis_label]})", analysis_sha[ANALYSIS_MANIFEST], rerun)
        link(label, ["inputs", "analysis", "files", ANALYSIS_RESULT, "sha256"], f"{analysis_label}: outputs.{ANALYSIS_RESULT}.sha256",
             manifests[analysis_label].get("outputs", {}).get(ANALYSIS_RESULT, {}).get("sha256"), rerun)
        link(label, ["inputs", "export", "export_manifest", "sha256"], f"sha256({files[export_role][EXPORT_MANIFEST]['path']})", sha[export_role][EXPORT_MANIFEST], rerun)
        link(label, ["inputs", "cohort", "files", COHORT_MANIFEST, "sha256"], f"sha256({files['cohort'][COHORT_MANIFEST]['path']})", cohort_sha, rerun)

    for platform in PLATFORMS:
        clean_path = files["cleaned"][f"{platform}/{CLEAN_MANIFEST}"]["path"]
        link("cohort", ["inputs", "clean", platform, "manifest", "sha256"], f"sha256({clean_path})", sha["cleaned"][f"{platform}/{CLEAN_MANIFEST}"], "`adni-sexdiff cohort`")
    for platform in PLATFORMS:
        clean_path = files["cleaned"][f"{platform}/{CLEAN_MANIFEST}"]["path"]
        link("export", ["inputs", "clean", platform, "manifest", "sha256"], f"sha256({clean_path})", sha["cleaned"][f"{platform}/{CLEAN_MANIFEST}"], "`adni-sexdiff export`")
    link("export", ["inputs", "cohort", "manifest", "sha256"], f"sha256({files['cohort'][COHORT_MANIFEST]['path']})", cohort_sha, "`adni-sexdiff export`")
    export_file_links("analyze", "`adni-sexdiff analyze`")
    diagnostics_links("axis-diagnostics", "analyze", primary_sha, "`adni-sexdiff axis-diagnostics`")
    export_file_links("latent-sensitivity (analysis)", arm_rerun)
    for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
        link("latent-sensitivity (analysis)", ["reference", "files", name, "sha256"], f"sha256({files[a_role][name]['path']})", primary_sha[name], arm_rerun)
    for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
        link("latent-sensitivity (comparison)", ["reference", "files", name, "sha256"], f"sha256({files[a_role][name]['path']})", primary_sha[name], arm_rerun)
    for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
        link("latent-sensitivity (comparison)", ["arm", "files", name, "sha256"], f"sha256({files[s_role][name]['path']})", arm_sha[name], arm_rerun)
    link("latent-sensitivity (comparison)", ["inputs", "export", "export_manifest", "sha256"], f"sha256({files['export'][EXPORT_MANIFEST]['path']})", export_sha, arm_rerun)
    link("latent-sensitivity (comparison)", ["inputs", "cohort", "files", COHORT_MANIFEST, "sha256"], f"sha256({files['cohort'][COHORT_MANIFEST]['path']})", cohort_sha, arm_rerun)
    diagnostics_links("axis-diagnostics (arm)", "latent-sensitivity (analysis)", arm_sha, _report_rerun(ad_role, "", dirs))
    export_path = files["export"][EXPORT_MANIFEST]["path"]
    for variant in REPORT_EXPORT_VARIANTS:
        labels = _variant_labels(variant)
        ve_role, va_role, vb_role = (_variant_role(variant, k) for k in ("export", "analysis", "bridge"))
        rerun = _report_rerun(ve_role, "", dirs)
        variant_sha = {name: sha[va_role][name] for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST)}
        for platform in PLATFORMS:
            clean_path = files["cleaned"][f"{platform}/{CLEAN_MANIFEST}"]["path"]
            link(labels["export"], ["inputs", "clean", platform, "manifest", "sha256"], f"sha256({clean_path})", sha["cleaned"][f"{platform}/{CLEAN_MANIFEST}"], rerun)
        link(labels["export"], ["inputs", "cohort", "manifest", "sha256"], f"sha256({files['cohort'][COHORT_MANIFEST]['path']})", cohort_sha, rerun)
        link(labels["export"], ["reference", "manifest", "sha256"], f"sha256({export_path})", export_sha, rerun)
        export_file_links(labels["analysis"], rerun, export_role=ve_role, export_label=labels["export"])
        for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
            link(labels["analysis"], ["reference", "files", name, "sha256"], f"sha256({files[a_role][name]['path']})", primary_sha[name], rerun)
        link(labels["analysis"], ["reference", "export", "manifest", "sha256"], f"sha256({export_path})", export_sha, rerun)
        for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
            link(labels["comparison"], ["reference", "files", name, "sha256"], f"sha256({files[a_role][name]['path']})", primary_sha[name], rerun)
        for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
            link(labels["comparison"], ["inputs", "variant", "analysis", "files", name, "sha256"], f"sha256({files[va_role][name]['path']})", variant_sha[name], rerun)
        link(labels["comparison"], ["inputs", "variant", "export", "manifest", "sha256"], f"sha256({files[ve_role][EXPORT_MANIFEST]['path']})", sha[ve_role][EXPORT_MANIFEST], rerun)
        link(labels["comparison"], ["inputs", "primary", "export", "manifest", "sha256"], f"sha256({export_path})", export_sha, rerun)
        if vb_role in files:
            name = EXPORT_SENSITIVITY_BRIDGE_TABLE
            link(labels["comparison"], ["inputs", "variant", "bridge", "sha256"], f"sha256({files[vb_role][name]['path']})", sha[vb_role][name], rerun)
        diagnostics_links(labels["diagnostics"], labels["analysis"], variant_sha, _report_rerun(_variant_role(variant, "diagnostics"), "", dirs), export_role=ve_role)
    st_c_role = _stage_arm_role("comparison")
    st_sha = {name: sha[st_a_role][name] for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST)}
    st_export_sha = sha[st_e_role][EXPORT_MANIFEST]
    export_outputs = manifests["export"].get("outputs", {})
    link(st_labels["export"], ["inputs", "cohort", "manifest", "sha256"], f"sha256({files['cohort'][COHORT_MANIFEST]['path']})", cohort_sha, st_rerun)
    link(st_labels["export"], ["inputs", "primary_export", "manifest", "sha256"], f"sha256({export_path})", export_sha, st_rerun)
    link(st_labels["export"], ["reference", "manifest", "sha256"], f"sha256({export_path})", export_sha, st_rerun)
    for block in EXPORT_BLOCKS:
        name = f"features_{block}.csv"
        link(st_labels["export"], ["reference", "feature_tables", name, "sha256"], f"export: outputs.{name}.sha256",
             export_outputs.get(name, {}).get("sha256"), st_rerun)
    export_file_links(st_labels["analysis"], st_rerun, export_role=st_e_role, export_label=st_labels["export"])
    for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
        link(st_labels["analysis"], ["reference", "files", name, "sha256"], f"sha256({files[a_role][name]['path']})", primary_sha[name], st_rerun)
    link(st_labels["analysis"], ["reference", "export", "manifest", "sha256"], f"sha256({export_path})", export_sha, st_rerun)
    for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
        link(st_labels["comparison"], ["reference", "files", name, "sha256"], f"sha256({files[a_role][name]['path']})", primary_sha[name], st_rerun)
    for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
        link(st_labels["comparison"], ["arm", "files", name, "sha256"], f"sha256({files[st_a_role][name]['path']})", st_sha[name], st_rerun)
    link(st_labels["comparison"], ["arm", "export", "manifest", "sha256"], f"sha256({st_export_path})", st_export_sha, st_rerun)
    link(st_labels["comparison"], ["inputs", "primary", "export", "manifest", "sha256"], f"sha256({export_path})", export_sha, st_rerun)
    link(st_labels["comparison"], ["inputs", "cohort", "files", COHORT_MANIFEST, "sha256"], f"sha256({files['cohort'][COHORT_MANIFEST]['path']})", cohort_sha, st_rerun)
    diagnostics_links(st_labels["diagnostics"], st_labels["analysis"], st_sha, _report_rerun(st_d_role, "", dirs), export_role=st_e_role)
    rank_sha = {k: {name: sha[_rank_sweep_role(k)][name] for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST)} for k in ranks}
    for k in ranks:
        label = _RANK_SWEEP_LABELS[k]
        export_file_links(label, rk_rerun)
        for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
            link(label, ["reference", "files", name, "sha256"], f"sha256({files[a_role][name]['path']})", primary_sha[name], rk_rerun)
        link(label, ["reference", "export", "manifest", "sha256"], f"sha256({export_path})", export_sha, rk_rerun)
    for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
        link(rk_c_label, ["reference", "files", name, "sha256"], f"sha256({files[a_role][name]['path']})", primary_sha[name], rk_rerun)
    for k in ranks:
        for name in (ANALYSIS_RESULT, ANALYSIS_MANIFEST):
            link(rk_c_label, ["ranks", _rank_dir_name(k), "files", name, "sha256"],
                 f"sha256({files[_rank_sweep_role(k)][name]['path']})", rank_sha[k][name], rk_rerun)
    link(rk_c_label, ["inputs", "export", "export_manifest", "sha256"], f"sha256({export_path})", export_sha, rk_rerun)
    top = int(ladder["diagnosed_rank"])
    diagnostics_links(rk_d_label, _RANK_SWEEP_LABELS[top], rank_sha[top], _report_rerun(rk_d_role, "", dirs))
    for row in chain:
        if not row["ok"]:
            label = row["link"].split(":")[0]
            raise RuntimeError(
                f"{manifest_paths[label]}: {row['link'].split(': ', 1)[1]} records {row['recorded']} but {row['upstream']} is "
                f"{row['sha256']}; the upstream output was regenerated after this step, rerun {row['rerun']} (then every "
                "step after it); nothing was written"
            )
    print(
        f"{log} chain: {len(chain)} links hold from the clean manifests to the arm's, every variant's, the CN / LMCI / AD "
        "arm's and the rank sweep's diagnostics"
    )

    # findings of the report itself (design D8)
    findings: list[str] = []
    for label, manifest in manifests.items():
        revision = manifest.get("git_revision") or {}
        if revision.get("dirty"):
            findings.append(f"{label} ({manifest_paths[label]}): the recorded revision {revision.get('commit')} is dirty")
    for label in numerics_absent:
        findings.append(f"{label} ({manifest_paths[label]}): no `numerics` block, written before `adni-portable-numerics`")
    for msg in findings:
        print(f"{log} FINDING: {msg}")

    def read_csv(role: str, name: str) -> pd.DataFrame:
        return pd.read_csv(files[role][name]["path"], dtype=object, keep_default_na=False)

    def diagnostics_tables(role: str) -> dict[str, pd.DataFrame]:
        return {
            "axis": read_csv(role, DIAGNOSTICS_AXIS_CORRELATIONS),
            "block_pcs": read_csv(role, DIAGNOSTICS_BLOCK_PCS),
            "geometry": read_csv(role, DIAGNOSTICS_GEOMETRY_SHARES),
            "components": read_csv(role, DIAGNOSTICS_COMPONENTS),
        }

    return {
        "dirs": dirs,
        "files": files,
        "manifests": manifests,
        "manifest_paths": manifest_paths,
        "records": {"primary": primary, "arm": arm, "variants": variant_records, "stage_arm": st_record, "ranks": rank_records},
        "tables": {
            "stage_counts": read_csv("cohort", COHORT_COUNTS),
            "comparison": read_csv(c_role, LATENT_SENSITIVITY_TABLE),
            "diagnostics": diagnostics_tables("diagnostics"),
            "arm_diagnostics": diagnostics_tables(ad_role),
            "variants": {
                variant: {
                    "comparison": read_csv(_variant_role(variant, "comparison"), EXPORT_SENSITIVITY_TABLE),
                    "bridge": (
                        read_csv(_variant_role(variant, "bridge"), EXPORT_SENSITIVITY_BRIDGE_TABLE)
                        if _variant_role(variant, "bridge") in files else None
                    ),
                    "diagnostics": diagnostics_tables(_variant_role(variant, "diagnostics")),
                }
                for variant in REPORT_EXPORT_VARIANTS
            },
            "stage_arm": {
                "comparison": read_csv(st_c_role, STAGE_SENSITIVITY_TABLE),
                "diagnostics": diagnostics_tables(st_d_role),
            },
            "rank_sweep": {
                "comparison": read_csv(rk_c_role, RANK_SENSITIVITY_TABLE),
                "diagnostics": diagnostics_tables(rk_d_role),
            },
        },
        "provenance": provenance,
        "chain": chain,
        "versions": versions,
        "numerics_absent": numerics_absent,
        "findings": findings,
    }


# --- report: rendering ------------------------------------------------------------

def _md_escape(value) -> str:
    return str(value).replace("|", "\\|")


def _markdown_table(df: pd.DataFrame, align: str | None = None) -> list[str]:
    """A Markdown table from a frame of strings; ``align`` is one ``l``/``r``/``c`` per column (left by default)."""
    columns = [str(c) for c in df.columns]
    align = align or "l" * len(columns)
    lines = [
        "| " + " | ".join(_md_escape(c) for c in columns) + " |",
        "|" + "|".join({"l": "---", "r": "---:", "c": ":---:"}[a] for a in align) + "|",
    ]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(_md_escape(v) for v in row) + " |")
    return lines


def _num(value, spec: str = ".6g") -> str:
    """A number read from a CSV as text (or a record value) for a report cell; ``n/a`` for an empty cell, None or NaN."""
    if value is None or value == "":
        return "n/a"
    return _fmt_nan(float(value), spec)


def _count(value) -> str:
    """An integer count for a report cell; ``n/a`` for None or an empty cell."""
    if value is None or value == "":
        return "n/a"
    return str(int(float(value)))


def _yes_no(value) -> str:
    if value in (None, ""):
        return "n/a"
    if isinstance(value, str):
        return "yes" if value == "True" else ("no" if value == "False" else value)
    return "yes" if value else "no"


def _text(value) -> str:
    """A text cell: strings as they are, None or empty as ``n/a``, everything else through ``str``."""
    if value is None or value == "":
        return "n/a"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ", ".join(_text(v) for v in value)
    return str(value)


def _flatten(node, prefix: str = "") -> dict[str, object]:
    """Nested scalars of a dict as ``a.b.c`` keys, in order."""
    out: dict[str, object] = {}
    if isinstance(node, dict):
        for k, v in node.items():
            out.update(_flatten(v, f"{prefix}{k}." if prefix or True else k))
    else:
        out[prefix[:-1]] = node
    return out


class _ReportBuilder:
    """The lines and the titled tables of the report, section by section (design D4 of ``adni-report``)."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.tables: dict[str, pd.DataFrame] = {}
        self.section_title = ""

    def section(self, title: str) -> None:
        self.lines += ["", f"## {title}"]
        self.section_title = title

    def para(self, *text: str) -> None:
        self.lines += ["", *text]

    def bullets(self, items: list[str]) -> None:
        self.lines += ["", *(f"- {item}" for item in items)]

    def heading(self, title: str) -> None:
        self.lines += ["", f"### {title}"]

    def code(self, *commands: str) -> None:
        self.lines += ["", "```", *commands, "```"]

    def table(self, title: str, rows: list[dict], columns: list[str], *, align: str | None = None) -> None:
        df = pd.DataFrame([[str(r[c]) for c in columns] for r in rows], columns=columns, dtype=object)
        key = f"{self.section_title} › {title}"
        if key in self.tables:
            raise ValueError(f"report table {key!r} is defined twice")
        self.tables[key] = df
        self.lines += ["", f"### {title}", "", *_markdown_table(df, align)]

    def text(self) -> str:
        return "\n".join(self.lines) + "\n"


def _statistics_rows(record: dict, *, rank_floor: int = ANALYSIS_RANK_FLOOR, alpha: float = ANALYSIS_ALPHA) -> list[dict]:
    """The rows of the statistics table as ``summary.md`` prints them (observed, p, rejected, null summary, note)."""
    design, meas, latent = record["design"], record["measurement"], record["latent"]
    stages = design["stage_levels"]
    selected = latent["selected_lv"]
    floor_binding = latent["component_selection"] == "cv" and selected == rank_floor
    eigengap = (record.get("config_spectrum", {}).get("pooled") or {}).get("relative_eigengap")
    rows = []
    for s in ANALYSIS_STATISTICS:
        p = record["p_values"].get(s)
        null = record["null_summary"].get(s, {})
        status = _rejected(p, alpha)
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
        rows.append({
            "statistic": s, "observed": _fmt(record["statistics"].get(s)), "p (RRPP)": _fmt(p),
            "rejected": "n/a" if status is None else ("yes" if status else "no"),
            "null mean": _fmt(null.get("mean")), "null sd": _fmt(null.get("sd")), "null q95": _fmt(null.get("q95")), "note": note,
        })
    return rows


def _latent_adjustment_lines(adjustment: dict, stages: list) -> list[str]:
    """The bullet lines of an arm's ``latent_adjustment`` block, as ``summary.md`` and ``latent_sensitivity.md`` print them."""
    design_cols = [str(c) for c in adjustment["design_columns"]]
    stage_names = {f"stage[{k}]": st for k, st in enumerate(stages)}
    n_cond = sum(c in stage_names for c in design_cols)
    r2 = adjustment.get("feature_r2", {})
    return [
        f"conditioning: `{adjustment['conditioning']}` (`{LATENT_SENSITIVITY_ARM['setting']}`, `LATENT_SENSITIVITY_ARM`): "
        "the basis is fitted on the pooled-standardized features with the covariates regressed out given the intercept "
        "and the stage indicators, per CV training set and on the full sample; the raw features are projected onto it; "
        "the trajectory model, LS-means and RRPP are the primary's",
        "covariates residualized (in order): " + ", ".join(f"`{c}`" for c in adjustment["covariates"]),
        f"residualization design columns: {len(design_cols)} ("
        + ", ".join(f"{c} = {stage_names[c]}" if c in stage_names else c for c in design_cols) + ")",
        f"samples {adjustment['n_samples']}; residual df {adjustment['residual_df']} (n − 1 − {n_cond} stage indicator(s) − "
        f"{len(design_cols) - n_cond} design column(s)); smallest CV training df {adjustment.get('cv_min_training_df')}",
        f"feature scale: `{adjustment['feature_scale']}`",
        "feature R² of the covariates given the intercept and the stage indicators (the share of each feature's variance "
        "the residualization removed; arm rule 6): q05 / q25 / q50 / q75 / q95 "
        + " / ".join(_fmt(r2.get(q), ".3f") for q in ("q05", "q25", "q50", "q75", "q95"))
        + f"; mean {_fmt(r2.get('mean'), '.3f')}; fraction above 0.5 {_fmt(r2.get('fraction_above_0.5'), '.3f')}",
    ]


def _flagged_axis_rows(axis: pd.DataFrame, variables: list[str]) -> list[dict]:
    """The flagged latent-component rows of ``axis_correlations.csv`` in the order ``diagnostics.md`` lists them (by |rho|)."""
    comps = list(dict.fromkeys(axis["component"]))
    flagged = axis[(axis["flag_raw"] == "True") | (axis["flag_partial"] == "True")].copy()
    if not len(flagged):
        return []
    rho = pd.to_numeric(flagged["spearman"].replace("", np.nan))
    partial = pd.to_numeric(flagged["partial_spearman"].replace("", np.nan))
    flagged["abs"] = rho.abs().fillna(partial.abs())
    flagged["c"] = flagged["component"].map({c: i for i, c in enumerate(comps)})
    flagged["v"] = flagged["variable"].map({v: i for i, v in enumerate(variables)})
    flagged = flagged.sort_values(["abs", "c", "v"], ascending=[False, True, True])
    return [
        {
            "row": f"{r.component} · {r.variable}", "component": r.component, "sd": _num(r.component_sd, ".4g"),
            "variable": f"`{r.variable}`", "source": r.source, "n": r.n, "rho": _num(r.spearman, ".3f"),
            "rho | design": _num(r.partial_spearman, ".3f"),
            "flag": "+".join(f for f, on in (("raw", r.flag_raw == "True"), ("partial", r.flag_partial == "True")) if on),
        }
        for r in flagged.itertuples(index=False)
    ]


def _flagged_block_rows(pcs: pd.DataFrame, variables: list[str]) -> list[dict]:
    """The flagged block-PC rows of ``block_pcs.csv`` in the order ``diagnostics.md`` lists them (by |rho|)."""
    flagged = pcs[(pcs["flag_raw"] == "True") | (pcs["flag_partial"] == "True")].copy()
    if not len(flagged):
        return []
    rho = pd.to_numeric(flagged["spearman"].replace("", np.nan))
    partial = pd.to_numeric(flagged["partial_spearman"].replace("", np.nan))
    flagged["abs"] = rho.abs().fillna(partial.abs())
    flagged["b"] = flagged["block"].map({b: i for i, b in enumerate(EXPORT_BLOCKS)})
    flagged["v"] = flagged["variable"].map({v: i for i, v in enumerate(variables)})
    flagged = flagged.sort_values(["abs", "b", "component", "v"], ascending=[False, True, True, True])
    return [
        {
            "row": f"{r.block} {r.component} · {r.variable}", "block": r.block, "component": r.component,
            "variance share": _num(r.variance_share, ".3f"), "variable": f"`{r.variable}`", "source": r.source, "n": r.n,
            "rho": _num(r.spearman, ".3f"), "rho | design": _num(r.partial_spearman, ".3f"),
            "flag": "+".join(f for f, on in (("raw", r.flag_raw == "True"), ("partial", r.flag_partial == "True")) if on),
        }
        for r in flagged.itertuples(index=False)
    ]


def _components_rows(components: pd.DataFrame) -> tuple[list[dict], list[str]]:
    """The rows of ``components.csv`` as ``diagnostics.md`` prints them, with the table's columns."""
    share_cols = [c for c in components.columns if c.startswith("loading_share_")]
    columns = ["component", "sd", *(f"share {c.removeprefix('loading_share_')}" for c in share_cols),
               "flagged raw", "flagged partial", "top variable", "top rho"]
    rows = []
    for r in components.to_dict("records"):
        rows.append({
            "component": r["component"], "sd": _num(r["sd"], ".4g"),
            **{f"share {c.removeprefix('loading_share_')}": _num(r[c], ".3f") for c in share_cols},
            "flagged raw": r["n_flagged_raw"], "flagged partial": r["n_flagged_partial"],
            "top variable": f"`{r['top_variable']}`" if r["top_variable"] else "n/a", "top rho": _num(r["top_spearman"], ".3f"),
        })
    return rows, columns


def _flagged_components(manifest: dict, components: pd.DataFrame, *, start: int = 0) -> str:
    """A diagnostics run's flagged components as text (``none`` without one), from the ``start``-th component on.

    A component is flagged when ``counts.per_component`` records flagged
    variables for it. The components are listed in the order of the run's
    ``components.csv`` (MOTCO's order), never in the manifest's, which is
    written with sorted keys (``pls_10`` before ``pls_2``; design D7 of
    ``adni-report-rank-sweep``); ``start`` selects by that order only.
    """
    per = manifest.get("counts", {}).get("per_component", {})
    names = [c for c in list(dict.fromkeys(components["component"]))[start:] if (per.get(c) or {}).get("flagged_variables")]
    return ", ".join(f"`{c}`" for c in names) if names else "none"


def _section_ref(title: str) -> str:
    """``section <n>``: the 1-based place of ``title`` in ``REPORT_SECTIONS``, so no section number in the text is a literal."""
    return f"section {REPORT_SECTIONS.index(title) + 1}"


def _diagnostics_section(b: _ReportBuilder, tables: dict, manifest: dict, *, prefix: str = "") -> None:
    """The flagged rows, the components table and the block PCs of one diagnostics run (the primary's, the arm's or a variant's)."""
    counts = manifest.get("counts", {})
    variables = [v["name"] if isinstance(v, dict) else v for v in manifest.get("settings", {}).get("DIAGNOSTIC_VARIABLES", [])]
    threshold = manifest.get("settings", {}).get("DIAGNOSTIC_CORRELATION_THRESHOLD")
    flagged = counts.get("flagged", {})
    b.para(
        f"Rows with |rho| ≥ {threshold} (`DIAGNOSTIC_CORRELATION_THRESHOLD`, raw and partial separately) are flagged: a "
        "reporting threshold, not an adoption rule; no p-value is attached to any correlation. Flagged rows recorded: "
        f"latent components {_count(flagged.get('axis_raw'))} raw and {_count(flagged.get('axis_partial'))} partial; block "
        f"principal components {_count(flagged.get('block_pcs_raw'))} raw and {_count(flagged.get('block_pcs_partial'))} partial."
    )
    axis_rows = _flagged_axis_rows(tables["axis"], variables)
    axis_columns = ["row", "component", "sd", "variable", "source", "n", "rho", "rho | design", "flag"]
    b.table(f"{prefix}Flagged latent components", axis_rows, axis_columns, align="llrllrrrl")
    if not axis_rows:
        b.para(f"No latent-component correlation reaches |rho| ≥ {threshold}.")
    pc_rows = _flagged_block_rows(tables["block_pcs"], variables)
    pc_columns = ["row", "block", "component", "variance share", "variable", "source", "n", "rho", "rho | design", "flag"]
    b.table(f"{prefix}Flagged block principal components", pc_rows, pc_columns, align="lllrllrrrl")
    if not pc_rows:
        b.para(f"No block principal component correlation reaches |rho| ≥ {threshold}.")
    comp_rows, comp_columns = _components_rows(tables["components"])
    b.para(
        "Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights "
        "on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw "
        "and on the partial correlation, and the variable with the largest |rho|."
    )
    b.table(f"{prefix}Components", comp_rows, comp_columns, align="lr" + "r" * (len(comp_columns) - 6) + "rrlr")
    block_rows = []
    blocks = counts.get("blocks", {})
    for block in sorted(blocks, key=lambda x: (EXPORT_BLOCKS.index(x) if x in EXPORT_BLOCKS else len(EXPORT_BLOCKS), x)):
        info = blocks[block]
        shares = info.get("variance_shares", {})
        pc1 = info.get("pc1_phase", {})
        block_rows.append({
            "block": block, "features": _count(info.get("features")),
            **{f"variance share {pc}": _num(shares.get(pc), ".3f") for pc in shares},
            "pc1 against phase: Spearman (here)": _num(pc1.get("spearman"), ".3f"),
            "|Pearson| recorded by export": _num(pc1.get("export_abs_corr_pearson"), ".3f"),
        })
    block_columns = list(block_rows[0]) if block_rows else ["block"]
    b.para(
        "Per z-scored block: the variance share of each of its first principal components and its pc1 against `phase` "
        "(Spearman here; the export manifest's |Pearson| of the first left-singular vector against the ADNI1 indicator, "
        "`counts.phase_offset.<block>.abs_corr_pc1_phase`)."
    )
    b.table(f"{prefix}Block principal components", block_rows, block_columns, align="l" + "r" * (len(block_columns) - 1))
    rows = counts.get("rows", {})
    b.para(
        f"The full tables are referenced by hash ({_section_ref('Provenance')}): "
        + ", ".join(f"`{name}` ({_count(rows.get(key))} rows)" for name, key in (
            (DIAGNOSTICS_AXIS_CORRELATIONS, "axis_correlations"), (DIAGNOSTICS_BLOCK_PCS, "block_pcs"),
            (DIAGNOSTICS_GEOMETRY_SHARES, "geometry_shares"), (DIAGNOSTICS_COMPONENTS, "components")))
        + "."
    )


def _first_component_rows(analyses: list[tuple[str, dict]]) -> list[dict]:
    """Each analysis' first latent component against ``phase``, read from its ``axis_correlations.csv``."""
    rows = []
    for label, tables in analyses:
        axis = tables["axis"]
        comps = list(dict.fromkeys(axis["component"]))
        sub = axis[(axis["component"] == comps[0]) & (axis["variable"] == "phase")] if comps else axis.iloc[0:0]
        r = sub.iloc[0] if len(sub) else None
        rows.append({
            "analysis": label, "component": comps[0] if comps else "n/a", "sd": _num(r["component_sd"], ".4g") if r is not None else "n/a",
            "rho with phase": _num(r["spearman"], ".3f") if r is not None else "n/a",
            "rho | design": _num(r["partial_spearman"], ".3f") if r is not None else "n/a",
            "flag": ("+".join(f for f, on in (("raw", r["flag_raw"] == "True"), ("partial", r["flag_partial"] == "True")) if on) or "none") if r is not None else "n/a",
        })
    return rows


#: The rule of a rule set that reads its variant against the primary only,
#: cited in the lead of that rule set's group of "Export sensitivity" (design
#: D3 of ``adni-report-nmr-all-columns``). ``EXPORT_VARIANT_READING_RULES``
#: has none: its rule 5 defines how a difference between its two variants is
#: read.
_GROUP_PRIMARY_ONLY_RULE: dict[str, int] = {"NMR_MEMBERSHIP_READING_RULES": 8}


def _export_variant_groups(variants: Sequence[str]) -> list[list[str]]:
    """The variants grouped by the rule set ``EXPORT_VARIANT_RULE_SETS`` names for each, in the order each rule set first appears (design D2 of ``adni-report-nmr-all-columns``)."""
    groups: dict[str, list[str]] = {}
    for v in variants:
        groups.setdefault(EXPORT_VARIANT_RULE_SETS[v]["rules"], []).append(v)
    return list(groups.values())


def _and_join(items: Sequence[str]) -> str:
    """``a``, ``a and b``, ``a, b and c``."""
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _export_sensitivity_section(b: _ReportBuilder, inputs: dict, *, stages: list[str], p_status: dict) -> None:
    """The "Export sensitivity" section: the primary beside every variant of ``REPORT_EXPORT_VARIANTS`` (design D4 of ``adni-report-variants``).

    The variants are grouped by their rule set (``_export_variant_groups``;
    design D2 of ``adni-report-nmr-all-columns``): the run-handling group
    (``nist_bridge``, ``per_run_standardized``, ``EXPORT_VARIANT_READING_RULES``)
    and the membership group (``nmr_all_columns``,
    ``NMR_MEMBERSHIP_READING_RULES``). A section lead names the groups when
    the pin holds more than one. Each group has its lead, then its tables,
    which hold the primary and that group's variants only: the first group's
    under the titles of the report of 2026-10-31, a later group's prefixed
    by its variant names (``nmr_all_columns: Statistics: primary and
    variant``). Every word that depends on the variant (its rule set,
    citation word, dependence label and what it changes and keeps) comes
    from ``_variant_words``; the lead of a rule set with a rule that reads
    its variant against the primary only cites it
    (``_GROUP_PRIMARY_ONLY_RULE``).

    Every value is read from a variant's ``export_sensitivity.csv``, its
    comparison and export manifests, its ``result.json``, ``nist_bridge.csv``
    and its diagnostics files; a group's primary rows from its first
    variant's ``export_sensitivity.csv`` (the chain checked that every
    comparison references the primary's record now on disk). The status
    sentences are ``_export_variant_status_line`` and the variant lines
    ``_export_variant_lines``, string-equal to each ``export_sensitivity.md``.
    The counts table leaves out the keys the steps compare themselves:
    ``analysis`` (``export-sensitivity``), ``phase_offset`` (the run-offset
    table) and ``diagnostics`` (``axis-diagnostics``).
    """
    dirs, manifests = inputs["dirs"], inputs["manifests"]
    primary, records = inputs["records"]["primary"], inputs["records"]["variants"]
    variants = list(REPORT_EXPORT_VARIANTS)
    groups = _export_variant_groups(variants)
    labels = {v: _variant_labels(v) for v in variants}
    rows = {v: {r["analysis"]: r for r in inputs["tables"]["variants"][v]["comparison"].to_dict("records")} for v in variants}
    v_rows = {v: rows[v][v] for v in variants}
    statuses = {v: manifests[labels[v]["comparison"]].get("counts", {}).get("statuses", {}) for v in variants}
    v_status = {v: {s: _rejected(records[v]["p_values"].get(s)) for s in ANALYSIS_STATISTICS} for v in variants}
    rules = _section_ref("Reading rules")
    ref_files = manifests[labels[variants[0]]["comparison"]].get("reference", {}).get("files", {})
    primary_text = f"The primary (`{dirs['analysis']}`, `{ANALYSIS_RESULT}` sha256 `{ref_files.get(ANALYSIS_RESULT, {}).get('sha256')}`)"
    if len(groups) > 1:
        b.para(
            f"{primary_text} beside its predeclared export variants (`EXPORT_VARIANTS`), in one group per rule set "
            "(`EXPORT_VARIANT_RULE_SETS`), in registry order: "
            + "; ".join(
                _and_join([f"`{v}`" for v in group]) + f" under `{_variant_words(group[0])['rules']}`" for group in groups
            )
            + f" ({rules}). Each group's tables hold the primary and that group's variants only, the primary row first and "
            "its status the result."
        )
    e_manifest = manifests["export"]
    for k, group in enumerate(groups):
        words, one = _variant_words(group[0]), len(group) == 1
        cite = words["cite"]
        a_variant, each = ("the variant", "the variant") if one else ("a variant", "each variant")
        if k == 0:
            prefix, noun, counts_title = "", "variants", "Variant exports against the predeclared counts"
        else:
            prefix, noun = ", ".join(group) + ": ", "variant" if one else "variants"
            counts_title = f"{prefix}Export{'' if one else 's'} against the predeclared counts"
        p_row = rows[group[0]]["primary"]
        clauses = [f"{a_variant} never replaces it ({cite} 1)", f"a status that differs is {words['dependence']} ({cite} 2)"]
        if words["rules"] in _GROUP_PRIMARY_ONLY_RULE:
            clauses.append(f"the variant is read against the primary only ({cite} {_GROUP_PRIMARY_ONLY_RULE[words['rules']]})")
        b.para(
            (primary_text if len(groups) == 1 else "The primary")
            + f" beside its predeclared export {noun} (`EXPORT_VARIANTS`): "
            + "; ".join(
                f"`{v}` (change `{EXPORT_VARIANTS[v]['change']}`: {EXPORT_VARIANTS[v]['setting']}; `{dirs[_variant_role(v, 'analysis')].parent}`)"
                for v in group
            )
            + f". Every other export and analysis setting is the primary's. Every table "
            + ("in this section" if len(groups) == 1 else "of this group")
            + f" quotes {a_variant} and is read under `READING_RULES` and `{words['rules']}` ({rules}): the primary row "
            "comes first and its status is the result; " + ", ".join(clauses[:-1]) + ", and " + clauses[-1] + "."
        )
        stat_rows = []
        for s in ANALYSIS_STATISTICS:
            for label, row in (("primary", p_row), *((v, v_rows[v]) for v in group)):
                stat_rows.append({
                    "row": f"{s} {label}", "statistic": s, "analysis": label, "observed": _num(row[f"{s}_observed"]),
                    "p (RRPP)": _num(row[f"{s}_p"]), "rejected": _yes_no(row[f"{s}_rejected"]),
                    "null mean": _num(row[f"{s}_null_mean"]), "null sd": _num(row[f"{s}_null_sd"]), "null q95": _num(row[f"{s}_null_q95"]),
                    "status": "the result" if label == "primary" else _text(statuses[label].get(s)),
                })
        b.table(f"{prefix}Statistics: primary and {noun}", stat_rows, ["row", "statistic", "analysis", "observed", "p (RRPP)", "rejected", "null mean", "null sd", "null q95", "status"], align="lllrrlrrrl")
        for v in group:
            v_row = v_rows[v]
            b.para(
                f"`angle` (degrees, endpoint stages {stages[0]} and {stages[-1]}) is read beside each analysis' CV-selected "
                f"rank, floor, eigengap and null summary (reading rule 2, {cite} 3): primary rank {_count(p_row['selected_rank'])} "
                f"(floor {ANALYSIS_RANK_FLOOR}, pooled relative eigengap {_num(p_row['eigengap'])}); {v} rank "
                f"{_count(v_row['selected_rank'])} (floor {ANALYSIS_RANK_FLOOR}, eigengap {_num(v_row['eigengap'])})"
                + (
                    f"; the ranks differ, which is reported, not ranked ({cite} 3)."
                    if p_row["selected_rank"] != v_row["selected_rank"] else "; the ranks are equal."
                )
            )
        for v in group:
            b.heading(f"Status per statistic: `{v}`")
            b.bullets([
                _export_variant_status_line(s, statuses[v].get(s, "n/a"), p_status[s], v_status[v][s], v) for s in ANALYSIS_STATISTICS
            ])
        perms = {
            "primary": primary.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {},
            **{v: records[v].get("config_spectrum", {}).get("permutation_pooled_eigengap") or {} for v in group},
        }
        all_rows = {"primary": p_row, **{v: v_rows[v] for v in group}}
        space_rows = [
            {"quantity": "PLS-DA rank (selection)", **{c: f"{_count(r['selected_rank'])} (`{r['component_selection']}`)" for c, r in all_rows.items()}},
            {"quantity": "rank floor (`ANALYSIS_RANK_FLOOR`)", **{c: str(ANALYSIS_RANK_FLOOR) for c in all_rows}},
            {"quantity": "cv_mean_auroc", **{c: _num(r["cv_mean_auroc"]) for c, r in all_rows.items()}},
            {"quantity": "CV repeats completed", **{c: _count(r["cv_repeats_completed"]) for c, r in all_rows.items()}},
            {"quantity": "pooled relative eigengap", **{c: _num(r["eigengap"]) for c, r in all_rows.items()}},
            {"quantity": "eigengap permutation null q05 / q50 / q95",
             **{c: f"{_fmt(q.get('q05'))} / {_fmt(q.get('q50'))} / {_fmt(q.get('q95'))}" for c, q in perms.items()}},
        ]
        b.table(f"{prefix}Latent space: primary and {noun}", space_rows, ["quantity", *all_rows], align="l" + "r" * len(all_rows))
        b.para(
            f"{each.capitalize()} shares with the primary the cleaned tables, the participants, {words['kept']}, the covariates and "
            "their design, the cells, the settings, the CV folds, the seed and the permutations; it differs only in "
            f"{words['changes']} ({cite} 2)."
        )
        exports = {"primary": e_manifest, **{v: manifests[labels[v]["export"]] for v in group}}
        offset_rows = []
        for p in e_manifest.get("settings", {}).get("blocks", EXPORT_BLOCKS):
            for label, m in exports.items():
                o = m.get("counts", {}).get("phase_offset", {}).get(p, {})
                e = m.get("expected", {}).get("phase_offset", {}).get(p, {})
                offset_rows.append({
                    "row": f"{p} {label}", "block": p, "export": label,
                    "median |d|": _num(o.get("median_abs_d"), ".2f"), "max |d|": _num(o.get("max_abs_d"), ".2f"),
                    "|d| > 0.5": _count(o.get("abs_d_gt_0_5")), "|d| > 1": _count(o.get("abs_d_gt_1")),
                    "|corr(PC1, phase)|": _num(o.get("abs_corr_pc1_phase"), ".2f"), "|corr(PC2, phase)|": _num(o.get("abs_corr_pc2_phase"), ".2f"),
                    "expected |d| > 0.5": _count(e.get("abs_d_gt_0_5")), "expected |d| > 1": _count(e.get("abs_d_gt_1")),
                })
        b.para(
            "The run offset per block (`phase`, ADNI1 against ADNI2GO, on each export's scale over the exported participants), "
            f"as the primary export manifest and {each} export manifest record it "
            "(`counts.phase_offset`), beside the predeclared counts (`EXPORT_EXPECTED_COUNTS`, `EXPORT_VARIANT_EXPECTED_COUNTS`; "
            "`n/a` where none is predeclared):"
        )
        b.table(f"{prefix}Run offset per export", offset_rows, ["row", "block", "export", "median |d|", "max |d|", "|d| > 0.5", "|d| > 1", "|corr(PC1, phase)|", "|corr(PC2, phase)|", "expected |d| > 0.5", "expected |d| > 1"], align="lllrrrrrrrr")
        flat = {v: _flatten(manifests[labels[v]["export"]].get("counts", {})) for v in group}
        flat_e = {v: _flatten(manifests[labels[v]["export"]].get("expected", {})) for v in group}
        keys = dict.fromkeys(
            key for v in group
            for key in _flatten({
                name: value for name, value in EXPORT_VARIANT_EXPECTED_COUNTS[v].items()
                if name not in ("analysis", "phase_offset", "diagnostics")
            })
        )
        count_rows = [
            {"quantity": key, **{c: _text(src[v].get(key)) for v in group for c, src in ((v, flat), (f"{v} expected", flat_e))}}
            for key in keys
        ]
        compared = "the analysis', which `export-sensitivity` compares itself"
        if any("diagnostics" in EXPORT_VARIANT_EXPECTED_COUNTS[v] for v in group):
            compared += ", and the diagnostics', which `axis-diagnostics` compares"
        b.para(
            f"{each.capitalize()} export's counts beside its predeclared ones (`EXPORT_VARIANT_EXPECTED_COUNTS`, every key but the run "
            f"offset above and {compared}; a deviation is copied under {_section_ref('Findings')}), as its export manifest "
            "records them (`counts`, `expected`):"
        )
        b.table(counts_title, count_rows, ["quantity", *(c for v in group for c in (v, f"{v} expected"))], align="l" + "r" * (2 * len(group)))
        for v in group:
            m = manifests[labels[v]["export"]]
            b.heading(f"Export variant `{v}`")
            b.para(*_export_variant_lines(m))
            bridge = m.get("bridge")
            if not bridge:
                continue
            observed, expected = bridge.get("summary", {}).get("p180_bridged", {}), m.get("expected", {}).get("p180_bridged", {})
            b.table(f"{v}: NIST bridge per kit", [
                {"kit": "not bridged" if kit == "not_bridged" else kit, "metabolites": _count(observed.get(kit)), "expected": _count(expected.get(kit))}
                for kit in dict.fromkeys([*observed, *expected])
            ], ["kit", "metabolites", "expected"], align="lrr")
            rule = bridge.get("rule", {})
            runs = [rule.get("reference_run"), rule.get("bridged_run")]
            table = inputs["tables"]["variants"][v]["bridge"]
            unbridged = table[table["bridged"] == "False"]
            b.table(f"{v}: Unbridged metabolites", [
                {
                    "metabolite": f"`{r['metabolite']}`", "kit": r["kit"], "NIST column": _text(r["nist_column"]),
                    **{f"{c} {run}": _count(r[f"{key}_{run}"]) for run in runs for c, key in (("replicates", "replicates"), ("valid", "valid"), ("ISTD flags", "istd_flags"))},
                    "b": _num(r["b"], "+.3f"),
                }
                for r in unbridged.to_dict("records")
            ], ["metabolite", "kit", "NIST column", *(f"{c} {run}" for run in runs for c in ("replicates", "valid", "ISTD flags")), "b"], align="lll" + "r" * (3 * len(runs) + 1))
            info = bridge.get("table", {})
            b.para(
                f"Each unbridged metabolite keeps factor {_text(rule.get('unbridged_factor'))} (`NIST_BRIDGE_RULE`: bridged when at "
                f"least {_text(rule.get('inclusion_share'))} of its replicates are valid in each run). The full table `{info.get('name')}` "
                f"(sha256 `{info.get('sha256')}`, {_count(info.get('rows'))} rows) is referenced by hash ({_section_ref('Provenance')}); "
                "the factor of every metabolite is in the variant export manifest (`bridge.factors_log2`)."
            )
        for v in group:
            d_manifest = manifests[labels[v]["diagnostics"]]
            b.para(
                f"Axis diagnostics of `{v}` (`{dirs[_variant_role(v, 'diagnostics')]}`, rank "
                f"{_count(d_manifest.get('counts', {}).get('components'))}, `is_primary` "
                f"{_text(d_manifest.get('inputs', {}).get('analysis', {}).get('is_primary'))}, export variant "
                f"`{_text(d_manifest.get('inputs', {}).get('analysis', {}).get('export_variant'))}`): a component of the variant "
                "that tracks a variable here is a measurement-space finding about the variant; it never reinterprets either "
                f"analysis' statistics and is never grounds to adopt the variant ({_variant_words(v)['cite']} 7)."
            )
            _diagnostics_section(b, inputs["tables"]["variants"][v]["diagnostics"], d_manifest, prefix=f"{v}: ")
        b.table(f"{prefix}First component against phase", _first_component_rows([
            ("primary", inputs["tables"]["diagnostics"]), *((v, inputs["tables"]["variants"][v]["diagnostics"]) for v in group)
        ]), ["analysis", "component", "sd", "rho with phase", "rho | design", "flag"], align="llrrrl")
        for v in group:
            settings = manifests[labels[v]["analysis"]].get("settings", {})
            b.para(
                f"The `motco analyze` command that reproduces `{v}`'s analysis directory (`cli_equivalent`; "
                + _text(settings.get("cli_equivalent", {}).get("note")) + "):"
            )
            b.code(_text(settings.get("cli_equivalent", {}).get("command")))


def _stage_sensitivity_section(b: _ReportBuilder, inputs: dict, *, stages: list[str], p_status: dict) -> None:
    """The "Stage-definition sensitivity" section: the primary beside the CN / LMCI / AD arm (design D4 of ``adni-report-stage-arm``).

    Every value is read from the arm's ``stage_sensitivity.csv``, its
    comparison, analysis and export manifests, the primary export manifest,
    the two ``result.json`` and the arm's diagnostics files (the chain
    checked that the comparison references the primary's record now on
    disk). The status sentences are ``_stage_arm_status_line``, the arm's
    bullets the ones ``_stage_arm_lines`` writes and its four definition
    tables ``_stage_arm_tables``, string-equal to ``stage_sensitivity.md``;
    the arm is read against the primary only (stage-arm rule 8).
    """
    dirs, manifests, paths = inputs["dirs"], inputs["manifests"], inputs["manifest_paths"]
    primary, record = inputs["records"]["primary"], inputs["records"]["stage_arm"]
    labels = _STAGE_ARM_LABELS
    name = STAGE_SENSITIVITY_ARM["name"]
    e_manifest, a_manifest = manifests[labels["export"]], manifests[labels["analysis"]]
    cmp_manifest, d_manifest = manifests[labels["comparison"]], manifests[labels["diagnostics"]]
    arm = e_manifest["stage_arm"]
    rows = {r["analysis"]: r for r in inputs["tables"]["stage_arm"]["comparison"].to_dict("records")}
    p_row, a_row = rows["primary"], rows[name]
    statuses = cmp_manifest.get("counts", {}).get("statuses", {})
    a_status = {s: _rejected(record["p_values"].get(s)) for s in ANALYSIS_STATISTICS}
    rules = _section_ref("Reading rules")
    ref_files = cmp_manifest.get("reference", {}).get("files", {})
    b.para(
        f"The primary (`{dirs['analysis']}`, `{ANALYSIS_RESULT}` sha256 `{ref_files.get(ANALYSIS_RESULT, {}).get('sha256')}`) beside "
        f"the CN / LMCI / AD arm `{name}` (`STAGE_SENSITIVITY_ARM`, change `{arm['change']}`: {_stage_arm_definition(arm)}; every "
        f"other export and analysis setting the primary's; `{dirs[_stage_arm_role('analysis')]}`, `{ANALYSIS_RESULT}` sha256 "
        f"`{a_manifest.get('outputs', {}).get(ANALYSIS_RESULT, {}).get('sha256')}` as its `{ANALYSIS_MANIFEST}` records it), as "
        f"`{paths[labels['comparison']]}` records them. Every table in this section quotes the arm and is read under "
        f"`READING_RULES` and `STAGE_SENSITIVITY_READING_RULES` ({rules}): the primary row comes first and its status is the "
        "result; the arm never replaces it (stage-arm rule 1), a status that differs is dependence on the stage definition "
        "and the sample (stage-arm rule 2), and the arm is read against the primary only (stage-arm rule 8)."
    )
    stat_rows = []
    for s in ANALYSIS_STATISTICS:
        for label, row in (("primary", p_row), (name, a_row)):
            stat_rows.append({
                "row": f"{s} {label}", "statistic": s, "analysis": label, "observed": _num(row[f"{s}_observed"]),
                "p (RRPP)": _num(row[f"{s}_p"]), "rejected": _yes_no(row[f"{s}_rejected"]),
                "null mean": _num(row[f"{s}_null_mean"]), "null sd": _num(row[f"{s}_null_sd"]), "null q95": _num(row[f"{s}_null_q95"]),
                "status": "the result" if label == "primary" else _text(statuses.get(s)),
            })
    b.table("Statistics: primary and arm", stat_rows, ["row", "statistic", "analysis", "observed", "p (RRPP)", "rejected", "null mean", "null sd", "null q95", "status"], align="lllrrlrrrl")
    b.para(
        f"`angle` (degrees, endpoint stages {stages[0]} and {stages[-1]}) is read beside each analysis' CV-selected rank, "
        f"floor, eigengap and null summary (reading rule 2, stage-arm rule 3): primary rank {_count(p_row['selected_rank'])} "
        f"(floor {ANALYSIS_RANK_FLOOR}, pooled relative eigengap {_num(p_row['eigengap'])}); {name} rank "
        f"{_count(a_row['selected_rank'])} (floor {ANALYSIS_RANK_FLOOR}, eigengap {_num(a_row['eigengap'])})"
        + (
            "; the ranks differ, which is reported, not ranked (stage-arm rule 3)."
            if p_row["selected_rank"] != a_row["selected_rank"] else "; the ranks are equal."
        )
    )
    b.para("Status per statistic:")
    b.bullets([_stage_arm_status_line(s, statuses.get(s, "n/a"), p_status[s], a_status[s]) for s in ANALYSIS_STATISTICS])
    p_perm = primary.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {}
    a_perm = record.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {}
    space_rows = [
        {"quantity": "participants", "primary": _count(p_row["participants"]), name: _count(a_row["participants"])},
        {"quantity": "PLS-DA rank (selection)", "primary": f"{_count(p_row['selected_rank'])} (`{p_row['component_selection']}`)", name: f"{_count(a_row['selected_rank'])} (`{a_row['component_selection']}`)"},
        {"quantity": "rank floor (`ANALYSIS_RANK_FLOOR`)", "primary": str(ANALYSIS_RANK_FLOOR), name: str(ANALYSIS_RANK_FLOOR)},
        {"quantity": "cv_mean_auroc", "primary": _num(p_row["cv_mean_auroc"]), name: _num(a_row["cv_mean_auroc"])},
        {"quantity": "CV repeats completed", "primary": _count(p_row["cv_repeats_completed"]), name: _count(a_row["cv_repeats_completed"])},
        {"quantity": "pooled relative eigengap", "primary": _num(p_row["eigengap"]), name: _num(a_row["eigengap"])},
        {"quantity": "eigengap permutation null q05 / q50 / q95",
         "primary": f"{_fmt(p_perm.get('q05'))} / {_fmt(p_perm.get('q50'))} / {_fmt(p_perm.get('q95'))}",
         name: f"{_fmt(a_perm.get('q05'))} / {_fmt(a_perm.get('q50'))} / {_fmt(a_perm.get('q95'))}"},
    ]
    b.table("Latent space: primary and arm", space_rows, ["quantity", "primary", name], align="lrr")
    b.heading(f"Arm `{name}`")
    b.bullets([line[2:] for line in _stage_arm_lines(e_manifest) if line.startswith("- ")])
    titles = ["Exported participants by `dx_bl`", "Sex × stage cells", "Runs within each stage", "Covariate levels"]
    for title, (header, align, table_rows) in zip(titles, _stage_arm_tables(e_manifest)):
        b.table(f"{name}: {title}", [dict(zip(header, r)) for r in table_rows], header, align=align)
    e_primary = manifests["export"]
    exports = {"primary": e_primary, name: e_manifest}
    offset_rows = []
    for block in e_primary.get("settings", {}).get("blocks", EXPORT_BLOCKS):
        for label, m in exports.items():
            o = m.get("counts", {}).get("phase_offset", {}).get(block, {})
            e = m.get("expected", {}).get("phase_offset", {}).get(block, {})
            offset_rows.append({
                "row": f"{block} {label}", "block": block, "export": label,
                "median |d|": _num(o.get("median_abs_d"), ".2f"), "max |d|": _num(o.get("max_abs_d"), ".2f"),
                "|d| > 0.5": _count(o.get("abs_d_gt_0_5")), "|d| > 1": _count(o.get("abs_d_gt_1")),
                "|corr(PC1, phase)|": _num(o.get("abs_corr_pc1_phase"), ".2f"), "|corr(PC2, phase)|": _num(o.get("abs_corr_pc2_phase"), ".2f"),
                "expected |d| > 0.5": _count(e.get("abs_d_gt_0_5")), "expected |d| > 1": _count(e.get("abs_d_gt_1")),
            })
    b.para(
        "The run offset per block (`phase`, ADNI1 against ADNI2GO, on the primary's scale and floors), over the primary's "
        "exported participants as the primary export manifest records it and over the arm's rows as the arm export manifest "
        "records it (`counts.phase_offset`), beside the predeclared counts (`EXPORT_EXPECTED_COUNTS`, "
        "`STAGE_SENSITIVITY_EXPECTED_COUNTS`; `n/a` where none is predeclared):"
    )
    b.table("Run offset: primary and arm", offset_rows, ["row", "block", "export", "median |d|", "max |d|", "|d| > 0.5", "|d| > 1", "|corr(PC1, phase)|", "|corr(PC2, phase)|", "expected |d| > 0.5", "expected |d| > 1"], align="lllrrrrrrrr")
    flat, flat_e = _flatten(e_manifest.get("counts", {})), _flatten(e_manifest.get("expected", {}))
    keys = dict.fromkeys(
        k for src in (STAGE_SENSITIVITY_EXPECTED_COUNTS["export"], e_manifest.get("expected", {}))
        for k in _flatten({key: value for key, value in src.items() if key != "phase_offset"})
    )
    b.para(
        "The arm export's counts beside its predeclared ones (`STAGE_SENSITIVITY_EXPECTED_COUNTS`, every key of its "
        "`export` entry but the run offset above; the analysis' and the diagnostics' entries are compared by their steps, "
        f"and a deviation is copied under {_section_ref('Findings')}), as its export manifest records them (`counts`, "
        "`expected`):"
    )
    b.table("Arm export against the predeclared counts", [
        {"quantity": key, "observed": _text(flat.get(key)), "expected": _text(flat_e.get(key))} for key in keys
    ], ["quantity", "observed", "expected"], align="lrr")
    d_analysis = d_manifest.get("inputs", {}).get("analysis", {})
    b.para(
        f"Axis diagnostics of `{name}` (`{dirs[_stage_arm_role('diagnostics')]}`, rank "
        f"{_count(d_manifest.get('counts', {}).get('components'))}, `is_primary` {_text(d_analysis.get('is_primary'))}, "
        f"stage arm `{_text(d_analysis.get('stage_arm'))}`): a component of the arm that tracks a variable here is a "
        "measurement-space finding about the arm; it never reinterprets either analysis' statistics and is never grounds "
        "to adopt the arm, and in the arm `dx_bl` orders the participants as `stage` does, so their correlations coincide "
        "(stage-arm rule 7)."
    )
    _diagnostics_section(b, inputs["tables"]["stage_arm"]["diagnostics"], d_manifest, prefix=f"{name}: ")
    b.table("First component against phase", _first_component_rows([
        ("primary", inputs["tables"]["diagnostics"]), (name, inputs["tables"]["stage_arm"]["diagnostics"])
    ]), ["analysis", "component", "sd", "rho with phase", "rho | design", "flag"], align="llrrrl")
    settings = a_manifest.get("settings", {})
    b.para(
        f"The `motco analyze` command that reproduces `{name}`'s analysis directory (`cli_equivalent`; "
        + _text(settings.get("cli_equivalent", {}).get("note")) + "):"
    )
    b.code(_text(settings.get("cli_equivalent", {}).get("command")))


def _rank_sensitivity_section(b: _ReportBuilder, inputs: dict, *, stages: list[str], p_status: dict) -> None:
    """The "Rank sensitivity" section: the primary beside every forced rank of ``RANK_SENSITIVITY_LADDER`` (design D4 of ``adni-report-rank-sweep``).

    Every value is read from ``rank_sensitivity.csv``, the comparison
    manifest, each rank's ``result.json`` and analysis manifest and the top
    rank's diagnostics files (the chain checked that the comparison
    references the primary's record and every rank's files now on disk).
    The status sentences are ``_rank_status_line``, the anchor and nesting
    bullets ``_rank_anchor_lines`` and the nesting table
    ``_rank_nesting_table``, string-equal to ``rank_sensitivity.md``; the
    sweep is read against the primary only (sweep rule 8), and no value
    across ranks is computed (sweep rule 6).
    """
    dirs, manifests, paths = inputs["dirs"], inputs["manifests"], inputs["manifest_paths"]
    primary, records = inputs["records"]["primary"], inputs["records"]["ranks"]
    ranks = [int(k) for k in RANK_SENSITIVITY_LADDER["ranks"]]
    top = max(ranks)
    names = {k: _rank_dir_name(k) for k in ranks}
    cmp_label = _RANK_SWEEP_LABELS["comparison"]
    cmp_manifest, d_manifest = manifests[cmp_label], manifests[_RANK_SWEEP_LABELS["diagnostics"]]
    ladder = cmp_manifest.get("settings", {}).get("RANK_SENSITIVITY_LADDER", {})
    counts = cmp_manifest.get("counts", {})
    statuses = counts.get("statuses", {})
    rows = {r["analysis"]: r for r in inputs["tables"]["rank_sweep"]["comparison"].to_dict("records")}
    p_row = rows["primary"]
    p_rank = primary["latent"]["selected_lv"]
    r_status = {k: {s: _rejected(records[k]["p_values"].get(s)) for s in ANALYSIS_STATISTICS} for k in ranks}
    rules = _section_ref("Reading rules")
    ref_files = cmp_manifest.get("reference", {}).get("files", {})
    b.para(
        f"The primary (`{dirs['analysis']}`, `{ANALYSIS_RESULT}` sha256 `{ref_files.get(ANALYSIS_RESULT, {}).get('sha256')}`, "
        f"rank {p_rank} selected by its cross-validation) beside the rank sweep `{ladder.get('name')}` "
        f"(`RANK_SENSITIVITY_LADDER`, change `{ladder.get('change')}`: the primary's analysis at each forced rank "
        + ", ".join(str(k) for k in ladder.get("ranks", [])) + f", `{ladder.get('setting')}` set to the rank and MOTCO's "
        f"cross-validation skipped; {ladder.get('draws')}; every other export and analysis setting the primary's; "
        f"`{dirs[_rank_sweep_role('comparison')].parent}`), as `{paths[cmp_label]}` records them. Every table in this "
        f"section quotes the sweep and is read under `READING_RULES` and `RANK_SENSITIVITY_READING_RULES` ({rules}): the "
        "primary row comes first and its status is the result; no rank is chosen, adopted or ranked (sweep rule 1), a "
        "status that differs is rank dependence (sweep rule 2), the sweep is not a test (sweep rule 6), and it is read "
        "against the primary only (sweep rule 8)."
    )
    stat_rows = []
    for s in ANALYSIS_STATISTICS:
        for label, row in (("primary", p_row), *((names[k], rows[names[k]]) for k in ranks)):
            stat_rows.append({
                "row": f"{s} {label}", "statistic": s, "analysis": label, "rank": _count(row["selected_rank"]),
                "observed": _num(row[f"{s}_observed"]), "p (RRPP)": _num(row[f"{s}_p"]), "rejected": _yes_no(row[f"{s}_rejected"]),
                "null mean": _num(row[f"{s}_null_mean"]), "null sd": _num(row[f"{s}_null_sd"]), "null q95": _num(row[f"{s}_null_q95"]),
                "status": "the result" if label == "primary" else _text(statuses.get(label, {}).get(s)),
            })
    b.table("Statistics: primary and ranks", stat_rows, ["row", "statistic", "analysis", "rank", "observed", "p (RRPP)", "rejected", "null mean", "null sd", "null q95", "status"], align="lllrrrlrrrl")
    b.para(
        f"`angle` (degrees, endpoint stages {stages[0]} and {stages[-1]}) is read beside each analysis' rank, floor "
        f"({ANALYSIS_RANK_FLOOR}), eigengap and its own null summary (reading rule 2, sweep rule 4; the latent spaces "
        "below), never against the `angle` of another rank."
    )
    b.para("Status per statistic:")
    b.bullets([
        _rank_status_line(s, p_status[s], {k: (statuses.get(names[k], {}).get(s, "n/a"), r_status[k][s]) for k in ranks})
        for s in ANALYSIS_STATISTICS
    ])
    space_rows = []
    for label, record in (("primary", primary), *((names[k], records[k]) for k in ranks)):
        row = rows[label]
        perm = record.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {}
        space_rows.append({
            "analysis": label, "rank (selection)": f"{_count(row['selected_rank'])} (`{row['component_selection']}`)",
            "rank floor": str(ANALYSIS_RANK_FLOOR), "cv_mean_auroc": _num(row["cv_mean_auroc"]),
            "CV repeats completed": _count(row["cv_repeats_completed"]), "pooled relative eigengap": _num(row["eigengap"]),
            "eigengap null q05 / q50 / q95": f"{_fmt(perm.get('q05'))} / {_fmt(perm.get('q50'))} / {_fmt(perm.get('q95'))}",
            "`angle` null mean / sd / q95": f"{_num(row['angle_null_mean'])} / {_num(row['angle_null_sd'])} / {_num(row['angle_null_q95'])}",
        })
    b.table("Latent space: primary and ranks", space_rows, list(space_rows[0]), align="lrrrrrrr")
    b.para(
        "The ranks share the primary export, the covariates and their design, the cells, the seed and the permutations; "
        f"at n_jobs = {REPORTED_N_JOBS} every rank permutes the same residual indices (sweep rule 2). They differ only in "
        "the latent rank: MOTCO skips the cross-validation at a forced rank, so `cv_mean_auroc` is not available and no "
        "CV repeat runs. Each rank's `pls_loadings.csv` (MOTCO's rotations) is its own and is not nested; it and the "
        f"rank's `{ANALYSIS_STAGE_MEANS}` are recorded by hash in the rank's `{ANALYSIS_MANIFEST}` (`outputs`), whose own "
        f"hash is in {_section_ref('Provenance')}."
    )
    anchor = cmp_manifest.get("anchor", {})
    b.heading("Anchor and nesting")
    b.bullets(_rank_anchor_lines(anchor, top=top, primary_rank=p_rank))
    header, align, nesting_rows = _rank_nesting_table(counts.get("nesting", {}), ranks, top=top)
    b.table("Nesting", [dict(zip(header, r)) for r in nesting_rows], header, align=align)
    expected = cmp_manifest.get("expected", {})
    count_rows = [
        {"quantity": "anchor.rank", "observed": _text(anchor.get("rank")), "expected": _text(expected.get("anchor", {}).get("rank"))},
        {"quantity": "comparison.rows", "observed": _text(counts.get("rows")), "expected": _text(expected.get("comparison", {}).get("rows"))},
    ]
    for k in ranks:
        m = manifests[_RANK_SWEEP_LABELS[k]]
        for key in ("selected_rank", "component_selection", "cv_repeats_completed"):
            count_rows.append({
                "quantity": f"{names[k]}.{key}", "observed": _text(m.get("counts", {}).get(key)),
                "expected": _text(m.get("expected", {}).get(key)),
            })
    b.para(
        "The anchor's rank, the comparison's rows and each rank's selection, rank and CV repeats beside their "
        "predeclared values (`RANK_SENSITIVITY_EXPECTED_COUNTS`), as the comparison manifest (`anchor`, `counts`, "
        "`expected`) and each rank's analysis manifest (`counts`, `expected`) record them; the other keys of "
        "`RANK_SENSITIVITY_EXPECTED_COUNTS` are compared by the steps, and a deviation is copied under "
        f"{_section_ref('Findings')}:"
    )
    b.table("Sweep against the predeclared counts", count_rows, ["quantity", "observed", "expected"], align="lrr")
    d_analysis = d_manifest.get("inputs", {}).get("analysis", {})
    read = d_analysis.get("rank_sweep") or {}
    d_tables = inputs["tables"]["rank_sweep"]["diagnostics"]
    b.para(
        f"Axis diagnostics of the top rank (`{dirs[_rank_sweep_role('diagnostics')]}`, `axis-diagnostics` on "
        f"`{_text(d_analysis.get('dir'))}`, rank {_count(d_manifest.get('counts', {}).get('components'))}, forced rank "
        f"{_text(read.get('forced_rank'))} of the sweep beside the primary's rank {_text(read.get('primary_rank'))}, "
        f"`is_primary` {_text(d_analysis.get('is_primary'))}), the sweep's predeclared diagnostic: PLS-DA components are "
        f"nested, so its components up to the primary's rank are the primary's, with the primary's correlations "
        f"({_section_ref('Axis diagnostics of the primary')}), and a component above it that tracks a variable is a "
        "measurement-space finding about the higher ranks and never grounds to choose a rank (sweep rule 7). Flagged "
        f"components after the primary's first {_text(read.get('primary_rank'))}, in the order of `{DIAGNOSTICS_COMPONENTS}`: "
        f"{_flagged_components(d_manifest, d_tables['components'], start=int(read.get('primary_rank') or 0))}."
    )
    _diagnostics_section(b, d_tables, d_manifest, prefix=f"{names[top]}: ")
    b.table("First component against phase", _first_component_rows([
        ("primary", inputs["tables"]["diagnostics"]), (names[top], d_tables)
    ]), ["analysis", "component", "sd", "rho with phase", "rho | design", "flag"], align="llrrrl")
    commands = {k: manifests[_RANK_SWEEP_LABELS[k]].get("settings", {}).get("cli_equivalent", {}) for k in ranks}
    b.para(
        f"The `motco analyze` commands that reproduce the {len(commands)} rank directories, in ladder order (`cli_equivalent`, "
        f"each with `--forced-components`; " + "; ".join(dict.fromkeys(_text(c.get("note")) for c in commands.values())) + "):"
    )
    b.code(*(_text(c.get("command")) for c in commands.values()))


def render_report(inputs: dict, *, date: str) -> tuple[str, dict[str, pd.DataFrame]]:
    """Render the case-study report from the loaded inputs (design D4 of ``adni-report``, ``adni-report-variants``, ``adni-report-stage-arm`` and ``adni-report-rank-sweep``; D2 to D5 of ``adni-report-nmr-all-columns``).

    Parameters
    ----------
    inputs:
        ``_load_report_inputs``.
    date:
        The date of the report's file name, written in the title line only.

    Returns
    -------
    tuple
        The Markdown text and every table it prints as a frame of strings,
        keyed ``"<section> › <title>"``.

    Notes
    -----
    The thirteen sections of ``REPORT_SECTIONS``, in order, each table titled
    by a level-3 heading and keyed by its first column; every reference to
    another section is numbered from ``REPORT_SECTIONS`` (``_section_ref``).
    Every number is read from a record, a manifest or a CSV and formatted
    with the digits of the summary it belongs to (``_fmt`` with six
    significant digits for record values, p-values as recorded, counts as
    integers, correlations and shares as ``diagnostics.md`` prints them); no
    statistic, correlation, mean or count is computed here, and no value
    across the ranks of the sweep. The reading sentences are
    ``_statistic_reading_line``, ``_arm_status_line``,
    ``_export_variant_status_line``, ``_stage_arm_status_line`` and
    ``_rank_status_line``, the ones ``summary.md``,
    ``latent_sensitivity.md``, ``export_sensitivity.md``,
    ``stage_sensitivity.md`` and ``rank_sensitivity.md`` print; the variant
    lines are ``_export_variant_lines``, the CN / LMCI / AD arm's bullets and
    definition tables are ``_stage_arm_lines`` and ``_stage_arm_tables``,
    and the sweep's anchor and nesting bullets and nesting table are
    ``_rank_anchor_lines`` and ``_rank_nesting_table``; the flagged
    components of a diagnostics run are listed in its ``components.csv``
    order (``_flagged_components``); the reading rules are the constants,
    verbatim. The export variants of ``REPORT_EXPORT_VARIANTS`` are read in
    one group per rule set (``_export_variant_groups``): the preamble names
    each group's rule set, the summary has one paragraph per group (its
    variants, changes, what they change, ranks, dependence label and rule
    set, all from ``_variant_words``) followed by each variant's status
    lines, "Export sensitivity" one group of tables per rule set
    (``_export_sensitivity_section``), and the reading-rules section one
    list per rule set, in group order, after
    ``LATENT_SENSITIVITY_READING_RULES``: six lists with
    ``EXPORT_VARIANT_READING_RULES`` and ``NMR_MEMBERSHIP_READING_RULES``.
    No sentence reads one sensitivity against another; a sentence that
    lists several, each beside the primary, compares none. The body
    depends on the inputs and ``date`` only: no revision, host, time or
    runtime of the report run is written.
    """
    b = _ReportBuilder()
    dirs, files, manifests, paths = inputs["dirs"], inputs["files"], inputs["manifests"], inputs["manifest_paths"]
    primary, arm = inputs["records"]["primary"], inputs["records"]["arm"]
    s_role = f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['analysis']}"
    p_manifest, e_manifest, c_manifest = manifests["analyze"], manifests["export"], manifests["cohort"]
    a_manifest, cmp_manifest = manifests["latent-sensitivity (analysis)"], manifests["latent-sensitivity (comparison)"]
    d_manifest, ad_manifest = manifests["axis-diagnostics"], manifests["axis-diagnostics (arm)"]
    design = primary["design"]
    stages, groups = [str(s) for s in design["stage_levels"]], [str(g) for g in design["group_levels"]]
    arm_name = LATENT_SENSITIVITY_ARM["name"]
    comparison = inputs["tables"]["comparison"]
    cmp_rows = {r["analysis"]: r for r in comparison.to_dict("records")}
    p_row, a_row = cmp_rows["primary"], cmp_rows[arm_name]
    statuses = cmp_manifest.get("counts", {}).get("statuses", {})
    p_status = {s: _rejected(primary["p_values"].get(s)) for s in ANALYSIS_STATISTICS}
    a_status = {s: _rejected(arm["p_values"].get(s)) for s in ANALYSIS_STATISTICS}
    sections = iter(REPORT_SECTIONS)

    variants = list(REPORT_EXPORT_VARIANTS)
    v_groups = _export_variant_groups(variants)
    b.lines.append(f"# {_REPORT_TITLE} — {date}")
    b.para(
        "Generated in full by `adni-sexdiff report` (changes `adni-report`, `adni-report-variants`, "
        "`adni-report-stage-arm`, `adni-report-rank-sweep` and `adni-report-nmr-all-columns`) from the kept aggregate "
        "outputs of the pipeline: every number is copied from a record, a manifest or a CSV and formatted with the digits "
        "of the summary it belongs to, every reading sentence is the one `summary.md`, `latent_sensitivity.md`, "
        "`export_sensitivity.md`, `stage_sensitivity.md` or `rank_sensitivity.md` prints, and the reading rules are the "
        "constants, verbatim. The primary analysis stays primary in every table; the arm is read beside it under "
        "`READING_RULES` and `LATENT_SENSITIVITY_READING_RULES`, "
        + ", ".join(
            f"the export variant{'' if len(group) == 1 else 's'} " + _and_join([f"`{v}`" for v in group])
            + f" under `READING_RULES` and `{_variant_words(group[0])['rules']}`"
            for group in v_groups
        )
        + ", the CN / LMCI / AD arm under `READING_RULES` and `STAGE_SENSITIVITY_READING_RULES`, and the rank sweep under "
        f"`READING_RULES` and `RANK_SENSITIVITY_READING_RULES` ({_section_ref('Reading rules')}). "
        "`adni-sexdiff report --check` compares this file with the outputs cell by cell. No value here is participant-level."
    )

    # 1. Summary ---------------------------------------------------------------------------
    b.section(next(sections))
    cells = design["cell_sizes"]
    cell_text = "; ".join(f"{g} " + " / ".join(f"{st} {cells[g][st]}" for st in stages) for g in groups)
    meas, latent = primary["measurement"], primary["latent"]
    eigengap = (primary.get("config_spectrum", {}).get("pooled") or {}).get("relative_eigengap")
    b.para(
        f"The primary analysis (`{dirs['analysis']}`: one `motco.analysis.analyze_trajectories` call on the covariate-blind "
        f"basis with the five covariates `{'`, `'.join(primary['covariates']['columns'])}`; MOTCO {primary['software']['motco']}): "
        f"n = {design['n_samples']} in the sex × stage cells {cell_text}; CV-selected PLS-DA rank {latent['selected_lv']} "
        f"(`{latent['component_selection']}`; rank floor `ANALYSIS_RANK_FLOOR` = {ANALYSIS_RANK_FLOOR}; pooled relative "
        f"eigengap {_fmt(eigengap)}); {meas['permutations']} RRPP permutations, seed {meas['seed']}; α = {ANALYSIS_ALPHA}, "
        f"rejected when {ANALYSIS_REJECTION_RULE} (`ANALYSIS_REJECTION_RULE`). "
        + " ".join(
            f"`{s}` {_fmt(primary['statistics'].get(s))} (p {_fmt(primary['p_values'].get(s))}, {_rejection_text(p_status[s])})"
            + ("." if s == ANALYSIS_STATISTICS[-1] else ";")
            for s in ANALYSIS_STATISTICS
        )
    )
    b.para(f"Reading, under `READING_RULES` ({_section_ref('Reading rules')}):")
    b.bullets([_statistic_reading_line(s, p_status[s], stages=stages) for s in ANALYSIS_STATISTICS])
    b.para(
        f"The predeclared sensitivity arm `{arm_name}` (`LATENT_SENSITIVITY_ARM`: `{LATENT_SENSITIVITY_ARM['setting']}` = "
        f"`{LATENT_SENSITIVITY_ARM['conditioning']}`, the same five covariates, every other setting the primary's; "
        f"{_section_ref('Latent-adjustment sensitivity')}) "
        f"selected rank {arm['latent']['selected_lv']}. Status per statistic (`same` when the rejection under "
        "`ANALYSIS_REJECTION_RULE` equals the primary's, else `differs (basis dependence)`; the primary's status is the "
        "result either way), read under `READING_RULES` and `LATENT_SENSITIVITY_READING_RULES`:"
    )
    b.bullets([_arm_status_line(s, statuses.get(s, "n/a"), p_status[s], a_status[s]) for s in ANALYSIS_STATISTICS])
    v_labels = {v: _variant_labels(v) for v in variants}
    v_records = inputs["records"]["variants"]
    v_status = {v: {s: _rejected(v_records[v]["p_values"].get(s)) for s in ANALYSIS_STATISTICS} for v in variants}
    for group in v_groups:
        words, one = _variant_words(group[0]), len(group) == 1
        changes = list(dict.fromkeys(EXPORT_VARIANTS[v]["change"] for v in group))
        b.para(
            f"The predeclared export variant{'' if one else 's'} "
            + ", ".join(f"`{v}`" for v in group)
            + f" (`EXPORT_VARIANTS`, change{'' if len(changes) == 1 else 's'} " + _and_join([f"`{c}`" for c in changes])
            + f": {'it changes' if one else 'each changes'} {words['changes']} only, every other export and analysis setting "
            f"the primary's; {_section_ref('Export sensitivity')}) selected rank{'' if one else 's'} "
            + " and ".join(f"{v_records[v]['latent']['selected_lv']} (`{v}`)" for v in group)
            + ". Status per statistic (`same` when the rejection under `ANALYSIS_REJECTION_RULE` equals the primary's, else "
            f"`{words['differs']}`; the primary's status is the result either way), read under `READING_RULES` "
            f"and `{words['rules']}`:"
        )
        for v in group:
            v_statuses = manifests[v_labels[v]["comparison"]].get("counts", {}).get("statuses", {})
            b.para(f"`{v}` (rank {v_records[v]['latent']['selected_lv']}):")
            b.bullets([
                _export_variant_status_line(s, v_statuses.get(s, "n/a"), p_status[s], v_status[v][s], v) for s in ANALYSIS_STATISTICS
            ])
    st_name = STAGE_SENSITIVITY_ARM["name"]
    st_record = inputs["records"]["stage_arm"]
    st_arm = manifests[_STAGE_ARM_LABELS["export"]]["stage_arm"]
    st_statuses = manifests[_STAGE_ARM_LABELS["comparison"]].get("counts", {}).get("statuses", {})
    st_status = {s: _rejected(st_record["p_values"].get(s)) for s in ANALYSIS_STATISTICS}
    b.para(
        f"The predeclared CN / LMCI / AD arm `{st_name}` (`STAGE_SENSITIVITY_ARM`, change `{st_arm['change']}`: "
        f"{_stage_arm_definition(st_arm)}; every other export and analysis setting the primary's; "
        f"{_section_ref('Stage-definition sensitivity')}) selected rank {st_record['latent']['selected_lv']}. Status per "
        "statistic (`same` when the rejection under `ANALYSIS_REJECTION_RULE` equals the primary's, else "
        f"`{_STAGE_SENSITIVITY_STATUS_DIFFERS}`; the primary's status is the result either way), read under `READING_RULES` "
        f"and `STAGE_SENSITIVITY_READING_RULES` ({_section_ref('Reading rules')}):"
    )
    b.bullets([_stage_arm_status_line(s, st_statuses.get(s, "n/a"), p_status[s], st_status[s]) for s in ANALYSIS_STATISTICS])
    ranks = [int(k) for k in RANK_SENSITIVITY_LADDER["ranks"]]
    rk_records = inputs["records"]["ranks"]
    rk_manifest = manifests[_RANK_SWEEP_LABELS["comparison"]]
    rk_ladder = rk_manifest.get("settings", {}).get("RANK_SENSITIVITY_LADDER", {})
    rk_statuses = rk_manifest.get("counts", {}).get("statuses", {})
    rk_anchor = rk_manifest.get("anchor", {})
    b.para(
        f"The predeclared rank sweep `{rk_ladder.get('name')}` (`RANK_SENSITIVITY_LADDER`, change `{rk_ladder.get('change')}`: "
        "the primary's analysis at the forced ranks " + ", ".join(str(k) for k in rk_ladder.get("ranks", []))
        + f", `{rk_ladder.get('setting')}` set to the rank, every other setting the primary's; the anchor, a forced run at "
        f"the primary's rank {rk_anchor.get('rank')}, reproduced the primary; {_section_ref('Rank sensitivity')}). Status "
        "per statistic (`same` when the rejection under `ANALYSIS_REJECTION_RULE` equals the primary's, else "
        f"`{_RANK_SENSITIVITY_STATUS_DIFFERS}`; the primary's status is the result either way), read under `READING_RULES` "
        f"and `RANK_SENSITIVITY_READING_RULES` ({_section_ref('Reading rules')}):"
    )
    b.bullets([
        _rank_status_line(
            s, p_status[s],
            {k: (rk_statuses.get(_rank_dir_name(k), {}).get(s, "n/a"), _rejected(rk_records[k]["p_values"].get(s))) for k in ranks},
        )
        for s in ANALYSIS_STATISTICS
    ])
    tables = inputs["tables"]
    d_flagged, ad_flagged = d_manifest.get("counts", {}).get("flagged", {}), ad_manifest.get("counts", {}).get("flagged", {})
    st_flagged = manifests[_STAGE_ARM_LABELS["diagnostics"]].get("counts", {}).get("flagged", {})
    rk_d_manifest = manifests[_RANK_SWEEP_LABELS["diagnostics"]]
    rk_flagged = rk_d_manifest.get("counts", {}).get("flagged", {})
    rk_top = _rank_dir_name(int(RANK_SENSITIVITY_LADDER["diagnosed_rank"]))
    b.para(
        f"Axis diagnostics (|rho| ≥ {d_manifest.get('settings', {}).get('DIAGNOSTIC_CORRELATION_THRESHOLD')} flagged, a "
        "reporting threshold, not an adoption rule): in the primary, "
        f"{_count(d_flagged.get('axis_raw'))} latent-component rows flagged on the raw correlation and "
        f"{_count(d_flagged.get('axis_partial'))} on the partial, the flagged components "
        f"{_flagged_components(d_manifest, tables['diagnostics']['components'])} "
        f"({_section_ref('Axis diagnostics of the primary')}); in the arm, {_count(ad_flagged.get('axis_raw'))} and "
        f"{_count(ad_flagged.get('axis_partial'))}, the flagged components "
        f"{_flagged_components(ad_manifest, tables['arm_diagnostics']['components'])} "
        f"({_section_ref('Latent-adjustment sensitivity')}); "
        + "; ".join(
            f"in `{v}`, {_count(f.get('axis_raw'))} and {_count(f.get('axis_partial'))}, the flagged components "
            f"{_flagged_components(manifests[v_labels[v]['diagnostics']], tables['variants'][v]['diagnostics']['components'])}"
            for v in variants
            for f in [manifests[v_labels[v]["diagnostics"]].get("counts", {}).get("flagged", {})]
        )
        + f" ({_section_ref('Export sensitivity')}); in `{st_name}`, {_count(st_flagged.get('axis_raw'))} and "
        f"{_count(st_flagged.get('axis_partial'))}, the flagged components "
        f"{_flagged_components(manifests[_STAGE_ARM_LABELS['diagnostics']], tables['stage_arm']['diagnostics']['components'])} "
        f"({_section_ref('Stage-definition sensitivity')}); in the rank sweep's top rank `{rk_top}`, whose components up to "
        f"the primary's rank are the primary's (sweep rule 7), {_count(rk_flagged.get('axis_raw'))} and "
        f"{_count(rk_flagged.get('axis_partial'))}, the flagged components "
        f"{_flagged_components(rk_d_manifest, tables['rank_sweep']['diagnostics']['components'])} "
        f"({_section_ref('Rank sensitivity')}). "
        "A flagged row is a measurement-space finding, never a change of a statistic."
    )

    # 2. Provenance ------------------------------------------------------------------------
    b.section(next(sections))
    b.para(
        "This section is the report's manifest: what each step recorded, every input with its sha256, and the chain the "
        "step checked before writing. The hashes of participant-level files are the ones the manifests record; the report "
        "opened none of them."
    )
    version_rows = [
        {"step": label, **{pkg: _text(m.get("versions", {}).get(pkg)) for pkg in _REPORT_VERSION_PACKAGES}}
        for label, m in manifests.items()
    ]
    b.table("Versions per step", version_rows, ["step", *_REPORT_VERSION_PACKAGES])
    revision_rows = []
    for label, m in manifests.items():
        rev, num = m.get("git_revision") or {}, m.get("numerics")
        revision_rows.append({
            "step": label, "manifest": str(paths[label]), "created at": _text(m.get("created_at")),
            "commit": _text(rev.get("commit")), "dirty": _text(rev.get("dirty")),
            "numerics": _REPORT_NO_NUMERICS if num is None else ("pinned" if num.get("pinned") else "not pinned"),
            "host": _text((num or {}).get("host")), "cpu": _text((num or {}).get("cpu_model")),
        })
    b.table("Revisions and numerics per step", revision_rows, ["step", "manifest", "created at", "commit", "dirty", "numerics", "host", "cpu"])
    input_rows = [
        {"file": str(r["path"]), "sha256": r["sha256"], "bytes": str(r["bytes"]), "recorded in": r["recorded_in"]}
        for r in inputs["provenance"]
    ]
    b.table("Inputs", input_rows, ["file", "sha256", "bytes", "recorded in"], align="llrl")
    raw: dict[str, list[tuple[str, dict]]] = {}
    for label, entries in ((f"clean {p}", manifests[f"clean {p}"].get("inputs", [])) for p in PLATFORMS):
        for e in entries:
            raw.setdefault(e["name"], []).append((label, e))
    for e in c_manifest.get("inputs", {}).get("raw", []):
        raw.setdefault(e["name"], []).append(("cohort", e))
    raw_rows = []
    for name, entries in raw.items():
        by_hash: dict[str, list[tuple[str, dict]]] = {}
        for label, e in entries:
            by_hash.setdefault(e.get("sha256"), []).append((label, e))
        for digest, group in by_hash.items():
            label0, e0 = group[0]
            repair = e0.get("repair")
            raw_rows.append({
                "file": name if len(by_hash) == 1 else f"{name} ({label0})", "sha256": _text(digest), "bytes": _count(e0.get("bytes")),
                "predeclared": _text(e0.get("predeclared")),
                "repair": "none" if not repair else f"repaired {repair.get('repaired_on')}: {repair.get('repair')} (defect: {repair.get('defect')})",
                "recorded in": ", ".join(lbl for lbl, _ in group),
            })
    b.table("Raw LONI inputs", raw_rows, ["file", "sha256", "bytes", "predeclared", "repair", "recorded in"], align="llrlll")
    qc: dict[tuple[str, str], dict] = {}
    for v in variants:
        recorded = manifests[v_labels[v]["export"]].get("inputs", {}).get("qc") or {}
        for kind in ("archives", "workbooks"):
            for e in recorded.get(kind, []):
                key = (e.get("member") or e.get("name"), e.get("sha256"))
                qc.setdefault(key, {"entry": e, "labels": []})["labels"].append(v_labels[v]["export"])
    if qc:
        b.para(
            "The QC archives and the NIST SRM 1950 workbook members `export-sensitivity` read in place through the data root's "
            "top-level symlinks, as the variant export manifests record them (`inputs.qc`), each beside its predeclared sha256 "
            "(`RAW_INPUT_SHA256` for the archives, `NIST_BRIDGE_WORKBOOK_SHA256` for the members):"
        )
        b.table("QC archives and NIST workbooks", [
            {
                "file": name, "location": f"member of `{e['archive']}`" if e.get("member") else f"data root, symlink to `{_text(e.get('target'))}`",
                "run": _text(e.get("run")), "kit": _text(e.get("kit")), "sha256": _text(digest), "bytes": _count(e.get("bytes")),
                "predeclared sha256": _text(e.get("predeclared_sha256")), "predeclared": _text(e.get("predeclared")),
                "recorded in": ", ".join(info["labels"]),
            }
            for (name, digest), info in qc.items() for e in [info["entry"]]
        ], ["file", "location", "run", "kit", "sha256", "bytes", "predeclared sha256", "predeclared", "recorded in"], align="lllllrlll")
    chain_rows = [
        {"link": r["link"], "upstream": r["upstream"], "sha256": _text(r["sha256"]), "ok": "yes" if r["ok"] else "no", "rerun on failure": r["rerun"]}
        for r in inputs["chain"]
    ]
    b.table("Chain links checked", chain_rows, ["link", "upstream", "sha256", "ok", "rerun on failure"])

    # 3. Cohort ----------------------------------------------------------------------------
    b.section(next(sections))
    cs, cc = c_manifest.get("settings", {}), c_manifest.get("counts", {})
    rule, stage_rule = cs.get("COHORT_RULE", {}), cs.get("STAGE_RULE", {})
    reading = cs.get("stage_source_reading", {})
    stage_source = cc.get("intersection", {}).get("stage_source", {})
    b.bullets([
        f"`COHORT_RULE` as `{paths['cohort']}` records it: clinical table `{rule.get('clinical_file')}`, one row per participant "
        f"from its `{rule.get('baseline_visit')}` row; a cleaned participant enters a platform's set only if every raw record "
        f"on that platform has visit `{rule.get('sample_visit')}` ("
        + ", ".join(f"`{f}` column `{c}`" for f, c in rule.get("sample_visit_columns", {}).items())
        + f"; runs without a visit column count as baseline: {', '.join(rule.get('runs_without_visit', []))}) and it has a "
        f"baseline row; the analysis cohort is the intersection of the sets of {', '.join(rule.get('platforms', []))}; no other "
        "exclusion.",
        f"`STAGE_RULE`: `{stage_rule.get('source')}` on the baseline row, "
        + ", ".join(f"{k} → {v}" for k, v in stage_rule.get("map", {}).items()) + ".",
        f"Stage source agreement (`{reading.get('column')}` on the baseline row read as "
        + ", ".join(f"{k} → {v}" for k, v in reading.get("map", {}).items())
        + f"; {reading.get('note')}): agree {_count(stage_source.get('agree'))}, differ {_count(stage_source.get('differ'))}, "
        f"missing {_count(stage_source.get('missing'))}.",
        f"Statin users in the intersection: {_count(cc.get('intersection', {}).get('statin_users'))}; missing covariate values: "
        f"{_count(cc.get('intersection', {}).get('missing_covariate_values'))}; phase-against-run disagreements: "
        f"{_count(cc.get('intersection', {}).get('phase_vs_run_disagreements'))}.",
    ])
    expected = c_manifest.get("expected", {})
    cascade_rows = [
        {
            "set": p, "cleaned": _count(cc.get(p, {}).get("cascade", {}).get("cleaned")),
            "excluded: sample not bl": _count(cc.get(p, {}).get("cascade", {}).get("excluded_sample_not_bl")),
            "excluded: no clinical bl row": _count(cc.get(p, {}).get("cascade", {}).get("excluded_no_clinical_bl_row")),
            "set size": _count(cc.get(p, {}).get("cascade", {}).get("set")),
            "expected set size": _count(expected.get(p, {}).get("cascade", {}).get("set")),
        }
        for p in rule.get("platforms", PLATFORMS)
    ]
    b.table("Cascade per platform set", cascade_rows, ["set", "cleaned", "excluded: sample not bl", "excluded: no clinical bl row", "set size", "expected set size"], align="lrrrrr")
    inter, union = cc.get("intersection", {}).get("cascade", {}), cc.get("union", {})
    e_inter, e_union = expected.get("intersection", {}).get("cascade", {}), expected.get("union", {})
    iu_rows = [
        {"quantity": "cleaned on both platforms", "n": _count(inter.get("cleaned_on_both")), "expected": _count(e_inter.get("cleaned_on_both"))},
        {"quantity": "intersection (the analysis cohort)", "n": _count(inter.get("set")), "expected": _count(e_inter.get("set"))},
        {"quantity": "union (rows of cohort.csv)", "n": _count(union.get("participants")), "expected": _count(e_union.get("participants"))},
        {"quantity": "union: both platforms", "n": _count(union.get("both")), "expected": _count(e_union.get("both"))},
        {"quantity": "union: p180 only", "n": _count(union.get("p180_only")), "expected": _count(e_union.get("p180_only"))},
        {"quantity": "union: nmr only", "n": _count(union.get("nmr_only")), "expected": _count(e_union.get("nmr_only"))},
    ]
    b.table("Intersection and union", iu_rows, ["quantity", "n", "expected"], align="lrr")
    visit_rows = [
        {"platform set · visit": f"{p} {k.replace('.', ' · ')}", "n": _count(v)}
        for p in rule.get("platforms", PLATFORMS) for k, v in _flatten(cc.get(p, {}).get("sample_visits", {})).items()
    ]
    b.table("Sample visits of the cleaned participants", visit_rows, ["platform set · visit", "n"], align="lr")
    sc = inputs["tables"]["stage_counts"]
    sexes, stage_cols = [*GROUP_VALUES, "all"], [*STAGE_LABELS, "all"]
    for set_name, title in (("p180", "Sex × stage: p180 set"), ("nmr", "Sex × stage: nmr set"), ("intersection", "Sex × stage: intersection")):
        sub = sc[(sc["set"] == set_name) & (sc["dx_bl"] == "all") & (sc["phase"] == "all")]
        lookup = {(r["sex"], r["stage"]): r["n"] for r in sub.to_dict("records")}
        rows = [{"sex": g, **{st: lookup.get((g, st), "n/a") for st in stage_cols}} for g in sexes]
        b.table(title, rows, ["sex", *stage_cols], align="l" + "r" * len(stage_cols))
    comp = sc[(sc["set"] == "intersection") & (sc["dx_bl"] != "all")]
    comp_rows = [
        {"cell": f"{r['sex']} {r['stage']} {r['dx_bl']} {r['phase']}", "sex": r["sex"], "stage": r["stage"], "DX.bl": r["dx_bl"], "phase": r["phase"], "n": r["n"]}
        for r in comp.to_dict("records")
    ]
    b.table("Intersection: sex × stage × DX.bl × phase", comp_rows, ["cell", "sex", "stage", "DX.bl", "phase", "n"], align="lllllr")
    descriptives = c_manifest.get("descriptives") or {}
    d_cells = descriptives.get("cells", {})
    b.para(
        f"Per sex × stage cell of the analysis cohort, copied from `{COHORT_MANIFEST}` (`descriptives`, set "
        f"`{descriptives.get('set')}`), not recomputed: n, age and education mean (sd), and counts per level of `apoe4` "
        f"(0 / 1 / 2), `phase` (ADNI1 / ADNI2GO) and `statin` (0 / 1). The covariate roles of the arm ({_section_ref('Latent-adjustment sensitivity')}) are read "
        "beside this table."
    )
    desc_rows = []
    for g in groups:
        for st in stages:
            c = d_cells.get(g, {}).get(st)
            if not c:
                desc_rows.append({"cell": f"{g} {st}", "n": "n/a", "age mean (sd)": "n/a", "education mean (sd)": "n/a",
                                  "apoe4 0 / 1 / 2": "n/a", "phase ADNI1 / ADNI2GO": "n/a", "statin 0 / 1": "n/a"})
                continue
            desc_rows.append({
                "cell": f"{g} {st}", "n": _count(c.get("n")),
                "age mean (sd)": f"{_fmt(c.get('age', {}).get('mean'))} ({_fmt(c.get('age', {}).get('sd'))})",
                "education mean (sd)": f"{_fmt(c.get('education', {}).get('mean'))} ({_fmt(c.get('education', {}).get('sd'))})",
                "apoe4 0 / 1 / 2": " / ".join(str(c.get("apoe4", {}).get(k, "n/a")) for k in ("0", "1", "2")),
                "phase ADNI1 / ADNI2GO": " / ".join(str(c.get("phase", {}).get(k, "n/a")) for k in ("ADNI1", "ADNI2GO")),
                "statin 0 / 1": " / ".join(str(c.get("statin", {}).get(k, "n/a")) for k in ("0", "1")),
            })
    b.table("Per-cell covariate descriptives", desc_rows, ["cell", "n", "age mean (sd)", "education mean (sd)", "apoe4 0 / 1 / 2", "phase ADNI1 / ADNI2GO", "statin 0 / 1"], align="lrrrrrr")
    pvr = cc.get("phase_vs_run", {})
    pvr_rows = [
        {
            "set": name, "ADNI1 → ADNI1": _count(info.get("table", {}).get("ADNI1", {}).get("ADNI1")),
            "ADNI2GO → ADNI2GO": _count(info.get("table", {}).get("ADNI2GO", {}).get("ADNI2GO")),
            "disagreements": _count(info.get("disagreements")),
        }
        for name, info in pvr.items()
    ]
    b.para("The `phase` covariate (ADNIMERGE `ORIGPROT`, ADNI-GO and ADNI-2 merged) against the p180 run of `p180_runs.csv`:")
    b.table("Phase against the p180 run", pvr_rows, ["set", "ADNI1 → ADNI1", "ADNI2GO → ADNI2GO", "disagreements"], align="lrrr")
    option_keys = list(dict.fromkeys(k for p in PLATFORMS for k in CLEAN_OPTIONS[p]))
    option_rows = [
        {"option": k, **{p: _text(manifests[f"clean {p}"].get("settings", {}).get("options", {}).get(k)) for p in PLATFORMS}}
        for k in option_keys
    ]
    b.para("Cleaning (`clean`, metabo_adni " + _text(inputs["versions"].get("metabo_adni")) + "; `CLEAN_OPTIONS` as each `clean_manifest.json` records them):")
    b.table("Cleaning options", option_rows, ["option", *PLATFORMS])
    b.bullets([f"`clean --platform {p}` ran metabo_adni as `{manifests[f'clean {p}'].get('settings', {}).get('cli_equivalent')}`" for p in PLATFORMS])
    table_order = [*CLEAN_P180_FILES, *CLEAN_TABLES.values()]
    for p in PLATFORMS:
        m = manifests[f"clean {p}"]
        observed, exp = m.get("counts", {}).get("observed", {}), m.get("counts", {}).get("expected", {})
        steps = m.get("settings", {}).get("metabo_adni_steps", list(observed.get("cells", {})))
        names = list(dict.fromkeys(t for step in steps for t in observed.get("cells", {}).get(step, {})))
        names.sort(key=lambda t: (table_order.index(t) if t in table_order else len(table_order), t))
        rows = []
        for step in steps:
            row = {"metabo_adni step": step}
            for t in names:
                o, e = observed.get("cells", {}).get(step, {}).get(t), exp.get("cells", {}).get(step, {}).get(t)
                row[t] = f"{o[0]} × {o[1]}" if o else "n/a"
                row[f"{t} expected"] = f"{e[0]} × {e[1]}" if e else "n/a"
            rows.append(row)
        columns = ["metabo_adni step", *(c for t in names for c in (t, f"{t} expected"))]
        b.table(f"Cleaning: {p} participants × metabolites per metabo_adni step", rows, columns)
    count_rows = []
    flat = {p: _flatten({k: v for k, v in manifests[f"clean {p}"].get("counts", {}).get("observed", {}).items() if k != "cells"}) for p in PLATFORMS}
    flat_e = {p: _flatten({k: v for k, v in manifests[f"clean {p}"].get("counts", {}).get("expected", {}).items() if k != "cells"}) for p in PLATFORMS}
    for key in dict.fromkeys(k for p in PLATFORMS for k in flat[p]):
        count_rows.append({"quantity": key, **{c: _text(src[p].get(key)) for p in PLATFORMS for c, src in ((p, flat), (f"{p} expected", flat_e))}})
    b.table("Cleaning counts", count_rows, ["quantity", *(c for p in PLATFORMS for c in (p, f"{p} expected"))], align="l" + "r" * (2 * len(PLATFORMS)))

    # 4. Export ----------------------------------------------------------------------------
    b.section(next(sections))
    es, ec, ee = e_manifest.get("settings", {}), e_manifest.get("counts", {}), e_manifest.get("expected", {})
    scale = es.get("EXPORT_FEATURE_RULE", {}).get("scale", {})
    membership = es.get("EXPORT_FEATURE_RULE", {}).get("membership", {})
    marks = "; ".join(
        f"{p}: " + (", ".join(f"{family} ({test} `{mark}`)" for family, (test, mark) in spec.get("derived", {}).items()) or "none")
        for p, spec in membership.items()
    )
    b.bullets([
        f"`EXPORT_FEATURE_RULE` as `{paths['export']}` records it: units `{es.get('units')}` (the floor of a metabolite its "
        f"{scale.get('floor_quantile')} quantile, `{scale.get('floor_method')}` interpolation, over the exported participants, "
        f"computed without sex, stage or a covariate); MOTCO transform `{es.get('motco_transform')}`; derived marks excluded "
        f"from the blocks: {marks}. Nothing imputed, replaced, winsorized, removed or centred per run.",
        f"Blocks in MOTCO order: {', '.join(es.get('blocks', []))}; sample column `{es.get('sample_column')}`, group `{es.get('group_column')}` "
        f"({', '.join(es.get('group_values', []))}), stage `{es.get('stage_column')}` ({' → '.join(es.get('stage_order', []))}); "
        f"covariate columns exported, not applied (`covariates_applied` {_text(es.get('covariates_applied'))}): "
        + ", ".join(f"`{c}`" for c in es.get("covariate_columns", [])) + ".",
        f"Participants {_count(ec.get('participants'))} (expected {_count(ee.get('participants'))}); joint features "
        f"{_count(ec.get('joint_features'))}; missing covariate values {_count(ec.get('missing_covariate_values'))}.",
    ])
    feat_rows = []
    for p in es.get("blocks", EXPORT_BLOCKS):
        f, e = ec.get("features", {}).get(p, {}), ee.get("features", {}).get(p, {})
        feat_rows.append({
            "block": p, "cleaned": _count(f.get("cleaned")), "kept": _count(f.get("kept")),
            **{f"derived {fam}": _count(f.get("derived", {}).get(fam)) for fam in ("percentage", "ratio", "degree", "size")},
            "share of the joint features": _num(ec.get("block_shares", {}).get(p), ".3f"), "expected kept": _count(e.get("kept")),
        })
    b.table("Features per block", feat_rows, ["block", "cleaned", "kept", "derived percentage", "derived ratio", "derived degree", "derived size", "share of the joint features", "expected kept"], align="lrrrrrrrr")
    offset_rows = []
    for p in es.get("blocks", EXPORT_BLOCKS):
        o = ec.get("phase_offset", {}).get(p, {})
        offset_rows.append({
            "block": p, "median |d|": _num(o.get("median_abs_d"), ".2f"), "max |d|": _num(o.get("max_abs_d"), ".2f"),
            "|d| > 0.5": _count(o.get("abs_d_gt_0_5")), "|d| > 1": _count(o.get("abs_d_gt_1")),
            "|corr(PC1, phase)|": _num(o.get("abs_corr_pc1_phase"), ".2f"), "|corr(PC2, phase)|": _num(o.get("abs_corr_pc2_phase"), ".2f"),
            "expected |d| > 1": _count(ee.get("phase_offset", {}).get(p, {}).get("abs_d_gt_1")),
            "contrast": _text(o.get("contrast")),
        })
    b.para(
        "The p180 run offset (`phase`, ADNI1 against ADNI2GO, on the rule's scale over the exported participants), recorded "
        "by `export` and not corrected: the runs differ in stage composition, so per-run centring would move stage signal "
        "between runs; `phase` enters the analysis as a covariate of the stage means."
    )
    b.table("Run offset per block (phase)", offset_rows, ["block", "median |d|", "max |d|", "|d| > 0.5", "|d| > 1", "|corr(PC1, phase)|", "|corr(PC2, phase)|", "expected |d| > 1", "contrast"], align="lrrrrrrrl")
    cell_rows = [
        {"quantity": label, **{c: _count(src.get(key, {}).get(p)) for p in es.get("blocks", EXPORT_BLOCKS) for c, src in ((p, ec), (f"{p} expected", ee))}}
        for label, key in (("zero cells", "zero_cells"), ("metabolites with zeros", "metabolites_with_zeros"),
                           ("floors not positive", "floors_not_positive"), ("non-finite cells", "non_finite"))
    ]
    b.table("Cells per block", cell_rows, ["quantity", *(c for p in es.get("blocks", EXPORT_BLOCKS) for c in (p, f"{p} expected"))], align="l" + "r" * (2 * len(es.get("blocks", EXPORT_BLOCKS))))
    ss = ec.get("sex_stage", {})
    b.table("Exported participants per sex × stage", [{"sex": g, **{st: _count(ss.get(g, {}).get(st)) for st in stages}} for g in groups], ["sex", *stages], align="l" + "r" * len(stages))

    # 5. Primary analysis ------------------------------------------------------------------
    b.section(next(sections))
    ps = p_manifest.get("settings", {})
    setting_rows = [
        {"setting": "`ANALYSIS_PERMUTATIONS`", "value": _text(ps.get("ANALYSIS_PERMUTATIONS")), "note": "RRPP permutations; the p-value (1 + b) / (1 + B) is exact in size at any count"},
        {"setting": "`ANALYSIS_SEED`", "value": _text(ps.get("ANALYSIS_SEED")), "note": "the RRPP seed (one stream per worker)"},
        {"setting": "`ANALYSIS_ALPHA`", "value": _text(ps.get("ANALYSIS_ALPHA")), "note": f"rejected when {ps.get('ANALYSIS_REJECTION_RULE')} (`ANALYSIS_REJECTION_RULE`)"},
        {"setting": "`ANALYSIS_RANK_FLOOR`", "value": _text(ps.get("ANALYSIS_RANK_FLOOR")), "note": f"`min_components` {_text(ps.get('min_components'))}, checked equal to MOTCO's default before any input is read"},
        {"setting": "`ANALYSIS_LATENT_ADJUSTMENT`", "value": "none" if ps.get("ANALYSIS_LATENT_ADJUSTMENT") is None else _text(ps.get("ANALYSIS_LATENT_ADJUSTMENT")), "note": f"the covariate-blind basis of MOTCO's validated path; the `stage`-conditioned arm is {_section_ref('Latent-adjustment sensitivity')}"},
        {"setting": "`ANALYSIS_MISSING_COVARIATES`", "value": _text(ps.get("ANALYSIS_MISSING_COVARIATES")), "note": "nothing imputed; a missing value stops the step"},
        {"setting": "`n_jobs`", "value": _text(ps.get("n_jobs")), "note": f"reported runs use `REPORTED_N_JOBS` = {_text(ps.get('REPORTED_N_JOBS'))}"},
        {"setting": "entry point", "value": f"`{ps.get('entry_point')}`", "note": "one call; never assembled from `motco plsr` + `motco de`"},
        {"setting": "group order", "value": ", ".join(_text(g) for g in ps.get("group_order", [])), "note": f"`{ps.get('group_column')}`"},
        {"setting": "stage order", "value": " → ".join(_text(s) for s in ps.get("stage_order", [])), "note": f"`{ps.get('stage_column')}`"},
        {"setting": "categorical covariates", "value": ", ".join(f"`{c}`" for c in ps.get("ANALYSIS_CATEGORICAL_COVARIATES", [])), "note": "`ANALYSIS_CATEGORICAL_COVARIATES`; the others numeric"},
    ]
    b.table("Settings", setting_rows, ["setting", "value", "note"])
    defaults = ps.get("motco_defaults_used", {})
    stated = defaults.get("stated_by_proposal", {})
    default_rows = [
        {"default": k, "as run": _text(defaults.get(k)), "stated by proposal": _text(stated.get(k)) if k in stated else "n/a"}
        for k in ("orientation_estimator", "cv1_splits", "cv2_splits", "n_repeats", "max_components", "random_state", "forced_components", "attribution")
    ]
    b.para("MOTCO's other settings stay its defaults and are read back from the record; a moved default is a finding:")
    b.table("MOTCO defaults used", default_rows, ["default", "as run", "stated by proposal"])
    b.para(
        f"MOTCO {primary['software']['motco']}; orientation `{meas['orientation_estimator']}`; {meas['permutations']} RRPP "
        f"permutations, seed {meas['seed']}; n_jobs {meas['n_jobs']}; α = {ANALYSIS_ALPHA}, rejected when {ANALYSIS_REJECTION_RULE}."
    )
    stat_columns = ["statistic", "observed", "p (RRPP)", "rejected", "null mean", "null sd", "null q95", "note"]
    b.table("Statistics", _statistics_rows(primary), stat_columns, align="lrrlrrrl")
    b.para(f"Reading, under the rules of {_section_ref('Reading rules')}:")
    b.bullets([_statistic_reading_line(s, p_status[s], stages=stages) for s in ANALYSIS_STATISTICS])
    b.table("Cell sizes", [{"group": g, **{f"stage {st}": _count(cells[g][st]) for st in stages}} for g in groups], ["group", *(f"stage {st}" for st in stages)], align="l" + "r" * len(stages))
    cv = latent.get("integration_params", {})
    permuted = primary.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {}
    blocks_text = ", ".join(f"{bl['name']} ({bl['n_features']} features, {bl['transform']})" for bl in primary["blocks"])
    latent_rows = [
        {"quantity": "PLS-DA rank (selection)", "value": f"{latent['selected_lv']} (`{latent['component_selection']}`)"},
        {"quantity": "rank floor (`ANALYSIS_RANK_FLOOR`)", "value": _count(cv.get("min_components", 1))},
        {"quantity": "floor binding", "value": "yes" if latent["component_selection"] == "cv" and latent["selected_lv"] == ANALYSIS_RANK_FLOOR else "no"},
        {"quantity": "cv_mean_auroc", "value": _fmt(latent.get("cv_mean_auroc"))},
        {"quantity": "CV repeats completed / requested", "value": f"{_count(latent.get('cv_repeats_completed'))} / {_count(cv.get('n_repeats'))}"},
        {"quantity": "pooled relative eigengap of the stage-mean configuration", "value": _fmt(eigengap)},
        {"quantity": "eigengap permutation null q05 / q50 / q95", "value": f"{_fmt(permuted.get('q05'))} / {_fmt(permuted.get('q50'))} / {_fmt(permuted.get('q95'))}"},
        {"quantity": "CV settings", "value": f"cv2_splits {cv.get('cv2_splits')}, cv1_splits {cv.get('cv1_splits')}, n_repeats {cv.get('n_repeats')}, max_components {cv.get('max_components')}, random_state {cv.get('random_state')}"},
        {"quantity": "blocks", "value": blocks_text + "; features z-scored by MOTCO (pooled per-feature scalers)"},
    ]
    b.table("Latent space", latent_rows, ["quantity", "value"])
    cov = primary.get("covariates") or {}
    b.bullets([
        "entered (in order, additively): " + ", ".join(f"`{c}` ({cov['kinds'][c]})" for c in cov.get("columns", [])),
        f"design columns: {len(cov.get('design_columns', []))} (" + ", ".join(cov.get("design_columns", [])) + ")",
        "reference levels: " + ", ".join(f"`{c}` {lvl}" for c, lvl in cov.get("reference_levels", {}).items()),
        f"missing policy: `{cov.get('missing_policy')}`; dropped participants: {_count(cov.get('n_dropped'))}",
        f"LS-means evaluated at the reference row (`{cov.get('lsmean_reference')}`); no sex × covariate or stage × covariate term",
    ])
    b.table("Reference row", [{"design column": c, "reference value": _fmt(v)} for c, v in cov.get("reference_row", {}).items()], ["design column", "reference value"], align="lr")
    level_rows = [
        {"level": f"`{c}` = {lvl}", "n": _count(n)}
        for c, levels in p_manifest.get("counts", {}).get("covariate_levels", {}).items() for lvl, n in levels.items()
    ]
    b.table("Covariate levels", level_rows, ["level", "n"], align="lr")
    b.para("The `motco analyze` command that reproduces the directory from its inputs (`cli_equivalent`; " + _text(ps.get("cli_equivalent", {}).get("note")) + "):")
    b.code(_text(ps.get("cli_equivalent", {}).get("command")))

    # 6. Axis diagnostics of the primary ---------------------------------------------------
    b.section(next(sections))
    ds, dc = d_manifest.get("settings", {}), d_manifest.get("counts", {})
    b.para(
        f"`{dirs['diagnostics']}` (`axis-diagnostics` on `{dirs['analysis']}`, rank {_count(dc.get('components'))}, n = "
        f"{_count(dc.get('participants'))}): Spearman correlations of every latent component with the "
        f"{len(ds.get('DIAGNOSTIC_VARIABLES', []))} predeclared variables, the partial Spearman correlations given the "
        f"{len(ds.get('conditioning_columns', []))} design columns of the record (" + ", ".join(ds.get("conditioning_columns", []))
        + f"), the same for the first {_count(ds.get('DIAGNOSTIC_N_BLOCK_PCS'))} principal components of each z-scored block, "
        "and the block composition of each component. Nothing here chooses a variant or an arm; the statistics keep their "
        "recorded status."
    )
    b.table("Variables (`DIAGNOSTIC_VARIABLES`)", [
        {"variable": f"`{v['name']}`", "source": v["file"], "derivation": v["derivation"]} for v in ds.get("DIAGNOSTIC_VARIABLES", [])
    ], ["variable", "source", "derivation"])
    _diagnostics_section(b, inputs["tables"]["diagnostics"], d_manifest)

    # 7. Latent-adjustment sensitivity ----------------------------------------------------
    b.section(next(sections))
    cmp_ref, cmp_arm = cmp_manifest.get("reference", {}), cmp_manifest.get("arm", {})
    adjustment = arm["latent_adjustment"]
    b.para(
        f"The primary (`{dirs['analysis']}`, `{ANALYSIS_RESULT}` sha256 `{cmp_ref.get('files', {}).get(ANALYSIS_RESULT, {}).get('sha256')}`) beside "
        f"its predeclared sensitivity arm `{arm_name}` (`LATENT_SENSITIVITY_ARM`, change `{LATENT_SENSITIVITY_ARM['change']}`: "
        f"`{LATENT_SENSITIVITY_ARM['setting']}` = `{adjustment['conditioning']}`, the same five covariates, every other setting "
        f"the primary's; `{dirs[s_role]}`, `{ANALYSIS_RESULT}` sha256 `{cmp_arm.get('files', {}).get(ANALYSIS_RESULT, {}).get('sha256')}`), "
        f"as `{paths['latent-sensitivity (comparison)']}` records them. Every table in this section quotes the arm and is read "
        f"under `READING_RULES` and `LATENT_SENSITIVITY_READING_RULES` ({_section_ref('Reading rules')}): the primary row comes first and its status "
        "is the result; the arm never replaces it (arm rule 1), and a status that differs is basis dependence (arm rule 2)."
    )
    cmp_table_rows = []
    for s in ANALYSIS_STATISTICS:
        for label, row in (("primary", p_row), (arm_name, a_row)):
            cmp_table_rows.append({
                "row": f"{s} {label}", "statistic": s, "analysis": label, "observed": _num(row[f"{s}_observed"]),
                "p (RRPP)": _num(row[f"{s}_p"]), "rejected": _yes_no(row[f"{s}_rejected"]),
                "null mean": _num(row[f"{s}_null_mean"]), "null sd": _num(row[f"{s}_null_sd"]), "null q95": _num(row[f"{s}_null_q95"]),
                "status": _text(statuses.get(s)),
            })
    b.table("Statistics: primary and arm", cmp_table_rows, ["row", "statistic", "analysis", "observed", "p (RRPP)", "rejected", "null mean", "null sd", "null q95", "status"], align="lllrrlrrrl")
    b.para(
        f"`angle` (degrees, endpoint stages {stages[0]} and {stages[-1]}) is read beside each analysis' CV-selected rank, "
        f"floor, eigengap and null summary (reading rule 2, arm rule 3): primary rank {_count(p_row['selected_rank'])} (floor "
        f"{ANALYSIS_RANK_FLOOR}, pooled relative eigengap {_num(p_row['eigengap'])}); {arm_name} rank {_count(a_row['selected_rank'])} "
        f"(floor {ANALYSIS_RANK_FLOOR}, eigengap {_num(a_row['eigengap'])})"
        + ("; the ranks differ, which is reported, not ranked as better or worse (arm rule 3)." if p_row["selected_rank"] != a_row["selected_rank"] else "; the ranks are equal.")
    )
    b.para("Status per statistic:")
    b.bullets([_arm_status_line(s, statuses.get(s, "n/a"), p_status[s], a_status[s]) for s in ANALYSIS_STATISTICS])
    p_perm = primary.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {}
    a_perm = arm.get("config_spectrum", {}).get("permutation_pooled_eigengap") or {}
    space_rows = [
        {"quantity": "PLS-DA rank (selection)", "primary": f"{_count(p_row['selected_rank'])} (`{p_row['component_selection']}`)", arm_name: f"{_count(a_row['selected_rank'])} (`{a_row['component_selection']}`)"},
        {"quantity": "rank floor (`ANALYSIS_RANK_FLOOR`)", "primary": str(ANALYSIS_RANK_FLOOR), arm_name: str(ANALYSIS_RANK_FLOOR)},
        {"quantity": "cv_mean_auroc", "primary": _num(p_row["cv_mean_auroc"]), arm_name: _num(a_row["cv_mean_auroc"])},
        {"quantity": "CV repeats completed", "primary": _count(p_row["cv_repeats_completed"]), arm_name: _count(a_row["cv_repeats_completed"])},
        {"quantity": "pooled relative eigengap", "primary": _num(p_row["eigengap"]), arm_name: _num(a_row["eigengap"])},
        {"quantity": "eigengap permutation null q05 / q50 / q95",
         "primary": f"{_fmt(p_perm.get('q05'))} / {_fmt(p_perm.get('q50'))} / {_fmt(p_perm.get('q95'))}",
         arm_name: f"{_fmt(a_perm.get('q05'))} / {_fmt(a_perm.get('q50'))} / {_fmt(a_perm.get('q95'))}"},
        {"quantity": "latent adjustment", "primary": "none", arm_name: f"`{_text(a_row['latent_adjustment'])}`"},
        {"quantity": "residual df", "primary": "n/a", arm_name: _count(a_row["residual_df"])},
        {"quantity": "smallest CV training df", "primary": "n/a", arm_name: _count(a_row["cv_min_training_df"])},
    ]
    b.table("Latent space: primary and arm", space_rows, ["quantity", "primary", arm_name], align="lrr")
    b.para(
        "The two analyses share the export, the covariates and their design, the cells, the CV folds (stratified on the "
        "stage, as the primary's), the seed and the permutations; they differ only in the latent basis and the CV-selected "
        "rank (arm rule 2)."
    )
    b.heading("Latent adjustment of the arm")
    b.bullets(_latent_adjustment_lines(adjustment, stages))
    b.para(
        "Each covariate's relation to the stage effect (`LATENT_SENSITIVITY_COVARIATE_ROLES`, decided before any run; no "
        "statistic or threshold is computed for it and nothing changes because of it), read beside the per-cell "
        f"descriptives of {_section_ref('Cohort')}. Residualizing a covariate that mediates the stage effect removes real stage signal, and "
        "no data can tell a confounder from a mediator (arm rule 7)."
    )
    b.table("Covariate roles", [
        {"covariate": f"`{name}`", "role": role["role"], "variable": role["variable"], "justification": role["justification"]}
        for name, role in LATENT_SENSITIVITY_COVARIATE_ROLES.items()
    ], ["covariate", "role", "variable", "justification"])
    decisions = cmp_manifest.get("settings", {}).get("motco_latent_adjustment_decisions", [])
    b.para(
        "MOTCO's two latent-adjustment decisions, as the comparison manifest records them (measured at one design, n = 80, "
        "none at this one; the arm carries no Type I or power claim of its own, arm rule 8):"
    )
    b.bullets([f"`{d.get('decision')}` (`{d.get('report')}`): {d.get('reading')}." for d in decisions])
    b.para(
        f"Axis diagnostics of the arm (`{dirs[f'sensitivity/{LATENT_SENSITIVITY_SUBDIRS['diagnostics']}']}`, rank "
        f"{_count(ad_manifest.get('counts', {}).get('components'))}, `is_primary` {_text(ad_manifest.get('inputs', {}).get('analysis', {}).get('is_primary'))}): "
        "a component of the arm that tracks a variable here is a measurement-space finding about the arm; it never "
        "reinterprets either analysis' statistics and is never grounds to adopt the arm (arm rule 9)."
    )
    _diagnostics_section(b, inputs["tables"]["arm_diagnostics"], ad_manifest, prefix="Arm: ")
    first_rows = _first_component_rows([("primary", inputs["tables"]["diagnostics"]), (arm_name, inputs["tables"]["arm_diagnostics"])])
    b.table("First component against phase", first_rows, ["analysis", "component", "sd", "rho with phase", "rho | design", "flag"], align="llrrrl")
    a_settings = a_manifest.get("settings", {})
    b.para("The `motco analyze` command that reproduces the arm's directory (`cli_equivalent`; " + _text(a_settings.get("cli_equivalent", {}).get("note")) + "):")
    b.code(_text(a_settings.get("cli_equivalent", {}).get("command")))

    # 8. Export sensitivity ----------------------------------------------------------------
    b.section(next(sections))
    _export_sensitivity_section(b, inputs, stages=stages, p_status=p_status)

    # 9. Stage-definition sensitivity ------------------------------------------------------
    b.section(next(sections))
    _stage_sensitivity_section(b, inputs, stages=stages, p_status=p_status)

    # 10. Rank sensitivity -----------------------------------------------------------------
    b.section(next(sections))
    _rank_sensitivity_section(b, inputs, stages=stages, p_status=p_status)

    # 11. Findings -------------------------------------------------------------------------
    b.section(next(sections))
    b.para("Every deviation from the predeclared counts and every finding of every input manifest, verbatim, under its step; then the report's own.")
    for label, m in manifests.items():
        b.heading(f"{m.get('step')} — {paths[label]}")
        items = [f"deviation: {d}" for d in m.get("deviations", [])] + [f"finding: {f}" for f in m.get("findings", [])]
        if items:
            b.bullets(items)
        else:
            b.para("None.")
    b.heading("report")
    if inputs["findings"]:
        b.bullets(inputs["findings"])
    else:
        b.para("None.")

    # 12. Reading rules --------------------------------------------------------------------
    b.section(next(sections))
    b.heading("READING_RULES")
    b.para("Binding for every reader of the result (`READING_RULES`, decided by `adni-analyze` before any run):")
    b.para(*(f"{i}. {rule}" for i, rule in enumerate(READING_RULES, 1)))
    b.heading("LATENT_SENSITIVITY_READING_RULES")
    b.para(
        f"Binding for every reader of the arm (`LATENT_SENSITIVITY_READING_RULES`, decided by "
        f"`{LATENT_SENSITIVITY_ARM['change']}` before any run), after `READING_RULES`:"
    )
    b.para(*(f"{i}. {rule}" for i, rule in enumerate(LATENT_SENSITIVITY_READING_RULES, 1)))
    for group in v_groups:
        words = _variant_words(group[0])
        b.heading(words["rules"])
        b.para(_export_variant_rules_heading(group[0])[-1])
        b.para(*(f"{i}. {rule}" for i, rule in enumerate(words["rule_tuple"], 1)))
    b.heading("STAGE_SENSITIVITY_READING_RULES")
    b.para(_stage_arm_rules_heading()[-1])
    b.para(*(f"{i}. {rule}" for i, rule in enumerate(STAGE_SENSITIVITY_READING_RULES, 1)))
    b.heading("RANK_SENSITIVITY_READING_RULES")
    b.para(_rank_sweep_rules_heading()[-1])
    b.para(*(f"{i}. {rule}" for i, rule in enumerate(RANK_SENSITIVITY_READING_RULES, 1)))

    # 13. Reproduction ---------------------------------------------------------------------
    b.section(next(sections))
    sens_dir = dirs[s_role].parent
    reads_root = [v for v in variants if manifests[v_labels[v]["export"]].get("variant", {}).get("reads_data_root")]
    archives = list(dict.fromkeys(
        e.get("name") for v in reads_root for e in (manifests[v_labels[v]["export"]].get("inputs", {}).get("qc") or {}).get("archives", [])
    ))
    b.para(
        "The pipeline, in order, each step reading the previous steps' outputs and checking their manifests' hashes; "
        "`clean`, `cohort` and "
        + (", ".join(f"`export-sensitivity --variant {v}`" for v in reads_root) or "no export variant")
        + " need the data root (`--data-root`, `ADNI_DATA_ROOT` or `data/`"
        + (f"; the QC archives {', '.join(f'`{a}`' for a in archives)} are read in place, through top-level symlinks the data root must hold" if archives else "")
        + "), the others read `results/` only, and `report` reads committed aggregate files only, so it runs on any clone:"
    )
    b.code(
        "uv run adni-sexdiff clean --platform all",
        "uv run adni-sexdiff cohort",
        "uv run adni-sexdiff export",
        "uv run adni-sexdiff analyze",
        "uv run adni-sexdiff axis-diagnostics",
        "uv run adni-sexdiff latent-sensitivity",
        f"uv run adni-sexdiff axis-diagnostics --analysis-dir {dirs[s_role]} --out-dir {sens_dir / LATENT_SENSITIVITY_SUBDIRS['diagnostics']}",
        "uv run adni-sexdiff export-sensitivity --variant all",
        *(
            f"uv run adni-sexdiff axis-diagnostics --input-dir {dirs[_variant_role(v, 'export')]} --analysis-dir "
            f"{dirs[_variant_role(v, 'analysis')]} --out-dir {dirs[_variant_role(v, 'diagnostics')]}"
            for v in variants
        ),
        "uv run adni-sexdiff stage-sensitivity",
        f"uv run adni-sexdiff axis-diagnostics --input-dir {dirs[_stage_arm_role('export')]} --analysis-dir "
        f"{dirs[_stage_arm_role('analysis')]} --out-dir {dirs[_stage_arm_role('diagnostics')]}",
        "uv run adni-sexdiff rank-sensitivity",
        f"uv run adni-sexdiff axis-diagnostics --analysis-dir {dirs[_rank_sweep_role(int(RANK_SENSITIVITY_LADDER['diagnosed_rank']))]} "
        f"--out-dir {dirs[_rank_sweep_role('diagnostics')]}",
        "uv run adni-sexdiff report",
        "uv run adni-sexdiff report --check",
    )
    b.para(
        f"`report --check` reads the newest `{REPORTS_DIR}/{REPORT_NAME.format(date='<date>')}` (or the file `--out` names), "
        "reruns every gate, regenerates the report from the outputs now on disk with the date taken from the file name and "
        "compares every table cell by cell and every other line line by line; a regenerated results directory fails it on "
        "the provenance hashes until a new report is written and checked."
    )
    v_settings = [manifests[v_labels[v]["analysis"]].get("settings", {}) for v in variants]
    st_settings = manifests[_STAGE_ARM_LABELS["analysis"]].get("settings", {})
    rk_settings = [manifests[_RANK_SWEEP_LABELS[k]].get("settings", {}) for k in ranks]
    commands = [
        _text(ps.get("cli_equivalent", {}).get("command")), _text(a_settings.get("cli_equivalent", {}).get("command")),
        *(_text(vs.get("cli_equivalent", {}).get("command")) for vs in v_settings),
        _text(st_settings.get("cli_equivalent", {}).get("command")),
        *(_text(rs.get("cli_equivalent", {}).get("command")) for rs in rk_settings),
    ]
    b.para(
        f"MOTCO's CLI equivalents of the {len(commands)} analyses, the primary, the arm, "
        + ", ".join(f"`{v}`" for v in variants) + f", the CN / LMCI / AD arm `{st_name}` and the {len(rk_settings)} forced "
        "ranks of the rank sweep " + ", ".join(f"`{_rank_dir_name(k)}`" for k in ranks) + " (`cli_equivalent` of their "
        "analysis manifests):"
    )
    b.code(*commands)
    return b.text(), b.tables


# --- report: the parser and the check ----------------------------------------------

_TABLE_CELL_RE = re.compile(r"(?<!\\)\|")


def _split_cells(line: str) -> list[str]:
    parts = _TABLE_CELL_RE.split(line.strip())
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip().replace("\\|", "|") for p in parts]


def parse_report(text: str) -> dict:
    """Split a report into its level-2 sections, their titled tables and their other lines (design D6 of ``adni-report``).

    Parameters
    ----------
    text:
        The report's Markdown.

    Returns
    -------
    dict
        ``sections``: a list of ``{"title", "tables", "lines"}`` in order,
        the preamble titled ``title``; each table ``{"title", "columns",
        "rows", "lineno"}`` (cells unescaped and stripped, the title the
        nearest preceding level-3 heading or bold lead line, else ``table
        <k>``); ``lines`` the non-table lines as ``(lineno, text)`` pairs.
        Fenced code blocks are never parsed as tables.
    """
    sections: list[dict] = [{"title": "title", "tables": [], "lines": []}]
    in_fence = False
    table: list[tuple[int, str]] = []
    last_title: str | None = None

    def flush() -> None:
        nonlocal table
        if not table:
            return
        rows = [_split_cells(t) for _, t in table]
        columns = rows[0] if rows else []
        body = rows[2:] if len(rows) > 2 else []
        section = sections[-1]
        section["tables"].append({
            "title": last_title if last_title is not None else f"table {len(section['tables']) + 1}",
            "columns": columns, "rows": body, "lineno": table[0][0],
        })
        table = []

    for lineno, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            flush()
            in_fence = not in_fence
            sections[-1]["lines"].append((lineno, line))
            continue
        if in_fence:
            sections[-1]["lines"].append((lineno, line))
            continue
        if line.startswith("## "):
            flush()
            sections.append({"title": line[3:].strip(), "tables": [], "lines": [(lineno, line)]})
            last_title = None
            continue
        if line.startswith("|"):
            table.append((lineno, line))
            continue
        flush()
        if line.startswith("### "):
            last_title = line[4:].strip()
        elif line.startswith("**") and line.rstrip().endswith("**"):
            last_title = line.strip().strip("*").strip()
        sections[-1]["lines"].append((lineno, line))
    flush()
    return {"sections": sections}


def _table_index(section: dict) -> dict[str, dict]:
    """A section's tables by title (a repeated title gets ``#k``)."""
    out: dict[str, dict] = {}
    for t in section["tables"]:
        key = t["title"]
        k = 2
        while key in out:
            key = f"{t['title']} #{k}"
            k += 1
        out[key] = t
    return out


def _row_index(table: dict) -> dict[str, list[str]]:
    """A table's rows by first cell (a repeated key gets ``#k``)."""
    out: dict[str, list[str]] = {}
    for row in table["rows"]:
        key = row[0] if row else ""
        k = 2
        while key in out:
            key = f"{row[0]} #{k}"
            k += 1
        out[key] = row
    return out


def _compare_parsed(report: dict, generated: dict) -> list[str]:
    """Every difference between two parsed reports: tables cell by cell, other lines line by line (design D6)."""
    mismatches: list[str] = []
    r_sections = {s["title"]: s for s in report["sections"]}
    g_sections = {s["title"]: s for s in generated["sections"]}
    for title in g_sections:
        if title not in r_sections:
            mismatches.append(f"{title}: section absent from the report")
    for title in r_sections:
        if title not in g_sections:
            mismatches.append(f"{title}: section not generated")
    r_titles = [s["title"] for s in report["sections"] if s["title"] in g_sections]
    g_titles = [s["title"] for s in generated["sections"] if s["title"] in r_sections]
    if r_titles != g_titles:
        mismatches.append(f"section order: report {r_titles}, generated {g_titles}")
    for title, g in g_sections.items():
        r = r_sections.get(title)
        if r is None:
            continue
        r_tables, g_tables = _table_index(r), _table_index(g)
        for t in g_tables:
            if t not in r_tables:
                mismatches.append(f"{title} › table \"{t}\": absent from the report")
        for t in r_tables:
            if t not in g_tables:
                mismatches.append(f"{title} › table \"{t}\": not generated")
        for t, gt in g_tables.items():
            rt = r_tables.get(t)
            if rt is None:
                continue
            if rt["columns"] != gt["columns"]:
                mismatches.append(f"{title} › table \"{t}\" › columns: report {rt['columns']}, generated {gt['columns']}")
            r_rows, g_rows = _row_index(rt), _row_index(gt)
            for key in g_rows:
                if key not in r_rows:
                    mismatches.append(f"{title} › table \"{t}\" › row {key}: absent from the report")
            for key in r_rows:
                if key not in g_rows:
                    mismatches.append(f"{title} › table \"{t}\" › row {key}: not generated")
            for key, g_row in g_rows.items():
                r_row = r_rows.get(key)
                if r_row is None:
                    continue
                for j, column in enumerate(gt["columns"]):
                    a = r_row[j] if j < len(r_row) else None
                    bb = g_row[j] if j < len(g_row) else None
                    if a != bb:
                        mismatches.append(f"{title} › table \"{t}\" › row {key} › {column}: report {a!r}, generated {bb!r}")
        r_lines, g_lines = r["lines"], g["lines"]
        for (r_no, r_text), (_, g_text) in zip(r_lines, g_lines):
            if r_text != g_text:
                mismatches.append(f"{title} › line {r_no}: report {r_text!r}, generated {g_text!r}")
        if len(r_lines) > len(g_lines):
            extra = r_lines[len(g_lines):]
            mismatches.append(f"{title} › line {extra[0][0]}: the report has {len(extra)} line(s) more than generated, from {extra[0][1]!r}")
        elif len(g_lines) > len(r_lines):
            extra = g_lines[len(r_lines):]
            mismatches.append(f"{title}: the report has {len(extra)} line(s) fewer than generated, from {extra[0][1]!r}")
    return mismatches


def _parse_back(text: str, tables: dict[str, pd.DataFrame]) -> tuple[int, int]:
    """Parse a written report and check that its tables equal the generated frames; returns (tables, cells) parsed."""
    parsed = parse_report(text)
    found: dict[str, dict] = {}
    for section in parsed["sections"]:
        for title, t in _table_index(section).items():
            found[f"{section['title']} › {title}"] = t
    n_cells = 0
    for key, df in tables.items():
        t = found.get(key)
        if t is None:
            raise RuntimeError(f"parse-back: the written report has no table {key!r} (the parser or the renderer is defective)")
        if t["columns"] != [str(c) for c in df.columns]:
            raise RuntimeError(f"parse-back: table {key!r} columns differ: written {t['columns']}, generated {list(df.columns)}")
        rows = [list(r) for r in df.itertuples(index=False)]
        if t["rows"] != rows:
            raise RuntimeError(f"parse-back: table {key!r} rows differ after parsing (the parser or the renderer is defective)")
        n_cells += len(rows) * len(df.columns)
    if len(found) != len(tables):
        raise RuntimeError(f"parse-back: {len(found)} tables parsed, {len(tables)} generated")
    return len(tables), n_cells


#: The level-3 heading of each export variant's block in "Export sensitivity",
#: one per variant a report quotes, in its order: the variants it lists
#: (design D6 of ``adni-report-nmr-all-columns``).
_REPORT_VARIANT_HEADING_RE = re.compile(r"^### Export variant `([^`]+)`$")


def _check_report_layout(path: Path) -> str:
    """The report's text, after checking its layout (design D6 of ``adni-report-variants`` and ``adni-report-nmr-all-columns``).

    Its level-2 headings must be ``REPORT_SECTIONS`` in order; then the
    export variants it lists, its headings ``Export variant `<name>``` in
    "Export sensitivity" in order (``_REPORT_VARIANT_HEADING_RE``), must be
    ``REPORT_EXPORT_VARIANTS``. A report written by an earlier layout of
    ``report`` (the reports of 2026-10-28, 2026-10-29 and 2026-10-30 by
    their sections, the report of 2026-10-31 by its two export variants)
    stops the check before any input gate and before any comparison,
    naming the report, the sections or variants it lacks and adds (or that
    their order differs), and how to find the revision that committed it,
    where it checks; nothing is written.
    """
    text = path.read_text()
    parsed = parse_report(text)
    titles = [section["title"] for section in parsed["sections"][1:]]
    hint = (
        f"It checks at the revision that committed it: `git log -1 --format=%H -- {path}`, then `adni-sexdiff report "
        f"--check --out {path}` in a worktree of that revision (`git worktree add <dir> <revision>`); no cell was compared; "
        "nothing was written"
    )

    def stop(what: str, expected: Sequence[str], found: list[str]) -> None:
        absent = [t for t in expected if t not in found]
        extra = [t for t in found if t not in expected]
        raise RuntimeError(
            f"{path} was written by an earlier layout of `report`: {what} (absent: "
            + (", ".join(repr(t) for t in absent) or "none") + "; extra: " + (", ".join(repr(t) for t in extra) or "none")
            + ("" if absent or extra else "; the order differs") + f"). {hint}"
        )

    if titles != list(REPORT_SECTIONS):
        stop("its level-2 sections are not REPORT_SECTIONS", REPORT_SECTIONS, titles)
    section = next(s for s in parsed["sections"] if s["title"] == "Export sensitivity")
    listed = [m.group(1) for _, line in section["lines"] if (m := _REPORT_VARIANT_HEADING_RE.match(line))]
    if listed != list(REPORT_EXPORT_VARIANTS):
        stop("its export variants are not REPORT_EXPORT_VARIANTS", REPORT_EXPORT_VARIANTS, listed)
    return text


def check_report(path: str | Path, inputs: dict, *, log: str = "[report]") -> dict:
    """Compare an existing report with the one the inputs generate (design D6 of ``adni-report``); writes nothing.

    A report whose level-2 headings are not ``REPORT_SECTIONS`` in order, or
    whose export variants are not ``REPORT_EXPORT_VARIANTS``, stops first
    (``_check_report_layout``).

    Parameters
    ----------
    path:
        The report; the date is read from its name.
    inputs:
        ``_load_report_inputs`` (its gates have run).
    log:
        The progress prefix.

    Returns
    -------
    dict
        ``path``, ``tables`` (the generated frames), ``checked`` ``True`` and
        ``mismatches``: one string per difference (section, table, row key
        and column with both values; or section and line with both texts;
        or an absent or extra section, table, row or line).
    """
    path = Path(path)
    date = _report_date(path)
    text = _check_report_layout(path)
    generated, tables = render_report(inputs, date=date)
    report_parsed, generated_parsed = parse_report(text), parse_report(generated)
    mismatches = _compare_parsed(report_parsed, generated_parsed)
    n_tables = sum(len(s["tables"]) for s in generated_parsed["sections"])
    n_cells = sum(len(t["rows"]) * len(t["columns"]) for s in generated_parsed["sections"] for t in s["tables"])
    n_lines = sum(len(s["lines"]) for s in generated_parsed["sections"])
    for msg in mismatches:
        print(f"{log} MISMATCH: {msg}")
    if mismatches:
        print(f"{log} {path}: {len(mismatches)} mismatch(es) against the generated report ({n_tables} tables, {n_cells} cells, {n_lines} other lines compared); nothing was written")
    else:
        print(f"{log} {path}: {n_tables} tables, {n_cells} cells and {n_lines} other lines compared; no mismatch; nothing was written")
    return {"path": path, "tables": tables, "checked": True, "mismatches": mismatches}


def _newest_report(reports_dir: Path) -> Path:
    """The newest ``REPORT_NAME`` under ``reports_dir`` by the date in its name; stops naming the directory and the pattern."""
    candidates = [(m.group(1), p) for p in reports_dir.glob("*") if (m := _REPORT_NAME_RE.match(p.name)) and p.is_file()]
    if not candidates:
        raise FileNotFoundError(
            f"{reports_dir} holds no report matching {REPORT_NAME.format(date='<YYYY-MM-DD>')}; pass --out or write one with "
            "`adni-sexdiff report`"
        )
    return max(candidates)[1]


def run_report(
    *,
    cleaned_dir: str | Path | None = None,
    cohort_dir: str | Path | None = None,
    input_dir: str | Path | None = None,
    analysis_dir: str | Path | None = None,
    diagnostics_dir: str | Path | None = None,
    sensitivity_dir: str | Path | None = None,
    export_sensitivity_dir: str | Path | None = None,
    stage_sensitivity_dir: str | Path | None = None,
    rank_sensitivity_dir: str | Path | None = None,
    out: str | Path | None = None,
    check: bool = False,
    force: bool = False,
) -> dict:
    """Write the case-study report from the kept aggregate outputs, or check an existing one against them.

    Parameters
    ----------
    cleaned_dir:
        Output root of ``clean`` (default ``constants.CLEANED_DIR``); the two
        ``clean_manifest.json`` are read.
    cohort_dir:
        Output directory of ``cohort`` (default ``constants.COHORT_DIR``);
        ``stage_counts.csv`` and ``cohort_manifest.json`` are read.
    input_dir:
        Output directory of ``export`` (default ``constants.MOTCO_INPUT_DIR``);
        ``manifest.json`` is read.
    analysis_dir:
        The primary's analysis directory (default
        ``constants.MOTCO_ANALYSIS_DIR``); ``result.json``,
        ``analysis_manifest.json`` and ``summary.md`` are read.
    diagnostics_dir:
        The primary's diagnostics (default ``constants.DIAGNOSTICS_DIR``); its
        six files are read.
    sensitivity_dir:
        The root of the sensitivity step (default
        ``constants.LATENT_SENSITIVITY_DIR``), read through
        ``LATENT_SENSITIVITY_SUBDIRS``: the arm's three aggregate analysis
        files, the comparison's three files and the arm diagnostics' six.
    export_sensitivity_dir:
        The root of ``export-sensitivity`` (default
        ``constants.EXPORT_SENSITIVITY_DIR``), read per variant of
        ``REPORT_EXPORT_VARIANTS`` through ``EXPORT_SENSITIVITY_SUBDIRS``: the
        bridge table (hook ``factors``), the variant export's manifest, the
        variant analysis' three aggregate files, the comparison's three files
        and the variant diagnostics' six. Every variant of the pin is
        required (all three registered variants since change
        ``adni-report-nmr-all-columns``); a variant registered later and
        left outside it is not read, and a progress line names it.
    stage_sensitivity_dir:
        The root of ``stage-sensitivity`` (default
        ``constants.STAGE_SENSITIVITY_DIR``), read through
        ``STAGE_SENSITIVITY_SUBDIRS`` (``REPORT_STAGE_ARM_FILES``): the CN /
        LMCI / AD arm export's manifest, the arm analysis' three aggregate
        files, the comparison's three files and the arm diagnostics' six.
        The arm is required.
    rank_sensitivity_dir:
        The root of ``rank-sensitivity`` (default
        ``constants.RANK_SENSITIVITY_DIR``), read per rank of
        ``RANK_SENSITIVITY_LADDER`` through ``RANK_SENSITIVITY_RANK_DIR`` and
        then through ``RANK_SENSITIVITY_SUBDIRS`` (``REPORT_RANK_SWEEP_FILES``):
        each rank's three aggregate analysis files, the comparison's three
        files and the top rank's diagnostics' six. The sweep is required.
    out:
        The report path, whose name must match ``constants.REPORT_NAME``
        (``reports/motco-adni-<date>.md``); the date is read from it. Write
        mode defaults to today's date; ``check`` to the newest report under
        ``constants.REPORTS_DIR`` by the date in its name.
    check:
        Instead of writing, read the report at ``out``, run every gate,
        regenerate the report and compare every table cell by cell and every
        other line line by line; every mismatch is named (section, table,
        row key, column, both values; or the line with both texts) and the
        CLI exits non-zero on any. A report written by an earlier layout,
        whose level-2 headings are not ``REPORT_SECTIONS`` or whose export
        variants (its ``Export variant `<name>``` headings) are not
        ``REPORT_EXPORT_VARIANTS`` (change ``adni-report-nmr-all-columns``:
        the report of 2026-10-31, which checks at 13ce7c8), stops before any
        gate, naming its absent and extra sections or variants and how to
        find the revision that committed it, where it checks. Nothing is
        written.
    force:
        Replace an existing report at ``out`` (write mode).

    Returns
    -------
    dict
        ``{"path": Path, "tables": {name: DataFrame}, "checked": bool, "mismatches": [...]}``;
        ``tables`` holds every table the report prints, as frames of
        strings keyed ``"<section> › <title>"``.

    Notes
    -----
    Inputs are the 106 kept aggregate files of ``REPORT_INPUT_FILES`` (33
    manifests) and nothing else: no participant-level file is opened or
    required, and the hashes the report quotes for one are the values the
    manifests record. So the step runs on any clone with the committed
    tree, needs no data root, no MOTCO call and no pinned numeric
    environment, and records no numerics. Gates (``_load_report_inputs``),
    before anything is written and each naming the file or setting, both
    values and the step to rerun: every input present; every aggregate file
    hashes to the value its own manifest records (the bridge table to its
    variant export manifest's ``bridge.table.sha256``); the primary is the
    primary, the arm is ``LATENT_SENSITIVITY_ARM``, each variant directory
    of ``REPORT_EXPORT_VARIANTS`` holds its ``EXPORT_VARIANTS`` entry, the CN / LMCI / AD arm is
    ``STAGE_SENSITIVITY_ARM`` (not crossed with an export variant or the
    latent adjustment) and the rank sweep is ``RANK_SENSITIVITY_LADDER``
    (each rank directory holds its rank, every rank records the ladder and
    the primary record's rank, no rank is crossed, the comparison's anchor
    is equal at the primary's rank, the diagnostics read the top rank);
    the primary, the arm, every variant analysis, the CN / LMCI / AD arm's
    analysis and every rank are reported runs (``n_jobs =
    REPORTED_N_JOBS``), every ``numerics`` block present is pinned and
    every manifest records the same MOTCO, scikit-learn and metabo_adni
    versions; the chain holds link by link (189 links on the committed
    tree: 31, then 23, 22 and 22 for the three variants, 24 for the CN /
    LMCI / AD arm, then 67 for the rank sweep) from the clean manifests to the arm's, every variant's, the CN /
    LMCI / AD arm's and the rank sweep's diagnostics, the primary feature
    tables the arm export names as the source of its floors included.
    Write mode also stops on an existing ``out`` without ``force``.

    Output contract (``render_report``): one Markdown file with the
    thirteen sections of ``REPORT_SECTIONS`` in order (summary; provenance;
    cohort; export; primary analysis; axis diagnostics of the primary;
    latent-adjustment sensitivity; export sensitivity, one group of tables
    per rule set of the pinned variants, each holding the primary and its
    group's variants only; stage-definition sensitivity; rank sensitivity;
    findings; reading rules; reproduction),
    every table titled by a level-3 heading and keyed by its first column,
    every number copied from a record, a manifest or a CSV at the digits of
    the summary it belongs to, every reading sentence produced by
    ``_statistic_reading_line``, ``_arm_status_line``,
    ``_export_variant_status_line``, ``_stage_arm_status_line`` and
    ``_rank_status_line`` (the code of ``summary.md``,
    ``latent_sensitivity.md``, ``export_sensitivity.md``,
    ``stage_sensitivity.md`` and ``rank_sensitivity.md``), the variant lines
    by ``_export_variant_lines``, the CN / LMCI / AD arm's bullets and
    definition tables by ``_stage_arm_lines`` and ``_stage_arm_tables``, the
    sweep's anchor and nesting bullets and nesting table by
    ``_rank_anchor_lines`` and ``_rank_nesting_table``, every word that
    depends on an export variant from ``_variant_words``, six rule lists
    verbatim: ``READING_RULES``, then ``LATENT_SENSITIVITY_READING_RULES``,
    then one per rule set of the pinned variants in group order
    (``EXPORT_VARIANT_READING_RULES``, ``NMR_MEMBERSHIP_READING_RULES``),
    then ``STAGE_SENSITIVITY_READING_RULES``, then
    ``RANK_SENSITIVITY_READING_RULES``, the arm's, each variant group's,
    the CN / LMCI / AD arm's and the sweep's constants named beside every
    table that quotes them, no sentence reading one sensitivity against
    another, and the primary's status the result in every table. The body depends on
    the inputs and the file name only (the date is in the name and the
    title line; no revision,
    host, time or runtime of the report run is written), so two runs on the
    same inputs are byte-identical. The file is written to ``<out>.tmp``,
    parsed back through ``parse_report`` and checked against the generated
    tables, then renamed; no temporary file remains. The report quotes
    aggregate values only and holds no participant identifier; ``reports/``
    is committed. Findings, never stops (printed and listed under
    "Findings"): every deviation and finding of every input manifest,
    verbatim under its step; a manifest whose recorded revision is dirty; a
    manifest without a ``numerics`` block.
    """
    log = "[report]"
    reports_dir = Path(REPORTS_DIR)
    if check:
        out_path = Path(out) if out is not None else _newest_report(reports_dir)
        if not out_path.is_file():
            raise FileNotFoundError(f"{out_path} does not exist; nothing to check (write one with `adni-sexdiff report`)")
        date = _report_date(out_path)
        _check_report_layout(out_path)
        print(
            f"{log} checking {out_path} (date {date} from its name; its sections are REPORT_SECTIONS and its export variants "
            "REPORT_EXPORT_VARIANTS)"
        )
    else:
        out_path = Path(out) if out is not None else reports_dir / REPORT_NAME.format(date=date_type.today().isoformat())
        date = _report_date(out_path)
        if out_path.exists() and not force:
            raise FileExistsError(f"{out_path} exists; pass --force to replace it; nothing was written")
    for variant in EXPORT_VARIANTS:
        if variant not in REPORT_EXPORT_VARIANTS:
            # the report's pin (design D6 of adni-nmr-all-columns): named here, never in the body
            print(
                f"{log} export variant {variant} (change {EXPORT_VARIANTS[variant]['change']}) is registered and not "
                "covered by this report (REPORT_EXPORT_VARIANTS): it is not read, and a report change adds it"
            )
    inputs = _load_report_inputs(
        cleaned_dir=cleaned_dir, cohort_dir=cohort_dir, input_dir=input_dir, analysis_dir=analysis_dir,
        diagnostics_dir=diagnostics_dir, sensitivity_dir=sensitivity_dir, export_sensitivity_dir=export_sensitivity_dir,
        stage_sensitivity_dir=stage_sensitivity_dir, rank_sensitivity_dir=rank_sensitivity_dir, log=log,
    )
    if check:
        return check_report(out_path, inputs, log=log)
    text, tables = render_report(inputs, date=date)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_name(out_path.name + ".tmp")
    try:
        tmp.write_text(text)
        n_tables, n_cells = _parse_back(tmp.read_text(), tables)
        if out_path.exists() and not force:
            raise FileExistsError(f"{out_path} appeared during the run; nothing was written")
        os.replace(tmp, out_path)
    finally:
        tmp.unlink(missing_ok=True)
    n_generated = sum(len(df) * len(df.columns) for df in tables.values())
    print(
        f"{log} wrote {out_path}: {len(REPORT_SECTIONS)} sections, {len(tables)} tables, {n_generated} cells; parsed back "
        f"{n_tables} tables, {n_cells} cells, equal to the generated ones"
    )
    print(f"{log} next: `adni-sexdiff report --check --out {out_path}` on the clean tree, then commit the report alone")
    return {"path": out_path, "tables": tables, "checked": False, "mismatches": []}


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
    "render_axis_diagnostics",
    "spearman",
    "partial_spearman",
    "block_principal_components",
    "geometry_shares",
    "block_loading_shares",
    "run_clean",
    "run_cohort",
    "run_export",
    "run_analysis",
    "run_axis_diagnostics",
    "render_latent_sensitivity",
    "run_latent_sensitivity",
    "render_report",
    "parse_report",
    "check_report",
    "run_report",
]
