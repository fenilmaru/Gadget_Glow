(function() {
    'use strict';

    var chatbotToggle = document.getElementById('chatbotToggle');
    var chatbotPanel = document.getElementById('chatbotPanel');
    var chatbotClose = document.getElementById('chatbotClose');
    var chatbotInput = document.getElementById('chatbotInput');
    var chatbotSend = document.getElementById('chatbotSend');
    var chatbotMessages = document.getElementById('chatbotMessages');
    var quickReplies = document.querySelectorAll('.qr-btn');

    /* ─── Toggle Chatbot ─── */
    function toggleChat() {
        if (!chatbotPanel) return;
        var isOpen = chatbotPanel.classList.contains('open');
        if (isOpen) {
            chatbotPanel.classList.remove('open');
        } else {
            chatbotPanel.classList.add('open');
            if (chatbotInput) chatbotInput.focus();
        }
    }

    if (chatbotToggle) {
        chatbotToggle.addEventListener('click', toggleChat);
    }
    if (chatbotClose) {
        chatbotClose.addEventListener('click', toggleChat);
    }

    /* ─── Send Message ─── */
    function sendMessage(msg) {
        if (!msg || !msg.trim()) return;
        msg = msg.trim();
        if (chatbotInput) chatbotInput.value = '';

        addMessage(msg, 'user');

        var loadingId = 'loading-' + Date.now();
        addTypingIndicator(loadingId);

        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        var token = csrfToken ? csrfToken.value : '';
        if (!token) {
            token = getCookie('csrftoken');
        }

        fetch('/api/v1/ai/chat/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': token
            },
            body: JSON.stringify({ message: msg })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            removeLoading(loadingId);
            var reply = data.reply || 'Sorry, I had trouble understanding that. Please try again.';
            addMessage(reply, 'bot');
            if (chatbotMessages) chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        })
        .catch(function() {
            removeLoading(loadingId);
            addMessage('Connection error. Please try again later.', 'bot');
            if (chatbotMessages) chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        });

        if (chatbotMessages) chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function addMessage(text, role) {
        if (!chatbotMessages) return;
        var div = document.createElement('div');
        div.className = 'chat-message ' + role;
        div.textContent = text;
        chatbotMessages.appendChild(div);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function addTypingIndicator(id) {
        if (!chatbotMessages) return;
        var div = document.createElement('div');
        div.className = 'chat-message bot';
        div.id = id;
        div.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        chatbotMessages.appendChild(div);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function removeLoading(id) {
        var el = document.getElementById(id);
        if (el) el.remove();
    }

    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : '';
    }

    if (chatbotSend) {
        chatbotSend.addEventListener('click', function() {
            if (chatbotInput) sendMessage(chatbotInput.value);
        });
    }
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage(this.value);
            }
        });
    }

    quickReplies.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var query = this.getAttribute('data-query') || this.textContent;
            if (!chatbotPanel.classList.contains('open')) {
                toggleChat();
            }
            setTimeout(function() { sendMessage(query); }, 300);
        });
    });

    /* ─── Voice Input ─── */
    var voiceBtn = document.getElementById('voiceInput');
    if (voiceBtn && 'webkitSpeechRecognition' in window) {
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.onresult = function(e) {
            var transcript = e.results[0][0].transcript;
            if (chatbotInput) {
                chatbotInput.value = transcript;
                sendMessage(transcript);
            }
            voiceBtn.classList.remove('listening');
        };
        recognition.onerror = function() {
            voiceBtn.classList.remove('listening');
        };
        voiceBtn.addEventListener('click', function() {
            this.classList.toggle('listening');
            if (this.classList.contains('listening')) {
                recognition.start();
            } else {
                recognition.stop();
            }
        });
    } else if (voiceBtn) {
        voiceBtn.style.display = 'none';
    }

    /* ─── Close on Escape ─── */
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && chatbotPanel && chatbotPanel.classList.contains('open')) {
            chatbotPanel.classList.remove('open');
        }
    });

    console.log('AI Chatbot initialized');
})();
