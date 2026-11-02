"""Named constants of the adni_sexdiff pipeline.

Two kinds of constant live here.

Conventions
    Paths, environment variables, platform and column names, output file
    names, version pins, the reporting rules of ``AGENTS.md`` and the pinned
    numeric environment (``NUMERIC_SETTINGS``, change
    ``adni-portable-numerics``). They are defined below and may be changed by
    an ordinary change. This module imports nothing but ``__future__``, so
    the package can read ``NUMERIC_SETTINGS`` before numpy loads.

Scientific constants
    Statistical choices are scientific decisions. Each enters this module
    only through an OpenSpec proposal that states it before any run, becomes
    a named constant here, and is listed under "Flag and ask" in
    ``AGENTS.md``. Decided so far: ``CLEAN_OPTIONS`` (metabo_adni's QC
    cutoffs, merge and transforms per platform), by the change
    ``adni-metabolomics-clean``; ``COHORT_RULE`` (the clinical table, the
    baseline row and baseline sample per participant, the platform
    intersection), ``STAGE_RULE`` (``DX.bl`` onto ``STAGE_LABELS``, subtypes
    merged) and ``ANALYSIS_COVARIATES`` (set, order, sources and coding), by
    the change ``adni-cohort``; ``EXPORT_FEATURE_RULE`` (which cleaned
    metabolites enter each block, by family, and on which scale), by the
    change ``adni-export``; ``ANALYSIS_PERMUTATIONS``, ``ANALYSIS_SEED``,
    ``ANALYSIS_ALPHA`` with ``ANALYSIS_REJECTION_RULE``,
    ``ANALYSIS_RANK_FLOOR``, ``ANALYSIS_LATENT_ADJUSTMENT`` (the primary's
    measurement settings, with the ``stage``-conditioned latent adjustment
    predeclared as a sensitivity arm of the change
    ``adni-latent-sensitivity``) and ``READING_RULES`` (the binding reading
    rules every reader of the result carries), by the change
    ``adni-analyze``; ``DIAGNOSTIC_VARIABLES`` (the eight variables the axis
    diagnostics correlate the latent and block axes with, their sources and
    codings) and ``DIAGNOSTIC_CORRELATION_THRESHOLD`` (the reporting flag on
    |rho|, never an adoption rule), by the change ``adni-axis-diagnostics``;
    ``LATENT_SENSITIVITY_ARM`` (the single ``stage``-conditioned
    latent-adjustment arm, tied to ``ANALYSIS_PREDECLARED_LATENT_SENSITIVITY``
    by an import-time assertion), ``LATENT_SENSITIVITY_COVARIATE_ROLES``
    (each covariate's relation to the stage effect, ``statin`` the mediator
    candidate) and ``LATENT_SENSITIVITY_READING_RULES`` (the nine statements
    every reader of the arm carries after ``READING_RULES``), by the change
    ``adni-latent-sensitivity``, with the predeclared
    ``LATENT_SENSITIVITY_EXPECTED_COUNTS`` and the conventions
    ``LATENT_SENSITIVITY_DIR``, ``LATENT_SENSITIVITY_SUBDIRS``,
    ``LATENT_SENSITIVITY_TABLE``, ``LATENT_SENSITIVITY_SUMMARY`` and
    ``LATENT_SENSITIVITY_MANIFEST``; ``EXPORT_VARIANTS`` (the registry of
    export variants that change only how the p180 assay run is handled:
    ``nist_bridge`` and ``per_run_standardized``), ``NIST_BRIDGE_RULE`` (the
    NIST SRM 1950 material, the valid replicate, the half-valid inclusion,
    the factor ``b``, the reference run and the kits) and
    ``EXPORT_VARIANT_READING_RULES`` (the seven statements every reader of a
    variant carries after ``READING_RULES``), by the change
    ``adni-nist-bridge``, with the predeclared
    ``EXPORT_VARIANT_EXPECTED_COUNTS`` and ``NIST_BRIDGE_WORKBOOK_SHA256``
    and the conventions ``EXPORT_SENSITIVITY_DIR``,
    ``EXPORT_SENSITIVITY_SUBDIRS`` and the output names;
    ``STAGE_SENSITIVITY_ARM`` (the single CN / LMCI / AD arm ``cn_lmci_ad``:
    the exported participants whose ``DX.bl`` is CN, LMCI or AD, staged by
    ``STAGE_RULE``'s own map, the primary export's rows and floors, the
    primary's analysis settings; tied to ``STAGE_RULE`` by three import-time
    assertions) and ``STAGE_SENSITIVITY_READING_RULES`` (the eight statements
    every reader of the arm carries after ``READING_RULES``), by the change
    ``adni-stage-sensitivity``, with the predeclared
    ``STAGE_SENSITIVITY_EXPECTED_COUNTS`` and the conventions
    ``STAGE_SENSITIVITY_DIR``, ``STAGE_SENSITIVITY_SUBDIRS`` and the output
    names; ``RANK_SENSITIVITY_LADDER`` (the single forced-rank ladder
    ``forced_rank_ladder``: ranks 2, 3, 4, 6, 9 and 12, the one setting
    ``forced_components``, the same seed and permutations at every rank, the
    anchor at the primary record's rank, the top rank diagnosed, every other
    setting the primary's; ordered and tied to ``ANALYSIS_RANK_FLOOR`` by three
    import-time assertions) and ``RANK_SENSITIVITY_READING_RULES`` (the eight
    statements every reader of the sweep carries after ``READING_RULES``), by
    the change ``adni-rank-sensitivity``, with the predeclared
    ``RANK_SENSITIVITY_EXPECTED_COUNTS`` and the conventions
    ``RANK_SENSITIVITY_DIR``, ``RANK_SENSITIVITY_RANK_DIR``,
    ``RANK_SENSITIVITY_SUBDIRS`` and the output names; the ``EXPORT_VARIANTS``
    entry ``nmr_all_columns`` (every cleaned NMR column in the block, the 80
    the feature rule marks ``derived`` among them, each on the rule's scale
    with its own floor; hook ``membership``), ``NMR_MEMBERSHIP_READING_RULES``
    (the eight statements every reader of that variant carries after
    ``READING_RULES``, in place of ``EXPORT_VARIANT_READING_RULES``) and its
    dependence label ``feature-membership dependence``, by the change
    ``adni-nmr-all-columns``, with the predeclared
    ``EXPORT_VARIANT_EXPECTED_COUNTS["nmr_all_columns"]`` (``analysis`` and
    ``diagnostics`` among its keys) and the conventions
    ``EXPORT_VARIANT_RULE_SETS`` (per variant its rules, citation word and
    dependence label; tied to ``EXPORT_VARIANTS`` by two import-time
    assertions) and ``REPORT_EXPORT_VARIANTS`` (the variants the report
    covers; a subsequence of the registry by an import-time assertion);
    ``SCALE_VARIANT_RULE`` (per scale variant the transform of a kept cell
    and its offset: ``x``, ``log2(x + 1)``, and the generalized log with λ per
    metabolite its smallest positive value over the exported participants
    divided by 10), the ``EXPORT_VARIANTS`` entries ``raw_scale``,
    ``log2_plus_one`` and ``glog`` (block ``all``, hook ``scale``: both blocks
    on the variant's scale, the primary's membership, the rule's floors
    recorded and not applied), ``SCALE_VARIANT_READING_RULES`` (the eight
    statements every reader of a scale variant carries after
    ``READING_RULES``, in place of ``EXPORT_VARIANT_READING_RULES``) and their
    dependence label ``scale dependence``, by the change
    ``adni-scale-variants``, with the predeclared
    ``EXPORT_VARIANT_EXPECTED_COUNTS`` of the three (``analysis`` among their
    keys, no ``diagnostics``) and their shared ``EXPORT_VARIANT_RULE_SETS``
    entry. Every scientific constant the six steps and the four sensitivity
    steps need is decided; a later variant or arm introduces its own by
    proposal. The changes
    ``adni-report`` (the ``report`` step), ``adni-report-variants`` (the
    report extended to every export variant), ``adni-report-stage-arm``
    (the report extended to the CN / LMCI / AD arm),
    ``adni-report-rank-sweep`` (the report extended to the rank sweep),
    ``adni-report-nmr-all-columns`` (``nmr_all_columns`` added to
    ``REPORT_EXPORT_VARIANTS``) and ``adni-report-scale-variants``
    (``raw_scale``, ``log2_plus_one`` and ``glog`` added to it, so the report
    covers every registered variant) introduce no scientific constant: their
    conventions ``REPORT_STAGE_ARM_FILES``, ``REPORT_RANK_SWEEP_FILES``,
    ``REPORT_INPUT_FILES`` (every file the step reads, by directory role; 145
    with the six variants of ``REPORT_EXPORT_VARIANTS``, the CN / LMCI / AD
    arm and the rank sweep) and
    ``REPORT_SECTIONS`` (the report's thirteen section titles, in order) are
    defined below, and the report quotes every setting by constant name from
    the manifests and every number from the records.
"""

from __future__ import annotations

# --- Data root -------------------------------------------------------------

#: Environment variable naming the data root; the default is ``data/``.
#: Raw ADNI files are uploaded by hand into it (there is no download step).
DATA_ROOT_ENV = "ADNI_DATA_ROOT"
#: Data root when neither a flag nor ``DATA_ROOT_ENV`` is set.
DEFAULT_DATA_ROOT = "data"

# --- Platforms and columns -------------------------------------------------

#: The metabolomics platforms, as metabo_adni names them (``-P``). Each is
#: one MOTCO block; later ADNI layers are added as blocks by a proposal.
PLATFORMS: tuple[str, ...] = ("p180", "nmr")
#: ADNI's participant key. Any table holding it is participant-level.
PARTICIPANT_ID_COLUMN = "RID"
#: Metadata columns of the MOTCO export (``metadata.csv``), in this order.
SAMPLE_COLUMN = "rid"
GROUP_COLUMN = "sex"
STAGE_COLUMN = "stage"
#: The stages of the design, in trajectory order. The rule that assigns a
#: participant to one of them is ``STAGE_RULE``.
STAGE_LABELS: tuple[str, ...] = ("CN", "MCI", "AD")

# --- Output directories ----------------------------------------------------

RESULTS_DIR = "results"
CLEANED_DIR = "results/cleaned"
COHORT_DIR = "results/cohort"
MOTCO_INPUT_DIR = "results/motco_input"
MOTCO_ANALYSIS_DIR = "results/motco_analysis"
DIAGNOSTICS_DIR = "results/motco_diagnostics"
#: The output root of ``export-sensitivity`` (change ``adni-nist-bridge``):
#: one directory per variant of ``EXPORT_VARIANTS``, laid out as
#: ``EXPORT_SENSITIVITY_SUBDIRS``.
EXPORT_SENSITIVITY_DIR = "results/motco_export_sensitivity"
#: The output root of ``stage-sensitivity`` (change ``adni-stage-sensitivity``),
#: laid out as ``STAGE_SENSITIVITY_SUBDIRS``.
STAGE_SENSITIVITY_DIR = "results/motco_stage_sensitivity"
#: The output root of ``rank-sensitivity`` (change ``adni-rank-sensitivity``):
#: one analysis directory per rank of ``RANK_SENSITIVITY_LADDER``
#: (``RANK_SENSITIVITY_RANK_DIR``), laid out as ``MOTCO_ANALYSIS_DIR``, and
#: ``RANK_SENSITIVITY_SUBDIRS``.
RANK_SENSITIVITY_DIR = "results/motco_rank_sensitivity"
REPORTS_DIR = "reports"

# --- Output file names -----------------------------------------------------

#: ``clean``: metabo_adni's cleaned files land in ``<CLEANED_DIR>/<platform>/``
#: with the names metabo_adni gives them; the manifest sits beside them.
CLEAN_MANIFEST = "clean_manifest.json"
#: ``cohort``: the participant table (participant-level) and the aggregate
#: group × stage counts.
COHORT_TABLE = "cohort.csv"
COHORT_COUNTS = "stage_counts.csv"
COHORT_MANIFEST = "cohort_manifest.json"
#: ``export``: one block per platform (``<platform>.csv``), the metadata and
#: covariate tables, a feature table per platform and the manifest.
EXPORT_METADATA = "metadata.csv"
EXPORT_COVARIATES = "covariates.csv"
EXPORT_FEATURES = "features_{platform}.csv"
EXPORT_MANIFEST = "manifest.json"
#: ``analyze``: MOTCO's artifact plus this package's three files.
ANALYSIS_RESULT = "result.json"
ANALYSIS_LATENT_SCORES = "latent_scores.csv"
ANALYSIS_PLS_LOADINGS = "pls_loadings.csv"
ANALYSIS_STAGE_MEANS = "stage_means.csv"
ANALYSIS_METADATA = "analysis_metadata.csv"
ANALYSIS_MANIFEST = "analysis_manifest.json"
ANALYSIS_SUMMARY = "summary.md"
#: ``axis-diagnostics``.
DIAGNOSTICS_AXIS_CORRELATIONS = "axis_correlations.csv"
DIAGNOSTICS_BLOCK_PCS = "block_pcs.csv"
DIAGNOSTICS_GEOMETRY_SHARES = "geometry_shares.csv"
DIAGNOSTICS_COMPONENTS = "components.csv"
DIAGNOSTICS_SUMMARY = "diagnostics.md"
DIAGNOSTICS_MANIFEST = "diagnostics_manifest.json"
#: ``report``: ``<REPORTS_DIR>/motco-adni-<date>.md``, named by the day it is
#: written; a later report of the same day takes an ordinal, 2 or more
#: (``REPORT_NAME_SAME_DAY``; change ``adni-report-scale-variants``, design
#: D11), so no report is written over a committed one.
REPORT_NAME = "motco-adni-{date}.md"
REPORT_NAME_SAME_DAY = "motco-adni-{date}-{n}.md"
assert REPORT_NAME_SAME_DAY == REPORT_NAME.replace("{date}", "{date}-{n}"), (
    "REPORT_NAME_SAME_DAY must be REPORT_NAME with the ordinal after the date"
)

# --- Controlled access -----------------------------------------------------

#: Outputs that are participant-level, as path patterns relative to the
#: repository root. They are never committed, never synced between machines
#: and never quoted. ``.gitignore`` and ``scripts/sync_results.sh`` carry the
#: same list; a change that adds a participant-level output extends all
#: three. Everything not matched here is aggregate.
PARTICIPANT_LEVEL_PATTERNS: tuple[str, ...] = (
    "data/**",
    f"{CLEANED_DIR}/**",
    f"{COHORT_DIR}/{COHORT_TABLE}",
    f"{MOTCO_INPUT_DIR}/**/*.csv",
    # each export variant's MOTCO input (``EXPORT_SENSITIVITY_SUBDIRS["export"]``),
    # its feature tables with it, as the primary's
    f"{EXPORT_SENSITIVITY_DIR}/*/motco_input/*.csv",
    # the CN / LMCI / AD arm's MOTCO input (``STAGE_SENSITIVITY_SUBDIRS["export"]``):
    # the primary export's rows of the participants it keeps
    f"{STAGE_SENSITIVITY_DIR}/motco_input/*.csv",
    f"{RESULTS_DIR}/**/{ANALYSIS_LATENT_SCORES}",
    f"{RESULTS_DIR}/**/{ANALYSIS_METADATA}",
)
#: Exceptions to ``PARTICIPANT_LEVEL_PATTERNS``: aggregate files that a
#: pattern above would otherwise match.
AGGREGATE_EXCEPTIONS: tuple[str, ...] = (
    f"{CLEANED_DIR}/*/{CLEAN_MANIFEST}",
    f"{MOTCO_INPUT_DIR}/**/*manifest*",
)

# --- Software pins and reporting rules ------------------------------------

