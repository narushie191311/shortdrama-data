# ReelShort API 分析レポート

## 📊 調査サマリー

| 項目 | 数値 |
|------|------|
| 発見したAPIエンドポイント | 29個 |
| 総作品数（日本語版） | 1,026件 |
| 日本オリジナル作品 | 1,033件（実質全作品が日本向け） |
| タグ数 | 164個 |
| Build ID | `5a4d409` |

---

## 🔌 発見したAPIエンドポイント

### 認証不要API（GET）

| エンドポイント | 説明 | パラメータ |
|---------------|------|-----------|
| `/api/video/book/getTagList` | 全タグリスト取得 | `language=ja` |
| `/api/video/book/getBookInfo` | 作品詳細情報 | `book_id`, `language` |
| `/api/video/book/getChapterList` | チャプターリスト | `book_id` |
| `/api/video/book/getChapterInfo` | チャプター詳細 | `chapter_id` |
| `/api/video/book/getFreeChapter` | 無料チャプター | `book_id` |
| `/api/video/book/getTagBook` | タグ別作品リスト | `tag_id`, `page`, `page_size`, `language` |
| `/api/video/book/getNewTagList` | 新タグリスト | `language` |
| `/api/video/search/webSearch` | 作品検索 | `keyword`, `language` |
| `/api/video/search/getSearchDefault` | デフォルト検索 | `language` |
| `/api/ms/contest/v1/info` | コンテスト情報 | `include_stages` |

### Next.js Data API（認証不要）

| エンドポイント | 説明 |
|---------------|------|
| `/_next/data/{buildId}/ja/movie-genres/all-movies.json` | 全作品リスト（1ページ目） |
| `/_next/data/{buildId}/ja/movie-genres/all-movies/{page}.json` | ページネーション |

### 認証必要API（POST）

| エンドポイント | 説明 |
|---------------|------|
| `/api/video/hall/checkUserKorean` | 韓国ユーザーチェック |
| `/api/video/hall/info` | ホール情報 |
| `/api/video/hall/webSeeAll` | 全作品表示 |
| `/api/video/book/getBookCollect` | コレクション取得 |
| `/api/video/book/myHistory` | 閲覧履歴 |
| `/api/video/book/getMyCollectList` | マイコレクション |
| `/api/video/user/getUserInfo` | ユーザー情報 |
| `/api/video/user/userLogin` | ログイン |
| `/api/video/user/thirdLoginCheck` | サードパーティログイン |
| `/api/video/user/accountLogs` | アカウントログ |
| `/api/video/store/checkOrder` | 注文確認 |
| `/api/auth/innerH5login` | H5ログイン |

---

## 📦 データ構造

### 作品基本情報（Book）

```json
{
  "_id": "6901b1f0e12f46f83f05026d",
  "t_book_id": "140000000000000355",
  "book_title": "おかえりパパとママだよ",
  "book_pic": "https://v-mps.crazymaplestudios.com/images/...",
  "book_source": 1,
  "special_desc": "説明文...",
  "tag": ["サスペンス"],
  "book_type": 1,
  "book_genre": 1,
  "tag_lang": [{"ori_name": "Suspense", "lang_name": "サスペンス", "lang": "ja"}],
  "read_count": 39676,
  "collect_count": 677,
  "chapter_count": 27,
  "is_paid": 1,
  "is_preview": 0
}
```

### 作品詳細情報（Book Detail）

追加フィールド:
- `lang`: 言語コード（"ja"）
- `update_status`: 更新ステータス
- `online_base`: 全エピソードリスト
- `start_play`: 再生情報（暗号化されたplay_info含む）
- `tag_list`: 詳細タグ情報（カテゴリ付き）
- `actor_info`: 俳優情報（IMDb URL含む）
- `publish_at`: 公開タイムスタンプ

### タグリスト カテゴリID

| category_id | 内容 |
|-------------|------|
| 1000 | 性別ターゲット（女性/男性） |
| 1001 | 俳優名 |
| 1005 | 俳優名（追加） |
| 1010 | ジャンル大分類 |
| 1011 | 時代設定 |
| 1012 | サブジャンル |
| 1013 | **国情報（撮影地）** ← 重要 |
| 1014 | 時代背景 |
| 1020 | キャラクター属性 |
| 1022 | 関係性タグ |
| 1023 | 場所設定 |
| 1024 | シチュエーション |

---

## 🇯🇵 日本オリジナル作品の判別方法

### 方法1: タグによる判別（推奨）

```python
def is_japanese_original(book):
    tags = book.get("tag", [])
    return "日本オリジナル" in tags
```

### 方法2: t_book_id の形式

日本向け作品は `140000000000000XXX` 形式のIDを持つ

### 方法3: 言語フィールド

`lang: "ja"` は日本語ローカライズを示す

### 重要な発見

**全1,033作品が「日本オリジナル」タグ付き**
→ 日本市場向けコンテンツ全体を指す可能性が高い

---

## 📁 取得したデータファイル

| ファイル名 | 説明 | 件数 |
|-----------|------|------|
| `all_movies_basic.json` | 全作品の基本情報 | 1,026件 |
| `all_movies_detailed_sample.json` | 詳細情報サンプル | 20件 |
| `all_movies_enriched.json` | 拡張データ | 20件 |
| `japanese_original_full.json` | 日本オリジナル全作品 | 200件（最大取得） |
| `all_tags.json` | 全タグリスト | 164個 |
| `book_detail_full.json` | 個別作品詳細サンプル | 1件 |

---

## 🔧 使用方法

### 全作品取得

```bash
python3 fetch_all_movies.py
```

### 個別作品詳細取得（curl）

```bash
curl "https://www.reelshort.com/api/video/book/getBookInfo?book_id=XXXXX&language=ja"
```

### 特定タグの作品取得

```bash
curl "https://www.reelshort.com/api/video/book/getTagBook?tag_id=XXXXX&page=1&page_size=50&language=ja"
```

---

## ⚠️ 注意事項

1. **Build ID**: `5a4d409` は変更される可能性あり（サイト更新時）
2. **レート制限**: 連続リクエストは0.5秒間隔を推奨
3. **認証API**: POST APIは認証トークンが必要
4. **play_info**: 動画再生情報は暗号化されている

---

## 📅 調査日時

- 調査日: 2025年12月25日
- 調査者: Kali Linux API Explorer
- 使用ツール: curl, jq, Python, ffuf

