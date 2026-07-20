# 注文モジュールのテスト現況

## 数値

- statement coverage: 92%
- branch coverage: 61%
- テスト数: 438
- 平均CI時間: 28分
- 直近30日: flaky再実行率12%、テストのみ修正したPRが47件
- mutation score: 未計測

## 観測事実

- AI生成PRでは実装とテストを同じセッションで作る。
- 既存テスト35件が `.skip`。理由・Issue・期限はない。
- `expect(result).toBeDefined()` だけのテストが多い。
- 値引き計算テストは実装と同じ式をexpected側でも再計算する。
- 全テストが共有の巨大fixtureを読み、時刻は `new Date()`、乱数seedは固定しない。
- CI失敗時のチーム慣行は「2回rerunして通ればmerge」。
- テスト削除・assertion削除・snapshot更新を検知するゲートはない。
- checkout/決済/在庫引当は高リスク、管理画面の表示整形は低リスク。

## 制約

- CI時間を今四半期に2倍へ増やすことはできない。
- ユーザーの未コミット変更がある共有作業ツリーを自動でstash/revertしてはいけない。
