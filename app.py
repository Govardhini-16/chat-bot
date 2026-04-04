from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

# Get the directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, '.env')

# Load environment variables from the .env file
load_dotenv(ENV_FILE, override=True)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configure APIs and Database
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'chatbot')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'conversations')

# Debug: Print if API key is loaded
if NVIDIA_API_KEY:
    masked_key = NVIDIA_API_KEY[:20] + '...' if len(NVIDIA_API_KEY) > 20 else NVIDIA_API_KEY
    print(f"✅ NVIDIA API Key loaded: {masked_key}")
else:
    print("❌ WARNING: NVIDIA_API_KEY not found in .env file")

# Initialize NVIDIA AI client (OpenAI compatible)
if NVIDIA_API_KEY and NVIDIA_API_KEY != 'your_api_key_here':
    try:
        nvidia_client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=NVIDIA_API_KEY
        )
        print("✅ NVIDIA API configured successfully (using OpenAI-compatible interface)")
    except Exception as e:
        print(f"❌ Failed to initialize NVIDIA client: {e}")
        nvidia_client = None
else:
    print("❌ WARNING: NVIDIA_API_KEY not configured in .env file")
    print("   Please add your NVIDIA API key to .env: NVIDIA_API_KEY=nvapi_...")
    nvidia_client = None

# Initialize MongoDB
try:
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    # Test connection
    client.admin.command('ping')
    print("MongoDB connected successfully!")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    collection = None


@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')


def extract_response_from_thinking(text):
    """
    Extract the final response from a text that may contain thinking tags.
    Removes <think>...</think>, </think>, and other XML-like tags, keeping only the actual response.
    """
    import re
    
    # Remove all thinking tags and their content
    # Handle <think>...</think>
    text = re.sub(r'<\s*think\s*>.*?<\s*/\s*think\s*>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Handle <thinking>...</thinking>
    text = re.sub(r'<\s*thinking\s*>.*?<\s*/\s*thinking\s*>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Handle stray closing tags
    text = re.sub(r'<\s*/\s*think\s*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*/\s*thinking\s*>', '', text, flags=re.IGNORECASE)
    
    # Handle {{think|...}} format
    text = re.sub(r'\{\{think\|.*?\}\}', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\n\s*\n+', '\n', text)  # Remove multiple blank lines
    text = ' '.join(text.split())  # Normalize whitespace
    text = text.strip()
    
    return text


@app.route('/chat', methods=['POST'])
def chat():
    """
    POST /chat endpoint
    Accepts: JSON with 'message' field
    Returns: JSON with 'response' field
    Saves conversation to MongoDB
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message field is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if not nvidia_client:
            return jsonify({
                'error': 'AI service not configured. Please add your NVIDIA API key to the .env file: NVIDIA_API_KEY=nvapi_...'
            }), 503
        
        # Call NVIDIA API using OpenAI-compatible interface
        try:
            completion = nvidia_client.chat.completions.create(
                model="qwen/qwq-32b",
                messages=[
                    {"role": "user", "content": user_message}
                ],
                temperature=0.6,
                top_p=0.7,
                max_tokens=1024
            )
            
            # Extract text from response
            raw_response = completion.choices[0].message.content
            
            # Clean up the response by removing thinking tags
            ai_response = extract_response_from_thinking(raw_response)
            
            # Fallback if nothing left after cleaning
            if not ai_response:
                ai_response = raw_response
        
        except Exception as e:
            print(f"NVIDIA API error: {e}")
            return jsonify({'error': f'AI service error: {str(e)}'}), 503
        
        # Save to MongoDB
        timestamp = datetime.utcnow()
        conversation_entry = {
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': timestamp
        }
        
        if collection:
            try:
                collection.insert_one(conversation_entry)
            except Exception as e:
                print(f"Database save error: {e}")
                # Still return response even if database save fails
        
        return jsonify({
            'response': ai_response,
            'timestamp': timestamp.isoformat()
        }), 200
    
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/history', methods=['GET'])
def get_history():
    """
    GET /history endpoint
    Returns: Full conversation history from MongoDB
    """
    try:
        if not collection:
            return jsonify({'error': 'Database not available'}), 503
        
        # Retrieve all conversations, sorted by timestamp
        history = list(collection.find(
            {},
            {'_id': 1, 'user_message': 1, 'ai_response': 1, 'timestamp': 1}
        ).sort('timestamp', 1))
        
        # Convert MongoDB ObjectId to string for JSON serialization
        for entry in history:
            entry['_id'] = str(entry['_id'])
            if isinstance(entry['timestamp'], datetime):
                entry['timestamp'] = entry['timestamp'].isoformat()
        
        return jsonify({'history': history}), 200
    
    except Exception as e:
        print(f"History endpoint error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/history', methods=['DELETE'])
def delete_history():
    """
    DELETE /history endpoint
    Clears all conversation history from MongoDB
    """
    try:
        if not collection:
            return jsonify({'error': 'Database not available'}), 503
        
        result = collection.delete_many({})
        
        return jsonify({
            'message': 'Chat history cleared successfully',
            'deleted_count': result.deleted_count
        }), 200
    
    except Exception as e:
        print(f"Delete history error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
