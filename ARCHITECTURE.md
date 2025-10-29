# 🏗️ Architecture Documentation

## System Overview

Smart Money Tinder is a full-stack application built with modern web technologies. It follows a client-server architecture with real-time communication capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Next.js Frontend (React + TypeScript)                │  │
│  │  - Solana Wallet Integration                          │  │
│  │  - Swipe UI with Framer Motion                        │  │
│  │  - Real-time Chat Interface                           │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────┴──────────────────────────────────────┐
│                      API Gateway                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend (Python)                             │  │
│  │  - REST API Endpoints                                 │  │
│  │  - WebSocket Connections                              │  │
│  │  - Business Logic                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────┬──────────────────────┬───────────────────────────┘
           │                      │
┌──────────┴────────┐   ┌────────┴─────────────────────────┐
│  Data Layer       │   │   External Services              │
│  ┌─────────────┐  │   │  ┌──────────────────────────┐   │
│  │   SQLite    │  │   │  │   Nansen API             │   │
│  │   Database  │  │   │  │   - PnL Summary          │   │
│  └─────────────┘  │   │  │   - Current Balance      │   │
└───────────────────┘   │  └──────────────────────────┘   │
                        └──────────────────────────────────┘
```

## Component Architecture

### Frontend Components

```
app/
├── layout.tsx                 # Root layout with WalletProvider
├── page.tsx                   # Main application page
└── globals.css               # Global styles

components/
├── WalletProvider.tsx        # Solana wallet configuration
├── SwipeCard.tsx            # Individual profile card with animations
├── Matches.tsx              # Matches list view
└── Chat.tsx                 # Real-time chat interface
```

### Backend Architecture

```python
main.py
├── FastAPI Application
├── CORS Middleware
├── Database Initialization
├── REST API Endpoints
│   ├── User Management
│   ├── Profile Discovery
│   ├── Swipe Actions
│   ├── Match Management
│   └── Chat Messages
└── WebSocket Manager
    └── Real-time Chat
