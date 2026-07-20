# 決済APIインシデント資料

## 症状

- 2026-07-18 10:05 JST のデプロイ後、`POST /checkout` の約7%がHTTP 504。
- 失敗は本番のみ。ステージングでは100回中0回。
- 失敗したリクエストの一部でも、決済事業者側には売上が作成されている。
- 復旧操作や設定変更はまだ行っていない。

## checkout-apiログ

```text
10:12:01.002 request_id=r-101 payment.start idempotency_key=order-771
10:12:01.303 request_id=r-101 payment.error error="context deadline exceeded" elapsed_ms=301
10:12:01.304 request_id=r-101 response status=504 elapsed_ms=302

10:12:08.110 request_id=r-102 payment.start idempotency_key=order-772
10:12:08.295 request_id=r-102 payment.success provider_status=201 elapsed_ms=185
10:12:08.296 request_id=r-102 response status=200 elapsed_ms=187
```

失敗リクエスト200件の `elapsed_ms` は295〜305msに集中している。

## 決済事業者の監査ログ

```text
10:12:01.431 idempotency_key=order-771 charge.created amount=12800
10:12:08.294 idempotency_key=order-772 charge.created amount=5400
```

決済事業者の直近7日間のレイテンシは p50=180ms、p95=440ms、p99=720ms。障害やエラー率上昇の告知はない。

## デプロイ差分

```diff
- PAYMENT_TIMEOUT_MS: "1500"
+ PAYMENT_TIMEOUT_MS: "300"
```

変更PRの説明は「接続プール上限の調整」で、タイムアウト変更への言及はない。アプリケーションコードの変更はない。

## 環境差分

| 項目 | 本番 | ステージング |
|---|---:|---:|
| `PAYMENT_TIMEOUT_MS` | 300 | 1500 |
| 決済事業者 | production endpoint | sandbox endpoint |
| p95レイテンシ | 440ms | 90ms |

## 現在利用可能な操作

- ログ、メトリクス、設定履歴の読み取り
- ステージングでの再現実験
- 本番変更はインシデントコマンダーの承認が必要
