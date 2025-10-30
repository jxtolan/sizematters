'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import { Chat } from './Chat'
import { FiMessageCircle, FiUser } from 'react-icons/fi'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Match {
  wallet_address: string
  chat_room_id: string
  created_at: string
}

interface MatchesProps {
  walletAddress: string
}

export const Matches: React.FC<MatchesProps> = ({ walletAddress }) => {
  const [matches, setMatches] = useState<Match[]>([])
  const [selectedChat, setSelectedChat] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMatches()
  }, [walletAddress])

  const loadMatches = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/api/matches/${walletAddress}`)
      setMatches(response.data.matches)
    } catch (error) {
      console.error('Error loading matches:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatWallet = (address: string) => {
    return `${address.slice(0, 4)}...${address.slice(-4)}`
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  if (selectedChat) {
    const match = matches.find(m => m.chat_room_id === selectedChat)
    return (
      <Chat
        chatRoomId={selectedChat}
        userWallet={walletAddress}
        otherWallet={match?.wallet_address || ''}
        onBack={() => setSelectedChat(null)}
      />
    )
  }

  return (
    <div className="glass rounded-3xl p-6 min-h-[600px] border-2 border-purple-500/30">
      <h2 className="text-3xl font-bold gradient-text mb-6 flex items-center gap-3">
        <span className="text-4xl">💎</span>
        Your Matches
      </h2>

      {loading ? (
        <div className="text-center text-white py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p>Loading your connections... 🚀</p>
        </div>
      ) : matches.length === 0 ? (
        <div className="text-center text-gray-300 py-12">
          <span className="text-8xl mb-4 block">🐋</span>
          <p className="text-2xl mb-2 gradient-text font-bold">No matches yet</p>
          <p className="text-sm text-gray-400">Start swiping to connect with elite traders! 💰</p>
        </div>
      ) : (
        <div className="space-y-4">
          {matches.map((match) => (
            <button
              key={match.chat_room_id}
              onClick={() => setSelectedChat(match.chat_room_id)}
              className="w-full glass hover:glow-cyan p-5 rounded-2xl transition-all flex items-center gap-4 group border-2 border-cyan-500/20 hover:border-cyan-500/50"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 via-pink-500 to-green-500 rounded-full flex items-center justify-center flex-shrink-0 glow-purple pulse-glow">
                <span className="text-3xl">🔥</span>
              </div>
              <div className="flex-1 text-left min-w-0">
                <p className="text-white font-bold text-lg mb-1 flex items-center gap-2">
                  <span>💎</span>
                  Trader {formatWallet(match.wallet_address)}
                </p>
                <p className="text-sm text-gray-400 font-mono truncate">
                  {match.wallet_address}
                </p>
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-xs text-cyan-400 mb-2 font-semibold">
                  {formatDate(match.created_at)}
                </p>
                <FiMessageCircle className="text-xl text-gray-400 group-hover:text-green-400 transition ml-auto" />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

