#!/usr/bin/env python
"""Spike: the CN / LMCI / AD arm's participants, covariates and run offset, for the adni-stage-sensitivity proposal.

Read-only and aggregate-only. Reads, in ``results/``, ``cohort.csv`` (checked
against ``cohort_manifest.json``, whose hash must equal the export manifest's
record), the four exported tables (checked against the export
``manifest.json``) and, for the floor comparison only, the cleaned p180 and
NMR tables (checked against their ``clean_manifest.json``). It keeps the
exported participants whose ``dx_bl`` is CN, LMCI or AD and counts them by
sex, stage, ``dx_bl``, phase and covariate level; it measures the run offset
of each block on the arm's rows of the primary export (the primary's floors)
with the export's own definition (``_phase_offset``); and it measures how far
each kept metabolite's floor would move if it were recomputed over the arm's
participants. It reads no MOTCO output and computes no sex or stage contrast
of a metabolite. No participant identifier or participant value is printed or
written.

Usage (inside the Nix shell):
  uv run python -I scripts/spike_stage_arm.py --cleaned-dir results/cleaned \
      --cohort-dir results/cohort --input-dir results/motco_input \
      --out openspec/changes/<change>/spike.md
"""

from __future__ import annotations

import adni_sexdiff  # noqa: F401  (sets the pinned numeric environment before numpy loads)

import argparse
import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd

from adni_sexdiff.constants import ANALYSIS_COVARIATES, EXPORT_BLOCKS, EXPORT_FEATURE_RULE, GROUP_VALUES, STAGE_LABELS
from adni_sexdiff.data import _phase_offset, _sha256_file

ARM_DX = ("CN", "LMCI", "AD")
DROPPED_DX = ("SMC", "EMCI")
PHASES = ("ADNI1", "ADNI2GO")
CLEAN = {"p180": ("p180", "P180.csv"), "nmr": ("nmr", "NMR.csv")}


def md_table(rows: list[dict], cols: list[str] | None = None) -> str:
    if not rows:
        return "(none)\n"
    cols = cols or list(rows[0])
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
    return "\n".join(out) + "\n"


