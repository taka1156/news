#!/usr/bin/env python3
"""Weekly Reader の画面チェック。

仮のサイト（http://wr.test）で public/ を配信し、/proxy では外部サイトの代わりに fixtures/ の仮ページを返してリーダーを開き、
幅 360/390px・ライト/ダークで撮影し、次を自動で確かめる：
  - スクリプトのエラーが出ていない
  - ヘッダーとフッターのボタンが横にはみ出していない
  - 記事が取れている（ページ数・記事数 > 0）
  - どのページも縦にはみ出していない
  - 号の日付が表示されている

使い方:
  python3 .claude/skills/check-ui/scripts/check_ui.py [--out DIR] [--kinds cooper,pycoders,twir]
終了コード: 問題なし 0 / 問題あり 1
"""
import argparse, json, pathlib, sys
from urllib.parse import unquote

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
REPO = SKILL.parents[2]
FIX = SKILL / "fixtures"
INDEX = REPO / "public" / "index.html"
ORIGIN = "http://wr.test"  # Worker と同じく /proxy を持つ仮のサイト

# kind → (開くハッシュ, 仮ページを選ぶ関数)
KINDS = {
    "cooper": "#js-812",
    "pycoders": "#py-758",
    "twir": "#rs-678",
}


def fixture_for(target: str) -> str:
    if "this-week-in-rust" in target:
        name = "twir-archive.html" if ("archives" in target or "atom.xml" in target) else "twir.html"
    elif "pycoders" in target:
        name = "pycoders.html"
    else:
        name = "cooper.html"
    return (FIX / name).read_text(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/wr-check")
    ap.add_argument("--kinds", default=",".join(KINDS))
    ap.add_argument("--widths", default="360,390")
    ap.add_argument("--themes", default="light,dark")
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    problems, shots, report = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for kind in a.kinds.split(","):
            for w in map(int, a.widths.split(",")):
                for theme in a.themes.split(","):
                    tag = f"{kind}-{w}-{theme}"
                    page = browser.new_page(viewport={"width": w, "height": 760}, color_scheme=theme)
                    errors = []
                    page.on("pageerror", lambda e, errors=errors: errors.append(str(e)))

                    def route(r):
                        u = r.request.url
                        if u.startswith(ORIGIN + "/proxy?url="):  # Worker の /proxy の代わり
                            target = unquote(u.split("url=", 1)[1])
                            return r.fulfill(status=200, body=fixture_for(target),
                                             headers={"content-type": "text/html; charset=utf-8", "x-weekly-proxy": "1", "x-final-url": target})
                        if u.startswith(ORIGIN + "/"):  # 静的ファイル（public/）
                            path = u[len(ORIGIN) + 1:].split("?")[0].split("#")[0] or "index.html"
                            f = (REPO / "public" / path)
                            if f.is_file():
                                ctype = {"html": "text/html; charset=utf-8", "png": "image/png", "svg": "image/svg+xml"}.get(f.suffix[1:], "application/octet-stream")
                                return r.fulfill(status=200, body=f.read_bytes(), headers={"content-type": ctype})
                            return r.fulfill(status=404, body="not found")
                        return r.abort()  # フォントや画像など外部は読み込まない

                    page.route("**/*", route)
                    page.add_init_script("try{localStorage.clear()}catch(e){}")
                    page.goto(ORIGIN + "/" + KINDS[kind])
                    page.wait_for_timeout(1200)

                    st = page.evaluate("""() => {
                      const q = s => document.querySelector(s);
                      const over = el => el ? el.scrollWidth - el.clientWidth : 0;
                      const pages = [...document.querySelectorAll('.page')];
                      return {
                        hdOver: over(q('.hd')), barOver: over(q('.bar')),
                        pages: pages.length, items: document.querySelectorAll('.it').length,
                        tallPages: pages.filter(p => p.scrollHeight > p.clientHeight + 1 && p.querySelectorAll('.it').length > 1).length,
                        date: (q('#date') || {}).textContent || '',
                        fallback: !!q('.fbcard, .fbbar'),
                        sections: [...new Set(pages.map(p => (p.querySelector('h2') || {}).firstChild?.textContent || ''))]
                      };
                    }""")
                    shot = out / f"{tag}.png"
                    page.screenshot(path=str(shot)); shots.append(shot)
                    page.close()

                    issues = []
                    if errors: issues.append("スクリプトエラー: " + " / ".join(errors))
                    if st["hdOver"] > 0: issues.append(f"ヘッダーが {st['hdOver']}px はみ出し")
                    if st["barOver"] > 0: issues.append(f"フッターが {st['barOver']}px はみ出し")
                    if st["fallback"]: issues.append("記事を取れずフォールバック表示になった")
                    if not st["items"]: issues.append("記事が0件")
                    if st["tallPages"]: issues.append(f"縦にはみ出すページが {st['tallPages']} 枚")
                    if not st["date"]: issues.append("日付が出ていない")
                    report.append({"case": tag, **st, "issues": issues})
                    problems += [f"{tag}: {i}" for i in issues]
        browser.close()

    # 一覧画像
    try:
        from PIL import Image
        ims = [Image.open(s) for s in shots]
        cols = 4
        W = max(i.width for i in ims); H = max(i.height for i in ims)
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (W * cols, H * rows), "white")
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * W, (k // cols) * H))
        sheet.save(out / "sheet.png")
    except Exception as e:  # PIL が無くても個別画像は残る
        print("一覧画像は作れませんでした:", e)

    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in report:
        mark = "NG" if r["issues"] else "OK"
        print(f"[{mark}] {r['case']}: pages={r['pages']} items={r['items']} date={r['date']!r} sections={len(r['sections'])}")
        for i in r["issues"]:
            print("     -", i)
    print(f"\n画像: {out}/sheet.png（個別: {out}/<kind>-<幅>-<テーマ>.png）")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
