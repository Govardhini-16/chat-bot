# AI Chat Application

A simple AI-powered chat application with Flask backend, MongoDB database, and responsive frontend interface.

## Features

 **Core Features:**
- Real-time chat with Claude AI (Anthropic)
- Chat history persistence with MongoDB
- Clean, responsive UI with modern design
- Loading indicators and typing animations
- Clear chat history functionality
- Error handling and validation
- Environment-based configuration (no hardcoded secrets)

 **Bonus Features:**
- Beautiful gradient UI with responsive design
- Typing indicators with animations
- Proper message timestamps
- Scroll-to-bottom auto-scroll for new messages
- Mobile-friendly interface

## Tech Stack

### Backend
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **MongoDB** - NoSQL database for chat history
- **Anthropic Claude API** - AI model for chat responses

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with flexbox and gradients
- **JavaScript (ES6)** - Dynamic interactions and API calls

## Prerequisites

- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas free tier)
- Anthropic Claude API key (free tier available)

## Setup Instructions

### 1. Clone/Download the Project
```bash
cd chatbot
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up MongoDB

**Option A: Local MongoDB**
1. Download and install MongoDB Community Edition from https://www.mongodb.com/try/download/community
2. Start MongoDB service:
   - **Windows:** MongoDB runs as a service automatically after installation
   - **macOS:** `brew services start mongodb-community`
   - **Linux:** `sudo systemctl start mongod`
3. Keep default MONGODB_URI: `mongodb://localhost:27017`

**Option B: MongoDB Atlas (Cloud - Recommended)**
1. Create free account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string: `mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority`
4. Use this as MONGODB_URI in `.env`

### 5. Get Anthropic Claude API Key

1. Visit https://console.anthropic.com/account/keys
2. Create a new API key
3. Copy the API key

### 6. Configure Environment Variables

Edit `.env` file and add:
```env
NVIDIA_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=chatbot
COLLECTION_NAME=conversations
```

Replace `your_api_key_here` with your actual Nvidia API key.

### 7. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Project Structure

```
chatbot/
├── app.py                 # Flask backend with API endpoints
├── .env                   # Environment variables (create this)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── templates/
│   └── index.html         # Main chat interface
└── static/
    ├── styles.css         # Styling
    └── script.js          # Frontend JavaScript
```

## API Endpoints

### POST /chat
Send a message to the AI

**Request:**
```json
{
  "message": "Hello, how are you?"
}
```

**Response:**
```json
{
  "response": "I'm doing well, thank you for asking!",
  "timestamp": "2026-04-03T12:34:56.789012"
}
```

### GET /history
Retrieve conversation history

**Response:**
```json
{
  "history": [
    {
      "_id": "...",
      "user_message": "Hello",
      "ai_response": "Hi! How can I help?",
      "timestamp": "2026-04-03T12:34:56.789012"
    }
  ]
}
```

### DELETE /history
Clear all conversation history

**Response:**
```json
{
  "message": "Chat history cleared successfully",
  "deleted_count": 5
}
```

## Usage

1. **Send a Message:** Type a message in the input field and press Enter or click "Send"
2. **View History:** All messages are automatically loaded and displayed on page load
3. **Clear History:** Click the "Clear History" button to delete all conversations
4. **Message Timestamps:** Each message shows the time it was sent

## AI Model Choice: Anthropic Claude API

### Why Claude?
-  **Free Tier:** 100K tokens per month free (generous for learning and testing)
-  **Quality:** State-of-the-art reasoning and text generation capabilities
-  **Reliability:** Highly stable and well-maintained API
-  **Easy Setup:** Simple SDK with excellent documentation
-  **No Credit Card Required:** Free tier available without signup hassle

### Alternative Options
If you want to use a different AI model:

**Google Gemini API:** Fast inference, generous free tier
```python
# Update requirements.txt
google-generativeai==0.7.0

# Update app.py to use Google's SDK
```

**OpenAI GPT:** More capable but requires payment
```python
# Update requirements.txt
openai==1.0.0

# Use OpenAI's official SDK
```

**Groq API:** Lightning-fast inference, free tier
```python
# Update requirements.txt
groq

# Use Groq's SDK for ultra-fast responses
```

## Challenges Faced & Solutions

### 1. **MongoDB Connection Issues**
- **Challenge:** Failed to connect to MongoDB on first attempt
- **Solution:** Implemented try-catch with clear error messages and fallback handling

### 2. **CORS Errors**
- **Challenge:** Frontend couldn't communicate with backend
- **Solution:** Implemented Flask-CORS to handle cross-origin requests

### 3. **API Rate Limiting**
- **Challenge:** Gemini API has rate limits
- **Solution:** Added proper error handling and user feedback for failed requests

### 4. **Chat State Management**
- **Challenge:** Keeping chat history in sync between frontend and database
- **Solution:** Load history on page load and save after each message

### 5. **Responsive Design**
- **Challenge:** UI needed to work on mobile and desktop
- **Solution:** Used CSS flexbox and media queries for responsive layout

## Error Handling

The application includes comprehensive error handling:

- **API Errors:** Clear error messages displayed to user
- **Database Errors:** Graceful fallback if MongoDB is unavailable
- **Network Errors:** User-friendly error messages
- **Input Validation:** Empty message prevention
- **Server Errors:** Proper HTTP status codes and error responses

## Future Enhancements

- [ ] User authentication and multiple conversations
- [ ] Conversation naming and organization
- [ ] Export chat as PDF
- [ ] Conversation search functionality
- [ ] Custom AI model selection
- [ ] Message editing and deletion
- [ ] Voice input/output
- [ ] Dark mode toggle
- [ ] Deployment to Heroku/Railway/Vercel

## License

This project is open source and free to use for educational purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error messages in browser console (F12)
3. Check Flask server logs for backend errors
4. Verify all credentials in `.env` file

---

**Happy Chatting!**
