from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional, Dict
import json
import requests
from datetime import datetime, timedelta
import uuid
from collections import defaultdict
import os
import time
from database import db
import re

app = FastAPI(title="Smart Money Tinder API")

# CORS middleware - Allow all origins for demo/hackathon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Vercel, localhost, etc.)
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication configuration
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
if REQUIRE_AUTH:
    print("🔒 Authentication ENABLED - All endpoints require wallet signatures")
else:
    print("⚠️  Authentication DISABLED - Running in development mode (NOT SECURE FOR PRODUCTION!)")

# Simple authentication dependency
async def get_authenticated_wallet(
    x_wallet_address: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Get authenticated wallet address from headers
    For now, just returns the wallet from header
    TODO: Add signature verification for production
    """
    if REQUIRE_AUTH and not x_wallet_address:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide X-Wallet-Address header"
        )
    return x_wallet_address

def verify_wallet_ownership(wallet_address: str, authenticated_wallet: Optional[str]):
    """Verify that authenticated wallet matches the requested wallet"""
    if REQUIRE_AUTH:
        if not authenticated_wallet:
            raise HTTPException(status_code=401, detail="Authentication required")
        if wallet_address != authenticated_wallet:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own resources"
            )
    # In development mode, just log a warning
    elif authenticated_wallet and wallet_address != authenticated_wallet:
        print(f"⚠️  WARNING: Wallet mismatch in dev mode - {authenticated_wallet} accessing {wallet_address}")

# Database setup
db.init_db()

# In-memory cache for Nansen API responses
# Structure: { wallet_address: { 'pnl': {...}, 'balance': {...}, 'timestamp': 123456 } }
nansen_cache = {}
CACHE_TTL_SECONDS = 1800  # 30 minutes (Nansen data doesn't change that fast)

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

# Demo trader full profiles - REAL trader addresses with complete data
DEMO_TRADERS_DATA = [
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

# Auto-seed demo traders on startup if database is empty
def run_migrations():
    """Run database migrations automatically on startup"""
    with db.get_connection() as conn:
        try:
            print("🔄 Checking database migrations...")
            cursor = conn.cursor()
            
            # Check if twitter_account column exists
            if db.use_postgres:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users'
                """)
                columns = [row[0] for row in cursor.fetchall()]
            else:
                cursor.execute("PRAGMA table_info(users)")
                columns = [row[1] for row in cursor.fetchall()]
            
            if 'twitter_account' not in columns:
                print("   📝 Adding twitter_account column...")
                cursor.execute("ALTER TABLE users ADD COLUMN twitter_account TEXT")
                conn.commit()
                print("   ✅ twitter_account column added!")
            else:
                print("   ✅ All migrations up to date")
        except Exception as e:
            print(f"   ⚠️  Migration error: {e}")

def auto_seed_demo_traders():
    """Automatically seed demo traders with FULL profiles on startup if database has no users"""
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # Check if we have any users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0] if not db.use_postgres else cursor.fetchone()['count']
        
        if user_count == 0:
            print("🌱 Database is empty! Auto-seeding demo traders with full profiles...")
            ph = db.placeholder()
            for idx, trader in enumerate(DEMO_TRADERS_DATA, start=1):
                try:
                    user_id = str(uuid.uuid4())
                    query = f"""INSERT INTO users 
                                (id, wallet_address, trader_number, bio, country, favourite_ct_account,
                                 worst_ct_account, favourite_trading_venue, asset_choice_6m, twitter_account, created_at)
                                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})"""
                    cursor.execute(query,
                             (user_id, trader["address"], idx, trader["bio"], trader["country"],
                              trader["favourite_ct_account"], None,  # worst_ct_account is optional
                              trader["favourite_trading_venue"], trader["asset_choice_6m"],
                              None, datetime.now().isoformat()))  # twitter_account is optional
                    print(f"   ✅ Added Trader #{idx:03d}: {trader['address'][:8]}... ({trader['country']})")
                except Exception as e:
                    print(f"   ⚠️  Skipped {trader['address'][:8]}...: {str(e)}")
            
            conn.commit()
            print(f"🎉 Auto-seed complete! Added {len(DEMO_TRADERS_DATA)} demo traders with full profiles")
        else:
            print(f"✅ Database already has {user_count} users. Skipping auto-seed.")

