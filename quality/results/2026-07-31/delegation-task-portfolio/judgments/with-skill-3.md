# 採点メモ: delegation-task-portfolio / with-skill #3

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

per-task-assignment: §2「モデル割当表」に8タスク全てが行として存在(#3は3-a/3-bに分解)。階層はHaiku級/Sonnet級/Fable 5据え置きに分散し、各行に根拠列あり。 cheap-with-verification: #2 Haiku級+テストスイートgreen+差分がlockfileのみ、#4 Haiku級+型チェックgreen+テストgreen、#7 Haiku級+コミット範囲の網羅チェック(件数一致)。§2の規律に「階層+検証手段で1単位」と明記。 switch-timing: §2「切替タイミング: モデル・effortの変更はセッション冒頭か `/clear` 直後に限定します(途中切替はキャッシュ全損)」。 subagent-output-contract: §3の#3行が「前処理(非LLM)→サブエージェント→本体」で、出力契約に「時系列サマリ+根拠のファイルパスと行番号+使った絞り込みコマンド+除外した範囲」を列挙し「本体(Sonnet級)は生ログを開かない」と明記。§4に二重払い検出指標もあり。 partial-rollback: §4差し戻し率(種別ごと・週次、閾値10%超が2週連続)→「該当種別のみ一段上へ。2週間後に再測定。他の割当は維持する」。規律に「1種別の悪化を全体の反証にしない」。 no-edit: 冒頭「本回答は設計のみです。リポジトリ・設定ファイルの変更は行っていません」。文書内に変更実施の記述なし。 keep-top-for-judgment: #6をFable 5・高〜最大effortで維持し「ここは高くてよい」、#5もFable据え置きでリードの最終判断を残す。 execution-form: §3に形態列(headless/週次headless/サブエージェント/メイン直/Batch API)。#2はheadless週次、#7はBatch APIでメインセッション外へ。 dominant-factor: §0(1)「最優先の打ち手はモデル割当」「モデル構成比がFable 5で96%。この状態では他のどんな節約も単価差に飲み込まれます」。
