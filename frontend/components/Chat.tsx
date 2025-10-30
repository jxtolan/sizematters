'use client'

import { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import { FiArrowLeft, FiSend } from 'react-icons/fi'
import toast from 'react-hot-toast'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Determine WebSocket URL based on API URL
const getWebSocketUrl = () => {
  if (typeof window === 'undefined') return 'ws://localhost:8000'
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  // Convert http/https to ws/wss
  if (apiUrl.startsWith('https://')) {
    return apiUrl.replace('https://', 'wss://')
  } else if (apiUrl.startsWith('http://')) {
    return apiUrl.replace('http://', 'ws://')
  }
  return 'ws://localhost:8000'
}

interface Message {
  sender_wallet: string
  message: string
  created_at: string
}

interface ChatProps {
  chatRoomId: string
  userWallet: string
  otherWallet: string
  onBack: () => void
}

export const Chat: React.FC<ChatProps> = ({
  chatRoomId,
  userWallet,
  otherWallet,
  onBack
}) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [ws, setWs] = useState<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadMessages()
    connectWebSocket()

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [chatRoomId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const connectWebSocket = () => {
    const wsUrl = `${getWebSocketUrl()}/ws/chat/${chatRoomId}`
    console.log('Connecting to WebSocket:', wsUrl)
    
    const websocket = new WebSocket(wsUrl)
    
    websocket.onopen = () => {
      console.log('✅ WebSocket connected')
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('📩 Received message:', data)
      setMessages(prev => [...prev, data])
    }
    
    websocket.onerror = (error) => {
      console.error('❌ WebSocket error:', error)
      toast.error('Chat connection error')
    }
    
    websocket.onclose = () => {
      console.log('WebSocket closed')
    }
    
    setWs(websocket)
  }

  const loadMessages = async () => {
    try {
      const response = await axios.get(
        `${API_BASE}/api/chat/${chatRoomId}/messages`
      )
      setMessages(response.data.messages)
    } catch (error) {
      console.error('Error loading messages:', error)
    }
  }

  const sendMessage = async () => {
    if (!newMessage.trim()) return

    const messageText = newMessage.trim()
    setNewMessage('') // Clear immediately for better UX

    try {
      console.log('Sending message:', messageText)
      await axios.post(`${API_BASE}/api/chat/message`, {
        chat_room_id: chatRoomId,
        sender_wallet: userWallet,
        message: messageText
      })
      console.log('✅ Message sent successfully')
    } catch (error) {
      console.error('❌ Error sending message:', error)
      toast.error('Failed to send message')
      setNewMessage(messageText) // Restore message on error
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const formatWallet = (address: string) => {
    return `${address.slice(0, 4)}...${address.slice(-4)}`
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="bg-gray-900 bg-opacity-50 rounded-3xl overflow-hidden flex flex-col h-[600px]">
      {/* Chat Header */}
      <div className="bg-gray-800 px-6 py-4 flex items-center gap-4 border-b border-gray-700">
        <button
          onClick={onBack}
          className="text-gray-400 hover:text-white transition"
        >
          <FiArrowLeft className="text-2xl" />
        </button>
        <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-green-500 rounded-full"></div>
        <div>
          <p className="text-white font-semibold">
            Trader {formatWallet(otherWallet)}
          </p>
          <p className="text-xs text-gray-400 font-mono">
            {otherWallet}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-12">
            <p className="text-lg mb-2">No messages yet</p>
            <p className="text-sm">Say hello! 👋</p>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isOwnMessage = msg.sender_wallet === userWallet
            return (
              <div
                key={index}
                className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                    isOwnMessage
                      ? 'bg-gradient-to-r from-purple-500 to-green-500 text-white'
                      : 'bg-gray-800 text-white'
                  }`}
                >
                  <p className="break-words">{msg.message}</p>
                  <p className={`text-xs mt-1 ${
                    isOwnMessage ? 'text-white opacity-70' : 'text-gray-500'
                  }`}>
                    {formatTime(msg.created_at)}
                  </p>
                </div>
              </div>
            )
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="bg-gray-800 px-6 py-4 border-t border-gray-700">
        <div className="flex gap-3">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            className="flex-1 bg-gray-700 text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={sendMessage}
            disabled={!newMessage.trim()}
            className="bg-gradient-to-r from-purple-500 to-green-500 px-6 py-3 rounded-xl hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiSend className="text-xl" />
          </button>
        </div>
      </div>
    </div>
  )
}

