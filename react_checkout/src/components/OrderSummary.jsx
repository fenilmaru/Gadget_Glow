import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, Tag, X, ShoppingBag } from 'lucide-react';

const defaultItems = [
  {
    id: 1,
    name: 'Quantum Wireless Buds Pro',
    quantity: 1,
    price: 129.99,
    color: 'from-glow-indigo to-glow-purple',
    emoji: '🎧',
  },
  {
    id: 2,
    name: 'Neon LED Smart Band',
    quantity: 2,
    price: 49.99,
    color: 'from-glow-purple to-glow-pink',
    emoji: '⌚',
  },
  {
    id: 3,
    name: 'Holographic Phone Stand',
    quantity: 1,
    price: 34.99,
    color: 'from-glow-blue to-glow-cyan',
    emoji: '📱',
  },
];

function OrderSummary({
  items = defaultItems,
  couponApplied,
  discount,
  onApplyCoupon,
  onRemoveCoupon,
  subtotal: externalSubtotal,
  discount: externalDiscount,
  shipping: externalShipping,
  tax: externalTax,
  total: externalTotal,
}) {
  const [couponCode, setCouponCode] = useState('');
  const [couponError, setCouponError] = useState('');
  const [isApplying, setIsApplying] = useState(false);

  const subtotal = externalSubtotal ?? items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const discountValue = externalDiscount ?? discount ?? (couponApplied ? subtotal * 0.15 : 0);
  const shipping = externalShipping ?? 0;
  const tax = externalTax ?? +(subtotal - discountValue) * 0.05;
  const total = externalTotal ?? +(subtotal - discountValue + shipping + tax);

  const handleApplyCoupon = useCallback(() => {
    if (!couponCode.trim()) {
      setCouponError('Please enter a coupon code');
      return;
    }
    setIsApplying(true);
    setCouponError('');
    setTimeout(() => {
      if (couponCode.toUpperCase() === 'GLOW15') {
        onApplyCoupon && onApplyCoupon(couponCode);
        setIsApplying(false);
      } else {
        setCouponError('Invalid coupon code');
        setIsApplying(false);
      }
    }, 1000);
  }, [couponCode, onApplyCoupon]);

  const formatPrice = (val) => `$${val.toFixed(2)}`;

  return (
    <div className="glass rounded-2xl p-6 border border-glow-border">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-glow-indigo to-glow-purple flex items-center justify-center">
          <ShoppingBag className="w-5 h-5 text-white" />
        </div>
        <h2 className="text-lg font-bold text-white">Your Order</h2>
      </div>

      <div className="space-y-4 mb-4">
        <AnimatePresence mode="popLayout">
          {items.map((item) => (
            <motion.div
              key={item.id}
              layout
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="flex items-center gap-3 p-3 rounded-xl bg-glow-darker/50 border border-glow-border/50"
            >
              <div
                className={`w-12 h-12 rounded-lg bg-gradient-to-br ${item.color} flex items-center justify-center text-xl flex-shrink-0`}
              >
                {item.emoji}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-200 truncate">{item.name}</p>
                <p className="text-xs text-gray-500">Qty: {item.quantity}</p>
              </div>
              <span className="text-sm font-semibold text-gray-200">
                ${(item.price * item.quantity).toFixed(2)}
              </span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div className="border-t border-glow-border pt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Subtotal</span>
          <span className="text-gray-300">{formatPrice(subtotal)}</span>
        </div>

        <AnimatePresence>
          {couponApplied && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="flex justify-between text-sm overflow-hidden"
            >
              <span className="text-green-400 flex items-center gap-1">
                <Tag className="w-3 h-3" />
                Discount (GLOW15)
              </span>
              <span className="text-green-400">-{formatPrice(discountValue)}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Shipping</span>
          <span className="text-green-400 font-medium">Free</span>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Tax (5%)</span>
          <span className="text-gray-300">{formatPrice(tax)}</span>
        </div>

        <div className="border-t border-glow-border pt-3 mt-3">
          <div className="flex justify-between items-baseline">
            <span className="text-base font-bold text-white">Total</span>
            <motion.span
              key={total}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
              className="text-xl font-extrabold neon-text"
            >
              {formatPrice(total)}
            </motion.span>
          </div>
        </div>
      </div>

      <div className="mt-5">
        {couponApplied ? (
          <div className="flex items-center justify-between bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-3">
            <div className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-green-400" />
              <span className="text-sm text-green-400">Coupon GLOW15 applied</span>
            </div>
            <button
              onClick={onRemoveCoupon}
              className="text-gray-500 hover:text-red-400 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={couponCode}
                  onChange={(e) => {
                    setCouponCode(e.target.value.toUpperCase());
                    setCouponError('');
                  }}
                  placeholder="Enter coupon"
                  className="w-full px-4 py-2.5 bg-glow-darker border border-glow-border rounded-xl text-sm text-gray-200 placeholder-gray-600 focus:border-glow-indigo focus:outline-none focus:ring-1 focus:ring-glow-indigo/30 transition-all"
                />
              </div>
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={handleApplyCoupon}
                disabled={isApplying}
                className="px-5 py-2.5 bg-gradient-to-r from-glow-indigo to-glow-purple rounded-xl text-sm font-semibold text-white disabled:opacity-50 hover:opacity-90 transition-all whitespace-nowrap"
              >
                {isApplying ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Applying
                  </span>
                ) : (
                  'Apply'
                )}
              </motion.button>
            </div>
            {couponError && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-red-400 text-xs mt-1.5 ml-1"
              >
                {couponError}
              </motion.p>
            )}
            <p className="text-gray-600 text-xs mt-2">Try code: GLOW15</p>
          </div>
        )}
      </div>

      <div className="mt-5 flex items-center gap-2 justify-center py-3 border-t border-glow-border/50">
        <Lock className="w-3.5 h-3.5 text-gray-500" />
        <span className="text-xs text-gray-500">Secure Checkout · Encrypted &amp; Safe</span>
      </div>
    </div>
  );
}

export default OrderSummary;
