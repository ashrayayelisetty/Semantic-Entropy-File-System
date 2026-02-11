# Setting Up Gemini AI for SEFS

This guide shows you how to configure SEFS to use Google's Gemini AI for intelligent folder naming - completely free!

## Why Gemini?

- **100% Free**: No credit card required
- **Generous Limits**: 15 requests per minute, 1500 per day
- **Fast & Reliable**: Gemini 1.5 Flash is optimized for speed
- **Easy Setup**: Get your API key in under 2 minutes

## Step-by-Step Setup

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated API key

### 2. Configure SEFS

1. Navigate to the `backend` directory:
   ```bash
   cd sefs-project/backend
   ```

2. Create a `.env` file (or copy from the example):
   ```bash
   # Windows
   copy .env.example .env
   
   # Unix/Mac
   cp .env.example .env
   ```

3. Edit the `.env` file and add your Gemini API key:
   ```bash
   # backend/.env
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   MODEL_NAME=gemini/gemini-1.5-flash
   ```

4. Save the file

### 3. Install Required Dependencies

Make sure you have the latest dependencies installed:

```bash
# Activate your virtual environment first
# Windows:
venv\Scripts\activate

# Unix/Mac:
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

This will install:
- `python-dotenv` - For loading environment variables
- `langchain-google-genai` - For Gemini API integration
- `langchain-openai` - For OpenAI API integration (optional)
- `crewai` - For AI agent orchestration

### 4. Test Your Setup

**Quick Test:**

```bash
# From project root
python test_ai_naming.py
```

This will verify:
- Environment variables are loaded
- AI namer initializes correctly
- Naming functionality works

**Full Test:**

Start the SEFS backend:

```bash
# From the backend directory
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Check the logs - you should see:
```
INFO:     Started server process
INFO:ai_namer:Using Gemini AI for naming
INFO:     Application startup complete.
```

If you see any errors about the API key, double-check your `.env` file.

### 5. Test AI Naming

1. Add some demo files:
   ```bash
   # From project root
   python create_demo_files.py
   ```

2. Trigger AI naming via the API:
   ```bash
   curl -X POST http://localhost:8000/generate-names
   ```

3. Check the response - you should see AI-generated folder names!

## How It Works

When you trigger AI naming:

1. SEFS analyzes the content of files in each cluster
2. Sends cluster summaries to Gemini (not full file contents)
3. Gemini generates meaningful, descriptive folder names
4. SEFS renames the OS folders automatically

Example:
- **Before**: `Cluster_0`, `Cluster_1`, `Cluster_2`
- **After**: `Machine_Learning_Research`, `Cooking_Recipes`, `Travel_Guides`

## Gemini API Limits

**Free Tier Limits:**
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per minute

For SEFS usage, this is more than enough! Each naming operation uses only 1-2 requests.

## Troubleshooting

### Error: "API key not valid"

**Solution**: 
- Verify your API key is correct in `.env`
- Make sure there are no extra spaces or quotes
- Try generating a new API key

### Error: "Module 'litellm' not found"

**Solution**:
```bash
pip install litellm python-dotenv
```

### Error: "Rate limit exceeded"

**Solution**: 
- Wait 1 minute and try again
- Gemini has a 15 requests/minute limit
- For SEFS, this is rarely an issue

### AI Naming Not Working

**Fallback Behavior**: If Gemini fails for any reason, SEFS automatically falls back to keyword-based naming. Your files will still be organized!

**Check**:
1. Is the `.env` file in the `backend` directory?
2. Is the API key correct?
3. Check backend logs for error messages
4. Try the API key in [Google AI Studio](https://aistudio.google.com/) directly

## Alternative: OpenAI

If you prefer to use OpenAI instead:

1. Get an API key from [OpenAI Platform](https://platform.openai.com/)
2. Update your `.env` file:
   ```bash
   OPENAI_API_KEY=sk-...your_key_here
   OPENAI_MODEL_NAME=gpt-4o-mini
   ```

**Note**: OpenAI requires a paid account with credits.

## Disabling AI Naming

To use only keyword-based naming:

1. Delete or rename the `.env` file
2. Or comment out the API key lines:
   ```bash
   # GEMINI_API_KEY=your_key_here
   ```

SEFS will automatically use keyword extraction from filenames instead.

## Privacy & Security

**What data is sent to Gemini?**
- Only cluster summaries (file names + short content previews)
- NOT full file contents
- No personal information

**Is it secure?**
- API keys are stored locally in `.env` (never committed to git)
- Communication with Gemini is encrypted (HTTPS)
- You can review the code in `backend/coordinator.py`

## Next Steps

Once Gemini is configured:

1. Run the full system with `START.bat` (Windows) or `./START.sh` (Unix/Mac)
2. Add files to `sefs_root/`
3. Watch as SEFS automatically organizes and names your folders intelligently!

## Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [CrewAI Documentation](https://docs.crewai.com/)
- [SEFS README](../README.md)

---

**Enjoy intelligent, AI-powered file organization - completely free!** 🚀
