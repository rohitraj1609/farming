// Chatbot functionality for Farming App
// Agriculture-focused chatbot with farming-related responses

// Chatbot data and responses
const chatbotResponses = {
    greetings: [
        "Hello! 🌱 I'm your farming assistant. How can I help you today?",
        "Hi there! 👋 Ready to grow? What farming question can I answer?",
        "Welcome! 🌾 I'm here to help with all your agricultural needs. What would you like to know?"
    ],
    farewells: [
        "Happy farming! 🌱 Feel free to come back anytime!",
        "Good luck with your crops! 🌾 See you soon!",
        "Take care of your farm! 🌱 Have a great day!"
    ],
    help: [
        "I can help you with:\n• Crop information and farming tips\n• Market prices and trends\n• Selling and buying crops\n• Agricultural best practices\n• App navigation\n\nWhat would you like to know?",
        "I'm here to assist with:\n🌾 Crop management\n📊 Market updates\n🛒 Buying and selling\n💡 Farming tips\n\nAsk me anything!",
        "I can help with farming questions, crop information, market trends, and using the app. What do you need?"
    ],
    crops: {
        wheat: "🌾 Wheat is a staple grain crop. Best grown in cool, dry climates. Requires well-drained soil and moderate water. Harvest time is typically 3-4 months after planting.",
        rice: "🌾 Rice needs warm, humid conditions and plenty of water. It's usually grown in flooded fields called paddies. Takes 3-6 months to mature.",
        tomatoes: "🍅 Tomatoes are warm-season vegetables. They need full sun, well-drained soil, and regular watering. Harvest in 60-80 days after planting.",
        vegetables: "🥕 Vegetables like carrots, potatoes, and onions are great for home gardens. They need good soil, regular watering, and proper spacing.",
        fruits: "🍎 Fruit crops like apples, mangoes, and citrus need specific climate conditions. They typically take longer to mature but provide good returns.",
        spices: "🌶️ Spices like chili, turmeric, and coriander are high-value crops. They need warm climates and well-drained soil."
    },
    selling: [
        "To sell crops:\n1. Go to the 'Sell Crops' page\n2. Fill in crop details (name, quantity, price)\n3. Add location and description\n4. Click 'List My Crop'\n\nYour listing will appear in the marketplace!",
        "Selling is easy! Navigate to the Sell page, fill in your crop information, set your price, and list it. Buyers can then contact you directly.",
        "Use the Sell Crops section to list your harvest. Include clear descriptions and competitive pricing to attract buyers quickly."
    ],
    buying: [
        "To buy crops:\n1. Visit the 'Buy Crops' page\n2. Browse available listings\n3. Use filters to find what you need\n4. Contact sellers directly\n5. Complete your purchase",
        "Check the Buy Crops page to see all available listings. You can filter by category, price, and location to find exactly what you need.",
        "Browse the marketplace on the Buy page. Filter by crop type, price range, or location to find the best deals near you."
    ],
    market: [
        "Market updates show current crop prices, trends, and agricultural news. Check the Market Updates page for the latest information.",
        "Stay informed with real-time market prices and trends. The Market Updates section has all the information you need.",
        "Market updates include price trends, weather impacts, and demand forecasts. Visit the Market Updates page regularly."
    ],
    tips: [
        "💡 Farming Tips:\n• Test your soil before planting\n• Use organic fertilizers when possible\n• Practice crop rotation\n• Monitor water levels carefully\n• Keep records of your harvests",
        "Best Practices:\n🌱 Rotate crops to maintain soil health\n💧 Water early morning or evening\n🌾 Use quality seeds\n📊 Track your expenses and yields\n🤝 Connect with other farmers",
        "Pro Tips:\n• Start with crops suitable for your climate\n• Invest in good irrigation systems\n• Learn about pest management\n• Join farming communities\n• Stay updated with market prices"
    ],
    default: [
        "I'm not sure I understand. Could you rephrase that? I can help with farming questions, crop information, or app navigation.",
        "Hmm, I'm still learning! Try asking about crops, selling, buying, or market updates. I'm here to help!",
        "I might not have the answer to that yet. Try asking about:\n• Crop information\n• How to sell/buy\n• Market updates\n• Farming tips"
    ]
};

