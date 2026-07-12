# api-data-design 適用例

## 題材

架空のレッスンスタジオ予約サービス。これまで自社Webアプリ(モノリス)内の機能だった予約を、外部の予約ポータル(パートナー2社)へAPIとして公開する。あわせて、現行DBではレッスンテーブルの `attendees` 列(JSON配列)に参加者を埋め込んでおり、予約単位の操作ができないため、独立した `reservations` テーブルへ移行したい。

## 入力

- 依頼: 「パートナーが空き枠を検索して予約を作れるAPIが欲しい。キャンセルもAPIで」
- 既存資産: モノリス(Rails相当)+ RDB。`lessons` テーブルに `attendees JSON` 列
- 非機能: パートナー経由の予約は全体の3割になる見込み。空き枠検索はピーク時 50 req/s

## 各ステップでの判断

**ステップ1(利用者とユースケース)**: 利用者は ①パートナーポータル(partner公開: 空き枠検索・予約作成・キャンセル)②自社Webアプリ(private)③夜間バッチ(集計、DBを直接読んでいる)。パートナーが使うのは4操作のみで、講師管理・料金改定は契約に入れない。バッチのDB直読みはデータ所有権違反として設計書のリスク欄に記録し、集計API提供を別課題化。

**ステップ2(スタイル選択)**: 利用者が外部でCRUD中心のためREST。予約確定の通知は「ポータル側が顧客へメールを送る」ユースケースのみ → 状態を運ばずIDのみの通知イベント(webhook)とし、詳細はAPIで再取得させる(通知イベント型)。リソースは用語集から `lessons`(レッスン枠)と `reservations`(予約)。「予約する」は `POST /reservations`、キャンセルは削除ではなく状態遷移なのでカスタムメソッド `POST /reservations/{id}:cancel`。

**ステップ3(契約の詳細設計)**: 空き枠検索はカーソルページング(既定20件・上限100件)。エラーは RFC 9457 で統一し、`type` カタログに「定員超過」「キャンセル期限超過」を業務エラーとして登録。予約作成はパートナーのリトライで二重予約が起きるため `Idempotency-Key` 必須(TTL 24時間、同一キー別ペイロードは422)。認可はパートナー単位のリソース認可 — 他社が作成した予約は404(403だと存在が漏れる)。

**ステップ4(データモデリング)**: `reservations` を独立テーブル化。「同一レッスンに同一顧客は1予約」を一意制約で、定員チェックはアプリ+トランザクションで担保(理由: 集約の不変条件。`ddd-design` の成果物と整合)。キャンセルは論理削除ではなく `status` の状態としてモデル化(チェックリスト§2.4の判断)。外部公開IDはULID(連番の露出回避)。

**ステップ5(互換性方針)**: partner公開のためバージョンはURLに置かず追加のみで進化、破壊的変更時のみ移行計画とセットで実施と契約書に明記。webhookペイロードに `schema_version` を埋め込む。パートナー2社と consumer-driven contract テストを合意(使用フィールドの可視化)。

**ステップ6(マイグレーション計画)**: `attendees JSON` → `reservations` テーブルは expand-contract(下表)。contract 実施条件は「旧列参照クエリゼロを14日間観測」。

**ステップ7(セルフレビュー)**: 「空き枠数 `available_slots` をレスポンスに含めたが、これは導出値であり結果整合(予約直後の検索にずれうる)」→ 契約に鮮度の注記を追加。「一番後悔しそうな妥協」としてバッチのDB直読み温存をリスク欄に明記。

## 成果物(抜粋)

### エンドポイント表

| 操作 | メソッド/パス | 主なステータス | 備考 |
|---|---|---|---|
| 空き枠検索 | `GET /lessons?date=&studio_id=&cursor=` | 200 | カーソルページング、`available_slots` は結果整合 |
| レッスン取得 | `GET /lessons/{lesson_id}` | 200 / 404 | |
| 予約作成 | `POST /reservations` | 201 / 409(満席・重複)/ 422 | `Idempotency-Key` 必須 |
| 予約取得 | `GET /reservations/{reservation_id}` | 200 / 404 | 他パートナーの予約は404 |
| 予約キャンセル | `POST /reservations/{reservation_id}:cancel` | 200 / 404 / 422(期限超過) | 冪等(キャンセル済みへの再実行は200) |
| 予約確定通知 | webhook `reservation.confirmed` | — | ID+`schema_version` のみ運ぶ通知イベント |

### スキーマ定義(DDL抜粋)

```sql
CREATE TABLE reservations (
  id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  public_id     CHAR(26)    NOT NULL UNIQUE,            -- ULID(外部公開ID)
  lesson_id     BIGINT      NOT NULL REFERENCES lessons(id),
  customer_id   BIGINT      NOT NULL REFERENCES customers(id),
  partner_id    BIGINT      REFERENCES partners(id),    -- NULL = 自社チャネル(意味を列コメントに明記)
  status        TEXT        NOT NULL CHECK (status IN ('confirmed', 'cancelled')),
  cancelled_at  TIMESTAMPTZ,                            -- status='cancelled' の時のみ非NULL
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (lesson_id, customer_id)                       -- 同一レッスンへの二重予約防止(冪等性の最終防衛線)
);
CREATE INDEX idx_reservations_lesson ON reservations (lesson_id, status);      -- 定員集計用
CREATE INDEX idx_reservations_partner ON reservations (partner_id, created_at); -- パートナー別一覧用
```

### マイグレーション段取り表(`attendees JSON` → `reservations`)

| # | 段階 | 変更内容 | デプロイ単位 | 完了の計測 | ロールバック |
|---|---|---|---|---|---|
| 1 | Expand | `reservations` テーブル追加 | DDLのみ | 適用確認 | テーブル削除 |
| 2 | 二重書き込み | 予約処理が `attendees` と `reservations` の両方へ書く(正は旧) | アプリ | 新規予約の両側件数一致 | アプリを旧版へ |
| 3 | バックフィル | 既存 `attendees` を `reservations` へコピー(1000行チャンク・冪等) | バッチ | 突合: 全レッスンで件数・顧客ID一致 | 再実行(冪等) |
| 4 | 読み取り切替 | 予約参照・定員判定を `reservations` 基準へ(フラグで段階切替) | アプリ | エラー率・予約成功率が切替前と同等 | フラグで旧読みへ |
| 5 | 書き込み縮退 | `attendees` への書き込み停止(直前に突合再実行) | アプリ | 旧列参照クエリゼロを14日間観測 | 3から再実行 |
| 6 | Contract | `attendees` 列を削除 | DDLのみ | — | 不可(バックアップのみ) |
