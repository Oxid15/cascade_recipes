# 02 - Data lineage

> "Model 00003 regressed. Was it the code, or did the dataset change under me?"

This example exercises:

- `DataLine` for versioned dataset storage
- Custom dataset metadata with `update_meta()`
- Version changes caused by source data, metadata-only edits, and pipeline shape
- Loading an exact historical dataset version
- Linking a model to the precise dataset version it used

## Run this example

From its directory, create the snapshots, version them, and train models on
two pinned versions:

```bash
python make_data.py
python version_data.py
python train_on_version.py
```

`version_data.py` writes versions to `dataline/`. `train_on_version.py` loads
versions `0.2` and `1.0`, trains a ticket router for each, and saves both
models to `repo/ticket_router/`.

## See the results

The versioning script prints the version assigned to every snapshot and
re-loads both an old and the latest version. To inspect the model lineage:

```bash
cd repo
cascade query slug tags description links
```

The dataset versions, their metadata, and serialized objects are under
`dataline/`; model metadata records the `tickets` dataset link and its version.

## Learn more

- [Datasets and modifiers](https://oxid15.github.io/cascade/en/latest/explanations/dataset.html)
- [DataLine API](https://oxid15.github.io/cascade/en/latest/modules/cascade.lines.html)
- [Linking tracked objects](https://oxid15.github.io/cascade/en/latest/howtos/links.html)
- [Experiment queries](https://oxid15.github.io/cascade/en/latest/tutorials/results_querying.html)
