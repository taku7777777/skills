# モノレポ文書インベントリ

## 利用ツール・環境

- Claude Code、Codex、社内エージェントを併用。
- 開発者の半数はWindows、半数はmacOS/Linux。
- Windows環境ではGit symlinkが通常ファイルとしてcheckoutされる設定がある。

## 現在のファイル

- `CLAUDE.md`: buildは `npm test` と記載。実際は `pnpm test`。
- `AGENTS.md`: buildは `pnpm test`、DB migration禁止と記載。
- `docs/setup.md`: Node 18と記載。CIはNode 22。
- `packages/billing/CLAUDE.md`: billing固有のテストコマンドと決済ルール。
- `wiki/Glossary`: 「契約」の意味がコードと異なる。更新者不明。
- `.agent/memory.md`: エージェントが自動追記し、過去の仮説が事実として残っている。
- `docs/runbooks/release.md`: 半年前の旧パイプラインを参照。

## 観測された失敗

- エージェントがnpmを使いlockfileを変更する事故が月4回。
- billing以外の作業でもbilling固有文書が常時ロードされ、指示が衝突する。
- 文書リンク切れを検査するCIはない。
