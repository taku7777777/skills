# Skills

ソフトウェア開発の上流〜実装〜レビュー〜リリース・運用、AI時代のエージェント協働・発信・戦略までをカバーする Claude Code 用スキル集。
世界的に評価の高いエンジニア・書籍・標準(Eric Evans, Vaughn Vernon, Martin Fowler, Kent Beck, Google Engineering Practices, John Ousterhout, Michael Nygard, Adam Shostack, OWASP, Karl Wiegers, Gojko Adzic, Simon Willison, Anthropic Engineering ほか)の知見を体系化している。

## スキルマップ

```
┌─ 開発ライフサイクル ─────────────────────────────────────┐
│ 要件 ────────→ 設計 ──────────→ 実装 ─────→ レビュー      │
│ requirements-  arch-security-   ddd-design   impl-review  │
│ definition     design                                      │
│                └ api-data-design(境界の契約・スキーマ)     │
│                                                            │
│ 品質・進化: ai-adaptable-testing(戦略)                     │
│   → test-analysis(何を) → test-design(どう)              │
│   refactoring-strategy                                     │
│                                                            │
│ リリース・運用: cicd-release(パイプライン・デプロイ戦略)   │
│   → ops-observability(SLO・監視・インシデント対応)        │
│   systematic-debugging(バグ・障害の原因調査)              │
└────────────────────────────────────────────────────────┘
┌─ AI協働基盤 ──────────────────────────────────────────┐
│ harness-engineering(検証・ゲート設計)                     │
│ agent-security-governance(安全な実行環境・導入ガバナンス)   │
│ docs-for-ai(人間とAI双方のためのドキュメント)               │
│ skill-improvement(スキル自体の評価駆動の作成・測定・改善)   │
└────────────────────────────────────────────────────────┘
┌─ 発信・戦略 ──────────────────────────────────────────┐
│ tech-writing(登壇・記事) / quarterly-strategy-review      │
└────────────────────────────────────────────────────────┘
```

## スキル一覧

### 開発ライフサイクル

| スキル | 用途 | 主な知見の出典 |
|---|---|---|
| [`requirements-definition`](requirements-definition/SKILL.md) | 曖昧な依頼から要件を発見・整理・定義する | Wiegers, Impact Mapping, User Story Mapping, Specification by Example, EARS, IPA非機能要求グレード |
| [`arch-security-design`](arch-security-design/SKILL.md) | アーキテクチャ+セキュリティを含む設計(品質特性シナリオ、C4、脅威モデリング、ADR) | SEI, C4 Model, Release It!, STRIDE/Shostack, OWASP, Well-Architected |
| [`api-data-design`](api-data-design/SKILL.md) | API契約・DBスキーマの設計と進化(互換性判定、expand-contractマイグレーション) | Zalando API Guidelines, Google AIP, 『Refactoring Databases』, Parallel Change |
| [`ddd-design`](ddd-design/SKILL.md) | DDDの思考プロセスで設計・実装(戦略的設計→集約設計→実装) | Evans, Vernon, Wlaschin, EventStorming |
| [`impl-review`](impl-review/SKILL.md) | 実装を設計観点まで含めて多層レビュー(設計→正当性→セキュリティ→テスト) | Google Code Review Guide, Ousterhout, OWASP |
| [`ai-adaptable-testing`](ai-adaptable-testing/SKILL.md) | AI協働を前提としたテスト戦略(仕様のテスト化、安全網構築、AIが書いたテストの品質確保) | Beck(TDD), Feathers, Adzic, Google Testing Blog |
| [`test-analysis`](test-analysis/SKILL.md) | 「何をテストすべきか」の分析(テストベースレビュー、モデル化、リスクベース優先順位、オラクル決定) | ISTQB CTAL-TA v4.0, Bach & Bolton(RST/HTSM), Kaner(BBST) |
| [`test-design`](test-design/SKILL.md) | テスト条件からのテストケース設計(技法選択・適用、テストデータ、探索チャーター) | ISTQB CTAL-TA v4.0, Kaner『Domain Testing Workbook』, NIST(Kuhn), Hendrickson『Explore It!』 |
| [`refactoring-strategy`](refactoring-strategy/SKILL.md) | Tidy Firstの経済性判断による段階的リファクタ・移行・依存脱却 | Beck『Tidy First?』, Fowler(Strangler Fig), Feathers, Tornhill |
| [`cicd-release`](cicd-release/SKILL.md) | デプロイパイプライン設計・デプロイ戦略選択・フィーチャーフラグ・ロールバック設計 | Humble & Farley『Continuous Delivery』, 『Accelerate』/DORA, Hodgson(feature flags), trunk-based development |
| [`ops-observability`](ops-observability/SKILL.md) | SLO設計・計装・アラート・ランブック・インシデント対応・ポストモーテム | Google SRE Book/Workbook, 『Observability Engineering』, Release It!, OpenTelemetry, PagerDuty |
| [`systematic-debugging`](systematic-debugging/SKILL.md) | 仮説駆動のデバッグ・障害調査(再現の最小化、二分探索、仮説ログ、再発防止) | Agans『Debugging』, Zeller『Why Programs Fail』, git bisect, Gregg(USE) |

