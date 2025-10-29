#!/bin/bash

echo "🚀 Starting Smart Money Tinder..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "${BLUE}Creating Python virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "${BLUE}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "${GREEN}✅ Dependencies ready!${NC}"
echo ""
echo "Starting backend on http://localhost:8000..."
echo "Starting frontend on http://localhost:3000..."
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

