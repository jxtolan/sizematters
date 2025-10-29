# 🌱 Seed Demo Traders Guide

This guide explains how to populate your database with real demo trader profiles.

## What Gets Seeded

15 real Solana wallet addresses with creative trader bios:
- Real addresses (including popular tokens like SOL, USDC)
- Fun, personality-driven bios
- Nansen API will fetch REAL PnL and balance data automatically

## Local Development

Run the seed script locally:

```bash
cd backend

# First, run migration if needed (adds bio column)
python3 migrate_add_bio.py

# Then seed the database
python3 seed_demo_traders.py
```

## Production (Render)

### Option 1: Run via Render Shell

1. Go to your Render dashboard: https://dashboard.render.com
2. Select your `sizematters-backend` service
3. Click "Shell" tab
4. Run these commands:

```bash
cd /opt/render/project/src/backend
python3 migrate_add_bio.py
python3 seed_demo_traders.py
```

### Option 2: Add to Render Build Command

Update your Render service's build command to include seeding:

```bash
pip install -r requirements.txt && cd backend && python3 migrate_add_bio.py && python3 seed_demo_traders.py
```

### Option 3: Manual Deploy Trigger

The seed script is idempotent (safe to run multiple times). It will:
- Skip existing users
- Add new users
- Update bios for existing addresses

Simply trigger a redeploy on Render and the scripts will be available.

## Verification

After seeding, check your app:
1. Connect your wallet
2. Click "Load Profiles"
3. You should see 15 demo traders with:
   - Real Nansen PnL data
   - Real current balances
   - Fun bios

## Demo Trader Addresses

These are REAL Solana addresses:
- `7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU` - The BONK degen
- `CckxW6C1CjsxYcXSiDbk7NYfPLhfqAm3kSB5LEZunnSE` - Quant trader
- `Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr` - Diamond hands
- And 12 more...

The Nansen API will fetch real trading data for these addresses! 🚀

## Notes

- The seed script won't duplicate entries
- Bios will be updated if you re-run the script
- Demo traders also serve as fallback when the database has ≤1 user
- Make sure `NANSEN_API_KEY` is set in Render environment variables for real data

