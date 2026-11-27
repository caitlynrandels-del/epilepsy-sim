# LAYERS.md: switchable layers (v4 interface: `P["layers"] = {name: True | False | {overrides}}`)

| Layer | Epilepsy meaning | Default | Changes outcomes? |
|---|---|---|---|
| sponge | 2-compartment porous buffer: escaped discharges (network) and reawakening attempts (relapse) | on | **yes, major** (−10.2 pt seizure freedom when removed) |
| materials | porosity, saturation, hysteresis, elasticity of the sponge | on | minor; only with the sponge |
| physics | pressure/diffusion/compression on sponge fill | on | negligible |
| heat | heat-trace diffusion/dissipation (observational) | on | no |
| inhibition | inhibitory surround with exhaustion (immune-surveillance analogue) | on | **yes, major** (−9.6 pt when removed) |
| hpa | stress-hormone load + cascades (stress → sleep loss; illness/binge → missed dose) | on | yes, moderate (+1.7 pt when removed) |
| kindling | Hawkes self-excitation | on | changes seizure counts (+0.16/yr), not seizure freedom |
| network | lagged whole-brain coupling between foci | on | small |
| shading | **PROVISIONAL** cel-shading (CELL_SHADING.md) | on, observational | no; the coupled variant does (−3.0 pt at feedback 1) |

Code: `code/layers.py`. Experiments: `layer_minus_*`, `layer_only_*`, `layer_only_*_with_sponge`. Results: RESULTS_SUMMARY §7, charts/04.
