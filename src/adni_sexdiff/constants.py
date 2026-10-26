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
    the change ``adni-cohort``. The others are undecided and not defined;
    the names reserved for them (a proposal may rename them) are:

    - ``ANALYSIS_PERMUTATIONS``, ``ANALYSIS_SEED``, ``ANALYSIS_ALPHA`` –
      MOTCO's RRPP permutations, seed and rejection rule.
    - ``ANALYSIS_RANK_FLOOR`` – the latent-rank floor passed to MOTCO.
    - ``EXPORT_FEATURE_RULE`` – which cleaned metabolites enter each block
      and on which scale.
    - ``DIAGNOSTIC_VARIABLES``, ``DIAGNOSTIC_CORRELATION_THRESHOLD`` – the
      axis diagnostics' variables and reporting flag.
    - ``READING_RULES`` – the binding reading rules of the report.
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
