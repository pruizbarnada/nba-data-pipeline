SELECT 
    CAST(id as integer) as team_id,
    full_name as team_name,
    abbreviation as team_abbreviation,
    nickname,
    city,
    _loaded_at
FROM {{source('raw', 'teams')}}