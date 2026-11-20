'''Load the small CSV fixtures into DuckDB so CI can run dbt without calling the API.'''
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]                  # project root, from this file's location
DB_PATH = ROOT / 'data' / 'warehouse' / 'nba.duckdb'        # same path dbt's profile points to
FIXTURES = ROOT / 'tests' / 'fixtures'                      # where the CSVs live

DB_PATH.parent.mkdir(parents=True, exist_ok=True)           # CI starts empty, so create data/warehouse
con = duckdb.connect(str(DB_PATH))                          # creates the database file if missing
con.execute('create schema if not exists raw')              # same raw schema ingest.py uses

for table in ('game_log', 'teams'):                         # loop over both tables
    csv_path = FIXTURES / f'{table}.csv'
    con.execute(
        f'create or replace table raw.{table} as '          # (re)create raw.game_log and raw.teams
        f'select *, current_timestamp as _loaded_at '       # add the load timestamp, as ingest.py does
        f'from read_csv_auto(\'{csv_path}\', all_varchar=true)'   # read the CSV; every column as text
    )
con.close()