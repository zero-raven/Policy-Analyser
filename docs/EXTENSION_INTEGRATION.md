# Browser Extension Integration Guide

This guide explains how to integrate the PolicyLens backend with a browser extension for real-time privacy policy analysis.

## Overview

The PolicyLens backend exposes REST API endpoints that can be called from a browser extension to:
1. Analyze privacy policies from any website
2. Interact with an AI chatbot about the policy
3. Get AI-generated explanations and summaries

## Backend Endpoints

### 1. Analyze URL - `POST /analyze-url`

Scrapes, chunks, classifies, and explains a privacy policy from a URL.

**Request:**
```json
{
  "url": "https://example.com/privacy-policy",
  "model": "bert"  // optional: "bert", "deberta", "deberta-v2"
}
```

**Response:**
```json
{
  "labels": ["First Party Collection/Use", "Third Party Sharing/Collection"],
  "scores": [0.95, 0.87, ...],
  "risks": ["medium", "high", ...],
  "risk_percentage": {"high": 33.3, "medium": 50.0, "low": 16.7},
  "explanation": "AI-generated explanation...",
  "summary": "AI-generated summary with metadata...",
  "chunk_count": 45,
  "chunks": ["chunk1 text...", "chunk2 text...", ...],
  "url": "https://example.com/privacy-policy"
}
```

### 2. Chat with Policy - `POST /chat`

Ask questions about the analyzed privacy policy using RAG.

**Request:**
```json
{
  "message": "What data do they collect?",
  "chunks": ["chunk1 text...", "chunk2 text...", ...]
}
```

**Response:**
```json
{
  "answer": "Based on the privacy policy, they collect...",
  "type": "RAG",  // or "INSTRUCTION", "GUARDRAIL"
  "sources": ["Policy Text"],
  "risks": {}
}
```

### 3. Quick Classification - `POST /predict`

Classify pasted text directly (no URL scraping).

**Request:**
```json
{
  "text": "We collect your email and phone number...",
  "model": "bert"
}
```

**Response:**
```json
{
  "labels": ["First Party Collection/Use"],
  "scores": [0.95, ...],
  "risks": ["medium", ...],
  "risk_percentage": {"medium": 100.0},
  "chunks": ["chunk1...", "chunk2..."],
  "model_used": "BERT (Uncased)"
}
```

## Extension Architecture

### manifest.json
```json
{
  "manifest_version": 3,
  "name": "PolicyLens Extension",
  "version": "1.0",
  "description": "Analyze privacy policies in real-time",
  "permissions": ["activeTab", "storage"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon.png"
  },
  "host_permissions": ["<all_urls>"],
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"]
  }]
}
```

### popup.html
```html
<!DOCTYPE html>
<html>
<head>
  <title>PolicyLens</title>
  <style>
    body { width: 400px; padding: 15px; font-family: Arial; }
    #status { padding: 10px; margin: 10px 0; border-radius: 5px; }
    .analyzing { background: #fff3cd; }
    .success { background: #d4edda; }
    .error { background: #f8d7da; }
    #results { margin-top: 15px; }
    .risk-high { color: #d32f2f; font-weight: bold; }
    .risk-medium { color: #f57c00; font-weight: bold; }
    .risk-low { color: #388e3c; font-weight: bold; }
    #chatbox { margin-top: 20px; border-top: 1px solid #ddd; padding-top: 15px; }
    #chat-messages { max-height: 200px; overflow-y: auto; margin-bottom: 10px; }
    .message { margin: 5px 0; padding: 8px; border-radius: 5px; }
    .user-message { background: #e3f2fd; text-align: right; }
    .bot-message { background: #f5f5f5; }
  </style>
</head>
<body>
  <h2>🔐 PolicyLens</h2>
  <button id="analyzeBtn">Analyze Current Page</button>
  <div id="status"></div>
  <div id="results"></div>
  
  <div id="chatbox" style="display:none;">
    <h3>💬 Ask about the Policy</h3>
    <div id="chat-messages"></div>
    <input type="text" id="chat-input" placeholder="What data do they collect?" style="width: 100%;">
    <button id="chat-send">Send</button>
  </div>
  
  <script src="popup.js"></script>
</body>
</html>
```

