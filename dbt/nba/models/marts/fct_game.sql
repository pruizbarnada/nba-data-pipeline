-- One row per team per game, foreign key team_id
{{ config(materialized='incremental', unique_key=['game_id', 'team_id']) }}

-- fct_game: one row per team per game (team_id is a foreign key to dim_team)
select
    game_id,
    team_id,
    game_date,
    is_win,
    points
from {{ ref('int_games_cleaned') }}

{% if is_incremental() %}
where game_date >= (select max(game_date) from {{ this }}) - interval 3 day
{% endif %}