#!/usr/bin/env python3
"""
日本人キャスト日本オリジナル作品の全探索スクリプト

t_book_id: 140000000140000XXX のパターンで
XXX = 001 〜 300 までを探索して存在する作品を全て発見する
"""

import requests
import json
import time
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# API設定
BASE_URL = "https://www.reelshort.com/api/video/book/getBookInfo"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://www.reelshort.com/ja/'
}

# t_book_idのプレフィックス
PREFIX = "140000000140000"

def check_book(number: int) -> dict:
    """
    指定された番号でt_book_idを生成しAPIにアクセス
    """
    t_book_id = f"{PREFIX}{number:03d}"
    
    try:
        url = f"{BASE_URL}?book_id={t_book_id}&language=ja"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0 and data.get('data'):
                book_data = data['data']
                return {
                    'found': True,
                    'number': number,
                    't_book_id': t_book_id,
                    'book_id': book_data.get('book_id', ''),
                    'book_title': book_data.get('book_title', ''),
                    'special_desc': book_data.get('special_desc', '')[:150] if book_data.get('special_desc') else '',
                    'play_cnt': book_data.get('play_cnt', 0),
                    'like_cnt': book_data.get('like_cnt', 0),
                    'episode_cnt': book_data.get('episode_cnt', 0),
                    'tag': book_data.get('tag', []),
                    'cover': book_data.get('cover', ''),
                    'raw_data': book_data
                }
        
        return {'found': False, 'number': number, 't_book_id': t_book_id}
    
    except Exception as e:
        return {'found': False, 'number': number, 't_book_id': t_book_id, 'error': str(e)}


def scan_range(start: int, end: int, workers: int = 5):
    """
    指定範囲の番号をスキャン
    """
    found_books = []
    checked = 0
    total = end - start + 1
    
    print(f"\n{'='*60}")
    print(f"スキャン範囲: {PREFIX}{start:03d} 〜 {PREFIX}{end:03d}")
    print(f"総チェック数: {total}")
    print(f"{'='*60}\n")
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(check_book, num): num for num in range(start, end + 1)}
        
        for future in as_completed(futures):
            result = future.result()
            checked += 1
            
            if result['found']:
                found_books.append(result)
                print(f"✓ [{checked}/{total}] 発見! {result['t_book_id']}: {result['book_title']}")
            else:
                if checked % 20 == 0:
                    print(f"  [{checked}/{total}] スキャン中... 発見: {len(found_books)}件")
            
            # レート制限対策
            time.sleep(0.1)
    
    return found_books


def main():
    print("="*60)
    print("日本人キャスト日本オリジナル作品 全探索")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print(f"\n探索パターン: {PREFIX}XXX")
    print("XXX = 001 〜 300 を探索します")
    
    # スキャン実行（001〜300）
    all_found = scan_range(1, 300, workers=5)
    
    # 番号でソート
    all_found.sort(key=lambda x: x['number'])
    
    print(f"\n{'='*60}")
    print(f"■ スキャン完了！発見: {len(all_found)}作品")
    print("="*60)
    
    # 結果表示
    print("\n【発見した作品一覧】")
    print("-"*60)
    for i, book in enumerate(all_found, 1):
        print(f"{i:2}. [{book['t_book_id']}] {book['book_title']}")
        print(f"    再生数: {book['play_cnt']:,} / いいね: {book['like_cnt']:,}")
    
    # CSVに保存
    csv_path = 'csv/日本人キャスト_全探索結果.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['number', 't_book_id', 'book_id', 'book_title', 'play_cnt', 'like_cnt', 'episode_cnt', 'special_desc']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_found)
    print(f"\n出力: {csv_path}")
    
    # JSONに保存（詳細データ）
    json_path = 'japanese_cast_original_full.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump([book['raw_data'] for book in all_found if 'raw_data' in book], f, ensure_ascii=False, indent=2)
    print(f"出力: {json_path}")
    
    # Excel出力
    try:
        import pandas as pd
        
        df = pd.DataFrame([{
            '番号': b['number'],
            't_book_id': b['t_book_id'],
            'book_id': b['book_id'],
            'タイトル': b['book_title'],
            '再生数': b['play_cnt'],
            'いいね数': b['like_cnt'],
            'エピソード数': b['episode_cnt'],
            'あらすじ': b['special_desc']
        } for b in all_found])
        
        excel_path = 'japanese_cast_original_full.xlsx'
        df.to_excel(excel_path, index=False, sheet_name='日本人キャスト作品')
        print(f"出力: {excel_path}")
        
    except ImportError:
        pass
    
    # 番号の分布を分析
    numbers = [b['number'] for b in all_found]
    if numbers:
        print(f"\n【番号の分布分析】")
        print(f"  最小番号: {min(numbers):03d}")
        print(f"  最大番号: {max(numbers):03d}")
        print(f"  番号リスト: {', '.join(f'{n:03d}' for n in sorted(numbers))}")
        
        # 連番かどうか確認
        missing = []
        for i in range(min(numbers), max(numbers) + 1):
            if i not in numbers:
                missing.append(i)
        
        if missing:
            print(f"\n  欠番（{len(missing)}件）: {', '.join(f'{n:03d}' for n in missing[:20])}")
            if len(missing) > 20:
                print(f"    ... 他 {len(missing)-20}件")
    
    return all_found


if __name__ == '__main__':
    results = main()

