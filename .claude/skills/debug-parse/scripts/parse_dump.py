#!/usr/bin/env python3
"""保存した本物の号ページを Weekly Reader の読み込み処理に通し、取れた中身を一覧にする。

使い方:
  python3 -I .claude/skills/debug-parse/scripts/parse_dump.py PAGE.html --kind cooper|pycoders|twir [--json]

PAGE.html は外部から取ってきたファイルなので、専用の空フォルダに置くこと。
このスクリプトはファイルを文字列として読み、ブラウザ内の DOMParser に渡すだけで、中のスクリプトは実行しない。
"""
import argparse, json, pathlib, sys

REPO = pathlib.Path(__file__).resolve().parents[4]
INDEX = REPO / "public" / "index.html"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--kind", required=True, choices=["cooper", "pycoders", "twir"])
    ap.add_argument("--json", action="store_true", help="結果をJSONで出す")
    a = ap.parse_args()
    html = pathlib.Path(a.page).read_text(encoding="utf-8", errors="replace")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.route("**/*", lambda r: r.continue_() if r.request.url.startswith("file:") else r.abort())
        pg.goto(INDEX.as_uri() + "#js-1")
        pg.wait_for_function("window.WR_DEBUG && window.WR_DEBUG.parse")
        res = pg.evaluate("([h, k]) => window.WR_DEBUG.parse(h, k)", [html, a.kind])
        b.close()

    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1)); return
    print(f"号数: {res.get('num') or '（読めず）'}   日付: {res.get('date') or '（読めず）'}")
    secs = res.get("sections", [])
    print(f"セクション: {len(secs)}   記事: {sum(len(s['items']) for s in secs)}\n")
    for s in secs:
        print(f"■ {s['name']}（{len(s['items'])}件）")
        for it in s["items"]:
            flags = (" [Sponsor]" if it.get("sp") else "") + (" [画像]" if it.get("img") else "")
            title = it.get("title") or "（タイトルなし：段落）"
            print(f"  - {title}{flags}")
            if it.get("author"): print(f"      著者/出典: {it['author']}")
            d = (it.get("desc") or "")
            if d: print(f"      {d[:110]}{'…' if len(d) > 110 else ''}")
        print()
    if not secs:
        print("記事が1件も取れていません。ページの構造が想定と違います。")
        sys.exit(1)


if __name__ == "__main__":
    main()
