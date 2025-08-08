import os, json
from flask import Flask, session, redirect, request, jsonify
from dotenv import load_dotenv
from gcal import make_flow, creds_from_json, creds_to_json, get_freebusy, build_service
from models import init_db, SessionLocal, UserToken
from openai_utils import parse_nl_to_event
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import pytz

load_dotenv()
init_db()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'devsecret')
REDIRECT_URI = os.environ.get('GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:5000/auth/callback')

@app.route('/auth/login')
def auth_login():
    flow = make_flow(REDIRECT_URI)
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
    session['oauth_state'] = state
    return redirect(auth_url)

@app.route('/auth/callback')
def auth_callback():
    state = session.get('oauth_state')
    flow = make_flow(REDIRECT_URI)
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    user_id = None
    if creds.id_token and isinstance(creds.id_token, dict):
        user_id = creds.id_token.get('email')
    if not user_id:
        user_id = f'user_{int(datetime.now().timestamp())}'
    db = SessionLocal()
    existing = db.query(UserToken).filter_by(user_id=user_id).first()
    if existing:
        existing.credentials = creds.to_json()
    else:
        ut = UserToken(user_id=user_id, credentials=creds.to_json())
        db.add(ut)
    db.commit()
    session['user_id'] = user_id
    return redirect(os.environ.get('BASE_URL', 'http://localhost:3000') + '/')

def get_user_creds(user_id):
    db = SessionLocal()
    row = db.query(UserToken).filter_by(user_id=user_id).first()
    if not row:
        return None
    creds = Credentials.from_authorized_user_info(json.loads(row.credentials), scopes=None)
    return creds

@app.route('/api/whoami')
def whoami():
    user_id = session.get('user_id')
    return jsonify({'user_id': user_id})

@app.route('/api/suggest', methods=['POST'])
def suggest():
    data = request.json
    nl = data.get('nl_text')
    look_days = int(data.get('look_days', 7))
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error':'not_authenticated'}), 401
    creds = get_user_creds(user_id)
    if not creds:
        return jsonify({'error':'no_creds'}), 401

    parsed = parse_nl_to_event(nl)
    duration_min = parsed.get('duration_minutes') or 30
    earliest = parsed.get('earliest')
    latest = parsed.get('latest')

    now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    start_search = now if not earliest else datetime.fromisoformat(earliest)
    end_search = (now + timedelta(days=look_days)) if not latest else datetime.fromisoformat(latest)

    busy = get_freebusy(creds, time_min=start_search.isoformat(), time_max=end_search.isoformat())

    suggestions = []
    preferred = parsed.get('preferred_hours') or "09:00-17:00"
    pref_start, pref_end = preferred.split('-')
    for day_offset in range((end_search.date() - start_search.date()).days + 1):
        day = (start_search + timedelta(days=day_offset)).date()
        day_start = datetime.combine(day, datetime.strptime(pref_start, "%H:%M").time()).replace(tzinfo=pytz.UTC)
        day_end = datetime.combine(day, datetime.strptime(pref_end, "%H:%M").time()).replace(tzinfo=pytz.UTC)
        if day_end <= start_search:
            continue
        candidate = day_start
        while candidate + timedelta(minutes=duration_min) <= day_end:
            slot_start = candidate
            slot_end = candidate + timedelta(minutes=duration_min)
            conflict = False
            for b in busy:
                b_start = datetime.fromisoformat(b['start']).replace(tzinfo=pytz.UTC)
                b_end = datetime.fromisoformat(b['end']).replace(tzinfo=pytz.UTC)
                if not (slot_end <= b_start or slot_start >= b_end):
                    conflict = True
                    break
            if not conflict and slot_start >= start_search:
                suggestions.append({
                    "start": slot_start.isoformat(),
                    "end": slot_end.isoformat(),
                    "reason": f"Available in preferred hours {preferred}"
                })
                if len(suggestions) >= 6:
                    break
            candidate += timedelta(minutes=30)
        if len(suggestions) >= 6:
            break

    return jsonify({"parsed": parsed, "suggestions": suggestions})

@app.route('/api/create_event', methods=['POST'])
def create_event():
    data = request.json
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error':'not_authenticated'}), 401
    creds = get_user_creds(user_id)
    if not creds:
        return jsonify({'error':'no_creds'}), 401
    service = build_service(creds)
    event = {
        'summary': data.get('title','Meeting'),
        'start': {'dateTime': data['start'], 'timeZone': 'UTC'},
        'end': {'dateTime': data['end'], 'timeZone': 'UTC'},
    }
    if data.get('attendees'):
        event['attendees'] = [{'email': a} for a in data['attendees']]
    created = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
    return jsonify(created)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
