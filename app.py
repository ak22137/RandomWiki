from flask import Flask, Response, request, jsonify, send_from_directory
import os
from mistralai import Mistral
from dotenv import load_dotenv
import time
import json
import re

# Load environment variables from .env.local file
load_dotenv('.env.local')

app = Flask(__name__, static_folder='static')

# Rate limiting: Track last request time
last_request_time = None
MIN_REQUEST_INTERVAL = 5  # Minimum 5 seconds between requests

def load_prompt(prompt_number):
    """Load prompt from external txt file"""
    prompt_file = f"prompt{prompt_number}.txt"
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise Exception(f"Prompt file {prompt_file} not found!")

def get_mistral_client():
    """Initialize Mistral client with API key"""
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is required")
    return Mistral(api_key=api_key)

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
    """Test if the Mistral API is accessible"""
    try:
        client = get_mistral_client()
        # Try a simple, short request
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": "Say 'API is working!' in 3 words."}]
        )
        return {'status': 'success', 'message': 'API is working!'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/generate-initial-ui', methods=['POST'])
def generate_initial_ui():
    """
    Generate initial UI with random topics - Mistral creates the HTML structure
    """
    try:
        print("Generating initial UI with Mistral AI...")
        
        client = get_mistral_client()
        
        prompt = """Generate HTML and CSS for a topic selection page with 6 diverse, VISUAL topics that can have interactive demonstrations.

Requirements:
1. Return a JSON object with two properties: "html" and "css"
2. HTML should include:
   - A header with title "RandomWiki Explorer"
   - 6 topic buttons with emojis (use onclick="generateTopicPage('TopicName')")
   - Each button should have a unique color/gradient
   - Grid layout
3. CSS should be modern with gradients, shadows, hover effects
4. Choose VISUAL/INTERACTIVE topics like:
   - Science: Parabola, Wave Motion, Pendulum, Solar System, DNA Structure
   - Physics: Projectile Motion, Simple Harmonic Motion, Electromagnetic Waves
   - Math: Fibonacci Spiral, Fractal Patterns, Sine Wave
   - Transportation: Moving Car, Flying Plane, Sailing Ship
   - Nature: Growing Tree, Blooming Flower, Ocean Waves
   - Technology: Digital Clock, Analog Clock, Speedometer
   - Music: Piano Keys, Sound Waves, Musical Notes
   - Space: Orbiting Planets, Rocket Launch, Galaxy Rotation
5. Mix categories: at least 2 math/science, 2 visual phenomena, 2 interactive objects
6. Return ONLY valid JSON, no markdown

Example: {{"html": "<div>...</div>", "css": ".button {{ ... }}"}}

Generate now:"""
        
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"AI response received, length: {len(response_text)}")
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            ui_data = json.loads(json_match.group())
            return jsonify({
                'success': True,
                'html': ui_data.get('html', ''),
                'css': ui_data.get('css', '')
            })
        else:
            # If AI fails, return error - NO hardcoded fallback!
            raise Exception("AI failed to generate topics. Please try again.")
            return jsonify({'success': True, 'html': html, 'css': css})
            
    except Exception as e:
        print(f"Error generating initial UI: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/generate-html', methods=['POST'])
def generate_html():
    """
    PART 1: Generate ONLY HTML structure (no CSS, no JavaScript)
    """
    try:
        data = request.get_json()
        topic = data.get('topic', 'General')
        
        print(f"[PART 1] Generating HTML for: {topic}")
        
        client = get_mistral_client()
        
        # Load prompt from external file
        prompt_template = load_prompt(1)
        prompt = prompt_template.format(topic=topic)
        
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"[PART 1] Response length: {len(response_text)}")
        
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            html_data = json.loads(json_match.group())
            html_code = html_data.get('html', '')
            print(f"[PART 1] ✅ HTML generated: {len(html_code)} chars")
            return jsonify({'success': True, 'html': html_code})
        else:
            raise Exception("No valid JSON in response")
            
    except Exception as e:
        print(f"[PART 1] ❌ Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/generate-css', methods=['POST'])
def generate_css():
    """
    PART 2: Generate ONLY CSS styles
    """
    try:
        data = request.get_json()
        topic = data.get('topic', 'General')
        
        print(f"[PART 2] Generating CSS for: {topic}")
        
        client = get_mistral_client()
        
        # Load prompt from external file
        prompt_template = load_prompt(2)
        prompt = prompt_template.format(topic=topic)
        
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"[PART 2] Response length: {len(response_text)}")
        
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            css_data = json.loads(json_match.group())
            css_code = css_data.get('css', '')
            print(f"[PART 2] ✅ CSS generated: {len(css_code)} chars")
            return jsonify({'success': True, 'css': css_code})
        else:
            raise Exception("No valid JSON in response")
            
    except Exception as e:
        print(f"[PART 2] ❌ Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/generate-topic-ui', methods=['POST'])
def generate_topic_ui():
    """
    Generate topic-specific UI with INTERACTIVE VISUALIZATIONS - Mistral creates themed HTML/CSS/JS
    """
    try:
        data = request.get_json()
        topic = data.get('topic', 'General Knowledge')
        
        print(f"Generating INTERACTIVE topic UI for: {topic}")
        
        client = get_mistral_client()
        
        # Load prompt from external file
        prompt_template = load_prompt(3)
        prompt = prompt_template.format(topic=topic)
        
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"Interactive UI response received for {topic}")
        print(f"Response length: {len(response_text)} characters")
        print(f"First 200 chars: {response_text[:200]}")
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                ui_data = json.loads(json_match.group())
                print(f"Successfully parsed JSON. Keys: {ui_data.keys()}")
                
                # Check if JavaScript is present
                has_js = 'javascript' in ui_data and ui_data.get('javascript')
                js_length = len(ui_data.get('javascript', '')) if has_js else 0
                print(f"JavaScript present: {has_js}, Length: {js_length} chars")
                if has_js:
                    print(f"First 100 chars of JS: {ui_data.get('javascript', '')[:100]}")
                
                return jsonify({
                    'success': True,
                    'html': ui_data.get('html', ''),
                    'css': ui_data.get('css', ''),
                    'javascript': ui_data.get('javascript', ''),
                    'startStreaming': True
                })
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                raise Exception(f"Failed to parse AI response: {e}")
        else:
            print("No JSON found in response")
            raise Exception("AI failed to generate UI for topic. Please try again.")
            
    except Exception as e:
        print(f"Error generating topic UI: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/generate-animation', methods=['POST'])
def generate_animation():
    """
    ROUND 2: Generate JavaScript animation code for the visualization
    """
    try:
        data = request.get_json()
        topic = data.get('topic', 'General')
        
        print(f"Generating ANIMATION for: {topic}")
        
        client = get_mistral_client()
        
        # Load prompt from external file
        prompt_template = load_prompt(4)
        prompt = prompt_template.format(topic=topic)
        
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"Animation response received, length: {len(response_text)}")
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                anim_data = json.loads(json_match.group())
                js_code = anim_data.get('javascript', '')
                print(f"Animation JavaScript: {len(js_code)} chars")
                print(f"First 150 chars: {js_code[:150]}")
                
                return jsonify({
                    'success': True,
                    'javascript': js_code
                })
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                return jsonify({'success': False, 'error': f"Parse error: {e}"}), 500
        else:
            print("No JSON found in animation response")
            return jsonify({'success': False, 'error': 'No valid JSON in response'}), 500
            
    except Exception as e:
        print(f"Error generating animation: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500





@app.route('/generate-content', methods=['POST'])
def generate_content():
    """Stream content generation from Mistral API"""
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
        
        # Construct prompt for Mistral - MINIMAL TEXT, focus on visualization
        prompt_template = load_prompt(5)
        prompt = prompt_template.format(topic=topic)
        
        def generate():
            """Generator function to stream content from Mistral"""
            try:
                # Initialize client for this request
                client = get_mistral_client()
                
                print(f"Starting content generation for topic: {topic}")
                
                # Call Mistral API with streaming
                response = client.chat.stream(
                    model="mistral-small-latest",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=200,  # Limit tokens to ensure brief content
                )
                
                # Stream each chunk as it arrives
                for chunk in response:
                    if chunk.data.choices[0].delta.content:
                        text = chunk.data.choices[0].delta.content
                        print(f"Sending chunk: {text[:50]}...")
                        # Send each text chunk to the frontend
                        yield f"data: {json.dumps({'text': text})}\n\n"
                
                # Send completion signal
                print("Stream completed successfully")
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                # Send error to frontend
                error_message = str(e)
                print(f"Error during generation: {error_message}")
                
                # Check if it's a rate limit error
                if '429' in error_message or 'rate limit' in error_message.lower():
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
