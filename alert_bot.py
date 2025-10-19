import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# The chat ID to send alerts to.  This should be set via the TELEGRAM_CHAT_ID environment
# variable and must be a valid user, group or channel ID (e.g. "@yourusername").  It is
# intentionally left blank by default to avoid accidentally sending alerts to the wrong place.
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_alert(articles):
    """
    Send Telegram alert with real article information.
    """
    if not BOT_TOKEN:
        print("Warning: TELEGRAM_BOT_TOKEN not set, skipping alert")
        return
    
    message = "🚨 Fuel Alert Triggered!\n\n"
    message += f"Found {len(articles)} articles with fuel-related keywords:\n\n"
    
    for i, article in enumerate(articles[:10], 1):
        keywords = ', '.join(article.get('matched_keywords', []))
        message += f"{i}. {article.get('title', 'No title')}\n"
        message += f"   🔑 Keywords: {keywords}\n"
        message += f"   🔗 {article.get('link', 'No link')}\n"
        message += f"   📰 Source: {article.get('source', 'Unknown')}\n\n"
    
    if len(articles) > 10:
        message += f"... and {len(articles) - 10} more articles.\n"
    
    message += f"\n⏰ Scan time: {articles[0].get('scan_time', 'N/A')}" if articles else ""
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message, "disable_web_page_preview": True},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Telegram alert sent successfully!")
        else:
            print(f"❌ Telegram alert failed: {response.text}")
            
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")
