# Quick Start: SEFS with Gemini AI (5 Minutes)

Get SEFS running with free AI-powered naming in 5 minutes!

## 1. Get Gemini API Key (2 minutes)

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy...`)

## 2. Configure SEFS (1 minute)

Create `backend/.env` file:

```bash
GEMINI_API_KEY=AIzaSy...paste_your_key_here
MODEL_NAME=gemini/gemini-1.5-flash
```

## 3. Install Dependencies (1 minute)

```bash
cd backend
pip install python-dotenv langchain-google-genai
```

## 4. Start SEFS (1 minute)

**Windows:**
```cmd
START.bat
```

**Unix/Mac:**
```bash
./START.sh
```

## 5. Test It!

1. **Quick test**: `python test_ai_naming.py`
2. Open http://localhost:3000
3. Run demo: `python create_demo_files.py`
4. Watch AI organize and name your files!

---

**That's it!** Your files will now get intelligent, AI-generated folder names like:
- "Machine_Learning_Research" instead of "Cluster_0"
- "Cooking_Recipes" instead of "Cluster_1"
- "Travel_Destinations" instead of "Cluster_2"

## Troubleshooting

**API key not working?**
- Check for typos in `.env`
- Make sure file is named exactly `.env` (not `.env.txt`)
- Restart the backend after creating `.env`

**Need help?**
- See full guide: [GEMINI_SETUP.md](GEMINI_SETUP.md)
- Check logs: `backend/backend.log`

## Why Gemini?

✅ **Free** - No credit card needed
✅ **Fast** - Gemini 1.5 Flash is optimized for speed  
✅ **Generous** - 1,500 requests/day (way more than you need)
✅ **Smart** - Understands context and generates meaningful names

Enjoy! 🚀
