// Weekly Reader 用 Worker：静的ファイル配信 + 記事ページの中継（/proxy?url=...）
const ALLOW = ['javascriptweekly.com', 'golangweekly.com', 'pycoders.com', 'this-week-in-rust.org'];

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname !== '/proxy') return env.ASSETS.fetch(req);

    let target;
    try { target = new URL(u.searchParams.get('url') || ''); } catch { return new Response('bad url', { status: 400 }); }
    if (target.protocol !== 'https:' || !ALLOW.includes(target.hostname)) return new Response('forbidden', { status: 403 });

    const r = await fetch(target, {
      headers: { 'user-agent': 'Mozilla/5.0 (WeeklyReader)', accept: 'text/html,application/xml' },
      cf: { cacheTtl: 600, cacheEverything: true },
    });
    return new Response(r.body, {
      status: r.status,
      headers: {
        'content-type': r.headers.get('content-type') || 'text/html; charset=utf-8',
        'cache-control': 'public, max-age=600',
        'access-control-allow-origin': '*',
        'x-weekly-proxy': '1',
        'x-final-url': r.url,
      },
    });
  },
};
