#!/usr/bin/env python3
"""
ReelShort 全動画データ取得スクリプト
======================================
すべての作品のメタデータ、インサイト、詳細情報を取得します。
日本オリジナル作品の判別も行います。

使用方法:
    python fetch_all_movies.py

出力:
    - all_movies.json: 全作品の基本情報
    - all_movies_detailed.json: 全作品の詳細情報（API制限に注意）
    - japanese_original_movies.json: 日本オリジナル作品のみ
"""

import json
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API設定
BASE_URL = "https://www.reelshort.com"
BUILD_ID = "5a4d409"  # Next.js build ID（変更される可能性あり）

# レート制限対策
REQUEST_DELAY = 0.5  # リクエスト間の待機時間（秒）
MAX_WORKERS = 3  # 並列リクエスト数

class ReelShortAPI:
    """ReelShort API クライアント"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Referer': 'https://www.reelshort.com/ja/'
        })
    
    def get_all_movies_page(self, page: int = 1, language: str = "ja") -> Dict:
        """
        全作品リストをページごとに取得（Next.js Data API使用）
        
        Args:
            page: ページ番号（1から開始）
            language: 言語コード
        
        Returns:
            ページデータ（books, total, totalPage等）
        """
        if page == 1:
            url = f"{BASE_URL}/_next/data/{BUILD_ID}/{language}/movie-genres/all-movies.json"
            params = {"slug": "all-movies"}
        else:
            url = f"{BASE_URL}/_next/data/{BUILD_ID}/{language}/movie-genres/all-movies/{page}.json"
            params = {"slug": ["all-movies", str(page)]}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("pageProps", {})
        except Exception as e:
            logger.error(f"ページ {page} 取得エラー: {e}")
            return {}
    
    def get_book_info(self, book_id: str, language: str = "ja") -> Optional[Dict]:
        """
        作品の詳細情報を取得
        
        Args:
            book_id: 作品ID
            language: 言語コード
        
        Returns:
            作品詳細データ
        """
        url = f"{BASE_URL}/api/video/book/getBookInfo"
        params = {"book_id": book_id, "language": language}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0:
                return data.get("data")
            else:
                logger.warning(f"作品 {book_id} 取得失敗: {data.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"作品 {book_id} 詳細取得エラー: {e}")
            return None
    
    def get_tag_list(self, language: str = "ja") -> List[Dict]:
        """
        全タグリストを取得
        
        Args:
            language: 言語コード
        
        Returns:
            タグリスト
        """
        url = f"{BASE_URL}/api/video/book/getTagList"
        params = {"language": language}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0:
                return data.get("data", [])
        except Exception as e:
            logger.error(f"タグリスト取得エラー: {e}")
        return []
    
    def get_tag_books(self, tag_id: str, page: int = 1, 
                      page_size: int = 50, language: str = "ja") -> Dict:
        """
        特定タグの作品リストを取得
        
        Args:
            tag_id: タグID
            page: ページ番号
            page_size: 1ページあたりの件数
            language: 言語コード
        
        Returns:
            作品リストデータ
        """
        url = f"{BASE_URL}/api/video/book/getTagBook"
        params = {
            "tag_id": tag_id,
            "page": page,
            "page_size": page_size,
            "language": language
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0:
                return data.get("data", {})
        except Exception as e:
            logger.error(f"タグ {tag_id} 作品取得エラー: {e}")
        return {}
    
    def get_chapter_list(self, book_id: str) -> List[Dict]:
        """
        作品のチャプターリストを取得
        
        Args:
            book_id: 作品ID
        
        Returns:
            チャプターリスト
        """
        url = f"{BASE_URL}/api/video/book/getChapterList"
        params = {"book_id": book_id}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0:
                return data.get("data", [])
        except Exception as e:
            logger.error(f"チャプターリスト取得エラー: {e}")
        return []
    
    def search(self, keyword: str, language: str = "ja") -> Dict:
        """
        作品を検索
        
        Args:
            keyword: 検索キーワード
            language: 言語コード
        
        Returns:
            検索結果
        """
        url = f"{BASE_URL}/api/video/search/webSearch"
        params = {"keyword": keyword, "language": language}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0:
                return data.get("data", {})
        except Exception as e:
            logger.error(f"検索エラー: {e}")
        return {}


def fetch_all_movies_basic(api: ReelShortAPI) -> List[Dict]:
    """全作品の基本情報を取得"""
    all_books = []
    
    # 最初のページを取得してトータルページ数を確認
    first_page = api.get_all_movies_page(1)
    total_pages = first_page.get("totalPage", 1)
    total_items = first_page.get("total", 0)
    
    logger.info(f"総作品数: {total_items}, 総ページ数: {total_pages}")
    
    # 最初のページの作品を追加
    if "tagBooks" in first_page and "books" in first_page["tagBooks"]:
        all_books.extend(first_page["tagBooks"]["books"])
    
    # 残りのページを取得
    for page in range(2, total_pages + 1):
        logger.info(f"ページ {page}/{total_pages} を取得中...")
        time.sleep(REQUEST_DELAY)
        
        page_data = api.get_all_movies_page(page)
        if "tagBooks" in page_data and "books" in page_data["tagBooks"]:
            all_books.extend(page_data["tagBooks"]["books"])
        
        # 進捗表示
        if page % 10 == 0:
            logger.info(f"現在 {len(all_books)} 作品取得完了")
    
    logger.info(f"全 {len(all_books)} 作品の基本情報を取得完了")
    return all_books


def fetch_detailed_info(api: ReelShortAPI, books: List[Dict]) -> List[Dict]:
    """各作品の詳細情報を取得"""
    detailed_books = []
    total = len(books)
    
    for i, book in enumerate(books):
        book_id = book.get("book_id") or book.get("_id")
        if not book_id:
            continue
        
        logger.info(f"詳細取得中: {i+1}/{total} - {book.get('book_title', 'Unknown')}")
        time.sleep(REQUEST_DELAY)
        
        detail = api.get_book_info(book_id)
        if detail:
            # 基本情報と詳細情報をマージ
            merged = {**book, **detail}
            detailed_books.append(merged)
        else:
            detailed_books.append(book)
        
        # 進捗表示
        if (i + 1) % 50 == 0:
            logger.info(f"詳細情報: {i+1}/{total} 完了")
    
    return detailed_books


def identify_japanese_original(book: Dict) -> bool:
    """日本オリジナル作品かどうかを判別"""
    tags = book.get("tag", [])
    
    # タグに「日本オリジナル」が含まれているか
    if "日本オリジナル" in tags:
        return True
    
    # tag_langでも確認
    tag_lang = book.get("tag_lang", [])
    for t in tag_lang:
        if t.get("lang_name") == "日本オリジナル" or t.get("ori_name") == "Japanese Original":
            return True
    
    return False


def enrich_movie_data(book: Dict) -> Dict:
    """作品データを拡張（ローカライズ判別等）"""
    enriched = book.copy()
    
    # 日本オリジナル判別
    enriched["is_japanese_original"] = identify_japanese_original(book)
    
    # 国情報を抽出（tag_listから）
    tag_list = book.get("tag_list", [])
    country_tags = [t for t in tag_list if t.get("category_id") == "1013"]
    enriched["production_country"] = country_tags[0].get("text") if country_tags else None
    
    # 性別ターゲットを抽出
    gender_tags = [t for t in tag_list if t.get("category_id") == "1000"]
    enriched["target_audience"] = gender_tags[0].get("text") if gender_tags else None
    
    # 再生数/コレクション数の正規化
    enriched["read_count"] = book.get("read_count", 0)
    enriched["collect_count"] = book.get("collect_count", 0)
    
    # エピソード数
    online_base = book.get("online_base", [])
    enriched["episode_count"] = len(online_base) if online_base else book.get("chapter_count", 0)
    
    return enriched


def main():
    """メイン処理"""
    output_dir = Path(__file__).parent
    api = ReelShortAPI()
    
    logger.info("=" * 60)
    logger.info("ReelShort 全動画データ取得開始")
    logger.info("=" * 60)
    
    # 1. 全作品の基本情報を取得
    logger.info("\n【Phase 1】全作品の基本情報を取得中...")
    all_movies = fetch_all_movies_basic(api)
    
    # 基本情報を保存
    with open(output_dir / "all_movies_basic.json", "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)
    logger.info(f"基本情報を all_movies_basic.json に保存 ({len(all_movies)} 作品)")
    
    # 2. 各作品の詳細情報を取得（時間がかかる）
    logger.info("\n【Phase 2】各作品の詳細情報を取得中...")
    logger.info("※ これには時間がかかります（約10-20分）")
    
    detailed_movies = fetch_detailed_info(api, all_movies[:20])  # まず20件でテスト
    
    # 詳細情報を保存
    with open(output_dir / "all_movies_detailed_sample.json", "w", encoding="utf-8") as f:
        json.dump(detailed_movies, f, ensure_ascii=False, indent=2)
    logger.info(f"詳細サンプルを all_movies_detailed_sample.json に保存")
    
    # 3. データを拡張（ローカライズ判別等）
    logger.info("\n【Phase 3】データ拡張中...")
    enriched_movies = [enrich_movie_data(m) for m in detailed_movies]
    
    # 拡張データを保存
    with open(output_dir / "all_movies_enriched.json", "w", encoding="utf-8") as f:
        json.dump(enriched_movies, f, ensure_ascii=False, indent=2)
    
    # 4. 日本オリジナル作品を抽出
    japanese_originals = [m for m in enriched_movies if m.get("is_japanese_original")]
    with open(output_dir / "japanese_original_movies.json", "w", encoding="utf-8") as f:
        json.dump(japanese_originals, f, ensure_ascii=False, indent=2)
    logger.info(f"日本オリジナル作品: {len(japanese_originals)} 件")
    
    # 5. タグリストも保存
    logger.info("\n【Phase 4】タグリストを取得中...")
    tag_list = api.get_tag_list()
    with open(output_dir / "all_tags.json", "w", encoding="utf-8") as f:
        json.dump(tag_list, f, ensure_ascii=False, indent=2)
    logger.info(f"タグリストを all_tags.json に保存 ({len(tag_list)} タグ)")
    
    # 6. サマリー表示
    logger.info("\n" + "=" * 60)
    logger.info("取得完了！サマリー:")
    logger.info("=" * 60)
    logger.info(f"総作品数: {len(all_movies)}")
    logger.info(f"詳細取得済み: {len(detailed_movies)}")
    logger.info(f"日本オリジナル: {len(japanese_originals)}")
    logger.info(f"タグ数: {len(tag_list)}")
    logger.info("\n出力ファイル:")
    logger.info("  - all_movies_basic.json: 全作品の基本情報")
    logger.info("  - all_movies_detailed_sample.json: 詳細情報サンプル")
    logger.info("  - all_movies_enriched.json: 拡張データ")
    logger.info("  - japanese_original_movies.json: 日本オリジナル作品")
    logger.info("  - all_tags.json: 全タグリスト")


if __name__ == "__main__":
    main()

