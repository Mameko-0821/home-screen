# home-screen

iPhone Duo のホーム画面デザインを考えるためのリポジトリ。

## 提案書

- `proposal/iphone-duo-home-screen.html` … 調査結果とデザイン案（モックアップ付き）。写真は `proposal/img/`
  - 公開ページ（claude.ai の Artifact）: https://claude.ai/artifact/CcPpBTxG9pDkheXbWm3ggR
  - このファイルは Artifact 用のソースで、`<!doctype>` と `<head>` は公開時に付きます。

## 考え方：表紙と見開き

iPhone Duo は外側（5.4型・1398×2034）と内側（7.6型・1878×2670）が同じ約1:1.4の比率です。外側の面積は内側のほぼ半分で、開くとホーム画面が2ページ並びます。
そこで **外側＝本の「表紙」（P1）、内側＝「見開き」（P1＋P2）** としてデザインします。

## 5つの案

| 案 | 名前 | アイコン | 主なウィジェット | 本体 |
|---|---|---|---|---|
| A | 砂丘時計 | クリア | 天気（中）／カレンダー（大） | スターホワイト |
| B | 文庫 | 色合い調整（墨色） | 縦書き日付（小）／メモ（特大 4×6） | スターホワイト |
| C | 夜間飛行 | ダーク | ミュージック（中）／TV（大）＋ショートカット（中） | ナイトスカイ |
| D | くすみ | ショートカットで作るカスタム | 写真・カレンダー・天気・時計 | スターホワイト |
| E | 推し色 | 色合い調整（推し色） | 写真「アルバム」（特大 4×6） | ナイトスカイ |

## 第2稿（11月2日）：あなた用の3案

回答：好きな案はA・B／右手・ケースあり／本体はナイトスカイ／壁紙は自然・柴犬／アプリと「開いてすること」は未定

| 案 | 名前 | 壁紙 | アイコン |
|---|---|---|---|
| A′ | 星見の柴 | 夜の砂丘で月を見上げる柴（昼は太陽と砂丘） | クリア |
| B′ | 柴日和 | 藍染めの和紙に水墨の山と月、岩の上の柴、「柴日和」の書と落款 | 色合い調整（生成り／墨） |
| A×B | 月夜の版画 | 木版画風の湖と山、月の道と岸辺の柴（昼は青空と雲） | 色合い調整（月の金／藍） |

配置の考え方：右手だと外側の左端に指が届かないので、左半分は月と柴が見える「窓」にして、アプリは右に集める。

- ①〜④：Dock（右端。閉じても開いても届く）
- ⑤〜⑩：P1の右2列。右下の⑤から指が届きやすい順に
- それ以外：ホーム画面に置かず、アプリライブラリから
- P2（開いた右ページ）：特大ウィジェット。決まるまでは柴の写真

## 第3稿（11月2日）：写真で作り直した3案

第2稿までの壁紙はコードで描いたイラストで、安っぽく見えたため、写真家の写真（Unsplash）に切り替えた。
外側（縦）と内側（横）で構図を切り直し、主役が折り目やアイコンに隠れない位置に置いている。

| 案 | 外側（閉じた状態） | 内側（開いた状態） | アイコン |
|---|---|---|---|
| 星空 | 天の川を縦に | 山並みの上の天の川（中心は左ページ） | クリア |
| 富士と紅葉 | 紅葉ごしの富士と湖 | 夕焼けの富士と湖（富士は左ページ） | 色合い調整（紺） |
| 柴と秋 | 紅葉が舞う中の柴犬 | 紅葉の庭と池＋右ページに柴の写真 | クリア |

### 第3稿の写真のクレジット（Unsplash License）

