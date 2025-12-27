#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReelShort 日本オリジナル作品 キャスト情報収集スクリプト（改良版）
================================================================

日本オリジナル作品は海外版のローカライズではなく、日本人キャストが出演。
APIに登録されているキャスト情報はアメリカ版のため、
Web検索で日本人キャスト情報を収集してExcelにまとめる。

発見した情報:
- 「冷酷御曹司の愛妻計画」主演: 長田成哉 (制作: nowhere film株式会社)
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import json

# 出力ディレクトリ
OUTPUT_DIR = Path(__file__).parent

# ========================================
# 既知の日本人キャスト情報（Web調査結果）
# ========================================
# 注意: これは調査中の情報で、追加調査が必要です

KNOWN_JAPANESE_CAST = {
    # 作品名: キャスト情報のリスト
    "冷酷御曹司の愛妻計画": [
        {
            "role": "主演",
            "actor_name_jp": "長田成哉",
            "actor_name_romaji": "Nagata Seiya",
            "agency": "",  # 要調査
            "instagram": "",  # 要調査
            "twitter": "",  # 要調査
            "tiktok": "",  # 要調査
            "imdb": "",
            "notes": "nowhere film株式会社制作の日本版リメイク。2025年5月公開。"
        }
    ],
    "財閥令嬢様の二重生活": [
        {
            "role": "出演",
            "actor_name_jp": "音野暁",
            "actor_name_romaji": "Otono Akira",
            "agency": "株式会社Kと",
            "instagram": "",  # 要調査
            "twitter": "",  # 要調査
            "tiktok": "",  # 要調査
            "imdb": "",
            "notes": "株式会社Kと契約俳優"
        },
        {
            "role": "出演",
            "actor_name_jp": "江畑浩規",
            "actor_name_romaji": "Ebata Koki",
            "agency": "株式会社Kと",
            "instagram": "",  # 要調査
            "twitter": "",  # 要調査
            "tiktok": "",  # 要調査
            "imdb": "",
            "notes": "株式会社Kと契約俳優"
        },
        {
            "role": "出演",
            "actor_name_jp": "梁錦川",
            "actor_name_romaji": "Ryo Kinsen",
            "agency": "株式会社Kと",
            "instagram": "",  # 要調査
            "twitter": "",  # 要調査
            "tiktok": "",  # 要調査
            "imdb": "",
            "notes": "株式会社Kと契約俳優"
        }
    ],
    # 他の作品は調査が必要
}

# 調査用リソース
RESEARCH_SOURCES = [
    "ReelShort公式Instagram: https://www.instagram.com/reelshort/",
    "ReelShort Japan TikTok: https://www.tiktok.com/@reelshort_japan",
    "nowhere film: https://nowhere-film.jp/",
    "PR TIMES検索: https://prtimes.jp/",
    "各キャストのInstagram/Twitterプロフィール",
]


def load_movie_list():
    """CSVから作品リストを読み込む"""
    csv_path = OUTPUT_DIR / "csv" / "日本人キャスト_日本オリジナル.csv"
    
    if not csv_path.exists():
        print(f"❌ CSVファイルが見つかりません: {csv_path}")
        return []
    
    df = pd.read_csv(csv_path)
    return df.to_dict('records')


