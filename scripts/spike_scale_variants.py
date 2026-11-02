#!/usr/bin/env python
"""Spike: both blocks on the three scale variants (the raw scale, log2(x + 1), the generalized log), for the adni-scale-variants proposal.

Read-only and aggregate-only. Reads, in ``results/``, the cleaned p180 and
NMR tables (each checked against its ``clean_manifest.json``, whose hash must
equal the export manifest's record) and the primary export's ``p180.csv``,
``nmr.csv``, ``covariates.csv``, ``features_p180.csv`` and
``features_nmr.csv`` (checked against the export ``manifest.json``). It
rebuilds each block on the rule's scale (``log2(x + floor)``, the 5 % floor
over the exported participants) and checks it against the primary's CSV cell
for cell, then builds the three variant scales of the same cells: the raw
scale (the cleaned concentrations as metabo_adni leaves them), ``log2(x + 1)``
and the generalized log ``log2((x + sqrt(x² + λ²)) / 2)`` with λ per
metabolite its smallest positive value over the exported participants divided
by ``GLOG_LAMBDA_DIVISOR`` (10). It measures each block on each scale with the
export's own count functions (``_shape_counts``, ``_spectrum``,
``_phase_offset``), the offsets against the concentrations (the rule's floor,
1 and λ against the median; the features whose median lies below 1), each
variant scale's agreement with the rule's scale per feature (Pearson r; every
scale is monotone in x, so Spearman is 1), where the zero cells land, how far
the generalized log is from ``log2(x)`` on the positive cells, and the joint
matrix per scale. It reads no MOTCO output, no metadata and no sex or stage,
and computes no sex or stage contrast. No participant identifier or
participant value is printed or written.

Usage (inside the Nix shell):
  uv run python -I scripts/spike_scale_variants.py --cleaned-dir results/cleaned \
      --input-dir results/motco_input --out openspec/changes/<change>/spike.md
"""

from __future__ import annotations

import adni_sexdiff  # noqa: F401  (sets the pinned numeric environment before numpy loads)

import argparse
import datetime as dt
import json
import socket
from pathlib import Path

import numpy as np
import pandas as pd

from adni_sexdiff.constants import (
    ANALYSIS_COVARIATES,
    CLEAN_TABLES,
    EXPORT_BLOCKS,
    EXPORT_FEATURE_RULE,
    PARTICIPANT_ID_COLUMN,
    SAMPLE_COLUMN,
)
from adni_sexdiff.data import _feature_family, _phase_offset, _sha256_file, _shape_counts, _spectrum

GLOG_LAMBDA_DIVISOR = 10.0
VARIANTS = ("raw_scale", "log2_plus_one", "glog")
SCALES = ("rule", *VARIANTS)
LABELS = {
    "rule": "rule: log2(x + floor)",
    "raw_scale": "raw_scale: x",
    "log2_plus_one": "log2_plus_one: log2(x + 1)",
    "glog": "glog: log2((x + sqrt(x² + λ²)) / 2)",
}
MEDIAN_BINS = ((0.0, 0.1), (0.1, 1.0), (1.0, 10.0), (10.0, 100.0), (100.0, np.inf))
REPRODUCTION_TOLERANCE = 1e-12
SHAPE_COLS = ("abs_skew_gt_1", "skew_lt_minus_1", "median_abs_skew", "max_abs_z_gt_5", "max_abs_z_gt_8", "max_abs_z_gt_15")
SPECTRUM_COLS = ("pc1_share", "pc1_3_share", "pc1_10_share", "effective_rank", "numerical_rank")
OFFSET_COLS = ("median_abs_d", "max_abs_d", "abs_d_gt_0_5", "abs_d_gt_1", "abs_corr_pc1_phase", "abs_corr_pc2_phase")


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


def f3(x) -> str:
    return f"{x:.3f}" if isinstance(x, (float, np.floating)) else str(x)


def glog2(X: np.ndarray, lam: np.ndarray) -> np.ndarray:
    return np.log2((X + np.sqrt(X * X + lam * lam)) / 2.0)