- 星空：Robson Hatsukami Morgan — https://unsplash.com/photos/silhouette-of-mountains-under-milky-way-galaxy--wEFdRCG4IU
- 紅葉と富士：Andreas Rasmussen — https://unsplash.com/photos/mount-fuji-and-autumn-maple-leaves-GhvpEtG5HMs
- 夕焼けの富士：Perry Merrity II — https://unsplash.com/photos/a-snow-covered-mountain-towering-over-a-lake-5P0lI61BIj8
- 紅葉と柴：Jaycee Xie — https://unsplash.com/photos/a-brown-and-white-dog-standing-next-to-a-tree-aH9Uskj8XTU
- 紅葉の庭：Lucas Calloch — https://unsplash.com/photos/red-and-green-trees-beside-river-during-daytime-P-yzuyWFEIk
- 落ち葉と柴：Charlotte Rush — https://unsplash.com/photos/brown-and-white-short-coated-dog-on-brown-leaves-during-daytime-odJtBMxGEfk
- 浜辺の柴：Marco Grosso — https://unsplash.com/photos/a-happy-shiba-inu-dog-sits-on-a-pebble-beach-En7pqRghArU

## 第4稿（11月2日）：見やすい幾何学模様

写真は背景がにぎやかでアイコンが見づらかったため、控えめな幾何学模様に切り替えた。
模様の線は背景とほぼ同じ明るさにして、アイコンと文字を読みやすくしている。外側と内側で模様の大きさをそろえ、内側は折り目を中心に左右対称。

- 模様：青海波・麻の葉・七宝・亀甲・市松・同心円
- 色：墨・鉄・焦茶・砂・苔・葡萄（青系は使わない。白い文字が読めるよう中間〜暗めの色）
- アイコン：クリア、または白（色合い調整）

### 壁紙（`wallpapers/`）

6つの模様の「墨」。外側用 `*_outer_1398x2034.jpg`、内側用 `*_inner_2670x1878.jpg`。
ほかの色は提案書のページで確認でき、希望の組み合わせで書き出せる。

## 調査メモ（デザインに効く事実）

- 内側はホーム画面を2ページ同時に表示し、左に「今日」の表示（Apple）
- Dock・ロック画面のコントロール・ナビゲーションは画面の横へ（Apple）。国内報道では右側
- iOS 27 で特大ウィジェット（4×6）が追加。純正は11アプリ17種類（9to5Mac、iPhone Mania）
- 外側は右手持ちだと左端に親指が届かない → よく使うアプリは右へ。ケース使用時は「左端を移動」（gori.me）
- 壁紙は外側が縦 1398×2034、内側が横 2670×1878 の2枚で1組（iClarified、duowallpaper.org）
- アクションボタンなし、Touch ID は電源ボタン（gori.me）
- 充電していなくても StandBy（Apple）
- 本体色はスターホワイト／ナイトスカイ。純正ケースはサンド／ネイビー、Folio はネイビー／トープ（Apple）
- ホーム画面の列×行数は未公表。提案書では 1ページ＝4列×6行 で描いている（推定）

## 出典

- Apple Newsroom: https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/
- Apple 技術仕様: https://www.apple.com/iphone-duo/specs/
- gori.me: https://gori.me/?p=171700
- Business Insider Japan: https://www.businessinsider.jp/article/2609-apple-unveils-iphone-duo/
- iPhone Mania: https://iphone-mania.jp/?p=607526
- ギズモード・ジャパン: https://www.gizmodo.jp/article/2610-iphone-duo-review-price-durability/
- 9to5Mac: https://9to5mac.com/2026/10/14/ios-27-adds-brand-new-widgets-for-your-iphones-home-screen/
- Macworld: https://macworld.com/article/3230936/iphone-duo-the-five-most-important-things-you-need-to-know.html
- Blake Crosley: https://blakecrosley.com/blog/iphone-duo-for-developers
- iClarified: https://www.iclarified.com/102102/download-the-official-iphone-duo-wallpaper-here
- duowallpaper.org（Apple非公式）: https://duowallpaper.org/iphone-duo-wallpaper-size
- MacRumors: https://macrumors.com/how-to/ios-make-app-icons-clear-iphone-home-screen/

## 次のステップ

提案書の最後にある6つの質問（好きな案、利き手とケース、本体色、毎日使うアプリ、壁紙のモチーフ、開いてすること）に答えてもらい、
配置図・実寸の壁紙ペア（ライト／ダーク）・設定手順のチェックリストを作る。
