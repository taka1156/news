# Weekly Reader

技術ニュースレター（JavaScript Weekly / Go Weekly / Ruby Weekly / PyCoder's Weekly / This Week in Rust）を、ダークモードでセクションごとにめくって読むリーダー。

## 構成

- `public/index.html` — リーダー本体。HTML・CSS・JS をこの1ファイルに収める。ビルドなし。
- `public/locales/ja.json`, `public/locales/en.json` — 画面の文言（i18next）。表示言語はブラウザの言語で初期化し、設定で切り替え。
- `public/og.png`, `public/favicon.svg` — OGP画像とアイコン（ロゴは Instrument Serif の「Weekly Reader」と「W」）。
- `worker.js` — Cloudflare Worker。静的配信と `/proxy?url=…`（記事ページの中継、許可ホストのみ）。
- `wrangler.jsonc` — Workers 設定。本番は `https://news.taka1156.site/`（独自ドメイン。旧 `news.tomo05061.workers.dev`）。
- `.claude/skills/` — 作業手順（下記）。

ページの読み込みは `kind` で3系統に分かれる：`cooper`（JS / Go / Ruby、Cooperpress 形式、`/issues/N` と `/latest`）、`pycoders`（PyCoder's Weekly、`/issues/N`）、`twir`（This Week in Rust、URLに日付が入るので過去号一覧から号数→URLの表を作る）。

## ユーザーとの約束（必ず守る）

- **見た目・UIを変えるときは、先に文章で案を出し、OKをもらってから作る。** 画像やコードを先に作らない。選択肢を出すときは、おすすめを1つ示す。
- **頼まれていないことは足さない。** 機能・装飾・自動表示（初回ツアーなど）を勝手に追加しない。
- ページ送りは本と同じ：**左が古い号（«）、右が新しい号（»）**。ページも右へ進む。
- 最新号より先へ進もうとしたらエラーにせず、今の号に留まって「#N が最新号です」と出す。
- URL：最新号を表示している間は `#latest`（ホーム画面に置いても毎回最新号が開く）。古い号は `#js-810`。`#rb-latest` は言語指定で最新号。ハッシュなし・`#latest` は最後に使った言語の最新号。
- 画面はできるだけ記事に使う。ヘッダー（約44px）とフッター（約46px）は低く保つ。フッターは送りボタンだけ。
- いつの記事かは重要なので、**号の日付は常に見える場所に出す**（ヘッダーの言語ボタン内）。
- デザインはシンプルに（紙白／墨黒、細い罫線、言語色は小さな点だけ）。ライト／ダーク両対応。
- 返答は日本語。短く、結論から。

## 作業の決まり

- 既定ブランチは **`master`**。push は `git -c push.negotiate=true push origin HEAD:master`。
- `public/index.html` を変えたら、設定パネルのバージョン表記を上げる（release スキル）。ユーザーはこれでデプロイ反映を確認する。
- `worker.js` を変えたときは、ユーザーに再デプロイ（`npx wrangler deploy`）が必要と伝える。
- 外部サイトはこの作業環境から取れない。UIの確認は check-ui、記事の切り出しの確認は debug-parse で行う。推測で「動く」と言わない。
- 外部ページの文字列は必ずエスケープして描画する（`esc()` / `textContent`）。
- **画面の文言は `public/locales/ja.json` と `en.json` の両方に追加する。** HTML は `data-i18n` / `data-i18n-aria` / `data-i18n-title` / `data-i18n-ph`、JS は `t('key')`。直書きしない。
- 外部ライブラリは cdnjs（Cloudflare）からバージョン固定で読み込む（i18next 23.16.8、Driver.js 1.3.1）。npm・ビルドは未導入（将来ビルド方式へ移行予定）。

## スキル

- `check-ui` — 仮のページでリーダーを開き、360/390px・ライト/ダークで撮影と自動チェック。
- `debug-parse` — 本物のHTMLを読み込み処理に通して、取れたセクションと記事を一覧にする。
- `add-newsletter` — ニュースレターを追加するときの更新箇所チェックリスト。
- `release` — バージョンを上げてコミットし、`master` に push する。
