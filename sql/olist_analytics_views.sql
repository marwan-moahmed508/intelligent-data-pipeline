
-- 1. Overall order KPIs
CREATE OR REPLACE VIEW vw_order_kpis AS
SELECT
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
    ) AS delivered_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'canceled'
    ) AS canceled_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'shipped'
    ) AS shipped_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'processing'
    ) AS processing_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'unavailable'
    ) AS unavailable_orders,
    COUNT(*) FILTER (
        WHERE EXISTS (
            SELECT 1
            FROM order_items i
            WHERE i.order_id = orders.order_id
        )
    ) AS orders_with_items
FROM orders;


-- 2. Sales KPIs
-- Aggregate order items before joining to orders.
CREATE OR REPLACE VIEW vw_sales_kpis AS
WITH order_values AS (
    SELECT
        order_id,
        SUM(price) AS item_gmv,
        SUM(freight_value) AS freight_value
    FROM order_items
    GROUP BY order_id
)
SELECT
    COALESCE(SUM(ov.item_gmv), 0) AS item_gmv_all_orders,
    COALESCE(
        SUM(ov.item_gmv) FILTER (
            WHERE o.order_status = 'delivered'
        ), 0
    ) AS delivered_item_gmv,
    COALESCE(SUM(ov.freight_value), 0) AS total_freight,
    COALESCE(
        SUM(ov.freight_value) FILTER (
            WHERE o.order_status = 'delivered'
        ), 0
    ) AS delivered_freight
FROM orders o
LEFT JOIN order_values ov
    ON o.order_id = ov.order_id;


-- 3. Monthly sales
CREATE OR REPLACE VIEW vw_monthly_sales AS
WITH order_values AS (
    SELECT
        order_id,
        SUM(price) AS item_gmv,
        SUM(freight_value) AS freight_value
    FROM order_items
    GROUP BY order_id
)
SELECT
    DATE_TRUNC(
        'month',
        o.order_purchase_timestamp
    )::date AS sales_month,

    COUNT(*) AS total_orders,

    COUNT(*) FILTER (
        WHERE o.order_status = 'delivered'
    ) AS delivered_orders,

    COUNT(*) FILTER (
        WHERE o.order_status = 'canceled'
    ) AS canceled_orders,

    COALESCE(SUM(ov.item_gmv), 0) AS item_gmv,

    COALESCE(
        SUM(ov.item_gmv) FILTER (
            WHERE o.order_status = 'delivered'
        ), 0
    ) AS delivered_item_gmv,

    COALESCE(SUM(ov.freight_value), 0) AS freight_value

FROM orders o
LEFT JOIN order_values ov
    ON o.order_id = ov.order_id

WHERE o.order_purchase_timestamp IS NOT NULL

GROUP BY DATE_TRUNC(
    'month',
    o.order_purchase_timestamp
);


-- 4. Product performance
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    p.product_id,
    p.product_category_name,
    ct.product_category_name_english,

    COUNT(i.order_id) AS items_sold,

    COUNT(DISTINCT i.order_id) AS orders_count,

    COALESCE(SUM(i.price), 0) AS item_gmv,

    COALESCE(SUM(i.freight_value), 0) AS freight_value,

    ROUND(AVG(i.price), 2) AS average_item_price

FROM products p

LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name

LEFT JOIN order_items i
    ON p.product_id = i.product_id

GROUP BY
    p.product_id,
    p.product_category_name,
    ct.product_category_name_english;


-- 5. Customer analytics
CREATE OR REPLACE VIEW vw_customer_analytics AS
WITH order_values AS (
    SELECT
        order_id,
        SUM(price) AS item_gmv
    FROM order_items
    GROUP BY order_id
),
customer_orders AS (
    SELECT
        o.customer_id,

        COUNT(*) AS total_orders,

        COUNT(*) FILTER (
            WHERE o.order_status = 'delivered'
        ) AS delivered_orders,

        COALESCE(SUM(ov.item_gmv), 0) AS item_gmv,

        COALESCE(
            SUM(ov.item_gmv) FILTER (
                WHERE o.order_status = 'delivered'
            ), 0
        ) AS delivered_item_gmv,

        COUNT(ov.order_id) AS orders_with_items,

        MIN(o.order_purchase_timestamp) AS first_order_date,

        MAX(o.order_purchase_timestamp) AS last_order_date

    FROM orders o

    LEFT JOIN order_values ov
        ON o.order_id = ov.order_id

    GROUP BY o.customer_id
)
SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,

    COALESCE(co.total_orders, 0) AS total_orders,

    COALESCE(co.delivered_orders, 0) AS delivered_orders,

    COALESCE(co.item_gmv, 0) AS item_gmv,

    COALESCE(co.delivered_item_gmv, 0) AS delivered_item_gmv,

    COALESCE(co.orders_with_items, 0) AS orders_with_items,

    ROUND(
        co.item_gmv / NULLIF(co.orders_with_items, 0),
        2
    ) AS average_item_gmv_per_order,

    co.first_order_date,
    co.last_order_date

FROM customers c

LEFT JOIN customer_orders co
    ON c.customer_id = co.customer_id;
