'use client'

import { motion, useMotionValue, useTransform, useAnimation } from 'framer-motion'
import { FiX, FiHeart, FiTrendingUp, FiDollarSign, FiCopy, FiCheck } from 'react-icons/fi'
import { useState } from 'react'
import toast from 'react-hot-toast'

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
  is_demo: boolean
}

interface SwipeCardProps {
  profile: Profile
  onSwipe: (direction: 'left' | 'right') => void
}

// Country code to flag emoji mapping (expanded)
const getCountryFlag = (countryCode: string | null) => {
  if (!countryCode) return ''
  const flags: Record<string, string> = {
    US: '🇺🇸', GB: '🇬🇧', CA: '🇨🇦', AU: '🇦🇺', DE: '🇩🇪', FR: '🇫🇷',
    ES: '🇪🇸', IT: '🇮🇹', IE: '🇮🇪', NL: '🇳🇱', BE: '🇧🇪', CH: '🇨🇭',
    AT: '🇦🇹', SE: '🇸🇪', NO: '🇳🇴', DK: '🇩🇰', FI: '🇫🇮', IS: '🇮🇸',
    PL: '🇵🇱', CZ: '🇨🇿', GR: '🇬🇷', PT: '🇵🇹', RO: '🇷🇴', HU: '🇭🇺',
    TR: '🇹🇷', RU: '🇷🇺', UA: '🇺🇦', SG: '🇸🇬', HK: '🇭🇰', JP: '🇯🇵',
    KR: '🇰🇷', CN: '🇨🇳', TW: '🇹🇼', IN: '🇮🇳', TH: '🇹🇭', VN: '🇻🇳',
    PH: '🇵🇭', ID: '🇮🇩', MY: '🇲🇾', NZ: '🇳🇿', AE: '🇦🇪', SA: '🇸🇦',
    IL: '🇮🇱', ZA: '🇿🇦', NG: '🇳🇬', EG: '🇪🇬', BR: '🇧🇷', MX: '🇲🇽',
    AR: '🇦🇷', CL: '🇨🇱', CO: '🇨🇴', PE: '🇵🇪', VE: '🇻🇪', OTHER: '🌍'
  }
  return flags[countryCode] || '🌍'
}

// Country code to full name mapping
const getCountryName = (countryCode: string | null) => {
  if (!countryCode) return 'Unknown'
  const names: Record<string, string> = {
    US: 'United States', GB: 'United Kingdom', CA: 'Canada', AU: 'Australia',
    DE: 'Germany', FR: 'France', ES: 'Spain', IT: 'Italy', IE: 'Ireland',
    NL: 'Netherlands', BE: 'Belgium', CH: 'Switzerland', AT: 'Austria',
    SE: 'Sweden', NO: 'Norway', DK: 'Denmark', FI: 'Finland', IS: 'Iceland',
    PL: 'Poland', CZ: 'Czech Republic', GR: 'Greece', PT: 'Portugal',
    RO: 'Romania', HU: 'Hungary', TR: 'Turkey', RU: 'Russia', UA: 'Ukraine',
    SG: 'Singapore', HK: 'Hong Kong', JP: 'Japan', KR: 'South Korea',
    CN: 'China', TW: 'Taiwan', IN: 'India', TH: 'Thailand', VN: 'Vietnam',
    PH: 'Philippines', ID: 'Indonesia', MY: 'Malaysia', NZ: 'New Zealand',
    AE: 'UAE', SA: 'Saudi Arabia', IL: 'Israel', ZA: 'South Africa',
    NG: 'Nigeria', EG: 'Egypt', BR: 'Brazil', MX: 'Mexico', AR: 'Argentina',
    CL: 'Chile', CO: 'Colombia', PE: 'Peru', VE: 'Venezuela', OTHER: 'Other'
  }
  return names[countryCode] || 'Unknown'
}

