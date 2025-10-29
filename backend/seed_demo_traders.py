"""
Seed the database with demo traders - real addresses with fun bios
Run this script to populate your database with real Solana traders
"""

import sqlite3
import uuid
from datetime import datetime

# Real Solana wallet addresses with creative trader bios
DEMO_TRADERS = [
    {
        "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "bio": "🎯 Degen since '21 | Made 420% on BONK before it was cool | Only trade in crocs | YOLO is my risk management"
    },
    {
        "address": "CckxW6C1CjsxYcXSiDbk7NYfPLhfqAm3kSB5LEZunnSE",
        "bio": "📊 Quant trader who got rugged once and never recovered emotionally | 200 IQ, 0 social skills | Will marry whoever invented MEV"
    },
    {
        "address": "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr",
        "bio": "💎 Diamond hands or food stamps | Lost my house keys but never my seed phrase | Survived 3 bear markets and 1 divorce"
    },
    {
        "address": "AArPXm8JatJiuyEffuC1un2Sc835SULa4uQqDcaGpAjN",
        "bio": "🚀 If it doesn't 100x in 24hrs I'm not interested | Sleep is for people without alpha | My therapist told me to log off"
    },
    {
        "address": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
        "bio": "🧙‍♂️ Wizard of the orderbook | I see liquidity pools in my dreams | Once made $50k in 10 mins then lost it in 11"
    },
    {
        "address": "GThUX1Atko4tqhN2NaiTazWSeFWMuiUvfFnyJyUghFMJ",
        "bio": "🐋 Not a whale but I identify as one | Bot operator with feelings | Married to volatility, divorced from stability"
    },
    {
        "address": "2ojv9BAiHUrvsm9gxDe7fJSzbNZSJcxZvf8dqmWGHG8S",
        "bio": "⚡ Speed trader | My Wi-Fi is faster than your reflexes | Haven't touched grass since Jupiter launched | Living on energy drinks"
    },
    {
        "address": "J1S9H3QjnRtBbbuD4HjPV6RpRhwuk4zKbxsnCHuTgh9w",
        "bio": "🎲 Professional gambler who found Solana | Somehow up 300% YTD | My secret? Being too dumb to panic sell"
    },
    {
        "address": "Ez2LhSqczEBLRWxuN3eD8wLnfr5mJKwCKmGSrfCB9VfV",
        "bio": "🌙 Night owl trader | Best trades happen at 3am | Coffee-powered memecoin connoisseur | Trust me bro is my DD"
    },
    {
        "address": "HvdKHqMKfPj6TzDPRVTHQNPLXDVGJnPeZFHzLG3qw8vN",
        "bio": "🏄 Riding waves since $SOL was $8 | Surf by day, trade by night | Looking for someone to explain what 'risk' means"
    },
    {
        "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "bio": "💰 USDC maxi with trust issues | Stablecoin gang | Once saw my portfolio go red and had an existential crisis"
    },
    {
        "address": "So11111111111111111111111111111111111111112",
        "bio": "☀️ Literal SOL | I AM the token | Dating me is basically insider trading | Probably not legal but definitely cool"
    },
    {
        "address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "bio": "🎰 DeFi degen | Yield farming since it was called ponzinomics | Lost count of my rugs | Still here, still bullish"
    },
    {
        "address": "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
        "bio": "🌊 Liquid staking enthusiast | My personality is as liquid as my assets | Validator simp | DeFi summer forever"
    },
    {
        "address": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
        "bio": "🔥 Got burned on Luna, learned nothing | Leverage is my love language | Risk assessment? Never heard of her"
    }
]

def seed_database():
    """Seed the database with demo traders"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    print("🌱 Seeding database with demo traders...")
    
    added = 0
    skipped = 0
    
    for trader in DEMO_TRADERS:
        try:
            # Check if trader already exists
            c.execute("SELECT id FROM users WHERE wallet_address = ?", (trader["address"],))
            existing = c.fetchone()
            
            if existing:
                # Update bio if user exists
                c.execute("UPDATE users SET bio = ? WHERE wallet_address = ?",
                         (trader["bio"], trader["address"]))
                print(f"✏️  Updated: {trader['address'][:8]}... - {trader['bio'][:50]}...")
                skipped += 1
            else:
                # Create new user
                user_id = str(uuid.uuid4())
                c.execute("INSERT INTO users (id, wallet_address, bio, created_at) VALUES (?, ?, ?, ?)",
                         (user_id, trader["address"], trader["bio"], datetime.now().isoformat()))
                print(f"✅ Added: {trader['address'][:8]}... - {trader['bio'][:50]}...")
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

