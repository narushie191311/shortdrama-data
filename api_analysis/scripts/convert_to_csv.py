#!/usr/bin/env python3
"""
JSON to CSV 変換スクリプト
ReelShort APIから取得したJSONデータをCSVに変換します
"""

import json
import csv
from pathlib import Path
from datetime import datetime


def flatten_dict(d, parent_key='', sep='_'):
    """ネストした辞書をフラットにする"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # リストは文字列に変換
            if len(v) > 0 and isinstance(v[0], dict):
                items.append((new_key, json.dumps(v, ensure_ascii=False)))
            else:
                items.append((new_key, '|'.join(str(x) for x in v)))
        else:
            items.append((new_key, v))
    return dict(items)


def convert_basic_movies(input_file, output_file):
    """基本情報JSONをCSVに変換"""
    print(f"変換中: {input_file} -> {output_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        print("データが空です")
        return
    
    # 必要なフィールドを選択
    fields = [
        '_id', 'book_id', 't_book_id', 'book_title', 'book_pic',
        'book_source', 'book_type', 'book_genre', 'special_desc',
        'read_count', 'collect_count', 'chapter_count',
        'is_paid', 'is_preview', 'init_read_count', 'init_collect_count',
        'chapter_id', 'serial_number'
    ]
    
    # タグを文字列に変換
    processed_data = []
    for item in data:
        row = {}
        for field in fields:
            row[field] = item.get(field, '')
        
        # タグを結合
        tags = item.get('tag', [])
        row['tags'] = '|'.join(tags) if isinstance(tags, list) else tags
        
        # tag_langからオリジナル名を抽出
        tag_lang = item.get('tag_lang', [])
        ori_names = [t.get('ori_name', '') for t in tag_lang if isinstance(t, dict)]
        row['tags_original'] = '|'.join(ori_names)
        
        processed_data.append(row)
    
    # CSV書き出し
    fieldnames = fields + ['tags', 'tags_original']
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)
    
    print(f"完了: {len(processed_data)} 件を出力")


def convert_detailed_movies(input_file, output_file):
    """詳細情報JSONをCSVに変換"""
    print(f"変換中: {input_file} -> {output_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        print("データが空です")
        return
    
    # 詳細フィールド
    fields = [
        '_id', 'book_id', 't_book_id', 'book_title', 'book_pic',
        'book_source', 'book_type', 'book_genre', 'special_desc',
        'lang', 'update_status', 'is_preview', 'is_paid',
        'read_count', 'collect_count', 'total',
        'publish_at'
    ]
    
    processed_data = []
    for item in data:
        row = {}
        for field in fields:
            value = item.get(field, '')
            # タイムスタンプを日時に変換
            if field == 'publish_at' and value:
                try:
                    row[field] = datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    row[field] = value
            else:
                row[field] = value
        
        # タグを結合
        tags = item.get('tag', [])
        row['tags'] = '|'.join(tags) if isinstance(tags, list) else tags
        
        # 日本オリジナル判定
        row['is_japanese_original'] = '日本オリジナル' in tags if isinstance(tags, list) else False
        
        # 俳優情報
        actor_info = item.get('actor_info', {})
        actors = actor_info.get('actors', [])
        actor_names = [a.get('actor_name', '') for a in actors if isinstance(a, dict)]
        row['actors'] = '|'.join(actor_names)
        
        # エピソード数
        online_base = item.get('online_base', [])
        row['episode_count'] = len(online_base)
        
        # tag_listから国情報を抽出
        tag_list = item.get('tag_list', [])
        country_tags = [t.get('text', '') for t in tag_list 
                       if isinstance(t, dict) and t.get('category_id') == '1013']
        row['production_country'] = '|'.join(country_tags)
        
        # 性別ターゲット
        gender_tags = [t.get('text', '') for t in tag_list 
                      if isinstance(t, dict) and t.get('category_id') == '1000']
        row['target_audience'] = '|'.join(gender_tags)
        
        processed_data.append(row)
    
    # CSV書き出し
    fieldnames = fields + ['tags', 'is_japanese_original', 'actors', 
                          'episode_count', 'production_country', 'target_audience']
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)
    
    print(f"完了: {len(processed_data)} 件を出力")


def convert_tags(input_file, output_file):
    """タグリストJSONをCSVに変換"""
    print(f"変換中: {input_file} -> {output_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        print("データが空です")
        return
    
    fieldnames = ['_id', 'name']
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"完了: {len(data)} 件を出力")


def convert_japanese_original(input_file, output_file):
    """日本オリジナル作品JSONをCSVに変換"""
    print(f"変換中: {input_file} -> {output_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    books = data.get('books', [])
    if not books:
        print("データが空です")
        return
    
    fields = [
        '_id', 'book_id', 't_book_id', 'book_title', 'book_pic',
        'book_source', 'book_type', 'book_genre', 'special_desc',
        'read_count', 'collect_count', 'chapter_count',
        'is_paid', 'is_preview'
    ]
    
    processed_data = []
    for item in books:
        row = {}
        for field in fields:
            row[field] = item.get(field, '')
        
        # タグを結合
        tags = item.get('tag', [])
        row['tags'] = '|'.join(tags) if isinstance(tags, list) else tags
        
        # tag_langからオリジナル名を抽出
        tag_lang = item.get('tag_lang', [])
        ori_names = [t.get('ori_name', '') for t in tag_lang if isinstance(t, dict)]
        row['tags_original'] = '|'.join(ori_names)
        
        processed_data.append(row)
    
    fieldnames = fields + ['tags', 'tags_original']
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)
    
    print(f"完了: {len(processed_data)} 件を出力")


def main():
    """メイン処理"""
    base_dir = Path(__file__).parent
    csv_dir = base_dir / 'csv'
    csv_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("JSON → CSV 変換開始")
    print("=" * 60)
    
    # 1. 基本情報
    if (base_dir / 'all_movies_basic.json').exists():
        convert_basic_movies(
            base_dir / 'all_movies_basic.json',
            csv_dir / 'all_movies_basic.csv'
        )
    
    # 2. 詳細情報
    if (base_dir / 'all_movies_detailed_sample.json').exists():
        convert_detailed_movies(
            base_dir / 'all_movies_detailed_sample.json',
            csv_dir / 'all_movies_detailed.csv'
        )
    
    # 3. 拡張情報
    if (base_dir / 'all_movies_enriched.json').exists():
        convert_detailed_movies(
            base_dir / 'all_movies_enriched.json',
            csv_dir / 'all_movies_enriched.csv'
        )
    
    # 4. タグリスト
    if (base_dir / 'all_tags.json').exists():
        convert_tags(
            base_dir / 'all_tags.json',
            csv_dir / 'all_tags.csv'
        )
    
    # 5. 日本オリジナル作品
    if (base_dir / 'japanese_original_full.json').exists():
        convert_japanese_original(
            base_dir / 'japanese_original_full.json',
            csv_dir / 'japanese_original.csv'
        )
    
    print("=" * 60)
    print("変換完了！")
    print(f"出力先: {csv_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

