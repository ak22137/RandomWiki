# 🚀 Deployment Guide

## Quick Fix for Vercel Build Error

The error you encountered was due to the Flask app initialization checking for the API key at import time. This has been fixed by:

1. **Lazy initialization**: The Gemini client is now initialized per-request instead of at module import
2. **Updated vercel.json**: Added proper static file handling for the `/static` folder
3. **Proper Flask app export**: The `app` object is now available at module level for Vercel

## Deploying to Vercel

### Option 1: Vercel Dashboard (Recommended)

1. **Push to GitHub**:
   ```powershell
   git add .
   git commit -m "Fix Vercel deployment configuration"
   git push origin main
   ```

2. **Import in Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Git Repository"
   - Select your `RandomWiki` repository
   - Click "Import"

3. **Configure Environment Variables**:
   - Before deploying, click "Environment Variables"
   - Add variable:
     - **Name**: `GEMINI_API_KEY`
     - **Value**: Your Gemini API key from [aistudio.google.com](https://aistudio.google.com/app/apikey)
   - Select all environments (Production, Preview, Development)
   - Click "Add"

4. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete (~1-2 minutes)
   - Your app will be live at `your-project.vercel.app`

### Option 2: Vercel CLI

```powershell
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (run from project root)
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Select your account
# - Link to existing project? No
# - What's your project's name? RandomWiki
# - In which directory is your code located? ./

# Add environment variable
vercel env add GEMINI_API_KEY production
# Paste your API key when prompted

# Deploy to production
vercel --prod
```

## Deploying to Render

1. **Create new Web Service**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: RandomWiki
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

3. **Add Environment Variable**:
   - Scroll to "Environment Variables"
   - Add: `GEMINI_API_KEY` = your API key

4. **Create Web Service**:
   - Click "Create Web Service"
   - Wait for deployment

## Troubleshooting

### Build fails with "No flask entrypoint found"
- **Fixed**: The app now properly exports the `app` object
- Make sure you've committed the latest changes

### Runtime error: "GEMINI_API_KEY not found"
- Go to Vercel/Render dashboard
- Add the environment variable
- Redeploy the application

### Streaming not working
- Some platforms may not support SSE properly
- Vercel supports it natively
- For other platforms, ensure they support Server-Sent Events

## Testing Locally

Before deploying, test locally:

```powershell
# Create .env.local file
cp .env.local.example .env.local

# Edit .env.local and add your API key
# GEMINI_API_KEY=your_key_here

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Test in browser at http://localhost:5000
```

## Post-Deployment Checklist

- ✅ App loads without errors
- ✅ All three buttons are visible
- ✅ Clicking a button triggers content generation
- ✅ Content streams progressively (not all at once)
- ✅ Markdown formatting is applied (headings, bold text)
- ✅ Loading spinner appears during generation
- ✅ Buttons are disabled during generation
- ✅ No console errors in browser dev tools

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify your API key is correct
3. Test the API key locally first
4. Ensure all files are committed and pushed

Happy deploying! 🎉
