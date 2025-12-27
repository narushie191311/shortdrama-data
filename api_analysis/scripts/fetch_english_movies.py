#!/usr/bin/env python3
"""
ReelShort 英語版 全作品データ取得スクリプト
https://www.reelshort.com/movie-genres/all-movies から全データを取得
"""

import requests
import json
import csv
import time
import re
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

def get_build_id():
    """Next.jsのbuild IDを取得"""
    print("🔍 Build ID取得中...")
    url = "https://www.reelshort.com/movie-genres/all-movies"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    
    # _next/data/{buildId}/ のパターンを探す
    match = re.search(r'/_next/data/([^/]+)/', resp.text)
    if match:
        build_id = match.group(1)
        print(f"✅ Build ID: {build_id}")
        return build_id
    
    # 別のパターン
    match = re.search(r'"buildId":"([^"]+)"', resp.text)
    if match:
        build_id = match.group(1)
        print(f"✅ Build ID: {build_id}")
        return build_id
    
    raise Exception("Build ID not found")

def fetch_all_movies_basic(build_id, language="en"):
    """全作品の基本情報を取得（ページネーション）"""
    all_movies = []
    page = 1
    
    print(f"\n📥 全作品取得中（言語: {language}）...")
    
    while True:
        url = f"https://www.reelshort.com/_next/data/{build_id}/{language}/movie-genres/all-movies/{page}.json"
        params = {'slug': 'all-movies', 'slug': str(page)}
        
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
            
            if resp.status_code != 200:
                print(f"   ページ {page}: ステータス {resp.status_code} - 終了")
                break
            
            data = resp.json()
            
            if 'pageProps' not in data or 'tagBooks' not in data['pageProps']:
                print(f"   ページ {page}: データなし - 終了")
                break
            
            books = data['pageProps']['tagBooks'].get('books', [])
            
            if not books:
                print(f"   ページ {page}: 空 - 終了")
                break
            
            all_movies.extend(books)
            print(f"   ページ {page}: {len(books)}作品取得 (累計: {len(all_movies)})")
            
            # 次のページがあるか確認
            total = data['pageProps']['tagBooks'].get('total', 0)
            if len(all_movies) >= total:
                print(f"   全{total}作品取得完了")
                break
            
            page += 1
            time.sleep(0.5)  # レート制限対策
            
        except Exception as e:
            print(f"   ページ {page}: エラー - {e}")
            break
    
    return all_movies

def fetch_movie_details(book_id, language="en"):
    """個別作品の詳細情報を取得"""
    url = f"https://www.reelshort.com/api/video/book/getBookInfo"
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

def fetch_all_tags(language="en"):
    """全タグ情報を取得"""
    print("\n🏷️ タグ情報取得中...")
    url = f"https://www.reelshort.com/api/video/book/getTagList"
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

def save_to_csv(movies, filename):
    """CSVファイルに保存"""
    filepath = CSV_DIR / filename
    
    if not movies:
        print(f"⚠️ データなし: {filename}")
        return
    
    # フィールド定義
    fieldnames = [
        'book_id', 't_book_id', 'book_title', 'read_count', 'collect_count', 
        'chapter_count', 'release_date', 'special_desc', 'tags', 
        'lang', 'book_source', 'cover_url'
    ]
    
    rows = []
    for m in movies:
        oid = m.get('_id') or m.get('book_id')
        release_dt = objectid_to_datetime(oid)
        
        row = {
            'book_id': m.get('book_id', ''),
            't_book_id': m.get('t_book_id', ''),
            'book_title': m.get('book_title', ''),
            'read_count': m.get('read_count', 0),
            'collect_count': m.get('collect_count', 0),
            'chapter_count': m.get('chapter_count', 0),
            'release_date': release_dt.strftime('%Y-%m-%d') if release_dt else '',
            'special_desc': m.get('special_desc', ''),
            'tags': '|'.join(m.get('tag', [])) if isinstance(m.get('tag'), list) else '',
            'lang': m.get('lang', ''),
            'book_source': m.get('book_source', ''),
            'cover_url': m.get('cover', {}).get('url', '') if isinstance(m.get('cover'), dict) else ''
        }
        rows.append(row)
    
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"💾 保存: {filepath}")

def main():
    print("=" * 70)
    print("🎬 ReelShort 英語版 全作品データ取得")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Build ID取得
    build_id = get_build_id()
    
    # 全作品基本情報取得
    all_movies = fetch_all_movies_basic(build_id, language="en")
    print(f"\n📊 取得完了: {len(all_movies)}作品")
    
    if not all_movies:
        print("❌ データ取得失敗")
        return
    
    # 全タグ取得
    all_tags = fetch_all_tags(language="en")
    
    # 詳細情報を一部取得（サンプル）
    print(f"\n📥 詳細情報取得中（最初の50作品）...")
    detailed_movies = []
    for i, movie in enumerate(all_movies[:50]):
        book_id = movie.get('book_id')
        if book_id:
            details = fetch_movie_details(book_id, language="en")
            if details:
                detailed_movies.append(details)
                print(f"   {i+1}/50: {movie.get('book_title', 'Unknown')[:30]}")
            time.sleep(0.3)
    
    # 統計情報
    print("\n" + "=" * 70)
    print("📈 統計サマリー")
    print("=" * 70)
    
    total_reads = sum(m.get('read_count', 0) for m in all_movies)
    total_likes = sum(m.get('collect_count', 0) for m in all_movies)
    
    print(f"  総作品数: {len(all_movies):,}")
    print(f"  総再生数: {total_reads:,}")
    print(f"  総いいね: {total_likes:,}")
    print(f"  平均再生数: {total_reads // len(all_movies):,}")
    
    # TOP10
    print("\n🏆 再生数TOP10:")
    sorted_movies = sorted(all_movies, key=lambda x: x.get('read_count', 0), reverse=True)
    for i, m in enumerate(sorted_movies[:10], 1):
        reads = m.get('read_count', 0)
        title = m.get('book_title', 'Unknown')[:40]
        print(f"  {i:2}. {reads:>12,} | {title}")
    
    # JSON保存
    print("\n" + "=" * 70)
    print("💾 ファイル保存")
    print("=" * 70)
    
    save_to_json(all_movies, "all_movies_english.json")
    save_to_json(all_tags, "all_tags_english.json")
    if detailed_movies:
        save_to_json(detailed_movies, "movies_detailed_english.json")
    
    # CSV保存
    save_to_csv(all_movies, "all_movies_english.csv")
    
    # 詳細CSV
    if detailed_movies:
        save_to_csv(detailed_movies, "movies_detailed_english.csv")
    
    print("\n" + "=" * 70)
    print("✅ 完了！")
    print("=" * 70)

if __name__ == "__main__":
    main()