// Chatbot state
let chatbotOpen = false;
let chatHistory = [];
let chatSessionId = null; // Unique session ID for this conversation

// Initialize chatbot
function initChatbot() {
    const chatButton = document.getElementById('chatbot-button');
    const chatWindow = document.getElementById('chatbot-window');
    const chatClose = document.getElementById('chatbot-close');
    const chatInput = document.getElementById('chatbot-input');
    const chatSend = document.getElementById('chatbot-send');
    const chatMessages = document.getElementById('chatbot-messages');

    // Open/close chatbot - prevent event bubbling
    if (chatButton) {
        chatButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleChatbot(e);
        });
    }

    if (chatClose) {
        chatClose.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleChatbot(e);
        });
    }

    // Prevent clicks inside chat window from closing it
    if (chatWindow) {
        chatWindow.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // Prevent document clicks from closing chatbot (only close via button)
    document.addEventListener('click', function(e) {
        const container = document.getElementById('chatbot-container');
        if (container && chatbotOpen && !container.contains(e.target)) {
            // Don't auto-close - user must click the button
            // This prevents accidental closing
        }
    });

    // Send message on button click
    if (chatSend) {
        chatSend.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            sendMessage();
        });
    }

    // Send message on Enter key
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                e.stopPropagation();
                sendMessage();
            }
        });
    }

    // Don't add welcome message on load - add it when first opened
}

// Toggle chatbot window
function toggleChatbot(e) {
    // Prevent any event propagation
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Toggle state
    chatbotOpen = !chatbotOpen;
    const chatWindow = document.getElementById('chatbot-window');
    const chatButton = document.getElementById('chatbot-button');
    const chatMessages = document.getElementById('chatbot-messages');

    if (chatWindow) {
        if (chatbotOpen) {
            chatWindow.style.display = 'flex';
            chatWindow.style.animation = 'slideUp 0.3s ease-out';
            
            // Create new session ID if this is a new conversation
            if (!chatSessionId || (chatMessages && chatMessages.children.length === 0)) {
                chatSessionId = generateSessionId();
                chatHistory = []; // Reset history for new session
                console.log('New chat session created:', chatSessionId);
            }
            
            // Add welcome message only if chat is empty (first time opening)
            if (chatMessages && chatMessages.children.length === 0) {
                addWelcomeMessage();
            }
            
            // Focus input when opened
            setTimeout(() => {
                const chatInput = document.getElementById('chatbot-input');
                if (chatInput) chatInput.focus();
            }, 300);
        } else {
            chatWindow.style.animation = 'slideDown 0.3s ease-out';
            setTimeout(() => {
                if (!chatbotOpen) { // Double check state before hiding
                    chatWindow.style.display = 'none';
                }
            }, 300);
        }
    }

    if (chatButton) {
        chatButton.classList.toggle('active', chatbotOpen);
    }
}

// Add welcome message
function addWelcomeMessage() {
    const greeting = "Hello! 🌱 I'm AgriBot, your AI farming assistant powered by advanced language models. I use chain-of-thought reasoning to provide you with the best farming advice. How can I help you today?";
    addMessage('bot', greeting);
}

