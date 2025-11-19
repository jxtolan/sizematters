# 🚀 Smart Money Tinder

**Connect with successful Solana traders using a Tinder-style interface!**

Smart Money Tinder is a revolutionary platform that allows you to discover and connect with profitable Solana traders. Swipe through profiles showing real-time PnL data and balance information from the Nansen API, match with traders you admire, and start meaningful conversations.

![Smart Money Tinder](https://img.shields.io/badge/Solana-Wallet-9945FF?style=for-the-badge&logo=solana)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?style=for-the-badge&logo=next.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192?style=for-the-badge&logo=postgresql)

## ✨ Features

- 🔐 **Solana Wallet Integration** - Connect with Phantom, Solflare, and other popular wallets
- 🔒 **Cryptographic Signature Verification** - Production-grade security with Ed25519 signatures
- 📊 **Real-time Trading Data** - View 90-day PnL summaries and current balance via Nansen API
- 💚 **Tinder-style Swiping** - Swipe right to like, left to pass
- 🎉 **Instant Matching** - When two traders like each other, it's an instant match!
- 💬 **Real-time Chat** - WebSocket-powered instant messaging
- 🎨 **Beautiful UI** - Modern, responsive design with smooth animations
- 💾 **Persistent Storage** - PostgreSQL database that never loses your data
- 🚀 **Auto-seeding** - 9 demo traders automatically added on first run

## 🏗️ Project Structure

```
smartmoneytinder/
├── backend/              # FastAPI backend server
│   ├── main.py          # API endpoints & WebSocket chat
│   ├── database.py      # Database abstraction (SQLite/PostgreSQL)
│   ├── requirements.txt # Python dependencies
│   └── test_db_connection.py  # Database test script
├── frontend/            # Next.js frontend application
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   └── components/
│       ├── WalletProvider.tsx
│       ├── SwipeCard.tsx
│       ├── Matches.tsx
│       ├── MyProfile.tsx
│       └── Chat.tsx
├── QUICKSTART_POSTGRESQL.md  # Deployment guide
└── README.md            # This file
```

## 🚀 Quick Start - Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn
- Solana wallet (Phantom recommended)
- Nansen API key (optional - works with mock data)

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test database connection (optional)
python3 test_db_connection.py

# 5. Run the server
python3 main.py
```

Backend runs on `http://localhost:8000`

**Note:** Database automatically:
- Creates tables on first run
- Seeds 9 demo traders if empty
- Uses SQLite locally (no setup needed!)

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev
```

Frontend runs on `http://localhost:3000`

## 🎮 How to Use

### 1. Connect Your Wallet
- Click "Select Wallet" on the homepage
- Choose your Solana wallet (Phantom, Solflare, etc.)
- Approve the connection

### 2. Complete Your Profile
- Add your bio, country, and trading preferences
- Get assigned a unique trader number (e.g., #001, #042)

### 3. Start Swiping! 🔥
- View profiles of verified smart traders
- See real-time PnL and balance data (via Nansen API)
- Swipe right (💚) to like, left (❌) to pass
- Watch the celebration animations!

### 4. Match & Chat
- When you both swipe right → Instant match! 🎉
- Navigate to "Matches" tab
- Click on a match to start chatting in real-time

## 🔒 Security & Authentication

Smart Money Tinder implements **cryptographic signature verification** to ensure only wallet owners can perform actions on their accounts.

### Security Modes

Set via environment variables on your backend:

| Mode | `REQUIRE_AUTH` | `REQUIRE_SIGNATURE` | Use Case |
|------|---------------|---------------------|----------|
| **Development** | `false` | `false` | Local testing only |
| **Basic Auth** | `true` | `false` | Staging/testing |
| **🔒 Production** | `true` | `true` | **Live users (RECOMMENDED)** |

### How It Works

1. User clicks "Update Profile" or sends a message
2. Frontend prompts wallet to sign an authentication message
3. Signed message + signature sent to backend
4. Backend verifies signature using Ed25519 cryptography
5. Request succeeds only if signature is valid

**Result:** Impossible to spoof without private key! 🔐

For detailed implementation guide, see: **`SIGNATURE_VERIFICATION.md`**

### Quick Setup for Production

```bash
# In Render.com Environment Variables:
REQUIRE_AUTH=true
REQUIRE_SIGNATURE=true
```

That's it! Your app is now cryptographically secured. ✅

---

## 🚀 Deploy to Production (Render)

**See `QUICKSTART_POSTGRESQL.md` for full deployment guide.**

Quick summary:

1. **Push code to GitHub**
2. **Create PostgreSQL database on Render** (free tier available)
3. **Deploy backend web service** with `DATABASE_URL`, `REQUIRE_AUTH=true`, `REQUIRE_SIGNATURE=true`
4. **Deploy frontend** (Vercel or Render Static Site)
5. **Done!** Your data persists forever and is fully secured 🎉

**Deployment time:** ~15 minutes

## 🔧 Key API Endpoints

### User Management
- `POST /api/users` - Check if user exists
- `POST /api/users/{wallet}/complete-profile` - Complete user profile
- `GET /api/users/{wallet}/profile` - Get user profile
- `PUT /api/users/{wallet}/profile` - Update user profile

### Swiping & Matching
- `GET /api/profiles/{wallet}` - Get profiles to swipe through
- `POST /api/swipe` - Record a swipe action (creates match if mutual)
- `GET /api/matches/{wallet}` - Get user's matches

### Chat
- `GET /api/chat/{room_id}/messages` - Get chat messages
- `POST /api/chat/message` - Send a message
- `WS /ws/chat/{room_id}` - WebSocket for real-time chat

### Configuration
- `POST /api/config/nansen` - Set Nansen API key
- `GET /api/config/trading-venues` - Get list of trading venues

## 🎨 Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Solana Wallet Adapter** - Multi-wallet support
- **Axios** - HTTP client
- **React Hot Toast** - Beautiful notifications

### Backend
- **FastAPI** - Modern async Python framework
- **PostgreSQL** - Production database (persistent storage)
- **SQLite** - Local development database
- **psycopg2** - PostgreSQL adapter
- **WebSockets** - Real-time chat
- **Pydantic** - Data validation

### Infrastructure
- **Vercel** - Frontend hosting
- **Render** - Backend & database hosting
- **GitHub** - Version control & CI/CD

## 🗄️ Database

### Automatic Switching
- **Local:** Uses SQLite (`smartmoney.db`) - no setup required
- **Production:** Uses PostgreSQL when `DATABASE_URL` is set

### Schema
```sql
users (
  id, wallet_address, trader_number, bio, country,
  favourite_ct_account, worst_ct_account,
  favourite_trading_venue, asset_choice_6m,
  twitter_account, created_at
)

swipes (id, user_id, target_wallet, direction, created_at)
matches (id, user1_wallet, user2_wallet, chat_room_id, created_at)
messages (id, chat_room_id, sender_wallet, message, created_at)
```

### Key Features
- ✅ Auto-migration on startup
- ✅ Auto-seeding of demo traders
- ✅ Persistent storage (PostgreSQL)
- ✅ 30-minute API response cache
- ✅ Optimized profile loading

## 🔌 Nansen API Integration

Fetches real trader data via Nansen's Profiler API:

### PnL Summary (90 days with all-time fallback)
- Total realized PnL (USD)
- PnL percentage
- Win rate
- Total trades
- Traded token count

### Current Balance
- Total balance (USD)
- SOL balance
- Token count
- Top holdings

**Mock data available** if no API key is provided.

## 🎬 Swipe Animations

### Swipe Right (LIKE) 💚
- Card flies off to the right with rotation
- "LIKE" badge spins and grows
- 8 celebration particles explode outward
- Smooth fade-out

### Swipe Left (NOPE) ❌
- Card flies off to the left
- "NOPE" badge spins dramatically
- Red flash effect
- Smooth fade-out

### Button Interactions
- Hover effects with scale & rotation
- Tap effects with squeeze animation
- Disabled during animation to prevent spam

## 🛠️ Environment Variables

### Backend (Required for Production)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db  # PostgreSQL connection
NANSEN_API_KEY=your_nansen_key_here              # Optional for real data
PYTHON_VERSION=3.12.0                            # Force Python version
```

### Frontend
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_SOLANA_NETWORK=mainnet-beta
```

## 🧪 Testing

### Test Database Connection
```bash
cd backend
python3 test_db_connection.py
```

### Test API
```bash
# Start backend
python3 main.py

# Visit in browser
open http://localhost:8000
# Should see: {"message": "Smart Money Tinder API", "status": "running"}
```

## 🚧 Troubleshooting

### "No module named 'psycopg2'"
```bash
pip install -r requirements.txt
```

### "Could not connect to database"
Check `DATABASE_URL` environment variable format:
```
postgresql://user:password@host:5432/database
```

### Profile loading slow
- Cache is active (30-min TTL)
- Loads 8 profiles (optimized for speed)
- Mock data is instant (no API calls)

### Demo traders not showing
- Database might have existing users
- Check logs for auto-seed message
- Manual seed not needed (auto-seeding built-in)

## 📊 Performance Optimizations

- ✅ **30-minute API response cache** (reduced from 5 minutes)
- ✅ **Loads 8 profiles** instead of 10 (faster initial load)
- ✅ **Checks 12 wallets** instead of 20 (less API calls)
- ✅ **Skips profiles with no valid data** (real users only)
- ✅ **WebSocket connection pooling** for chat
- ✅ **PostgreSQL connection reuse**

## 🔐 Security Notes

For production deployment:
- ✅ PostgreSQL (not SQLite)
- ✅ Environment variables for secrets
- ⚠️ Add rate limiting (TODO)
- ⚠️ Add wallet signature verification (TODO)
- ⚠️ Enable CORS only for your domain (currently allows all)
- ⚠️ Add input sanitization
- ⚠️ Implement proper auth middleware

## 🚀 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] PostgreSQL database created on Render
- [ ] Backend deployed with `DATABASE_URL` set
- [ ] Frontend deployed with `NEXT_PUBLIC_API_URL` set
- [ ] Test wallet connection
- [ ] Test profile creation
- [ ] Test swiping
- [ ] Test matching
- [ ] Test chat
- [ ] Verify data persists after restart ✨

## 💰 Hosting Costs

### Free Tier (Perfect for MVP)
- Render PostgreSQL: 1GB storage (free)
- Render Web Service: 750 hours/month (free)
- Vercel Frontend: Unlimited (free)
- **Total: $0/month**

### Production Tier
- Render PostgreSQL: $7/month (10GB + backups)
- Render Web Service: $7/month (always-on)
- Vercel Pro: $20/month (optional)
- **Total: $14-34/month**

## 📄 License

MIT License - feel free to use this project for your own purposes!

## 🎉 Acknowledgments

- **Nansen** - For the amazing analytics API
- **Solana** - For the fast, low-cost blockchain
- **Render** - For easy deployment and PostgreSQL hosting
- **Vercel** - For Next.js and frontend hosting
- **FastAPI** - For the incredible Python framework

---

**Built with ❤️ for the Solana trading community**

**Ready to find your trading soulmate? Let's swipe! 🚀**

For deployment help, see `QUICKSTART_POSTGRESQL.md`
