# MOTCO case-study report: ADNI serum metabolomics, sex × stage — 2026-10-29

Generated in full by `adni-sexdiff report` (changes `adni-report` and `adni-report-variants`) from the kept aggregate outputs of the pipeline: every number is copied from a record, a manifest or a CSV and formatted with the digits of the summary it belongs to, every reading sentence is the one `summary.md`, `latent_sensitivity.md` or `export_sensitivity.md` prints, and the reading rules are the constants, verbatim. The primary analysis stays primary in every table; the arm is read beside it under `READING_RULES` and `LATENT_SENSITIVITY_READING_RULES`, and each export variant under `READING_RULES` and `EXPORT_VARIANT_READING_RULES` (section 10). `adni-sexdiff report --check` compares this file with the outputs cell by cell. No value here is participant-level.

## Summary

The primary analysis (`results/motco_analysis`: one `motco.analysis.analyze_trajectories` call on the covariate-blind basis with the five covariates `age`, `education`, `apoe4`, `phase`, `statin`; MOTCO 0.10.0): n = 1501 in the sex × stage cells Female CN 237 / MCI 310 / AD 125; Male CN 223 / MCI 448 / AD 158; CV-selected PLS-DA rank 8 (`cv`; rank floor `ANALYSIS_RANK_FLOOR` = 2; pooled relative eigengap 0.74399); 9999 RRPP permutations, seed 20261027; α = 0.05, rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`). `delta` 1.10279 (p 0.1116, not rejected); `angle` 16.5406 (p 0.6879, not rejected); `shape` 0.107355 (p 0.7105, not rejected).

Reading, under `READING_RULES` (section 10):

- `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design.
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design).

The predeclared sensitivity arm `latent_stage` (`LATENT_SENSITIVITY_ARM`: `covariate_latent_adjustment` = `stage`, the same five covariates, every other setting the primary's; section 7) selected rank 4. Status per statistic (`same` when the rejection under `ANALYSIS_REJECTION_RULE` equals the primary's, else `differs (basis dependence)`; the primary's status is the result either way), read under `READING_RULES` and `LATENT_SENSITIVITY_READING_RULES`:

- `delta`: same (primary not rejected, latent_stage not rejected). Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, latent_stage not rejected). Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, latent_stage not rejected). Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

