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

# Get all registered trader wallets from database
def get_all_trader_wallets():
    """Get all trader wallet addresses from the database"""
    conn = sqlite3.connect('smartmoney.db')
    c = conn.cursor()
    c.execute("SELECT wallet_address FROM users")
    wallets = [row[0] for row in c.fetchall()]
    conn.close()
    return wallets

# Store Nansen API key - Load from environment variable
nansen_api_key = os.getenv("NANSEN_API_KEY", "")

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

@app.get("/api/profiles/{wallet_address}")
async def get_profiles(wallet_address: str):
    """Get profiles to swipe through (excluding already swiped wallets)"""
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
    
    profiles = []
    for wallet in available_wallets[:10]:  # Return up to 10 profiles
        # Get Nansen data
        pnl_data = get_nansen_pnl(wallet)
        balance_data = get_nansen_balance(wallet)
        
        profiles.append({
            "wallet_address": wallet,
            "pnl_summary": pnl_data,
            "balance": balance_data
        })
    
    return {"profiles": profiles}

def get_nansen_pnl(wallet_address: str):
    """Fetch PnL summary from Nansen API"""
    if not nansen_api_key:
        # Return mock data for demo
        return {
            "total_pnl": round(1000 + hash(wallet_address) % 50000, 2),
            "pnl_percentage": round(10 + (hash(wallet_address) % 100), 2),
            "win_rate": round(50 + (hash(wallet_address) % 40), 2),
            "total_trades": 100 + (hash(wallet_address) % 500)
        }
    
    try:
        # Calculate 90 days ago
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        response = requests.post(
            "https://api.nansen.ai/api/v1/profiler/address/pnl-summary",
            headers={"apiKey": nansen_api_key, "Content-Type": "application/json"},
            data=json.dumps({
                "address": wallet_address,
                "chain": "solana",
                "date": {
                    "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                    "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                }
            }),
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch PnL data"}
    except Exception as e:
        return {"error": str(e)}

def get_nansen_balance(wallet_address: str):
    """Fetch current balance from Nansen API"""
    if not nansen_api_key:
        # Return mock data for demo
        return {
            "total_balance_usd": round(10000 + hash(wallet_address[:10]) % 100000, 2),
            "sol_balance": round(50 + (hash(wallet_address[:8]) % 500), 2),
            "token_count": 5 + (hash(wallet_address[:6]) % 20)
        }
    
    try:
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
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch balance data"}
    except Exception as e:
        return {"error": str(e)}

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

@app.get("/")
async def root():
    return {"message": "Smart Money Tinder API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

