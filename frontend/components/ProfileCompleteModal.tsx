'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from 'axios'
import toast from 'react-hot-toast'
import { FiX, FiCheck } from 'react-icons/fi'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ProfileCompleteModalProps {
  walletAddress: string
  onComplete: () => void
}

// Country list with emoji flags (expanded)
const COUNTRIES = [
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
  { code: 'DE', name: 'Germany', flag: '🇩🇪' },
  { code: 'FR', name: 'France', flag: '🇫🇷' },
  { code: 'ES', name: 'Spain', flag: '🇪🇸' },
  { code: 'IT', name: 'Italy', flag: '🇮🇹' },
  { code: 'IE', name: 'Ireland', flag: '🇮🇪' },
  { code: 'NL', name: 'Netherlands', flag: '🇳🇱' },
  { code: 'BE', name: 'Belgium', flag: '🇧🇪' },
  { code: 'CH', name: 'Switzerland', flag: '🇨🇭' },
  { code: 'AT', name: 'Austria', flag: '🇦🇹' },
  { code: 'SE', name: 'Sweden', flag: '🇸🇪' },
  { code: 'NO', name: 'Norway', flag: '🇳🇴' },
  { code: 'DK', name: 'Denmark', flag: '🇩🇰' },
  { code: 'FI', name: 'Finland', flag: '🇫🇮' },
  { code: 'IS', name: 'Iceland', flag: '🇮🇸' },
  { code: 'PL', name: 'Poland', flag: '🇵🇱' },
  { code: 'CZ', name: 'Czech Republic', flag: '🇨🇿' },
  { code: 'GR', name: 'Greece', flag: '🇬🇷' },
  { code: 'PT', name: 'Portugal', flag: '🇵🇹' },
  { code: 'RO', name: 'Romania', flag: '🇷🇴' },
  { code: 'HU', name: 'Hungary', flag: '🇭🇺' },
  { code: 'TR', name: 'Turkey', flag: '🇹🇷' },
  { code: 'RU', name: 'Russia', flag: '🇷🇺' },
  { code: 'UA', name: 'Ukraine', flag: '🇺🇦' },
  { code: 'SG', name: 'Singapore', flag: '🇸🇬' },
  { code: 'HK', name: 'Hong Kong', flag: '🇭🇰' },
  { code: 'JP', name: 'Japan', flag: '🇯🇵' },
  { code: 'KR', name: 'South Korea', flag: '🇰🇷' },
  { code: 'CN', name: 'China', flag: '🇨🇳' },
  { code: 'TW', name: 'Taiwan', flag: '🇹🇼' },
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'TH', name: 'Thailand', flag: '🇹🇭' },
  { code: 'VN', name: 'Vietnam', flag: '🇻🇳' },
  { code: 'PH', name: 'Philippines', flag: '🇵🇭' },
  { code: 'ID', name: 'Indonesia', flag: '🇮🇩' },
  { code: 'MY', name: 'Malaysia', flag: '🇲🇾' },
  { code: 'NZ', name: 'New Zealand', flag: '🇳🇿' },
  { code: 'AE', name: 'UAE', flag: '🇦🇪' },
  { code: 'SA', name: 'Saudi Arabia', flag: '🇸🇦' },
  { code: 'IL', name: 'Israel', flag: '🇮🇱' },
  { code: 'ZA', name: 'South Africa', flag: '🇿🇦' },
  { code: 'NG', name: 'Nigeria', flag: '🇳🇬' },
  { code: 'EG', name: 'Egypt', flag: '🇪🇬' },
  { code: 'BR', name: 'Brazil', flag: '🇧🇷' },
  { code: 'MX', name: 'Mexico', flag: '🇲🇽' },
  { code: 'AR', name: 'Argentina', flag: '🇦🇷' },
  { code: 'CL', name: 'Chile', flag: '🇨🇱' },
  { code: 'CO', name: 'Colombia', flag: '🇨🇴' },
  { code: 'PE', name: 'Peru', flag: '🇵🇪' },
  { code: 'VE', name: 'Venezuela', flag: '🇻🇪' },
  { code: 'OTHER', name: 'Other', flag: '🌍' }
]

