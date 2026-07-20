# 顧客名フィールド変更

## 現行

```json
GET /v1/customers/c-123
{"id":"c-123","full_name":"Ada Lovelace","updated_at":"2026-07-01T00:00:00Z"}
```

DB: `customers(id uuid primary key, full_name text not null, updated_at timestamptz not null)`

利用者はWeb、iOS、外部パートナー3社。外部パートナーの更新頻度は四半期ごと。旧アプリのインスタンスはローリングデプロイ中に最大30分残る。

## 提案されている一括変更

1. DBの `full_name` を `first_name` と `last_name` にrenameする。
2. APIレスポンスから `full_name` を削除し、2フィールドを返す。
3. 同じリリースで全行を空白分割してbackfillする。
4. 問題があればアプリだけ前バージョンへrollbackする。

## 制約・例外

- 日本語名、単名、複合姓があり、機械分割できないレコードが18%。
- 顧客名は本人が後から修正できる。
- APIには `If-Match` による楽観ロックが既にある。
- 移行中も書き込みを止められない。
- 外部パートナーの移行完了をAPI利用ログで確認できる。
