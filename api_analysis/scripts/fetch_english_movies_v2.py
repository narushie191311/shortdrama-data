#!/usr/bin/env python3
"""
ReelShort 英語版 全作品データ取得スクリプト v2
getTagBook APIを使用して全作品を取得
"""

import requests
import json
import csv
import time
from datetime import datetime
from pathlib import Path

# 出力ディレクトリ
OUTPUT_DIR = Path(__file__).parent.parent / "data"
CSV_DIR = Path(__file__).parent.parent / "csv"
OUTPUT_DIR.mkdir(exist_ok=True)
CSV_DIR.mkdir(exist_ok=True)

# ヘッダー
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.reelshort.com/',
}

def fetch_all_movies_via_tag(language="en"):
    """getTagBook APIで全作品を取得"""
    all_movies = []
    page = 1
    page_size = 100
    
    print(f"\n📥 全作品取得中（言語: {language}）...")
    
    while True:
        url = "https://www.reelshort.com/api/video/book/getTagBook"
        params = {
            'tag_id': '',  # 空で全作品
            'page': page,
            'page_size': page_size,
            'language': language
        }
        
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
            
            if resp.status_code != 200:
                print(f"   ページ {page}: ステータス {resp.status_code}")
                break
            
            data = resp.json()
            
            if data.get('code') != 0:
                print(f"   ページ {page}: APIエラー - {data.get('message', 'Unknown')}")
                break
            
            books = data.get('data', {}).get('books', [])
            
            if not books:
                print(f"   ページ {page}: データなし - 終了")
                break
            
            all_movies.extend(books)
            total = data.get('data', {}).get('total', 0)
            print(f"   ページ {page}: {len(books)}作品取得 (累計: {len(all_movies)}/{total})")
            
            if len(all_movies) >= total or len(books) < page_size:
                print(f"   全作品取得完了")
                break
            
            page += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ページ {page}: エラー - {e}")
            break
    
    return all_movies

def fetch_recent_updates(language="en"):
    """最近更新された作品を取得"""
    all_movies = []
    page = 1
    page_size = 100
    
    print(f"\n📥 最近更新された作品を取得中...")
    
    while True:
        url = "https://www.reelshort.com/api/video/book/getRecentUpdateBook"
        params = {
            'page': page,
            'page_size': page_size,
            'language': language
        }
        
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
            
            if resp.status_code != 200:
                break
            
            data = resp.json()
            
            if data.get('code') != 0:
                break
            
            books = data.get('data', {}).get('books', [])
            
            if not books:
                break
            
            all_movies.extend(books)
            total = data.get('data', {}).get('total', 0)
            print(f"   ページ {page}: {len(books)}作品取得 (累計: {len(all_movies)}/{total})")
            
            if len(all_movies) >= total or len(books) < page_size:
                break
            
            page += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   エラー: {e}")
            break
    
    return all_movies

def fetch_movies_by_category(tag_id, tag_name, language="en"):
    """カテゴリ別に作品を取得"""
    all_movies = []
    page = 1
    page_size = 100
    
    while True:
        url = "https://www.reelshort.com/api/video/book/getTagBook"
        params = {
            'tag_id': tag_id,
            'page': page,
            'page_size': page_size,
            'language': language
        }
        
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
            
            if resp.status_code != 200:
                break
            
            data = resp.json()
            
            if data.get('code') != 0:
                break
            
            books = data.get('data', {}).get('books', [])
            
            if not books:
                break
            
            all_movies.extend(books)
            total = data.get('data', {}).get('total', 0)
            
            if len(all_movies) >= total or len(books) < page_size:
                break
            
            page += 1
            time.sleep(0.3)
            
        except:
            break
    
    return all_movies

def fetch_all_tags(language="en"):
    """全タグ情報を取得"""
    print("\n🏷️ タグ情報取得中...")
    url = "https://www.reelshort.com/api/video/book/getTagList"
    params = {'language': language}
    
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 0:
                tags = data.get('data', [])
                print(f"✅ {len(tags)}個のタグカテゴリ取得")
                return tags
    except Exception as e:
        print(f"❌ タグ取得エラー: {e}")
    return []

def fetch_movie_details(book_id, language="en"):
    """個別作品の詳細情報を取得"""
    url = "https://www.reelshort.com/api/video/book/getBookInfo"
    params = {'book_id': book_id, 'language': language}
    
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 0:
                return data.get('data', {})
    except:
        pass
    return None

def objectid_to_datetime(oid):
    """MongoDB ObjectIdから日時を抽出"""
    if not oid or len(oid) < 8:
        return None
    try:
        timestamp = int(oid[:8], 16)
        return datetime.fromtimestamp(timestamp)
    except:
        return None

def save_to_json(data, filename):
    """JSONファイルに保存"""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 保存: {filepath}")

