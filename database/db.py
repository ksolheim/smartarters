"""Database functions."""
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection."""
    server = os.getenv('MSSQL_SERVER')
    database = os.getenv('MSSQL_DATABASE')
    username = os.getenv('MSSQL_USERNAME')
    password = os.getenv('MSSQL_PASSWORD')
    
    connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;'
    conn = pyodbc.connect(connection_string)
    return conn

def dict_cursor(cursor):
    """Convert cursor row to dictionary."""
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dict_cursor_one(cursor):
    """Convert cursor row to dictionary."""
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None
