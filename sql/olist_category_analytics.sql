
CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    p.product_category_name,
    COALESCE(
        ct.product_category_name_english,
        'Unknown'
    ) AS category_name_english,

    COUNT(DISTINCT p.product_id) AS total_products,

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
    p.product_category_name,
    ct.product_category_name_english;
