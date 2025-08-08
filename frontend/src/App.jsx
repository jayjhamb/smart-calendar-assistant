import React, { useEffect, useState } from 'react';
import LoginButton from './components/LoginButton';
import ComposeEvent from './components/ComposeEvent';
import api from './api';

export default function App(){
  const [user, setUser] = useState(null);

  useEffect(()=> {
    api.get('/api/whoami').then(res => setUser(res.data.user_id || null)).catch(()=>{});
  }, []);

  return (
    <div style={{padding:20}}>
      <h1>Smart Calendar Assistant</h1>
      {user ? (
        <>
          <p>Signed in as: {user}</p>
          <ComposeEvent />
        </>
      ) : (
        <>
          <p>Please sign in with Google to continue.</p>
          <LoginButton />
        </>
      )}
    </div>
  );
}