export const ProfileCompleteModal: React.FC<ProfileCompleteModalProps> = ({ walletAddress, onComplete }) => {
  const [bio, setBio] = useState('')
  const [country, setCountry] = useState('')
  const [favouriteCT, setFavouriteCT] = useState('')
  const [worstCT, setWorstCT] = useState('')
  const [twitterAccount, setTwitterAccount] = useState('')
  const [venue, setVenue] = useState('')
  const [customVenue, setCustomVenue] = useState('')
  const [assetChoice, setAssetChoice] = useState('')
  const [venues, setVenues] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(1)

  useEffect(() => {
    fetchVenues()
  }, [])

  const fetchVenues = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/config/trading-venues`)
      setVenues(response.data.venues)
    } catch (error) {
      console.error('Failed to fetch venues:', error)
    }
  }

  const validate = () => {
    if (!bio.trim()) return 'Bio is required'
    if (!country) return 'Country is required'
    if (!favouriteCT.trim()) return 'Favourite CT account is required'
    // worstCT is now optional
    if (!venue) return 'Favourite trading venue is required'
    if (venue === 'Other' && !customVenue.trim()) return 'Please specify your trading venue'
    if (!assetChoice.trim()) return 'Asset choice is required'
    return null
  }

  const handleSubmit = async () => {
    const error = validate()
    if (error) {
      toast.error(error)
      return
    }

    setLoading(true)
    try {
      const finalVenue = venue === 'Other' ? customVenue : venue
      await axios.post(`${API_BASE}/api/users/${walletAddress}/complete-profile`, {
        bio: bio.trim(),
        country: country,
        favourite_ct_account: favouriteCT.trim(),
        worst_ct_account: worstCT.trim() || null,  // Optional field
        favourite_trading_venue: finalVenue,
        asset_choice_6m: assetChoice.trim(),
        twitter_account: twitterAccount.trim() || null  // Optional field
      })
      
      toast.success('Profile completed! 🎉')
      onComplete()
    } catch (error) {
      toast.error('Failed to complete profile')
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  const selectedCountry = COUNTRIES.find(c => c.code === country)

  return (
    <motion.div
      className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center p-4 z-50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <motion.div
        className="glass max-w-2xl w-full max-h-[90vh] overflow-y-auto p-8 rounded-3xl border border-purple-500/30"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
      >
        <div className="mb-6">
          <h2 className="text-3xl font-bold gradient-text mb-2">
            Complete Your Profile ✨
          </h2>
          <p className="text-gray-400">
            Let other traders know about you! Fields marked with * are required.
          </p>
          <div className="mt-4 flex gap-2">
            {[1, 2].map(s => (
              <div
                key={s}
                className={`flex-1 h-2 rounded-full ${
                  s <= step ? 'bg-purple-500' : 'bg-gray-700'
                }`}
              />
            ))}
          </div>
        </div>

        {step === 1 ? (
          <div className="space-y-6">
            {/* Bio */}
            <div>
              <label className="block text-sm font-semibold text-purple-300 mb-2">
                Bio * 📝
              </label>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Tell us about your trading style..."
                className="w-full p-4 bg-gray-800 border border-purple-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none"
                rows={4}
                maxLength={300}
              />
              <p className="text-xs text-gray-500 mt-1">{bio.length}/300</p>
            </div>

            {/* Country */}
            <div>
              <label className="block text-sm font-semibold text-purple-300 mb-2">
                Country * {selectedCountry?.flag}
              </label>
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="w-full p-4 bg-gray-800 border border-purple-500/30 rounded-xl text-white focus:outline-none focus:border-purple-500"
              >
                <option value="">Select your country...</option>
                {COUNTRIES.map(c => (
                  <option key={c.code} value={c.code}>
                    {c.flag} {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Asset Choice */}
            <div>
              <label className="block text-sm font-semibold text-purple-300 mb-2">
                Asset of Choice (Next 6 months) * 🎯
              </label>
              <input
                type="text"
                value={assetChoice}
                onChange={(e) => setAssetChoice(e.target.value)}
                placeholder="e.g., SOL, BTC, ETH, Memecoins..."
                className="w-full p-4 bg-gray-800 border border-purple-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                maxLength={50}
              />
            </div>

            <button
              onClick={() => setStep(2)}
              className="w-full bg-purple-500 hover:bg-purple-600 text-white font-bold py-4 rounded-xl transition glow-purple"
            >
              Next →
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Favourite CT Account */}
            <div>
              <label className="block text-sm font-semibold text-green-300 mb-2">
                Favourite CT Account * 💚
              </label>
              <input
                type="text"
                value={favouriteCT}
                onChange={(e) => setFavouriteCT(e.target.value)}
                placeholder="@username"
                className="w-full p-4 bg-gray-800 border border-green-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
                maxLength={50}
              />
            </div>

            {/* Worst CT Account */}
            <div>
              <label className="block text-sm font-semibold text-red-300 mb-2">
                Worst CT Account (Optional) 💔
              </label>
              <input
                type="text"
                value={worstCT}
                onChange={(e) => setWorstCT(e.target.value)}
                placeholder="@username (optional)"
                className="w-full p-4 bg-gray-800 border border-red-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-red-500"
                maxLength={50}
              />
            </div>

            {/* Twitter Account */}
            <div>
              <label className="block text-sm font-semibold text-blue-300 mb-2">
                Your Twitter (Optional) 🐦
              </label>
              <input
                type="text"
                value={twitterAccount}
                onChange={(e) => setTwitterAccount(e.target.value)}
                placeholder="@username (optional)"
                className="w-full p-4 bg-gray-800 border border-blue-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                maxLength={50}
              />
            </div>

            {/* Favourite Trading Venue */}
            <div>
              <label className="block text-sm font-semibold text-cyan-300 mb-2">
                Favourite Trading Venue * ⚡
              </label>
              <select
                value={venue}
                onChange={(e) => setVenue(e.target.value)}
                className="w-full p-4 bg-gray-800 border border-cyan-500/30 rounded-xl text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="">Select venue...</option>
                {venues.map(v => (
                  <option key={v} value={v}>{v}</option>
                ))}
              </select>
              
              {venue === 'Other' && (
                <input
                  type="text"
                  value={customVenue}
                  onChange={(e) => setCustomVenue(e.target.value)}
                  placeholder="Enter venue name..."
                  className="w-full p-4 bg-gray-800 border border-cyan-500/30 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 mt-3"
                  maxLength={50}
                />
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-bold py-4 rounded-xl transition"
              >
                ← Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="flex-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold py-4 px-8 rounded-xl transition glow-purple disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Complete Profile! 🚀'}
              </button>
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  )
}

