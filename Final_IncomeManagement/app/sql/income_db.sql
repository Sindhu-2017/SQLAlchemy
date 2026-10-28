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


CREATE TABLE expense (
    expense_id SERIAL PRIMARY KEY,
    income_id INTEGER NOT NULL REFERENCES income(income_id) ON DELETE CASCADE,
    expense_name VARCHAR(100) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    payment_method VARCHAR(30) NOT NULL,
    expense_date DATE NOT NULL,
    description TEXT
);

INSERT INTO income (income_date, source, income_type, amount, tax_percentage,
 tax_amount, expense_amount, net_income, cash_in_hand, description)
VALUES
('2026-10-04','Investment','Dividend',30000,5,1500,3000,28500,25500,'Dividend income'),
('2026-10-05','Part Time Job','Hourly',22000,2,440,4000,21560,17560,'Part time work'),
('2026-10-06','Consulting','IT Consulting',90000,12,10800,25000,79200,54200,'IT consulting project'),
('2026-10-02','Freelance','Design',35000,8,2800,5000,32200,27200,'Logo design project');


CREATE OR REPLACE PROCEDURE create_expense(
    IN p_income_id INTEGER,
    IN p_expense_name VARCHAR(100),
    IN p_amount NUMERIC(12, 2),
    IN p_payment_method VARCHAR(30),
    IN p_expense_date DATE,
    IN p_description TEXT,
    INOUT p_expense_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO expense (
        income_id,
        expense_name,
        amount,
        payment_method,
        expense_date,
        description
    )
    VALUES (
        p_income_id,
        p_expense_name,
        p_amount,
        p_payment_method,
        p_expense_date,
        p_description
    )
    RETURNING expense_id INTO p_expense_id;
END;
$$;


CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
	role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);


