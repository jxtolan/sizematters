from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import requests
from datetime import datetime, timedelta
import sqlite3
import uuid
from collections import defaultdict
import os
import time

app = FastAPI(title="Smart Money Tinder API")

# CORS middleware - Allow all origins for demo/hackathon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Vercel, localhost, etc.)
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def init_db():
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY,
                  wallet_address TEXT UNIQUE NOT NULL,
                  bio TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Swipes table
    c.execute('''CREATE TABLE IF NOT EXISTS swipes
                 (id TEXT PRIMARY KEY,
                  user_id TEXT NOT NULL,
                  target_wallet TEXT NOT NULL,
                  direction TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Matches table
    c.execute('''CREATE TABLE IF NOT EXISTS matches
                 (id TEXT PRIMARY KEY,
                  user1_wallet TEXT NOT NULL,
                  user2_wallet TEXT NOT NULL,
                  chat_room_id TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id TEXT PRIMARY KEY,
                  chat_room_id TEXT NOT NULL,
                  sender_wallet TEXT NOT NULL,
                  message TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

# In-memory cache for Nansen API responses
# Structure: { wallet_address: { 'pnl': {...}, 'balance': {...}, 'timestamp': 123456 } }
nansen_cache = {}
CACHE_TTL_SECONDS = 300  # 5 minutes

def get_cached_data(wallet_address: str, data_type: str):
    """Get cached Nansen data if not expired"""
    if wallet_address not in nansen_cache:
        return None
    
    cache_entry = nansen_cache[wallet_address]
    
    # Check if cache expired
    if time.time() - cache_entry.get('timestamp', 0) > CACHE_TTL_SECONDS:
        # Cache expired, remove it
        del nansen_cache[wallet_address]
        return None
    
    return cache_entry.get(data_type)

def set_cached_data(wallet_address: str, data_type: str, data: dict):
    """Cache Nansen API response"""
    if wallet_address not in nansen_cache:
        nansen_cache[wallet_address] = {'timestamp': time.time()}
    else:
        nansen_cache[wallet_address]['timestamp'] = time.time()
    
    nansen_cache[wallet_address][data_type] = data

def clear_expired_cache():
    """Periodic cleanup of expired cache entries"""
    current_time = time.time()
    expired_wallets = [
        wallet for wallet, data in nansen_cache.items()
        if current_time - data.get('timestamp', 0) > CACHE_TTL_SECONDS
    ]
    for wallet in expired_wallets:
        del nansen_cache[wallet]
    
    if expired_wallets:
        print(f"🧹 Cleared {len(expired_wallets)} expired cache entries")

# Helper function to format numbers with k/M abbreviations
def format_currency(amount):
    """Format currency with k/M abbreviations"""
    if amount is None:
        return "$0"
    
    abs_amount = abs(amount)
    sign = "-" if amount < 0 else ""
    
    if abs_amount >= 1_000_000:
        # Format as millions
        formatted = f"{abs_amount / 1_000_000:.1f}M"
        # Remove .0 if it's a whole number
        if formatted.endswith('.0M'):
            formatted = formatted[:-3] + 'M'
    elif abs_amount >= 1_000:
        # Format as thousands
        formatted = f"{abs_amount / 1_000:.1f}k"
        # Remove .0 if it's a whole number
        if formatted.endswith('.0k'):
            formatted = formatted[:-3] + 'k'
    else:
        # Less than 1k, show as is
        formatted = f"{abs_amount:.0f}"
    
    return f"{sign}${formatted}"

# Demo trader bios mapping - REAL trader addresses with varied formatting
DEMO_TRADER_BIOS = {
    "ERjMXMF6AVnMckiQb6zvTEcaCVc7iBpNqmtbNVjeKCpc": "degen since '21. made 420% on BONK before it was cool\n\nonly trade in crocs btw. YOLO is my risk management 💀",
    "99HXufoq4yepb8hNKgd1ghXRKMwAfMoXCZjAdXxXyEUh": "Quant trader, Got rugged once and never recovered emotionally... 200 IQ, 0 social skills. Will marry whoever invented MEV fr",
    "Au1GUWfcadx7jMzhsg6gHGUgViYJrnPfL1vbdqnvLK4i": "💎 DIAMOND HANDS OR FOOD STAMPS 💎\nLost my house keys but never my seed phrase\nSurvived: 3 bear markets, 1 divorce",
    "8J6UcrwcSj6i9FdGeLYHUWNYiJrqhEAVJbWhjtBZvwHT": "If it doesn't 100x in 24hrs I'm not interested \n\nSleep is for people without alpha. My therapist told me to log off (I didn't)",
    "EdAsdt7JY6fcBYNbzY4HxXTEWSupiQMdRS3KjNLuSLKy": "🧙‍♂️ wizard of the orderbook\n\ni see liquidity pools in my dreams\n\nonce made $50k in 10 mins then lost it in 11 lol",
    "7Hkpf3NJwCdcnDqwZMTR1d76pHnfeyqnP8vxrV4TLKHR": "not a whale but I identify as one | bot operator with feelings | married to volatility, divorced from stability",
    "EvwaHadVPP7bTdmfc4cxk3Pz5sr638sVUq1BJY8HArW7": "SPEED TRADER\nHaven't touched grass since Jupiter launched\n(living on energy drinks)",
    "2CSqY1nUFZbuznxY3PUMWdBUif6WAqsTWtrfZKJQUgTb": "Professional gambler who found Solana 🎲 Somehow up 300% YTD?? My secret? Being too dumb to panic sell 🤷",
    "6jMQdtwEAfoBvKdE4HYGTdHCRSxYfCrgPmjQ6rnGr5mn": "night owl trader\nbest trades happen at 3am coffee-powered memecoin connoisseur\n\n'trust me bro' is my DD"
}

# Auto-seed demo traders on startup if database is empty
def auto_seed_demo_traders():
    """Automatically seed demo traders on startup if database has no users"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    # Check if we have any users
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    
    if user_count == 0:
        print("🌱 Database is empty! Auto-seeding demo traders...")
        for address, bio in DEMO_TRADER_BIOS.items():
            try:
                user_id = str(uuid.uuid4())
                c.execute("INSERT INTO users (id, wallet_address, bio) VALUES (?, ?, ?)",
                         (user_id, address, bio))
                print(f"   ✅ Added: {address[:8]}...")
            except Exception as e:
                print(f"   ⚠️  Skipped {address[:8]}...: {str(e)}")
        
        conn.commit()
        print(f"🎉 Auto-seed complete! Added {len(DEMO_TRADER_BIOS)} demo traders")
    else:
        print(f"✅ Database already has {user_count} users. Skipping auto-seed.")
    
    conn.close()

# Run auto-seed on startup
auto_seed_demo_traders()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, chat_room_id: str):
        await websocket.accept()
        self.active_connections[chat_room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_room_id: str):
        self.active_connections[chat_room_id].remove(websocket)

    async def broadcast(self, message: dict, chat_room_id: str):
        for connection in self.active_connections[chat_room_id]:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class UserCreate(BaseModel):
    wallet_address: str

class SwipeAction(BaseModel):
    user_wallet: str
    target_wallet: str
    direction: str  # "left" or "right"

class MessageCreate(BaseModel):
    chat_room_id: str
    sender_wallet: str
    message: str

class NansenConfig(BaseModel):
    api_key: str

class BioUpdate(BaseModel):
    bio: str

# Demo trader addresses (backup if database is empty) - REAL trader addresses
DEMO_TRADERS = [
    "ERjMXMF6AVnMckiQb6zvTEcaCVc7iBpNqmtbNVjeKCpc",
    "99HXufoq4yepb8hNKgd1ghXRKMwAfMoXCZjAdXxXyEUh",
    "Au1GUWfcadx7jMzhsg6gHGUgViYJrnPfL1vbdqnvLK4i",
    "8J6UcrwcSj6i9FdGeLYHUWNYiJrqhEAVJbWhjtBZvwHT",
    "EdAsdt7JY6fcBYNbzY4HxXTEWSupiQMdRS3KjNLuSLKy",
    "7Hkpf3NJwCdcnDqwZMTR1d76pHnfeyqnP8vxrV4TLKHR",
    "EvwaHadVPP7bTdmfc4cxk3Pz5sr638sVUq1BJY8HArW7",
    "2CSqY1nUFZbuznxY3PUMWdBUif6WAqsTWtrfZKJQUgTb",
    "6jMQdtwEAfoBvKdE4HYGTdHCRSxYfCrgPmjQ6rnGr5mn"
]

# Get all registered trader wallets from database
def get_all_trader_wallets():
    """Get all trader wallet addresses from the database (REAL USERS FIRST, then demos)"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    c.execute("SELECT wallet_address FROM users ORDER BY created_at DESC")
    real_wallets = [row[0] for row in c.fetchall()]
    conn.close()
    
    # Remove demo traders from real_wallets (in case they were manually added)
    real_users_only = [w for w in real_wallets if w not in DEMO_TRADERS]
    
    # ALWAYS show real users first, then demo traders as filler
    all_wallets = real_users_only + DEMO_TRADERS
    
    print(f"👥 Total profiles: {len(real_users_only)} real users + {len(DEMO_TRADERS)} demos")
    
    return all_wallets

# Store Nansen API key - Load from environment variable
nansen_api_key = os.getenv("NANSEN_API_KEY", "")
if nansen_api_key:
    print(f"✅ Nansen API key loaded: {nansen_api_key[:8]}...{nansen_api_key[-4:]}")
else:
    print("⚠️ WARNING: No NANSEN_API_KEY found! Using mock data.")

@app.post("/api/config/nansen")
async def set_nansen_config(config: NansenConfig):
    """Set Nansen API key"""
    global nansen_api_key
    nansen_api_key = config.api_key
    return {"status": "success", "message": "Nansen API key configured"}

@app.post("/api/users")
async def create_user(user: UserCreate):
    """Create a new user account"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT id FROM users WHERE wallet_address = ?", (user.wallet_address,))
    existing_user = c.fetchone()
    
    if existing_user:
        conn.close()
        return {"user_id": existing_user[0], "wallet_address": user.wallet_address, "exists": True}
    
    # Create new user
    user_id = str(uuid.uuid4())
    c.execute("INSERT INTO users (id, wallet_address) VALUES (?, ?)", 
              (user_id, user.wallet_address))
    conn.commit()
    conn.close()
    
    return {"user_id": user_id, "wallet_address": user.wallet_address, "exists": False}

@app.put("/api/users/{wallet_address}/bio")
async def update_user_bio(wallet_address: str, bio_data: BioUpdate):
    """Update user's bio"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    c.execute("UPDATE users SET bio = ? WHERE wallet_address = ?", 
              (bio_data.bio, wallet_address))
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Bio updated"}

@app.get("/api/profiles/{wallet_address}")
async def get_profiles(wallet_address: str):
    """Get profiles to swipe through (excluding already swiped wallets)"""
    # Cleanup expired cache entries periodically
    clear_expired_cache()
    
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    # Get user's already swiped wallets
    c.execute("""SELECT target_wallet FROM swipes 
                 WHERE user_id = (SELECT id FROM users WHERE wallet_address = ?)""", 
              (wallet_address,))
    swiped_wallets = [row[0] for row in c.fetchall()]
    conn.close()
    
    # Get all available trader wallets from database
    all_wallets = get_all_trader_wallets()
    
    # Filter out current user and already swiped wallets
    available_wallets = [w for w in all_wallets 
                         if w != wallet_address and w not in swiped_wallets]
    
    print(f"📊 Cache status: {len(nansen_cache)} wallets cached")
    
    profiles = []
    is_demo = lambda w: w in DEMO_TRADERS
    
    for wallet in available_wallets[:20]:  # Check more to account for skipped profiles
        if len(profiles) >= 10:  # Stop once we have 10 valid profiles
            break
            
        # Get Nansen data
        pnl_data = get_nansen_pnl(wallet)
        balance_data = get_nansen_balance(wallet)
        
        # For REAL users (not demos), skip if no valid data
        if not is_demo(wallet):
            # Check if we have real Nansen data (not mock/error data)
            has_real_pnl = (
                pnl_data.get("total_trades", 0) > 0 and 
                "time_period" in pnl_data
            )
            has_real_balance = balance_data.get("total_balance_usd", 0) > 0
            
            if not (has_real_pnl or has_real_balance):
                print(f"⚠️ Skipping real user {wallet[:8]}... - No valid Nansen data")
                continue
        
        # Get bio from database
        conn = sqlite3.connect('smartmoney.db')
        c = conn.cursor()
        c.execute("SELECT bio FROM users WHERE wallet_address = ?", (wallet,))
        bio_result = c.fetchone()
        conn.close()
        bio = bio_result[0] if bio_result else None
        
        profiles.append({
            "wallet_address": wallet,
            "pnl_summary": pnl_data,
            "balance": balance_data,
            "bio": bio,
            "is_demo": is_demo(wallet)
        })
    
    print(f"📊 Returning {len(profiles)} valid profiles")
    return {"profiles": profiles}

def get_nansen_pnl(wallet_address: str):
    """Fetch PnL summary from Nansen API with 90D fallback to all-time (CACHED)"""
    # Check cache first
    cached_pnl = get_cached_data(wallet_address, 'pnl')
    if cached_pnl:
        print(f"⚡ Cache HIT for PnL: {wallet_address[:8]}...")
        return cached_pnl
    
    print(f"💾 Cache MISS for PnL: {wallet_address[:8]}... fetching from API")
    
    if not nansen_api_key:
        print(f"⚠️ No Nansen API key - using mock data for {wallet_address[:8]}...")
        # Return mock data for demo
        pnl = round(1000 + hash(wallet_address) % 50000, 2)
        pnl_pct = round(10 + (hash(wallet_address) % 100), 1)
        win_rate = round(50 + (hash(wallet_address) % 40))
        mock_data = {
            "total_pnl": pnl,
            "total_pnl_formatted": format_currency(pnl),
            "pnl_percentage": pnl_pct,
            "win_rate": win_rate,
            "total_trades": 100 + (hash(wallet_address) % 500),
            "time_period": "90D"
        }
        set_cached_data(wallet_address, 'pnl', mock_data)
        return mock_data
    
    try:
        # Try 90 days first
        end_date = datetime.now()
        start_date_90d = end_date - timedelta(days=90)
        
        print(f"📊 Fetching Nansen 90D PnL for {wallet_address[:8]}...")
        
        response = requests.post(
            "https://api.nansen.ai/api/v1/profiler/address/pnl-summary",
            headers={"apiKey": nansen_api_key, "Content-Type": "application/json"},
            data=json.dumps({
                "address": wallet_address,
                "chain": "solana",
                "date": {
                    "from": start_date_90d.strftime("%Y-%m-%dT00:00:00Z"),
                    "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                }
            }),
            timeout=10
        )
        
        print(f"📊 Nansen 90D PnL Response: Status {response.status_code}")
        
        time_period = "90D"
        data = None
        
        if response.status_code == 200:
            data = response.json()
            # Check if we have meaningful data (traded_times > 0)
            if data.get("traded_times", 0) == 0:
                print(f"⚠️ No 90D trades, trying all-time for {wallet_address[:8]}...")
                # Try all-time (5 years)
                start_date_alltime = end_date - timedelta(days=1825)
                
                response_alltime = requests.post(
                    "https://api.nansen.ai/api/v1/profiler/address/pnl-summary",
                    headers={"apiKey": nansen_api_key, "Content-Type": "application/json"},
                    data=json.dumps({
                        "address": wallet_address,
                        "chain": "solana",
                        "date": {
                            "from": start_date_alltime.strftime("%Y-%m-%dT00:00:00Z"),
                            "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                        }
                    }),
                    timeout=10
                )
                
                if response_alltime.status_code == 200:
                    data = response_alltime.json()
                    time_period = "All Time"
                    print(f"✅ Using all-time PnL for {wallet_address[:8]}")
        
        if data and data.get("traded_times", 0) > 0:
            print(f"✅ Nansen PnL Data: {data}")
            
            # Extract and format values
            pnl = data.get("realized_pnl_usd", 0)
            pnl_pct = round(data.get("realized_pnl_percent", 0) * 100, 1)  # Round to 0.1%
            win_rate = round(data.get("win_rate", 0) * 100)  # Round to nearest %
            
            # Transform Nansen response to frontend-expected format
            result = {
                "total_pnl": pnl,
                "total_pnl_formatted": format_currency(pnl),
                "pnl_percentage": pnl_pct,
                "win_rate": win_rate,
                "total_trades": data.get("traded_times", 0),
                "traded_token_count": data.get("traded_token_count", 0),
                "time_period": time_period
            }
            
            # Cache the successful result
            set_cached_data(wallet_address, 'pnl', result)
            return result
        else:
            print(f"❌ Nansen PnL Error: {response.status_code} - {response.text}")
            # Return mock data on error
            pnl = round(1000 + hash(wallet_address) % 50000, 2)
            pnl_pct = round(10 + (hash(wallet_address) % 100), 1)
            win_rate = round(50 + (hash(wallet_address) % 40))
            return {
                "total_pnl": pnl,
                "total_pnl_formatted": format_currency(pnl),
                "pnl_percentage": pnl_pct,
                "win_rate": win_rate,
                "total_trades": 100 + (hash(wallet_address) % 500),
                "time_period": "90D"
            }
    except Exception as e:
        print(f"❌ Exception fetching Nansen PnL: {str(e)}")
        # Return mock data on exception
        pnl = round(1000 + hash(wallet_address) % 50000, 2)
        pnl_pct = round(10 + (hash(wallet_address) % 100), 1)
        win_rate = round(50 + (hash(wallet_address) % 40))
        return {
            "total_pnl": pnl,
            "total_pnl_formatted": format_currency(pnl),
            "pnl_percentage": pnl_pct,
            "win_rate": win_rate,
            "total_trades": 100 + (hash(wallet_address) % 500),
            "time_period": "90D"
        }

def get_nansen_balance(wallet_address: str):
    """Fetch current balance from Nansen API (CACHED)"""
    # Check cache first
    cached_balance = get_cached_data(wallet_address, 'balance')
    if cached_balance:
        print(f"⚡ Cache HIT for balance: {wallet_address[:8]}...")
        return cached_balance
    
    print(f"💾 Cache MISS for balance: {wallet_address[:8]}... fetching from API")
    
    if not nansen_api_key:
        print(f"⚠️ No Nansen API key - using mock balance for {wallet_address[:8]}...")
        # Return mock data for demo
        balance = round(10000 + hash(wallet_address[:10]) % 100000, 2)
        sol = round(50 + (hash(wallet_address[:8]) % 500), 2)
        mock_data = {
            "total_balance_usd": balance,
            "total_balance_formatted": format_currency(balance),
            "sol_balance": sol,
            "sol_balance_formatted": f"{round(sol, 1)} SOL",
            "token_count": 5 + (hash(wallet_address[:6]) % 20)
        }
        set_cached_data(wallet_address, 'balance', mock_data)
        return mock_data
    
    try:
        print(f"💰 Fetching Nansen balance for {wallet_address[:8]}...")
        
        response = requests.post(
            "https://api.nansen.ai/api/v1/profiler/address/current-balance",
            headers={"apiKey": nansen_api_key, "Content-Type": "application/json"},
            data=json.dumps({
                "address": wallet_address,
                "chain": "solana",
                "hide_spam_token": True,
                "pagination": {
                    "page": 1,
                    "per_page": 10
                }
            }),
            timeout=10
        )
        
        print(f"💰 Nansen Balance Response: Status {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Nansen Balance Data: {data}")
            
            # Transform Nansen response to frontend-expected format
            tokens = data.get("data", [])
            
            # Calculate total balance
            total_balance_usd = sum(token.get("value_usd", 0) for token in tokens)
            
            # Find SOL balance
            sol_balance = 0
            for token in tokens:
                if token.get("token_symbol") == "SOL":
                    sol_balance = token.get("token_amount", 0)
                    break
            
            result = {
                "total_balance_usd": round(total_balance_usd, 2),
                "total_balance_formatted": format_currency(total_balance_usd),
                "sol_balance": round(sol_balance, 2),
                "sol_balance_formatted": f"{round(sol_balance, 1)} SOL" if sol_balance < 1000 else f"{round(sol_balance / 1000, 1)}k SOL",
                "token_count": len(tokens),
                "tokens": tokens[:5]  # Include top 5 tokens for detail
            }
            
            # Cache the successful result
            set_cached_data(wallet_address, 'balance', result)
            return result
        else:
            print(f"❌ Nansen Balance Error: {response.status_code} - {response.text}")
            # Return mock data on error
            balance = round(10000 + hash(wallet_address[:10]) % 100000, 2)
            sol = round(50 + (hash(wallet_address[:8]) % 500), 2)
            return {
                "total_balance_usd": balance,
                "total_balance_formatted": format_currency(balance),
                "sol_balance": sol,
                "sol_balance_formatted": f"{round(sol, 1)} SOL",
                "token_count": 5 + (hash(wallet_address[:6]) % 20)
            }
    except Exception as e:
        print(f"❌ Exception fetching Nansen balance: {str(e)}")
        # Return mock data on exception
        balance = round(10000 + hash(wallet_address[:10]) % 100000, 2)
        sol = round(50 + (hash(wallet_address[:8]) % 500), 2)
        return {
            "total_balance_usd": balance,
            "total_balance_formatted": format_currency(balance),
            "sol_balance": sol,
            "sol_balance_formatted": f"{round(sol, 1)} SOL",
            "token_count": 5 + (hash(wallet_address[:6]) % 20)
        }

@app.post("/api/swipe")
async def swipe(swipe_action: SwipeAction):
    """Record a swipe action"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    # Get user ID
    c.execute("SELECT id FROM users WHERE wallet_address = ?", (swipe_action.user_wallet,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user[0]
    
    # Record swipe
    swipe_id = str(uuid.uuid4())
    c.execute("INSERT INTO swipes (id, user_id, target_wallet, direction) VALUES (?, ?, ?, ?)",
              (swipe_id, user_id, swipe_action.target_wallet, swipe_action.direction))
    
    # Check for match if swiped right
    match_created = False
    chat_room_id = None
    
    if swipe_action.direction == "right":
        # Check if target wallet also swiped right on this user
        c.execute("""SELECT s.id FROM swipes s
                     JOIN users u ON s.user_id = u.id
                     WHERE u.wallet_address = ? 
                     AND s.target_wallet = ? 
                     AND s.direction = 'right'""",
                  (swipe_action.target_wallet, swipe_action.user_wallet))
        
        mutual_swipe = c.fetchone()
        
        if mutual_swipe:
            # Create match
            match_id = str(uuid.uuid4())
            chat_room_id = str(uuid.uuid4())
            c.execute("""INSERT INTO matches (id, user1_wallet, user2_wallet, chat_room_id) 
                         VALUES (?, ?, ?, ?)""",
                      (match_id, swipe_action.user_wallet, swipe_action.target_wallet, chat_room_id))
            match_created = True
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "match_created": match_created,
        "chat_room_id": chat_room_id
    }

@app.get("/api/matches/{wallet_address}")
async def get_matches(wallet_address: str):
    """Get all matches for a user"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    c.execute("""SELECT user1_wallet, user2_wallet, chat_room_id, created_at 
                 FROM matches 
                 WHERE user1_wallet = ? OR user2_wallet = ?
                 ORDER BY created_at DESC""",
              (wallet_address, wallet_address))
    
    matches = []
    for row in c.fetchall():
        other_wallet = row[1] if row[0] == wallet_address else row[0]
        matches.append({
            "wallet_address": other_wallet,
            "chat_room_id": row[2],
            "created_at": row[3]
        })
    
    conn.close()
    return {"matches": matches}

@app.get("/api/chat/{chat_room_id}/messages")
async def get_messages(chat_room_id: str, limit: int = 50):
    """Get messages for a chat room"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    c.execute("""SELECT sender_wallet, message, created_at 
                 FROM messages 
                 WHERE chat_room_id = ? 
                 ORDER BY created_at DESC 
                 LIMIT ?""",
              (chat_room_id, limit))
    
    messages = []
    for row in c.fetchall():
        messages.append({
            "sender_wallet": row[0],
            "message": row[1],
            "created_at": row[2]
        })
    
    conn.close()
    return {"messages": list(reversed(messages))}

@app.post("/api/chat/message")
async def send_message(message_data: MessageCreate):
    """Send a message to a chat room"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    
    message_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    c.execute("""INSERT INTO messages (id, chat_room_id, sender_wallet, message, created_at) 
                 VALUES (?, ?, ?, ?, ?)""",
              (message_id, message_data.chat_room_id, message_data.sender_wallet, 
               message_data.message, created_at))
    
    conn.commit()
    conn.close()
    
    # Broadcast message to WebSocket connections
    await manager.broadcast({
        "sender_wallet": message_data.sender_wallet,
        "message": message_data.message,
        "created_at": created_at
    }, message_data.chat_room_id)
    
    return {"status": "success", "message_id": message_id}

@app.websocket("/ws/chat/{chat_room_id}")
async def websocket_chat(websocket: WebSocket, chat_room_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, chat_room_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_room_id)

@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    current_time = time.time()
    cached_wallets = []
    
    for wallet, data in nansen_cache.items():
        age_seconds = current_time - data.get('timestamp', 0)
        cached_wallets.append({
            "wallet": f"{wallet[:8]}...{wallet[-4:]}",
            "age_seconds": round(age_seconds, 1),
            "has_pnl": 'pnl' in data,
            "has_balance": 'balance' in data,
            "expires_in": round(CACHE_TTL_SECONDS - age_seconds, 1)
        })
    
    return {
        "total_cached": len(nansen_cache),
        "ttl_seconds": CACHE_TTL_SECONDS,
        "wallets": cached_wallets
    }

@app.post("/api/cache/clear")
async def clear_cache():
    """Manually clear all cache"""
    global nansen_cache
    count = len(nansen_cache)
    nansen_cache = {}
    return {"status": "success", "cleared": count}

@app.get("/")
async def root():
    return {"message": "Smart Money Tinder API", "status": "running", "cache_enabled": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

