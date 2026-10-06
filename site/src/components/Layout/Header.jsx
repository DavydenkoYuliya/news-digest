
export function Header({ activeTab, setActiveTab, onFilterToggle, activeFiltersCount }) {

  return (
    <div className="header">
      <div className="header-world-map" />

      <div className="logo">
        <svg viewBox="0 0 32 32" fill="none">
          <defs>
            <linearGradient id="globeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style={{ stopColor: '#4A90D9' }} />
              <stop offset="100%" style={{ stopColor: '#2563EB' }} />
            </linearGradient>
          </defs>
          <circle cx="16" cy="16" r="14" fill="url(#globeGrad)" stroke="white" strokeWidth="1.5"/>
          <ellipse cx="16" cy="16" rx="6" ry="14" fill="none" stroke="white" strokeWidth="1.2" opacity="0.6"/>
          <ellipse cx="16" cy="16" rx="14" ry="6" fill="none" stroke="white" strokeWidth="1.2" opacity="0.6"/>
          <line x1="2" y1="16" x2="30" y2="16" stroke="white" strokeWidth="1" opacity="0.5"/>
          <circle cx="8" cy="6" r="1.5" fill="white" opacity="0.8"/>
          <circle cx="26" cy="8" r="1" fill="white" opacity="0.7"/>
          <circle cx="24" cy="24" r="1.2" fill="white" opacity="0.9"/>
        </svg>
        <span className="logo-text">MHP AI Digest News</span>
      </div>

      <div className="nav-tabs">
        {[
          ['today', 'Головне сьогодні'],
          ['news', 'Новини'],
          ['market', 'Ринок закупівель'],
          ['competitors', 'Конкуренти'],
        ].map(([key, label]) => (
          <button key={key} className={`nav-tab ${activeTab === key ? 'active' : ''}`} onClick={() => setActiveTab(key)}>
            {label}
          </button>
        ))}
      </div>

      <div className="header-right">
        {/* Mobile filter button — visible only on mobile */}
        {activeTab === 'news' && (
          <button className="filter-mob-btn" onClick={onFilterToggle} title="Фільтри">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46"/>
            </svg>
            {activeFiltersCount > 0 && (
              <span className="filter-mob-badge">{activeFiltersCount}</span>
            )}
          </button>
        )}

      </div>
    </div>
  );
}
