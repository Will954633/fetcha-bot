#!/usr/bin/env python3
"""
Fetcha - Telegram Price Tracker Bot
Version: v1.0 • Updated: 2025-01-06 21:45 AEST (Brisbane)

MVP Features:
- Track product URLs from any website
- Price change detection
- Telegram notifications
- Basic user management
- Integration with test_universal_parser_approach.py

Usage:
1. Set TELEGRAM_BOT_TOKEN environment variable
2. Run: python telegram_price_tracker_mvp.py
"""

import os
import sys
import json
import time
import logging
import asyncio
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Configure logging FIRST (before any imports that might fail)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add parent directory to path for scraper import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import scraper - if not available (cloud deployment), scraping will be disabled
try:
    from test_universal_parser_approach import UniversalExtractionTester
    SCRAPER_AVAILABLE = True
    logger.info("Scraper module loaded successfully")
except ImportError:
    SCRAPER_AVAILABLE = False
    logger.warning("Scraper module not available - product tracking disabled. This is normal for cloud deployment.")

# Database setup
DB_PATH = Path(__file__).parent / "price_tracker.db"


class PriceTrackerDB:
    """SQLite database for tracking users and products"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table with region support
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    region TEXT DEFAULT 'unknown',
                    language_code TEXT DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tier TEXT DEFAULT 'free',
                    tracked_count INTEGER DEFAULT 0
                )
            ''')
            
            # Tracked products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracked_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    url TEXT NOT NULL,
                    product_name TEXT,
                    current_price REAL,
                    alert_price REAL,
                    last_check TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active INTEGER DEFAULT 1,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            ''')
            
            # Price history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    price REAL,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES tracked_products (id)
                )
            ''')
            
            # Feature requests table with region and platform tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feature_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    region TEXT,
                    category TEXT,
                    platform TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            ''')
            
            conn.commit()
    
    def add_user(self, telegram_id: int, username: str, first_name: str, 
                 region: str = 'unknown', language_code: str = 'en'):
        """Add or update user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (telegram_id, username, first_name, region, language_code)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, username, first_name, region, language_code))
            conn.commit()
    
    def update_user_region(self, telegram_id: int, region: str):
        """Update user's region"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET region = ? WHERE telegram_id = ?
            ''', (region, telegram_id))
            conn.commit()
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Get user details"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'telegram_id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'created_at': row[3],
                    'tier': row[4],
                    'tracked_count': row[5]
                }
            return None
    
    def add_tracked_product(self, telegram_id: int, url: str, product_name: str, 
                           current_price: float, alert_price: Optional[float] = None) -> int:
        """Add tracked product"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tracked_products 
                (telegram_id, url, product_name, current_price, alert_price, last_check)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (telegram_id, url, product_name, current_price, alert_price, datetime.now()))
            
            product_id = cursor.lastrowid
            
            # Update user's tracked count
            cursor.execute('''
                UPDATE users SET tracked_count = tracked_count + 1
                WHERE telegram_id = ?
            ''', (telegram_id,))
            
            conn.commit()
            return product_id
    
    def get_tracked_products(self, telegram_id: int) -> List[Dict]:
        """Get user's tracked products"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, url, product_name, current_price, alert_price, last_check, created_at
                FROM tracked_products
                WHERE telegram_id = ? AND active = 1
                ORDER BY created_at DESC
            ''', (telegram_id,))
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    'id': row[0],
                    'url': row[1],
                    'product_name': row[2],
                    'current_price': row[3],
                    'alert_price': row[4],
                    'last_check': row[5],
                    'created_at': row[6]
                })
            return products
    
    def update_product_price(self, product_id: int, new_price: float) -> Tuple[bool, float]:
        """Update product price and return if price changed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current price
            cursor.execute('SELECT current_price FROM tracked_products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            old_price = row[0] if row else None
            
            # Update price
            cursor.execute('''
                UPDATE tracked_products 
                SET current_price = ?, last_check = ?
                WHERE id = ?
            ''', (new_price, datetime.now(), product_id))
            
            # Add to price history
            cursor.execute('''
                INSERT INTO price_history (product_id, price)
                VALUES (?, ?)
            ''', (product_id, new_price))
            
            conn.commit()
            
            price_changed = old_price is not None and abs(old_price - new_price) > 0.01
            return price_changed, old_price if old_price else new_price
    
    def delete_tracked_product(self, product_id: int, telegram_id: int):
        """Delete tracked product"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tracked_products SET active = 0
                WHERE id = ? AND telegram_id = ?
            ''', (product_id, telegram_id))
            
            cursor.execute('''
                UPDATE users SET tracked_count = tracked_count - 1
                WHERE telegram_id = ?
            ''', (telegram_id,))
            
            conn.commit()
    
    def add_feature_request(self, telegram_id: int, category: str, description: str,
                           region: str = 'unknown', platform: str = None):
        """Add feature request with region and platform tracking"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feature_requests (telegram_id, region, category, platform, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, region, category, platform, description))
            conn.commit()
    
    def get_market_stats(self, region: str = None) -> Dict:
        """Get statistics by market/region"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if region:
                cursor.execute('''
                    SELECT COUNT(*) as users, SUM(tracked_count) as products
                    FROM users WHERE region = ?
                ''', (region,))
            else:
                cursor.execute('''
                    SELECT region, COUNT(*) as users, SUM(tracked_count) as products
                    FROM users GROUP BY region
                ''')
            
            if region:
                row = cursor.fetchone()
                return {'users': row[0], 'products': row[1]} if row else {'users': 0, 'products': 0}
            else:
                stats = {}
                for row in cursor.fetchall():
                    stats[row[0]] = {'users': row[1], 'products': row[2]}
                return stats
    
    def get_all_tracked_products(self) -> List[Dict]:
        """Get all active tracked products for background checking"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, telegram_id, url, product_name, current_price, alert_price
                FROM tracked_products
                WHERE active = 1
            ''')
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    'id': row[0],
                    'telegram_id': row[1],
                    'url': row[2],
                    'product_name': row[3],
                    'current_price': row[4],
                    'alert_price': row[5]
                })
            return products


class PriceTrackerBot:
    """Main bot class"""
    
    def __init__(self, token: str):
        self.token = token
        self.db = PriceTrackerDB()
        self.application = None
        
        # Free tier limits
        self.FREE_TIER_LIMIT = 3  # 3 tracked products for free
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with region selection"""
        user = update.effective_user
        
        # Check if user already exists
        existing_user = self.db.get_user(user.id)
        
        if not existing_user or existing_user.get('region') == 'unknown':
            # New user - ask for region
            keyboard = [
                [InlineKeyboardButton("🇺🇸 USA", callback_data="region_usa"),
                 InlineKeyboardButton("🇮🇳 India", callback_data="region_india")],
                [InlineKeyboardButton("🇦🇺 Australia", callback_data="region_australia"),
                 InlineKeyboardButton("🇮🇩 Indonesia", callback_data="region_indonesia")],
                [InlineKeyboardButton("🇷🇺 Russia", callback_data="region_russia"),
                 InlineKeyboardButton("🇧🇷 Brazil", callback_data="region_brazil")],
                [InlineKeyboardButton("🌏 Other", callback_data="region_other")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "👋 **Welcome to Fetcha Beta!**\n\n"
                "🌍 First, please select your region:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Add user with unknown region for now
            language_code = user.language_code or 'en'
            self.db.add_user(user.id, user.username, user.first_name, 'unknown', language_code)
            return
        
        # Existing user - show normal welcome
        await self._show_welcome_message(update, existing_user.get('region', 'unknown'))
    
    async def _show_welcome_message(self, update: Update, region: str):
        """Show welcome message after region is set"""
        
        welcome_message = f"""
👋 **Welcome to Fetcha!**

I help small business owners track competitor prices automatically.

**🎯 What I can do:**
• Track any product URL
• Monitor price changes
• Send instant alerts
• Compare prices over time

**📝 Quick Start:**
1. Send me a product URL to track
2. I'll extract the current price
3. Set your alert threshold
4. Get notified of changes!

**🆓 Beta Access:**
You can track up to {self.FREE_TIER_LIMIT} products for free during beta.

**📋 Commands:**
/track - Add a product to track
/list - View your tracked products
/help - Get help
/feedback - Send feature requests

**🔔 Beta Testing:**
This is a beta version. We want YOUR feedback!
Use /feedback to tell us what features you need.

Ready to start? Send me a product URL!
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
**📖 Help & Commands**

**Basic Commands:**
/start - Start the bot
/track - Track a new product
/list - View tracked products
/help - Show this help
/feedback - Send feature requests

**How to Track a Product:**
1. Copy product URL from any website
2. Send URL to me (or use /track command)
3. I'll show you the current price
4. Set your alert price (optional)
5. Get notified when price changes!

**Supported Websites:**
✅ Amazon.com.au
✅ eBay.com.au
✅ Bunnings.com.au
✅ JB Hi-Fi
✅ Kogan
✅ ANY Australian e-commerce site!

**Beta Limits:**
• {limit} tracked products (free)
• Daily price checks
• Telegram alerts only

**Need More?**
Use /feedback to tell us what features you need!

**Questions?**
Contact @your_username
        """.format(limit=self.FREE_TIER_LIMIT)
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def track_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /track command"""
        await update.message.reply_text(
            "📎 Send me the product URL you want to track.\n\n"
            "Example: https://www.amazon.com.au/product/B08N5WRWNW"
        )
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        user_id = update.effective_user.id
        products = self.db.get_tracked_products(user_id)
        
        if not products:
            await update.message.reply_text(
                "📭 You're not tracking any products yet.\n\n"
                "Send me a product URL to start tracking!"
            )
            return
        
        message = f"📊 **Your Tracked Products** ({len(products)}/{self.FREE_TIER_LIMIT})\n\n"
        
        for i, product in enumerate(products, 1):
            price_text = f"${product['current_price']:.2f}" if product['current_price'] else "Unknown"
            alert_text = f" (Alert: ${product['alert_price']:.2f})" if product['alert_price'] else ""
            
            message += f"{i}. **{product['product_name']}**\n"
            message += f"   💰 Price: {price_text}{alert_text}\n"
            message += f"   🔗 [Link]({product['url'][:50]}...)\n"
            message += f"   📅 Added: {product['created_at'][:10]}\n\n"
        
        # Add action buttons
        keyboard = []
        for product in products[:5]:  # Show first 5
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ Delete: {product['product_name'][:30]}",
                    callback_data=f"delete_{product['id']}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    
    async def feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /feedback command with platform selection"""
        keyboard = [
            [InlineKeyboardButton("🎯 Feature Request", callback_data="feedback_feature")],
            [InlineKeyboardButton("🐛 Bug Report", callback_data="feedback_bug")],
            [InlineKeyboardButton("💰 Pricing Feedback", callback_data="feedback_pricing")],
            [InlineKeyboardButton("🌐 Platform Support", callback_data="feedback_platform")],
            [InlineKeyboardButton("💡 General Feedback", callback_data="feedback_general")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "**🎤 Multi-Market Beta Feedback!**\n\n"
            "Your feedback helps us build the right product for YOUR market.\n\n"
            "What would you like to share?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_url_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle URL messages for tracking"""
        user_id = update.effective_user.id
        url = update.message.text.strip()
        
        # Validate URL
        if not url.startswith('http'):
            return
        
        # Check user limits
        user = self.db.get_user(user_id)
        if user and user['tracked_count'] >= self.FREE_TIER_LIMIT:
            await update.message.reply_text(
                f"⚠️ **Free Tier Limit Reached**\n\n"
                f"You're currently tracking {self.FREE_TIER_LIMIT} products (beta limit).\n\n"
                f"To track more, please remove a product first using /list"
            )
            return
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "🔍 **Analyzing product...**\n"
            "⏱️ This may take 30-60 seconds..."
        )
        
        try:
            # Check if scraper is available
            if not SCRAPER_AVAILABLE:
                await processing_msg.edit_text(
                    "⚠️ **Product Scraping Temporarily Unavailable**\n\n"
                    "We're currently in beta and the scraping feature is being upgraded.\n\n"
                    "**You can help!**\n"
                    "Please use /feedback to tell us:\n"
                    "• What website/platform you want to track\n"
                    "• What data points matter to you\n"
                    "• How often you need updates\n\n"
                    "Your feedback shapes the final product!",
                    parse_mode='Markdown'
                )
                return
            
            # Use universal scraper to extract product data
            tester = UniversalExtractionTester(target_url=url)
            success = tester.run_intelligent_extraction_test()
            
            if not success:
                await processing_msg.edit_text(
                    "❌ **Extraction Failed**\n\n"
                    "Could not extract product data from this URL.\n"
                    "Please try a different URL or contact support."
                )
                return
            
            # Get extracted data
            results = tester._dedicated_parser_results if hasattr(tester, '_dedicated_parser_results') else {}
            
            # Extract product name and price
            product_name = self._extract_product_name(results)
            current_price = self._extract_price(results)
            
            if not product_name or current_price is None:
                await processing_msg.edit_text(
                    "⚠️ **Partial Success**\n\n"
                    "Could extract some data but missing product name or price.\n"
                    "Please try a different URL."
                )
                return
            
            # Add to tracking
            product_id = self.db.add_tracked_product(
                user_id, url, product_name, current_price
            )
            
            # Success message with alert setup
            keyboard = [
                [InlineKeyboardButton("🔔 Set Price Alert", callback_data=f"alert_{product_id}")],
                [InlineKeyboardButton("📊 View All Products", callback_data="view_all")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(
                f"✅ **Product Tracked Successfully!**\n\n"
                f"📦 **{product_name}**\n"
                f"💰 Current Price: **${current_price:.2f}**\n\n"
                f"I'll check this product daily and notify you of any price changes.\n\n"
                f"Want to set a specific alert price?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error tracking product: {e}")
            await processing_msg.edit_text(
                f"❌ **Error**\n\n"
                f"Something went wrong: {str(e)}\n\n"
                f"Please try again or contact support."
            )
    
    def _extract_product_name(self, results: Dict) -> Optional[str]:
        """Extract product name from results"""
        # Try various field names
        for key in ['product_name', 'title', 'name', 'heading', 'product_title']:
            if key in results:
                value = results[key]
                if isinstance(value, dict) and 'value' in value:
                    return str(value['value'])[:100]
                elif isinstance(value, str):
                    return value[:100]
        
        return "Unknown Product"
    
    def _extract_price(self, results: Dict) -> Optional[float]:
        """Extract price from results"""
        # Try various field names
        for key in ['price', 'current_price', 'sale_price', 'product_price']:
            if key in results:
                value = results[key]
                if isinstance(value, dict) and 'value' in value:
                    value = value['value']
                
                # Extract numeric price
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, str):
                    # Remove currency symbols and commas
                    price_str = value.replace('$', '').replace(',', '').strip()
                    try:
                        return float(price_str)
                    except:
                        pass
        
        return None
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith('delete_'):
            product_id = int(data.split('_')[1])
            self.db.delete_tracked_product(product_id, query.from_user.id)
            await query.edit_message_text(
                "✅ Product removed from tracking.\n\n"
                "Use /list to see remaining products."
            )
        
        elif data.startswith('alert_'):
            product_id = data.split('_')[1]
            await query.edit_message_text(
                f"🔔 To set a price alert, send me the price threshold.\n\n"
                f"Example: Send `250` to get notified when price drops below $250\n\n"
                f"(Feature coming in next update!)",
                parse_mode='Markdown'
            )
        
        elif data == 'view_all':
            # Trigger /list command
            await self.list_command(update, context)
        
        elif data.startswith('feedback_'):
            category = data.split('_')[1]
            
            # For platform feedback, show platform selection
            if category == 'platform':
                # Get user's region to show relevant platforms
                user = self.db.get_user(query.from_user.id)
                region = user.get('region', 'unknown') if user else 'unknown'
                
                # Region-specific platforms
                platform_options = self._get_platform_options(region)
                
                keyboard = []
                for platform in platform_options:
                    keyboard.append([InlineKeyboardButton(platform, callback_data=f"platform_{platform}")])
                keyboard.append([InlineKeyboardButton("✍️ Other (type it)", callback_data="platform_other")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"**🌐 Which platform do you need support for?**\n\n"
                    f"Your region: {region.upper()}\n\n"
                    f"Select from popular platforms in your market:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                context.user_data['feedback_category'] = category
            else:
                await query.edit_message_text(
                    f"**{category.title()} Feedback**\n\n"
                    f"Please describe your {category} in detail:\n\n"
                    f"(Send your message now, I'll save it!)",
                    parse_mode='Markdown'
                )
                context.user_data['feedback_category'] = category
        
        elif data.startswith('platform_'):
            platform = data.split('_', 1)[1]
            
            if platform == 'other':
                await query.edit_message_text(
                    "**✍️ Type the platform name**\n\n"
                    "Please type the name of the platform/website you need support for:",
                    parse_mode='Markdown'
                )
            else:
                context.user_data['feedback_platform'] = platform
                await query.edit_message_text(
                    f"**🌐 Platform: {platform}**\n\n"
                    f"What specific feature or support do you need for {platform}?\n\n"
                    f"(Send your message now, I'll save it!)",
                    parse_mode='Markdown'
                )
            
            context.user_data['feedback_category'] = 'platform'
        
        elif data.startswith('region_'):
            region = data.split('_')[1]
            
            # Update user's region
            self.db.update_user_region(query.from_user.id, region)
            
            await query.edit_message_text(
                f"✅ **Region set to: {region.upper()}**\n\n"
                f"Thank you! This helps us provide better service for your market.",
                parse_mode='Markdown'
            )
            
            # Show welcome message
            await self._show_welcome_message(query, region)
    
    async def handle_feedback_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle feedback messages with region and platform tracking"""
        if 'feedback_category' in context.user_data:
            category = context.user_data['feedback_category']
            description = update.message.text
            
            # Get user's region
            user = self.db.get_user(update.effective_user.id)
            region = user.get('region', 'unknown') if user else 'unknown'
            
            # Get platform if available
            platform = context.user_data.get('feedback_platform', None)
            
            # Save to database with region and platform
            self.db.add_feature_request(
                update.effective_user.id,
                category,
                description,
                region,
                platform
            )
            
            response = "✅ **Thank you for your multi-market feedback!**\n\n"
            response += f"📍 Region: {region.upper()}\n"
            response += f"📋 Category: {category.title()}\n"
            if platform:
                response += f"🌐 Platform: {platform}\n"
            response += "\nYour input helps us build the right product for YOUR market!"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
            # Clear context
            del context.user_data['feedback_category']
            if 'feedback_platform' in context.user_data:
                del context.user_data['feedback_platform']
    
    async def background_price_check(self, context: ContextTypes.DEFAULT_TYPE):
        """Background job to check all tracked products"""
        logger.info("Starting background price check...")
        
        products = self.db.get_all_tracked_products()
        
        for product in products:
            try:
                # Skip if scraper not available
                if not SCRAPER_AVAILABLE:
                    continue
                
                # Extract current price
                tester = UniversalExtractionTester(target_url=product['url'])
                success = tester.run_intelligent_extraction_test()
                
                if success and hasattr(tester, '_dedicated_parser_results'):
                    results = tester._dedicated_parser_results
                    new_price = self._extract_price(results)
                    
                    if new_price:
                        # Update price in database
                        price_changed, old_price = self.db.update_product_price(
                            product['id'], new_price
                        )
                        
                        # Send alert if price changed significantly
                        if price_changed:
                            price_diff = new_price - old_price
                            percent_change = (price_diff / old_price) * 100
                            
                            if abs(percent_change) >= 5:  # 5% threshold
                                emoji = "🔻" if price_diff < 0 else "🔺"
                                await context.bot.send_message(
                                    chat_id=product['telegram_id'],
                                    text=f"{emoji} **PRICE CHANGE ALERT**\n\n"
                                         f"📦 {product['product_name']}\n"
                                         f"💰 ${old_price:.2f} → ${new_price:.2f}\n"
                                         f"📊 {percent_change:+.1f}%\n\n"
                                         f"[View Product]({product['url']})",
                                    parse_mode='Markdown',
                                    disable_web_page_preview=True
                                )
                
                # Rate limiting
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error checking product {product['id']}: {e}")
                continue
        
        logger.info("Background price check complete")
    
    def _get_platform_options(self, region: str) -> list:
        """Get relevant platform options based on user's region"""
        platforms = {
            'usa': ['Amazon.com', 'eBay', 'Walmart', 'Shopify', 'Etsy'],
            'india': ['Amazon India', 'Flipkart', 'Meesho', 'Snapdeal', 'IndiaMART'],
            'indonesia': ['Shopee', 'Tokopedia', 'Bukalapak', 'Lazada', 'Blibli'],
            'russia': ['Wildberries', 'Ozon', 'Yandex Market', 'AliExpress', 'Lamoda'],
            'brazil': ['Mercado Livre', 'Americanas', 'Shopee Brazil', 'Amazon Brazil', 'Magalu'],
            'australia': ['eBay.com.au', 'Amazon.com.au', 'Bunnings', 'Kogan', 'Catch']
        }
        
        return platforms.get(region, ['Amazon', 'eBay', 'Shopify', 'Other'])
    
    def run(self):
        """Start the bot"""
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("track", self.track_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        self.application.add_handler(CommandHandler("feedback", self.feedback_command))
        
        # URL message handler
        self.application.add_handler(
            MessageHandler(filters.TEXT & filters.Regex(r'http'), self.handle_url_message)
        )
        
        # Feedback message handler
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_feedback_message)
        )
        
        # Button callback handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Background job (check prices every 24 hours)
        job_queue = self.application.job_queue
        job_queue.run_repeating(
            self.background_price_check,
            interval=86400,  # 24 hours
            first=60  # Start after 1 minute
        )
        
        # Start bot
        logger.info("Starting Fetcha Bot...")
        self.application.run_polling()


def main():
    """Main entry point"""
    # Get token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("\nTo run the bot:")
        print("1. Get a bot token from @BotFather on Telegram")
        print("2. Set environment variable:")
        print("   export TELEGRAM_BOT_TOKEN='your_token_here'")
        print("3. Run this script again")
        sys.exit(1)
    
    # Start bot
    bot = PriceTrackerBot(token)
    bot.run()


if __name__ == '__main__':
    main()
