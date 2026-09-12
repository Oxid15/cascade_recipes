import logging
import os

import numpy as np
from sklearn.linear_model import SGDClassifier

from cascade.base import Config
from cascade.lines import ModelLine
from cascade.utils.sklearn import SkMetric, SkModel

HERE = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


class TrainConfig(Config):
    window_days = 30  # how much history the nightly job pulls
    l2 = 1e-4  # regulariser
    class_weight = "balanced"
    min_rows = 500  # abort if the feature store gave us less
    seed = 0


def pull_features(window_days: int, seed: int):
    """
    Mocked feature store call
    """
    rng = np.random.default_rng(seed)
    n = 40 * window_days
    x = rng.normal(size=(n, 6))
    y = (x[:, 0] * 0.9 + x[:, 3] * 0.5 + rng.normal(scale=0.6, size=n) > 0).astype(int)
    return x, y


def main():
    cfg = TrainConfig()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    logger.info("pulling %s days of features", cfg.window_days)
    x, y = pull_features(cfg.window_days, cfg.seed)

    if len(x) < cfg.min_rows:
        raise RuntimeError(
            f"feature store returned {len(x)} rows, below min_rows={cfg.min_rows}; "
            "refusing to ship a model trained on a partial window"
        )

    split = int(len(x) * 0.8)
    model = SkModel(
        blocks=[
            SGDClassifier(
                alpha=cfg.l2, class_weight=cfg.class_weight, random_state=cfg.seed
            )
        ],
        **cfg.to_dict(),  # this will track everything from config as Model.params
    )
    model.fit(x[:split], y[:split])
    model.evaluate(
        x[split:],
        y[split:],
        [
            SkMetric(
                "accuracy_score",
                split="val",
                direction="up",
            ),
            SkMetric(
                "f1_score",
                split="val",
                direction="up",
            ),
        ],
    )
    logger.info(
        "metrics: %s", [(m.name, round(float(m.value), 4)) for m in model.metrics]
    )

    model.describe(f"Nightly retrain over a {cfg.window_days}-day window")
    model.tag("nightly")
    model.add_config()  # will not work outside `cascade run`
    model.add_log()  # will not work outside `cascade run`

    line = ModelLine(os.path.join(HERE, "line"), model_cls=SkModel)
    line.save(model)
    logger.info("saved to %s", model.get_meta()[0].get("path"))


if __name__ == "__main__":
    main()
