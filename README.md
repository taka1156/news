# Weekly Reader

JavaScript Weekly / Go Weekly / PyCoder's Weekly / This Week in Rust / Ruby Weekly を、セクションごとにめくって読むためのページ。

- `public/index.html`: リーダー本体（1ファイル）
- `worker.js`: 静的配信と、記事ページの中継（`/proxy?url=...`、5サイトのみ許可）
- `wrangler.jsonc`: Cloudflare Workers の設定

## デプロイ

```sh
npx wrangler deploy
```
