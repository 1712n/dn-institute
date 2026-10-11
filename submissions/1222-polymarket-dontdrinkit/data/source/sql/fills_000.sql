SELECT id, toUnixTimestamp(timestamp) AS timestamp_epoch,
          maker, taker, maker_asset_id, taker_asset_id,
          toString(maker_amount_filled) AS maker_amount_raw,
          toString(taker_amount_filled) AS taker_amount_raw,
          toString(fee) AS fee_raw, block_number
          FROM polymarket.orders_filled FINAL PREWHERE timestamp >= '2025-12-27 00:00:00' AND timestamp < '2026-01-04 00:00:00' AND (maker_asset_id IN ('24918067747661759048720135607687934209172945708698786072564741153847301974566','98590363695810976489755414330258191966783137178752226225745237702303580425394') OR taker_asset_id IN ('24918067747661759048720135607687934209172945708698786072564741153847301974566','98590363695810976489755414330258191966783137178752226225745237702303580425394'))
          WHERE is_deleted=0 AND id > ''
          ORDER BY id LIMIT 2000 FORMAT JSON