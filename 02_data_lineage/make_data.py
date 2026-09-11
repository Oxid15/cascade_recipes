"""
Synthetic support-ticket corpus - three weekly snapshots of the same dataset.

Week 1: raw dump, has duplicates and inconsistent label spellings.
Week 2: same rows, one label taxonomy fix applied upstream.
Week 3: more rows arrive.
"""

import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))

SUBJECTS = [
    "cannot log in after password reset",
    "invoice charged twice this month",
    "app crashes when opening reports",
    "how do I export my data",
    "refund for cancelled subscription",
    "SSO redirect loop on staging",
    "feature request: dark mode",
    "API returns 500 on bulk upload",
]
LABELS = ["billing", "bug", "account", "question", "feature"]
MESSY = {"billing": "Billing", "bug": "BUG", "account": "account "}


def rows(n, seed, messy):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        subj = rng.choice(SUBJECTS)
        label = rng.choice(LABELS)
        if messy:
            label = MESSY.get(label, label)
        out.append(
            {
                "id": i,
                "text": f"{subj} (ref {rng.randint(1000, 9999)})",
                "label": label,
                "priority": rng.choice(["low", "normal", "high"]),
            }
        )
    if messy:
        out += rng.sample(out, 40)  # duplicates that need de-duping
    return out


def write(name, data):
    path = os.path.join(HERE, "data", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in data:
            f.write(json.dumps(r) + "\n")
    print(f"{name}: {len(data)} rows")


if __name__ == "__main__":
    write("tickets_w1.jsonl", rows(400, seed=1, messy=True))
    write("tickets_w2.jsonl", rows(400, seed=1, messy=False))
    write("tickets_w3.jsonl", rows(600, seed=2, messy=False))
