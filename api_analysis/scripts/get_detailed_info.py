#!/usr/bin/env python3
"""
日本人キャスト作品の詳細情報（公開日・再生数）を取得
"""

import requests
import json
import time
from datetime import datetime
import csv

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://www.reelshort.com/ja/'
}


def get_book_detail(book_id):
    """作品の詳細情報を取得"""
    url = f"https://www.reelshort.com/api/video/book/getBookInfo?book_id={book_id}&language=ja"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return data.get('data')
    except Exception as e:
        print(f"Error: {e}")
    return None


def format_number(num):
    """数値をK/M形式でフォーマット"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)


def parse_date(date_str):
    """日付文字列をパース"""
    if not date_str:
        return None, "不明"
    
    try:
        # Unix timestamp (milliseconds)
        if isinstance(date_str, (int, float)) or date_str.isdigit():
            ts = int(date_str) / 1000 if int(date_str) > 1e10 else int(date_str)
            dt = datetime.fromtimestamp(ts)
            return dt, dt.strftime('%Y-%m-%d')
    except:
        pass
    
    try:
        # ISO format
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt, dt.strftime('%Y-%m-%d')
    except:
        pass
    
    return None, str(date_str)


def main():
    print("="*70)
    print("日本人キャスト日本オリジナル作品 - 詳細情報取得")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 既存データから日本人キャスト作品を取得
    with open('all_movies_basic.json', 'r', encoding='utf-8') as f:
        all_movies = json.load(f)
    
    # 140000000140000 パターンでフィルタ
    jp_cast_movies = [m for m in all_movies if m.get('t_book_id', '').startswith('140000000140000')]
    
    print(f"\n日本人キャスト作品: {len(jp_cast_movies)}件")
    print("\n詳細情報を取得中...")
    
    detailed_list = []
    
    for i, movie in enumerate(jp_cast_movies):
        book_id = movie.get('book_id', '')
        title = movie.get('book_title', '')
        t_book_id = movie.get('t_book_id', '')
        
        print(f"  [{i+1}/{len(jp_cast_movies)}] {title}...")
        
        detail = get_book_detail(book_id)
        
        if detail:
            # 日付フィールドを探す
            create_time = detail.get('create_time') or detail.get('created_at') or detail.get('publish_time')
            update_time = detail.get('update_time') or detail.get('updated_at')
            release_date = detail.get('release_date') or detail.get('release_time')
            
            # エピソードから公開日を推測
            episodes = detail.get('episode_list', [])
            first_ep_date = None
            if episodes:
                first_ep = episodes[0] if episodes else {}
                first_ep_date = first_ep.get('create_time') or first_ep.get('release_time')
            
            # 使用する日付を決定
            date_to_use = release_date or create_time or first_ep_date
            _, formatted_date = parse_date(date_to_use)
            
            play_cnt = detail.get('play_cnt', 0)
            like_cnt = detail.get('like_cnt', 0)
            episode_cnt = detail.get('episode_cnt', 0)
            
            detailed_list.append({
                'book_id': book_id,
                't_book_id': t_book_id,
                'number': int(t_book_id[15:]) if len(t_book_id) > 15 else 0,
                'title': title,
                'play_cnt': play_cnt,
                'like_cnt': like_cnt,
                'episode_cnt': episode_cnt,
                'release_date': formatted_date,
                'raw_create_time': str(create_time) if create_time else '',
                'raw_update_time': str(update_time) if update_time else '',
                'special_desc': detail.get('special_desc', '')[:100] if detail.get('special_desc') else ''
            })
        else:
            # APIから取得できない場合は既存データを使用
            detailed_list.append({
                'book_id': book_id,
                't_book_id': t_book_id,
                'number': int(t_book_id[15:]) if len(t_book_id) > 15 else 0,
                'title': title,
                'play_cnt': movie.get('play_cnt', 0),
                'like_cnt': movie.get('like_cnt', 0),
                'episode_cnt': movie.get('episode_cnt', 0),
                'release_date': '不明',
                'raw_create_time': '',
                'raw_update_time': '',
                'special_desc': movie.get('special_desc', '')[:100] if movie.get('special_desc') else ''
            })
        
        time.sleep(0.3)
    
    # 再生数で降順ソート
    detailed_list.sort(key=lambda x: x['play_cnt'], reverse=True)
    
    print("\n" + "="*70)
    print("【再生数順ランキング】日本人キャスト日本オリジナル作品")
    print("="*70)
    
    print("\n{:2} {:6} {:35} {:>12} {:>10} {:12}".format(
        "順", "番号", "タイトル", "再生数", "いいね", "公開日"
    ))
    print("-"*85)
    
    for rank, item in enumerate(detailed_list, 1):
        num = f"[{item['number']:03d}]"
        title = item['title'][:32] + "..." if len(item['title']) > 32 else item['title']
        play = format_number(item['play_cnt'])
        like = format_number(item['like_cnt'])
        date = item['release_date']
        
        print(f"{rank:2} {num:6} {title:35} {play:>12} {like:>10} {date:12}")
    
    # CSVに保存
    csv_path = 'csv/日本人キャスト_再生数ランキング.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['順位', '番号', 'タイトル', '再生数', 'いいね数', 'エピソード数', '公開日', 'book_id', 't_book_id']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rank, item in enumerate(detailed_list, 1):
            writer.writerow({
                '順位': rank,
                '番号': item['number'],
                'タイトル': item['title'],
                '再生数': item['play_cnt'],
                'いいね数': item['like_cnt'],
                'エピソード数': item['episode_cnt'],
                '公開日': item['release_date'],
                'book_id': item['book_id'],
                't_book_id': item['t_book_id']
            })
    print(f"\n出力: {csv_path}")
    
    # Excel出力
    try:
        import pandas as pd
        
        df = pd.DataFrame([{
            '順位': rank,
            '番号': item['number'],
            'タイトル': item['title'],
            '再生数': item['play_cnt'],
            '再生数（表示）': format_number(item['play_cnt']),
            'いいね数': item['like_cnt'],
            'エピソード数': item['episode_cnt'],
            '公開日': item['release_date'],
            'あらすじ': item['special_desc']
        } for rank, item in enumerate(detailed_list, 1)])
        
        excel_path = 'japanese_cast_ranking.xlsx'
        df.to_excel(excel_path, index=False, sheet_name='再生数ランキング')
        print(f"出力: {excel_path}")
        
    except ImportError:
        pass
    
    # 統計情報
    total_plays = sum(item['play_cnt'] for item in detailed_list)
    total_likes = sum(item['like_cnt'] for item in detailed_list)
    avg_plays = total_plays / len(detailed_list) if detailed_list else 0
    
    print("\n" + "="*70)
    print("【統計情報】")
    print("="*70)
    print(f"  総作品数: {len(detailed_list)}作品")
    print(f"  総再生数: {format_number(total_plays)} ({total_plays:,})")
    print(f"  総いいね数: {format_number(total_likes)} ({total_likes:,})")
    print(f"  平均再生数: {format_number(int(avg_plays))} ({int(avg_plays):,})")
    
    return detailed_list


if __name__ == '__main__':
    results = main()

