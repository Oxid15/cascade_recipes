"""
Shared pipeline definition for the ticket dataset.

Kept in its own module because `DataLine.save` pickles the pipeline, and pickle
needs every stage class to be importable by qualified name.
"""

import json
import os

from cascade.data import Dataset, Filter, Modifier

HERE = os.path.dirname(os.path.abspath(__file__))

CANONICAL = {
    "billing": "billing",
    "bug": "bug",
    "account": "account",
    "question": "question",
    "feature": "feature",
}


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


class NormalizeLabels(Modifier):
    """Fold 'BUG' / 'Billing' / 'account ' into the canonical taxonomy."""

    def get(self, index):
        item = dict(self._dataset[index])
        item["label"] = CANONICAL[item["label"].strip().lower()]
        return item


class Dedup(Modifier):
    """Drop rows whose id was seen before. Index map is built eagerly."""

    def __init__(self, dataset, **kwargs):
        super().__init__(dataset, **kwargs)
        seen = set()
        self._keep = []
        for i in range(len(self._dataset)):
            tid = self._dataset[i]["id"]
            if tid not in seen:
                seen.add(tid)
                self._keep.append(i)

    def get(self, index):
        return self._dataset[self._keep[index]]

    def __len__(self):
        return len(self._keep)


def not_low_priority(item):
    return item["priority"] != "low"


def build(snapshot: str, drop_low_priority: bool = False):
    ds = TicketDump(snapshot)
    ds = NormalizeLabels(ds)
    ds = Dedup(ds)
    if drop_low_priority:
        ds = Filter(ds, not_low_priority)
    return ds
