#!/usr/bin/env python
"""Spike: the NIST SRM 1950 bridge of the two p180 runs, for the adni-nist-bridge proposal.

Read-only and aggregate-only. Reads, in the data root, the NIST SRM 1950 sheets
of the four p180 QC workbooks (inside the two supplement archives, nothing
extracted) and the study-pool rows (``RID`` 999999) of the four raw p180 files;
in ``results/``, the cleaned p180 table and its run labels (checked against
``clean_manifest.json``) and the exported block (checked against the export
``manifest.json``, for the exported participants and to reproduce the rule).
It reads no sex, stage, diagnosis or covariate: the bridge is estimated from
reference material only, and its effect is described against the assay run
only. It writes one Markdown report of counts, per-metabolite summaries of
reference material and per-metabolite summaries over participants. No
participant identifier or participant value is printed or written.

Usage (inside the Nix shell):
  uv run python -I scripts/spike_nist_bridge.py --data-root data \
      --cleaned-dir results/cleaned --input-dir results/motco_input \
      --out openspec/changes/<change>/spike.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import re
import zipfile
from importlib.metadata import version as pkg_version
from pathlib import Path

import numpy as np
import pandas as pd

RUNS = ["ADNI1", "ADNI2GO"]
KITS = ["FIA", "UPLC"]
FLOOR_QUANTILE = 0.05
POOL_RID = 999999
NIST_SHEET = "NIST SRM 1950 Data"
NIST_LABEL = "NIST SRM 1950"
# The QC workbooks, inside the supplement archives of the data root.
ARCHIVES = {
    "ADNI1": ("Metabolomics/p180/ADMC_supplement.zip", {
        "FIA": "admc_supplement/duke_raw_data/4097_FIA_NIST_and_QC_Data.xlsx",
        "UPLC": "admc_supplement/duke_raw_data/4097_UPLC_NIST_and_QC_Data.xlsx"}),
    "ADNI2GO": ("Metabolomics/p180/ADMCDUKEP180SUPP_20170410.zip", {
        "FIA": "4610 FIA p180 QC and NIST Data.xlsx",
        "UPLC": "4610 UPLC p180 QC and NIST Data.xlsx"}),
}
# The raw p180 files metabo_adni reads (flat names in the data root), for the pool rows.
RAW_FILES = {
    ("ADNI1", "FIA"): "ADMCDUKEP180FIA_01_15_16.csv", ("ADNI1", "UPLC"): "ADMCDUKEP180UPLC_01_15_16.csv",
    ("ADNI2GO", "FIA"): "ADMCDUKEP180FIAADNI2GO.csv", ("ADNI2GO", "UPLC"): "ADMCDUKEP180UPLCADNI2GO.csv",
}
# The ADNI-GO/2 workbooks carry a status per cell; the methods summary says data
# flagged for an internal standard out of range "should not be used".
ISTD_STATUS = "ISTD Out of Range"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def key(name: str) -> str:
    """Metabolite name with case and punctuation dropped (``C3-DC (C4-OH)`` = ``C3.DC..C4.OH.``)."""
    return re.sub(r"[^0-9a-z]", "", str(name).lower())


def md_table(rows: list[dict], cols: list[str] | None = None) -> str:
    if not rows:
        return "(none)\n"
    cols = cols or list(rows[0])
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
    return "\n".join(out) + "\n"


def read_nist(member: bytes) -> dict:
    """NIST SRM 1950 rows of one QC workbook: values, ISTD flags and plates, columns keyed by ``key``."""
    df = pd.read_excel(io.BytesIO(member), sheet_name=NIST_SHEET, header=1)
    df = df[df["Customer Sample Identification"].astype(str).str.strip() == NIST_LABEL].reset_index(drop=True)
    start = list(df.columns).index("Injection Number") + 1
    mets = [c for c in df.columns[start:] if not str(c).endswith("Status")]
    vals = df[mets].apply(pd.to_numeric, errors="coerce")
    vals = vals.where(vals > 0)
    text = int(df[mets].map(lambda v: isinstance(v, str)).to_numpy().sum())
    istd = pd.DataFrame(False, index=df.index, columns=mets)
    statuses: dict[str, int] = {}
    for m in mets:
        s = f"{m} Status"
        if s in df.columns:
            istd[m] = df[s].astype(str).str.strip() == ISTD_STATUS
            for v, n in df[s].astype(str).str.strip().value_counts().items():
                statuses[v] = statuses.get(v, 0) + int(n)
    keys = [key(m) for m in mets]
    if len(set(keys)) != len(keys):
        raise SystemExit("duplicate metabolite keys in a NIST sheet")
    vals.columns = istd.columns = keys
    return {"values": vals, "istd": istd, "plates": df["Plate Bar Code"].astype(str).to_numpy(),
            "names": dict(zip(keys, mets)), "text_cells": text, "statuses": statuses}


def run_level(L: pd.Series, plates: np.ndarray) -> tuple[float, float, int, int]:
    """Mean of log2 over valid replicates, its plate-clustered SE, valid replicates, plates with one."""
    ok = L.notna().to_numpy()
    if ok.sum() == 0:
        return np.nan, np.nan, 0, 0
    pm = pd.Series(L.to_numpy()[ok]).groupby(plates[ok]).mean()
    se = pm.std(ddof=1) / np.sqrt(len(pm)) if len(pm) > 1 else np.nan
    return float(L.to_numpy()[ok].mean()), float(se), int(ok.sum()), int(len(pm))


def pool_factors(raw: Path, keys: list[str]) -> pd.DataFrame:
    """metabo_adni's per-plate correction factor q_plate / q_global from the pool rows, per metabolite key."""
    df = pd.read_csv(raw, low_memory=False)
    pool = df[df["RID"] == POOL_RID]
    cols = {key(c): c for c in df.columns}
    out = {}
    for k in keys:
        if k not in cols:
            continue
        v = pd.to_numeric(pool[cols[k]], errors="coerce")
        q = v.groupby(pool["Plate.Bar.Code"].astype(str)).mean()
        out[k] = q / v.mean()
    return pd.DataFrame(out)


