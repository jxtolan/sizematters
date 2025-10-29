# 🎯 Quick Setup Guide for Smart Money Tinder

Follow these steps to get the demo running in minutes!

## Step 1: Backend Setup (Terminal 1)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

✅ Backend should now be running on `http://localhost:8000`

## Step 2: Frontend Setup (Terminal 2)

Open a **new terminal window** and run:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

✅ Frontend should now be running on `http://localhost:3000`

## Step 3: Connect Your Wallet

1. Open `http://localhost:3000` in your browser
2. Install Phantom wallet if you haven't: https://phantom.app/
3. Click "Select Wallet" and choose Phantom
4. Approve the connection

## Step 4: Start Swiping! 🎉

- Swipe right (💚) on traders you like
- Swipe left (❌) to pass
- Match with traders and start chatting!

## Optional: Add Nansen API Key

For real data instead of mock data:

1. Get a Nansen API key from https://nansen.ai
2. Click the settings icon (⚙️) in the app
3. Enter your API key
4. Click "Save"

## Troubleshooting

### Backend won't start?
- Make sure port 8000 is available
- Check Python version: `python --version` (need 3.8+)

### Frontend won't start?
- Make sure port 3000 is available
- Check Node version: `node --version` (need 18+)
- Try: `rm -rf node_modules && npm install`

### Wallet won't connect?
- Make sure you have Phantom installed
- Try refreshing the page
- Check browser console for errors

### Can't see profiles?
- Backend must be running
- Check backend logs for errors
- Try refreshing the page

## Demo Data

The app uses sample Solana wallet addresses with mock PnL and balance data. This allows you to test the full functionality without needing real Nansen API access.

## Need Help?

Check the main README.md for detailed documentation or create an issue!

---

**That's it! You're ready to find your trading soulmate! 🚀**

