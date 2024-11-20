"""Database functions."""
import os
import sqlite3
import csv

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
    # Enable WAL mode
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_price_column():
    """Initialize price column in artworks table if it doesn't exist."""
    conn = get_db_connection()
    try:
        # Check if price column exists
        cursor = conn.execute("PRAGMA table_info(artworks)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add price column if it doesn't exist
        if 'price' not in columns:
            conn.execute("ALTER TABLE artworks ADD COLUMN price INTEGER")
            conn.commit()
    except Exception as e:
        print(f"Error initializing price column: {e}")
    finally:
        conn.close()

def update_artwork_prices(csv_path):
    """Update artwork prices from CSV file."""
    conn = get_db_connection()
    try:
        # Initialize price column if needed
        init_price_column()
        
        # Read and update prices from CSV with UTF-8-SIG encoding to handle BOM
        with open(csv_path, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) >= 2:  # Ensure we have both art_id and price
                    try:
                        art_id = int(row[0])
                        # Remove any non-numeric characters and convert to integer
                        price = int(''.join(filter(str.isdigit, row[1])))
                        
                        conn.execute(
                            "UPDATE artworks SET price = ? WHERE art_id = ?",
                            (price, art_id)
                        )
                    except (ValueError, IndexError) as e:
                        print(f"Error processing row {row}: {e}")
                        continue
        
        conn.commit()
        print("Price update completed successfully")
    except Exception as e:
        print(f"Error updating prices: {e}")
        conn.rollback()
    finally:
        conn.close()