### AI協働基盤

| スキル | 用途 | 主な知見の出典 |
|---|---|---|
| [`harness-engineering`](harness-engineering/SKILL.md) | エージェント委任のための検証ハーネス・ゲート(HARD/SOFT/AUTO)・フィードバックループ設計 | Anthropic(effective harnesses), Böckeler, Spec Growth Engine, Parnas, fitness functions |
| [`agent-security-governance`](agent-security-governance/SKILL.md) | 二層防御(permission×sandbox)・egress制御・供給網審査・組織導入ガバナンス | Willison(lethal trifecta), Anthropic, Meta(Rule of Two), OWASP Agentic Top 10, MCP Security BP |
| [`docs-for-ai`](docs-for-ai/SKILL.md) | 人間とAI双方が使えるドキュメント体系(CLAUDE.md設計、用語集、陳腐化防止) | Diátaxis, Software Engineering at Google, Docs as Code, Parnas |
| [`skill-improvement`](skill-improvement/SKILL.md) | スキル自体を評価駆動で作成・測定・改善(evals.md 整備、発火診断、厳密改善時のみ採用の反復) | Anthropic(skill authoring best practices / skill-creator), スキル自動最適化研究, SWE-Skills-Bench |

### 発信・戦略

| スキル | 用途 | 主な知見の出典 |
|---|---|---|
| [`tech-writing`](tech-writing/SKILL.md) | 登壇スライド・技術記事の構成設計と執筆(一次情報による信頼蓄積) | Duarte『Resonate』, プレゼンテーションZen, Google Tech Writing, Willison |
| [`quarterly-strategy-review`](quarterly-strategy-review/SKILL.md) | 未来予測・キャリア戦略文書のウォッチリスト駆動レビュー(反証チェック、シナリオ確率更新) | Tetlock『超予測力』, Annie Duke, レッドチーム思考 |

各スキルは単体でも使えるが、成果物が次工程に引き継がれるよう設計している(要件定義の用語集 → DDDのユビキタス言語、受け入れ基準 → テスト仕様 → ハーネスの完了定義、品質特性の優先順位 → アーキテクチャ判断の基準)。

## 構成

各スキルは `SKILL.md`(本体: 原則+ワークフロー)+ `references/`(詳細チェックリスト・テンプレート、および適用実例 `worked-example.md`)+ `evals.md`(評価セット: 発火テスト・検証シナリオ・実行記録)で構成。常時コンテキストに載るのは frontmatter の name/description のみで、SKILL.md 本文は発火時に全文ロードされる。このため SKILL.md は簡潔に保ち、詳細は必要時に references を参照する段階構成(progressive disclosure)にしている。evals.md はスキル実行時に読まれるファイルではなく、スキル自体の効果を測定するための定義(運用方法は `skill-improvement` スキル)。worked-example は「入力 → 各ステップの判断 → 成果物フォーマット準拠の完成例」を架空の題材で示す。上流4スキル(要件→設計→DDD→レビュー)の実例は経費精算SaaSの多段階承認を共通題材とし、test-analysis → test-design の実例はクーポン適用機能で成果物を引き継ぐなど、パイプラインの連続性も再現している。

## 使い方

Claude Code から利用するには、スキルディレクトリを以下のいずれかに配置(またはシンボリックリンク):

- 全プロジェクト共通: `~/.claude/skills/<skill-name>/`
- 特定プロジェクト: `<project>/.claude/skills/<skill-name>/`

```bash
# 例: 全スキルを共通スキルとしてリンク
for s in */; do
  [ -f "$s/SKILL.md" ] && ln -sfn "$(pwd)/${s%/}" ~/.claude/skills/"${s%/}"
done
```

配置後、「DDDで設計して」「この実装をレビューして」「ハーネスを設計して」等の依頼で自動起動するほか、`/ddd-design` のように明示的に呼び出せる。
