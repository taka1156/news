---
name: release
description: Weekly Reader の変更を出すときの手順。check-ui で確認し、設定パネルのバージョン表記を上げ、決まった形式でコミットして master に push する。ユーザーに「push して」と言われたとき、または変更が終わったときに使う。
---

# release

## 手順

1. **確認。** `public/index.html` を変えたなら check-ui を実行し、`[NG]` がないこと。
2. **バージョンを上げる。**（`public/index.html` を変えたときだけ）
   ```sh
   python3 .claude/skills/release/scripts/bump_version.py
   ```
   出力された `YYYY-MM-DD.N` を控える。ユーザーはデプロイ後、設定パネルのこの表記で反映を確認する。
3. **コミット。** 1行目は英語で何を変えたか、空行のあと箇条書きで要点。末尾にはその会話の指示にある署名行（`Co-Authored-By:` など）を付ける。
   ```sh
   git add -A
   git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -m "…"
   ```
4. **push。** 既定ブランチは `master`。
   ```sh
   git -c push.negotiate=true push origin HEAD:master
   ```
   - 拒否されたら、先に `git fetch --depth=50 origin master` してから載せ直す。ユーザーが GitHub 上で直接変えていることがある。
5. **報告。** 短く、結論から：
   - 何を変えたか（箇条書き）
   - コミットの短いID
   - 「設定パネルが『バージョン YYYY-MM-DD.N』になっていれば反映されています」
   - `worker.js` を変えたなら「Worker の再デプロイ（`npx wrangler deploy`、GitHub 連携なら push で自動）が必要」
   - 確認は仮のページで行ったことを明記する
