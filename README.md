# YMAP_TOP100_MOUNTAIN_JAPAN
GPS track for 日本百名山（にほんひゃくめいざん / 100 Famous Mountains of Japan）

## 概要 (Overview)

このリポジトリは、深田久弥によって選定された「日本百名山」の登山情報とGPXデータを整理したものです。各山について、主要な登山ルート（モデルコース）とそのGPXファイルを提供しています。

This repository organizes hiking information and GPX data for the "100 Famous Mountains of Japan" (日本百名山) selected by Kyūya Fukada. For each mountain, we provide information on major climbing routes (model courses) and their GPX files.

## プロジェクト構成 (Project Structure)

```
YMAP_TOP100_MOUNTAIN_JAPAN/
├── README.md                          # このファイル (This file)
├── mountains.json                     # 100名山の基本情報 (Basic information of 100 mountains)
└── mountains/                         # 各山のデータディレクトリ (Data directory for each mountain)
    ├── 001_利尻山_Rishiri-zan/
    │   ├── README.md                  # 山の詳細情報 (Detailed mountain information)
    │   └── oshidomari_course.gpx     # モデルコースGPX (Model course GPX)
    ├── 072_富士山_Fuji-san/
    │   ├── README.md
    │   ├── yoshida_route.gpx         # 吉田ルート
    │   └── fujinomiya_route.gpx      # 富士宮ルート
    └── 054_槍ヶ岳_Yari-ga-take/
        ├── README.md
        └── kamikochi_yarisawa_route.gpx
```

## 使い方 (Usage)

### 山の情報を探す (Find Mountain Information)

1. `mountains.json` で目的の山を検索
2. 対応する山のディレクトリ（例: `mountains/072_富士山_Fuji-san/`）を開く
3. `README.md` で登山ルートの詳細を確認
4. 必要なGPXファイルをダウンロード

### GPXファイルの利用 (Using GPX Files)

GPXファイルは以下のアプリケーション・サービスで利用できます：
- YAMAP（ヤマップ）
- ヤマレコ
- Garmin GPSデバイス
- Google Earth
- その他のGPS対応登山アプリ

## データ形式 (Data Format)

### mountains.json
全100座の基本情報を含むJSONファイル：
- 山名（日本語・ローマ字）
- 標高
- 所在地（都道府県）
- 位置座標（緯度・経度）

### 各山のディレクトリ
- `README.md`: 山の概要、モデルコース詳細、注意事項
- `*.gpx`: 各ルートのGPXトラックファイル

## 貢献 (Contributing)

このプロジェクトへの貢献を歓迎します！以下のような貢献が可能です：
- 新しいモデルコースの追加
- GPXデータの精度向上
- 登山情報の更新
- 翻訳の改善

詳細なガイドラインについては [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

For detailed contribution guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## ライセンス (License)

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください

## 免責事項 (Disclaimer)

このリポジトリの情報は参考用です。登山の際は最新の情報を確認し、十分な準備と装備を行ってください。登山は自己責任で行い、気象条件や体調を考慮して安全な判断をしてください。

The information in this repository is for reference only. When hiking, please check the latest information and make adequate preparations. Hiking is at your own risk, and please make safe decisions considering weather conditions and physical condition.