#: The exact metabo_adni release the lock holds; ``clean`` refuses any other.
METABO_ADNI_VERSION = "0.5.8"
#: MOTCO's release tag in ``pyproject.toml``; ``analyze`` refuses an older one.
ANALYSIS_MOTCO_MIN_VERSION = "0.10.0"
#: Reported runs use one worker: MOTCO seeds one RRPP stream per worker, so
#: another ``n_jobs`` changes the permutation draws.
REPORTED_N_JOBS = 1
#: The pinned numeric environment (change ``adni-portable-numerics``): with
#: it, every machine computes the same bits from the same inputs, so the hash
#: chain between steps holds whichever machine runs them. Importing the
#: package sets these variables before numpy loads; every manifest records
#: the state the process actually had (``numerics``). Measured on 2026-10-28
#: on an AVX-512 machine against outputs made on one without it: unpinned,
#: ``export``, ``analyze`` and the block SVD differed at about 1e-15; pinned,
#: every committed output reproduced, on 24 CPUs and on 1.
NUMERIC_SETTINGS: dict[str, str] = {
    # numpy's AVX-512 dispatch: its AVX-512 ``log2`` differs in the last bit
    # from the baseline one (``export``'s floored log2). Disabling a feature a
    # machine lacks is silently ignored.
    "NPY_DISABLE_CPU_FEATURES": "X86_V4 AVX512_ICL",
    # OpenBLAS's kernel choice: AVX-512 machines pick "SkylakeX", whose
    # products differ in the last bit from "Haswell"'s (``analyze``).
    "OPENBLAS_CORETYPE": "Haswell",
    # The block SVD's reductions depend on the thread count, and OpenBLAS caps
    # threads at the available CPUs; one thread is the count every machine
    # (and a one-CPU cluster job) can run. ``analyze`` took 19 s at 1 and 24.
    "OPENBLAS_NUM_THREADS": "1",
    # OpenMP threads: no effect on any output on 2026-10-28; pinned so that a
    # later OpenMP reduction cannot reintroduce a machine dependence.
    "OMP_NUM_THREADS": "1",
}


# --- clean: inputs, outputs and the repair registry ------------------------

#: The fasting file metabo_adni reads (``-F``; baseline rows of ``RID``,
#: ``VISCODE2``, ``BIFAST``).
CLEAN_FASTING_FILE = "BIOMARK.csv"
#: The medication table. metabo_adni's ``--residualize-meds`` reads it, but
#: the flag is off in ``CLEAN_OPTIONS`` and ``clean`` does not read it;
#: ``cohort`` reads its statin column (``ANALYSIS_COVARIATES``).
CLEAN_MEDICATION_FILE = "ADMCPATIENTDRUGCLASSES_20170512.csv"
#: The p180 concentration files per metabo_adni table key, in the order of
#: metabo_adni's ``load.read_files``; the run is the key's prefix.
CLEAN_P180_FILES: dict[str, str] = {
    "ADNI1-UPLC": "ADMCDUKEP180UPLC_01_15_16.csv",
    "ADNI1-FIA": "ADMCDUKEP180FIA_01_15_16.csv",
    "ADNI2GO-UPLC": "ADMCDUKEP180UPLCADNI2GO.csv",
    "ADNI2GO-FIA": "ADMCDUKEP180FIAADNI2GO.csv",
}
#: The p180 LOD workbooks, in the order of metabo_adni's ``load.read_lod_files``
#: (which opens all four unconditionally).
CLEAN_P180_LOD_FILES: tuple[str, ...] = (
    "4097_UPLC_p180_Data.xlsx",
    "4097_FIA_p180_Data.xlsx",
    "4610 UPLC p180 Data.xlsx",
    "4610 FIA p180 Data.xlsx",
)
#: Every raw file ``clean`` reads per platform, by the exact name metabo_adni
#: expects in the data root. No other file is read.
CLEAN_INPUT_FILES: dict[str, tuple[str, ...]] = {
    "p180": (*CLEAN_P180_FILES.values(), *CLEAN_P180_LOD_FILES, CLEAN_FASTING_FILE),
    "nmr": ("ADNINIGHTINGALE2.csv", CLEAN_FASTING_FILE),
}
#: The cleaned table per platform, under the name metabo_adni's command line
#: gives it (``<key>.csv`` after ``--merge``). Participant-level.
CLEAN_TABLES: dict[str, str] = {"p180": "P180.csv", "nmr": "NMR.csv"}
#: The p180 run provenance table (``RID``, ``run``). Participant-level.
CLEAN_RUNS_TABLE = "p180_runs.csv"
#: metabo_adni's captured output (it prints participant identifiers), relative
#: to the platform directory. Participant-level.
CLEAN_LOG = "logs/metabo_adni.log"

#: Known defects of LONI's raw exports, keyed by the name in the data root.
#: The archive copy carries the repair, applied by hand; ``clean`` recognises
#: the repaired bytes by hash and refuses LONI's unrepaired bytes. It never
#: repairs a file itself.
KNOWN_RAW_FILE_REPAIRS: dict[str, dict[str, str]] = {
    "ADMCDUKEP180UPLCADNI2GO.csv": {
        "defect": (
            "LONI's export lacks its final byte, the closing double quote of the last "
            "record's update_stamp field, so pandas' C parser fails with 'EOF inside string'"
        ),
        "repair": (
            "a double quote and a newline appended at the end of the archive copy "
            "(the last record's timestamp and metabolite values are complete)"
        ),
        "repaired_on": "2026-10-26",
        "loni_sha256": "f28ede9aa70e02d2c8bf4ef2b3f4873a217675e424cd2498e4dd3f43d03df326",
        "repaired_sha256": "7ad17d63eed26368a3e51254c942e9c2f39890d43decda37f7b1a2ade38de3a6",
    },
}

# --- clean: scientific constant and predeclared counts --------------------

#: Decided by the change ``adni-metabolomics-clean``. metabo_adni's QC with
#: its default cutoffs (missing metabolites ``mmc``, missing participants
#: ``mpc``, ``cv``, ``icc``), its ``--merge``, and none of its transforms.
#: ``cv`` and ``icc`` apply to p180 only in metabo_adni and are not set for
#: NMR. Scale (pseudo-count, log, z-score) belongs to ``EXPORT_FEATURE_RULE``;
#: outlier removal and medication residualization are not in the primary
#: pipeline. Never changed by a flag, a result or a count.
CLEAN_OPTIONS: dict[str, dict[str, float | bool]] = {
    "p180": {
        "mmc": 0.2,
        "mpc": 0.2,
        "cv": 0.2,
        "icc": 0.65,
        "merge": True,
        "log2": False,
        "zscore": False,
        "winsorize": False,
        "remove_moutliers": False,
        "residualize_meds": False,
    },
    "nmr": {
        "mmc": 0.2,
        "mpc": 0.2,
        "merge": True,
        "log2": False,
        "zscore": False,
        "winsorize": False,
        "remove_moutliers": False,
        "residualize_meds": False,
    },
}

#: Predeclared by the change ``adni-metabolomics-clean`` from its spike
#: (``spike.md``, 2026-10-26) on the inputs of ``RAW_INPUT_SHA256``. ``cells``
#: is (unique participants, metabolites) per metabo_adni table after each of
#: metabo_adni's steps; ``cross_plate_correction`` rescales values and drops
#: nothing, so its cells equal the step before (the spike reported it with
#: the CV step). ``clean`` compares its observed counts with these and records
#: every difference as a finding; a difference never stops the step and never
#: changes an option.
CLEAN_EXPECTED_COUNTS: dict[str, dict] = {
    "p180": {
        "cells": {
            "read_files": {
                "ADNI1-UPLC": (807, 41), "ADNI1-FIA": (807, 141),
                "ADNI2GO-UPLC": (874, 41), "ADNI2GO-FIA": (874, 141),
            },
            "remove_missing_metabolites": {
                "ADNI1-UPLC": (807, 32), "ADNI1-FIA": (807, 117),
                "ADNI2GO-UPLC": (874, 32), "ADNI2GO-FIA": (874, 126),
            },
            "cross_plate_correction": {
                "ADNI1-UPLC": (807, 32), "ADNI1-FIA": (807, 117),
                "ADNI2GO-UPLC": (874, 32), "ADNI2GO-FIA": (874, 126),
            },
            "remove_cv": {
                "ADNI1-UPLC": (807, 31), "ADNI1-FIA": (807, 116),
                "ADNI2GO-UPLC": (874, 32), "ADNI2GO-FIA": (874, 124),
            },
            "remove_icc": {
                "ADNI1-UPLC": (807, 28), "ADNI1-FIA": (807, 110),
                "ADNI2GO-UPLC": (874, 31), "ADNI2GO-FIA": (874, 121),
            },
            "remove_missing_participants": {
                "ADNI1-UPLC": (807, 28), "ADNI1-FIA": (806, 110),
                "ADNI2GO-UPLC": (874, 31), "ADNI2GO-FIA": (874, 121),
            },
            "consolidate_replicates": {
                "ADNI1-UPLC": (807, 28), "ADNI1-FIA": (806, 110),
                "ADNI2GO-UPLC": (874, 31), "ADNI2GO-FIA": (874, 121),
            },
            "remove_non_fasters": {
                "ADNI1-UPLC": (747, 28), "ADNI1-FIA": (746, 110),
                "ADNI2GO-UPLC": (846, 31), "ADNI2GO-FIA": (846, 121),
            },
            "remove_bad_qc_tags": {
                "ADNI1-UPLC": (747, 27), "ADNI1-FIA": (746, 110),
                "ADNI2GO-UPLC": (846, 31), "ADNI2GO-FIA": (846, 120),
            },
            "imputation": {
                "ADNI1-UPLC": (747, 27), "ADNI1-FIA": (746, 110),
                "ADNI2GO-UPLC": (846, 31), "ADNI2GO-FIA": (846, 120),
            },
            "merge": {"P180": (1592, 133)},
        },
        "imputed_points": {
            "ADNI1-UPLC": 16, "ADNI1-FIA": 730, "ADNI2GO-UPLC": 262, "ADNI2GO-FIA": 643, "total": 1651,
        },
        "final": {"participants": 1592, "metabolites": 133},
        "duplicated_participants": 0,
        "runs": {"ADNI1": 746, "ADNI2GO": 846},
        "zeros": {"values": 0, "metabolites": 0},
        "multi_plate_lod": {"metabolites": 34, "points": 1608},
    },
    "nmr": {
        "cells": {
            "read_files": {"NMR": (1646, 250)},
            "remove_missing_metabolites": {"NMR": (1646, 245)},
            "remove_missing_participants": {"NMR": (1645, 245)},
            "consolidate_replicates": {"NMR": (1645, 245)},
            "remove_non_fasters": {"NMR": (1563, 245)},
            "remove_bad_qc_tags": {"NMR": (1504, 245)},
            "imputation": {"NMR": (1504, 245)},
            "merge": {"NMR": (1504, 245)},
        },
        "imputed_points": {"NMR": 155, "total": 155},
        "final": {"participants": 1504, "metabolites": 245},
        "duplicated_participants": 0,
        "zeros": {"values": 41, "metabolites": 3},
        "non_baseline_records": 3,
    },
}

#: The sha256 of each raw file in the data root at its predeclaration: the
#: metabolomics files at ``adni-metabolomics-clean`` (the LONI downloads of
#: 10-11 July 2024, the UPLC ADNI-GO/2 file with its repair; the medication
#: table, which ``clean`` does not read, because its spike inventoried it)
#: and the ADNIMERGE freeze at ``adni-cohort``; the two p180 supplement
#: archives that hold the NIST SRM 1950 QC workbooks at ``adni-nist-bridge``
#: (read in place by ``export-sensitivity --variant nist_bridge``; their
#: members' hashes are ``NIST_BRIDGE_WORKBOOK_SHA256``). A step that finds
#: another hash records a finding (a fresh download); the predeclared counts
#: hold for these bytes only.
RAW_INPUT_SHA256: dict[str, str] = {
    "ADMCDUKEP180UPLC_01_15_16.csv": "b99835be2d07460f5c1089fd72276454099d3ec7c14e662c740b496de0dad4fb",
    "ADMCDUKEP180FIA_01_15_16.csv": "0c765d0048f05fdc89f0eaa575b31f655fcefa2faf9fb0da92263836959f7290",
    "ADMCDUKEP180UPLCADNI2GO.csv": "7ad17d63eed26368a3e51254c942e9c2f39890d43decda37f7b1a2ade38de3a6",
    "ADMCDUKEP180FIAADNI2GO.csv": "a414de4884d2ccd88a6519d3f5627155677ba5bf08be160191e316f5290459e9",
    "4097_UPLC_p180_Data.xlsx": "84648d2e896d23154d8483e7ec4bae87868562df80fb77cf85a4843d096698cb",
    "4097_FIA_p180_Data.xlsx": "57f0d41e992b2009ed595e2c76ebb0a3f2d1bd294f1ac8e9b6ca5f1e33fa1b45",
    "4610 UPLC p180 Data.xlsx": "f118ccc5c9112c413aeeb47c1f329afde3e858606bf64b68865f7c366d87eada",
    "4610 FIA p180 Data.xlsx": "ddbf46eda9aab32c2fe1d9251efdff7ce93701124d8281c4c7b4f3c18c60c617",
    "ADNINIGHTINGALE2.csv": "524bde27672021fe8a9c4cc4b5d0d89a38f6f04129b930c955bd31e04c651ebf",
    "BIOMARK.csv": "0c7bc024fd3de367395c1edf7ab870bb7af37bc66dffaa11312d66570541671d",
    "ADMCPATIENTDRUGCLASSES_20170512.csv": "2f0dd41dfb4c17f679818f19f8a5a41a2de81c30712863286a74e29fdd597343",
    "ADNI_adnimerge_20170629_QT-freeze.csv": "e3eae0464106f0a3df4eb23946e57f1f7fd5f8456eb60af6540654a36a16f7a2",
    "ADMC_supplement.zip": "dc822b5683990f877f919af9ff521e0bbe5c12ca87a410b4a8bcff67f247544e",
    "ADMCDUKEP180SUPP_20170410.zip": "c3f9a0874af9ba74fb995da9d9f25dd95fdd6f4c0d0a43b3bff5455c90856332",
}


# --- cohort: scientific constants -------------------------------------------

#: Decided by the change ``adni-cohort``. The clinical table is the QT-PAD
#: ADNIMERGE freeze of 2017-06-29 (the file of the 2022 study); each
#: participant's clinical values come from its row at ``baseline_visit``
#: (ADNIMERGE ``VISCODE``). A cleaned participant enters a platform's set only
#: if every raw record of the participant on that platform has visit
#: ``sample_visit`` (read from the column ``sample_visit_columns`` names per
#: raw file) and it has a ``baseline_visit`` row; the ADNI-1 p180 files carry
#: no visit column, so participants of the runs in ``runs_without_visit``
#: (``p180_runs.csv``) count as baseline (ADMC measured ADNI-1 baseline
#: serum). The analysis cohort is the intersection of the ``platforms``' sets.
#: No other exclusion, and none depends on sex, stage or a covariate value.
#: Never changed by a flag, a result or a count.
COHORT_RULE: dict = {
    "clinical_file": "ADNI_adnimerge_20170629_QT-freeze.csv",
    "baseline_visit": "bl",
    "sample_visit": "bl",
    "sample_visit_columns": {
        "ADMCDUKEP180UPLCADNI2GO.csv": "VISCODE",
        "ADMCDUKEP180FIAADNI2GO.csv": "VISCODE",
        "ADNINIGHTINGALE2.csv": "VISCODE2",
    },
    "runs_without_visit": ("ADNI1",),
    "platforms": ("p180", "nmr"),
}

#: Decided by the change ``adni-cohort``. The stage is ADNI's enrollment
#: category ``DX.bl`` on the baseline row, merged as in the 2022 study: SMC
#: into CN, EMCI and LMCI into MCI. ``DX.bl`` is kept beside the stage; a value
#: outside ``map`` stops the step.
STAGE_RULE: dict = {
    "source": "DX.bl",
    "map": {"CN": "CN", "SMC": "CN", "EMCI": "MCI", "LMCI": "MCI", "AD": "AD"},
}

