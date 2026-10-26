#!/usr/bin/env python
"""Spike: inventory of the raw ADNI metabolomics files and the cohort they support.

Read-only and counts-only. Reads the raw files from the data root through
metabo_adni's own loaders and QC functions in a temporary working copy (the
truncated UPLC ADNI-GO/2 file repaired there by appending its missing closing
quote), the QT-PAD ADNIMERGE freeze and the medication table, and writes one
Markdown report of aggregate counts. No participant identifier is printed or
written; metabo_adni's own printing (which lists RIDs) is silenced. The
working copy is deleted at the end.

Usage (inside the Nix shell):
  uv run python -I scripts/spike_raw_inventory.py --data-root data \
      --out openspec/changes/<change>/spike.md --workdir <scratch dir>
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import io
import os
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as stats
from importlib.metadata import version as pkg_version

from metabo_adni.data import load
from metabo_adni.qc import metabolites, participants, transformations

RAW_FILES = [
    "ADMCDUKEP180UPLC_01_15_16.csv",
    "ADMCDUKEP180FIA_01_15_16.csv",
    "ADMCDUKEP180UPLCADNI2GO.csv",
    "ADMCDUKEP180FIAADNI2GO.csv",
    "4097_UPLC_p180_Data.xlsx",
    "4097_FIA_p180_Data.xlsx",
    "4610 UPLC p180 Data.xlsx",
    "4610 FIA p180 Data.xlsx",
    "ADNINIGHTINGALE2.csv",
    "BIOMARK.csv",
    "ADMCPATIENTDRUGCLASSES_20170512.csv",
]
REPAIR_FILE = "ADMCDUKEP180UPLCADNI2GO.csv"
ADNIMERGE = "ADNI_adnimerge_20170629_QT-freeze.csv"
P180_FILES = {
    "ADNI1-UPLC": "ADMCDUKEP180UPLC_01_15_16.csv",
    "ADNI1-FIA": "ADMCDUKEP180FIA_01_15_16.csv",
    "ADNI2GO-UPLC": "ADMCDUKEP180UPLCADNI2GO.csv",
    "ADNI2GO-FIA": "ADMCDUKEP180FIAADNI2GO.csv",
}
DEFAULTS = {"mmc": 0.2, "mpc": 0.2, "cv": 0.2, "icc": 0.65}
PAPER_MPC = 0.4
STAGE_MAP = {"CN": "CN", "SMC": "CN", "MCI": "MCI", "EMCI": "MCI", "LMCI": "MCI", "AD": "AD"}
STAGES = ["CN", "MCI", "AD"]
MIN_MED_USERS = 20


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def quiet(fn, *args, **kwargs):
    """Call a metabo_adni function with its stdout discarded (it prints RID tables)."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def md_table(rows: list[dict], cols: list[str] | None = None) -> str:
    if not rows:
        return "(none)\n"
    cols = cols or list(rows[0].keys())
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out) + "\n"


def shape_of(files: dict, platform: str) -> dict[str, tuple[int, int]]:
    out = {}
    for key, df in files.items():
        if not hasattr(df, "shape"):
            out[key] = (0, 0)
            continue
        mets = load._get_metabo_col_names(df, key)
        idx = load._get_data_indices(df, platform)
        sub = df.loc[idx]
        out[key] = (int(sub.index.nunique()), len(mets))
    return out


def fmt_shapes(shapes: dict) -> str:
    return "; ".join(f"{k}: {n} × {m}" for k, (n, m) in shapes.items())


