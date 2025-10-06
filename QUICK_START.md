# Fetcha Bot - Quick Start Guide
**Version:** v1.1 • Updated: 2025-01-06 21:56 AEST (Brisbane)
**Bot:** @FetchaGlobal_bot

## 🚀 Launch Fetcha in 30 Seconds!

### Option 1: Use the Startup Script (Recommended)

```bash
cd /Users/willsimpson/Documents/Fields/Property\ Scraping_V3/07_Telegram_App/Exploration
./start_fetcha_bot.sh
```

That's it! The script handles everything automatically.

### Option 2: Manual Start

```bash
cd /Users/willsimpson/Documents/Fields/Property\ Scraping_V3/07_Telegram_App/Exploration
export TELEGRAM_BOT_TOKEN='8336055003:AAEMqahmVx6PYaRy8SkOcE88YnLPjrFwH3o'
python3 telegram_price_tracker_mvp.py
```

---

## ✅ What You Should See

When the bot starts successfully, you'll see:

```
INFO - Starting Fetcha Bot...
INFO - Application started
```

**The bot is now running!** It will stay active until you press `Ctrl+C`.

---

## 📱 Test Your Bot

1. **Open Telegram** on your phone or desktop
2. **Search for:** `@FetchaGlobal_bot`
3. **Send:** `/start`
4. **Select your region** (e.g., 🇺🇸 USA)
5. **Send a product URL** (e.g., from Amazon, eBay, etc.)

Example URL to test:
```
https://www.amazon.com.au/dp/B08N5WRWNW
```

---

## 🔧 Configuration Complete

All setup files are ready:

✅ **Bot Token:** Set in `.env`  
✅ **Startup Script:** `start_fetcha_bot.sh` (executable)  
✅ **Database:** Will be created automatically on first run  
✅ **Backups Directory:** `backups/` created  
✅ **Dependencies:** python-telegram-bot v20.7 installed  

---

## 📊 Monitor Your Bot

### View Database Stats

```bash
cd /Users/willsimpson/Documents/Fields/Property\ Scraping_V3/07_Telegram_App/Exploration
sqlite3 price_tracker.db "SELECT * FROM users;"
```

### Check Logs

The bot outputs logs directly to the terminal. Watch for:
- User signups
- Product tracking requests
- Price change alerts
- Error messages

---

## 🛑 Stop the Bot

Press `Ctrl+C` in the terminal where the bot is running.

---

## 🎯 Next Steps

### 1. Configure Bot Profile (5 minutes)

Go to @BotFather on Telegram:

```
/setdescription
Select: @FetchaGlobal_bot
Send: Fetcha - Track product prices automatically across any e-commerce site. Get instant alerts when prices change. Free beta for business owners!
```

```
/setabouttext
Select: @FetchaGlobal_bot
Send: Fetcha: Multi-market price tracking bot for small business owners. Free beta - help us build the perfect tool for YOUR market!
```

```
/setcommands
Select: @FetchaGlobal_bot
Send:
start - Start the bot and select region
track - Add a product URL to track
list - View all tracked products
help - Get help and documentation
feedback - Send feature requests or report bugs
```

### 2. Invite Beta Testers

Share this link: **https://t.me/FetchaGlobal_bot**

Week 1 Target: 10 users  
Week 2 Target: 30 users  
Week 4 Target: 100 users

### 3. Monitor Feedback

```bash
sqlite3 price_tracker.db "SELECT region, category, platform, description FROM feature_requests ORDER BY created_at DESC LIMIT 10;"
```

### 4. Weekly Analysis

```bash
sqlite3 price_tracker.db <<EOF
SELECT region, COUNT(*) as users, SUM(tracked_count) as products 
FROM users 
GROUP BY region;
EOF
```

---

## 🐛 Troubleshooting

### Bot Won't Start?

**Check Python version:**
```bash
python3 --version  # Should be 3.8+
```

**Check dependencies:**
```bash
pip show python-telegram-bot
```

**Re-install if needed:**
```bash
pip install --upgrade python-telegram-bot
```

### Bot Starts But Users Can't Connect?

1. Check bot token in `.env` is correct
2. Verify bot username is `@FetchaGlobal_bot`
3. Make sure you're searching for the right bot

### Scraping Fails?

This is normal during beta! Common causes:
- API rate limits
- Website blocking
- Unsupported site structure

Ask users to try a different URL and send feedback via `/feedback`.

---

## 📁 Important Files

```
07_Telegram_App/Exploration/
├── telegram_price_tracker_mvp.py  # Main bot code
├── start_fetcha_bot.sh            # Startup script
├── .env                            # Configuration (keep secret!)
├── price_tracker.db                # Database (created on first run)
├── backups/                        # Database backups
├── DEPLOYMENT_GUIDE.md             # Full deployment guide
├── QUICK_START.md                  # This file
└── MULTI_MARKET_EXPANSION_STRATEGY.md
```

---

## 🎉 You're Ready!

The bot is fully configured and ready to launch.

**To start:** `./start_fetcha_bot.sh`  
**Bot URL:** https://t.me/FetchaGlobal_bot  
**Status:** Ready for beta testing

Good luck with your launch! 🚀