#: Decided by the change ``adni-cohort``: the covariates, in this order, with
#: their source (``clinical``: the ADNIMERGE baseline row; ``medication``: the
#: medication table's row at ``visit``) and coding. ``levels`` are the values
#: a categorical covariate may take; ``map`` recodes the source value first.
#: ``statin`` is ``1`` when the cell is filled and ``0`` when it is empty.
#: Missing policy ``error``: a missing value stops ``cohort``, nothing is
#: imputed and nobody is dropped for it. The ``coding`` is what ``analyze``
#: declares to MOTCO (``apoe4`` and ``statin`` are written as integers).
ANALYSIS_COVARIATES: dict[str, dict] = {
    "age": {"file": "clinical", "column": "AGE", "coding": "numeric"},
    "education": {"file": "clinical", "column": "PTEDUCAT", "coding": "numeric"},
    "apoe4": {"file": "clinical", "column": "APOE4", "coding": "categorical", "levels": (0, 1, 2)},
    "phase": {
        "file": "clinical",
        "column": "ORIGPROT",
        "coding": "categorical",
        "levels": ("ADNI1", "ADNI2GO"),
        "map": {"ADNI1": "ADNI1", "ADNIGO": "ADNI2GO", "ADNI2": "ADNI2GO"},
    },
    "statin": {
        "file": "medication",
        "column": "HMG CoA reductase inhibitors",
        "visit": "sc",
        "coding": "categorical",
        "levels": (0, 1),
    },
}

# --- cohort: conventions and predeclared counts ------------------------------

#: The clinical table ``cohort`` reads, by its name in the data root (a
#: symlink into ``<root>/Clinical/``).
COHORT_CLINICAL_FILE = COHORT_RULE["clinical_file"]
#: The values of sex (``PTGENDER``) as they appear. A value check, not the
#: group order passed to MOTCO (the analyze change decides that).
GROUP_VALUES: tuple[str, ...] = ("Female", "Male")
#: The columns of ``cohort.csv``, in this order: one row per participant of
#: either platform set, a flag per platform; the intersection is the rows
#: with every flag true.
COHORT_COLUMNS: tuple[str, ...] = (
    SAMPLE_COLUMN,
    GROUP_COLUMN,
    STAGE_COLUMN,
    "dx_bl",
    "protocol",
    *ANALYSIS_COVARIATES,
    "visit",
    *COHORT_RULE["platforms"],
)

#: Predeclared by the change ``adni-cohort`` from its spike (``spike.md``,
#: 2026-10-26) on the clean outputs of ``adni-metabolomics-clean`` and the
#: inputs of ``RAW_INPUT_SHA256``. Per platform set: the cleaned participants
#: by the visit set of their raw records (``sample_visits``; p180 per run),
#: the exclusion cascade (the sample rule first, then the baseline row) and
#: sex × stage. For the intersection: its cascade, sex × stage, the
#: composition cells (sex × ``DX.bl`` × phase, observed cells only), the
#: agreement of ``DX`` on the baseline row with the stage, phase-against-run
#: disagreements, statin users and missing covariate values. For the union
#: (the rows of ``cohort.csv``): its size and split. ``cohort`` compares its
#: observed counts with these and records every difference as a finding; a
#: difference never stops the step and never changes a rule.
COHORT_EXPECTED_COUNTS: dict[str, dict] = {
    "p180": {
        "sample_visits": {"ADNI1": {"no visit column": 746}, "ADNI2GO": {"bl": 846}},
        "cascade": {"cleaned": 1592, "excluded_sample_not_bl": 0, "excluded_no_clinical_bl_row": 0, "set": 1592},
        "sex_stage": {"Female": {"CN": 254, "MCI": 329, "AD": 140}, "Male": {"CN": 230, "MCI": 470, "AD": 169}},
    },
    "nmr": {
        "sample_visits": {"bl": 1503, "sc": 1},
        "cascade": {"cleaned": 1504, "excluded_sample_not_bl": 1, "excluded_no_clinical_bl_row": 0, "set": 1503},
        "sex_stage": {"Female": {"CN": 237, "MCI": 310, "AD": 126}, "Male": {"CN": 223, "MCI": 449, "AD": 158}},
    },
    "intersection": {
        "cascade": {"cleaned_on_both": 1502, "set": 1501},
        "sex_stage": {"Female": {"CN": 237, "MCI": 310, "AD": 125}, "Male": {"CN": 223, "MCI": 448, "AD": 158}},
        "composition": {
            "Female": {
                "CN": {"ADNI1": 94, "ADNI2GO": 89},
                "SMC": {"ADNI2GO": 54},
                "EMCI": {"ADNI2GO": 123},
                "LMCI": {"ADNI1": 117, "ADNI2GO": 70},
                "AD": {"ADNI1": 72, "ADNI2GO": 53},
            },
            "Male": {
                "CN": {"ADNI1": 98, "ADNI2GO": 83},
                "SMC": {"ADNI2GO": 42},
                "EMCI": {"ADNI2GO": 152},
                "LMCI": {"ADNI1": 221, "ADNI2GO": 75},
                "AD": {"ADNI1": 82, "ADNI2GO": 76},
            },
        },
        "stage_source": {"agree": 1498, "differ": 2, "missing": 1},
        "phase_vs_run_disagreements": 0,
        "statin_users": 704,
        "missing_covariate_values": 0,
    },
    "union": {"participants": 1594, "both": 1501, "p180_only": 91, "nmr_only": 2},
}


# --- export: scientific constant ---------------------------------------------

#: Decided by the change ``adni-export``. Two parts. ``membership``: a block
#: holds the measured concentrations of its platform, each once. Every
#: cleaned p180 metabolite enters (µM concentrations). A cleaned NMR column
#: enters unless its name carries one of the ``derived`` marks, which name
#: the deterministic functions of other columns of the block: the
#: percentages (suffix ``_PCT``), the ratios (containing ``_BY_``), the
#: degree of unsaturation (``UNSATURATION``) and the particle sizes (suffix
#: ``_SIZE``). The marks are tested in this order; the change's spike checked
#: them against the Nightingale dictionary's units for every cleaned column.
#: ``scale``: every kept value is exported as ``log2(x + floor)``, the floor
#: of a metabolite being its ``floor_quantile`` quantile over the exported
#: participants (``floor_method`` is numpy's interpolation), computed without
#: sex, stage or a covariate and recorded per feature; a non-positive floor
#: stops the step. MOTCO's unit transform is ``motco_transform`` and MOTCO
#: z-scores every feature itself. No value is imputed, replaced, winsorized
#: or removed, and nothing is centred per run. Never changed by a flag, a
#: result or a count.
EXPORT_FEATURE_RULE: dict[str, dict] = {
    "membership": {
        "p180": {"derived": {}},
        "nmr": {
            "derived": {
                "percentage": ("endswith", "_PCT"),
                "ratio": ("contains", "_BY_"),
                "degree": ("equals", "UNSATURATION"),
                "size": ("endswith", "_SIZE"),
            }
        },
    },
    "scale": {
        "transform": "log2(x + floor)",
        "floor_quantile": 0.05,
        "floor_method": "linear",
        "motco_transform": "identity",
    },
}

# --- export: conventions and predeclared counts ------------------------------

#: The blocks in the order passed to MOTCO (``<platform>.csv`` each).
EXPORT_BLOCKS: tuple[str, ...] = ("p180", "nmr")
#: The status of a cleaned column under ``EXPORT_FEATURE_RULE``: ``kept`` (a
#: column of the block) or ``derived`` (excluded, with its family).
EXPORT_FEATURE_STATUSES: tuple[str, ...] = ("kept", "derived")
#: The columns of ``covariates.csv`` after ``rid``: the ``ANALYSIS_COVARIATES``
#: in declared order, copied from ``cohort.csv`` unchanged.
EXPORT_COVARIATE_COLUMNS: tuple[str, ...] = tuple(ANALYSIS_COVARIATES)

#: Predeclared by the change ``adni-export`` from its spike (``spike.md``,
#: 2026-10-27) on the clean and cohort outputs of ``adni-metabolomics-clean``
#: and ``adni-cohort``: the exported participants and their sex × stage
#: cells; per platform the cleaned columns, the kept ones and the derived
#: ones by family, the zero cells and the metabolites holding them (counted
#: before the floor), the non-positive floors, the non-finite cells after
#: the transform and the metabolites whose phase offset ``|d|`` exceeds 1 on
#: the rule's scale; the missing covariate values. ``export`` compares its
#: observed counts with these and records every difference as a finding; a
#: difference never stops the step and never changes the rule.
EXPORT_EXPECTED_COUNTS: dict[str, dict | int] = {
    "participants": 1501,
    "sex_stage": {"Female": {"CN": 237, "MCI": 310, "AD": 125}, "Male": {"CN": 223, "MCI": 448, "AD": 158}},
    "features": {
        "p180": {"cleaned": 133, "kept": 133, "derived": {"percentage": 0, "ratio": 0, "degree": 0, "size": 0}},
        "nmr": {"cleaned": 245, "kept": 165, "derived": {"percentage": 72, "ratio": 4, "degree": 1, "size": 3}},
    },
    "zero_cells": {"p180": 0, "nmr": 41},
    "metabolites_with_zeros": {"p180": 0, "nmr": 3},
    "floors_not_positive": {"p180": 0, "nmr": 0},
    "non_finite": {"p180": 0, "nmr": 0},
    "phase_offset": {"p180": {"abs_d_gt_1": 80}, "nmr": {"abs_d_gt_1": 0}},
    "missing_covariate_values": 0,
}


# --- analyze: scientific constants -------------------------------------------

#: Decided by the change ``adni-analyze`` (2026-10-27, before any run) and
#: never changed by a flag, a result or a count. The measurement settings of
#: the primary analysis, one ``motco.analysis.analyze_trajectories`` call on
#: the exported blocks: MOTCO's RRPP permutations (the p-value is
#: ``(1 + b) / (1 + B)``, exact in size at any count; 9999 sets the Monte
#: Carlo resolution at 0.0001), the RRPP seed (the proposal's date), the
#: rejection rule (``p <= alpha``, the rule of MOTCO's covariate Type I
#: check, exact for that p-value), the latent-rank floor (``min_components``,
#: MOTCO's validated default, passed explicitly and checked equal to MOTCO's
#: default before any input is read) and the latent adjustment of the primary
#: (``None``: the covariate-blind basis of MOTCO's validated path). Every
#: other MOTCO setting stays MOTCO's default and is read back from the record
#: into the manifest. ``phase`` enters as a covariate of the stage means
#: (``ANALYSIS_COVARIATES``), additively; the run offset is not corrected.
ANALYSIS_PERMUTATIONS = 9999
ANALYSIS_SEED = 20261027
ANALYSIS_ALPHA = 0.05
ANALYSIS_REJECTION_RULE = "p <= alpha"
ANALYSIS_RANK_FLOOR = 2
ANALYSIS_LATENT_ADJUSTMENT: str | None = None
#: The ``stage``-conditioned latent adjustment (``covariate_latent_adjustment``
#: ``"stage"``, the same five covariates, every other setting equal) is
#: decided by ``adni-analyze`` as a predeclared sensitivity arm, run by the
#: following change after ``axis-diagnostics``; it is read beside the primary
#: under ``READING_RULES`` and never replaces it. ``group_stage`` conditioning
#: is not admissible and does not run.
ANALYSIS_PREDECLARED_LATENT_SENSITIVITY: dict[str, str] = {
    "setting": "covariate_latent_adjustment",
    "conditioning": "stage",
    "change": "adni-latent-sensitivity",
}

#: Decided by the change ``adni-analyze``, written before any run: the
#: binding reading rules of the result, printed verbatim in ``summary.md``
#: and carried by every report, sensitivity and diagnostic that reads the
#: analysis. Carried from MOTCO's reports (``../MOTCO/docs/roadmap.md``).
READING_RULES: tuple[str, ...] = (
    "The primary result is the covariate-adjusted analysis on the covariate-blind basis with the five "
    "covariates; every sensitivity (latent adjustment, export variants, the CN / LMCI / AD arm, a rank sweep) "
    "is read beside it, and a rejection status that differs in an arm is dependence on that arm's setting, "
    "never a replacement of the primary.",
    "The CV-selected rank, the rank floor, the record's `config_spectrum` eigengap and the `angle` null "
    "summary are reported beside `angle`. The floor defines `angle` and `shape` in at least two dimensions; "
    "it does not make them powerful.",
    "`angle` and `shape` non-rejections are uninformative: MOTCO's operating characteristics were measured "
    "at n = 80 on a structural analogue (InterSIM blocks, 498 features), and no power statement exists at "
    "this design (n = 1501, 298 metabolites, six design columns). `angle` reads only the endpoint stages "
    "(CN and AD). A rejection is evidence that the trajectories differ in that respect, with Type I "
    "controlled at the validated designs.",
    "A `delta` rejection is evidence of a difference between the sexes' trajectories, not specifically of "
    "a difference in size.",
    "The covariate block of the record (design columns, reference row, missing policy, dropped "
    "participants) is reported beside the results. The adjustment is additive and linear on a "
    "covariate-blind basis, validated at three design columns and n = 80, and has no sex × covariate or "
    "stage × covariate term: the run offset is assumed equal in both sexes and across stages.",
    "The p180 run offset (export manifest `counts.phase_offset`: median |d| 1.12, 80 of 133 metabolites "
    "above 1, PC1 correlation 0.73 with phase; NMR 0.21, 0, 0.13) and the block shares (p180 133 / 298, "
    "unweighted in MOTCO 0.10.0) are reported beside the results. A latent component that tracks phase is "
    "a reading matter for `axis-diagnostics` and the latent-adjusted arm, not an adjustment of the primary.",
    "Feature membership and scale (`EXPORT_FEATURE_RULE`: 165 of 245 NMR columns, the floored log2, "
    "nothing imputed, winsorized or removed) are reported beside the results.",
    "Reported runs use `n_jobs = 1`; a run at another value carries a finding and is not reported. Report "
    "numbers are pasted from the generated files and checked by `report --check`.",
    "No result changes a constant. The analysis is run once at these settings; a second run at other "
    "settings is a new proposal.",
)

# --- analyze: conventions and predeclared counts ------------------------------

#: The statistics MOTCO reports, in the order the summary lists them.
ANALYSIS_STATISTICS: tuple[str, ...] = ("delta", "angle", "shape")
#: MOTCO's missing-covariate policy: a missing value stops the step (the
#: loader stops first, naming the column and a count); nothing is imputed.
ANALYSIS_MISSING_COVARIATES = "error"
#: The covariates declared categorical to MOTCO, derived from the coding
#: decided by ``adni-cohort`` so that it lives in one place.
ANALYSIS_CATEGORICAL_COVARIATES: tuple[str, ...] = tuple(
    name for name, spec in ANALYSIS_COVARIATES.items() if spec["coding"] == "categorical"
)
#: Every export file ``analyze`` reads, by name in the export directory. No
#: other file is read.
ANALYSIS_INPUT_FILES: tuple[str, ...] = (
    *(f"{platform}.csv" for platform in EXPORT_BLOCKS),
    EXPORT_METADATA,
    EXPORT_COVARIATES,
    EXPORT_MANIFEST,
)

#: Predeclared by the change ``adni-analyze`` from the export and cohort
#: manifests (none from a MOTCO run on ADNI data): the exported participants
#: and their sex × stage cells, the features per block and joint, the design
#: columns MOTCO renders from ``ANALYSIS_COVARIATES`` (typed out, so a renamed
#: level surfaces as a deviation), the observed count per categorical level,
#: the participants dropped for a missing covariate, the rank selection mode,
#: the floor and the permutations as the record states them. ``analyze``
#: compares its observed counts with these and records every difference as a
#: finding; a difference never stops the step and never changes a setting.
ANALYSIS_EXPECTED_COUNTS: dict[str, dict | int | str | tuple] = {
    "participants": 1501,
    "sex_stage": {"Female": {"CN": 237, "MCI": 310, "AD": 125}, "Male": {"CN": 223, "MCI": 448, "AD": 158}},
    "features": {"p180": 133, "nmr": 165, "joint": 298},
    "design_columns": ("age", "education", "apoe4[1]", "apoe4[2]", "phase[ADNI2GO]", "statin[1]"),
    "covariate_levels": {
        "apoe4": {"0": 810, "1": 542, "2": 149},
        "phase": {"ADNI1": 684, "ADNI2GO": 817},
        "statin": {"0": 797, "1": 704},
    },
    "dropped": 0,
    "component_selection": "cv",
    "min_components": ANALYSIS_RANK_FLOOR,
    "permutations": ANALYSIS_PERMUTATIONS,
}


