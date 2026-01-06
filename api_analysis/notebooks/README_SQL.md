# ReelShort分析ノートブック（SQL版）

PostgreSQLからデータを取得して分析を行うバージョンです。

## セットアップ

### 1. 環境変数の設定

```bash
# env.example を .env にコピー
cp env.example .env

# .env を編集して接続情報を設定
nano .env
```

### 2. 必要なPythonパッケージ

```bash
pip install sqlalchemy psycopg2-binary python-dotenv pandas numpy plotly
```

### 3. PostgreSQLの準備

リモートサーバーに `reelshort` データベースを作成してください。

```sql
CREATE DATABASE reelshort;
```

## 使い方

### 初回実行

1. **セル1**: DB接続設定（接続テスト）
2. **セル2**: テーブル作成
3. **セル3**: JSONデータをDBにインポート
4. **セル4以降**: 分析を実行

### 2回目以降

1. **セル1**: DB接続設定
2. **セル4以降**: 分析を実行（データはDBから取得）

## テーブル構成

### ja_movies（日本語版作品）

| カラム | 型 | 説明 |
|--------|-----|------|
| id | SERIAL | 主キー |
| book_id | VARCHAR(50) | 作品ID |
| t_book_id | VARCHAR(50) | 内部作品ID |
| title | VARCHAR(500) | タイトル |
| read_count | BIGINT | 再生数 |
| collect_count | INTEGER | いいね数 |
| chapter_count | INTEGER | 話数 |
| release_date | TIMESTAMP | 公開日 |
| tags | JSONB | タグ（配列） |
| origin | VARCHAR(50) | 製作国 |
| is_japanese_cast | BOOLEAN | 日本オリジナルか |

### en_movies（英語版作品）

同様の構造（is_japanese_cast なし）

## 製作国の分類

| origin | 説明 |
|--------|------|
| Japan_Original | ReelShortが日本で制作 |
| USA | アメリカ制作 |
| China | 中国制作 |
| Thailand | タイ制作 |
| Other_Asia | その他アジア |
| Other | その他 |

## SQLクエリ例

```sql
-- 製作国別の再生数統計
SELECT origin,
       COUNT(*) as works,
       SUM(read_count) as total_views,
       AVG(read_count) as avg_views
FROM ja_movies
GROUP BY origin
ORDER BY total_views DESC;

-- 再生数TOP10
SELECT title, read_count, origin
FROM ja_movies
ORDER BY read_count DESC
LIMIT 10;
```



