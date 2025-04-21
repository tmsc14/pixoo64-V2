function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

function initializeDarkMode() {
    if (localStorage.getItem('darkMode') === 'true') document.body.classList.add('dark-mode');
}

function toggleChatSettings() {
    const panel = document.getElementById('chat-settings-panel');
    panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
}

let currentConversationId = null;
let idleTimer = null;
let sendCount = 0;
const IDLE_TIMEOUT = 3 * 60 * 1000; // 3 minutes

function resetIdleTimer() {
    if (idleTimer) clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
        updatePixooDisplay({ theme: 'chatbot', state: 'sleeping', send_count: sendCount });
    }, IDLE_TIMEOUT);
}

function appendMessage(content, role, isTyping = false) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}${isTyping ? ' typing' : ''}`;
    
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const timestampSpan = document.createElement('span');
    timestampSpan.className = 'chat-timestamp';
    timestampSpan.textContent = timestamp;
    timestampSpan.setAttribute('aria-label', `Sent at ${timestamp}`);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'chat-content';
    if (isTyping) {
        contentDiv.className = 'typing-indicator';
        contentDiv.innerHTML = '<span></span><span></span><span></span>';
    } else {
        contentDiv.textContent = content;
    }

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'avatar';

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timestampSpan);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(10px)';
    setTimeout(() => {
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);

    return messageDiv;
}

async function updatePixooDisplay(data) {
    try {
        const response = await fetch('/api/pixoo-display', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...data,
                background_color: hexToRgb(document.getElementById('chatbot-bg-color')?.value || '#000000'),
                show_chat: document.getElementById('chatbot-show-chat')?.checked ?? true
            })
        });
        const result = await response.json();
        if (result.status !== 'success') {
            console.error('Pixoo display error:', result.message);
        }
    } catch (error) {
        console.error('Pixoo display fetch error:', error);
    }
}

async function handleChatMessage() {
    const input = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-chat');
    const statusDiv = document.getElementById('chat-status');
    const message = input.value.trim();

    if (!message) return;

    input.disabled = true;
    sendButton.disabled = true;

    appendMessage(message, 'user');
    updatePixooDisplay({ 
        theme: 'chatbot', 
        state: 'thinking', 
        message, 
        send_count: ++sendCount,
        show_chat: document.getElementById('chatbot-show-chat')?.checked ?? true
    });
    resetIdleTimer();
    input.value = '';

    const typingDiv = appendMessage('', 'bot', true);
    statusDiv.textContent = 'Bot is responding...';
    statusDiv.className = 'chat-status active';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: message,
                response_mode: "streaming",
                user: "pixoo-user",
                conversation_id: currentConversationId || "",
                inputs: {}
            })
        });

        if (!response.ok) throw new Error(`HTTP error ${response.status}`);

        typingDiv.remove();

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botMessage = '';
        let messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message bot';
        
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'chat-timestamp';
        timestampSpan.textContent = timestamp;
        timestampSpan.setAttribute('aria-label', `Sent at ${timestamp}`);
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'chat-content';
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestampSpan);
        document.getElementById('chat-messages').appendChild(messageDiv);

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const events = chunk.split('\n\n');
            
            events.forEach(event => {
                if (event.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(event.slice(6));
                        if (data.event === 'message') {
                            const answer = data.answer.replace(/\r\n/g, '\n');
                            botMessage += answer;
                            contentDiv.textContent = botMessage;
                            messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        } else if (data.event === 'message_end') {
                            currentConversationId = data.conversation_id;
                            updatePixooDisplay({ 
                                theme: 'chatbot', 
                                state: 'smiling', 
                                bot_response: botMessage,
                                send_count: sendCount,
                                show_chat: document.getElementById('chatbot-show-chat')?.checked ?? true
                            });
                            resetIdleTimer();
                        }
                    } catch (e) {
                        console.error('Error parsing event:', e);
                    }
                }
            });
        }

        if (!botMessage.includes('\n') && botMessage.length > 200) {
            contentDiv.textContent = botMessage.replace(/(.{100,200}\.)\s/g, '$1\n\n');
        }

        statusDiv.className = 'chat-status';
    } catch (error) {
        console.error('Chat error:', error);
        appendMessage('Sorry, something went wrong. Please try again.', 'error');
        statusDiv.textContent = 'Connection error';
        statusDiv.className = 'chat-status active error';
        updatePixooDisplay({ 
            theme: 'chatbot', 
            state: 'error', 
            send_count: sendCount,
            show_chat: document.getElementById('chatbot-show-chat')?.checked ?? true
        });
        resetIdleTimer();
        setTimeout(() => {
            statusDiv.className = 'chat-status';
        }, 3000);
    } finally {
        input.disabled = false;
        sendButton.disabled = false;
        input.focus();
    }
}

function clearChat() {
    const messagesDiv = document.getElementById('chat-messages');
    const statusDiv = document.getElementById('chat-status');
    const input = document.getElementById('chat-input');
    messagesDiv.innerHTML = '';
    currentConversationId = null;
    sendCount = 0;
    statusDiv.className = 'chat-status';
    input.disabled = false;
    input.value = '';
    input.focus();
    resetIdleTimer();
}

function autoResizeTextarea() {
    const textarea = document.getElementById('chat-input');
    textarea.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 100)}px`;
    });
}

