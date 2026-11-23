from nba_api.stats.endpoints import leaguegamelog
from nba_api.stats.static import teams
import duckdb
import pandas as pd
import os
import time
from pathlib import Path
import argparse
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'data' / 'warehouse' / 'nba.duckdb'
RAW_DIR = ROOT / 'data' / 'raw'
SEASON = os.getenv('NBA_SEASON', '2025-26')

def get_league_game_log(season: str = '2025-26', date_from: str | None = None) -> pd.DataFrame:
    """
    Get the league game log for a given season.
    If date_from (MM/DD/YYYY) is given, only games from that date onward are returned.
    """
    kwargs = {'season': season, 'season_type_all_star': 'Regular Season', 'timeout': 60}
    if date_from:
        kwargs['date_from_nullable'] = date_from
    df = leaguegamelog.LeagueGameLog(**kwargs).get_data_frames()[0]
    return df

def get_teams() -> pd.DataFrame:
    """
    Get the list of NBA teams.
    """
    teams_df = pd.DataFrame(teams.get_teams())
    return teams_df

def save_snapshot(df, name):
    """
    Save a snapshot of the dataframe to a CSV file.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DIR / f'{name}.csv', index=False)

def load_replace(con, table: str, df: pd.DataFrame) -> None:
    '''Idempotent: re-running replaces the table instead of duplicating
    rows.'''
    con.register('df_view', df)
    con.execute(f'create or replace table raw.{table} as select *, current_timestamp as _loaded_at from df_view')
    con.unregister('df_view')



def compute_start_date(max_loaded: str | None, lookback_days: int = 3) -> str | None:
    '''ISO start date for the next load, or None when nothing is loaded yet.
    A few days of overlap catches late stat corrections.'''
    if max_loaded is None:
        return None
    return (date.fromisoformat(str(max_loaded)) - timedelta(days=lookback_days)).isoformat()


def table_exists(con, schema: str, table: str) -> bool:
    sql = 'select count(*) from information_schema.tables where table_schema = ? and table_name = ?'
    return con.execute(sql, [schema, table]).fetchall()[0][0] > 0

def load_incremental(con, df: pd.DataFrame, start_date: str) -> None:
    '''Delete the overlapping window, then insert it again. Safe to repeat.'''
    con.register('df_view', df)
    con.execute('delete from raw.game_log where game_date >= ?', [start_date]).fetchall()
    con.execute('insert into raw.game_log select *, current_timestamp as _loaded_at from df_view')
    con.unregister('df_view')



def main(full_refresh: bool = False) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    con.execute('create schema if not exists raw')

    load_replace(con, 'teams', get_teams())

    if full_refresh or not table_exists(con, 'raw', 'game_log'):
        games = get_league_game_log(SEASON)
        save_snapshot(games, f'game_log_{SEASON}')
        load_replace(con, 'game_log', games)
    else:
        max_date = con.execute('select max(game_date) from raw.game_log').fetchall()[0][0]
        start = compute_start_date(max_date)
        date_from = date.fromisoformat(start).strftime('%m/%d/%Y')  # the API wants MM/DD/YYYY
        games = get_league_game_log(SEASON, date_from)
        if games.empty:
            print('No new games in the window.')
        else:
            load_incremental(con, games, start)

    rows = con.execute('select count(*), count(distinct game_id) from raw.game_log').fetchall()[0]
    print(f'raw.game_log: {rows[0]} rows, {rows[1]} games')
    con.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full-refresh', action='store_true')
    main(full_refresh=parser.parse_args().full_refresh)

