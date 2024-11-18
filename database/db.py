"""Database functions."""
import os
import sqlite3

# Get database path from environment variable, or use a default path
DATABASE = os.getenv('DB_PATH', 'database/raffle_rankings.db')

def get_db_connection():
    """Get database connection."""
    # Ensure the directory exists
    db_dir = os.path.dirname(DATABASE)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
