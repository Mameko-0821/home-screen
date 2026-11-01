# home-screen

iPhone Duo のホーム画面デザインを考えるためのリポジトリ。

## 提案書

- `proposal/iphone-duo-home-screen.html` … 調査結果と5つのデザイン案（モックアップ付き）
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