document.querySelectorAll('.theme-card').forEach(card => {
    card.addEventListener('click', function() {
        document.querySelectorAll('.theme-card, .theme-settings').forEach(el => el.classList.remove('active'));
        this.classList.add('active');
        document.getElementById(this.dataset.settings).classList.add('active');
        fetchKPIData();
        if (this.dataset.theme !== 'chatbot') {
            resetIdleTimer();
        }
    });
});

async function postKPIData() {
    const activeTheme = document.querySelector('.theme-card.active').dataset.theme;
    const button = document.getElementById('update-values');
    const statusMessage = document.querySelector('.status-message');

    console.log(`postKPIData called for theme: ${activeTheme}`); // Debug log

    const data = {
        theme: activeTheme,
        background_color: hexToRgb(document.getElementById(
            activeTheme === 'flags' ? 'background-color' : 
            activeTheme === 'beer' ? 'beer-bg-color' : 'chatbot-bg-color'
        )?.value || '#000000'),
        text_color: hexToRgb(document.getElementById(
            activeTheme === 'flags' ? 'text-color' : 
            activeTheme === 'beer' ? 'beer-text-color' : '#ffffff'
        )?.value || '#ffffff')
    };

    try {
        if (activeTheme === 'chatbot') {
            data.show_chat = document.getElementById('chatbot-show-chat')?.checked ?? true;
        } else if (activeTheme === 'flags') {
            data.green_flags = parseInt(document.getElementById('green-flags').value) || 0;
            data.red_flags = parseInt(document.getElementById('red-flags').value) || 0;
            data.attendance = parseInt(document.getElementById('attendance').value) || 0;
            data.showDateTime = document.getElementById('toggle-date-time').checked;
            data.country = document.getElementById('country-select').value;
            data.line_color = hexToRgb(document.getElementById('line-color').value);
        } else if (activeTheme === 'beer') {
            console.log('Collecting Beer Consumed data...'); // Debug log
            const location = document.getElementById('beer-location')?.value?.trim() || 'Unknown';
            const beersTotalAvailable = parseInt(document.getElementById('beers-total-available')?.value) || 1000;
            const beersConsumed = parseInt(document.getElementById('beers-consumed')?.value) || 0;
            const country = document.getElementById('country-select-beer')?.value || 'Philippines';
            const showDateTime = document.getElementById('toggle-date-time-beer')?.checked ?? false;

            if (!location) throw new Error('Location is required');
            if (beersTotalAvailable < 1) throw new Error('Total beers available must be at least 1');
            if (beersConsumed < 0) throw new Error('Beers consumed cannot be negative');

            data.location = location;
            data.beers_total_available = beersTotalAvailable;
            data.beers_consumed = beersConsumed;
            data.country = country;
            data.showDateTime = showDateTime;
            console.log('Beer Consumed data:', data); // Debug log
        } else {
            throw new Error('Invalid theme');
        }

        button.disabled = true;
        button.textContent = 'Updating...';
        statusMessage.style.display = 'none';

        console.log('Sending /api/update-kpis request:', JSON.stringify(data)); // Debug log

        const response = await fetch('/api/update-kpis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error: ${response.status} ${errorText}`);
        }

        const result = await response.json();
        if (result.status !== 'success') {
            throw new Error(result.message || 'Update failed');
        }

        statusMessage.textContent = 'Display updated successfully!';
        statusMessage.className = 'status-message success';
    } catch (error) {
        console.error('postKPIData error:', error);
        statusMessage.textContent = `Error updating display: ${error.message}`;
        statusMessage.className = 'status-message error';
    } finally {
        statusMessage.style.display = 'block';
        button.disabled = false;
        button.textContent = 'Update Display';
        setTimeout(() => statusMessage.style.display = 'none', 3000);
    }
}

