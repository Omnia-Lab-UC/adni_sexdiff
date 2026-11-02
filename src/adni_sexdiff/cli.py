"""Command-line interface for adni-sexdiff.

A thin argparse layer over ``data.py``: one subcommand per pipeline step
(``clean``, ``cohort``, ``export``, ``analyze``, ``axis-diagnostics``,
``report``) and one per sensitivity step (``latent-sensitivity``,
``export-sensitivity``, ``stage-sensitivity``, ``rank-sensitivity``), each
printing ``[command]``-prefixed progress messages that name files and
counts, never a participant. ``report --check`` exits 1 on any mismatch.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .constants import (
    CLEANED_DIR,
    COHORT_DIR,
    DATA_ROOT_ENV,
    DEFAULT_DATA_ROOT,
    DIAGNOSTICS_DIR,
    EXPORT_SENSITIVITY_DIR,
    EXPORT_SENSITIVITY_SUBDIRS,
    EXPORT_VARIANTS,
    LATENT_SENSITIVITY_DIR,
    LATENT_SENSITIVITY_SUBDIRS,
    MOTCO_ANALYSIS_DIR,
    MOTCO_INPUT_DIR,
    PLATFORMS,
    RANK_SENSITIVITY_DIR,
    RANK_SENSITIVITY_LADDER,
    RANK_SENSITIVITY_RANK_DIR,
    RANK_SENSITIVITY_SUBDIRS,
    REPORT_EXPORT_VARIANTS,
    REPORT_NAME,
    REPORT_NAME_SAME_DAY,
    REPORTED_N_JOBS,
    REPORTS_DIR,
    STAGE_SENSITIVITY_DIR,
    STAGE_SENSITIVITY_SUBDIRS,
)
from .data import (
    run_analysis,
    run_axis_diagnostics,
    run_clean,
    run_cohort,
    run_export,
    run_export_sensitivity,
    run_latent_sensitivity,
    run_rank_sensitivity,
    run_report,
    run_stage_sensitivity,
)


def _add_force(p: argparse.ArgumentParser) -> None:
    p.add_argument("--force", action="store_true", help="Replace an existing output directory")


def _add_data_root(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help=f"Directory holding the raw ADNI files (default: ${DATA_ROOT_ENV}, then {DEFAULT_DATA_ROOT}/)",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with one subcommand per pipeline step.

    Returns
    -------
    argparse.ArgumentParser
        The parser; ``main`` dispatches on ``args.command``.
    """
    parser = argparse.ArgumentParser(
        prog="adni-sexdiff",
        description=(
            "Sex x stage (CN / MCI / AD) trajectory comparison on ADNI serum "
            "metabolomics (Biocrates p180, Nightingale NMR) with MOTCO."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("clean", help="Clean the raw ADNI files per platform through metabo_adni -> results/cleaned/")
    p.add_argument("--platform", choices=[*PLATFORMS, "all"], default="all", help="Platform to clean (default: all)")
    _add_data_root(p)
    p.add_argument("--out-dir", type=Path, default=None, help=f"Cleaned root (default: {CLEANED_DIR})")
    _add_force(p)

    p = sub.add_parser(
        "cohort",
        help="One baseline row per participant (sex, merged stage, covariates) for the p180 and NMR sets "
        "and their intersection, sex x stage counts -> results/cohort/",
    )
    p.add_argument("--cleaned-dir", type=Path, default=None, help=f"Output root of clean (default: {CLEANED_DIR})")
    _add_data_root(p)
    p.add_argument("--out-dir", type=Path, default=None, help=f"Cohort directory (default: {COHORT_DIR})")
    _add_force(p)

    p = sub.add_parser(
        "export",
        help="MOTCO blocks under the feature rule, metadata and covariates of the analysis cohort from the cleaned "
        "matrices and the cohort -> results/motco_input/",
    )
    p.add_argument("--cleaned-dir", type=Path, default=None, help=f"Output root of clean (default: {CLEANED_DIR})")
    p.add_argument("--cohort-dir", type=Path, default=None, help=f"Output directory of cohort (default: {COHORT_DIR})")
    p.add_argument("--out-dir", type=Path, default=None, help=f"MOTCO input directory (default: {MOTCO_INPUT_DIR})")
    _add_force(p)

    p = sub.add_parser(
        "analyze",
        help="Covariate-adjusted MOTCO trajectory analysis (one analyze_trajectories call at the predeclared "
        "settings) on the exported blocks -> results/motco_analysis/",
    )
    p.add_argument("--input-dir", type=Path, default=None, help=f"Output directory of export (default: {MOTCO_INPUT_DIR})")
    p.add_argument("--out-dir", type=Path, default=None, help=f"Analysis directory (default: {MOTCO_ANALYSIS_DIR})")
    p.add_argument(
        "--n-jobs",
        type=int,
        default=REPORTED_N_JOBS,
        help=f"Parallel jobs for MOTCO's CV and RRPP (default: {REPORTED_N_JOBS}; reported runs use {REPORTED_N_JOBS})",
    )
    _add_force(p)

    p = sub.add_parser(
        "axis-diagnostics",
        help="Spearman and design-partial correlations of the latent components and the block PCs with the predeclared "
        "variables, the geometry shares and the block composition per component, from the kept outputs only "
        "-> results/motco_diagnostics/",
    )
    p.add_argument("--input-dir", type=Path, default=None, help=f"Output directory of export (default: {MOTCO_INPUT_DIR})")
    p.add_argument("--analysis-dir", type=Path, default=None, help=f"Output directory of analyze (default: {MOTCO_ANALYSIS_DIR})")
    p.add_argument("--cohort-dir", type=Path, default=None, help=f"Output directory of cohort (default: {COHORT_DIR})")
    p.add_argument("--out-dir", type=Path, default=None, help=f"Diagnostics directory (default: {DIAGNOSTICS_DIR})")
    _add_force(p)

    p = sub.add_parser(
        "latent-sensitivity",
        help="The predeclared stage-conditioned latent-adjustment arm (LATENT_SENSITIVITY_ARM: one analyze_trajectories "
        "call at the primary's settings plus covariate_latent_adjustment = stage) and its comparison with the primary, "
        f"read beside it and never replacing it -> {LATENT_SENSITIVITY_DIR}/{{{LATENT_SENSITIVITY_SUBDIRS['analysis']},"
        f"{LATENT_SENSITIVITY_SUBDIRS['comparison']}}}/",
    )
    p.add_argument("--input-dir", type=Path, default=None, help=f"Output directory of export (default: {MOTCO_INPUT_DIR})")
    p.add_argument(
        "--analysis-dir", type=Path, default=None,
        help=f"The primary's analysis directory, read as the reference, never written (default: {MOTCO_ANALYSIS_DIR})",
    )
    p.add_argument(
        "--cohort-dir", type=Path, default=None,
        help=f"Output directory of cohort; only cohort_manifest.json is read (default: {COHORT_DIR})",
    )
    p.add_argument(
        "--out-dir", type=Path, default=None,
        help=f"Output root; {LATENT_SENSITIVITY_SUBDIRS['analysis']}/ and {LATENT_SENSITIVITY_SUBDIRS['comparison']}/ are "
        f"written under it, {LATENT_SENSITIVITY_SUBDIRS['diagnostics']}/ never (default: {LATENT_SENSITIVITY_DIR})",
    )
    p.add_argument(
        "--n-jobs",
        type=int,
        default=REPORTED_N_JOBS,
        help=f"Parallel jobs for MOTCO's CV and RRPP (default: {REPORTED_N_JOBS}; reported runs use {REPORTED_N_JOBS})",
    )
    _add_force(p)

    written = ", ".join(EXPORT_SENSITIVITY_SUBDIRS[k] for k in ("bridge", "export", "analysis", "comparison"))
    p = sub.add_parser(
        "export-sensitivity",
        help="Predeclared export variants, of the p180 run handling, the NMR membership or the scale of both blocks "
        "(EXPORT_VARIANTS: "
        + ", ".join(EXPORT_VARIANTS)
        + "): each reruns the export with its one setting, analyses it at the primary's settings and compares it "
        f"with the primary, read beside it and never replacing it -> {EXPORT_SENSITIVITY_DIR}/<variant>/{{{written}}}/",
    )
    p.add_argument(
        "--variant", required=True, choices=[*EXPORT_VARIANTS, "all"],
        help="The registered variant to run, or all of them in registry order (" + ", ".join(EXPORT_VARIANTS) + ")",
    )
    _add_data_root(p)
    p.add_argument("--cleaned-dir", type=Path, default=None, help=f"Output root of clean (default: {CLEANED_DIR})")
    p.add_argument("--cohort-dir", type=Path, default=None, help=f"Output directory of cohort (default: {COHORT_DIR})")
    p.add_argument(
        "--input-dir", type=Path, default=None,
        help=f"The primary export, read as the reference, never written (default: {MOTCO_INPUT_DIR})",
    )
    p.add_argument(
        "--analysis-dir", type=Path, default=None,
        help=f"The primary's analysis directory, read as the reference, never written (default: {MOTCO_ANALYSIS_DIR})",
    )
    p.add_argument(
        "--out-dir", type=Path, default=None,
        help=f"Output root; <variant>/{{{written}}}/ are written under it, <variant>/"
        f"{EXPORT_SENSITIVITY_SUBDIRS['diagnostics']}/ never (default: {EXPORT_SENSITIVITY_DIR})",
    )
    p.add_argument(
        "--n-jobs",
        type=int,
        default=REPORTED_N_JOBS,
        help=f"Parallel jobs for MOTCO's CV and RRPP (default: {REPORTED_N_JOBS}; reported runs use {REPORTED_N_JOBS})",
    )
    _add_force(p)

    written = ", ".join(STAGE_SENSITIVITY_SUBDIRS[k] for k in ("export", "analysis", "comparison"))
    p = sub.add_parser(
        "stage-sensitivity",
        help="The predeclared CN / LMCI / AD arm (STAGE_SENSITIVITY_ARM: the primary export's rows of the participants "
        "whose DX.bl is CN, LMCI or AD, SMC and EMCI dropped, analysed at the primary's settings) and its comparison "
        f"with the primary, read beside it and never replacing it -> {STAGE_SENSITIVITY_DIR}/{{{written}}}/",
    )
    p.add_argument(
        "--input-dir", type=Path, default=None,
        help=f"The primary export, read as the reference and copied by rows, never written (default: {MOTCO_INPUT_DIR})",
    )
    p.add_argument(
        "--analysis-dir", type=Path, default=None,
        help=f"The primary's analysis directory, read as the reference, never written (default: {MOTCO_ANALYSIS_DIR})",
    )
    p.add_argument(
        "--cohort-dir", type=Path, default=None,
        help=f"Output directory of cohort; cohort.csv (dx_bl) and cohort_manifest.json are read (default: {COHORT_DIR})",
    )
    p.add_argument(
        "--out-dir", type=Path, default=None,
        help=f"Output root; {{{written}}}/ are written under it, {STAGE_SENSITIVITY_SUBDIRS['diagnostics']}/ never "
        f"(default: {STAGE_SENSITIVITY_DIR})",
    )
    p.add_argument(
        "--n-jobs",
        type=int,
        default=REPORTED_N_JOBS,
        help=f"Parallel jobs for MOTCO's CV and RRPP (default: {REPORTED_N_JOBS}; reported runs use {REPORTED_N_JOBS})",
    )
    _add_force(p)

    ranks = ", ".join(str(k) for k in RANK_SENSITIVITY_LADDER["ranks"])
    rank_dirs = RANK_SENSITIVITY_RANK_DIR.replace("{rank:02d}", "<kk>")
    p = sub.add_parser(
        "rank-sensitivity",
        help=f"The predeclared rank sweep (RANK_SENSITIVITY_LADDER: the primary's analysis at the forced ranks {ranks}, "
        "after an anchor run at the primary's rank reproduces the primary) and its comparison with the primary, read "
        f"beside it and never replacing it -> {RANK_SENSITIVITY_DIR}/{{{rank_dirs},{RANK_SENSITIVITY_SUBDIRS['comparison']}}}/",
    )
    p.add_argument(
        "--input-dir", type=Path, default=None,
        help=f"The primary export, read as analyze reads it, never written (default: {MOTCO_INPUT_DIR})",
    )
    p.add_argument(
        "--analysis-dir", type=Path, default=None,
        help=f"The primary's analysis directory, read as the reference, never written (default: {MOTCO_ANALYSIS_DIR})",
    )
    p.add_argument(
        "--out-dir", type=Path, default=None,
        help=f"Output root; one {rank_dirs}/ per rank and {RANK_SENSITIVITY_SUBDIRS['comparison']}/ are written under it, "
        f"{RANK_SENSITIVITY_SUBDIRS['diagnostics']}/ never (default: {RANK_SENSITIVITY_DIR})",
    )
    p.add_argument(
        "--n-jobs",
        type=int,
        default=REPORTED_N_JOBS,
        help=f"Parallel jobs for MOTCO's RRPP (default: {REPORTED_N_JOBS}; reported runs use {REPORTED_N_JOBS})",
    )
    _add_force(p)

    p = sub.add_parser(
        "report",
        help="Write the case-study report from the kept aggregate outputs (no participant-level file is read), or check "
        f"one against them cell by cell -> {REPORTS_DIR}/{REPORT_NAME.format(date='<date>')}",
    )
    p.add_argument("--cleaned-dir", type=Path, default=None, help=f"Output root of clean; the clean manifests are read (default: {CLEANED_DIR})")
    p.add_argument("--cohort-dir", type=Path, default=None, help=f"Output directory of cohort (default: {COHORT_DIR})")
    p.add_argument("--input-dir", type=Path, default=None, help=f"Output directory of export; its manifest is read (default: {MOTCO_INPUT_DIR})")
    p.add_argument("--analysis-dir", type=Path, default=None, help=f"The primary's analysis directory (default: {MOTCO_ANALYSIS_DIR})")
    p.add_argument("--diagnostics-dir", type=Path, default=None, help=f"The primary's diagnostics directory (default: {DIAGNOSTICS_DIR})")
    p.add_argument(
        "--sensitivity-dir", type=Path, default=None,
        help=f"Root of latent-sensitivity, read as {'/, '.join(LATENT_SENSITIVITY_SUBDIRS.values())}/ (default: {LATENT_SENSITIVITY_DIR})",
    )
    p.add_argument(
        "--export-sensitivity-dir", type=Path, default=None,
        help=f"Root of export-sensitivity, read per variant of REPORT_EXPORT_VARIANTS ({', '.join(REPORT_EXPORT_VARIANTS)}) as <variant>/"
        f"{'/, <variant>/'.join(EXPORT_SENSITIVITY_SUBDIRS.values())}/ (default: {EXPORT_SENSITIVITY_DIR})",
    )
    p.add_argument(
        "--stage-sensitivity-dir", type=Path, default=None,
        help=f"Root of stage-sensitivity (the CN / LMCI / AD arm), read as {'/, '.join(STAGE_SENSITIVITY_SUBDIRS.values())}/ "
        f"(default: {STAGE_SENSITIVITY_DIR})",
    )
    p.add_argument(
        "--rank-sensitivity-dir", type=Path, default=None,
        help=f"Root of rank-sensitivity (the rank sweep), read as one {rank_dirs}/ per rank ({ranks}), then "
        f"{'/, '.join(RANK_SENSITIVITY_SUBDIRS.values())}/ (default: {RANK_SENSITIVITY_DIR})",
    )
    p.add_argument(
        "--out", type=Path, default=None,
        help=f"Report path, named {REPORT_NAME.format(date='<date>')}, or {REPORT_NAME_SAME_DAY.format(date='<date>', n='<n>')} "
        f"(<n> 2 or more) for a later report of the same day; the date and the ordinal are read from the name (default: "
        f"{REPORTS_DIR}/{REPORT_NAME.format(date='<today>')}, or with --check the newest report there by date, then ordinal)",
    )
    p.add_argument(
        "--check", action="store_true",
        help="Compare the report at --out with the one the outputs now generate, every table cell by cell and every other "
        "line line by line, instead of writing it; exits 1 on any mismatch and writes nothing",
    )
    p.add_argument("--force", action="store_true", help="Replace an existing report at --out")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run the requested step.

    Parameters
    ----------
    argv:
        Arguments without the program name; ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        Process exit status (0 on success).
    """
    args = build_parser().parse_args(argv)
    if args.command == "clean":
        run_clean(platform=args.platform, data_root=args.data_root, out_dir=args.out_dir, force=args.force)
    elif args.command == "cohort":
        run_cohort(cleaned_dir=args.cleaned_dir, data_root=args.data_root, out_dir=args.out_dir, force=args.force)
    elif args.command == "export":
        run_export(cleaned_dir=args.cleaned_dir, cohort_dir=args.cohort_dir, out_dir=args.out_dir, force=args.force)
    elif args.command == "analyze":
        run_analysis(input_dir=args.input_dir, out_dir=args.out_dir, n_jobs=args.n_jobs, force=args.force)
    elif args.command == "axis-diagnostics":
        run_axis_diagnostics(
            input_dir=args.input_dir,
            analysis_dir=args.analysis_dir,
            cohort_dir=args.cohort_dir,
            out_dir=args.out_dir,
            force=args.force,
        )
    elif args.command == "latent-sensitivity":
        run_latent_sensitivity(
            input_dir=args.input_dir,
            analysis_dir=args.analysis_dir,
            cohort_dir=args.cohort_dir,
            out_dir=args.out_dir,
            n_jobs=args.n_jobs,
            force=args.force,
        )
    elif args.command == "export-sensitivity":
        run_export_sensitivity(
            variant=args.variant,
            data_root=args.data_root,
            cleaned_dir=args.cleaned_dir,
            cohort_dir=args.cohort_dir,
            input_dir=args.input_dir,
            analysis_dir=args.analysis_dir,
            out_dir=args.out_dir,
            n_jobs=args.n_jobs,
            force=args.force,
        )
    elif args.command == "stage-sensitivity":
        run_stage_sensitivity(
            input_dir=args.input_dir,
            analysis_dir=args.analysis_dir,
            cohort_dir=args.cohort_dir,
            out_dir=args.out_dir,
            n_jobs=args.n_jobs,
            force=args.force,
        )
    elif args.command == "rank-sensitivity":
        run_rank_sensitivity(
            input_dir=args.input_dir,
            analysis_dir=args.analysis_dir,
            out_dir=args.out_dir,
            n_jobs=args.n_jobs,
            force=args.force,
        )
    elif args.command == "report":
        result = run_report(
            cleaned_dir=args.cleaned_dir,
            cohort_dir=args.cohort_dir,
            input_dir=args.input_dir,
            analysis_dir=args.analysis_dir,
            diagnostics_dir=args.diagnostics_dir,
            sensitivity_dir=args.sensitivity_dir,
            export_sensitivity_dir=args.export_sensitivity_dir,
            stage_sensitivity_dir=args.stage_sensitivity_dir,
            rank_sensitivity_dir=args.rank_sensitivity_dir,
            out=args.out,
            check=args.check,
            force=args.force,
        )
        if result["mismatches"]:
            return 1
    else:  # pragma: no cover - argparse enforces the choices
        raise SystemExit(f"Unknown command {args.command!r}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
