# 採点メモ: delegation-task-portfolio / with-skill #2

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

per-task-assignment: §2モデル割当表に8タスク全て、階層はHaiku級/Sonnet級/Fable維持に分散、各行に根拠列。#1・#8には試行枠(条件付き引き下げ)も付記。 cheap-with-verification: #2 Haiku級+CI green(テスト8分+lint+型)+差分がlockfileと依存宣言のみ、#4 Haiku級+型green+テストgreen+差分が機械的置換のみ、#7 Haiku級+対象コミットSHAの全言及検査(未言及0件が通過条件)。§2冒頭に「階層と検証手段のペアで1つの割当」と明記。 switch-timing: §2「切替はセッション冒頭または `/clear` 直後に限定。セッション途中のモデル・effort切替はプロンプトキャッシュを全損します」+「タスクを切り替えるときは /clear して階層を設定する」を運用ルール化。 subagent-output-contract: §3の#3行がカスタムサブエージェント(model: haiku明示)+Bash事前絞り込みで、出力契約に「症状/該当時刻レンジ/エラー分類と件数/根拠となるログの引用(タイムスタンプ+行番号)/該当コードのファイルパス:行番号/仮説と次に確認すべきこと」を列挙し「本体はログを開き直さない」と明記。さらに二重払い予防節で週1件の抜き取り点検を規定。 partial-rollback: §4に差し戻し率(10%超が2週連続→該当種別のみ一段上へ、2週間後に再測定)、#5専用の見逃し率(ベースライン+5pt→Fableへ戻す/高リスク定義拡大の部分巻き戻しを先に試す)。規律「悪化1種別を全体の反証にしない」。 no-edit: 冒頭「ファイル変更は行っていません。以下は設計案です」。 keep-top-for-judgment: #6はFable 5維持(effort高/thinking on)、#5でも料金計算・在庫引当・認証・課金に触るPRはFable維持、リードの最終判断を人間ゲートとして据え置く旨を§2の判断根拠で明示。 execution-form: §3に形態列(メイン直/headless週次/カスタムサブエージェント/headlessリリース時)。#2は週次headless、#7はheadless(リリース時スクリプト)でメインセッション外へ。採用しなかった形態(Batch/agent teams/外部委譲)の理由も記録。 dominant-factor: 冒頭「打ち手の順序はモデル割当が第一。添付資料のモデル構成比はFable 5が96%。…この構成比が支配的な間はコンテキスト整理や依頼文の改善では桁が動きません」。
