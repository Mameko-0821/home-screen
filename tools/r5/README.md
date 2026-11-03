# 第5稿の壁紙を描くスクリプト

numpy と Pillow だけで、第5稿の4組（8枚）を描きます。出力は `out/` に入り、`export.py` でリポジトリへ書き出します。

```bash
cd tools/r5
python3 shoji.py          # 障子の影   → out/shoji_outer.jpg, out/shoji_inner.jpg
python3 moon.py           # 満ちる月   → out/tsuki_*.jpg（初回は NASA の月の地図を cache/ に取得）
python3 dunes.py          # 夜明けの砂丘 → out/sakyu_*.jpg（内側は数分かかります）
python3 book.py           # 表紙と見返し → out/hon_*.jpg
python3 export.py shoji tsuki sakyu hon
```

- `lib.py`：色の変換、ぼかし、ノイズ、図形の描画、粒子（フィルムグレイン）
- `shiba_path.py`：座った柴の横顔のシルエット（障子の影と表紙の箔押しで共通）
- `moon.py`：月は NASA SVS「CGI Moon Kit」の色地図（パブリックドメイン）を正射影で球に貼り、満ち欠けの光を当てています
- `dunes.py`：砂丘は高さの関数から、奥行き方向の走査で見える面を求め、太陽への影の光線と大気の霞をつけています
- 位置や明るさは各スクリプトの `make*` 関数の数字で調整できます（外側は右半分にアイコンが並ぶので、主役は左半分に置いています）
