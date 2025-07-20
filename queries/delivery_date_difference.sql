-- TODO: This query will return a table with two columns; State, and 
-- Delivery_Difference. The first one will have the letters that identify the 
-- states, and the second one the average difference between the estimate 
-- delivery date and the date when the items were actually delivered to the 
-- customer.
-- HINTS:
-- 1. You can use the julianday function to convert a date to a number.
-- 2. You can use the CAST function to convert a number to an integer.
-- 3. You can use the STRFTIME function to convert a order_delivered_customer_date to a string removing hours, minutes and seconds.
-- 4. order_status == 'delivered' AND order_delivered_customer_date IS NOT NULL
-- Use olist_orders and olist_customers tables

SELECT
  customers.customer_state AS State,
  CAST(
    AVG(
      julianday(strftime('%Y-%m-%d', orders.order_estimated_delivery_date )) -
      julianday(strftime('%Y-%m-%d', orders.order_delivered_customer_date ))
    ) AS INTEGER
  ) AS Delivery_Difference
FROM
  olist_customers AS customers
JOIN
  olist_orders AS orders
  ON customers.customer_id = orders.customer_id
WHERE
  orders.order_status = 'delivered'
  AND orders.order_delivered_customer_date IS NOT NULL
GROUP BY
  customers.customer_state
ORDER BY
  Delivery_Difference ASC;