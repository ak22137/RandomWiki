# 📚 RandomWiki: Gemini Content Generator

A dynamic web application that generates AI-powered encyclopedia articles using Google's Gemini API with real-time streaming.

## 🚀 Features

- **Real-time Streaming**: Content streams directly from Gemini API to your browser
- **Three Pre-configured Topics**: Russia, Japan, and Mars Mission
- **Markdown Formatting**: Automatic rendering of headings, bold text, and lists
- **Responsive Design**: Beautiful gradient UI that works on all devices
- **Serverless Ready**: Optimized for deployment on Vercel, Render, or similar platforms

## 🛠️ Tech Stack

- **Backend**: Python 3.10+ with Flask
- **AI Model**: Google Gemini 1.5 Flash 8B (lightweight, efficient)
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **API Architecture**: Server-Sent Events (SSE) for streaming
- **Rate Limiting**: Built-in 5-second cooldown between requests

## 📋 Prerequisites

- Python 3.10 or higher
- A Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

## 🔧 Installation & Setup

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   
   Create a `.env` or `.env.local` file in the root directory:
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   PORT=5000
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 🌐 Deployment

### Vercel Deployment

1. **Push your code to GitHub** (if not already done)

2. **Import project in Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository

3. **Set Environment Variable**:
   - In the Vercel project settings, go to "Environment Variables"
   - Add: `GEMINI_API_KEY` = `your_actual_api_key`
   - Make sure to add it for all environments (Production, Preview, Development)

4. **Deploy**:
   - Click "Deploy"
   - Vercel will automatically build and deploy your app

**Alternative: Deploy via CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variable (first time only)
vercel env add GEMINI_API_KEY
```

### Render Deployment

1. Create a new Web Service on Render
2. Connect your repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Add `GEMINI_API_KEY`

## 📁 Project Structure

```
RandomWiki/
├── app.py                    # Flask backend with streaming endpoint
├── requirements.txt          # Python dependencies
├── .env.local.example       # Example environment variables
├── .gitignore               # Git ignore rules
├── README.md                # This file
└── static/
    └── index.html           # Frontend (HTML + CSS + JavaScript)
```

## 🎯 How It Works

1. **User clicks a button** (e.g., "Generate Page: Russia")
2. **Frontend sends POST request** to `/generate-content` with the topic
3. **Backend constructs a prompt** instructing Gemini to write an encyclopedia article
4. **Gemini API streams response** chunk by chunk
5. **Backend forwards chunks** to frontend via Server-Sent Events
6. **Frontend processes chunks** with TextDecoder and getReader()
7. **JavaScript applies Markdown formatting** in real-time
8. **Content appears progressively** in the display area

## 🎨 Customization

### Add More Topics

Edit `static/index.html` and add new buttons:

```html
<button onclick="generateContent('Your Topic')">
    🔹 Generate Page: Your Topic
</button>
```

### Modify AI Behavior

Edit the prompt in `app.py` (line ~45) to change the writing style, length, or format.

### Change Styling

Modify the `<style>` section in `static/index.html` to customize colors, fonts, and layout.

## 🐛 Troubleshooting

**Issue**: "GEMINI_API_KEY environment variable is required"
- **Solution**: Make sure your `.env.local` file exists and contains the API key

**Issue**: Stream not displaying
- **Solution**: Check browser console for errors, verify API key is valid

**Issue**: 429 Rate Limit Error
- **Solution**: Wait a moment and try again, or upgrade your Gemini API quota

## 📝 License

MIT License - feel free to use this project for learning or commercial purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 👏 Credits

Built with ❤️ using Google Gemini API and Flask
