#!/usr/bin/env python3
"""public/index.html のバージョン表記（<meta name="version"> と設定パネルの <span id="ver">）を上げる。

形式: YYYY-MM-DD.N（同じ日なら N+1、日付が変わったら .1）
使い方: python3 .claude/skills/release/scripts/bump_version.py [--date YYYY-MM-DD]
新しいバージョンを標準出力に出す。
"""
import argparse, datetime, pathlib, re, sys

INDEX = pathlib.Path(__file__).resolve().parents[4] / "public" / "index.html"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    s = INDEX.read_text(encoding="utf-8")
    m = re.search(r'<meta name="version" content="(\d{4}-\d{2}-\d{2})\.(\d+)">', s)
    if not m:
        sys.exit("バージョン表記が見つかりません")
    old = f"{m.group(1)}.{m.group(2)}"
    new = f"{a.date}.{int(m.group(2)) + 1}" if m.group(1) == a.date else f"{a.date}.1"
    n_meta = s.count(f'content="{old}"'); n_ui = s.count(f'<span id="ver">{old}</span>')
    if n_meta != 1 or n_ui != 1:
        sys.exit(f"表記の数が想定と違います（meta={n_meta}, 設定パネル={n_ui}）")
    s = s.replace(f'content="{old}"', f'content="{new}"').replace(f'<span id="ver">{old}</span>', f'<span id="ver">{new}</span>')
    INDEX.write_text(s, encoding="utf-8")
    print(new)


if __name__ == "__main__":
    main()
