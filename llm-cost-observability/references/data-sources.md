# データソース: ローカルトランスクリプトから測る(計測基盤ゼロの初手)

導入ステージ0(`/usage`・`/context`・請求書)と、ステージ3(OTel)の間には大きな段差がある。その段差を埋めるのがローカルトランスクリプトで、**追加契約ゼロ・基盤構築ゼロ・jq だけ**で費目分解・離席ギャップ・モデル切替・起動固定費が取れる。兄弟スキル `context-economy` のステップ1が要求する4入力は、**合計値としてはすべてここで閉じる**(起動固定費の**内訳**まで割りたいときだけ `/context` が要る。§2 (d))。

## 前提(先に読む)

- **公開仕様ではない。** 以下のファイル配置とフィールド名は実機観測(2026-07、Claude Code の macOS ローカル環境)であり、バージョンで変わりうる。動かなくなったら壊れたコマンドの推測修正をせず、まず `jq -r 'keys|join(",")' <file> | sort -u` と `jq -r 'select(.type=="assistant")|.message.usage|keys|join(",")' <file> | sort -u` で構造を確認する。
- **トランスクリプトにはプロンプト本文・ファイル内容・コマンド出力が丸ごと含まれる。** 本ファイルのコマンドはどれも集計値(トークン数・タイムスタンプ・モデル名)しか出さないように書いてある。生レコードを共有・貼り付け・LLMへ投入するときは必ずリダクションを通す。チーム計測でメンバーのトランスクリプトを集める設計は、この一点だけでもOTel(トークン量だけが流れる)より慎重な合意を要する。

## 目次

- 1. 置き場所とレコード型
- 2. 4入力の取得(jqワンライナー)+ TTL実測・モデル別構成比
- 3. ワンライナーでは閉じないが取れるもの
- 4. トランスクリプトからは取れないもの(OTelへ進む判断基準)
- 5. 落とし穴

## 1. 置き場所とレコード型

```
~/.claude/projects/<cwdをスラッシュ置換したプロジェクト名>/
  <session-id>.jsonl                                         # 本体セッション
  <session-id>/subagents/agent-<id>.jsonl                    # サブエージェント(本体とは別ファイル)
  <session-id>/subagents/agent-<id>.meta.json                # agentType / spawnDepth / toolUseId (+ 稀に parentAgentId)
  <session-id>/subagents/workflows/wf_<id>/agent-<id>.jsonl  # workflow経由の起動はもう1階層下・journal.jsonl が同居
```

**ディレクトリの階層と spawn の入れ子は別物。** 実測(1,020件のmeta)では `spawnDepth` が2以上のエージェントも `subagents/` 直下のフラット配置で、階層が1つ深くなるのは workflow 経由の起動だけだった(実測1,059ファイル中532件)。**入れ子は `spawnDepth` で表現される** — 収集は再帰(`subagents` 配下を `find`)、入れ子の解決は `meta.json` と覚える。ファイル名で `agent-*.jsonl` を指定すれば `journal.jsonl`(assistantレコードを持たない workflow の進行ログ)を自然に除ける。

1行1レコードのJSONL。コスト計測で使うのは次の3種:

| レコード | 判別 | 持っているもの |
|---|---|---|
| アシスタント応答(=課金の単位) | `.type=="assistant"` | `.timestamp`(ISO8601・UTC)/ `.message.model` / `.message.usage.{input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens}` / `.message.usage.cache_creation.{ephemeral_1h_input_tokens, ephemeral_5m_input_tokens}` / `.requestId` / `.sessionId` |
| 人間の指示 | 下の `H` フィルタ | プロンプト境界。プロンプト単価分布の分母 |
| ツール結果 | `.type=="user"` かつ `.toolUseResult` あり | 課金単位ではない。プロンプト数の分母に入れない |

人間の指示は `promptSource=="typed"` だけでは**足りない**。実測(ある1環境の本体セッションjsonl全件)では `sdk` 2,039 / `typed` 1,565 / フィールド自体が無いレコード 791 / `queued`(送信待ちに積まれた指示)30 が混在し、`typed` だけを数えると**この環境では2.83倍**、`sdk` を除いても**1.52倍**の過小計上になった(v2.1.215〜2.1.220 の全バージョンで欠落を確認。古い版だけの問題ではない)。倍率は環境の使い方で大きく動くので、**この数字を持ち込まず自環境で1度数える**。除くべきは `promptSource=="system"`(ハーネス注入の擬似プロンプト。ステップ2の「人間の指示へ畳み込む」対象)と `isMeta`(システム注入コンテキスト)・`isCompactSummary`(compactの要約)である。

以降のコマンドは、この共通フィルタを前提にする(`<synthetic>` を除く理由は §5):

