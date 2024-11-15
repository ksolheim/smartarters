import sqlite3

DATABASE = 'database/raffle_rankings.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn