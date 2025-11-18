"""
Quick test script to verify database connection works
Run this locally to test SQLite
Set DATABASE_URL to test PostgreSQL connection
"""

import os
from database import db

def test_connection():
    """Test database connection and table creation"""
    print("=" * 60)
    print("🧪 Testing Database Connection")
    print("=" * 60)
    print()
    
    # Show which database we're using
    if db.use_postgres:
        print("🐘 Using PostgreSQL")
        print(f"   Connection: {os.getenv('DATABASE_URL', '')[:50]}...")
    else:
        print("📁 Using SQLite (smartmoney.db)")
    
    print()
    
    # Test connection
    try:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # Test a simple query
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            if result:
                print("✅ Database connection successful!")
            else:
                print("❌ Connection failed - no result returned")
                return False
            
            # Check if users table exists
            if db.use_postgres:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'users'
                """)
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                print("✅ Users table exists")
                
                # Count users
                cursor.execute("SELECT COUNT(*) FROM users")
                result = cursor.fetchone()
                count = result['count'] if isinstance(result, dict) else result[0]
                print(f"✅ Found {count} users in database")
            else:
                print("⚠️  Users table doesn't exist yet (will be created on first run)")
            
            print()
            print("=" * 60)
            print("🎉 All tests passed! Database is ready.")
            print("=" * 60)
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print("Troubleshooting:")
        if db.use_postgres:
            print("  - Check DATABASE_URL is correct")
            print("  - Verify PostgreSQL server is running")
            print("  - Check network connectivity to database")
        else:
            print("  - Check write permissions in backend/ directory")
            print("  - Verify SQLite3 is installed")
        print()
        return False

if __name__ == "__main__":
    test_connection()

