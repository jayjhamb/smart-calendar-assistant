import React, {useState} from 'react';
import api from '../api';

export default function ComposeEvent(){
  const [text, setText] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [parsed, setParsed] = useState(null);

  async function handleSuggest(){
    const res = await api.post('/api/suggest', { nl_text: text, look_days: 14 });
    if(res.data){
      setParsed(res.data.parsed);
      setSuggestions(res.data.suggestions || []);
    }
  }

  async function createEvent(s){
    const title = parsed?.title || "Meeting";
    const body = { start: s.start, end: s.end, title, attendees: parsed?.attendees || [] };
    const res = await api.post('/api/create_event', body);
    alert("Created: " + (res.data.htmlLink || res.status));
  }

  return (
    <div>
      <h3>Describe what you'd like to schedule</h3>
      <textarea value={text} onChange={e=>setText(e.target.value)} rows={4} cols={80} />
      <div>
        <button onClick={handleSuggest}>Suggest Times</button>
      </div>
      {parsed && <pre>Parsed: {JSON.stringify(parsed, null, 2)}</pre>}
      <h4>Suggestions</h4>
      <ul>
        {suggestions.map((s, i) => (
          <li key={i}>
            {new Date(s.start).toLocaleString()} — {new Date(s.end).toLocaleString()} ({s.reason})
            <button onClick={()=>createEvent(s)} style={{marginLeft:10}}>Create Event</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
