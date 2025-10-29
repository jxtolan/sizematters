# 🚀 Smart Money Tinder

**Connect with successful Solana traders using a Tinder-style interface!**

Smart Money Tinder is a revolutionary platform that allows you to discover and connect with profitable Solana traders. Swipe through profiles showing real-time PnL data and balance information from the Nansen API, match with traders you admire, and start meaningful conversations.

![Smart Money Tinder](https://img.shields.io/badge/Solana-Wallet-9945FF?style=for-the-badge&logo=solana)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?style=for-the-badge&logo=next.js)

## ✨ Features

- 🔐 **Solana Wallet Integration** - Connect with Phantom, Solflare, and other popular wallets
- 📊 **Real-time Trading Data** - View 90-day PnL summaries and current balance via Nansen API
- 💚 **Tinder-style Swiping** - Swipe right to like, left to pass
- 🎉 **Instant Matching** - When two traders like each other, it's an instant match!
- 💬 **Real-time Chat** - Group chat with matched traders using WebSockets
- 🎨 **Beautiful UI** - Modern, responsive design with smooth animations

## 🏗️ Architecture

```
smartmoneytinder/
├── backend/           # FastAPI backend server
│   ├── main.py       # API endpoints & WebSocket chat
│   └── requirements.txt
└── frontend/          # Next.js frontend application
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   └── globals.css
    └── components/
        ├── WalletProvider.tsx
        ├── SwipeCard.tsx
        ├── Matches.tsx
        └── Chat.tsx
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Solana wallet (Phantom recommended)
- Nansen API key (optional - demo works with mock data)

### Backend Setup

1. **Navigate to the backend directory:**
```bash
cd backend
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Populate the database with smart trader addresses:**
```bash
python populate_traders.py
```

This will add 66 real smart trader addresses from the CSV to your database!

5. **Run the server:**
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
# or
yarn install
```

3. **Run the development server:**
```bash
npm run dev
# or
yarn dev
```

The frontend will start on `http://localhost:3000`

## 🎮 How to Use

1. **Connect Your Wallet**
   - Click "Select Wallet" on the homepage
   - Choose your Solana wallet (Phantom, Solflare, etc.)
   - Approve the connection

2. **Start Swiping Through REAL Smart Traders! 🔥**
   - View profiles of 66+ verified smart traders from Nansen
   - See their real-time PnL and balance data via Nansen API
   - Swipe right (💚) with awesome celebration animations!
   - Swipe left (❌) with rejection effects
   - Or use the buttons for instant animated swipes

3. **Match & Chat**
   - When you and another trader both swipe right, it's a match! 🎉
   - Navigate to the "Matches" tab
   - Click on a match to start chatting in real-time

4. **Configure Nansen API (Optional)**
   - Click the settings icon (⚙️) in the header
   - Enter your Nansen API key for real-time data
   - Without an API key, the demo uses realistic mock data

## 🎬 Swipe Animations

### Swipe Right (LIKE) 💚
- Card flies off screen to the right
- "LIKE" badge spins and grows
- 8 celebration particles explode outward
- Smooth rotation animation

### Swipe Left (NOPE) ❌
- Card flies off screen to the left
- "NOPE" badge spins dramatically
- Red flash effect
- Card fades out smoothly

### Button Interactions
- Hover: Scale up and rotate
- Tap: Squeeze and rotate more
- Disabled during animation

## 🔧 API Endpoints

### User Management
- `POST /api/users` - Create or get user account
- `GET /api/profiles/{wallet_address}` - Get profiles to swipe

### Swiping & Matching
- `POST /api/swipe` - Record a swipe action
- `GET /api/matches/{wallet_address}` - Get user's matches

### Chat
- `GET /api/chat/{chat_room_id}/messages` - Get chat messages
- `POST /api/chat/message` - Send a message
- `WS /ws/chat/{chat_room_id}` - WebSocket for real-time chat

### Configuration
- `POST /api/config/nansen` - Set Nansen API key

## 🔌 Nansen API Integration

The platform integrates with Nansen's Profiler API to fetch:

### PnL Summary (90 days)
```python
POST https://api.nansen.ai/api/v1/profiler/address/pnl-summary
{
  "address": "wallet_address",
  "chain": "solana",
  "date": {
    "from": "2025-08-01T00:00:00Z",
    "to": "2025-10-28T23:59:59Z"
  }
}
```

### Current Balance
```python
POST https://api.nansen.ai/api/v1/profiler/address/current-balance
{
  "address": "wallet_address",
  "chain": "solana",
  "hide_spam_token": true,
  "pagination": {
    "page": 1,
    "per_page": 10
  }
}
```

## 🎨 Tech Stack

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Solana Wallet Adapter** - Wallet integration
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Database (easily upgradeable to PostgreSQL)
- **WebSockets** - Real-time chat
- **Requests** - Nansen API integration
- **Pydantic** - Data validation

## 🛠️ Customization

### Adding More Sample Wallets
Edit `SAMPLE_SOLANA_WALLETS` in `backend/main.py`:
```python
SAMPLE_SOLANA_WALLETS = [
    "your_wallet_address_1",
    "your_wallet_address_2",
    # Add more...
]
```

### Changing Network
Edit `frontend/components/WalletProvider.tsx`:
```typescript
const network = WalletAdapterNetwork.Mainnet  // or Devnet/Testnet
```

### Styling
Customize colors in `frontend/tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: '#9945FF',    // Purple
      secondary: '#14F195',  // Green
    },
  },
}
```

## 📱 Screenshots

### Landing Page
Beautiful gradient background with wallet connection

### Swipe Interface
Tinder-style cards showing trader stats with smooth animations

### Matches & Chat
Real-time messaging with matched traders

## 🚧 Future Enhancements

- [ ] User profiles with trading strategies
- [ ] Advanced filtering (PnL range, balance, win rate)
- [ ] Trading groups and communities
- [ ] Portfolio sharing
- [ ] Trading signals and alerts
- [ ] Mobile app (React Native)
- [ ] Push notifications for matches
- [ ] Video chat integration
- [ ] Leaderboards

## 🤝 Contributing

This is a demo project, but contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

MIT License - feel free to use this project for your own purposes!

## 👨‍💻 Developer Notes

### Database Schema
The SQLite database includes:
- **users** - Wallet addresses and user IDs
- **swipes** - Record of all swipe actions
- **matches** - Successful mutual swipes
- **messages** - Chat messages

### WebSocket Implementation
Real-time chat uses WebSocket connections managed by a `ConnectionManager` class that:
- Maintains active connections per chat room
- Broadcasts messages to all participants
- Handles disconnections gracefully

### Security Considerations
For production deployment:
- Use environment variables for API keys
- Implement rate limiting
- Add authentication middleware
- Use PostgreSQL instead of SQLite
- Enable HTTPS
- Implement proper CORS policies
- Add input sanitization
- Implement message encryption

## 🆘 Support

Need help? Reach out:
- Check the [Issues](https://github.com/yourrepo/issues) page
- Join our Discord community
- Email: support@smartmoneytinder.com

## 🎉 Acknowledgments

- **Nansen** - For the amazing analytics API
- **Solana** - For the fast, low-cost blockchain
- **Vercel** - For Next.js and deployment platform
- **FastAPI** - For the incredible Python framework

---

Built with ❤️ by your development team

**Ready to find your trading soulmate? Let's swipe! 🚀**

