import { useState, useMemo, useEffect } from 'react';

const LS_KEY = 'mhp_filters';

function loadFilters() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

const DEFAULT_FILTERS = {
  search: '',
  minScore: 1,
  domains: [],
  categories: [],
  countries: [],
  commodities: [],
  sort: 'score',
};

export function useFilters(news) {
  const saved = loadFilters();
  const [filters, setFilters] = useState({ ...DEFAULT_FILTERS, ...saved });

  useEffect(() => {
    try { localStorage.setItem(LS_KEY, JSON.stringify(filters)); } catch {}
  }, [filters]);

  // Build unique option lists from data
  const options = useMemo(() => {
    const count = (key) => {
      const map = {};
      news.forEach(n => {
        const val = n[key];
        if (!val) return;
        // Multi-value fields (country, commodity) split by comma
        const parts = String(val).split(',').map(s => s.trim()).filter(Boolean);
        parts.forEach(p => { map[p] = (map[p] || 0) + 1; });
      });
      return Object.entries(map).sort((a, b) => b[1] - a[1]);
    };
    return {
      domains: count('domain'),
      categories: count('category'),
      countries: count('country'),
      commodities: count('commodity'),
    };
  }, [news]);

  const filtered = useMemo(() => {
    let result = news;
    const q = filters.search.toLowerCase().trim();

    if (q) {
      result = result.filter(n =>
        n.title.toLowerCase().includes(q) ||
        n.summary.toLowerCase().includes(q) ||
        n.source.toLowerCase().includes(q)
      );
    }

    if (filters.minScore > 1) {
      result = result.filter(n => n.score >= filters.minScore);
    }

    if (filters.domains.length > 0) {
      result = result.filter(n => filters.domains.includes(n.domain));
    }
    if (filters.categories.length > 0) {
      result = result.filter(n => filters.categories.some(c => n.category.includes(c)));
    }
    if (filters.countries.length > 0) {
      result = result.filter(n => {
        const parts = n.country.split(',').map(s => s.trim());
        return filters.countries.some(c => parts.includes(c));
      });
    }
    if (filters.commodities.length > 0) {
      result = result.filter(n => {
        const parts = n.commodity.split(',').map(s => s.trim());
        return filters.commodities.some(c => parts.includes(c));
      });
    }

    // Sort
    if (filters.sort === 'score') {
      result = [...result].sort((a, b) => b.score - a.score);
    } else if (filters.sort === 'date_new') {
      result = [...result].sort((a, b) => {
        const da = a.date ? a.date.getTime() : 0;
        const db = b.date ? b.date.getTime() : 0;
        return db - da;
      });
    } else if (filters.sort === 'date_old') {
      result = [...result].sort((a, b) => {
        const da = a.date ? a.date.getTime() : 0;
        const db = b.date ? b.date.getTime() : 0;
        return da - db;
      });
    } else if (filters.sort === 'source') {
      result = [...result].sort((a, b) => a.source.localeCompare(b.source));
    }

    return result;
  }, [news, filters]);

  const reset = () => setFilters(DEFAULT_FILTERS);

  const setFilter = (key, value) => setFilters(f => ({ ...f, [key]: value }));

  const toggleMulti = (key, value) => {
    setFilters(f => {
      const arr = f[key];
      return {
        ...f,
        [key]: arr.includes(value) ? arr.filter(v => v !== value) : [...arr, value],
      };
    });
  };

  return { filters, filtered, options, setFilter, toggleMulti, reset };
}
