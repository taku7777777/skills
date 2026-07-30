# 採点メモ: delegation-task-portfolio / baseline #2

合格基準: 6/9

- per-task-assignment: pass
- cheap-with-verification: pass
- switch-timing: FAIL
- subagent-output-contract: FAIL
- partial-rollback: pass
- no-edit: pass
- keep-top-for-judgment: pass
- execution-form: pass
- dominant-factor: FAIL

## 採点者の根拠

per-task-assignment: §4割当表(マスター)に8タスク全て。Sonnet 5/Opus 5/Fable 5/レーン分割に分散し、§5.1〜5.8に個別根拠あり。 cheap-with-verification: #2 Sonnet 5 low+テストスイート(8分)、#4 Sonnet 5 low+型チェッカ+テスト、#1 Sonnet+CI(OpenAPI整合)。§3の軸1で「検証者が機械なら階層を下げる」と対応付け、全行に検証者列。#7の検証者は人間の目視のみだが、criterionの列挙は例示であり全割当に検証者が対で置かれているためtrue。 switch-timing: 不成立。/clear・セッション冒頭・途中切替の限定に触れる記述が本文に存在しない(該当語のgrepで確認)。キャッシュ関連の言及は§5.5の前置バイト安定性とcache_read_input_tokens確認、§9-7のみで、切替タイミングの規律ではない。取り決め1はレーン定義側にモデルを固定して/modelを不要にする方針で、切替時点の限定は述べていない。 subagent-output-contract: 不成立。§5.3で#3を前段フィルタ→サブエージェント→メインに出し「要約だけを親セッションに返す」「サブエージェントを使う理由は文脈隔離」とは書くが、結論・該当ファイル/行の参照・検証結果といった出力契約の要素指定がない。§4マスター表にも出力契約の列がなく、本体が読み直さずに済む形の具体指定に至っていない。 partial-rollback: 取り決め2で手戻り率(見落とし追加件数・ノイズ削除件数・差し戻し件数)のベースライン計測を前提化し、取り決め8「手戻り率がベースラインを超えたレーンは即座に1段上げる」でレーン単位の一段引き上げを明示。取り決め9に縮退順序も。 no-edit: 出力は割当設計文書のみで、ファイル変更を行った記述はない(明示的な不変更宣言はないが、変更の痕跡・記載もない)。 keep-top-for-judgment: #6はFable 5据え置き・最適化対象外(§5.6、取り決め6の保護レーン)、#5 Lane 3(料金計算・在庫引当・スキーマ移行・認証)はFable 5でメインセッション、リード最終判断を維持。 execution-form: §4に実行形態列(headless/サブエージェント/メインセッション)。#2はheadless並列で月曜朝の定期実行、#7はheadless(タグ作成時起動)とメインセッション外へ。 dominant-factor: 不成立。§1で「$2,400は『モデル選択のミス』ではなく『選択が手動操作を要求していたこと』の帰結」と明示的に別要因へ帰属し、付録でも「最大の原因|階層選択ではなく、選択が手動操作を要求していたこと」。削減の主軸の第1はeffort=max解除で「最も安く、最も即効性がある」、階層固定は3番目。§2.3は「単一の階層選択よりも(セッション共有の)寄与が大きい可能性がある」とする。96%は§2.1の事実表に記載されるが、モデル割当を最優先の打ち手には位置づけていない。
