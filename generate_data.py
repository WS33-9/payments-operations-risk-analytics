from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

RANDOM_SEED = 42
NUMBER_OF_TRANSACTIONS = 50_000

rng = np.random.default_rng(RANDOM_SEED)
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

channels = ["Interac e-Transfer", "Debit", "Online Checkout", "Mobile Wallet"]
provinces = ["ON", "QC", "BC", "AB", "MB", "NS"]
merchant_categories = [
    "Grocery",
    "Restaurants",
    "Retail",
    "Travel",
    "Utilities",
    "Entertainment",
]
sending_institutions = ["Bank A", "Bank B", "Bank C", "Credit Union D"]
receiving_institutions = ["Bank A", "Bank B", "Bank C", "Credit Union D"]

start = datetime(2025, 1, 1)

timestamps = [
    start + timedelta(
        minutes=int(rng.integers(0, 365 * 24 * 60))
    )
    for _ in range(NUMBER_OF_TRANSACTIONS)
]

amounts = np.round(
    np.maximum(
        1,
        rng.lognormal(mean=4.2, sigma=0.8, size=NUMBER_OF_TRANSACTIONS),
    ),
    2,
)

statuses = rng.choice(
    ["Completed", "Failed", "Reversed", "Pending"],
    size=NUMBER_OF_TRANSACTIONS,
    p=[0.91, 0.05, 0.025, 0.015],
)

processing_seconds = np.maximum(
    1,
    rng.normal(4.5, 2.0, NUMBER_OF_TRANSACTIONS),
).round(2)

risk_scores = np.clip(
    rng.beta(2, 10, NUMBER_OF_TRANSACTIONS) * 100,
    0,
    100,
).round(2)

transactions = pd.DataFrame(
    {
        "transaction_id": [
            f"TXN{1000000 + i}" for i in range(NUMBER_OF_TRANSACTIONS)
        ],
        "transaction_timestamp": timestamps,
        "amount": amounts,
        "channel": rng.choice(channels, NUMBER_OF_TRANSACTIONS),
        "province": rng.choice(provinces, NUMBER_OF_TRANSACTIONS),
        "merchant_category": rng.choice(
            merchant_categories,
            NUMBER_OF_TRANSACTIONS,
        ),
        "sending_institution": rng.choice(
            sending_institutions,
            NUMBER_OF_TRANSACTIONS,
        ),
        "receiving_institution": rng.choice(
            receiving_institutions,
            NUMBER_OF_TRANSACTIONS,
        ),
        "status": statuses,
        "processing_seconds": processing_seconds,
        "risk_score": risk_scores,
    }
)

transactions["is_high_value"] = (
    transactions["amount"] >= 1000
).astype(int)

transactions["is_suspicious"] = (
    (transactions["risk_score"] >= 70)
    | (
        (transactions["amount"] >= 2000)
        & (
            pd.to_datetime(
                transactions["transaction_timestamp"]
            ).dt.hour.isin([0, 1, 2, 3, 4])
        )
    )
).astype(int)

settlements = transactions[
    transactions["status"] == "Completed"
][
    ["transaction_id", "transaction_timestamp", "amount"]
].copy()

settlements["settlement_id"] = [
    f"SET{2000000 + i}" for i in range(len(settlements))
]

settlements["settlement_date"] = (
    pd.to_datetime(settlements["transaction_timestamp"]).dt.date
    + pd.to_timedelta(
        rng.choice([0, 1, 2], len(settlements), p=[0.86, 0.11, 0.03]),
        unit="D",
    )
)

settlements["settlement_amount"] = settlements["amount"]

mismatch_mask = rng.random(len(settlements)) < 0.01
settlements.loc[mismatch_mask, "settlement_amount"] = (
    settlements.loc[mismatch_mask, "settlement_amount"]
    - rng.uniform(0.01, 10, mismatch_mask.sum())
).round(2)

missing_mask = rng.random(len(settlements)) < 0.005
settlements = settlements.loc[~missing_mask].copy()

duplicate_rows = settlements.sample(
    n=max(1, int(len(settlements) * 0.002)),
    random_state=RANDOM_SEED,
)
settlements = pd.concat([settlements, duplicate_rows], ignore_index=True)

transactions.to_csv(
    data_dir / "transactions.csv",
    index=False,
)

settlements[
    [
        "settlement_id",
        "transaction_id",
        "settlement_date",
        "settlement_amount",
    ]
].to_csv(
    data_dir / "settlements.csv",
    index=False,
)

print(f"Created {len(transactions):,} transactions")
print(f"Created {len(settlements):,} settlement records")
print("Files saved in data/")
