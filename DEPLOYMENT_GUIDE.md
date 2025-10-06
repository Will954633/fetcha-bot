# Fetcha Bot Deployment Guide
**Bot:** @FetchaGlobal_bot
**Version:** v1.1 • Updated: 2025-01-06 21:56 AEST (Brisbane)

## 🎉 Your Bot is Created!

**Bot Name:** Fetcha
**Bot Username:** @FetchaGlobal_bot
**Bot URL:** https://t.me/FetchaGlobal_bot
**Status:** Ready to deploy

⚠️ **IMPORTANT:** Keep your bot token secure! It's like a password.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Set Environment Variable

**On Mac/Linux:**
```bash
cd /Users/willsimpson/Documents/Fields/Property\ Scraping_V3/07_Telegram_App/Exploration

export TELEGRAM_BOT_TOKEN='8336055003:AAEMqahmVx6PYaRy8SkOcE88YnLPjrFwH3o'
```

**On Windows:**
```cmd
set TELEGRAM_BOT_TOKEN=8045851756:AAFHR7hIPluHIKFSvOu3TmIYxUTy3TQCjwE
```

### Step 2: Install Dependencies

```bash
pip install python-telegram-bot
```

### Step 3: Run the Bot

```bash
python telegram_price_tracker_mvp.py
```

You should see:
```
INFO - Starting Telegram Price Tracker MVP Bot...
```

### Step 4: Test It!

1. Open Telegram
2. Search for: @FetchaGlobal_bot
3. Send: `/start`
4. Follow the prompts!

---

## 📝 First-Time Setup Checklist

After starting the bot:

- [ ] Test `/start` command (should ask for region)
- [ ] Select a region (e.g., USA, India, Australia)
- [ ] Send a test product URL (e.g., Amazon product)
- [ ] Verify scraping works (should show product data)
- [ ] Test `/list` command
- [ ] Test `/feedback` command
- [ ] Send a price alert test

---

## 🔧 Bot Configuration

### Set Bot Description

1. Go to @BotFather on Telegram
2. Send: `/setdescription`
3. Select: @FetchaGlobal_bot
4. Send:
```
Fetcha - Track product prices automatically across any e-commerce site. 
Get instant alerts when prices change. Free beta for business owners!
```

### Set About Text

1. Send: `/setabouttext` to @BotFather
2. Select: @FetchaGlobal_bot
3. Send:
```
Fetcha: Multi-market price tracking bot for small business owners. 
Free beta - help us build the perfect tool for YOUR market!
```

### Set Bot Commands

1. Send: `/setcommands` to @BotFather
2. Select: @FetchaGlobal_bot
3. Send:
```
start - Start the bot and select region
track - Add a product URL to track
list - View all tracked products
help - Get help and documentation
feedback - Send feature requests or report bugs
```

### Add Profile Picture

1. Send: `/setuserpic` to @BotFather
2. Select: @FetchaGlobal_bot
3. Upload an image (512x512 recommended)

---

## 🌍 Testing Multi-Market Features

### Test Flow:

1. **New User (USA)**
   - Start bot → Select 🇺🇸 USA
   - Send Amazon URL
   - Give feedback → Platform Support → Amazon
   - Check database to see USA region saved

2. **New User (India)**
   - Start bot → Select 🇮🇳 India
   - Send Flipkart URL
   - Give feedback → Platform Support → Flipkart
   - Check database to see India region + Flipkart request

3. **Verify Database**
   ```bash
   sqlite3 price_tracker.db "SELECT region, COUNT(*) FROM users GROUP BY region;"
   ```

---

## 📊 Monitor Beta Performance

### Check User Stats

```bash
sqlite3 price_tracker.db
```

```sql
-- Total users by region
SELECT region, COUNT(*) as users 
FROM users 
GROUP BY region;

-- Products tracked by region
SELECT u.region, COUNT(tp.id) as products
FROM users u
LEFT JOIN tracked_products tp ON u.telegram_id = tp.telegram_id
GROUP BY u.region;

-- Top feature requests
SELECT region, category, COUNT(*) as count
FROM feature_requests
GROUP BY region, category
ORDER BY count DESC;

-- Platform requests by region
SELECT region, platform, COUNT(*) as count
FROM feature_requests
WHERE platform IS NOT NULL
GROUP BY region, platform
ORDER BY count DESC;
```

---

## 🐛 Troubleshooting

### Bot Not Starting?