def pearson_columns(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Pearson r between the j-th columns of ``A`` and ``B``, for every j."""
    Za = (A - A.mean(axis=0)) / A.std(axis=0)
    Zb = (B - B.mean(axis=0)) / B.std(axis=0)
    return (Za * Zb).mean(axis=0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cleaned-dir", type=Path, default=Path("results/cleaned"))
    ap.add_argument("--input-dir", type=Path, default=Path("results/motco_input"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    md: list[str] = []
    w = md.append

    # ---- inputs, chained --------------------------------------------------------
    manifest_path = args.input_dir / "manifest.json"
    export_manifest = json.loads(manifest_path.read_text())
    outputs = export_manifest["outputs"]
    hashes = [("motco_input/manifest.json", _sha256_file(manifest_path), "read")]
    cleaned: dict[str, pd.DataFrame] = {}
    for platform in EXPORT_BLOCKS:
        record = export_manifest["inputs"]["clean"][platform]
        cm_path = args.cleaned_dir / platform / "clean_manifest.json"
        hashes.append((f"cleaned/{platform}/clean_manifest.json",
                       check(cm_path, record["manifest"]["sha256"], f"{platform}/clean_manifest.json"), "export manifest"))
        cm = json.loads(cm_path.read_text())
        name = CLEAN_TABLES[platform]
        hashes.append((f"cleaned/{platform}/{name}",
                       check(args.cleaned_dir / platform / name, cm["outputs"][name]["sha256"], name), "clean manifest"))
        cleaned[platform] = pd.read_csv(args.cleaned_dir / platform / name, index_col=PARTICIPANT_ID_COLUMN)
    for name in ("p180.csv", "nmr.csv", "covariates.csv", "features_p180.csv", "features_nmr.csv"):
        hashes.append((f"motco_input/{name}", check(args.input_dir / name, outputs[name]["sha256"], name), "export manifest"))

    # round_trip: the export writes each float as its shortest repr, so the cells parse back exactly
    primary = {p: pd.read_csv(args.input_dir / f"{p}.csv", float_precision="round_trip") for p in EXPORT_BLOCKS}
    covariates = pd.read_csv(args.input_dir / "covariates.csv")
    features = {p: pd.read_csv(args.input_dir / f"features_{p}.csv", float_precision="round_trip").set_index("feature")
                for p in EXPORT_BLOCKS}
    rids = primary["p180"][SAMPLE_COLUMN].to_numpy()
    if not (np.array_equal(rids, primary["nmr"][SAMPLE_COLUMN].to_numpy())
            and np.array_equal(rids, covariates[SAMPLE_COLUMN].to_numpy())):
        raise SystemExit("the exported tables do not carry the same rid column in the same order")
    phase_levels = tuple(ANALYSIS_COVARIATES["phase"]["levels"])
    phase = covariates["phase"].to_numpy()
    scale = EXPORT_FEATURE_RULE["scale"]
    recorded = export_manifest["counts"]
    pinned_record = "numerics" in export_manifest

    # ---- the blocks on the four scales ---------------------------------------------
    B: dict[str, dict] = {}
    for platform in EXPORT_BLOCKS:
        table = cleaned[platform]
        n_absent = int((~pd.Index(rids).isin(table.index)).sum())
        if n_absent:
            raise SystemExit(f"{n_absent} exported participant(s) absent from {CLEAN_TABLES[platform]}")
        table = table.loc[rids]
        marks = EXPORT_FEATURE_RULE["membership"][platform]["derived"]
        columns = [str(c) for c in table.columns]
        kept = [c for c in columns if _feature_family(c, marks) is None]
        block_columns = export_manifest["settings"]["block_columns"][platform]
        X = table[kept].to_numpy(dtype=float)
        n_missing = int(np.isnan(X).sum())
        if n_missing:
            raise SystemExit(f"{platform}: {n_missing} missing cell(s) among the exported participants")
        floor = np.quantile(X, scale["floor_quantile"], axis=0, method=scale["floor_method"])
        T_rule = np.log2(X + floor)
        same_columns = kept == block_columns
        same_cells = bool(np.array_equal(T_rule, primary[platform][block_columns].to_numpy(dtype=float)))
        same_floors = bool(np.array_equal(floor, features[platform].loc[kept, "floor"].to_numpy(dtype=float)))
        positive_min = np.where(X > 0, X, np.inf).min(axis=0)
        n_no_positive = int((~np.isfinite(positive_min)).sum())
        if n_no_positive:
            raise SystemExit(f"{platform}: {n_no_positive} metabolite(s) with no positive cell; λ is undefined")
        lam = positive_min / GLOG_LAMBDA_DIVISOR
        mats = {
            "rule": T_rule,
            "raw_scale": X.copy(),
            "log2_plus_one": np.log2(X + 1.0),
            "glog": glog2(X, lam),
        }
        median = np.median(X, axis=0)
        zeros = X == 0
        measures = {}
        for s, M in mats.items():
            d, offset = _phase_offset(M, phase, phase_levels)
            measures[s] = {
                "non_finite": int((~np.isfinite(M)).sum()),
                "shape": _shape_counts(M),
                "spectrum": _spectrum(M),
                "offset": offset,
                "d": d,
                "pearson": None if s == "rule" else pearson_columns(M, T_rule),
            }
        # reproduction of the primary manifest's counts on the rule's scale
        reproduced = {}
        for key, got in (("shape", measures["rule"]["shape"]), ("spectrum", measures["rule"]["spectrum"]),
                         ("phase_offset", measures["rule"]["offset"])):
            want = recorded[key][platform]
            diffs = [abs(got[k] - want[k]) for k in got if isinstance(got[k], float)]
            exact = got == want
            same_ints = all(got[k] == want[k] for k in got if not isinstance(got[k], float))
            reproduced[key] = (exact, same_ints and max(diffs, default=0.0) <= REPRODUCTION_TOLERANCE, max(diffs, default=0.0))
        # the generalized log against log2(x) on the positive cells
        pos = X > 0
        glog_minus_log = np.abs(mats["glog"][pos] - np.log2(X[pos]))
        # where a zero cell lands on each scale, relative to the metabolite's smallest positive value (in bits)
        B[platform] = dict(
            columns=columns, kept=kept, X=X, floor=floor, lam=lam, median=median, zeros=zeros, mats=mats,
            measures=measures, same_columns=same_columns, same_cells=same_cells, same_floors=same_floors,
            reproduced=reproduced, positive_min=positive_min, glog_minus_log_max=float(glog_minus_log.max()),
            glog_minus_log_q99=float(np.quantile(glog_minus_log, 0.99)),
        )

    # ---- write ------------------------------------------------------------------------
    w(f"# Spike: both blocks on the three scale variants ({dt.date.today().isoformat()})\n")
    w(
        "Read-only and aggregate-only (`scripts/spike_scale_variants.py`). It reads the cleaned p180 and NMR tables "
        "and the primary export's `p180.csv`, `nmr.csv`, `covariates.csv`, `features_p180.csv` and "
        "`features_nmr.csv`, each checked against the manifest that records it. It rebuilds each block on the rule's "
        "scale (`log2(x + floor)`, the 5 % floor over the exported participants) and checks it against the primary's "
        "CSV cell for cell, then builds the three variant scales of the same cells: `raw_scale` (the cleaned "
        "concentrations as metabo_adni leaves them), `log2_plus_one` (`log2(x + 1)`) and `glog` "
        "(`log2((x + sqrt(x² + λ²)) / 2)`, λ per metabolite its smallest positive value over the exported "
        f"participants divided by {GLOG_LAMBDA_DIVISOR:g}). It measures each block on each scale with the export's own "
        "count functions (`_shape_counts`, `_spectrum`, `_phase_offset`). It reads no MOTCO output, no metadata and "
        "no sex or stage, and computes no sex or stage contrast. No participant identifier or value is written.\n"
    )
    w(f"Host: `{socket.gethostname()}`; run {dt.date.today().isoformat()}.\n")

    w("## Inputs\n")
    w(md_table([{"file": f"`{n}`", "sha256": f"`{s}`", "checked against": c} for n, s, c in hashes]))
    w(f"\nThe exported tables carry the same `{SAMPLE_COLUMN}` column in the same order ({len(rids)} participants).\n")

    w("## The rule's scale reproduced\n")
    rows = []
    for p in EXPORT_BLOCKS:
        b = B[p]
        rows.append({
            "block": p, "kept columns": len(b["kept"]),
            "columns equal `block_columns`": "yes" if b["same_columns"] else "no",
            "floors equal `features_*.csv`": "yes" if b["same_floors"] else "no",
            "cells equal the primary CSV (bitwise)": "yes" if b["same_cells"] else "no",
            "counts reproduced": "; ".join(
                f"`{k}` " + ("equal" if exact else f"{'within' if close else 'NOT within'} {REPRODUCTION_TOLERANCE:g} ({diff:.1e})")
                for k, (exact, close, diff) in b["reproduced"].items()),
        })
    w(md_table(rows))
    if not pinned_record:
        w(
            "\nThe primary export manifest has no `numerics` block (written on 2026-10-27, before "
            "`adni-portable-numerics`), so its SVD-based floats come from an unpinned run; a pinned recomputation "
            "differs from them at about 1e-15, as AGENTS.md records, while the exported files reproduce byte for byte.\n"
        )

    w("\n## The scales\n")
    w(
        "Every scale below is applied to the same cells: the primary's participants and the primary's membership "
        "(133 p180 metabolites, 165 NMR concentrations). Each is a monotone increasing function of the "
        "concentration, so per feature the ranks of the participants are the same on every scale (Spearman 1 with "
        "the rule's scale); what changes is the spacing: how far the low values are compressed and how far the high "
        "values spread.\n"
    )
    w(md_table([
        {"scale": "`rule`", "transform": "`log2(x + floor)`", "offset": "the metabolite's 5 % quantile", "where x = 0 lands": "`log2(floor)`"},
        {"scale": "`raw_scale`", "transform": "`x`", "offset": "none", "where x = 0 lands": "0"},
        {"scale": "`log2_plus_one`", "transform": "`log2(x + 1)`", "offset": "1, in the platform's unit", "where x = 0 lands": "0"},
        {"scale": "`glog`", "transform": "`log2((x + sqrt(x² + λ²)) / 2)`", "offset": f"λ = the metabolite's smallest positive value / {GLOG_LAMBDA_DIVISOR:g}",
         "where x = 0 lands": f"`log2(λ / 2)`, {np.log2(2 * GLOG_LAMBDA_DIVISOR):.2f} bits below `log2` of the smallest positive value"},
    ]))

    w("\n## The offsets against the concentrations\n")
    w("Quantiles over the kept metabolites of a block (native units: p180 µM, NMR mostly mmol/L):\n")
    rows = []
    for p in EXPORT_BLOCKS:
        b = B[p]
        for label, v in (("median concentration", b["median"]), ("rule floor", b["floor"]),
                         ("rule floor / median", b["floor"] / b["median"]), ("smallest positive value", b["positive_min"]),
                         ("λ / median", b["lam"] / b["median"]), ("1 / median", 1.0 / b["median"])):
            q = np.quantile(v, [0.05, 0.25, 0.5, 0.75, 0.95])
            rows.append({"block": p, "quantity": label, **{f"q{int(k*100):02d}": f"{x:.4g}" for k, x in zip((0.05, 0.25, 0.5, 0.75, 0.95), q)}})
    w(md_table(rows))
    w("\nKept metabolites by median concentration (native units), the regime of `log2(x + 1)`:\n")
    rows = []
    for p in EXPORT_BLOCKS:
        m = B[p]["median"]
        row = {"block": p, "kept": len(m)}
        for lo, hi in MEDIAN_BINS:
            key = f"[{lo:g}, {hi:g})" if np.isfinite(hi) else f"≥ {lo:g}"
            row[key] = int(((m >= lo) & (m < hi)).sum())
        row["median < 1 (near-linear under log2(x + 1))"] = int((m < 1).sum())
        row["median ≥ 100 (near log2(x))"] = int((m >= 100).sum())
        rows.append(row)
    w(md_table(rows))
    w(
        "\nUnder `log2(x + 1)` a metabolite whose values lie well below 1 is nearly linear (`log2(1 + x) ≈ x / ln 2`), "
        "and one whose values lie well above 1 is nearly `log2(x)`; the pseudo-count is the same number in each "
        "platform's unit, so the scale a metabolite gets depends on its abundance and its unit.\n"
    )

    w("\n## Zero cells\n")
    rows = []
    for p in EXPORT_BLOCKS:
        b = B[p]
        z = b["zeros"]
        cols_with = int((z.sum(axis=0) > 0).sum())
        rows.append({"block": p, "zero cells": int(z.sum()), "metabolites with zeros": cols_with,
                     "rule: `log2(floor)`": "per metabolite", "raw_scale": "0", "log2_plus_one": "0",
                     "glog": f"`log2(λ / 2)`, {np.log2(2 * GLOG_LAMBDA_DIVISOR):.2f} bits below the smallest positive value"})
    w(md_table(rows))
    w("\nThe generalized log against `log2(x)` on the positive cells (bits):\n")
    w(md_table([{"block": p, "largest |glog − log2(x)|": f"{B[p]['glog_minus_log_max']:.4f}",
                 "q99": f"{B[p]['glog_minus_log_q99']:.4f}",
                 "bound at x = smallest positive value": f"{np.log2((1 + np.sqrt(1 + 1 / GLOG_LAMBDA_DIVISOR**2)) / 2):.4f}"}
                for p in EXPORT_BLOCKS]))

    w("\n## Each block on each scale\n")
    for p in EXPORT_BLOCKS:
        b = B[p]
        w(f"\n### {p} ({len(b['kept'])} metabolites)\n")
        w("Shape (`_shape_counts`: pandas skew, largest |z| at the population sd) and non-finite cells:\n")
        w(md_table([{"scale": LABELS[s], **{k: f3(b["measures"][s]["shape"][k]) for k in SHAPE_COLS},
                     "non_finite": b["measures"][s]["non_finite"]} for s in SCALES]))
        w("\nSpectrum (`_spectrum`: the standardized block):\n")
        w(md_table([{"scale": LABELS[s], **{k: f3(b["measures"][s]["spectrum"][k]) for k in SPECTRUM_COLS}} for s in SCALES]))
        w("\nRun offset (`_phase_offset`: ADNI1 minus ADNI2GO, pooled within-phase sd; PC correlations with phase):\n")
        w(md_table([{"scale": LABELS[s], **{k: f3(b["measures"][s]["offset"][k]) for k in OFFSET_COLS}} for s in SCALES]))
        w("\nAgreement with the rule's scale per metabolite (Pearson r of the two scalings of the same column):\n")
        rows = []
        for s in VARIANTS:
            r = b["measures"][s]["pearson"]
            rows.append({"scale": LABELS[s], "median r": f3(float(np.median(r))), "q05": f3(float(np.quantile(r, 0.05))),
                         "min": f3(float(r.min())), "r < 0.9": int((r < 0.9).sum()), "r < 0.99": int((r < 0.99).sum())})
        w(md_table(rows))
        tdf = {s: pd.DataFrame(b["mats"][s], columns=b["kept"]) for s in SCALES}
        skew = {s: tdf[s].skew() for s in SCALES}
        maxz = {s: ((tdf[s] - tdf[s].mean()) / tdf[s].std(ddof=0)).abs().max() for s in SCALES}
        top = skew["raw_scale"].abs().sort_values(ascending=False).head(5)
        w("\nThe metabolites with the largest |skew| on the raw scale: "
          + ", ".join(f"`{c}` {skew['raw_scale'][c]:+.1f} (rule {skew['rule'][c]:+.2f})" for c in top.index) + ".\n")
        top = maxz["raw_scale"].sort_values(ascending=False).head(5)
        w("The metabolites with the largest |z| on the raw scale: "
          + ", ".join(f"`{c}` {maxz['raw_scale'][c]:.1f} (rule {maxz['rule'][c]:.1f})" for c in top.index) + ".\n")
        r = pd.Series(b["measures"]["log2_plus_one"]["pearson"], index=b["kept"])
        low = r.sort_values().head(5)
        w("The metabolites whose `log2(x + 1)` scaling agrees least with the rule's: "
          + ", ".join(f"`{c}` r {r[c]:.3f} (median {b['median'][b['kept'].index(c)]:.3g})" for c in low.index) + ".\n")
        r = pd.Series(b["measures"]["glog"]["pearson"], index=b["kept"])
        low = r.sort_values().head(5)
        w("The metabolites whose `glog` scaling agrees least with the rule's: "
          + ", ".join(f"`{c}` r {r[c]:.3f} (floor / median {b['floor'][b['kept'].index(c)] / b['median'][b['kept'].index(c)]:.2f})"
                      for c in low.index) + ".\n")

    w("\n## The joint matrix per scale (p180 then NMR, as MOTCO concatenates them)\n")
    rows = []
    for s in SCALES:
        J = np.hstack([B[p]["mats"][s] for p in EXPORT_BLOCKS])
        sp = _spectrum(J)
        _, off = _phase_offset(J, phase, phase_levels)
        sh = _shape_counts(J)
        rows.append({"scale": LABELS[s], "features": J.shape[1], "abs_skew_gt_1": sh["abs_skew_gt_1"],
                     "max_abs_z_gt_8": sh["max_abs_z_gt_8"], "pc1 share": f3(sp["pc1_share"]),
                     "pc1-10 share": f3(sp["pc1_10_share"]), "effective rank": f3(sp["effective_rank"]),
                     "numerical rank": sp["numerical_rank"], "pc1 corr phase": f3(off["abs_corr_pc1_phase"]),
                     "pc2 corr phase": f3(off["abs_corr_pc2_phase"])})
    w(md_table(rows))
    w(
        "\nThe spectrum and the phase correlations are of the standardized joint matrix (population sd), descriptive "
        "only: MOTCO's PLS-DA basis is supervised by stage and is not this PCA. MOTCO 0.10.0 z-scores every feature, "
        "so a scale changes the geometry through the spacing of each feature's values, not through its variance.\n"
    )

    w("\n## Counts for the proposal\n")
    rows = []
    for s in VARIANTS:
        for p in EXPORT_BLOCKS:
            m = B[p]["measures"][s]
            rows.append({
                "variant": f"`{s}`", "block": p,
                "abs_skew_gt_1": m["shape"]["abs_skew_gt_1"], "max_abs_z_gt_8": m["shape"]["max_abs_z_gt_8"],
                "phase abs_d_gt_0_5": m["offset"]["abs_d_gt_0_5"], "phase abs_d_gt_1": m["offset"]["abs_d_gt_1"],
                "non_finite": m["non_finite"],
                "median < 1": int((B[p]["median"] < 1).sum()) if s == "log2_plus_one" else "",
                "zero cells": int(B[p]["zeros"].sum()),
            })
    w(md_table(rows))
    w(md_table([{"quantity": "joint features; p180 / NMR share", "value": f"{sum(len(B[p]['kept']) for p in EXPORT_BLOCKS)}; "
                 + " / ".join(f3(len(B[p]['kept']) / sum(len(B[q]['kept']) for q in EXPORT_BLOCKS)) for p in EXPORT_BLOCKS)},
                {"quantity": "rule's cells equal to the primary's, both blocks", "value": "yes" if all(B[p]["same_cells"] and B[p]["same_columns"] for p in EXPORT_BLOCKS) else "no"},
                {"quantity": "metabolites with no positive cell (λ undefined)", "value": "0"}]))

    args.out.write_text("\n".join(md))
    print(f"[spike] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
