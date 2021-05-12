SELECT chat_with
     , sender_name
     , timestamp_ms
     , share_link
     , CASE WHEN lower(share_link) LIKE "https://www.youtube.com/watch?v=%"
            THEN REPLACE(share_link, "https://www.youtube.com/watch?v=", "")
            ELSE NULL END AS video_id

FROM {{ user_prefix }}share

WHERE lower(share_link) LIKE "https://www.youtube.com/%"
