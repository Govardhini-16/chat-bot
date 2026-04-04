// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const clearBtn = document.getElementById('clearBtn');
const loadingIndicator = document.getElementById('loadingIndicator');

// API Base URL
const API_URL = '/';

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
clearBtn.addEventListener('click', clearHistory);

// Load chat history on page load
document.addEventListener('DOMContentLoaded', () => {
    loadChatHistory();
});

/**
 * Send a message to the AI chat endpoint
 */
async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message) {
        alert('Please enter a message');
        return;
    }

    // Remove welcome message if it exists
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    // Display user message
    displayMessage(message, 'user');
    messageInput.value = '';
    messageInput.focus();

    // Show loading indicator
    showLoading(true);
    sendBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        displayMessage(data.response, 'ai');
    } catch (error) {
        console.error('Error:', error);
        displayMessage(
            `Error: ${error.message || 'Failed to get response from AI'}`,
            'ai'
        );
    } finally {
        showLoading(false);
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

/**
 * Display a message in the chat
 * @param {string} text - The message text
 * @param {string} sender - 'user' or 'ai'
 */
function displayMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    // Clean thinking tags from AI responses
    let displayText = text;
    if (sender === 'ai') {
        displayText = cleanThinkingTags(text);
    }

    const messageContent = document.createElement('div');
    messageContent.innerHTML = `
        <div class="message-bubble">${escapeHtml(displayText)}</div>
        <div class="message-time">${new Date().toLocaleTimeString()}</div>
    `;

    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);

    // Auto-scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Load chat history from the server
 */
async function loadChatHistory() {
    try {
        const response = await fetch(`${API_URL}history`);

        if (!response.ok) {
            console.error('Failed to load history');
            return;
        }

        const data = await response.json();
        const history = data.history || [];

        if (history.length > 0) {
            // Remove welcome message
            const welcomeMessage = chatMessages.querySelector('.welcome-message');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }

            // Display each message from history
            history.forEach((entry) => {
                displayMessage(entry.user_message, 'user');
                displayMessage(entry.ai_response, 'ai');
            });
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

/**
 * Clear chat history
 */
async function clearHistory() {
    if (!confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}history`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to clear history');
        }

        // Clear the chat display
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>Welcome to AI Chat</h2>
                <p>Start a conversation with the AI assistant. Your chat history will be saved automatically.</p>
            </div>
        `;

        messageInput.focus();
        alert('Chat history cleared successfully!');
    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    }
}

/**
 * Show or hide loading indicator
 * @param {boolean} show - Whether to show the loading indicator
 */
function showLoading(show) {
    if (show) {
        loadingIndicator.classList.add('show');
    } else {
        loadingIndicator.classList.remove('show');
    }
}

/**
 * Clean thinking tags and thinking text from response
 * Handles multiple formats of thinking content
 */
function cleanThinkingTags(text) {
    // Remove XML-style tags
    text = text.replace(/<think>[\s\S]*?<\/think>/gi, '');
    text = text.replace(/<thinking>[\s\S]*?<\/thinking>/gi, '');
    text = text.replace(/<\s*\/\s*think\s*>/gi, '');
    text = text.replace(/<\s*\/\s*thinking\s*>/gi, '');
    text = text.replace(/\{\{think\|[\s\S]*?\}\}/gi, '');
    
    // Split into lines and filter out thinking lines
    const lines = text.split('\n').filter(line => {
        const trimmed = line.trim().toLowerCase();
        return trimmed && !hasThinkingIndicators(trimmed);
    });
    
    // Join back together and clean up
    text = lines.join('\n').trim();
    
    // Remove multiple blank lines
    text = text.replace(/\n\s*\n+/g, '\n');
    
    // Return cleaned text, or default message if empty
    return text.trim() || "I'm ready to help!";
}

/**
 * Check if a line contains thinking/reasoning indicators
 */
function hasThinkingIndicators(text) {
    const indicators = [
        'okay, the user',
        'i should ',
        'let me ',
        'i need to',
        'i think',
        'thinking',
        'consider',
        'the user said',
        'responding',
        'perhaps',
        'maybe i should',
        'based on',
        'analyzing',
        'reasoning',
        'let\'s think',
        'should respond'
    ];
    
    return indicators.some(indicator => text.includes(indicator));
}

/**
 * Escape HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