```sh
# A: 課金対象のアシスタント応答。H: 人間の指示
A='select(.type=="assistant" and (.message.model|strings|.!="<synthetic>"))'
H='select(.type=="user" and (.toolUseResult|not) and (.isMeta|not) and (.isCompactSummary|not) and (.promptSource!="system"))'
F=~/.claude/projects/<project>/<session-id>.jsonl

jq -r "$H | .uuid" "$F" | wc -l   # このセッションの人間プロンプト数
```

**`H` は `promptSource=="sdk"`(`claude -p` / SDK経由の指示)も通す。** 上の実測ではこれが最頻値だった。ヘッドレス実行を「人間の指示」と数えるかは分析の目的で決める — 使い方の改善が目的なら含める(誰かがそのジョブを書いた)、対話セッションの単価分布を見たいなら `and (.promptSource!="sdk")` を足して除く。**どちらを採ったかを分母の定義として記録し、途中で変えたら過去の数字と並べない。**

`A` の `strings` は飾りではない。これが無いと `.message.model` に文字列以外・想定外の値が入ったレコードで集計が壊れる(実際に壊れる実例に遭遇済み)。

## 2. 4入力の取得(jqワンライナー)

**(a) 費目構成 — キャッシュ書き込み/読みの内訳**(支配費目の特定。SKILL.md ステップ4)

```sh
jq -s "[.[] | $A | .message.usage] | {input:(map(.input_tokens//0)|add), output:(map(.output_tokens//0)|add), cache_write:(map(.cache_creation_input_tokens//0)|add), cache_read:(map(.cache_read_input_tokens//0)|add)}" "$F"
```

トークン量のまま読む。金額は `evidence.md` の単価表を掛けて**読み出し時に**計算する(大原則3)。定額レーンではトークン量そのものが不変量なので、換算せずここで止めてよい。

**(b) 離席ギャップ × 再書込トークン**(cache write の原因特定)

```sh
jq -r "$A | [(.timestamp|sub(\"\\\\.[0-9]+Z$\";\"Z\")|fromdateiso8601), (.message.usage.cache_creation_input_tokens//0)] | @tsv" "$F" \
  | sort -n | awk -F'\t' 'NR>1{printf "%d\t%d\n",($1-p)/60,$2} {p=$1}' | sort -t$'\t' -k2 -rn | head
```

出力は「直前リクエストからの間隔(分) / そのリクエストの再書込トークン」で、**第2列(再書込トークン)の降順**に並ぶ。ここを間隔でソートすると「長い間隔の行が上位に来る」という同語反復になり、下の後半の読み方が `head` で切り落とされて到達不能になる。上位行が長い間隔に偏っていれば離席起因、間隔が短い行に大きな再書込が並ぶなら切替・ツール定義変更を疑う(`evidence.md` の再書込率分布と突き合わせる)。

**(c) モデル切替イベント**(セッション途中の `/model`・`/effort` 切替はキャッシュ全損)

```sh
jq -r "$A | [.timestamp, .message.model] | @tsv" "$F" \
  | sort | awk -F'\t' 'NR>1 && $2!=p {print $1"  "p" -> "$2} {p=$2}'
```

出力が空なら切替なし。行が出たらその時刻の直後のリクエストを (b) で確認する — 切替直後の再書込は「離席」ではなく切替が原因であり、打ち手が違う。

**(d) 起動固定費**(セッション初回リクエストの入力側合計)

```sh
jq -r "$A | [.timestamp, ((.message.usage.input_tokens//0)+(.message.usage.cache_creation_input_tokens//0)+(.message.usage.cache_read_input_tokens//0))] | @tsv" "$F" | sort | head -1
```

**再開セッションでは初回リクエストが冷たい起動ではない。** `--continue` / `--resume` / `/rewind` で始めたセッションの初回は既存プレフィックスの読み直しであり、これを新規起動と並べると起動固定費が実際より小さく見える。`cache_read_input_tokens` が大きい初回行は再開の疑いとして除外し、新規起動セッション同士でのみ比較する。内訳(システムプロンプト/ツール定義/CLAUDE.md/スキル)まで割りたいときは、トランスクリプトではなく `/context` を使う。

**(e) 請求レーンのTTL実測**(ステップ1のレーン確認を自分のデータで裏取りする)

```sh
jq -s "[.[] | $A | .message.usage.cache_creation//empty] | {h1:(map(.ephemeral_1h_input_tokens//0)|add), m5:(map(.ephemeral_5m_input_tokens//0)|add)}" "$F"
```

`h1` 側に偏れば1時間TTL、`m5` 側なら5分TTL。`evidence.md` の「認証方式でTTLが異なる」表を信じる代わりに、自分の環境の実効TTLを確認できる。定額購読でも usage credits 消費中は5分へ降格するため、表と実測がずれることが実際にある — ずれたら実測が正しい。

