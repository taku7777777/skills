# 採点メモ: delegation-task-portfolio / baseline #1

合格基準: 8/9

- per-task-assignment: pass
- cheap-with-verification: pass
- switch-timing: pass
- subagent-output-contract: FAIL
- partial-rollback: pass
- no-edit: pass
- keep-top-for-judgment: pass
- execution-form: pass
- dominant-factor: pass

## 採点者の根拠

per-task-assignment: §3割当表に8タスクの階層(Sonnet/Haiku/Sonnet/Sonnet/Opus/Fable/Haiku/Opus)、§4に各タスクの根拠。階層は分散。cheap-with-verification: #2=Haiku 4.5/low+『8分のテストスイートが完全な合否判定』(落ちたらSonnetへ昇格)、#4=Sonnet 5/low+『型チェックが漏れを機械的に検出』、#1=Sonnet+CIのOpenAPI整合。§3表に検証列(強/弱/なし)を持ち、§7.3のロールバックもCI初回通過率に紐づく。なお#7 CHANGELOGの検証欄は『強(人間の目視は軽い)』で機械ゲートは置いていない。switch-timing: §6.3『セッション途中で /model を使わない』『モデルは各セッション/実行の開始時に決める。途中で変えない』『effortも同様にセッション/実行単位で固定』、理由としてモデル単位のキャッシュ無効化を明記(/clear への言及はないが冒頭限定は明示)。subagent-output-contract: #3をサブエージェントへ出す点は満たすが、出力契約は『異常パターンの列挙だけさせる』『要約だけが親に返ります』にとどまり、本体が再読せず進むための参照情報(ファイル・行・時刻範囲等)や検証結果の指定がない。全文および grep で他節にも#3の返却フィールド定義は無し。partial-rollback: §6.1に差し戻し率/CI初回通過率/リード指摘の見逃し/人間所要時間を定義し、ベースライン2週取得のうえ『差し戻し率がベースラインの1.5倍を超えたタスク種別は、階層を1段戻す』と種別単位の巻き戻し。#5は撤退先(Opus 5/high→Fable 5/high)を段階指定。no-edit: §6.2『本回答ではファイルは作成していません…実際の設定ファイル追加は別途』、成果物は設計文書のみ。keep-top-for-judgment: #6はFable 5/high〜xhigh据え置き、#5は一次Opus 5+リードが要精査としたPRのみFable 5/high等の二次パス、最終判断はリード維持。execution-form: §3に実行形態列、#1/#2(月曜cron・3リポ並列)/#4/#7(リリースCI)/#8をheadless、#3/#5をサブエージェント。dominant-factor: §1.1要因Aで最上位モデル一律を筆頭要因に置き、§1.2でFable 96%(約$2,304)から必要移行割合 f≈0.74 を逆算、『Fable 5支出の7割前後をSonnet階層以下に移す必要がある。低頻度タスクの整理では到達不可能』と結論。