# --- axis-diagnostics: scientific constants ----------------------------------

#: Decided by the change ``adni-axis-diagnostics`` (2026-10-27, before any
#: run) and never chosen or extended from a result. The variables every
#: latent component and block principal component is correlated with, each
#: with its source among the kept outputs (``file``), the column read and the
#: derivation. A variable's value is the column as is when the entry has no
#: ``levels`` (``age``, ``education``: years) and the 0-based index of the
#: value in ``levels`` when it has (``apoe4`` and ``statin`` keep their
#: integers; ``phase``, ``stage``, ``male`` and ``dx_bl`` become ordinals); a
#: value outside ``levels`` stops the step naming the column and a count.
#: The five covariates are read as the analysis codes them (``covariates.csv``);
#: ``stage`` and ``male`` are the design (``metadata.csv``); ``dx_bl`` is the
#: enrollment category ``STAGE_RULE`` merged (``cohort.csv``), read so that
#: the tables show whether a component separates SMC from CN or EMCI from
#: LMCI, which the stage does not, and because SMC and EMCI exist only in
#: ADNI-GO/2 (a phase axis is also a ``dx_bl`` axis). The tables keep this
#: order. Never changed by a flag, a result or a count.
DIAGNOSTIC_VARIABLES: dict[str, dict] = {
    "age": {"file": EXPORT_COVARIATES, "column": "age", "derivation": "as exported (years)"},
    "education": {"file": EXPORT_COVARIATES, "column": "education", "derivation": "as exported (years)"},
    "apoe4": {
        "file": EXPORT_COVARIATES,
        "column": "apoe4",
        "levels": (0, 1, 2),
        "derivation": "APOE e4 allele count 0 / 1 / 2, read as ordinal",
    },
    "phase": {
        "file": EXPORT_COVARIATES,
        "column": "phase",
        "levels": ("ADNI1", "ADNI2GO"),
        "derivation": "1 for ADNI2GO, 0 for ADNI1 (the p180 run; the design column phase[ADNI2GO])",
    },
    "statin": {
        "file": EXPORT_COVARIATES,
        "column": "statin",
        "levels": (0, 1),
        "derivation": "1 for a statin user at sc, 0 otherwise",
    },
    "stage": {
        "file": EXPORT_METADATA,
        "column": STAGE_COLUMN,
        "levels": STAGE_LABELS,
        "derivation": "ordinal CN 0, MCI 1, AD 2",
    },
    "male": {
        "file": EXPORT_METADATA,
        "column": GROUP_COLUMN,
        "levels": GROUP_VALUES,
        "derivation": "1 for Male, 0 for Female",
    },
    "dx_bl": {
        "file": COHORT_TABLE,
        "column": "dx_bl",
        "levels": ("CN", "SMC", "EMCI", "LMCI", "AD"),
        "derivation": "ordinal CN 0, SMC 1, EMCI 2, LMCI 3, AD 4 (ADNI's enrollment gradient)",
    },
}
#: Decided by the change ``adni-axis-diagnostics``: a reporting flag on
#: |Spearman rho|, raw and partial, for latent components and block PCs
#: alike. It reads magnitude, not significance (no p-value is attached to any
#: correlation; at n = 1501 the sampling SD of rho under independence is
#: about 0.026), and it is not an adoption rule: nothing is chosen from a
#: flagged row. Never changed by a flag, a result or a count.
DIAGNOSTIC_CORRELATION_THRESHOLD = 0.3

# --- axis-diagnostics: conventions and predeclared counts ---------------------

#: Principal components correlated per z-scored block (the export recorded
#: PC1 and PC2 against phase; three keeps the next one).
DIAGNOSTIC_N_BLOCK_PCS = 3
#: The conditioning set of the partial correlations: the six design columns
#: of the record, exactly the covariate design of the stage-means model
#: (numeric covariates as is, drop-first indicators ``<name>[<level>]`` for
#: the categorical ones), so a partial reads as what the model's adjustment
#: leaves. Built from ``covariates.csv`` with the codings the export manifest
#: records and checked, by name and by column mean, against the record.
DIAGNOSTIC_CONDITIONING_COLUMNS: tuple[str, ...] = tuple(ANALYSIS_EXPECTED_COUNTS["design_columns"])
#: Every analysis file ``axis-diagnostics`` reads, by name in the analysis
#: directory. No other file is read there.
DIAGNOSTICS_ANALYSIS_FILES: tuple[str, ...] = (
    ANALYSIS_RESULT,
    ANALYSIS_LATENT_SCORES,
    ANALYSIS_STAGE_MEANS,
    ANALYSIS_PLS_LOADINGS,
    ANALYSIS_MANIFEST,
)
#: The trajectory-geometry quantities of ``geometry_shares.csv``, from
#: ``stage_means.csv``, with their definitions (groups in ``GROUP_VALUES``
#: order, stages in ``STAGE_LABELS`` order).
DIAGNOSTICS_GEOMETRY_QUANTITIES: dict[str, str] = {
    "net_displacement": "a sex's net displacement (last stage mean minus first stage mean; what angle reads)",
    "sex_difference_by_stage": (
        "the per-stage sex-difference vectors (first group minus second, Female minus Male), squares summed over stages"
    ),
    "sex_difference_centred": (
        "the per-stage sex-difference vectors minus their mean over stages, squares summed over stages"
    ),
}

#: Predeclared by the change ``adni-axis-diagnostics`` from the committed
#: export, cohort and analysis manifests (none from a diagnostic run): the
#: exported participants and their sex × stage cells, the variable names in
#: declared order, the conditioning columns under the record's names, the
#: blocks with their features and PCs, and, for the primary analysis only,
#: its CV-selected rank, selection mode, latent adjustment and ``n_jobs`` and
#: the rows the four tables hold at that rank (8 × 8, 2 × 3 × 8, 4 × 8, 8).
#: ``axis-diagnostics`` compares its observed counts with these and records
#: every difference as a finding; a difference never stops the step and never
#: changes a constant. On an arm (``--analysis-dir``, or a recorded latent
#: adjustment) the ``primary`` and ``rows`` keys are not expected.
DIAGNOSTICS_EXPECTED_COUNTS: dict[str, dict | int | tuple] = {
    "participants": 1501,
    "sex_stage": {"Female": {"CN": 237, "MCI": 310, "AD": 125}, "Male": {"CN": 223, "MCI": 448, "AD": 158}},
    "variables": tuple(DIAGNOSTIC_VARIABLES),
    "conditioning_columns": DIAGNOSTIC_CONDITIONING_COLUMNS,
    "blocks": {
        "p180": {"features": 133, "pcs": DIAGNOSTIC_N_BLOCK_PCS},
        "nmr": {"features": 165, "pcs": DIAGNOSTIC_N_BLOCK_PCS},
    },
    "primary": {
        "selected_rank": 8,
        "component_selection": "cv",
        "latent_adjustment": ANALYSIS_LATENT_ADJUSTMENT,
        "n_jobs": REPORTED_N_JOBS,
    },
    "rows": {"axis_correlations": 64, "block_pcs": 48, "geometry_shares": 32, "components": 8},
}
#: The keys of ``DIAGNOSTICS_EXPECTED_COUNTS`` that do not depend on the
#: analysis read being the primary; the others are skipped on an arm.
DIAGNOSTICS_RANK_INDEPENDENT_KEYS: tuple[str, ...] = (
    "participants",
    "sex_stage",
    "variables",
    "conditioning_columns",
    "blocks",
)


# --- latent-sensitivity: conventions ------------------------------------------

#: The output root of the ``latent-sensitivity`` step and its three
#: subdirectories: ``analysis`` (the arm's analysis directory, laid out as the
#: primary's, written by ``latent-sensitivity``), ``comparison`` (the two
#: records side by side, written by ``latent-sensitivity``) and ``diagnostics``
#: (``axis-diagnostics --analysis-dir <analysis> --out-dir <diagnostics>``,
#: never touched by ``latent-sensitivity``).
LATENT_SENSITIVITY_DIR = "results/motco_latent_sensitivity"
LATENT_SENSITIVITY_SUBDIRS: dict[str, str] = {
    "analysis": "analysis",
    "comparison": "comparison",
    "diagnostics": "diagnostics",
}
#: The comparison's files under ``<LATENT_SENSITIVITY_DIR>/comparison/``.
LATENT_SENSITIVITY_TABLE = "latent_sensitivity.csv"
LATENT_SENSITIVITY_SUMMARY = "latent_sensitivity.md"
LATENT_SENSITIVITY_MANIFEST = "latent_sensitivity_manifest.json"

# --- latent-sensitivity: scientific constants ---------------------------------

#: Decided by the change ``adni-latent-sensitivity`` (2026-10-28, before any
#: run) and never changed by a flag, a result or a count. The single
#: sensitivity arm: MOTCO's covariate latent adjustment conditioned on
#: ``stage`` (the basis is fitted on the features with the five covariates
#: regressed out within each stage; the raw features are measured in it), the
#: same five covariates in the same order and coding, and every other setting
#: the primary's (``ANALYSIS_*`` and MOTCO's defaults; ``n_jobs = 1`` for the
#: reported run). It is the arm ``adni-analyze`` predeclared
#: (``ANALYSIS_PREDECLARED_LATENT_SENSITIVITY``), which the assertion below
#: ties it to. It is read beside the primary and never replaces it: MOTCO's
#: power comparison returned ``candidate_fails`` for ``stage`` conditioning.
#: No ``extended_covariates`` arm (the kept outputs hold no further
#: covariate) and no ``group_stage`` arm (not admissible).
LATENT_SENSITIVITY_ARM: dict = {
    "name": "latent_stage",
    "setting": "covariate_latent_adjustment",
    "conditioning": "stage",
    "covariates": tuple(ANALYSIS_COVARIATES),
    "change": "adni-latent-sensitivity",
    "other_settings": "the primary's (ANALYSIS_* constants and MOTCO's defaults)",
}
assert {k: LATENT_SENSITIVITY_ARM[k] for k in ("setting", "conditioning", "change")} == ANALYSIS_PREDECLARED_LATENT_SENSITIVITY, (
    "LATENT_SENSITIVITY_ARM must be the arm adni-analyze predeclared (ANALYSIS_PREDECLARED_LATENT_SENSITIVITY)"
)

#: Decided by the change ``adni-latent-sensitivity``: the justification
#: MOTCO's latent-adjustment Type I check asks for (why no residualized
#: covariate mediates the stage effect), stated per covariate as its relation
#: to the stage effect. Residualizing a covariate that mediates the stage
#: effect removes real stage signal, and no data can tell a confounder from a
#: mediator, so the roles are predeclared and no statistic or threshold is
#: computed for them; ``latent_sensitivity.md`` prints them beside the cohort
#: manifest's per-cell descriptives, copied. ``statin`` is the one mediator
#: candidate; it stays in the arm because the arm was predeclared with the
#: five covariates, and the reading carries the limitation.
LATENT_SENSITIVITY_COVARIATE_ROLES: dict[str, dict[str, str]] = {
    "age": {
        "role": "pre-disease",
        "variable": "age at baseline",
        "justification": "precedes disease: it can confound the stage effect but cannot be downstream of it",
    },
    "education": {
        "role": "pre-disease",
        "variable": "years of schooling, completed before enrolment",
        "justification": "precedes disease: it can confound the stage effect but cannot be downstream of it",
    },
    "apoe4": {
        "role": "pre-disease",
        "variable": "germline APOE e4 genotype (allele count)",
        "justification": "precedes disease: it can confound the stage effect but cannot be downstream of it",
    },
    "phase": {
        "role": "design",
        "variable": "the assay run and enrolment protocol (p180 kits ADNI-1 against ADNI-GO/2)",
        "justification": (
            "tied to stage composition by design (SMC and EMCI exist only in ADNI-GO/2), not caused by stage"
        ),
    },
    "statin": {
        "role": "mediator candidate",
        "variable": "HMG-CoA reductase inhibitor use on the screening medication row",
        "justification": (
            "a treatment that may follow diagnosis: prescribing differs with cognitive status; it stays in the arm "
            "because the arm was predeclared with the five covariates, and the reading carries the limitation"
        ),
    },
}
assert tuple(LATENT_SENSITIVITY_COVARIATE_ROLES) == tuple(ANALYSIS_COVARIATES), (
    "LATENT_SENSITIVITY_COVARIATE_ROLES must name the ANALYSIS_COVARIATES in their order"
)

#: Decided by the change ``adni-latent-sensitivity``, written before any run:
#: the binding reading rules of the arm, printed verbatim after
#: ``READING_RULES`` in the arm's ``summary.md``, in ``latent_sensitivity.md``,
#: in the arm's ``diagnostics.md`` and in every report that quotes the arm.
#: The numbers quoted are from MOTCO's two latent-adjustment reports
#: (``../MOTCO/docs/reports/latent-adjustment-type-i-2026-10-20.md`` and
#: ``latent-adjustment-power-2026-10-20.md``), none from a run of the arm.
LATENT_SENSITIVITY_READING_RULES: tuple[str, ...] = (
    "The arm is read beside the primary and never replaces it. MOTCO's power comparison returned "
    "`candidate_fails` for `stage` conditioning, which excludes the latent adjustment as a replacement of the "
    "covariate-blind primary.",
    "The primary and the arm share the export, the covariates and their design, the cells, the CV folds, the "
    "seed and the permutations. They differ only in the latent basis and the CV-selected rank: the arm's basis is "
    "fitted on the features with the five covariates regressed out within stage, and the raw features are "
    "measured in it. A rejection status that differs is basis dependence, not a result of the arm.",
    "The arm's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank "
    "that differs from the primary's is reported, not ranked as better or worse.",
    "An `angle` rejection that appears only in the arm is read against MOTCO's controls, and is not evidence of "
    "an orientation difference on its own: the translation control rejected `angle` at 0.085–0.092 under `stage` "
    "conditioning, against the 0.0706 bound (the covariate-blind basis was above it too, at 0.076–0.086); under "
    "the Type I check, `angle` held the bound by only 0.004 (0.067 against 0.0706).",
    "A `delta` or `shape` non-rejection in the arm is weaker than the primary's. MOTCO measured lost `shape` "
    "power with a covariate-aligned nuisance axis (0.243 against 0.428) and lost small-magnitude `delta` power "
    "without one (0.400 against 0.520 at e = 0.1). Reading rules 3 and 4 hold in the arm.",
    "The arm's `latent_adjustment` block and its covariate block are reported beside its results. The "
    "`latent_adjustment` block holds the conditioning, the design columns, the residual df, the smallest CV "
    "training df and the feature R² summary; `feature_r2` states how much feature variance the residualization "
    "removed.",
    "Residualizing a covariate that mediates the stage effect removes real stage signal, and no data can tell a "
    "confounder from a mediator. `age`, `education` and `apoe4` precede disease, and `phase` is the assay run and "
    "protocol (`LATENT_SENSITIVITY_COVARIATE_ROLES`). `statin` may follow diagnosis, so the arm's basis may have "
    "removed stage signal that runs through treatment.",
    "MOTCO's latent-adjustment operating characteristics were measured at one design: n = 80, the SEA-AD MTG "
    "structure, 498 features, eight covariates in nine design columns, covariates confounded with group × stage "
    "far beyond this design's. None was measured at this design (n = 1501, 298 metabolites, six design columns), "
    "and the arm carries no Type I or power claim of its own.",
    "A component of the arm that tracks a variable in its axis diagnostic is a measurement-space finding about "
    "the arm. It never reinterprets either analysis' statistics and is never grounds to adopt the arm.",
)

