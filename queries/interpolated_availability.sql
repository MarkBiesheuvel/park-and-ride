WITH binned_timeseries AS (
  SELECT BIN(time, 5m) AS binned_timestamp, AVG(measure_value::bigint) AS avg_availability
  FROM "Database-guHLCfEsVTts"."Table-xQefOgJKHuvZ"
  WHERE Location = 'P+R Noord'
    AND time > ago(1h)
  GROUP BY BIN(time, 5m)
), interpolated_timeseries AS (
  SELECT INTERPOLATE_SPLINE_CUBIC(
        CREATE_TIME_SERIES(binned_timestamp, avg_availability),
            SEQUENCE(min(binned_timestamp), max(binned_timestamp), 2m)) AS interpolated_avg_availability
  FROM binned_timeseries
)
SELECT time, ROUND(value, 2) AS interpolated_availability
FROM interpolated_timeseries
CROSS JOIN UNNEST(interpolated_avg_availability)
