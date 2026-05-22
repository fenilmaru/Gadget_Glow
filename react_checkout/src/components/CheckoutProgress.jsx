import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check } from 'lucide-react';

const steps = [
  { id: 1, label: 'Address' },
  { id: 2, label: 'Payment' },
  { id: 3, label: 'Confirmation' },
];

function CheckoutProgress({ currentStep }) {
  return (
    <div className="w-full py-6 px-4">
      <div className="max-w-2xl mx-auto flex items-center justify-between relative">
        {steps.map((step, index) => {
          const isCompleted = currentStep > step.id;
          const isCurrent = currentStep === step.id;
          const isLast = index === steps.length - 1;

          return (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center relative z-10">
                <motion.div
                  initial={false}
                  animate={{
                    scale: isCurrent ? 1.15 : 1,
                    backgroundColor: isCompleted ? '#6366f1' : isCurrent ? '#111122' : '#1e1e3a',
                  }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                  className={`w-11 h-11 rounded-full flex items-center justify-center border-2 relative ${
                    isCompleted
                      ? 'border-glow-indigo bg-glow-indigo'
                      : isCurrent
                      ? 'border-glow-indigo bg-glow-card shadow-lg neon-glow'
                      : 'border-glow-border bg-glow-card'
                  }`}
                >
                  {isCompleted ? (
                    <motion.div
                      initial={{ scale: 0, rotate: -180 }}
                      animate={{ scale: 1, rotate: 0 }}
                      transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                    >
                      <Check className="w-5 h-5 text-white" />
                    </motion.div>
                  ) : (
                    <span
                      className={`text-sm font-bold ${
                        isCurrent ? 'text-glow-indigo' : 'text-gray-500'
                      }`}
                    >
                      {step.id}
                    </span>
                  )}
                </motion.div>
                <motion.span
                  initial={false}
                  animate={{
                    color: isCurrent || isCompleted ? '#6366f1' : '#6b7280',
                    fontWeight: isCurrent ? 600 : 400,
                  }}
                  className="text-xs mt-2 whitespace-nowrap"
                >
                  {step.label}
                </motion.span>
                {isCurrent && (
                  <motion.div
                    layoutId="step-indicator"
                    className="w-1 h-1 rounded-full bg-glow-indigo mt-1"
                    transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                  />
                )}
              </div>
              {!isLast && (
                <div className="flex-1 mx-3 relative">
                  <div className="h-0.5 bg-glow-border rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: '0%' }}
                      animate={{
                        width: isCompleted ? '100%' : isCurrent ? '0%' : '0%',
                      }}
                      transition={{ duration: 0.5, ease: 'easeInOut' }}
                      className="h-full rounded-full bg-gradient-to-r from-glow-indigo to-glow-purple"
                    />
                  </div>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

export default CheckoutProgress;
