SELECT BIN(time, 15m) AS binned_timestamp, ROUND(AVG(measure_value::bigint), 2) AS availability
FROM "Database-guHLCfEsVTts"."Table-xQefOgJKHuvZ"
WHERE Location = 'P+R Noord'
  AND time > ago(1h)
GROUP BY BIN(time, 15m)
ORDER BY binned_timestamp
