import { useState, useEffect, useCallback } from 'react';

let toastFn = null;

export function showToast(msg) {
  if (toastFn) toastFn(msg);
}

export function Toast() {
  const [msg, setMsg] = useState(null);

  useEffect(() => {
    toastFn = setMsg;
    return () => { toastFn = null; };
  }, []);

  useEffect(() => {
    if (!msg) return;
    const t = setTimeout(() => setMsg(null), 3000);
    return () => clearTimeout(t);
  }, [msg]);

  if (!msg) return null;

  return (
    <div className="toast">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
      {msg}
    </div>
  );
}
