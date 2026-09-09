import os

from cascade.repos import Repo

from pipeline import build

HERE = os.path.dirname(os.path.abspath(__file__))


def show(dl, ds, note):
    print(f"{note:<46} -> version {dl.get_version(ds)}")


def main():
    dl = Repo("repo").add_line("dataline", line_type="data")
    dl.describe("Support tickets, weekly snapshots from the helpdesk export")

    # week 1: messy dump
    ds = build("tickets_w1.jsonl")
    ds.update_meta({"snapshot_week": 1, "known_issues": ["dupes", "label spellings"]})
    dl.save(ds)
    show(dl, ds, "w1 raw dump")

    # annotate it: meta-only change, expect a MINOR bump
    ds.update_meta({"reviewed_by": "data-eng", "ticket": "DATA-114"})
    dl.save(ds)
    show(dl, ds, "w1 + review annotation (meta only)")

    # week 2: same pipeline, cleaner source
    ds2 = build("tickets_w2.jsonl")
    ds2.update_meta({"snapshot_week": 2, "known_issues": []})
    dl.save(ds2)
    show(dl, ds2, "w2 clean source (same pipeline shape)")

    # new pipeline stage: expect a MAJOR bump
    ds3 = build("tickets_w3.jsonl", drop_low_priority=True)
    ds3.update_meta({"snapshot_week": 3, "known_issues": []})
    dl.save(ds3)
    show(dl, ds3, "w3 + Filter stage (pipeline shape changed)")

    print("\nversions on disk:", sorted(os.listdir(dl.get_root())))
    print("latest:", dl.get_latest_version())

    # reproduce an old version exactly
    old = dl.load("0.1")
    print(f"\nreloaded 0.1: {len(old)} rows, first label = {old[0]['label']!r}")
    new = dl.load(str(dl.get_latest_version()))
    print(f"reloaded latest: {len(new)} rows, first label = {new[0]['label']!r}")


if __name__ == "__main__":
    main()
