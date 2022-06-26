WITH week0 AS (
  SELECT date_trunc('minute', time) AS truncated_time, measure_value::bigint AS availability
  FROM "Database-guHLCfEsVTts"."Table-xQefOgJKHuvZ"
  WHERE Location = 'P+R Noord'
    AND time BETWEEN from_iso8601_timestamp('2022-06-20T00:00:00')
                 AND from_iso8601_timestamp('2022-06-20T23:59:59')
), week1 AS (
  SELECT date_trunc('minute', time + 7d) AS truncated_time, measure_value::bigint AS availability
  FROM "Database-guHLCfEsVTts"."Table-xQefOgJKHuvZ"
  WHERE Location = 'P+R Noord'
    AND time BETWEEN from_iso8601_timestamp('2022-06-13T00:00:00')
                 AND from_iso8601_timestamp('2022-06-13T23:59:59')
), week2 AS (
  SELECT date_trunc('minute', time + 14d) AS truncated_time, measure_value::bigint AS availability
  FROM "Database-guHLCfEsVTts"."Table-xQefOgJKHuvZ"
  WHERE Location = 'P+R Noord'
  AND time BETWEEN from_iso8601_timestamp('2022-06-06T00:00:00')
               AND from_iso8601_timestamp('2022-06-06T23:59:59')
), week3 AS (
  SELECT date_trunc('minute', time + 14d) AS truncated_time, measure_value::bigint AS availability
  FROM "Database-guHLCfEsVTts"."Table-xQefOgJKHuvZ"
  WHERE Location = 'P+R Noord'
  AND time BETWEEN from_iso8601_timestamp('2022-06-06T00:00:00')
               AND from_iso8601_timestamp('2022-06-06T23:59:59')
)
SELECT week0.truncated_time, week0.availability AS a0, week1.availability AS a1, week2.availability AS a2, week3.availability AS a3,
  (week0.availability + week1.availability + week2.availability + week3.availability) / 4 AS avarage_availibility
FROM week0
INNER JOIN week1 ON week0.truncated_time = week1.truncated_time
INNER JOIN week2 ON week0.truncated_time = week2.truncated_time
INNER JOIN week3 ON week0.truncated_time = week3.truncated_time
