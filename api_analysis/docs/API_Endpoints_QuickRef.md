# ReelShort API クイックリファレンス

## 認証不要API

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/video/book/getBookInfo?book_id={id}&language=ja` | 作品詳細 |
| GET | `/api/video/book/getTagList?language=ja` | 全タグリスト |
| GET | `/api/video/book/getTagBook?tag_id={id}&page=1&page_size=50&language=ja` | タグ別作品 |
| GET | `/api/video/book/getChapterList?book_id={id}` | チャプター一覧 |
| GET | `/api/video/book/getChapterInfo?chapter_id={id}` | チャプター詳細 |
| GET | `/api/video/book/getFreeChapter?book_id={id}` | 無料チャプター |
| GET | `/api/video/book/getNewTagList?language=ja` | 新タグ |
| GET | `/api/video/search/webSearch?keyword={kw}&language=ja` | 検索 |
| GET | `/api/video/search/getSearchDefault?language=ja` | デフォルト検索 |
| GET | `/api/ms/contest/v1/info?include_stages=true` | コンテスト情報 |

## Next.js Data API

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/_next/data/{buildId}/ja/movie-genres/all-movies.json?slug=all-movies` | 全作品（1ページ目） |
| GET | `/_next/data/{buildId}/ja/movie-genres/all-movies/{page}.json?slug=all-movies&slug={page}` | 全作品（ページN） |

## 認証必要API (POST)

| エンドポイント | 説明 |
|---------------|------|
| `/api/video/user/getUserInfo` | ユーザー情報 |
| `/api/video/user/userLogin` | ログイン |
| `/api/video/user/thirdLoginCheck` | サードパーティログイン |
| `/api/video/book/getBookCollect` | コレクション取得 |
| `/api/video/book/getMyCollectList` | マイコレクション |
| `/api/video/book/myHistory` | 閲覧履歴 |
| `/api/video/hall/info` | ホール情報 |
| `/api/video/hall/checkUserKorean` | 韓国ユーザー確認 |
| `/api/video/hall/webSeeAll` | 全作品表示 |
| `/api/video/store/checkOrder` | 注文確認 |
| `/api/auth/innerH5login` | H5ログイン |

## 重要なID

| 項目 | ID |
|------|-----|
| 日本オリジナルタグ | `67525ca75dc67bc7ba0ce69f` |
| Build ID | `5a4d409` |

## curlコマンド例

```bash
# 全作品取得（ページ1）
curl "https://www.reelshort.com/_next/data/5a4d409/ja/movie-genres/all-movies.json?slug=all-movies"

# 作品詳細
curl "https://www.reelshort.com/api/video/book/getBookInfo?book_id=6901b1f0e12f46f83f05026d&language=ja"

# 日本オリジナル作品
curl "https://www.reelshort.com/api/video/book/getTagBook?tag_id=67525ca75dc67bc7ba0ce69f&page=1&page_size=100&language=ja"

# タグリスト
curl "https://www.reelshort.com/api/video/book/getTagList?language=ja"

# 検索
curl "https://www.reelshort.com/api/video/search/webSearch?keyword=恋愛&language=ja"
```

