import os
from flask import Flask, request, Response, send_from_directory
from google import genai
from google.genai import types
import json
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta

# Load environment variables from .env.local file
load_dotenv('.env.local')

app = Flask(__name__, static_folder='static')

# Rate limiting: Track last request time
last_request_time = None
MIN_REQUEST_INTERVAL = 5  # Minimum 5 seconds between requests

def get_gemini_client():
    """Initialize Gemini client with API key"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    return genai.Client(api_key=api_key)

def check_rate_limit():
    """Enforce minimum time between requests"""
    global last_request_time
    
    if last_request_time:
        elapsed = time.time() - last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - elapsed
            raise Exception(f"Please wait {int(wait_time)} seconds before making another request. This prevents rate limiting.")
    
    last_request_time = time.time()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')

@app.route('/test-api', methods=['GET'])
def test_api():
    """Test if the Gemini API is accessible"""
    try:
        client = get_gemini_client()
        # Try a simple, short request
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="Say 'API is working!' in 3 words."
        )
        return {'status': 'success', 'message': 'API is working!'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/generate-content', methods=['POST'])
def generate_content():
    """Stream content generation from Gemini API"""
    try:
        # Check rate limit first
        try:
            check_rate_limit()
        except Exception as e:
            return Response(
                json.dumps({'error': str(e)}),
                status=429,
                mimetype='application/json'
            )
        
        # Get topic from request
        data = request.get_json()
        topic = data.get('topic', '')
        
        if not topic:
            return Response(
                json.dumps({'error': 'Topic is required'}),
                status=400,
                mimetype='application/json'
            )
        
        # Construct prompt for Gemini
        prompt = f"""You are an expert encyclopedia writer. Generate a comprehensive article about "{topic}".

Requirements:
- Use proper Markdown formatting
- Include a main title with ## (H2 heading)
- Organize with ### (H3) subheadings
- Use **bold** for key terms
- Write 3-4 detailed paragraphs
- Length: approximately 400-600 words

Topic: {topic}

Begin writing:"""
        
        def generate():
            """Generator function to stream content from Gemini"""
            try:
                # Initialize client for this request
                client = get_gemini_client()
                
                print(f"Starting content generation for topic: {topic}")
                
                # Call Gemini API with streaming - NO RETRY, just once
                response = client.models.generate_content_stream(
                    model='gemini-2.0-flash-exp',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=1500,
                    )
                )
                
                # Stream each chunk as it arrives
                for chunk in response:
                    if hasattr(chunk, 'text') and chunk.text:
                        print(f"Sending chunk: {chunk.text[:50]}...")
                        # Send each text chunk to the frontend
                        yield f"data: {json.dumps({'text': chunk.text})}\n\n"
                
                # Send completion signal
                print("Stream completed successfully")
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                # Send error to frontend
                error_message = str(e)
                print(f"Error during generation: {error_message}")
                
                # Check if it's a rate limit error
                if '429' in error_message or 'RESOURCE_EXHAUSTED' in error_message:
                    # Extract retry time if available
                    if 'retry in' in error_message.lower():
                        yield f"data: {json.dumps({'error': 'Rate limit exceeded. Please wait about 40 seconds and try again. The free tier has limited requests per minute.'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'error': 'Rate limit exceeded. Please wait a moment and try again.'})}\n\n"
                else:
                    yield f"data: {json.dumps({'error': error_message})}\n\n"
        
        # Return streaming response with proper headers
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=500,
            mimetype='application/json'
        )

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
