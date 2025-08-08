import os, json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar.readonly']

def make_flow(redirect_uri):
    client_config = {
        "web": {
            "client_id": os.environ['GOOGLE_CLIENT_ID'],
            "client_secret": os.environ['GOOGLE_CLIENT_SECRET'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri)
    return flow

def creds_from_json(json_str):
    data = json.loads(json_str)
    return Credentials.from_authorized_user_info(data, SCOPES)

def creds_to_json(creds):
    return creds.to_json()

def build_service(creds):
    return build('calendar', 'v3', credentials=creds, cache_discovery=False)

def get_freebusy(creds, calendar_id='primary', time_min=None, time_max=None):
    service = build_service(creds)
    if time_min is None:
        time_min = datetime.utcnow().isoformat() + 'Z'
    if time_max is None:
        time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": calendar_id}]
    }
    resp = service.freebusy().query(body=body).execute()
    return resp.get('calendars', {}).get(calendar_id, {}).get('busy', [])
