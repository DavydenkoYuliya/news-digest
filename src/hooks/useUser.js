import { useState, useEffect } from 'react';

const KEY = 'mhp_username';

export function useUser() {
  const [name, setName] = useState(() => localStorage.getItem(KEY) || '');
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (!name) setShowModal(true);
  }, [name]);

  const saveName = (n) => {
    const trimmed = n.trim();
    if (!trimmed) return;
    localStorage.setItem(KEY, trimmed);
    setName(trimmed);
    setShowModal(false);
  };

  const initials = name
    ? name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
    : '?';

  return { name, initials, showModal, setShowModal, saveName };
}
