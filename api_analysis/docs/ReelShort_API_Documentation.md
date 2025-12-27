# ReelShort API ドキュメント

## 概要

ReelShortは短編ドラマストリーミングサービスで、Crazy Maple Studioが運営しています。
本ドキュメントは、リバースエンジニアリングにより発見したAPIエンドポイントをまとめたものです。

- **ベースURL**: `https://www.reelshort.com`
- **調査日**: 2025年12月25日
- **Build ID**: `5a4d409`（変更される可能性あり）

---

## 認証

### 認証不要API

以下のAPIは認証なしでアクセス可能です：
- 作品情報取得系
- タグリスト取得系
- 検索系
- Next.js Data API

### 認証必要API

以下のAPIは認証トークンが必要です：
- ユーザー情報系
- コレクション系
- 履歴系

---

## API エンドポイント一覧

### 1. 作品情報API

#### 1.1 作品詳細取得

```
GET /api/video/book/getBookInfo
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| book_id | string | ✓ | 作品ID（24文字のMongoDB ObjectId） |
| language | string | | 言語コード（デフォルト: en） |

**リクエスト例:**
```bash
curl "https://www.reelshort.com/api/video/book/getBookInfo?book_id=6901b1f0e12f46f83f05026d&language=ja"
```

**レスポンス例:**
```json
{
  "code": 0,
  "msg": "success",
  "server_time": 1766643979,
  "data": {
    "book_id": "6901b1f0e12f46f83f05026d",
    "book_title": "おかえりパパとママだよ",
    "book_type": 1,
    "book_genre": 1,
    "book_source": 1,
    "book_pic": "https://v-mps.crazymaplestudios.com/images/...",
    "special_desc": "説明文...",
    "lang": "ja",
    "t_book_id": "140000000000000355",
    "tag": ["サスペンス"],
    "update_status": 1,
    "is_preview": 0,
    "read_count": 39676,
    "collect_count": 677,
    "online_base": [...],
    "start_play": {...},
    "total": 27,
    "is_paid": 1,
    "tag_list": [...],
    "actor_info": {...},
    "publish_at": 1717655795
  }
}
```

---

#### 1.2 チャプターリスト取得

```
GET /api/video/book/getChapterList
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| book_id | string | ✓ | 作品ID |

**リクエスト例:**
```bash
curl "https://www.reelshort.com/api/video/book/getChapterList?book_id=6901b1f0e12f46f83f05026d"
```

---

#### 1.3 チャプター詳細取得

```
GET /api/video/book/getChapterInfo
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| chapter_id | string | ✓ | チャプターID |

---

#### 1.4 無料チャプター取得

```
GET /api/video/book/getFreeChapter
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| book_id | string | ✓ | 作品ID |

---

### 2. タグ・カテゴリAPI

#### 2.1 全タグリスト取得

```
GET /api/video/book/getTagList
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| language | string | | 言語コード |

**リクエスト例:**
```bash
curl "https://www.reelshort.com/api/video/book/getTagList?language=ja"
```

**レスポンス例:**
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {"_id": "6348f5093c6ca761764d8602", "name": "再会"},
    {"_id": "67525ca75dc67bc7ba0ce69f", "name": "日本オリジナル"},
    ...
  ]
}
```

---

#### 2.2 タグ別作品リスト取得

```
GET /api/video/book/getTagBook
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| tag_id | string | ✓ | タグID |
| page | int | | ページ番号（デフォルト: 1） |
| page_size | int | | 1ページの件数（デフォルト: 20、最大: 200） |
| language | string | | 言語コード |

**リクエスト例:**
```bash
curl "https://www.reelshort.com/api/video/book/getTagBook?tag_id=67525ca75dc67bc7ba0ce69f&page=1&page_size=50&language=ja"
```

**レスポンス例:**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "desc": "",
    "books": [...],
    "page": 1,
    "page_size": 50,
    "total_items": 1033
  }
}
```

---

#### 2.3 新タグリスト取得

```
GET /api/video/book/getNewTagList
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| language | string | | 言語コード |

---

### 3. 検索API

#### 3.1 作品検索

```
GET /api/video/search/webSearch
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| keyword | string | ✓ | 検索キーワード |
| language | string | | 言語コード |

**リクエスト例:**
```bash
curl "https://www.reelshort.com/api/video/search/webSearch?keyword=恋愛&language=ja"
```

---

#### 3.2 デフォルト検索取得

```
GET /api/video/search/getSearchDefault
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| language | string | | 言語コード |

---

### 4. Next.js Data API

#### 4.1 全作品リスト（ページ1）

```
GET /_next/data/{buildId}/{lang}/movie-genres/all-movies.json
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| slug | string | ✓ | "all-movies" |

**リクエスト例:**
```bash
curl "https://www.reelshort.com/_next/data/5a4d409/ja/movie-genres/all-movies.json?slug=all-movies"
```

**レスポンス例:**
```json
{
  "pageProps": {
    "tags": [...],
    "tagBooks": {
      "books": [...],
      "total_items": 1031
    },
    "total": 1031,
    "totalPage": 86,
    "page": 1,
    "nextPageLink": "https://www.reelshort.com/ja/movie-genres/all-movies/2"
  }
}
```

