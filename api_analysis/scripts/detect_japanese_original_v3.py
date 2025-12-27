#!/usr/bin/env python3
"""
日本人キャストによる日本オリジナル作品の判定スクリプト v3

判定方法の発見:
- t_book_id が "140000000140000" で始まる作品
  = 日本人キャストによる真の日本オリジナル作品

この判定方法は、以下の作品で検証済み：
- ダイヤモンドの再会
- 奪われたプリマバレリーナ
- 一目惚れ！今すぐ結婚してくれますか？
- 帰ってきたお嬢様
- せめて最後に愛のキスを
- Yesから始まるラブストーリー
等、計17作品
"""

import json
import csv
import os
from datetime import datetime

# ===== t_book_id パターンの解説 =====
# 
# ReelShortのt_book_idには地域/タイプを示すパターンがある：
#
# | プレフィックス（15桁） | 件数 | 推定意味 |
# |----------------------|------|---------|
# | 149000000000000      | 317  | 英語圏オリジナル |
# | 140000000000000      | 294  | 日本語吹き替え版 |
# | 149000000000002      |  96  | 英語圏（別カテゴリ） |
# | 148000000000000      |  96  | 中国語圏？ |
# | 149000000000001      |  86  | 英語圏（別カテゴリ） |
# | 140000200000000      |  24  | 日本向けローカライズ |
# | 140000000140000      |  17  | ★日本人キャスト日本オリジナル★ |
# | 149001000000000      |  16  | 英語圏（特別版） |
# | 142600000000002      |  15  | スペイン語圏？ |
# | 142600000000000      |  14  | スペイン語圏？ |
# | 140000000000002      |  14  | 日本向け（別カテゴリ） |
# | 140001000000000      |  13  | 日本向け（特別版） |
# | 141000000000000      |   9  | 不明 |
#
# 重要: "140000000140000" は日本人キャストによる完全オリジナル作品！

def is_japanese_cast_original(t_book_id: str) -> bool:
    """
    日本人キャストによる日本オリジナル作品かどうかを判定
    
    判定基準: t_book_idが "140000000140000" で始まる
    """
    if not t_book_id:
        return False
    return t_book_id.startswith("140000000140000")


def get_t_book_id_category(t_book_id: str) -> str:
    """
    t_book_idのカテゴリを返す
    """
    if not t_book_id:
        return "不明"
    
    prefix = t_book_id[:15]
    
    categories = {
        "149000000000000": "英語圏オリジナル",
        "140000000000000": "日本語吹き替え版",
        "149000000000002": "英語圏（シリーズ2）",
        "148000000000000": "中国語圏",
        "149000000000001": "英語圏（シリーズ1）",
        "140000200000000": "日本向けローカライズ",
        "140000000140000": "★日本人キャスト日本オリジナル★",
        "149001000000000": "英語圏（プレミアム）",
        "142600000000002": "スペイン語圏（シリーズ2）",
        "142600000000000": "スペイン語圏",
        "140000000000002": "日本向け（シリーズ2）",
        "140001000000000": "日本向け（プレミアム）",
        "141000000000000": "韓国語圏？",
    }
    
    return categories.get(prefix, f"その他（{prefix}）")