**Error:** "TELEGRAM_BOT_TOKEN not set"
- Solution: Run the export command again in the same terminal

**Error:** "No module named 'telegram'"
- Solution: `pip install python-telegram-bot`

**Error:** "No module named 'test_universal_parser_approach'"
- Solution: Make sure you're running from the correct directory
  ```bash
  cd /Users/willsimpson/Documents/Fields/Property\ Scraping_V3/07_Telegram_App/Exploration
  ```

### Bot Running But Not Responding?

1. Check bot is actually running (should show INFO messages)
2. Make sure you're messaging the correct bot: @FetchaGlobal_bot
3. Try `/start` command
4. Check terminal for error messages

### Scraping Not Working?

**Issue:** "Extraction Failed" message
- Claude API might be rate limited
- Bright Data might be hitting limits
- URL might not be supported
- Check terminal logs for actual error

---

## 🚀 Production Deployment (Optional)

### Option 1: Keep Running Locally
- Simple, but computer must stay on
- Good for initial testing (first 50-100 users)

### Option 2: Deploy to Cloud

**Digital Ocean (Easiest):**
```bash
# 1. Create droplet (Ubuntu 22.04)
# 2. SSH into server
# 3. Install dependencies
sudo apt update
sudo apt install python3-pip
pip3 install python-telegram-bot

# 4. Upload bot files
scp telegram_price_tracker_mvp.py user@server:/home/user/
scp -r ../../ user@server:/home/user/scraper/  # Upload scraper code

# 5. Set environment variable
echo "export TELEGRAM_BOT_TOKEN='YOUR_TOKEN'" >> ~/.bashrc
source ~/.bashrc

# 6. Run with nohup
nohup python3 telegram_price_tracker_mvp.py &
```

**AWS/GCP:**
- Use EC2/Compute Engine
- Same process as Digital Ocean
- More configuration options

---

## 📈 Beta Launch Checklist

### Week 1: Friends & Family (10 users)
- [ ] Share bot link with 10 trusted people
- [ ] Ask them to test all features
- [ ] Collect initial feedback
- [ ] Fix critical bugs
- [ ] Verify database working

### Week 2: Closed Beta (30 users)
- [ ] Post in 2-3 Facebook groups
- [ ] Share on Reddit (r/ecommerce, r/Entrepreneur)
- [ ] Monitor usage daily
- [ ] Respond to feedback
- [ ] Add requested features

### Week 3-4: Analysis
- [ ] Export database stats
- [ ] Analyze feature requests by region
- [ ] Identify top platform needs
- [ ] Validate pricing assumptions
- [ ] Plan next features

---

## 💾 Backup Your Data

**Daily Backup:**
```bash
# Backup database
cp price_tracker.db price_tracker_backup_$(date +%Y%m%d).db

# Or automate with cron
crontab -e
# Add: 0 2 * * * cp /path/to/price_tracker.db /path/to/backups/price_tracker_$(date +\%Y\%m\%d).db
```

**Export to CSV:**
```bash
sqlite3 price_tracker.db <<EOF
.headers on
.mode csv
.output users.csv
SELECT * FROM users;
.output feature_requests.csv
SELECT * FROM feature_requests;
.output tracked_products.csv
SELECT * FROM tracked_products;
EOF
```

---

## 🎯 Success Metrics to Track

### Week 1 Targets:
- [ ] 10 users signed up
- [ ] 30+ products tracked
- [ ] 5+ feature requests received
- [ ] 0 critical bugs
- [ ] 80%+ successful scrapes

### Week 4 Targets:
- [ ] 100 users across 3+ regions
- [ ] 300+ products tracked
- [ ] 50+ feature requests
- [ ] Clear top 3 platform needs
- [ ] Pricing validated per region

---

## 📞 Support & Help

**Bot Issues:**
- Check terminal logs
- Review this guide
- Search error messages

**Feature Requests:**
- Use `/feedback` in bot
- Or email yourself notes

**Questions:**
- Check README.md
- Check TELEGRAM_BOT_FEASIBILITY_STUDY.md
- Check MULTI_MARKET_EXPANSION_STRATEGY.md

---

## 🎉 You're Ready to Launch!

**Next Steps:**
1. Set up bot profile (@BotFather)
2. Test with 5 friends first
3. Fix any bugs
4. Invite 30 beta testers
5. Analyze results weekly
6. Build what users actually want!

**Bot Link:** https://t.me/FetchaGlobal_bot

Good luck! 🚀
