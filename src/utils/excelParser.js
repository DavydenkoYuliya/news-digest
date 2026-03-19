import * as XLSX from 'xlsx';
import { parseDateSafe } from './dateUtils';
import { getDomainKey as getDK } from './constants';

/**
 * Parse ArrayBuffer of an xlsx/csv file into news array
 */
export function parseExcelBuffer(buffer) {
  const workbook = XLSX.read(buffer, { type: 'array', cellDates: true });
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];
  const rows = XLSX.utils.sheet_to_json(sheet, { defval: '' });

  return rows.map((row, idx) => {
    // Map columns (support both xlsx and csv column names)
    const dateRaw = row['date_published_utc'] || row['Дата'] || row['date'] || '';
    const source = row['source'] || row['Джерело'] || '';
    const titleUk = row['title_uk'] || row['Заголовок UA'] || row['title'] || '';
    const summaryUk = row['ai_summary'] || row['AI-резюме'] || row['summary'] || '';
    const domain = row['ai_domain'] || row['Домен'] || row['domain'] || '';
    const category = row['ai_category'] || row['Категорія'] || row['category'] || '';
    const country = row['ai_country'] || row['Країна'] || row['country'] || '';
    const commodity = row['ai_commodity'] || row['Сировина'] || row['commodity'] || '';
    const url = row['url'] || row['Посилання'] || row['url_canonical'] || '';
    const score = parseFloat(row['ai_score'] || row['Score'] || row['signal_level'] === 'high' ? 8 : 5) || 0;

    let parsedDate = null;
    if (dateRaw instanceof Date) {
      parsedDate = dateRaw;
    } else {
      parsedDate = parseDateSafe(String(dateRaw));
    }

    return {
      id: `news_${idx}_${String(titleUk).slice(0, 20)}`,
      date: parsedDate,
      dateRaw: String(dateRaw),
      source: String(source).trim(),
      title: String(titleUk || row['title_original'] || '').trim(),
      summary: String(summaryUk || row['summary_original'] || '').trim(),
      domain: String(domain).trim(),
      domainKey: getDK(String(domain).trim()),
      category: String(category).trim(),
      country: String(country).trim(),
      commodity: String(commodity).trim(),
      url: String(url).trim(),
      score: isNaN(score) ? 0 : score,
    };
  }).filter(n => n.title);
}