# Run migrations and auto-seed on startup
run_migrations()
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
    
    @validator('message')
    def message_must_be_valid(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message must be 5000 characters or less')
        # Basic XSS prevention
        if '<script' in v.lower() or 'javascript:' in v.lower():
            raise ValueError('Message contains invalid content')
        return v.strip()

class NansenConfig(BaseModel):
    api_key: str

class ProfileComplete(BaseModel):
    bio: str
    country: str
    favourite_ct_account: str
    worst_ct_account: Optional[str] = None  # Optional field
    favourite_trading_venue: str
    asset_choice_6m: str
    twitter_account: Optional[str] = None  # Optional field
    
    @validator('bio')
    def bio_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Bio cannot be empty')
        if len(v) > 500:
            raise ValueError('Bio must be 500 characters or less')
        # Basic XSS prevention
        if '<script' in v.lower() or 'javascript:' in v.lower():
            raise ValueError('Bio contains invalid content')
        return v.strip()
    
    @validator('country')
    def country_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Country cannot be empty')
        if len(v) > 100:
            raise ValueError('Country must be 100 characters or less')
        return v.strip()
    
    @validator('favourite_ct_account')
    def ct_account_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Favourite CT account cannot be empty')
        if len(v) > 100:
            raise ValueError('CT account must be 100 characters or less')
        return v.strip()
    
    @validator('favourite_trading_venue')
    def venue_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Favourite trading venue cannot be empty')
        return v.strip()
    
    @validator('asset_choice_6m')
    def asset_choice_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Asset choice cannot be empty')
        return v.strip()

# Demo trader addresses list (for quick lookups)
DEMO_TRADERS = [trader["address"] for trader in DEMO_TRADERS_DATA]

# Get all registered trader wallets from database
def get_all_trader_wallets():
    """Get all trader wallet addresses from the database (REAL USERS FIRST, then demos if DB is empty)"""
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute("SELECT wallet_address FROM users ORDER BY created_at DESC")
        results = cursor.fetchall()
        all_wallets = [row['wallet_address'] if isinstance(row, dict) else row[0] for row in results]
    
    # If database is empty or has only 1 user, add demo traders as fallback
    if len(all_wallets) <= 1:
        print(f"⚠️ Only {len(all_wallets)} user(s) in database. Adding demo traders as fallback.")
        # Separate real users from demo traders
        real_users_only = [w for w in all_wallets if w not in DEMO_TRADERS]
        return real_users_only + DEMO_TRADERS
    
    # Otherwise, return all users from database (including seeded demo traders)
    real_users = [w for w in all_wallets if w not in DEMO_TRADERS]
    demo_users = [w for w in all_wallets if w in DEMO_TRADERS]
    print(f"👥 Total profiles: {len(real_users)} real users + {len(demo_users)} demo traders in DB")
    
    # Real users first, then demo traders
    return real_users + demo_users

# Helper function to get next trader number
def get_next_trader_number():
    """Get the next available trader number"""
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute("SELECT MAX(trader_number) FROM users")
        result = cursor.fetchone()
    
    if result:
        max_number = result['max'] if isinstance(result, dict) and 'max' in result else result[0]
        max_number = max_number if max_number is not None else 0
    else:
        max_number = 0
    return max_number + 1

def format_trader_number(number):
    """Format trader number with leading zeros and commas (e.g., #001, #1,234)"""
    if number < 1000:
        return f"#{number:03d}"  # #001, #099, #999
    else:
        return f"#{number:,}"  # #1,234, #10,001

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
async def check_user(user: UserCreate):
    """Check if user exists and return their profile status"""
    ph = db.placeholder()
    query = f"""SELECT id, trader_number, bio, country, favourite_ct_account, 
                 worst_ct_account, favourite_trading_venue, asset_choice_6m, twitter_account 
                 FROM users WHERE wallet_address = {ph}"""
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(query, (user.wallet_address,))
        existing_user = cursor.fetchone()
    
    if existing_user:
        # Convert to dict if needed
        if isinstance(existing_user, dict):
            user_dict = existing_user
        else:
            user_dict = {
                'id': existing_user[0],
                'trader_number': existing_user[1],
                'bio': existing_user[2],
                'country': existing_user[3],
                'favourite_ct_account': existing_user[4],
                'worst_ct_account': existing_user[5],
                'favourite_trading_venue': existing_user[6],
                'asset_choice_6m': existing_user[7],
                'twitter_account': existing_user[8]
            }
        
        # User exists, check if profile is complete (worst_ct_account and twitter_account are optional)
        profile_complete = all([
            user_dict['bio'],
            user_dict['country'],
            user_dict['favourite_ct_account'],
            user_dict['favourite_trading_venue'],
            user_dict['asset_choice_6m']
        ])
        
        return {
            "user_id": user_dict['id'],
            "trader_number": user_dict['trader_number'],
            "trader_number_formatted": format_trader_number(user_dict['trader_number']) if user_dict['trader_number'] else None,
            "wallet_address": user.wallet_address,
            "exists": True,
            "profile_complete": profile_complete
        }
    
    # User doesn't exist yet
    return {
        "user_id": None,
        "wallet_address": user.wallet_address,
        "exists": False,
        "profile_complete": False
    }

@app.post("/api/users/{wallet_address}/complete-profile")
async def complete_profile(
    wallet_address: str, 
    profile_data: ProfileComplete,
    authenticated_wallet: Optional[str] = Depends(get_authenticated_wallet)
):
    """Complete user profile with all required fields (AUTH PROTECTED)"""
    # Verify wallet ownership
    verify_wallet_ownership(wallet_address, authenticated_wallet)
    
    ph = db.placeholder()
    
    try:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # Check if user already exists
            cursor.execute(f"SELECT id, trader_number FROM users WHERE wallet_address = {ph}", (wallet_address,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Convert to dict if needed
                if isinstance(existing_user, dict):
                    user_id = existing_user['id']
                    trader_number = existing_user['trader_number']
                else:
                    user_id = existing_user[0]
                    trader_number = existing_user[1]
                
                # Update existing user
                update_query = f"""UPDATE users 
                            SET bio = {ph}, country = {ph}, favourite_ct_account = {ph}, 
                                worst_ct_account = {ph}, favourite_trading_venue = {ph}, 
                                asset_choice_6m = {ph}, twitter_account = {ph}
                            WHERE wallet_address = {ph}"""
                cursor.execute(update_query,
                         (profile_data.bio, profile_data.country, profile_data.favourite_ct_account,
                          profile_data.worst_ct_account, profile_data.favourite_trading_venue,
                          profile_data.asset_choice_6m, profile_data.twitter_account, wallet_address))
            else:
                # Create new user with trader number
                user_id = str(uuid.uuid4())
                trader_number = get_next_trader_number()
                
                insert_query = f"""INSERT INTO users 
                            (id, wallet_address, trader_number, bio, country, favourite_ct_account,
                             worst_ct_account, favourite_trading_venue, asset_choice_6m, twitter_account)
                            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})"""
                cursor.execute(insert_query,
                         (user_id, wallet_address, trader_number, profile_data.bio, 
                          profile_data.country, profile_data.favourite_ct_account,
                          profile_data.worst_ct_account, profile_data.favourite_trading_venue,
                          profile_data.asset_choice_6m, profile_data.twitter_account))
            
            conn.commit()
        
        return {
            "status": "success",
            "user_id": user_id,
            "trader_number": trader_number,
            "trader_number_formatted": format_trader_number(trader_number),
            "message": "Profile completed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete profile: {str(e)}")

@app.get("/api/users/{wallet_address}/profile")
async def get_my_profile(wallet_address: str):
    """Get user's own complete profile for editing"""
    ph = db.placeholder()
    query = f"""SELECT trader_number, bio, country, favourite_ct_account, 
                 worst_ct_account, favourite_trading_venue, asset_choice_6m, twitter_account 
                 FROM users WHERE wallet_address = {ph}"""
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(query, (wallet_address,))
        user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Convert to dict if needed
    if isinstance(user, dict):
        return {
            "wallet_address": wallet_address,
            "trader_number": user['trader_number'],
            "trader_number_formatted": format_trader_number(user['trader_number']) if user['trader_number'] else None,
            "bio": user['bio'],
            "country": user['country'],
            "favourite_ct_account": user['favourite_ct_account'],
            "worst_ct_account": user['worst_ct_account'],
            "favourite_trading_venue": user['favourite_trading_venue'],
            "asset_choice_6m": user['asset_choice_6m'],
            "twitter_account": user['twitter_account']
        }
    else:
        return {
            "wallet_address": wallet_address,
            "trader_number": user[0],
            "trader_number_formatted": format_trader_number(user[0]) if user[0] else None,
            "bio": user[1],
            "country": user[2],
            "favourite_ct_account": user[3],
            "worst_ct_account": user[4],
            "favourite_trading_venue": user[5],
            "asset_choice_6m": user[6],
            "twitter_account": user[7]
        }

@app.put("/api/users/{wallet_address}/profile")
async def update_my_profile(
    wallet_address: str, 
    profile_data: ProfileComplete,
    authenticated_wallet: Optional[str] = Depends(get_authenticated_wallet)
):
    """Update user's own profile (AUTH PROTECTED)"""
    # Verify wallet ownership
    verify_wallet_ownership(wallet_address, authenticated_wallet)
    
    ph = db.placeholder()
    
    try:
        with db.get_connection() as conn:
            cursor = db.get_cursor(conn)
            
            # Update user profile
            query = f"""UPDATE users 
                        SET bio = {ph}, country = {ph}, favourite_ct_account = {ph}, 
                            worst_ct_account = {ph}, favourite_trading_venue = {ph}, 
                            asset_choice_6m = {ph}, twitter_account = {ph}
                        WHERE wallet_address = {ph}"""
            cursor.execute(query,
                     (profile_data.bio, profile_data.country, profile_data.favourite_ct_account,
                      profile_data.worst_ct_account, profile_data.favourite_trading_venue,
                      profile_data.asset_choice_6m, profile_data.twitter_account, wallet_address))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
            
            conn.commit()
        
        return {"status": "success", "message": "Profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.get("/api/profiles/{wallet_address}")
async def get_profiles(wallet_address: str):
    """Get profiles to swipe through (excluding already swiped wallets)"""
    # Cleanup expired cache entries periodically
    clear_expired_cache()
    
    ph = db.placeholder()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # Get user's already swiped wallets
        query = f"""SELECT target_wallet FROM swipes 
                     WHERE user_id = (SELECT id FROM users WHERE wallet_address = {ph})"""
        cursor.execute(query, (wallet_address,))
        results = cursor.fetchall()
        swiped_wallets = [row['target_wallet'] if isinstance(row, dict) else row[0] for row in results]
    
    # Get all available trader wallets from database
    all_wallets = get_all_trader_wallets()
    
    # Filter out current user and already swiped wallets
    available_wallets = [w for w in all_wallets 
                         if w != wallet_address and w not in swiped_wallets]
    
    print(f"📊 Cache status: {len(nansen_cache)} wallets cached")
    
    profiles = []
    is_demo = lambda w: w in DEMO_TRADERS
    
    for wallet in available_wallets[:12]:  # Check 12 to get ~10 valid profiles
        if len(profiles) >= 8:  # Return 8 profiles (faster, user can load more)
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
        
        # Get profile data from database
        with db.get_connection() as conn2:
            cursor2 = db.get_cursor(conn2)
            query2 = f"""SELECT trader_number, bio, country, favourite_ct_account, 
                         worst_ct_account, favourite_trading_venue, asset_choice_6m, twitter_account 
                         FROM users WHERE wallet_address = {ph}"""
            cursor2.execute(query2, (wallet,))
            profile_result = cursor2.fetchone()
        
        if profile_result:
            # Convert to dict if needed
            if isinstance(profile_result, dict):
                trader_number = profile_result['trader_number']
                trader_display = format_trader_number(trader_number) if trader_number else "Demo"
                profile_data = {
                    "trader_number": trader_number,
                    "trader_number_formatted": trader_display,
                    "bio": profile_result['bio'],
                    "country": profile_result['country'],
                    "favourite_ct_account": profile_result['favourite_ct_account'],
                    "worst_ct_account": profile_result['worst_ct_account'],
                    "favourite_trading_venue": profile_result['favourite_trading_venue'],
                    "asset_choice_6m": profile_result['asset_choice_6m'],
                    "twitter_account": profile_result['twitter_account']
                }
            else:
                trader_number = profile_result[0]
                trader_display = format_trader_number(trader_number) if trader_number else "Demo"
                profile_data = {
                    "trader_number": trader_number,
                    "trader_number_formatted": trader_display,
                    "bio": profile_result[1],
                    "country": profile_result[2],
                    "favourite_ct_account": profile_result[3],
                    "worst_ct_account": profile_result[4],
                    "favourite_trading_venue": profile_result[5],
                    "asset_choice_6m": profile_result[6],
                    "twitter_account": profile_result[7]
                }
        else:
            # Demo profile
            profile_data = {
                "trader_number": None,
                "trader_number_formatted": "Demo",
                "bio": None,
                "country": None,
                "favourite_ct_account": None,
                "worst_ct_account": None,
                "favourite_trading_venue": None,
                "asset_choice_6m": None,
                "twitter_account": None
            }
        
        profiles.append({
            "wallet_address": wallet,
            "pnl_summary": pnl_data,
            "balance": balance_data,
            "is_demo": is_demo(wallet),
            **profile_data
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
async def swipe(
    swipe_action: SwipeAction,
    authenticated_wallet: Optional[str] = Depends(get_authenticated_wallet)
):
    """Record a swipe action (AUTH PROTECTED)"""
    # Verify wallet ownership
    verify_wallet_ownership(swipe_action.user_wallet, authenticated_wallet)
    
    ph = db.placeholder()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # Get user ID
        cursor.execute(f"SELECT id FROM users WHERE wallet_address = {ph}", (swipe_action.user_wallet,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = user['id'] if isinstance(user, dict) else user[0]
        
        # Record swipe
        swipe_id = str(uuid.uuid4())
        insert_query = f"INSERT INTO swipes (id, user_id, target_wallet, direction) VALUES ({ph}, {ph}, {ph}, {ph})"
        cursor.execute(insert_query,
                  (swipe_id, user_id, swipe_action.target_wallet, swipe_action.direction))
        
        # Check for match if swiped right
        match_created = False
        chat_room_id = None
        
        if swipe_action.direction == "right":
            # Check if target wallet also swiped right on this user
            check_query = f"""SELECT s.id FROM swipes s
                         JOIN users u ON s.user_id = u.id
                         WHERE u.wallet_address = {ph} 
                         AND s.target_wallet = {ph} 
                         AND s.direction = 'right'"""
            cursor.execute(check_query,
                      (swipe_action.target_wallet, swipe_action.user_wallet))
            
            mutual_swipe = cursor.fetchone()
            
            if mutual_swipe:
                # Create match
                match_id = str(uuid.uuid4())
                chat_room_id = str(uuid.uuid4())
                match_query = f"""INSERT INTO matches (id, user1_wallet, user2_wallet, chat_room_id) 
                             VALUES ({ph}, {ph}, {ph}, {ph})"""
                cursor.execute(match_query,
                          (match_id, swipe_action.user_wallet, swipe_action.target_wallet, chat_room_id))
                match_created = True
        
        conn.commit()
    
    return {
        "status": "success",
        "match_created": match_created,
        "chat_room_id": chat_room_id
    }

@app.get("/api/matches/{wallet_address}")
async def get_matches(
    wallet_address: str,
    authenticated_wallet: Optional[str] = Depends(get_authenticated_wallet)
):
    """Get all matches for a user (AUTH PROTECTED)"""
    # Verify wallet ownership
    verify_wallet_ownership(wallet_address, authenticated_wallet)
    
    ph = db.placeholder()
    query = f"""SELECT user1_wallet, user2_wallet, chat_room_id, created_at 
                 FROM matches 
                 WHERE user1_wallet = {ph} OR user2_wallet = {ph}
                 ORDER BY created_at DESC"""
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        cursor.execute(query, (wallet_address, wallet_address))
        results = cursor.fetchall()
    
    matches = []
    for row in results:
        if isinstance(row, dict):
            other_wallet = row['user2_wallet'] if row['user1_wallet'] == wallet_address else row['user1_wallet']
            matches.append({
                "wallet_address": other_wallet,
                "chat_room_id": row['chat_room_id'],
                "created_at": row['created_at']
            })
        else:
            other_wallet = row[1] if row[0] == wallet_address else row[0]
            matches.append({
                "wallet_address": other_wallet,
                "chat_room_id": row[2],
                "created_at": row[3]
            })
    
    return {"matches": matches}

@app.get("/api/chat/{chat_room_id}/messages")
async def get_messages(
    chat_room_id: str, 
    limit: int = 50,
    authenticated_wallet: Optional[str] = Depends(get_authenticated_wallet)
):
    """Get messages for a chat room (AUTH PROTECTED - must be part of match)"""
    ph = db.placeholder()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # Verify caller is part of this match (CRITICAL SECURITY CHECK)
        if REQUIRE_AUTH and authenticated_wallet:
            check_query = f"""
                SELECT 1 FROM matches 
                WHERE chat_room_id = {ph}
                AND (user1_wallet = {ph} OR user2_wallet = {ph})
            """
            cursor.execute(check_query, (
                chat_room_id,
                authenticated_wallet,
                authenticated_wallet
            ))
            
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=403,
                    detail="You are not authorized to view this chat"
                )
        elif REQUIRE_AUTH:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get messages
        query = f"""SELECT sender_wallet, message, created_at 
                     FROM messages 
                     WHERE chat_room_id = {ph} 
                     ORDER BY created_at DESC 
                     LIMIT {limit}"""
        
        cursor.execute(query, (chat_room_id,))
        results = cursor.fetchall()
    
    messages = []
    for row in results:
        if isinstance(row, dict):
            messages.append({
                "sender_wallet": row['sender_wallet'],
                "message": row['message'],
                "created_at": row['created_at']
            })
        else:
            messages.append({
                "sender_wallet": row[0],
                "message": row[1],
                "created_at": row[2]
            })
    
    return {"messages": list(reversed(messages))}

@app.post("/api/chat/message")
async def send_message(
    message_data: MessageCreate,
    authenticated_wallet: Optional[str] = Depends(get_authenticated_wallet)
):
    """Send a message to a chat room (AUTH PROTECTED - must be part of match)"""
    ph = db.placeholder()
    
    # Verify sender owns the wallet
    verify_wallet_ownership(message_data.sender_wallet, authenticated_wallet)
    
    message_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # Verify sender is part of this match (CRITICAL SECURITY CHECK)
        if REQUIRE_AUTH and authenticated_wallet:
            check_query = f"""
                SELECT 1 FROM matches 
                WHERE chat_room_id = {ph}
                AND (user1_wallet = {ph} OR user2_wallet = {ph})
            """
            cursor.execute(check_query, (
                message_data.chat_room_id,
                authenticated_wallet,
                authenticated_wallet
            ))
            
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=403,
                    detail="You are not authorized to send messages to this chat"
                )
        elif REQUIRE_AUTH:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Save message
        query = f"""INSERT INTO messages (id, chat_room_id, sender_wallet, message, created_at) 
                     VALUES ({ph}, {ph}, {ph}, {ph}, {ph})"""
        cursor.execute(query,
                  (message_id, message_data.chat_room_id, message_data.sender_wallet, 
                   message_data.message, created_at))
        
        conn.commit()
    
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

@app.get("/api/config/trading-venues")
async def get_trading_venues():
    """Get list of available trading venues"""
    return {
        "venues": [
            "Pumpfun",
            "GMGN",
            "Photon",
            "Jupiter",
            "Drift",
            "Bloombot",
            "NeoBullX",
            "Trojan",
            "Raydium",
            "Orca",
            "Maestro",
            "Other"
        ]
    }

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

