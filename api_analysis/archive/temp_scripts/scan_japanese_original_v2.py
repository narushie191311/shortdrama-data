#!/usr/bin/env python3
"""
日本人キャスト日本オリジナル作品の全探索スクリプト v2

方法1: 全作品ページをスキャンして t_book_id パターンでフィルタリング
方法2: 日本オリジナルタグで取得した作品から t_book_id パターンでフィルタリング
"""

import requests
import json
import time
import csv
from datetime import datetime

# API設定
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://www.reelshort.com/ja/'
}

# Build ID取得
def get_build_id():
    """ReelShortのbuild IDを取得"""
    url = "https://www.reelshort.com/ja/movie-genres/all-movies/1"
    response = requests.get(url, headers=HEADERS, timeout=10)
    
    if response.status_code == 200:
        html = response.text
        import re
        match = re.search(r'"buildId":"([^"]+)"', html)
        if match:
            return match.group(1)
    return None


def fetch_all_movies_via_pages(build_id):
    """全ページをスキャンして作品を取得"""
    all_movies = []
    page = 1
    
    print("\n📖 全ページスキャン開始...")
    
    while True:
        url = f"https://www.reelshort.com/_next/data/{build_id}/ja/movie-genres/all-movies/{page}.json?slug=all-movies&slug={page}"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code != 200:
                print(f"  ページ {page}: HTTPエラー {response.status_code}")
                break
            
            data = response.json()
            page_props = data.get('pageProps', {})
            tag_books = page_props.get('tagBooks', {})
            books = tag_books.get('books', [])
            
            if not books:
                print(f"  ページ {page}: 作品なし - 終了")
                break
            
            all_movies.extend(books)
            print(f"  ページ {page}: {len(books)}作品取得 (累計: {len(all_movies)})")
            
            # 次のページ確認
            has_more = tag_books.get('has_more', False)
            if not has_more:
                break
            
            page += 1
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  ページ {page}: エラー - {e}")
            break
    
    return all_movies


def fetch_all_movies_via_tag(tag_id="67525ca75dc67bc7ba0ce69f"):
    """日本オリジナルタグで作品を取得"""
    all_movies = []
    page = 1
    
    print("\n🏷️ 日本オリジナルタグで取得開始...")
    
    while True:
        url = f"https://www.reelshort.com/api/video/book/getTagBook?tag_id={tag_id}&page={page}&count=50&language=ja"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            if data.get('code') != 0:
                break
            
            books = data.get('data', {}).get('books', [])
            if not books:
                break
            
            all_movies.extend(books)
            print(f"  ページ {page}: {len(books)}作品取得 (累計: {len(all_movies)})")
            
            if not data.get('data', {}).get('has_more', False):
                break
            
            page += 1
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  ページ {page}: エラー - {e}")
            break
    
    return all_movies


def filter_japanese_cast_original(movies):
    """t_book_idパターンで日本人キャスト作品をフィルタリング"""
    japanese_cast = []
    
    for movie in movies:
        t_book_id = movie.get('t_book_id', '')
        if t_book_id.startswith('140000000140000'):
            japanese_cast.append(movie)
    
    return japanese_cast


