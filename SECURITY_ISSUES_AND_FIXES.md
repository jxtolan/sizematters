# 🚨 CRITICAL SECURITY ISSUES & FIXES

## Executive Summary

**SEVERITY: 🔴 CRITICAL**

Your backend has **NO AUTHENTICATION** - anyone can:
- ✅ Update anyone's profile/bio
- ✅ Send messages as anyone
- ✅ Read anyone's chats
- ✅ See anyone's matches
- ✅ Create fake swipes/matches

**Status:** Currently in production with these vulnerabilities!

---

## 🔴 Issue #1: No Wallet Authentication (CRITICAL)

### Current Code (VULNERABLE):

```python
@app.put("/api/users/{wallet_address}/profile")
async def update_my_profile(wallet_address: str, profile_data: ProfileComplete):
    # ❌ Anyone can call this and update anyone's profile!
    # ❌ No verification that caller owns the wallet
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        query = f"""UPDATE users 
                    SET bio = {ph}, country = {ph}, ...
                    WHERE wallet_address = {ph}"""
        cursor.execute(query, (..., wallet_address))
```

### Attack Scenario:
```bash
# Attacker changes victim's bio to scam text
curl -X PUT https://your-backend.onrender.com/api/users/VICTIM_WALLET/profile \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Send me 10 SOL and I will double it!",
    "country": "XX",
    "favourite_ct_account": "@scammer",
    "favourite_trading_venue": "ScamExchange",
    "asset_choice_6m": "Your money"
  }'
```

### ✅ FIXED Code:

```python
from fastapi import Depends
from auth import get_authenticated_wallet, verify_wallet_match

@app.put("/api/users/{wallet_address}/profile")
async def update_my_profile(
    wallet_address: str, 
    profile_data: ProfileComplete,
    authenticated_wallet: str = Depends(get_authenticated_wallet)  # ✅ NOW REQUIRED
):
    """Update user's own profile - requires wallet signature"""
    # ✅ Verify caller owns this wallet
    await verify_wallet_match(wallet_address, authenticated_wallet)
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        query = f"""UPDATE users 
                    SET bio = {ph}, country = {ph}, ...
                    WHERE wallet_address = {ph}"""
        cursor.execute(query, (..., wallet_address))
```

---

## 🔴 Issue #2: Messages Have No Authorization (CRITICAL)

### Current Code (VULNERABLE):

```python
@app.post("/api/chat/message")
async def send_message(message_data: MessageCreate):
    # ❌ Anyone can send messages as anyone!
    # ❌ No check if sender is part of the match!
    message_id = str(uuid.uuid4())
    cursor.execute(query,
              (message_id, message_data.chat_room_id, 
               message_data.sender_wallet,  # ❌ Trust user input!
               message_data.message, created_at))
```

### Attack Scenario:
```bash
# Attacker sends fake messages as victim
curl -X POST https://your-backend.onrender.com/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "chat_room_id": "abc-123",
    "sender_wallet": "VICTIM_WALLET",
    "message": "Please send me crypto at scammer.wallet.sol"
  }'
```

### ✅ FIXED Code:

```python
@app.post("/api/chat/message")
async def send_message(
    message_data: MessageCreate,
    authenticated_wallet: str = Depends(get_authenticated_wallet)  # ✅ NOW REQUIRED
):
    """Send a message - requires wallet signature"""
    ph = db.placeholder()
    
    # ✅ Verify sender owns the wallet
    if message_data.sender_wallet != authenticated_wallet:
        raise HTTPException(403, "You can only send messages as yourself")
    
    # ✅ Verify sender is part of this match
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # Check if sender is in this chat room
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
            raise HTTPException(403, "You are not part of this chat")
        
        # Now save the message
        message_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        insert_query = f"""INSERT INTO messages 
                          (id, chat_room_id, sender_wallet, message, created_at) 
                          VALUES ({ph}, {ph}, {ph}, {ph}, {ph})"""
        cursor.execute(insert_query,
                      (message_id, message_data.chat_room_id, 
                       authenticated_wallet,  # ✅ Use verified wallet!
                       message_data.message, created_at))
        
        conn.commit()
```