**(f) モデル別の費目内訳(数週間分・セッション横断)**(兄弟スキル `delegation-economy` のステップ1が要求する「数週間のモデル構成比」。`/usage` はセッション単位しか出さない)

§1の `$A` を先に定義しておく(このレシピだけは `$F` を使わず、プロジェクト配下を横断する)。単一ファイルではないので `jq -s` で全件をメモリに載せず、レコード単位でTSVへ落として `awk` で畳む(`xargs` が `jq` を複数回起動しても結果が壊れない)。

```sh
DAYS=28
SINCE=$(date -u -v-${DAYS}d +%Y-%m-%d)   # macOS。GNU dateなら date -u -d "-${DAYS} days" +%F
find ~/.claude/projects -name '*.jsonl' -mtime -${DAYS} -print0 \
  | xargs -0 -r jq -r "$A | select(.timestamp >= \"$SINCE\") | [.message.model, (.message.usage.input_tokens//0), (.message.usage.output_tokens//0), (.message.usage.cache_creation_input_tokens//0), (.message.usage.cache_read_input_tokens//0)] | @tsv" \
  | awk -F'\t' '{n[$1]++;i[$1]+=$2;o[$1]+=$3;w[$1]+=$4;r[$1]+=$5} END{for(m in n) printf "%s\treq=%d\tin=%d\tout=%d\twrite=%d\tread=%d\n",m,n[m],i[m],o[m],w[m],r[m]}' | sort
```

出るのはモデル別の**トークン量**であって金額ではない。構成比を金額で見るには `evidence.md` の単価表を費目ごとに掛ける — cache write と read で倍率が違うので、4費目を足したトークン合計のまま比べると読みを誤る(read偏重のモデルほど過大に見える)。`-mtime` はファイル更新時刻による粗い前絞りで、期間を確定するのは `select(.timestamp >= …)` 側 — **両者の窓を必ず同じ `$DAYS` から作る**。日付をベタ書きすると時間が経つほど `-mtime` 側だけが狭く滑り、頼んだ期間が黙って切り詰められる(エラーは出ない)。サブエージェントのファイルもそのまま含まれる — §3と違い横断集計なので二重計上にはならず、むしろ含めないと委任の多いモデルが過小に出る。

## 3. ワンライナーでは閉じないが取れるもの

**サブエージェント費(セッション単位)** — 本体jsonlには含まれないので、別ファイルを足す。本体だけを見ると委任の多いセッションほど過小評価になる。

```sh
D=~/.claude/projects/<project>/<session-id>
find "$D/subagents" -name 'agent-*.jsonl' -print0 \
  | xargs -0 -r jq -r "$A | [(.message.usage.input_tokens//0), (.message.usage.output_tokens//0), (.message.usage.cache_creation_input_tokens//0), (.message.usage.cache_read_input_tokens//0)] | @tsv" \
  | awk -F'\t' '{n++;i+=$1;o+=$2;w+=$3;r+=$4} END{printf "req=%d\tinput=%d\toutput=%d\tcache_write=%d\tcache_read=%d\n",n,i,o,w,r}'
```

`$(find …)` をコマンド置換で jq に渡す形にしない。サブエージェントが1つも無いセッションでは引数ゼロの `jq` が標準入力を待って**エラーも出さずに固まる**。`-print0 | xargs -0 -r` なら入力が空のとき jq 自体が起動しない。`-r` は必須で、これが無いと GNU xargs(Linux)は入力が空でも jq を1回起動してしまい、同じ固まり方をする(BSD xargs=macOS は既定で起動しないが `-r` も受け付けるので、両環境で `-r` を付けておく)。ファイル数が多くて `xargs` が jq を複数回起動しても、レコード単位TSV+`awk` の畳み込みなので合計は壊れない(`jq -s` だと起動ごとに別の集計結果が出る)。

**プロンプト単位のspawn連鎖帰属** — ワンライナーでは閉じないが、小さなスクリプトで到達できる。`agent-<id>.meta.json` の `toolUseId` は、**そのエージェントを起動した側の会話**のトランスクリプト内の `tool_use` ブロックの `id` に一致する。本体jsonlとは限らない:

- `spawnDepth == 1` → 本体 `<session-id>.jsonl` 内。
- `spawnDepth >= 2` → **親エージェントの `agent-*.jsonl` 内**(本体jsonlを検索しても見つからない。実測1,020件中84件がこれ)。`parentAgentId` があればそれが親だが、実測では18件しか持っていなかった。**無い場合はセッション配下の `agent-*.jsonl` を横断して当該 `id` を持つファイルを探す**のが確実で、見つかったファイルのエージェントが親。これを親が `spawnDepth == 1` になるまで再帰する。

