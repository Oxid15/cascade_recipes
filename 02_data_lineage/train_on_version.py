# %% [rst]
# Pin the Model to Dataset Version
# ********************************
#
# Trains two classifiers on two different DataLine versions and records
# the link, so ``cascade query`` can answer "which data version did this model see?".

# %%

import os

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier

from cascade.repos import Repo
from cascade.utils.sklearn import SkMetric, SkModel

HERE = os.path.dirname(os.path.abspath(__file__))

# %% [rst]
# Here we load two dataset versions and train a classifier on each version.
#
# We can link dataset and even its line to the model using special methods.
# This will allow us to not lose track of where the data came from.


# %%


def main():
    repo = Repo(os.path.join(HERE, "repo"))
    dl = repo.add_line("dataline", line_type="data")
    line = repo.add_line("ticket_router", line_type="model")

    for version in ("0.2", "1.0"):
        ds = dl.load(version)
        x = [item["text"] for item in ds]
        y = [item["label"] for item in ds]

        model = SkModel(
            blocks=[
                HashingVectorizer(n_features=2048),
                SGDClassifier(loss="log_loss", random_state=0),
            ],
            data_version=version,
        )
        model.fit(x, y)
        model.evaluate(x, y, [SkMetric("accuracy_score")])

        model.link_dataset(ds, name="tickets", split="train", line=dl)
        model.link(name="dataline", uri=dl.get_root())
        model.describe(f"Ticket router trained on dataline version {version}")
        model.tag(f"data-{version}")

        line.save(model)
        print(f"data {version}: {len(ds)} rows, acc={model.metrics[0].value:.3f}")


if __name__ == "__main__":
    main()

# %% [rst]
# Conclusion
# **********
#
# In this recipe dataset versioning in Cascade is excercised.
# It is able to automatically version and track datasets and processing pipeline.
# You can also link data to the model you are training and always go back and reproduce
# your machine learning experiment exactly.
