# 学生 Android アプリ

Tomoshibi 学生端の Android 実装（Kotlin + Jetpack Compose）。機能・画面は iOS 学生端に揃える方針。

| ファイル / ディレクトリ | 役割 |
|---|---|
| `ANDROID_DESIGN_LOG.md` | Android 専属の設計決定アーカイブ |
| `v1/` | Kotlin + Compose 実装本体（Gradle プロジェクト）|

## v1/ 構成

| パス | 役割 |
|---|---|
| `app/src/main/java/jp/tomoshibi/android/MainActivity.kt` | エントリポイント |
| `.../TomoshibiApp.kt` | アプリ骨格 |
| `.../ui/` | 各画面（Compose）— ホーム / 点呼 / 申請 / お知らせ など |
| `.../nav/` | 画面遷移（Navigation）|
| `.../data/` | データ層（API クライアント / モデル）|

## ビルド

```
cd v1 && ./gradlew assembleDebug
```

## 関連文書

- 共用機能マトリクス（source of truth）: `../../design/system_features.md`
- iOS 対応実装（視覚・機能の基準）: `../student_ios/`
