# スキル評価研究のエビデンス

## 一次情報

- [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) — 2026-07-20参照、preprint。固定したGitHubリポジトリと実行可能な受け入れ条件で、スキル有無の限界効果をpaired評価する。報告値を他モデル・他領域の普遍値として扱わず、「スキルは測定しなければ価値が分からない」という設計根拠に使う。
- [Agent Skill Evaluation and Evolution](https://arxiv.org/abs/2606.11435) — 2026-07-20参照、survey/preprint。utilityだけでなく安全性、一般化、効率、更新を含む評価軸。
- [SkillGrad](https://arxiv.org/abs/2605.27760) — 2026-07-20参照、preprint。単発反省ではなく、反復して現れる診断と対照的な実行証拠を保持する考え方。
- [OPID](https://arxiv.org/abs/2606.26790) — 2026-07-20参照、preprint。trajectory由来のskill supervisionは生成したpolicyとstate distributionに依存するため、別モデルへの転用を無条件に仮定しない。

## 採用上の注意

- preprintの実験結果を本リポジトリの改善証拠として代用しない。本リポジトリ自身のbaseline/with-skillを実行する。
- モデル、tool policy、task fixture、rubric、反復数、token/latencyを固定・記録する。
- 実行エージェントとgraderを分離し、grader rubricと期待答えを実行側から隔離する。
