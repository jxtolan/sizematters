"""
Database abstraction layer - supports both SQLite (local) and PostgreSQL (production)
Automatically switches based on DATABASE_URL environment variable
"""

import os
import sqlite3
from typing import Any, List, Optional, Tuple
from contextlib import contextmanager

# Check if we should use PostgreSQL or SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "")
USE_POSTGRES = DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
    from urllib.parse import urlparse
    
    # Parse DATABASE_URL
    result = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'database': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }
    print(f"🐘 Using PostgreSQL: {result.hostname}")
else:
    DB_CONFIG = {'database': 'smartmoney.db'}
    print(f"📁 Using SQLite: smartmoney.db")


class Database:
    """Database wrapper that works with both SQLite and PostgreSQL"""
    
    def __init__(self):
        self.use_postgres = USE_POSTGRES
    
    @contextmanager
    def get_connection(self):
        """Get a database connection (context manager)"""
        if self.use_postgres:
            conn = psycopg2.connect(**DB_CONFIG)
            try:
                yield conn
            finally:
                conn.close()
        else:
            conn = sqlite3.connect(DB_CONFIG['database'])
            try:
                yield conn
            finally:
                conn.close()
    
    def get_cursor(self, conn):
        """Get a cursor for the connection"""
        if self.use_postgres:
            return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            conn.row_factory = sqlite3.Row
            return conn.cursor()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Any]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            
            # Convert to list of dicts for consistency
            if self.use_postgres:
                return [dict(row) for row in results]
            else:
                return [dict(row) for row in results]
    
    def execute_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Any]:
        """Execute a SELECT query and return one result"""
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = cursor.fetchone()
            
            if result is None:
                return None
            
            # Convert to dict for consistency
            if self.use_postgres:
                return dict(result)
            else:
                return dict(result)
    
    def execute_write(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
    
    def placeholder(self) -> str:
        """Return the parameter placeholder for the database type"""
        return "%s" if self.use_postgres else "?"
    
    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table with extended profile fields
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                         (id TEXT PRIMARY KEY,
                          wallet_address TEXT UNIQUE NOT NULL,
                          trader_number INTEGER UNIQUE,
                          bio TEXT NOT NULL,
                          country TEXT NOT NULL,
                          favourite_ct_account TEXT NOT NULL,
                          worst_ct_account TEXT,
                          favourite_trading_venue TEXT NOT NULL,
                          asset_choice_6m TEXT NOT NULL,
                          twitter_account TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            # Swipes table
            cursor.execute('''CREATE TABLE IF NOT EXISTS swipes
                         (id TEXT PRIMARY KEY,
                          user_id TEXT NOT NULL,
                          target_wallet TEXT NOT NULL,
                          direction TEXT NOT NULL,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (user_id) REFERENCES users(id))''')
            
            # Matches table
            cursor.execute('''CREATE TABLE IF NOT EXISTS matches
                         (id TEXT PRIMARY KEY,
                          user1_wallet TEXT NOT NULL,
                          user2_wallet TEXT NOT NULL,
                          chat_room_id TEXT NOT NULL,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            # Messages table
            cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                         (id TEXT PRIMARY KEY,
                          chat_room_id TEXT NOT NULL,
                          sender_wallet TEXT NOT NULL,
                          message TEXT NOT NULL,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            conn.commit()
            print("✅ Database tables initialized")


# Global database instance
db = Database()

