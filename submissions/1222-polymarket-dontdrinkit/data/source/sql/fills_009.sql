SELECT id, toUnixTimestamp(timestamp) AS timestamp_epoch,
          maker, taker, maker_asset_id, taker_asset_id,
          toString(maker_amount_filled) AS maker_amount_raw,
          toString(taker_amount_filled) AS taker_amount_raw,
          toString(fee) AS fee_raw, block_number
          FROM polymarket.orders_filled FINAL PREWHERE timestamp >= '2025-12-27 00:00:00' AND timestamp < '2026-01-04 00:00:00' AND (maker_asset_id IN ('24918067747661759048720135607687934209172945708698786072564741153847301974566','98590363695810976489755414330258191966783137178752226225745237702303580425394') OR taker_asset_id IN ('24918067747661759048720135607687934209172945708698786072564741153847301974566','98590363695810976489755414330258191966783137178752226225745237702303580425394'))
          WHERE is_deleted=0 AND id > '0xe7618eb8c101b875ae5041d10c77561b30ab8ce269f86a411b2513dd6bbec5ee_0x08e3f516082d36dcc4d4616393b58e76667a8ff90f22ec0cdb5eed37a93130c1'
          ORDER BY id LIMIT 2000 FORMAT JSON