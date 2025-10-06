# Fetcha Bot - Cloud Deployment Guide
**Version:** v1.0 • Created: 2025-01-06 22:08 AEST (Brisbane)

## 🚀 Deploy to Railway.app (Recommended - 5 Minutes)

Railway is the easiest way to deploy your bot. Free tier available!

### Step 1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. Verify your account

### Step 2: Deploy from GitHub

1. Push your code to GitHub:
   ```bash
   cd /Users/willsimpson/Documents/Fields/Property\ Scraping_V3/07_Telegram_App/Exploration
   
   # Initialize git if needed
   git init
   git add .
   git commit -m "Fetcha bot initial deployment"
   
   # Create new repo on GitHub, then:
   git remote add origin https://github.com/YOUR_USERNAME/fetcha-bot.git
   git push -u origin main
   ```

2. In Railway dashboard:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `fetcha-bot` repository
   - Click "Deploy Now"

### Step 3: Add Environment Variables

In Railway dashboard:

1. Click your deployed project
2. Go to "Variables" tab
3. Add variable:
   ```
   TELEGRAM_BOT_TOKEN=8336055003:AAEMqahmVx6PYaRy8SkOcE88YnLPjrFwH3o
   ```
4. Click "Save"

### Step 4: Bot Auto-Deploys! ✅

Railway will:
- Install dependencies from `requirements.txt`
- Run your bot via `Procfile`
- Keep it running 24/7
- Auto-restart if it crashes

**Check logs:** Click "Deployments" → "View Logs"

You should see:
```
INFO - Starting Fetcha Bot...
INFO - Application started
```

### Step 5: Test Your Bot

1. Open Telegram
2. Search: `@FetchaGlobal_bot`
3. Send: `/start`
4. It works! 🎉

---

## 🌐 Alternative: Deploy to Heroku

### Prerequisites
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login
```

### Deploy Steps

```bash
cd /Users/willsimpson/Documents/Fields/Property\ Scraping_V3/07_Telegram_App/Exploration

# Create Heroku app
heroku create fetcha-global-bot

# Add environment variable
heroku config:set TELEGRAM_BOT_TOKEN=8336055003:AAEMqahmVx6PYaRy8SkOcE88YnLPjrFwH3o

# Initialize git if needed
git init
git add .
git commit -m "Initial deployment"

# Deploy
git push heroku main

