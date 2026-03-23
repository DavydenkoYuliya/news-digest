import { useState } from 'react';

export function useAnalyticsGeneration() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generate = async (filteredNews, filterLabel) => {
    if (!filteredNews?.length) {
      setError('Немає новин для аналізу. Завантажте дані або оберіть інші фільтри.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const items = filteredNews.slice(0, 30);
    const newsText = items
      .map((n, i) => {
        const date = n.date ? n.date.toLocaleDateString('uk-UA') : '';
        return `${i + 1}. [${date}] ${n.title}\n   ${n.summary || ''}`;
      })
      .join('\n\n');

    const prompt = `Ти — аналітик ринку сировини для менеджера із закупівель агропромислового холдингу МХП.
Нижче наведено ${items.length} новин по темі: "${filterLabel}".

Зроби структурований аналіз:

**1. Загальна ситуація** — що відбувається зараз (3-5 речень)

**2. Ключові ризики** — що може негативно вплинути на закупівлі або ціни (2-4 пункти зі знаком -)

**3. Можливості** — що може дати перевагу або позитивно вплинути (1-3 пункти зі знаком -)

**4. Прогноз на 30 днів** — короткий висновок для менеджера (2-3 речення)

Відповідай чітко, по ділу, без загальних фраз. Відповідь українською мовою.

Новини:
${newsText}`;

    try {
      const response = await fetch('https://mhp-digest-proxy.vercel.app/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error || `Помилка сервера: HTTP ${response.status}`);
      }

      const data = await response.json();
      setResult(data.text);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const clear = () => {
    setResult(null);
    setError(null);
  };

  return { generate, result, loading, error, clear };
}
