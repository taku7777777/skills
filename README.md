# Skills

ソフトウェア開発の上流〜実装〜レビュー〜リリース・運用、AI時代のエージェント協働・AI利用の経済性(コスト計測と運用)・発信・戦略までをカバーする Claude Code 用スキル集。
世界的に評価の高いエンジニア・書籍・標準(Eric Evans, Vaughn Vernon, Martin Fowler, Kent Beck, Google Engineering Practices, John Ousterhout, Michael Nygard, Adam Shostack, OWASP, Karl Wiegers, Gojko Adzic, Simon Willison, Anthropic Engineering ほか)の知見に加え、Anthropic公式ドキュメントと利用コストの一次実測(metsuke)を体系化している。

> **metsuke について** — 上記の列挙で唯一の一次実測であり、著者自身の Claude Code 全ログの計測([taku7777777/metsuke](https://github.com/taku7777777/metsuke))を指す。**単一利用者・特定期間の観測であり、無作為化比較でも査読済み研究でもない。**桁感覚とレンジの根拠として使っており、他環境への予測値ではない。他の列挙(Evans / Fowler / OWASP 等)と同格の権威として読まないこと。

## スキルマップ

```
┌─ 開発ライフサイクル ───────────────────────────────────────┐
│ 要件 ────────→ 設計 ──────────→ 実装 ─────→ レビュー       │
│ requirements-  arch-security-   ddd-design   impl-review   │
│ definition     design                                      │
│                └ api-data-design(境界の契約・スキーマ)     │
│                                                            │
│ 品質・進化: ai-adaptable-testing(戦略)                     │
│   → test-analysis(何を) → test-design(どう)                │
│   refactoring-strategy                                     │
│                                                            │
│ リリース・運用: cicd-release(パイプライン・デプロイ戦略)   │
│   → ops-observability(SLO・監視・インシデント対応)         │
│   systematic-debugging(バグ・障害の原因調査)               │
└────────────────────────────────────────────────────────────┘
┌─ AI協働基盤 ───────────────────────────────────────────────┐
│ harness-engineering(検証・ゲート設計)                      │
│ agent-security-governance(安全な実行環境・導入ガバナンス)  │
│ docs-for-ai(人間とAI双方のためのドキュメント)              │
│ skill-improvement(スキル自体の評価駆動の作成・測定・改善)  │
└────────────────────────────────────────────────────────────┘
┌─ AI協働の経済性 ───────────────────────────────────────────┐
│ 計測: llm-cost-observability(利用費の計測・帰属・介入設計) │
│   → 行動: context-economy(セッション・キャッシュ運用)      │
│           delegation-economy(モデル選択・委任・並列化)     │
│           prompt-economy(1回で通す依頼設計・早期打ち切り)  │
│   → 再計測してループを閉じる                               │
└────────────────────────────────────────────────────────────┘
┌─ 発信・戦略 ───────────────────────────────────────────────┐
│ tech-writing(登壇・記事) / quarterly-strategy-review       │
└────────────────────────────────────────────────────────────┘
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

### AI協働の経済性

| スキル | 用途 | 主な知見の出典 |
|---|---|---|
| [`llm-cost-observability`](llm-cost-observability/SKILL.md) | LLM利用コストの計測・帰属・予算運用と、行動変容につながる介入設計(計測→行動ループの起点。計測基盤ゼロでもローカルのセッショントランスクリプトから当日中に着手できる) | Anthropic(costs / monitoring-usage / pricing), metsuke実測 |
| [`context-economy`](context-economy/SKILL.md) | セッション・コンテキスト・プロンプトキャッシュの経済運用(離席・再開、/clear・/compact・/rewind、起動固定費) | Anthropic(prompt caching / costs / context windows), metsuke実測 |
| [`delegation-economy`](delegation-economy/SKILL.md) | タスク種別ごとのモデル階層・委任形態・並列化のコスト効率設計(counter-metricsつき委任マトリクス) | Anthropic(pricing / sub-agents / costs), metsuke実測 |
| [`prompt-economy`](prompt-economy/SKILL.md) | 1回で通る依頼設計(受け入れ条件・検証手段の同梱)と迷走の早期打ち切り | Anthropic(best practices / costs), metsuke実測 |

この4スキルの数値根拠は Anthropic公式ドキュメント(単価・キャッシュ・サブエージェント等の仕様)と metsuke実測(n=1 の観測。上記の注を参照)の2層で、閾値・比率はいずれも自環境で測り直す前提で書いている。**契約形態と枠の層(定額サブスク / API従量 / クラウドプロバイダ経由の選択、週次・5時間枠の上限到達時の退避)は現在どのスキルもカバーしていない** — 下記「品質保証」末尾の未充足領域を参照。

### 発信・戦略

| スキル | 用途 | 主な知見の出典 |
|---|---|---|
| [`tech-writing`](tech-writing/SKILL.md) | 登壇スライド・技術記事の構成設計と執筆(一次情報による信頼蓄積) | Duarte『Resonate』, プレゼンテーションZen, Google Tech Writing, Willison |
| [`quarterly-strategy-review`](quarterly-strategy-review/SKILL.md) | 未来予測・キャリア戦略文書のウォッチリスト駆動レビュー(反証チェック、シナリオ確率更新) | Tetlock『超予測力』, Annie Duke, レッドチーム思考 |

各スキルは単体でも使えるが、成果物が次工程に引き継がれるよう設計している(要件定義の用語集 → DDDのユビキタス言語、受け入れ基準 → テスト仕様 → ハーネスの完了定義、品質特性の優先順位 → アーキテクチャ判断の基準)。

## 使い方

### クイックスタート

前提は Claude Code(スキル機能に対応したバージョン。開発・検証は v2.1.215〜2.1.220 / macOS で行っている)と、検証スクリプトを回す場合のみ python3(CIは 3.12 で回している。標準ライブラリのみを使うが、3.12未満での動作は確認していない)。

リポジトリを clone し、そのルートで:

```bash
mkdir -p ~/.claude/skills
for s in */; do
  name="${s%/}"
  [ -f "$s/SKILL.md" ] || continue
  target="$HOME/.claude/skills/$name"
  # 実ディレクトリが既にある場合、ln -sfn はその内部にリンクを作ってしまうので飛ばす
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "skip: $target は実ディレクトリです" >&2
    continue
  fi
  ln -sfn "$(pwd)/$name" "$target"
done
```

成功判定: `ls -l ~/.claude/skills | grep -c '\->'` が 22 になる。Claude Code 側では `/context` を開くとロード済みスキルが一覧できる。特定プロジェクトだけで使う場合はリンク先を `<project>/.claude/skills/<skill-name>/` にする。

配置後は「DDDで設計して」「この実装をレビューして」「ハーネスを設計して」等の依頼で自動起動するほか、`/ddd-design` のように明示的に呼び出せる。

### 最小セットから始める

22件すべてを入れる必要はない。動機別の出発点:

| 動機 | まず入れる2件 | 次の1件 |
|---|---|---|
| レビュー品質を上げたい | `impl-review` + `systematic-debugging` | `test-analysis` |
| コストを下げたい | `llm-cost-observability` + `context-economy` | `delegation-economy` |
| エージェントに安全に任せたい | `harness-engineering` + `agent-security-governance` | `docs-for-ai` |
| 上流の設計から固めたい | `requirements-definition` + `arch-security-design` | `ddd-design` |

### まず読むファイル

中身を確かめるだけなら、このREADMEのスキルマップ → 対象スキルの `SKILL.md` → そのスキルの `references/worked-example.md` の3ファイルで、原則・ワークフロー・成果物の形が一通り分かる。1つだけ選ぶなら [`impl-review/references/worked-example.md`](impl-review/references/worked-example.md)。

### 制約

- **description はすべて日本語である。** Claude Code のスキル選択は description のマッチングに依存するため、英語プロンプトでは発火が弱まる。英語で使うなら各 `SKILL.md` の frontmatter を訳すか、`/skill-name` で明示的に呼ぶ。
- 常時コンテキストに載るのは22件の name/description(description 合計4,772文字)のみで、SKILL.md 本文は発火時にロードされる。全件入れても常駐コストはこの範囲に収まる。

## 構成

各スキルは `SKILL.md`(本体: 原則+ワークフロー)+ `references/`(詳細チェックリスト・テンプレート、および適用実例 `worked-example.md`)+ `evals.md`(評価セット: 発火テスト・検証シナリオ・実行記録)で構成。常時コンテキストに載るのは frontmatter の name/description のみで、SKILL.md 本文は発火時に全文ロードされる。このため SKILL.md は簡潔に保ち、詳細は必要時に references を参照する段階構成(progressive disclosure)にしている。evals.md は通常の発火時に自動ロードされないが、同じファイルシステムにあれば探索可能なのでhidden rubricとしては扱わない。実行用fixtureと採点rubricは `quality/` で分離し、評価時にはexecutorへtask packetだけを渡す。worked-example は「入力 → 各ステップの判断 → 成果物フォーマット準拠の完成例」を架空の題材で示す。上流4スキル(要件→設計→DDD→レビュー)の実例は経費精算SaaSの多段階承認を共通題材とし、test-analysis → test-design の実例はクーポン適用機能で成果物を引き継ぐなど、パイプラインの連続性も再現している。

## 品質保証

静的検証、全体ルーティング評価、baseline/with-skill比較をリポジトリ標準の品質ゲートとする。

```bash
# frontmatter、リンク、eval定義、reference構造、fixture、出典manifest
python3 scripts/validate_skills.py

# 47件の単一・複合・非発火ルーティングケースを検証
python3 scripts/eval_routing.py --validate-only

# 全22スキルのraw fixtureとhidden rubricを検証
python3 scripts/eval_tasks.py validate

# /tmp配下にexecutor用とgrader用の分離パケットを生成
python3 scripts/eval_tasks.py prepare
```

`prepare` が出力する `run-packets/` の個別 `task.md` だけを実行エージェントへ渡す。`grader-packets/`、`manifest.json`、この開発リポジトリ、過去出力は見せない。baselineとwith-skillを同一モデル・tool policyで各3回以上実行し、`score-template` が出力するJSONLへblind採点結果・token・latency・cost・tool errorを記入して `score` で比較する。ここでの blind は「採点者に条件を伏せる」までを指す。採点モデルは実行モデルと別系統にするのが望ましく(同一だと自己採点になる)、`run.json` には `executor_model` / `grader_model` / `isolation.grader` を必ず残して、達成できた盲検化の水準を後から検証できるようにする。providerが実額を公開しない場合、`cost_usd` は推測値や0ではなく `null` とする。全ケースが完了し、平均品質が厳密に改善し、critical失敗とtool errorが悪化しない場合だけ `adoption_ready=true` になる。

```bash
python3 scripts/eval_tasks.py score-template --manifest <packet-dir>/manifest.json
python3 scripts/eval_tasks.py score --manifest <packet-dir>/manifest.json --scores <scores.jsonl>
```

通常CIでは外部モデルを呼ばず、評価資産の構造と漏洩防止境界を検証する。リリース可否を判定するときは `python3 scripts/validate_skills.py --strict` を使い、全スキルの実行記録が揃っていない状態を失敗にする。現在の `--strict` は22スキル全件がERRORになる(どのevals.mdにも未実施の評価行が残るため)ので、進捗は `validate_skills.py` が最後に出す `coverage:` 行(未実施ゼロのスキル数 / 完了task case数)で読む。2026-07-31時点の値は **未実施ゼロのスキル 0/22・完了task case 3件**。

### 完了した3ケースの採点プロトコル

| ケース | 実施日 | executor model | grader model | 採点の盲検化 | decision |
|---|---|---|---|---|---|
| `impl-review-coupon-pr` | 2026-07-20 | gpt-5.6-sol(Codex CLI 0.144.6) | **未記録** | 条件エイリアスを全判定完了まで秘匿 | adopt |
| `context-economy-usage-week` | 2026-07-31 | claude-opus-5 | claude-opus-5 | 匿名タグ(A〜F)で条件を秘匿。**実行者と同一モデルによる自己採点** | adopt |
| `delegation-task-portfolio` | 2026-07-31 | claude-opus-5 | claude-opus-5 | 同上 | adopt |

2026-07-31の2件は grader と executor がどちらも claude-opus-5 であり、条件は伏せたものの**同一モデルが自分の系統の出力を採点している**。同系の出力を読みやすい・妥当だと評価する方向のモデル固有バイアスは除去できておらず、これが pass rate delta の解釈の上限になる。加えて with-skill 出力はスキル指定の成果物フォーマットに従うため、書式から条件が推測されうる残存リスクがある。2026-07-20の1件は grader モデル自体が記録されていない。tokenの定義も世代間で異なり(2026-07-20 = executorの入出力トークン、2026-07-31 = セッション全体のusage合計でキャッシュ読取を含む)、桁が3つ違う値を横並びで比較してはならない。各ケースの詳細な限界は `quality/results/<date>/<case>/run.json` の `limitations` にある。

### 結果と、その読み方の限界

2026-07-31時点でbaseline/with-skill比較を完了したのは全22 task casesのうち3件だけである。実行日もモデルも採点プロトコルも異なるため、この3件をひとつの比較系列としては読めない。2026-07-31の2件はいずれも decision が `adopt`(pass rate delta それぞれ +0.222 / +0.259)になったが、以下の留保がすべて付く。

- **評価対象は出荷版ではない。** 対象はサイクル2改善**前**のスナップショット(`quality/results/2026-07-31/<case>/skill-snapshot/`)。乖離の規模はケースで大きく違い、`context-economy` は SKILL.md が 95行→113行(+31/−13。現行本文の約27%が評価後の追記)・`references/evidence.md` が 64行→86行(+23/−1)で、本文の相当部分が adopt 判定の対象外である。`delegation-economy` は SKILL.md 97行→102行(+9/−4)と軽微。
- **採点rubricも当時の版である。** 掲載している件数・deltaはすべて `quality/results/<date>/<case>/rubric.json`(改訂**前**)に対する値で、現行の `quality/graders/` では再現しない。`delegation-task-portfolio` は採点後に `green-provenance` が追加され9→10基準になっており(`validate_skills.py` がこのドリフトをWARNで検出する)、`context-economy-usage-week` は基準数は同じだが `ttl-lane` ほか6基準の文言を改訂した。**再採点は実施していない** — 結論を知ったうえでの非盲検の再採点は記録の価値を下げるため、数値を書き換えず限界を開示する方針を採った。
- **`context-economy-usage-week` はwith-skill条件でもcritical失敗が3件残る。** ただしレビューはこの3件のうち2件を「1時間TTLの採用を要求していた改訂前 `ttl-lane` の欠陥を測ったもの」と判定している(損益分岐上、このfixtureでは1時間TTLは損であり、正しく却下した回答がfailしていた)。改訂後の文言では判定が変わりうるが、上記のとおり再採点していない。`adopt` は依然として「平均品質が厳密に改善し、critical失敗とtool errorが悪化しない」の意味でしかない。
- **見かけの測定幅より実効的な測定幅は狭い。** 両ケースとも複数の基準が両条件6/6 passで判別力を持たず(context-economy は9基準中4件、delegation は9基準中6件)、delta を作っているのは前者で5基準・後者で3基準である。基準別のpass行列とガードレール基準を分けた集計は各 `summary.json` の `criterion_pass_matrix` / `discriminator_pass_rate` にある。

同日に着手した `prompt-economy-failed-session` と `llm-cost-team-usage` はセッション上限で中断したため、部分結果を集計に含めていない。この2件を含む残り19 casesは比較未成立であり、リポジトリ全体の `adoption_ready` はfalseのままである。2ケースでの改善をスキル群全体の有効性の証拠とはみなさず、静的検証の合格や同一シナリオでの改善後回帰も、未評価シナリオへの効果の証明とはみなさない。

実行結果は `quality/results/` に保存する。モデルのraw responseと評価時点のskill snapshotは再現証跡として改変せず保持するため、隔離実行に使った一時workspaceへのリンクを含むことがある。これらの生成済みMarkdownは通常ドキュメントのリンク検査対象から除外し、集計値は対応するJSON/JSONLと `evals.md` から参照する。

時点依存の統計・標準・製品挙動は `quality/sources.json` で一次URL、公開日、アクセス日、見直し期限、適用範囲を管理する。安定原則はSKILL.md、変動する数値は各スキルの `references/evidence.md` に置く。

### 未充足領域(既知のギャップ)

- **契約・枠の層**。「コストを抑えつつコーディングエージェントを使いこなす」という目的に対し、経済性4スキルは使い方の最適化(計測 / セッション / 委任 / 依頼)を扱うが、**どの契約・どの枠で回すか**は扱っていない — 定額サブスク vs API従量 vs Bedrock/Vertex等の損益分岐、週次・5時間枠の消費モニタと上限到達前の退避設計、上限に当たったときのフォールバック、複数チャネル併用時の按分と請求突合。`llm-cost-observability` は組織内部の帰属と配分、`delegation-economy` はモデル階層と実行形態の割当であり、いずれも購買・契約の層には踏み込まない。実際に上限へ当たった利用者がこのリポジトリから得られる答えは現状ゼロである。将来 `plan-quota-economy` として切り出す候補だが未着手(非LLM手段へのオフロード判断は独立スキルにせず、`delegation-economy` の委任マトリクス最下層として扱うのが正しい — 単独スキル化すると発火が競合する)。
- **自動発火の実測**。`quality/routing/cases.jsonl` の47ケースは構造検証(`--validate-only`)までで、実モデルでの発火確認は未実施。サイクル3で `context-economy` / `docs-for-ai` / `ai-adaptable-testing` の description に境界句を追加したが、その回帰は実モデルで確認していない。
- **評価設計そのものの検査**。`validate_skills.py` は評価資産の構造(F/N行数・シナリオ数・rubricの形・rubricドリフト)しか見ない。基準がスキル本文の言い換えでないか、fixtureが答えを先出ししていないか、基準に判別力があるかは自動検査していないため、未実施19ケースについては `--strict` の合格が評価設計の妥当性を保証しない。

