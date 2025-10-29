# How to Populate Smart Traders Database

## Quick Start

1. **Make sure the CSV file is in the right place:**
   ```bash
   # The script expects smart_traders.csv in the parent directory
   # Your structure should be:
   # smartmoneytinder_backup/
   #   ├── smart_traders.csv  <-- CSV file here
   #   └── backend/
   #       └── populate_traders.py
   ```

2. **Run the population script:**
   ```bash
   cd backend
   python populate_traders.py
   ```

3. **Verify:**
   ```bash
   # Check how many traders were added
   sqlite3 smartmoney.db "SELECT COUNT(*) FROM users;"
   ```

## What This Does

The script reads the `smart_traders.csv` file and:
- Extracts all wallet addresses from the 'address' column
- Adds them to the SQLite database as user profiles
- Skips duplicates automatically
- Creates unique user IDs for each trader

## Important Notes

✅ **Real Nansen Data**: The app will fetch REAL-TIME data from the Nansen API for these addresses when users swipe through them

✅ **CSV Data Not Used**: The PnL data in the CSV is only for reference - the app fetches fresh data from Nansen

✅ **66 Smart Traders**: Your CSV contains 66 verified smart trader addresses (not 1000, but these are high-quality!)

## Addresses Included

These are real smart traders identified by Nansen with labels like:
- 🤓 180D Smart Trader
- 🤓 90D Smart Trader  
- 🤓 30D Smart Trader
- 👤 Named traders (Hugo Fartingale, Theo, etc.)

Examples:
- ERjMXMF6AVnMckiQb6zvTEcaCVc7iBpNqmtbNVjeKCpc (180D Smart Trader)
- 6jMQdtwEAfoBvKdE4HYGTdHCRSxYfCrgPmjQ6rnGr5mn (Sigil Fund)
- Au1GUWfcadx7jMzhsg6gHGxfzdGVJScWNp1U2AoYG98oRXfn (Hugo Fartingale)

## Testing

After populating:
1. Start the backend: `python main.py`
2. Start the frontend: `cd ../frontend && npm run dev`
3. Connect your wallet
4. Start swiping through real smart trader profiles!

## API Key Setup

Remember to add your Nansen API key in the settings (⚙️ icon) to get real data, or leave it empty to use mock data for testing.

