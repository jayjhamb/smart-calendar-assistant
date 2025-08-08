import os, openai
openai.api_key = os.environ.get('OPENAI_API_KEY')

def parse_nl_to_event(nl_text):
    prompt = f"""
You are an assistant that extracts structured scheduling requests from human text.
Input: """{nl_text}"""
Output strictly JSON with keys:
title, duration_minutes, earliest (ISO date or null), latest (ISO date or null), preferred_hours (e.g. "09:00-12:00"), attendees (array of emails) .
If unknown put null or [].
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"system","content":"You convert text to calendar scheduling JSON."},
                  {"role":"user","content":prompt}],
        temperature=0
    )
    text = resp.choices[0].message.content.strip()
    import re, json
    m = re.search(r'(\{[\s\S]*\})', text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return {"title": nl_text[:60], "duration_minutes": 30, "earliest": None, "latest": None, "preferred_hours": None, "attendees": []}
