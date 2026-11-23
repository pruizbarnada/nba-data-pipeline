select
    team_id,
    count(*) as games_played,
    sum(case when is_win then 1 else 0 end) as wins,
    round(sum(case when is_win then 1 else 0 end) * 1.0 / count(*), 3) as
    win_pct
from {{ ref('fct_game') }}
group by 1

