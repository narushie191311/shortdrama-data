#!/usr/bin/env python3
"""
日本人キャスト作品の再生数ランキングと公開日
MongoDB ObjectIdから公開日を抽出
"""

import json
from datetime import datetime
import csv

def objectid_to_datetime(oid):
    """MongoDB ObjectIdから作成日時を抽出"""
    if not oid or len(oid) < 8:
        return None
    try:
        # ObjectIdの最初の8文字（4バイト）はUnixタイムスタンプ（秒）
        timestamp = int(oid[:8], 16)
        return datetime.fromtimestamp(timestamp)
    except:
        return None


def format_number(num):
    """数値をK/M形式でフォーマット"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)


def main():
    print("="*80)
    print("日本人キャスト日本オリジナル作品 - 再生数ランキング & 公開日")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 既存データ読み込み
    with open('all_movies_basic.json', 'r', encoding='utf-8') as f:
        all_movies = json.load(f)
    
    # 日本人キャスト作品をフィルタ
    jp_cast = [m for m in all_movies if m.get('t_book_id', '').startswith('140000000140000')]
    
    # 詳細情報を整理
    detailed_list = []
    for m in jp_cast:
        oid = m.get('_id') or m.get('book_id')
        release_dt = objectid_to_datetime(oid)
        
        t_book_id = m.get('t_book_id', '')
        number = int(t_book_id[15:]) if len(t_book_id) > 15 else 0
        
        detailed_list.append({
            'number': number,
            't_book_id': t_book_id,
            'book_id': m.get('book_id', ''),
            'title': m.get('book_title', ''),
            'read_count': m.get('read_count', 0),
            'collect_count': m.get('collect_count', 0),
            'chapter_count': m.get('chapter_count', 0),
            'release_date': release_dt.strftime('%Y-%m-%d') if release_dt else '不明',
            'release_datetime': release_dt,
            'special_desc': m.get('special_desc', '')[:100] if m.get('special_desc') else '',
            'tags': '|'.join(m.get('tag', [])) if isinstance(m.get('tag'), list) else ''
        })
    
    # 再生数で降順ソート
    detailed_list.sort(key=lambda x: x['read_count'], reverse=True)
    
    print(f"\n日本人キャスト作品: {len(detailed_list)}件\n")
    
    # ヘッダー
    print("="*90)
    print("【再生数順ランキング】")
    print("="*90)
    print(f"{'順':>2} {'番号':>6} {'タイトル':<35} {'再生数':>12} {'いいね':>10} {'EP':>4} {'公開日':>12}")
    print("-"*90)
    
    for rank, item in enumerate(detailed_list, 1):
        num = f"[{item['number']:03d}]"
        title = item['title']
        if len(title) > 33:
            title = title[:30] + "..."
        
        read = format_number(item['read_count'])
        collect = format_number(item['collect_count'])
        eps = item['chapter_count']
        date = item['release_date']
        
        print(f"{rank:2} {num:>6} {title:<35} {read:>12} {collect:>10} {eps:>4} {date:>12}")
    
    # 公開日順でも表示
    print("\n" + "="*90)
    print("【公開日順】（古い順）")
    print("="*90)
    
    dated_list = [item for item in detailed_list if item['release_datetime']]
    dated_list.sort(key=lambda x: x['release_datetime'])
    
    print(f"{'順':>2} {'番号':>6} {'タイトル':<35} {'再生数':>12} {'いいね':>10} {'公開日':>12}")
    print("-"*90)
    
    for i, item in enumerate(dated_list, 1):
        num = f"[{item['number']:03d}]"
        title = item['title']
        if len(title) > 33:
            title = title[:30] + "..."
        
        read = format_number(item['read_count'])
        collect = format_number(item['collect_count'])
        date = item['release_date']
        
        print(f"{i:2} {num:>6} {title:<35} {read:>12} {collect:>10} {date:>12}")
    
    # 統計情報
    total_reads = sum(item['read_count'] for item in detailed_list)
    total_collects = sum(item['collect_count'] for item in detailed_list)
    avg_reads = total_reads / len(detailed_list) if detailed_list else 0
    
    print("\n" + "="*90)
    print("【統計情報】")
    print("="*90)
    print(f"  総作品数: {len(detailed_list)}作品")
    print(f"  総再生数: {format_number(total_reads)} ({total_reads:,})")
    print(f"  総いいね数: {format_number(total_collects)} ({total_collects:,})")
    print(f"  平均再生数: {format_number(int(avg_reads))} ({int(avg_reads):,})")
    print(f"  最も古い公開日: {dated_list[0]['release_date'] if dated_list else '不明'}")
    print(f"  最も新しい公開日: {dated_list[-1]['release_date'] if dated_list else '不明'}")
    
    # CSV出力
    csv_path = 'csv/日本人キャスト_再生数ランキング.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['順位', '番号', 'タイトル', '再生数', 'いいね数', 'エピソード数', '公開日', 'book_id', 't_book_id', 'タグ']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rank, item in enumerate(detailed_list, 1):
            writer.writerow({
                '順位': rank,
                '番号': item['number'],
                'タイトル': item['title'],
                '再生数': item['read_count'],
                'いいね数': item['collect_count'],
                'エピソード数': item['chapter_count'],
                '公開日': item['release_date'],
                'book_id': item['book_id'],
                't_book_id': item['t_book_id'],
                'タグ': item['tags']
            })
    print(f"\n出力: {csv_path}")
    
    # Excel出力
    try:
        import pandas as pd
        
        # 再生数順シート
        df_ranking = pd.DataFrame([{
            '順位': rank,
            '番号': item['number'],
            'タイトル': item['title'],
            '再生数': item['read_count'],
            '再生数（表示）': format_number(item['read_count']),
            'いいね数': item['collect_count'],
            'エピソード数': item['chapter_count'],
            '公開日': item['release_date'],
            'あらすじ': item['special_desc']
        } for rank, item in enumerate(detailed_list, 1)])
        
        # 公開日順シート
        df_date = pd.DataFrame([{
            '順位': rank,
            '番号': item['number'],
            'タイトル': item['title'],
            '公開日': item['release_date'],
            '再生数': item['read_count'],
            '再生数（表示）': format_number(item['read_count']),
            'いいね数': item['collect_count'],
            'エピソード数': item['chapter_count']
        } for rank, item in enumerate(dated_list, 1)])
        
        excel_path = 'japanese_cast_ranking.xlsx'
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_ranking.to_excel(writer, sheet_name='再生数順ランキング', index=False)
            df_date.to_excel(writer, sheet_name='公開日順', index=False)
        print(f"出力: {excel_path}")
        
    except ImportError:
        pass
    
    return detailed_list


if __name__ == '__main__':
    results = main()

