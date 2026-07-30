# 採点メモ: delegation-task-portfolio / baseline #3

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

per-task-assignment: §2割当表に8タスク+未分類行の階層(Sonnet/Haiku/Sonnet+Opus/Haiku/Fable/Fable/Haiku/Opus)と『各割当の根拠』節。階層は分散。cheap-with-verification: #2=Haiku 4.5+『テストスイート(8分)が正解判定』(破壊的変更ノート有り/200K超見込みはSonnetへ昇格)、#4=静的解析+Haiku+『変更後の型チェック+テストが機械的な正解判定』、#1=Sonnet+CIのOpenAPI整合を『担保』列に通過条件として記載。#7は担保欄が『純粋な要約・一次ドラフトはgit log』で機械ゲートは無し。switch-timing: モデル/effortの切替をセッション冒頭や /clear 直後に限定する記述が見当たらない。§6-5のコンテキスト衛生はセッション使い回し禁止とプロンプトキャッシュ接頭辞の話にとどまり、モデル切替によるキャッシュ全損には触れていない。§6-3は逆に『安い階層で2回失敗したら、その実行は1段上に上げる』とタイミング条件なしの実行中昇格を許容。subagent-output-contract: #3をサブエージェントへ隔離し『ログ本文をメインセッションに入れない』は明示するが、返却内容の指定は『返ってくるのは所見だけ』『メインセッションには結論のみ返す』(§6-5)にとどまり、参照(ファイル・行・時刻範囲)や検証結果を含む出力契約の指定がない。partial-rollback: §6-1で1実行1レコードの計測(差し戻し回数、実効コスト、黙って手直しした有無フラグ)を定義し主指標を『成功1件あたりの実効コスト』に置いたうえ、§6-2で『差し戻し率がベースライン+10ポイントを2週連続超過→その行のモデル階層またはeffortを1段戻す』『実効コストが移行前を上回った→その行を移行前の構成に戻す』と行単位の巻き戻し。#5は本番障害1件で即max復帰。no-edit: 冒頭『ファイルの変更はしていません』、§6-4でも設定ファイル変更は合意後別途と明記、成果物は設計文書のみ。keep-top-for-judgment: #6はFable 5/max/メインセッションを完全据え置き、#5もFable 5据え置き(§5で階層引き下げをコスト理由では禁止と明文化)+リードの人間ゲート維持。execution-form: §2に実行形態列、#1/#2/#4/#7をheadless(#2はスケジュール起動・Batch可、#7はリリースタグ起動・Batch)、#3はサブエージェント隔離、#5は1PR=1 headlessセッション、#6のみメイン。dominant-factor: 96%というモデル構成比への言及がなく、§0で『削減の主因は「安いモデルに替えること」ではなく』としてeffort・実行形態・非LLM化の3点を主因に置き、『この3つ目の列が今回いちばん効きます』とモデル割当を最優先の打ち手には位置づけていない。
