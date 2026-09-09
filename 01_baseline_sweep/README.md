# 01 - Baseline sweep

> “I ran twelve variants last week - which one won, with which settings, and on which version of the features?”

This example exercises:

- `TableDataset` and dataset metadata for a tabular source
- Custom `Modifier`, `split`, and a small feature pipeline
- `SkModel` and `SkMetric`
- `Repo` and `ModelLine` for storing comparable experiments
- model `parameters`, `tags`, `descriptions`, and `links` to the feature dataset

## Run this example

From its directory:

```bash
python make_data.py
python train.py
```

`make_data.py` creates the synthetic churn table in `data/churn.csv`. `train.py`
runs the configured logistic-regression and decision-tree variants and saves them
under `repo/`.

## See the results

Inspect the saved models with the CLI:

```bash
cd repo
cascade query slug description tags 'metrics[0].name' 'metrics[0].value' sort 'metrics[0].value' desc
```

The model metadata, serialized models, and feature-pipeline artifacts are also
available below `repo/baseline_logreg/` and `repo/baseline_tree/`.

## Learn more

- [Datasets and modifiers](https://oxid15.github.io/cascade/en/latest/explanations/dataset.html)
- [Model training](https://oxid15.github.io/cascade/en/latest/howtos/model_training.html)
- [Linking tracked objects](https://oxid15.github.io/cascade/en/latest/howtos/links.html)
- [Experiment queries](https://oxid15.github.io/cascade/en/latest/tutorials/results_querying.html)
