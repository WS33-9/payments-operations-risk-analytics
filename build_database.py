from pathlib import Path

import duckdb

transaction_file = Path("data/transactions.csv")
settlement_file = Path("data/settlements.csv")

if not transaction_file.exists() or not settlement_file.exists():
    raise FileNotFoundError(
        "Run generate_data.py first. "
        "The data folder must contain transactions.csv and settlements.csv."
    )

con = duckdb.connect("payments_analytics.duckdb")

con.execute("""
CREATE OR REPLACE TABLE transactions AS
SELECT
    CAST(transaction_id AS VARCHAR) AS transaction_id,
    CAST(transaction_timestamp AS TIMESTAMP) AS transaction_timestamp,
    CAST(amount AS DOUBLE) AS amount,
    CAST(channel AS VARCHAR) AS channel,
    CAST(province AS VARCHAR) AS province,
    CAST(merchant_category AS VARCHAR) AS merchant_category,
    CAST(sending_institution AS VARCHAR) AS sending_institution,
    CAST(receiving_institution AS VARCHAR) AS receiving_institution,
    CAST(status AS VARCHAR) AS status,
    CAST(processing_seconds AS DOUBLE) AS processing_seconds,
    CAST(risk_score AS DOUBLE) AS risk_score,
    CAST(is_high_value AS INTEGER) AS is_high_value,
    CAST(is_suspicious AS INTEGER) AS is_suspicious
FROM read_csv_auto('data/transactions.csv', header=true);
""")

con.execute("""
CREATE OR REPLACE TABLE settlements AS
SELECT
    CAST(settlement_id AS VARCHAR) AS settlement_id,
    CAST(transaction_id AS VARCHAR) AS transaction_id,
    CAST(settlement_date AS DATE) AS settlement_date,
    CAST(settlement_amount AS DOUBLE) AS settlement_amount
FROM read_csv_auto('data/settlements.csv', header=true);
""")

sql_files = [
    "sql/data_quality_checks.sql",
    "sql/reconciliation_analysis.sql",
    "sql/operational_kpis.sql",
]

for file_name in sql_files:
    sql_text = Path(file_name).read_text(encoding="utf-8")
    con.execute(sql_text)

print("Database created: payments_analytics.duckdb")
print(
    "Transactions:",
    con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0],
)
print(
    "Settlements:",
    con.execute("SELECT COUNT(*) FROM settlements").fetchone()[0],
)

con.close()
