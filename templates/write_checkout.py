import os
os.chdir(r'C:\Gadget_Glow\templates')

html = """{% extends 'base.html' %}
{% load static %}
{% block title %}Checkout - Gadget Glow{% endblock %}
{% block extra_css %}
<style>
:root { --glass-bg: rgba(255,255,255,0.04); --glass-border: rgba(255,255,255,0.08); --glass-shadow: 0 8px 32px rgba(0,0,0,0.3); }
[data-theme="light"] { --glass-bg: rgba(0,0,0,0.03); --glass-border: rgba(0,0,0,0.08); --glass-shadow: 0 8px 32px rgba(0,0,0,0.06); }
.checkout-container { max-width: 1320px; margin: 0 auto; }
.progress-steps { display: flex; justify-content: center; gap: 0; margin-bottom: 2.5rem; position: relative; }
.progress-steps::before { content: ''; position: absolute; top: 24px; left: 10%; right: 10%; height: 2px; background: var(--border); z-index: 0; }
.progress-steps .step { display: flex; flex-direction: column; align-items: center; gap: 8px; position: relative; z-index: 1; flex: 1; }
.progress-steps .step .circle { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem; background: var(--bg-card); border: 2px solid var(--border); color: var(--text-muted); transition: all 0.4s cubic-bezier(0.4,0,0.2,1); }
.progress-steps .step.active .circle { border-color: var(--primary-light); background: rgba(99,102,241,0.15); color: var(--primary-light); box-shadow: 0 0 20px rgba(99,102,241,0.3); }
.progress-steps .step.done .circle { border-color: var(--success); background: var(--success); color: #fff; box-shadow: 0 0 20px rgba(34,197,94,0.3); }
.progress-steps .step .label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); }
.progress-steps .step.active .label { color: var(--primary-light); }
.progress-steps .step.done .label { color: var(--success); }
.glass-card { background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--glass-border); border-radius: 20px; padding: 1.75rem; box-shadow: var(--glass-shadow); transition: all 0.3s ease; }
.glass-card:hover { border-color: rgba(99,102,241,0.2); box-shadow: 0 8px 40px rgba(99,102,241,0.08); }
.payment-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; }
.payment-option-card { position: relative; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 6px; border-radius: 16px; background: var(--glass-bg); border: 2px solid var(--glass-border); cursor: pointer; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); text-align: center; user-select: none; }
.payment-option-card:hover { border-color: rgba(99,102,241,0.3); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(99,102,241,0.1); }
.payment-option-card.active { border-color: var(--primary-light); background: rgba(99,102,241,0.08); box-shadow: 0 0 30px rgba(99,102,241,0.15), inset 0 0 20px rgba(99,102,241,0.05); }
.payment-option-card .icon-wrap { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; }
.payment-option-card input[type="radio"] { position: absolute; opacity: 0; pointer-events: none; }
.payment-option-card .pmt-label { font-size: 0.65rem; font-weight: 600; line-height: 1.2; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; }
.payment-option-card.active .pmt-label { color: var(--primary-light); }
.payment-option-card .active-dot { position: absolute; top: 6px; right: 6px; width: 8px; height: 8px; border-radius: 50%; background: var(--primary-light); opacity: 0; transform: scale(0); transition: all 0.3s; }
.payment-option-card.active .active-dot { opacity: 1; transform: scale(1); }
.payment-option-card .pulse-ring { position: absolute; inset: -4px; border-radius: 18px; border: 2px solid var(--primary-light); opacity: 0; animation: pulseRing 2s ease-in-out infinite; pointer-events: none; }
.payment-option-card.active .pulse-ring { opacity: 1; }
@keyframes pulseRing { 0% { opacity: 0.6; transform: scale(1); } 100% { opacity: 0; transform: scale(1.06); } }
.payment-form-panel { display: none; animation: slideUp 0.4s cubic-bezier(0.4,0,0.2,1); }
.payment-form-panel.active { display: block; }
@keyframes slideUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.futuristic-input { background: rgba(255,255,255,0.04) !important; border: 1px solid var(--glass-border) !important; border-radius: 12px !important; color: inherit !important; padding: 12px 16px !important; font-size: 0.95rem !important; transition: all 0.3s !important; }
.futuristic-input:focus { border-color: var(--primary-light) !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important; outline: none !important; }
.futuristic-input::placeholder { color: var(--text-muted); opacity: 0.5; }
.futuristic-label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 6px; display: block; }
.qr-container { position: relative; display: inline-flex; flex-direction: column; align-items: center; gap: 12px; }
.qr-box { position: relative; width: 200px; height: 200px; border-radius: 20px; overflow: hidden; background: #fff; padding: 12px; box-shadow: 0 0 30px rgba(99,102,241,0.2); }
.qr-box img { width: 100%; height: 100%; object-fit: contain; }
.qr-glow { position: absolute; inset: -4px; border-radius: 22px; border: 2px solid transparent; background: linear-gradient(135deg, var(--primary-light), #a855f7, var(--primary-light)) border-box; -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0); mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0); -webkit-mask-composite: xor; mask-composite: exclude; animation: qrGlow 2s ease-in-out infinite; pointer-events: none; }
@keyframes qrGlow { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
.qr-scan-line { position: absolute; top: 0; left: 12px; right: 12px; height: 2px; background: linear-gradient(90deg, transparent, var(--primary-light), transparent); animation: scanLine 2.5s ease-in-out infinite; border-radius: 2px; pointer-events: none; }
@keyframes scanLine { 0% { top: 12px; } 50% { top: calc(100% - 12px); } 100% { top: 12px; } }
.qr-timer { font-size: 0.85rem; font-weight: 700; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
@keyframes spin { to { transform: rotate(360deg); } }
.qr-vendors { display: flex; gap: 12px; margin-top: 8px; flex-wrap: wrap; justify-content: center; }
.qr-vendor-badge { display: flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; border: 1px solid var(--glass-border); background: var(--glass-bg); }
.payment-status { display: none; margin-top: 16px; padding: 16px 20px; border-radius: 16px; background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); }
.payment-status.active { display: flex; align-items: center; gap: 14px; animation: slideUp 0.4s ease; }
.payment-status .status-icon { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; }
.payment-status .status-text { font-weight: 600; font-size: 0.9rem; }
.payment-status .status-sub { font-size: 0.75rem; color: var(--text-muted); }
.status-waiting .status-icon { background: rgba(251,191,36,0.15); color: #f59e0b; }
.status-detected .status-icon { background: rgba(99,102,241,0.15); color: var(--primary-light); }
.status-success .status-icon { background: rgba(34,197,94,0.15); color: var(--success); }
.summary-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--glass-border); }
.summary-item:last-child { border-bottom: none; }
.summary-item .thumb { width: 48px; height: 48px; border-radius: 10px; object-fit: cover; background: var(--glass-bg); flex-shrink: 0; }
.success-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(8px); z-index: 9999; display: none; align-items: center; justify-content: center; padding: 20px; }
.success-overlay.active { display: flex; }
.success-modal { background: var(--bg-card); border-radius: 24px; padding: 2.5rem; max-width: 440px; width: 100%; text-align: center; border: 1px solid var(--glass-border); box-shadow: 0 32px 64px rgba(0,0,0,0.4); animation: modalIn 0.5s cubic-bezier(0.4,0,0.2,1); }
@keyframes modalIn { from { opacity: 0; transform: scale(0.9) translateY(20px); } to { opacity: 1; transform: scale(1) translateY(0); } }
.checkmark-anim { width: 80px; height: 80px; border-radius: 50%; background: rgba(34,197,94,0.12); display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; position: relative; }
.checkmark-anim .check-icon { font-size: 2.5rem; color: var(--success); animation: checkBounce 0.6s cubic-bezier(0.4,0,0.2,1); }
@keyframes checkBounce { 0% { transform: scale(0); } 50% { transform: scale(1.3); } 100% { transform: scale(1); } }
.checkmark-anim .check-ring { position: absolute; inset: -8px; border-radius: 50%; border: 2px solid var(--success); animation: ringExpand 1.5s ease-out infinite; }
@keyframes ringExpand { 0% { opacity: 0.6; transform: scale(1); } 100% { opacity: 0; transform: scale(1.2); } }
.success-modal .coupon-display { background: rgba(99,102,241,0.08); border: 2px dashed var(--primary-light); border-radius: 16px; padding: 16px; margin: 16px 0; }
.success-modal .coupon-display code { font-size: 1.3rem; font-weight: 800; letter-spacing: 2px; color: var(--primary-light); }
.loading-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); z-index: 9998; display: none; align-items: center; justify-content: center; }
.loading-overlay.active { display: flex; }
.loading-card { background: var(--bg-card); border-radius: 20px; padding: 2.5rem; text-align: center; border: 1px solid var(--glass-border); }
.loading-spinner { width: 48px; height: 48px; border: 3px solid var(--glass-border); border-top-color: var(--primary-light); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@media (max-width: 991.98px) {
  .mobile-sticky-bar { display: flex; position: fixed; bottom: 0; left: 0; right: 0; background: var(--bg-card); border-top: 1px solid var(--glass-border); padding: 12px 16px; z-index: 1050; gap: 12px; align-items: center; backdrop-filter: blur(16px); }
  .mobile-sticky-bar .msb-total { font-size: 1.1rem; font-weight: 800; }
  .mobile-sticky-bar .msb-total small { font-size: 0.7rem; font-weight: 400; color: var(--text-muted); display: block; }
  body { padding-bottom: 76px; }
}
.mobile-sticky-bar { display: none; }
.btn-neon { position: relative; background: linear-gradient(135deg, var(--primary-light), #7c3aed); border: none; border-radius: 14px; padding: 14px 32px; font-weight: 700; font-size: 1rem; color: #fff; overflow: hidden; transition: all 0.3s; z-index: 1; }
.btn-neon::before { content: ''; position: absolute; inset: 0; border-radius: 14px; background: linear-gradient(135deg, #7c3aed, var(--primary-light)); opacity: 0; transition: opacity 0.3s; z-index: -1; }
.btn-neon:hover::before { opacity: 1; }
.btn-neon:hover { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(99,102,241,0.35); }
.btn-neon:active { transform: translateY(0); }
.btn-neon-sm { padding: 10px 20px; font-size: 0.85rem; border-radius: 10px; }
.secure-badges { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 16px; }
.secure-badge { display: flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 20px; font-size: 0.7rem; font-weight: 500; background: var(--glass-bg); border: 1px solid var(--glass-border); color: var(--text-muted); }
.price-line { display: flex; justify-content: space-between; padding: 6px 0; font-size: 0.9rem; }
.price-line.total { padding: 12px 0 0; margin-top: 8px; border-top: 1px solid var(--glass-border); font-size: 1.1rem; font-weight: 800; }
.price-line.total .amount { color: var(--primary-light); font-size: 1.3rem; }
</style>
{% endblock %}
{% block content %}
<div class="checkout-container container py-4">
{% if generated_coupon %}
<div class="success-overlay active">
  <div class="success-modal">
    <div class="checkmark-anim"><i class="bi bi-check-lg check-icon"></i><div class="check-ring"></div></div>
    <h3 class="fw-bold mb-2">Order Confirmed!</h3>
    <p class="text-muted mb-1">Order #<strong>{{ order.id }}</strong> placed successfully.</p>
    <p class="text-muted mb-3 small">Track it from your <a href="{% url 'orders_page' %}" style="color:var(--primary-light);">orders page</a>.</p>
    <div class="coupon-display">
      <i class="bi bi-gift fs-4" style="color:var(--primary-light);"></i>
      <p class="fw-bold mb-1">You Earned a Reward Coupon!</p>
      <p class="small text-muted mb-2">15% off featured accessories</p>
      <code>{{ generated_coupon }}</code>
      <div class="mt-2"><button class="btn btn-neon btn-neon-sm" onclick="navigator.clipboard.writeText('{{ generated_coupon }}').then(()=>{this.textContent='Copied!'})"><i class="bi bi-clipboard me-1"></i>Copy Code</button></div>
    </div>
    <div class="d-flex gap-2 justify-content-center mt-3">
      <a href="{% url 'home' %}" class="btn btn-outline-light btn-sm"><i class="bi bi-house me-1"></i>Home</a>
      <a href="{% url 'products_page' %}?featured=true" class="btn btn-neon btn-neon-sm"><i class="bi bi-lightning me-1"></i>Shop Featured</a>
    </div>
  </div>
</div>
{% elif cart_items %}
"""
with open('checkout.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Part 1 written, length:', len(html))