export const SwipeCard: React.FC<SwipeCardProps> = ({ profile, onSwipe }) => {
  const x = useMotionValue(0)
  const rotate = useTransform(x, [-200, 200], [-25, 25])
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0])
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null)
  const [copied, setCopied] = useState(false)
  const [showMore, setShowMore] = useState(false)
  const controls = useAnimation()

  const handleCopyAddress = async () => {
    try {
      await navigator.clipboard.writeText(profile.wallet_address)
      setCopied(true)
      toast.success('Address copied!')
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      toast.error('Failed to copy')
    }
  }

  const handleDragEnd = (event: any, info: any) => {
    if (info.offset.x > 100) {
      handleSwipeAnimation('right')
    } else if (info.offset.x < -100) {
      handleSwipeAnimation('left')
    } else {
      // Snap back to center
      controls.start({ x: 0, rotate: 0 })
    }
  }

  const handleSwipeAnimation = async (direction: 'left' | 'right') => {
    setExitDirection(direction)
    
    // Animate card flying off screen
    await controls.start({
      x: direction === 'right' ? 1000 : -1000,
      rotate: direction === 'right' ? 45 : -45,
      opacity: 0,
      transition: { duration: 0.3, ease: 'easeIn' }
    })
    
    // Call the parent's onSwipe handler
    onSwipe(direction)
    
    // Reset the card position for the next card
    setExitDirection(null)
    controls.set({ x: 0, rotate: 0, opacity: 1 })
  }

  const handleButtonSwipe = (direction: 'left' | 'right') => {
    handleSwipeAnimation(direction)
  }

  const formatWallet = (address: string) => {
    return `${address.slice(0, 4)}...${address.slice(-4)}`
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  return (
    <div className="relative">
      <motion.div
        className="glass rounded-3xl overflow-hidden shadow-2xl border-2 border-purple-500/30"
        style={{ x, rotate, opacity }}
        animate={controls}
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        onDragEnd={handleDragEnd}
        whileTap={{ cursor: 'grabbing' }}
        initial={{ scale: 0.9, opacity: 0 }}
        whileInView={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {/* Swipe Indicators with animations */}
        <motion.div
          className="absolute top-8 right-8 z-10 bg-red-500 text-white px-6 py-3 rounded-xl font-bold text-2xl rotate-12 border-4 border-white shadow-lg"
          style={{ opacity: useTransform(x, [-200, -50, 0], [1, 0.5, 0]) }}
          animate={exitDirection === 'left' ? { 
            scale: [1, 1.5, 1.5],
            rotate: [12, 12, 360 + 12],
          } : {}}
          transition={{ duration: 0.5 }}
        >
          NOPE
        </motion.div>
        <motion.div
          className="absolute top-8 left-8 z-10 bg-green-500 text-white px-6 py-3 rounded-xl font-bold text-2xl -rotate-12 border-4 border-white shadow-lg"
          style={{ opacity: useTransform(x, [0, 50, 200], [0, 0.5, 1]) }}
          animate={exitDirection === 'right' ? { 
            scale: [1, 1.5, 1.5],
            rotate: [-12, -12, -360 - 12],
          } : {}}
          transition={{ duration: 0.5 }}
        >
          LIKE
        </motion.div>
        
        {/* Celebration particles for LIKE */}
        {exitDirection === 'right' && (
          <>
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute top-1/2 left-1/2 w-4 h-4 bg-green-400 rounded-full"
                initial={{ scale: 0, x: 0, y: 0 }}
                animate={{
                  scale: [0, 1, 0],
                  x: Math.cos((i * Math.PI) / 4) * 200,
                  y: Math.sin((i * Math.PI) / 4) * 200,
                  opacity: [1, 1, 0],
                }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              />
            ))}
          </>
        )}
        
        {/* Shake animation for NOPE */}
        {exitDirection === 'left' && (
          <motion.div
            className="absolute inset-0 bg-red-500 opacity-20"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.3, 0] }}
            transition={{ duration: 0.3 }}
          />
        )}

        {/* Profile Content */}
        <div className="p-8">
          {/* Header - Trader Number + Country */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-3xl font-bold text-white">
                Trader {profile.trader_number_formatted || '#000'}
              </h2>
              {profile.country && (
                <span className="text-4xl">{getCountryFlag(profile.country)}</span>
              )}
            </div>
            <button
              onClick={handleCopyAddress}
              className="flex items-center gap-2 text-sm text-gray-400 font-mono hover:text-purple-400 transition group"
            >
              <span className="break-all">{profile.wallet_address}</span>
              {copied ? (
                <FiCheck className="text-green-400 flex-shrink-0" />
              ) : (
                <FiCopy className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition" />
              )}
            </button>
          </div>

          {/* Bio */}
          {profile.bio && (
            <div className="mb-6 glass p-4 rounded-2xl border border-purple-500/30 glow-purple">
              <p className="text-gray-200 italic">💬 "{profile.bio}"</p>
            </div>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            {/* PnL Card */}
            <div className="glass p-5 rounded-2xl border border-purple-500/50 glow-purple">
              <div className="flex items-center gap-2 mb-2">
                <FiTrendingUp className="text-purple-300" />
                <p className="text-xs text-purple-300 font-semibold">
                  📈 {profile.pnl_summary.time_period || '90D'} PnL
                </p>
              </div>
              <p className="text-2xl font-bold gradient-text">
                {profile.pnl_summary.total_pnl_formatted || '$0'}
              </p>
              <p className="text-sm text-purple-200 mt-1">
                {profile.pnl_summary.pnl_percentage || 0}% return 🚀
              </p>
            </div>

            {/* Balance Card */}
            <div className="glass p-5 rounded-2xl border border-green-500/50 glow-green">
              <div className="flex items-center gap-2 mb-2">
                <FiDollarSign className="text-green-300" />
                <p className="text-xs text-green-300 font-semibold">💰 Balance</p>
              </div>
              <p className="text-2xl font-bold gradient-text">
                {profile.balance.total_balance_formatted || '$0'}
              </p>
              <p className="text-sm text-green-200 mt-1">
                {profile.balance.sol_balance_formatted || '0 SOL'} ⚡
              </p>
            </div>
          </div>

          {/* Quick Info - Venue + CT */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            {profile.favourite_trading_venue && (
              <div className="glass p-4 rounded-xl border border-cyan-500/30">
                <p className="text-xs text-cyan-300 mb-1">⚡ Venue</p>
                <p className="text-sm text-white font-semibold truncate">
                  {profile.favourite_trading_venue}
                </p>
              </div>
            )}
            {profile.favourite_ct_account && (
              <div className="glass p-4 rounded-xl border border-green-500/30">
                <p className="text-xs text-green-300 mb-1">💚 Fav CT</p>
                <p className="text-sm text-white font-semibold truncate">
                  {profile.favourite_ct_account}
                </p>
              </div>
            )}
          </div>

          {/* View More Toggle */}
          <button
            onClick={() => setShowMore(!showMore)}
            className="w-full bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 text-purple-200 font-semibold py-3 rounded-xl transition mb-4"
          >
            {showMore ? '▲ View Less' : '▼ View More'}
          </button>

          {/* Expandable Details */}
          {showMore && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-gray-800 bg-opacity-50 p-5 rounded-2xl space-y-3 mb-4"
            >
              <div className="flex justify-between">
                <span className="text-gray-400">Win Rate</span>
                <span className="text-white font-semibold">
                  {Math.round(profile.pnl_summary.win_rate || 0)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total Trades</span>
                <span className="text-white font-semibold">
                  {profile.pnl_summary.total_trades || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Token Holdings</span>
                <span className="text-white font-semibold">
                  {profile.balance.token_count || 0} tokens
                </span>
              </div>
              {profile.country && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Country</span>
                  <span className="text-white font-semibold">
                    {getCountryFlag(profile.country)} {getCountryName(profile.country)}
                  </span>
                </div>
              )}
              {profile.worst_ct_account && (
                <div className="flex justify-between">
                  <span className="text-gray-400">💔 Worst CT</span>
                  <span className="text-white font-semibold truncate max-w-[150px]">
                    {profile.worst_ct_account}
                  </span>
                </div>
              )}
              {profile.asset_choice_6m && (
                <div className="flex justify-between">
                  <span className="text-gray-400">🎯 Asset Choice</span>
                  <span className="text-white font-semibold truncate max-w-[150px]">
                    {profile.asset_choice_6m}
                  </span>
                </div>
              )}
            </motion.div>
          )}

          {/* Trading Style Badge */}
          <div className="mt-6 flex flex-wrap gap-2">
            {profile.pnl_summary.pnl_percentage > 50 && (
              <span className="bg-yellow-500 bg-opacity-20 text-yellow-300 px-4 py-2 rounded-full text-sm font-semibold">
                🔥 Hot Trader
              </span>
            )}
            {profile.pnl_summary.win_rate > 70 && (
              <span className="bg-blue-500 bg-opacity-20 text-blue-300 px-4 py-2 rounded-full text-sm font-semibold">
                🎯 High Win Rate
              </span>
            )}
            {profile.balance.total_balance_usd > 50000 && (
              <span className="bg-purple-500 bg-opacity-20 text-purple-300 px-4 py-2 rounded-full text-sm font-semibold">
                💎 Whale
              </span>
            )}
          </div>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <div className="flex justify-center gap-6 mt-8">
        <motion.button
          onClick={() => handleButtonSwipe('left')}
          className="bg-red-500 hover:bg-red-600 text-white w-20 h-20 rounded-full flex items-center justify-center shadow-lg transition glow-red"
          whileHover={{ scale: 1.2, rotate: -10 }}
          whileTap={{ scale: 0.85, rotate: -20 }}
          disabled={exitDirection !== null}
        >
          <span className="text-4xl">❌</span>
        </motion.button>
        <motion.button
          onClick={() => handleButtonSwipe('right')}
          className="bg-green-500 hover:bg-green-600 text-white w-20 h-20 rounded-full flex items-center justify-center shadow-lg transition glow-green pulse-glow"
          whileHover={{ scale: 1.2, rotate: 10 }}
          whileTap={{ scale: 0.85, rotate: 20 }}
          disabled={exitDirection !== null}
        >
          <span className="text-4xl">🔥</span>
        </motion.button>
      </div>
    </div>
  )
}

