const OWNER = 'DavydenkoYuliya';
const REPO = 'news-digest';
const BRANCH = 'main';
const LOG_PATH = 'public/data/analytics_log.jsonl';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', 'https://davydenkoyuliya.github.io');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { user, tab } = req.body || {};
  if (!user || !tab) return res.status(400).json({ error: 'Missing user or tab' });

  const token = process.env.GITHUB_TOKEN;
  if (!token) return res.status(500).json({ error: 'Server misconfigured: no GITHUB_TOKEN' });

  const line = JSON.stringify({
    ts: new Date().toISOString(),
    user: String(user).slice(0, 50),
    tab: String(tab).slice(0, 30),
  });

  const url = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${LOG_PATH}`;
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: 'application/vnd.github+json',
  };

  try {
    // Retry loop: handles the race where two visits write at nearly the same
    // moment and the second PUT gets rejected because the file's sha moved.
    for (let attempt = 0; attempt < 3; attempt++) {
      const getRes = await fetch(`${url}?ref=${BRANCH}`, { headers });

      let sha;
      let existingContent = '';
      if (getRes.status === 200) {
        const data = await getRes.json();
        sha = data.sha;
        existingContent = Buffer.from(data.content, 'base64').toString('utf-8');
      } else if (getRes.status !== 404) {
        return res.status(502).json({ error: `GitHub GET failed: ${getRes.status}` });
      }

      const sep = existingContent && !existingContent.endsWith('\n') ? '\n' : '';
      const newContent = existingContent + sep + line + '\n';

      const putBody = {
        message: `track: ${line}`,
        content: Buffer.from(newContent, 'utf-8').toString('base64'),
        branch: BRANCH,
      };
      if (sha) putBody.sha = sha;

      const putRes = await fetch(url, {
        method: 'PUT',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify(putBody),
      });

      if (putRes.ok) return res.status(200).json({ ok: true });
      if (putRes.status === 409 && attempt < 2) continue; // sha conflict, retry

      const errData = await putRes.json().catch(() => ({}));
      return res.status(502).json({ error: errData.message || `GitHub PUT failed: ${putRes.status}` });
    }
    return res.status(409).json({ error: 'Conflict after retries' });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
}
