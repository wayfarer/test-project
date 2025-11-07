"""Database connection and utilities."""
import os
import getpass
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional


def get_db_connection():
    """
    Get a database connection to the test_project database.
    
    Uses environment variables for connection details:
    - DB_HOST (default: localhost)
    - DB_PORT (default: 5432)
    - DB_NAME (default: test_project)
    - DB_USER (default: current system user via getpass.getuser())
    - DB_PASSWORD (optional, if not set uses passwordless auth)
    
    Returns:
        psycopg2.connection: Database connection object.
    """
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "test_project")
    user = os.getenv("DB_USER", getpass.getuser())
    password = os.getenv("DB_PASSWORD")
    
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create players table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            player_name VARCHAR(255) NOT NULL,
            position VARCHAR(10) NOT NULL,
            games INTEGER NOT NULL,
            at_bats INTEGER NOT NULL,
            runs INTEGER NOT NULL,
            hits INTEGER NOT NULL,
            doubles INTEGER NOT NULL,
            triples INTEGER NOT NULL,
            home_runs INTEGER NOT NULL,
            rbis INTEGER NOT NULL,
            walks INTEGER NOT NULL,
            strikeouts INTEGER NOT NULL,
            stolen_bases INTEGER NOT NULL,
            caught_stealing INTEGER NOT NULL,
            batting_average DECIMAL(5, 3) NOT NULL,
            on_base_percentage DECIMAL(5, 3) NOT NULL,
            slugging_percentage DECIMAL(5, 3) NOT NULL,
            ops DECIMAL(5, 3) NOT NULL,
            is_edited BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create player_descriptions table for LLM-generated descriptions cache
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_descriptions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(player_id)
        )
    """)
    
    # Create index on player_name for faster lookups
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name)
    """)
    
    # Remove hits_per_game column if it exists (now calculated on-the-fly)
    cur.execute("""
        ALTER TABLE players
        DROP COLUMN IF EXISTS hits_per_game
    """)
    
    conn.commit()
    cur.close()
    conn.close()

