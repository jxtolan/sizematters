# 🚀 Render + PostgreSQL Deployment Guide

## What We Fixed

Your database was resetting because **SQLite uses local files that get wiped on every deployment**. We've now migrated to PostgreSQL, which provides **persistent storage** that survives restarts and redeployments.

✅ **No more data loss!**  
✅ **All chats and messages preserved**  
✅ **User profiles stay intact**

---

## Prerequisites

1. GitHub account (to deploy from repo)
2. Render.com account (free tier available)
3. Your code pushed to GitHub

---

## Step 1: Push Code to GitHub

```bash
cd /Users/nansen/Desktop/General/aiapp/smartmoneytinder_backup

# Initialize git if not already done
git init
git add .
git commit -m "Migrate to PostgreSQL for persistent storage"

# Push to your GitHub repo
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

---

## Step 2: Create PostgreSQL Database on Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"PostgreSQL"**
3. Configure your database:
   - **Name**: `smartmoneytinder-db` (or any name you prefer)
   - **Database**: `smartmoney` (default is fine)
   - **User**: Auto-generated (default is fine)
   - **Region**: Choose closest to your users
   - **Plan**: Free tier (or Starter $7/month for production)
4. Click **"Create Database"**
5. Wait 1-2 minutes for database to be provisioned
6. **IMPORTANT**: Copy the **Internal Database URL** (starts with `postgresql://`)
   - You'll find this in the database's **"Info"** section
   - It looks like: `postgresql://user:password@host/database`

---

## Step 3: Deploy Backend Web Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the backend service:

### Basic Settings:
- **Name**: `smartmoneytinder-backend` (or any name)
- **Region**: Same as database
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Environment Variables:
Click **"Advanced"** → **"Add Environment Variable"** and add these:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Paste the **Internal Database URL** from Step 2 |
| `NANSEN_API_KEY` | Your Nansen API key (if you have one) |
| `PYTHON_VERSION` | `3.12.0` |

4. Click **"Create Web Service"**
5. Wait 3-5 minutes for deployment to complete
6. Once deployed, copy your backend URL (e.g., `https://smartmoneytinder-backend.onrender.com`)

---

## Step 4: Update Frontend Environment Variables

### On Render (if deploying frontend there):

1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `smartmoneytinder-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `.next`

4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = Your backend URL from Step 3

### On Vercel (if using Vercel for frontend):

1. Go to your project settings on Vercel
2. Navigate to **"Environment Variables"**
3. Add:
   - `NEXT_PUBLIC_API_URL` = Your backend URL from Step 3
4. Redeploy

---

## Step 5: Initialize Database (First Time Only)

The database will automatically create tables on first startup! The backend code includes:
- Auto table creation
- Auto migration for existing columns
- Auto-seeding of 9 demo traders if database is empty

**No manual setup required!** 🎉

To verify it's working:
1. Visit your backend URL: `https://your-backend.onrender.com`
2. You should see: `{"message": "Smart Money Tinder API", "status": "running"}`

---

## Step 6: Test Your App

1. Open your frontend URL
2. Connect your wallet
3. Complete your profile
4. Start swiping!

**Your data will now persist across restarts!** 🎊

---

## How It Works Now

### Local Development (SQLite):
```bash
cd backend
python main.py
```
- Uses `smartmoney.db` (SQLite file)
- Perfect for testing

### Production (PostgreSQL on Render):
- Automatically detects `DATABASE_URL` environment variable
- Switches to PostgreSQL
- Data persists forever!

The code automatically switches between SQLite (local) and PostgreSQL (production) based on the `DATABASE_URL` environment variable.

---

## Troubleshooting

### Issue: "Table already exists" error
**Solution**: This is fine! It means tables were already created. The app handles this gracefully.

### Issue: Database connection timeout
**Solution**: 
1. Make sure you copied the **Internal Database URL** (not External)
2. Check that both backend and database are in the same region
3. Wait a minute and try again (Render databases take time to wake up on free tier)

### Issue: Demo traders not appearing
**Solution**: 
1. Check backend logs in Render dashboard
2. Look for "Auto-seed complete!" message
3. If not there, database might have existing users already

### Issue: "No module named 'database'"
**Solution**: Make sure `database.py` is in the `backend/` folder and pushed to GitHub

---

## Monitoring Your Database

### View Database Data:
1. Go to your PostgreSQL database in Render
2. Click **"Connect"** → **"External Connection"**
3. Use any PostgreSQL client (TablePlus, pgAdmin, DBeaver) to connect

### Check Database Size:
- Free tier: 1 GB storage
- Starter ($7/mo): 10 GB storage
- Current usage shown in Render dashboard

---

## Costs

### Free Tier (Good for Testing):
- ✅ PostgreSQL database (1GB storage)
- ✅ Web service (750 hours/month)
- ⚠️ Services sleep after 15 min of inactivity
- ⚠️ 90 second startup time when waking up

### Starter Tier ($7/month total):
- ✅ PostgreSQL: $7/month
- ✅ No sleep, always on
- ✅ 10 GB storage
- ✅ Automatic backups
- ✅ Better for production

---

## Migration Complete! ✅

Your app now uses PostgreSQL and will **never lose data again** due to restarts or deployments!

### What Changed:
- ✅ Added `psycopg2-binary` for PostgreSQL support
- ✅ Created `database.py` abstraction layer
- ✅ Updated all database queries in `main.py`
- ✅ Automatic detection of SQLite vs PostgreSQL
- ✅ Works locally with SQLite, production with PostgreSQL

### Next Steps:
1. Test locally: `cd backend && python main.py`
2. Deploy to Render following steps above
3. Enjoy persistent data! 🎉

---

## Questions?

If you encounter any issues:
1. Check Render logs: Dashboard → Your Service → Logs
2. Check database connection: Make sure `DATABASE_URL` is set correctly
3. Verify tables exist: Connect to database with pgAdmin/TablePlus

Need help? Just ask! 🚀