def crosstab_md(df: pd.DataFrame, row: str, col: str, row_order=None, col_order=None) -> str:
    ct = pd.crosstab(df[row], df[col], margins=True, margins_name="all")
    if row_order:
        ct = ct.reindex([r for r in row_order if r in ct.index] + ["all"])
    if col_order:
        ct = ct.reindex(columns=[c for c in col_order if c in ct.columns] + ["all"])
    rows = [{row: str(i), **{str(c): int(v) for c, v in r.items()}} for i, r in ct.iterrows()]
    return md_table(rows, [row] + [str(c) for c in ct.columns])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-root", type=Path, default=Path(os.environ.get("ADNI_DATA_ROOT", "data")))
    ap.add_argument("--out", type=Path, required=True, help="Markdown report to write (aggregate counts only)")
    ap.add_argument("--workdir", type=Path, required=True, help="Directory for the temporary working copy")
    args = ap.parse_args()
    root = args.data_root.resolve()
    repo_root = Path.cwd()
    today = dt.date.today().isoformat()

    args.workdir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="spike_", dir=args.workdir))
    R: list[str] = []  # report lines
    try:
        # ---- working copy + hashes -------------------------------------
        hashes = []
        for name in RAW_FILES:
            src = root / name
            dst = work / name
            shutil.copyfile(src, dst)  # follows symlinks
            hashes.append({"file": f"`{name}`", "target": f"`{os.readlink(src) if src.is_symlink() else name}`",
                           "bytes": src.stat().st_size, "sha256": sha256(src)[:16] + "…"})
        raw = (work / REPAIR_FILE).read_bytes()
        repaired = not raw.endswith(b'"\n')
        if repaired:
            (work / REPAIR_FILE).write_bytes(raw + b'"\n')
        am_src = root / ADNIMERGE
        hashes.append({"file": f"`{ADNIMERGE}`", "target": "(archive)", "bytes": am_src.stat().st_size,
                       "sha256": sha256(am_src)[:16] + "…"})

        R.append(f"# Spike: raw ADNI metabolomics inventory and cohort cells ({today})\n")
        R.append("Read-only, counts only. Generated by `scripts/spike_raw_inventory.py` from the data root through "
                 "metabo_adni's own loaders and QC functions (version "
                 f"{pkg_version('metabo_adni')}, pandas {pd.__version__}) in a temporary working copy, deleted "
                 "afterwards. metabo_adni's printing (which lists RIDs) was silenced; every number below is a count, "
                 "a proportion or a hash. No participant identifier appears in this file.\n")
        R.append(f"`{REPAIR_FILE}`: LONI's export lacks its final closing quote (see AGENTS.md). "
                 f"{'The working copy appended it.' if repaired else 'The archive copy already carries the repair, so the working copy applied none.'}\n")
        R.append("## Files read\n")
        R.append(md_table(hashes))

        # ---- raw inventory ----------------------------------------------
        R.append("## Raw records per file\n")
        inv = []
        for key, name in P180_FILES.items():
            df = pd.read_csv(work / name, na_values=["< LOD", "No Interception", ">Highest CS"], low_memory=False)
            part = df[df["RID"] < 99999]
            pool = df[df["RID"] == 999999]
            dup = part["RID"].value_counts()
            vis = part["VISCODE"].value_counts().to_dict() if "VISCODE" in part.columns else {"(no VISCODE column)": len(part)}
            inv.append({"file": key, "records": len(df), "QC pool records": len(pool), "participant records": len(part),
                        "unique RIDs": part["RID"].nunique(), "RIDs with replicates": int((dup > 1).sum()),
                        "plates": part["Plate.Bar.Code"].nunique(), "visit codes": ", ".join(f"{k}: {v}" for k, v in sorted(vis.items()))})
        nmr = pd.read_csv(work / "ADNINIGHTINGALE2.csv", na_values=["TAG"], low_memory=False)
        dup = nmr["RID"].value_counts()
        inv.append({"file": "NMR", "records": len(nmr), "QC pool records": 0, "participant records": len(nmr),
                    "unique RIDs": nmr["RID"].nunique(), "RIDs with replicates": int((dup > 1).sum()), "plates": "",
                    "visit codes": ", ".join(f"{k}: {v}" for k, v in sorted(nmr["VISCODE2"].value_counts().to_dict().items()))})
        R.append(md_table(inv))
        qc_cols = load._get_nmr_qc_cols()
        tagged = (nmr[qc_cols[:-1]].fillna(0).sum(axis=1) > 0)
        blq = nmr[qc_cols[-1]].fillna(0) > 0
        R.append(f"NMR records with any QC tag other than below-limit-of-quantification: {int(tagged.sum())}; "
                 f"with the below-LOQ tag: {int(blq.sum())}; with any missing (`TAG`) metabolite value: "
                 f"{int(nmr[load._get_metabo_col_names(nmr, 'NMR')].isna().any(axis=1).sum())}.\n")

        # ---- metabo_adni pipeline per platform ---------------------------
        R.append("## metabo_adni pipeline with its defaults (per platform, in memory)\n")
        R.append(f"Cutoffs: missing metabolites > {DEFAULTS['mmc']}, missing participants > {DEFAULTS['mpc']}, "
                 f"CV > {DEFAULTS['cv']}, ICC < {DEFAULTS['icc']}; the fasting file is `BIOMARK.csv`; p180 imputation "
                 "uses the LOD workbooks; no transform flag. Cells are participants × metabolites after each step.\n")
        cleaned: dict[str, pd.DataFrame] = {}
        phase_of_rid: dict[int, str] = {}
        imput_points: dict[str, int] = {}
        imput_kept: dict[str, int] = {}
        multi_plate: dict[str, tuple[int, int]] = {}
        between_cutoffs: dict[str, int] = {}
        for platform in ("p180", "nmr"):
            steps = []
            files = quiet(load.read_files, str(work), platform)
            os.chdir(repo_root)
            steps.append({"step": "read", "cells": fmt_shapes(shape_of(files, platform))})
            files = quiet(metabolites.remove_missing, files, platform, DEFAULTS["mmc"])
            steps.append({"step": f"metabolites missing > {DEFAULTS['mmc']}", "cells": fmt_shapes(shape_of(files, platform))})
            if platform == "p180":
                files = quiet(metabolites.cross_plate_correction, files, platform)
                files = quiet(metabolites.remove_cv, files, platform, DEFAULTS["cv"])
                steps.append({"step": f"cross-plate correction; CV > {DEFAULTS['cv']}", "cells": fmt_shapes(shape_of(files, platform))})
                files = quiet(metabolites.remove_icc, files, platform, DEFAULTS["icc"])
                steps.append({"step": f"ICC < {DEFAULTS['icc']}", "cells": fmt_shapes(shape_of(files, platform))})
            # participants between the two missingness cutoffs
            before = shape_of(files, platform)
            at_default = shape_of(quiet(participants.remove_missing, copy.deepcopy(files), platform, DEFAULTS["mpc"]), platform)
            at_paper = shape_of(quiet(participants.remove_missing, copy.deepcopy(files), platform, PAPER_MPC), platform)
            between_cutoffs[platform] = sum(at_paper[k][0] - at_default[k][0] for k in before)
            files = quiet(participants.remove_missing, files, platform, DEFAULTS["mpc"])
            steps.append({"step": f"participants missing > {DEFAULTS['mpc']}", "cells": fmt_shapes(shape_of(files, platform))})
            files = quiet(participants.consolidate_replicates, files, platform)
            steps.append({"step": "replicates averaged", "cells": fmt_shapes(shape_of(files, platform))})
            files = quiet(participants.remove_non_fasters, files, str(work / "BIOMARK.csv"))
            steps.append({"step": "non-fasting removed", "cells": fmt_shapes(shape_of(files, platform))})
            files = quiet(participants.remove_bad_qc_tags, files, platform)
            steps.append({"step": "bad QC tags", "cells": fmt_shapes(shape_of(files, platform))})
            # imputation accounting before imputing
            pts = 0
            mp_mets, mp_points = 0, 0
            kept_cols: dict[str, set] = {}
            if platform == "p180":
                for kit in ("UPLC", "FIA"):
                    a = set(load._get_metabo_col_names(files[f"ADNI1-{kit}"], f"ADNI1-{kit}"))
                    b = set(load._get_metabo_col_names(files[f"ADNI2GO-{kit}"], f"ADNI2GO-{kit}"))
                    kept_cols[f"ADNI1-{kit}"] = kept_cols[f"ADNI2GO-{kit}"] = a & b
            for key, df in files.items():
                mets = load._get_metabo_col_names(df, key)
                sub = df.loc[load._get_data_indices(df, platform), list(mets)]
                pts += int(sub.isna().sum().sum())
                kept = [m for m in mets if m in kept_cols.get(key, set(mets))]
                imput_kept[key] = int(sub[kept].isna().sum().sum())
                if platform == "p180":
                    plates = df.loc[load._get_data_indices(df, platform), "Plate.Bar.Code"]
                    for m in mets[sub.isna().any()]:
                        n_pl = plates[sub[m].isna()].nunique()
                        if n_pl > 1:
                            mp_mets += 1
                            mp_points += int(sub[m].isna().sum())
                imput_points[key] = int(sub.isna().sum().sum())
            multi_plate[platform] = (mp_mets, mp_points)
            files = quiet(transformations.imputation, files, platform, str(work) if platform == "p180" else None)
            os.chdir(repo_root)
            steps.append({"step": f"imputation ({pts} points)", "cells": fmt_shapes(shape_of(files, platform))})
            if platform == "p180":
                for key, df in files.items():
                    for rid in df.index[load._get_data_indices(df, platform)]:
                        phase_of_rid.setdefault(int(rid), "ADNI1" if key.startswith("ADNI1") else "ADNI2GO")
                        if (key.startswith("ADNI2GO") and phase_of_rid[int(rid)] == "ADNI1"):
                            phase_of_rid[int(rid)] = "both"
            files = quiet(transformations.merge, files, platform)
            steps.append({"step": "merge (p180: FIA ⋈ UPLC within phase, phases stacked, metabolite intersection)",
                          "cells": fmt_shapes(shape_of(files, platform))})
            R.append(f"### {platform}\n")
            R.append(md_table(steps))
            final = next(iter(files.values()))
            dups = int(final.index.duplicated().sum())
            R.append(f"Final `{next(iter(files))}` table: {final.index.nunique()} participants × {final.shape[1]} metabolites; "
                     f"duplicated RIDs after merge: {dups}. Participants removed at the paper's {PAPER_MPC} cutoff minus "
                     f"those removed at the default {DEFAULTS['mpc']}: {between_cutoffs[platform]} "
                     f"(negative means the default removes more).\n")
            cleaned[platform] = final[~final.index.duplicated(keep="first")]
            # zeros and minima after imputation
            vals = cleaned[platform].to_numpy(dtype=float)
            pos = vals[vals > 0]
            zero_mets = list(cleaned[platform].columns[(cleaned[platform] == 0).any()])
            R.append(f"Values after imputation: zeros {int((vals == 0).sum())} in "
                     f"{len(zero_mets)} metabolites ({', '.join(f'`{z}`' for z in zero_mets) or 'none'}); values below 1: "
                     f"{int((vals < 1).sum())} of {vals.size} ({(vals < 1).mean():.1%}); smallest positive "
                     f"{pos.min():.3g}; median {np.median(vals):.3g}; metabolites with median below 1: "
                     f"{int((cleaned[platform].median() < 1).sum())}.\n")
        p180_phase = pd.Series({r: p for r, p in phase_of_rid.items() if r in cleaned["p180"].index})
        R.append(f"p180 participants by run after the pipeline: {p180_phase.value_counts().to_dict()}.\n")
        R.append("### Imputation accounting (before imputing)\n")
        R.append(md_table([{"table": k, "missing points": v, "of which in metabolites the merge keeps": imput_kept.get(k, v)}
                           for k, v in imput_points.items()]))
        R.append(f"p180 metabolites whose missing values span more than one plate: "
                 f"{multi_plate['p180'][0]} ({multi_plate['p180'][1]} points). metabo_adni 0.5.8 assigns the last "
                 "plate's LOD/2 to every missing value of such a metabolite (its per-plate loop overwrites the same "
                 "rows), and for ADNI2GO-UPLC it assigns the LOD itself, not LOD/2. Upstream findings, not patched here.\n")

        # ---- ADNIMERGE baseline ------------------------------------------
        R.append("## QT-PAD ADNIMERGE freeze (2017-06-29), baseline rows\n")
        am = pd.read_csv(am_src, low_memory=False)
        bl = am[am["VISCODE"] == "bl"].copy()
        R.append(f"Rows {len(am)}; baseline rows {len(bl)}; unique RIDs at baseline {bl['RID'].nunique()} "
                 f"(duplicated baseline RIDs: {int(bl['RID'].duplicated().sum())}).\n")
        bl["stage"] = bl["DX.bl"].map(STAGE_MAP)
        R.append("Baseline diagnosis (`DX.bl`) by original protocol:\n")
        R.append(crosstab_md(bl.fillna({"DX.bl": "(missing)"}), "DX.bl", "ORIGPROT"))
        R.append("Merged stage (SMC → CN; EMCI, LMCI → MCI) by sex:\n")
        R.append(crosstab_md(bl.fillna({"stage": "(missing)"}), "stage", "PTGENDER", row_order=STAGES))
        miss = {c: int(bl[c].isna().sum()) for c in ["DX.bl", "PTGENDER", "AGE", "PTEDUCAT", "APOE4"]}
        R.append(f"Missing at baseline: {miss}. `COLPROT` equals `ORIGPROT` at baseline for "
                 f"{int((bl['COLPROT'] == bl['ORIGPROT']).sum())} of {len(bl)} rows.\n")

        # ---- intersections ----------------------------------------------
        R.append("## Platform availability and the intersection cohort\n")
        cov_cols = ["AGE", "PTEDUCAT", "APOE4"]
        meta = bl.set_index("RID")[["ORIGPROT", "PTGENDER", "stage"] + cov_cols]
        meta = meta[~meta.index.duplicated(keep="first")]
        have = pd.DataFrame(index=meta.index)
        have["p180"] = have.index.isin(cleaned["p180"].index)
        have["nmr"] = have.index.isin(cleaned["nmr"].index)
        not_in_merge = {p: int((~cleaned[p].index.isin(meta.index)).sum()) for p in cleaned}
        R.append(f"Cleaned participants absent from the ADNIMERGE baseline rows: {not_in_merge}.\n")
        sets = {"p180 only": have["p180"] & ~have["nmr"], "NMR only": have["nmr"] & ~have["p180"],
                "both platforms": have["p180"] & have["nmr"], "either": have["p180"] | have["nmr"]}
        rows = []
        for name, mask in sets.items():
            sub = meta[mask]
            complete = sub.dropna(subset=["stage", "PTGENDER"] + cov_cols)
            rows.append({"set": name, "n": int(mask.sum()), "with stage and sex": int(sub.dropna(subset=["stage", "PTGENDER"]).shape[0]),
                         "complete covariates (age, education, APOE4)": int(complete.shape[0])})
        R.append(md_table(rows))
        both = meta[sets["both platforms"]].dropna(subset=["stage", "PTGENDER"] + cov_cols).copy()
        both["run"] = both.index.map(lambda r: phase_of_rid.get(int(r), "?"))
        R.append("### Intersection cohort (both platforms, stage, sex and covariates complete): sex × stage\n")
        R.append(crosstab_md(both, "PTGENDER", "stage", col_order=STAGES))
        R.append("### Intersection cohort: sex × stage per original protocol\n")
        for prot in sorted(both["ORIGPROT"].dropna().unique()):
            R.append(f"{prot}:\n")
            R.append(crosstab_md(both[both["ORIGPROT"] == prot], "PTGENDER", "stage", col_order=STAGES))
        R.append("### Intersection cohort: p180 run against original protocol\n")
        R.append(crosstab_md(both, "run", "ORIGPROT"))
        R.append("### Single-platform cohorts (stage, sex and covariates complete): sex × stage\n")
        for p in ("p180", "nmr"):
            sub = meta[have[p]].dropna(subset=["stage", "PTGENDER"] + cov_cols)
            R.append(f"{p} (n = {len(sub)}):\n")
            R.append(crosstab_md(sub, "PTGENDER", "stage", col_order=STAGES))
        R.append("Covariates in the intersection cohort: " + "; ".join(
            f"{c} mean {both[c].mean():.1f}, sd {both[c].std():.1f}" for c in ["AGE", "PTEDUCAT"]) +
            f"; APOE4 allele count {both['APOE4'].value_counts().sort_index().to_dict()}.\n")

        # ---- multivariate outliers (would-be) ----------------------------
        R.append("## Would-be multivariate outliers (not removed)\n")
        R.append("metabo_adni's Mahalanobis rule (chi-square 0.999 quantile) applied to the intersection cohort after "
                 "log2(x + 1) and z-scoring, per platform; counted, never applied to any output.\n")
        for p in ("p180", "nmr"):
            df = cleaned[p].loc[both.index].copy()
            key = "P180" if p == "p180" else "NMR"
            dfz = np.log2(df + 1).apply(stats.zscore, nan_policy="omit")
            try:
                kept = quiet(participants.remove_moutliers, {key: dfz.copy()}, p)[key]
                removed = both.loc[~both.index.isin(kept.index)]
                R.append(f"{p}: {len(removed)} of {len(both)} would be removed; by sex × stage:\n")
                R.append(crosstab_md(removed, "PTGENDER", "stage", col_order=STAGES) if len(removed) else "(none)\n")
            except np.linalg.LinAlgError as e:
                R.append(f"{p}: covariance not invertible ({e}); the rule cannot run on this block as is.\n")

        # ---- medications --------------------------------------------------
        R.append("## Medication classes (intersection cohort)\n")
        raw_meds = pd.read_csv(work / "ADMCPATIENTDRUGCLASSES_20170512.csv", dtype=str, low_memory=False)
        cls_cols = [c for c in raw_meds.columns if c not in ("RID", "VISCODE2", "Phase", "NA")]
        vis_rows = {v: raw_meds[raw_meds["VISCODE2"] == v] for v in ("sc", "bl")}
        R.append("The table has one row per participant and visit; medication classes are filled at the screening "
                 "visit (`sc`), not at baseline (`bl`): " + "; ".join(
                     f"`{v}` rows {len(s)}, unique RIDs {s['RID'].nunique()}, rows with no class cell "
                     f"{int((s[cls_cols].notna().sum(axis=1) == 0).sum())}" for v, s in vis_rows.items()) +
                 ". metabo_adni 0.5.8's `read_meds_file` keeps the `bl` rows, so its `--residualize-meds` sees almost no "
                 "medication (upstream finding, not patched here). The counts below use the `sc` rows, one per RID, a "
                 "class counted when its cell is filled.\n")
        sc = vis_rows["sc"].copy()
        sc["RID"] = sc["RID"].astype(int)
        meds = sc.set_index("RID")[cls_cols].notna().astype(int)
        meds = meds[~meds.index.duplicated(keep="first")]
        m = both.join(meds, how="inner")
        classes = [c for c in meds.columns if m[c].sum() >= MIN_MED_USERS]
        os.chdir(work)
        meds_bl = quiet(load.read_meds_file)
        os.chdir(repo_root)
        bl_classes = int((both.join(meds_bl[~meds_bl.index.duplicated(keep='first')], how="inner")[list(meds_bl.columns)].sum() >= MIN_MED_USERS).sum())
        R.append(f"Participants of the intersection cohort with a screening medication record: {len(m)} of {len(both)}; "
                 f"classes with at least {MIN_MED_USERS} users there: {len(classes)} of {len(cls_cols)} "
                 f"(through metabo_adni's baseline reader: {bl_classes}).\n")
        rows = []
        for c in classes:
            by_sex = m.groupby("PTGENDER")[c].mean()
            by_stage = m.groupby("stage")[c].mean().reindex(STAGES)
            rows.append({"class": c, "users": int(m[c].sum()), "F %": f"{100 * by_sex.get('Female', np.nan):.0f}",
                         "M %": f"{100 * by_sex.get('Male', np.nan):.0f}",
                         "CN %": f"{100 * by_stage['CN']:.0f}", "MCI %": f"{100 * by_stage['MCI']:.0f}", "AD %": f"{100 * by_stage['AD']:.0f}",
                         "_sex_gap": abs(by_sex.get('Female', 0) - by_sex.get('Male', 0)),
                         "_stage_gap": by_stage.max() - by_stage.min()})
        rows.sort(key=lambda r: -r["users"])
        cols = ["class", "users", "F %", "M %", "CN %", "MCI %", "AD %"]
        R.append(f"All classes with at least {MIN_MED_USERS} users, by prevalence:\n")
        R.append(md_table(rows, cols))
        R.append("Largest sex gaps (percentage points):\n")
        R.append(md_table(sorted(rows, key=lambda r: -r["_sex_gap"])[:10], cols))
        R.append("Largest stage gaps (percentage points):\n")
        R.append(md_table(sorted(rows, key=lambda r: -r["_stage_gap"])[:10], cols))

        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("\n".join(R), encoding="utf-8")
        print(f"[spike] wrote {args.out} ({len(R)} blocks); working copy removed")
        return 0
    finally:
        os.chdir(repo_root)
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