def create_comprehensive_excel(movies: list, output_path: str):
    """
    キャスト情報を整理したExcelファイルを作成
    
    シート構成:
    1. 作品リスト: 全作品の基本情報
    2. 確認済みキャスト: 調査で確認できたキャスト
    3. 調査用テンプレート: 手動調査用のフォーマット
    4. 調査リソース: 調査に役立つリンク集
    5. 制作会社情報: 日本版制作会社
    """
    print(f"\n📊 Excelファイル作成中...")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # ===== シート1: 作品リスト =====
        movie_records = []
        for movie in movies:
            title = movie.get('book_title', '')
            known_cast = KNOWN_JAPANESE_CAST.get(title, [])
            cast_names = ", ".join([c.get('actor_name_jp', '') for c in known_cast]) if known_cast else "要調査"
            
            movie_records.append({
                "No": len(movie_records) + 1,
                "作品タイトル": title,
                "book_id": movie.get('book_id', ''),
                "カテゴリ": movie.get('category', ''),
                "確認済みキャスト": cast_names,
                "調査状況": "完了" if known_cast else "未調査",
                "タグ": movie.get('tags', ''),
                "概要": movie.get('description', '')[:100] + "..." if len(str(movie.get('description', ''))) > 100 else movie.get('description', ''),
            })
        
        df_movies = pd.DataFrame(movie_records)
        df_movies.to_excel(writer, sheet_name="作品リスト", index=False)
        
        # カラム幅調整
        worksheet = writer.sheets["作品リスト"]
        worksheet.column_dimensions['A'].width = 5
        worksheet.column_dimensions['B'].width = 40
        worksheet.column_dimensions['C'].width = 28
        worksheet.column_dimensions['D'].width = 25
        worksheet.column_dimensions['E'].width = 20
        worksheet.column_dimensions['F'].width = 12
        worksheet.column_dimensions['G'].width = 40
        
        # ===== シート2: 確認済みキャスト =====
        cast_records = []
        for title, cast_list in KNOWN_JAPANESE_CAST.items():
            for cast in cast_list:
                cast_records.append({
                    "作品タイトル": title,
                    "役柄": cast.get('role', ''),
                    "キャスト名（日本語）": cast.get('actor_name_jp', ''),
                    "キャスト名（ローマ字）": cast.get('actor_name_romaji', ''),
                    "事務所": cast.get('agency', ''),
                    "Instagram": cast.get('instagram', ''),
                    "Twitter/X": cast.get('twitter', ''),
                    "TikTok": cast.get('tiktok', ''),
                    "IMDb": cast.get('imdb', ''),
                    "備考": cast.get('notes', ''),
                })
        
        if cast_records:
            df_cast = pd.DataFrame(cast_records)
        else:
            df_cast = pd.DataFrame(columns=[
                "作品タイトル", "役柄", "キャスト名（日本語）", "キャスト名（ローマ字）",
                "事務所", "Instagram", "Twitter/X", "TikTok", "IMDb", "備考"
            ])
        df_cast.to_excel(writer, sheet_name="確認済みキャスト", index=False)
        
        # ===== シート3: 調査用テンプレート =====
        template_records = []
        for movie in movies:
            title = movie.get('book_title', '')
            if title not in KNOWN_JAPANESE_CAST:
                # 未調査の作品用のテンプレート行を追加
                for i in range(3):  # 各作品に3行分のスペース
                    template_records.append({
                        "作品タイトル": title if i == 0 else "",
                        "book_id": movie.get('book_id', '') if i == 0 else "",
                        "役柄": "",
                        "キャスト名（日本語）": "",
                        "キャスト名（ローマ字）": "",
                        "事務所": "",
                        "Instagram": "",
                        "Twitter/X": "",
                        "TikTok": "",
                        "IMDb": "",
                        "情報源URL": "",
                        "確認日": "",
                    })
        
        df_template = pd.DataFrame(template_records)
        df_template.to_excel(writer, sheet_name="調査用テンプレート", index=False)
        
        # ===== シート4: API取得キャスト（アメリカ版） =====
        # 既存のJSONファイルから読み込み
        json_files = list(OUTPUT_DIR.glob("japanese_original_cast_*.json"))
        if json_files:
            latest_json = sorted(json_files)[-1]
            with open(latest_json, 'r', encoding='utf-8') as f:
                api_cast = json.load(f)
            
            api_records = []
            for cast in api_cast:
                appearances = cast.get("appearances", [])
                for app in appearances:
                    api_records.append({
                        "作品タイトル": app.get("title", ""),
                        "キャスト名（API）": cast.get("actor_name", ""),
                        "ReelShort URL": cast.get("reelshort_url", ""),
                        "外部URL": cast.get("external_url", ""),
                        "備考": "※これはアメリカ版のキャストです。日本版は別のキャストが出演しています。"
                    })
            
            df_api = pd.DataFrame(api_records)
            df_api.to_excel(writer, sheet_name="API取得キャスト（米国版参考）", index=False)
        
        # ===== シート5: 調査リソース =====
        resource_records = [
            {"リソース名": "ReelShort公式サイト", "URL": "https://www.reelshort.com/ja/", "説明": "作品ページで出演者タグを確認"},
            {"リソース名": "ReelShort公式Instagram", "URL": "https://www.instagram.com/reelshort/", "説明": "新作や出演者情報の投稿を確認"},
            {"リソース名": "ReelShort Japan TikTok", "URL": "https://www.tiktok.com/@reelshort_japan", "説明": "日本オリジナル作品の宣伝動画"},
            {"リソース名": "nowhere film", "URL": "https://nowhere-film.jp/", "説明": "日本版リメイク制作会社"},
            {"リソース名": "PR TIMES", "URL": "https://prtimes.jp/", "説明": "プレスリリースでキャスト情報を検索"},
            {"リソース名": "note nowhere inc.", "URL": "https://note.com/nowhere_inc_/", "説明": "制作裏話、キャスト情報"},
            {"リソース名": "Google検索", "URL": "", "説明": "「作品名 + ReelShort + キャスト」で検索"},
            {"リソース名": "Twitter/X検索", "URL": "https://twitter.com/search", "説明": "「作品名 + ReelShort」で出演者情報を検索"},
        ]
        df_resources = pd.DataFrame(resource_records)
        df_resources.to_excel(writer, sheet_name="調査リソース", index=False)
        
        # ===== シート6: 制作会社情報 =====
        company_records = [
            {
                "会社名": "nowhere film株式会社",
                "URL": "https://nowhere-film.jp/",
                "担当作品": "冷酷御曹司の愛妻計画",
                "note": "https://note.com/nowhere_inc_/",
                "備考": "課金型ドラマ500作品以上の制作実績"
            },
            {
                "会社名": "ReelShort (Crazy Maple Studio)",
                "URL": "https://www.reelshort.com/",
                "担当作品": "全作品（配信プラットフォーム）",
                "note": "",
                "備考": "アメリカの短編ドラマ配信アプリ"
            }
        ]
        df_companies = pd.DataFrame(company_records)
        df_companies.to_excel(writer, sheet_name="制作会社情報", index=False)
        
        # ===== シート7: サマリー =====
        summary_data = {
            "項目": [
                "総作品数",
                "調査完了作品数",
                "未調査作品数",
                "確認済みキャスト数",
                "データ作成日時",
                "最終更新日時",
            ],
            "値": [
                len(movies),
                len([m for m in movies if m.get('book_title', '') in KNOWN_JAPANESE_CAST]),
                len([m for m in movies if m.get('book_title', '') not in KNOWN_JAPANESE_CAST]),
                sum(len(cast) for cast in KNOWN_JAPANESE_CAST.values()),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "手動更新してください",
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name="サマリー", index=False)
    
    print(f"   → 保存完了: {output_path}")


def main():
    """メイン処理"""
    print("=" * 60)
    print("🎬 ReelShort 日本オリジナル作品 キャスト情報整理")
    print("=" * 60)
    print(f"作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 作品リスト読み込み
    movies = load_movie_list()
    
    if not movies:
        print("❌ 作品リストを読み込めませんでした")
        return
    
    print(f"\n📂 読み込んだ作品数: {len(movies)}")
    
    # 確認済み情報の表示
    print(f"\n✅ 確認済みキャスト情報:")
    for title, cast_list in KNOWN_JAPANESE_CAST.items():
        print(f"   【{title}】")
        for cast in cast_list:
            print(f"      - {cast.get('role', '')}: {cast.get('actor_name_jp', '')}")
    
    # Excel作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"日本オリジナル作品_キャスト情報_{timestamp}.xlsx"
    
    create_comprehensive_excel(movies, str(output_path))
    
    # 完了メッセージ
    print("\n" + "=" * 60)
    print("✅ 処理完了!")
    print("=" * 60)
    
    print(f"\n📁 出力ファイル: {output_path}")
    
    print(f"\n📋 次のステップ:")
    print("   1. Excelファイルの「調査用テンプレート」シートを使用")
    print("   2. 各作品を「調査リソース」に記載のサイトで検索")
    print("   3. 発見したキャスト情報を記入")
    print("   4. 「確認済みキャスト」シートに転記")
    
    print(f"\n🔍 調査のヒント:")
    print("   - ReelShort公式Instagram/TikTokで作品名を検索")
    print("   - PR TIMESで「ReelShort + 作品名」を検索")
    print("   - noteで「nowhere film」や制作会社を検索")
    print("   - Twitterで作品名+俳優/キャストで検索")


if __name__ == "__main__":
    main()

