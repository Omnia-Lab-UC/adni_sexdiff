# Spike: the NMR block with all 245 cleaned columns (2026-10-30)

Read-only and aggregate-only (`scripts/spike_nmr_all_columns.py`). It reads the cleaned NMR table and the primary export's `nmr.csv`, `p180.csv`, `covariates.csv` and `features_nmr.csv`, each checked against the manifest that records it. It builds the NMR block of `nmr_all_columns`: every cleaned column in cleaned order, each on `EXPORT_FEATURE_RULE`'s scale (`log2(x + floor)`, its own 5 % floor, linear, over the exported participants). It measures that block with the export's own count functions (`_shape_counts`, `_spectrum`, `_phase_offset`). It reads no MOTCO output, no metadata and no sex or stage, and computes no sex or stage contrast. No participant identifier or value is written.

Host: `nixos-office`; run 2026-10-30.

## Inputs

| file | sha256 | checked against |
|---|---|---|
| `motco_input/manifest.json` | `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204` | read |
| `cleaned/nmr/clean_manifest.json` | `089df72cd5891029a791d1704578d5ef049efe9c25dd99cc41511e1ce64f7657` | export manifest |
| `cleaned/nmr/NMR.csv` | `e711d62cf03f9da3f761fb18bfe4acb2d5fdf15fab6695fa5ed3901fa45d3159` | clean manifest |
| `motco_input/nmr.csv` | `a90d3eb43a86db456861e53a413f73ce8c70ec4d121eaa56e258725493114e43` | export manifest |
| `motco_input/p180.csv` | `5547356eb1761705eeee2295cfe5838e302821594b5b2675630419123861402e` | export manifest |
| `motco_input/covariates.csv` | `06999e827d4f6eb6987bfa9c63bb24f9dfd4c07dfac96ce0b55500e8cd3fccfd` | export manifest |
| `motco_input/features_nmr.csv` | `d4495f6aae38985460a118582e8e3250f9c56b8e27fc38d64bedc5b14514b9ee` | export manifest |


The exported tables carry the same `rid` column in the same order (1501 participants), every one in `NMR.csv`; missing cells among them: 0.

## Membership

| family | columns |
|---|---|
| concentration (kept by the rule) | 165 |
| percentage | 72 |
| ratio | 4 |
| degree | 1 |
| size | 3 |
| all (the variant) | 245 |


The 165 concentration columns in cleaned order equal the primary manifest's `block_columns.nmr`: yes. Their floors equal `features_nmr.csv`'s: yes. Their cells equal the primary `nmr.csv`'s, every one bitwise (parsed `round_trip`): yes.

The export's count functions on the 165 columns against the primary manifest's `counts.*.nmr`: `shape` equal; `spectrum` within 1e-12 (largest difference 1.8e-15); `phase_offset` within 1e-12 (largest difference 8.3e-17). The primary export manifest has no `numerics` block (it was written on 2026-10-27, before `adni-portable-numerics`), so its SVD-based floats come from an unpinned run; a pinned recomputation differs from them at about 1e-15, as AGENTS.md records, while the exported files reproduce byte for byte.

## Floors, zeros and finiteness (245 columns)

| columns | zero cells | columns with zeros | floors not positive | non-finite cells |
|---|---|---|---|---|
| concentration (165) | 41 | 3 | 0 | 0 |
| derived (80) | 0 | 0 | 0 | 0 |
| all (245) | 41 | 3 | 0 | 0 |


## The NMR block: primary (165) and variant (245)

Shape (`_shape_counts`: pandas skew, largest |z| at the population sd):

| block | abs_skew_gt_1 | skew_lt_minus_1 | median_abs_skew | max_abs_z_gt_5 | max_abs_z_gt_8 | max_abs_z_gt_15 |
|---|---|---|---|---|---|---|
| primary (165) | 3 | 1 | 0.178 | 4 | 1 | 0 |
| primary manifest | 3 | 1 | 0.178 | 4 | 1 | 0 |
| variant (245) | 24 | 19 | 0.265 | 38 | 9 | 1 |


Spectrum (`_spectrum`: the standardized block):

