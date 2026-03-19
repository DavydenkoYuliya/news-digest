import { useState, useEffect, useCallback } from 'react';
import * as XLSX from 'xlsx';
import { parseDateSafe } from '../utils/dateUtils';
import { getDomainKey, cleanSource } from '../utils/constants';

function parseRows(rows) {
  return rows.map((row, idx) => {
    const dateRaw = row['date_published_utc'] || row['Дата'] || row['date'] || '';
    const sourceRaw = String(row['source'] || row['Джерело'] || '').trim();
    const source = cleanSource(sourceRaw) || sourceRaw.slice(0, 30);
    const titleUk = String(row['title_uk'] || row['Заголовок UA'] || row['title_original'] || row['title'] || '').trim();
    const summaryUk = String(row['ai_summary'] || row['AI-резюме'] || row['summary_uk'] || row['summary'] || '').trim();
    const domain = String(row['ai_domain'] || row['Домен'] || row['domain'] || '').trim();
    const category = String(row['ai_category'] || row['Категорія'] || row['category'] || '').trim();
    const country = String(row['ai_country'] || row['Країна'] || row['country'] || '').trim();
    const commodity = String(row['ai_commodity'] || row['Сировина'] || row['commodity'] || '').trim();
    const url = String(row['url'] || row['url_canonical'] || row['Посилання'] || '').trim();

    let rawScore = row['ai_score'] || row['Score'] || '';
    let score = parseFloat(rawScore);
    if (isNaN(score)) {
      const sig = row['signal_level'] || '';
      score = sig === 'high' ? 8 : sig === 'medium' ? 5 : 3;
    }

    let parsedDate = null;
    if (dateRaw instanceof Date) {
      parsedDate = dateRaw;
    } else {
      parsedDate = parseDateSafe(String(dateRaw));
    }

    return {
      id: `n${idx}`,
      date: parsedDate,
      source,
      title: titleUk,
      summary: summaryUk,
      domain,
      domainKey: getDomainKey(domain),
      category,
      country,
      commodity,
      url,
      score,
    };
  }).filter(n => n.title);
}

export function useExcelData() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fileName, setFileName] = useState('');

  const loadFromUrl = useCallback(async (url) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const buffer = await res.arrayBuffer();
      const wb = XLSX.read(buffer, { type: 'array', cellDates: true });
      const sheet = wb.Sheets[wb.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json(sheet, { defval: '' });
      setNews(parseRows(rows));
      setFileName(url.split('/').pop());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadFromFile = useCallback((file) => {
    setLoading(true);
    setError(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const wb = XLSX.read(e.target.result, { type: 'array', cellDates: true });
        const sheet = wb.Sheets[wb.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json(sheet, { defval: '' });
        setNews(parseRows(rows));
        setFileName(file.name);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    reader.readAsArrayBuffer(file);
  }, []);

  // Auto-load from manifest on mount
  useEffect(() => {
    async function autoLoad() {
      try {
        const res = await fetch('/data/manifest.json');
        if (!res.ok) throw new Error('no manifest');
        const manifest = await res.json();
        const latest = manifest.latest || (manifest.files && manifest.files[manifest.files.length - 1]);
        if (latest) {
          await loadFromUrl(`/data/${latest}`);
          return;
        }
      } catch {
        // no manifest - try fallback
      }
      setLoading(false);
    }
    autoLoad();
  }, [loadFromUrl]);

  return { news, loading, error, fileName, loadFromFile, loadFromUrl };
}
