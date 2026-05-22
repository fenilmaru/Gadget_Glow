import React, { useState, useCallback, useEffect, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CreditCard, Smartphone, QrCode, Wallet, Phone, Building2,
  Banknote, ChevronRight, ChevronLeft, Shield, Check, RefreshCw,
  MapPin, User, Mail, Lock, Eye, EyeOff, Clock, AlertCircle,
  ArrowRight, ArrowLeft, RotateCw, Circle, DollarSign,
} from 'lucide-react';
import CheckoutProgress from './CheckoutProgress';
import OrderSummary from './OrderSummary';
import SuccessModal from './SuccessModal';

const PAYMENT_METHODS = [
  { id: 'card', label: 'Credit/Debit Card', icon: CreditCard, gradient: 'from-violet-600 to-indigo-600' },
  { id: 'upi', label: 'UPI Payment', icon: Smartphone, gradient: 'from-purple-600 to-pink-600' },
  { id: 'scanpay', label: 'Scan & Pay', icon: QrCode, gradient: 'from-cyan-600 to-blue-600' },
  { id: 'gpay', label: 'Google Pay', icon: Wallet, gradient: 'from-blue-600 to-indigo-600', badge: 'GPay' },
  { id: 'phonepe', label: 'PhonePe', icon: Phone, gradient: 'from-purple-600 to-indigo-600' },
  { id: 'paytm', label: 'Paytm Wallet', icon: Wallet, gradient: 'from-blue-500 to-cyan-600' },
  { id: 'netbanking', label: 'Net Banking', icon: Building2, gradient: 'from-gray-600 to-gray-800' },
  { id: 'cod', label: 'Cash on Delivery', icon: Banknote, gradient: 'from-emerald-600 to-teal-600' },
  { id: 'paypal', label: 'PayPal', icon: CreditCard, gradient: 'from-blue-700 to-indigo-800' },
];

const BANKS = ['Select Bank', 'State Bank of India', 'HDFC Bank', 'ICICI Bank', 'Axis Bank', 'Kotak Mahindra', 'Yes Bank'];
const STATES = [
  'Select State', 'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala',
  'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha',
  'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
  'Uttarakhand', 'West Bengal',
];

const generateOrderNumber = () => {
  const prefix = 'GG';
  const timestamp = Date.now().toString(36).toUpperCase();
  const random = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `${prefix}-${timestamp}-${random}`;
};

function formatCardNumber(value) {
  const digits = value.replace(/\D/g, '').slice(0, 16);
  return digits.replace(/(\d{4})(?=\d)/g, '$1 ');
}

function formatExpiry(value) {
  const digits = value.replace(/\D/g, '').slice(0, 4);
  if (digits.length >= 2) {
    return digits.slice(0, 2) + '/' + digits.slice(2);
  }
  return digits;
}

function CheckoutPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedPayment, setSelectedPayment] = useState('card');
  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    street: '',
    city: '',
    state: '',
    zip: '',
    saveAddress: false,
    cardName: '',
    cardNumber: '',
    cardExpiry: '',
    cardCvv: '',
    upiId: '',
    upiVerified: false,
    bank: '',
    accountHolder: '',
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState('idle');
  const [qrExpired, setQrExpired] = useState(false);
  const [qrTimer, setQrTimer] = useState(120);
  const [qrPaymentStatus, setQrPaymentStatus] = useState(0);
  const [couponApplied, setCouponApplied] = useState(false);
  const [discount, setDiscount] = useState(0);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [orderNumber, setOrderNumber] = useState('');
  const [showCvv, setShowCvv] = useState(false);
  const [verifyingUpi, setVerifyingUpi] = useState(false);
  const [addressErrors, setAddressErrors] = useState({});
  const [cardErrors, setCardErrors] = useState({});

  const qrTimerRef = useRef(null);
  const qrStatusRef = useRef(null);
  const processingRef = useRef(null);

  useEffect(() => {
    return () => {
      if (qrTimerRef.current) clearInterval(qrTimerRef.current);
      if (qrStatusRef.current) clearInterval(qrStatusRef.current);
      if (processingRef.current) clearTimeout(processingRef.current);
    };
  }, []);

  const handleQrTimer = useCallback(() => {
    setQrTimer(120);
    setQrExpired(false);
    setQrPaymentStatus(0);
    if (qrTimerRef.current) clearInterval(qrTimerRef.current);
    if (qrStatusRef.current) clearInterval(qrStatusRef.current);

    qrTimerRef.current = setInterval(() => {
      setQrTimer((prev) => {
        if (prev <= 1) {
          clearInterval(qrTimerRef.current);
          setQrExpired(true);
          setQrPaymentStatus(0);
          if (qrStatusRef.current) clearInterval(qrStatusRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    qrStatusRef.current = setInterval(() => {
      setQrPaymentStatus((prev) => {
        if (prev >= 4) {
          clearInterval(qrStatusRef.current);
          return 4;
        }
        return prev + 1;
      });
    }, 3000);
  }, []);

  useEffect(() => {
    if (selectedPayment === 'scanpay') {
      handleQrTimer();
    }
    return () => {
      if (qrTimerRef.current) clearInterval(qrTimerRef.current);
      if (qrStatusRef.current) clearInterval(qrStatusRef.current);
    };
  }, [selectedPayment, handleQrTimer]);

  const handleInputChange = useCallback((field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (field === 'cardNumber') {
      setCardErrors((prev) => ({ ...prev, cardNumber: '' }));
    }
    if (field === 'cardExpiry') {
      setCardErrors((prev) => ({ ...prev, cardExpiry: '' }));
    }
    if (field === 'cardCvv') {
      setCardErrors((prev) => ({ ...prev, cardCvv: '' }));
    }
  }, []);

  const validateAddress = useCallback(() => {
    const errors = {};
    if (!formData.fullName.trim()) errors.fullName = 'Required';
    if (!formData.phone.trim() || formData.phone.length < 10) errors.phone = 'Valid phone required';
    if (!formData.street.trim()) errors.street = 'Required';
    if (!formData.city.trim()) errors.city = 'Required';
    if (!formData.state || formData.state === 'Select State') errors.state = 'Select a state';
    if (!formData.zip.trim() || formData.zip.length < 5) errors.zip = 'Valid ZIP required';
    setAddressErrors(errors);
    return Object.keys(errors).length === 0;
  }, [formData]);

  const validateCard = useCallback(() => {
    const errors = {};
    if (!formData.cardName.trim()) errors.cardName = 'Required';
    if (formData.cardNumber.replace(/\s/g, '').length < 16) errors.cardNumber = 'Enter valid 16-digit card number';
    if (formData.cardExpiry.length < 5) errors.cardExpiry = 'Enter valid expiry';
    if (formData.cardCvv.length < 3) errors.cardCvv = 'Enter valid CVV';
    setCardErrors(errors);
    return Object.keys(errors).length === 0;
  }, [formData]);

  const handleContinueToPayment = useCallback(() => {
    if (validateAddress()) {
      setCurrentStep(2);
    }
  }, [validateAddress]);

  const handlePlaceOrder = useCallback(() => {
    if (selectedPayment === 'card' && !validateCard()) return;
    if (selectedPayment === 'upi' && (!formData.upiId || !formData.upiVerified)) return;
    if (selectedPayment === 'netbanking' && (!formData.bank || formData.bank === 'Select Bank')) return;

    setIsProcessing(true);
    setPaymentStatus('processing');

    processingRef.current = setTimeout(() => {
      setIsProcessing(false);
      setPaymentStatus('success');
      setOrderNumber(generateOrderNumber());
      setShowSuccessModal(true);
      setCurrentStep(3);
    }, 3000);
  }, [selectedPayment, formData, validateCard]);

  const handleApplyCoupon = useCallback((code) => {
    setCouponApplied(true);
    setDiscount(15);
  }, []);

  const handleRemoveCoupon = useCallback(() => {
    setCouponApplied(false);
    setDiscount(0);
  }, []);

  const handleVerifyUpi = useCallback(() => {
    if (!formData.upiId.includes('@')) return;
    setVerifyingUpi(true);
    setTimeout(() => {
      setVerifyingUpi(false);
      handleInputChange('upiVerified', true);
    }, 1500);
  }, [formData.upiId, handleInputChange]);

  const handleCloseModal = useCallback(() => {
    setShowSuccessModal(false);
    setCurrentStep(1);
    setSelectedPayment('card');
    setFormData({
      fullName: '', phone: '', street: '', city: '', state: '', zip: '',
      saveAddress: false, cardName: '', cardNumber: '', cardExpiry: '', cardCvv: '',
      upiId: '', upiVerified: false, bank: '', accountHolder: '',
    });
    setCouponApplied(false);
    setDiscount(0);
    setQrTimer(120);
    setQrExpired(false);
    setQrPaymentStatus(0);
    setPaymentStatus('idle');
  }, []);

  const subtotal = useMemo(() => 129.99 + 49.99 * 2 + 34.99, []);
  const calculatedDiscount = useMemo(
    () => (couponApplied ? subtotal * 0.15 : 0),
    [couponApplied, subtotal]
  );
  const shipping = 0;
  const tax = useMemo(() => +(subtotal - calculatedDiscount) * 0.05, [subtotal, calculatedDiscount]);
  const total = useMemo(
    () => +(subtotal - calculatedDiscount + shipping + tax),
    [subtotal, calculatedDiscount, shipping, tax]
  );

  const qrStatusSteps = [
    { text: 'Waiting for payment...', color: 'text-yellow-400', dot: 'bg-yellow-400' },
    { text: 'Payment detected...', color: 'text-blue-400', dot: 'bg-blue-400' },
    { text: 'Verifying...', color: 'text-purple-400', dot: 'bg-purple-400' },
    { text: 'Payment successful!', color: 'text-green-400', dot: 'bg-green-400' },
  ];

  const renderAddressForm = () => (
    <motion.div
      initial={{ opacity: 0, x: -30 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 30 }}
      className="glass rounded-2xl p-6 md:p-8 border border-glow-border"
    >
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-glow-indigo to-glow-purple flex items-center justify-center">
          <MapPin className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Shipping Address</h2>
          <p className="text-xs text-gray-500">Where should we deliver your order?</p>
        </div>
      </div>

      <div className="space-y-5">
        <div className="floating-input-group">
          <input
            type="text"
            id="fullName"
            value={formData.fullName}
            onChange={(e) => handleInputChange('fullName', e.target.value)}
            placeholder=" "
            className={addressErrors.fullName ? '!border-red-500' : ''}
          />
          <label htmlFor="fullName">Full Name</label>
          {addressErrors.fullName && (
            <p className="text-red-400 text-xs mt-1">{addressErrors.fullName}</p>
          )}
        </div>

        <div className="floating-input-group">
          <input
            type="tel"
            id="phone"
            value={formData.phone}
            onChange={(e) => {
              const val = e.target.value.replace(/\D/g, '').slice(0, 10);
              handleInputChange('phone', val);
            }}
            placeholder=" "
            className={addressErrors.phone ? '!border-red-500' : ''}
          />
          <label htmlFor="phone">Phone Number</label>
          {addressErrors.phone && (
            <p className="text-red-400 text-xs mt-1">{addressErrors.phone}</p>
          )}
        </div>

        <div className="floating-input-group">
          <input
            type="text"
            id="street"
            value={formData.street}
            onChange={(e) => handleInputChange('street', e.target.value)}
            placeholder=" "
            className={addressErrors.street ? '!border-red-500' : ''}
          />
          <label htmlFor="street">Street Address</label>
          {addressErrors.street && (
            <p className="text-red-400 text-xs mt-1">{addressErrors.street}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="floating-input-group">
            <input
              type="text"
              id="city"
              value={formData.city}
              onChange={(e) => handleInputChange('city', e.target.value)}
              placeholder=" "
              className={addressErrors.city ? '!border-red-500' : ''}
            />
            <label htmlFor="city">City</label>
            {addressErrors.city && (
              <p className="text-red-400 text-xs mt-1">{addressErrors.city}</p>
            )}
          </div>

          <div className="floating-input-group">
            <select
              id="state"
              value={formData.state}
              onChange={(e) => handleInputChange('state', e.target.value)}
              className={addressErrors.state ? '!border-red-500' : ''}
            >
              {STATES.map((s) => (
                <option key={s} value={s === 'Select State' ? '' : s}>
                  {s}
                </option>
              ))}
            </select>
            <label htmlFor="state">State</label>
            {addressErrors.state && (
              <p className="text-red-400 text-xs mt-1">{addressErrors.state}</p>
            )}
          </div>

          <div className="floating-input-group">
            <input
              type="text"
              id="zip"
              value={formData.zip}
              onChange={(e) => {
                const val = e.target.value.replace(/\D/g, '').slice(0, 6);
                handleInputChange('zip', val);
              }}
              placeholder=" "
              className={addressErrors.zip ? '!border-red-500' : ''}
            />
            <label htmlFor="zip">ZIP Code</label>
            {addressErrors.zip && (
              <p className="text-red-400 text-xs mt-1">{addressErrors.zip}</p>
            )}
          </div>
        </div>

        <label className="flex items-center gap-3 cursor-pointer group">
          <div
            className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all ${
              formData.saveAddress
                ? 'border-glow-indigo bg-glow-indigo'
                : 'border-glow-border group-hover:border-glow-indigo/50'
            }`}
            onClick={() => handleInputChange('saveAddress', !formData.saveAddress)}
          >
            {formData.saveAddress && <Check className="w-3.5 h-3.5 text-white" />}
          </div>
          <span className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">
            Save address for next time
          </span>
        </label>

        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          onClick={handleContinueToPayment}
          className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-glow-indigo to-glow-purple text-white font-bold text-lg hover:opacity-90 transition-all neon-glow flex items-center justify-center gap-2"
        >
          Continue to Payment
          <ArrowRight className="w-5 h-5" />
        </motion.button>
      </div>
    </motion.div>
  );

  const renderPaymentMethods = () => (
    <div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
        {PAYMENT_METHODS.map((method) => {
          const Icon = method.icon;
          const isActive = selectedPayment === method.id;

          return (
            <motion.button
              key={method.id}
              whileHover={{ scale: 1.03, y: -2 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => {
                setSelectedPayment(method.id);
                handleInputChange('upiVerified', false);
              }}
              className={`relative p-3 rounded-xl border-2 text-left transition-all ${
                isActive
                  ? 'border-glow-indigo payment-active'
                  : 'border-glow-border bg-glow-card/50 hover:border-glow-border/80'
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="activePayment"
                  className="absolute inset-0 rounded-xl bg-gradient-to-br from-glow-indigo/10 to-glow-purple/10"
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
              <div className="relative z-10 flex flex-col items-center text-center gap-1.5">
                <div
                  className={`w-10 h-10 rounded-lg bg-gradient-to-br ${method.gradient} flex items-center justify-center ${
                    isActive ? 'animate-breathe' : ''
                  }`}
                >
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <span className="text-[11px] font-medium text-gray-300 leading-tight">
                  {method.label}
                </span>
                {method.badge && (
                  <span className="text-[9px] font-bold text-glow-indigo bg-glow-indigo/10 px-1.5 py-0.5 rounded-full">
                    {method.badge}
                  </span>
                )}
              </div>
            </motion.button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={selectedPayment}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.25 }}
        >
          {renderPaymentForm()}
        </motion.div>
      </AnimatePresence>
    </div>
  );

  const renderCardForm = () => (
    <div className="glass rounded-2xl p-6 md:p-8 border border-glow-border">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
          <CreditCard className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Card Details</h2>
          <p className="text-xs text-gray-500">Enter your card information securely</p>
        </div>
      </div>

      <div className="space-y-5">
        <div className="floating-input-group">
          <input
            type="text"
            id="cardName"
            value={formData.cardName}
            onChange={(e) => handleInputChange('cardName', e.target.value)}
            placeholder=" "
            className={cardErrors.cardName ? '!border-red-500' : ''}
          />
          <label htmlFor="cardName">Card Holder Name</label>
          {cardErrors.cardName && <p className="text-red-400 text-xs mt-1">{cardErrors.cardName}</p>}
        </div>

        <div className="floating-input-group">
          <input
            type="text"
            id="cardNumber"
            value={formData.cardNumber}
            onChange={(e) => handleInputChange('cardNumber', formatCardNumber(e.target.value))}
            placeholder=" "
            className={cardErrors.cardNumber ? '!border-red-500' : ''}
            inputMode="numeric"
          />
          <label htmlFor="cardNumber">Card Number</label>
          {cardErrors.cardNumber && <p className="text-red-400 text-xs mt-1">{cardErrors.cardNumber}</p>}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="floating-input-group">
            <input
              type="text"
              id="cardExpiry"
              value={formData.cardExpiry}
              onChange={(e) => handleInputChange('cardExpiry', formatExpiry(e.target.value))}
              placeholder=" "
              className={cardErrors.cardExpiry ? '!border-red-500' : ''}
              inputMode="numeric"
            />
            <label htmlFor="cardExpiry">MM/YY</label>
            {cardErrors.cardExpiry && <p className="text-red-400 text-xs mt-1">{cardErrors.cardExpiry}</p>}
          </div>

          <div className="floating-input-group">
            <div className="relative">
              <input
                type={showCvv ? 'text' : 'password'}
                id="cardCvv"
                value={formData.cardCvv}
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, '').slice(0, 3);
                  handleInputChange('cardCvv', val);
                }}
                placeholder=" "
                className={`pr-10 ${cardErrors.cardCvv ? '!border-red-500' : ''}`}
                inputMode="numeric"
                maxLength={3}
              />
              <button
                type="button"
                onClick={() => setShowCvv(!showCvv)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
              >
                {showCvv ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <label htmlFor="cardCvv">CVV</label>
            {cardErrors.cardCvv && <p className="text-red-400 text-xs mt-1">{cardErrors.cardCvv}</p>}
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          onClick={handlePlaceOrder}
          className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-glow-indigo to-glow-purple text-white font-bold text-lg hover:opacity-90 transition-all neon-glow flex items-center justify-center gap-2"
        >
          <Lock className="w-5 h-5" />
          Pay ${total.toFixed(2)}
        </motion.button>
      </div>
    </div>
  );

  const renderUpiForm = () => (
    <div className="glass rounded-2xl p-6 md:p-8 border border-glow-border">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
          <Smartphone className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">UPI Payment</h2>
          <p className="text-xs text-gray-500">Pay using any UPI app</p>
        </div>
      </div>

      <div className="space-y-5">
        <div className="floating-input-group">
          <input
            type="text"
            id="upiId"
            value={formData.upiId}
            onChange={(e) => {
              handleInputChange('upiId', e.target.value);
              if (formData.upiVerified) handleInputChange('upiVerified', false);
            }}
            placeholder=" "
          />
          <label htmlFor="upiId">UPI ID (e.g., name@upi)</label>
          {!formData.upiId.includes('@') && formData.upiId.length > 0 && (
            <p className="text-gray-500 text-xs mt-1">Include @ symbol (e.g., name@upi)</p>
          )}
        </div>

        {formData.upiVerified ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-3"
          >
            <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
              <Check className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm text-green-400 font-medium">UPI ID Verified</span>
          </motion.div>
        ) : (
          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={handleVerifyUpi}
            disabled={!formData.upiId.includes('@') || verifyingUpi}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold disabled:opacity-40 hover:opacity-90 transition-all flex items-center justify-center gap-2"
          >
            {verifyingUpi ? (
              <>
                <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Verifying...
              </>
            ) : (
              <>
                <Shield className="w-5 h-5" />
                Verify UPI ID
              </>
            )}
          </motion.button>
        )}

        {formData.upiVerified && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={handlePlaceOrder}
            className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-glow-indigo to-glow-purple text-white font-bold text-lg hover:opacity-90 transition-all neon-glow flex items-center justify-center gap-2"
          >
            Pay ${total.toFixed(2)} via UPI
          </motion.button>
        )}
      </div>
    </div>
  );

  const renderQrForm = () => (
    <div className="glass rounded-2xl p-6 md:p-8 border border-glow-border">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-extrabold neon-text mb-1">Scan & Pay</h2>
        <p className="text-sm text-gray-500">Scan any QR code with your preferred app</p>
      </div>

      <div className="qr-grid grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {[
          {
            name: 'Google Pay',
            color: 'from-blue-500 to-indigo-500',
            glowColor: 'neon-glow-blue',
            bg: 'bg-gradient-to-br from-blue-900/30 to-indigo-900/30',
            dots: '#3b82f6',
          },
          {
            name: 'PhonePe',
            color: 'from-purple-500 to-indigo-500',
            glowColor: 'neon-glow-purple',
            bg: 'bg-gradient-to-br from-purple-900/30 to-indigo-900/30',
            dots: '#8b5cf6',
          },
          {
            name: 'Paytm',
            color: 'from-blue-500 to-cyan-500',
            glowColor: 'neon-glow-cyan',
            bg: 'bg-gradient-to-br from-blue-900/30 to-cyan-900/30',
            dots: '#06b6d4',
          },
        ].map((qr) => (
          <motion.div
            key={qr.name}
            whileHover={{ scale: 1.03 }}
            className={`flex flex-col items-center p-5 rounded-2xl ${qr.bg} border border-glow-border/50 ${qr.glowColor} animate-pulse-glow`}
          >
            <div className="qr-placeholder mb-3">
              <div className={`absolute inset-0 rounded-2xl ${qr.bg}`} />
              <div className="relative z-10 grid grid-cols-4 grid-rows-4 gap-1.5 p-4">
                {Array.from({ length: 16 }).map((_, i) => (
                  <div
                    key={i}
                    className="rounded-sm"
                    style={{
                      backgroundColor: Math.random() > 0.4 ? qr.dots : 'transparent',
                      opacity: 0.7 + Math.random() * 0.3,
                      aspectRatio: '1',
                    }}
                  />
                ))}
              </div>
              <div className="qr-scan-line" />
            </div>
            <span className={`text-sm font-bold bg-gradient-to-r ${qr.color} bg-clip-text text-transparent`}>
              {qr.name}
            </span>
            <span className="text-[10px] text-gray-500 mt-1">Scan this QR</span>
          </motion.div>
        ))}
      </div>

      <div className="flex items-center justify-between mb-6 p-4 rounded-xl bg-glow-darker/50 border border-glow-border/50">
        <div className="flex items-center gap-3">
          <Clock className={`w-5 h-5 ${qrExpired ? 'text-red-400' : qrTimer < 10 ? 'text-red-400 animate-pulse' : 'text-gray-400'}`} />
          <div>
            <p className="text-xs text-gray-500">QR expires in</p>
            <p className={`text-lg font-mono font-bold ${qrExpired ? 'text-red-400' : qrTimer < 10 ? 'text-red-400 animate-countdown-pulse' : 'text-gray-200'}`}>
              {qrExpired ? 'Expired' : `00:${qrTimer.toString().padStart(2, '0')}`}
            </p>
          </div>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleQrTimer}
          className="p-2.5 rounded-xl bg-glow-darker border border-glow-border hover:border-glow-indigo/50 transition-all"
        >
          <RefreshCw className="w-5 h-5 text-gray-400 hover:text-glow-indigo transition-colors" />
        </motion.button>
      </div>

      <div className="space-y-3 mb-6">
        {qrStatusSteps.map((step, index) => (
          <motion.div
            key={step.text}
            initial={{ opacity: 0, x: -20 }}
            animate={
              qrPaymentStatus >= index
                ? { opacity: 1, x: 0 }
                : { opacity: 0, x: -20 }
            }
            transition={{ delay: index * 0.15, duration: 0.4 }}
            className={`flex items-center gap-3 p-3 rounded-xl ${
              qrPaymentStatus >= index ? 'bg-glow-darker/50' : ''
            } border border-transparent ${
              qrPaymentStatus >= index ? 'border-glow-border/30' : ''
            }`}
          >
            <div
              className={`w-3 h-3 rounded-full ${step.dot} ${
                qrPaymentStatus === index ? 'animate-pulse' : ''
              }`}
            />
            <span className={`text-sm ${qrPaymentStatus >= index ? step.color : 'text-gray-600'}`}>
              {step.text}
            </span>
          </motion.div>
        ))}
      </div>

      {qrPaymentStatus >= 4 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={() => {
              setOrderNumber(generateOrderNumber());
              setShowSuccessModal(true);
              setCurrentStep(3);
            }}
            className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold text-lg hover:opacity-90 transition-all flex items-center justify-center gap-2"
          >
            <Check className="w-5 h-5" />
            Complete Order
          </motion.button>
        </motion.div>
      )}
    </div>
  );

  const renderNetBankingForm = () => (
    <div className="glass rounded-2xl p-6 md:p-8 border border-glow-border">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-600 to-gray-800 flex items-center justify-center">
          <Building2 className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Net Banking</h2>
          <p className="text-xs text-gray-500">Pay via your bank's internet banking</p>
        </div>
      </div>

      <div className="space-y-5">
        <div className="floating-input-group">
          <select
            id="bank"
            value={formData.bank}
            onChange={(e) => handleInputChange('bank', e.target.value)}
          >
            {BANKS.map((b) => (
              <option key={b} value={b === 'Select Bank' ? '' : b}>
                {b}
              </option>
            ))}
          </select>
          <label htmlFor="bank">Select Bank</label>
        </div>

        <div className="floating-input-group">
          <input
            type="text"
            id="accountHolder"
            value={formData.accountHolder}
            onChange={(e) => handleInputChange('accountHolder', e.target.value)}
            placeholder=" "
          />
          <label htmlFor="accountHolder">Account Holder Name</label>
        </div>

        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          disabled={!formData.bank || formData.bank === 'Select Bank'}
          onClick={() => {
            setIsProcessing(true);
            setTimeout(() => {
              setIsProcessing(false);
              setOrderNumber(generateOrderNumber());
              setShowSuccessModal(true);
              setCurrentStep(3);
            }, 2500);
          }}
          className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-gray-600 to-gray-800 text-white font-bold text-lg hover:opacity-90 transition-all disabled:opacity-40 flex items-center justify-center gap-2 border border-gray-500/30"
        >
          <Shield className="w-5 h-5" />
          Continue to Bank
        </motion.button>
      </div>
    </div>
  );

  const renderRedirectForm = (appName, gradient) => (
    <div className="glass rounded-2xl p-8 border border-glow-border text-center">
      <div className={`w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br ${gradient} flex items-center justify-center animate-breathe`}>
        {appName === 'Google Pay' ? (
          <Wallet className="w-10 h-10 text-white" />
        ) : appName === 'PhonePe' ? (
          <Phone className="w-10 h-10 text-white" />
        ) : appName === 'Paytm' ? (
          <Wallet className="w-10 h-10 text-white" />
        ) : (
          <CreditCard className="w-10 h-10 text-white" />
        )}
      </div>
      <h3 className="text-xl font-bold text-white mb-2">{appName}</h3>
      <p className="text-gray-400 text-sm mb-6">Redirecting to {appName}...</p>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => {
          setIsProcessing(true);
          setTimeout(() => {
            setIsProcessing(false);
            setOrderNumber(generateOrderNumber());
            setShowSuccessModal(true);
            setCurrentStep(3);
          }, 2500);
        }}
        className="px-8 py-3 rounded-xl bg-gradient-to-r from-glow-indigo to-glow-purple text-white font-semibold hover:opacity-90 transition-all neon-glow flex items-center justify-center gap-2 mx-auto"
      >
        <ArrowRight className="w-5 h-5" />
        Redirect to {appName}
      </motion.button>
    </div>
  );

  const renderCodForm = () => (
    <div className="glass rounded-2xl p-6 md:p-8 border border-glow-border">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center">
          <Banknote className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Cash on Delivery</h2>
          <p className="text-xs text-gray-500">Pay when you receive your order</p>
        </div>
      </div>

      <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-5 mb-6 text-center">
        <div className="inline-flex items-center gap-2 bg-emerald-500/20 px-4 py-2 rounded-full mb-3">
          <Banknote className="w-5 h-5 text-emerald-400" />
          <span className="text-emerald-400 font-bold text-lg">Pay on Delivery</span>
        </div>
        <p className="text-gray-400 text-sm">
          No online payment needed. Pay in cash or card when your order arrives.
          <br />A ₹40 processing fee will be added.
        </p>
      </div>

      <motion.button
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        onClick={() => {
          setIsProcessing(true);
          setTimeout(() => {
            setIsProcessing(false);
            setOrderNumber(generateOrderNumber());
            setShowSuccessModal(true);
            setCurrentStep(3);
          }, 2000);
        }}
        className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold text-lg hover:opacity-90 transition-all flex items-center justify-center gap-2"
      >
        Place Order (Pay Later)
      </motion.button>
    </div>
  );

  const renderPaymentForm = () => {
    switch (selectedPayment) {
      case 'card':
        return renderCardForm();
      case 'upi':
        return renderUpiForm();
      case 'scanpay':
        return renderQrForm();
      case 'netbanking':
        return renderNetBankingForm();
      case 'gpay':
        return renderRedirectForm('Google Pay', 'from-blue-600 to-indigo-600');
      case 'phonepe':
        return renderRedirectForm('PhonePe', 'from-purple-600 to-indigo-600');
      case 'paytm':
        return renderRedirectForm('Paytm', 'from-blue-500 to-cyan-600');
      case 'paypal':
        return renderRedirectForm('PayPal', 'from-blue-700 to-indigo-800');
      case 'cod':
        return renderCodForm();
      default:
        return renderCardForm();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-glow-dark via-[#0d0d24] to-glow-darker">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="text-center mb-2">
          <h1 className="text-2xl md:text-3xl font-extrabold neon-text tracking-tight">
            Gadget Glow
          </h1>
          <p className="text-xs text-gray-600 mt-0.5">Premium Futuristic Checkout</p>
        </div>

        <CheckoutProgress currentStep={currentStep} />

        <div className="flex flex-col lg:flex-row gap-6 mt-2">
          {currentStep === 1 && (
            <motion.div
              layout
              className="flex-1 lg:w-3/5"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {renderAddressForm()}
            </motion.div>
          )}

          {currentStep === 2 && (
            <motion.div
              layout
              className="flex-1 lg:w-3/5"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {renderPaymentMethods()}
            </motion.div>
          )}

          {currentStep === 3 && (
            <motion.div
              layout
              className="flex-1 lg:w-3/5"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <div className="glass rounded-2xl p-8 md:p-12 border border-glow-border text-center">
                <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-glow-indigo to-glow-purple flex items-center justify-center animate-breathe">
                  <Check className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-2xl font-extrabold neon-text mb-2">Order Confirmed!</h2>
                <p className="text-gray-400 text-sm mb-2">
                  Your order <span className="text-glow-indigo font-mono font-bold">{orderNumber}</span> has been placed.
                </p>
                <p className="text-gray-500 text-xs mb-6">
                  A confirmation email will be sent shortly.
                </p>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleCloseModal}
                  className="px-8 py-3 rounded-2xl bg-gradient-to-r from-glow-indigo to-glow-purple text-white font-bold hover:opacity-90 transition-all neon-glow inline-flex items-center gap-2"
                >
                  <ArrowLeft className="w-5 h-5" />
                  Back to Shopping
                </motion.button>
              </div>
            </motion.div>
          )}

          <div className="flex-1 lg:w-2/5">
            <div className="lg:sticky lg:top-6 space-y-4">
              {currentStep <= 2 && (
                <OrderSummary
                  couponApplied={couponApplied}
                  discount={calculatedDiscount}
                  onApplyCoupon={handleApplyCoupon}
                  onRemoveCoupon={handleRemoveCoupon}
                />
              )}

              {currentStep === 2 && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setCurrentStep(1)}
                  className="w-full py-3 rounded-xl border border-glow-border text-gray-400 hover:text-white hover:border-glow-indigo/50 transition-all flex items-center justify-center gap-2 text-sm font-medium"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to Address
                </motion.button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Processing Overlay */}
      <AnimatePresence>
        {isProcessing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 flex items-center justify-center bg-black/80 backdrop-blur-xl"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="text-center"
            >
              <div className="processing-spinner mx-auto mb-8" />
              <p className="text-xl font-bold neon-text mb-2">Processing your payment...</p>
              <p className="text-gray-500 text-sm">
                Please wait
                <span className="processing-dots" />
              </p>
              <div className="flex gap-1.5 justify-center mt-4">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.3 }}
                    className="w-2 h-2 rounded-full bg-glow-indigo"
                  />
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Success Modal */}
      <SuccessModal
        show={showSuccessModal}
        orderNumber={orderNumber}
        onClose={handleCloseModal}
      />
    </div>
  );
}

export default CheckoutPage;
