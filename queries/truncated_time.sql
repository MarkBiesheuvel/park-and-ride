SELECT date_trunc('minute', time) AS truncated_time, measure_value::bigint AS availability
FROM "Database-guHLCfEsVTts"."Table-xQefOgJKHuvZ"
WHERE Location = 'P+R Noord'
  AND time BETWEEN from_iso8601_timestamp('2022-06-19T00:00:00')
               AND from_iso8601_timestamp('2022-06-19T23:59:59')
