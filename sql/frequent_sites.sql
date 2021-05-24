WITH base AS (
  SELECT STRFTIME('%Y', created_dt) AS created_year
       , share_host
       , count(*) AS n_shares

  FROM {{ user_prefix }}share

  GROUP BY 1,2
)
, ranking AS (
  SELECT *
       , SUM(n_shares) OVER (PARTITION BY share_host ORDER BY created_year ASC ) AS total_shares
       , ROW_NUMBER() OVER (PARTITION BY created_year ORDER BY n_shares DESC, share_host ASC) AS rn
  FROM base
)

SELECT created_year
     , share_host
     , n_shares
     , total_shares

FROM ranking

WHERE rn <= 5
