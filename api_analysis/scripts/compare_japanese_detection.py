#!/usr/bin/env python3
"""
日本オリジナル判定方法の比較スクリプト
複数の判定方法で日本オリジナルかどうかを判定し、Excelで比較できるようにします。
"""

import json
import pandas as pd
from pathlib import Path
import requests
import time
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

# 判定方法の定義
DETECTION_METHODS = {
    'method1_tag': '「日本オリジナル」タグ',
    'method2_t_book_id': 't_book_id が 14000... で始まる',
    'method3_lang_ja': 'lang == "ja"',
    'method4_country_japan': 'tag_list内の国が「日本」',
    'method5_book_source': 'book_source の値',
}


def detect_japanese_original(book: dict) -> dict:
    """複数の方法で日本オリジナルかどうかを判定"""
    results = {}
    
    # 方法1: タグに「日本オリジナル」が含まれる
    tags = book.get('tag', [])
    results['method1_tag'] = '日本オリジナル' in tags if isinstance(tags, list) else False
    
    # 方法2: t_book_id が 14000... で始まる（日本向けID）
    t_book_id = str(book.get('t_book_id', ''))
    results['method2_t_book_id'] = t_book_id.startswith('14000000000000')
    
    # 方法3: lang が "ja"
    lang = book.get('lang', '')
    results['method3_lang_ja'] = lang == 'ja'
    
    # 方法4: tag_list内の国情報が「日本」
    tag_list = book.get('tag_list', [])
    country_tags = [t.get('text', '') for t in tag_list 
                   if isinstance(t, dict) and t.get('category_id') == '1013']
    results['method4_country_japan'] = '日本' in country_tags
    results['country_value'] = '|'.join(country_tags) if country_tags else ''
    
    # 方法5: book_source の値
    book_source = book.get('book_source', '')
    results['method5_book_source'] = book_source
    
    return results


