
from modules.news_fetcher import fetch_news
from modules.signal_parser import parse_signals
from modules.notifier import send_alert
import yaml
import os

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Fetch and analyze
alerts = []
for category in config['categories']:
    results = fetch_news(category['queries'])
    alerts += parse_signals(results, category['keywords'], category['signal_type'])

# Notify
if alerts:
    for alert in alerts:
        send_alert(alert)
