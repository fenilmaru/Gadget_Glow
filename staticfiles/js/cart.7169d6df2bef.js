(function() {
    'use strict';

    /* ─── AJAX Add to Cart ─── */
    document.querySelectorAll('.btn-add-cart-ajax').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var productId = this.getAttribute('data-product-id');
            var quantity = this.getAttribute('data-quantity') || 1;

            var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            var token = csrfToken ? csrfToken.value : '';
            if (!token) {
                var match = document.cookie.match(new RegExp('(^| )csrftoken=([^;]+)'));
                token = match ? decodeURIComponent(match[2]) : '';
            }

            var btnEl = this;
            var originalHtml = btnEl.innerHTML;
            btnEl.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            btnEl.disabled = true;

            fetch('/api/v1/cart/add_item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': token
                },
                body: JSON.stringify({
                    product_id: parseInt(productId),
                    quantity: parseInt(quantity)
                })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                btnEl.innerHTML = '<i class="bi bi-check-lg"></i> Added';
                btnEl.style.background = 'var(--success)';
                if (window.showToast) {
                    window.showToast('Added to cart!', 'success');
                }
                var countEl = document.getElementById('cartCount');
                if (countEl && data.total_items !== undefined) {
                    countEl.textContent = data.total_items;
                    countEl.style.display = data.total_items > 0 ? '' : 'none';
                }
                updateCartBadge(data);
                setTimeout(function() {
                    btnEl.innerHTML = originalHtml;
                    btnEl.disabled = false;
                    btnEl.style.background = '';
                }, 2000);
            })
            .catch(function() {
                btnEl.innerHTML = originalHtml;
                btnEl.disabled = false;
                if (window.showToast) {
                    window.showToast('Error adding to cart', 'error');
                }
            });
        });
    });

    /* ─── Update Quantity ─── */
    document.querySelectorAll('.cart-qty-select').forEach(function(select) {
        select.addEventListener('change', function() {
            var itemId = this.getAttribute('data-item-id');
            var qty = this.value;
            var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            var token = csrfToken ? csrfToken.value : '';

            fetch('/api/v1/cart/update_quantity/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': token
                },
                body: JSON.stringify({
                    item_id: parseInt(itemId),
                    quantity: parseInt(qty)
                })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                updateCartUI(data);
                if (window.showToast) {
                    window.showToast('Cart updated', 'success');
                }
            })
            .catch(function() {
                if (window.showToast) {
                    window.showToast('Error updating cart', 'error');
                }
            });
        });
    });

    /* ─── Remove Item ─── */
    document.querySelectorAll('.cart-remove-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var itemId = this.getAttribute('data-item-id');
            var row = this.closest('.cart-item-row');
            var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            var token = csrfToken ? csrfToken.value : '';

            if (row) row.style.opacity = '0.3';

            fetch('/api/v1/cart/remove_item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': token
                },
                body: JSON.stringify({
                    item_id: parseInt(itemId)
                })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (row) row.remove();
                updateCartUI(data);
                if (window.showToast) {
                    window.showToast('Item removed from cart', 'info');
                }
            })
            .catch(function() {
                if (row) row.style.opacity = '1';
                if (window.showToast) {
                    window.showToast('Error removing item', 'error');
                }
            });
        });
    });

    /* ─── Clear Cart ─── */
    var clearCartBtn = document.getElementById('clearCartBtn');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (!confirm('Clear your entire cart?')) return;
            var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            var token = csrfToken ? csrfToken.value : '';

            fetch('/api/v1/cart/clear/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': token
                }
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                location.reload();
            })
            .catch(function() {
                if (window.showToast) {
                    window.showToast('Error clearing cart', 'error');
                }
            });
        });
    }

    function updateCartBadge(data) {
        var badge = document.getElementById('cartCount');
        if (!badge) return;
        var count = data.total_items || data.item_count || 0;
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = '';
        } else {
            badge.style.display = 'none';
        }
        var mobBadge = document.querySelector('.mob-nav-item .mob-badge');
        if (mobBadge) {
            if (count > 0) {
                mobBadge.textContent = count;
                mobBadge.style.display = '';
            } else {
                mobBadge.style.display = 'none';
            }
        }
    }

    function updateCartUI(data) {
        var summaryTotal = document.getElementById('cartSummaryTotal');
        var summaryCount = document.getElementById('cartSummaryCount');
        if (summaryTotal && data.total_price !== undefined) {
            summaryTotal.textContent = '$' + parseFloat(data.total_price).toFixed(2);
        }
        if (summaryCount && data.total_items !== undefined) {
            summaryCount.textContent = data.total_items + ' item' + (data.total_items !== 1 ? 's' : '');
        }
        if (typeof data.total_items !== 'undefined') {
            var badge = document.getElementById('cartCount');
            if (badge) {
                badge.textContent = data.total_items;
                badge.style.display = data.total_items > 0 ? '' : 'none';
            }
        }
        if (data.items && data.items.length === 0) {
            var emptyCart = document.getElementById('emptyCart');
            var cartContent = document.getElementById('cartContent');
            if (emptyCart && cartContent) {
                cartContent.style.display = 'none';
                emptyCart.style.display = 'block';
            }
        }
    }

})();
