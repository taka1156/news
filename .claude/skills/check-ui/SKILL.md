---
name: check-ui
description: Weekly Reader（public/index.html）の画面を、仮のページを使って幅360/390px・ライト/ダークで開き、撮影と自動チェックをする。UIやページ分割、読み込み処理を変えたあと、push する前に使う。
---

# check-ui

この作業環境からは javascriptweekly.com などの本物のサイトに接続できない。仮のサイト `http://wr.test` で `public/` を配信し、Worker の `/proxy` の代わりに `fixtures/` の仮ページを返してリーダーを開き、見た目と動作を確かめる。

## 手順

1. 実行する（Playwright の Chromium を使う。無ければ `pip install --break-system-packages playwright && python3 -m playwright install chromium`）。
   ```sh
   python3 .claude/skills/check-ui/scripts/check_ui.py --out /tmp/wr-check
   ```
   - 一部だけ: `--kinds twir --widths 360 --themes dark --locales en`
   - 既定で表示言語 ja / en の両方を確認する（24通り）。i18next は外から取れないので、`/tmp/wr-vendor/i18next.min.js` があればそれを使う（`npm pack i18next@23.16.8` して `package/dist/umd/i18next.min.js` を置く）。無くても代わりの仕組みで文言は出る。
2. 出力の `[NG]` 行を直す。チェック内容：
   - スクリプトエラー
   - ヘッダー／フッターの横はみ出し（360px で全ボタンが収まること）
   - 記事0件・フォールバック表示（＝読み込み処理が壊れた）
   - 縦にはみ出すページ（2件以上入っているのに画面に収まらない）
   - 日付が出ていない
   - 翻訳されていないキー（`nav.next` など）がそのまま表示されている、html の lang が表示言語と違う
3. `/tmp/wr-check/sheet.png` を Read で見て、崩れがないか目でも確認する。
4. 結果をユーザーに伝えるときは「仮のページで確認した」と明記する。本物のページでの動作は保証しない。

## 仮ページ（fixtures）

| ファイル | 対象 | 再現している特徴 |
|---|---|---|
| `cooper.html` | JS / Go / Ruby Weekly | 号数のゼロ幅スペース、`el-item item`、`<br>` 後の著者、`IN BRIEF:`、`th` 見出し、sponsor、画像 |
| `pycoders.html` | PyCoder's Weekly | `/link/N/web`、大文字の出典行、`sponsor` 接尾、h2 見出し |
| `twir.html` | This Week in Rust | h2/h3 + toclink、li の記事、リスト前ラベル（Rust/Cargo）、入れ子リスト、段落だけのセクション、長いリスト |
| `twir-archive.html` | This Week in Rust 過去号一覧 | 号数→URL の対応表 |

本物のページで新しい崩れ方が見つかったら（debug-parse で原因が分かったら）、その特徴を仮ページに足して再発を防ぐ。記事の中身は架空の文にする（実在の記事本文をコピーしない）。
