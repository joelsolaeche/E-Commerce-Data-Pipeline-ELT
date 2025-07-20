-- TODO: This query will return a table with two columns; order_status, and
-- Ammount. The first one will have the different order status classes and the
-- second one the total ammount of each.

select o.order_status as order_status, count(o.order_status) as Ammount
from olist_orders o 
group by o.order_status