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

// Apply all filters except those listed in `skip`
function applyFilters(news, filters, skip = []) {
  let result = news;
  const q = filters.search.toLowerCase().trim();

  if (q) {
    result = result.filter(n =>
      n.title.toLowerCase().includes(q) ||
      n.summary.toLowerCase().includes(q) ||
      n.source.toLowerCase().includes(q) ||
      n.country.toLowerCase().includes(q) ||
      n.domain.toLowerCase().includes(q) ||
      n.category.toLowerCase().includes(q) ||
      n.commodity.toLowerCase().includes(q)
    );
  }

  if (filters.minScore > 1) {
    result = result.filter(n => n.score >= filters.minScore);
  }

  if (!skip.includes('domains') && filters.domains.length > 0) {
    result = result.filter(n => filters.domains.includes(n.domain));
  }
  if (!skip.includes('categories') && filters.categories.length > 0) {
    result = result.filter(n => filters.categories.some(c => n.category.includes(c)));
  }
  if (!skip.includes('countries') && filters.countries.length > 0) {
    result = result.filter(n => {
      const parts = n.country.split(',').map(s => s.trim());
      return filters.countries.some(c => parts.includes(c));
    });
  }
  if (!skip.includes('commodities') && filters.commodities.length > 0) {
    result = result.filter(n => {
      const parts = n.commodity.split(',').map(s => s.trim());
      return filters.commodities.some(c => parts.includes(c));
    });
  }

  return result;
}

function countField(rows, key) {
  const map = {};
  rows.forEach(n => {
    const val = n[key];
    if (!val) return;
    const parts = String(val).split(',').map(s => s.trim()).filter(Boolean);
    parts.forEach(p => { map[p] = (map[p] || 0) + 1; });
  });
  return Object.entries(map).sort((a, b) => a[0].localeCompare(b[0], 'uk-UA', { sensitivity: 'base' }));
}

export function useFilters(news) {
  const saved = loadFilters();
  const [filters, setFilters] = useState({ ...DEFAULT_FILTERS, ...saved });

  useEffect(() => {
    try { localStorage.setItem(LS_KEY, JSON.stringify(filters)); } catch {}
  }, [filters]);

  // Cross-filtered options: each filter's options are based on all OTHER active filters
  const options = useMemo(() => ({
    domains:     countField(applyFilters(news, filters, ['domains']),     'domain'),
    categories:  countField(applyFilters(news, filters, ['categories']),  'category'),
    countries:   countField(applyFilters(news, filters, ['countries']),   'country'),
    commodities: countField(applyFilters(news, filters, ['commodities']), 'commodity'),
  }), [news, filters]);

  const filtered = useMemo(() => {
    let result = applyFilters(news, filters);

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
  const setMulti = (key, values) => {
    setFilters(f => ({ ...f, [key]: values }));
  };

  return { filters, filtered, options, setFilter, toggleMulti, setMulti, reset };
}
