import os
os.chdir(r'C:\Gadget_Glow\templates')
html = r"""
<div class="progress-steps">
    <div class="step done"><div class="circle"><i class="bi bi-check-lg"></i></div><span class="label">Cart</span></div>
    <div class="step active"><div class="circle">2</div><span class="label">Checkout</span></div>
    <div class="step"><div class="circle">3</div><span class="label">Payment</span></div>
    <div class="step"><div class="circle">4</div><span class="label">Confirm</span></div>
</div>
<div class="row g-4">
<div class="col-lg-7 col-xl-8">
<form method="post" id="checkoutForm">{% csrf_token %}
<div class="glass-card mb-4">
  <h5 class="fw-bold mb-3"><i class="bi bi-geo-alt me-2" style="color:var(--primary-light);"></i>Shipping Address</h5>
  <textarea name="shipping_address" class="form-control futuristic-input" rows="2" required placeholder="Street, city, state, ZIP code">{{ request.user.profile.address|default:'' }}</textarea>
  <div class="form-check mt-2"><input class="form-check-input" type="checkbox" id="saveAddr" checked><label class="form-check-label small" for="saveAddr">Save this address</label></div>
</div>
<div class="glass-card mb-4">
  <h5 class="fw-bold mb-3"><i class="bi bi-credit-card me-2" style="color:var(--primary-light);"></i>Payment Method</h5>
  <div class="payment-grid" id="paymentGrid">
    <label class="payment-option-card active" data-method="credit_card">
      <input type="radio" name="payment_method" value="credit_card" checked><div class="active-dot"></div><div class="pulse-ring"></div>
      <div class="icon-wrap" style="color:#6366f1;"><i class="bi bi-credit-card-2-front"></i></div><span class="pmt-label">Card</span>
    </label>
    <label class="payment-option-card" data-method="upi">
      <input type="radio" name="payment_method" value="upi"><div class="active-dot"></div><div class="pulse-ring"></div>
      <div class="icon-wrap" style="color:#22c55e;"><i class="bi bi-phone"></i></div><span class="pmt-label">UPI</span>
    </label>
    <label class="payment-option-card" data-method="scanpay">
      <input type="radio" name="payment_method" value="scanpay"><div class="active-dot"></div><div class="pulse-ring"></div>
      <div class="icon-wrap" style="color:#a855f7;"><i class="bi bi-qr-code"></i></div><span class="pmt-label">Scan &amp; Pay</span>
    </label>
    <label class="payment-option-card" data-method="gpay">
      <input type="radio" name="payment_method" value="gpay"><div class="active-dot"></div><div class="pulse-ring"></div>
      <div class="icon-wrap" style="color:#1a73e8;"><i class="bi bi-google"></i></div><span class="pmt-label">GPay</span>
    </label>
    <label class="payment-option-card" data-method="phonepe">
      <input type="radio" name="payment_method" value="phonepe"><div class="active-dot"></div><div class="pulse-ring"></div>
      <div class="icon-wrap" style="color:#5f259f;"><i class="bi bi-wallet2"></i></div><span class="pmt-label">PhonePe</span>
    </label>
    <label class="payment-option-card" data-method="paytm">
      <input type="radio" name="payment_method" value="paytm"><div class="active-dot"></div><div class="pulse-ring"></div>
      <div class="icon-wrap" style="color:#00baf2;"><i class="bi bi-currency-rupee"></i></div><span class="pmt-label">Paytm</span>
    </label>
    <label class="payment-option-card" data-method="netbanking">
      <input type="radio" name="payment_method" value="netbanking"><div class="active-dot"></div><div class="pulse-ring"></div>
      <div class="icon-wrap" style="color:#f59e0b;"><i class="bi bi-bank"></i></div><span class="pmt-label">Net Banking</span>
    </label>
    <label class="payment-option-card" data-method="cod">
      <input type="radio" name="payment_method" value="cod"><div class="active-dot"></div><div class="pulse-ring"></div>
      <div class="icon-wrap" style="color:#10b981;"><i class="bi bi-cash-stack"></i></div><span class="pmt-label">COD</span>
    </label>
    <label class="payment-option-card" data-method="paypal">
      <input type="radio" name="payment_method" value="paypal"><div class="active-dot"></div><div class="pulse-ring"></div>
      <div class="icon-wrap" style="color:#003087;"><i class="bi bi-paypal"></i></div><span class="pmt-label">PayPal</span>
    </label>
  </div>
"""
with open('checkout.html', 'a', encoding='utf-8') as f:
    f.write(html)
print('Part 2a appended')
