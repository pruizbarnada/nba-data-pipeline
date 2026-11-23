select
    team_id,
    team_name,
    team_abbreviation,
    nickname,
    city,
from {{ ref('stg_teams') }}
qualify row_number() over (partition by team_id order by _loaded_at desc) = 1