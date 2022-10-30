with trades_univ3 as (
SELECT
    DATE_TRUNC('{{Time_series_granularity}}',t."block_time") AS dt,
    project || version AS project,
    t."token_a_address",
    t."token_b_address",
    t."token_a_symbol" || '/' || t."token_b_symbol" AS pair,
    t.exchange_contract_address,
    SUM(t.token_a_amount) AS token_a_amount,
    SUM(t.token_b_amount) AS token_b_amount
    FROM dex.trades t
    WHERE t.project = 'Uniswap' AND t.version = '3' AND t."block_time" > LEAST('{{Initial Date}}',NOW())
        AND t.exchange_contract_address='{{Exchange_contract_address_univ3}}'
    group by 1, 2, 3, 4, 5, 6
    LIMIT 100
),
trades_univ2 as (
    SELECT
    DATE_TRUNC('{{Time_series_granularity}}',t."block_time") AS dt,
    project || version AS project,
    t."token_a_address",
    t."token_b_address",
    t."token_a_symbol" || '/' || t."token_b_symbol" AS pair,
    t.exchange_contract_address,
    SUM(t.token_a_amount) AS token_a_amount,
    SUM(t.token_b_amount) AS token_b_amount
    FROM dex.trades t
    WHERE t.project = 'Uniswap' AND t.version = '2' AND t."block_time" > LEAST('{{Initial Date}}',NOW())
        AND t.exchange_contract_address='{{Exchange_contract_address_univ2}}'
    group by 1, 2, 3, 4, 5, 6
    LIMIT 100
)
SELECT v3.dt, v3.pair, v3.token_a_amount as token_a_amount_v3_initial, --v3.token_b_amount as token_b_amount_v3,
    --v2.token_a_amount as token_a_amount_v2, v2.token_b_amount as token_b_amount_v2,
    v3.token_a_amount/v3.token_b_amount as price_pair_v3,
    v2.token_b_amount/v2.token_a_amount as price_pair_v2,
    (v3.token_a_amount/v3.token_b_amount-v2.token_b_amount/v2.token_a_amount) as dif_price_v3_over_v2_tokena,
    v3.token_b_amount/(v2.token_a_amount/v2.token_b_amount) as tokena_simulated_amount_v3_after_arbitrage,
    round(((v3.token_b_amount/(v2.token_a_amount/v2.token_b_amount)) - v3.token_a_amount)/v3.token_a_amount*100, 2) as perc_gained_with_arbitrage_of_tokena
FROM trades_univ3 v3
INNER JOIN trades_univ2 v2 ON v2.token_a_address = v3.token_b_address and v2.token_b_address = v3.token_a_address AND v2.dt = v3.dt;