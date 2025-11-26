'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { useEffect, useState } from 'react'
import { SwipeCard } from '@/components/SwipeCard'
import { Matches } from '@/components/Matches'
import { ProfileCompleteModal } from '@/components/ProfileCompleteModal'
import { MyProfile } from '@/components/MyProfile'
import axios from 'axios'
import toast, { Toaster } from 'react-hot-toast'
import { FiHeart, FiMessageCircle, FiSettings } from 'react-icons/fi'
import { getAuthHeaders, clearSessionToken } from '@/utils/auth'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Profile {
  wallet_address: string
  pnl_summary: any
  balance: any
  trader_number: number | null
  trader_number_formatted: string
  bio: string | null
  country: string | null
  favourite_ct_account: string | null
  worst_ct_account: string | null
  favourite_trading_venue: string | null
  asset_choice_6m: string | null
  twitter_account: string | null
  is_demo: boolean
}

export default function Home() {
  const wallet = useWallet()
  const { publicKey, connected } = wallet
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [currentProfileIndex, setCurrentProfileIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const [view, setView] = useState<'swipe' | 'matches'>('swipe')
  const [showSettings, setShowSettings] = useState(false)
  const [showMyProfile, setShowMyProfile] = useState(false)
  const [nansenApiKey, setNansenApiKey] = useState('')
  const [showProfileModal, setShowProfileModal] = useState(false)

  useEffect(() => {
    if (connected && publicKey) {
      checkUserProfile()
      loadProfiles()
    } else {
      // Clear session when wallet disconnects
      clearSessionToken()
    }
  }, [connected, publicKey])

  const checkUserProfile = async () => {
    if (!publicKey) return
    try {
      const response = await axios.post(`${API_BASE}/api/users`, {
        wallet_address: publicKey.toString()
      })
      // If profile incomplete, show modal
      if (!response.data.profile_complete) {
        setShowProfileModal(true)
      }
    } catch (error) {
      console.error('Error checking user profile:', error)
    }
  }

  const handleProfileComplete = () => {
    setShowProfileModal(false)
    toast.success('Welcome to SizeMatters! 🎉')
    loadProfiles()
  }

  const loadProfiles = async () => {
    if (!publicKey) return
    setLoading(true)
    try {
      const response = await axios.get(
        `${API_BASE}/api/profiles/${publicKey.toString()}`
      )
      console.log('Loaded profiles:', response.data.profiles)
      if (response.data.profiles && response.data.profiles.length > 0) {
        setProfiles(response.data.profiles)
        setCurrentProfileIndex(0)
      } else {
        toast.error('No trader profiles available yet. Check back soon! 🚀')
        setProfiles([])
      }
    } catch (error) {
      toast.error('Failed to connect to API. Please try again.')
      console.error('Error loading profiles:', error)
      setProfiles([])
    } finally {
      setLoading(false)
    }
  }

  const handleSwipe = async (direction: 'left' | 'right') => {
    if (!publicKey || !profiles[currentProfileIndex]) return

    try {
      // Get authenticated headers (with signature if available)
      const headers = await getAuthHeaders(wallet)
      
      const response = await axios.post(`${API_BASE}/api/swipe`, {
        user_wallet: publicKey.toString(),
        target_wallet: profiles[currentProfileIndex].wallet_address,
        direction
      }, {
        headers
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
      <div className="min-h-screen flex items-center justify-center relative overflow-hidden" style={{ background: 'var(--color-bg-dark)' }}>
        <Toaster />
        <div className="text-center relative z-10">
          <div className="mb-8">
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
          <div className="mt-8 space-y-3 text-gray-300 glass p-6 rounded-2xl inline-block border border-[#FD3021]/30">
            <p className="flex items-center gap-3 text-lg"><span className="text-2xl">🔥</span> Swipe through elite traders</p>
            <p className="flex items-center gap-3 text-lg"><span className="text-2xl">📊</span> Real-time Nansen PnL data</p>
            <p className="flex items-center gap-3 text-lg"><span className="text-2xl">💬</span> Connect & strategize together</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-bg-dark)' }}>
      <Toaster />
      
      {/* Header */}
      <div className="glass border-b-2 border-[#FD3021]/30 relative z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold gradient-text">
              SizeMatters
            </h1>
          </div>
          
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowMyProfile(true)}
              className="px-4 py-2 bg-[#FD3021]/20 hover:bg-[#FD3021]/30 border border-[#FD3021]/50 text-[#FBFFFE] rounded-lg transition font-semibold"
            >
              👤 My Profile
            </button>
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
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
          <div className="glass p-8 rounded-3xl max-w-md w-full mx-4 border-2 border-cyan-500/30 glow-cyan">
            <h2 className="text-3xl font-bold mb-6 gradient-text flex items-center gap-2">
              <span className="text-4xl">⚙️</span> Settings
            </h2>
            <div className="mb-6">
              <label className="block text-sm text-gray-300 mb-3 font-semibold">
                🔑 Nansen API Key (Optional)
              </label>
              <input
                type="password"
                value={nansenApiKey}
                onChange={(e) => setNansenApiKey(e.target.value)}
                className="w-full px-4 py-3 glass border-2 border-[#FD3021]/50 rounded-xl text-white focus:outline-none focus:border-[#FF6B5B] focus:glow-coral transition"
                placeholder="Enter your Nansen API key..."
              />
              <p className="text-xs text-gray-400 mt-2">
                💡 Leave empty to use mock data for demo
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={saveNansenApiKey}
                className="flex-1 bg-gradient-to-r from-[#FD3021] to-[#FF6B5B] py-3 rounded-xl font-bold hover:scale-105 glow-coral transition-all"
              >
                💾 Save
              </button>
              <button
                onClick={() => setShowSettings(false)}
                className="flex-1 glass py-3 rounded-xl font-bold hover:glow-red border-2 border-gray-700 transition-all"
              >
                ✖️ Close
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
                ? 'bg-gradient-to-r from-[#FD3021] to-[#FF6B5B]'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Swipe
          </button>
          <button
            onClick={() => setView('matches')}
            className={`flex-1 py-3 rounded-xl font-semibold transition ${
              view === 'matches'
                ? 'bg-gradient-to-r from-[#FD3021] to-[#FF6B5B]'
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
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-[#FD3021] mx-auto mb-4"></div>
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
                className="bg-gradient-to-r from-[#FD3021] to-[#FF6B5B] px-6 py-3 rounded-xl font-semibold hover:opacity-90 transition"
              >
                Reload Profiles
              </button>
            </div>
          )
        ) : (
          <Matches walletAddress={publicKey?.toString() || ''} />
        )}
      </div>

      {/* Profile Complete Modal */}
      {showProfileModal && publicKey && (
        <ProfileCompleteModal
          walletAddress={publicKey.toString()}
          onComplete={handleProfileComplete}
        />
      )}

      {/* My Profile Modal */}
      {showMyProfile && publicKey && (
        <MyProfile
          walletAddress={publicKey.toString()}
          onClose={() => setShowMyProfile(false)}
        />
      )}
    </div>
  )
}

