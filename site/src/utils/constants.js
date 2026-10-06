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
