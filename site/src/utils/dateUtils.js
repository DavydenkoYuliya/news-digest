/**
 * Returns the cutoff boundaries for news sections.
 * Boundaries are based on 05:00 cutoff times.
 * If referenceDate is provided (e.g. max date in loaded data), boundaries are
 * computed relative to it — so the "latest" section always matches the digest.
 * If omitted, uses current time.
 */
export function getDateBoundaries() {
  const now = new Date();

  // Use the last 05:00 that has already passed as the upper bound
  // e.g. on 23.03 at 10:00 → cutoff = 23.03 05:00
  // e.g. on 23.03 at 03:00 → cutoff = 22.03 05:00 (today's 05:00 hasn't arrived yet)
  const cutoff = new Date(now);
  cutoff.setHours(5, 0, 0, 0);
  if (now < cutoff) {
    cutoff.setDate(cutoff.getDate() - 1);
  }

  const d1 = new Date(cutoff); d1.setDate(d1.getDate() - 1);
  const d2 = new Date(cutoff); d2.setDate(d2.getDate() - 2);
  const d3 = new Date(cutoff); d3.setDate(d3.getDate() - 3);

  return {
    todayStart: cutoff,  // e.g. 23.03 05:00
    yestStart: d1,       // e.g. 22.03 05:00
    day2Start: d2,       // e.g. 21.03 05:00
    day3Start: d3,       // e.g. 20.03 05:00
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