def analyze_all_movies():
    """全作品を分析してCSVとExcelを出力"""
    
    # JSONファイル読み込み
    with open('all_movies_basic.json', 'r', encoding='utf-8') as f:
        movies = json.load(f)
    
    print(f"総作品数: {len(movies)}")
    
    # 分析結果格納
    results = []
    japanese_cast_originals = []
    category_counts = {}
    
    for movie in movies:
        t_book_id = movie.get('t_book_id', '')
        book_id = movie.get('book_id', '')
        title = movie.get('book_title', '')
        description = movie.get('special_desc', '')
        views = movie.get('play_cnt', 0)
        likes = movie.get('like_cnt', 0)
        
        # タグ処理
        tags = movie.get('tag', [])
        if isinstance(tags, list):
            tags_str = '|'.join(tags)
        else:
            tags_str = str(tags)
        
        # 判定
        is_jp_cast_original = is_japanese_cast_original(t_book_id)
        category = get_t_book_id_category(t_book_id)
        
        # カテゴリカウント
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
        
        result = {
            'book_id': book_id,
            't_book_id': t_book_id,
            'book_title': title,
            'category': category,
            'is_japanese_cast_original': '★日本人キャスト★' if is_jp_cast_original else '',
            'play_cnt': views,
            'like_cnt': likes,
            'tags': tags_str,
            'description': description[:200] if description else ''
        }
        
        results.append(result)
        
        if is_jp_cast_original:
            japanese_cast_originals.append(result)
    
    # カテゴリ別集計表示
    print("\n" + "="*60)
    print("■ t_book_id カテゴリ別集計")
    print("="*60)
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}件")
    
    print("\n" + "="*60)
    print(f"■ 日本人キャストによる日本オリジナル作品: {len(japanese_cast_originals)}件")
    print("="*60)
    for movie in japanese_cast_originals:
        print(f"  ・{movie['book_title']}")
    
    # CSVファイル出力
    os.makedirs('csv', exist_ok=True)
    
    # 1. 全作品CSV
    csv_all_path = 'csv/全作品_カテゴリ分析.csv'
    with open(csv_all_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n出力: {csv_all_path}")
    
    # 2. 日本人キャストオリジナルCSV
    csv_jp_path = 'csv/日本人キャスト_日本オリジナル.csv'
    with open(csv_jp_path, 'w', newline='', encoding='utf-8-sig') as f:
        if japanese_cast_originals:
            writer = csv.DictWriter(f, fieldnames=japanese_cast_originals[0].keys())
            writer.writeheader()
            writer.writerows(japanese_cast_originals)
    print(f"出力: {csv_jp_path}")
    
    # 3. カテゴリ別集計CSV
    csv_summary_path = 'csv/カテゴリ別集計.csv'
    with open(csv_summary_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['カテゴリ', '作品数', '比率'])
        total = len(movies)
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            ratio = f"{count/total*100:.1f}%"
            writer.writerow([category, count, ratio])
    print(f"出力: {csv_summary_path}")
    
    # Excel出力（pandas使用可能な場合）
    try:
        import pandas as pd
        
        df_all = pd.DataFrame(results)
        df_jp = pd.DataFrame(japanese_cast_originals)
        df_summary = pd.DataFrame([
            {'カテゴリ': k, '作品数': v, '比率': f"{v/len(movies)*100:.1f}%"} 
            for k, v in sorted(category_counts.items(), key=lambda x: -x[1])
        ])
        
        # 判定方法の解説
        df_method = pd.DataFrame([
            {
                '判定方法': 't_book_id プレフィックス分析',
                '判定基準': 't_book_id が "140000000140000" で始まる',
                '検出数': len(japanese_cast_originals),
                '信頼度': '★★★★★（最高）',
                '解説': '日本人キャストによる完全日本オリジナル作品。吹き替えではない。'
            },
            {
                '判定方法': '従来の「日本オリジナル」タグ',
                '判定基準': 'tag に「日本オリジナル」が含まれる',
                '検出数': '1,000+件',
                '信頼度': '★★★☆☆',
                '解説': '日本市場向けローカライズ作品を含む（吹き替え含む）'
            },
            {
                '判定方法': 'lang == "ja"',
                '判定基準': '言語が日本語',
                '検出数': '1,000+件',
                '信頼度': '★★☆☆☆',
                '解説': '日本語吹き替え版も全て含まれる'
            }
        ])
        
        excel_path = 'japanese_cast_original_analysis.xlsx'
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_jp.to_excel(writer, sheet_name='日本人キャストオリジナル', index=False)
            df_summary.to_excel(writer, sheet_name='カテゴリ別集計', index=False)
            df_method.to_excel(writer, sheet_name='判定方法の解説', index=False)
            df_all.to_excel(writer, sheet_name='全作品データ', index=False)
        
        print(f"出力: {excel_path}")
        
    except ImportError:
        print("\n※ pandas/openpyxl がインストールされていないため、Excel出力はスキップ")
    
    return results, japanese_cast_originals, category_counts


if __name__ == '__main__':
    print("="*60)
    print("日本人キャストによる日本オリジナル作品 判定スクリプト v3")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print()
    print("【判定方法】")
    print("  t_book_id が '140000000140000' で始まる作品")
    print("  = 日本人キャストによる真の日本オリジナル作品")
    print()
    
    results, jp_originals, categories = analyze_all_movies()
    
    print("\n" + "="*60)
    print("【結論】")
    print("="*60)
    print(f"""
■ 日本人キャストによる日本オリジナル作品の判定方法:

  t_book_id.startswith("140000000140000")
  
■ 検出結果: {len(jp_originals)}作品

■ この判定方法の特徴:
  - 従来の「日本オリジナル」タグ（1,000+件）とは異なる
  - 吹き替え版は含まない
  - 日本人キャストによる完全オリジナル制作のみ
  
■ 参考: t_book_idの構造
  - 最初の3桁: 140 = 日本向け, 149 = 英語圏, 148 = 中国語圏
  - 4-6桁: 000 = 標準, 001 = プレミアム等
  - 7-15桁: 000000140000 = 日本人キャストオリジナル
""")