# --- latent-sensitivity: predeclared counts -----------------------------------

#: Predeclared by the change ``adni-latent-sensitivity`` from the committed
#: manifests and MOTCO's design rules (none from a run of the arm): every key
#: of ``ANALYSIS_EXPECTED_COUNTS`` with its value, and the record's
#: ``latent_adjustment`` block: conditioning ``stage``, the five covariates,
#: the residualization design columns (MOTCO names the stage indicators by its
#: ordinal codes: ``stage[1]`` is MCI, ``stage[2]`` is AD; then the six design
#: columns), the samples, the residual df ``n − 1 − k − q`` (1501 − 1 − 2
#: stage indicators − 6 design columns) and the feature scale. The arm's rank
#: is not predeclared. ``latent-sensitivity`` compares the arm record with
#: these and records every difference as a finding; a difference never stops
#: the step and never changes a setting.
LATENT_SENSITIVITY_EXPECTED_COUNTS: dict[str, dict | int | str | tuple] = {
    **ANALYSIS_EXPECTED_COUNTS,
    "latent_adjustment": {
        "conditioning": "stage",
        "covariates": tuple(ANALYSIS_COVARIATES),
        "design_columns": ("stage[1]", "stage[2]", *ANALYSIS_EXPECTED_COUNTS["design_columns"]),
        "n_samples": 1501,
        "residual_df": 1501 - 1 - 2 - 6,
        "feature_scale": "pooled_standardized",
    },
}


# --- export-sensitivity: conventions ------------------------------------------

#: The subdirectories of each variant's directory
#: ``<EXPORT_SENSITIVITY_DIR>/<variant>/``: ``bridge`` (``nist_bridge`` only:
#: the bridge table, reference material only), ``export`` (the variant's MOTCO
#: input, laid out as ``MOTCO_INPUT_DIR``; its CSVs are participant-level),
#: ``analysis`` (laid out as ``MOTCO_ANALYSIS_DIR``) and ``comparison``, all
#: written by ``export-sensitivity``, and ``diagnostics`` (``axis-diagnostics
#: --input-dir <export> --analysis-dir <analysis> --out-dir <diagnostics>``,
#: never touched by ``export-sensitivity``).
EXPORT_SENSITIVITY_SUBDIRS: dict[str, str] = {
    "bridge": "bridge",
    "export": "motco_input",
    "analysis": "analysis",
    "comparison": "comparison",
    "diagnostics": "diagnostics",
}
#: ``bridge/``: one row per exported p180 metabolite (aggregate).
EXPORT_SENSITIVITY_BRIDGE_TABLE = "nist_bridge.csv"
#: ``comparison/``: the primary and the variant side by side.
EXPORT_SENSITIVITY_TABLE = "export_sensitivity.csv"
EXPORT_SENSITIVITY_SUMMARY = "export_sensitivity.md"
EXPORT_SENSITIVITY_MANIFEST = "export_sensitivity_manifest.json"

# --- export-sensitivity: scientific constants ---------------------------------

#: Decided by the change ``adni-nist-bridge`` (2026-10-29, before any run) and
#: never changed by a flag, a result or a count. The bridge between the two
#: p180 assay runs, computed from NIST SRM 1950 ("Metabolites in Frozen Human
#: Plasma", the one material both runs measured) alone: no participant row, no
#: label and no covariate is read. The material is the rows labelled ``label``
#: of the sheet ``sheet`` (header on row ``header_row``) of the four QC
#: workbooks ``workbooks`` (per run, an archive of the data root read in place
#: and its member per kit). A replicate's cell is valid when it is a positive
#: number whose status, where the workbook has a status column (``<metabolite>
#: Status``; only the ADNI-GO/2 workbooks do), is not ``excluded_status`` (the
#: methods summary: such data "should not be used"); text cells (``< LOD``,
#: ``No Interception``) are missing. A metabolite is bridged when at least
#: ``inclusion_share`` of its replicates are valid in each run; its factor
#: ``b`` is the mean log2 of its valid ``reference_run`` replicates minus that
#: of its valid ``bridged_run`` replicates, with no plate correction (the spike:
#: metabo_adni's pool factors would move ``b`` by a median 0.0007 log2); a
#: metabolite not bridged keeps factor 1. Names are matched within kit with
#: case and punctuation dropped. On the predeclared bytes the rule bridges 126
#: of the 133 p180 metabolites (FIA 102, UPLC 24); ``C0``, ``C10:2``, ``C12``,
#: ``C14:1-OH``, ``C6 (C4:1-DC)``, serotonin and spermidine keep factor 1
#: (``C0`` because 17 of its 24 ADNI-GO/2 cells are ISTD-flagged).
NIST_BRIDGE_RULE: dict = {
    "material": "NIST SRM 1950",
    "workbooks": {
        "ADNI1": {
            "archive": "ADMC_supplement.zip",
            "members": {
                "FIA": "admc_supplement/duke_raw_data/4097_FIA_NIST_and_QC_Data.xlsx",
                "UPLC": "admc_supplement/duke_raw_data/4097_UPLC_NIST_and_QC_Data.xlsx",
            },
        },
        "ADNI2GO": {
            "archive": "ADMCDUKEP180SUPP_20170410.zip",
            "members": {
                "FIA": "4610 FIA p180 QC and NIST Data.xlsx",
                "UPLC": "4610 UPLC p180 QC and NIST Data.xlsx",
            },
        },
    },
    "sheet": "NIST SRM 1950 Data",
    "header_row": 1,
    "label_column": "Customer Sample Identification",
    "label": "NIST SRM 1950",
    "plate_column": "Plate Bar Code",
    "metabolites_after": "Injection Number",
    "status_suffix": " Status",
    "excluded_status": "ISTD Out of Range",
    "valid": (
        "a positive number whose status, where the workbook has a status column, is not excluded_status; "
        "text cells (< LOD, No Interception) are missing"
    ),
    "inclusion_share": 0.5,
    "estimator": (
        "b = mean log2 of the valid reference_run replicates minus mean log2 of the valid bridged_run replicates; "
        "every bridged_run concentration is multiplied by 2^b"
    ),
    "plate_correction": False,
    "reference_run": "ADNI1",
    "bridged_run": "ADNI2GO",
    "kits": ("FIA", "UPLC"),
    "name_matching": (
        "case and punctuation dropped (every character outside 0-9 and a-z), within the first kit whose sheet holds "
        "the name in both runs"
    ),
    "unbridged_factor": 1,
}
#: Predeclared by the change ``adni-nist-bridge`` (its spike, 2026-10-29): the
#: sha256 of each QC workbook of ``NIST_BRIDGE_RULE``, by its member name in
#: its archive. Another hash is a finding; the predeclared counts hold for
#: these bytes only.
NIST_BRIDGE_WORKBOOK_SHA256: dict[str, str] = {
    "admc_supplement/duke_raw_data/4097_FIA_NIST_and_QC_Data.xlsx": (
        "b19419d272dc7d19cfa5bc86c65ef1af81a718dbd704175126278babfc9ea6a0"
    ),
    "admc_supplement/duke_raw_data/4097_UPLC_NIST_and_QC_Data.xlsx": (
        "3b966a92cc3c3a1a6277adad4456fe9c9c42c0f495f8523ba4b446e3e16ed4d7"
    ),
    "4610 FIA p180 QC and NIST Data.xlsx": "f3873558779ae40202cc62207ddaf57cb6517a0adf3fff53901badda170acb93",
    "4610 UPLC p180 QC and NIST Data.xlsx": "807575d5b5937e39ae32db0b6812ddff76758ce508155c9b1305795bfbdcb602",
}

#: Decided by the change ``adni-scale-variants`` (2026-11-02, before any run of
#: a scale variant) and never changed by a flag, a result or a count. Per scale
#: variant of ``EXPORT_VARIANTS`` (hook ``scale``, both blocks), the transform
#: of a kept cell ``x`` (a cleaned concentration in its platform's unit: p180
#: µM, NMR mostly mmol/L) that replaces the rule's ``log2(x + floor)`` on the
#: primary's membership, and its additive ``offset``: ``None`` (no offset),
#: ``1`` (in the platform's unit) or ``"lambda"`` (``glog``: λ per metabolite
#: its smallest positive value over the exported participants divided by
#: ``lambda_divisor``). Every transform is monotone in the concentration. The
#: rule's floor is still computed, gated and recorded per metabolite, and not
#: applied; MOTCO's transform stays ``identity`` and MOTCO z-scores every
#: feature. A metabolite with no positive cell leaves λ undefined and stops
#: ``glog`` before anything is written.
SCALE_VARIANT_RULE: dict[str, dict] = {
    "raw_scale": {"transform": "x", "offset": None},
    "log2_plus_one": {"transform": "log2(x + 1)", "offset": 1},
    "glog": {
        "transform": "log2((x + sqrt(x² + λ²)) / 2)",
        "offset": "lambda",
        "lambda_divisor": 10,
        "lambda": (
            "per metabolite, its smallest positive value over the exported participants divided by lambda_divisor; a "
            "metabolite with no positive cell leaves λ undefined and stops the step before anything is written"
        ),
    },
}

#: Decided by the change ``adni-nist-bridge`` (2026-10-29, before any run): the
#: registry of export variants ``export-sensitivity`` runs, in this order. Each
#: changes one setting of the primary export (``block``, through the hook
#: ``hook`` of the shared export body) and keeps every other setting of
#: ``EXPORT_FEATURE_RULE``, the participants, the other block, the metadata
#: and the covariates; its analysis keeps every setting of the primary's. A
#: variant is read beside the primary and never replaces it. ``nist_bridge``
#: multiplies every cleaned p180 concentration of an ADNI-GO/2 participant (the
#: run of ``p180_runs.csv``) by 2^b of its metabolite under
#: ``NIST_BRIDGE_RULE`` before the floors; ``per_run_standardized`` centres
#: each p180 metabolite on the rule's scale (pooled floors) and divides it by
#: its population SD within its run. ``nmr_all_columns`` (decided by the change
#: ``adni-nmr-all-columns``, 2026-10-30, before any run of it) keeps every
#: cleaned NMR column, the 80 the rule marks ``derived`` among them, in cleaned
#: order, each on the rule's scale with its own floor. ``raw_scale``,
#: ``log2_plus_one`` and ``glog`` (decided by the change
#: ``adni-scale-variants``, 2026-11-02, before any run of them; block ``all``,
#: hook ``scale``) put every kept cell of both blocks on the scale of
#: ``SCALE_VARIANT_RULE`` in place of the rule's, on the primary's membership.
#: Never set or changed by a flag, a result or a count.
EXPORT_VARIANTS: dict[str, dict] = {
    "nist_bridge": {
        "block": "p180",
        "hook": "factors",
        "rule": "NIST_BRIDGE_RULE",
        "reads_data_root": True,
        "setting": (
            "every cleaned p180 concentration of a participant whose run in p180_runs.csv is ADNI2GO multiplied by "
            "2^b of its metabolite under NIST_BRIDGE_RULE before the floors; EXPORT_FEATURE_RULE then unchanged, its "
            "floors recomputed over the exported participants"
        ),
        "change": "adni-nist-bridge",
    },
    "per_run_standardized": {
        "block": "p180",
        "hook": "standardize_by_run",
        "rule": None,
        "reads_data_root": False,
        "setting": (
            "the p180 values on the scale of EXPORT_FEATURE_RULE (pooled floors, log2(x + floor)), each metabolite "
            "centred and divided by its population SD within its run of p180_runs.csv"
        ),
        "change": "adni-nist-bridge",
    },
    "nmr_all_columns": {
        "block": "nmr",
        "hook": "membership",
        "rule": None,
        "reads_data_root": False,
        "setting": (
            "every cleaned NMR column enters the block (245): the 165 concentrations of EXPORT_FEATURE_RULE and its 80 "
            "derived columns (72 percentages, 4 ratios, the degree of unsaturation, 3 sizes), each on the rule's scale, "
            "log2(x + floor) with its own 5 % floor over the exported participants; the p180 block, the participants, "
            "the metadata and the covariates the primary's"
        ),
        "change": "adni-nmr-all-columns",
    },
    "raw_scale": {
        "block": "all",
        "hook": "scale",
        "rule": "SCALE_VARIANT_RULE",
        "reads_data_root": False,
        "setting": (
            "both blocks on the raw scale: every kept cell the cleaned concentration as metabo_adni leaves it, in its "
            "platform's unit, with no log and no offset (SCALE_VARIANT_RULE); MOTCO's transform identity and its "
            "z-scoring; the membership, the participants, the metadata and the covariates the primary's; the rule's "
            "floors recorded, not applied"
        ),
        "change": "adni-scale-variants",
    },
    "log2_plus_one": {
        "block": "all",
        "hook": "scale",
        "rule": "SCALE_VARIANT_RULE",
        "reads_data_root": False,
        "setting": (
            "both blocks on log2(x + 1): every kept cell log2 of the cleaned concentration plus 1 in its platform's "
            "unit, the transform of the 2022 study (SCALE_VARIANT_RULE); the membership, the participants, the "
            "metadata and the covariates the primary's; the rule's floors recorded, not applied"
        ),
        "change": "adni-scale-variants",
    },
    "glog": {
        "block": "all",
        "hook": "scale",
        "rule": "SCALE_VARIANT_RULE",
        "reads_data_root": False,
        "setting": (
            "both blocks on the generalized log log2((x + sqrt(x² + λ²)) / 2), λ per metabolite its smallest positive "
            "value over the exported participants divided by 10 (SCALE_VARIANT_RULE); the membership, the "
            "participants, the metadata and the covariates the primary's; the rule's floors recorded, not applied"
        ),
        "change": "adni-scale-variants",
    },
}

#: Decided by the change ``adni-nist-bridge``, written before any run: the
#: binding reading rules of an export variant, printed verbatim after
#: ``READING_RULES`` in each variant's ``summary.md``, in
#: ``export_sensitivity.md``, in a variant's ``diagnostics.md`` and in every
#: report that quotes a variant. The numbers quoted are from the change's
#: spike, none from a run of a variant.
EXPORT_VARIANT_READING_RULES: tuple[str, ...] = (
    "A variant is read beside the primary and never replaces it. No variant result changes a constant, reruns "
    "the primary or adopts a variant.",
    "A variant shares with the primary the cleaned tables, the participants, the NMR block, the covariates and "
    "their design, the cells, the settings, the CV folds, the seed and the permutations. It differs only in the "
    "p180 values. A rejection status that differs is dependence on the handling of the p180 run, not a result of "
    "the variant.",
    "The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A "
    "rank that differs from the primary's is reported, not ranked.",
    "`nist_bridge` removes the part of the run offset that NIST SRM 1950 carries, between-run calibration. It "
    "assumes the run acts as one factor per metabolite, the same in plasma (NIST) and serum (participants). It "
    "leaves what NIST cannot see: a shift common to most metabolites, sample-handling differences between the "
    "protocols (the largest residuals are aspartate and glutamate) and the seven unbridged metabolites. `phase` "
    "stays a covariate of the stage means and carries what remains.",
    "`per_run_standardized` removes each p180 metabolite's whole difference in mean and spread between the runs, "
    "whatever its source: calibration, sample handling, and the stage-composition difference the runs carry, since "
    "SMC and EMCI were enrolled only in ADNI-GO/2. A difference between it and `nist_bridge` is read as the part of "
    "the run difference that is not calibration, never as evidence for either variant.",
    "A non-rejection in a variant is no more informative than the primary's: reading rule 3 holds, and no power "
    "statement exists at this design. A rejection that appears only in a variant is dependence on the run "
    "handling and is read beside the variant's rank and null summary.",
    "The variant's export manifest records the run offset per block, and for `nist_bridge` the factor per "
    "metabolite; both are reported beside the results. A variant component that tracks a variable in its axis "
    "diagnostic is a measurement-space finding and never grounds to adopt the variant.",
)

