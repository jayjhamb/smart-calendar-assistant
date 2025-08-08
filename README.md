# Smart Calendar Assistant
Full-stack project: React frontend + Flask backend integrating OpenAI (GPT-4) and Google Calendar (OAuth2).

## Features
- Natural language parsing with GPT-4 to extract meeting details.
- Google OAuth2 + Calendar API for secure access and free/busy checks.
- REST API for suggestions and event creation.

## Local dev (quick)
1. Backend:
   - cd backend
   - copy `.env.example` to `.env` and fill values (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OPENAI_API_KEY, SECRET_KEY, BASE_URL)
   - python -m venv venv
   - source venv/bin/activate  # or venv\Scripts\activate on Windows
   - pip install -r requirements.txt
   - python app.py
2. Frontend:
   - cd frontend
   - npm install
   - npm start
