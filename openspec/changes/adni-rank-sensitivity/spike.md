# Spike: forced ranks in MOTCO 0.10.0 (synthetic)

Run on 2026-10-30 on nixos-office, in the session scratchpad, with MOTCO 0.10.0, scikit-learn 1.8.0 and numpy 2.4.6, importing `adni_sexdiff` first so that the pinned numerics hold. **It read no ADNI file and ran no forced rank on ADNI data.** It fed the design and the reading rules, not a constant's value.

## Questions

1. Is the latent space at a forced rank k the first k components of a higher forced rank?
2. Does a forced run at the CV-selected rank reproduce the CV run?
3. What does MOTCO record for a forced run, and which ranks does it accept?

## Data

- **Sample:** 360 synthetic samples, sex Female / Male, stage CN / MCI / AD drawn 0.35 / 0.40 / 0.25.
- **Covariates:** the five covariates with the primary's names and kinds (`age`, `education` numeric; `apoe4`, `phase`, `statin` categorical).
- **Blocks:**
  - `p180` (40 features) and `nmr` (50), standard normal;
  - five features per block shifted by the stage code;
  - five more shifted by `phase`, a run offset in miniature.
- **Settings:** the primary's `TrajectoryAnalysisParams`, except 199 permutations: seed 20261027, `n_jobs` 1, `min_components` 2.

## Code path read

- `motco.analysis.analyze_trajectories` passes `forced_components` to `motco.simulations.evaluation.fit_pls_latent_space`.
- On the forced path the cross-validation is skipped. The pooled `fit_plsda_model` (`sklearn.cross_decomposition.PLSRegression`, NIPALS) is fitted at the forced rank, and the latent matrix is its `x_scores_`.
- `_forced_components` rejects a value outside `[2, min(n_features, n_samples)]` and never clamps it.
- RRPP draws `rng.permutation(n)` from `np.random.default_rng(seed)` (`motco.stats.permutation`). The draws depend on the seed and n, not on the rank.

## Results

| check | result |
|---|---|
| CV-selected rank on the synthetic data | 2 (`cv`) |
| scores at forced 2, 3 and 12: the first k columns of forced 12's | bit for bit equal (max abs difference 0) |
| `pls_loadings.csv` columns of forced 2 and 3 against forced 12's | not equal: the rotations depend on the rank |
| forced 2 against the CV run (rank 2) | latent scores, `statistics`, `p_values`, `null_summary` and `config_spectrum` bit for bit equal |
| the forced record's `latent` | `component_selection` `forced`, `selected_lv` k, `cv_mean_auroc` null, `cv_repeats_completed` 0, `integration_params` `{stage_col, selected_lv, forced_components}` (no CV keys, no `min_components`) |
| the forced record's `params` | `forced_components` k, `min_components` 2, `max_components` 20 |
| forced rank 1 | `TrajectoryAnalysisError`: outside the feasible range `[2, 90]` |
| runtime per forced rank (199 permutations) | 0.05 s, against 5.2 s for the CV run |

## What follows for the change

- **Nesting** (question 1): a forced rank at or below the primary's 8 measures the primary's own first components, and a rank above 8 adds components. One axis diagnostic of the top rank covers every rank's components (design D8), and reading rule 3 states the nesting.
- **Anchor** (question 2): a forced run at the primary's rank must reproduce the primary's statistics and its `latent_scores.csv`, `pls_loadings.csv` and `stage_means.csv`. The step gates on it before writing (design D3).
- **Findings** (question 3): the forced record has no CV keys and no `min_components` in `integration_params`, and `cv_repeats_completed` 0. Three findings of `analyze` would misfire on it: "CV completed 0 of 5 repeats", "the CV ran with rank floor 1" and "MOTCO default `forced_components` moved". They must become forced-aware (design D5).
- **Feasibility:** every rank of the ladder lies inside `[2, 298]` on the primary export.

## Script

Kept in the session scratchpad (`spike_rank/forced_nesting.py`). It is not part of the repository. Its logic:

```python
import adni_sexdiff  # pinned numerics before numpy
import numpy as np, pandas as pd
from motco.analysis import OmicsBlock, TrajectoryAnalysisParams, TrajectoryDataset, analyze_trajectories

rng = np.random.default_rng(7)
n = 360
# metadata: sex, stage (0.35 / 0.40 / 0.25), the five covariates with the primary's names and kinds
# blocks: p180 (40) and nmr (50) standard normal; 5 features shifted by the stage code, 5 by phase
ds = TrajectoryDataset(..., covariate_cols=("age", "education", "apoe4", "phase", "statin"),
                       categorical_covariates=("apoe4", "phase", "statin"), missing_covariates="error")

def run(forced):
    return analyze_trajectories(ds, TrajectoryAnalysisParams(
        permutations=199, seed=20261027, n_jobs=1, min_components=2, forced_components=forced))

cv = run(None)
k = cv.record["latent"]["selected_lv"]
res = {r: run(r) for r in sorted({2, 3, k, 12})}
# nesting: res[r].latent_scores equals res[12].latent_scores.iloc[:, :r], bit for bit
# anchor: cv and res[k] have equal latent scores, statistics, p_values, null_summary, config_spectrum
# feasibility: run(1) raises TrajectoryAnalysisError
```