### popup.js
```javascript
const API_BASE = 'http://localhost:8000';
let currentChunks = [];

document.getElementById('analyzeBtn').addEventListener('click', analyzePage);
document.getElementById('chat-send').addEventListener('click', sendChatMessage);
document.getElementById('chat-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendChatMessage();
});

async function analyzePage() {
  const statusDiv = document.getElementById('status');
  const resultsDiv = document.getElementById('results');
  const chatbox = document.getElementById('chatbox');
  
  // Get current tab URL
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  statusDiv.className = 'analyzing';
  statusDiv.textContent = '🔄 Analyzing privacy policy...';
  resultsDiv.innerHTML = '';
  chatbox.style.display = 'none';
  
  try {
    const response = await fetch(`${API_BASE}/analyze-url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: tab.url, model: 'bert' })
    });
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    // Store chunks for chatbot
    currentChunks = data.chunks || [];
    
    // Display results
    statusDiv.className = 'success';
    statusDiv.textContent = `✅ Analyzed ${data.chunk_count} sections`;
    
    let html = '<h3>Detected Privacy Practices:</h3><ul>';
    data.labels.forEach((label, i) => {
      const risk = data.risks[i];
      html += `<li><span class="risk-${risk}">${risk.toUpperCase()}</span>: ${label}</li>`;
    });
    html += '</ul>';
    
    if (data.summary) {
      html += `<h3>Summary:</h3><p>${data.summary.substring(0, 200)}...</p>`;
    }
    
    resultsDiv.innerHTML = html;
    
    // Show chatbot
    if (currentChunks.length > 0) {
      chatbox.style.display = 'block';
    }
    
  } catch (error) {
    statusDiv.className = 'error';
    statusDiv.textContent = `❌ Error: ${error.message}`;
  }
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const messagesDiv = document.getElementById('chat-messages');
  const message = input.value.trim();
  
  if (!message) return;
  
  // Show user message
  messagesDiv.innerHTML += `<div class="message user-message">${message}</div>`;
  input.value = '';
  
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message: message,
        chunks: currentChunks 
      })
    });
    
    const data = await response.json();
    
    // Show bot response
    messagesDiv.innerHTML += `<div class="message bot-message">${data.answer}</div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
  } catch (error) {
    messagesDiv.innerHTML += `<div class="message bot-message" style="color:red;">Error: ${error.message}</div>`;
  }
}
```

## CORS Configuration

The backend is already configured with CORS enabled:

```python
# backend_fastapi.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Installation Steps

1. **Start the Backend**
   ```bash
   uvicorn backend_fastapi:app --reload
   ```

2. **Load Extension in Chrome**
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select your extension folder

3. **Test the Extension**
   - Navigate to any website with a privacy policy
   - Click the extension icon
   - Click "Analyze Current Page"
   - Use the chatbot to ask questions

## Features

✅ **Real-time Analysis**: Instant privacy policy classification  
✅ **AI Chatbot**: Ask questions about the analyzed policy  
✅ **Risk Detection**: Automatic high/medium/low risk classification  
✅ **Summaries**: AI-generated policy summaries  
✅ **Multi-Model**: Support for BERT, DeBERTa variants  

## Security Notes

- The extension needs `<all_urls>` permission to analyze any page
- API calls are made to localhost by default
- For production, deploy backend and update `API_BASE` URL
- Consider adding API authentication for production use

## Troubleshooting

**Extension can't connect:**
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in backend
- Verify no firewall blocking localhost connections

**Analysis fails:**
- Check if the page has a valid privacy policy
- Verify GROQ_API_KEY is set in backend `.env`
- Check backend logs for errors

**Chatbot not working:**
- Ensure policy was analyzed first (chunks loaded)
- Check that `/chat` endpoint is receiving chunks
- Verify Groq API is accessible