```

## Data Flow

### 1. User Authentication Flow
```
User → Wallet Connect → Public Key → Create Account → Session Start
```

### 2. Profile Discovery Flow
```
User → Request Profiles → Backend → Filter Already Swiped → Fetch Nansen Data → Return Profiles
```

### 3. Swipe Flow
```
User → Swipe Action → Record in DB → Check for Match → Create Chat Room (if match) → Notify User
```

### 4. Chat Flow
```
User → Send Message → API → Store in DB → WebSocket Broadcast → Other Users Receive
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    wallet_address TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Swipes Table
```sql
CREATE TABLE swipes (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    target_wallet TEXT NOT NULL,
    direction TEXT NOT NULL,  -- 'left' or 'right'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

### Matches Table
```sql
CREATE TABLE matches (
    id TEXT PRIMARY KEY,
    user1_wallet TEXT NOT NULL,
    user2_wallet TEXT NOT NULL,
    chat_room_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Messages Table
```sql
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    chat_room_id TEXT NOT NULL,
    sender_wallet TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## API Endpoints

### User Management
- **POST** `/api/users`
  - Create or retrieve user account
  - Body: `{ wallet_address: string }`
  - Returns: User ID and account info

### Profile Discovery
- **GET** `/api/profiles/{wallet_address}`
  - Get profiles to swipe through
  - Excludes already swiped wallets
  - Returns: Array of profiles with Nansen data

### Swipe Actions
- **POST** `/api/swipe`
  - Record a swipe action
  - Body: `{ user_wallet: string, target_wallet: string, direction: string }`
  - Returns: Match status and chat room ID if matched

### Match Management
- **GET** `/api/matches/{wallet_address}`
  - Get all matches for a user
  - Returns: Array of matches with chat room IDs

### Chat
- **GET** `/api/chat/{chat_room_id}/messages`
  - Get messages for a chat room
  - Query: `limit` (optional, default 50)
  - Returns: Array of messages

- **POST** `/api/chat/message`
  - Send a message
  - Body: `{ chat_room_id: string, sender_wallet: string, message: string }`
  - Returns: Message ID

- **WS** `/ws/chat/{chat_room_id}`
  - WebSocket connection for real-time chat
  - Broadcasts messages to all connected clients

### Configuration
- **POST** `/api/config/nansen`
  - Set Nansen API key
  - Body: `{ api_key: string }`
  - Returns: Success status

## Real-time Communication

### WebSocket Manager
```python
class ConnectionManager:
    active_connections: Dict[str, List[WebSocket]]
    
    async def connect(websocket, chat_room_id)
    def disconnect(websocket, chat_room_id)
    async def broadcast(message, chat_room_id)
```

### Connection Flow
1. Client connects to `/ws/chat/{chat_room_id}`
2. Server adds connection to room's connection pool
3. When message sent via API, server broadcasts to all connections in room
4. Clients receive real-time updates

## External API Integration

### Nansen API

#### PnL Summary Endpoint
```
POST https://api.nansen.ai/api/v1/profiler/address/pnl-summary
```

**Request:**
```json
{
  "address": "wallet_address",
  "chain": "solana",
  "date": {
    "from": "2025-08-01T00:00:00Z",
    "to": "2025-10-28T23:59:59Z"
  }
}
```

**Response:** PnL data including total P&L, percentage, win rate, and trade count

#### Current Balance Endpoint
```
POST https://api.nansen.ai/api/v1/profiler/address/current-balance
```

**Request:**
```json
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

**Response:** Balance data including total USD value, SOL balance, and token holdings

### Mock Data Fallback
When Nansen API key is not configured, the system generates realistic mock data based on wallet address hashing for consistent results.

## Security Considerations

### Current Implementation (Demo)
- Open CORS for localhost
- No authentication beyond wallet signature
- SQLite for easy setup
- Mock data fallback

### Production Recommendations
1. **Authentication**
   - Implement wallet signature verification
   - Session management with JWT
   - Rate limiting per wallet

2. **Data Security**
   - PostgreSQL with proper indexes
   - Encrypted sensitive data
   - Input sanitization
   - SQL injection prevention

3. **API Security**
   - Environment variables for secrets
   - CORS restricted to production domain
   - HTTPS only
   - API rate limiting

4. **WebSocket Security**
   - Authentication on connection
   - Message validation
   - Connection limits per user
   - Heartbeat/ping-pong

## Performance Optimization

### Frontend
- React component memoization
- Code splitting with Next.js
- Image optimization
- CSS-in-JS for critical styles
- Lazy loading for chat components

### Backend
- Connection pooling for database
- Caching for Nansen API responses
- Async/await for non-blocking operations
- WebSocket connection management
- Batch database operations

### Database
- Indexes on frequently queried fields
- Connection pooling
- Query optimization
- Pagination for large result sets

## Scalability Considerations

### Current Limitations (Demo)
- Single server instance
- SQLite database
- In-memory WebSocket manager
- No caching layer

### Scaling Strategy
1. **Horizontal Scaling**
   - Load balancer
   - Multiple API servers
   - Redis for WebSocket state
   - PostgreSQL with read replicas

2. **Caching**
   - Redis for Nansen API responses
   - CDN for static assets
   - Database query caching

3. **Message Queue**
   - RabbitMQ/Redis for async tasks
   - Celery for background jobs
   - Nansen API request queuing

4. **Monitoring**
   - Application performance monitoring
   - Error tracking (Sentry)
   - Analytics (Mixpanel)
   - Server monitoring (DataDog)

## Technology Stack Justification

### Frontend: Next.js + TypeScript
- **Pros:** Server-side rendering, excellent DX, TypeScript safety
- **Use Case:** Fast loading, SEO-ready, type-safe React development

### Backend: FastAPI
- **Pros:** Fast, async support, automatic API docs, Python ecosystem
- **Use Case:** Quick development, WebSocket support, Nansen SDK compatible

### Database: SQLite (Demo) → PostgreSQL (Production)
- **SQLite Pros:** Zero configuration, file-based, perfect for demo
- **PostgreSQL Pros:** Production-ready, ACID compliance, scalable

### State Management: React Hooks
- **Pros:** Built-in, no external dependencies, simple for this use case
- **Use Case:** Component-level state, enough for current needs

### Styling: Tailwind CSS
- **Pros:** Utility-first, fast development, small bundle size
- **Use Case:** Rapid UI development, consistent design system

### Animations: Framer Motion
- **Pros:** React-first, smooth animations, gesture support
- **Use Case:** Swipe gestures, smooth card animations

## Deployment Architecture

### Recommended Setup

```
┌─────────────────────────────────────────────┐
│              Vercel (Frontend)               │
│  - Next.js Static/SSR                        │
│  - Edge Functions                            │
│  - CDN                                       │
└──────────────┬──────────────────────────────┘
               │
┌──────────────┴──────────────────────────────┐
│          Railway/Render (Backend)            │
│  - FastAPI Server                            │
│  - WebSocket Support                         │
│  - PostgreSQL Database                       │
└──────────────────────────────────────────────┘
```

### Environment Variables

**Backend:**
```
NANSEN_API_KEY=xxx
DATABASE_URL=postgresql://...
CORS_ORIGINS=https://yourdomain.com
```

**Frontend:**
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_SOLANA_NETWORK=mainnet-beta
```

## Testing Strategy

### Frontend Testing
- Unit tests: Jest + React Testing Library
- E2E tests: Playwright
- Component tests: Storybook

### Backend Testing
- Unit tests: pytest
- Integration tests: TestClient
- API tests: httpx
- WebSocket tests: pytest-asyncio

### Manual Testing Checklist
- [ ] Wallet connection
- [ ] Profile loading
- [ ] Swipe left/right
- [ ] Match creation
- [ ] Chat send/receive
- [ ] Settings save
- [ ] Mobile responsiveness

## Future Enhancements

### Phase 1: Core Features
- User profiles with bio
- Profile photos (IPFS/Arweave)
- Advanced filtering
- Push notifications

### Phase 2: Social Features
- Trading groups
- Portfolio sharing
- Trading signals
- Leaderboards

### Phase 3: Monetization
- Premium subscriptions
- Featured profiles
- Analytics dashboard
- Trading copy feature

### Phase 4: Mobile
- React Native app
- Push notifications
- Biometric auth
- Deep linking

---

This architecture is designed to be:
- **Scalable**: Easy to upgrade from demo to production
- **Maintainable**: Clean separation of concerns
- **Extensible**: Easy to add new features
- **Developer-friendly**: Clear structure and documentation

