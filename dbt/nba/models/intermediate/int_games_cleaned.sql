SELECT
    game_id,
    team_id,
    game_date,
    points,
    _loaded_at,
    wl = 'W' as is_win,
    team_abbreviation
FROM {{ref('stg_game_log') }}
QUALIFY ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY _loaded_at DESC) = 1