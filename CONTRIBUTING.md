# Contributing Guide / 貢献ガイド

このガイドでは、新しい山やモデルコースを追加する方法を説明します。

This guide explains how to add new mountains and model courses to the repository.

## ディレクトリ命名規則 (Directory Naming Convention)

各山のディレクトリは以下の形式で作成してください：

```
mountains/{ID}_{日本語名}_{Romaji名}/
```

例 (Examples):
- `001_利尻山_Rishiri-zan/`
- `072_富士山_Fuji-san/`
- `054_槍ヶ岳_Yari-ga-take/`

## 新しい山を追加する (Adding a New Mountain)

### 1. ディレクトリを作成 (Create Directory)

```bash
mkdir -p "mountains/{ID}_{日本語名}_{Romaji名}"
```

### 2. README.mdを作成 (Create README.md)

以下のテンプレートを使用してください：

```markdown
# {日本語名} ({Romaji名})

**標高 (Elevation):** {標高}m  
**所在地 (Location):** {都道府県} ({Prefecture in English})  
**緯度経度 (Coordinates):** {緯度}°N, {経度}°E

## 概要 (Overview)
{山の説明}

## モデルコース (Model Courses)

### コース1: {コース名} ({Course Name in English})
- **難易度 (Difficulty):** {初級/中級/上級} ({Beginner/Intermediate/Advanced})
- **所要時間 (Duration):** {時間} ({hours in English})
- **距離 (Distance):** 約{数値}km (Approx. {数値}km)
- **標高差 (Elevation Gain):** 約{数値}m (Approx. {数値}m)
- **GPXファイル (GPX File):** `{ファイル名}.gpx`

#### コース詳細 (Course Details)
1. {地点名} ({Place Name in English}) - 標高{標高}m
2. {地点名} ({Place Name in English}) - 標高{標高}m
...

## 注意事項 (Notes)
- {注意点1}
- {注意点2}
...
```

### 3. GPXファイルを作成 (Create GPX File)

GPX 1.1形式で作成してください。テンプレート：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="YMAP_TOP100_MOUNTAIN_JAPAN"
     xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>{山名} {コース名} ({Mountain Name Course Name})</name>
    <desc>{コースの説明}</desc>
    <author>
      <name>YMAP TOP100 MOUNTAIN JAPAN</name>
    </author>
    <time>{作成日時 YYYY-MM-DDTHH:MM:SSZ}</time>
  </metadata>
  <trk>
    <name>{コース名}</name>
    <desc>{コース説明}</desc>
    <trkseg>
      <!-- トラックポイントを追加 -->
      <trkpt lat="{緯度}" lon="{経度}">
        <ele>{標高}</ele>
        <name>{地点名}</name>
      </trkpt>
      <!-- さらにポイントを追加 -->
    </trkseg>
  </trk>
</gpx>
```

## GPXデータの収集方法 (How to Collect GPX Data)

### 実際に登山して記録する (Record During Actual Hiking)
1. GPS対応の登山アプリを使用（YAMAP, ヤマレコ, etc.）
2. 登山中にGPSトラッキングをON
3. 下山後にGPXファイルをエクスポート

### 既存のデータを参考にする (Reference Existing Data)
1. YAMAP、ヤマレコなどの公開されているルート情報を参考
2. 国土地理院の地図データを使用
3. **注意**: 他人のGPXデータをそのまま使用する場合は、ライセンスと著作権を確認してください

### GPXファイルの編集ツール (GPX Editing Tools)
- [GPX Editor](https://www.gpxeditor.co.uk/) - オンラインエディタ
- [Viking](https://sourceforge.net/projects/viking/) - デスクトップアプリ
- テキストエディタで直接編集も可能

## データ品質のガイドライン (Data Quality Guidelines)

### GPXファイル (GPX Files)
- トラックポイントは主要な地点（登山口、山小屋、分岐点、山頂など）を含める
- 標高データを正確に記録
- 地点名は日本語と英語の両方を含める（可能な場合）
- ファイルサイズを抑えるため、トラックポイントは適度に間引く

### README.md
- 難易度は客観的に評価（体力・技術レベルを考慮）
- 所要時間は一般的な登山者を想定
- 最新の登山道情報を反映
- 安全に関する重要な情報を必ず記載

## プルリクエストの作成 (Creating a Pull Request)

1. このリポジトリをフォーク
2. 新しいブランチを作成: `git checkout -b add-mountain-{山名}`
3. 変更をコミット: `git commit -m "Add {山名} with {コース数} courses"`
4. ブランチをプッシュ: `git push origin add-mountain-{山名}`
5. プルリクエストを作成

## レビュー基準 (Review Criteria)

プルリクエストは以下の点を確認します：

- [ ] ディレクトリ名が命名規則に従っている
- [ ] README.mdに必要な情報が含まれている
- [ ] GPXファイルが有効なXML形式である
- [ ] GPXファイルにメタデータとトラックポイントが含まれている
- [ ] 日本語と英語の両方で情報が提供されている（可能な限り）
- [ ] mountains.jsonの該当エントリと一致している

## ヘルプ (Help)

質問や提案がある場合は、Issueを作成してください。

If you have questions or suggestions, please create an Issue.

## ライセンス (License)

貢献したコンテンツはMITライセンスの下で公開されることに同意するものとします。

By contributing, you agree that your contributions will be licensed under the MIT License.
