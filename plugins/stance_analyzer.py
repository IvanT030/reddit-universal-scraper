"""
Stance Analysis Plugin - Analyzes stance between posts and comments
Saves results for display in dashboard
"""
import pandas as pd
import json
from pathlib import Path
import sys
from typing import Dict, List
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from export.database import get_connection

class StanceAnalyzerPlugin:
    def __init__(self, data_dir: str = "data/r_Valorant"):
        self.data_dir = Path(data_dir)
        self.results_dir = self.data_dir / "stance_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # 初始化數據庫連接
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
    
    def load_data(self):
        """加載 posts 和 comments 數據"""
        posts_file = self.data_dir / "posts.csv"
        comments_file = self.data_dir / "comments.csv"
        
        print(f"Loading posts from {posts_file}...")
        self.posts = pd.read_csv(posts_file)
        
        print(f"Loading comments from {comments_file}...")
        self.comments = pd.read_csv(comments_file)
        
        print(f"Loaded {len(self.posts)} posts and {len(self.comments)} comments")
    
    def filter_discuss_posts(self) -> pd.DataFrame:
        """過濾 flair 為 'discussion' 的 posts"""
        discuss_posts = self.posts[
            self.posts['flair'].astype(str).str.lower().str.strip() == 'discussion'
        ].copy()
        print(f"Found {len(discuss_posts)} posts")
        return discuss_posts
    
    def get_root_comments(self) -> pd.DataFrame:
        """取得 depth=0 的 comments（根級回應）"""
        root_comments = self.comments[self.comments['depth'] == 0].copy()
        print(f"Found {len(root_comments)} root comments (depth=0)")
        return root_comments
    
    def analyze_stances(self, discuss_posts: pd.DataFrame, root_comments: pd.DataFrame) -> Dict:
        """
        分析 posts 與 comments 之間的立場
        返回 {post_id: {stance_counts: {...}, comments: [...]}}
        """
        results = {}
        
        for idx, post in discuss_posts.iterrows():
            post_id = str(post['id'])
            # 確保 post_text 是字符串，處理 NaN 值
            selftext = str(post['selftext']) if pd.notna(post['selftext']) else ''
            title = str(post['title']) if pd.notna(post['title']) else ''
            post_text = selftext if selftext.strip() else title
            
            if not post_text or len(str(post_text).strip()) < 3:
                continue
            
            # 找到回應這個 post 的所有根級 comments
            post_comments = root_comments[
                root_comments['post_permalink'].astype(str).str.contains(post_id, na=False)
            ].copy()
            
            if len(post_comments) == 0:
                continue
            
            # 批量分析立場
            text_pairs = []
            comment_ids = []
            
            for _, comment in post_comments.iterrows():
                # 確保 comment_text 是字符串，處理 NaN 值
                comment_text = str(comment['body']) if pd.notna(comment['body']) else ''
                if comment_text and len(comment_text.strip()) >= 3:
                    text_pairs.append((post_text, comment_text))
                    comment_ids.append(comment['comment_id'])
            
            if not text_pairs:
                continue
            
            from analytics.LLM_stance_detection import analyzer
            print(f"\nAnalyzing post {post_id} with {len(text_pairs)} comments...")
            stances = analyzer.analyze_batch(text_pairs)
            
            # 整理結果
            stance_counts = {
                'agree': 0,
                'disagree': 0,
                'discussion': 0,
                'not related': 0
            }
            
            comments_by_stance = {
                'agree': [],
                'disagree': [],
                'discussion': [],
                'not related': []
            }
            
            for comment_id, stance in zip(comment_ids, stances):
                stance_counts[stance] += 1
                comment_data = post_comments[post_comments['comment_id'] == comment_id].iloc[0]
                
                comments_by_stance[stance].append({
                    'comment_id': comment_id,
                    'author': str(comment_data['author']) if pd.notna(comment_data['author']) else 'Unknown',
                    'body': str(comment_data['body'])[:200] if pd.notna(comment_data['body']) else '',
                    'score': int(comment_data['score']),
                    'created_utc': str(comment_data['created_utc']) if pd.notna(comment_data['created_utc']) else ''
                })
            
            results[post_id] = {
                'post_title': title,
                'post_text': post_text[:500],  # 截斷
                'stance_counts': stance_counts,
                'comments_by_stance': comments_by_stance,
                'analyzed_at': datetime.now().isoformat()
            }
        
        return results
    
    def save_results(self, results: Dict):
        """保存結果到 JSON 文件"""
        output_file = self.results_dir / "stance_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\nResults saved to {output_file}")
        print(f"Total posts analyzed: {len(results)}")
        
        # 統計摘要
        total_comments = 0
        stance_totals = {'contradiction': 0, 'entailment': 0, 'neutral': 0}
        
        for post_data in results.values():
            for stance in stance_totals:
                count = post_data['stance_counts'][stance]
                stance_totals[stance] += count
                total_comments += count
        
        print(f"Total comments analyzed: {total_comments}")
        print(f"Stance distribution:")
        for stance, count in stance_totals.items():
            pct = (count / total_comments * 100) if total_comments > 0 else 0
            print(f"  {stance}: {count} ({pct:.1f}%)")
        
        return output_file
    
    def run(self):
        """執行完整分析"""
        self.load_data()
        discuss_posts = self.filter_discuss_posts()
        root_comments = self.get_root_comments()
        
        if len(discuss_posts) == 0 or len(root_comments) == 0:
            print("No data to analyze")
            return None
        
        results = self.analyze_stances(discuss_posts, root_comments)
        output_file = self.save_results(results)
        
        return output_file

if __name__ == "__main__":
    plugin = StanceAnalyzerPlugin()
    plugin.run()
