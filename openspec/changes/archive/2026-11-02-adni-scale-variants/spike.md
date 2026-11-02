# Spike: both blocks on the three scale variants (2026-11-02)

Read-only and aggregate-only (`scripts/spike_scale_variants.py`). It reads the cleaned p180 and NMR tables and the primary export's `p180.csv`, `nmr.csv`, `covariates.csv`, `features_p180.csv` and `features_nmr.csv`, each checked against the manifest that records it. It rebuilds each block on the rule's scale (`log2(x + floor)`, the 5 % floor over the exported participants) and checks it against the primary's CSV cell for cell, then builds the three variant scales of the same cells: `raw_scale` (the cleaned concentrations as metabo_adni leaves them), `log2_plus_one` (`log2(x + 1)`) and `glog` (`log2((x + sqrt(x² + λ²)) / 2)`, λ per metabolite its smallest positive value over the exported participants divided by 10). It measures each block on each scale with the export's own count functions (`_shape_counts`, `_spectrum`, `_phase_offset`). It reads no MOTCO output, no metadata and no sex or stage, and computes no sex or stage contrast. No participant identifier or value is written.

Host: `nixos-home`; run 2026-11-02.

## Inputs

| file | sha256 | checked against |
|---|---|---|
| `motco_input/manifest.json` | `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204` | read |
| `cleaned/p180/clean_manifest.json` | `6f11a627648d17a5c1294420fd3ed32c1e125c8c0cb53b37d3f3d247fb5f78ce` | export manifest |
| `cleaned/p180/P180.csv` | `33b18bd2187173179aa280ee74fc0a8f37ca2f155cdd37d4f87412631132ff9d` | clean manifest |
| `cleaned/nmr/clean_manifest.json` | `089df72cd5891029a791d1704578d5ef049efe9c25dd99cc41511e1ce64f7657` | export manifest |
| `cleaned/nmr/NMR.csv` | `e711d62cf03f9da3f761fb18bfe4acb2d5fdf15fab6695fa5ed3901fa45d3159` | clean manifest |
| `motco_input/p180.csv` | `5547356eb1761705eeee2295cfe5838e302821594b5b2675630419123861402e` | export manifest |
| `motco_input/nmr.csv` | `a90d3eb43a86db456861e53a413f73ce8c70ec4d121eaa56e258725493114e43` | export manifest |
| `motco_input/covariates.csv` | `06999e827d4f6eb6987bfa9c63bb24f9dfd4c07dfac96ce0b55500e8cd3fccfd` | export manifest |
| `motco_input/features_p180.csv` | `7793776534d580f9a49e0ad95e0d8f6ecef3b5a7ff3c02f64dd07c905f4bb5ee` | export manifest |
| `motco_input/features_nmr.csv` | `d4495f6aae38985460a118582e8e3250f9c56b8e27fc38d64bedc5b14514b9ee` | export manifest |


The exported tables carry the same `rid` column in the same order (1501 participants).

## The rule's scale reproduced

| block | kept columns | columns equal `block_columns` | floors equal `features_*.csv` | cells equal the primary CSV (bitwise) | counts reproduced |
|---|---|---|---|---|---|
| p180 | 133 | yes | yes | yes | `shape` equal; `spectrum` within 1e-12 (2.2e-16); `phase_offset` within 1e-12 (1.1e-16) |
| nmr | 165 | yes | yes | yes | `shape` equal; `spectrum` within 1e-12 (1.8e-15); `phase_offset` within 1e-12 (8.3e-17) |


The primary export manifest has no `numerics` block (written on 2026-10-27, before `adni-portable-numerics`), so its SVD-based floats come from an unpinned run; a pinned recomputation differs from them at about 1e-15, as AGENTS.md records, while the exported files reproduce byte for byte.


## The scales

