#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日本人キャスト日本オリジナル作品のキャスト情報収集スクリプト
=====================================================
- ReelShort APIから各作品のキャスト情報を取得
- 各キャストの事務所・SNSアカウント情報を収集
- Excelファイルに出力

使用モジュール:
- requests: HTTPリクエストを送信するライブラリ
- pandas: データ分析・Excel出力用ライブラリ  
- openpyxl: Excelファイル作成用ライブラリ
- time: リクエスト間隔調整用
- re: 正規表現パターンマッチング用
"""

import requests
import pandas as pd
import time
import json
import re
from datetime import datetime
from pathlib import Path

# =========================================
# 設定
# =========================================

# ReelShort APIベースURL
BASE_URL = "https://www.reelshort.com"

# API エンドポイント
# getBookInfo: 作品詳細を取得するエンドポイント
# book_id: 作品を識別する24文字のMongoDB ObjectId
BOOK_INFO_API = "/api/video/book/getBookInfo"

# リクエストヘッダー
# User-Agent: ブラウザを模倣してブロックを回避
# Accept: JSON形式のレスポンスを要求
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.reelshort.com/",
}

# リクエスト間隔（秒）- サーバー負荷軽減のため
REQUEST_INTERVAL = 0.8

# 出力ディレクトリ
OUTPUT_DIR = Path(__file__).parent


def load_movie_list(csv_path: str) -> list:
    """
    CSVファイルから作品リストを読み込む
    
    Parameters:
    -----------
    csv_path : str
        CSVファイルのパス
        
    Returns:
    --------
    list : 作品情報の辞書リスト
    
    解説:
    -----
    pd.read_csv(): pandasのCSV読み込み関数
    - CSVファイルを自動的にDataFrame（表形式データ）に変換
    - 文字コードの自動判定も行う
    to_dict('records'): DataFrameを辞書のリストに変換
    - 各行が1つの辞書になる
    """
    print(f"\n📂 CSVファイル読み込み: {csv_path}")
    
    df = pd.read_csv(csv_path)
    movies = df.to_dict('records')
    
    print(f"   → {len(movies)}作品を読み込みました")
    return movies


def get_book_info(book_id: str) -> dict:
    """
    ReelShort APIから作品詳細を取得
    
    Parameters:
    -----------
    book_id : str
        24文字の作品ID（MongoDB ObjectId形式）
        例: "67f9757fed8210901d04168f"
        
    Returns:
    --------
    dict : 作品詳細情報（actor_info含む）
    
    解説:
    -----
    requests.get(): HTTP GETリクエストを送信
    - params: URLクエリパラメータを辞書で指定
      ?book_id=xxx&language=ja のように自動変換される
    - headers: HTTPヘッダーを指定（認証やブラウザ偽装）
    - timeout: 応答待ち時間（秒）、超過でTimeoutError
    
    response.json(): レスポンスボディをJSONとしてパース
    - dict型のPythonオブジェクトに変換
    """
    url = f"{BASE_URL}{BOOK_INFO_API}"
    
    params = {
        "book_id": book_id,
        "language": "ja"  # 日本語でタグ等を取得
    }
    
    try:
        response = requests.get(
            url, 
            params=params, 
            headers=HEADERS, 
            timeout=30
        )
        
        # HTTPステータスコードチェック
        # 200: 成功, 404: 見つからない, 500: サーバーエラー
        response.raise_for_status()
        
        data = response.json()
        
        # APIレスポンスのcode値確認
        # code=0: 成功, それ以外: エラー
        if data.get("code") == 0:
            return data.get("data", {})
        else:
            print(f"   ⚠️ API エラー: code={data.get('code')}, msg={data.get('msg')}")
            return {}
            
    except requests.exceptions.Timeout:
        print(f"   ⚠️ タイムアウト: {book_id}")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ リクエストエラー: {e}")
        return {}


def extract_cast_info(book_info: dict) -> list:
    """
    作品情報からキャスト情報を抽出
    
    Parameters:
    -----------
    book_info : dict
        getBookInfo APIのレスポンス
        
    Returns:
    --------
    list : キャスト情報の辞書リスト
    
    解説:
    -----
    actor_info構造:
    {
        "imdb_id": "",
        "imdb_url": "",
        "actors": [
            {
                "actor_name": "俳優名",
                "actor_pic": "画像URL",
                "inside_url": "ReelShort内プロフィール",
                "outside_url": "外部リンク（IMDb等）"
            }
        ]
    }
    
    tag_list構造（俳優名も含まれる）:
    category_id = "1001" または "1005" が俳優名
    """
    cast_list = []
    
    # actor_info から取得
    actor_info = book_info.get("actor_info", {})
    actors = actor_info.get("actors", [])
    
    for actor in actors:
        cast_list.append({
            "actor_name": actor.get("actor_name", ""),
            "actor_pic": actor.get("actor_pic", ""),
            "reelshort_url": actor.get("inside_url", ""),
            "external_url": actor.get("outside_url", ""),
        })
    
    # tag_listからも俳優名を補完
    # category_id "1001" と "1005" が俳優タグ
    tag_list = book_info.get("tag_list", [])
    existing_names = {c["actor_name"] for c in cast_list}
    
    for tag in tag_list:
        category_id = tag.get("category_id", "")
        if category_id in ["1001", "1005"]:
            name = tag.get("text", "")
            if name and name not in existing_names:
                cast_list.append({
                    "actor_name": name,
                    "actor_pic": "",
                    "reelshort_url": "",
                    "external_url": "",
                })
                existing_names.add(name)
    
    return cast_list


def is_japanese_name(name: str) -> bool:
    """
    日本語名かどうかを判定
    
    解説:
    -----
    正規表現パターン:
    - [\u3040-\u309F]: ひらがな範囲
    - [\u30A0-\u30FF]: カタカナ範囲  
    - [\u4E00-\u9FFF]: CJK統合漢字（日本語漢字含む）
    
    re.search(): パターンに一致する部分を検索
    - 見つかれば Match オブジェクト（Truthy）
    - 見つからなければ None（Falsy）
    """
    japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')
    return bool(japanese_pattern.search(name))


def search_sns_info(actor_name: str, is_japanese: bool) -> dict:
    """
    キャストのSNS情報を検索して取得
    
    ※注意: Google検索APIには制限があるため、
    ReelShort内のプロフィールページから情報を取得することを推奨
    
    Parameters:
    -----------
    actor_name : str
        キャスト名
    is_japanese : bool
        日本語名かどうか
        
    Returns:
    --------
    dict : SNS情報辞書
    """
    # プレースホルダー - 実際のWeb検索は別途実装
    return {
        "twitter": "",
        "instagram": "",
        "tiktok": "",
        "agency": "",
        "notes": ""
    }


def fetch_reelshort_profile(profile_url: str) -> dict:
    """
    ReelShortのプロフィールページから追加情報を取得
    
    Parameters:
    -----------
    profile_url : str
        ReelShort内プロフィールURL
        例: https://www.reelshort.com/fandom/reelshort-actor-xxx/
        
    Returns:
    --------
    dict : 追加情報
    """
    if not profile_url:
        return {}
        
    try:
        response = requests.get(profile_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # HTMLからSNSリンクを抽出
        html = response.text
        
        info = {}
        
        # Instagram検出
        ig_match = re.search(r'instagram\.com/([a-zA-Z0-9_.]+)', html)
        if ig_match:
            info["instagram"] = f"@{ig_match.group(1)}"
            
        # Twitter/X検出
        tw_match = re.search(r'(?:twitter|x)\.com/([a-zA-Z0-9_]+)', html)
        if tw_match:
            info["twitter"] = f"@{tw_match.group(1)}"
            
        # TikTok検出
        tt_match = re.search(r'tiktok\.com/@([a-zA-Z0-9_.]+)', html)
        if tt_match:
            info["tiktok"] = f"@{tt_match.group(1)}"
            
        return info
        
    except Exception as e:
        print(f"      プロフィール取得エラー: {e}")
        return {}


def collect_all_cast_info(movies: list) -> list:
    """
    全作品からキャスト情報を収集
    
    Parameters:
    -----------
    movies : list
        作品情報リスト
        
    Returns:
    --------
    list : キャスト情報リスト（作品ごと）
    """
    all_cast_data = []
    unique_actors = {}  # 俳優名 -> 情報のマッピング
    
    print(f"\n🎬 {len(movies)}作品のキャスト情報を収集中...")
    print("=" * 60)
    
    for i, movie in enumerate(movies, 1):
        book_id = movie.get("book_id", "")
        title = movie.get("book_title", "")
        
        if not book_id:
            continue
            
        print(f"\n[{i}/{len(movies)}] {title}")
        print(f"   Book ID: {book_id}")
        
        # API呼び出し
        book_info = get_book_info(book_id)
        
        if not book_info:
            print("   → キャスト情報取得失敗")
            continue
            
        # キャスト抽出
        cast_list = extract_cast_info(book_info)
        
        if not cast_list:
            print("   → キャスト情報なし")
        else:
            print(f"   → {len(cast_list)}名のキャストを検出")
            
        for cast in cast_list:
            actor_name = cast.get("actor_name", "")
            is_jp = is_japanese_name(actor_name)
            
            # 重複チェックと情報マージ
            if actor_name not in unique_actors:
                unique_actors[actor_name] = {
                    "actor_name": actor_name,
                    "is_japanese": is_jp,
                    "actor_pic": cast.get("actor_pic", ""),
                    "reelshort_url": cast.get("reelshort_url", ""),
                    "external_url": cast.get("external_url", ""),
                    "appearances": []
                }
            
            # 出演作品を追加
            unique_actors[actor_name]["appearances"].append({
                "book_id": book_id,
                "title": title
            })
            
            # 画像URLが空なら更新
            if not unique_actors[actor_name]["actor_pic"] and cast.get("actor_pic"):
                unique_actors[actor_name]["actor_pic"] = cast["actor_pic"]
                
            # ReelShort URLが空なら更新
            if not unique_actors[actor_name]["reelshort_url"] and cast.get("reelshort_url"):
                unique_actors[actor_name]["reelshort_url"] = cast["reelshort_url"]
                
            # 外部URLが空なら更新
            if not unique_actors[actor_name]["external_url"] and cast.get("external_url"):
                unique_actors[actor_name]["external_url"] = cast["external_url"]
        
        # リクエスト間隔
        time.sleep(REQUEST_INTERVAL)
    
    # ReelShortプロフィールから追加情報取得
    print(f"\n🔍 {len(unique_actors)}名のキャストのプロフィール情報を取得中...")
    
    for i, (name, info) in enumerate(unique_actors.items(), 1):
        profile_url = info.get("reelshort_url", "")
        if profile_url:
            print(f"   [{i}/{len(unique_actors)}] {name} のプロフィール取得中...")
            profile_info = fetch_reelshort_profile(profile_url)
            info.update(profile_info)
            time.sleep(0.5)
    
    return list(unique_actors.values())


def create_excel_report(cast_data: list, movies: list, output_path: str):
    """
    Excel形式でレポートを作成
    
    Parameters:
    -----------
    cast_data : list
        キャスト情報リスト
    movies : list
        作品リスト
    output_path : str
        出力ファイルパス
        
    解説:
    -----
    pd.ExcelWriter: Excelファイル書き込み用コンテキストマネージャー
    - engine='openpyxl': openpyxlエンジンを使用
    - 'with'文で自動的にファイルを閉じる
    
    df.to_excel(): DataFrameをExcelシートに書き込み
    - sheet_name: シート名を指定
    - index=False: 行番号を出力しない
    """
    print(f"\n📊 Excelファイル作成中...")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # ===== シート1: キャスト一覧 =====
        cast_records = []
        for cast in cast_data:
            appearances = cast.get("appearances", [])
            appearance_titles = " / ".join([a["title"] for a in appearances])
            appearance_count = len(appearances)
            
            cast_records.append({
                "キャスト名": cast.get("actor_name", ""),
                "日本語名": "○" if cast.get("is_japanese") else "",
                "出演作品数": appearance_count,
                "出演作品": appearance_titles,
                "プロフィール画像": cast.get("actor_pic", ""),
                "ReelShort URL": cast.get("reelshort_url", ""),
                "IMDb/外部URL": cast.get("external_url", ""),
                "Instagram": cast.get("instagram", ""),
                "Twitter/X": cast.get("twitter", ""),
                "TikTok": cast.get("tiktok", ""),
                "事務所": cast.get("agency", ""),
                "備考": cast.get("notes", "")
            })
        
        df_cast = pd.DataFrame(cast_records)
        # 出演作品数で降順ソート
        df_cast = df_cast.sort_values("出演作品数", ascending=False)
        df_cast.to_excel(writer, sheet_name="キャスト一覧", index=False)
        
        # ===== シート2: 作品別キャスト =====
        movie_cast_records = []
        for cast in cast_data:
            for appearance in cast.get("appearances", []):
                movie_cast_records.append({
                    "作品ID": appearance.get("book_id", ""),
                    "作品タイトル": appearance.get("title", ""),
                    "キャスト名": cast.get("actor_name", ""),
                    "日本語名": "○" if cast.get("is_japanese") else "",
                    "ReelShort URL": cast.get("reelshort_url", ""),
                    "IMDb/外部URL": cast.get("external_url", ""),
                })
        
        df_movie_cast = pd.DataFrame(movie_cast_records)
        df_movie_cast = df_movie_cast.sort_values("作品タイトル")
        df_movie_cast.to_excel(writer, sheet_name="作品別キャスト", index=False)
        
        # ===== シート3: 日本人キャスト =====
        japanese_cast = [c for c in cast_records if c["日本語名"] == "○"]
        df_jp = pd.DataFrame(japanese_cast)
        df_jp.to_excel(writer, sheet_name="日本人キャスト", index=False)
        
        # ===== シート4: 作品一覧 =====
        df_movies = pd.DataFrame(movies)
        df_movies.to_excel(writer, sheet_name="作品一覧", index=False)
        
        # ===== シート5: 収集情報サマリー =====
        summary_data = {
            "項目": [
                "総作品数",
                "総キャスト数",
                "日本人キャスト数",
                "外国人キャスト数",
                "ReelShort URLあり",
                "外部URLあり",
                "収集日時"
            ],
            "値": [
                len(movies),
                len(cast_data),
                len([c for c in cast_data if c.get("is_japanese")]),
                len([c for c in cast_data if not c.get("is_japanese")]),
                len([c for c in cast_data if c.get("reelshort_url")]),
                len([c for c in cast_data if c.get("external_url")]),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name="サマリー", index=False)
    
    print(f"   → 保存完了: {output_path}")


def save_json(data: list, output_path: str):
    """
    JSON形式で保存（バックアップ用）
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   → JSON保存: {output_path}")


