import React from 'react';

export default function LoginButton(){
  const onLogin = () => {
    window.location.href = "http://localhost:5000/auth/login";
  };
  return <button onClick={onLogin}>Sign in with Google</button>;
}
