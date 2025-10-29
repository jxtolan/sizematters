import csv
import sqlite3

def populate_smart_traders():
    """Populate the database with smart trader addresses from CSV"""
    
    # Read the CSV file
    traders = []
    with open('../smart_traders.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            address = row['address'].strip()
            if address:
                traders.append(address)
    
    print(f"Found {len(traders)} trader addresses in CSV")
    
    # Connect to database
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    # Add traders to database
    added = 0
    for address in traders:
        try:
            # Check if already exists
            c.execute("SELECT id FROM users WHERE wallet_address = ?", (address,))
            if c.fetchone() is None:
                # Generate a user ID
                import uuid
                user_id = str(uuid.uuid4())
                c.execute("INSERT INTO users (id, wallet_address) VALUES (?, ?)", 
                         (user_id, address))
                added += 1
        except Exception as e:
            print(f"Error adding {address}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {added} new smart trader addresses to database")
    print(f"Total traders available for matching: {len(traders)}")

if __name__ == "__main__":
    populate_smart_traders()

