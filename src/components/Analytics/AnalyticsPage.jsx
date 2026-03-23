import { useState, useMemo } from 'react';
import { useAnalyticsGeneration } from '../../hooks/useAnalyticsGeneration';

function getUnique(news, field) {
  const vals = new Set();
  news.forEach(n => {
    const v = n[field];
    if (v) {
      v.split(',').forEach(part => {
        const t = part.trim();
        if (t && t.toLowerCase() !== 'n/a' && t !== '-') vals.add(t);
      });
    }
  });
  return [...vals].sort();
}

function AnalyticsResult({ text }) {
  return (
    <div className="ar-body">
      {text.split('\n').map((line, i) => {
        if (!line.trim()) return <div key={i} className="ar-gap" />;

        const renderInline = (str) => {
          const parts = str.split(/(\*\*[^*]+\*\*)/g);
          return parts.map((part, j) =>
            part.startsWith('**') && part.endsWith('**')
              ? <strong key={j}>{part.slice(2, -2)}</strong>
              : part
          );
        };

        if (/^\*\*\d+\./.test(line) || (line.startsWith('**') && line.endsWith('**'))) {
          return <div key={i} className="ar-heading">{renderInline(line)}</div>;
        }
        if (line.startsWith('- ') || line.startsWith('• ')) {
          return <div key={i} className="ar-bullet">{renderInline(line.slice(2))}</div>;
        }
        return <div key={i} className="ar-para">{renderInline(line)}</div>;
      })}
    </div>
  );
}

export function AnalyticsPage({ news }) {
  const [domain, setDomain] = useState('');
  const [category, setCategory] = useState('');
  const [commodity, setCommodity] = useState('');
  const [country, setCountry] = useState('');
  const { generate, result, loading, error, clear } = useAnalyticsGeneration();

  const options = useMemo(() => ({
    domains:     getUnique(news, 'domain'),
    categories:  getUnique(news, 'category'),
    commodities: getUnique(news, 'commodity'),
    countries:   getUnique(news, 'country'),
  }), [news]);

  const filtered = useMemo(() => {
    return news.filter(n => {
      if (domain && n.domain !== domain) return false;
      if (category && n.category !== category) return false;
      if (commodity) {
        const vals = (n.commodity || '').split(',').map(s => s.trim());
        if (!vals.includes(commodity)) return false;
      }
      if (country) {
        const vals = (n.country || '').split(',').map(s => s.trim());
        if (!vals.includes(country)) return false;
      }
      return true;
    });
  }, [news, domain, category, commodity, country]);

  const hasFilters = domain || category || commodity || country;
  const filterLabel = [domain, category, commodity, country].filter(Boolean).join(', ') || 'всі новини';
  const newsCount = filtered.length;
  const usedCount = Math.min(newsCount, 30);

  const handleChange = (setter) => (e) => { setter(e.target.value); clear(); };
  const handleReset = () => { setDomain(''); setCategory(''); setCommodity(''); setCountry(''); clear(); };

  return (
    <div className="content">
      <div className="section-bar">
        <div className="section-title">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#4A90D9" strokeWidth="2">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          AI-Аналітика
        </div>
      </div>

      <div className="analytics-scroll">
        <div className="analytics-filter-bar">
          <select className="sort-select analytics-select" value={domain} onChange={handleChange(setDomain)}>
            <option value="">Всі домени</option>
            {options.domains.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
          <select className="sort-select analytics-select" value={category} onChange={handleChange(setCategory)}>
            <option value="">Всі категорії</option>
            {options.categories.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select className="sort-select analytics-select" value={commodity} onChange={handleChange(setCommodity)}>
            <option value="">Вся сировина</option>
            {options.commodities.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select className="sort-select analytics-select" value={country} onChange={handleChange(setCountry)}>
            <option value="">Всі країни</option>
            {options.countries.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          {hasFilters && (
            <button className="reset-btn analytics-reset-btn" onClick={handleReset}>Скинути</button>
          )}
        </div>

        <div className="analytics-action-bar">
          <span className="found-count">
            Знайдено: {newsCount} новин{newsCount > 30 ? ` · буде використано топ-${usedCount}` : ''}
          </span>
          <button
            className="analytics-gen-btn"
            onClick={() => generate(filtered, filterLabel)}
            disabled={loading || newsCount === 0}
          >
            {loading ? (
              <><span className="analytics-spinner" /> Аналізую...</>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
                Генерувати аналітику
              </>
            )}
          </button>
        </div>

        {error && <div className="analytics-error">{error}</div>}

        {result && (
          <div className="analytics-result-card">
            <div className="analytics-result-meta">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4A90D9" strokeWidth="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              Аналіз по: <strong>{filterLabel}</strong>
              <span className="analytics-result-count">· {usedCount} новин</span>
            </div>
            <AnalyticsResult text={result} />
          </div>
        )}

        {!result && !loading && !error && (
          <div className="analytics-placeholder">
            <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="rgba(74,144,217,0.25)" strokeWidth="1.2">
              <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            <span>Оберіть фільтри і натисніть «Генерувати аналітику»</span>
            <span className="analytics-placeholder-sub">AI проаналізує відфільтровані новини і надасть висновки щодо ризиків, можливостей та прогнозу</span>
          </div>
        )}
      </div>
    </div>
  );
}
