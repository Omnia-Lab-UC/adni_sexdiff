"""Command-line interface for adni-sexdiff.

A thin argparse layer over ``data.py``: one subcommand per pipeline step
(``clean``, ``cohort``, ``export``, ``analyze``, ``axis-diagnostics``,
``report``), each printing ``[command]``-prefixed progress messages.
``clean``, ``cohort``, ``export`` and ``analyze`` are implemented; the other
steps are stubs that raise ``NotImplementedError``.
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
    MOTCO_ANALYSIS_DIR,
    MOTCO_INPUT_DIR,
    PLATFORMS,
    REPORTED_N_JOBS,
)
from .data import (
    run_analysis,
    run_axis_diagnostics,
    run_clean,
    run_cohort,
    run_export,
    run_report,
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

    p = sub.add_parser("axis-diagnostics", help="Correlations of the latent and block axes with predeclared variables -> results/motco_diagnostics/")
    p.add_argument("--input-dir", type=Path, default=None, help=f"Output directory of export (default: {MOTCO_INPUT_DIR})")
    p.add_argument("--analysis-dir", type=Path, default=None, help=f"Output directory of analyze (default: {MOTCO_ANALYSIS_DIR})")
    p.add_argument("--cohort-dir", type=Path, default=None, help=f"Output directory of cohort (default: {COHORT_DIR})")
    p.add_argument("--out-dir", type=Path, default=None, help=f"Diagnostics directory (default: {DIAGNOSTICS_DIR})")
    _add_force(p)

    p = sub.add_parser("report", help="Write the case-study report from the generated files, or check one against them")
    p.add_argument("--analysis-dir", type=Path, default=None, help=f"Output directory of analyze (default: {MOTCO_ANALYSIS_DIR})")
    p.add_argument("--cohort-dir", type=Path, default=None, help=f"Output directory of cohort (default: {COHORT_DIR})")
    p.add_argument("--diagnostics-dir", type=Path, default=None, help=f"Output directory of axis-diagnostics (default: {DIAGNOSTICS_DIR})")
    p.add_argument("--out", type=Path, default=None, help="Report path (default: reports/motco-adni-<date>.md)")
    p.add_argument("--check", action="store_true", help="Check the numbers of the report at --out against the generated files instead of writing it")

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
    elif args.command == "report":
        run_report(
            analysis_dir=args.analysis_dir,
            cohort_dir=args.cohort_dir,
            diagnostics_dir=args.diagnostics_dir,
            out=args.out,
            check=args.check,
        )
    else:  # pragma: no cover - argparse enforces the choices
        raise SystemExit(f"Unknown command {args.command!r}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
