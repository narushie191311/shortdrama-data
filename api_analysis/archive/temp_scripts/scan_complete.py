#!/usr/bin/env python3
"""
日本人キャスト作品の完全探索

1. 既存book_idを使ってAPIから最新情報を取得
2. 類似パターンの探索
3. 欠番の確認
"""

import requests
import json
import time
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://www.reelshort.com/ja/'
}


def get_book_info_by_book_id(book_id):
    """book_idで作品情報を取得"""
    url = f"https://www.reelshort.com/api/video/book/getBookInfo?book_id={book_id}&language=ja"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return data.get('data')
    except:
        pass
    return None


def search_by_keyword(keyword):
    """キーワードで検索"""
    url = f"https://www.reelshort.com/api/video/book/searchBook?keyword={keyword}&language=ja"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return data.get('data', {}).get('books', [])
    except:
        pass
    return []


def main():
    print("="*70)
    print("日本人キャスト作品 完全探索")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 既存データ読み込み
    with open('all_movies_basic.json', 'r', encoding='utf-8') as f:
        all_movies = json.load(f)
    
    print(f"\n既存データ総数: {len(all_movies)}作品")
    
    # t_book_idプレフィックス分析
    prefix_counts = {}
    for movie in all_movies:
        t_id = movie.get('t_book_id', '')
        if len(t_id) >= 15:
            prefix = t_id[:15]
            if prefix not in prefix_counts:
                prefix_counts[prefix] = []
            prefix_counts[prefix].append(movie)
    
    print("\n" + "="*70)
    print("t_book_id プレフィックス分析（日本向け: 140... で始まるもの）")
    print("="*70)
    
    jp_patterns = {}
    for prefix, movies in sorted(prefix_counts.items()):
        if prefix.startswith('140'):
            jp_patterns[prefix] = movies
            print(f"\n{prefix}: {len(movies)}件")
            for m in movies[:5]:
                print(f"  - [{m.get('t_book_id', '')[-3:]}] {m.get('book_title', '')}")
            if len(movies) > 5:
                print(f"  ... 他 {len(movies)-5}件")
    
    # 140000000140000 パターンの詳細
    print("\n" + "="*70)
    print("【重要】140000000140000 パターン（日本人キャスト）")
    print("="*70)
    
    jp_cast_movies = jp_patterns.get('140000000140000', [])
    
    if jp_cast_movies:
        # 番号抽出
        numbers = []
        for m in jp_cast_movies:
            t_id = m.get('t_book_id', '')
            if len(t_id) > 15:
                try:
                    num = int(t_id[15:])
                    numbers.append((num, m))
                except:
                    pass
        
        numbers.sort(key=lambda x: x[0])
        
        print(f"\n現在発見済み: {len(numbers)}作品")
        for num, movie in numbers:
            print(f"  [{num:03d}] {movie.get('book_title', '')}")
        
        # 欠番分析
        all_nums = [n for n, _ in numbers]
        min_num, max_num = min(all_nums), max(all_nums)
        full_range = set(range(min_num, max_num + 1))
        found_set = set(all_nums)
        missing = sorted(full_range - found_set)
        
        print(f"\n番号範囲: {min_num:03d} 〜 {max_num:03d}")
        print(f"欠番 ({len(missing)}件): {missing}")
    
    # 類似パターン探索（140000000130000 など）
    print("\n" + "="*70)
    print("類似パターンの分析")
    print("="*70)
    
    similar_patterns = [
        '140000000130000',  # 1つ前のシリーズ？
        '140000000150000',  # 次のシリーズ？
        '140000000120000',
        '140000000110000',
        '140000000100000',
        '140000000160000',
        '140000000170000',
        '140000000180000',
        '140000000190000',
        '140000000200000',
        '140000000300000',
    ]
    
    for pattern in similar_patterns:
        if pattern in prefix_counts:
            movies = prefix_counts[pattern]
            print(f"\n{pattern}: {len(movies)}件")
            for m in movies:
                print(f"  - {m.get('book_title', '')}")
    
    # キーワード検索で追加作品を探す
    print("\n" + "="*70)
    print("キーワード検索による追加作品探索")
    print("="*70)
    
    keywords = ['日本', 'オリジナル', '令嬢', '御曹司', '億万長者']
    found_new = {}
    
    for keyword in keywords:
        print(f"\n🔍 「{keyword}」で検索中...")
        results = search_by_keyword(keyword)
        print(f"  結果: {len(results)}件")
        
        for movie in results:
            t_id = movie.get('t_book_id', '')
            book_id = movie.get('book_id', '')
            
            if t_id.startswith('140000000140000') and book_id not in found_new:
                found_new[book_id] = movie
                print(f"  ★ 発見: [{t_id[-3:]}] {movie.get('book_title', '')}")
        
        time.sleep(0.5)
    
    print(f"\n検索で発見した日本人キャスト作品: {len(found_new)}件")
    
    # 既存の日本人キャスト作品のbook_idから最新情報を取得
    print("\n" + "="*70)
    print("既存作品の最新情報取得")
    print("="*70)
    
    if jp_cast_movies:
        print(f"\n{len(jp_cast_movies)}作品の最新情報を取得中...")
        
        updated_movies = []
        for i, movie in enumerate(jp_cast_movies):
            book_id = movie.get('book_id', '')
            if book_id:
                info = get_book_info_by_book_id(book_id)
                if info:
                    updated_movies.append(info)
                    t_id = info.get('t_book_id', '')
                    play = info.get('play_cnt', 0)
                    like = info.get('like_cnt', 0)
                    print(f"  [{i+1:2}] {info.get('book_title', '')} - 再生: {play:,} いいね: {like:,}")
                time.sleep(0.3)
        
        # 最新データを保存
        if updated_movies:
            with open('japanese_cast_original_updated.json', 'w', encoding='utf-8') as f:
                json.dump(updated_movies, f, ensure_ascii=False, indent=2)
            print(f"\n出力: japanese_cast_original_updated.json")
            
            # Excel出力
            try:
                import pandas as pd
                
                df_data = []
                for m in sorted(updated_movies, key=lambda x: x.get('t_book_id', '')):
                    t_id = m.get('t_book_id', '')
                    df_data.append({
                        '番号': t_id[-3:] if len(t_id) > 15 else '',
                        't_book_id': t_id,
                        'タイトル': m.get('book_title', ''),
                        '再生数': m.get('play_cnt', 0),
                        'いいね数': m.get('like_cnt', 0),
                        'エピソード数': m.get('episode_cnt', 0),
                        'タグ': '|'.join(m.get('tag', [])) if isinstance(m.get('tag'), list) else '',
                        'あらすじ': m.get('special_desc', '')[:150] if m.get('special_desc') else ''
                    })
                
                df = pd.DataFrame(df_data)
                df.to_excel('japanese_cast_original_updated.xlsx', index=False, sheet_name='日本人キャスト作品')
                print(f"出力: japanese_cast_original_updated.xlsx")
                
            except ImportError:
                pass
    
    # 最終まとめ
    print("\n" + "="*70)
    print("【最終まとめ】")
    print("="*70)
    print(f"""
■ 日本人キャスト日本オリジナル作品の判定方法:

  t_book_id.startswith("140000000140000")
  
■ 発見済み: {len(jp_cast_movies)}作品
  番号: {[int(m.get('t_book_id', '')[15:]) for m in jp_cast_movies if len(m.get('t_book_id', '')) > 15]}

■ 番号の傾向分析:
  - 番号は連番ではなく、制作/公開順に付与されている可能性
  - 欠番は未公開作品または削除作品の可能性
  - 最大番号164まで存在 → 今後さらに追加される可能性あり

■ 類似パターン:
  140000000000000: 日本語吹き替え版（海外原作）
  140000000140000: 日本人キャスト日本オリジナル ★これが重要★
  140000200000000: 日本向けローカライズ版
""")
    
    return jp_cast_movies


if __name__ == '__main__':
    results = main()

