"""
Migration script to add extended profile fields to existing database
Run this on both local and production databases
"""

import sqlite3
from datetime import datetime

def migrate():
    """Add new columns to users table"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    print("🔄 Migrating database to extended profiles schema...")
    
    try:
        # Check existing columns
        c.execute("PRAGMA table_info(users)")
        existing_columns = [col[1] for col in c.fetchall()]
        print(f"📋 Existing columns: {existing_columns}")
        
        # Add trader_number column if it doesn't exist
        if 'trader_number' not in existing_columns:
            print("➕ Adding trader_number column...")
            c.execute("ALTER TABLE users ADD COLUMN trader_number INTEGER")
            
            # Assign trader numbers to existing users
            c.execute("SELECT id, wallet_address FROM users ORDER BY created_at")
            users = c.fetchall()
            for idx, (user_id, wallet) in enumerate(users, start=1):
                c.execute("UPDATE users SET trader_number = ? WHERE id = ?", (idx, user_id))
                print(f"   Assigned #{idx:03d} to {wallet[:8]}...")
        else:
            c.execute("SELECT id, wallet_address FROM users ORDER BY created_at")
            users = c.fetchall()
        
        # Add other new columns (nullable for existing users)
        new_columns = {
            'country': 'TEXT',
            'favourite_ct_account': 'TEXT',
            'worst_ct_account': 'TEXT',
            'favourite_trading_venue': 'TEXT',
            'asset_choice_6m': 'TEXT'
        }
        
        for column, col_type in new_columns.items():
            if column not in existing_columns:
                print(f"➕ Adding {column} column...")
                c.execute(f"ALTER TABLE users ADD COLUMN {column} {col_type}")
        
        # Make bio NOT NULL is tricky with SQLite, so we'll just ensure it exists
        if 'bio' not in existing_columns:
            print("➕ Adding bio column...")
            c.execute("ALTER TABLE users ADD COLUMN bio TEXT")
        
        conn.commit()
        print("\n✅ Migration complete!")
        print(f"📊 Total users: {len(users) if 'users' in locals() else 'N/A'}")
        print("\n⚠️  NOTE: Existing users will need to complete their profiles")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

