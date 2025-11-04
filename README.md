# TruthFi - Complete Setup Guide

## 🚀 Quick Start (5 Minutes)

This guide will get you from zero to a working prototype in under 5 minutes!

---

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- A Reddit account (for free API access)

---

## Part 1: Backend Setup

### Step 1: Create Project Structure

```bash
# Create main project folder
mkdir truthfi
cd truthfi

# Create backend folder
mkdir backend
cd backend
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn praw python-dotenv
```

### Step 3: Get Reddit API Credentials (FREE!)

1. Go to: https://www.reddit.com/prefs/apps
2. Scroll to bottom and click **"create another app..."**
3. Fill out the form:
   - **name**: TruthFi
   - **App type**: Select **"script"**
   - **description**: Crypto scam detection
   - **about url**: (leave blank)
   - **redirect uri**: http://localhost:8000
4. Click **"create app"**
5. You'll see your credentials:
   - **client_id**: (under "personal use script")
   - **client_secret**: (next to "secret")

### Step 4: Create .env File

Create a file called `.env` in the backend folder:

```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

Replace with your actual credentials from Step 3!

### Step 5: Add the Python Files

Create these files in your backend folder:

1. **reddit_collector.py** - (Copy from artifact)
2. **pattern_detector.py** - (Copy from artifact)
3. **truth_scorer.py** - (Copy from artifact)
4. **main.py** - (Copy from artifact)

### Step 6: Run the Backend

```bash
# Make sure you're in the backend folder with venv activated
python main.py
```

You should see:
```
🚀 TruthFi API Starting Up
✓ FastAPI server initialized
📡 API available at: http://localhost:8000
```

**Keep this terminal running!**

---

## Part 2: Frontend Setup

### Step 1: Create Next.js App

Open a **NEW terminal** (keep backend running in the other one):

```bash
# Go back to main project folder
cd ..  # (if you're still in backend folder)

# Create Next.js app
npx create-next-app@latest frontend

# When prompted:
# ✓ TypeScript? Yes
# ✓ ESLint? Yes  
# ✓ Tailwind CSS? Yes
# ✓ src/ directory? No
# ✓ App Router? Yes
# ✓ Customize import alias? No
```

### Step 2: Install Extra Dependencies

```bash
cd frontend
npm install lucide-react
```

### Step 3: Replace the Home Page

Replace the contents of `app/page.tsx` with the code from the artifact.

### Step 4: Run the Frontend

```bash
npm run dev
```

You should see:
```
✓ Ready on http://localhost:3000
```

---

## 🎉 Test Your Application!

1. Open your browser to: **http://localhost:3000**
2. Type in a token symbol like: **BTC**
3. Click **Analyze**
4. Wait 5-10 seconds (it's searching Reddit)
5. See your results!

---

## Project Structure

Your final structure should look like this:

```
truthfi/
├── backend/
│   ├── venv/
│   ├── .env
│   ├── reddit_collector.py
│   ├── pattern_detector.py
│   ├── truth_scorer.py
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── app/
    │   └── page.tsx
    ├── package.json
    └── node_modules/
```

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'praw'`
```bash
# Make sure venv is activated
pip install praw fastapi uvicorn python-dotenv
```

**Problem**: `Invalid Reddit credentials`
```bash
# Check your .env file
# Make sure there are no quotes around the values
# Should be: REDDIT_CLIENT_ID=abc123
# NOT: REDDIT_CLIENT_ID="abc123"
```

**Problem**: `Port 8000 already in use`
```bash
# Kill the process on port 8000
# Mac/Linux:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F
```

### Frontend Issues

**Problem**: `Failed to fetch`
```bash
# Make sure backend is running on http://localhost:8000
# Check browser console for CORS errors
```

**Problem**: `Module not found: lucide-react`
```bash
npm install lucide-react
```

### Reddit API Issues

**Problem**: `No data found for token`
- Try a more popular token (BTC, ETH, DOGE)
- Check if Reddit is down: https://www.redditstatus.com

**Problem**: `Rate limit exceeded`
- Reddit free tier: 60 requests/minute
- Wait a minute and try again
- Don't spam the analyze button