def save_movies_to_csv(movies, filename):
    """作品データをCSVに保存"""
    filepath = CSV_DIR / filename
    
    if not movies:
        print(f"⚠️ データなし: {filename}")
        return
    
    # フィールド定義
    fieldnames = [
        'book_id', 't_book_id', 'book_title', 'read_count', 'collect_count', 
        'chapter_count', 'release_date', 'special_desc', 'tags', 
        'lang', 'book_source', 'cover_url', 'status'
    ]
    
    rows = []
    for m in movies:
        oid = m.get('_id') or m.get('book_id')
        release_dt = objectid_to_datetime(oid)
        
        # tagsを処理
        tags = m.get('tag', [])
        if isinstance(tags, list):
            tags_str = '|'.join(tags)
        else:
            tags_str = str(tags) if tags else ''
        
        # coverを処理
        cover = m.get('cover', {})
        cover_url = cover.get('url', '') if isinstance(cover, dict) else ''
        
        row = {
            'book_id': m.get('book_id', ''),
            't_book_id': m.get('t_book_id', ''),
            'book_title': m.get('book_title', ''),
            'read_count': m.get('read_count', 0),
            'collect_count': m.get('collect_count', 0),
            'chapter_count': m.get('chapter_count', 0),
            'release_date': release_dt.strftime('%Y-%m-%d') if release_dt else '',
            'special_desc': (m.get('special_desc', '') or '')[:500],
            'tags': tags_str,
            'lang': m.get('lang', ''),
            'book_source': m.get('book_source', ''),
            'cover_url': cover_url,
            'status': m.get('status', '')
        }
        rows.append(row)
    
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"💾 保存: {filepath}")

def main():
    print("=" * 70)
    print("🎬 ReelShort 英語版 全作品データ取得 v2")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # タグ一覧取得
    all_tags = fetch_all_tags(language="en")
    
    # 全作品を複数の方法で取得
    all_movies = {}  # book_id をキーにして重複排除
    
    # 方法1: getTagBook (tag_id空)
    movies1 = fetch_all_movies_via_tag(language="en")
    for m in movies1:
        bid = m.get('book_id')
        if bid:
            all_movies[bid] = m
    print(f"   方法1結果: {len(movies1)}作品")
    
    # 方法2: getRecentUpdateBook
    movies2 = fetch_recent_updates(language="en")
    for m in movies2:
        bid = m.get('book_id')
        if bid:
            all_movies[bid] = m
    print(f"   方法2結果: {len(movies2)}作品")
    
    # 方法3: 主要タグから取得
    print("\n📥 主要カテゴリから作品取得中...")
    major_categories = []
    for cat in all_tags:
        for tag in cat.get('tag_list', []):
            major_categories.append({
                'id': tag.get('_id', ''),
                'name': tag.get('text', ''),
                'count': tag.get('count', 0)
            })
    
    # カウント順でソートして上位を取得
    major_categories.sort(key=lambda x: x['count'], reverse=True)
    
    for i, cat in enumerate(major_categories[:30]):  # 上位30カテゴリ
        if not cat['id']:
            continue
        movies = fetch_movies_by_category(cat['id'], cat['name'], language="en")
        new_count = 0
        for m in movies:
            bid = m.get('book_id')
            if bid and bid not in all_movies:
                all_movies[bid] = m
                new_count += 1
        if new_count > 0:
            print(f"   {cat['name']}: +{new_count}作品 (累計: {len(all_movies)})")
        time.sleep(0.3)
    
    # リストに変換
    movies_list = list(all_movies.values())
    print(f"\n📊 重複排除後: {len(movies_list)}作品")
    
    if not movies_list:
        print("❌ データ取得失敗")
        return
    
    # 詳細情報を取得（上位100作品）
    print(f"\n📥 詳細情報取得中...")
    detailed_movies = []
    sorted_movies = sorted(movies_list, key=lambda x: x.get('read_count', 0), reverse=True)
    
    for i, movie in enumerate(sorted_movies[:100]):
        book_id = movie.get('book_id')
        if book_id:
            details = fetch_movie_details(book_id, language="en")
            if details:
                detailed_movies.append(details)
                if (i + 1) % 20 == 0:
                    print(f"   {i+1}/100 完了")
            time.sleep(0.2)
    
    # 統計情報
    print("\n" + "=" * 70)
    print("📈 統計サマリー")
    print("=" * 70)
    
    total_reads = sum(m.get('read_count', 0) for m in movies_list)
    total_likes = sum(m.get('collect_count', 0) for m in movies_list)
    
    print(f"  総作品数: {len(movies_list):,}")
    print(f"  総再生数: {total_reads:,}")
    print(f"  総いいね: {total_likes:,}")
    if movies_list:
        print(f"  平均再生数: {total_reads // len(movies_list):,}")
    
    # TOP10
    print("\n🏆 再生数TOP10:")
    for i, m in enumerate(sorted_movies[:10], 1):
        reads = m.get('read_count', 0)
        title = m.get('book_title', 'Unknown')[:40]
        print(f"  {i:2}. {reads:>12,} | {title}")
    
    # 保存
    print("\n" + "=" * 70)
    print("💾 ファイル保存")
    print("=" * 70)
    
    save_to_json(movies_list, "all_movies_english.json")
    save_to_json(all_tags, "all_tags_english.json")
    if detailed_movies:
        save_to_json(detailed_movies, "movies_detailed_english.json")
    
    save_movies_to_csv(movies_list, "all_movies_english.csv")
    if detailed_movies:
        save_movies_to_csv(detailed_movies, "movies_detailed_english.csv")
    
    print("\n" + "=" * 70)
    print("✅ 完了！")
    print("=" * 70)

if __name__ == "__main__":
    main()



