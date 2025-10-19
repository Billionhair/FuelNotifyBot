import os
import json
import requests
from datetime import datetime

def get_google_sheets_client():
    """
    Get authenticated Google Sheets client using Replit connector.
    """
    hostname = os.getenv('REPLIT_CONNECTORS_HOSTNAME')
    x_replit_token = (
        'repl ' + os.getenv('REPL_IDENTITY') if os.getenv('REPL_IDENTITY')
        else 'depl ' + os.getenv('WEB_REPL_RENEWAL') if os.getenv('WEB_REPL_RENEWAL')
        else None
    )
    
    if not x_replit_token:
        raise Exception('X_REPLIT_TOKEN not found for repl/depl')
    
    response = requests.get(
        f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet',
        headers={
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
    )
    
    connection_settings = response.json().get('items', [])[0] if response.json().get('items') else None
    
    if not connection_settings:
        raise Exception('Google Sheet not connected')
    
    access_token = connection_settings.get('settings', {}).get('access_token')
    
    if not access_token:
        raise Exception('No access token found')
    
    return access_token

def get_or_create_spreadsheet(spreadsheet_name="Fuel Alert Logs"):
    """
    Get or create a Google Spreadsheet for logging.
    Returns spreadsheet ID.
    """
    try:
        access_token = get_google_sheets_client()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        search_response = requests.get(
            'https://www.googleapis.com/drive/v3/files',
            params={
                'q': f"name='{spreadsheet_name}' and mimeType='application/vnd.google-apps.spreadsheet'",
                'spaces': 'drive',
                'fields': 'files(id, name)'
            },
            headers=headers
        )
        
        files = search_response.json().get('files', [])
        
        if files:
            return files[0]['id']
        
        create_response = requests.post(
            'https://sheets.googleapis.com/v4/spreadsheets',
            headers=headers,
            json={
                'properties': {
                    'title': spreadsheet_name
                },
                'sheets': [{
                    'properties': {
                        'title': 'Alert Logs',
                        'gridProperties': {
                            'frozenRowCount': 1
                        }
                    }
                }]
            }
        )
        
        spreadsheet_id = create_response.json()['spreadsheetId']
        
        requests.post(
            f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/Alert Logs!A1:append',
            params={'valueInputOption': 'RAW'},
            headers=headers,
            json={
                'values': [[
                    'Timestamp', 'Article Title', 'URL', 'Source', 
                    'Matched Keywords', 'Match Score', 'Alert Sent', 'Search Group'
                ]]
            }
        )
        
        return spreadsheet_id
        
    except Exception as e:
        print(f"Error creating/getting spreadsheet: {e}")
        return None

def log_to_sheets(articles, alert_sent=False, search_group="General", total_fetched=0):
    """
    Log scan results to Google Sheets. Always logs, even with zero matches.
    """
    try:
        spreadsheet_id = get_or_create_spreadsheet()
        
        if not spreadsheet_id:
            print("Could not get spreadsheet ID")
            return False
        
        access_token = get_google_sheets_client()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        rows = []
        
        if articles:
            for article in articles:
                row = [
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    article.get('title', 'N/A'),
                    article.get('link', 'N/A'),
                    article.get('source', 'Unknown'),
                    ', '.join(article.get('matched_keywords', [])),
                    str(article.get('match_score', 0)),
                    'Yes' if alert_sent else 'No',
                    search_group
                ]
                rows.append(row)
        else:
            row = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                f'[Scan completed - No matches found]',
                f'Total articles scanned: {total_fetched}',
                'System',
                'None',
                '0',
                'No',
                search_group
            ]
            rows.append(row)
        
        response = requests.post(
            f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/Alert Logs!A2:append',
            params={'valueInputOption': 'RAW'},
            headers=headers,
            json={'values': rows}
        )
        
        if articles:
            print(f"Logged {len(rows)} matched articles to Google Sheets")
        else:
            print(f"Logged scan summary (no matches) to Google Sheets")
        return True
        
    except Exception as e:
        print(f"Error logging to sheets: {e}")
        return False
