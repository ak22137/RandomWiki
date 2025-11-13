import os
from flask import Flask, request, Response, send_from_directory
from google import genai
from google.genai import types
import json

app = Flask(__name__, static_folder='static')

def get_gemini_client():
    """Initialize Gemini client with API key"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    return genai.Client(api_key=api_key)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')

@app.route('/generate-content', methods=['POST'])
def generate_content():
    """Stream content generation from Gemini API"""
    try:
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
        prompt = f"""You are an expert encyclopedia writer. Generate a comprehensive, well-structured article about "{topic}".

Requirements:
- Use proper Markdown formatting throughout
- Include a main title with ## (H2 heading)
- Organize content with ### (H3) subheadings
- Use **bold** for emphasis on key terms
- Use bullet points where appropriate
- Write 4-6 detailed paragraphs covering different aspects
- Make it informative, engaging, and educational
- Length: approximately 500-800 words

Topic: {topic}

Begin writing the article now:"""
        
        def generate():
            """Generator function to stream content from Gemini"""
            try:
                # Initialize client for this request
                client = get_gemini_client()
                
                # Call Gemini API with streaming
                response = client.models.generate_content_stream(
                    model='gemini-2.0-flash-exp',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=2048,
                    )
                )
                
                # Stream each chunk as it arrives
                for chunk in response:
                    if chunk.text:
                        # Send each text chunk to the frontend
                        yield f"data: {json.dumps({'text': chunk.text})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                # Send error to frontend
                error_message = str(e)
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