Every scale below is applied to the same cells: the primary's participants and the primary's membership (133 p180 metabolites, 165 NMR concentrations). Each is a monotone increasing function of the concentration, so per feature the ranks of the participants are the same on every scale (Spearman 1 with the rule's scale); what changes is the spacing: how far the low values are compressed and how far the high values spread.

| scale | transform | offset | where x = 0 lands |
|---|---|---|---|
| `rule` | `log2(x + floor)` | the metabolite's 5 % quantile | `log2(floor)` |
| `raw_scale` | `x` | none | 0 |
| `log2_plus_one` | `log2(x + 1)` | 1, in the platform's unit | 0 |
| `glog` | `log2((x + sqrt(x² + λ²)) / 2)` | λ = the metabolite's smallest positive value / 10 | `log2(λ / 2)`, 4.32 bits below `log2` of the smallest positive value |


## The offsets against the concentrations

Quantiles over the kept metabolites of a block (native units: p180 µM, NMR mostly mmol/L):

| block | quantity | q05 | q25 | q50 | q75 | q95 |
|---|---|---|---|---|---|---|
| p180 | median concentration | 0.05004 | 0.4688 | 2.937 | 29.51 | 143 |
| p180 | rule floor | 0.02398 | 0.2696 | 1.791 | 20.57 | 95.95 |
| p180 | rule floor / median | 0.4491 | 0.5654 | 0.6028 | 0.6313 | 0.704 |
| p180 | smallest positive value | 0.0073 | 0.1252 | 0.9719 | 9.203 | 64.98 |
| p180 | λ / median | 0.004988 | 0.02536 | 0.03349 | 0.03943 | 0.0493 |
| p180 | 1 / median | 0.007006 | 0.03389 | 0.3405 | 2.133 | 20.02 |
| nmr | median concentration | 0.0002223 | 0.04812 | 0.1559 | 0.6922 | 3.917 |
| nmr | rule floor | 7.858e-05 | 0.01787 | 0.09405 | 0.4915 | 2.878 |
| nmr | rule floor / median | 0.09142 | 0.4784 | 0.6505 | 0.7101 | 0.8032 |
| nmr | smallest positive value | 1.955e-06 | 0.001463 | 0.04255 | 0.29 | 1.947 |
| nmr | λ / median | 0.0001003 | 0.008931 | 0.03503 | 0.04774 | 0.05961 |
| nmr | 1 / median | 0.2554 | 1.445 | 6.415 | 20.78 | 4574 |


Kept metabolites by median concentration (native units), the regime of `log2(x + 1)`:

| block | kept | [0, 0.1) | [0.1, 1) | [1, 10) | [10, 100) | ≥ 100 | median < 1 (near-linear under log2(x + 1)) | median ≥ 100 (near log2(x)) |
|---|---|---|---|---|---|---|---|---|
| p180 | 133 | 10 | 36 | 37 | 37 | 13 | 46 | 13 |
| nmr | 165 | 67 | 62 | 33 | 3 | 0 | 129 | 0 |


Under `log2(x + 1)` a metabolite whose values lie well below 1 is nearly linear (`log2(1 + x) ≈ x / ln 2`), and one whose values lie well above 1 is nearly `log2(x)`; the pseudo-count is the same number in each platform's unit, so the scale a metabolite gets depends on its abundance and its unit.


## Zero cells

| block | zero cells | metabolites with zeros | rule: `log2(floor)` | raw_scale | log2_plus_one | glog |
|---|---|---|---|---|---|---|
| p180 | 0 | 0 | per metabolite | 0 | 0 | `log2(λ / 2)`, 4.32 bits below the smallest positive value |
| nmr | 41 | 3 | per metabolite | 0 | 0 | `log2(λ / 2)`, 4.32 bits below the smallest positive value |


The generalized log against `log2(x)` on the positive cells (bits):

| block | largest |glog − log2(x)| | q99 | bound at x = smallest positive value |
|---|---|---|---|
| p180 | 0.0036 | 0.0022 | 0.0036 |
| nmr | 0.0036 | 0.0022 | 0.0036 |


## Each block on each scale


### p180 (133 metabolites)

Shape (`_shape_counts`: pandas skew, largest |z| at the population sd) and non-finite cells:

| scale | abs_skew_gt_1 | skew_lt_minus_1 | median_abs_skew | max_abs_z_gt_5 | max_abs_z_gt_8 | max_abs_z_gt_15 | non_finite |
|---|---|---|---|---|---|---|---|
| rule: log2(x + floor) | 1 | 0 | 0.317 | 17 | 0 | 0 | 0 |
| raw_scale: x | 46 | 0 | 0.903 | 74 | 12 | 0 | 0 |
| log2_plus_one: log2(x + 1) | 14 | 0 | 0.310 | 27 | 9 | 0 | 0 |
| glog: log2((x + sqrt(x² + λ²)) / 2) | 6 | 6 | 0.089 | 17 | 6 | 2 | 0 |


Spectrum (`_spectrum`: the standardized block):

| scale | pc1_share | pc1_3_share | pc1_10_share | effective_rank | numerical_rank |
|---|---|---|---|---|---|
| rule: log2(x + floor) | 0.418 | 0.549 | 0.747 | 5.222 | 133 |
| raw_scale: x | 0.407 | 0.535 | 0.732 | 5.502 | 133 |
| log2_plus_one: log2(x + 1) | 0.415 | 0.545 | 0.742 | 5.310 | 133 |
| glog: log2((x + sqrt(x² + λ²)) / 2) | 0.416 | 0.546 | 0.743 | 5.285 | 133 |


Run offset (`_phase_offset`: ADNI1 minus ADNI2GO, pooled within-phase sd; PC correlations with phase):

| scale | median_abs_d | max_abs_d | abs_d_gt_0_5 | abs_d_gt_1 | abs_corr_pc1_phase | abs_corr_pc2_phase |
|---|---|---|---|---|---|---|
| rule: log2(x + floor) | 1.121 | 2.876 | 109 | 80 | 0.734 | 0.398 |
| raw_scale: x | 1.083 | 2.292 | 108 | 76 | 0.723 | 0.398 |
| log2_plus_one: log2(x + 1) | 1.109 | 2.322 | 108 | 80 | 0.731 | 0.392 |
| glog: log2((x + sqrt(x² + λ²)) / 2) | 1.130 | 2.956 | 109 | 80 | 0.731 | 0.399 |


Agreement with the rule's scale per metabolite (Pearson r of the two scalings of the same column):

| scale | median r | q05 | min | r < 0.9 | r < 0.99 |
|---|---|---|---|---|---|
| raw_scale: x | 0.990 | 0.951 | 0.886 | 1 | 62 |
| log2_plus_one: log2(x + 1) | 0.998 | 0.976 | 0.934 | 0 | 12 |
| glog: log2((x + sqrt(x² + λ²)) / 2) | 0.997 | 0.989 | 0.918 | 0 | 9 |


The metabolites with the largest |skew| on the raw scale: `C10` +6.4 (rule +1.45), `C6..C4.1.DC.` +4.1 (rule +0.66), `C12` +3.5 (rule +0.13), `PC.aa.C42.6` +3.3 (rule +0.76), `C4` +3.2 (rule +0.86).

The metabolites with the largest |z| on the raw scale: `PC.aa.C42.6` 14.5 (rule 7.4), `C4` 14.1 (rule 7.0), `PC.ae.C40.3` 13.8 (rule 7.2), `C5` 13.4 (rule 4.8), `C10` 13.2 (rule 6.2).

The metabolites whose `log2(x + 1)` scaling agrees least with the rule's: `C6..C4.1.DC.` r 0.934 (median 0.0385), `C5` r 0.943 (median 0.108), `C14.2` r 0.946 (median 0.0383), `C12` r 0.958 (median 0.119), `Serotonin` r 0.959 (median 0.505).

The metabolites whose `glog` scaling agrees least with the rule's: `SM.C26.1` r 0.918 (floor / median 0.61), `PC.ae.C40.3` r 0.940 (floor / median 0.62), `PC.aa.C36.0` r 0.974 (floor / median 0.26), `PC.aa.C42.4` r 0.978 (floor / median 0.62), `PC.ae.C36.0` r 0.985 (floor / median 0.60).


### nmr (165 metabolites)

Shape (`_shape_counts`: pandas skew, largest |z| at the population sd) and non-finite cells:

| scale | abs_skew_gt_1 | skew_lt_minus_1 | median_abs_skew | max_abs_z_gt_5 | max_abs_z_gt_8 | max_abs_z_gt_15 | non_finite |
|---|---|---|---|---|---|---|---|
| rule: log2(x + floor) | 3 | 1 | 0.178 | 4 | 1 | 0 | 0 |
| raw_scale: x | 43 | 0 | 0.674 | 48 | 4 | 0 | 0 |
| log2_plus_one: log2(x + 1) | 30 | 0 | 0.513 | 30 | 4 | 0 | 0 |
| glog: log2((x + sqrt(x² + λ²)) / 2) | 25 | 23 | 0.248 | 35 | 13 | 0 | 0 |


Spectrum (`_spectrum`: the standardized block):

| scale | pc1_share | pc1_3_share | pc1_10_share | effective_rank | numerical_rank |
|---|---|---|---|---|---|
| rule: log2(x + floor) | 0.438 | 0.770 | 0.920 | 3.773 | 165 |
| raw_scale: x | 0.436 | 0.777 | 0.927 | 3.776 | 104 |
| log2_plus_one: log2(x + 1) | 0.437 | 0.777 | 0.926 | 3.766 | 165 |
| glog: log2((x + sqrt(x² + λ²)) / 2) | 0.433 | 0.753 | 0.903 | 3.902 | 165 |


Run offset (`_phase_offset`: ADNI1 minus ADNI2GO, pooled within-phase sd; PC correlations with phase):

| scale | median_abs_d | max_abs_d | abs_d_gt_0_5 | abs_d_gt_1 | abs_corr_pc1_phase | abs_corr_pc2_phase |
|---|---|---|---|---|---|---|
| rule: log2(x + floor) | 0.208 | 0.672 | 2 | 0 | 0.135 | 0.072 |
| raw_scale: x | 0.195 | 0.676 | 2 | 0 | 0.133 | 0.063 |
| log2_plus_one: log2(x + 1) | 0.197 | 0.676 | 2 | 0 | 0.133 | 0.065 |
| glog: log2((x + sqrt(x² + λ²)) / 2) | 0.207 | 0.665 | 2 | 0 | 0.132 | 0.077 |


Agreement with the rule's scale per metabolite (Pearson r of the two scalings of the same column):

| scale | median r | q05 | min | r < 0.9 | r < 0.99 |
|---|---|---|---|---|---|
| raw_scale: x | 0.994 | 0.883 | 0.580 | 12 | 64 |
| log2_plus_one: log2(x + 1) | 0.997 | 0.890 | 0.608 | 10 | 46 |
| glog: log2((x + sqrt(x² + λ²)) / 2) | 0.997 | 0.963 | 0.804 | 3 | 29 |


The metabolites with the largest |skew| on the raw scale: `GLUCOSE` +3.5 (rule +2.06), `ACETOACETATE` +3.3 (rule +0.51), `BOHBUTYRATE` +3.3 (rule +0.12), `ACETONE` +3.1 (rule +1.57), `XXL_VLDL_TG` +2.6 (rule -0.88).

The metabolites with the largest |z| on the raw scale: `ACETOACETATE` 13.2 (rule 4.2), `GLUCOSE` 12.7 (rule 9.2), `BOHBUTYRATE` 11.6 (rule 3.4), `ACETONE` 9.9 (rule 5.8), `ACETATE` 7.8 (rule 4.1).

The metabolites whose `log2(x + 1)` scaling agrees least with the rule's: `XXL_VLDL_TG` r 0.608 (median 0.0165), `XL_VLDL_PL` r 0.750 (median 0.0228), `XXL_VLDL_PL` r 0.751 (median 0.00657), `XXL_VLDL_P` r 0.806 (median 3.69e-07), `XXL_VLDL_FC` r 0.859 (median 0.00658).

The metabolites whose `glog` scaling agrees least with the rule's: `XL_HDL_PL` r 0.804 (floor / median 0.16), `L_VLDL_PL` r 0.832 (floor / median 0.18), `BOHBUTYRATE` r 0.855 (floor / median 0.14), `ACETOACETATE` r 0.918 (floor / median 0.28), `XL_VLDL_TG` r 0.925 (floor / median 0.10).


## The joint matrix per scale (p180 then NMR, as MOTCO concatenates them)

| scale | features | abs_skew_gt_1 | max_abs_z_gt_8 | pc1 share | pc1-10 share | effective rank | numerical rank | pc1 corr phase | pc2 corr phase |
|---|---|---|---|---|---|---|---|---|---|
| rule: log2(x + floor) | 298 | 4 | 1 | 0.316 | 0.789 | 6.654 | 298 | 0.415 | 0.148 |
| raw_scale: x | 298 | 89 | 16 | 0.313 | 0.784 | 6.778 | 237 | 0.404 | 0.148 |
| log2_plus_one: log2(x + 1) | 298 | 44 | 13 | 0.316 | 0.789 | 6.669 | 298 | 0.411 | 0.147 |
| glog: log2((x + sqrt(x² + λ²)) / 2) | 298 | 31 | 19 | 0.314 | 0.777 | 6.826 | 298 | 0.413 | 0.159 |


The spectrum and the phase correlations are of the standardized joint matrix (population sd), descriptive only: MOTCO's PLS-DA basis is supervised by stage and is not this PCA. MOTCO 0.10.0 z-scores every feature, so a scale changes the geometry through the spacing of each feature's values, not through its variance.


## Counts for the proposal

| variant | block | abs_skew_gt_1 | max_abs_z_gt_8 | phase abs_d_gt_0_5 | phase abs_d_gt_1 | non_finite | median < 1 | zero cells |
|---|---|---|---|---|---|---|---|---|
| `raw_scale` | p180 | 46 | 12 | 108 | 76 | 0 |  | 0 |
| `raw_scale` | nmr | 43 | 4 | 2 | 0 | 0 |  | 41 |
| `log2_plus_one` | p180 | 14 | 9 | 108 | 80 | 0 | 46 | 0 |
| `log2_plus_one` | nmr | 30 | 4 | 2 | 0 | 0 | 129 | 41 |
| `glog` | p180 | 6 | 6 | 109 | 80 | 0 |  | 0 |
| `glog` | nmr | 25 | 13 | 2 | 0 | 0 |  | 41 |

| quantity | value |
|---|---|
| joint features; p180 / NMR share | 298; 0.446 / 0.554 |
| rule's cells equal to the primary's, both blocks | yes |
| metabolites with no positive cell (λ undefined) | 0 |
