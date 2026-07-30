# 採点メモ: delegation-task-portfolio / with-skill #1

合格基準: 9/9

- per-task-assignment: pass
- cheap-with-verification: pass
- switch-timing: pass
- subagent-output-contract: pass
- partial-rollback: pass
- no-edit: pass
- keep-top-for-judgment: pass
- execution-form: pass
- dominant-factor: pass

## 採点者の根拠

per-task-assignment: §2の割当表に8タスク全ての階層(Haiku/Sonnet/Fable の混在)と根拠列があり、#3/#4/#8は工程分割で複数階層を割当。cheap-with-verification: #2=Haiku+『テストgreen+lint+型green+差分がlockfileのみ』、#4=Haiku(決定論ツール優先)+『型green+テストgreen』、#7=Haiku+Batchで『対象コミット範囲の全PRがCHANGELOGに1行以上存在することをスクリプト検証』と、通過条件を機械判定に変換して添えている。switch-timing: §2『モデル・effortの切替はセッション冒頭か /clear 直後に限定する。セッション途中の切替はキャッシュが全損して次ターンが最も高くなる』と明記。subagent-output-contract: §3で#3を『決定論的前処理→サブエージェント(model: haiku)→本体Sonnet』に出し、出力契約として『事象要約/該当ログの抜粋(ファイル名+行番号+時刻範囲)/件数の時系列/使用したクエリ/未解決の疑問』を列挙し『本体は生ログを開かない』と明示。partial-rollback: §4に差し戻し率(種別ごと10%超が2週連続→『その種別だけ一段上へ。他の割当は維持』)、CI一発green率、リード重大指摘/PR、再依頼率の4指標。『1種別の悪化を全体の反証にしない』と部分巻き戻しを規律化。no-edit: 冒頭『ファイル変更は行っていない。以下は設計案のみ』、成果物は設計文書のみ。keep-top-for-judgment: #6はFable 5/effort高を一切変更せず、#5も料金計算・在庫引当に触るPRはFable 5温存+リード最終判断を全PRで維持。execution-form: §3に形態列(メイン直/headless/サブエージェント/Batch)があり#2はheadless週次、#7はBatch、#3/#8は外出し。dominant-factor: 要約冒頭『打ち手の順序はモデル割当が第一。構成比がFable 5で96%なので…桁で効く』と96%を主要因に特定。
