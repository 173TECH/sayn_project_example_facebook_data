SELECT chat_with
     , sender_name
     , created_ts
     , created_dt
     , STRFTIME('%Y', created_dt) AS year
     , STRFTIME('%Y-%m', created_dt) AS month
     , CASE WHEN sender_name != LAG(sender_name) OVER (PARTITION BY chat_with ORDER BY timestamp_ms)
            AND (timestamp_ms - LAG(timestamp_ms) OVER (PARTITION BY chat_with ORDER BY timestamp_ms)) < 600000000 THEN
            (timestamp_ms - LAG(timestamp_ms) OVER (PARTITION BY chat_with ORDER BY timestamp_ms))/1000
            ELSE NULL END
       AS time_between_replies_seconds
     , LOWER(content) AS content
     , type
     , is_unsent

FROM {{ user_prefix }}logs_chat_data

WHERE type = 'Generic'

ORDER BY 2 DESC
