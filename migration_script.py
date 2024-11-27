import os
import sqlite3
from database.db import get_db_connection

def create_mssql_tables(mssql_conn):
    cursor = mssql_conn.cursor()
    
    # Create users table first since it's referenced by other tables
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            name NVARCHAR(255) NOT NULL,
            email NVARCHAR(255) UNIQUE NOT NULL,
            password NVARCHAR(255) NOT NULL,
            is_verified BIT DEFAULT 0,
            reset_token_used BIT DEFAULT 0
        )
    """)

    # Create artworks table
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='artworks' AND xtype='U')
        CREATE TABLE artworks (
            art_id INT PRIMARY KEY,
            art_title NVARCHAR(255) NOT NULL,
            artist NVARCHAR(255) NOT NULL,
            jpg_name NVARCHAR(255) NOT NULL,
            price INT
        )
    """)

    # Create user_rankings table with foreign key constraints
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='user_rankings' AND xtype='U')
        CREATE TABLE user_rankings (
            user_id INT,
            art_id INT,
            rank INT,
            PRIMARY KEY (user_id, art_id),
            FOREIGN KEY (art_id) REFERENCES artworks (art_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Create artwork_status table with foreign key constraints
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='artwork_status' AND xtype='U')
        CREATE TABLE artwork_status (
            user_id INT,
            art_id INT,
            is_won BIT DEFAULT 0,
            PRIMARY KEY (user_id, art_id),
            FOREIGN KEY (art_id) REFERENCES artworks (art_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    mssql_conn.commit()

def migrate_data():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(os.getenv('DB_PATH'))
    sqlite_conn.row_factory = sqlite3.Row
    
    # Connect to MS SQL
    mssql_conn = get_db_connection()
    
    try:
        # Create tables in MS SQL with proper constraints
        create_mssql_tables(mssql_conn)
        
        # Dictionary to store old->new user ID mappings
        user_id_mapping = {}
        
        # First, get all existing users from SQLite with their IDs
        users = sqlite_conn.execute('SELECT * FROM users ORDER BY id').fetchall()
        
        # Reset IDENTITY in MS SQL to match SQLite IDs
        mssql_conn.execute("DBCC CHECKIDENT ('users', RESEED, 0)")
        
        # Migrate users maintaining the same IDs
        for user in users:
            mssql_conn.execute("""
                SET IDENTITY_INSERT users ON;
                INSERT INTO users (id, name, email, password, is_verified, reset_token_used)
                VALUES (?, ?, ?, ?, ?, ?);
                SET IDENTITY_INSERT users OFF;
            """, (user['id'], user['name'], user['email'], user['password'], 
                 bool(user['is_verified']), bool(user['reset_token_used'])))
            
            user_id_mapping[user['id']] = user['id']  # In this case, they're the same

        # Migrate artworks next
        artworks = sqlite_conn.execute('SELECT * FROM artworks').fetchall()
        for artwork in artworks:
            mssql_conn.execute("""
                INSERT INTO artworks (art_id, art_title, artist, jpg_name, price)
                VALUES (?, ?, ?, ?, ?)
            """, (artwork['art_id'], artwork['art_title'], artwork['artist'],
                 artwork['jpg_name'], artwork['price']))

        # Migrate user_rankings with mapped user IDs
        rankings = sqlite_conn.execute('SELECT * FROM user_rankings').fetchall()
        for ranking in rankings:
            new_user_id = user_id_mapping[ranking['user_id']]
            mssql_conn.execute("""
                INSERT INTO user_rankings (user_id, art_id, rank)
                VALUES (?, ?, ?)
            """, (new_user_id, ranking['art_id'], ranking['rank']))

        # Migrate artwork_status with mapped user IDs
        statuses = sqlite_conn.execute('SELECT * FROM artwork_status').fetchall()
        for status in statuses:
            new_user_id = user_id_mapping[status['user_id']]
            mssql_conn.execute("""
                INSERT INTO artwork_status (user_id, art_id, is_won)
                VALUES (?, ?, ?)
            """, (new_user_id, status['art_id'], bool(status['is_won'])))

        mssql_conn.commit()
        
        # Get the current maximum user ID
        max_id = mssql_conn.execute("SELECT MAX(id) as max_id FROM users").fetchone()[0]
        
        # Reset IDENTITY to continue from the max ID
        mssql_conn.execute(f"DBCC CHECKIDENT ('users', RESEED, {max_id})")
        
        print("Migration completed successfully!")
        print("\nUser IDs have been preserved from SQLite to MS SQL")

    except Exception as e:
        print(f"Error during migration: {e}")
        mssql_conn.rollback()
    finally:
        sqlite_conn.close()
        mssql_conn.close()

if __name__ == "__main__":
    migrate_data() 