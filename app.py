from pathlib import Path
import subprocess
import sys

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATABASE_FILE = Path("payments_analytics.duckdb")


def prepare_database():
    if not DATABASE_FILE.exists():
        subprocess.run(
            [sys.executable, "generate_data.py"],
            check=True,
        )

        subprocess.run(
            [sys.executable, "build_database.py"],
            check=True,
        )


prepare_database()

st.set_page_config(
    page_title="Payments Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {background:#F4F7FB;}
.block-container {padding-top:1.25rem; max-width:1500px;}
section[data-testid="stSidebar"] {background:#0B1220;}
section[data-testid="stSidebar"] * {color:#F8FAFC;}
.hero {
    padding:24px 28px; border-radius:16px; color:white; margin-bottom:18px;
    background:linear-gradient(135deg,#0F172A,#1D4E89);
    box-shadow:0 8px 24px rgba(15,23,42,.14);
}
.hero h1 {margin:0 0 6px 0; font-size:2rem;}
.hero p {margin:0; color:#D6E3F0;}
div[data-testid="stMetric"] {
    background:white; border:1px solid #E2E8F0; border-radius:14px;
    padding:16px 18px; box-shadow:0 4px 14px rgba(15,23,42,.05);
}
div[data-testid="stMetricLabel"] {color:#64748B; font-weight:600;}
div[data-testid="stMetricValue"] {color:#0F172A; font-weight:700;}
.section {font-size:1.08rem; font-weight:700; color:#0F172A; margin:14px 0 8px;}
.note {
    background:white; border:1px solid #E2E8F0; border-left:5px solid #2563EB;
    border-radius:12px; padding:16px 18px; margin:8px 0;
}
.warn {
    background:#FFF7ED; border:1px solid #FED7AA; border-left:5px solid #EA580C;
    border-radius:12px; padding:16px 18px; margin:8px 0;
}
.good {
    background:#F0FDF4; border:1px solid #BBF7D0; border-left:5px solid #16A34A;
    border-radius:12px; padding:16px 18px; margin:8px 0;
}
.stTabs [data-baseweb="tab"] {
    background:#E2E8F0; border-radius:10px 10px 0 0; padding:10px 16px;
    color:#334155; font-weight:600;
}
.stTabs [aria-selected="true"] {background:white; color:#0F172A;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    con = duckdb.connect(str(DATABASE_FILE), read_only=True)
    tx = con.execute("SELECT * FROM transactions").df()
    rec = con.execute("SELECT * FROM reconciliation_exceptions").df()
    quality = con.execute("SELECT * FROM data_quality_summary").df()
    con.close()
    tx["transaction_timestamp"] = pd.to_datetime(tx["transaction_timestamp"])
    return tx, rec, quality

tx, rec, quality = load_data()

st.sidebar.markdown("## Payments Intelligence")
st.sidebar.caption("Executive reporting workspace")
st.sidebar.markdown("---")

min_date = tx["transaction_timestamp"].min().date()
max_date = tx["transaction_timestamp"].max().date()

dates = st.sidebar.date_input(
    "Reporting period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

channels = st.sidebar.multiselect(
    "Payment channel",
    sorted(tx["channel"].unique()),
    default=sorted(tx["channel"].unique()),
)

provinces = st.sidebar.multiselect(
    "Province",
    sorted(tx["province"].unique()),
    default=sorted(tx["province"].unique()),
)

statuses = st.sidebar.multiselect(
    "Transaction status",
    sorted(tx["status"].unique()),
    default=sorted(tx["status"].unique()),
)

if isinstance(dates, tuple) and len(dates) == 2:
    start_date, end_date = dates
else:
    start_date, end_date = min_date, max_date

data = tx[
    (tx["transaction_timestamp"].dt.date >= start_date)
    & (tx["transaction_timestamp"].dt.date <= end_date)
    & tx["channel"].isin(channels)
    & tx["province"].isin(provinces)
    & tx["status"].isin(statuses)
].copy()

if data.empty:
    st.warning("No records match the selected filters.")
    st.stop()

completed_ids = set(data.loc[data["status"] == "Completed", "transaction_id"])
filtered_rec = rec[rec["transaction_id"].isin(completed_ids)].copy()

transaction_count = len(data)
transaction_value = data["amount"].sum()
avg_transaction = data["amount"].mean()
success_rate = data["status"].eq("Completed").mean() * 100
avg_processing = data["processing_seconds"].mean()
sla_breach = data["processing_seconds"].gt(8).mean() * 100
suspicious_rate = data["is_suspicious"].mean() * 100

if filtered_rec.empty:
    match_rate = 0.0
    unreconciled = 0.0
    exception_count = 0
else:
    matched = filtered_rec["reconciliation_status"].eq("Matched")
    match_rate = matched.mean() * 100
    unreconciled = filtered_rec.loc[~matched, "absolute_difference"].sum()
    exception_count = (~matched).sum()

channel_perf = (
    data.groupby("channel", as_index=False)
    .agg(
        transaction_count=("transaction_id", "count"),
        transaction_value=("amount", "sum"),
        average_transaction=("amount", "mean"),
        success_rate=("status", lambda s: s.eq("Completed").mean() * 100),
        average_processing=("processing_seconds", "mean"),
        sla_breach_rate=("processing_seconds", lambda s: s.gt(8).mean() * 100),
        suspicious_rate=("is_suspicious", lambda s: s.mean() * 100),
    )
)

province_perf = (
    data.groupby("province", as_index=False)
    .agg(
        transaction_count=("transaction_id", "count"),
        transaction_value=("amount", "sum"),
        success_rate=("status", lambda s: s.eq("Completed").mean() * 100),
    )
)

daily = (
    data.assign(day=data["transaction_timestamp"].dt.date)
    .groupby("day", as_index=False)
    .agg(
        transaction_value=("amount", "sum"),
        transaction_count=("transaction_id", "count"),
    )
)

status_mix = (
    data.groupby("status", as_index=False)
    .agg(transaction_count=("transaction_id", "count"))
)

merchant_risk = (
    data.groupby("merchant_category", as_index=False)
    .agg(
        suspicious_transactions=("is_suspicious", "sum"),
        suspicious_value=("amount", lambda s: s[data.loc[s.index, "is_suspicious"].eq(1)].sum()),
    )
)

st.markdown("""
<div class="hero">
  <h1>Payments Operations, Risk & Finance Intelligence</h1>
  <p>Executive monitoring of transaction performance, settlement reconciliation, service levels, risk indicators, and data quality.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section">Executive Snapshot</div>', unsafe_allow_html=True)

r1 = st.columns(4)
r1[0].metric("Transaction Value", f"${transaction_value:,.0f}")
r1[1].metric("Transactions", f"{transaction_count:,}")
r1[2].metric("Success Rate", f"{success_rate:.2f}%")
r1[3].metric("Average Transaction", f"${avg_transaction:,.2f}")

r2 = st.columns(4)
r2[0].metric("Settlement Match", f"{match_rate:.2f}%")
r2[1].metric("Unreconciled Value", f"${unreconciled:,.2f}")
r2[2].metric("SLA Breach Rate", f"{sla_breach:.2f}%")
r2[3].metric("Suspicious Rate", f"{suspicious_rate:.2f}%")

overview, operations, reconciliation, risk, quality_tab = st.tabs(
    [
        "Executive Overview",
        "Operations",
        "Reconciliation",
        "Risk",
        "Data Quality",
    
    ]
)

with overview:
    left, right = st.columns([1.7, 1])

    with left:
        fig = px.line(
            daily,
            x="day",
            y="transaction_value",
            title="Daily Transaction Value",
        )
        fig.update_traces(line=dict(color="#2563EB", width=2.5))
        fig.update_layout(
            template="plotly_white",
            height=390,
            margin=dict(l=10, r=10, t=55, b=10),
            xaxis_title="",
            yaxis_title="Transaction Value ($)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.pie(
            status_mix,
            names="status",
            values="transaction_count",
            hole=.62,
            title="Transaction Status Mix",
            color="status",
            color_discrete_map={
                "Completed":"#16A34A",
                "Failed":"#DC2626",
                "Reversed":"#F59E0B",
                "Pending":"#64748B",
            },
        )
        fig.update_layout(
            template="plotly_white",
            height=390,
            margin=dict(l=10, r=10, t=55, b=10),
            legend_title_text="",
        )
        st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        channel_perf.sort_values("transaction_value"),
        x="transaction_value",
        y="channel",
        orientation="h",
        color="success_rate",
        color_continuous_scale=["#CBD5E1", "#60A5FA", "#1D4ED8"],
        text_auto=".2s",
        title="Transaction Value by Payment Channel",
    )
    fig.update_layout(
        template="plotly_white",
        height=420,
        margin=dict(l=10, r=10, t=55, b=10),
        xaxis_title="Transaction Value ($)",
        yaxis_title="",
        coloraxis_colorbar_title="Success %",
    )
    st.plotly_chart(fig, use_container_width=True)

    best = channel_perf.sort_values("success_rate", ascending=False).iloc[0]
    slowest = channel_perf.sort_values("average_processing", ascending=False).iloc[0]

    a, b = st.columns(2)
    a.markdown(
        f'<div class="good"><strong>Strongest success performance</strong><br>{best["channel"]} recorded the highest success rate at <strong>{best["success_rate"]:.2f}%</strong>.</div>',
        unsafe_allow_html=True,
    )
    b.markdown(
        f'<div class="warn"><strong>Processing-time watch item</strong><br>{slowest["channel"]} had the highest average processing time at <strong>{slowest["average_processing"]:.2f} seconds</strong>.</div>',
        unsafe_allow_html=True,
    )

with operations:
    left, right = st.columns(2)

    with left:
        fig = px.bar(
            channel_perf.sort_values("average_processing"),
            x="average_processing",
            y="channel",
            orientation="h",
            text_auto=".2f",
            title="Average Processing Time by Channel",
            color="average_processing",
            color_continuous_scale=["#DBEAFE", "#2563EB"],
        )
        fig.update_layout(
            template="plotly_white",
            height=400,
            xaxis_title="Seconds",
            yaxis_title="",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            channel_perf.sort_values("sla_breach_rate"),
            x="sla_breach_rate",
            y="channel",
            orientation="h",
            text_auto=".2f",
            title="SLA Breach Rate by Channel",
            color="sla_breach_rate",
            color_continuous_scale=["#FEF3C7", "#DC2626"],
        )
        fig.update_layout(
            template="plotly_white",
            height=400,
            xaxis_title="SLA Breach Rate (%)",
            yaxis_title="",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        province_perf.sort_values("transaction_value"),
        x="transaction_value",
        y="province",
        orientation="h",
        color="success_rate",
        color_continuous_scale=["#E2E8F0", "#0F766E"],
        text_auto=".2s",
        title="Transaction Value by Province",
    )
    fig.update_layout(
        template="plotly_white",
        height=420,
        xaxis_title="Transaction Value ($)",
        yaxis_title="",
        coloraxis_colorbar_title="Success %",
    )
    st.plotly_chart(fig, use_container_width=True)

    display = channel_perf.rename(columns={
        "channel":"Channel",
        "transaction_count":"Transactions",
        "transaction_value":"Transaction Value",
        "average_transaction":"Average Transaction",
        "success_rate":"Success Rate (%)",
        "average_processing":"Average Processing (s)",
        "sla_breach_rate":"SLA Breach Rate (%)",
        "suspicious_rate":"Suspicious Rate (%)",
    })
    st.dataframe(
        display.style.format({
            "Transaction Value":"${:,.2f}",
            "Average Transaction":"${:,.2f}",
            "Success Rate (%)":"{:.2f}",
            "Average Processing (s)":"{:.2f}",
            "SLA Breach Rate (%)":"{:.2f}",
            "Suspicious Rate (%)":"{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

with reconciliation:
    c = st.columns(4)
    c[0].metric("Completed Payments", f"{len(completed_ids):,}")
    c[1].metric("Exceptions", f"{exception_count:,}")
    c[2].metric("Settlement Match", f"{match_rate:.2f}%")
    c[3].metric("Unreconciled Value", f"${unreconciled:,.2f}")

    if not filtered_rec.empty:
        rec_mix = (
            filtered_rec.groupby("reconciliation_status", as_index=False)
            .agg(transaction_count=("transaction_id", "count"))
        )
        left, right = st.columns([1, 1.4])

        with left:
            fig = px.pie(
                rec_mix,
                names="reconciliation_status",
                values="transaction_count",
                hole=.60,
                title="Reconciliation Status",
                color="reconciliation_status",
                color_discrete_map={
                    "Matched":"#16A34A",
                    "Missing Settlement":"#DC2626",
                    "Amount Mismatch":"#F59E0B",
                },
            )
            fig.update_layout(
                template="plotly_white",
                height=410,
                legend_title_text="",
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            exposure = (
                filtered_rec[filtered_rec["reconciliation_status"] != "Matched"]
                .groupby("reconciliation_status", as_index=False)
                .agg(
                    exception_count=("transaction_id", "count"),
                    financial_exposure=("absolute_difference", "sum"),
                )
            )
            fig = px.bar(
                exposure,
                x="reconciliation_status",
                y="financial_exposure",
                color="reconciliation_status",
                text_auto=".2f",
                title="Financial Exposure by Exception Type",
                color_discrete_map={
                    "Missing Settlement":"#DC2626",
                    "Amount Mismatch":"#F59E0B",
                },
            )
            fig.update_layout(
                template="plotly_white",
                height=410,
                xaxis_title="",
                yaxis_title="Unreconciled Value ($)",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        priority = (
            filtered_rec[filtered_rec["reconciliation_status"] != "Matched"]
            .sort_values("absolute_difference", ascending=False)
            .head(100)
        )
        st.dataframe(
            priority.style.format({
                "transaction_amount":"${:,.2f}",
                "settlement_amount":"${:,.2f}",
                "settlement_difference":"${:,.2f}",
                "absolute_difference":"${:,.2f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

with risk:
    suspicious = data[data["is_suspicious"] == 1].copy()

    fig = px.bar(
        merchant_risk.sort_values("suspicious_value"),
        x="suspicious_value",
        y="merchant_category",
        orientation="h",
        color="suspicious_transactions",
        color_continuous_scale=["#FFEDD5", "#C2410C"],
        text_auto=".2s",
        title="Suspicious Transaction Value by Merchant Category",
    )
    fig.update_layout(
        template="plotly_white",
        height=430,
        xaxis_title="Suspicious Transaction Value ($)",
        yaxis_title="",
        coloraxis_colorbar_title="Count",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        suspicious.sort_values(["risk_score", "amount"], ascending=False)
        .head(100)
        .style.format({
            "amount":"${:,.2f}",
            "processing_seconds":"{:.2f}",
            "risk_score":"{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        '<div class="warn"><strong>Important limitation</strong><br>Suspicious activity is identified using transparent portfolio rules. It is not a production fraud-detection model.</div>',
        unsafe_allow_html=True,
    )

with quality_tab:
    total_issues = int(quality["issue_count"].sum())

    c = st.columns(3)
    c[0].metric("Control Checks", f"{len(quality):,}")
    c[1].metric("Issues Identified", f"{total_issues:,}")
    c[2].metric(
        "Indicative Clean Rate",
        f"{max(0, 100 - total_issues / max(transaction_count, 1) * 100):.2f}%",
    )

    fig = px.bar(
        quality.sort_values("issue_count"),
        x="issue_count",
        y="control_name",
        orientation="h",
        color="issue_count",
        color_continuous_scale=["#E2E8F0", "#7C3AED"],
        text_auto=True,
        title="Data Quality Issues by Control",
    )
    fig.update_layout(
        template="plotly_white",
        height=450,
        xaxis_title="Issue Count",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(quality, use_container_width=True, hide_index=True)


 

st.markdown('<div class="section">Executive Recommendations</div>', unsafe_allow_html=True)

a, b, c = st.columns(3)
a.markdown(
    '<div class="note"><strong>1. Automate reconciliation</strong><br>Run daily payment-to-settlement matching and prioritize exceptions by exposure and age.</div>',
    unsafe_allow_html=True,
)
b.markdown(
    '<div class="note"><strong>2. Strengthen monitoring</strong><br>Create alerts for declining success rates, SLA breaches, and channel-level delays.</div>',
    unsafe_allow_html=True,
)
c.markdown(
    '<div class="note"><strong>3. Formalize risk review</strong><br>Use transparent rules to prioritize review and document investigation outcomes.</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Portfolio project using synthetic data. This dashboard does not represent Interac or any real payment network."
)