# Check if it's running
heroku logs --tail
```

Should see:
```
INFO - Starting Fetcha Bot...
INFO - Application started
```

**Note:** Heroku free tier is discontinued. You'll need a paid plan (~$5/month).

---

## ⚠️ Important: Scraping Feature Limitation

### Current Limitation

The bot currently imports `test_universal_parser_approach.py` for scraping, which requires the entire parent directory structure. This won't work in cloud deployment.

### Temporary Solution

For initial cloud deployment, the scraping feature will be **disabled**. Users can still:
- ✅ Use `/start` command
- ✅ Select regions
- ✅ Use `/feedback` to send requests
- ✅ Test all bot commands
- ❌ **Cannot scrape products yet** (will show error message)

### Permanent Solution (Coming Soon)

**Option 1:** Package scraper as separate module
**Option 2:** Use API-based scraping service
**Option 3:** Implement simplified scraper in bot code

For now, focus on collecting user feedback about features they want!

---

## 📊 Monitor Your Bot

### Railway Dashboard

- **Logs:** See all bot activity in real-time
- **Metrics:** CPU, memory usage
- **Deployments:** Track each deployment
- **Variables:** Manage environment variables

### Check Database

Since Railway doesn't have persistent storage by default, you need to:

**Option 1:** Add Railway PostgreSQL
```bash
# In Railway dashboard
# Click "New" → "Database" → "PostgreSQL"
# Update bot code to use PostgreSQL instead of SQLite
```

**Option 2:** Use Railway Volume (for SQLite)
```bash
# In Railway settings
# Add volume mount: /app/data
# Update DB_PATH to /app/data/price_tracker.db
```

**Option 3:** Start without persistence
- Database recreates on each deployment
- Fine for initial testing
- Add persistence later when you have users

---

## 🔧 Troubleshooting

### Bot Not Starting?

**Check logs in Railway:**
```
Click Deployments → View Logs
```

Common issues:
- Missing environment variable
- Wrong Python version
- Dependency install failed

### Bot Starts But Doesn't Respond?

1. Verify token is correct
2. Check bot username: `@FetchaGlobal_bot`
3. Ensure bot is not blocked by Telegram

### Scraping Errors?

Expected! Scraping feature disabled in cloud for now.
Bot will show: "Feature temporarily unavailable"

---

## 💰 Cost Comparison

### Railway
- **Free Tier:** $5 credit/month (enough for small bot)
- **Pro:** $20/month (recommended for production)
- **Pros:** Easy, great UI, good logs
- **Cons:** Free tier limited

### Heroku
- **Free Tier:** Discontinued
- **Paid:** $7/month minimum
- **Pros:** Reliable, well-documented
- **Cons:** More expensive than Railway

### DigitalOcean
- **Droplet:** $4-6/month
- **Pros:** Full control, SSH access
- **Cons:** Manual setup, need Linux knowledge

**Recommendation:** Start with Railway. Easiest and reliable.

---

## 🚀 Quick Railway Deploy Checklist

- [ ] Create Railway account
- [ ] Push code to GitHub
- [ ] Create new Railway project from GitHub
- [ ] Add `TELEGRAM_BOT_TOKEN` environment variable
- [ ] Wait for deployment (~2 minutes)
- [ ] Check logs for "Application started"
- [ ] Test bot on Telegram: `/start`
- [ ] Configure bot via @BotFather (description, commands)
- [ ] Invite beta testers!

---

## 📝 Files Needed for Deployment

Your repository should have:

```
07_Telegram_App/Exploration/
├── telegram_price_tracker_mvp.py  ✅ Main bot code
├── requirements.txt                ✅ Python dependencies
├── Procfile                        ✅ Tells Railway how to run bot
├── .env                            ⚠️  DO NOT commit this!
└── README.md                       ✅ Documentation
```

**Important:** Add `.env` to `.gitignore`:
```bash
echo ".env" >> .gitignore
echo "*.db" >> .gitignore
echo "__pycache__/" >> .gitignore
```

---

## 🎯 After Deployment

### 1. Set Bot Profile (@BotFather)

```
/setdescription
Select: @FetchaGlobal_bot
Send: Fetcha - Track product prices automatically. Free beta!

/setabouttext
Select: @FetchaGlobal_bot
Send: Multi-market price tracking bot for business owners. Beta testing!

/setcommands
Select: @FetchaGlobal_bot
Send:
start - Start the bot
feedback - Send feedback
help - Get help
```

### 2. Test All Features

- [ ] `/start` - Region selection works
- [ ] `/feedback` - Feedback submission works
- [ ] `/help` - Help text displays
- [ ] Error handling for scraping (expected to fail gracefully)

### 3. Invite Beta Testers

Share: **https://t.me/FetchaGlobal_bot**

Focus on collecting feedback about:
- What platforms they want supported
- What data points matter most
- How often they need updates
- What they'd pay for this

---

## ✅ Success Criteria

Your bot is successfully deployed when:

1. ✅ Railway shows "Deployed" status
2. ✅ Logs show "Application started"
3. ✅ Bot responds to `/start` on Telegram
4. ✅ Users can select regions
5. ✅ Feedback system works
6. ✅ No crashes in logs for 24 hours

---

## 🎉 You're Live!

Once deployed to Railway, your bot runs 24/7 with:
- ✅ Automatic restarts
- ✅ Easy updates (just push to GitHub)
- ✅ Log monitoring
- ✅ No network issues
- ✅ Free tier to start

**Bot URL:** https://t.me/FetchaGlobal_bot

Ready to collect real user feedback! 🚀
