-- TODO: This query will return a table with the revenue by month and year. It
-- will have different columns: month_no, with the month numbers going from 01
-- to 12; month, with the 3 first letters of each month (e.g. Jan, Feb);
-- Year2016, with the revenue per month of 2016 (0.00 if it doesn't exist);
-- Year2017, with the revenue per month of 2017 (0.00 if it doesn't exist) and
-- Year2018, with the revenue per month of 2018 (0.00 if it doesn't exist).


SELECT
    STRFTIME('%m', orders.order_delivered_customer_date) as month_no,
    CASE STRFTIME('%m', orders.order_delivered_customer_date)
        WHEN '01' THEN 'Jan'
        WHEN '02' THEN 'Feb'
        WHEN '03' THEN 'Mar'
        WHEN '04' THEN 'Apr'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'Jun'
        WHEN '07' THEN 'Jul'
        WHEN '08' THEN 'Aug'
        WHEN '09' THEN 'Sep'
        WHEN '10' THEN 'Oct'
        WHEN '11' THEN 'Nov'
        WHEN '12' THEN 'Dec'
    END AS month,
    SUM(CASE WHEN STRFTIME('%Y', orders.order_delivered_customer_date) = '2016' THEN payments.min_payment_value ELSE 0 END) as Year2016,
    SUM(CASE WHEN STRFTIME('%Y', orders.order_delivered_customer_date) = '2017' THEN payments.min_payment_value ELSE 0 END) as Year2017,
    SUM(CASE WHEN STRFTIME('%Y', orders.order_delivered_customer_date) = '2018' THEN payments.min_payment_value ELSE 0 END) as Year2018
FROM (
    SELECT
        order_id, order_purchase_timestamp,
        order_delivered_customer_date, order_status, customer_id
    FROM olist_orders
) AS orders
JOIN (
    SELECT 
    MIN(payment_value) as min_payment_value,
    order_id
    FROM olist_order_payments
    GROUP BY
    order_id
    ) as payments
ON
    payments.order_id = orders.order_id
WHERE 
    STRFTIME('%Y', orders.order_delivered_customer_date) IN ('2016', '2017', '2018')
    AND orders.order_delivered_customer_date IS NOT NULL
    AND orders.order_purchase_timestamp IS NOT NULL
    AND orders.order_status in ('delivered', 'shipped', 'invoiced', 'approved', 'created')
    AND month_no IS NOT NULL
GROUP BY
    month_no
ORDER BY
    month_no ASC;