---

#### 4.2 全作品リスト（ページN）

```
GET /_next/data/{buildId}/{lang}/movie-genres/all-movies/{page}.json
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| slug | array | ✓ | ["all-movies", "{page}"] |

**リクエスト例:**
```bash
curl "https://www.reelshort.com/_next/data/5a4d409/ja/movie-genres/all-movies/2.json?slug=all-movies&slug=2"
```

---

### 5. コンテストAPI

#### 5.1 コンテスト情報取得

```
GET /api/ms/contest/v1/info
```

**パラメータ:**

| パラメータ | 型 | 必須 | 説明 |
|-----------|------|------|------|
| include_stages | boolean | | ステージ情報を含める |

---

### 6. 認証必要API（POST）

以下のAPIは認証トークンが必要です。

#### 6.1 ユーザー情報取得

```
POST /api/video/user/getUserInfo
```

#### 6.2 ユーザーログイン

```
POST /api/video/user/userLogin
```

#### 6.3 サードパーティログインチェック

```
POST /api/video/user/thirdLoginCheck
```

#### 6.4 コレクション取得

```
POST /api/video/book/getBookCollect
```

#### 6.5 マイコレクションリスト

```
POST /api/video/book/getMyCollectList
```

#### 6.6 閲覧履歴

```
POST /api/video/book/myHistory
```

#### 6.7 ホール情報

```
POST /api/video/hall/info
```

#### 6.8 韓国ユーザーチェック

```
POST /api/video/hall/checkUserKorean
```

#### 6.9 注文確認

```
POST /api/video/store/checkOrder
```

#### 6.10 H5ログイン

```
POST /api/auth/innerH5login
```

---

## データ構造

### Book（作品）オブジェクト

```typescript
interface Book {
  _id: string;                    // MongoDB ObjectId
  t_book_id: string;              // 内部ID（日本向け: 140000000000000XXX）
  book_title: string;             // タイトル
  book_pic: string;               // サムネイルURL
  book_source: number;            // ソースタイプ（1: 標準）
  book_type: number;              // 作品タイプ
  book_genre: number;             // ジャンル
  special_desc: string;           // 説明文
  lang: string;                   // 言語コード
  tag: string[];                  // タグ配列
  tag_lang: TagLang[];            // 多言語タグ
  read_count: number;             // 再生数
  collect_count: number;          // コレクション数
  chapter_count: number;          // チャプター数
  is_paid: number;                // 有料フラグ（1: 有料）
  is_preview: number;             // プレビューフラグ
  update_status: number;          // 更新ステータス
  online_base: Episode[];         // エピソードリスト
  tag_list: TagDetail[];          // 詳細タグ
  actor_info: ActorInfo;          // 俳優情報
  publish_at: number;             // 公開タイムスタンプ
}
```

### TagLang（多言語タグ）

```typescript
interface TagLang {
  ori_name: string;   // オリジナル名（英語）
  lang_name: string;  // ローカライズ名
  lang: string;       // 言語コード
}
```

### TagDetail（詳細タグ）

```typescript
interface TagDetail {
  id: string;          // タグID
  category_id: string; // カテゴリID
  text: string;        // タグテキスト
}
```

### カテゴリID一覧

| category_id | 内容 |
|-------------|------|
| 1000 | 性別ターゲット（女性/男性） |
| 1001 | 俳優名 |
| 1005 | 俳優名（追加） |
| 1010 | ジャンル大分類 |
| 1011 | 時代設定 |
| 1012 | サブジャンル |
| 1013 | **国情報（撮影地）** |
| 1014 | 時代背景 |
| 1015 | 年齢制限 |
| 1020 | キャラクター属性 |
| 1022 | 関係性タグ |
| 1023 | 場所設定 |
| 1024 | シチュエーション |

---

## エラーコード

| code | 説明 |
|------|------|
| 0 | 成功 |
| 101 | エラー（パラメータ不正など） |
| 405 | Method Not Allowed |
| 502 | 認証失敗/パラメータ不足 |

---

## レート制限

- 推奨リクエスト間隔: **0.5秒以上**
- 最大ページサイズ: **200件**
- 連続エラー時は指数バックオフを推奨

---

## 重要なタグID

| タグ名 | タグID |
|--------|--------|
| 日本オリジナル | `67525ca75dc67bc7ba0ce69f` |
| 女性向けのドラマ | `66124bba32b773444c060974` |
| 男向けのドラマ | `66124bba32b773444c060975` |
| ロマンス | `6600da16c2888abefc0e7a62` |
| 復讐 | `66124bba32b773444c0609ce` |

---

## 日本オリジナル作品の判別

```python
def is_japanese_original(book: dict) -> bool:
    """日本オリジナル作品かどうかを判別"""
    # 方法1: タグに「日本オリジナル」が含まれる
    if "日本オリジナル" in book.get("tag", []):
        return True
    
    # 方法2: t_book_idが日本向け形式
    t_book_id = book.get("t_book_id", "")
    if t_book_id.startswith("14000000000000"):
        return True
    
    return False
```

---

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2025-12-25 | 初版作成 |

