"""
Seed the database with demo traders - real addresses with fun bios
Run this script to populate your database with real Solana traders
"""

import sqlite3
import uuid
from datetime import datetime

# REAL Solana trader addresses with varied formatting for natural look + extended profiles
# Note: Optional fields (worst_ct_account, twitter_account) are left empty to look more realistic
DEMO_TRADERS = [
    {
        "address": "ERjMXMF6AVnMckiQb6zvTEcaCVc7iBpNqmtbNVjeKCpc",
        "bio": "degen since '21. made 420% on BONK before it was cool\n\nonly trade in crocs btw. YOLO is my risk management 💀",
        "country": "US",
        "favourite_ct_account": "@cobie",
        "favourite_trading_venue": "Pumpfun",
        "asset_choice_6m": "BONK & memecoins"
    },
    {
        "address": "99HXufoq4yepb8hNKgd1ghXRKMwAfMoXCZjAdXxXyEUh",
        "bio": "Quant trader, Got rugged once and never recovered emotionally... 200 IQ, 0 social skills. Will marry whoever invented MEV fr",
        "country": "SG",
        "favourite_ct_account": "@0xfoobar",
        "favourite_trading_venue": "Jupiter",
        "asset_choice_6m": "SOL derivatives"
    },
    {
        "address": "Au1GUWfcadx7jMzhsg6gHGUgViYJrnPfL1vbdqnvLK4i",
        "bio": "💎 DIAMOND HANDS OR FOOD STAMPS 💎\nLost my house keys but never my seed phrase\nSurvived: 3 bear markets, 1 divorce",
        "country": "GB",
        "favourite_ct_account": "@derekmajor",
        "favourite_trading_venue": "Raydium",
        "asset_choice_6m": "Blue chips only"
    },
    {
        "address": "8J6UcrwcSj6i9FdGeLYHUWNYiJrqhEAVJbWhjtBZvwHT",
        "bio": "If it doesn't 100x in 24hrs I'm not interested \n\nSleep is for people without alpha. My therapist told me to log off (I didn't)",
        "country": "AU",
        "favourite_ct_account": "@milkybullz",
        "favourite_trading_venue": "GMGN",
        "asset_choice_6m": "Shit coins to 100x"
    },
    {
        "address": "EdAsdt7JY6fcBYNbzY4HxXTEWSupiQMdRS3KjNLuSLKy",
        "bio": "🧙‍♂️ wizard of the orderbook\n\ni see liquidity pools in my dreams\n\nonce made $50k in 10 mins then lost it in 11 lol",
        "country": "DE",
        "favourite_ct_account": "@hsakatrades",
        "favourite_trading_venue": "Drift",
        "asset_choice_6m": "Perps & leverage"
    },
    {
        "address": "7Hkpf3NJwCdcnDqwZMTR1d76pHnfeyqnP8vxrV4TLKHR",
        "bio": "not a whale but I identify as one | bot operator with feelings | married to volatility, divorced from stability",
        "country": "NL",
        "favourite_ct_account": "@inversebrah",
        "favourite_trading_venue": "Photon",
        "asset_choice_6m": "MEV opportunities"
    },
    {
        "address": "EvwaHadVPP7bTdmfc4cxk3Pz5sr638sVUq1BJY8HArW7",
        "bio": "SPEED TRADER\nHaven't touched grass since Jupiter launched\n(living on energy drinks)",
        "country": "KR",
        "favourite_ct_account": "@byzantinegeneral",
        "favourite_trading_venue": "Maestro",
        "asset_choice_6m": "Fast flips"
    },
    {
        "address": "2CSqY1nUFZbuznxY3PUMWdBUif6WAqsTWtrfZKJQUgTb",
        "bio": "Professional gambler who found Solana 🎲 Somehow up 300% YTD?? My secret? Being too dumb to panic sell 🤷",
        "country": "CA",
        "favourite_ct_account": "@gainzy",
        "favourite_trading_venue": "NeoBullX",
        "asset_choice_6m": "Whatever pumps"
    },
    {
        "address": "6jMQdtwEAfoBvKdE4HYGTdHCRSxYfCrgPmjQ6rnGr5mn",
        "bio": "night owl trader\nbest trades happen at 3am coffee-powered memecoin connoisseur\n\n'trust me bro' is my DD",
        "country": "JP",
        "favourite_ct_account": "@0xngmi",
        "favourite_trading_venue": "Trojan",
        "asset_choice_6m": "Anime coins"
    }
]

def seed_database():
    """Seed the database with demo traders"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    print("🌱 Seeding database with demo traders...")
    
    added = 0
    skipped = 0
    
    for idx, trader in enumerate(DEMO_TRADERS, start=1):
        try:
            # Check if trader already exists
            c.execute("SELECT id, trader_number FROM users WHERE wallet_address = ?", (trader["address"],))
            existing = c.fetchone()
            
            if existing:
                # Update existing user with new fields (optional fields default to None)
                c.execute("""UPDATE users 
                            SET bio = ?, country = ?, favourite_ct_account = ?,
                                worst_ct_account = ?, favourite_trading_venue = ?,
                                asset_choice_6m = ?, twitter_account = ?
                            WHERE wallet_address = ?""",
                         (trader["bio"], trader["country"], trader["favourite_ct_account"],
                          trader.get("worst_ct_account"), trader["favourite_trading_venue"],
                          trader["asset_choice_6m"], trader.get("twitter_account"), trader["address"]))
                print(f"✏️  Updated: {trader['address'][:8]}... - {trader['country']} - {trader['favourite_trading_venue']}")
                skipped += 1
            else:
                # Create new user with all fields (optional fields default to None)
                user_id = str(uuid.uuid4())
                c.execute("""INSERT INTO users 
                            (id, wallet_address, trader_number, bio, country, favourite_ct_account,
                             worst_ct_account, favourite_trading_venue, asset_choice_6m, twitter_account, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (user_id, trader["address"], idx, trader["bio"], trader["country"],
                          trader["favourite_ct_account"], trader.get("worst_ct_account"),
                          trader["favourite_trading_venue"], trader["asset_choice_6m"],
                          trader.get("twitter_account"), datetime.now().isoformat()))
                print(f"✅ Added #{idx:03d}: {trader['address'][:8]}... - {trader['country']} {trader['favourite_trading_venue']}")
                added += 1
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Error adding {trader['address'][:8]}...: {str(e)}")
    
    conn.close()
    
    print(f"\n🎉 Seeding complete!")
    print(f"   ✅ Added: {added} new traders")
    print(f"   ✏️  Updated: {skipped} existing traders")
    print(f"   📊 Total: {len(DEMO_TRADERS)} demo traders in system")
    print(f"\n💡 Nansen API will fetch real PnL and balance data when profiles load!")

if __name__ == "__main__":
    seed_database()

