/**
 * Returns the cutoff boundaries for news sections.
 * "Today" = last 24h from 07:00 of today
 * "Yesterday" = prev 24h
 * "2 days ago" = prev 24h before that
 */
export function getDateBoundaries() {
  const now = new Date();
  const todayMorning = new Date(now);
  todayMorning.setHours(7, 0, 0, 0);

  // If current time < 07:00, "today morning" is yesterday's 07:00
  if (now < todayMorning) {
    todayMorning.setDate(todayMorning.getDate() - 1);
  }

  const d1 = new Date(todayMorning); d1.setDate(d1.getDate() - 1);
  const d2 = new Date(todayMorning); d2.setDate(d2.getDate() - 2);
  const d3 = new Date(todayMorning); d3.setDate(d3.getDate() - 3);

  return {
    todayStart: todayMorning,  // e.g. 18.03 07:00
    yestStart: d1,             // e.g. 17.03 07:00
    day2Start: d2,             // e.g. 16.03 07:00
    day3Start: d3,             // e.g. 15.03 07:00
  };
}

export function formatTime(dateStr) {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    return d.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
}

export function formatDateShort(dateStr) {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit' });
  } catch {
    return '';
  }
}

export function formatDateLong(date) {
  return date.toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', year: 'numeric' });
}

export function parseDateSafe(dateStr) {
  if (!dateStr) return null;
  try {
    // Handle "YYYY-MM-DD HH:MM:SS" format (no T)
    const normalized = String(dateStr).replace(' ', 'T');
    const d = new Date(normalized);
    if (isNaN(d.getTime())) return null;
    return d;
  } catch {
    return null;
  }
}
