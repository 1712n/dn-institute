SELECT toDate(timestamp) AS day,
        count() AS fills, min(timestamp) AS first, max(timestamp) AS last
        FROM polymarket.orders_filled FINAL PREWHERE timestamp >= '2025-12-01 05:00:00' AND timestamp < '2026-01-03 06:00:00'
        WHERE is_deleted=0 GROUP BY day ORDER BY day FORMAT JSON