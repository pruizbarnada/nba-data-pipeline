SELECT
    CAST(game_id as varchar) as game_id,
    CAST(team_id as integer) as team_id,
    CAST(game_date as date) as game_date,
    CAST(pts as integer) as points,
    team_abbreviation,
    team_id
    _loaded_at,
    wl
FROM {{source('raw', 'game_log')}}