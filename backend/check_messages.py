"""
Check if messages exist in the database
"""
import os
from database import db

def check_messages():
    print("=" * 60)
    print("🔍 Checking Messages in Database")
    print("=" * 60)
    print()
    
    try:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # Count total messages
            cursor.execute("SELECT COUNT(*) as count FROM messages")
            result = cursor.fetchone()
            message_count = result['count'] if isinstance(result, dict) else result[0]
            print(f"📨 Total messages in database: {message_count}")
            
            # Count total matches
            cursor.execute("SELECT COUNT(*) as count FROM matches")
            result = cursor.fetchone()
            match_count = result['count'] if isinstance(result, dict) else result[0]
            print(f"💚 Total matches in database: {match_count}")
            
            # Count total users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            result = cursor.fetchone()
            user_count = result['count'] if isinstance(result, dict) else result[0]
            print(f"👥 Total users in database: {user_count}")
            
            print()
            
            if message_count > 0:
                print("📜 Recent messages:")
                cursor.execute("""
                    SELECT sender_wallet, message, created_at 
                    FROM messages 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                messages = cursor.fetchall()
                for msg in messages:
                    wallet = msg['sender_wallet'] if isinstance(msg, dict) else msg[0]
                    text = msg['message'] if isinstance(msg, dict) else msg[1]
                    time = msg['created_at'] if isinstance(msg, dict) else msg[2]
                    print(f"  - {wallet[:8]}...: {text[:50]} ({time})")
            else:
                print("⚠️  No messages found in database!")
            
            print()
            
            if match_count > 0:
                print("💚 Recent matches:")
                cursor.execute("""
                    SELECT user1_wallet, user2_wallet, chat_room_id, created_at 
                    FROM matches 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                matches = cursor.fetchall()
                for match in matches:
                    w1 = match['user1_wallet'] if isinstance(match, dict) else match[0]
                    w2 = match['user2_wallet'] if isinstance(match, dict) else match[1]
                    room = match['chat_room_id'] if isinstance(match, dict) else match[2]
                    time = match['created_at'] if isinstance(match, dict) else match[3]
                    print(f"  - {w1[:8]}... ↔️  {w2[:8]}... (Room: {room[:8]}...) ({time})")
            else:
                print("⚠️  No matches found in database!")
            
            print()
            print("=" * 60)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_messages()