def offset_summary(M: np.ndarray, run: np.ndarray) -> dict:
    """The export's phase offset summary, against the assay run (equal to phase for every participant)."""
    a, b = M[run == RUNS[0]], M[run == RUNS[1]]
    d = (a.mean(0) - b.mean(0)) / np.sqrt((a.var(0) + b.var(0)) / 2)
    Z = (M - M.mean(0)) / M.std(0)
    u, s, _ = np.linalg.svd(Z, full_matrices=False)
    g = (run == RUNS[0]).astype(float)
    return {"median abs d": f"{np.median(np.abs(d)):.2f}", "max abs d": f"{np.abs(d).max():.2f}",
            "abs d > 0.5": int((np.abs(d) > 0.5).sum()), "abs d > 1": int((np.abs(d) > 1).sum()),
            "abs corr(PC1, run)": f"{abs(np.corrcoef(u[:, 0], g)[0, 1]):.2f}",
            "abs corr(PC2, run)": f"{abs(np.corrcoef(u[:, 1], g)[0, 1]):.2f}",
            "PC1 share": f"{s[0] ** 2 / (s ** 2).sum():.3f}"}


def export_scale(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    floor = np.quantile(X, FLOOR_QUANTILE, axis=0, method="linear")
    return np.log2(X + floor), floor


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-root", type=Path, default=Path("data"))
    ap.add_argument("--cleaned-dir", type=Path, default=Path("results/cleaned"))
    ap.add_argument("--input-dir", type=Path, default=Path("results/motco_input"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    root = args.data_root
    md: list[str] = []
    w = md.append

    # ---- files read ------------------------------------------------------
    files = []
    members: dict[tuple[str, str], bytes] = {}
    for run, (zpath, mem) in ARCHIVES.items():
        files.append({"file": f"`{zpath}`", "sha256": sha256(root / zpath)[:16] + "…", "note": "archive"})
        with zipfile.ZipFile(root / zpath) as zf:
            for kit, name in mem.items():
                members[(run, kit)] = zf.read(name)
                files.append({"file": f"`{Path(name).name}` (in the archive)",
                              "sha256": sha256_bytes(members[(run, kit)])[:16] + "…", "note": f"{run} {kit} QC workbook"})
    for (run, kit), name in RAW_FILES.items():
        files.append({"file": f"`{name}`", "sha256": sha256(root / name)[:16] + "…", "note": f"{run} {kit} raw, pool rows only"})
    clean_man = json.loads((args.cleaned_dir / "p180" / "clean_manifest.json").read_text())
    for name in ("P180.csv", "p180_runs.csv"):
        h = sha256(args.cleaned_dir / "p180" / name)
        files.append({"file": f"`cleaned/p180/{name}`", "sha256": h[:16] + "…",
                      "note": f"equals clean_manifest.json: {h == clean_man['outputs'][name]['sha256']}"})
    exp_man = json.loads((args.input_dir / "manifest.json").read_text())
    h = sha256(args.input_dir / "p180.csv")
    files.append({"file": "`motco_input/p180.csv`", "sha256": h[:16] + "…",
                  "note": f"equals manifest.json: {h == exp_man['outputs']['p180.csv']['sha256']}"})

    w(f"# Spike: the NIST SRM 1950 bridge of the p180 runs ({dt.date.today().isoformat()})\n")
    w(f"Read-only, aggregate only. Generated by `scripts/spike_nist_bridge.py` (pandas {pkg_version('pandas')}, "
      f"numpy {pkg_version('numpy')}, openpyxl {pkg_version('openpyxl')}). Every number below is a count, a summary "
      "of reference-material replicates, a summary over participants of one metabolite, a summary over metabolites, "
      "or a hash. No sex, stage, diagnosis or covariate is read: the bridge comes from NIST SRM 1950 alone, and its "
      "effect is described against the assay run alone. No participant identifier or participant value appears "
      "in this file.\n")
    w("## Files read\n")
    w(md_table(files))

    # ---- NIST design ---------------------------------------------------
    nist = {(r, k): read_nist(members[(r, k)]) for r in RUNS for k in KITS}
    exported = pd.read_csv(args.input_dir / "p180.csv")
    feat_names = [c for c in exported.columns if c != "rid"]
    feat_keys = [key(c) for c in feat_names]
    kit_of = {}
    for k in KITS:
        for fk in feat_keys:
            if fk in nist[("ADNI1", k)]["values"].columns and fk in nist[("ADNI2GO", k)]["values"].columns:
                kit_of.setdefault(fk, k)
    rows = []
    for (r, k), nd in nist.items():
        reps = pd.Series(nd["plates"]).value_counts()
        rows.append({"run": r, "kit": k, "plates": len(reps), "replicates": len(nd["plates"]),
                     "replicates per plate": "/".join(map(str, sorted(set(reps)))),
                     "metabolite columns": nd["values"].shape[1],
                     "exported metabolites present": sum(fk in nd["values"].columns for fk in feat_keys),
                     "text cells (< LOD, No Interception)": nd["text_cells"],
                     "status column values": ", ".join(f"{v} {n}" for v, n in sorted(nd["statuses"].items())) or "no status columns"})
    w("## NIST SRM 1950 in the two runs\n")
    w("NIST SRM 1950 (\"Metabolites in Frozen Human Plasma\") is the one material measured in both runs. "
      "The study pools are run-specific (`4610 study pool` in the ADNI-GO/2 files; the ADNI-1 pool was made from "
      "ADNI-1 samples), and the Biocrates QC levels carry different identifiers in the two runs.\n")
    w(md_table(rows))
    w(f"Exported p180 metabolites matched to a NIST column of one kit in both runs: {len(kit_of)} of {len(feat_keys)} "
      f"(FIA {sum(v == 'FIA' for v in kit_of.values())}, UPLC {sum(v == 'UPLC' for v in kit_of.values())}). "
      "Names are matched with case and punctuation dropped.\n")
    for r in RUNS:
        for k in KITS:
            p = set(nist[(r, k)]["plates"])
            pool_plates = set(pd.read_csv(root / RAW_FILES[(r, k)], usecols=["RID", "Plate.Bar.Code"], low_memory=False)
                              .query("RID == @POOL_RID")["Plate.Bar.Code"].astype(str))
            w(f"- {r} {k}: NIST plates that carry study-pool rows: {len(p & pool_plates)} of {len(p)}.")
    w("")

    # ---- the bridge per metabolite ----------------------------------------
    per = []
    for fk, name in zip(feat_keys, feat_names):
        k = kit_of.get(fk)
        rec = {"metabolite": name, "kit": k}
        if k is None:
            per.append(rec)
            continue
        for r in RUNS:
            nd = nist[(r, k)]
            L = np.log2(nd["values"][fk])
            m, se, n, npl = run_level(L, nd["plates"])
            Lx = L.where(~nd["istd"][fk])
            mx, sex, nx, _ = run_level(Lx, nd["plates"])
            rec.update({f"mean {r}": m, f"se {r}": se, f"valid {r}": n, f"plates {r}": npl,
                        f"replicates {r}": len(L), f"mean {r} no ISTD": mx, f"se {r} no ISTD": sex,
                        f"valid {r} no ISTD": nx, f"istd {r}": int(nd["istd"][fk].sum())})
        rec["b"] = rec["mean ADNI1"] - rec["mean ADNI2GO"]
        rec["se b"] = float(np.hypot(rec["se ADNI1"], rec["se ADNI2GO"]))
        rec["b no ISTD"] = rec["mean ADNI1 no ISTD"] - rec["mean ADNI2GO no ISTD"]
        rec["se b no ISTD"] = float(np.hypot(rec["se ADNI1 no ISTD"], rec["se ADNI2GO no ISTD"]))
        per.append(rec)
    P = pd.DataFrame(per).set_index("metabolite")
    for r in RUNS:
        P[f"valid share {r}"] = P[f"valid {r}"] / P[f"replicates {r}"]
        P[f"rule share {r}"] = P[f"valid {r} no ISTD"] / P[f"replicates {r}"]
    # The proposal's rule: a replicate is valid when its cell is a positive number not
    # flagged ISTD Out of Range; a metabolite is bridged when at least half its
    # replicates are valid in each run; its factor is b over the valid replicates.
    P["bridged"] = (P["rule share ADNI1"] >= 0.5) & (P["rule share ADNI2GO"] >= 0.5)
    P["b rule"] = np.where(P["bridged"], P["b no ISTD"], 0.0)

    w("## Valid NIST replicates per exported metabolite\n")
    w("A replicate is valid when its cell is a positive number; `< LOD` and `No Interception` are text in both "
      "runs and count as missing. The ADNI-GO/2 workbooks also flag cells whose internal standard was out of range "
      "(the methods summary: such data \"should not be used\"); the ADNI-1 workbooks carry no status column.\n")
    rows = []
    for k in KITS:
        S = P[P["kit"] == k]
        for r in RUNS:
            v = S[f"valid share {r}"]
            rows.append({"kit": k, "run": r, "metabolites": len(S), "min valid share": f"{v.min():.2f}",
                         "median valid share": f"{v.median():.2f}", "valid share < 0.5": int((v < 0.5).sum()),
                         "valid share < 0.75": int((v < 0.75).sum()), "no valid replicate": int((S[f'valid {r}'] == 0).sum()),
                         "metabolites with an ISTD flag": int((S[f"istd {r}"] > 0).sum())})
    w(md_table(rows))
    low = P[(P["valid share ADNI1"] < 0.5) | (P["valid share ADNI2GO"] < 0.5)]
    w(f"Metabolites with fewer than half their NIST replicates valid in either run ({len(low)}): "
      + (", ".join(f"`{m}` ({r['valid ADNI1']}/{r['replicates ADNI1']}, {r['valid ADNI2GO']}/{r['replicates ADNI2GO']})"
                   for m, r in low.iterrows()) or "none") + ".\n")

    w("## The bridge factor\n")
    w("Per metabolite, `b` = mean log2 of the valid NIST replicates in ADNI-1 minus the same in ADNI-GO/2; "
      "multiplying an ADNI-GO/2 concentration by 2^b puts it on the ADNI-1 run's scale. The SE is plate-clustered "
      "(the SD of the plate means over the square root of the plates, per run, combined in quadrature).\n")
    rows = []
    for label, S in [("all", P[P["kit"].notna()]), *[(k, P[P["kit"] == k]) for k in KITS]]:
        b, se = S["b"].dropna(), S["se b"].dropna()
        rows.append({"metabolites": label, "n": len(b), "median b": f"{b.median():+.3f}", "median abs b": f"{b.abs().median():.3f}",
                     "IQR b": f"{b.quantile(0.25):+.3f} to {b.quantile(0.75):+.3f}", "b > 0 (ADNI-GO/2 lower)": int((b > 0).sum()),
                     "abs b > 0.5": int((b.abs() > 0.5).sum()), "median SE": f"{se.median():.3f}",
                     "abs b < 2 SE": int((b.abs() < 2 * S.loc[b.index, 'se b']).sum())})
    w(md_table(rows))
    d_istd = (P["b no ISTD"] - P["b"]).abs()
    w(f"Dropping the ADNI-GO/2 cells flagged `{ISTD_STATUS}` changes `b` for {int((d_istd > 0).sum())} metabolites; "
      f"the largest change is {d_istd.max():.3f} log2 and the median change among them "
      f"{d_istd[d_istd > 0].median() if (d_istd > 0).any() else 0:.3f}.\n")

    # ---- the plate correction ---------------------------------------------
    w("## The plate correction and the run level\n")
    w("metabo_adni divides every participant value by its plate's factor q_plate / q_global (the plate's mean "
      "study-pool value over the run's mean pool value; `cross_plate_correction`). The NIST rows carry no such "
      "correction. Applying the same factors to the NIST replicates changes `b` by:\n")
    rows = []
    corr_b = {}
    for k in KITS:
        keys_k = [fk for fk in feat_keys if kit_of.get(fk) == k]
        means = {}
        for r in RUNS:
            F = pool_factors(root / RAW_FILES[(r, k)], keys_k)
            nd = nist[(r, k)]
            for fk in keys_k:
                if fk not in F.columns:
                    continue
                f = pd.Series(nd["plates"]).map(F[fk]).to_numpy()
                L = np.log2(nd["values"][fk].to_numpy() / f)
                means.setdefault(fk, {})[r] = np.nanmean(L)
        for fk, m in means.items():
            if len(m) == 2:
                corr_b[fk] = m["ADNI1"] - m["ADNI2GO"]
        diffs = pd.Series({fk: corr_b[fk] - P.loc[feat_names[feat_keys.index(fk)], "b"] for fk in keys_k if fk in corr_b})
        rows.append({"kit": k, "metabolites with pool factors": len(diffs), "median abs change": f"{diffs.abs().median():.4f}",
                     "max abs change": f"{diffs.abs().max():.4f}"})
    w(md_table(rows))

    # ---- effect on the exported block, against the run --------------------
    cleaned = pd.read_csv(args.cleaned_dir / "p180" / "P180.csv").set_index("RID")
    runs = pd.read_csv(args.cleaned_dir / "p180" / "p180_runs.csv").set_index("RID")["run"]
    rids = exported["rid"].to_numpy()
    X = cleaned.loc[rids, feat_names].to_numpy(float)
    run = runs.loc[rids].to_numpy().astype(str)
    T0, floor0 = export_scale(X)
    repro = np.abs(T0 - exported[feat_names].to_numpy(float)).max()
    w("## Effect on the exported p180 block, against the run\n")
    w(f"The {len(rids)} exported participants (run ADNI-1 {int((run == 'ADNI1').sum())}, ADNI-GO/2 "
      f"{int((run == 'ADNI2GO').sum())}). The bridge multiplies the cleaned concentrations of the ADNI-GO/2 rows by "
      "2^b before the export rule (floor at the 5 % quantile over the exported participants, then log2(x + floor)); "
      f"the floors are recomputed. The rule applied to the unbridged table reproduces `motco_input/p180.csv` to "
      f"{repro:.1e} (the file's printed precision). Offsets are ADNI-1 minus ADNI-GO/2, as the export records them.\n")

    unbridged = P.index[~P["bridged"]]
    w(f"The proposal's rule (a replicate is valid when it is a positive number not flagged `{ISTD_STATUS}`; a "
      "metabolite is bridged when at least half its replicates are valid in each run; both kits) bridges "
      f"{int(P['bridged'].sum())} of {len(P)} metabolites (FIA {int(P.loc[P['kit'] == 'FIA', 'bridged'].sum())}, "
      f"UPLC {int(P.loc[P['kit'] == 'UPLC', 'bridged'].sum())}). Not bridged (factor 1): "
      + ", ".join(f"`{m}` ({P.loc[m, 'valid ADNI1 no ISTD']}/{P.loc[m, 'replicates ADNI1']}, "
                  f"{P.loc[m, 'valid ADNI2GO no ISTD']}/{P.loc[m, 'replicates ADNI2GO']})" for m in unbridged) + ".\n")
    b_rule = P.loc[feat_names, "b rule"].to_numpy(float)
    variants = {
        "primary (no bridge)": np.zeros(len(feat_names)),
        "the proposal's rule": b_rule,
        "every metabolite, ISTD-flagged cells used": P.loc[feat_names, "b"].fillna(0).to_numpy(),
        "the rule, FIA metabolites only": np.where(P.loc[feat_names, "kit"] == "FIA", b_rule, 0.0),
    }
    rows = []
    for label, b in variants.items():
        Xb = X * np.where(run[:, None] == "ADNI2GO", 2.0 ** b[None, :], 1.0)
        Tb, fl = export_scale(Xb)
        lo = np.log2(Xb)
        o = lo[run == "ADNI1"].mean(0) - lo[run == "ADNI2GO"].mean(0)
        rows.append({"block": label, "bridged": int((b != 0).sum()), "median abs log2 offset": f"{np.median(np.abs(o)):.3f}",
                     **offset_summary(Tb, run), "floors not positive": int((fl <= 0).sum()),
                     "non-finite cells": int((~np.isfinite(Tb)).sum())})
    Tz = T0.copy()
    for r in RUNS:
        Tz[run == r] = (T0[run == r] - T0[run == r].mean(0)) / T0[run == r].std(0)
    rows.append({"block": "per-run z-score (rule's scale, then centred and scaled within run)", "bridged": "—",
                 "median abs log2 offset": "—", **offset_summary(Tz, run), "floors not positive": int((floor0 <= 0).sum()),
                 "non-finite cells": int((~np.isfinite(Tz)).sum())})
    w(md_table(rows))
    sd_ratio = T0[run == "ADNI2GO"].std(0) / T0[run == "ADNI1"].std(0)
    w(f"Within-run SD on the rule's scale, ADNI-GO/2 over ADNI-1, per metabolite: median {np.median(sd_ratio):.2f}, "
      f"IQR {np.percentile(sd_ratio, 25):.2f} to {np.percentile(sd_ratio, 75):.2f}, outside 0.83 to 1.2: "
      f"{int(((sd_ratio < 1 / 1.2) | (sd_ratio > 1.2)).sum())} (run composition included).\n")

    # ---- NIST against the participants, per metabolite --------------------
    lo = np.log2(X)
    o = pd.Series(lo[run == "ADNI1"].mean(0) - lo[run == "ADNI2GO"].mean(0), index=feat_names)
    b = P.loc[feat_names, "b rule"]
    resid = (o - b)[P.loc[feat_names, "bridged"].to_numpy()]
    w("## NIST against the participants, per metabolite\n")
    w("Participant offset `o` = mean log2 cleaned concentration in ADNI-1 minus ADNI-GO/2 over the exported "
      "participants (the run's composition included); residual = `o − b`, the part of the run difference NIST does "
      "not carry, over the metabolites the rule bridges. Descriptive: no setting of the bridge is taken from this "
      "section.\n")
    rows = []
    for label, idx in [("all", resid.index), *[(k, resid.index[P.loc[resid.index, "kit"] == k]) for k in KITS]]:
        rows.append({"metabolites": label, "n": len(idx), "median abs o": f"{o[idx].abs().median():.3f}",
                     "median abs residual": f"{resid[idx].abs().median():.3f}", "median residual": f"{resid[idx].median():+.3f}",
                     "Spearman(o, b)": f"{o[idx].rank().corr(b[idx].rank()):.2f}",
                     "share of sum of squares of o carried by b": f"{1 - (resid[idx] ** 2).sum() / (o[idx] ** 2).sum():.2f}",
                     "abs residual > 0.5": int((resid[idx].abs() > 0.5).sum())})
    w(md_table(rows))
    big = resid[resid.abs() > 0.5]
    w("Metabolites whose residual exceeds 0.5 log2: " + (", ".join(
        f"`{m}` (o {o[m]:+.2f}, b {b[m]:+.2f})" for m in big.index) or "none") + ". Not bridged, for reference: "
      + ", ".join(f"`{m}` o {o[m]:+.2f}" for m in unbridged) + ".\n")

    # ---- appendix ----------------------------------------------------------
    w("## Appendix: the bridge per metabolite\n")
    w("Valid counts and NIST means (log2 µM) under the rule (ISTD-flagged cells not valid); `b` is the factor "
      "the rule applies (0 when not bridged); `b, ISTD used` for reference. `o` as above, over participants.\n")
    rows = []
    for m in feat_names:
        r = P.loc[m]
        rows.append({"metabolite": f"`{m}`", "kit": r["kit"],
                     "valid ADNI1": f"{r['valid ADNI1 no ISTD']}/{r['replicates ADNI1']}",
                     "valid ADNI2GO": f"{r['valid ADNI2GO no ISTD']}/{r['replicates ADNI2GO']}",
                     "ISTD flags ADNI2GO": int(r["istd ADNI2GO"]), "bridged": "yes" if r["bridged"] else "no",
                     "NIST ADNI1": f"{r['mean ADNI1 no ISTD']:.3f}", "NIST ADNI2GO": f"{r['mean ADNI2GO no ISTD']:.3f}",
                     "b": f"{r['b rule']:+.3f}", "SE b": f"{r['se b no ISTD']:.3f}", "b, ISTD used": f"{r['b']:+.3f}",
                     "o": f"{o[m]:+.3f}", "o − b": f"{o[m] - r['b rule']:+.3f}"})
    w(md_table(rows))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(md))
    print(f"wrote {args.out} ({len(feat_names)} metabolites, {len(rids)} participants counted, no identifier written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
