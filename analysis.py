from pathlib import Path

import duckdb

Path("outputs").mkdir(exist_ok=True)

con = duckdb.connect("payments_analytics.duckdb", read_only=True)

queries = {
    "executive_kpis": "SELECT * FROM executive_kpis",
    "channel_performance": "SELECT * FROM channel_performance",
    "province_performance": "SELECT * FROM province_performance",
    "reconciliation_exceptions": """
        SELECT *
        FROM reconciliation_exceptions
        ORDER BY absolute_difference DESC
        LIMIT 100
    """,
    "data_quality_summary": "SELECT * FROM data_quality_summary",
    "risk_summary": "SELECT * FROM risk_summary",
}

for name, query in queries.items():
    df = con.execute(query).df()
    df.to_csv(f"outputs/{name}.csv", index=False)
    print(f"\n{name.upper()}\n")
    print(df.head(10).to_string(index=False))

con.close()
print("\nAnalysis outputs saved in outputs/")
