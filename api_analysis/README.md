# 🎬 ReelShort API分析プロジェクト

ReelShortの全作品データを取得・分析するプロジェクトです。

## 📁 ディレクトリ構造

```
api_analysis/
├── data/                    # 📊 メインデータファイル
│   ├── all_movies_basic.json      # 全作品の基本情報（1,026作品）
│   ├── all_movies_enriched.json   # 詳細情報付きデータ
│   ├── all_tags.json              # 全タグ一覧
│   └── japanese_original_movies.json  # 日本オリジナル作品
│
├── csv/                     # 📋 CSV形式データ
│   ├── all_movies_*.csv           # 全作品データ
│   ├── 日本人キャスト_*.csv       # 日本人キャスト関連
│   └── 判定分析_*.csv             # 判定分析結果
│
├── excel/                   # 📗 最新Excelファイル
│   ├── japanese_cast_ranking.xlsx        # 日本人キャストランキング
│   ├── reelshort_full_analysis.xlsx      # 全作品分析
│   ├── japanese_detection_comparison.xlsx # 判定方法比較
│   └── ReelShort_日本オリジナル_*.xlsx   # 日本オリジナル情報
│
├── notebooks/               # 📓 Jupyter Notebook
│   └── ReelShort_Analysis.ipynb  # メイン分析ノートブック
│
├── scripts/                 # 🐍 Pythonスクリプト
│   ├── fetch_all_movies.py        # データ取得
│   ├── visualize_all_data.py      # 可視化
│   ├── get_ranking.py             # ランキング生成
│   └── ...                        # その他分析スクリプト
│
├── docs/                    # 📚 ドキュメント
│   ├── ReelShort_API_Documentation.md  # API詳細ドキュメント
│   ├── API_Endpoints_QuickRef.md       # APIクイックリファレンス
│   └── API_ANALYSIS_REPORT.md          # 分析レポート
│
├── visualizations/          # 🖼️ 可視化画像
│   ├── reelshort_overview.png     # 概要グラフ
│   ├── reelshort_detailed.png     # 詳細グラフ
│   └── wordcloud_*.png            # ワードクラウド
│
├── archive/                 # 📦 アーカイブ（古いファイル）
│   ├── old_excel/                 # 古いExcelファイル
│   ├── old_json/                  # 中間JSONファイル
│   └── temp_scripts/              # 探索用スクリプト
│
└── venv/                    # 🔧 Python仮想環境
```

## 🚀 クイックスタート

### 1. Jupyter Notebookで分析
```bash
cd notebooks
jupyter notebook ReelShort_Analysis.ipynb
```

### 2. データ可視化の再生成
```bash
cd scripts
python3 visualize_all_data.py
```

### 3. 最新データの取得
```bash
cd scripts
python3 fetch_all_movies.py
```

## 📊 統計サマリー

| 項目 | 数値 |
|-----|------|
| 総作品数 | 1,026作品 |
| 総再生数 | 14.4億回 |
| 日本人キャスト作品 | 17作品 |
| 日本人キャスト総再生数 | 9,470万回 |

## 📌 日本人キャスト作品TOP5

1. **令嬢決戦！私こそが学園のクイーン** - 14.3M再生
2. **ダイヤモンドの再会** - 11.6M再生
3. **冷酷御曹司の愛妻計画** - 10.9M再生
4. **財閥令嬢様の二重生活** - 10.7M再生
5. **嫌いなアイツの専属メイド!?** - 9.1M再生

## 🔍 APIドキュメント

詳細なAPIドキュメントは `docs/ReelShort_API_Documentation.md` を参照してください。

## 📅 更新履歴

- 2025-12-25: 初期バージョン作成、ディレクトリ整理完了