def main():
    """
    メイン処理
    
    実行フロー:
    1. CSVから作品リスト読み込み
    2. 各作品のAPIからキャスト情報取得
    3. キャストのプロフィール情報取得
    4. Excelファイル出力
    """
    print("=" * 60)
    print("🎬 日本人キャスト日本オリジナル作品 キャスト情報収集")
    print("=" * 60)
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 入力ファイル
    csv_path = OUTPUT_DIR / "csv" / "日本人キャスト_日本オリジナル.csv"
    
    # 出力ファイル
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_output = OUTPUT_DIR / f"japanese_original_cast_{timestamp}.xlsx"
    json_output = OUTPUT_DIR / f"japanese_original_cast_{timestamp}.json"
    
    # 1. 作品リスト読み込み
    movies = load_movie_list(csv_path)
    
    # 2. キャスト情報収集
    cast_data = collect_all_cast_info(movies)
    
    # 3. 結果出力
    print("\n" + "=" * 60)
    print("📁 結果出力")
    print("=" * 60)
    
    # JSON保存（バックアップ）
    save_json(cast_data, json_output)
    
    # Excel作成
    create_excel_report(cast_data, movies, excel_output)
    
    # 完了メッセージ
    print("\n" + "=" * 60)
    print("✅ 処理完了!")
    print("=" * 60)
    print(f"終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📊 収集結果:")
    print(f"   - 作品数: {len(movies)}")
    print(f"   - キャスト数: {len(cast_data)}")
    print(f"   - 日本人キャスト: {len([c for c in cast_data if c.get('is_japanese')])}名")
    print(f"\n📁 出力ファイル:")
    print(f"   - {excel_output}")
    print(f"   - {json_output}")


if __name__ == "__main__":
    main()

