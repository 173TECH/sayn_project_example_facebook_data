SELECT CASE WHEN sender_name != 'Tim Sugaipov' THEN "Friend" ELSE "Me" END AS sender_name
     , DATETIME(ROUND(timestamp_ms / 1000), 'unixepoch') AS isodatetime
     , DATE(DATETIME(ROUND(timestamp_ms / 1000), 'unixepoch')) AS isodate
     , STRFTIME('%Y-%m', DATETIME(ROUND(timestamp_ms / 1000), 'unixepoch')) AS month
     , CASE WHEN sender_name != LAG(sender_name) OVER (ORDER BY timestamp_ms)
            AND (timestamp_ms - LAG(timestamp_ms) OVER (ORDER BY timestamp_ms)) < 600000000 THEN
            (timestamp_ms - LAG(timestamp_ms) OVER (ORDER BY timestamp_ms))/1000
            ELSE NULL END
       AS time_between_replies_seconds
     , LOWER(content) AS content
     , type
     , is_unsent

FROM {{ user_prefix }}logs_chat_data

ORDER BY 2 DESC