def check(path: Path, recorded: str, label: str) -> str:
    sha = _sha256_file(path)
    if sha != recorded:
        raise SystemExit(f"{label}: sha256 {sha} differs from the recorded {recorded}; not a data machine")
    return sha


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cleaned-dir", type=Path, default=Path("results/cleaned"))
    ap.add_argument("--cohort-dir", type=Path, default=Path("results/cohort"))
    ap.add_argument("--input-dir", type=Path, default=Path("results/motco_input"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    md: list[str] = []
    w = md.append

    # ---- inputs, chained --------------------------------------------------------
    export_manifest = json.loads((args.input_dir / "manifest.json").read_text())
    cohort_manifest_path = args.cohort_dir / "cohort_manifest.json"
    cohort_manifest = json.loads(cohort_manifest_path.read_text())
    hashes = []
    hashes.append(("cohort_manifest.json", check(
        cohort_manifest_path, export_manifest["inputs"]["cohort"]["manifest"]["sha256"], "cohort_manifest.json")))
    hashes.append(("cohort.csv", check(
        args.cohort_dir / "cohort.csv", cohort_manifest["outputs"]["cohort.csv"]["sha256"], "cohort.csv")))
    for name in ("p180.csv", "nmr.csv", "metadata.csv", "covariates.csv", "features_p180.csv", "features_nmr.csv"):
        hashes.append((name, check(args.input_dir / name, export_manifest["outputs"][name]["sha256"], name)))
    for platform, (sub, name) in CLEAN.items():
        cm = json.loads((args.cleaned_dir / sub / "clean_manifest.json").read_text())
        hashes.append((f"{sub}/{name}", check(args.cleaned_dir / sub / name, cm["outputs"][name]["sha256"], name)))

    cohort = pd.read_csv(args.cohort_dir / "cohort.csv")
    both = cohort[cohort[list(EXPORT_BLOCKS)].astype(bool).all(axis=1)].reset_index(drop=True)
    meta = pd.read_csv(args.input_dir / "metadata.csv")
    cov = pd.read_csv(args.input_dir / "covariates.csv")
    if both["rid"].tolist() != meta["rid"].tolist() or cov["rid"].tolist() != meta["rid"].tolist():
        raise SystemExit("the both-flag rows of cohort.csv are not the exported participants in order")
    if not (both["sex"].tolist() == meta["sex"].tolist() and both["stage"].tolist() == meta["stage"].tolist()):
        raise SystemExit("cohort.csv and metadata.csv disagree on sex or stage")
    frame = both[["sex", "stage", "dx_bl"]].join(cov[list(ANALYSIS_COVARIATES)])
    keep = frame["dx_bl"].isin(ARM_DX).to_numpy()
    arm = frame[keep].reset_index(drop=True)

    w(f"# Spike: the CN / LMCI / AD arm ({dt.date.today().isoformat()})\n")
    w("Read-only and aggregate-only (`scripts/spike_stage_arm.py`). It reads `cohort.csv`, the primary export and, "
      "for the floor comparison only, the cleaned tables, each checked against the manifest that records it. It "
      "counts the arm's participants and covariate levels, measures the run offset of each block on the arm's rows "
      "of the primary export with the export's own definition, and measures how far the floors would move if "
      "recomputed over the arm. It reads no MOTCO output and computes no sex or stage contrast of a metabolite. "
      "No participant identifier or value is written.\n")
    w("## Inputs\n")
    w(md_table([{"file": f"`{n}`", "sha256": f"`{s}`", "equals its record": "yes"} for n, s in hashes]))
    w(f"The {len(both)} rows of `cohort.csv` with both platform flags are the exported participants in export "
      "order, and their sex and stage equal `metadata.csv`.\n")

    # ---- participants ---------------------------------------------------------------
    w("## Participants\n")
    w(f"Exported: {len(frame)}. Dropped by the arm (`dx_bl` SMC or EMCI): {int((~keep).sum())}. Kept: {len(arm)}.\n")
    rows = []
    for dx in ("CN", "SMC", "EMCI", "LMCI", "AD"):
        sub = frame[frame["dx_bl"] == dx]
        rows.append({"dx_bl": dx, "stage (STAGE_RULE)": sub["stage"].iloc[0] if len(sub) else "",
                     **{f"{s} {p}": int(((sub["sex"] == s) & (sub["phase"] == p)).sum()) for s in GROUP_VALUES for p in PHASES},
                     "total": len(sub), "in the arm": "yes" if dx in ARM_DX else "no"})
    w(md_table(rows))
    mismatch = int((arm["stage"] != arm["dx_bl"].map({"CN": "CN", "LMCI": "MCI", "AD": "AD"})).sum())
    w(f"Rows whose stage differs from the arm's map of `dx_bl` (CN → CN, LMCI → MCI, AD → AD): {mismatch}.\n")
    w("### Sex × stage cells\n")
    rows = []
    for s in GROUP_VALUES:
        rows.append({"sex": s, **{f"{st} primary": int(((frame["sex"] == s) & (frame["stage"] == st)).sum()) for st in STAGE_LABELS},
                     **{f"{st} arm": int(((arm["sex"] == s) & (arm["stage"] == st)).sum()) for st in STAGE_LABELS}})
    w(md_table(rows))
    w("### Phase within stage\n")
    w("Share of ADNI-1 participants per stage, and the `dx_bl` categories each run contributes to the stage.\n")
    rows = []
    for st in STAGE_LABELS:
        for label, f in (("primary", frame), ("arm", arm)):
            sub = f[f["stage"] == st]
            rows.append({"stage": st, "set": label, "n": len(sub),
                         "ADNI1": int((sub["phase"] == "ADNI1").sum()), "ADNI2GO": int((sub["phase"] == "ADNI2GO").sum()),
                         "ADNI1 share": f"{(sub['phase'] == 'ADNI1').mean():.3f}",
                         "dx_bl in ADNI1": ", ".join(sorted(sub.loc[sub["phase"] == "ADNI1", "dx_bl"].unique())),
                         "dx_bl in ADNI2GO": ", ".join(sorted(sub.loc[sub["phase"] == "ADNI2GO", "dx_bl"].unique()))})
    w(md_table(rows))

    # ---- covariates -----------------------------------------------------------------
    w("## Covariates\n")
    rows = []
    for name, spec in ANALYSIS_COVARIATES.items():
        if spec["coding"] != "categorical":
            for label, f in (("primary", frame), ("arm", arm)):
                rows.append({"covariate": name, "set": label, "levels": f"mean {f[name].mean():.3f}, sd {f[name].std():.3f}",
                             "missing": int(f[name].isna().sum())})
            continue
        for label, f in (("primary", frame), ("arm", arm)):
            counts = {str(level): int((f[name].astype(str) == str(level)).sum()) for level in spec["levels"]}
            rows.append({"covariate": name, "set": label, "levels": ", ".join(f"{k} {v}" for k, v in counts.items()),
                         "missing": int(f[name].isna().sum())})
    w(md_table(rows))
    # Full rank of the stage-means design: the six sex × stage cells and the six covariate design columns.
    cells = pd.get_dummies(arm["sex"] + ":" + arm["stage"]).astype(float).to_numpy()
    design = [arm["age"].to_numpy(float), arm["education"].to_numpy(float)]
    for name, spec in ANALYSIS_COVARIATES.items():
        if spec["coding"] == "categorical":
            design += [(arm[name].astype(str) == str(level)).to_numpy(float) for level in spec["levels"][1:]]
    X = np.column_stack([cells, *design])
    w(f"Stage-means design of the arm (6 cell indicators and the 6 covariate design columns): {X.shape[1]} columns, "
      f"rank {np.linalg.matrix_rank(X)}.\n")
    rows = []
    for s in GROUP_VALUES:
        for st in STAGE_LABELS:
            sub = arm[(arm["sex"] == s) & (arm["stage"] == st)]
            rows.append({"sex": s, "stage": st, "n": len(sub),
                         "apoe4 0 / 1 / 2": " / ".join(str(int((sub["apoe4"] == v).sum())) for v in (0, 1, 2)),
                         "phase ADNI1 / ADNI2GO": " / ".join(str(int((sub["phase"] == p).sum())) for p in PHASES),
                         "statin 0 / 1": " / ".join(str(int((sub["statin"] == v).sum())) for v in (0, 1))})
    w("Per arm cell:\n")
    w(md_table(rows))

    # ---- run offset ---------------------------------------------------------------
    w("## Run offset on the primary export\n")
    w("`_phase_offset` of `export` (ADNI1 minus ADNI2GO, pooled within-phase SD; PC correlations of the "
      "standardized block with phase) on the primary export's values: all 1501 rows (it must reproduce the export "
      "manifest's `counts.phase_offset`) and the arm's rows (the primary's floors).\n")
    rows = []
    phase_all = cov["phase"].to_numpy()
    for platform in EXPORT_BLOCKS:
        T = pd.read_csv(args.input_dir / f"{platform}.csv", index_col=0, float_precision="round_trip").to_numpy(float)
        recorded = export_manifest["counts"]["phase_offset"][platform]
        for label, rows_mask in (("primary (1501)", np.ones(len(T), bool)), ("arm", keep)):
            _, off = _phase_offset(T[rows_mask], phase_all[rows_mask], PHASES)
            rows.append({"block": platform, "rows": label, "median abs d": f"{off['median_abs_d']:.3f}",
                         "abs d > 0.5": off["abs_d_gt_0_5"], "abs d > 1": off["abs_d_gt_1"],
                         "max abs d": f"{off['max_abs_d']:.3f}", "PC1 corr": f"{off['abs_corr_pc1_phase']:.3f}",
                         "PC2 corr": f"{off['abs_corr_pc2_phase']:.3f}"})
        rows.append({"block": platform, "rows": "export manifest", "median abs d": f"{recorded['median_abs_d']:.3f}",
                     "abs d > 0.5": recorded["abs_d_gt_0_5"], "abs d > 1": recorded["abs_d_gt_1"],
                     "max abs d": f"{recorded['max_abs_d']:.3f}", "PC1 corr": f"{recorded['abs_corr_pc1_phase']:.3f}",
                     "PC2 corr": f"{recorded['abs_corr_pc2_phase']:.3f}"})
    w(md_table(rows))

    # ---- floors -------------------------------------------------------------------
    scale = EXPORT_FEATURE_RULE["scale"]
    w("## Floors recomputed over the arm (descriptive, for the floor decision)\n")
    w(f"Per kept metabolite, the floor of `EXPORT_FEATURE_RULE` ({scale['floor_quantile']:.0%} quantile, "
      f"{scale['floor_method']}) over the arm's participants against the primary's floor (`features_<platform>.csv`), "
      "and the largest change a recomputed floor would make to a transformed cell, `|log2(x + f_arm) − log2(x + f)|`, "
      "over the arm's cells. The arm does not use these floors.\n")
    rows = []
    for platform, (sub, name) in CLEAN.items():
        feats = pd.read_csv(args.input_dir / f"features_{platform}.csv")
        kept = feats[feats["status"] == "kept"]
        cleaned = pd.read_csv(args.cleaned_dir / sub / name, index_col=0)
        Xa = cleaned.loc[meta["rid"][keep].to_numpy(), kept["feature"].astype(str).tolist()].to_numpy(float)
        f_arm = np.quantile(Xa, scale["floor_quantile"], axis=0, method=scale["floor_method"])
        f_primary = kept["floor"].to_numpy(float)
        ratio = np.log2(f_arm / f_primary)
        shift = np.abs(np.log2(Xa + f_arm) - np.log2(Xa + f_primary)).max(axis=0)
        rows.append({"block": platform, "kept": len(kept),
                     "median abs log2(f_arm / f)": f"{np.median(np.abs(ratio)):.4f}",
                     "max abs log2(f_arm / f)": f"{np.abs(ratio).max():.4f}",
                     "floors moving > 10 %": int((np.abs(f_arm / f_primary - 1) > 0.10).sum()),
                     "median of the largest cell change": f"{np.median(shift):.4f}",
                     "largest cell change": f"{shift.max():.4f}"})
    w(md_table(rows))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(md))
    print(f"wrote {args.out} ({len(arm)} of {len(frame)} participants counted, no identifier written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
