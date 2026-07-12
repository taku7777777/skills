---
name: api-data-design
description: API契約とデータモデルを設計するスキル。REST/RPC/イベントAPIの契約設計、DBスキーマ設計、互換性・バージョニング方針の策定、expand-contractによるスキーママイグレーション計画を行うときに使用する。トリガー例:「APIを設計して」「エンドポイントを設計して」「DBスキーマを設計して」「テーブル設計して」「この変更は破壊的変更か判定して」「マイグレーション計画を立てて」
---

# API・データモデリング設計スキル

Zalando RESTful API Guidelines、Google API Improvement Proposals(AIP)、進化的データベース設計(Sadalage & Fowler の同名記事、Ambler & Sadalage『Refactoring Databases』)、Parallel Change(expand-contract)、consumer-driven contracts、頑健性原理(Postel's law)の現代的再検討の知見を統合した、「境界の契約とその進化」を具体化する設計プロセス。

領分の境界: システム分割・技術選定・脅威モデリングは `arch-security-design`、集約・ドメインロジックの内部構造は `ddd-design`、契約テストの設計は `test-design`、マイグレーションのデプロイ順序・リリース工程は `cicd-release` の領分(いずれも同スキル集内)。本スキルはその間にある「境界に公開する契約と、その安全な進化」を担う。

## 大原則

1. **APIは実装の露出ではなく、利用者の語彙とユースケースから設計する。** 内部テーブルやORMの形がそのままJSONに透けたAPIは、実装の変更が全利用者の変更になる。契約は「利用者が何をしたいか」から書き、実装とは独立にレビューする(API First)。
2. **公開した契約は一方通行。** 破壊的変更は「してはいけない」ではなく「移行計画とセットでしか、できない」。公開範囲(チーム内/パートナー/一般公開)が広いほど取り消しコストは桁で増えるため、公開前の契約レビューに最も労力を割く。
3. **スキーマはコードより寿命が長い。** コードは書き直せるがデータは移行するしかない。テーブル設計の妥協は10年残る前提で、制約・型・NULLの規律に初期投資する。
4. **互換性の判定を曖昧にしない。** 「何が破壊的変更か」を個人の感覚ではなくチームの共通判定表で機械的に判定する。寛容な受信(頑健性原理)に互換性を頼らない — 曖昧に受理した入力は観測され、事実上の契約になって仕様を蝕む。未知フィールドの無視(tolerant reader)だけを消費側の明示的な契約として許す。
5. **スキーマ変更は expand-contract(Parallel Change)を既定にする。** 追加(expand)→移行(migrate)→削除(contract)に分割し、各段階を独立にデプロイ・ロールバック可能にする。ビッグバン切替は最終手段であり、選ぶなら理由を設計書に書く。
6. **データの所有権を一意にする。** 同じ事実を複数システムが所有すると必ず矛盾する。各データに単一の所有者を定め、他システムが持つ写しはキャッシュ/レプリカ(鮮度と更新経路つき)と明示する。
7. **機械可読な契約を single source of truth にする**(AI時代の補正)。API契約とスキーマ定義は、エージェントが実装・テスト・レビューで最も頻繁に参照する仕様である。OpenAPI・スキーマ定義・DDLを正とし、人間向け文書はそこから生成する(配置規約は `docs-for-ai` スキル)。文書と定義が乖離した瞬間、エージェントは古い方を信じて誤実装する。

## ワークフロー

### ステップ1: 利用者とユースケースの整理

契約を書く前に「誰が・何のために・どの頻度で」呼ぶかを表にする:

- 利用者の列挙: 自社フロントエンド、他チームのサービス、外部パートナー、バッチ、AIエージェント。それぞれの公開範囲(private / partner / public)を分類する — 範囲が契約変更のコストを決める
- ユースケースごとに、必要な操作と参照するフィールドを利用者側の視点で列挙する(consumer-driven)。**使われる見込みのないフィールドを契約に入れない** — 公開したものは全て将来の変更コストになる
- 非機能の前提: 呼び出し頻度、データ量、レイテンシ要求、結果整合で許されるか

### ステップ2: スタイル選択とリソース/操作モデリング

- スタイルを判断基準で選ぶ(併用が普通): **REST** = リソースのCRUDが中心で利用者が広い / **RPC(gRPC等)** = 操作中心の内部サービス間・性能重視 / **イベント** = 結果整合でよい通知・複数購読者。「流行っているから」はどれの根拠にもならない
- RESTならリソースを抽出する。名前は `ddd-design` の用語集(ユビキタス言語)から取り、標準メソッド(List/Get/Create/Update/Delete)に寄せ、収まらない操作だけをカスタムメソッド(例: `:cancel`)にする(Google AIP のリソース指向設計)
- イベントは通知イベント(IDのみ運び、詳細はAPIで取得)か event-carried state transfer(状態を運ぶ)かを、購読者の結合度と再取得コストで選ぶ
- **内部モデルをそのまま公開しない。** 公開契約は内部のドメインモデルから独立に設計する(`ddd-design` の統合イベント/Published Language と同じ規律)

### ステップ3: 契約の詳細設計

[`references/api-schema-checklists.md`](references/api-schema-checklists.md) のREST API設計チェックリストに従い、命名・HTTPメソッドとステータスコード・ページング・フィルタ・エラー形式(RFC 9457 Problem Details)・冪等性・認可の粒度を決める。特に:

- エラー形式・ページング・冪等性は**エンドポイント個別ではなくAPI全体の規約**として先に決め、全エンドポイントで一貫させる
- 契約は OpenAPI(イベントなら AsyncAPI / スキーマレジストリ)で書き、これを正とする。実装コードからの自動生成に頼ると実装の都合が契約に漏れる

### ステップ4: データモデリング

- エンティティと所有権を確定する(`arch-security-design` のデータ管理設計から引き継ぐ)。集約の不変条件は `ddd-design` の成果物を参照し、トランザクション境界とテーブル設計を整合させる
- **制約はDBに宣言する**(NOT NULL・一意・外部キー・CHECK)。アプリケーションコードだけで守る制約は、経路が増えた瞬間に必ず破れる
- 正規化を既定とし、非正規化は「計測された性能問題+元データからの再導出手段」とセットでのみ行う
- インデックスは主要クエリのアクセスパスから設計する(推測でなくクエリ一覧から)
- 型・NULL・監査列・論理削除の判断は [`references/api-schema-checklists.md`](references/api-schema-checklists.md) のスキーマ設計チェックリストで確認する

### ステップ5: 互換性・バージョニング方針

- [`references/api-schema-checklists.md`](references/api-schema-checklists.md) の**互換性判定表をチームの共通判定基準として合意**し、契約変更レビューのゲートにする
- 既定は「バージョンを上げない」: 互換的な追加のみで進化させる。破壊的変更が必要になったら、それはバージョニングの問題ではなく**移行計画(ステップ6)の問題**である
- イベントスキーマにはバージョンを埋め込む(ペイロードまたはトピック名)。イベントは保存され再生されるため、APIより長く旧バージョンと共存する
- 「誰がどのフィールドを使っているか」を consumer-driven contract テストで可視化する(テストケース設計は `test-design` の契約ケース設計へ)。契約にない利用は互換性保証の対象外であることを明文化する

### ステップ6: マイグレーション計画

- expand-contract で段取りを組む: [`references/api-schema-checklists.md`](references/api-schema-checklists.md) の手順書(API版・DB版)に従い、段階ごとの変更・デプロイ単位・ロールバック手段を表にする
- **contract(削除)の実施条件を数値で決める**(例: 旧エンドポイント呼び出しゼロを14日間観測、旧カラム参照クエリゼロ)。期限と計測がない deprecated は永遠に残る
- 大テーブルのALTERはロック挙動を事前に調べ、バックフィルはチャンク分割+突合検証を計画に含める
- 各段階のデプロイ順序・リリース工程の実装は `cicd-release` スキルへ

### ステップ7: セルフレビュー

設計書提出前に自問する:

- [ ] 実装の内部構造が契約に漏れていないか(テーブル名・ORMの形がそのままJSONに出ていないか)
- [ ] 全ての変更を互換性判定表で判定したか。破壊的変更に移行計画が付いているか
- [ ] エラー形式・ページング・冪等性が全エンドポイントで一貫しているか
- [ ] 各データの所有者は一意か。写しはキャッシュ/レプリカと明示されているか
- [ ] このスキーマを10年運用する前提で、一番後悔しそうな妥協は何か → 正直にリスク欄へ書く
- [ ] OpenAPI・スキーマ定義・DDLが single source of truth になっているか(手書き文書との乖離経路がないか)

## 成果物フォーマット

設計書は以下の構成で出力する(規模に応じて省略可、ただし省略は明示):

```markdown
# <API/機能名> API・データ設計書
## 1. 利用者とユースケース(誰が・何のために・どの頻度で)
## 2. スタイル選択とリソースモデル(判断根拠つき)
## 3. API契約(エンドポイント表 + OpenAPI等の定義ファイルへの参照)
## 4. データモデル(DDL/ER図、制約、インデックス、データの所有権)
## 5. 互換性・バージョニング方針(合意した互換性判定表への参照を含む)
## 6. マイグレーション計画(expand-contract 段取り表、contract実施条件)
## 7. リスクと未解決事項(正直に)
```

実例: `references/worked-example.md`

## 知見の出典

- Zalando RESTful API Guidelines(API First、互換性ルール、Problem JSON の採用)
- Google API Improvement Proposals(AIP)/ Google API Design Guide(リソース指向設計、標準メソッドとカスタムメソッド)
- Pramod Sadalage & Martin Fowler「Evolutionary Database Design」(martinfowler.com)/ Scott Ambler & Pramod Sadalage『Refactoring Databases』(データベースリファクタリング、移行期間の二重稼働)
- Danilo Sato「Parallel Change」(martinfowler.com, expand-contract)
- Ian Robinson「Consumer-Driven Contracts」(martinfowler.com)
- Jon Postel(頑健性原理)/ RFC 9413『Maintaining Robust Protocols』(寛容な受信への批判的再検討)
- Martin Fowler「Tolerant Reader」(martinfowler.com)
- RFC 9457『Problem Details for HTTP APIs』
- Greg Young『Versioning in an Event Sourced System』(イベントスキーマの進化)
