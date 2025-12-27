#!/usr/bin/env python3
"""
日本オリジナル作品の正確な判定分析 v2
「日本オリジナル」タグはAPI内部タグであり、作品のtagフィールドには含まれない
"""

import json
import requests
import time
import pandas as pd
from pathlib import Path

def fetch_japanese_original_ids():
    """日本オリジナルタグの作品IDを全て取得"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
    })
    
    all_ids = set()
    page = 1
    
    while True:
        print(f"日本オリジナルタグ作品取得中: ページ {page}...")
        url = f"https://www.reelshort.com/api/video/book/getTagBook?tag_id=67525ca75dc67bc7ba0ce69f&page={page}&page_size=100&language=ja"
        
        try:
            resp = session.get(url, timeout=30)
            data = resp.json()
            
            if data.get('code') != 0:
                break
            
            books = data['data'].get('books', [])
            if not books:
                break
            
            for book in books:
                book_id = book.get('book_id', book.get('_id'))
                all_ids.add(book_id)
            
            total = data['data'].get('total_items', 0)
            if len(all_ids) >= total:
                break
            
            page += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"エラー: {e}")
            break
    
    print(f"日本オリジナルタグ作品: {len(all_ids)}件")
    return all_ids


def analyze_all_books(base_dir: Path, jp_original_ids: set):
    """全作品を分析"""
    
    # 詳細データを読み込み
    detailed_file = base_dir / 'all_movies_detailed_100.json'
    if detailed_file.exists():
        with open(detailed_file, 'r', encoding='utf-8') as f:
            detailed_books = json.load(f)
    else:
        detailed_books = []
    
    results = []
    
    for book in detailed_books:
        book_id = book.get('book_id', book.get('_id', ''))
        t_book_id = str(book.get('t_book_id', ''))
        
        # 判定方法
        is_jp_original_tag = book_id in jp_original_ids
        is_jp_t_book_id = t_book_id.startswith('14000000000000')
        is_lang_ja = book.get('lang') == 'ja'
        
        # 国タグ
        country = ''
        for t in book.get('tag_list', []):
            if t.get('category_id') == '1013':
                country = t.get('text', '')
                break
        
        is_country_japan = country == '日本'
        
        # book_source
        book_source = book.get('book_source', '')
        
        row = {
            'book_id': book_id,
            't_book_id': t_book_id,
            'book_title': book.get('book_title', ''),
            'lang': book.get('lang', ''),
            'book_source': book_source,
            'country': country,
            'tags': '|'.join(book.get('tag', [])),
            
            # 判定結果
            '判定A_日本オリジナルタグ': '○' if is_jp_original_tag else '×',
            '判定B_t_book_id_14000': '○' if is_jp_t_book_id else '×',
            '判定C_lang_ja': '○' if is_lang_ja else '×',
            '判定D_国タグ日本': '○' if is_country_japan else '×',
            
            # 総合判定
            'タグで日本オリジナル': is_jp_original_tag,
            'ID形式で日本向け': is_jp_t_book_id,
            '日本語版': is_lang_ja,
            '撮影地が日本': is_country_japan,
        }
        
        results.append(row)
    
    return pd.DataFrame(results)


def create_analysis_excel(df: pd.DataFrame, jp_original_ids: set, output_file: str):
    """分析結果をExcelに出力"""
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # シート1: サマリー
        summary = {
            '項目': [
                '調査対象作品数',
                '',
                '【判定A】日本オリジナルタグ（API内部タグ）',
                '【判定B】t_book_id が 14000... 形式',
                '【判定C】lang == "ja"',
                '【判定D】撮影地が「日本」',
                '',
                '日本オリジナルタグ総数（全作品対象）',
            ],
            '件数': [
                len(df),
                '',
                len(df[df['判定A_日本オリジナルタグ'] == '○']),
                len(df[df['判定B_t_book_id_14000'] == '○']),
                len(df[df['判定C_lang_ja'] == '○']),
                len(df[df['判定D_国タグ日本'] == '○']),
                '',
                len(jp_original_ids),
            ],
            '説明': [
                '詳細情報を取得した作品',
                '',
                '日本市場向けオリジナル制作/ローカライズ作品',
                '日本向けコンテンツID形式',
                '日本語版（吹き替え含む）',
                '撮影地が日本の作品',
                '',
                'getTagBookで取得可能な全作品',
            ]
        }
        pd.DataFrame(summary).to_excel(writer, sheet_name='サマリー', index=False)
        
        # シート2: 判定結果の解説
        explanation = {
            '判定方法': [
                '判定A: 日本オリジナルタグ',
                '判定B: t_book_id 形式',
                '判定C: lang == ja',
                '判定D: 撮影地タグ',
            ],
            '意味': [
                'API内部で「日本オリジナル」タグが付与された作品',
                '日本向け配信用のID形式（14000...）',
                '日本語でローカライズされた作品（吹き替え含む）',
                'tag_listの国情報が「日本」',
            ],
            '判定できる内容': [
                '日本市場向けにローカライズ/制作された作品',
                '日本向けに配信されている作品',
                '日本語で視聴可能な作品',
                '撮影地が日本の作品（ほとんどない）',
            ],
            '注意点': [
                '作品のtagフィールドには含まれない。APIフィルタ用。',
                'ほぼ全ての日本語版作品がこの形式',
                '海外作品の吹き替えも含まれる',
                'ほとんどがアメリカ/イギリス撮影',
            ],
            '推奨度': [
                '★★★★★ 最も信頼できる',
                '★★★★☆ 広範囲だが正確',
                '★★★☆☆ 吹き替え含むため広すぎ',
                '★☆☆☆☆ 該当ほぼなし',
            ]
        }
        pd.DataFrame(explanation).to_excel(writer, sheet_name='判定方法の解説', index=False)
        
        # シート3: 全データ
        df.to_excel(writer, sheet_name='全データ', index=False)
        
        # シート4: 国タグの分布
        country_dist = df['country'].value_counts().reset_index()
        country_dist.columns = ['国', '件数']
        country_dist.to_excel(writer, sheet_name='撮影地分布', index=False)
        
        # シート5: book_source の分布
        source_dist = df['book_source'].value_counts().reset_index()
        source_dist.columns = ['book_source', '件数']
        source_dist.to_excel(writer, sheet_name='book_source分布', index=False)
        
        # シート6: 判定不一致の作品
        # 日本オリジナルタグがあるが国タグが日本でない
        mismatch = df[
            (df['判定A_日本オリジナルタグ'] == '○') & 
            (df['判定D_国タグ日本'] == '×')
        ].copy()
        mismatch.to_excel(writer, sheet_name='日本オリジナルだが撮影地は海外', index=False)
    
    print(f"\nExcel保存: {output_file}")


def main():
    base_dir = Path(__file__).parent
    
    print("=" * 60)
    print("日本オリジナル作品 判定方法の詳細分析 v2")
    print("=" * 60)
    
    # 1. 日本オリジナルタグの作品IDを取得
    jp_original_ids = fetch_japanese_original_ids()
    
    # IDを保存
    with open(base_dir / 'japanese_original_ids.json', 'w') as f:
        json.dump(list(jp_original_ids), f)
    
    # 2. 全作品を分析
    print("\n全作品を分析中...")
    df = analyze_all_books(base_dir, jp_original_ids)
    
    # 3. Excelに出力
    output_file = base_dir / 'japanese_detection_analysis_v2.xlsx'
    create_analysis_excel(df, jp_original_ids, str(output_file))
    
    # 4. 結論を表示
    print("\n" + "=" * 60)
    print("【結論】日本オリジナル作品の判定方法")
    print("=" * 60)
    print("""
┌─────────────────────────────────────────────────────────┐
│ 推奨判定方法                                            │
├─────────────────────────────────────────────────────────┤
│ 1. 日本オリジナルタグ（API内部）                       │
│    → getTagBook API で tag_id=67525ca75dc67bc7ba0ce69f │
│    → 最も信頼できる（日本市場向け制作/ローカライズ）   │
│                                                         │
│ 2. t_book_id が 14000... で始まる                      │
│    → 日本向け配信ID                                    │
│    → ほぼ同じ結果だが、よりプログラム的に判定しやすい │
├─────────────────────────────────────────────────────────┤
│ 注意事項                                                │
├─────────────────────────────────────────────────────────┤
│ • lang == "ja" は日本語版であり、海外吹き替え含む      │
│ • 撮影地タグは ほぼアメリカ（日本撮影はほぼなし）      │
│ • 「日本オリジナル」タグは作品のtagには含まれない      │
└─────────────────────────────────────────────────────────┘
""")


if __name__ == "__main__":
    main()

