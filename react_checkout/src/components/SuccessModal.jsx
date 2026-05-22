import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag } from 'lucide-react';

const confettiColors = [
  '#6366f1', '#8b5cf6', '#3b82f6', '#06b6d4',
  '#ec4899', '#f59e0b', '#10b981', '#ef4444',
];

function ConfettiPiece({ color, delay, left }) {
  return (
    <div
      className="confetti-piece"
      style={{
        backgroundColor: color,
        left: `${left}%`,
        animationDelay: `${delay}s`,
        width: `${4 + Math.random() * 6}px`,
        height: `${4 + Math.random() * 6}px`,
        borderRadius: Math.random() > 0.5 ? '50%' : '2px',
      }}
    />
  );
}

function SuccessModal({ show, orderNumber, onClose }) {
  const confettiPieces = useMemo(
    () =>
      Array.from({ length: 40 }, (_, i) => ({
        id: i,
        color: confettiColors[i % confettiColors.length],
        delay: Math.random() * 2,
        left: Math.random() * 100,
      })),
    []
  );

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/70 backdrop-blur-md"
          />

          <motion.div
            initial={{ scale: 0.8, opacity: 0, y: 40 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.8, opacity: 0, y: 40 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="relative z-10 glass-strong rounded-3xl p-8 md:p-12 max-w-md w-full text-center overflow-hidden border border-glow-border"
          >
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              {confettiPieces.map((p) => (
                <ConfettiPiece key={p.id} color={p.color} delay={p.delay} left={p.left} />
              ))}
            </div>

            <div className="relative z-10">
              <div className="w-24 h-24 mx-auto mb-6 relative">
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="#6366f1"
                    strokeWidth="6"
                    strokeLinecap="round"
                    className="checkmark-circle"
                    style={{
                      strokeDasharray: 283,
                      strokeDashoffset: 283,
                      animation: 'draw-circle 0.8s ease-in-out forwards',
                    }}
                  />
                  <path
                    d="M30 50 L45 65 L70 35"
                    fill="none"
                    stroke="#6366f1"
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="checkmark-path"
                    style={{
                      strokeDasharray: 100,
                      strokeDashoffset: 100,
                      animation: 'draw-check 0.6s ease-in-out 0.8s forwards',
                    }}
                  />
                </svg>

                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.5, type: 'spring', stiffness: 200 }}
                  className="absolute inset-0 rounded-full animate-pulse-glow"
                />
              </div>

              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="text-3xl font-extrabold neon-text mb-3"
              >
                Payment Successful!
              </motion.h2>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="text-gray-400 text-sm mb-6"
              >
                Thank you for shopping at <span className="text-glow-indigo font-semibold">Gadget Glow</span>
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 }}
                className="bg-glow-darker/50 rounded-2xl p-4 mb-6 border border-glow-border/50"
              >
                <p className="text-xs text-gray-500 mb-1">Order Number</p>
                <p className="text-lg font-mono font-bold text-glow-indigo tracking-wider">
                  {orderNumber}
                </p>
              </motion.div>

              <motion.button
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onClose}
                className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-glow-indigo to-glow-purple text-white font-bold text-lg hover:opacity-90 transition-all neon-glow flex items-center justify-center gap-2"
              >
                <ShoppingBag className="w-5 h-5" />
                Continue Shopping
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default SuccessModal;