#: Decided by the change ``adni-nmr-all-columns``, written before any run: the
#: binding reading rules of ``nmr_all_columns``, printed verbatim after
#: ``READING_RULES`` in its ``summary.md``, its ``export_sensitivity.md``, its
#: ``diagnostics.md`` and every report that quotes it, in place of
#: ``EXPORT_VARIANT_READING_RULES`` (whose rule 2 says a variant differs only
#: in the p180 values). Rules 1, 2, 3, 6 and 7 have the roles of
#: ``EXPORT_VARIANT_READING_RULES`` 1, 2, 3, 6 and 7, so a sentence that cites
#: a rule by its role cites the same number under both sets. The numbers
#: quoted are from the change's spike, none from a run of the variant.
NMR_MEMBERSHIP_READING_RULES: tuple[str, ...] = (
    "`nmr_all_columns` is read beside the primary and never replaces it. No result of it changes a constant "
    "(`EXPORT_FEATURE_RULE` included), reruns the primary or adopts the variant.",
    "The variant shares a great deal with the primary: the cleaned tables, the participants, the p180 block, the "
    "165 NMR concentrations with their floors and cells, the covariates and their design, the cells, the settings, "
    "the CV folds, the seed and the permutations. It differs only in the NMR block's membership. It adds the 80 "
    "columns `EXPORT_FEATURE_RULE` marks `derived`, so the joint matrix holds 378 features, and the p180 share falls "
    "from 133 / 298 (0.446) to 133 / 378 (0.352). A rejection status that differs is dependence on the feature "
    "membership, not a result of the variant.",
    "The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A "
    "rank that differs from the primary's is reported, not ranked.",
    "The 80 columns add no measurement. Each is a function of the block's concentrations: a lipid's share of its "
    "lipoprotein subclass (72 percentages), a ratio (4), the degree of unsaturation, or a particle size (3). On the "
    "rule's scale the 165 concentrations explain a median 0.998 of a derived column's variance (lowest 0.798). MOTCO "
    "z-scores every feature and weights features, not blocks, so the columns add weight to the lipoprotein "
    "directions they are computed from. On the rule's scale, 21 of them have |skew| > 1 and 8 a largest |z| above 8, "
    "mostly percentages of the large HDL and VLDL lipids. A difference reflects the weight of those directions and "
    "those tails, never evidence that the derived columns measure what the concentrations do not.",
    "The 2022 study (doi:10.3389/fradi.2022.782864) used all 245 NMR columns, with `log2(x + 1)`, winsorizing, "
    "outlier removal and medication residuals. The variant changes the membership only, on the rule's scale. It is "
    "not a reproduction of that study, and no agreement or disagreement with it is read from the variant.",
    "A non-rejection in the variant is no more informative than the primary's: reading rule 3 holds, and no power "
    "statement exists at this design. A rejection that appears only in the variant is dependence on the feature "
    "membership, read beside the variant's rank and null summary.",
    "The variant's export manifest records the block shares, the NMR block's shape counts and the run offset per "
    "block. Its axis diagnostic records each block's loading share per component (`components.csv`). They are "
    "reported beside the results. A variant component that tracks a variable in its axis diagnostic is a "
    "measurement-space finding and never grounds to adopt the variant.",
    "The variant is read against the primary only, never against another export variant, arm or rank. No sentence "
    "reads it against another sensitivity.",
)

#: Decided by the change ``adni-scale-variants``, written before any run: the
#: binding reading rules shared by the scale variants ``raw_scale``,
#: ``log2_plus_one`` and ``glog``, printed verbatim after ``READING_RULES`` in
#: each one's ``summary.md``, its ``export_sensitivity.md``, its
#: ``diagnostics.md`` and every report that quotes it, in place of
#: ``EXPORT_VARIANT_READING_RULES``, and cited as "scale rule N". Rules 1, 2, 3,
#: 6 and 7 have the roles of ``EXPORT_VARIANT_READING_RULES`` 1, 2, 3, 6 and 7,
#: so a sentence that cites a rule by its role cites the same number under
#: every set. The numbers quoted are from the change's spike, none from a run
#: of a scale variant.
SCALE_VARIANT_READING_RULES: tuple[str, ...] = (
    "A scale variant is read beside the primary and never replaces it. No result of a scale variant changes a "
    "constant (the scale of `EXPORT_FEATURE_RULE` included), reruns the primary or adopts a variant.",
    "A scale variant shares with the primary the cleaned tables, the participants, the membership of both blocks (133 "
    "p180 metabolites, 165 NMR concentrations), the covariates and their design, the cells, the settings, the CV "
    "folds, the seed and the permutations. It differs only in the scale of the cell values of both blocks. Every "
    "scale is a monotone function of the concentration, so each participant's rank on each feature is the primary's; "
    "what changes is the spacing of the values, which MOTCO's z-scoring passes to the basis and the statistics. A "
    "rejection status that differs is dependence on the scale, not a result of the variant.",
    "The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A "
    "rank that differs from the primary's is reported, not ranked.",
    "`log2_plus_one` and `glog` keep the log and change its offset. The primary's offset is the metabolite's 5 % "
    "quantile (floor over median: p180 median 0.60, NMR 0.65), which compresses the lowest values of every metabolite "
    "alike. `log2_plus_one` is the transform of the 2022 study (doi:10.3389/fradi.2022.782864): its offset is 1 in "
    "each platform's unit (p180 µM, NMR mostly mmol/L), so an abundant metabolite gets nearly `log2(x)` and a scarce "
    "one a nearly linear scale (median below 1: 46 of 133 p180 metabolites, 129 of 165 NMR concentrations). It is not "
    "a reproduction of that study, whose membership, winsorizing, outlier removal and medication residuals differ, "
    "and no agreement or disagreement with it is read from the variant. `glog` is the generalized log with λ a tenth "
    "of the metabolite's smallest positive value: `log2(x)` within 0.004 bits on every positive cell, a zero cell 4.3 "
    "bits below the smallest positive value (41 NMR cells in 3 metabolites), and no compression of the low values, "
    "so it carries left tails (|skew| > 1 for 6 p180 and 25 NMR metabolites, a largest |z| above 8 for 6 and 13).",
    "`raw_scale` takes the cleaned concentrations with no log. MOTCO z-scores each feature, so the right tails of the "
    "concentration distributions carry leverage (|skew| > 1 for 46 p180 and 43 NMR metabolites, a largest |z| above 8 "
    "for 12 and 4, against 1 and 3, 0 and 1 on the rule's scale), and the NMR block loses numerical rank (104 of 165; "
    "the joint matrix 237 of 298): the lipoprotein measures are exact sums of their components on the concentration "
    "scale, a relation the log breaks. A difference reflects those tails and that geometry, never evidence that one "
    "scale measures what another does not.",
    "A non-rejection in a variant is no more informative than the primary's: reading rule 3 holds, and no power "
    "statement exists at this design. A rejection that appears only in a variant is dependence on the scale, read "
    "beside the variant's rank and null summary.",
    "The variant's export manifest records the shape counts of each block on its scale, the numerical rank of each "
    "block, the run offset per block and the offset of each metabolite (the feature tables). They are reported "
    "beside the results. The run offset barely moves with the scale (p180 median |d| 1.08 to 1.13 against the "
    "primary's 1.12). A variant component that tracks a variable in its axis diagnostic is a measurement-space "
    "finding and never grounds to adopt the variant.",
    "A scale variant is read against the primary only, never against another scale variant, another export variant, "
    "an arm or a rank. No sentence reads it against another sensitivity, and a difference between two scale variants "
    "is not evidence for either.",
)

#: A convention (change ``adni-nmr-all-columns``, design D3): per variant of
#: ``EXPORT_VARIANTS``, in its order, the reading rules it carries and the
#: words its readers print. ``rules`` names the rule tuple of this module and
#: ``change`` the change that decided it; ``heading`` and ``reader`` are the
#: heading and the reader of the rules section; ``cite`` is the citation word
#: ("variant rule N"); ``dependence`` the status label of a differing statistic
#: (``differs (<dependence>)``) and ``source`` what a differing status depends
#: on. The p180 variants keep the words their committed outputs print; the
#: entries are kept apart from ``EXPORT_VARIANTS``, whose entries the variant
#: manifests record. The ``dependence`` of ``nmr_all_columns`` is decided by
#: ``adni-nmr-all-columns``; the scale variants share one entry, whose
#: ``dependence`` is decided by ``adni-scale-variants``.
_P180_RUN_RULE_SET: dict[str, str] = {
    "rules": "EXPORT_VARIANT_READING_RULES",
    "change": "adni-nist-bridge",
    "cite": "variant rule",
    "dependence": "run-handling dependence",
    "source": "the handling of the p180 run",
    "heading": "Reading rules of the export variants",
    "reader": "an export variant",
}
_SCALE_RULE_SET: dict[str, str] = {
    "rules": "SCALE_VARIANT_READING_RULES",
    "change": "adni-scale-variants",
    "cite": "scale rule",
    "dependence": "scale dependence",
    "source": "the scale of both blocks",
    "heading": "Reading rules of the scale variants",
    "reader": "a scale variant",
}
EXPORT_VARIANT_RULE_SETS: dict[str, dict[str, str]] = {
    "nist_bridge": _P180_RUN_RULE_SET,
    "per_run_standardized": _P180_RUN_RULE_SET,
    "nmr_all_columns": {
        "rules": "NMR_MEMBERSHIP_READING_RULES",
        "change": "adni-nmr-all-columns",
        "cite": "membership rule",
        "dependence": "feature-membership dependence",
        "source": "the NMR feature membership",
        "heading": "Reading rules of the NMR membership variant",
        "reader": "the NMR membership variant",
    },
    "raw_scale": _SCALE_RULE_SET,
    "log2_plus_one": _SCALE_RULE_SET,
    "glog": _SCALE_RULE_SET,
}
assert tuple(EXPORT_VARIANT_RULE_SETS) == tuple(EXPORT_VARIANTS), (
    "EXPORT_VARIANT_RULE_SETS must name the rule set of every EXPORT_VARIANTS entry, in its order"
)
assert all(isinstance(globals().get(entry["rules"]), tuple) for entry in EXPORT_VARIANT_RULE_SETS.values()), (
    "EXPORT_VARIANT_RULE_SETS names a reading-rule tuple this module does not define: "
    + ", ".join(
        f"{variant} ({entry['rules']!r})" for variant, entry in EXPORT_VARIANT_RULE_SETS.items()
        if not isinstance(globals().get(entry["rules"]), tuple)
    )
    + "; every EXPORT_VARIANTS entry needs its rules"
)

# --- export-sensitivity: predeclared counts -----------------------------------

#: Predeclared by the change ``adni-nist-bridge`` from its spike (``spike.md``,
#: 2026-10-29; none from a run of a variant), per variant. The export keys:
#: every key of ``EXPORT_EXPECTED_COUNTS`` (participants, cells, features per
#: block and family, zero cells, floors not positive, non-finite cells, missing
#: covariate values) with the p180 run offset replaced by the variant's (the
#: metabolites with phase |d| above 0.5 and above 1); for ``nist_bridge`` the
#: bridged p180 metabolites per kit and the unbridged count, and the exported
#: metabolites with no NIST column; the exported participants whose run in
#: ``p180_runs.csv`` differs from their ``phase``; and ``nmr.csv``,
#: ``metadata.csv`` and ``covariates.csv`` equal to the primary export
#: manifest's hashes. ``analysis``: every key of ``ANALYSIS_EXPECTED_COUNTS``.
#: ``nmr_all_columns`` is predeclared by the change ``adni-nmr-all-columns``
#: from its spike (``spike.md``, 2026-10-30) and the committed manifests: the
#: NMR features with every derived column kept (``derived`` 0 per family, the
#: kept ones under ``derived_kept``), the joint features, the NMR block's shape
#: counts (|skew| > 1, largest |z| > 8), the run offset per block, ``p180.csv``,
#: ``metadata.csv`` and ``covariates.csv`` equal to the primary's, the rule's
#: NMR columns equal to the primary ``nmr.csv``'s (``rule_columns_equal_primary``),
#: ``analysis`` with its features, and ``diagnostics``: the rank-independent
#: keys of ``DIAGNOSTICS_EXPECTED_COUNTS`` with its NMR features, which
#: ``axis-diagnostics`` expects on the variant's read. ``raw_scale``,
#: ``log2_plus_one`` and ``glog`` are predeclared by the change
#: ``adni-scale-variants`` from its spike (``spike.md``, 2026-11-02) and the
#: committed manifests (``_SCALE_VARIANT_SHARED_COUNTS`` holds what the three
#: share): every key of ``EXPORT_EXPECTED_COUNTS`` (the zero cells counted
#: before the transform) with the run offset per block replaced by the
#: variant's, per block the shape counts (|skew| > 1, largest |z| > 8) and the
#: numerical rank on the variant's scale, for ``log2_plus_one`` the kept
#: metabolites whose median lies below its offset 1 (``scale``), the
#: participants whose run differs from ``phase``, ``metadata.csv`` and
#: ``covariates.csv`` equal to the primary's, and ``analysis``; no
#: ``diagnostics`` key, so ``axis-diagnostics`` expects the rank-independent
#: keys (165 NMR features). The ranks are not predeclared.
#: ``export-sensitivity`` compares each variant manifest with these and
#: records every difference as a finding; a difference never stops the step
#: and never changes a setting.
_SCALE_VARIANT_SHARED_COUNTS: dict = {
    **{key: value for key, value in EXPORT_EXPECTED_COUNTS.items() if key != "phase_offset"},
    "runs_differing_from_phase": 0,
    "unchanged_equal_primary": {EXPORT_METADATA: True, EXPORT_COVARIATES: True},
    "analysis": ANALYSIS_EXPECTED_COUNTS,
}
EXPORT_VARIANT_EXPECTED_COUNTS: dict[str, dict] = {
    "nist_bridge": {
        **{key: value for key, value in EXPORT_EXPECTED_COUNTS.items() if key != "phase_offset"},
        "phase_offset": {"p180": {"abs_d_gt_0_5": 35, "abs_d_gt_1": 8}, "nmr": {"abs_d_gt_1": 0}},
        "p180_bridged": {"FIA": 102, "UPLC": 24, "not_bridged": 7},
        "p180_unmatched": 0,
        "runs_differing_from_phase": 0,
        "unchanged_equal_primary": {EXPORT_METADATA: True, EXPORT_COVARIATES: True, "nmr.csv": True},
        "analysis": ANALYSIS_EXPECTED_COUNTS,
    },
    "per_run_standardized": {
        **{key: value for key, value in EXPORT_EXPECTED_COUNTS.items() if key != "phase_offset"},
        "phase_offset": {"p180": {"abs_d_gt_0_5": 0, "abs_d_gt_1": 0}, "nmr": {"abs_d_gt_1": 0}},
        "runs_differing_from_phase": 0,
        "unchanged_equal_primary": {EXPORT_METADATA: True, EXPORT_COVARIATES: True, "nmr.csv": True},
        "analysis": ANALYSIS_EXPECTED_COUNTS,
    },
    "nmr_all_columns": {
        **EXPORT_EXPECTED_COUNTS,
        "features": {
            "p180": EXPORT_EXPECTED_COUNTS["features"]["p180"],
            "nmr": {
                "cleaned": 245,
                "kept": 245,
                "derived": {"percentage": 0, "ratio": 0, "degree": 0, "size": 0},
                "derived_kept": {"percentage": 72, "ratio": 4, "degree": 1, "size": 3},
            },
        },
        "phase_offset": {"p180": {"abs_d_gt_0_5": 109, "abs_d_gt_1": 80}, "nmr": {"abs_d_gt_0_5": 5, "abs_d_gt_1": 0}},
        "joint_features": 378,
        "shape": {"nmr": {"abs_skew_gt_1": 24, "max_abs_z_gt_8": 9}},
        "runs_differing_from_phase": 0,
        "unchanged_equal_primary": {EXPORT_METADATA: True, EXPORT_COVARIATES: True, "p180.csv": True},
        "rule_columns_equal_primary": True,
        "analysis": {**ANALYSIS_EXPECTED_COUNTS, "features": {"p180": 133, "nmr": 245, "joint": 378}},
        "diagnostics": {
            **{key: DIAGNOSTICS_EXPECTED_COUNTS[key] for key in DIAGNOSTICS_RANK_INDEPENDENT_KEYS},
            "blocks": {
                "p180": DIAGNOSTICS_EXPECTED_COUNTS["blocks"]["p180"],
                "nmr": {"features": 245, "pcs": DIAGNOSTIC_N_BLOCK_PCS},
            },
        },
    },
    "raw_scale": {
        **_SCALE_VARIANT_SHARED_COUNTS,
        "phase_offset": {"p180": {"abs_d_gt_0_5": 108, "abs_d_gt_1": 76}, "nmr": {"abs_d_gt_0_5": 2, "abs_d_gt_1": 0}},
        "shape": {"p180": {"abs_skew_gt_1": 46, "max_abs_z_gt_8": 12}, "nmr": {"abs_skew_gt_1": 43, "max_abs_z_gt_8": 4}},
        "spectrum": {"p180": {"numerical_rank": 133}, "nmr": {"numerical_rank": 104}},
    },
    "log2_plus_one": {
        **_SCALE_VARIANT_SHARED_COUNTS,
        "phase_offset": {"p180": {"abs_d_gt_0_5": 108, "abs_d_gt_1": 80}, "nmr": {"abs_d_gt_0_5": 2, "abs_d_gt_1": 0}},
        "shape": {"p180": {"abs_skew_gt_1": 14, "max_abs_z_gt_8": 9}, "nmr": {"abs_skew_gt_1": 30, "max_abs_z_gt_8": 4}},
        "spectrum": {"p180": {"numerical_rank": 133}, "nmr": {"numerical_rank": 165}},
        "scale": {"median_below_offset": {"p180": 46, "nmr": 129}},
    },
    "glog": {
        **_SCALE_VARIANT_SHARED_COUNTS,
        "phase_offset": {"p180": {"abs_d_gt_0_5": 109, "abs_d_gt_1": 80}, "nmr": {"abs_d_gt_0_5": 2, "abs_d_gt_1": 0}},
        "shape": {"p180": {"abs_skew_gt_1": 6, "max_abs_z_gt_8": 6}, "nmr": {"abs_skew_gt_1": 25, "max_abs_z_gt_8": 13}},
        "spectrum": {"p180": {"numerical_rank": 133}, "nmr": {"numerical_rank": 165}},
    },
}
assert tuple(EXPORT_VARIANT_EXPECTED_COUNTS) == tuple(EXPORT_VARIANTS), (
    "EXPORT_VARIANT_EXPECTED_COUNTS must predeclare every EXPORT_VARIANTS entry, in its order"
)


