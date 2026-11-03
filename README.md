# home-screen

iPhone Duo のホーム画面デザインを考えるためのリポジトリ。

## 提案書

- `proposal/iphone-duo-home-screen.html` … 調査結果とデザイン案（モックアップ付き）。写真は `proposal/img/`
  - 公開ページ（claude.ai の Artifact）: https://claude.ai/artifact/CcPpBTxG9pDkheXbWm3ggR
  - このファイルは Artifact 用のソースで、`<!doctype>` と `<head>` は公開時に付きます。
  - 公開時は `proposal/img/` を `img/`、`wallpapers/r5-*` を `wallpapers/` として一緒に載せます（第5稿の「実寸の画像」のリンク先）。

## 第6稿（11月3日）：まず、見やすく

「なんか見づらい」という声を受けて、壁紙を作り直すのをやめ、見づらさの原因から組み直した。
第5稿までは、アイコンがどれも同じ灰色のガラスで見分けにくく、アプリが画面のまん中に小さく固まり、開いた右ページは空っぽだった。

やめた前提と、第6稿でどうしたか：

| これまで | 第6稿 |
|---|---|
| 壁紙の絵で個性を出す | 壁紙は無地の1色（墨＝ほぼ黒、または生成り＝明るい色）。iPhone の「カラー」で選べる |
| アイコンをクリアや1色にそろえる | 標準のカラーアイコン。色で探せる |
| 指が届かない左側は景色のために空ける | 届かない所には見るだけのもの（上に日付・天気、左下に柴の写真）。アプリは親指が届く右下に4つ |
| 開いた右ページは壁紙だけ | 特大ウィジェットで柴の写真か今日の予定を1枚 |

- 配置：Dock①〜④（右端）、P1右下⑤〜⑧、P1上にカレンダー（小）と天気（小）、P1左下に写真（小）、P2に特大ウィジェット
- 生成りの場合：アプリ名は白い文字で明るい背景では読めないため、アイコンを「大」にして名前を消す前提
- 第5稿までの絵は、アイコンが並ばないロック画面で使える（「ホーム画面をカスタマイズ」→「カラー」で、ロック画面は絵・ホーム画面は無地の1組にする）
- 壁紙：`wallpapers/r6-sumi_*`（墨 #1C1B1A）と `wallpapers/r6-kinari_*`（生成り #E9E4DA）。外側 `*_outer_1398x2034.jpg`、内側 `*_inner_2670x1878.jpg`

## 第5稿（11月3日）：開くと続きが見える、2枚1組の壁紙

Duo の壁紙は外側（閉じたとき）と内側（開いたとき）の2枚で1組。第5稿では2枚を同じ写真の切り抜きにせず、閉じた絵の「続き」を開いた絵に描いた。
アイコンが並ぶ右側はどの絵も暗く落ち着いた色にして、白い文字が読めるようにしている（青は使わない）。

| 案 | 閉じたとき（外側） | 開いたとき（内側） |
|---|---|---|
| 障子の影 | 月明かりの障子に柴の影と紅葉の影 | 障子が開き、縁側で満月を見上げる柴。右ページは閉じたままの障子で、枠が折り目に重なる |
| 満ちる月 | 三日月（暗い部分に地球照）とすすき | 満月と、すすきの野原 |
| 夜明けの砂丘 | 夜明け前の砂丘と明けの明星 | 地平線からのぼる朝日と、手前に伸びる長い影 |
| 表紙と見返し | 焦茶の布張りの表紙に、三日月と柴の金の箔押し | 金の筋が入った墨流しの見返し。中央に綴じ目の影 |

- 壁紙：`wallpapers/r5-*_outer_1398x2034.jpg`（外側）と `wallpapers/r5-*_inner_2670x1878.jpg`（内側）の4組8枚。ページ用の縮小版は `proposal/img/r5-*.jpg`
- 作り方：`tools/r5/` の Python スクリプト（numpy と Pillow）で描画。手順は `tools/r5/README.md`
- 素材：月の表面は NASA's Scientific Visualization Studio「CGI Moon Kit」（パブリックドメイン、https://svs.gsfc.nasa.gov/4720 ）。障子・紅葉・すすき・砂丘・布・墨流しはすべてコードで描いたもの

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

提案書の最後にある5つの質問（まだ見づらいところ、背景の色、開いた右ページ、ロック画面の絵、使う順のアプリ）に答えてもらい、
アプリ名入りの配置図・背景色とロック画面の組み合わせ・StandBy の合わせ方を作る。
