#!/usr/bin/env python
"""Spike: the NMR block with all 245 cleaned columns on the rule's scale, for the adni-nmr-all-columns proposal.

Read-only and aggregate-only. Reads, in ``results/``, the cleaned NMR table
(checked against ``nmr/clean_manifest.json``, whose hash must equal the
export manifest's record) and the primary export's ``nmr.csv``, ``p180.csv``,
``covariates.csv`` and ``features_nmr.csv`` (checked against the export
``manifest.json``). It builds the NMR block of the variant ``nmr_all_columns``
(every cleaned column, in cleaned order, each on ``EXPORT_FEATURE_RULE``'s
scale with its own 5 % floor over the exported participants), checks that its
165 concentration columns equal the primary's cell for cell and that the
export's own count functions reproduce the primary manifest's NMR counts on
them, then measures the variant block with the same functions (shape,
spectrum, run offset), the 80 derived columns per family, how much of each
derived column the concentrations explain linearly on this scale, and the
joint matrix of the two blocks (block shares, spectrum, run offset). It reads
no MOTCO output, no metadata and no sex or stage, and computes no sex or
stage contrast. No participant identifier or participant value is printed or
written.

Usage (inside the Nix shell):
  uv run python -I scripts/spike_nmr_all_columns.py --cleaned-dir results/cleaned \
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

from adni_sexdiff.constants import ANALYSIS_COVARIATES, EXPORT_FEATURE_RULE, PARTICIPANT_ID_COLUMN, SAMPLE_COLUMN
from adni_sexdiff.data import _feature_family, _phase_offset, _sha256_file, _shape_counts, _spectrum, _standardize

FAMILIES = ("percentage", "ratio", "degree", "size")
REPRODUCTION_TOLERANCE = 1e-12


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


def f3(x: float) -> str:
    return f"{x:.3f}"


def r_squared(Y: np.ndarray, X: np.ndarray) -> np.ndarray:
    """R² of the least-squares fit of each column of ``Y`` on ``X`` with an intercept."""
    A = np.column_stack([np.ones(X.shape[0]), _standardize(X)])
    coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
    res = Y - A @ coef
    return 1 - (res**2).sum(axis=0) / ((Y - Y.mean(axis=0)) ** 2).sum(axis=0)


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
    clean_record = export_manifest["inputs"]["clean"]["nmr"]
    clean_manifest_path = args.cleaned_dir / "nmr" / "clean_manifest.json"
    hashes = [
        ("motco_input/manifest.json", _sha256_file(manifest_path), "read"),
        ("cleaned/nmr/clean_manifest.json", check(
            clean_manifest_path, clean_record["manifest"]["sha256"], "nmr/clean_manifest.json"), "export manifest"),
    ]
    clean_manifest = json.loads(clean_manifest_path.read_text())
    hashes.append(("cleaned/nmr/NMR.csv", check(
        args.cleaned_dir / "nmr" / "NMR.csv", clean_manifest["outputs"]["NMR.csv"]["sha256"], "NMR.csv"),
        "clean manifest"))
    for name in ("nmr.csv", "p180.csv", "covariates.csv", "features_nmr.csv"):
        hashes.append((f"motco_input/{name}", check(args.input_dir / name, outputs[name]["sha256"], name), "export manifest"))

    # round_trip: the export writes each float as its shortest repr, so the cells parse back exactly
    nmr_primary = pd.read_csv(args.input_dir / "nmr.csv", float_precision="round_trip")
    p180_primary = pd.read_csv(args.input_dir / "p180.csv", float_precision="round_trip")
    covariates = pd.read_csv(args.input_dir / "covariates.csv")
    features = pd.read_csv(args.input_dir / "features_nmr.csv", float_precision="round_trip")
    rids = nmr_primary[SAMPLE_COLUMN].to_numpy()
    if not (np.array_equal(rids, p180_primary[SAMPLE_COLUMN].to_numpy())
            and np.array_equal(rids, covariates[SAMPLE_COLUMN].to_numpy())):
        raise SystemExit("the exported tables do not carry the same rid column in the same order")
    cleaned = pd.read_csv(args.cleaned_dir / "nmr" / "NMR.csv", index_col=PARTICIPANT_ID_COLUMN)
    n_absent = int((~pd.Index(rids).isin(cleaned.index)).sum())
    if n_absent:
        raise SystemExit(f"{n_absent} exported participant(s) absent from NMR.csv")
    table = cleaned.loc[rids]
    phase_levels = tuple(ANALYSIS_COVARIATES["phase"]["levels"])
    phase = covariates["phase"].to_numpy()

    # ---- the variant block ----------------------------------------------------------
    marks = EXPORT_FEATURE_RULE["membership"]["nmr"]["derived"]
    scale = EXPORT_FEATURE_RULE["scale"]
    columns = [str(c) for c in table.columns]
    families = {c: _feature_family(c, marks) for c in columns}
    kept = [c for c in columns if families[c] is None]
    derived = [c for c in columns if families[c] is not None]
    X = table.to_numpy(dtype=float)
    n_missing = int(np.isnan(X).sum())
    floor = np.quantile(X, scale["floor_quantile"], axis=0, method=scale["floor_method"])
    T = np.log2(X + floor)
    pos = {c: j for j, c in enumerate(columns)}
    ki = [pos[c] for c in kept]
    di = [pos[c] for c in derived]
    Tk, Td = T[:, ki], T[:, di]

    block_columns = export_manifest["settings"]["block_columns"]["nmr"]
    same_columns = kept == block_columns
    same_cells = bool(np.array_equal(Tk, nmr_primary[block_columns].to_numpy(dtype=float)))
    feat = features.set_index("feature")
    same_floors = bool(np.array_equal(floor[ki], feat.loc[kept, "floor"].to_numpy(dtype=float)))

    recorded = export_manifest["counts"]
    primary_shape, primary_spectrum = _shape_counts(Tk), _spectrum(Tk)
    _, primary_offset = _phase_offset(Tk, phase, phase_levels)
    # The primary export manifest predates the pinned numerics (no `numerics` block): its SVD-based floats
    # differ from a pinned recomputation at about 1e-15 (AGENTS.md), so they are compared within a tolerance.
    reproduced = {}
    for key, got in (("shape", primary_shape), ("spectrum", primary_spectrum), ("phase_offset", primary_offset)):
        want = recorded[key]["nmr"]
        diffs = [abs(got[k] - want[k]) for k in got if isinstance(got[k], float)]
        exact = got == want
        same_ints = all(got[k] == want[k] for k in got if not isinstance(got[k], float))
        reproduced[key] = (exact, same_ints and max(diffs, default=0.0) <= REPRODUCTION_TOLERANCE, max(diffs, default=0.0))
    pinned_record = "numerics" in export_manifest
    var_shape, var_spectrum = _shape_counts(T), _spectrum(T)
    d_all, var_offset = _phase_offset(T, phase, phase_levels)

    # ---- write ------------------------------------------------------------------------
    w("# Spike: the NMR block with all 245 cleaned columns (2026-10-30)\n")
    w(
        "Read-only and aggregate-only (`scripts/spike_nmr_all_columns.py`). It reads the cleaned NMR table and the "
        "primary export's `nmr.csv`, `p180.csv`, `covariates.csv` and `features_nmr.csv`, each checked against the "
        "manifest that records it. It builds the NMR block of `nmr_all_columns`: every cleaned column in cleaned "
        "order, each on `EXPORT_FEATURE_RULE`'s scale (`log2(x + floor)`, its own 5 % floor, linear, over the "
        "exported participants). It measures that block with the export's own count functions (`_shape_counts`, "
        "`_spectrum`, `_phase_offset`). It reads no MOTCO output, no metadata and no sex or stage, and computes no "
        "sex or stage contrast. No participant identifier or value is written.\n"
    )
    w(f"Host: `{socket.gethostname()}`; run {dt.date.today().isoformat()}.\n")
    w("## Inputs\n")
    w(md_table([{"file": f"`{n}`", "sha256": f"`{s}`", "checked against": c} for n, s, c in hashes]))
    w(
        f"\nThe exported tables carry the same `{SAMPLE_COLUMN}` column in the same order ({len(rids)} participants), "
        f"every one in `NMR.csv`; missing cells among them: {n_missing}.\n"
    )

    w("## Membership\n")
    fam_rows = [{"family": "concentration (kept by the rule)", "columns": len(kept)}]
    fam_rows += [{"family": f, "columns": sum(1 for c in derived if families[c] == f)} for f in FAMILIES]
    fam_rows.append({"family": "all (the variant)", "columns": len(columns)})
    w(md_table(fam_rows))
    w(
        f"\nThe 165 concentration columns in cleaned order equal the primary manifest's `block_columns.nmr`: "
        f"{'yes' if same_columns else 'no'}. Their floors equal `features_nmr.csv`'s: {'yes' if same_floors else 'no'}. "
        f"Their cells equal the primary `nmr.csv`'s, every one bitwise (parsed `round_trip`): "
        f"{'yes' if same_cells else 'no'}.\n"
    )
    w(
        "The export's count functions on the 165 columns against the primary manifest's `counts.*.nmr`: "
        + "; ".join(
            f"`{k}` "
            + ("equal" if exact else
               f"{'within' if close else 'NOT within'} {REPRODUCTION_TOLERANCE:g} (largest difference {diff:.1e})")
            for k, (exact, close, diff) in reproduced.items()
        )
        + ". "
        + ("" if pinned_record else
           "The primary export manifest has no `numerics` block (it was written on 2026-10-27, before "
           "`adni-portable-numerics`), so its SVD-based floats come from an unpinned run; a pinned recomputation "
           "differs from them at about 1e-15, as AGENTS.md records, while the exported files reproduce byte for byte.")
        + "\n"
    )

    w("## Floors, zeros and finiteness (245 columns)\n")
    zeros = (X == 0).sum(axis=0)
    w(md_table([
        {"columns": "concentration (165)", "zero cells": int(zeros[ki].sum()), "columns with zeros": int((zeros[ki] > 0).sum()),
         "floors not positive": int((floor[ki] <= 0).sum()), "non-finite cells": int((~np.isfinite(Tk)).sum())},
        {"columns": "derived (80)", "zero cells": int(zeros[di].sum()), "columns with zeros": int((zeros[di] > 0).sum()),
         "floors not positive": int((floor[di] <= 0).sum()), "non-finite cells": int((~np.isfinite(Td)).sum())},
        {"columns": "all (245)", "zero cells": int(zeros.sum()), "columns with zeros": int((zeros > 0).sum()),
         "floors not positive": int((floor <= 0).sum()), "non-finite cells": int((~np.isfinite(T)).sum())},
    ]))

    w("\n## The NMR block: primary (165) and variant (245)\n")
    w("Shape (`_shape_counts`: pandas skew, largest |z| at the population sd):\n")
    w(md_table([
        {"block": "primary (165)", **{k: (f3(v) if isinstance(v, float) else v) for k, v in primary_shape.items()}},
        {"block": "primary manifest", **{k: (f3(v) if isinstance(v, float) else v) for k, v in recorded["shape"]["nmr"].items()}},
        {"block": "variant (245)", **{k: (f3(v) if isinstance(v, float) else v) for k, v in var_shape.items()}},
    ]))
    w("\nSpectrum (`_spectrum`: the standardized block):\n")
    w(md_table([
        {"block": "primary (165)", **{k: (f3(v) if isinstance(v, float) and k != "numerical_rank_tolerance" else v) for k, v in primary_spectrum.items()}},
        {"block": "variant (245)", **{k: (f3(v) if isinstance(v, float) and k != "numerical_rank_tolerance" else v) for k, v in var_spectrum.items()}},
    ]))
    w("\nRun offset (`_phase_offset`: ADNI1 minus ADNI2GO, pooled within-phase sd; PC correlations with phase):\n")
    off_cols = ["median_abs_d", "max_abs_d", "abs_d_gt_0_5", "abs_d_gt_1", "abs_corr_pc1_phase", "abs_corr_pc2_phase"]
    w(md_table([
        {"block": "primary (165)", **{k: (f3(primary_offset[k]) if isinstance(primary_offset[k], float) else primary_offset[k]) for k in off_cols}},
        {"block": "variant (245)", **{k: (f3(var_offset[k]) if isinstance(var_offset[k], float) else var_offset[k]) for k in off_cols}},
    ], ["block", *off_cols]))

    w("\n## The 80 derived columns per family, on the rule's scale\n")
    Tdf = pd.DataFrame(T, columns=columns)
    skew_raw = pd.DataFrame(X, columns=columns).skew()
    skew_t = Tdf.skew()
    max_z = ((Tdf - Tdf.mean()) / Tdf.std(ddof=0)).abs().max()
    d = pd.Series(d_all, index=columns)
    r2 = pd.Series(r_squared(Td, Tk), index=derived)
    median = pd.Series(np.median(X, axis=0), index=columns)
    fl = pd.Series(floor, index=columns)
    rows = []
    for f in (*FAMILIES, None):
        cs = [c for c in derived if f is None or families[c] == f]
        rows.append({
            "family": f or "all derived",
            "n": len(cs),
            "median floor / median": f3(float((fl[cs] / median[cs]).median())),
            "abs skew raw > 1": int((skew_raw[cs].abs() > 1).sum()),
            "abs skew > 1": int((skew_t[cs].abs() > 1).sum()),
            "max abs z > 8": int((max_z[cs] > 8).sum()),
            "median abs d": f3(float(d[cs].abs().median())),
            "abs d > 0.5": int((d[cs].abs() > 0.5).sum()),
            "max abs d": f3(float(d[cs].abs().max())),
            "R² on the 165, median": f3(float(r2[cs].median())),
            "R² on the 165, min": f3(float(r2[cs].min())),
        })
    w(md_table(rows))
    w(
        "\nR² is the share of a derived column's variance (on the rule's scale) that a least-squares fit on the 165 "
        "concentration columns (on the same scale, with an intercept) explains: how far the column is a linear "
        "function of the concentrations as the analysis sees them.\n"
    )
    top_skew = skew_t[derived].abs().sort_values(ascending=False).head(5)
    top_d = d[derived].abs().sort_values(ascending=False).head(5)
    low_r2 = r2.sort_values().head(5)
    w("\nThe derived columns with the largest |skew| on the rule's scale: "
      + ", ".join(f"`{c}` {skew_t[c]:+.2f}" for c in top_skew.index) + ".\n")
    w("The derived columns with the largest phase |d|: " + ", ".join(f"`{c}` {d[c]:+.3f}" for c in top_d.index) + ".\n")
    w("The derived columns with the lowest R² on the concentrations: " + ", ".join(f"`{c}` {r2[c]:.3f}" for c in low_r2.index) + ".\n")

    w("\n## The joint matrix (p180 then NMR, as MOTCO concatenates them)\n")
    P = p180_primary.drop(columns=[SAMPLE_COLUMN]).to_numpy(dtype=float)
    joint_rows = []
    for label, N in (("primary (133 + 165)", Tk), ("variant (133 + 245)", T)):
        J = np.hstack([P, N])
        sp = _spectrum(J)
        _, off = _phase_offset(J, phase, phase_levels)
        joint_rows.append({
            "matrix": label,
            "features": J.shape[1],
            "p180 share": f3(P.shape[1] / J.shape[1]),
            "nmr share": f3(N.shape[1] / J.shape[1]),
            "pc1 share": f3(sp["pc1_share"]),
            "pc1-10 share": f3(sp["pc1_10_share"]),
            "effective rank": f3(sp["effective_rank"]),
            "numerical rank": sp["numerical_rank"],
            "pc1 corr phase": f3(off["abs_corr_pc1_phase"]),
            "pc2 corr phase": f3(off["abs_corr_pc2_phase"]),
        })
    w(md_table(joint_rows))
    w(
        "\nThe shares are of the features; MOTCO 0.10.0 z-scores every feature and weights features, not blocks. The "
        "spectrum and the phase correlations are of the standardized joint matrix (population sd), descriptive only: "
        "MOTCO's PLS-DA basis is supervised by stage and is not this PCA.\n"
    )

    w("\n## Counts for the proposal\n")
    w(md_table([
        {"quantity": "NMR columns cleaned / kept / derived kept", "value": f"{len(columns)} / {len(columns)} / {len(derived)}"},
        {"quantity": "joint features; p180 / NMR share", "value": f"{P.shape[1] + T.shape[1]}; {f3(P.shape[1] / (P.shape[1] + T.shape[1]))} / {f3(T.shape[1] / (P.shape[1] + T.shape[1]))}"},
        {"quantity": "NMR zero cells / columns with zeros", "value": f"{int(zeros.sum())} / {int((zeros > 0).sum())}"},
        {"quantity": "NMR floors not positive / non-finite cells", "value": f"{int((floor <= 0).sum())} / {int((~np.isfinite(T)).sum())}"},
        {"quantity": "NMR phase abs d > 0.5 / > 1", "value": f"{var_offset['abs_d_gt_0_5']} / {var_offset['abs_d_gt_1']}"},
        {"quantity": "165 concentration columns equal to the primary's", "value": "yes" if (same_columns and same_cells) else "no"},
    ]))

    args.out.write_text("\n".join(md))
    print(f"[spike] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