# --- stage-sensitivity: conventions -------------------------------------------

#: The subdirectories of ``STAGE_SENSITIVITY_DIR``: ``export`` (the arm's MOTCO
#: input, laid out as ``MOTCO_INPUT_DIR`` without the feature tables; its CSVs
#: are participant-level), ``analysis`` (laid out as ``MOTCO_ANALYSIS_DIR``) and
#: ``comparison``, all written by ``stage-sensitivity``, and ``diagnostics``
#: (``axis-diagnostics --input-dir <export> --analysis-dir <analysis> --out-dir
#: <diagnostics>``, never touched by ``stage-sensitivity``).
STAGE_SENSITIVITY_SUBDIRS: dict[str, str] = {
    "export": "motco_input",
    "analysis": "analysis",
    "comparison": "comparison",
    "diagnostics": "diagnostics",
}
#: ``comparison/``: the primary and the arm side by side.
STAGE_SENSITIVITY_TABLE = "stage_sensitivity.csv"
STAGE_SENSITIVITY_SUMMARY = "stage_sensitivity.md"
STAGE_SENSITIVITY_MANIFEST = "stage_sensitivity_manifest.json"

# --- stage-sensitivity: scientific constants ----------------------------------

#: Decided by the change ``adni-stage-sensitivity`` (2026-10-29, before any run)
#: and never changed by a flag, a result or a count. The single CN / LMCI / AD
#: arm: the exported participants whose enrollment category ``dx_bl``
#: (``cohort.csv``, ADNIMERGE ``DX.bl`` on the baseline row) is in ``keep``,
#: staged by ``STAGE_RULE``'s own map (``stage_map``); the categories in
#: ``drop`` (SMC and EMCI, enrolled only in ADNI-GO/2) leave the arm. Its rows
#: are the primary export's rows of the kept participants, every cell unchanged
#: (the primary's floors and scale); its analysis is the primary's
#: (``ANALYSIS_*`` and MOTCO's defaults, no latent adjustment, ``n_jobs = 1``
#: for the reported run). It is not crossed with the latent adjustment or an
#: export variant. It is read beside the primary and never replaces it. The
#: assertions below tie it to ``STAGE_RULE``.
STAGE_SENSITIVITY_ARM: dict = {
    "name": "cn_lmci_ad",
    "source": "dx_bl",
    "keep": ("CN", "LMCI", "AD"),
    "drop": ("SMC", "EMCI"),
    "stage_map": {"CN": "CN", "LMCI": "MCI", "AD": "AD"},
    "floors": (
        "the primary export's (EXPORT_FEATURE_RULE over the exported participants); the arm's rows are the primary "
        "export's rows"
    ),
    "analysis": "the primary's (ANALYSIS_* constants and MOTCO's defaults; no latent adjustment)",
    "change": "adni-stage-sensitivity",
}
assert set(STAGE_SENSITIVITY_ARM["keep"]) | set(STAGE_SENSITIVITY_ARM["drop"]) == set(STAGE_RULE["map"]), (
    "STAGE_SENSITIVITY_ARM must keep or drop every category of STAGE_RULE's map"
)
assert all(STAGE_RULE["map"][dx] == stage for dx, stage in STAGE_SENSITIVITY_ARM["stage_map"].items()), (
    "STAGE_SENSITIVITY_ARM's stage_map must be STAGE_RULE's map for the categories it keeps"
)
assert tuple(STAGE_SENSITIVITY_ARM["stage_map"]) == STAGE_SENSITIVITY_ARM["keep"], (
    "STAGE_SENSITIVITY_ARM's stage_map must map exactly the kept categories, in their order"
)

#: Decided by the change ``adni-stage-sensitivity``, written before any run:
#: the binding reading rules of the CN / LMCI / AD arm, printed verbatim after
#: ``READING_RULES`` in the arm's ``summary.md``, in ``stage_sensitivity.md``,
#: in the arm's ``diagnostics.md`` and in every report that quotes the arm. The
#: numbers quoted are from the committed ``stage_counts.csv`` and the change's
#: spike, none from a run of the arm.
STAGE_SENSITIVITY_READING_RULES: tuple[str, ...] = (
    "The arm is read beside the primary and never replaces it. No arm result changes a constant, `STAGE_RULE` or "
    "`COHORT_RULE`, reruns the primary or adopts the arm.",
    "The arm's rows are the primary export's rows of the 1130 participants whose `DX.bl` is CN, LMCI or AD, with the "
    "cells unchanged (the primary's floors). The covariates, their coding and every analysis setting are the "
    "primary's. It differs in the participants: the 96 SMC and 275 EMCI participants, enrolled only in ADNI-GO/2, are "
    "dropped. Its CN is `DX.bl` CN and its MCI is LMCI. Its z-scoring, CV folds, latent basis, rank, covariate "
    "reference row and permutation draws are its own. A rejection status that differs is dependence on the stage "
    "definition and the sample, not a result of the arm.",
    "The arm's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that "
    "differs from the primary's is reported, not ranked.",
    "In the arm each stage holds one `DX.bl` category in both runs, so the `phase` coefficient of the stage-means "
    "model is estimated from contrasts within one diagnosis. In the primary, the ADNI-GO/2 rows of CN and MCI add SMC "
    "and EMCI. The arm neither balances the runs across stages nor removes the run offset, which is measurement: the "
    "ADNI-1 share per stage is CN 0.527, MCI 0.700, AD 0.544 in the arm and 0.417, 0.446, 0.544 in the primary; the "
    "p180 median |d| is 1.10 on the arm's rows and 1.12 on the primary's, and PC1's correlation with phase 0.71 and "
    "0.73. `phase` stays a covariate under the additive assumption of reading rule 5.",
    "The arm's MCI (LMCI) is a later and narrower stage than the primary's MCI, and its CN excludes subjective memory "
    "concern. A difference that involves the middle stage is a difference of stage definition. `angle` reads only the "
    "endpoint stages: the arm's AD cells are the primary's, and its CN cells lose the SMC participants.",
    "The arm holds 1130 of the 1501 participants. Its non-rejection is no more informative than the primary's: "
    "reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in the arm is "
    "dependence on the stage definition and the sample, read beside its rank and null summary.",
    "The arm's export manifest records its cells, the runs within each stage and the run offset on its rows, and they "
    "are reported beside the results with the primary's. A component of the arm that tracks a variable in its axis "
    "diagnostic is a measurement-space finding about the arm and never grounds to adopt it. In the arm, `dx_bl` "
    "orders the participants as `stage` does, so their correlations coincide.",
    "The arm is not crossed with the latent adjustment or an export variant, and is read against the primary only. No "
    "sentence reads it against another sensitivity.",
)

# --- stage-sensitivity: predeclared counts ------------------------------------

#: Predeclared by the change ``adni-stage-sensitivity`` from the committed
#: ``stage_counts.csv`` and its spike (``spike.md``, 2026-10-29; none from a run
#: of the arm). ``export``: the kept participants and the dropped ones per
#: ``dx_bl``, the sex × stage cells, the runs within each stage (``phase``), the
#: features per block (the primary's ``block_columns``), every row of the four
#: CSVs equal to the primary's, the missing covariate values and non-finite
#: cells, and the p180 metabolites with phase |d| above 0.5 and above 1 on the
#: arm's rows (NMR above 1). ``analysis``: every key of
#: ``ANALYSIS_EXPECTED_COUNTS`` with the arm's participants, cells and
#: covariate levels. ``diagnostics``: the rank-independent keys of
#: ``DIAGNOSTICS_EXPECTED_COUNTS`` with the arm's participants and cells. The
#: arm's rank is not predeclared. ``stage-sensitivity`` and ``axis-diagnostics``
#: compare the arm with these and record every difference as a finding; a
#: difference never stops a step and never changes a setting.
_STAGE_SENSITIVITY_CELLS: dict[str, dict[str, int]] = {
    "Female": {"CN": 183, "MCI": 187, "AD": 125},
    "Male": {"CN": 181, "MCI": 296, "AD": 158},
}
STAGE_SENSITIVITY_EXPECTED_COUNTS: dict[str, dict] = {
    "export": {
        "participants": 1130,
        "dropped": {"SMC": 96, "EMCI": 275},
        "sex_stage": _STAGE_SENSITIVITY_CELLS,
        "phase_by_stage": {
            "CN": {"ADNI1": 192, "ADNI2GO": 172},
            "MCI": {"ADNI1": 338, "ADNI2GO": 145},
            "AD": {"ADNI1": 154, "ADNI2GO": 129},
        },
        "features": {"p180": 133, "nmr": 165},
        "rows_equal_primary": {"p180.csv": True, "nmr.csv": True, EXPORT_METADATA: True, EXPORT_COVARIATES: True},
        "missing_covariate_values": 0,
        "non_finite": {"p180": 0, "nmr": 0},
        "phase_offset": {"p180": {"abs_d_gt_0_5": 107, "abs_d_gt_1": 77}, "nmr": {"abs_d_gt_1": 0}},
    },
    "analysis": {
        **ANALYSIS_EXPECTED_COUNTS,
        "participants": 1130,
        "sex_stage": _STAGE_SENSITIVITY_CELLS,
        "covariate_levels": {
            "apoe4": {"0": 589, "1": 413, "2": 128},
            "phase": {"ADNI1": 684, "ADNI2GO": 446},
            "statin": {"0": 603, "1": 527},
        },
    },
    "diagnostics": {
        **{key: DIAGNOSTICS_EXPECTED_COUNTS[key] for key in DIAGNOSTICS_RANK_INDEPENDENT_KEYS},
        "participants": 1130,
        "sex_stage": _STAGE_SENSITIVITY_CELLS,
    },
}


# --- rank-sensitivity: conventions --------------------------------------------

#: The analysis directory of one rank under ``RANK_SENSITIVITY_DIR``, the rank
#: in two digits so that directory order is rank order (``rank_02`` …
#: ``rank_12``). Each is laid out as ``MOTCO_ANALYSIS_DIR``; there is no
#: ``motco_input/``, since every rank reads the primary export.
RANK_SENSITIVITY_RANK_DIR = "rank_{rank:02d}"
#: The other subdirectories of ``RANK_SENSITIVITY_DIR``: ``comparison`` (the
#: primary and every rank side by side, written by ``rank-sensitivity``) and
#: ``diagnostics`` (``axis-diagnostics --analysis-dir <root>/rank_12 --out-dir
#: <diagnostics>``, never touched by ``rank-sensitivity``).
RANK_SENSITIVITY_SUBDIRS: dict[str, str] = {
    "comparison": "comparison",
    "diagnostics": "diagnostics",
}
#: ``comparison/``: the primary and the ranks side by side.
RANK_SENSITIVITY_TABLE = "rank_sensitivity.csv"
RANK_SENSITIVITY_SUMMARY = "rank_sensitivity.md"
RANK_SENSITIVITY_MANIFEST = "rank_sensitivity_manifest.json"

# --- rank-sensitivity: scientific constants -----------------------------------

#: Decided by the change ``adni-rank-sensitivity`` (2026-10-30, before any
#: forced rank ran on ADNI data) and never changed by a flag, a result or a
#: count. The single rank sweep: the primary analysis rerun once per rank of
#: ``ranks`` with MOTCO's ``forced_components`` set to the rank (the rank is
#: fixed and MOTCO's cross-validation skipped) and every other setting the
#: primary's (the primary export, ``ANALYSIS_*`` and MOTCO's defaults, no
#: latent adjustment, ``n_jobs = 1`` for the reported run), the same seed and
#: permutations at every rank. 2 is ``ANALYSIS_RANK_FLOOR`` and
#: ``n_stages − 1``; 3 the next rank; 4, 6, 9 and 12 the steps of MOTCO's rank
#: ladder and of the template's sweep. The primary's rank is not on the
#: ladder: one forced run at the primary record's rank (the anchor) must
#: reproduce the primary before any rank runs, and is not kept. The top rank
#: is the one the axis diagnostic reads (PLS-DA components are nested, so its
#: components hold every rank's). Not crossed with the latent adjustment, an
#: export variant or the CN / LMCI / AD arm. It is read beside the primary and
#: never replaces it. The assertions below keep the ladder ordered, tie its
#: bottom to the floor and its diagnosed rank to its top.
RANK_SENSITIVITY_LADDER: dict = {
    "name": "forced_rank_ladder",
    "setting": "forced_components",
    "ranks": (2, 3, 4, 6, 9, 12),
    "draws": "ANALYSIS_SEED and ANALYSIS_PERMUTATIONS at every rank (the same permutation indices at n_jobs = 1)",
    "anchor": "one forced run at the primary record's rank, compared with the primary before any rank runs; not kept",
    "diagnosed_rank": 12,
    "analysis": "the primary's (the primary export; ANALYSIS_* constants and MOTCO's defaults; no latent adjustment)",
    "change": "adni-rank-sensitivity",
}
assert RANK_SENSITIVITY_LADDER["ranks"] == tuple(sorted(set(RANK_SENSITIVITY_LADDER["ranks"]))), (
    "RANK_SENSITIVITY_LADDER's ranks must be distinct and in increasing order"
)
assert RANK_SENSITIVITY_LADDER["ranks"][0] == ANALYSIS_RANK_FLOOR, (
    "RANK_SENSITIVITY_LADDER's lowest rank must be ANALYSIS_RANK_FLOOR"
)
assert RANK_SENSITIVITY_LADDER["diagnosed_rank"] == max(RANK_SENSITIVITY_LADDER["ranks"]), (
    "RANK_SENSITIVITY_LADDER's diagnosed rank must be its top rank"
)

