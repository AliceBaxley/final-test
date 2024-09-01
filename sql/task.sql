

SELECT c."login", COUNT(o.id) AS orders_in_delivery
FROM "Couriers" c
JOIN "Orders" o ON c.id = o."courierId"
WHERE o."inDelivery" = true
GROUP BY c."login";


SELECT
    "track",
    CASE
        WHEN "finished" = true THEN 2
        WHEN "cancelled" = true THEN -1
        WHEN "inDelivery" = true THEN 1
        ELSE 0
    END AS status
FROM
    "Orders";
