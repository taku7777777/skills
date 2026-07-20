# 決済サービスの現行リリース

## 現行パイプライン

```text
merge main
  -> build image
  -> unit tests
  -> deploy production (全podを一括更新)
  -> smoke test
```

- stagingとproductionで別々にimageをbuildする。
- DB migrationは新アプリ起動時に自動実行し、古いカラムをその場でdropすることがある。
- rollbackは「前のimage tagを手で探して再deploy」。DBは戻さない。
- feature flagにowner・期限・削除条件がない。
- production deployは週1回、平均差分1,800行。

## 直近90日の実績

- deploy 12回、変更障害4回、平均復旧95分。
- 原因特定に時間がかかり、3回は複数変更をまとめてrollbackした。
- smoke testは正常なカード1件のみ。
- checkout成功率とp95 latencyは計測済み。エラーバジェットポリシーはない。

## 制約

- Kubernetesを利用。10%単位のtraffic splitが可能。
- 新旧アプリを最大1時間共存させられる。
- 決済・認証・DB schema変更は人間承認が必要。