function rgbToHex(rgb) {
    if (!rgb) return '#000000';
    const parts = rgb.split(',').map(Number);
    return `#${parts.map(p => p.toString(16).padStart(2, '0')).join('')}`;
}

function hexToRgb(hex) {
    const normalizedHex = hex.length === 4 ? 
        `#${hex[1]}${hex[1]}${hex[2]}${hex[2]}${hex[3]}${hex[3]}` : hex;
    return [
        parseInt(normalizedHex.substring(1, 3), 16),
        parseInt(normalizedHex.substring(3, 5), 16),
        parseInt(normalizedHex.substring(5, 7), 16),
    ].join(',');
}

function updateUI(data) {
    const activeTheme = document.querySelector('.theme-card.active').dataset.theme;
    
    if (activeTheme === 'chatbot') {
        document.getElementById('chatbot-bg-color').value = rgbToHex(data.background_color || '#000000');
        document.getElementById('chatbot-show-chat').checked = data.show_chat ?? true;
    } else if (activeTheme === 'flags') {
        document.getElementById('green-flags').value = data.green_flags || 0;
        document.getElementById('red-flags').value = data.red_flags || 0;
        document.getElementById('attendance').value = data.attendance || 0;
        document.getElementById('toggle-date-time').checked = data.showDateTime;
        document.getElementById('country-select').value = data.country || 'Australia';
        document.getElementById('background-color').value = rgbToHex(data.background_color || '#000000');
        document.getElementById('text-color').value = rgbToHex(data.text_color || '#ffffff');
        document.getElementById('line-color').value = rgbToHex(data.line_color || '#ffffff');
    } else {
        document.getElementById('beer-location').value = data.location || 'Unknown';
        document.getElementById('beers-total-available').value = data.beers_total_available || 1000;
        document.getElementById('beers-consumed').value = data.beers_consumed || 0;
        document.getElementById('country-select-beer').value = data.country || 'Philippines';
        document.getElementById('toggle-date-time-beer').checked = data.showDateTime || false;
        document.getElementById('beer-bg-color').value = rgbToHex(data.background_color || '#000000');
        document.getElementById('beer-text-color').value = rgbToHex(data.text_color || '#ffffff');
    }
    initializeColorPreviews();
}

function initializeColorPreviews() {
    document.querySelectorAll('.color-picker-input').forEach(input => {
        const previewId = input.id.replace('-color', '-preview');
        const previewBox = document.getElementById(previewId);
        if (previewBox) {
            previewBox.style.backgroundColor = input.value;
            input.addEventListener('input', () => previewBox.style.backgroundColor = input.value);
        }
    });
}

async function fetchKPIData() {
    try {
        const activeTheme = document.querySelector('.theme-card.active').dataset.theme;
        const response = await fetch(`/api/kpi-data?theme=${activeTheme}`);
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Chat event listeners
document.getElementById('send-chat').addEventListener('click', handleChatMessage);
document.getElementById('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleChatMessage();
    }
});
document.getElementById('clear-chat').addEventListener('click', clearChat);

// Initialize
initializeDarkMode();
document.getElementById('update-values').addEventListener('click', postKPIData);
initializeColorPreviews();
fetchKPIData();
autoResizeTextarea();