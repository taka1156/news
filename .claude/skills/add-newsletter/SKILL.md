---
name: add-newsletter
description: Weekly Reader に新しいニュースレター（言語）を追加するときの手順と更新箇所チェックリスト。「〇〇 Weekly も追加して」と頼まれたときに使う。
---

# add-newsletter

## 1. 形式を調べる

- WebSearch / WebFetch で、号のURLの形と配信元を確かめる。
  - Cooperpress（`/issues/N` と `/latest`、Ruby / JS / Go と同じ）→ `kind: 'cooper'`。読み込み処理はそのまま使える。
  - PyCoder's 型（`/issues/N`、`/link/N/web`）→ `kind: 'pycoders'`。
  - This Week in Rust 型（URLに日付）→ `kind: 'twir'` か、号数→URLの表を作る仕組みが必要。
  - URLが号数から決まらない・ページの作りが別物 → そのまま足せない。ユーザーに「この形式は使えない」と伝え、代わりの候補を探して提案する（勝手に足さない）。
- 新しい形式なら、本物のHTMLを debug-parse の手順でもらって構造を確かめてから読み込み処理を書く。

## 2. 更新箇所（漏れなく）

`public/index.html`
- [ ] `LANGS` に1行：`xx: {label, mono:'2文字', name, kind, base, fb}`。`mono` は2文字（JS / Go / Py / Rs / Rb のように）。
- [ ] 色：`:root` に `--c-xx:light-dark(ライト用の濃い色, ダーク用の明るい色)`。既存の色（黄・水色・青・オレンジ・赤）と見分けがつくこと。
- [ ] `:root[data-lang=xx]{--acc:var(--c-xx)}`
- [ ] `fromHash` の正規表現 `#(js|go|py|rs|rb|xx)`
- [ ] `<meta name="description">` と `og:description` にニュースレター名
- [ ] ツアーの文言「JS / Go / … を切り替えられます」
- [ ] 新しい形式なら `parse()` に分岐を追加

`worker.js`
- [ ] `ALLOW` にホスト名（`www.` の有無に注意）

その他
- [ ] `README.md` の対象一覧と「Nサイトのみ許可」
- [ ] `CLAUDE.md` の対象一覧（と、新しい kind なら説明）
- [ ] 新しい形式なら `check-ui/fixtures/` に仮ページ（架空の文で）と `check_ui.py` の `KINDS` / `fixture_for` を追加

## 3. 確かめて出す

1. check-ui を実行（言語メニューに出ること、360px でヘッダーが収まること）。
2. release スキルでバージョンを上げて push。
3. `worker.js` を変えたので、ユーザーに再デプロイ（`npx wrangler deploy`、または GitHub 連携なら push で自動）が必要と伝える。
