"""
Generate a small synthetic telecom-churn table
"""

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "churn.csv")


def make_df(n: int = 2000, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    tenure = rng.integers(1, 72, size=n)
    monthly = rng.normal(70, 25, size=n).clip(15, 150)
    contract = rng.choice(["month", "year", "two_year"], size=n, p=[0.55, 0.3, 0.15])
    support_calls = rng.poisson(1.2, size=n)
    is_fiber = rng.random(size=n) < 0.45
    paperless = rng.random(size=n) < 0.6

    logit = (
        -1.2
        - 0.04 * tenure
        + 0.012 * monthly
        + 0.35 * support_calls
        + 0.6 * is_fiber
        + 0.2 * paperless
        + np.where(contract == "month", 0.9, np.where(contract == "year", 0.0, -0.7))
    )
    p = 1 / (1 + np.exp(-logit))
    churn = (rng.random(size=n) < p).astype(int)

    return pd.DataFrame(
        {
            "tenure_months": tenure,
            "monthly_charges": monthly.round(2),
            "contract": contract,
            "support_calls": support_calls,
            "is_fiber": is_fiber.astype(int),
            "paperless_billing": paperless.astype(int),
            "churn": churn,
        }
    )


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df = make_df()
    df.to_csv(OUT, index=False)
    print(f"wrote {len(df)} rows to {OUT}, churn rate {df['churn'].mean():.3f}")