---

## 🔴 Issue #3: Anyone Can Read Any Chat (CRITICAL)

### Current Code (VULNERABLE):

```python
@app.get("/api/chat/{chat_room_id}/messages")
async def get_messages(chat_room_id: str, limit: int = 50):
    # ❌ No check if caller is part of this chat!
    # ❌ Anyone with room ID can read all messages!
    cursor.execute(query, (chat_room_id,))
    results = cursor.fetchall()
```

### ✅ FIXED Code:

```python
@app.get("/api/chat/{chat_room_id}/messages")
async def get_messages(
    chat_room_id: str, 
    limit: int = 50,
    authenticated_wallet: str = Depends(get_authenticated_wallet)  # ✅ NOW REQUIRED
):
    """Get messages - requires wallet signature and membership"""
    ph = db.placeholder()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        
        # ✅ Verify caller is part of this match
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
            raise HTTPException(403, "You are not part of this chat")
        
        # Now get messages
        query = f"""SELECT sender_wallet, message, created_at 
                     FROM messages 
                     WHERE chat_room_id = {ph} 
                     ORDER BY created_at DESC 
                     LIMIT {limit}"""
        cursor.execute(query, (chat_room_id,))
        results = cursor.fetchall()
        
    # ... rest of code
```

---

## 🔴 Issue #4: Profile Updates Can Erase Data

### Problem:

```python
# Current: Updates ALL fields at once
UPDATE users 
SET bio = ?, country = ?, favourite_ct_account = ?, ...
WHERE wallet_address = ?
```

**Issue:** If frontend sends empty string for bio, it gets saved!

### ✅ FIXED Code:

```python
@app.put("/api/users/{wallet_address}/profile")
async def update_my_profile(
    wallet_address: str, 
    profile_data: ProfileComplete,
    authenticated_wallet: str = Depends(get_authenticated_wallet)
):
    """Update user's own profile"""
    await verify_wallet_match(wallet_address, authenticated_wallet)
    
    # ✅ Validate required fields aren't empty
    if not profile_data.bio or len(profile_data.bio.strip()) == 0:
        raise HTTPException(400, "Bio cannot be empty")
    
    if not profile_data.country:
        raise HTTPException(400, "Country cannot be empty")
    
    if not profile_data.favourite_ct_account:
        raise HTTPException(400, "Favourite CT account cannot be empty")
    
    # ✅ Add updated_at timestamp
    updated_at = datetime.now().isoformat()
    
    with db.get_connection() as conn:
        cursor = db.get_cursor(conn)
        query = f"""UPDATE users 
                    SET bio = {ph}, country = {ph}, 
                        favourite_ct_account = {ph}, 
                        worst_ct_account = {ph}, 
                        favourite_trading_venue = {ph}, 
                        asset_choice_6m = {ph}, 
                        twitter_account = {ph},
                        updated_at = {ph}
                    WHERE wallet_address = {ph}"""
        cursor.execute(query, (..., updated_at, wallet_address))
```

**Also need to add `updated_at` column to database:**

```python
# In init_db()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id TEXT PRIMARY KEY,
              wallet_address TEXT UNIQUE NOT NULL,
              ...existing fields...,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
```

---

## 🟡 Issue #5: Messages Missing Metadata (MEDIUM)

### Current Schema:
```sql
messages (id, chat_room_id, sender_wallet, message, created_at)
```

### ✅ IMPROVED Schema:

```sql
CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  chat_room_id TEXT NOT NULL,
  sender_wallet TEXT NOT NULL,
  message TEXT NOT NULL,
  message_type TEXT DEFAULT 'text',  -- 'text', 'image', 'system'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  read_at TIMESTAMP,                -- When recipient read it
  edited_at TIMESTAMP,              -- If message was edited
  deleted_at TIMESTAMP,             -- Soft delete
  FOREIGN KEY (chat_room_id) REFERENCES matches(chat_room_id)
)
```

