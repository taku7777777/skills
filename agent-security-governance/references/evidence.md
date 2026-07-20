# エージェントセキュリティの時点依存エビデンス

## 引用規律

- 安定した設計原則と、時点依存の件数・割合・製品挙動を分ける。
- 数字には調査日、対象集合、分母、「悪意」「脆弱性」「検出」の定義を付ける。
- ブログやベンダー調査の数字は脅威の存在証明には使えても、対象組織の発生率として転用しない。
- 重要な導入判断では公開情報を起点に、対象バージョンの公式文書・CVE・実環境の境界テストを再確認する。

## 公式・一次情報

- [Anthropic: How we contain Claude across products](https://www.anthropic.com/engineering/how-we-contain-claude) — 2026-07-20参照。Claude Codeの権限プロンプトが約93%承認されたというAnthropic内テレメトリ、sandbox/egress/credential境界の設計。値はClaude Code利用者という母集団に限定する。
- [Anthropic: How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) — 2026-07-20参照。承認疲労、任意コード実行を許す広すぎるルールの除外、分類器の限界。
- [Anthropic: Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) — 2026-07-20参照。filesystem/network isolationとプロキシによるcredential注入。
- [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) — 2026-07-20参照。版は2026。永続コンテキスト汚染、過剰な自律性等の分類は改訂時に再照合する。

## 市場・インシデント統計の扱い

ClawHub、skills.sh、MCP市場などの監査件数はスナップショットであり、重複キャンペーン、調査対象、検出手法によって比率が大きく変わる。成果物で利用する場合は、元レポートのURL・公開日・対象件数・判定定義をその場で再取得する。再取得できない数字は削除し、「第三者拡張が供給網攻撃面になる」という定性的根拠だけを使う。

## 更新規律

- 四半期ごと、およびClaude Code/MCP/サンドボックスの主要更新時に確認する。
- `quality/sources.json` の `review_due` を越えた出典は、再確認するまで最新値として引用しない。
