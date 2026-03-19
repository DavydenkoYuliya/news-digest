
export function Header({ activeTab, setActiveTab, bookmarkCount, user, onExport, onFilterToggle, activeFiltersCount }) {

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
        <button
          className={`nav-tab ${activeTab === 'news' ? 'active' : ''}`}
          onClick={() => setActiveTab('news')}
        >
          Новини
        </button>
        <button
          className={`nav-tab ${activeTab === 'bookmarks' ? 'active' : ''}`}
          onClick={() => setActiveTab('bookmarks')}
        >
          Закладки
          {bookmarkCount > 0 && (
            <span className="bookmark-count-badge">{bookmarkCount}</span>
          )}
        </button>
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

        <button className="upload-btn" onClick={onExport} title="Експортувати поточні новини в Excel">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
          </svg>
          <span>Експорт Excel</span>
        </button>
        <div className="user-badge" onClick={user.openModal} title="Змінити ім'я">
          <div className="user-avatar">{user.initials}</div>
          <span className="user-name">{user.name}</span>
        </div>
      </div>
    </div>
  );
}