The predeclared export variants `nist_bridge`, `per_run_standardized` (`EXPORT_VARIANTS`, change `adni-nist-bridge`: each changes the p180 values only, every other export and analysis setting the primary's; section 8) selected ranks 6 (`nist_bridge`) and 4 (`per_run_standardized`). Status per statistic (`same` when the rejection under `ANALYSIS_REJECTION_RULE` equals the primary's, else `differs (run-handling dependence)`; the primary's status is the result either way), read under `READING_RULES` and `EXPORT_VARIANT_READING_RULES`:

`nist_bridge` (rank 6):

- `delta`: same (primary not rejected, nist_bridge not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, nist_bridge not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, nist_bridge not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

`per_run_standardized` (rank 4):

- `delta`: same (primary not rejected, per_run_standardized not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, per_run_standardized not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, per_run_standardized not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

Axis diagnostics (|rho| ≥ 0.3 flagged, a reporting threshold, not an adoption rule): in the primary, 5 latent-component rows flagged on the raw correlation and 1 on the partial, the flagged components `pls_0`, `pls_1`, `pls_3`, `pls_4` (section 6); in the arm, 3 and 1, the flagged components `pls_1`, `pls_2` (section 7); in `nist_bridge`, 1 and 1, the flagged components `pls_1`; in `per_run_standardized`, 2 and 1, the flagged components `pls_1`, `pls_3` (section 8). A flagged row is a measurement-space finding, never a change of a statistic.

## Provenance

This section is the report's manifest: what each step recorded, every input with its sha256, and the chain the step checked before writing. The hashes of participant-level files are the ones the manifests record; the report opened none of them.

### Versions per step

| step | python | adni-sexdiff | metabo_adni | motco | scikit-learn | numpy | scipy | pandas | statsmodels | pingouin | openpyxl |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean p180 | 3.12.15 | 0.1.0 | 0.5.8 | n/a | n/a | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| clean nmr | 3.12.15 | 0.1.0 | 0.5.8 | n/a | n/a | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| cohort | 3.12.15 | 0.1.0 | 0.5.8 | n/a | n/a | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| export | 3.12.15 | 0.1.0 | 0.5.8 | n/a | n/a | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| analyze | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| axis-diagnostics | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| latent-sensitivity (analysis) | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| latent-sensitivity (comparison) | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| axis-diagnostics (arm) | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| export-sensitivity nist_bridge (export) | 3.12.15 | 0.1.0 | 0.5.8 | n/a | n/a | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| export-sensitivity nist_bridge (analysis) | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| export-sensitivity nist_bridge (comparison) | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| axis-diagnostics (nist_bridge) | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| export-sensitivity per_run_standardized (export) | 3.12.15 | 0.1.0 | 0.5.8 | n/a | n/a | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| export-sensitivity per_run_standardized (analysis) | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| export-sensitivity per_run_standardized (comparison) | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |
| axis-diagnostics (per_run_standardized) | 3.12.15 | 0.1.0 | 0.5.8 | 0.10.0 | 1.8.0 | 2.4.6 | 1.18.1 | 2.3.3 | 0.15.0 | 0.5.4 | 3.1.5 |

### Revisions and numerics per step

| step | manifest | created at | commit | dirty | numerics | host | cpu |
|---|---|---|---|---|---|---|---|
| clean p180 | results/cleaned/p180/clean_manifest.json | 2026-10-26T21:49:16+00:00 | 13119c9c707bd4537f449194bb91b80c0f1f6e46 | false | no block (written before `adni-portable-numerics`) | n/a | n/a |
| clean nmr | results/cleaned/nmr/clean_manifest.json | 2026-10-26T21:49:18+00:00 | 13119c9c707bd4537f449194bb91b80c0f1f6e46 | false | no block (written before `adni-portable-numerics`) | n/a | n/a |
| cohort | results/cohort/cohort_manifest.json | 2026-10-26T22:43:46+00:00 | 1ab8f6a142301dfed8dd7038c7b8408cdc924558 | false | no block (written before `adni-portable-numerics`) | n/a | n/a |
| export | results/motco_input/manifest.json | 2026-10-27T14:13:06+00:00 | b10da517bed5919012610813aa8d7cdd778ce7bf | false | no block (written before `adni-portable-numerics`) | n/a | n/a |
| analyze | results/motco_analysis/analysis_manifest.json | 2026-10-27T18:14:42+00:00 | af4d6e4c85de4929766bcc52cf85b261968499f4 | false | no block (written before `adni-portable-numerics`) | n/a | n/a |
| axis-diagnostics | results/motco_diagnostics/diagnostics_manifest.json | 2026-10-28T16:30:34+00:00 | 35a1b62c65e4343bf5b879b8db44f155e6f0bcc5 | false | pinned | nixos-office | AMD Ryzen 9 7900X 12-Core Processor |
| latent-sensitivity (analysis) | results/motco_latent_sensitivity/analysis/analysis_manifest.json | 2026-10-28T17:32:59+00:00 | ed17ca94835d8949a0b88c7800a115b1e483b6bf | false | pinned | nixos-office | AMD Ryzen 9 7900X 12-Core Processor |
| latent-sensitivity (comparison) | results/motco_latent_sensitivity/comparison/latent_sensitivity_manifest.json | 2026-10-28T17:32:59+00:00 | ed17ca94835d8949a0b88c7800a115b1e483b6bf | false | pinned | nixos-office | AMD Ryzen 9 7900X 12-Core Processor |
| axis-diagnostics (arm) | results/motco_latent_sensitivity/diagnostics/diagnostics_manifest.json | 2026-10-28T17:33:00+00:00 | ed17ca94835d8949a0b88c7800a115b1e483b6bf | false | pinned | nixos-office | AMD Ryzen 9 7900X 12-Core Processor |
| export-sensitivity nist_bridge (export) | results/motco_export_sensitivity/nist_bridge/motco_input/manifest.json | 2026-10-29T13:58:59+00:00 | 94a004658a6fe0e895fb8df3b51bd573d6c2e1b1 | false | pinned | nixos-home | AMD Ryzen 7 5800X 8-Core Processor |
| export-sensitivity nist_bridge (analysis) | results/motco_export_sensitivity/nist_bridge/analysis/analysis_manifest.json | 2026-10-29T13:59:26+00:00 | 94a004658a6fe0e895fb8df3b51bd573d6c2e1b1 | false | pinned | nixos-home | AMD Ryzen 7 5800X 8-Core Processor |
| export-sensitivity nist_bridge (comparison) | results/motco_export_sensitivity/nist_bridge/comparison/export_sensitivity_manifest.json | 2026-10-29T13:59:26+00:00 | 94a004658a6fe0e895fb8df3b51bd573d6c2e1b1 | false | pinned | nixos-home | AMD Ryzen 7 5800X 8-Core Processor |
| axis-diagnostics (nist_bridge) | results/motco_export_sensitivity/nist_bridge/diagnostics/diagnostics_manifest.json | 2026-10-29T13:59:55+00:00 | 94a004658a6fe0e895fb8df3b51bd573d6c2e1b1 | false | pinned | nixos-home | AMD Ryzen 7 5800X 8-Core Processor |
| export-sensitivity per_run_standardized (export) | results/motco_export_sensitivity/per_run_standardized/motco_input/manifest.json | 2026-10-29T13:59:26+00:00 | 94a004658a6fe0e895fb8df3b51bd573d6c2e1b1 | false | pinned | nixos-home | AMD Ryzen 7 5800X 8-Core Processor |
| export-sensitivity per_run_standardized (analysis) | results/motco_export_sensitivity/per_run_standardized/analysis/analysis_manifest.json | 2026-10-29T13:59:53+00:00 | 94a004658a6fe0e895fb8df3b51bd573d6c2e1b1 | false | pinned | nixos-home | AMD Ryzen 7 5800X 8-Core Processor |
| export-sensitivity per_run_standardized (comparison) | results/motco_export_sensitivity/per_run_standardized/comparison/export_sensitivity_manifest.json | 2026-10-29T13:59:53+00:00 | 94a004658a6fe0e895fb8df3b51bd573d6c2e1b1 | false | pinned | nixos-home | AMD Ryzen 7 5800X 8-Core Processor |
| axis-diagnostics (per_run_standardized) | results/motco_export_sensitivity/per_run_standardized/diagnostics/diagnostics_manifest.json | 2026-10-29T13:59:56+00:00 | 94a004658a6fe0e895fb8df3b51bd573d6c2e1b1 | false | pinned | nixos-home | AMD Ryzen 7 5800X 8-Core Processor |

### Inputs

| file | sha256 | bytes | recorded in |
|---|---|---:|---|
| results/cleaned/p180/clean_manifest.json | 6f11a627648d17a5c1294420fd3ed32c1e125c8c0cb53b37d3f3d247fb5f78ce | 16096 | hashed for the chain (recorded by the manifests downstream) |
| results/cleaned/nmr/clean_manifest.json | 089df72cd5891029a791d1704578d5ef049efe9c25dd99cc41511e1ce64f7657 | 6234 | hashed for the chain (recorded by the manifests downstream) |
| results/cohort/stage_counts.csv | f6b73ea38d7955e511a010903cdcdb195b0062212ddc7317ca8ff3d4b9b0a948 | 1633 | cohort: outputs.stage_counts.csv.sha256 |
| results/cohort/cohort_manifest.json | dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630 | 15164 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_input/manifest.json | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | 14840 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_analysis/result.json | d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0 | 7818 | analyze: outputs.result.json.sha256 |
| results/motco_analysis/analysis_manifest.json | d09447600a477d19970fed803206af3ebd27fe237dcf359a9acba38bfdc4eed3 | 11512 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_analysis/summary.md | 082038e020857db4a20da8743989f0c80e3a0a995e7f8a3b6d0e11d30037ed19 | 5862 | analyze: outputs.summary.md.sha256 |
| results/motco_diagnostics/axis_correlations.csv | d0406d1964eadd9081f7ebccf414e51586cbd0a46bd0aedf953764e2c904afa5 | 6200 | axis-diagnostics: outputs.axis_correlations.csv.sha256 |
| results/motco_diagnostics/block_pcs.csv | 4998e90e387ad927c4fd5e711edbf442a62fe4a8387bc6bc661e9b6197620796 | 4879 | axis-diagnostics: outputs.block_pcs.csv.sha256 |
| results/motco_diagnostics/geometry_shares.csv | e7341dc12d34636525dbcd176a2ad076bdc4bc56eccbc3f62e2da1d86e86bb8e | 3157 | axis-diagnostics: outputs.geometry_shares.csv.sha256 |
| results/motco_diagnostics/components.csv | 0c8b5c8351bc661ac627a21039f9f0d55587958488f76878116801df00e9db13 | 847 | axis-diagnostics: outputs.components.csv.sha256 |
| results/motco_diagnostics/diagnostics.md | 87a135c09c8053196e8607b0785a8e583b241d7923d9def0ae46b657b8eb931a | 12968 | axis-diagnostics: outputs.diagnostics.md.sha256 |
| results/motco_diagnostics/diagnostics_manifest.json | cce4b8f2e9c07a4e53c95677ce531f78ca3e5951d5cb3a6e67b34a8f37243689 | 16845 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_latent_sensitivity/analysis/result.json | f24e0e7417af6faa8a54ea46cd275aba221c5c94a5c7978f4f583de0a9fb3f70 | 7725 | latent-sensitivity (analysis): outputs.result.json.sha256 |
| results/motco_latent_sensitivity/analysis/analysis_manifest.json | 75935b879433291cb3c19e42a871722ccd7c2e24f3702c98e1e785ca73f5f4cb | 15081 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_latent_sensitivity/analysis/summary.md | d128ca0f46672dd8dc941760ccc3fb75beb1d7e598c6c64972f63ee137d48b61 | 10351 | latent-sensitivity (analysis): outputs.summary.md.sha256 |
| results/motco_latent_sensitivity/comparison/latent_sensitivity.csv | a40e95550541d2c96a08266c865cc078fd0811f0bef15b77970edf4fbdea81e0 | 1310 | latent-sensitivity (comparison): outputs.latent_sensitivity.csv.sha256 |
| results/motco_latent_sensitivity/comparison/latent_sensitivity.md | 27de7c89576d5a323f81e0fad46ca6ea6a505b00a7c43fcca9432f0edc06b667 | 13925 | latent-sensitivity (comparison): outputs.latent_sensitivity.md.sha256 |
| results/motco_latent_sensitivity/comparison/latent_sensitivity_manifest.json | f547b8b700ab66d6f4f7f04915a3e48fa4495a2cf68284c345fb9a836ae5e92a | 16535 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_latent_sensitivity/diagnostics/axis_correlations.csv | 54a4102129624c52504816f952e95025d5a3242639a8ca8ab22ccb659b1df63b | 3153 | axis-diagnostics (arm): outputs.axis_correlations.csv.sha256 |
| results/motco_latent_sensitivity/diagnostics/block_pcs.csv | 4998e90e387ad927c4fd5e711edbf442a62fe4a8387bc6bc661e9b6197620796 | 4879 | axis-diagnostics (arm): outputs.block_pcs.csv.sha256 |
| results/motco_latent_sensitivity/diagnostics/geometry_shares.csv | 4e8afb28b633449390d0edcff4c215ddea1b923fff325859504377c78b6cf44c | 1592 | axis-diagnostics (arm): outputs.geometry_shares.csv.sha256 |
| results/motco_latent_sensitivity/diagnostics/components.csv | 5994f1ff615245728ce3ed2d7da8f3f617423fefdcb01019463c98dcfecfd4d7 | 479 | axis-diagnostics (arm): outputs.components.csv.sha256 |
| results/motco_latent_sensitivity/diagnostics/diagnostics.md | 96c2c3d45da4a33bc937f3a4c6c55c36a45452d9fbdd9fff0b38324cebeba8b7 | 14304 | axis-diagnostics (arm): outputs.diagnostics.md.sha256 |
| results/motco_latent_sensitivity/diagnostics/diagnostics_manifest.json | 3ec15736871d2e58879ac10387b9c74ea6af2c943de8802a104898b487eb29e1 | 15399 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_export_sensitivity/nist_bridge/bridge/nist_bridge.csv | bcfcf7460a6fb049f89cbe2f39b4c009d1214074fa7e4ab24a3b037b76b87fd3 | 24372 | export-sensitivity nist_bridge (export): bridge.table.sha256 |
| results/motco_export_sensitivity/nist_bridge/motco_input/manifest.json | c9be35f6c8f46c04e1334441c6fb8a1b043d1ac5eae827fb4e9515d79578e05c | 30416 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_export_sensitivity/nist_bridge/analysis/result.json | dbf60485b704c6d62e48fa00cdd48ac85d80ced14cd8e596fb823076b1504ee4 | 7381 | export-sensitivity nist_bridge (analysis): outputs.result.json.sha256 |
| results/motco_export_sensitivity/nist_bridge/analysis/analysis_manifest.json | 70b71d57e058beb47bf33e7b3566262393638ac92726eea2ca5732e5d867d5e9 | 14196 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_export_sensitivity/nist_bridge/analysis/summary.md | e0fac31255fcde2db362b327c29fb043d60bbbed33b9f14bc9b78f089cd83623 | 10874 | export-sensitivity nist_bridge (analysis): outputs.summary.md.sha256 |
| results/motco_export_sensitivity/nist_bridge/comparison/export_sensitivity.csv | 806293461dfa48260c69a6655e4ec54a2b443d231e454abf8e924cd198026db0 | 1054 | export-sensitivity nist_bridge (comparison): outputs.export_sensitivity.csv.sha256 |
| results/motco_export_sensitivity/nist_bridge/comparison/export_sensitivity.md | 10a06206fded07ccc9f218228a5ac21fee293a6b23b7f014d7ff301a8407bd13 | 11500 | export-sensitivity nist_bridge (comparison): outputs.export_sensitivity.md.sha256 |
| results/motco_export_sensitivity/nist_bridge/comparison/export_sensitivity_manifest.json | eca9a5bde409f3798123a245b71afe731030984bf4de838a4acf3c88eda408e6 | 19805 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_export_sensitivity/nist_bridge/diagnostics/axis_correlations.csv | e0ab5de0a3dbc29626653fa07042b08e75f9e1d51af8e02829a7d540bfeebba1 | 4681 | axis-diagnostics (nist_bridge): outputs.axis_correlations.csv.sha256 |
| results/motco_export_sensitivity/nist_bridge/diagnostics/block_pcs.csv | 3830ed4e964a31c9571cad586bc92137229578010131b5f566fc9687f60a701d | 4892 | axis-diagnostics (nist_bridge): outputs.block_pcs.csv.sha256 |
| results/motco_export_sensitivity/nist_bridge/diagnostics/geometry_shares.csv | e64b8502640735d2e0d1662d1293db75d778fa15aedaec637426833e7e33e88e | 2369 | axis-diagnostics (nist_bridge): outputs.geometry_shares.csv.sha256 |
| results/motco_export_sensitivity/nist_bridge/diagnostics/components.csv | e0e4aa6a643333e14588c0fbf18eb6bcf0b88d73606f8d634cec39f1db0c7f83 | 660 | axis-diagnostics (nist_bridge): outputs.components.csv.sha256 |
| results/motco_export_sensitivity/nist_bridge/diagnostics/diagnostics.md | 5fe6350b34ed69d2bf193f7a0aa95f546efee761743b9fa3114bf3c56fe77e6a | 14475 | axis-diagnostics (nist_bridge): outputs.diagnostics.md.sha256 |
| results/motco_export_sensitivity/nist_bridge/diagnostics/diagnostics_manifest.json | 9c4256d84d6d9c420c99667b6f66db208e4bc799c100b3afc079caac8aede8c8 | 16001 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_export_sensitivity/per_run_standardized/motco_input/manifest.json | 9827243de549660001fa3cf4b61d6b6d8fa2118b7af7cb1c15b3047c2fbd0f6e | 18766 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_export_sensitivity/per_run_standardized/analysis/result.json | 15250f6c93c5b94ee821dae1dad41c1497026f877b1b487cfce09137107a9a27 | 6909 | export-sensitivity per_run_standardized (analysis): outputs.result.json.sha256 |
| results/motco_export_sensitivity/per_run_standardized/analysis/analysis_manifest.json | bfbebaae8b50ee44bb9bb8c5104c17c769d0ffb28d6cfd1209b6d04918af8c31 | 14195 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_export_sensitivity/per_run_standardized/analysis/summary.md | 3aaf1bcead9dad1413e94621fd9e1e28100d9c63184c14a65d6448976eda44b9 | 10070 | export-sensitivity per_run_standardized (analysis): outputs.summary.md.sha256 |
| results/motco_export_sensitivity/per_run_standardized/comparison/export_sensitivity.csv | fd841cf7615ab814fdffca35f42454a4593774da26eddc656fe81d85634e2969 | 1068 | export-sensitivity per_run_standardized (comparison): outputs.export_sensitivity.csv.sha256 |
| results/motco_export_sensitivity/per_run_standardized/comparison/export_sensitivity.md | 2c3530a9a17571db1c7847bf512dd93b5eabe587fb58d203cf40144378b67d30 | 10777 | export-sensitivity per_run_standardized (comparison): outputs.export_sensitivity.md.sha256 |
| results/motco_export_sensitivity/per_run_standardized/comparison/export_sensitivity_manifest.json | b502d8275cb26e2aa265b5361c4f8503892759c958a086e6f258a3cbedad5eae | 14081 | hashed for the chain (recorded by the manifests downstream) |
| results/motco_export_sensitivity/per_run_standardized/diagnostics/axis_correlations.csv | 567c43b521428a5cf472e52cfe401a57f746eab73a1beac1d6d85d573f62e13c | 3146 | axis-diagnostics (per_run_standardized): outputs.axis_correlations.csv.sha256 |
| results/motco_export_sensitivity/per_run_standardized/diagnostics/block_pcs.csv | c0b52b10c7dc906673c2667cb65b9523cc333bb4171be2ed45b9c6c7e438119b | 4881 | axis-diagnostics (per_run_standardized): outputs.block_pcs.csv.sha256 |
| results/motco_export_sensitivity/per_run_standardized/diagnostics/geometry_shares.csv | 28a4445e7b4b34d8d48127dd9c435dce792abc98d6d644d710e70d7ad20a0375 | 1585 | axis-diagnostics (per_run_standardized): outputs.geometry_shares.csv.sha256 |
| results/motco_export_sensitivity/per_run_standardized/diagnostics/components.csv | bc2fece401f1ced180ecbf5df32714f8386517ed5544d290962de9885ed467e0 | 478 | axis-diagnostics (per_run_standardized): outputs.components.csv.sha256 |
| results/motco_export_sensitivity/per_run_standardized/diagnostics/diagnostics.md | dc7f5da5d26d0dd8d9aacaf855b338dc683329567a3bace1653ac690630fdf6d | 13513 | axis-diagnostics (per_run_standardized): outputs.diagnostics.md.sha256 |
| results/motco_export_sensitivity/per_run_standardized/diagnostics/diagnostics_manifest.json | ade5d0c12d0b8edad64f6d5ff6a2f52a83a600ddea5858159664af0c6ed65a51 | 15531 | hashed for the chain (recorded by the manifests downstream) |

### Raw LONI inputs

| file | sha256 | bytes | predeclared | repair | recorded in |
|---|---|---:|---|---|---|
| ADMCDUKEP180UPLC_01_15_16.csv | b99835be2d07460f5c1089fd72276454099d3ec7c14e662c740b496de0dad4fb | 317635 | true | none | clean p180 |
| ADMCDUKEP180FIA_01_15_16.csv | 0c765d0048f05fdc89f0eaa575b31f655fcefa2faf9fb0da92263836959f7290 | 957984 | true | none | clean p180 |
| ADMCDUKEP180UPLCADNI2GO.csv | 7ad17d63eed26368a3e51254c942e9c2f39890d43decda37f7b1a2ade38de3a6 | 459273 | true | repaired 2026-10-26: a double quote and a newline appended at the end of the archive copy (the last record's timestamp and metabolite values are complete) (defect: LONI's export lacks its final byte, the closing double quote of the last record's update_stamp field, so pandas' C parser fails with 'EOF inside string') | clean p180, cohort |
| ADMCDUKEP180FIAADNI2GO.csv | a414de4884d2ccd88a6519d3f5627155677ba5bf08be160191e316f5290459e9 | 1158894 | true | none | clean p180, cohort |
| 4097_UPLC_p180_Data.xlsx | 84648d2e896d23154d8483e7ec4bae87868562df80fb77cf85a4843d096698cb | 1321580 | true | none | clean p180 |
| 4097_FIA_p180_Data.xlsx | 57f0d41e992b2009ed595e2c76ebb0a3f2d1bd294f1ac8e9b6ca5f1e33fa1b45 | 4467097 | true | none | clean p180 |
| 4610 UPLC p180 Data.xlsx | f118ccc5c9112c413aeeb47c1f329afde3e858606bf64b68865f7c366d87eada | 714796 | true | none | clean p180 |
| 4610 FIA p180 Data.xlsx | ddbf46eda9aab32c2fe1d9251efdff7ce93701124d8281c4c7b4f3c18c60c617 | 2420391 | true | none | clean p180 |
| BIOMARK.csv | 0c7bc024fd3de367395c1edf7ab870bb7af37bc66dffaa11312d66570541671d | 4310571 | true | none | clean p180, clean nmr |
| ADNINIGHTINGALE2.csv | 524bde27672021fe8a9c4cc4b5d0d89a38f6f04129b930c955bd31e04c651ebf | 8660093 | true | none | clean nmr, cohort |
| ADNI_adnimerge_20170629_QT-freeze.csv | e3eae0464106f0a3df4eb23946e57f1f7fd5f8456eb60af6540654a36a16f7a2 | 8127476 | true | none | cohort |
| ADMCPATIENTDRUGCLASSES_20170512.csv | 2f0dd41dfb4c17f679818f19f8a5a41a2de81c30712863286a74e29fdd597343 | 5295787 | true | none | cohort |

The QC archives and the NIST SRM 1950 workbook members `export-sensitivity` read in place through the data root's top-level symlinks, as the variant export manifests record them (`inputs.qc`), each beside its predeclared sha256 (`RAW_INPUT_SHA256` for the archives, `NIST_BRIDGE_WORKBOOK_SHA256` for the members):

### QC archives and NIST workbooks

| file | location | run | kit | sha256 | bytes | predeclared sha256 | predeclared | recorded in |
|---|---|---|---|---|---:|---|---|---|
| ADMC_supplement.zip | data root, symlink to `Metabolomics/p180/ADMC_supplement.zip` | n/a | n/a | dc822b5683990f877f919af9ff521e0bbe5c12ca87a410b4a8bcff67f247544e | 4394499 | dc822b5683990f877f919af9ff521e0bbe5c12ca87a410b4a8bcff67f247544e | true | export-sensitivity nist_bridge (export) |
| ADMCDUKEP180SUPP_20170410.zip | data root, symlink to `Metabolomics/p180/ADMCDUKEP180SUPP_20170410.zip` | n/a | n/a | c3f9a0874af9ba74fb995da9d9f25dd95fdd6f4c0d0a43b3bff5455c90856332 | 3279354 | c3f9a0874af9ba74fb995da9d9f25dd95fdd6f4c0d0a43b3bff5455c90856332 | true | export-sensitivity nist_bridge (export) |
| admc_supplement/duke_raw_data/4097_FIA_NIST_and_QC_Data.xlsx | member of `ADMC_supplement.zip` | ADNI1 | FIA | b19419d272dc7d19cfa5bc86c65ef1af81a718dbd704175126278babfc9ea6a0 | 260956 | b19419d272dc7d19cfa5bc86c65ef1af81a718dbd704175126278babfc9ea6a0 | true | export-sensitivity nist_bridge (export) |
| admc_supplement/duke_raw_data/4097_UPLC_NIST_and_QC_Data.xlsx | member of `ADMC_supplement.zip` | ADNI1 | UPLC | 3b966a92cc3c3a1a6277adad4456fe9c9c42c0f495f8523ba4b446e3e16ed4d7 | 251801 | 3b966a92cc3c3a1a6277adad4456fe9c9c42c0f495f8523ba4b446e3e16ed4d7 | true | export-sensitivity nist_bridge (export) |
| 4610 FIA p180 QC and NIST Data.xlsx | member of `ADMCDUKEP180SUPP_20170410.zip` | ADNI2GO | FIA | f3873558779ae40202cc62207ddaf57cb6517a0adf3fff53901badda170acb93 | 86693 | f3873558779ae40202cc62207ddaf57cb6517a0adf3fff53901badda170acb93 | true | export-sensitivity nist_bridge (export) |
| 4610 UPLC p180 QC and NIST Data.xlsx | member of `ADMCDUKEP180SUPP_20170410.zip` | ADNI2GO | UPLC | 807575d5b5937e39ae32db0b6812ddff76758ce508155c9b1305795bfbdcb602 | 73711 | 807575d5b5937e39ae32db0b6812ddff76758ce508155c9b1305795bfbdcb602 | true | export-sensitivity nist_bridge (export) |

### Chain links checked

| link | upstream | sha256 | ok | rerun on failure |
|---|---|---|---|---|
| cohort: inputs.clean.p180.manifest.sha256 | sha256(results/cleaned/p180/clean_manifest.json) | 6f11a627648d17a5c1294420fd3ed32c1e125c8c0cb53b37d3f3d247fb5f78ce | yes | `adni-sexdiff cohort` |
| cohort: inputs.clean.nmr.manifest.sha256 | sha256(results/cleaned/nmr/clean_manifest.json) | 089df72cd5891029a791d1704578d5ef049efe9c25dd99cc41511e1ce64f7657 | yes | `adni-sexdiff cohort` |
| export: inputs.clean.p180.manifest.sha256 | sha256(results/cleaned/p180/clean_manifest.json) | 6f11a627648d17a5c1294420fd3ed32c1e125c8c0cb53b37d3f3d247fb5f78ce | yes | `adni-sexdiff export` |
| export: inputs.clean.nmr.manifest.sha256 | sha256(results/cleaned/nmr/clean_manifest.json) | 089df72cd5891029a791d1704578d5ef049efe9c25dd99cc41511e1ce64f7657 | yes | `adni-sexdiff export` |
| export: inputs.cohort.manifest.sha256 | sha256(results/cohort/cohort_manifest.json) | dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630 | yes | `adni-sexdiff export` |
| analyze: inputs.export_manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff analyze` |
| analyze: inputs.files.p180.csv.recorded | export: outputs.p180.csv.sha256 | 5547356eb1761705eeee2295cfe5838e302821594b5b2675630419123861402e | yes | `adni-sexdiff analyze` |
| analyze: inputs.files.nmr.csv.recorded | export: outputs.nmr.csv.sha256 | a90d3eb43a86db456861e53a413f73ce8c70ec4d121eaa56e258725493114e43 | yes | `adni-sexdiff analyze` |
| analyze: inputs.files.metadata.csv.recorded | export: outputs.metadata.csv.sha256 | 9c445b7de5a50ee14c0771f2ebf57416120e46f6daa3703e48ff90308cecf221 | yes | `adni-sexdiff analyze` |
| analyze: inputs.files.covariates.csv.recorded | export: outputs.covariates.csv.sha256 | 06999e827d4f6eb6987bfa9c63bb24f9dfd4c07dfac96ce0b55500e8cd3fccfd | yes | `adni-sexdiff analyze` |
| axis-diagnostics: inputs.analysis.analysis_manifest.sha256 | sha256(results/motco_analysis/analysis_manifest.json) | d09447600a477d19970fed803206af3ebd27fe237dcf359a9acba38bfdc4eed3 | yes | `adni-sexdiff axis-diagnostics` |
| axis-diagnostics: inputs.analysis.files.result.json.sha256 | analyze: outputs.result.json.sha256 | d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0 | yes | `adni-sexdiff axis-diagnostics` |
| axis-diagnostics: inputs.export.export_manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff axis-diagnostics` |
| axis-diagnostics: inputs.cohort.files.cohort_manifest.json.sha256 | sha256(results/cohort/cohort_manifest.json) | dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630 | yes | `adni-sexdiff axis-diagnostics` |
| latent-sensitivity (analysis): inputs.export_manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (analysis): inputs.files.p180.csv.recorded | export: outputs.p180.csv.sha256 | 5547356eb1761705eeee2295cfe5838e302821594b5b2675630419123861402e | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (analysis): inputs.files.nmr.csv.recorded | export: outputs.nmr.csv.sha256 | a90d3eb43a86db456861e53a413f73ce8c70ec4d121eaa56e258725493114e43 | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (analysis): inputs.files.metadata.csv.recorded | export: outputs.metadata.csv.sha256 | 9c445b7de5a50ee14c0771f2ebf57416120e46f6daa3703e48ff90308cecf221 | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (analysis): inputs.files.covariates.csv.recorded | export: outputs.covariates.csv.sha256 | 06999e827d4f6eb6987bfa9c63bb24f9dfd4c07dfac96ce0b55500e8cd3fccfd | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (analysis): reference.files.result.json.sha256 | sha256(results/motco_analysis/result.json) | d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0 | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (analysis): reference.files.analysis_manifest.json.sha256 | sha256(results/motco_analysis/analysis_manifest.json) | d09447600a477d19970fed803206af3ebd27fe237dcf359a9acba38bfdc4eed3 | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (comparison): reference.files.result.json.sha256 | sha256(results/motco_analysis/result.json) | d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0 | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (comparison): reference.files.analysis_manifest.json.sha256 | sha256(results/motco_analysis/analysis_manifest.json) | d09447600a477d19970fed803206af3ebd27fe237dcf359a9acba38bfdc4eed3 | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (comparison): arm.files.result.json.sha256 | sha256(results/motco_latent_sensitivity/analysis/result.json) | f24e0e7417af6faa8a54ea46cd275aba221c5c94a5c7978f4f583de0a9fb3f70 | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (comparison): arm.files.analysis_manifest.json.sha256 | sha256(results/motco_latent_sensitivity/analysis/analysis_manifest.json) | 75935b879433291cb3c19e42a871722ccd7c2e24f3702c98e1e785ca73f5f4cb | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (comparison): inputs.export.export_manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff latent-sensitivity` |
| latent-sensitivity (comparison): inputs.cohort.files.cohort_manifest.json.sha256 | sha256(results/cohort/cohort_manifest.json) | dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630 | yes | `adni-sexdiff latent-sensitivity` |
| axis-diagnostics (arm): inputs.analysis.analysis_manifest.sha256 | sha256(results/motco_latent_sensitivity/analysis/analysis_manifest.json) | 75935b879433291cb3c19e42a871722ccd7c2e24f3702c98e1e785ca73f5f4cb | yes | `adni-sexdiff axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics` |
| axis-diagnostics (arm): inputs.analysis.files.result.json.sha256 | latent-sensitivity (analysis): outputs.result.json.sha256 | f24e0e7417af6faa8a54ea46cd275aba221c5c94a5c7978f4f583de0a9fb3f70 | yes | `adni-sexdiff axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics` |
| axis-diagnostics (arm): inputs.export.export_manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics` |
| axis-diagnostics (arm): inputs.cohort.files.cohort_manifest.json.sha256 | sha256(results/cohort/cohort_manifest.json) | dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630 | yes | `adni-sexdiff axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics` |
| export-sensitivity nist_bridge (export): inputs.clean.p180.manifest.sha256 | sha256(results/cleaned/p180/clean_manifest.json) | 6f11a627648d17a5c1294420fd3ed32c1e125c8c0cb53b37d3f3d247fb5f78ce | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (export): inputs.clean.nmr.manifest.sha256 | sha256(results/cleaned/nmr/clean_manifest.json) | 089df72cd5891029a791d1704578d5ef049efe9c25dd99cc41511e1ce64f7657 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (export): inputs.cohort.manifest.sha256 | sha256(results/cohort/cohort_manifest.json) | dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (export): reference.manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (analysis): inputs.export_manifest.sha256 | sha256(results/motco_export_sensitivity/nist_bridge/motco_input/manifest.json) | c9be35f6c8f46c04e1334441c6fb8a1b043d1ac5eae827fb4e9515d79578e05c | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (analysis): inputs.files.p180.csv.recorded | export-sensitivity nist_bridge (export): outputs.p180.csv.sha256 | 5bce3cfc54d25922d32f4d2d0901951a25f005f1903ce0c877c3caa3e84cc383 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (analysis): inputs.files.nmr.csv.recorded | export-sensitivity nist_bridge (export): outputs.nmr.csv.sha256 | a90d3eb43a86db456861e53a413f73ce8c70ec4d121eaa56e258725493114e43 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (analysis): inputs.files.metadata.csv.recorded | export-sensitivity nist_bridge (export): outputs.metadata.csv.sha256 | 9c445b7de5a50ee14c0771f2ebf57416120e46f6daa3703e48ff90308cecf221 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (analysis): inputs.files.covariates.csv.recorded | export-sensitivity nist_bridge (export): outputs.covariates.csv.sha256 | 06999e827d4f6eb6987bfa9c63bb24f9dfd4c07dfac96ce0b55500e8cd3fccfd | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (analysis): reference.files.result.json.sha256 | sha256(results/motco_analysis/result.json) | d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (analysis): reference.files.analysis_manifest.json.sha256 | sha256(results/motco_analysis/analysis_manifest.json) | d09447600a477d19970fed803206af3ebd27fe237dcf359a9acba38bfdc4eed3 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (analysis): reference.export.manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (comparison): reference.files.result.json.sha256 | sha256(results/motco_analysis/result.json) | d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (comparison): reference.files.analysis_manifest.json.sha256 | sha256(results/motco_analysis/analysis_manifest.json) | d09447600a477d19970fed803206af3ebd27fe237dcf359a9acba38bfdc4eed3 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (comparison): inputs.variant.analysis.files.result.json.sha256 | sha256(results/motco_export_sensitivity/nist_bridge/analysis/result.json) | dbf60485b704c6d62e48fa00cdd48ac85d80ced14cd8e596fb823076b1504ee4 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (comparison): inputs.variant.analysis.files.analysis_manifest.json.sha256 | sha256(results/motco_export_sensitivity/nist_bridge/analysis/analysis_manifest.json) | 70b71d57e058beb47bf33e7b3566262393638ac92726eea2ca5732e5d867d5e9 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (comparison): inputs.variant.export.manifest.sha256 | sha256(results/motco_export_sensitivity/nist_bridge/motco_input/manifest.json) | c9be35f6c8f46c04e1334441c6fb8a1b043d1ac5eae827fb4e9515d79578e05c | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (comparison): inputs.primary.export.manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| export-sensitivity nist_bridge (comparison): inputs.variant.bridge.sha256 | sha256(results/motco_export_sensitivity/nist_bridge/bridge/nist_bridge.csv) | bcfcf7460a6fb049f89cbe2f39b4c009d1214074fa7e4ab24a3b037b76b87fd3 | yes | `adni-sexdiff export-sensitivity --variant nist_bridge --force`, then the variant's `axis-diagnostics` |
| axis-diagnostics (nist_bridge): inputs.analysis.analysis_manifest.sha256 | sha256(results/motco_export_sensitivity/nist_bridge/analysis/analysis_manifest.json) | 70b71d57e058beb47bf33e7b3566262393638ac92726eea2ca5732e5d867d5e9 | yes | `adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/nist_bridge/motco_input --analysis-dir results/motco_export_sensitivity/nist_bridge/analysis --out-dir results/motco_export_sensitivity/nist_bridge/diagnostics` |
| axis-diagnostics (nist_bridge): inputs.analysis.files.result.json.sha256 | export-sensitivity nist_bridge (analysis): outputs.result.json.sha256 | dbf60485b704c6d62e48fa00cdd48ac85d80ced14cd8e596fb823076b1504ee4 | yes | `adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/nist_bridge/motco_input --analysis-dir results/motco_export_sensitivity/nist_bridge/analysis --out-dir results/motco_export_sensitivity/nist_bridge/diagnostics` |
| axis-diagnostics (nist_bridge): inputs.export.export_manifest.sha256 | sha256(results/motco_export_sensitivity/nist_bridge/motco_input/manifest.json) | c9be35f6c8f46c04e1334441c6fb8a1b043d1ac5eae827fb4e9515d79578e05c | yes | `adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/nist_bridge/motco_input --analysis-dir results/motco_export_sensitivity/nist_bridge/analysis --out-dir results/motco_export_sensitivity/nist_bridge/diagnostics` |
| axis-diagnostics (nist_bridge): inputs.cohort.files.cohort_manifest.json.sha256 | sha256(results/cohort/cohort_manifest.json) | dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630 | yes | `adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/nist_bridge/motco_input --analysis-dir results/motco_export_sensitivity/nist_bridge/analysis --out-dir results/motco_export_sensitivity/nist_bridge/diagnostics` |
| export-sensitivity per_run_standardized (export): inputs.clean.p180.manifest.sha256 | sha256(results/cleaned/p180/clean_manifest.json) | 6f11a627648d17a5c1294420fd3ed32c1e125c8c0cb53b37d3f3d247fb5f78ce | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (export): inputs.clean.nmr.manifest.sha256 | sha256(results/cleaned/nmr/clean_manifest.json) | 089df72cd5891029a791d1704578d5ef049efe9c25dd99cc41511e1ce64f7657 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (export): inputs.cohort.manifest.sha256 | sha256(results/cohort/cohort_manifest.json) | dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (export): reference.manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (analysis): inputs.export_manifest.sha256 | sha256(results/motco_export_sensitivity/per_run_standardized/motco_input/manifest.json) | 9827243de549660001fa3cf4b61d6b6d8fa2118b7af7cb1c15b3047c2fbd0f6e | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (analysis): inputs.files.p180.csv.recorded | export-sensitivity per_run_standardized (export): outputs.p180.csv.sha256 | 6cb3a25dedd9029ca6421e37e01b7c1267c905a1e2e330321a7917bf83930182 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (analysis): inputs.files.nmr.csv.recorded | export-sensitivity per_run_standardized (export): outputs.nmr.csv.sha256 | a90d3eb43a86db456861e53a413f73ce8c70ec4d121eaa56e258725493114e43 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (analysis): inputs.files.metadata.csv.recorded | export-sensitivity per_run_standardized (export): outputs.metadata.csv.sha256 | 9c445b7de5a50ee14c0771f2ebf57416120e46f6daa3703e48ff90308cecf221 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (analysis): inputs.files.covariates.csv.recorded | export-sensitivity per_run_standardized (export): outputs.covariates.csv.sha256 | 06999e827d4f6eb6987bfa9c63bb24f9dfd4c07dfac96ce0b55500e8cd3fccfd | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (analysis): reference.files.result.json.sha256 | sha256(results/motco_analysis/result.json) | d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (analysis): reference.files.analysis_manifest.json.sha256 | sha256(results/motco_analysis/analysis_manifest.json) | d09447600a477d19970fed803206af3ebd27fe237dcf359a9acba38bfdc4eed3 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (analysis): reference.export.manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (comparison): reference.files.result.json.sha256 | sha256(results/motco_analysis/result.json) | d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (comparison): reference.files.analysis_manifest.json.sha256 | sha256(results/motco_analysis/analysis_manifest.json) | d09447600a477d19970fed803206af3ebd27fe237dcf359a9acba38bfdc4eed3 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (comparison): inputs.variant.analysis.files.result.json.sha256 | sha256(results/motco_export_sensitivity/per_run_standardized/analysis/result.json) | 15250f6c93c5b94ee821dae1dad41c1497026f877b1b487cfce09137107a9a27 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (comparison): inputs.variant.analysis.files.analysis_manifest.json.sha256 | sha256(results/motco_export_sensitivity/per_run_standardized/analysis/analysis_manifest.json) | bfbebaae8b50ee44bb9bb8c5104c17c769d0ffb28d6cfd1209b6d04918af8c31 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (comparison): inputs.variant.export.manifest.sha256 | sha256(results/motco_export_sensitivity/per_run_standardized/motco_input/manifest.json) | 9827243de549660001fa3cf4b61d6b6d8fa2118b7af7cb1c15b3047c2fbd0f6e | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| export-sensitivity per_run_standardized (comparison): inputs.primary.export.manifest.sha256 | sha256(results/motco_input/manifest.json) | 9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204 | yes | `adni-sexdiff export-sensitivity --variant per_run_standardized --force`, then the variant's `axis-diagnostics` |
| axis-diagnostics (per_run_standardized): inputs.analysis.analysis_manifest.sha256 | sha256(results/motco_export_sensitivity/per_run_standardized/analysis/analysis_manifest.json) | bfbebaae8b50ee44bb9bb8c5104c17c769d0ffb28d6cfd1209b6d04918af8c31 | yes | `adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/per_run_standardized/motco_input --analysis-dir results/motco_export_sensitivity/per_run_standardized/analysis --out-dir results/motco_export_sensitivity/per_run_standardized/diagnostics` |
| axis-diagnostics (per_run_standardized): inputs.analysis.files.result.json.sha256 | export-sensitivity per_run_standardized (analysis): outputs.result.json.sha256 | 15250f6c93c5b94ee821dae1dad41c1497026f877b1b487cfce09137107a9a27 | yes | `adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/per_run_standardized/motco_input --analysis-dir results/motco_export_sensitivity/per_run_standardized/analysis --out-dir results/motco_export_sensitivity/per_run_standardized/diagnostics` |
| axis-diagnostics (per_run_standardized): inputs.export.export_manifest.sha256 | sha256(results/motco_export_sensitivity/per_run_standardized/motco_input/manifest.json) | 9827243de549660001fa3cf4b61d6b6d8fa2118b7af7cb1c15b3047c2fbd0f6e | yes | `adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/per_run_standardized/motco_input --analysis-dir results/motco_export_sensitivity/per_run_standardized/analysis --out-dir results/motco_export_sensitivity/per_run_standardized/diagnostics` |
| axis-diagnostics (per_run_standardized): inputs.cohort.files.cohort_manifest.json.sha256 | sha256(results/cohort/cohort_manifest.json) | dcb65a530bfc41f3d77bec08ad530bc81dede9f90ac2b4580d88e2e156d1e630 | yes | `adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/per_run_standardized/motco_input --analysis-dir results/motco_export_sensitivity/per_run_standardized/analysis --out-dir results/motco_export_sensitivity/per_run_standardized/diagnostics` |

## Cohort

- `COHORT_RULE` as `results/cohort/cohort_manifest.json` records it: clinical table `ADNI_adnimerge_20170629_QT-freeze.csv`, one row per participant from its `bl` row; a cleaned participant enters a platform's set only if every raw record on that platform has visit `bl` (`ADMCDUKEP180FIAADNI2GO.csv` column `VISCODE`, `ADMCDUKEP180UPLCADNI2GO.csv` column `VISCODE`, `ADNINIGHTINGALE2.csv` column `VISCODE2`; runs without a visit column count as baseline: ADNI1) and it has a baseline row; the analysis cohort is the intersection of the sets of p180, nmr; no other exclusion.
- `STAGE_RULE`: `DX.bl` on the baseline row, AD → AD, CN → CN, EMCI → MCI, LMCI → MCI, SMC → CN.
- Stage source agreement (`DX` on the baseline row read as Dementia → AD, MCI → MCI, NL → CN; a recorded change 'X to Y' counts as Y; read for the agreement count only): agree 1498, differ 2, missing 1.
- Statin users in the intersection: 704; missing covariate values: 0; phase-against-run disagreements: 0.

### Cascade per platform set

| set | cleaned | excluded: sample not bl | excluded: no clinical bl row | set size | expected set size |
|---|---:|---:|---:|---:|---:|
| p180 | 1592 | 0 | 0 | 1592 | 1592 |
| nmr | 1504 | 1 | 0 | 1503 | 1503 |

### Intersection and union

| quantity | n | expected |
|---|---:|---:|
| cleaned on both platforms | 1502 | 1502 |
| intersection (the analysis cohort) | 1501 | 1501 |
| union (rows of cohort.csv) | 1594 | 1594 |
| union: both platforms | 1501 | 1501 |
| union: p180 only | 91 | 91 |
| union: nmr only | 2 | 2 |

### Sample visits of the cleaned participants

| platform set · visit | n |
|---|---:|
| p180 ADNI1 · no visit column | 746 |
| p180 ADNI2GO · bl | 846 |
| nmr bl | 1503 |
| nmr sc | 1 |

### Sex × stage: p180 set

| sex | CN | MCI | AD | all |
|---|---:|---:|---:|---:|
| Female | 254 | 329 | 140 | 723 |
| Male | 230 | 470 | 169 | 869 |
| all | 484 | 799 | 309 | 1592 |

### Sex × stage: nmr set

| sex | CN | MCI | AD | all |
|---|---:|---:|---:|---:|
| Female | 237 | 310 | 126 | 673 |
| Male | 223 | 449 | 158 | 830 |
| all | 460 | 759 | 284 | 1503 |

### Sex × stage: intersection

| sex | CN | MCI | AD | all |
|---|---:|---:|---:|---:|
| Female | 237 | 310 | 125 | 672 |
| Male | 223 | 448 | 158 | 829 |
| all | 460 | 758 | 283 | 1501 |

### Intersection: sex × stage × DX.bl × phase

| cell | sex | stage | DX.bl | phase | n |
|---|---|---|---|---|---:|
| Female CN CN ADNI1 | Female | CN | CN | ADNI1 | 94 |
| Female CN CN ADNI2GO | Female | CN | CN | ADNI2GO | 89 |
| Female CN SMC ADNI2GO | Female | CN | SMC | ADNI2GO | 54 |
| Female MCI EMCI ADNI2GO | Female | MCI | EMCI | ADNI2GO | 123 |
| Female MCI LMCI ADNI1 | Female | MCI | LMCI | ADNI1 | 117 |
| Female MCI LMCI ADNI2GO | Female | MCI | LMCI | ADNI2GO | 70 |
| Female AD AD ADNI1 | Female | AD | AD | ADNI1 | 72 |
| Female AD AD ADNI2GO | Female | AD | AD | ADNI2GO | 53 |
| Male CN CN ADNI1 | Male | CN | CN | ADNI1 | 98 |
| Male CN CN ADNI2GO | Male | CN | CN | ADNI2GO | 83 |
| Male CN SMC ADNI2GO | Male | CN | SMC | ADNI2GO | 42 |
| Male MCI EMCI ADNI2GO | Male | MCI | EMCI | ADNI2GO | 152 |
| Male MCI LMCI ADNI1 | Male | MCI | LMCI | ADNI1 | 221 |
| Male MCI LMCI ADNI2GO | Male | MCI | LMCI | ADNI2GO | 75 |
| Male AD AD ADNI1 | Male | AD | AD | ADNI1 | 82 |
| Male AD AD ADNI2GO | Male | AD | AD | ADNI2GO | 76 |

Per sex × stage cell of the analysis cohort, copied from `cohort_manifest.json` (`descriptives`, set `intersection`), not recomputed: n, age and education mean (sd), and counts per level of `apoe4` (0 / 1 / 2), `phase` (ADNI1 / ADNI2GO) and `statin` (0 / 1). The covariate roles of the arm (section 7) are read beside this table.

### Per-cell covariate descriptives

| cell | n | age mean (sd) | education mean (sd) | apoe4 0 / 1 / 2 | phase ADNI1 / ADNI2GO | statin 0 / 1 |
|---|---:|---:|---:|---:|---:|---:|
| Female CN | 237 | 73.47 (5.50884) | 15.7384 (2.70575) | 168 / 66 / 3 | 94 / 143 | 145 / 92 |
| Female MCI | 310 | 71.9277 (7.81451) | 15.4548 (2.74768) | 158 / 117 / 35 | 117 / 193 | 175 / 135 |
| Female AD | 125 | 73.5624 (7.88453) | 14.464 (2.72546) | 46 / 58 / 21 | 72 / 53 | 76 / 49 |
| Male CN | 223 | 74.8197 (5.99741) | 17.0897 (2.5874) | 163 / 53 / 7 | 98 / 125 | 113 / 110 |
| Male MCI | 448 | 73.9257 (7.39195) | 16.2299 (2.83132) | 222 / 178 / 48 | 221 / 227 | 213 / 235 |
| Male AD | 158 | 75.4392 (7.73803) | 15.7975 (3.06565) | 53 / 70 / 35 | 82 / 76 | 75 / 83 |

The `phase` covariate (ADNIMERGE `ORIGPROT`, ADNI-GO and ADNI-2 merged) against the p180 run of `p180_runs.csv`:

### Phase against the p180 run

| set | ADNI1 → ADNI1 | ADNI2GO → ADNI2GO | disagreements |
|---|---:|---:|---:|
| intersection | 684 | 817 | 0 |
| p180 | 746 | 846 | 0 |

Cleaning (`clean`, metabo_adni 0.5.8; `CLEAN_OPTIONS` as each `clean_manifest.json` records them):

### Cleaning options

| option | p180 | nmr |
|---|---|---|
| mmc | 0.2 | 0.2 |
| mpc | 0.2 | 0.2 |
| cv | 0.2 | n/a |
| icc | 0.65 | n/a |
| merge | true | true |
| log2 | false | false |
| zscore | false | false |
| winsorize | false | false |
| remove_moutliers | false | false |
| residualize_meds | false | false |

- `clean --platform p180` ran metabo_adni as `clean_files -D <work> -P p180 -F BIOMARK.csv -L <work> --mmc 0.2 --mpc 0.2 --cv 0.2 --icc 0.65 --merge`
- `clean --platform nmr` ran metabo_adni as `clean_files -D <work> -P nmr -F BIOMARK.csv --mmc 0.2 --mpc 0.2 --merge`

### Cleaning: p180 participants × metabolites per metabo_adni step

| metabo_adni step | ADNI1-UPLC | ADNI1-UPLC expected | ADNI1-FIA | ADNI1-FIA expected | ADNI2GO-UPLC | ADNI2GO-UPLC expected | ADNI2GO-FIA | ADNI2GO-FIA expected | P180 | P180 expected |
|---|---|---|---|---|---|---|---|---|---|---|
| read_files | 807 × 41 | 807 × 41 | 807 × 141 | 807 × 141 | 874 × 41 | 874 × 41 | 874 × 141 | 874 × 141 | n/a | n/a |
| remove_missing_metabolites | 807 × 32 | 807 × 32 | 807 × 117 | 807 × 117 | 874 × 32 | 874 × 32 | 874 × 126 | 874 × 126 | n/a | n/a |
| cross_plate_correction | 807 × 32 | 807 × 32 | 807 × 117 | 807 × 117 | 874 × 32 | 874 × 32 | 874 × 126 | 874 × 126 | n/a | n/a |
| remove_cv | 807 × 31 | 807 × 31 | 807 × 116 | 807 × 116 | 874 × 32 | 874 × 32 | 874 × 124 | 874 × 124 | n/a | n/a |
| remove_icc | 807 × 28 | 807 × 28 | 807 × 110 | 807 × 110 | 874 × 31 | 874 × 31 | 874 × 121 | 874 × 121 | n/a | n/a |
| remove_missing_participants | 807 × 28 | 807 × 28 | 806 × 110 | 806 × 110 | 874 × 31 | 874 × 31 | 874 × 121 | 874 × 121 | n/a | n/a |
| consolidate_replicates | 807 × 28 | 807 × 28 | 806 × 110 | 806 × 110 | 874 × 31 | 874 × 31 | 874 × 121 | 874 × 121 | n/a | n/a |
| remove_non_fasters | 747 × 28 | 747 × 28 | 746 × 110 | 746 × 110 | 846 × 31 | 846 × 31 | 846 × 121 | 846 × 121 | n/a | n/a |
| remove_bad_qc_tags | 747 × 27 | 747 × 27 | 746 × 110 | 746 × 110 | 846 × 31 | 846 × 31 | 846 × 120 | 846 × 120 | n/a | n/a |
| imputation | 747 × 27 | 747 × 27 | 746 × 110 | 746 × 110 | 846 × 31 | 846 × 31 | 846 × 120 | 846 × 120 | n/a | n/a |
| merge | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 1592 × 133 | 1592 × 133 |

### Cleaning: nmr participants × metabolites per metabo_adni step

| metabo_adni step | NMR | NMR expected |
|---|---|---|
| read_files | 1646 × 250 | 1646 × 250 |
| remove_missing_metabolites | 1646 × 245 | 1646 × 245 |
| remove_missing_participants | 1645 × 245 | 1645 × 245 |
| consolidate_replicates | 1645 × 245 | 1645 × 245 |
| remove_non_fasters | 1563 × 245 | 1563 × 245 |
| remove_bad_qc_tags | 1504 × 245 | 1504 × 245 |
| imputation | 1504 × 245 | 1504 × 245 |
| merge | 1504 × 245 | 1504 × 245 |

### Cleaning counts

| quantity | p180 | p180 expected | nmr | nmr expected |
|---|---:|---:|---:|---:|
| duplicated_participants | 0 | 0 | 0 | 0 |
| final.metabolites | 133 | 133 | 245 | 245 |
| final.participants | 1592 | 1592 | 1504 | 1504 |
| imputed_points.ADNI1-FIA | 730 | 730 | n/a | n/a |
| imputed_points.ADNI1-UPLC | 16 | 16 | n/a | n/a |
| imputed_points.ADNI2GO-FIA | 643 | 643 | n/a | n/a |
| imputed_points.ADNI2GO-UPLC | 262 | 262 | n/a | n/a |
| imputed_points.total | 1651 | 1651 | 155 | 155 |
| multi_plate_lod.metabolites | 34 | 34 | n/a | n/a |
| multi_plate_lod.points | 1608 | 1608 | n/a | n/a |
| runs.ADNI1 | 746 | 746 | n/a | n/a |
| runs.ADNI2GO | 846 | 846 | n/a | n/a |
| zeros.metabolites | 0 | 0 | 3 | 3 |
| zeros.values | 0 | 0 | 41 | 41 |
| imputed_points.NMR | n/a | n/a | 155 | 155 |
| non_baseline_records | n/a | n/a | 3 | 3 |

## Export

- `EXPORT_FEATURE_RULE` as `results/motco_input/manifest.json` records it: units `log2(x + floor)` (the floor of a metabolite its 0.05 quantile, `linear` interpolation, over the exported participants, computed without sex, stage or a covariate); MOTCO transform `identity`; derived marks excluded from the blocks: nmr: degree (equals `UNSATURATION`), percentage (endswith `_PCT`), ratio (contains `_BY_`), size (endswith `_SIZE`); p180: none. Nothing imputed, replaced, winsorized, removed or centred per run.
- Blocks in MOTCO order: p180, nmr; sample column `rid`, group `sex` (Female, Male), stage `stage` (CN → MCI → AD); covariate columns exported, not applied (`covariates_applied` false): `age`, `education`, `apoe4`, `phase`, `statin`.
- Participants 1501 (expected 1501); joint features 298; missing covariate values 0.

### Features per block

| block | cleaned | kept | derived percentage | derived ratio | derived degree | derived size | share of the joint features | expected kept |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| p180 | 133 | 133 | 0 | 0 | 0 | 0 | 0.446 | 133 |
| nmr | 245 | 165 | 72 | 4 | 1 | 3 | 0.554 | 165 |

The p180 run offset (`phase`, ADNI1 against ADNI2GO, on the rule's scale over the exported participants), recorded by `export` and not corrected: the runs differ in stage composition, so per-run centring would move stage signal between runs; `phase` enters the analysis as a covariate of the stage means.

### Run offset per block (phase)

| block | median \|d\| | max \|d\| | \|d\| > 0.5 | \|d\| > 1 | \|corr(PC1, phase)\| | \|corr(PC2, phase)\| | expected \|d\| > 1 | contrast |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| p180 | 1.12 | 2.88 | 109 | 80 | 0.73 | 0.40 | 80 | ADNI1 minus ADNI2GO, pooled within-phase sd |
| nmr | 0.21 | 0.67 | 2 | 0 | 0.13 | 0.07 | 0 | ADNI1 minus ADNI2GO, pooled within-phase sd |

### Cells per block

| quantity | p180 | p180 expected | nmr | nmr expected |
|---|---:|---:|---:|---:|
| zero cells | 0 | 0 | 41 | 41 |
| metabolites with zeros | 0 | 0 | 3 | 3 |
| floors not positive | 0 | 0 | 0 | 0 |
| non-finite cells | 0 | 0 | 0 | 0 |

### Exported participants per sex × stage

| sex | CN | MCI | AD |
|---|---:|---:|---:|
| Female | 237 | 310 | 125 |
| Male | 223 | 448 | 158 |

## Primary analysis

### Settings

| setting | value | note |
|---|---|---|
| `ANALYSIS_PERMUTATIONS` | 9999 | RRPP permutations; the p-value (1 + b) / (1 + B) is exact in size at any count |
| `ANALYSIS_SEED` | 20261027 | the RRPP seed (one stream per worker) |
| `ANALYSIS_ALPHA` | 0.05 | rejected when p <= alpha (`ANALYSIS_REJECTION_RULE`) |
| `ANALYSIS_RANK_FLOOR` | 2 | `min_components` 2, checked equal to MOTCO's default before any input is read |
| `ANALYSIS_LATENT_ADJUSTMENT` | none | the covariate-blind basis of MOTCO's validated path; the `stage`-conditioned arm is section 7 |
| `ANALYSIS_MISSING_COVARIATES` | error | nothing imputed; a missing value stops the step |
| `n_jobs` | 1 | reported runs use `REPORTED_N_JOBS` = 1 |
| entry point | `motco.analysis.analyze_trajectories` | one call; never assembled from `motco plsr` + `motco de` |
| group order | Female, Male | `sex` |
| stage order | CN → MCI → AD | `stage` |
| categorical covariates | `apoe4`, `phase`, `statin` | `ANALYSIS_CATEGORICAL_COVARIATES`; the others numeric |

MOTCO's other settings stay its defaults and are read back from the record; a moved default is a finding:

### MOTCO defaults used

| default | as run | stated by proposal |
|---|---|---|
| orientation_estimator | net_displacement | net_displacement |
| cv1_splits | 3 | 3 |
| cv2_splits | 4 | 4 |
| n_repeats | 5 | 5 |
| max_components | 20 | 20 |
| random_state | 1203 | 1203 |
| forced_components | n/a | n/a |
| attribution | false | n/a |

MOTCO 0.10.0; orientation `net_displacement`; 9999 RRPP permutations, seed 20261027; n_jobs 1; α = 0.05, rejected when p <= alpha.

### Statistics

| statistic | observed | p (RRPP) | rejected | null mean | null sd | null q95 | note |
|---|---:|---:|---|---:|---:|---:|---|
| delta | 1.10279 | 0.1116 | no | 0.553618 | 0.423602 | 1.37094 |  |
| angle | 16.5406 | 0.6879 | no | 20.9569 | 7.64839 | 35.4399 | degrees, endpoint stages CN and AD; CV-selected rank 8 (rank floor 2); pooled relative eigengap 0.74399 |
| shape | 0.107355 | 0.7105 | no | 0.164185 | 0.0869842 | 0.322799 |  |

Reading, under the rules of section 10:

- `delta` is not rejected: no evidence of a difference between the sexes' trajectories at this design.
- `angle` is not rejected: uninformative about orientation, not evidence that the sexes' directions agree (reading rule 3: no power statement exists at this design).
- `shape` is not rejected: uninformative about shape, not evidence that the sexes' trajectory shapes agree (reading rule 3: no power statement exists at this design).

### Cell sizes

| group | stage CN | stage MCI | stage AD |
|---|---:|---:|---:|
| Female | 237 | 310 | 125 |
| Male | 223 | 448 | 158 |

### Latent space

| quantity | value |
|---|---|
| PLS-DA rank (selection) | 8 (`cv`) |
| rank floor (`ANALYSIS_RANK_FLOOR`) | 2 |
| floor binding | no |
| cv_mean_auroc | 0.599514 |
| CV repeats completed / requested | 5 / 5 |
| pooled relative eigengap of the stage-mean configuration | 0.74399 |
| eigengap permutation null q05 / q50 / q95 | 0.537295 / 0.733669 / 0.855842 |
| CV settings | cv2_splits 4, cv1_splits 3, n_repeats 5, max_components 20, random_state 1203 |
| blocks | p180 (133 features, identity), nmr (165 features, identity); features z-scored by MOTCO (pooled per-feature scalers) |

- entered (in order, additively): `age` (numeric), `education` (numeric), `apoe4` (categorical), `phase` (categorical), `statin` (categorical)
- design columns: 6 (age, education, apoe4[1], apoe4[2], phase[ADNI2GO], statin[1])
- reference levels: `apoe4` 0, `phase` ADNI1, `statin` 0
- missing policy: `error`; dropped participants: 0
- LS-means evaluated at the reference row (`pooled_mean`); no sex × covariate or stage × covariate term

### Reference row

| design column | reference value |
|---|---:|
| age | 73.703 |
| education | 15.9274 |
| apoe4[1] | 0.361093 |
| apoe4[2] | 0.0992672 |
| phase[ADNI2GO] | 0.544304 |
| statin[1] | 0.469021 |

### Covariate levels

| level | n |
|---|---:|
| `apoe4` = 0 | 810 |
| `apoe4` = 1 | 542 |
| `apoe4` = 2 | 149 |
| `phase` = ADNI1 | 684 |
| `phase` = ADNI2GO | 817 |
| `statin` = 0 | 797 |
| `statin` = 1 | 704 |

The `motco analyze` command that reproduces the directory from its inputs (`cli_equivalent`; replace OUT_DIR with a new directory; paths are relative to the directory analyze ran in):

```
motco analyze --block p180=results/motco_input/p180.csv --block nmr=results/motco_input/nmr.csv --metadata results/motco_analysis/analysis_metadata.csv --sample-col rid --group-col sex --stage-col stage --stage-order CN,MCI,AD --group-order Female,Male --covariate age --covariate education --categorical-covariate apoe4 --categorical-covariate phase --categorical-covariate statin --missing-covariates error --permutations 9999 --seed 20261027 --n-jobs 1 --min-components 2 --out-dir OUT_DIR
```

## Axis diagnostics of the primary

`results/motco_diagnostics` (`axis-diagnostics` on `results/motco_analysis`, rank 8, n = 1501): Spearman correlations of every latent component with the 8 predeclared variables, the partial Spearman correlations given the 6 design columns of the record (age, education, apoe4[1], apoe4[2], phase[ADNI2GO], statin[1]), the same for the first 3 principal components of each z-scored block, and the block composition of each component. Nothing here chooses a variant or an arm; the statistics keep their recorded status.

### Variables (`DIAGNOSTIC_VARIABLES`)

| variable | source | derivation |
|---|---|---|
| `age` | covariates.csv | as exported (years) |
| `education` | covariates.csv | as exported (years) |
| `apoe4` | covariates.csv | APOE e4 allele count 0 / 1 / 2, read as ordinal |
| `phase` | covariates.csv | 1 for ADNI2GO, 0 for ADNI1 (the p180 run; the design column phase[ADNI2GO]) |
| `statin` | covariates.csv | 1 for a statin user at sc, 0 otherwise |
| `stage` | metadata.csv | ordinal CN 0, MCI 1, AD 2 |
| `male` | metadata.csv | 1 for Male, 0 for Female |
| `dx_bl` | cohort.csv | ordinal CN 0, SMC 1, EMCI 2, LMCI 3, AD 4 (ADNI's enrollment gradient) |

Rows with |rho| ≥ 0.3 (`DIAGNOSTIC_CORRELATION_THRESHOLD`, raw and partial separately) are flagged: a reporting threshold, not an adoption rule; no p-value is attached to any correlation. Flagged rows recorded: latent components 5 raw and 1 partial; block principal components 4 raw and 3 partial.

### Flagged latent components

| row | component | sd | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| pls_0 · phase | pls_0 | 7.334 | `phase` | covariates.csv | 1501 | 0.542 | n/a | raw |
| pls_3 · phase | pls_3 | 3.472 | `phase` | covariates.csv | 1501 | -0.535 | n/a | raw |
| pls_1 · male | pls_1 | 3.901 | `male` | metadata.csv | 1501 | -0.405 | -0.396 | raw+partial |
| pls_4 · statin | pls_4 | 2.54 | `statin` | covariates.csv | 1501 | -0.357 | n/a | raw |
| pls_4 · phase | pls_4 | 2.54 | `phase` | covariates.csv | 1501 | 0.324 | n/a | raw |

### Flagged block principal components

| row | block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---|---:|---|---|---:|---:|---:|---|
| p180 pc1 · phase | p180 | pc1 | 0.418 | `phase` | covariates.csv | 1501 | -0.757 | n/a | raw |
| p180 pc2 · phase | p180 | pc2 | 0.071 | `phase` | covariates.csv | 1501 | -0.400 | n/a | raw |
| p180 pc2 · male | p180 | pc2 | 0.071 | `male` | metadata.csv | 1501 | 0.390 | 0.391 | raw+partial |
| nmr pc2 · male | nmr | pc2 | 0.247 | `male` | metadata.csv | 1501 | -0.383 | -0.371 | raw+partial |
| p180 pc1 · male | p180 | pc1 | 0.418 | `male` | metadata.csv | 1501 | -0.190 | -0.347 | partial |

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

### Components

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 7.334 | 0.567 | 0.433 | 1 | 0 | `phase` | 0.542 |
| pls_1 | 3.901 | 0.635 | 0.365 | 1 | 1 | `male` | -0.405 |
| pls_2 | 5.566 | 0.599 | 0.401 | 0 | 0 | `male` | -0.219 |
| pls_3 | 3.472 | 0.739 | 0.261 | 1 | 0 | `phase` | -0.535 |
| pls_4 | 2.54 | 0.701 | 0.299 | 2 | 0 | `statin` | -0.357 |
| pls_5 | 2.944 | 0.558 | 0.442 | 0 | 0 | `male` | -0.253 |
| pls_6 | 1.906 | 0.685 | 0.315 | 0 | 0 | `phase` | 0.130 |
| pls_7 | 1.995 | 0.665 | 0.335 | 0 | 0 | `age` | 0.188 |

Per z-scored block: the variance share of each of its first principal components and its pc1 against `phase` (Spearman here; the export manifest's |Pearson| of the first left-singular vector against the ADNI1 indicator, `counts.phase_offset.<block>.abs_corr_pc1_phase`).

### Block principal components

| block | features | variance share pc1 | variance share pc2 | variance share pc3 | pc1 against phase: Spearman (here) | \|Pearson\| recorded by export |
|---|---:|---:|---:|---:|---:|---:|
| p180 | 133 | 0.418 | 0.071 | 0.060 | -0.757 | 0.734 |
| nmr | 165 | 0.438 | 0.247 | 0.085 | -0.130 | 0.135 |

The full tables are referenced by hash (section 2): `axis_correlations.csv` (64 rows), `block_pcs.csv` (48 rows), `geometry_shares.csv` (32 rows), `components.csv` (8 rows).

## Latent-adjustment sensitivity

The primary (`results/motco_analysis`, `result.json` sha256 `d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0`) beside its predeclared sensitivity arm `latent_stage` (`LATENT_SENSITIVITY_ARM`, change `adni-latent-sensitivity`: `covariate_latent_adjustment` = `stage`, the same five covariates, every other setting the primary's; `results/motco_latent_sensitivity/analysis`, `result.json` sha256 `f24e0e7417af6faa8a54ea46cd275aba221c5c94a5c7978f4f583de0a9fb3f70`), as `results/motco_latent_sensitivity/comparison/latent_sensitivity_manifest.json` records them. Every table in this section quotes the arm and is read under `READING_RULES` and `LATENT_SENSITIVITY_READING_RULES` (section 10): the primary row comes first and its status is the result; the arm never replaces it (arm rule 1), and a status that differs is basis dependence (arm rule 2).

### Statistics: primary and arm

| row | statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |
|---|---|---|---:|---:|---|---:|---:|---:|---|
| delta primary | delta | primary | 1.10279 | 0.1116 | no | 0.553618 | 0.423602 | 1.37094 | same |
| delta latent_stage | delta | latent_stage | 1.55786 | 0.0568 | no | 0.648911 | 0.496943 | 1.60501 | same |
| angle primary | angle | primary | 16.5406 | 0.6879 | no | 20.9569 | 7.64839 | 35.4399 | same |
| angle latent_stage | angle | latent_stage | 14.2407 | 0.7244 | no | 21.3608 | 10.5721 | 41.2466 | same |
| shape primary | shape | primary | 0.107355 | 0.7105 | no | 0.164185 | 0.0869842 | 0.322799 | same |
| shape latent_stage | shape | latent_stage | 0.179861 | 0.6402 | no | 0.241913 | 0.129156 | 0.475997 | same |

`angle` (degrees, endpoint stages CN and AD) is read beside each analysis' CV-selected rank, floor, eigengap and null summary (reading rule 2, arm rule 3): primary rank 8 (floor 2, pooled relative eigengap 0.74399); latent_stage rank 4 (floor 2, eigengap 0.878123); the ranks differ, which is reported, not ranked as better or worse (arm rule 3).

Status per statistic:

- `delta`: same (primary not rejected, latent_stage not rejected). Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, latent_stage not rejected). Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, latent_stage not rejected). Both are non-rejections; the arm's is weaker than the primary's (arm rule 5), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

### Latent space: primary and arm

| quantity | primary | latent_stage |
|---|---:|---:|
| PLS-DA rank (selection) | 8 (`cv`) | 4 (`cv`) |
| rank floor (`ANALYSIS_RANK_FLOOR`) | 2 | 2 |
| cv_mean_auroc | 0.599514 | 0.580311 |
| CV repeats completed | 5 | 5 |
| pooled relative eigengap | 0.74399 | 0.878123 |
| eigengap permutation null q05 / q50 / q95 | 0.537295 / 0.733669 / 0.855842 | 0.632903 / 0.875739 / 0.975946 |
| latent adjustment | none | `stage` |
| residual df | n/a | 1492 |
| smallest CV training df | n/a | 741 |

The two analyses share the export, the covariates and their design, the cells, the CV folds (stratified on the stage, as the primary's), the seed and the permutations; they differ only in the latent basis and the CV-selected rank (arm rule 2).

### Latent adjustment of the arm

- conditioning: `stage` (`covariate_latent_adjustment`, `LATENT_SENSITIVITY_ARM`): the basis is fitted on the pooled-standardized features with the covariates regressed out given the intercept and the stage indicators, per CV training set and on the full sample; the raw features are projected onto it; the trajectory model, LS-means and RRPP are the primary's
- covariates residualized (in order): `age`, `education`, `apoe4`, `phase`, `statin`
- residualization design columns: 8 (stage[1] = MCI, stage[2] = AD, age, education, apoe4[1], apoe4[2], phase[ADNI2GO], statin[1])
- samples 1501; residual df 1492 (n − 1 − 2 stage indicator(s) − 6 design column(s)); smallest CV training df 741
- feature scale: `pooled_standardized`
- feature R² of the covariates given the intercept and the stage indicators (the share of each feature's variance the residualization removed; arm rule 6): q05 / q25 / q50 / q75 / q95 0.015 / 0.034 / 0.116 / 0.258 / 0.486; mean 0.166; fraction above 0.5 0.047

Each covariate's relation to the stage effect (`LATENT_SENSITIVITY_COVARIATE_ROLES`, decided before any run; no statistic or threshold is computed for it and nothing changes because of it), read beside the per-cell descriptives of section 3. Residualizing a covariate that mediates the stage effect removes real stage signal, and no data can tell a confounder from a mediator (arm rule 7).

### Covariate roles

| covariate | role | variable | justification |
|---|---|---|---|
| `age` | pre-disease | age at baseline | precedes disease: it can confound the stage effect but cannot be downstream of it |
| `education` | pre-disease | years of schooling, completed before enrolment | precedes disease: it can confound the stage effect but cannot be downstream of it |
| `apoe4` | pre-disease | germline APOE e4 genotype (allele count) | precedes disease: it can confound the stage effect but cannot be downstream of it |
| `phase` | design | the assay run and enrolment protocol (p180 kits ADNI-1 against ADNI-GO/2) | tied to stage composition by design (SMC and EMCI exist only in ADNI-GO/2), not caused by stage |
| `statin` | mediator candidate | HMG-CoA reductase inhibitor use on the screening medication row | a treatment that may follow diagnosis: prescribing differs with cognitive status; it stays in the arm because the arm was predeclared with the five covariates, and the reading carries the limitation |

MOTCO's two latent-adjustment decisions, as the comparison manifest records them (measured at one design, n = 80, none at this one; the arm carries no Type I or power claim of its own, arm rule 8):

- `adopt_stage` (`../MOTCO/docs/reports/latent-adjustment-type-i-2026-10-20.md`): the `stage`-conditioned adjustment holds Type I at the validated design under conditions this change meets: the case study's own proposal justifies the covariate set (`LATENT_SENSITIVITY_COVARIATE_ROLES`), `group_stage` is not used, the record's `latent_adjustment` and `covariates` blocks are reported beside the results, no categorical level is rare enough to drop out of a CV training set, and the earlier binding statements stand; `angle` held the 0.0706 bound by 0.004 (0.067).
- `candidate_fails` (`../MOTCO/docs/reports/latent-adjustment-power-2026-10-20.md`): the adjustment loses `shape` power with a covariate-aligned nuisance axis (0.243 against 0.428) and small-magnitude `delta` power without one (0.400 against 0.520 at e = 0.1), so it is a sensitivity read beside the covariate-blind primary, never a replacement of it.

Axis diagnostics of the arm (`results/motco_latent_sensitivity/diagnostics`, rank 4, `is_primary` false): a component of the arm that tracks a variable here is a measurement-space finding about the arm; it never reinterprets either analysis' statistics and is never grounds to adopt the arm (arm rule 9).

Rows with |rho| ≥ 0.3 (`DIAGNOSTIC_CORRELATION_THRESHOLD`, raw and partial separately) are flagged: a reporting threshold, not an adoption rule; no p-value is attached to any correlation. Flagged rows recorded: latent components 3 raw and 1 partial; block principal components 4 raw and 3 partial.

### Arm: Flagged latent components

| row | component | sd | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| pls_1 · male | pls_1 | 3.583 | `male` | metadata.csv | 1501 | -0.477 | -0.458 | raw+partial |
| pls_2 · phase | pls_2 | 6.797 | `phase` | covariates.csv | 1501 | 0.416 | n/a | raw |
| pls_2 · statin | pls_2 | 6.797 | `statin` | covariates.csv | 1501 | 0.334 | n/a | raw |

### Arm: Flagged block principal components

| row | block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---|---:|---|---|---:|---:|---:|---|
| p180 pc1 · phase | p180 | pc1 | 0.418 | `phase` | covariates.csv | 1501 | -0.757 | n/a | raw |
| p180 pc2 · phase | p180 | pc2 | 0.071 | `phase` | covariates.csv | 1501 | -0.400 | n/a | raw |
| p180 pc2 · male | p180 | pc2 | 0.071 | `male` | metadata.csv | 1501 | 0.390 | 0.391 | raw+partial |
| nmr pc2 · male | nmr | pc2 | 0.247 | `male` | metadata.csv | 1501 | -0.383 | -0.371 | raw+partial |
| p180 pc1 · male | p180 | pc1 | 0.418 | `male` | metadata.csv | 1501 | -0.190 | -0.347 | partial |

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

### Arm: Components

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 6.298 | 0.254 | 0.746 | 0 | 0 | `phase` | 0.241 |
| pls_1 | 3.583 | 0.573 | 0.427 | 1 | 1 | `male` | -0.477 |
| pls_2 | 6.797 | 0.676 | 0.324 | 2 | 0 | `phase` | 0.416 |
| pls_3 | 2.453 | 0.768 | 0.232 | 0 | 0 | `statin` | -0.185 |

Per z-scored block: the variance share of each of its first principal components and its pc1 against `phase` (Spearman here; the export manifest's |Pearson| of the first left-singular vector against the ADNI1 indicator, `counts.phase_offset.<block>.abs_corr_pc1_phase`).

### Arm: Block principal components

| block | features | variance share pc1 | variance share pc2 | variance share pc3 | pc1 against phase: Spearman (here) | \|Pearson\| recorded by export |
|---|---:|---:|---:|---:|---:|---:|
| p180 | 133 | 0.418 | 0.071 | 0.060 | -0.757 | 0.734 |
| nmr | 165 | 0.438 | 0.247 | 0.085 | -0.130 | 0.135 |

The full tables are referenced by hash (section 2): `axis_correlations.csv` (32 rows), `block_pcs.csv` (48 rows), `geometry_shares.csv` (16 rows), `components.csv` (4 rows).

### First component against phase

| analysis | component | sd | rho with phase | rho \| design | flag |
|---|---|---:|---:|---:|---|
| primary | pls_0 | 7.334 | 0.542 | n/a | raw |
| latent_stage | pls_0 | 6.298 | 0.241 | n/a | none |

The `motco analyze` command that reproduces the arm's directory (`cli_equivalent`; replace OUT_DIR with a new directory; paths are relative to the directory analyze ran in):

```
motco analyze --block p180=results/motco_input/p180.csv --block nmr=results/motco_input/nmr.csv --metadata results/motco_latent_sensitivity/analysis/analysis_metadata.csv --sample-col rid --group-col sex --stage-col stage --stage-order CN,MCI,AD --group-order Female,Male --covariate age --covariate education --categorical-covariate apoe4 --categorical-covariate phase --categorical-covariate statin --missing-covariates error --latent-adjustment stage --permutations 9999 --seed 20261027 --n-jobs 1 --min-components 2 --out-dir OUT_DIR
```

## Export sensitivity

The primary (`results/motco_analysis`, `result.json` sha256 `d4a5cbf90dda74763dea91b9f9be8df47439da0e5fd4c475a8546fe2a6f581f0`) beside its predeclared export variants (`EXPORT_VARIANTS`): `nist_bridge` (change `adni-nist-bridge`: every cleaned p180 concentration of a participant whose run in p180_runs.csv is ADNI2GO multiplied by 2^b of its metabolite under NIST_BRIDGE_RULE before the floors; EXPORT_FEATURE_RULE then unchanged, its floors recomputed over the exported participants; `results/motco_export_sensitivity/nist_bridge`); `per_run_standardized` (change `adni-nist-bridge`: the p180 values on the scale of EXPORT_FEATURE_RULE (pooled floors, log2(x + floor)), each metabolite centred and divided by its population SD within its run of p180_runs.csv; `results/motco_export_sensitivity/per_run_standardized`). Every other export and analysis setting is the primary's. Every table in this section quotes a variant and is read under `READING_RULES` and `EXPORT_VARIANT_READING_RULES` (section 10): the primary row comes first and its status is the result; a variant never replaces it (variant rule 1), and a status that differs is run-handling dependence (variant rule 2).

### Statistics: primary and variants

| row | statistic | analysis | observed | p (RRPP) | rejected | null mean | null sd | null q95 | status |
|---|---|---|---:|---:|---|---:|---:|---:|---|
| delta primary | delta | primary | 1.10279 | 0.1116 | no | 0.553618 | 0.423602 | 1.37094 | the result |
| delta nist_bridge | delta | nist_bridge | 1.08274 | 0.1366 | no | 0.578207 | 0.440758 | 1.42918 | same |
| delta per_run_standardized | delta | per_run_standardized | 1.56843 | 0.0526 | no | 0.643575 | 0.483599 | 1.58117 | same |
| angle primary | angle | primary | 16.5406 | 0.6879 | no | 20.9569 | 7.64839 | 35.4399 | the result |
| angle nist_bridge | angle | nist_bridge | 13.6961 | 0.7569 | no | 19.7572 | 8.11592 | 35.0172 | same |
| angle per_run_standardized | angle | per_run_standardized | 11.7506 | 0.718 | no | 17.1938 | 8.26608 | 32.7672 | same |
| shape primary | shape | primary | 0.107355 | 0.7105 | no | 0.164185 | 0.0869842 | 0.322799 | the result |
| shape nist_bridge | shape | nist_bridge | 0.0619491 | 0.9048 | no | 0.177528 | 0.0949426 | 0.352329 | same |
| shape per_run_standardized | shape | per_run_standardized | 0.137403 | 0.6978 | no | 0.204485 | 0.108356 | 0.404777 | same |

`angle` (degrees, endpoint stages CN and AD) is read beside each analysis' CV-selected rank, floor, eigengap and null summary (reading rule 2, variant rule 3): primary rank 8 (floor 2, pooled relative eigengap 0.74399); nist_bridge rank 6 (floor 2, eigengap 0.795928); the ranks differ, which is reported, not ranked (variant rule 3).

`angle` (degrees, endpoint stages CN and AD) is read beside each analysis' CV-selected rank, floor, eigengap and null summary (reading rule 2, variant rule 3): primary rank 8 (floor 2, pooled relative eigengap 0.74399); per_run_standardized rank 4 (floor 2, eigengap 0.90948); the ranks differ, which is reported, not ranked (variant rule 3).

### Status per statistic: `nist_bridge`

- `delta`: same (primary not rejected, nist_bridge not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, nist_bridge not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, nist_bridge not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

### Status per statistic: `per_run_standardized`

- `delta`: same (primary not rejected, per_run_standardized not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree (no power statement exists at this design).
- `angle`: same (primary not rejected, per_run_standardized not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).
- `shape`: same (primary not rejected, per_run_standardized not rejected). Both are non-rejections; the variant's is no more informative than the primary's (variant rule 6), and neither is evidence that the sexes' trajectories agree in this respect (reading rule 3: no power statement exists at this design).

### Latent space: primary and variants

| quantity | primary | nist_bridge | per_run_standardized |
|---|---:|---:|---:|
| PLS-DA rank (selection) | 8 (`cv`) | 6 (`cv`) | 4 (`cv`) |
| rank floor (`ANALYSIS_RANK_FLOOR`) | 2 | 2 | 2 |
| cv_mean_auroc | 0.599514 | 0.598348 | 0.599812 |
| CV repeats completed | 5 | 5 | 5 |
| pooled relative eigengap | 0.74399 | 0.795928 | 0.90948 |
| eigengap permutation null q05 / q50 / q95 | 0.537295 / 0.733669 / 0.855842 | 0.590906 / 0.784286 / 0.892094 | 0.725679 / 0.908248 / 0.985986 |

Each variant shares with the primary the cleaned tables, the participants, the NMR block, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations; it differs only in the p180 values (variant rule 2).

The run offset per block (`phase`, ADNI1 against ADNI2GO, on each export's scale over the exported participants), as the primary export manifest and each variant export manifest record it (`counts.phase_offset`), beside the predeclared counts (`EXPORT_EXPECTED_COUNTS`, `EXPORT_VARIANT_EXPECTED_COUNTS`; `n/a` where none is predeclared):

### Run offset per export

| row | block | export | median \|d\| | max \|d\| | \|d\| > 0.5 | \|d\| > 1 | \|corr(PC1, phase)\| | \|corr(PC2, phase)\| | expected \|d\| > 0.5 | expected \|d\| > 1 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| p180 primary | p180 | primary | 1.12 | 2.88 | 109 | 80 | 0.73 | 0.40 | n/a | 80 |
| p180 nist_bridge | p180 | nist_bridge | 0.29 | 2.88 | 35 | 8 | 0.22 | 0.58 | 35 | 8 |
| p180 per_run_standardized | p180 | per_run_standardized | 0.00 | 0.00 | 0 | 0 | 0.00 | 0.00 | 0 | 0 |
| nmr primary | nmr | primary | 0.21 | 0.67 | 2 | 0 | 0.13 | 0.07 | n/a | 0 |
| nmr nist_bridge | nmr | nist_bridge | 0.21 | 0.67 | 2 | 0 | 0.13 | 0.07 | n/a | 0 |
| nmr per_run_standardized | nmr | per_run_standardized | 0.21 | 0.67 | 2 | 0 | 0.13 | 0.07 | n/a | 0 |

Each variant export's counts beside its predeclared ones (`EXPORT_VARIANT_EXPECTED_COUNTS`, every key but the run offset above and the analysis', which `export-sensitivity` compares itself; a deviation is copied under section 9), as its export manifest records them (`counts`, `expected`):

### Variant exports against the predeclared counts

| quantity | nist_bridge | nist_bridge expected | per_run_standardized | per_run_standardized expected |
|---|---:|---:|---:|---:|
| participants | 1501 | 1501 | 1501 | 1501 |
| sex_stage.Female.CN | 237 | 237 | 237 | 237 |
| sex_stage.Female.MCI | 310 | 310 | 310 | 310 |
| sex_stage.Female.AD | 125 | 125 | 125 | 125 |
| sex_stage.Male.CN | 223 | 223 | 223 | 223 |
| sex_stage.Male.MCI | 448 | 448 | 448 | 448 |
| sex_stage.Male.AD | 158 | 158 | 158 | 158 |
| features.p180.cleaned | 133 | 133 | 133 | 133 |
| features.p180.kept | 133 | 133 | 133 | 133 |
| features.p180.derived.percentage | 0 | 0 | 0 | 0 |
| features.p180.derived.ratio | 0 | 0 | 0 | 0 |
| features.p180.derived.degree | 0 | 0 | 0 | 0 |
| features.p180.derived.size | 0 | 0 | 0 | 0 |
| features.nmr.cleaned | 245 | 245 | 245 | 245 |
| features.nmr.kept | 165 | 165 | 165 | 165 |
| features.nmr.derived.percentage | 72 | 72 | 72 | 72 |
| features.nmr.derived.ratio | 4 | 4 | 4 | 4 |
| features.nmr.derived.degree | 1 | 1 | 1 | 1 |
| features.nmr.derived.size | 3 | 3 | 3 | 3 |
| zero_cells.p180 | 0 | 0 | 0 | 0 |
| zero_cells.nmr | 41 | 41 | 41 | 41 |
| metabolites_with_zeros.p180 | 0 | 0 | 0 | 0 |
| metabolites_with_zeros.nmr | 3 | 3 | 3 | 3 |
| floors_not_positive.p180 | 0 | 0 | 0 | 0 |
| floors_not_positive.nmr | 0 | 0 | 0 | 0 |
| non_finite.p180 | 0 | 0 | 0 | 0 |
| non_finite.nmr | 0 | 0 | 0 | 0 |
| missing_covariate_values | 0 | 0 | 0 | 0 |
| p180_bridged.FIA | 102 | 102 | n/a | n/a |
| p180_bridged.UPLC | 24 | 24 | n/a | n/a |
| p180_bridged.not_bridged | 7 | 7 | n/a | n/a |
| p180_unmatched | 0 | 0 | n/a | n/a |
| runs_differing_from_phase | 0 | 0 | 0 | 0 |
| unchanged_equal_primary.metadata.csv | true | true | true | true |
| unchanged_equal_primary.covariates.csv | true | true | true | true |
| unchanged_equal_primary.nmr.csv | true | true | true | true |

### Export variant `nist_bridge`

- variant: `nist_bridge` (`EXPORT_VARIANTS`, change `adni-nist-bridge`): every cleaned p180 concentration of a participant whose run in p180_runs.csv is ADNI2GO multiplied by 2^b of its metabolite under NIST_BRIDGE_RULE before the floors; EXPORT_FEATURE_RULE then unchanged, its floors recomputed over the exported participants
- read beside the primary export `results/motco_input` (`manifest.json` sha256 `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204`); the participants, the NMR block, the metadata and the covariates are the primary's
- assay run of the exported participants (`p180_runs.csv`): ADNI1 684, ADNI2GO 817; 0 differ from `phase`
- NIST SRM 1950 bridge (`NIST_BRIDGE_RULE`): 133 p180 metabolite(s), bridged FIA 102, UPLC 24, not bridged 7 (factor 1: `C0`, `C10.2`, `C12`, `C14.1.OH`, `C6..C4.1.DC.`, `Serotonin`, `Spermidine`); no NIST column: none
- log2 factor b over the bridged metabolites (ADNI1 minus ADNI2GO; ADNI2GO concentrations multiplied by 2^b): q05 / q25 / q50 / q75 / q95 -0.109 / +0.110 / +0.311 / +0.401 / +0.603; median |b| 0.321; b > 0 for 108
- bridge table `bridge/nist_bridge.csv` (sha256 `bcfcf7460a6fb049f89cbe2f39b4c009d1214074fa7e4ab24a3b037b76b87fd3`): per metabolite the replicates, valid replicates, ISTD flags, run means and plate-clustered SEs, b and whether it is bridged
- p180 run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40; variant median |d| 0.29, |d| > 0.5 for 35 and > 1 for 8 metabolite(s), |corr(PC1, phase)| 0.22, |corr(PC2, phase)| 0.58
- nmr run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07; variant median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07

### nist_bridge: NIST bridge per kit

| kit | metabolites | expected |
|---|---:|---:|
| FIA | 102 | 102 |
| UPLC | 24 | 24 |
| not bridged | 7 | 7 |

### nist_bridge: Unbridged metabolites

| metabolite | kit | NIST column | replicates ADNI1 | valid ADNI1 | ISTD flags ADNI1 | replicates ADNI2GO | valid ADNI2GO | ISTD flags ADNI2GO | b |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `C0` | FIA | C0 | 33 | 33 | 0 | 24 | 7 | 17 | -0.147 |
| `C10.2` | FIA | C10:2 | 33 | 14 | 0 | 24 | 19 | 0 | +0.004 |
| `C12` | FIA | C12 | 33 | 4 | 0 | 24 | 7 | 0 | +0.390 |
| `C14.1.OH` | FIA | C14:1-OH | 33 | 3 | 0 | 24 | 16 | 0 | +0.075 |
| `C6..C4.1.DC.` | FIA | C6 (C4:1-DC) | 33 | 11 | 0 | 24 | 24 | 0 | +0.011 |
| `Serotonin` | UPLC | Serotonin | 33 | 23 | 0 | 24 | 10 | 0 | +0.095 |
| `Spermidine` | UPLC | Spermidine | 33 | 21 | 0 | 24 | 1 | 0 | +0.078 |

Each unbridged metabolite keeps factor 1 (`NIST_BRIDGE_RULE`: bridged when at least 0.5 of its replicates are valid in each run). The full table `bridge/nist_bridge.csv` (sha256 `bcfcf7460a6fb049f89cbe2f39b4c009d1214074fa7e4ab24a3b037b76b87fd3`, 133 rows) is referenced by hash (section 2); the factor of every metabolite is in the variant export manifest (`bridge.factors_log2`).

### Export variant `per_run_standardized`

- variant: `per_run_standardized` (`EXPORT_VARIANTS`, change `adni-nist-bridge`): the p180 values on the scale of EXPORT_FEATURE_RULE (pooled floors, log2(x + floor)), each metabolite centred and divided by its population SD within its run of p180_runs.csv
- read beside the primary export `results/motco_input` (`manifest.json` sha256 `9f4adf8cbc1da0b4cacdfe6673479991b40676033c365bc1433cc382f67d7204`); the participants, the NMR block, the metadata and the covariates are the primary's
- assay run of the exported participants (`p180_runs.csv`): ADNI1 684, ADNI2GO 817; 0 differ from `phase`
- p180 run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 1.12, |d| > 0.5 for 109 and > 1 for 80 metabolite(s), |corr(PC1, phase)| 0.73, |corr(PC2, phase)| 0.40; variant median |d| 0.00, |d| > 0.5 for 0 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.00, |corr(PC2, phase)| 0.00
- nmr run offset (`phase`, ADNI1 against ADNI2GO): primary median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07; variant median |d| 0.21, |d| > 0.5 for 2 and > 1 for 0 metabolite(s), |corr(PC1, phase)| 0.13, |corr(PC2, phase)| 0.07

Axis diagnostics of `nist_bridge` (`results/motco_export_sensitivity/nist_bridge/diagnostics`, rank 6, `is_primary` false, export variant `nist_bridge`): a component of the variant that tracks a variable here is a measurement-space finding about the variant; it never reinterprets either analysis' statistics and is never grounds to adopt the variant (variant rule 7).

Rows with |rho| ≥ 0.3 (`DIAGNOSTIC_CORRELATION_THRESHOLD`, raw and partial separately) are flagged: a reporting threshold, not an adoption rule; no p-value is attached to any correlation. Flagged rows recorded: latent components 1 raw and 1 partial; block principal components 4 raw and 3 partial.

### nist_bridge: Flagged latent components

| row | component | sd | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| pls_1 · male | pls_1 | 4.156 | `male` | metadata.csv | 1501 | -0.411 | -0.397 | raw+partial |

### nist_bridge: Flagged block principal components

| row | block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---|---:|---|---|---:|---:|---:|---|
| p180 pc2 · phase | p180 | pc2 | 0.087 | `phase` | covariates.csv | 1501 | -0.593 | n/a | raw |
| nmr pc2 · male | nmr | pc2 | 0.247 | `male` | metadata.csv | 1501 | -0.383 | -0.371 | raw+partial |
| p180 pc1 · male | p180 | pc1 | 0.309 | `male` | metadata.csv | 1501 | -0.362 | -0.365 | raw+partial |
| p180 pc1 · statin | p180 | pc1 | 0.309 | `statin` | covariates.csv | 1501 | -0.306 | n/a | raw |
| p180 pc2 · male | p180 | pc2 | 0.087 | `male` | metadata.csv | 1501 | 0.292 | 0.303 | partial |

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

### nist_bridge: Components

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 6.268 | 0.416 | 0.584 | 0 | 0 | `phase` | 0.290 |
| pls_1 | 4.156 | 0.718 | 0.282 | 1 | 1 | `male` | -0.411 |
| pls_2 | 6.175 | 0.660 | 0.340 | 0 | 0 | `male` | -0.286 |
| pls_3 | 2.787 | 0.729 | 0.271 | 0 | 0 | `statin` | -0.243 |
| pls_4 | 2.097 | 0.678 | 0.322 | 0 | 0 | `male` | -0.237 |
| pls_5 | 2.137 | 0.713 | 0.287 | 0 | 0 | `male` | -0.152 |

Per z-scored block: the variance share of each of its first principal components and its pc1 against `phase` (Spearman here; the export manifest's |Pearson| of the first left-singular vector against the ADNI1 indicator, `counts.phase_offset.<block>.abs_corr_pc1_phase`).

### nist_bridge: Block principal components

| block | features | variance share pc1 | variance share pc2 | variance share pc3 | pc1 against phase: Spearman (here) | \|Pearson\| recorded by export |
|---|---:|---:|---:|---:|---:|---:|
| p180 | 133 | 0.309 | 0.087 | 0.062 | -0.210 | 0.215 |
| nmr | 165 | 0.438 | 0.247 | 0.085 | -0.130 | 0.135 |

The full tables are referenced by hash (section 2): `axis_correlations.csv` (48 rows), `block_pcs.csv` (48 rows), `geometry_shares.csv` (24 rows), `components.csv` (6 rows).

Axis diagnostics of `per_run_standardized` (`results/motco_export_sensitivity/per_run_standardized/diagnostics`, rank 4, `is_primary` false, export variant `per_run_standardized`): a component of the variant that tracks a variable here is a measurement-space finding about the variant; it never reinterprets either analysis' statistics and is never grounds to adopt the variant (variant rule 7).

Rows with |rho| ≥ 0.3 (`DIAGNOSTIC_CORRELATION_THRESHOLD`, raw and partial separately) are flagged: a reporting threshold, not an adoption rule; no p-value is attached to any correlation. Flagged rows recorded: latent components 2 raw and 1 partial; block principal components 3 raw and 2 partial.

### per_run_standardized: Flagged latent components

| row | component | sd | variable | source | n | rho | rho \| design | flag |
|---|---|---:|---|---|---:|---:|---:|---|
| pls_1 · male | pls_1 | 3.941 | `male` | metadata.csv | 1501 | -0.414 | -0.400 | raw+partial |
| pls_3 · statin | pls_3 | 2.808 | `statin` | covariates.csv | 1501 | -0.317 | n/a | raw |

### per_run_standardized: Flagged block principal components

| row | block | component | variance share | variable | source | n | rho | rho \| design | flag |
|---|---|---|---:|---|---|---:|---:|---:|---|
| p180 pc1 · male | p180 | pc1 | 0.307 | `male` | metadata.csv | 1501 | -0.392 | -0.373 | raw+partial |
| nmr pc2 · male | nmr | pc2 | 0.247 | `male` | metadata.csv | 1501 | -0.383 | -0.371 | raw+partial |
| p180 pc1 · statin | p180 | pc1 | 0.307 | `statin` | covariates.csv | 1501 | -0.318 | n/a | raw |

Per latent component: the score SD, the share of its squared `pls_loadings.csv` entries (MOTCO's rotation weights on the z-scored joint features; the blocks enter unweighted) held by each block, the variables flagged on the raw and on the partial correlation, and the variable with the largest |rho|.

### per_run_standardized: Components

| component | sd | share p180 | share nmr | flagged raw | flagged partial | top variable | top rho |
|---|---:|---:|---:|---:|---:|---|---:|
| pls_0 | 6.159 | 0.333 | 0.667 | 0 | 0 | `statin` | 0.239 |
| pls_1 | 3.941 | 0.698 | 0.302 | 1 | 1 | `male` | -0.414 |
| pls_2 | 6.278 | 0.682 | 0.318 | 0 | 0 | `male` | -0.278 |
| pls_3 | 2.808 | 0.710 | 0.290 | 1 | 0 | `statin` | -0.317 |

Per z-scored block: the variance share of each of its first principal components and its pc1 against `phase` (Spearman here; the export manifest's |Pearson| of the first left-singular vector against the ADNI1 indicator, `counts.phase_offset.<block>.abs_corr_pc1_phase`).

### per_run_standardized: Block principal components

| block | features | variance share pc1 | variance share pc2 | variance share pc3 | pc1 against phase: Spearman (here) | \|Pearson\| recorded by export |
|---|---:|---:|---:|---:|---:|---:|
| p180 | 133 | 0.307 | 0.068 | 0.064 | 0.005 | 0.000 |
| nmr | 165 | 0.438 | 0.247 | 0.085 | -0.130 | 0.135 |

The full tables are referenced by hash (section 2): `axis_correlations.csv` (32 rows), `block_pcs.csv` (48 rows), `geometry_shares.csv` (16 rows), `components.csv` (4 rows).

### First component against phase

| analysis | component | sd | rho with phase | rho \| design | flag |
|---|---|---:|---:|---:|---|
| primary | pls_0 | 7.334 | 0.542 | n/a | raw |
| nist_bridge | pls_0 | 6.268 | 0.290 | n/a | none |
| per_run_standardized | pls_0 | 6.159 | 0.156 | n/a | none |

The `motco analyze` command that reproduces `nist_bridge`'s analysis directory (`cli_equivalent`; replace OUT_DIR with a new directory; paths are relative to the directory analyze ran in):

```
motco analyze --block p180=results/motco_export_sensitivity/nist_bridge/motco_input/p180.csv --block nmr=results/motco_export_sensitivity/nist_bridge/motco_input/nmr.csv --metadata results/motco_export_sensitivity/nist_bridge/analysis/analysis_metadata.csv --sample-col rid --group-col sex --stage-col stage --stage-order CN,MCI,AD --group-order Female,Male --covariate age --covariate education --categorical-covariate apoe4 --categorical-covariate phase --categorical-covariate statin --missing-covariates error --permutations 9999 --seed 20261027 --n-jobs 1 --min-components 2 --out-dir OUT_DIR
```

The `motco analyze` command that reproduces `per_run_standardized`'s analysis directory (`cli_equivalent`; replace OUT_DIR with a new directory; paths are relative to the directory analyze ran in):

```
motco analyze --block p180=results/motco_export_sensitivity/per_run_standardized/motco_input/p180.csv --block nmr=results/motco_export_sensitivity/per_run_standardized/motco_input/nmr.csv --metadata results/motco_export_sensitivity/per_run_standardized/analysis/analysis_metadata.csv --sample-col rid --group-col sex --stage-col stage --stage-order CN,MCI,AD --group-order Female,Male --covariate age --covariate education --categorical-covariate apoe4 --categorical-covariate phase --categorical-covariate statin --missing-covariates error --permutations 9999 --seed 20261027 --n-jobs 1 --min-components 2 --out-dir OUT_DIR
```

## Findings

Every deviation from the predeclared counts and every finding of every input manifest, verbatim, under its step; then the report's own.

### clean — results/cleaned/p180/clean_manifest.json

None.

### clean — results/cleaned/nmr/clean_manifest.json

None.

### cohort — results/cohort/cohort_manifest.json

None.

### export — results/motco_input/manifest.json

None.

### analyze — results/motco_analysis/analysis_manifest.json

None.

### axis-diagnostics — results/motco_diagnostics/diagnostics_manifest.json

- finding: pls_0: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (0.54; partial n/a)
- finding: pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.40; partial -0.40)
- finding: pls_3: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (-0.53; partial n/a)
- finding: pls_4: 2 of 8 variables flagged at |rho| >= 0.3 (raw or partial): statin (-0.36; partial n/a), phase (0.32; partial n/a)

### latent-sensitivity — results/motco_latent_sensitivity/analysis/analysis_manifest.json

- finding: the arm's CV-selected rank 4 differs from the primary's 8: reported beside angle, not ranked as better or worse (arm rule 3)

### latent-sensitivity — results/motco_latent_sensitivity/comparison/latent_sensitivity_manifest.json

- finding: the arm's CV-selected rank 4 differs from the primary's 8: reported beside angle, not ranked as better or worse (arm rule 3)

### axis-diagnostics — results/motco_latent_sensitivity/diagnostics/diagnostics_manifest.json

- finding: pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.48; partial -0.46)
- finding: pls_2: 2 of 8 variables flagged at |rho| >= 0.3 (raw or partial): phase (0.42; partial n/a), statin (0.33; partial n/a)
- finding: the analysis read is not the primary (directory results/motco_latent_sensitivity/analysis, latent adjustment 'stage'): the primary's rank and the row counts are not expected; the rank-independent counts are

### export-sensitivity — results/motco_export_sensitivity/nist_bridge/motco_input/manifest.json

None.

### export-sensitivity — results/motco_export_sensitivity/nist_bridge/analysis/analysis_manifest.json

- finding: the variant nist_bridge's CV-selected rank 6 differs from the primary's 8: reported beside angle, not ranked (variant rule 3)

### export-sensitivity — results/motco_export_sensitivity/nist_bridge/comparison/export_sensitivity_manifest.json

- finding: the variant nist_bridge's CV-selected rank 6 differs from the primary's 8: reported beside angle, not ranked (variant rule 3)

### axis-diagnostics — results/motco_export_sensitivity/nist_bridge/diagnostics/diagnostics_manifest.json

- finding: pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.41; partial -0.40)
- finding: the analysis read is not the primary (directory results/motco_export_sensitivity/nist_bridge/analysis, latent adjustment None, export variant 'nist_bridge'): the primary's rank and the row counts are not expected; the rank-independent counts are

### export-sensitivity — results/motco_export_sensitivity/per_run_standardized/motco_input/manifest.json

None.

### export-sensitivity — results/motco_export_sensitivity/per_run_standardized/analysis/analysis_manifest.json

- finding: the variant per_run_standardized's CV-selected rank 4 differs from the primary's 8: reported beside angle, not ranked (variant rule 3)

### export-sensitivity — results/motco_export_sensitivity/per_run_standardized/comparison/export_sensitivity_manifest.json

- finding: the variant per_run_standardized's CV-selected rank 4 differs from the primary's 8: reported beside angle, not ranked (variant rule 3)

### axis-diagnostics — results/motco_export_sensitivity/per_run_standardized/diagnostics/diagnostics_manifest.json

- finding: pls_1: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): male (-0.41; partial -0.40)
- finding: pls_3: 1 of 8 variables flagged at |rho| >= 0.3 (raw or partial): statin (-0.32; partial n/a)
- finding: the analysis read is not the primary (directory results/motco_export_sensitivity/per_run_standardized/analysis, latent adjustment None, export variant 'per_run_standardized'): the primary's rank and the row counts are not expected; the rank-independent counts are

### report

- clean p180 (results/cleaned/p180/clean_manifest.json): no `numerics` block, written before `adni-portable-numerics`
- clean nmr (results/cleaned/nmr/clean_manifest.json): no `numerics` block, written before `adni-portable-numerics`
- cohort (results/cohort/cohort_manifest.json): no `numerics` block, written before `adni-portable-numerics`
- export (results/motco_input/manifest.json): no `numerics` block, written before `adni-portable-numerics`
- analyze (results/motco_analysis/analysis_manifest.json): no `numerics` block, written before `adni-portable-numerics`

## Reading rules

### READING_RULES

Binding for every reader of the result (`READING_RULES`, decided by `adni-analyze` before any run):

1. The primary result is the covariate-adjusted analysis on the covariate-blind basis with the five covariates; every sensitivity (latent adjustment, export variants, the CN / LMCI / AD arm, a rank sweep) is read beside it, and a rejection status that differs in an arm is dependence on that arm's setting, never a replacement of the primary.
2. The CV-selected rank, the rank floor, the record's `config_spectrum` eigengap and the `angle` null summary are reported beside `angle`. The floor defines `angle` and `shape` in at least two dimensions; it does not make them powerful.
3. `angle` and `shape` non-rejections are uninformative: MOTCO's operating characteristics were measured at n = 80 on a structural analogue (InterSIM blocks, 498 features), and no power statement exists at this design (n = 1501, 298 metabolites, six design columns). `angle` reads only the endpoint stages (CN and AD). A rejection is evidence that the trajectories differ in that respect, with Type I controlled at the validated designs.
4. A `delta` rejection is evidence of a difference between the sexes' trajectories, not specifically of a difference in size.
5. The covariate block of the record (design columns, reference row, missing policy, dropped participants) is reported beside the results. The adjustment is additive and linear on a covariate-blind basis, validated at three design columns and n = 80, and has no sex × covariate or stage × covariate term: the run offset is assumed equal in both sexes and across stages.
6. The p180 run offset (export manifest `counts.phase_offset`: median |d| 1.12, 80 of 133 metabolites above 1, PC1 correlation 0.73 with phase; NMR 0.21, 0, 0.13) and the block shares (p180 133 / 298, unweighted in MOTCO 0.10.0) are reported beside the results. A latent component that tracks phase is a reading matter for `axis-diagnostics` and the latent-adjusted arm, not an adjustment of the primary.
7. Feature membership and scale (`EXPORT_FEATURE_RULE`: 165 of 245 NMR columns, the floored log2, nothing imputed, winsorized or removed) are reported beside the results.
8. Reported runs use `n_jobs = 1`; a run at another value carries a finding and is not reported. Report numbers are pasted from the generated files and checked by `report --check`.
9. No result changes a constant. The analysis is run once at these settings; a second run at other settings is a new proposal.

### LATENT_SENSITIVITY_READING_RULES

Binding for every reader of the arm (`LATENT_SENSITIVITY_READING_RULES`, decided by `adni-latent-sensitivity` before any run), after `READING_RULES`:

1. The arm is read beside the primary and never replaces it. MOTCO's power comparison returned `candidate_fails` for `stage` conditioning, which excludes the latent adjustment as a replacement of the covariate-blind primary.
2. The primary and the arm share the export, the covariates and their design, the cells, the CV folds, the seed and the permutations. They differ only in the latent basis and the CV-selected rank: the arm's basis is fitted on the features with the five covariates regressed out within stage, and the raw features are measured in it. A rejection status that differs is basis dependence, not a result of the arm.
3. The arm's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked as better or worse.
4. An `angle` rejection that appears only in the arm is read against MOTCO's controls, and is not evidence of an orientation difference on its own: the translation control rejected `angle` at 0.085–0.092 under `stage` conditioning, against the 0.0706 bound (the covariate-blind basis was above it too, at 0.076–0.086); under the Type I check, `angle` held the bound by only 0.004 (0.067 against 0.0706).
5. A `delta` or `shape` non-rejection in the arm is weaker than the primary's. MOTCO measured lost `shape` power with a covariate-aligned nuisance axis (0.243 against 0.428) and lost small-magnitude `delta` power without one (0.400 against 0.520 at e = 0.1). Reading rules 3 and 4 hold in the arm.
6. The arm's `latent_adjustment` block and its covariate block are reported beside its results. The `latent_adjustment` block holds the conditioning, the design columns, the residual df, the smallest CV training df and the feature R² summary; `feature_r2` states how much feature variance the residualization removed.
7. Residualizing a covariate that mediates the stage effect removes real stage signal, and no data can tell a confounder from a mediator. `age`, `education` and `apoe4` precede disease, and `phase` is the assay run and protocol (`LATENT_SENSITIVITY_COVARIATE_ROLES`). `statin` may follow diagnosis, so the arm's basis may have removed stage signal that runs through treatment.
8. MOTCO's latent-adjustment operating characteristics were measured at one design: n = 80, the SEA-AD MTG structure, 498 features, eight covariates in nine design columns, covariates confounded with group × stage far beyond this design's. None was measured at this design (n = 1501, 298 metabolites, six design columns), and the arm carries no Type I or power claim of its own.
9. A component of the arm that tracks a variable in its axis diagnostic is a measurement-space finding about the arm. It never reinterprets either analysis' statistics and is never grounds to adopt the arm.

### EXPORT_VARIANT_READING_RULES

Binding for every reader of an export variant (`EXPORT_VARIANT_READING_RULES`, decided by `adni-nist-bridge` before any run), after `READING_RULES`:

1. A variant is read beside the primary and never replaces it. No variant result changes a constant, reruns the primary or adopts a variant.
2. A variant shares with the primary the cleaned tables, the participants, the NMR block, the covariates and their design, the cells, the settings, the CV folds, the seed and the permutations. It differs only in the p180 values. A rejection status that differs is dependence on the handling of the p180 run, not a result of the variant.
3. The variant's CV-selected rank, floor, eigengap and `angle` null summary are reported beside its `angle`. A rank that differs from the primary's is reported, not ranked.
4. `nist_bridge` removes the part of the run offset that NIST SRM 1950 carries, between-run calibration. It assumes the run acts as one factor per metabolite, the same in plasma (NIST) and serum (participants). It leaves what NIST cannot see: a shift common to most metabolites, sample-handling differences between the protocols (the largest residuals are aspartate and glutamate) and the seven unbridged metabolites. `phase` stays a covariate of the stage means and carries what remains.
5. `per_run_standardized` removes each p180 metabolite's whole difference in mean and spread between the runs, whatever its source: calibration, sample handling, and the stage-composition difference the runs carry, since SMC and EMCI were enrolled only in ADNI-GO/2. A difference between it and `nist_bridge` is read as the part of the run difference that is not calibration, never as evidence for either variant.
6. A non-rejection in a variant is no more informative than the primary's: reading rule 3 holds, and no power statement exists at this design. A rejection that appears only in a variant is dependence on the run handling and is read beside the variant's rank and null summary.
7. The variant's export manifest records the run offset per block, and for `nist_bridge` the factor per metabolite; both are reported beside the results. A variant component that tracks a variable in its axis diagnostic is a measurement-space finding and never grounds to adopt the variant.

## Reproduction

The pipeline, in order, each step reading the previous steps' outputs and checking their manifests' hashes; `clean`, `cohort` and `export-sensitivity --variant nist_bridge` need the data root (`--data-root`, `ADNI_DATA_ROOT` or `data/`; the QC archives `ADMC_supplement.zip`, `ADMCDUKEP180SUPP_20170410.zip` are read in place, through top-level symlinks the data root must hold), the others read `results/` only, and `report` reads committed aggregate files only, so it runs on any clone:

```
uv run adni-sexdiff clean --platform all
uv run adni-sexdiff cohort
uv run adni-sexdiff export
uv run adni-sexdiff analyze
uv run adni-sexdiff axis-diagnostics
uv run adni-sexdiff latent-sensitivity
uv run adni-sexdiff axis-diagnostics --analysis-dir results/motco_latent_sensitivity/analysis --out-dir results/motco_latent_sensitivity/diagnostics
uv run adni-sexdiff export-sensitivity --variant all
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/nist_bridge/motco_input --analysis-dir results/motco_export_sensitivity/nist_bridge/analysis --out-dir results/motco_export_sensitivity/nist_bridge/diagnostics
uv run adni-sexdiff axis-diagnostics --input-dir results/motco_export_sensitivity/per_run_standardized/motco_input --analysis-dir results/motco_export_sensitivity/per_run_standardized/analysis --out-dir results/motco_export_sensitivity/per_run_standardized/diagnostics
uv run adni-sexdiff report
uv run adni-sexdiff report --check
```

`report --check` reads the newest `reports/motco-adni-<date>.md` (or the file `--out` names), reruns every gate, regenerates the report from the outputs now on disk with the date taken from the file name and compares every table cell by cell and every other line line by line; a regenerated results directory fails it on the provenance hashes until a new report is written and checked.

MOTCO's CLI equivalents of the 4 analyses, the primary, the arm and `nist_bridge`, `per_run_standardized` (`cli_equivalent` of their analysis manifests):

```
motco analyze --block p180=results/motco_input/p180.csv --block nmr=results/motco_input/nmr.csv --metadata results/motco_analysis/analysis_metadata.csv --sample-col rid --group-col sex --stage-col stage --stage-order CN,MCI,AD --group-order Female,Male --covariate age --covariate education --categorical-covariate apoe4 --categorical-covariate phase --categorical-covariate statin --missing-covariates error --permutations 9999 --seed 20261027 --n-jobs 1 --min-components 2 --out-dir OUT_DIR
motco analyze --block p180=results/motco_input/p180.csv --block nmr=results/motco_input/nmr.csv --metadata results/motco_latent_sensitivity/analysis/analysis_metadata.csv --sample-col rid --group-col sex --stage-col stage --stage-order CN,MCI,AD --group-order Female,Male --covariate age --covariate education --categorical-covariate apoe4 --categorical-covariate phase --categorical-covariate statin --missing-covariates error --latent-adjustment stage --permutations 9999 --seed 20261027 --n-jobs 1 --min-components 2 --out-dir OUT_DIR
motco analyze --block p180=results/motco_export_sensitivity/nist_bridge/motco_input/p180.csv --block nmr=results/motco_export_sensitivity/nist_bridge/motco_input/nmr.csv --metadata results/motco_export_sensitivity/nist_bridge/analysis/analysis_metadata.csv --sample-col rid --group-col sex --stage-col stage --stage-order CN,MCI,AD --group-order Female,Male --covariate age --covariate education --categorical-covariate apoe4 --categorical-covariate phase --categorical-covariate statin --missing-covariates error --permutations 9999 --seed 20261027 --n-jobs 1 --min-components 2 --out-dir OUT_DIR
motco analyze --block p180=results/motco_export_sensitivity/per_run_standardized/motco_input/p180.csv --block nmr=results/motco_export_sensitivity/per_run_standardized/motco_input/nmr.csv --metadata results/motco_export_sensitivity/per_run_standardized/analysis/analysis_metadata.csv --sample-col rid --group-col sex --stage-col stage --stage-order CN,MCI,AD --group-order Female,Male --covariate age --covariate education --categorical-covariate apoe4 --categorical-covariate phase --categorical-covariate statin --missing-covariates error --permutations 9999 --seed 20261027 --n-jobs 1 --min-components 2 --out-dir OUT_DIR
```
