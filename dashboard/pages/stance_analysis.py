"""
Stance Analysis Dashboard Page - Display and browse stance analysis results
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys
from datetime import datetime
import matplotlib.pyplot as plt
# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plugins.stance_analyzer import StanceAnalyzerPlugin

st.set_page_config(
    page_title="Stance Analysis - Reddit Scraper",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Stance Analysis Dashboard")
st.markdown("""
This dashboard shows the stance analysis between discussion posts and their comments.
- **Entailment**: Comments that support or agree with the post
- **Contradiction**: Comments that disagree or contradict the post
- **Neutral**: Comments that are neither agreeing nor disagreeing
""")

@st.cache_data
def load_results():
    """加載分析結果"""
    results_file = Path("data/r_Valorant/stance_results/stance_analysis.json")
    if results_file.exists():
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def run_analysis():
    """運行新分析"""
    with st.spinner("Analyzing stances... This may take a while..."):
        plugin = StanceAnalyzerPlugin()
        plugin.run()
    st.success("Analysis complete!")
    st.rerun()

# 側邊欄控制
st.sidebar.header("🎛️ Controls")

if st.sidebar.button("🔄 Run Analysis", use_container_width=True):
    run_analysis()

# 載入結果
results = load_results()

if results is None:
    st.warning("No analysis results found. Click 'Run Analysis' to start.")
    if st.button("▶️ Run Analysis Now", use_container_width=True):
        run_analysis()
else:
    # 整體統計
    st.header("📊 Overall Statistics")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    total_posts = len(results)
    total_comments = 0
    stance_totals = {'agree': 0, 'disagree': 0, 'discussion': 0, 'not related': 0}
    
    for post_data in results.values():
        for stance in stance_totals:
            count = post_data['stance_counts'][stance]
            stance_totals[stance] += count
            total_comments += count
    
    with col1:
        st.metric("Posts Analyzed", total_posts)
    with col2:
        st.metric("Total Comments", total_comments)
    with col3:
        st.metric("Agree", stance_totals['agree'])
    with col4:
        st.metric("Disagree", stance_totals['disagree'])
    with col5:
        st.metric("Discussion", stance_totals['discussion'])
    with col6:
        st.metric("Not Related", stance_totals['not related'])
    
    # 立場分佈圖表
    st.subheader("Stance Distribution")
    
    stance_data = pd.DataFrame({
        'Stance': list(stance_totals.keys()),
        'Count': list(stance_totals.values())
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.bar_chart(
            stance_data.set_index('Stance')
        )

    with col2:

        fig, ax = plt.subplots()

        ax.pie(
            stance_data['Count'],
            labels=stance_data['Stance'],
            autopct='%1.1f%%'
        )

        ax.set_title("Stance Distribution")

        st.pyplot(fig)
    
    # 瀏覽單個 post
    st.header("🔍 Browse Posts")
    
    # 建立 post 清單
    post_list = []
    for post_id, post_data in results.items():
        total = sum(post_data['stance_counts'].values())
        post_list.append({
            'post_id': post_id,
            'title': post_data['post_title'],
            'agree': post_data['stance_counts']['agree'],
            'disagree': post_data['stance_counts']['disagree'],
            'discussion': post_data['stance_counts']['discussion'],
            'not related': post_data['stance_counts']['not related'],
            'total': total
        })
    posts_df = pd.DataFrame(post_list)
    
    # 排序選項
    sort_by = st.selectbox(
        "Sort by:",
        ["Total Comments", "Agree", "Disagree", "Discussion", "Not Related", "Title"]
    )
    
    sort_column_map = {
        "Total Comments": "total",
        "Agree": "agree",
        "Disagree": "disagree",
        "Discussion": "discussion",
        "Not Related": "not related",
        "Title": "title"
    }
    
    posts_df_sorted = posts_df.sort_values(sort_column_map[sort_by], ascending=False)
    
    # 顯示 post 列表
    selected_post = st.selectbox(
        "Select a post to view details:",
        options=posts_df_sorted['post_id'].tolist(),
        format_func=lambda x:
        f"{results[x]['post_title'][:60]}... "
        f"(A:{results[x]['stance_counts']['agree']} | "
        f"D:{results[x]['stance_counts']['disagree']} | "
        f"DS:{results[x]['stance_counts']['discussion']} | "
        f"NR:{results[x]['stance_counts']['not related']})" )
    
    if selected_post:
        post_data = results[selected_post]
        
        st.subheader(f"📌 {post_data['post_title']}")
        
        # 顯示 post 內容
        with st.expander("View Post Content"):
            st.text(post_data['post_text'])
        
        # 顯示立場統計
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "✅ Agree (Support)",
                post_data['stance_counts']['agree'],
                help="Comments that support or agree with the post"
            )
        
        with col2:
            st.metric(
                "❌ Disagree (Contradiction)",
                post_data['stance_counts']['disagree'],
                help="Comments that disagree or contradict the post"
            )
        
        with col3:
            st.metric(
                "➖ Discussion",
                post_data['stance_counts']['discussion'],
                help="Comments that are discussing or exploring the post"
            )

        with col4:
            st.metric(
                "🚫 Not related",
                post_data['stance_counts']['not related'],
                help="Comments that are not related to the post"
            )
        
        # 顯示各類別的 comments
        st.subheader("💬 Comments by Stance")
        
        tabs = st.tabs(["agree", "disagree", "discussion", "not related"])
        stances = ['agree', 'disagree', 'discussion', 'not related']
        
        for tab, stance in zip(tabs, stances):
            with tab:
                comments = post_data['comments_by_stance'][stance]
                
                if not comments:
                    st.info(f"No {stance} comments found.")
                else:
                    for i, comment in enumerate(comments, 1):
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**{comment['author']}** • {comment['score']} points")
                            with col2:
                                st.caption(comment['created_utc'][:10])
                            
                            st.markdown(comment['body'])
    
    # 數據表格
    st.subheader("📋 All Posts Summary")

    st.dataframe(
        posts_df_sorted,
        use_container_width=True,
        hide_index=True,
        column_config={
            "post_id": "Post ID",
            "title": "Title",
            "agree": "✅ Agree",
            "disagree": "❌ Disagree",
            "discussion": "➖ Discussion",
            "not related": "🚫 Not related",
            "total": "Total Comments"
        }
    )
    
    # 下載結果
    st.header("📥 Export")
    
    with open("data/r_Valorant/stance_results/stance_analysis.json", 'r', encoding='utf-8') as f:
        json_data = f.read()
    
    st.download_button(
        label="Download Results as JSON",
        data=json_data,
        file_name=f"stance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
    
    # Footer
    st.divider()
    st.caption(f"Analysis updated: {post_data['analyzed_at']}")
