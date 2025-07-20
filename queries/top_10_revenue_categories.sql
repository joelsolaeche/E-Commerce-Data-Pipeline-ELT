-- TODO: This query will return a table with the top 10 revenue categories in 
-- English, the number of orders and their total revenue. The first column will 
-- be Category, that will contain the top 10 revenue categories; the second one 
-- will be Num_order, with the total amount of orders of each category; and the 
-- last one will be Revenue, with the total revenue of each catgory.
-- HINT: All orders should have a delivered status and the Category and actual 
-- delivery date should be not null.

select p.product_category_name_english as Category, count(distinct(o2.order_id)) as Num_order, round(sum(op.payment_value), 2) as Revenue
from product_category_name_translation p
join olist_products o 
on p.product_category_name = o.product_category_name
join olist_order_items o2 
on o2.product_id = o.product_id
join olist_orders o3
on o3.order_id = o2.order_id
join olist_order_payments op
on o3.order_id = op.order_id
where o3.order_status = 'delivered' 
and p.product_category_name_english is not null 
and o3.order_delivered_customer_date is not null
group by Category
order by Revenue desc
limit 10;