def main():
    print("="*70)
    print("日本人キャスト日本オリジナル作品 全探索 v2")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Build ID取得
    print("\n🔍 Build ID取得中...")
    build_id = get_build_id()
    if build_id:
        print(f"  Build ID: {build_id}")
    else:
        print("  Build ID取得失敗 - デフォルト使用")
        build_id = "Qww-TZBTyBXr7oUqobpPv"
    
    # 方法1: 全ページスキャン
    all_movies = fetch_all_movies_via_pages(build_id)
    print(f"\n📊 全作品取得完了: {len(all_movies)}作品")
    
    # 日本人キャストオリジナルをフィルタリング
    japanese_cast = filter_japanese_cast_original(all_movies)
    
    # t_book_idの番号でソート
    japanese_cast.sort(key=lambda x: x.get('t_book_id', ''))
    
    print(f"\n{'='*70}")
    print(f"■ 日本人キャスト日本オリジナル: {len(japanese_cast)}作品")
    print("="*70)
    
    for i, movie in enumerate(japanese_cast, 1):
        t_id = movie.get('t_book_id', '')
        title = movie.get('book_title', '')
        # t_book_idの末尾3桁を抽出
        num = t_id[-3:] if len(t_id) >= 3 else '???'
        print(f"{i:2}. [{num}] {title}")
    
    # t_book_idの番号分析
    numbers = []
    for movie in japanese_cast:
        t_id = movie.get('t_book_id', '')
        if t_id.startswith('140000000140000') and len(t_id) > 15:
            try:
                num = int(t_id[15:])
                numbers.append(num)
            except:
                pass
    
    if numbers:
        numbers.sort()
        print(f"\n【番号分析】")
        print(f"  発見した番号: {numbers}")
        print(f"  最小: {min(numbers)}, 最大: {max(numbers)}")
        
        # 欠番確認
        full_range = set(range(min(numbers), max(numbers) + 1))
        found_set = set(numbers)
        missing = full_range - found_set
        if missing:
            print(f"  欠番 ({len(missing)}件): {sorted(missing)}")
    
    # CSVに保存
    csv_path = 'csv/日本人キャスト_最新全リスト.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['t_book_id', 'book_id', 'book_title', 'special_desc', 'play_cnt', 'like_cnt', 'tag']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for movie in japanese_cast:
            row = {
                't_book_id': movie.get('t_book_id', ''),
                'book_id': movie.get('book_id', ''),
                'book_title': movie.get('book_title', ''),
                'special_desc': movie.get('special_desc', '')[:200] if movie.get('special_desc') else '',
                'play_cnt': movie.get('play_cnt', 0),
                'like_cnt': movie.get('like_cnt', 0),
                'tag': '|'.join(movie.get('tag', [])) if isinstance(movie.get('tag'), list) else ''
            }
            writer.writerow(row)
    print(f"\n出力: {csv_path}")
    
    # JSONに保存
    json_path = 'japanese_cast_original_latest.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(japanese_cast, f, ensure_ascii=False, indent=2)
    print(f"出力: {json_path}")
    
    # Excel出力
    try:
        import pandas as pd
        
        df_data = []
        for movie in japanese_cast:
            t_id = movie.get('t_book_id', '')
            num = t_id[-3:] if len(t_id) >= 3 else ''
            df_data.append({
                '番号': num,
                't_book_id': t_id,
                'book_id': movie.get('book_id', ''),
                'タイトル': movie.get('book_title', ''),
                '再生数': movie.get('play_cnt', 0),
                'いいね数': movie.get('like_cnt', 0),
                'タグ': '|'.join(movie.get('tag', [])) if isinstance(movie.get('tag'), list) else '',
                'あらすじ': movie.get('special_desc', '')[:150] if movie.get('special_desc') else ''
            })
        
        df = pd.DataFrame(df_data)
        excel_path = 'japanese_cast_original_latest.xlsx'
        df.to_excel(excel_path, index=False, sheet_name='日本人キャスト作品')
        print(f"出力: {excel_path}")
        
    except ImportError:
        pass
    
    # 方法2も試す（日本オリジナルタグから）
    print("\n" + "="*70)
    print("【補足】日本オリジナルタグからの取得も試行")
    print("="*70)
    
    tag_movies = fetch_all_movies_via_tag()
    tag_japanese_cast = filter_japanese_cast_original(tag_movies)
    
    print(f"\n日本オリジナルタグ総作品数: {len(tag_movies)}")
    print(f"うち日本人キャスト作品: {len(tag_japanese_cast)}")
    
    # 両方の結果を比較
    page_ids = set(m.get('book_id') for m in japanese_cast)
    tag_ids = set(m.get('book_id') for m in tag_japanese_cast)
    
    only_in_pages = page_ids - tag_ids
    only_in_tag = tag_ids - page_ids
    
    if only_in_pages:
        print(f"\n全ページでのみ発見: {len(only_in_pages)}件")
        for book_id in only_in_pages:
            movie = next((m for m in japanese_cast if m.get('book_id') == book_id), None)
            if movie:
                print(f"  - {movie.get('book_title')}")
    
    if only_in_tag:
        print(f"\n日本オリジナルタグでのみ発見: {len(only_in_tag)}件")
        for book_id in only_in_tag:
            movie = next((m for m in tag_japanese_cast if m.get('book_id') == book_id), None)
            if movie:
                print(f"  - {movie.get('book_title')}")
    
    return japanese_cast


if __name__ == '__main__':
    results = main()

