#!/usr/bin/env python3
"""
Migration script to add twitter_account column to users table
"""
import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('smartmoney.db')
        c = conn.cursor()
        
        print("🔄 Starting migration: Adding twitter_account column...")
        
        # Check if column already exists
        c.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in c.fetchall()]
        
        if 'twitter_account' in columns:
            print("✅ twitter_account column already exists. No migration needed.")
            conn.close()
            return
        
        # Add twitter_account column
        c.execute("ALTER TABLE users ADD COLUMN twitter_account TEXT")
        conn.commit()
        
        print("✅ Migration successful: twitter_account column added!")
        print("📊 All existing users will have twitter_account set to NULL (optional field)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate()

