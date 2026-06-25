# Executive Summary

## Business Problem

A digital-payments organization processes a high volume of transactions across multiple channels, financial institutions, merchant categories, and Canadian provinces.

Finance, Operations, Risk, Product, and executive stakeholders need standardized reporting to monitor payment performance, settlement activity, operational service levels, suspicious transaction indicators, and data-quality issues.

Without a centralized reporting solution, it may be difficult to identify settlement exceptions, assess financial exposure, compare channel performance, and prioritize operational investigations.

## Project Objective

The objective of this project is to create an end-to-end payments operations, risk, and finance intelligence platform using Python, SQL, DuckDB, Streamlit, and Plotly.

The solution is designed to:

* Monitor transaction volume and value
* Measure payment success and failure rates
* Track processing time and service-level breaches
* Reconcile completed transactions against settlement records
* Identify missing settlements and amount mismatches
* Monitor suspicious transaction indicators
* Detect data-quality issues
* Compare performance across payment channels and provinces
* Provide management with actionable recommendations

## Solution Overview

The project generates synthetic transaction and settlement data to simulate a digital-payments environment.

Python is used to create and prepare the data. DuckDB stores the transaction and settlement records and executes SQL analysis.

SQL controls identify:

* Duplicate transaction and settlement records
* Invalid transaction statuses
* Non-positive transaction amounts
* Missing province values
* Completed transactions without settlement records
* Settlement amount mismatches
* Unreconciled transaction value

A Streamlit dashboard presents operational, financial, and risk KPIs for management review.

## Key Performance Indicators

The dashboard tracks:

* Total transaction value
* Total transaction count
* Average transaction value
* Payment success rate
* Average processing time
* Service-level breach rate
* Settlement match rate
* Unreconciled value
* Suspicious transaction rate
* Channel performance
* Province performance
* Data-quality exception counts

## Key Findings

## Key Findings

* The platform analyzed **50,000 payment transactions** with a total value of approximately **$4.59 million**.

* Overall payment performance was stable, with a **90.94% transaction success rate** and an average processing time of **4.54 seconds**.

* The overall **SLA breach rate was 4.09%**, meaning approximately one in every 24 transactions exceeded the assumed eight-second processing threshold.

* The settlement process achieved a **98.48% match rate**. However, reconciliation controls identified approximately **$25,172.55 in unreconciled transaction value** requiring further investigation.

* Data-quality controls identified **236 completed transactions without a corresponding settlement record** and **90 duplicate settlement IDs**. No duplicate transaction IDs, invalid statuses, non-positive transaction amounts, or missing province values were detected.

* **Online Checkout** generated the highest transaction value at approximately **$1.17 million**, representing the largest payment channel by value.

* **Debit** recorded the highest channel success rate at **91.26%**, while **Interac e-Transfer** recorded the lowest at **90.80%**. The variation across channels was relatively small, suggesting broadly consistent payment performance.

* Average processing time was consistent across all channels at approximately **4.53 to 4.55 seconds**. Online Checkout had the highest SLA breach rate at **4.21%**, while Mobile Wallet had the lowest at **3.91%**.

* Ontario generated the highest provincial transaction value at approximately **$783,069**, while Nova Scotia generated the lowest at approximately **$747,223**. Transaction activity was otherwise distributed relatively evenly across the six provinces.

* Rule-based monitoring identified **four suspicious transactions** with a combined value of approximately **$181.19**. Interac e-Transfer accounted for the highest suspicious transaction count and value, although the overall suspicious transaction rate remained very low at **0.01%**.

* The largest individual reconciliation exception was a **missing settlement of $615.37**. The highest-value exceptions were primarily caused by missing settlement records rather than small amount mismatches.

## Overall Assessment

The analysis indicates that the simulated payments environment is operationally stable, with consistent channel performance, strong settlement matching, and limited suspicious activity. The primary improvement opportunity is strengthening settlement controls through automated duplicate detection, missing-settlement alerts, and risk-based exception prioritization.


## Management Recommendations

1. Implement daily automated transaction-to-settlement reconciliation.

2. Prioritize reconciliation exceptions based on financial value, exception type, and age.

3. Establish alerts when settlement-match rates or payment success rates fall below defined thresholds.

4. Investigate payment channels with elevated failure rates, processing times, or service-level breaches.

5. Standardize transaction-status and settlement-status definitions across Finance and Operations.

6. Create a formal exception-management workflow with assigned owners, investigation status, and resolution timelines.

7. Review suspicious transactions using transparent business rules before applying more advanced fraud-detection models.

8. Monitor data-quality controls as part of recurring management reporting.

## Business Value

The solution demonstrates how automated reporting can improve:

* Financial visibility
* Settlement reconciliation
* Operational performance monitoring
* Exception prioritization
* Risk awareness
* Data governance
* Cross-functional decision-making
* Management reporting efficiency

The platform could reduce reliance on manual spreadsheet reporting and provide Finance, Operations, Risk, and Product teams with a consistent source of performance information.

## Assumptions and Limitations

* The project uses synthetic data and does not represent Interac or any real payment network.
* The suspicious transaction indicators are rule-based and are not a production fraud-detection model.
* Unreconciled value represents items requiring investigation and should not be interpreted as confirmed financial loss.
* The service-level threshold of eight seconds is a project assumption.
* The settlement process is simplified and does not model the full complexity of a real financial network.
* Regulatory reporting, privacy requirements, chargebacks, and fraud investigations are outside the current project scope.

## Tools Used

* Python
* pandas
* NumPy
* DuckDB
* SQL
* Streamlit
* Plotly
* VS Code
* GitHub
