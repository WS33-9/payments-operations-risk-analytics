CREATE OR REPLACE VIEW reconciliation_exceptions AS
SELECT
    t.transaction_id,
    t.transaction_timestamp,
    t.amount AS transaction_amount,
    s.settlement_id,
    s.settlement_date,
    s.settlement_amount,
    ROUND(
        COALESCE(s.settlement_amount, 0) - t.amount,
        2
    ) AS settlement_difference,
    ROUND(
        ABS(COALESCE(s.settlement_amount, 0) - t.amount),
        2
    ) AS absolute_difference,
    CASE
        WHEN s.transaction_id IS NULL THEN 'Missing Settlement'
        WHEN ABS(s.settlement_amount - t.amount) > 0.01
            THEN 'Amount Mismatch'
        ELSE 'Matched'
    END AS reconciliation_status
FROM transactions t
LEFT JOIN settlements s
    ON t.transaction_id = s.transaction_id
WHERE t.status = 'Completed';

CREATE OR REPLACE VIEW settlement_summary AS
SELECT
    COUNT(*) AS completed_transactions,
    SUM(
        CASE
            WHEN reconciliation_status = 'Matched'
            THEN 1 ELSE 0
        END
    ) AS matched_transactions,
    SUM(
        CASE
            WHEN reconciliation_status <> 'Matched'
            THEN 1 ELSE 0
        END
    ) AS exception_transactions,
    ROUND(
        SUM(
            CASE
                WHEN reconciliation_status <> 'Matched'
                THEN absolute_difference
                ELSE 0
            END
        ),
        2
    ) AS unreconciled_value,
    ROUND(
        100.0
        * SUM(
            CASE
                WHEN reconciliation_status = 'Matched'
                THEN 1 ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS settlement_match_rate_pct
FROM reconciliation_exceptions;
