'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { useEffect, useState } from 'react'
import { SwipeCard } from '@/components/SwipeCard'
import { Matches } from '@/components/Matches'
import axios from 'axios'
import toast, { Toaster } from 'react-hot-toast'
import { FiHeart, FiMessageCircle, FiSettings } from 'react-icons/fi'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Profile {
  wallet_address: string
  pnl_summary: any
  balance: any
  bio?: string
}

export default function Home() {
  const { publicKey, connected } = useWallet()
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [currentProfileIndex, setCurrentProfileIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const [view, setView] = useState<'swipe' | 'matches'>('swipe')
  const [showSettings, setShowSettings] = useState(false)
  const [nansenApiKey, setNansenApiKey] = useState('')
  const [showBioModal, setShowBioModal] = useState(false)
  const [bio, setBio] = useState('')

  useEffect(() => {
    if (connected && publicKey) {
      createUserAccount()
      loadProfiles()
    }
  }, [connected, publicKey])

  const createUserAccount = async () => {
    if (!publicKey) return
    try {
      const response = await axios.post(`${API_BASE}/api/users`, {
        wallet_address: publicKey.toString()
      })
      // If new user, show bio modal
      if (!response.data.exists) {
        setShowBioModal(true)
      }
    } catch (error) {
      console.error('Error creating user account:', error)
    }
  }

  const saveBio = async () => {
    if (!publicKey || !bio.trim()) {
      toast.error('Please enter a bio')
      return
    }
    try {
      await axios.put(`${API_BASE}/api/users/${publicKey.toString()}/bio`, {
        bio: bio.trim()
      })
      toast.success('Bio saved!')
      setShowBioModal(false)
    } catch (error) {
      toast.error('Failed to save bio')
      console.error('Error saving bio:', error)
    }
  }

  const loadProfiles = async () => {
    if (!publicKey) return
    setLoading(true)
    try {
      const response = await axios.get(
        `${API_BASE}/api/profiles/${publicKey.toString()}`
      )
      setProfiles(response.data.profiles)
      setCurrentProfileIndex(0)
    } catch (error) {
      toast.error('Failed to load profiles')
      console.error('Error loading profiles:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSwipe = async (direction: 'left' | 'right') => {
    if (!publicKey || !profiles[currentProfileIndex]) return

    try {
      const response = await axios.post(`${API_BASE}/api/swipe`, {
        user_wallet: publicKey.toString(),
        target_wallet: profiles[currentProfileIndex].wallet_address,
        direction
      })

      if (response.data.match_created) {
        toast.success('🎉 It\'s a match! Start chatting now!', {
          duration: 5000,
          position: 'top-center',
          style: {
            background: '#10B981',
            color: 'white',
            fontSize: '16px',
            fontWeight: 'bold',
          }
        })
      } else if (direction === 'right') {
        toast('👍 Liked!', { icon: '💚' })
      }

      // Move to next profile after a small delay to allow animation to complete
      setTimeout(() => {
        if (currentProfileIndex < profiles.length - 1) {
          setCurrentProfileIndex(currentProfileIndex + 1)
        } else {
          // Load more profiles
          toast.success('Loading more profiles...')
          loadProfiles()
        }
      }, 100)
    } catch (error) {
      toast.error('Failed to record swipe')
      console.error('Error swiping:', error)
    }
  }

  const saveNansenApiKey = async () => {
    try {
      await axios.post(`${API_BASE}/api/config/nansen`, {
        api_key: nansenApiKey
      })
      toast.success('Nansen API key saved!')
      setShowSettings(false)
      loadProfiles()
    } catch (error) {
      toast.error('Failed to save API key')
    }
  }

  if (!connected) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-black to-green-900 relative overflow-hidden">
        <Toaster />
        <div className="text-center relative z-10">
          <div className="mb-8">
            <div className="text-9xl mb-6 animate-pulse">💎</div>
            <h1 className="text-7xl font-bold mb-6 gradient-text">
              SizeMatters
            </h1>
            <p className="text-2xl text-gray-200 mb-8 font-medium">
              Where whales flirt through PnL 🐋✨
            </p>
          </div>
          <div className="mb-8">
            <WalletMultiButton />
          </div>
          <div className="mt-8 space-y-3 text-gray-300 glass p-6 rounded-2xl inline-block border border-purple-500/30">
            <p className="flex items-center gap-3 text-lg"><span className="text-2xl">🔥</span> Swipe through elite traders</p>
            <p className="flex items-center gap-3 text-lg"><span className="text-2xl">📊</span> Real-time Nansen PnL data</p>
            <p className="flex items-center gap-3 text-lg"><span className="text-2xl">💬</span> Connect & strategize together</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-black to-green-900">
      <Toaster />
      
      {/* Header */}
      <div className="glass border-b-2 border-purple-500/30 relative z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-4xl">💎</span>
            <h1 className="text-3xl font-bold gradient-text">
              SizeMatters
            </h1>
          </div>
          
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 hover:bg-gray-800 rounded-lg transition"
            >
              <FiSettings className="text-2xl text-gray-300" />
            </button>
            <WalletMultiButton />
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
          <div className="bg-gray-900 p-8 rounded-2xl max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-4 text-white">Settings</h2>
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2">
                Nansen API Key (Optional)
              </label>
              <input
                type="password"
                value={nansenApiKey}
                onChange={(e) => setNansenApiKey(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
                placeholder="Enter your Nansen API key"
              />
              <p className="text-xs text-gray-500 mt-2">
                Leave empty to use mock data for demo
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={saveNansenApiKey}
                className="flex-1 bg-gradient-to-r from-purple-500 to-green-500 py-2 rounded-lg font-semibold hover:opacity-90 transition"
              >
                Save
              </button>
              <button
                onClick={() => setShowSettings(false)}
                className="flex-1 bg-gray-800 py-2 rounded-lg font-semibold hover:bg-gray-700 transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="max-w-md mx-auto px-4 pt-4">
        <div className="flex gap-2 bg-gray-900 bg-opacity-50 rounded-2xl p-1">
          <button
            onClick={() => setView('swipe')}
            className={`flex-1 py-3 rounded-xl font-semibold transition ${
              view === 'swipe'
                ? 'bg-gradient-to-r from-purple-500 to-green-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Swipe
          </button>
          <button
            onClick={() => setView('matches')}
            className={`flex-1 py-3 rounded-xl font-semibold transition ${
              view === 'matches'
                ? 'bg-gradient-to-r from-purple-500 to-green-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <FiMessageCircle />
              Matches
            </div>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-md mx-auto px-4 py-8">
        {view === 'swipe' ? (
          loading ? (
            <div className="text-center text-white">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
              <p>Loading profiles...</p>
            </div>
          ) : profiles.length > 0 && currentProfileIndex < profiles.length ? (
            <SwipeCard
              key={profiles[currentProfileIndex].wallet_address}
              profile={profiles[currentProfileIndex]}
              onSwipe={handleSwipe}
            />
          ) : (
            <div className="text-center text-white bg-gray-900 bg-opacity-50 p-8 rounded-2xl">
              <p className="text-xl mb-4">No more profiles available</p>
              <p className="text-sm text-gray-400 mb-4">
                You've seen all {profiles.length} available traders!
              </p>
              <button
                onClick={loadProfiles}
                className="bg-gradient-to-r from-purple-500 to-green-500 px-6 py-3 rounded-xl font-semibold hover:opacity-90 transition"
              >
                Reload Profiles
              </button>
            </div>
          )
        ) : (
          <Matches walletAddress={publicKey?.toString() || ''} />
        )}
      </div>

      {/* Bio Modal */}
      {showBioModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl p-8 max-w-md w-full border border-gray-700">
            <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-green-400 bg-clip-text text-transparent">
              Welcome to SizeMatters! 🚀
            </h2>
            <p className="text-gray-300 mb-6">
              Tell other traders about yourself
            </p>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="I'm a DeFi degen who loves high-risk trades and memecoins..."
              className="w-full bg-gray-800 text-white rounded-xl p-4 mb-4 border border-gray-600 focus:border-purple-500 focus:outline-none min-h-[120px] resize-none"
              maxLength={200}
            />
            <div className="text-sm text-gray-400 mb-4">
              {bio.length}/200 characters
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowBioModal(false)}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-xl font-semibold transition"
              >
                Skip
              </button>
              <button
                onClick={saveBio}
                className="flex-1 bg-gradient-to-r from-purple-500 to-green-500 hover:opacity-90 text-white px-6 py-3 rounded-xl font-semibold transition"
              >
                Save Bio
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

