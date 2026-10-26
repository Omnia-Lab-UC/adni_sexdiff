"""Pipeline steps of adni_sexdiff.

Every step is a stub: its docstring states the inputs it reads, the files it
writes and the contract of those files, and its body raises
``NotImplementedError`` until an OpenSpec change implements it. The
statistical choices each step needs (cohort rule, stage rule, covariate set,
permutations, seed, rank floor, metabo_adni options, reading rules) are
undecided and enter only through a proposal (see ``constants``).

ADNI is controlled-access. Every table keyed by ``RID`` is participant-level:
it stays under the ignored paths of ``constants.PARTICIPANT_LEVEL_PATTERNS``,
is never printed, never synced and never quoted. Progress output names
counts and files, never participants.
"""

from __future__ import annotations

import os
from pathlib import Path

from .constants import DATA_ROOT_ENV, DEFAULT_DATA_ROOT, PLATFORMS


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
        constant moved apart).
    """
    raise NotImplementedError("check_metabo_adni_version is a stub; implemented by the clean change")


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
        ``"p180"``, ``"nmr"`` or ``"all"`` (``constants.PLATFORMS``).
    data_root:
        Directory holding the raw ADNI files under their original LONI
        names, as metabo_adni's ``load.read_files`` expects them (p180:
        ``ADMCDUKEP180UPLC_01_15_16.csv``, ``ADMCDUKEP180FIA_01_15_16.csv``,
        ``ADMCDUKEP180UPLCADNI2GO.csv``, ``ADMCDUKEP180FIAADNI2GO.csv`` plus
        the p180 LOD workbooks its ``read_lod_files`` names; NMR:
        ``ADNINIGHTINGALE2.csv``; both: the fasting file ``BIOMARK.csv``;
        ``ADMCPATIENTDRUGCLASSES_20170512.csv`` only if ``--residualize-meds``
        is chosen). Resolved by ``resolve_data_root``.
    out_dir:
        Cleaned root (default ``constants.CLEANED_DIR``); each platform goes
        to ``<out_dir>/<platform>/``.
    force:
        Replace an existing platform directory.

    Returns
    -------
    dict
        Platform → ``{"dir": Path, "files": {name: Path}, "manifest": dict}``.

    Notes
    -----
    Cleaning is metabo_adni's (``metabo_adni==0.5.8``, pinned; the installed
    version is checked by ``check_metabo_adni_version`` before any file is
    read) and is never reimplemented here: the step runs metabo_adni's
    ``clean_files`` pipeline with the options of the (undecided) constant
    ``CLEAN_OPTIONS`` for the platform, in a working copy, since metabo_adni
    changes into the data directory and writes its cleaned files there.
    Output contract per platform: metabo_adni's cleaned files under the
    names it gives them (``<cohort>-<kit>.csv`` for p180, ``NMR.csv`` for
    NMR; participant × metabolite, keyed by ``RID``, participant-level and
    gitignored) and ``clean_manifest.json`` (metabo_adni and software
    versions, the options used, every input file with its sha256, the
    participant and metabolite counts before and after each of metabo_adni's
    steps, git revision, findings). The manifest is aggregate and holds no
    ``RID``. Each platform is written to ``<platform>.tmp/`` and renamed when
    complete.
    """
    raise NotImplementedError("run_clean is a stub; implemented by the clean change")


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
        Output root of ``clean`` (default ``constants.CLEANED_DIR``); every
        platform directory and its manifest are read.
    data_root:
        Directory holding the ADNI clinical tables the cohort rule names
        (diagnosis, demographics, the covariates' sources), uploaded by hand
        with their original names. Resolved by ``resolve_data_root``.
    out_dir:
        Cohort directory (default ``constants.COHORT_DIR``).
    force:
        Replace an existing cohort directory.

    Returns
    -------
    dict
        ``{"dir": Path, "counts": DataFrame, "manifest": dict, "findings": [...]}``.

    Notes
    -----
    Applies the (undecided) constants ``COHORT_RULE`` (the baseline visit per
    participant, the platform intersection, exclusions), ``STAGE_RULE`` (the
    ADNI diagnosis → ``STAGE_LABELS`` mapping, with its merging of subtypes)
    and ``ANALYSIS_COVARIATES`` (sources and coding; nothing imputed, missing
    values listed in the manifest). Output contract: ``cohort.csv`` (one row
    per participant: ``rid``, ``sex``, ``stage``, the covariates, the visit
    used, a presence flag per platform; participant-level and gitignored),
    ``stage_counts.csv`` (sex × stage counts per platform and for the
    intersection; aggregate, the only committed table) and
    ``cohort_manifest.json`` (the rules as applied, input file hashes incl.
    the clean manifests, counts at every exclusion, software, git revision,
    findings; no ``RID``). Deviations from the counts the proposal
    predeclares go to ``findings``, never silently.
    """
    raise NotImplementedError("run_cohort is a stub; implemented by the cohort change")


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
    ``STAGE_LABELS`` order, with the (undecided) constants
    ``ANALYSIS_COVARIATES`` (missing policy ``error``, nothing imputed),
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
    "check_metabo_adni_version",
    "check_motco_version",
    "run_clean",
    "run_cohort",
    "run_export",
    "run_analysis",
    "run_axis_diagnostics",
    "run_report",
]
