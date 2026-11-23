-- One team per row

select
    t.team_id,
    t.team_abbreviation,
    t.city,
    c.conference,
    c.division
from {{ ref('int_teams_cleaned') }} as t
left join {{ ref('team_conference') }} as c
    on t.team_abbreviation = c.team_abbreviation