#: Decided by the change ``adni-rank-sensitivity``, written before any run:
#: the binding reading rules of the rank sweep, printed verbatim after
#: ``READING_RULES`` in each rank's ``summary.md``, in ``rank_sensitivity.md``,
#: in the top rank's ``diagnostics.md`` and in every report that quotes the
#: sweep. The forced-rank evidence quoted is MOTCO's rank ladder
#: (``latent-rank-ladder-2026-09-08``), none from a forced run on ADNI data.
RANK_SENSITIVITY_READING_RULES: tuple[str, ...] = (
    "The sweep is read beside the primary and never replaces it. The primary's rank is its CV-selected rank (8). No "
    "rank of the sweep is chosen, adopted or ranked, and no sweep result changes a constant (`ANALYSIS_RANK_FLOOR` "
    "and the ladder included), reruns the primary or defines another arm.",
    "Every rank is the primary's analysis with one setting changed: `forced_components`, which fixes the rank and "
    "skips MOTCO's cross-validation. The export, the covariates and their coding, the seed, the permutations and "
    "every other setting are the primary's, and at `n_jobs = 1` every rank permutes the same residual indices. A "
    "difference between ranks is a difference of measurement, not of permutation draws. A rejection status that "
    "differs from the primary's is rank dependence, not a result at that rank.",
    "PLS-DA components are nested. At a forced rank at or below the primary's 8, the latent space is spanned by the "
    "primary's first components; a rank above 8 adds components the cross-validation did not select. The anchor run "
    "at rank 8 reproduces the primary's record and files exactly, so the primary row is also the sweep's row at its "
    "rank.",
    "Each rank's floor, eigengap and `angle` null summary are reported beside its `angle`. The `angle` null depends "
    "on the rank, so each `angle` is read against its own null, never against the `angle` of another rank. At rank "
    "2, the floor, `angle` and `shape` are measured in two dimensions (reading rule 2).",
    "MOTCO's forced-rank evidence is its Phase 5 rank ladder (2026-09-08; MOTCO 0.6.0, n = 1200, four stages, no "
    "covariates): size held at every forced rank, and the ranks above `n_stages − 1` lost `shape` power and gained "
    "no `angle` power. No Type I or power check exists at a forced rank at this design or with covariates. A "
    "non-rejection at any rank is no more informative than the primary's (reading rule 3), and a rejection at a "
    "forced rank only is rank dependence, read beside that rank's null summary.",
    "The sweep is not a test. No rule combines the ranks, picks the rank with the smallest p-value or counts the "
    "ranks that reject, and the p-values are not adjusted for multiplicity because no decision is taken from them.",
    "The axis diagnostic of the top rank (12) is reported beside the sweep. Its components up to the primary's rank "
    "are the primary's, with the primary's correlations. A component above it that tracks a variable, `phase` in "
    "particular, is a measurement-space finding about the higher ranks and never grounds to choose a rank.",
    "The sweep is not crossed with the latent adjustment, an export variant or the CN / LMCI / AD arm, and is read "
    "against the primary only. The CV-selected ranks of those analyses are their own selections, and no sentence "
    "reads them against the sweep.",
)

# --- rank-sensitivity: predeclared counts -------------------------------------

#: Predeclared by the change ``adni-rank-sensitivity`` from the committed
#: primary manifests and the ladder (none from a forced run on ADNI data).
#: ``anchor``: the primary record's rank, at which the anchor runs.
#: ``analysis``, per rank: every key of ``ANALYSIS_EXPECTED_COUNTS`` with
#: selection ``forced``, the forced rank and no CV repeat. ``comparison``: the
#: primary row and one row per rank. ``diagnostics``: the rank-independent keys
#: of ``DIAGNOSTICS_EXPECTED_COUNTS``, the read (the top rank, forced, no latent
#: adjustment, ``n_jobs`` 1) and the rows the four tables hold at that rank
#: (12 × 8, 2 × 3 × 8, 4 × 12, 12). No rank's statistic or status is
#: predeclared. ``rank-sensitivity`` and ``axis-diagnostics`` compare the sweep
#: with these and record every difference as a finding; a difference never
#: stops a step and never changes a setting.
RANK_SENSITIVITY_EXPECTED_COUNTS: dict[str, dict] = {
    "anchor": {"rank": DIAGNOSTICS_EXPECTED_COUNTS["primary"]["selected_rank"]},
    "analysis": {
        rank: {**ANALYSIS_EXPECTED_COUNTS, "component_selection": "forced", "selected_rank": rank, "cv_repeats_completed": 0}
        for rank in RANK_SENSITIVITY_LADDER["ranks"]
    },
    "comparison": {"rows": 1 + len(RANK_SENSITIVITY_LADDER["ranks"])},
    "diagnostics": {
        **{key: DIAGNOSTICS_EXPECTED_COUNTS[key] for key in DIAGNOSTICS_RANK_INDEPENDENT_KEYS},
        "primary": {
            "selected_rank": 12,
            "component_selection": "forced",
            "latent_adjustment": ANALYSIS_LATENT_ADJUSTMENT,
            "n_jobs": REPORTED_N_JOBS,
        },
        "rows": {"axis_correlations": 96, "block_pcs": 48, "geometry_shares": 48, "components": 12},
    },
}


# --- report: conventions ------------------------------------------------------

#: The six files ``axis-diagnostics`` writes, all aggregate; the report reads
#: them for the primary, for the arm and for every export variant.
DIAGNOSTICS_FILES: tuple[str, ...] = (
    DIAGNOSTICS_AXIS_CORRELATIONS,
    DIAGNOSTICS_BLOCK_PCS,
    DIAGNOSTICS_GEOMETRY_SHARES,
    DIAGNOSTICS_COMPONENTS,
    DIAGNOSTICS_SUMMARY,
    DIAGNOSTICS_MANIFEST,
)
#: The files the report reads in each subdirectory of an export variant, by
#: the key of ``EXPORT_SENSITIVITY_SUBDIRS`` (change ``adni-report-variants``):
#: ``bridge`` only for a variant with hook ``factors``; the variant export's
#: CSVs, ``features_<platform>.csv`` and the variant analysis'
#: ``latent_scores.csv``, ``analysis_metadata.csv``, ``stage_means.csv`` and
#: ``pls_loadings.csv`` are quoted by the hashes their manifests record.
REPORT_VARIANT_FILES: dict[str, tuple[str, ...]] = {
    "bridge": (EXPORT_SENSITIVITY_BRIDGE_TABLE,),
    "export": (EXPORT_MANIFEST,),
    "analysis": (ANALYSIS_RESULT, ANALYSIS_MANIFEST, ANALYSIS_SUMMARY),
    "comparison": (EXPORT_SENSITIVITY_TABLE, EXPORT_SENSITIVITY_SUMMARY, EXPORT_SENSITIVITY_MANIFEST),
    "diagnostics": DIAGNOSTICS_FILES,
}
#: The files the report reads in each subdirectory of the CN / LMCI / AD arm,
#: by the key of ``STAGE_SENSITIVITY_SUBDIRS`` (change
#: ``adni-report-stage-arm``): the arm export's manifest, the arm analysis'
#: three aggregate files, the comparison's three files and the arm
#: diagnostics' six; the arm export's CSVs and the arm analysis'
#: ``latent_scores.csv``, ``analysis_metadata.csv``, ``stage_means.csv`` and
#: ``pls_loadings.csv`` are quoted by the hashes their manifests record.
REPORT_STAGE_ARM_FILES: dict[str, tuple[str, ...]] = {
    "export": (EXPORT_MANIFEST,),
    "analysis": (ANALYSIS_RESULT, ANALYSIS_MANIFEST, ANALYSIS_SUMMARY),
    "comparison": (STAGE_SENSITIVITY_TABLE, STAGE_SENSITIVITY_SUMMARY, STAGE_SENSITIVITY_MANIFEST),
    "diagnostics": DIAGNOSTICS_FILES,
}
assert tuple(REPORT_STAGE_ARM_FILES) == tuple(STAGE_SENSITIVITY_SUBDIRS), (
    "REPORT_STAGE_ARM_FILES must name the files of every STAGE_SENSITIVITY_SUBDIRS key, in its order"
)
#: The files the report reads in the rank sweep (change
#: ``adni-report-rank-sweep``): ``rank`` in each rank directory
#: (``RANK_SENSITIVITY_RANK_DIR``, one per rank of ``RANK_SENSITIVITY_LADDER``),
#: then by the key of ``RANK_SENSITIVITY_SUBDIRS``: the comparison's three
#: files and the top rank's diagnostics' six. Each rank's
#: ``latent_scores.csv``, ``analysis_metadata.csv``, ``stage_means.csv`` and
#: ``pls_loadings.csv`` are quoted by the hashes its manifest records.
REPORT_RANK_SWEEP_FILES: dict[str, tuple[str, ...]] = {
    "rank": (ANALYSIS_RESULT, ANALYSIS_MANIFEST, ANALYSIS_SUMMARY),
    "comparison": (RANK_SENSITIVITY_TABLE, RANK_SENSITIVITY_SUMMARY, RANK_SENSITIVITY_MANIFEST),
    "diagnostics": DIAGNOSTICS_FILES,
}
assert tuple(REPORT_RANK_SWEEP_FILES) == ("rank", *RANK_SENSITIVITY_SUBDIRS), (
    "REPORT_RANK_SWEEP_FILES must name the files of a rank directory, then of every RANK_SENSITIVITY_SUBDIRS key, in "
    "its order"
)
#: The export variants the report reads, checks and quotes, in registry order
#: (change ``adni-nmr-all-columns``, design D6): the report's coverage. A
#: registered variant outside it is not read or required and leaves the
#: report's body unchanged; ``report`` names it on a progress line. The change
#: that adds a variant to the report extends this tuple and re-issues the
#: report: ``nmr_all_columns`` by the change ``adni-report-nmr-all-columns``
#: (design D1), ``raw_scale``, ``log2_plus_one`` and ``glog`` by the change
#: ``adni-report-scale-variants`` (design D1), so every registered variant is
#: covered. ``report --check`` compares it with the variants a report lists
#: (its ``Export variant`` headings), and a report of an earlier pin is an
#: earlier layout.
REPORT_EXPORT_VARIANTS: tuple[str, ...] = (
    "nist_bridge",
    "per_run_standardized",
    "nmr_all_columns",
    "raw_scale",
    "log2_plus_one",
    "glog",
)
assert [variant for variant in EXPORT_VARIANTS if variant in REPORT_EXPORT_VARIANTS] == list(REPORT_EXPORT_VARIANTS), (
    "REPORT_EXPORT_VARIANTS must be a subsequence of EXPORT_VARIANTS, in registry order, each name once"
)
#: Every file the ``report`` step reads (change ``adni-report``), by the role
#: of the directory it lives in: ``cleaned`` (``--cleaned-dir``, paths
#: relative to the cleaned root), ``cohort`` (``--cohort-dir``), ``export``
#: (``--input-dir``), ``analysis`` (``--analysis-dir``, the primary),
#: ``diagnostics`` (``--diagnostics-dir``, the primary's) and the three
#: subdirectories of ``--sensitivity-dir`` (``LATENT_SENSITIVITY_SUBDIRS``:
#: the arm's analysis, the comparison and the arm's diagnostics), and, per
#: variant of ``REPORT_EXPORT_VARIANTS`` in registry order (change
#: ``adni-report-variants``; the pin, change ``adni-nmr-all-columns``; its
#: third variant, change ``adni-report-nmr-all-columns``; the three scale
#: variants, change ``adni-report-scale-variants``), the
#: roles ``export-sensitivity/<variant>/<subdir>``
#: of ``--export-sensitivity-dir`` (``EXPORT_SENSITIVITY_SUBDIRS`` in its
#: order: the bridge table for a variant with hook ``factors``, the variant
#: export's manifest, the variant analysis' three aggregate files, the
#: comparison's three files and the variant diagnostics' six), and the roles
#: ``stage-sensitivity/<subdir>`` of ``--stage-sensitivity-dir`` (change
#: ``adni-report-stage-arm``; ``STAGE_SENSITIVITY_SUBDIRS`` in its order, the
#: files of ``REPORT_STAGE_ARM_FILES``), and the roles
#: ``rank-sensitivity/<rank_kk>`` (one per rank of ``RANK_SENSITIVITY_LADDER``
#: in ladder order, named by ``RANK_SENSITIVITY_RANK_DIR``) and
#: ``rank-sensitivity/<subdir>`` of ``--rank-sensitivity-dir`` (change
#: ``adni-report-rank-sweep``; ``RANK_SENSITIVITY_SUBDIRS`` in its order, the
#: files of ``REPORT_RANK_SWEEP_FILES``). All 145 are aggregate and committed
#: (93 before ``adni-report-nmr-all-columns`` added the 13 of
#: ``nmr_all_columns``, which has no bridge table, and 106 before
#: ``adni-report-scale-variants`` added the 13 of each scale variant, which
#: have none either);
#: no participant-level file is read, and the hashes the report quotes for
#: one come from these manifests. No other file is read.
REPORT_INPUT_FILES: dict[str, tuple[str, ...]] = {
    "cleaned": tuple(f"{platform}/{CLEAN_MANIFEST}" for platform in PLATFORMS),
    "cohort": (COHORT_COUNTS, COHORT_MANIFEST),
    "export": (EXPORT_MANIFEST,),
    "analysis": (ANALYSIS_RESULT, ANALYSIS_MANIFEST, ANALYSIS_SUMMARY),
    "diagnostics": DIAGNOSTICS_FILES,
    f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['analysis']}": (ANALYSIS_RESULT, ANALYSIS_MANIFEST, ANALYSIS_SUMMARY),
    f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['comparison']}": (
        LATENT_SENSITIVITY_TABLE,
        LATENT_SENSITIVITY_SUMMARY,
        LATENT_SENSITIVITY_MANIFEST,
    ),
    f"sensitivity/{LATENT_SENSITIVITY_SUBDIRS['diagnostics']}": DIAGNOSTICS_FILES,
    **{
        f"export-sensitivity/{variant}/{sub}": REPORT_VARIANT_FILES[key]
        for variant in REPORT_EXPORT_VARIANTS
        for key, sub in EXPORT_SENSITIVITY_SUBDIRS.items()
        if key != "bridge" or EXPORT_VARIANTS[variant]["hook"] == "factors"
    },
    **{f"stage-sensitivity/{sub}": REPORT_STAGE_ARM_FILES[key] for key, sub in STAGE_SENSITIVITY_SUBDIRS.items()},
    **{
        f"rank-sensitivity/{RANK_SENSITIVITY_RANK_DIR.format(rank=rank)}": REPORT_RANK_SWEEP_FILES["rank"]
        for rank in RANK_SENSITIVITY_LADDER["ranks"]
    },
    **{f"rank-sensitivity/{sub}": REPORT_RANK_SWEEP_FILES[key] for key, sub in RANK_SENSITIVITY_SUBDIRS.items()},
}
#: The report's level-2 sections, in order (design D4 of ``adni-report``;
#: "Export sensitivity" added by ``adni-report-variants``, "Stage-definition
#: sensitivity" by ``adni-report-stage-arm``, "Rank sensitivity" by
#: ``adni-report-rank-sweep``).
#: ``report --check`` names a mismatch by section, table, row and column.
REPORT_SECTIONS: tuple[str, ...] = (
    "Summary",
    "Provenance",
    "Cohort",
    "Export",
    "Primary analysis",
    "Axis diagnostics of the primary",
    "Latent-adjustment sensitivity",
    "Export sensitivity",
    "Stage-definition sensitivity",
    "Rank sensitivity",
    "Findings",
    "Reading rules",
    "Reproduction",
)
