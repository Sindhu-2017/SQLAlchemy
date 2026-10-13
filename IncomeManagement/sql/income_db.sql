CREATE TABLE income (
    income_id SERIAL PRIMARY KEY,
    income_date DATE NOT NULL,
    source VARCHAR(100) NOT NULL,
    income_type VARCHAR(50) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    tax_percentage NUMERIC(5,2) NOT NULL DEFAULT 0,
    tax_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    expense_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    net_income NUMERIC(12,2) NOT NULL,
    cash_in_hand NUMERIC(12,2) NOT NULL,
    description TEXT
);

INSERT INTO income (
    income_date,
    source,
    income_type,
    amount,
    tax_percentage,
    tax_amount,
    expense_amount,
    net_income,
    cash_in_hand,
    description
)
VALUES
(
    '2026-10-04', 'Investment', 'Dividend',
    30000, 5, 1500, 3000, 28500, 25500,
    'Dividend income'
),
(
    '2026-10-05', 'Part Time Job', 'Hourly',
    22000, 2, 440, 4000, 21560, 17560,
    'Part time work'
),
(
    '2026-10-06', 'Consulting', 'IT Consulting',
    90000, 12, 10800, 25000, 79200, 54200,
    'IT consulting project'
),
(
    '2026-10-02', 'Freelance', 'Design',
    35000, 8, 2800, 5000, 32200, 27200,
    'Logo design project'
);