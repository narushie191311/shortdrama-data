#!/usr/bin/env python3
"""
日本人キャスト日本オリジナル作品の全探索スクリプト v3

book_idを使ってAPIから詳細情報を取得し、
t_book_idのパターンを確認する
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

PREFIX = "140000000140000"


def get_book_info(book_id):
    """book_idで作品情報を取得"""
    url = f"https://www.reelshort.com/api/video/book/getBookInfo?book_id={book_id}&language=ja"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0 and data.get('data'):
                return data['data']
    except Exception as e:
        print(f"  Error fetching {book_id}: {e}")
    
    return None


def fetch_all_movies_direct():
    """getRecentUpdateBookを使って全作品を取得"""
    all_movies = []
    page = 1
    
    print("\n📖 全作品リスト取得中 (getRecentUpdateBook API)...")
    
    while True:
        url = f"https://www.reelshort.com/api/video/book/getRecentUpdateBook?page={page}&count=100&language=ja"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            
            if response.status_code != 200:
                print(f"  ページ {page}: HTTPエラー {response.status_code}")
                break
            
            data = response.json()
            if data.get('code') != 0:
                print(f"  ページ {page}: APIエラー")
                break
            
            books = data.get('data', {}).get('books', [])
            
            if not books:
                print(f"  ページ {page}: 作品なし - 終了")
                break
            
            all_movies.extend(books)
            print(f"  ページ {page}: {len(books)}作品取得 (累計: {len(all_movies)})")
            
            has_more = data.get('data', {}).get('has_more', False)
            if not has_more:
                break
            
            page += 1
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  ページ {page}: エラー - {e}")
            break
    
    return all_movies


def fetch_all_movies_getall():
    """getAll APIを使って全作品を取得（もし存在すれば）"""
    all_movies = []
    page = 1
    
    print("\n📖 全作品リスト取得中 (getAll API)...")
    
    # 複数のAPIエンドポイントを試す
    endpoints = [
        "https://www.reelshort.com/api/video/book/getAll",
        "https://www.reelshort.com/api/video/book/getHomeList",
        "https://www.reelshort.com/api/video/book/getBookList",
    ]
    
    for endpoint in endpoints:
        url = f"{endpoint}?page=1&count=100&language=ja"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            print(f"  {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"    Response: {json.dumps(data, ensure_ascii=False)[:200]}...")
        except Exception as e:
            print(f"  {endpoint}: Error - {e}")
    
    return all_movies


def fetch_movies_by_tag_all():
    """全タグを取得し、各タグから作品を取得"""
    all_movies = {}
    
    # まず全タグを取得
    print("\n🏷️ 全タグリスト取得中...")
    url = "https://www.reelshort.com/api/video/book/getTagList?language=ja"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tags = data.get('data', [])
            print(f"  タグ数: {len(tags)}")
            
            # 各タグから作品を取得
            for tag in tags[:50]:  # 最初の50タグ
                tag_id = tag.get('_id', '')
                tag_name = tag.get('text', tag.get('name', ''))
                
                # このタグの作品を取得
                tag_url = f"https://www.reelshort.com/api/video/book/getTagBook?tag_id={tag_id}&page=1&count=100&language=ja"
                try:
                    tag_response = requests.get(tag_url, headers=HEADERS, timeout=10)
                    if tag_response.status_code == 200:
                        tag_data = tag_response.json()
                        books = tag_data.get('data', {}).get('books', [])
                        for book in books:
                            book_id = book.get('book_id', '')
                            if book_id not in all_movies:
                                all_movies[book_id] = book
                        if books:
                            print(f"  [{tag_name}]: {len(books)}作品")
                    time.sleep(0.2)
                except:
                    pass
    except Exception as e:
        print(f"  タグ取得エラー: {e}")
    
    return list(all_movies.values())


def main():
    print("="*70)
    print("日本人キャスト日本オリジナル作品 全探索 v3")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 方法1: getRecentUpdateBook
    movies1 = fetch_all_movies_direct()
    print(f"\n方法1 (getRecentUpdateBook): {len(movies1)}作品")
    
    # 方法2: タグ経由で全作品収集
    movies2 = fetch_movies_by_tag_all()
    print(f"\n方法2 (タグ経由): {len(movies2)}作品")
    
    # 統合（重複除去）
    all_movies = {}
    for movie in movies1 + movies2:
        book_id = movie.get('book_id', '')
        if book_id:
            all_movies[book_id] = movie
    
    print(f"\n統合後（重複除去）: {len(all_movies)}作品")
    
    # t_book_idでフィルタリング
    japanese_cast = []
    for movie in all_movies.values():
        t_book_id = movie.get('t_book_id', '')
        if t_book_id.startswith(PREFIX):
            japanese_cast.append(movie)
    
    # ソート
    japanese_cast.sort(key=lambda x: x.get('t_book_id', ''))
    
    print(f"\n{'='*70}")
    print(f"■ 日本人キャスト日本オリジナル: {len(japanese_cast)}作品")
    print("="*70)
    
    for i, movie in enumerate(japanese_cast, 1):
        t_id = movie.get('t_book_id', '')
        num = t_id[15:] if len(t_id) > 15 else '???'
        title = movie.get('book_title', '')
        print(f"{i:2}. [{num}] {title}")
    
    # 既存データと比較
    print("\n" + "="*70)
    print("既存データ (all_movies_basic.json) との比較")
    print("="*70)
    
    try:
        with open('all_movies_basic.json', 'r', encoding='utf-8') as f:
            existing_movies = json.load(f)
        
        existing_jc = [m for m in existing_movies if m.get('t_book_id', '').startswith(PREFIX)]
        print(f"既存データ内の日本人キャスト作品: {len(existing_jc)}件")
        
        # 番号リスト
        existing_nums = []
        for m in existing_jc:
            t_id = m.get('t_book_id', '')
            if len(t_id) > 15:
                try:
                    existing_nums.append(int(t_id[15:]))
                except:
                    pass
        
        existing_nums.sort()
        print(f"既存データの番号: {existing_nums}")
        
        # 新規発見チェック
        new_nums = []
        for m in japanese_cast:
            t_id = m.get('t_book_id', '')
            if len(t_id) > 15:
                try:
                    new_nums.append(int(t_id[15:]))
                except:
                    pass
        
        new_nums.sort()
        newly_found = set(new_nums) - set(existing_nums)
        if newly_found:
            print(f"\n新規発見: {sorted(newly_found)}")
        else:
            print("\n新規発見: なし")
        
        # 既存データから日本人キャスト作品のみを出力
        print(f"\n既存データの日本人キャスト作品一覧:")
        for i, movie in enumerate(sorted(existing_jc, key=lambda x: x.get('t_book_id', '')), 1):
            t_id = movie.get('t_book_id', '')
            num = t_id[15:] if len(t_id) > 15 else '???'
            title = movie.get('book_title', '')
            print(f"{i:2}. [{num}] {title}")
        
    except Exception as e:
        print(f"既存データ読み込みエラー: {e}")
    
    # CSV出力
    csv_path = 'csv/日本人キャスト_v3探索結果.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['番号', 't_book_id', 'book_id', 'book_title', 'play_cnt', 'like_cnt']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for movie in japanese_cast:
            t_id = movie.get('t_book_id', '')
            num = t_id[15:] if len(t_id) > 15 else ''
            writer.writerow({
                '番号': num,
                't_book_id': t_id,
                'book_id': movie.get('book_id', ''),
                'book_title': movie.get('book_title', ''),
                'play_cnt': movie.get('play_cnt', 0),
                'like_cnt': movie.get('like_cnt', 0)
            })
    print(f"\n出力: {csv_path}")
    
    return japanese_cast


if __name__ == '__main__':
    results = main()

