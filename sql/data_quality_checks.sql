CREATE OR REPLACE VIEW data_quality_summary AS
SELECT
    'Duplicate transaction IDs' AS control_name,
    COUNT(*) - COUNT(DISTINCT transaction_id) AS issue_count
FROM transactions

UNION ALL

SELECT
    'Invalid or missing transaction status',
    COUNT(*)
FROM transactions
WHERE status IS NULL
   OR status NOT IN ('Completed', 'Failed', 'Reversed', 'Pending')

UNION ALL

SELECT
    'Non-positive transaction amounts',
    COUNT(*)
FROM transactions
WHERE amount <= 0

UNION ALL

SELECT
    'Missing provinces',
    COUNT(*)
FROM transactions
WHERE province IS NULL OR TRIM(province) = ''

UNION ALL

SELECT
    'Duplicate settlement IDs',
    COUNT(*) - COUNT(DISTINCT settlement_id)
FROM settlements

UNION ALL

SELECT
    'Completed transactions without settlement',
    COUNT(*)
FROM transactions t
LEFT JOIN settlements s
    ON t.transaction_id = s.transaction_id
WHERE t.status = 'Completed'
  AND s.transaction_id IS NULL;
