# Fuel Notify Bot

This repository contains a Python/FastAPI project designed to monitor news and government feeds for early signs of fuel‑supply disruptions in Australia.  The bot periodically fetches RSS news feeds, searches for key terms (for example *"fuel shortage"* or *"truck delivery delays"*), and sends a Telegram alert when multiple matching articles are found.  It can also log scan results to a Google Sheet if configured.

## Features

* ✅ **Real‑time scanning:** fetches recent articles from major Australian news RSS feeds and optionally the NewsAPI.
* ✅ **Keyword matching:** configurable list of keywords and an alert threshold in `config.yaml`.
* ✅ **Telegram notifications:** sends a summary of matched articles via Telegram.  Requires you to set environment variables for `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
* ✅ **Background scheduler:** uses APScheduler to run the scan automatically (every 15 minutes by default).
* 🔧 **Optional Google Sheets logging:** logs scan results to a Google Sheet using the Replit connectors API (the `sheets_logger.py` module).  This is only needed if you are running the bot on Replit with Google Sheets integration configured.

## File overview

| File               | Purpose                                                                                       |
|--------------------|------------------------------------------------------------------------------------------------|
| **`main.py`**      | Entry point for the FastAPI application.  Defines endpoints and manages the background scheduler. |
| **`alert_bot.py`** | Sends alerts to Telegram using `requests`.  Reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from environment variables. |
| **`news_fetcher.py`** | Fetches articles from RSS feeds (and optionally NewsAPI) and filters them by keyword. |
| **`config.yaml`**  | Contains your list of keywords, alert threshold, and grouped search queries.  Edit this to customise your monitoring. |
| **`sheets_logger.py`** | (Optional) Logs scan results to a Google Sheet.  Only needed when using Replit’s Google Sheets connector. |
| **`requirements.txt`** | Python dependencies required to run the bot.  Install with `pip install -r requirements.txt`. |

## Usage

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/fuel-notify-bot.git
cd fuel-notify-bot
```

### 2. Install dependencies

It’s recommended to use a virtual environment (venv or conda), but not required.  Then install the dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Set the following environment variables before running the bot:

* **`TELEGRAM_BOT_TOKEN`** – The API token for your Telegram bot (obtained from [@BotFather](https://t.me/botfather)).
* **`TELEGRAM_CHAT_ID`** – The chat ID or channel/user name (e.g. `@your_username`) where alerts should be sent.  If you leave this unset the bot will not send any messages.
* *(Optional)* **`NEWSAPI_API_KEY`** – If you want to use the NewsAPI fallback in `news_fetcher.py` to fetch additional articles.  Leave unset to skip NewsAPI.
* *(Optional)* Replit sheet variables – If you plan to use the `sheets_logger.py` module on Replit for logging, you need the appropriate Replit connector variables (`REPLIT_CONNECTORS_HOSTNAME` and either `REPL_IDENTITY` or `WEB_REPL_RENEWAL`).

These can be exported in your shell or configured in your hosting environment.

### 4. Customise searches

Open `config.yaml` and adjust:

* `alert_threshold`: number of matching articles required before sending an alert.
* `alert_keywords`: words or phrases that should trigger an alert when found in article titles or summaries.
* `search_groups`: list of categories and the queries used for each.  You can add or remove search groups and queries.

### 5. Run the bot

Start the FastAPI server with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

When the server starts, it will also begin a background scheduler that scans every 15 minutes (see `main.py`).  You can manually trigger a scan by visiting `http://localhost:8000/scan` in your browser or via `curl`.

### 6. Deploying

This project runs anywhere Python is available.  For persistent operation you should deploy it on a platform that allows long‑running processes:

* 🟢 **Replit** – simple to set up, supports background tasks.  Ensure you have a Replit plan that allows always‑on processes.
* 🟡 **Render.com** or **Railway.app** – support continuous Python services and environment variables.
* 🔵 **VPS** (DigitalOcean, IONOS, Contabo, etc.) – install Python, copy the repo, set your environment variables, and use `systemd` or `tmux` to keep it running.

Shared web hosting plans (like IONOS Web Hosting Plus) typically do **not** support persistent Python bots.  You need a VPS or a serverless platform for a process that runs continuously.

### Optional: Logging to Google Sheets

If you are running on **Replit** and have connected a Google Sheets connector, set up your connector secrets (`REPLIT_CONNECTORS_HOSTNAME`, `REPL_IDENTITY` or `WEB_REPL_RENEWAL`).  The `sheets_logger.log_to_sheets` function will then automatically append results to a sheet titled “Fuel Alert Logs.”  Outside of Replit this module will raise exceptions because the Replit connector is not available.

## License

This project is provided as‑is under the [MIT License](LICENSE).  Feel free to adapt and extend it for your own monitoring needs.