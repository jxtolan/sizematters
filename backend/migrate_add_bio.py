"""
Migration script to add bio column to users table
"""

import sqlite3

def migrate():
    """Add bio column to users table"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    try:
        # Check if bio column exists
        c.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'bio' not in columns:
            print("📝 Adding 'bio' column to users table...")
            c.execute("ALTER TABLE users ADD COLUMN bio TEXT")
            conn.commit()
            print("✅ Migration complete! Bio column added.")
        else:
            print("✅ Bio column already exists. No migration needed.")
    
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

