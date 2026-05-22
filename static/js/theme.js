(function() {
    'use strict';

    var themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            var html = document.documentElement;
            var current = html.getAttribute('data-theme');
            var next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('gadget_glow_theme', next);
            var icon = themeToggle.querySelector('i');
            icon.className = next === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
            document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: next } }));
        });
    }

    var savedTheme = localStorage.getItem('gadget_glow_theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (themeToggle) {
            var icon = themeToggle.querySelector('i');
            icon.className = savedTheme === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
        }
    }

    document.querySelectorAll('.theme-dot').forEach(function(dot) {
        dot.addEventListener('click', function() {
            var brand = this.getAttribute('data-brand');
            document.querySelectorAll('.theme-dot').forEach(function(d) { d.classList.remove('active'); });
            this.classList.add('active');
            document.documentElement.setAttribute('data-brand-theme', brand);
            localStorage.setItem('gadget_glow_brand_theme', brand);
        });
    });

    var savedBrand = localStorage.getItem('gadget_glow_brand_theme');
    if (savedBrand) {
        document.documentElement.setAttribute('data-brand-theme', savedBrand);
        document.querySelectorAll('.theme-dot').forEach(function(d) {
            if (d.getAttribute('data-brand') === savedBrand) { d.classList.add('active'); }
        });
    }

    /* ─── Auto theme based on time ─── */
    if (!localStorage.getItem('gadget_glow_theme')) {
        var hour = new Date().getHours();
        var autoTheme = (hour >= 6 && hour < 18) ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', autoTheme);
        localStorage.setItem('gadget_glow_theme', autoTheme);
        if (themeToggle) {
            var icon = themeToggle.querySelector('i');
            icon.className = autoTheme === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
        }
    }
})();
