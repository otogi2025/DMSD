# 教師用 Web ダッシュボード

Tomoshibi 教師端の Web アプリ（React + TypeScript + Vite）。iPad ブラウザでの利用を想定。Ryō 風スタイル。

| ファイル / ディレクトリ | 役割 |
|---|---|
| `WEB_DESIGN_LOG.md` | Web 専属の設計決定アーカイブ |
| `DESIGN_BRIEF.md` | デザイン方針 |
| `v1/` | React + TS + Vite 実装本体 |

## v1/src/ 構成

| パス | 役割 |
|---|---|
| `App.tsx` / `Shell.tsx` | アプリ骨格・レイアウト |
| `components/` | 各画面コンポーネント（点呼 / 指導 / 事案 / 行事 / 前台 など）|
| `api/` | バックエンド API クライアント |
| `theme.ts` / `styles.css` | Ryō 風テーマ |

## ビルド

```
cd v1 && npm install && npm run build
```

## 関連文書

- 共用機能マトリクス（source of truth）: `../../design/system_features.md`
- バックエンド API: `../backend/v1/`