起点の `tool_use` を含む assistant レコードまで辿れたら、そこから `parentUuid` を遡り、**最初に当たる §1 の `H` を満たす user レコード**が起点プロンプト(`promptSource=="typed"` 単独で遡らない。§1・§5と同じ分母の定義を使う — typed 単独の遡上は、解決可能な spawn のうち相当数——別途の実測では約1/4——でアンカーを1つも見つけられない)。`H` は `promptSource=="system"` の擬似プロンプトを既に除いているので、擬似プロンプトに当たったらそのまま親へ遡り続ける形になり、SKILL.md ステップ2の「人間の指示へ畳み込む」と一致する。これで「どの人間の指示が、どのサブエージェント費を引き起こしたか」が決まる。

**この経路のカバレッジには限界がある。** 実測では meta.json の約半数(1,020件中493件。内訳は `workflow-subagent` 406件・`general-purpose` 87件)が `toolUseId` 自体を持たず、この経路では起点を決められない。**帰属できなかった分は「欠損」として件数とトークン量を報告し、暗黙に0として落とさない**(大原則3の「未知を暗黙のデフォルトで埋めない」と同じ扱い)。カバレッジを併記しない帰属表は、委任の多い利用者を過小評価したまま順位づけする。

コストの見積り: この帰属スクリプトは1〜2時間の作業であり、ワンライナーの延長ではない。**高額テールの構成比でサブエージェント費が上位に来て初めて着手する** — 支配費目でないなら §2 の (a)〜(e) で止めてよい。

## 4. トランスクリプトからは取れないもの(OTelへ進む判断基準)

| 欲しいもの | トランスクリプトで取れるか | 代わりに何が要るか |
|---|---|---|
| チーム横断のper-user集計 | ✗(各自のマシンのローカルファイル。集めること自体が §前提のプライバシー問題) | OTelメトリクス(トークン量だけが流れる)/ Analytics API |
| ニアリアルタイムの共有ビュー | ✗(事後のファイル読み) | OTel |
| クラウドプロバイダ経由(Bedrock/Vertex)の請求突合 | ✗ | OTel か gateway |
| 介入conversion(警告に従った率) | ✗ | 介入の発火と直後の行動を**記録する仕組みを自分で作る**。どのデータソースにも存在しない |
| 差し戻し率・手戻り率(counter-metrics) | ✗ | PR記録・再依頼記録からの人手集計。テレメトリではなく人間の判定 |

下2行は「まだ取れていない」のではなく**原理的にテレメトリではない**。conversion と counter-metrics は人間の判断の記録であり、だからこそ大原則6が「介入にはconversionの計測と改訂基準を最初からつける」と要求している — 後から掘り出せるデータではないので、介入を作る時点で記録経路も一緒に作る。

**OTelへ進む判断基準**: 上表の上3行のいずれかが実際の意思決定を止めているときだけ。「個人の使い方を直したい」段階では §2 で足りる。チーム帰属・組織統制が要件になった時点でステージ3へ上げる(`cost-metrics-catalog.md` の導入ステージ判断表)。

## 5. 落とし穴

- **`<synthetic>` を除く。** `.message.model` には実モデルIDのほかに `<synthetic>` が現れる(ハーネスが生成した擬似応答)。除かないとモデル構成比に存在しないモデルが混じり、リクエスト数の分母も狂う。大原則3(未知モデルを暗黙のデフォルト単価で埋めない)の実例そのもの — 単価表に無いモデルIDが出たら、埋めずにコスト欠損として扱う。
- **人間プロンプト数を `promptSource=="typed"` で数えない。** §1の `H` を使う(`sdk` を含めるかの判断も§1で1度決めて記録する)。`typed` だけだと実測で1.5〜2.8倍の過小計上になり、プロンプト単価分布の**分母が壊れる** — 平均・分位点がそろって高く出て、実際にはテールでない案件をテールと誤認する。分母を変えたら過去の数字と並べない。
- **`.timestamp` はUTC。** ローカル日で集計するなら変換を1箇所に固定する。UTC日とローカル日を混ぜて日次で並べない(SKILL.md ステップ1)。
- **サブエージェントを二重に数えるのは `<session-id>/**/*.jsonl` のように再帰globを使ったとき。** 本体は `<session-id>.jsonl`(単一ファイル)、サブエージェントは `<session-id>/subagents/` 配下と分かれているので、本体の集計は再帰させない。古い形式のトランスクリプトでは本体ファイル内に `isSidechain==true` が混ざることがあるので、合算する前に `jq -r '.isSidechain' | sort | uniq -c` で確認する。
- **セッション費 ≠ 本体jsonlの合計。** §3 の subagents ディレクトリを足していない集計は、委任の多いセッションで系統的に過小評価する。
- **ここで出るのはトークン量であって請求額ではない。** 金額にするには単価表を掛ける必要があり、定額レーンではその換算値は請求額ではない(大原則7)。閾値をトークン建てで持てば換算そのものが不要になる(`evidence.md` のトークン建て閾値)。
