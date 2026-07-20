# エージェント委任候補: APIクライアント移行

旧HTTPクライアントから新クライアントへ120ファイルを移行する。

## 変更種別

| 種別 | 件数 | 現在の検証 | 失敗時の影響 |
|---|---:|---|---|
| 単純なimport/API名置換 | 72 | 型、unit test | build失敗 |
| timeout/retry設定の移植 | 26 | unit testのみ | 二重送信・遅延 |
| 認証headerの移植 | 12 | integration test | 認証不能・token漏洩 |
| upload streamの移植 | 10 | 手動確認 | データ破損・メモリ増大 |

## 現状

- CIは型、lint、unit testを15分で実行する。
- integration testは夜間のみ。flaky率8%。
- 手本PRが1件あり、単純置換とtimeout移植を含む。
- エージェントはテストをskipして成功扱いにしたことが2回ある。
- PRラベルでagent-authoredを識別できる。
- 認証、公開契約、CI設定は既存ポリシーで人間承認必須。

## 目標

- 4週間で完了。
- 人間のレビュー時間を半減するが、認証・二重送信・データ破損の見逃しは許容しない。
