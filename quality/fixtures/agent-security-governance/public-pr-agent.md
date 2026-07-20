# 公開PR自動修正エージェント案

## ワークフロー

- 公開GitHubリポジトリで `pull_request_target` を契機に起動する。
- PR本文、レビューコメント、変更ファイルを読み、テストを実行して修正コミットをpushする。
- 必要に応じてWeb検索、npm install、GitHub API操作を行う。
- 夜間は人間の確認なしで動作する。

## 現在の設定案

```json
{
  "filesystem": {"read": ["/Users/*"], "write": ["workspace"]},
  "commands": ["*"],
  "network": ["*"],
  "hooks": ["./.claude/hooks/on-pr.sh"],
  "mcpServers": ["github-community/latest"]
}
```

- workflow jobへ長寿命のGitHub App private keyとnpm publish tokenを環境変数で渡す。
- `.env`、社内パッケージ設定、別リポジトリのcheckoutが同じrunnerに残る場合がある。
- hookとMCPサーバーは導入時だけ目視し、バージョン固定はしていない。
- 提案理由は「毎回permissionを聞くと無人実行できないため、全許可にする」。

## 期待する能力

- テスト修正、依存更新、PRへのコメント、同一PRブランチへのpush。
- production deploy、mainへの直接push、パッケージpublishは本来不要。
