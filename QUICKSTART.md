# 🚀 Quick Start Guide - Get Running in 5 Minutes!

## Step 1: Setup Backend (2 minutes)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Populate database with 66 real smart traders! 🔥
python populate_traders.py

# Start backend
python main.py
```

✅ Backend running on `http://localhost:8000`

---

## Step 2: Setup Frontend (2 minutes)

Open a **NEW terminal window**:

```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

✅ Frontend running on `http://localhost:3000`

---

## Step 3: Start Swiping! (1 minute)

1. Open `http://localhost:3000` in your browser
2. Install [Phantom Wallet](https://phantom.app/) if you don't have it
3. Click "Select Wallet" and connect
4. **START SWIPING THROUGH 66 REAL SMART TRADERS!** 🎉

---

## What You're Swiping Through:

✨ **66 Verified Smart Traders** from Nansen including:
- 180D Smart Traders with $100K+ PnL
- 90D Smart Traders with 50%+ win rates  
- 30D Smart Traders with hot streaks
- Named traders like Hugo Fartingale, Theo, etc.

📊 **Real-Time Data** (with Nansen API key):
- 90-day PnL summaries
- Current portfolio balance
- Win rates and trade counts
- Token holdings

---

## Pro Tips:

### Get Your Nansen API Key (Optional but Recommended!)
1. Sign up at [Nansen.ai](https://nansen.ai)
2. Get your API key
3. Click ⚙️ in the app and paste it
4. Now you're seeing REAL live data! 📊

### Animation Controls:
- **Drag** cards left/right to swipe
- **Click buttons** for instant animated swipes
- Watch the celebration particles on LIKE! 🎉
- Feel the rejection on NOPE! ❌

### Match Someone:
Since you're the only real user, matches happen when you swipe right on addresses that also "like you back" (simulated for demo). Try swiping right on multiple traders!

---

## Troubleshooting:

**Port already in use?**
```bash
# Kill the process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change the port in backend/main.py
```

**Frontend won't start?**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Database issues?**
```bash
cd backend
rm smartmoney.db
python populate_traders.py
```

---

## You're All Set! 🎊

Now go find your trading soulmate! Swipe through profiles of real smart traders, match with the best, and start chatting!

**Need help?** Check out the full README.md for detailed documentation.

