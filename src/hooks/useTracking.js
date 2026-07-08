import { useEffect, useRef } from 'react';

const TRACK_URL = 'https://news-digest-eosin.vercel.app/api/track';

// Fires once per (user, tab) change. Best-effort — never blocks the UI
// and silently ignores failures (tracking must not affect the app).
export function useTracking(user, tab) {
  const lastKey = useRef(null);

  useEffect(() => {
    if (!user || !tab) return;
    const key = `${user}::${tab}`;
    if (lastKey.current === key) return;
    lastKey.current = key;

    fetch(TRACK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user, tab }),
    }).catch(() => {});
  }, [user, tab]);
}