def fetch_detailed_info(book_ids: list, max_count: int = 100) -> list:
    """作品の詳細情報を取得"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })
    
    detailed_books = []
    
    for i, book_id in enumerate(book_ids[:max_count]):
        print(f"詳細取得中: {i+1}/{min(len(book_ids), max_count)}")
        
        url = f"https://www.reelshort.com/api/video/book/getBookInfo?book_id={book_id}&language=ja"
        try:
            response = session.get(url, timeout=30)
            data = response.json()
            if data.get('code') == 0:
                detailed_books.append(data.get('data', {}))
        except Exception as e:
            print(f"エラー: {e}")
        
        time.sleep(0.5)  # レート制限対策
    
    return detailed_books


def create_comparison_excel(books: list, output_file: str):
    """判定結果を比較するExcelファイルを作成"""
    
    # 各判定方法の結果を収集
    all_results = []
    
    for book in books:
        detection = detect_japanese_original(book)
        
        row = {
            'book_id': book.get('book_id', book.get('_id', '')),
            't_book_id': book.get('t_book_id', ''),
            'book_title': book.get('book_title', ''),
            'lang': book.get('lang', ''),
            'book_source': book.get('book_source', ''),
            'tags': '|'.join(book.get('tag', [])) if isinstance(book.get('tag'), list) else '',
            'country': detection.get('country_value', ''),
            'method1_日本オリジナルタグ': '○' if detection['method1_tag'] else '×',
            'method2_t_book_id_14000': '○' if detection['method2_t_book_id'] else '×',
            'method3_lang_ja': '○' if detection['method3_lang_ja'] else '×',
            'method4_国タグ日本': '○' if detection['method4_country_japan'] else '×',
            'method5_book_source': detection['method5_book_source'],
        }
        
        # 判定一致数
        matches = sum([
            detection['method1_tag'],
            detection['method2_t_book_id'],
            detection['method3_lang_ja'],
            detection['method4_country_japan'],
        ])
        row['判定一致数'] = matches
        
        all_results.append(row)
    
    # DataFrameに変換
    df_all = pd.DataFrame(all_results)
    
    # 各判定方法でフィルタリング
    df_method1 = df_all[df_all['method1_日本オリジナルタグ'] == '○'].copy()
    df_method2 = df_all[df_all['method2_t_book_id_14000'] == '○'].copy()
    df_method3 = df_all[df_all['method3_lang_ja'] == '○'].copy()
    df_method4 = df_all[df_all['method4_国タグ日本'] == '○'].copy()
    
    # 判定が分かれる作品（一部の方法でのみ日本と判定）
    df_mismatch = df_all[(df_all['判定一致数'] > 0) & (df_all['判定一致数'] < 4)].copy()
    
    # Excelファイル作成
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # シート1: 全データ
        df_all.to_excel(writer, sheet_name='全データ', index=False)
        
        # シート2: サマリー統計
        summary_data = {
            '判定方法': [
                '方法1: 日本オリジナルタグ',
                '方法2: t_book_id 14000...',
                '方法3: lang == ja',
                '方法4: 国タグが日本',
                '全方法一致（4/4）',
                '一部一致（1-3/4）',
                '全方法不一致（0/4）',
            ],
            '該当件数': [
                len(df_method1),
                len(df_method2),
                len(df_method3),
                len(df_method4),
                len(df_all[df_all['判定一致数'] == 4]),
                len(df_all[(df_all['判定一致数'] > 0) & (df_all['判定一致数'] < 4)]),
                len(df_all[df_all['判定一致数'] == 0]),
            ],
            '全体比率': [
                f"{len(df_method1)/len(df_all)*100:.1f}%",
                f"{len(df_method2)/len(df_all)*100:.1f}%",
                f"{len(df_method3)/len(df_all)*100:.1f}%",
                f"{len(df_method4)/len(df_all)*100:.1f}%",
                f"{len(df_all[df_all['判定一致数'] == 4])/len(df_all)*100:.1f}%",
                f"{len(df_all[(df_all['判定一致数'] > 0) & (df_all['判定一致数'] < 4)])/len(df_all)*100:.1f}%",
                f"{len(df_all[df_all['判定一致数'] == 0])/len(df_all)*100:.1f}%",
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='サマリー', index=False)
        
        # シート3-6: 各判定方法の結果
        df_method1.to_excel(writer, sheet_name='方法1_日本オリジナルタグ', index=False)
        df_method2.to_excel(writer, sheet_name='方法2_t_book_id', index=False)
        df_method3.to_excel(writer, sheet_name='方法3_lang_ja', index=False)
        df_method4.to_excel(writer, sheet_name='方法4_国タグ日本', index=False)
        
        # シート7: 判定が分かれる作品
        df_mismatch.to_excel(writer, sheet_name='判定不一致', index=False)
        
        # book_source の値一覧
        source_counts = df_all['method5_book_source'].value_counts().reset_index()
        source_counts.columns = ['book_source値', '件数']
        source_counts.to_excel(writer, sheet_name='book_source分析', index=False)
    
    print(f"Excelファイルを保存: {output_file}")
    
    # サマリー表示
    print("\n" + "=" * 60)
    print("判定結果サマリー")
    print("=" * 60)
    print(f"総作品数: {len(df_all)}")
    print(f"\n方法1（日本オリジナルタグ）: {len(df_method1)}件")
    print(f"方法2（t_book_id 14000...）: {len(df_method2)}件")
    print(f"方法3（lang == ja）: {len(df_method3)}件")
    print(f"方法4（国タグ日本）: {len(df_method4)}件")
    print(f"\n全方法一致: {len(df_all[df_all['判定一致数'] == 4])}件")
    print(f"判定不一致: {len(df_mismatch)}件")
    
    return df_all


def main():
    base_dir = Path(__file__).parent
    
    print("=" * 60)
    print("日本オリジナル判定方法の比較")
    print("=" * 60)
    
    # 既存の詳細データを読み込む
    detailed_file = base_dir / 'all_movies_detailed_sample.json'
    
    if detailed_file.exists():
        print(f"\n既存の詳細データを読み込み: {detailed_file}")
        with open(detailed_file, 'r', encoding='utf-8') as f:
            detailed_books = json.load(f)
        print(f"読み込み件数: {len(detailed_books)}")
    else:
        detailed_books = []
    
    # 基本データから追加で詳細取得
    basic_file = base_dir / 'all_movies_basic.json'
    if basic_file.exists() and len(detailed_books) < 100:
        print(f"\n基本データから追加取得...")
        with open(basic_file, 'r', encoding='utf-8') as f:
            basic_books = json.load(f)
        
        # 既存IDを除外
        existing_ids = {b.get('book_id', b.get('_id')) for b in detailed_books}
        new_ids = [b.get('book_id', b.get('_id')) for b in basic_books 
                   if b.get('book_id', b.get('_id')) not in existing_ids]
        
        # 追加取得
        additional = fetch_detailed_info(new_ids, max_count=80)
        detailed_books.extend(additional)
        
        # 保存
        with open(base_dir / 'all_movies_detailed_100.json', 'w', encoding='utf-8') as f:
            json.dump(detailed_books, f, ensure_ascii=False, indent=2)
        print(f"詳細データを保存: {len(detailed_books)}件")
    
    # Excelファイル作成
    output_file = base_dir / 'japanese_detection_comparison.xlsx'
    create_comparison_excel(detailed_books, str(output_file))
    
    print("\n" + "=" * 60)
    print("完了！")
    print("=" * 60)
    print(f"出力ファイル: {output_file}")


if __name__ == "__main__":
    main()