### Benefits:
- ✅ Track read receipts
- ✅ Allow message editing
- ✅ Soft delete messages
- ✅ Support different message types

---

## 🟡 Issue #6: No Duplicate Match Prevention (MEDIUM)

### Problem:
```python
# Can create multiple matches between same two users!
INSERT INTO matches (id, user1_wallet, user2_wallet, chat_room_id)
VALUES (?, ?, ?, ?)
```

### ✅ FIX: Add Unique Constraint

```python
# In init_db()
c.execute('''CREATE TABLE IF NOT EXISTS matches
             (id TEXT PRIMARY KEY,
              user1_wallet TEXT NOT NULL,
              user2_wallet TEXT NOT NULL,
              chat_room_id TEXT NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              last_message_at TIMESTAMP,
              UNIQUE(user1_wallet, user2_wallet),
              CHECK(user1_wallet < user2_wallet))''')
```

**Also normalize user order:**
```python
# Before inserting match:
user1, user2 = sorted([wallet_a, wallet_b])  # Always alphabetical
```

---

## 📋 IMPLEMENTATION PRIORITY

### 🔴 CRITICAL (Do Immediately):
1. ✅ **Add wallet authentication** (auth.py)
2. ✅ **Protect profile updates** (verify wallet ownership)
3. ✅ **Protect chat messages** (verify sender & membership)
4. ✅ **Protect chat reading** (verify membership)
5. ✅ **Protect swipe actions** (verify wallet ownership)

### 🟡 IMPORTANT (Do Soon):
6. ✅ **Add input validation** (non-empty required fields)
7. ✅ **Add updated_at timestamps**
8. ✅ **Prevent duplicate matches**
9. ✅ **Add message character limits**

### 🟢 NICE TO HAVE (Future):
10. ✅ Add read receipts
11. ✅ Add message editing
12. ✅ Add soft delete
13. ✅ Add rate limiting

---

## 🔧 QUICK FIX GUIDE

### Step 1: Add Dependencies

```bash
# Add to requirements.txt
pynacl==1.5.0
base58==2.1.1
```

### Step 2: Create auth.py

Already created above! ✅

### Step 3: Update main.py

Add to imports:
```python
from auth import get_authenticated_wallet, verify_wallet_match
from fastapi import Depends
```

### Step 4: Protect All Endpoints

Add `authenticated_wallet: str = Depends(get_authenticated_wallet)` to:
- `/api/users/{wallet}/profile` (PUT)
- `/api/users/{wallet}/complete-profile` (POST)
- `/api/swipe` (POST)
- `/api/chat/message` (POST)
- `/api/chat/{room}/messages` (GET)
- `/api/matches/{wallet}` (GET)

### Step 5: Update Frontend

Frontend needs to sign messages with wallet:

```typescript
// Before API call
const message = `${wallet.publicKey.toBase58()}:${Date.now()}`;
const signature = await wallet.signMessage(new TextEncoder().encode(message));

// Add to API headers
headers: {
  'X-Wallet-Address': wallet.publicKey.toBase58(),
  'X-Wallet-Signature': base58.encode(signature),
  'X-Message': message
}
```

---

## ⚠️ CURRENT RISK LEVEL

**Without Fixes:**
- 🔴 Anyone can impersonate any user
- 🔴 Anyone can read all chats
- 🔴 Anyone can modify any profile
- 🔴 Data integrity: ZERO
- 🔴 User trust: ZERO

**With Fixes:**
- ✅ Only wallet owner can act as themselves
- ✅ Only chat participants can read messages
- ✅ Only owner can modify their profile
- ✅ Data integrity: HIGH
- ✅ User trust: HIGH

---

## 🚨 RECOMMENDATION

**DO NOT GO TO PRODUCTION WITHOUT FIXING CRITICAL ISSUES!**

Minimum viable security:
1. ✅ Implement wallet authentication
2. ✅ Protect all user-specific endpoints
3. ✅ Validate chat room membership
4. ✅ Add input validation

This will take **~4 hours of development** but is **ABSOLUTELY NECESSARY** before launch.

---

Want me to implement these fixes now? 🛠️

