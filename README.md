
# FuelNotifyCronBot

A modular, cron-based fuel disruption alert system.

## Setup

1. Install Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Add secrets to `.env` file.

3. Deploy to shared host (e.g., IONOS).

4. Set CRON:
   ```
   */5 * * * * /usr/bin/python3 /path-to/fuelnotifycronbot/main.py >> log.txt 2>&1
   ```

## Configurable

Edit `config.yaml` to adjust search categories and keywords.