| block | features | pc1_share | pc1_3_share | pc1_10_share | effective_rank | numerical_rank | numerical_rank_tolerance |
|---|---|---|---|---|---|---|---|
| primary (165) | 165 | 0.438 | 0.770 | 0.920 | 3.773 | 165 | 1e-08 |
| variant (245) | 245 | 0.335 | 0.712 | 0.887 | 4.964 | 245 | 1e-08 |


Run offset (`_phase_offset`: ADNI1 minus ADNI2GO, pooled within-phase sd; PC correlations with phase):

| block | median_abs_d | max_abs_d | abs_d_gt_0_5 | abs_d_gt_1 | abs_corr_pc1_phase | abs_corr_pc2_phase |
|---|---|---|---|---|---|---|
| primary (165) | 0.208 | 0.672 | 2 | 0 | 0.135 | 0.072 |
| variant (245) | 0.196 | 0.694 | 5 | 0 | 0.148 | 0.011 |


## The 80 derived columns per family, on the rule's scale

| family | n | median floor / median | abs skew raw > 1 | abs skew > 1 | max abs z > 8 | median abs d | abs d > 0.5 | max abs d | R² on the 165, median | R² on the 165, min |
|---|---|---|---|---|---|---|---|---|---|---|
| percentage | 72 | 0.843 | 27 | 21 | 8 | 0.146 | 3 | 0.694 | 0.998 | 0.798 |
| ratio | 4 | 0.631 | 2 | 0 | 0 | 0.138 | 0 | 0.293 | 0.999 | 0.995 |
| degree | 1 | 0.924 | 0 | 0 | 0 | 0.199 | 0 | 0.199 | 0.993 | 0.993 |
| size | 3 | 0.974 | 0 | 0 | 0 | 0.199 | 0 | 0.255 | 0.999 | 0.998 |
| all derived | 80 | 0.843 | 29 | 21 | 8 | 0.153 | 3 | 0.694 | 0.998 | 0.798 |


R² is the share of a derived column's variance (on the rule's scale) that a least-squares fit on the 165 concentration columns (on the same scale, with an intercept) explains: how far the column is a linear function of the concentrations as the analysis sees them.


The derived columns with the largest |skew| on the rule's scale: `L_HDL_PL_PCT` -6.96, `L_HDL_C_PCT` -3.74, `L_HDL_FC_PCT` -3.63, `L_VLDL_PL_PCT` -3.49, `L_HDL_CE_PCT` -3.39.

The derived columns with the largest phase |d|: `S_LDL_PL_PCT` -0.694, `S_LDL_CE_PCT` +0.581, `S_LDL_C_PCT` +0.550, `L_VLDL_FC_PCT` +0.493, `L_VLDL_TG_PCT` -0.449.

The derived columns with the lowest R² on the concentrations: `XL_VLDL_C_PCT` 0.798, `XL_VLDL_CE_PCT` 0.830, `L_HDL_PL_PCT` 0.888, `XL_VLDL_FC_PCT` 0.912, `XL_VLDL_TG_PCT` 0.917.


## The joint matrix (p180 then NMR, as MOTCO concatenates them)

| matrix | features | p180 share | nmr share | pc1 share | pc1-10 share | effective rank | numerical rank | pc1 corr phase | pc2 corr phase |
|---|---|---|---|---|---|---|---|---|---|
| primary (133 + 165) | 298 | 0.446 | 0.554 | 0.316 | 0.789 | 6.654 | 298 | 0.415 | 0.148 |
| variant (133 + 245) | 378 | 0.352 | 0.648 | 0.267 | 0.783 | 7.522 | 378 | 0.400 | 0.015 |


The shares are of the features; MOTCO 0.10.0 z-scores every feature and weights features, not blocks. The spectrum and the phase correlations are of the standardized joint matrix (population sd), descriptive only: MOTCO's PLS-DA basis is supervised by stage and is not this PCA.


## Counts for the proposal

| quantity | value |
|---|---|
| NMR columns cleaned / kept / derived kept | 245 / 245 / 80 |
| joint features; p180 / NMR share | 378; 0.352 / 0.648 |
| NMR zero cells / columns with zeros | 41 / 3 |
| NMR floors not positive / non-finite cells | 0 / 0 |
| NMR phase abs d > 0.5 / > 1 | 5 / 0 |
| 165 concentration columns equal to the primary's | yes |
