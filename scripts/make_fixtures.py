import duckdb

con = duckdb.connect('data/warehouse/nba.duckdb', read_only=True)   # open your real database, read-only

con.sql('''
    select * exclude (_loaded_at) from raw.game_log        -- all columns except the load timestamp
    where game_id in (
        select distinct game_id from raw.game_log
        order by game_id limit 80                          -- pick 80 games
    )
''').df().to_csv('tests/fixtures/game_log.csv', index=False)   # save as CSV, no row-number column

con.sql('select * exclude (_loaded_at) from raw.teams').df().to_csv(
    'tests/fixtures/teams.csv', index=False)               # all 30 teams