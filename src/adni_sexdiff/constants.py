"""Named constants of the adni_sexdiff pipeline.

Two kinds of constant live here.

Conventions
    Paths, environment variables, platform and column names, output file
    names, version pins and the reporting rules of ``AGENTS.md``. They are
    defined below and may be changed by an ordinary change.

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
    ``adni-analyze``. The others are undecided and not defined; the names
    reserved for them (a proposal may rename them) are:

    - ``DIAGNOSTIC_VARIABLES``, ``DIAGNOSTIC_CORRELATION_THRESHOLD`` – the
      axis diagnostics' variables and reporting flag.
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
DIAGNOSTICS_SUMMARY = "diagnostics.md"
DIAGNOSTICS_MANIFEST = "diagnostics_manifest.json"
#: ``report``: ``<REPORTS_DIR>/motco-adni-<date>.md``.
REPORT_NAME = "motco-adni-{date}.md"

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
#: and the ADNIMERGE freeze at ``adni-cohort``. A step that finds another
#: hash records a finding (a fresh download); the predeclared counts hold
#: for these bytes only.
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
