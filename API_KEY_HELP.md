# 🔑 How to Get a Working Gemini API Key

## The Problem
Your current API key shows `limit: 0` which means it has no quota or is exhausted.

## Solution: Create a New API Key

### Step 1: Go to Google AI Studio
Visit: https://aistudio.google.com/app/apikey

### Step 2: Sign in with a Different Google Account (if possible)
- If you have another Gmail account, use it
- OR use the same account but create a new API key

### Step 3: Create API Key
1. Click "Create API Key"
2. Select "Create API key in new project" (don't reuse old project)
3. Copy the new API key

### Step 4: Update Your .env.local File
Replace the API key in `d:\Projects\RandomWiki\.env.local`:
```
GEMINI_API_KEY=YOUR_NEW_API_KEY_HERE
```

### Step 5: Restart the Flask Server
Press Ctrl+C in the terminal running the Flask server, then:
```powershell
.\venv\Scripts\Activate.ps1; python app.py
```

## Alternative: Enable Billing

If you want higher limits:
1. Go to https://console.cloud.google.com/
2. Select your project
3. Enable billing
4. This gives you much higher quotas

## Free Tier Limits (After Fresh Key)
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

## Current Status
Your key shows these violations:
- `generate_content_free_tier_requests` - limit: 0
- `generate_content_free_tier_input_token_count` - limit: 0

This means the key needs to be replaced or billing needs to be enabled.
