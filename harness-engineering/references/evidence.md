# ハーネス設計の時点依存エビデンス

## 使い方

数値を成果物へ引用するときは、対象モデル、エージェント構成、課題集合、成功確率、更新日を併記する。ベンチマークの比率を個別組織の委任上限へ直接転用せず、自組織のタスクで再測定する。

## 一次情報

- [METR: Task-Completion Time Horizons of Frontier AI Models](https://metr.org/time-horizons/) — 継続更新ページ。2026-07-20参照。time horizonは、人間専門家の所要時間で表した課題難易度に対する成功確率の推定であり、エージェントのwall-clock稼働時間ではない。公開モデル・課題集合・方法論の更新に伴って値が変わるため、引用時にページの最終更新日を確認する。
- [Anthropic: How we contain Claude across products](https://www.anthropic.com/engineering/how-we-contain-claude) — 2026-07-20参照。能力だけでなくsandbox、filesystem、egress、credential境界でblast radiusを制約する実装上の知見。

## 更新規律

- 四半期ごと、または主要モデル/エージェント構成の更新時に再確認する。
- 数値が変わっても「能力評価と高信頼委任は別」「検証可能性と影響半径で委任を決める」という安定原則はSKILL.mdに残す。
- 外挿値は実測値と明確に区別し、運用ポリシーの唯一の根拠にしない。