// Send user message
async function sendMessage() {
    const chatInput = document.getElementById('chatbot-input');
    const chatSend = document.getElementById('chatbot-send');
    const message = chatInput ? chatInput.value.trim() : '';

    if (!message) return;

    // Add user message to chat
    addMessage('user', message);

    // Clear input and disable send button
    if (chatInput) {
        chatInput.value = '';
        chatInput.disabled = true;
    }
    if (chatSend) {
        chatSend.disabled = true;
        chatSend.innerHTML = '<span>⏳</span>';
    }

    // Add thinking indicator
    const thinkingId = addThinkingIndicator();

    try {
        // Prepare conversation history for context
        const history = chatHistory.slice(-10).map(msg => ({
            user: msg.sender === 'user' ? msg.text : '',
            assistant: msg.sender === 'bot' ? msg.text : ''
        })).filter(msg => msg.user || msg.assistant);

        // Call LLM API with session ID
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: chatSessionId,
                history: history
            })
        });

        // Remove thinking indicator
        removeThinkingIndicator(thinkingId);

        const data = await response.json();

        if (data.success) {
            // Update session ID if returned from server
            if (data.session_id && data.session_id !== chatSessionId) {
                chatSessionId = data.session_id;
                console.log('Session ID updated from server:', chatSessionId);
            }
            addMessage('bot', data.response);
        } else {
            addMessage('bot', data.response || data.error || "I'm sorry, I encountered an error. Please try again.");
        }
    } catch (error) {
        console.error('Chatbot error:', error);
        removeThinkingIndicator(thinkingId);
        addMessage('bot', "I'm sorry, I'm having trouble connecting. Please check your internet connection and try again.");
    } finally {
        // Re-enable input and send button
        if (chatInput) {
            chatInput.disabled = false;
            setTimeout(() => chatInput.focus(), 100);
        }
        if (chatSend) {
            chatSend.disabled = false;
            chatSend.innerHTML = '<span>➤</span>';
        }
    }
}

// Add thinking indicator while waiting for LLM response
function addThinkingIndicator() {
    const chatMessages = document.getElementById('chatbot-messages');
    if (!chatMessages) return null;

    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'chat-message bot thinking';
    thinkingDiv.id = 'thinking-indicator';
    
    const thinkingContent = document.createElement('div');
    thinkingContent.className = 'message-content';
    thinkingContent.innerHTML = '<span class="thinking-dots">🤔 Thinking</span>';
    
    thinkingDiv.appendChild(thinkingContent);
    chatMessages.appendChild(thinkingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return 'thinking-indicator';
}

// Remove thinking indicator
function removeThinkingIndicator(thinkingId) {
    if (!thinkingId) return;
    const thinkingDiv = document.getElementById(thinkingId);
    if (thinkingDiv) {
        thinkingDiv.remove();
    }
}

// Add message to chat
function addMessage(sender, text) {
    const chatMessages = document.getElementById('chatbot-messages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Render markdown if marked.js is available, otherwise fallback to plain text
    if (typeof marked !== 'undefined') {
        // Configure marked.js options
        marked.setOptions({
            breaks: true,  // Convert single line breaks to <br>
            gfm: true,    // GitHub Flavored Markdown (includes tables)
            tables: true, // Enable tables (redundant with gfm, but explicit)
            headerIds: true, // Enable header IDs
            mangle: false, // Don't mangle email addresses
            pedantic: false, // Don't be pedantic about markdown
            sanitize: false, // Allow HTML (we'll sanitize manually if needed)
            smartLists: true, // Use smart list behavior
            smartypants: false // Don't use smart typography
        });
        
        try {
            // Render markdown to HTML
            messageContent.innerHTML = marked.parse(text);
        } catch (error) {
            console.error('Markdown parsing error:', error);
            // Fallback to plain text with line breaks
            const escapedText = text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
            messageContent.innerHTML = escapedText.replace(/\n/g, '<br>');
        }
    } else {
        // Fallback if marked.js is not loaded
        const escapedText = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
        messageContent.innerHTML = escapedText.replace(/\n/g, '<br>');
    }

    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Add to history
    chatHistory.push({ sender, text, timestamp: new Date() });
}

// Generate unique session ID
function generateSessionId() {
    // Generate a unique session ID using timestamp and random string
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 15);
    return `chat_${timestamp}_${random}`;
}

// Make functions globally accessible
window.initChatbot = initChatbot;
window.toggleChatbot = toggleChatbot;
window.sendMessage = sendMessage;
window.generateSessionId = generateSessionId;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initChatbot();
});

