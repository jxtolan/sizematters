# 🚀 Run SizeMatters Locally

## Quick Start (2 terminals)

### Terminal 1: Backend
```bash
cd /Users/nansen/Desktop/General/aiapp/smartmoneytinder_backup/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: **http://localhost:8000**

### Terminal 2: Frontend
```bash
cd /Users/nansen/Desktop/General/aiapp/smartmoneytinder_backup/frontend
npm run dev
```

Frontend will run at: **http://localhost:3000**

## Environment Variables

### Backend (.env file)
Create `backend/.env`:
```bash
DATABASE_URL=sqlite:///./smartmoney.db
NANSEN_API_KEY=your_key_here
REQUIRE_AUTH=false
REQUIRE_SIGNATURE=false
```

### Frontend (.env.local file)
Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Access the App
Open your browser to **http://localhost:3000**

Connect your Solana wallet and you're ready! 🎉

