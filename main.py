from fastapi import FastAPI
import uvicorn
from alert_bot import send_alert
from news_fetcher import fetch_news_from_rss, search_articles_for_keywords
from sheets_logger import log_to_sheets
import yaml
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

scheduler = BackgroundScheduler()

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def perform_scan():
    """
    Main scanning function that fetches real news and checks for keywords.
    Called by scheduler and /scan endpoint.
    """
    try:
        print(f"\n[{datetime.now()}] Starting fuel alert scan...")
        
        config = load_config()
        
        print("Fetching news from RSS feeds...")
        articles = fetch_news_from_rss([], hours_back=24)
        print(f"Fetched {len(articles)} articles")
        
        print("Searching for keyword matches...")
        matched_articles = search_articles_for_keywords(articles, config["alert_keywords"])
        print(f"Found {len(matched_articles)} articles with keyword matches")
        
        alert_sent = False
        if len(matched_articles) >= config["alert_threshold"]:
            print(f"Alert threshold ({config['alert_threshold']}) met! Sending Telegram alert...")
            send_alert(matched_articles)
            alert_sent = True
            print("Telegram alert sent!")
        else:
            print(f"Threshold not met ({len(matched_articles)}/{config['alert_threshold']}). No alert sent.")
        
        print("Logging results to Google Sheets...")
        log_to_sheets(matched_articles, alert_sent=alert_sent, search_group="All Sources", total_fetched=len(articles))
        print("Results logged to Google Sheets!")
        
        return {
            "status": "success",
            "timestamp": str(datetime.now()),
            "articles_fetched": len(articles),
            "articles_matched": len(matched_articles),
            "alert_sent": alert_sent,
            "matched_articles": matched_articles[:10]
        }
        
    except Exception as e:
        print(f"Error during scan: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": str(datetime.now())
        }

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        perform_scan,
        'interval',
        minutes=15,
        id='fuel_scan',
        replace_existing=True
    )
    scheduler.start()
    print("✅ Background scheduler started - scanning every 15 minutes")
    
    perform_scan()
    
    yield
    
    scheduler.shutdown()
    print("Scheduler stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {
        "name": "Fuel Alert Bot",
        "description": "Monitors fuel-related news in real-time and sends Telegram alerts",
        "status": "Active - Scanning every 15 minutes",
        "endpoints": {
            "/": "API information",
            "/scan": "Manually trigger fuel alert scan",
            "/status": "Get scanning status"
        }
    }

@app.get("/scan")
def scan():
    """
    Manually trigger a fuel alert scan.
    """
    result = perform_scan()
    return result

@app.get("/status")
def status():
    """
    Get the current status of the background scanner.
    """
    jobs = scheduler.get_jobs()
    return {
        "scheduler_running": scheduler.running,
        "active_jobs": len(jobs),
        "next_scan": str(jobs[0].next_run_time) if jobs else "No scheduled scans"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000)
