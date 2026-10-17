# %% [rst]
# Data Transformation Pipeline
# ****************************
#
# Here is the pipeline definition in a separate file for the ticket dataset.

# %%
import json
import os

from cascade.data import Dataset, Filter, Modifier, Sampler

HERE = os.path.dirname(os.path.abspath(__file__))

CANONICAL = {
    "billing": "billing",
    "bug": "bug",
    "account": "account",
    "question": "question",
    "feature": "feature",
}

# %% [rst]
# First we inherit ``cascade.data.Dataset`` to create simple JSON reading custom data source.
# Main methods of a custom ``Dataset`` to define are ``get`` and ``__len__``. There is also an
# ability to customize its metadata using ``get_meta`` method.
# Metadata can then be tracked when we link a dataset to a model.
# %%


class TicketDump(Dataset):
    """Raw JSONL dump as exported by the helpdesk."""

    def __init__(self, snapshot: str, **kwargs):
        self._snapshot = snapshot
        with open(os.path.join(HERE, "data", snapshot)) as f:
            self._rows = [json.loads(line) for line in f]
        super().__init__(**kwargs)

    def get(self, index):
        return self._rows[index]

    def __len__(self):
        return len(self._rows)

    def get_meta(self):
        meta = super().get_meta()
        meta[0]["snapshot"] = self._snapshot
        meta[0]["labels"] = sorted({r["label"] for r in self._rows})
        return meta


# %% [rst]
# We build a pipeline by stacking ``Modifier``s on top of a ``Dataset``.
# Each modifier can call its dataset, perform some operations over the results
# of the previous stage and return.


# %%


class NormalizeLabels(Modifier):
    """Fold 'BUG' / 'Billing' / 'account ' into the canonical taxonomy."""

    def get(self, index):
        item = dict(self._dataset[index])
        item["label"] = CANONICAL[item["label"].strip().lower()]
        return item


# %% [rst]
# Modifiers that change dataset's length are called ``Sampler``s. This sampler is
# removing duplicate rows. We pass new length to sampler's parent constructor
# so that it will be used in ``__len__`` automatically.


# %%


class Dedup(Sampler):
    """
    Drop rows whose id was seen before
    """

    def __init__(self, dataset, **kwargs):
        seen = set()
        self._keep = []
        for i in range(len(dataset)):
            tid = dataset[i]["id"]
            if tid not in seen:
                seen.add(tid)
                self._keep.append(i)

        super().__init__(dataset, len(self._keep), **kwargs)

    def get(self, index):
        return self._dataset[self._keep[index]]


# %% [rst]
# We also use default ``cascade.data.Filter`` with a filter function that returns ``bool``.

# %%


def not_low_priority(item):
    return item["priority"] != "low"


def build(snapshot: str, drop_low_priority: bool = False):
    ds = TicketDump(snapshot)
    ds = NormalizeLabels(ds)
    ds = Dedup(ds)
    if drop_low_priority:
        ds = Filter(ds, not_low_priority)
    return ds
