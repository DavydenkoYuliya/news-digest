import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Прибираємо те, що зберігала попередня версія сайту: ім'я користувача і закладки.
try { ['mhp_username', 'mhp_bookmarks'].forEach(k => localStorage.removeItem(k)); } catch {}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
