#!/usr/bin/env python3
"""
ReelShort全作品データの可視化
- 再生数と公開日の散布図
- エピソード数と再生数/公開日のグラフ
- あらすじのワードクラウド
- 国・カテゴリ分布
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import numpy as np
from collections import Counter
import re

# 日本語フォント設定
plt.rcParams['font.family'] = ['DejaVu Sans', 'Noto Sans CJK JP', 'IPAGothic', 'TakaoGothic']
plt.rcParams['axes.unicode_minus'] = False

def objectid_to_datetime(oid):
    """MongoDB ObjectIdから作成日時を抽出"""
    if not oid or len(oid) < 8:
        return None
    try:
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

def get_category_from_t_book_id(t_book_id):
    """t_book_idからカテゴリを判定"""
    if not t_book_id:
        return "不明"
    
    prefix = t_book_id[:15] if len(t_book_id) >= 15 else t_book_id
    
    categories = {
        "149000000000000": "英語圏オリジナル",
        "140000000000000": "日本語吹き替え版",
        "149000000000002": "英語圏（シリーズ2）",
        "148000000000000": "中国語圏",
        "149000000000001": "英語圏（シリーズ1）",
        "140000200000000": "日本向けローカライズ",
        "140000000140000": "日本人キャスト",
        "149001000000000": "英語圏（プレミアム）",
        "142600000000002": "スペイン語圏",
        "142600000000000": "スペイン語圏",
        "140000000000002": "日本向け（シリーズ2）",
        "140001000000000": "日本向け（プレミアム）",
        "141000000000000": "韓国語圏",
    }
    
    return categories.get(prefix, "その他")

def get_region_from_t_book_id(t_book_id):
    """t_book_idから地域を判定"""
    if not t_book_id:
        return "不明"
    
    prefix3 = t_book_id[:3] if len(t_book_id) >= 3 else ""
    
    regions = {
        "149": "英語圏（アメリカ等）",
        "140": "日本",
        "148": "中国語圏",
        "142": "スペイン語圏",
        "141": "韓国語圏",
    }
    
    return regions.get(prefix3, "その他")

def main():
    print("="*70)
    print("ReelShort全作品データ可視化")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # データ読み込み
    with open('all_movies_basic.json', 'r', encoding='utf-8') as f:
        all_movies = json.load(f)
    
    print(f"\n総作品数: {len(all_movies)}")
    
    # DataFrameに変換
    data = []
    for m in all_movies:
        oid = m.get('_id') or m.get('book_id')
        release_dt = objectid_to_datetime(oid)
        t_book_id = m.get('t_book_id', '')
        
        data.append({
            'book_id': m.get('book_id', ''),
            't_book_id': t_book_id,
            'title': m.get('book_title', ''),
            'read_count': m.get('read_count', 0),
            'collect_count': m.get('collect_count', 0),
            'chapter_count': m.get('chapter_count', 0),
            'release_date': release_dt,
            'special_desc': m.get('special_desc', ''),
            'tags': m.get('tag', []),
            'category': get_category_from_t_book_id(t_book_id),
            'region': get_region_from_t_book_id(t_book_id),
            'is_japanese_cast': t_book_id.startswith('140000000140000')
        })
    
    df = pd.DataFrame(data)
    
    # 日付がない行を除外（可視化用）
    df_with_date = df[df['release_date'].notna()].copy()
    df_with_date['release_date_num'] = df_with_date['release_date'].apply(lambda x: x.timestamp() if x else 0)
    
    print(f"日付データあり: {len(df_with_date)}作品")
    
    # ========== 1. 日本人キャストシートを更新 ==========
    print("\n" + "="*70)
    print("1. 日本人キャスト作品のExcel更新")
    print("="*70)
    
    jp_cast_df = df[df['is_japanese_cast']].copy()
    jp_cast_df = jp_cast_df.sort_values('read_count', ascending=False)
    
    # t_book_idから番号抽出
    jp_cast_df['番号'] = jp_cast_df['t_book_id'].apply(lambda x: int(x[15:]) if len(x) > 15 else 0)
    jp_cast_df['公開日'] = jp_cast_df['release_date'].apply(lambda x: x.strftime('%Y-%m-%d') if x else '不明')
    jp_cast_df['再生数表示'] = jp_cast_df['read_count'].apply(format_number)
    jp_cast_df['いいね表示'] = jp_cast_df['collect_count'].apply(format_number)
    
    # Excel用DataFrame
    jp_excel_df = pd.DataFrame({
        '順位': range(1, len(jp_cast_df) + 1),
        '番号': jp_cast_df['番号'].values,
        'タイトル': jp_cast_df['title'].values,
        '再生数': jp_cast_df['read_count'].values,
        '再生数（表示）': jp_cast_df['再生数表示'].values,
        'いいね数': jp_cast_df['collect_count'].values,
        'エピソード数': jp_cast_df['chapter_count'].values,
        '公開日': jp_cast_df['公開日'].values,
        'あらすじ': jp_cast_df['special_desc'].apply(lambda x: x[:150] if x else '').values
    })
    
    # 公開日順シート
    jp_date_sorted = jp_cast_df.sort_values('release_date')
    jp_date_df = pd.DataFrame({
        '順位': range(1, len(jp_date_sorted) + 1),
        '公開日': jp_date_sorted['公開日'].values,
        'タイトル': jp_date_sorted['title'].values,
        '再生数': jp_date_sorted['read_count'].values,
        '再生数（表示）': jp_date_sorted['再生数表示'].values,
        'いいね数': jp_date_sorted['collect_count'].values,
        'エピソード数': jp_date_sorted['chapter_count'].values
    })
    
    # Excel保存
    with pd.ExcelWriter('japanese_cast_ranking.xlsx', engine='openpyxl') as writer:
        jp_excel_df.to_excel(writer, sheet_name='再生数順ランキング', index=False)
        jp_date_df.to_excel(writer, sheet_name='公開日順', index=False)
    
    print(f"  出力: japanese_cast_ranking.xlsx")
    
    # ========== 2. 可視化 ==========
    print("\n" + "="*70)
    print("2. 全作品データ可視化")
    print("="*70)
    
    # 図のサイズ設定
    fig = plt.figure(figsize=(20, 24))
    
    # ----- 2.1 再生数と公開日の散布図 -----
    ax1 = fig.add_subplot(3, 2, 1)
    
    colors = df_with_date['is_japanese_cast'].map({True: 'red', False: 'blue'})
    sizes = df_with_date['chapter_count'].apply(lambda x: max(10, min(x, 100)))
    
    scatter = ax1.scatter(
        df_with_date['release_date'], 
        df_with_date['read_count'],
        c=colors,
        s=sizes,
        alpha=0.5
    )
    
    ax1.set_xlabel('Release Date')
    ax1.set_ylabel('Play Count')
    ax1.set_title('Play Count vs Release Date\n(Red: Japanese Cast, Blue: Others)')
    ax1.set_yscale('log')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # ----- 2.2 エピソード数と再生数の散布図 -----
    ax2 = fig.add_subplot(3, 2, 2)
    
    ax2.scatter(
        df_with_date['chapter_count'], 
        df_with_date['read_count'],
        c=colors,
        alpha=0.5
    )
    
    ax2.set_xlabel('Episode Count')
    ax2.set_ylabel('Play Count')
    ax2.set_title('Play Count vs Episode Count\n(Red: Japanese Cast, Blue: Others)')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    
    # ----- 2.3 地域別作品数（円グラフ） -----
    ax3 = fig.add_subplot(3, 2, 3)
    
    region_counts = df['region'].value_counts()
    colors_pie = plt.cm.Set3(np.linspace(0, 1, len(region_counts)))
    
    wedges, texts, autotexts = ax3.pie(
        region_counts.values, 
        labels=region_counts.index,
        autopct='%1.1f%%',
        colors=colors_pie,
        startangle=90
    )
    ax3.set_title('Distribution by Region')
    
    # ----- 2.4 カテゴリ別作品数（横棒グラフ） -----
    ax4 = fig.add_subplot(3, 2, 4)
    
    category_counts = df['category'].value_counts()
    y_pos = np.arange(len(category_counts))
    
    bars = ax4.barh(y_pos, category_counts.values, color=plt.cm.viridis(np.linspace(0, 1, len(category_counts))))
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(category_counts.index)
    ax4.set_xlabel('Number of Works')
    ax4.set_title('Distribution by Category')
    
    for i, (count, bar) in enumerate(zip(category_counts.values, bars)):
        ax4.text(count + 5, i, str(count), va='center')
    
    # ----- 2.5 月別公開作品数 -----
    ax5 = fig.add_subplot(3, 2, 5)
    
    df_with_date['year_month'] = df_with_date['release_date'].apply(lambda x: x.strftime('%Y-%m') if x else None)
    monthly_counts = df_with_date.groupby('year_month').size()
    
    ax5.bar(range(len(monthly_counts)), monthly_counts.values, color='steelblue')
    ax5.set_xticks(range(len(monthly_counts)))
    ax5.set_xticklabels(monthly_counts.index, rotation=45, ha='right')
    ax5.set_xlabel('Month')
    ax5.set_ylabel('Number of Releases')
    ax5.set_title('Monthly Release Count')
    
    # ----- 2.6 再生数分布（ヒストグラム） -----
    ax6 = fig.add_subplot(3, 2, 6)
    
    read_counts_log = np.log10(df[df['read_count'] > 0]['read_count'])
    ax6.hist(read_counts_log, bins=30, color='coral', edgecolor='black', alpha=0.7)
    ax6.set_xlabel('Play Count (log10)')
    ax6.set_ylabel('Frequency')
    ax6.set_title('Distribution of Play Counts')
    
    # X軸ラベルを見やすく
    ticks = ax6.get_xticks()
    ax6.set_xticklabels([f'{10**int(t):,}' if t == int(t) else '' for t in ticks])
    
    plt.tight_layout()
    plt.savefig('visualizations/reelshort_overview.png', dpi=150, bbox_inches='tight')
    print(f"  出力: visualizations/reelshort_overview.png")
    plt.close()
    
    # ========== 3. ワードクラウド ==========
    print("\n" + "="*70)
    print("3. あらすじワードクラウド作成")
    print("="*70)
    
    try:
        from wordcloud import WordCloud
        
        # 全あらすじを結合
        all_desc = ' '.join(df['special_desc'].dropna().tolist())
        
        # 日本語ストップワード
        stopwords = {'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 
                     'いる', 'も', 'な', 'こと', 'として', 'い', 'や', 'など', 'その', 'から',
                     'する', 'ない', 'なる', 'この', 'という', 'ため', 'それ', 'だ', 'である',
                     '彼', '彼女', '私', '俺', '僕', '自分', '人', '女', '男', '女性', '男性',
                     'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'shall', 'can', 'to', 'of', 'in',
                     'for', 'on', 'with', 'at', 'by', 'from', 'up', 'about', 'into',
                     'over', 'after', 'and', 'but', 'or', 'as', 'if', 'when', 'than',
                     'that', 'which', 'who', 'whom', 'this', 'these', 'those', 'it', 'its',
                     'her', 'his', 'their', 'my', 'your', 'our', 'he', 'she', 'they', 'we'}
        
        # フォントパス（日本語対応）
        font_paths = [
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf'
        ]
        
        font_path = None
        import os
        for fp in font_paths:
            if os.path.exists(fp):
                font_path = fp
                break
        
        wc = WordCloud(
            width=1200, 
            height=600,
            background_color='white',
            max_words=200,
            stopwords=stopwords,
            font_path=font_path,
            colormap='viridis'
        )
        
        wc.generate(all_desc)
        
        plt.figure(figsize=(15, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud of Story Descriptions', fontsize=16)
        plt.savefig('visualizations/wordcloud_descriptions.png', dpi=150, bbox_inches='tight')
        print(f"  出力: visualizations/wordcloud_descriptions.png")
        plt.close()
        
        # タグのワードクラウド
        all_tags = []
        for tags in df['tags']:
            if isinstance(tags, list):
                all_tags.extend(tags)
        
        tag_counts = Counter(all_tags)
        
        wc_tags = WordCloud(
            width=1200, 
            height=600,
            background_color='white',
            max_words=100,
            font_path=font_path,
            colormap='plasma'
        )
        
        wc_tags.generate_from_frequencies(tag_counts)
        
        plt.figure(figsize=(15, 8))
        plt.imshow(wc_tags, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud of Tags', fontsize=16)
        plt.savefig('visualizations/wordcloud_tags.png', dpi=150, bbox_inches='tight')
        print(f"  出力: visualizations/wordcloud_tags.png")
        plt.close()
        
    except ImportError:
        print("  警告: wordcloudがインストールされていません")
    
    # ========== 4. 追加の可視化 ==========
    print("\n" + "="*70)
    print("4. 追加の可視化")
    print("="*70)
    
    fig2 = plt.figure(figsize=(20, 16))
    
    # ----- 4.1 日本人キャスト作品の詳細 -----
    ax7 = fig2.add_subplot(2, 2, 1)
    
    jp_sorted = jp_cast_df.sort_values('read_count', ascending=True)
    y_pos = np.arange(len(jp_sorted))
    
    bars = ax7.barh(y_pos, jp_sorted['read_count'].values / 1e6, color='crimson')
    ax7.set_yticks(y_pos)
    ax7.set_yticklabels([t[:20] + '...' if len(t) > 20 else t for t in jp_sorted['title'].values])
    ax7.set_xlabel('Play Count (Millions)')
    ax7.set_title('Japanese Cast Original Works - Play Count Ranking')
    
    for i, (count, bar) in enumerate(zip(jp_sorted['read_count'].values, bars)):
        ax7.text(count/1e6 + 0.2, i, format_number(count), va='center', fontsize=8)
    
    # ----- 4.2 公開日と累積再生数 -----
    ax8 = fig2.add_subplot(2, 2, 2)
    
    df_sorted = df_with_date.sort_values('release_date')
    df_sorted['cumulative_reads'] = df_sorted['read_count'].cumsum()
    
    ax8.plot(df_sorted['release_date'], df_sorted['cumulative_reads'] / 1e9, linewidth=2, color='navy')
    ax8.fill_between(df_sorted['release_date'], df_sorted['cumulative_reads'] / 1e9, alpha=0.3, color='navy')
    ax8.set_xlabel('Release Date')
    ax8.set_ylabel('Cumulative Play Count (Billions)')
    ax8.set_title('Cumulative Play Count Over Time')
    ax8.tick_params(axis='x', rotation=45)
    ax8.grid(True, alpha=0.3)
    
    # ----- 4.3 タグ別作品数TOP20 -----
    ax9 = fig2.add_subplot(2, 2, 3)
    
    tag_counts_top = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20])
    
    y_pos = np.arange(len(tag_counts_top))
    ax9.barh(y_pos, list(tag_counts_top.values()), color='teal')
    ax9.set_yticks(y_pos)
    ax9.set_yticklabels(list(tag_counts_top.keys()))
    ax9.set_xlabel('Number of Works')
    ax9.set_title('Top 20 Tags by Work Count')
    ax9.invert_yaxis()
    
    # ----- 4.4 エピソード数の分布 -----
    ax10 = fig2.add_subplot(2, 2, 4)
    
    ep_counts = df['chapter_count']
    ax10.hist(ep_counts, bins=50, color='forestgreen', edgecolor='black', alpha=0.7)
    ax10.set_xlabel('Episode Count')
    ax10.set_ylabel('Frequency')
    ax10.set_title('Distribution of Episode Counts')
    ax10.axvline(ep_counts.mean(), color='red', linestyle='--', label=f'Mean: {ep_counts.mean():.1f}')
    ax10.axvline(ep_counts.median(), color='orange', linestyle='--', label=f'Median: {ep_counts.median():.1f}')
    ax10.legend()
    
    plt.tight_layout()
    plt.savefig('visualizations/reelshort_detailed.png', dpi=150, bbox_inches='tight')
    print(f"  出力: visualizations/reelshort_detailed.png")
    plt.close()
    
    # ========== 5. 統計サマリー ==========
    print("\n" + "="*70)
    print("5. 統計サマリー")
    print("="*70)
    
    stats = {
        '総作品数': len(df),
        '総再生数': df['read_count'].sum(),
        '総いいね数': df['collect_count'].sum(),
        '平均再生数': df['read_count'].mean(),
        '中央値再生数': df['read_count'].median(),
        '平均エピソード数': df['chapter_count'].mean(),
        '日本人キャスト作品数': len(jp_cast_df),
        '日本人キャスト総再生数': jp_cast_df['read_count'].sum(),
    }
    
    for key, val in stats.items():
        if isinstance(val, float):
            print(f"  {key}: {format_number(int(val))} ({int(val):,})")
        else:
            print(f"  {key}: {format_number(val)} ({val:,})")
    
    # 統計をExcelに保存
    stats_df = pd.DataFrame([
        {'項目': k, '値': v, '表示': format_number(int(v)) if isinstance(v, (int, float)) else str(v)}
        for k, v in stats.items()
    ])
    
    # 地域別統計
    region_stats = df.groupby('region').agg({
        'read_count': ['sum', 'mean', 'count'],
        'collect_count': 'sum',
        'chapter_count': 'mean'
    }).round(0)
    region_stats.columns = ['総再生数', '平均再生数', '作品数', '総いいね数', '平均EP数']
    region_stats = region_stats.sort_values('作品数', ascending=False)
    
    # カテゴリ別統計
    category_stats = df.groupby('category').agg({
        'read_count': ['sum', 'mean', 'count'],
        'collect_count': 'sum',
        'chapter_count': 'mean'
    }).round(0)
    category_stats.columns = ['総再生数', '平均再生数', '作品数', '総いいね数', '平均EP数']
    category_stats = category_stats.sort_values('作品数', ascending=False)
    
    # 全作品データExcel
    with pd.ExcelWriter('reelshort_full_analysis.xlsx', engine='openpyxl') as writer:
        stats_df.to_excel(writer, sheet_name='統計サマリー', index=False)
        region_stats.to_excel(writer, sheet_name='地域別統計')
        category_stats.to_excel(writer, sheet_name='カテゴリ別統計')
        
        # 全作品データ
        all_data_df = pd.DataFrame({
            'タイトル': df['title'],
            '再生数': df['read_count'],
            'いいね数': df['collect_count'],
            'エピソード数': df['chapter_count'],
            '公開日': df['release_date'].apply(lambda x: x.strftime('%Y-%m-%d') if x else ''),
            'カテゴリ': df['category'],
            '地域': df['region'],
            '日本人キャスト': df['is_japanese_cast'].map({True: '○', False: ''})
        })
        all_data_df = all_data_df.sort_values('再生数', ascending=False)
        all_data_df.to_excel(writer, sheet_name='全作品データ', index=False)
    
    print(f"\n  出力: reelshort_full_analysis.xlsx")
    
    print("\n" + "="*70)
    print("完了！")
    print("="*70)
    
    return df


if __name__ == '__main__':
    import os
    os.makedirs('visualizations', exist_ok=True)
    results = main()

