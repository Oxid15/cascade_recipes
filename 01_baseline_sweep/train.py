import os

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from cascade import data as cdd
from cascade.repos import Repo
from cascade.utils.sklearn import SkMetric, SkModel
from cascade.utils.tables import TableDataset

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "churn.csv")

CONTRACT_CODES = {"month": 0, "year": 1, "two_year": 2}


class Featurize(cdd.Modifier):
    """Table row -> {"x": list[float], "y": int}."""

    def __init__(self, dataset, use_contract: bool, **kwargs):
        self._use_contract = use_contract
        super().__init__(dataset, **kwargs)

    def get(self, index):
        row = self._dataset[index]
        x = [
            row["tenure_months"],
            row["monthly_charges"],
            row["support_calls"],
            row["is_fiber"],
            row["paperless_billing"],
        ]
        if self._use_contract:
            x.append(CONTRACT_CODES[row["contract"]])
        return {"x": x, "y": int(row["churn"])}


class Rows(cdd.Modifier):
    """Normalize table to dicts per row"""

    def get(self, index):
        item = self._dataset[index]
        if isinstance(item, pd.DataFrame):
            item = item.iloc[0]
        return item.to_dict() if hasattr(item, "to_dict") else item


def build_pipeline(use_contract: bool):
    table = TableDataset(t=pd.read_csv(CSV))
    ds = Rows(table)
    ds = Featurize(ds, use_contract=use_contract)
    ds.describe("Churn features from the raw billing export")
    ds.update_meta({"feature_count": 6 if use_contract else 5})
    return ds


def xy(ds):
    x = [item["x"] for item in ds]
    y = [item["y"] for item in ds]
    return x, y


SWEEP = [
    {"family": "logreg", "C": 0.1, "use_contract": True},
    {"family": "logreg", "C": 1.0, "use_contract": True},
    {"family": "logreg", "C": 1.0, "use_contract": False},
    {"family": "tree", "max_depth": 3, "use_contract": True},
    {"family": "tree", "max_depth": 6, "use_contract": True},
    {"family": "tree", "max_depth": 6, "use_contract": False},
]


def make_model(cfg):
    if cfg["family"] == "logreg":
        return SkModel(
            blocks=[StandardScaler(), LogisticRegression(C=cfg["C"], max_iter=200)],
            **cfg,
        )
    return SkModel(
        blocks=[DecisionTreeClassifier(max_depth=cfg["max_depth"], random_state=0)],
        **cfg,
    )


def main():
    repo = Repo(os.path.join(HERE, "repo"))
    repo.describe("Churn baseline sweep, Q3 planning")

    for cfg in SWEEP:
        ds = build_pipeline(cfg["use_contract"])
        train_ds, test_ds = cdd.split(ds, frac=0.8)

        model = make_model(cfg)
        model.fit(*xy(train_ds))

        x_test, y_test = xy(test_ds)
        model.evaluate(
            x_test,
            y_test,
            [
                SkMetric("f1_score"),
                SkMetric("accuracy_score"),
                SkMetric("roc_auc_score"),
            ],
        )

        model.tag(cfg["family"])
        model.describe(
            f"{cfg['family']} baseline, contract feature={cfg['use_contract']}"
        )
        model.link(ds, name="features")

        line = repo.add_line(f"baseline_{cfg['family']}", line_type="model")
        line.save(model)
        print(f"saved {cfg} -> {[(m.name, m.value) for m in model.metrics]}")


if __name__ == "__main__":
    main()