---

## Testing Different Tokens

Try these to see different results:

**Low Risk** (legitimate projects):
- BTC
- ETH
- SOL

**High Risk** (often mentioned in pump schemes):
- PEPE
- SHIB
- Check r/CryptoMoonShots for new ones

**Trending** (click "View Trending Tokens" to see what's hot)

---

## Next Steps

### Add Telegram Scraping (Optional)

1. Get Telegram API credentials: https://my.telegram.org
2. Add to `.env`:
```bash
TELEGRAM_API_ID=your_id
TELEGRAM_API_HASH=your_hash
```
3. Create `telegram_collector.py` (similar to Reddit collector)

### Add Local AI (Optional)

1. Install Ollama: https://ollama.ai
2. Run: `ollama pull llama3`
3. Create `local_ai_analyzer.py`
4. Much better scam detection!

### Deploy to Production

**Backend**:
- Railway.app (free tier)
- Render.com (free tier)
- Fly.io (free tier)

**Frontend**:
- Vercel (unlimited free)
- Netlify (free)

### Add Database

Currently everything is in-memory. To save results:

```bash
pip install sqlalchemy psycopg2-binary
# Use Supabase free PostgreSQL
```

---

## Costs Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| Reddit API | **$0** | 60 requests/min |
| Hosting (Railway) | **$0** | 500 hours/month free |
| Hosting (Vercel) | **$0** | Unlimited |
| Domain | **$12/year** | Optional |
| **Total** | **$0-12/year** | 🎉 |

---

## API Endpoints

Your backend exposes these endpoints:

- `POST /api/analyze` - Analyze a token
- `GET /api/trending` - Get trending tokens
- `GET /api/sentiment/{symbol}` - Get token sentiment
- `GET /api/health` - Health check

Test in browser:
- http://localhost:8000/docs (interactive API docs)
- http://localhost:8000/api/trending

---

## Development Tips

### Auto-reload on Changes

Both servers auto-reload:
- **Backend**: Changes to .py files auto-reload
- **Frontend**: Changes to .tsx files auto-reload

### View Logs

- **Backend**: Check terminal running `python main.py`
- **Frontend**: Check browser console (F12)

### Debug Mode

Add print statements in Python:
```python
print(f"Analyzing token: {token_symbol}")
print(f"Found {len(posts)} posts")
```

---

## Common Use Cases

### Analyze Before Buying
```
User: Should I buy this new token I saw on Twitter?
You: Enter the symbol in TruthFi first!
```

### Check Trending Tokens
```
Click "View Trending" to see what's hot on Reddit
Quick-analyze popular tokens
```

### Report Scams
```
High risk score? Share results with community
Help others avoid scams
```

---

## Performance Notes

- First analysis: 5-10 seconds (collecting from Reddit)
- Subsequent analyses: 3-5 seconds (if similar data)
- Trending tokens: 1-2 seconds

**Why is it slow?**
- Reddit API has rate limits
- Fetching 100+ posts takes time
- Analysis is thorough

**Speed it up:**
- Reduce post_limit in request (default 100)
- Add caching with Redis
- Use background tasks

---

## Security Notes

**Important**: 
- Never commit your `.env` file to Git
- Add `.env` to `.gitignore`
- Rotate Reddit credentials if exposed

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "node_modules/" >> .gitignore
```

---

## Getting Help

**Issues?**
1. Check the Troubleshooting section above
2. Make sure both servers are running
3. Check browser console for errors
4. Check terminal for error messages

**Want to contribute?**
- Add more data sources
- Improve scoring algorithms
- Add more visualizations
- Build mobile app

---

## What's Next?

You now have a working crypto scam detector! 🎉

**Immediate improvements:**
1. Add user accounts (Clerk/Supabase Auth)
2. Save analysis history
3. Add watchlists
4. Email/SMS alerts
5. Mobile app with React Native

**Advanced features:**
1. Real-time monitoring
2. Telegram integration
3. On-chain analysis
4. Machine learning models
5. Community reporting

---

## License

MIT License - feel free to use and modify!

---

## Support

Found this useful? Star the repo and share with friends!

**Stay safe out there! 🛡️**