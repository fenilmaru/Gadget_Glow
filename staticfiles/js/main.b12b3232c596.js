(function() {
    'use strict';

    function getCSRFToken() {
        var el = document.querySelector('[name=csrfmiddlewaretoken]');
        if (el) return el.value;
        var match = document.cookie.match(new RegExp('(^| )csrftoken=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : '';
    }

    /* ─── Intersection Observer for animations ─── */
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.fade-in-up').forEach(function(el) {
        observer.observe(el);
    });

    /* ─── Toast system ─── */
    window.showToast = function(msg, type) {
        type = type || 'info';
        var container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        var toast = document.createElement('div');
        toast.className = 'custom-toast ' + type;
        var iconMap = { success: 'check-circle-fill', error: 'exclamation-circle-fill', info: 'info-circle-fill' };
        toast.innerHTML = '<div class="d-flex align-items-center gap-2"><i class="bi bi-' + (iconMap[type] || 'info-circle-fill') + '"></i><span>' + msg + '</span></div>';
        container.appendChild(toast);
        setTimeout(function() { toast.style.opacity = '0'; toast.style.transform = 'translateX(120%)'; toast.style.transition = 'all 0.3s ease'; setTimeout(function() { toast.remove(); }, 300); }, 3500);
    };

    /* ─── Wishlist AJAX ─── */
    function toggleWishlist(productId, btn) {
        var token = getCSRFToken();
        var icon = btn.querySelector('i');
        var isFilled = icon && icon.classList.contains('bi-heart-fill');
        var action = isFilled ? 'remove' : 'add';

        fetch('/api/v1/wishlist/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
            body: JSON.stringify({ product_id: parseInt(productId), action: action })
        })
        .then(function(r) {
            if (r.status === 401 || r.status === 403) { window.showToast('Please login to use wishlist', 'error'); return null; }
            return r.json();
        })
        .then(function(data) {
            if (!data || !data.success) return;
            if (isFilled) {
                if (icon) { icon.className = 'bi bi-heart'; }
                btn.classList.remove('active');
                window.showToast('Removed from wishlist', 'info');
            } else {
                if (icon) { icon.className = 'bi bi-heart-fill'; }
                btn.classList.add('active');
                window.showToast('Added to wishlist!', 'success');
            }
            var detailBtn = document.querySelector('.wishlist-btn-detail[data-product-id="' + productId + '"]');
            if (detailBtn) {
                var di = detailBtn.querySelector('i');
                if (di) {
                    di.className = isFilled ? 'bi bi-heart me-1' : 'bi bi-heart-fill me-1';
                }
                detailBtn.innerHTML = (isFilled ? '<i class="bi bi-heart me-1"></i>Add to' : '<i class="bi bi-heart-fill me-1"></i>Remove from') + ' Wishlist';
            }
        })
        .catch(function() {
            window.showToast('Error updating wishlist', 'error');
        });
    }

    document.querySelectorAll('.wishlist-btn, .wishlist-btn-detail').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var pid = this.getAttribute('data-product-id');
            if (!pid) {
                var form = this.closest('form');
                if (form) { form.submit(); return; }
                return;
            }
            toggleWishlist(pid, this);
        });
    });

    /* ─── Image error fallback ─── */
    document.querySelectorAll('img').forEach(function(img) {
        img.addEventListener('error', function() {
            if (!this.hasAttribute('data-fallback')) {
                this.setAttribute('data-fallback', '1');
                this.src = 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop';
            }
        });
    });

    /* ─── Product image zoom ─── */
    var mainImageContainer = document.getElementById('mainImageContainer');
    if (mainImageContainer) {
        mainImageContainer.addEventListener('mousemove', function(e) {
            var rect = this.getBoundingClientRect();
            var x = ((e.clientX - rect.left) / rect.width) * 100;
            var y = ((e.clientY - rect.top) / rect.height) * 100;
            var img = this.querySelector('img');
            if (img) {
                img.style.transformOrigin = x + '% ' + y + '%';
                img.style.transform = 'scale(1.8)';
            }
        });
        mainImageContainer.addEventListener('mouseleave', function() {
            var img = this.querySelector('img');
            if (img) {
                img.style.transformOrigin = 'center center';
                img.style.transform = 'scale(1)';
            }
        });
    }

    window.changeImage = function(thumb, url) {
        document.querySelectorAll('.thumb').forEach(function(t) { t.classList.remove('active'); });
        thumb.classList.add('active');
        var mainImg = document.getElementById('mainProductImage');
        if (mainImg) {
            mainImg.src = url;
            mainImg.style.transform = 'scale(1)';
        }
    };

    /* ─── Quantity buttons ─── */
    document.querySelectorAll('.qty-minus, .qty-plus').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var input = this.parentElement.querySelector('input[type="number"]');
            if (!input) return;
            var min = parseInt(input.getAttribute('min') || 1);
            var max = parseInt(input.getAttribute('max') || 99);
            var val = parseInt(input.value) || 1;
            if (this.classList.contains('qty-minus') && val > min) { val--; }
            if (this.classList.contains('qty-plus') && val < max) { val++; }
            input.value = val;
            input.dispatchEvent(new Event('change'));
        });
    });

    function showSkeleton(container, count) {
        if (!container) return;
        var html = '';
        for (var i = 0; i < (count || 4); i++) {
            html += '<div class="col-6 col-md-4 col-lg-3"><div class="card" style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;">' +
                '<div class="skeleton skeleton-img"></div>' +
                '<div class="p-3"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text-sm"></div></div></div></div>';
        }
        container.innerHTML = html;
    }

    /* ─── Navbar shadow ─── */
    var navbar = document.querySelector('.navbar-gadget');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.3)';
            } else {
                navbar.style.boxShadow = 'none';
            }
        });
    }

    /* ─── Live Search ─── */
    var searchInput = document.getElementById('liveSearch');
    if (searchInput) {
        var searchTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimer);
            var query = this.value.trim();
            var dropdown = document.getElementById('searchResults');
            if (!dropdown) return;
            if (query.length < 2) {
                dropdown.classList.remove('open');
                dropdown.innerHTML = '';
                return;
            }
            searchTimer = setTimeout(function() {
                fetch('/api/v1/products/search/?q=' + encodeURIComponent(query))
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        var results = data.results || [];
                        dropdown.innerHTML = '';
                        if (results.length === 0) {
                            dropdown.innerHTML = '<div class="p-3 text-center text-muted small">No products found</div>';
                            dropdown.classList.add('open');
                            return;
                        }
                        results.forEach(function(p) {
                            var item = document.createElement('a');
                            item.className = 'search-result-item';
                            item.href = '/products/' + p.slug + '/';
                            item.innerHTML = '<img src="' + (p.display_image || 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop') + '" alt="' + p.name + '" onerror="this.src=\'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop\'">' +
                                '<div class="info"><div class="name">' + p.name + '</div><div class="price">$' + p.price + '</div></div>';
                            dropdown.appendChild(item);
                        });
                        dropdown.classList.add('open');
                    })
                    .catch(function() {
                        dropdown.innerHTML = '<div class="p-3 text-center text-muted small">Search error</div>';
                        dropdown.classList.add('open');
                    });
            }, 300);
        });
        document.addEventListener('click', function(e) {
            var dropdown = document.getElementById('searchResults');
            if (dropdown && !e.target.closest('.search-bar')) {
                dropdown.classList.remove('open');
            }
        });
    }

    /* ─── Grid/List View Toggle ─── */
    var gridView = document.getElementById('gridView');
    var listView = document.getElementById('listView');
    var productGrid = document.getElementById('productGrid');
    if (gridView && listView && productGrid) {
        gridView.addEventListener('click', function() {
            gridView.classList.add('active'); listView.classList.remove('active');
            productGrid.className = 'row g-3';
            document.querySelectorAll('.product-item').forEach(function(el) {
                el.className = 'col-6 col-md-4 col-lg-4 product-item';
                var card = el.querySelector('.product-card');
                if (card) { card.style.display = ''; card.style.flexDirection = ''; }
            });
        });
        listView.addEventListener('click', function() {
            listView.classList.add('active'); gridView.classList.remove('active');
            productGrid.className = 'row g-3';
            document.querySelectorAll('.product-item').forEach(function(el) {
                el.className = 'col-12 product-item';
                var card = el.querySelector('.product-card');
                if (card) { card.style.display = 'flex'; card.style.flexDirection = 'row'; }
                var imgContainer = el.querySelector('.card-img-container');
                if (imgContainer) { imgContainer.style.minWidth = '200px'; imgContainer.style.paddingTop = '200px'; }
            });
        });
    }

    /* ─── Countdown Timer ─── */
    function initCountdown(elementId, hours, minutes) {
        var el = document.getElementById(elementId);
        if (!el) return;
        var totalSeconds = (hours || 0) * 3600 + (minutes || 0) * 60;
        if (totalSeconds <= 0) totalSeconds = 86400;
        setInterval(function() {
            var h = Math.floor(totalSeconds / 3600);
            var m = Math.floor((totalSeconds % 3600) / 60);
            var s = totalSeconds % 60;
            var hrs = document.getElementById('countdown-hours');
            var mins = document.getElementById('countdown-minutes');
            var secs = document.getElementById('countdown-seconds');
            if (hrs) hrs.textContent = String(h).padStart(2, '0');
            if (mins) mins.textContent = String(m).padStart(2, '0');
            if (secs) secs.textContent = String(s).padStart(2, '0');
            totalSeconds = totalSeconds <= 0 ? 0 : totalSeconds - 1;
        }, 1000);
    }
    initCountdown('countdown', 12, 0);

    /* ─── Hero Slider ─── */
    var heroSlider = document.getElementById('heroSlider');
    if (heroSlider) {
        var slides = heroSlider.querySelectorAll('.hero-slide');
        var dots = heroSlider.querySelectorAll('.dot');
        var current = 0;
        if (slides.length > 0) {
            function showSlide(idx) {
                slides.forEach(function(s, i) {
                    s.style.display = i === idx ? 'block' : 'none';
                });
                dots.forEach(function(d, i) {
                    d.classList.toggle('active', i === idx);
                });
                current = idx;
            }
            showSlide(0);
            dots.forEach(function(dot) {
                dot.addEventListener('click', function() {
                    showSlide(parseInt(this.getAttribute('data-index')));
                });
            });
            setInterval(function() {
                showSlide((current + 1) % slides.length);
            }, 5000);
        }
    }

    console.log('Gadget Glow — UI Engine Loaded');
})();
