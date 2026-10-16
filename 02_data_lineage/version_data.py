# %% [rst]
# Version Datasets
# ****************
#
# In the following file we simulate the process of getting the source data
# we have received, building the pipeline we defined previously and then
# saving it in ``DataLine`` - special container that allows to track
# and automatically version data pipelines.
# It can store dataset metadata and even pickle the
# pipeline object to be loaded elsewhere exactly as it was created.
#
# We can see an example of how automatic versioning works below.

# %%

import os

from cascade.repos import Repo

from pipeline import build

HERE = os.path.dirname(os.path.abspath(__file__))


def show(dl, ds, note):
    print(f"{note:<46} -> version {dl.get_version(ds)}")


# %% [rst]
# This is the first iteration
# We add description, build dataset and use ``update_meta`` to add
# more fields to dataset's metadata so that they could be tracked and influence the
# automatic versioning when changed.
#
# In the following example we build a pipeline, update its meta and save it in line.

# %%


def main():
    dl = Repo("repo").add_line("dataline", line_type="data")
    dl.describe("Support tickets, weekly snapshots from the helpdesk export")

    ds = build("tickets_w1.jsonl")
    ds.update_meta({"snapshot_week": 1, "known_issues": ["dupes", "label spellings"]})
    dl.save(ds)
    show(dl, ds, "w1 raw dump")

    # %% [rst]
    # ``DataLine`` will assign a version to the dataset at the moment of saving automatically.
    # It uses metadata to determine if the pipeline changed. The version has two components - major
    # and minor. Major component changes when the pipeline's contents change. For example with a new
    # ``Modifier`` or when some step is removed. Minor changes on any metadata field change.
    #
    # Here we just update fields in meta so when we save new dataset it will bump minor component.

    # %%

    ds.update_meta({"reviewed_by": "data-eng", "ticket": "DATA-114"})
    dl.save(ds)
    show(dl, ds, "w1 + review annotation (meta only)")

    # %% [rst]
    # This week should also get a minor bump.

    # %%

    ds2 = build("tickets_w2.jsonl")
    ds2.update_meta({"snapshot_week": 2, "known_issues": []})
    dl.save(ds2)
    show(dl, ds2, "w2 clean source (same pipeline shape)")

    # %% [rst]
    # This week get a major bump since pipelie also gets ``Filter`` step.

    # %%

    ds3 = build("tickets_w3.jsonl", drop_low_priority=True)
    ds3.update_meta({"snapshot_week": 3, "known_issues": []})
    dl.save(ds3)
    show(dl, ds3, "w3 + Filter stage (pipeline shape changed)")

    print("\nversions on disk:", sorted(os.listdir(dl.get_root())))
    print("latest:", dl.get_latest_version())

    # %% [rst]
    # Reproduce Dataset Version Exactly
    # *********************************
    #
    # After saving a dataset in line, we can load it exactly
    # using its version.
    # Here we ``load`` the dataset of version ``0.1`` and the latest version.

    # %%

    old = dl.load("0.1")
    print(f"\nreloaded 0.1: {len(old)} rows, first label = {old[0]['label']!r}")
    new = dl.load(str(dl.get_latest_version()))
    print(f"reloaded latest: {len(new)} rows, first label = {new[0]['label']!r}")


if __name__ == "__main__":
    main()
