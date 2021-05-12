WITH base AS (
  SELECT chat_with
     , sender_name
     , sticker_link
     , COUNT(*) AS sticker_frequency

  FROM sticker

  GROUP BY 1,2,3

  ORDER BY 1,2,4 DESC
)


SELECT chat_with
     , sender_name
     , sticker_link
     , sticker_frequency
     , CAST(sticker_frequency AS REAL)/(SUM(sticker_frequency) OVER (PARTITION BY chat_with, sender_name)) AS proportion
     , ROW_NUMBER() OVER (PARTITION BY chat_with, sender_name ORDER BY sticker_frequency) AS ranking

FROM base
