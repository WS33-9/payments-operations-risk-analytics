CREATE OR REPLACE VIEW executive_kpis AS
WITH transaction_summary AS (
    SELECT
        COUNT(*) AS transaction_count,
        ROUND(SUM(amount), 2) AS total_value,
        ROUND(AVG(processing_seconds), 2)
            AS avg_processing_seconds,
        ROUND(
            100.0 * SUM(
                CASE WHEN status = 'Completed' THEN 1 ELSE 0 END
            ) / COUNT(*),
            2
        ) AS success_rate_pct,
        ROUND(
            100.0 * SUM(
                CASE WHEN processing_seconds > 8 THEN 1 ELSE 0 END
            ) / COUNT(*),
            2
        ) AS sla_breach_rate_pct,
        ROUND(
            100.0 * SUM(is_suspicious) / COUNT(*),
            2
        ) AS suspicious_rate_pct
    FROM transactions
)
SELECT
    t.*,
    s.unreconciled_value,
    s.settlement_match_rate_pct
FROM transaction_summary t
CROSS JOIN settlement_summary s;

CREATE OR REPLACE VIEW channel_performance AS
SELECT
    channel,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS transaction_value,
    ROUND(AVG(amount), 2) AS average_transaction_value,
    ROUND(
        100.0 * SUM(
            CASE WHEN status = 'Completed' THEN 1 ELSE 0 END
        ) / COUNT(*),
        2
    ) AS success_rate_pct,
    ROUND(AVG(processing_seconds), 2)
        AS avg_processing_seconds,
    ROUND(
        100.0 * SUM(
            CASE WHEN processing_seconds > 8 THEN 1 ELSE 0 END
        ) / COUNT(*),
        2
    ) AS sla_breach_rate_pct,
    ROUND(
        100.0 * SUM(is_suspicious) / COUNT(*),
        2
    ) AS suspicious_rate_pct
FROM transactions
GROUP BY channel
ORDER BY transaction_value DESC;

CREATE OR REPLACE VIEW province_performance AS
SELECT
    province,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS transaction_value,
    ROUND(
        100.0 * SUM(
            CASE WHEN status = 'Completed' THEN 1 ELSE 0 END
        ) / COUNT(*),
        2
    ) AS success_rate_pct
FROM transactions
GROUP BY province
ORDER BY transaction_value DESC;

CREATE OR REPLACE VIEW risk_summary AS
SELECT
    channel,
    SUM(is_suspicious) AS suspicious_transactions,
    ROUND(
        SUM(
            CASE WHEN is_suspicious = 1 THEN amount ELSE 0 END
        ),
        2
    ) AS suspicious_value,
    ROUND(
        100.0 * SUM(is_suspicious) / COUNT(*),
        2
    ) AS suspicious_rate_pct
FROM transactions
GROUP BY channel
ORDER BY suspicious_value DESC;
