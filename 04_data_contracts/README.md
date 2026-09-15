# Data contracts

> "The upstream vendor shipped a bad file at 3am. Which row, which field, and which pipeline stage noticed?"

This example exercises:

- a Pydantic row schema declared with `SchemaModifier`
- `ValidationError` and `GetItemError` for locating a bad row and pipeline stage
- `DataCard`, `Assessor`, and `LabelingInfo` metadata

## Run this example

```bash
python contract.py
```

`contract.py` parses rows into the
Pydantic model, reports the corrupt row with its wrapped Cascade error, and
prints the data card from pipeline metadata.

## Learn more

- [Tracking dataset errors](https://oxid15.github.io/cascade/en/latest/howtos/track_dataset_errors.html)
- [Datasets, modifiers, and data cards](https://oxid15.github.io/cascade/en/latest/explanations/dataset.html)
- [`cascade.data` API](https://oxid15.github.io/cascade/en/latest/modules/cascade.data.html)
