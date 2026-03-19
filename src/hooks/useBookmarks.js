import { useState, useEffect, useCallback } from 'react';

const KEY = 'mhp_bookmarks';
const EXPIRE_DAYS = 30;

function loadBookmarks() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return {};
    const data = JSON.parse(raw);
    const now = Date.now();
    const cleaned = {};
    for (const [id, item] of Object.entries(data)) {
      if (item.expiresAt > now) {
        // Restore date string → Date object
        if (item.date && !(item.date instanceof Date)) {
          const d = new Date(item.date);
          item.date = isNaN(d.getTime()) ? null : d;
        }
        cleaned[id] = item;
      }
    }
    return cleaned;
  } catch {
    return {};
  }
}

export function useBookmarks() {
  const [bookmarks, setBookmarks] = useState(loadBookmarks);

  useEffect(() => {
    try {
      localStorage.setItem(KEY, JSON.stringify(bookmarks));
    } catch {}
  }, [bookmarks]);

  const isBookmarked = useCallback((id) => !!bookmarks[id], [bookmarks]);

  const toggle = useCallback((newsItem) => {
    setBookmarks(prev => {
      if (prev[newsItem.id]) {
        const next = { ...prev };
        delete next[newsItem.id];
        return next;
      } else {
        const expiresAt = Date.now() + EXPIRE_DAYS * 24 * 60 * 60 * 1000;
        return {
          ...prev,
          [newsItem.id]: { ...newsItem, savedAt: Date.now(), expiresAt },
        };
      }
    });
    return !bookmarks[newsItem.id];
  }, [bookmarks]);

  const bookmarkList = Object.values(bookmarks).sort((a, b) => b.savedAt - a.savedAt);

  return { bookmarks, bookmarkList, isBookmarked, toggle };
}
