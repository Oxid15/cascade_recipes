# Cascade Recipes

This repo contains examples of how you can apply Cascade to solve various real-life problems

Cascade is small-scale MLOps library that allows you to have experiment tracking, data versioning and validation, web UI and
much more without the need for complex setups, cloud and servers.

```bash
pip install cascade-ml
```

More info can be found in [Cascade docs](https://oxid15.github.io/cascade/en/latest/) or [Cascade GitHub](https://github.com/Oxid15/cascade)

## List of recipes

### 01 - Baseline Sweep

> "I ran six experiments last week - which one won, with which settings, and on which version of the features?"

This is a basic use case - train models with different settings and then analyze which one is best and what features produced it.

Topics: `pipeline building`, `experiment tracking`, `result querying`

### 02 - Data Lineage

> "Model regressed. Was it the code, or did the dataset change under me?"

Pin model to an exactly reproduced pipeline to understand which change in demo caused quality drop.

Topics: `dataset versioning`, `data quality`, `reproducibility`

### 03 - Scheduled Retrain

> "Last Tuesday’s model is the current best. What config produced it, and can I re-run it with a single thing changed?"

Run training scripts with different configs without changing the source code.

Topics: `configuration management`, `reproducibility`, `log tracking`

### 04 - Data contracts

> "The upstream vendor shipped a bad file at 3am. Which row, which field, and which pipeline stage noticed?"

See how you can enable data validation to never miss an item with unexpected values and track it inside the pipeline
down to a specific index with no effort.

Topics: `data validation`, `error tracking`, `data tracking`

## Contributing

Contributions of new recipes are welcome!
