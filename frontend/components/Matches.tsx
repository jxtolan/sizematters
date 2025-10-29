'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'
import { Chat } from './Chat'
import { FiMessageCircle, FiUser } from 'react-icons/fi'

const API_BASE = 'http://localhost:8000'

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
    <div className="bg-gray-900 bg-opacity-50 rounded-3xl p-6 min-h-[600px]">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        <FiMessageCircle className="text-pink-500" />
        Your Matches
      </h2>

      {loading ? (
        <div className="text-center text-white py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p>Loading matches...</p>
        </div>
      ) : matches.length === 0 ? (
        <div className="text-center text-gray-400 py-12">
          <FiUser className="text-6xl mx-auto mb-4 opacity-50" />
          <p className="text-xl mb-2">No matches yet</p>
          <p className="text-sm">Start swiping to find traders!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {matches.map((match) => (
            <button
              key={match.chat_room_id}
              onClick={() => setSelectedChat(match.chat_room_id)}
              className="w-full bg-gray-800 hover:bg-gray-750 p-4 rounded-2xl transition flex items-center gap-4 group"
            >
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                <FiUser className="text-2xl text-white" />
              </div>
              <div className="flex-1 text-left">
                <p className="text-white font-semibold mb-1">
                  Trader {formatWallet(match.wallet_address)}
                </p>
                <p className="text-sm text-gray-400 font-mono">
                  {match.wallet_address}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500 mb-2">
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

