export const DOMAIN_MAP = {
  'логістика': 'logistics',
  'геополітика': 'geo',
  'енергетика': 'energy',
  'агро': 'agro',
  'агрокультури': 'agro',
  'фінанси': 'finance',
  'регуляторне': 'regulatory',
  'страйки_перебої': 'logistics',
  'страйки': 'logistics',
  'перебої': 'logistics',
  'торгівля': 'finance',
  'санкції': 'regulatory',
  'politics': 'geo',
  'logistics': 'logistics',
  'energy': 'energy',
  'finance': 'finance',
};

export const DOMAIN_ICONS = {
  logistics: (
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M1 3h15v13H1z"/><path d="M16 8h4l3 3v5h-7V8z"/>
      <circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
    </svg>`
  ),
  geo: (
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
    </svg>`
  ),
  energy: (
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>`
  ),
  agro: (
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 22V8M5 12l7-4 7 4M9 6l3-4 3 4"/>
    </svg>`
  ),
  finance: (
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
      <polyline points="16 7 22 7 22 13"/>
    </svg>`
  ),
  regulatory: (
    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
    </svg>`
  ),
};

export function getDomainKey(domainUk) {
  if (!domainUk) return 'geo';
  const lower = domainUk.toLowerCase().trim();
  return DOMAIN_MAP[lower] || 'geo';
}

export function getScoreClass(score) {
  const s = parseFloat(score);
  if (s >= 8) return 'score-high';
  if (s >= 5) return 'score-mid';
  return 'score-low';
}

export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Clean long source names:
// "Al Jazeera – Breaking News..." → "Al Jazeera"
// '"site:reuters.com..." - Google News' → "Google News"
export function cleanSource(raw) {
  if (!raw) return '';
  let s = String(raw).replace(/^["']/, '').trim();
  if (s.includes(' - ')) {
    const parts = s.split(' - ');
    const last = parts[parts.length - 1].trim();
    // If last part looks like a real name (not a search query), use it
    if (!last.includes(':') && last.length < 60) s = last;
    else s = parts[0].trim();
  }
  if (s.includes(' – ')) s = s.split(' – ')[0].trim();
  if (s.length > 30) s = s.slice(0, 28) + '…';
  return s;
}

// Return first N countries from comma-separated string
export function firstCountries(str, n = 2) {
  if (!str) return [];
  return str.split(',').map(s => s.trim()).filter(Boolean).slice(0, n);
}
