# impl-review 適用例

題材: 架空の中堅企業向け経費精算SaaS「ケイヒフロー」の「多段階承認ワークフロー」実装PRのレビュー。要件はUS-02(閾値による2段階承認・職務分掌)とFR-02(全承認操作の監査ログ)。別セッションのエージェントが実装したPRを人間がレビュー依頼してきた、という設定。

## 入力(ユーザーの依頼と文脈)

> 「承認ユースケースのPRをレビューして。テストは通ってる」

## 各ステップでの判断

- **ステップ0(コンテキスト把握)**: PR説明ではなく要件(US-02 / FR-02)とDDD設計書から期待挙動を再導出。差分は約120行で1パスで読める。diffの外にある呼び出し元(コントローラ)と`ExpenseReport`のモデル定義も読む。既存テストを実行しベースラインgreenを確認。
- **ステップ1(設計)**: DDD設計書は「承認は`report.approve()`の振る舞い、不変条件は集約が守る」としているが、実装はユースケース層でフィールドを直接書き換えており設計と不一致 → 認可欠落(下記🔴)の温床にもなっている。
- **ステップ2(正当性)**: 認可・並行性・境界(pendingステップなし)で具体的な失敗シナリオを構成できたものだけ指摘化。
- **ステップ2.5(AI生成コード特有)**: 実装とテストが同一エージェント製 →「テストが通っている」ことを正しさの根拠から大きく割り引く。実際、テストは正常系のみで自己承認の拒否テストがない。未使用パラメータ`comment`を検出。
- **ステップ3(セキュリティ)**: 認可チェックの欠落を確認(🔴-1として確定)。
- **ステップ4(テスト)**: 境界・エラーパスのテスト欠如は🔴-1・🟠の修正とセットで指摘。
- **ステップ5(可読性)**: 状態の文字列リテラル散在のみ(🟡)。

## レビュー対象コード(抜粋)

```typescript
// src/application/approve-expense.usecase.ts
export class ApproveExpenseUsecase {
  constructor(
    private readonly expenseRepo: ExpenseReportRepository,
    private readonly auditLogger: AuditLogger,
  ) {}

  async execute(input: {
    expenseId: string;
    approverId: string;
    comment?: string;
  }): Promise<void> {
    const report = await this.expenseRepo.findById(input.expenseId);
    if (!report) throw new NotFoundError(input.expenseId);

    const step = report.steps.find((s) => s.status === 'pending');
    step.status = 'approved';
    step.approvedBy = input.approverId;
    step.approvedAt = new Date();

    if (report.steps.every((s) => s.status === 'approved')) {
      report.status = 'approved';
    }

    await this.expenseRepo.save(report);
    this.auditLogger.log('expense.approved', {
      expenseId: input.expenseId,
      approverId: input.approverId,
    });
  }
}
```

## 成果物(レビュー出力)

```markdown
## レビュー結果: 経費承認ユースケースの追加

**判定**: escalate — 認可(職務分掌)に関わるHARDゲート領域の差分であり、かつBlockerあり。修正後も人間レビュー必須

### 総評
US-02(閾値による2段階承認)の承認操作を実装するPR。レビュー対象は別エージェントの生成物のため、要件・設計書から期待挙動を再導出して突き合わせた。リポジトリ経由の永続化や既存のNotFoundError規約への追従は良い。一方、設計書が集約の不変条件としたルールがユースケース層に(しかも一部欠落した形で)実装されており、認可の欠落という実害につながっている。

### 指摘事項

#### 🔴 Blocker — マージ前に修正必須(バグ・データ破壊・セキュリティ)
1. `src/application/approve-expense.usecase.ts:16` — 承認者の認可検証がない
   **失敗シナリオ**: 認証済みの申請者本人が自分の申請IDと自分のIDで本APIを呼ぶ → 自分の高額経費を自己承認できる(US-02の職務分掌違反・IDOR)。担当外の任意ステップも承認できる
   **修正案**: 設計書どおり`report.approve(approverId)`を集約に実装し、「現在ステップの担当承認者以外」「申請者本人」をドメインエラーで拒否。拒否テストを追加

#### 🟠 Major — 修正を強く推奨(設計問題・将来の高コスト)
1. `src/application/approve-expense.usecase.ts:16-23` — 状態遷移の検証なしのフィールド直接書き換え
   **失敗シナリオ**: 最終承認済みの申請に再度実行 → `find`がundefinedを返し`step.status`でTypeError(二重送信で容易に発生)。取り下げ済み申請でも承認が進む
   **修正案**: 遷移検証を集約メソッドに集約(🔴-1の修正と同時に解消)
2. `src/application/approve-expense.usecase.ts:14-25` — read-modify-writeに競合制御がない
   **失敗シナリオ**: 承認と取り下げが同時実行 → 後勝ちで一方の更新が消え、取り下げ済みなのに承認済みの申請が生まれる
   **修正案**: ExpenseReportにバージョン列を追加し楽観ロック

#### 🟡 Minor — 改善提案(対応は任意)
1. `:26-29` — 監査ログが承認の永続化と別トランザクションで、失敗しても検知されない。FR-02(記録漏れ0件)に照らし同一トランザクションでの記録を推奨
2. `'pending'` / `'approved'` の文字列リテラル散在 → 設計書のExpenseStatus VOへ

#### 💬 Nit / 質問
1. `input.comment`が受け取られたまま未使用。承認コメントは保存する仕様か(US-03の差し戻し理由との混同?)

### 確認したが問題なしと判断した点
- 閾値判定(5万円)が本ユースケースにないのは欠落ではない — 承認ルートは申請時に確定する設計(ADR-01)で、提出ユースケース側に実装済みであることを確認
- `report.steps`の順序は申請時にルート順で構築・永続化されることをスキーマとファクトリで確認(`find`が先頭のpendingを返す前提は成立)
```
