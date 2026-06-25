# Data Dictionary

## transactions.csv

- transaction_id: unique transaction identifier
- transaction_timestamp: date and time of payment attempt
- amount: transaction amount in Canadian dollars
- channel: payment channel
- province: Canadian province code
- merchant_category: merchant industry group
- sending_institution: originating financial institution
- receiving_institution: destination financial institution
- status: Completed, Failed, Reversed, or Pending
- processing_seconds: processing time
- risk_score: synthetic risk score from 0 to 100
- is_high_value: 1 when amount is at least 1,000
- is_suspicious: transparent rule-based risk flag

## settlements.csv

- settlement_id: settlement record identifier
- transaction_id: related payment transaction
- settlement_date: date of settlement
- settlement_amount: settled amount
