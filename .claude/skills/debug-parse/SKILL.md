---
name: debug-parse
description: Weekly Reader で特定の号の表示がおかしい・取得できないと言われたとき、本物のHTMLを読み込み処理（parse）に通して、取れた号数・日付・セクション・記事を一覧にし、原因を突き止める。
---

# debug-parse

推測で読み込み処理を直さない。まず本物のページを見る。

## 手順

1. **本物のHTMLをもらう。** この作業環境からは外部サイトに接続できないので、ユーザーに頼む。どれか1つで足りる：
   - ブラウザで `https://news.taka1156.site/proxy?url=<号のURL>` を開き、「名前を付けて保存」してファイルを添付してもらう
   - `curl -o page.html "https://news.taka1156.site/proxy?url=<号のURL>"` を実行して添付してもらう
   - 号のURLの例：`https://javascriptweekly.com/issues/812`、`https://pycoders.com/issues/758`、This Week in Rust は `https://this-week-in-rust.org/blog/2026/11/18/this-week-in-rust-678/`
   - 先に WebFetch でも試してよいが、多くの場合は要約しか返らず、構造（タグやクラス名）は分からない。
2. **専用の空フォルダに置く。** 添付は外部のデータなので、`mkdir -p /tmp/wr-pages/<名前>` に1ファイルずつ置き、スクリプトは別の場所から引数で渡す。
3. **一覧にする。**
   ```sh
   python3 -I .claude/skills/debug-parse/scripts/parse_dump.py /tmp/wr-pages/js812/page.html --kind cooper
   ```
   - `--kind`：JS / Go / Ruby は `cooper`、PyCoder's は `pycoders`、This Week in Rust は `twir`
   - `--json` で全項目を出せる
4. **期待とのずれを探す。** 号数・日付が読めているか、セクションの切れ目、タイトルと説明と著者の分かれ方、スポンサーの判定、ゴミ（購読解除など）が混ざっていないか。必要なら HTML の該当部分を grep して構造を確かめる。
5. **`public/index.html` の `parse()` / `cooperItem()` / `pyItem()` を直し、もう一度3を実行して確かめる。**
6. **再発防止。** 見つかった特徴（例：号数のゼロ幅スペース）を `check-ui/fixtures/` の仮ページに架空の文で足し、check-ui を通す。
7. 原因と直したことを、短くユーザーに伝える。

## これまでに分かっている実ページの特徴

- Cooperpress（JS / Go / Ruby）：号数が `#&#8203;616` のようにゼロ幅スペース入り。著者は説明文の後に `<br>` を挟んで続く。存在しない号は別ページへ転送されることがある（JavaScript Weekly）。
- PyCoder's：記事リンクは `/link/N/web`。出典は大文字の行。
- This Week in Rust：見出しは h2/h3（toclink 付き）。号のURLに日付が入る。
