'use client'

import { motion, useMotionValue, useTransform, useAnimation } from 'framer-motion'
import { FiX, FiHeart, FiTrendingUp, FiDollarSign } from 'react-icons/fi'
import { useState } from 'react'

interface Profile {
  wallet_address: string
  pnl_summary: any
  balance: any
  bio?: string
}

interface SwipeCardProps {
  profile: Profile
  onSwipe: (direction: 'left' | 'right') => void
}

export const SwipeCard: React.FC<SwipeCardProps> = ({ profile, onSwipe }) => {
  const x = useMotionValue(0)
  const rotate = useTransform(x, [-200, 200], [-25, 25])
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0])
  const [exitDirection, setExitDirection] = useState<'left' | 'right' | null>(null)
  const controls = useAnimation()

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
        className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl overflow-hidden shadow-2xl border border-gray-700"
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
          {/* Wallet Address */}
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-white mb-2">
              Trader {formatWallet(profile.wallet_address)}
            </h2>
            <p className="text-sm text-gray-400 font-mono break-all">
              {profile.wallet_address}
            </p>
          </div>

          {/* Bio */}
          {profile.bio && (
            <div className="mb-6 bg-gradient-to-r from-purple-900/30 to-green-900/30 p-4 rounded-2xl border border-gray-700">
              <p className="text-gray-300 italic">"{profile.bio}"</p>
            </div>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            {/* PnL Card */}
            <div className="bg-gradient-to-br from-purple-900 to-purple-800 p-5 rounded-2xl">
              <div className="flex items-center gap-2 mb-2">
                <FiTrendingUp className="text-purple-300" />
                <p className="text-xs text-purple-300 font-semibold">90D PnL</p>
              </div>
              <p className="text-2xl font-bold text-white">
                {formatCurrency(profile.pnl_summary.total_pnl || 0)}
              </p>
              <p className="text-sm text-purple-200 mt-1">
                {profile.pnl_summary.pnl_percentage || 0}% return
              </p>
            </div>

            {/* Balance Card */}
            <div className="bg-gradient-to-br from-green-900 to-green-800 p-5 rounded-2xl">
              <div className="flex items-center gap-2 mb-2">
                <FiDollarSign className="text-green-300" />
                <p className="text-xs text-green-300 font-semibold">Balance</p>
              </div>
              <p className="text-2xl font-bold text-white">
                {formatCurrency(profile.balance.total_balance_usd || 0)}
              </p>
              <p className="text-sm text-green-200 mt-1">
                {profile.balance.sol_balance || 0} SOL
              </p>
            </div>
          </div>

          {/* Additional Stats */}
          <div className="bg-gray-800 bg-opacity-50 p-5 rounded-2xl space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-400">Win Rate</span>
              <span className="text-white font-semibold">
                {profile.pnl_summary.win_rate || 0}%
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
          </div>

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
          className="bg-red-500 hover:bg-red-600 text-white w-16 h-16 rounded-full flex items-center justify-center shadow-lg transition"
          whileHover={{ scale: 1.1, rotate: -10 }}
          whileTap={{ scale: 0.9, rotate: -20 }}
          disabled={exitDirection !== null}
        >
          <FiX className="text-3xl" />
        </motion.button>
        <motion.button
          onClick={() => handleButtonSwipe('right')}
          className="bg-green-500 hover:bg-green-600 text-white w-16 h-16 rounded-full flex items-center justify-center shadow-lg transition"
          whileHover={{ scale: 1.1, rotate: 10 }}
          whileTap={{ scale: 0.9, rotate: 20 }}
          disabled={exitDirection !== null}
        >
          <FiHeart className="text-3xl" />
        </motion.button>
      </div>
    </div>
  )
}

