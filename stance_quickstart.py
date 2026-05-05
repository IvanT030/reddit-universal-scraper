#!/usr/bin/env python
"""
Quick Start Guide - Run this to set up and test Stance Analysis
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    print(f"✅ Success: {description}")
    return True

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║       Reddit Universal Scraper - Stance Analysis           ║
    ║                    Quick Start Guide                        ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    project_root = Path(__file__).parent
    
    # # 1. Check dependencies
    # print("\n📋 Checking dependencies...")
    # required_packages = [
    #     'pandas',
    #     'sentence_transformers',
    #     'fastapi',
    #     'streamlit',
    #     'numpy',
    #     'torch'
    # ]
    
    # missing_packages = []
    # for package in required_packages:
    #     try:
    #         __import__(package)
    #         print(f"  ✅ {package}")
    #     except ImportError:
    #         print(f"  ❌ {package}")
    #         missing_packages.append(package)
    
    # if missing_packages:
    #     print(f"\n⚠️  Installing missing packages: {', '.join(missing_packages)}")
    #     run_command(
    #         f"pip install {' '.join(missing_packages)}",
    #         "Install missing dependencies"
    #     )
    
    # 2. Check data files
    print("\n📂 Checking data files...")
    posts_file = project_root / "data" / "r_Valorant" / "posts.csv"
    comments_file = project_root / "data" / "r_Valorant" / "comments.csv"
    
    if posts_file.exists():
        print(f"  ✅ {posts_file}")
    else:
        print(f"  ⚠️  {posts_file} not found")
    
    if comments_file.exists():
        print(f"  ✅ {comments_file}")
    else:
        print(f"  ⚠️  {comments_file} not found")
    
    if not (posts_file.exists() and comments_file.exists()):
        print("\n⚠️  Data files required for analysis")
    
    # 3. Create results directory
    print("\n📁 Setting up directories...")
    results_dir = project_root / "data" / "r_Valorant" / "stance_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ Results directory ready: {results_dir}")
    
    # 4. Menu
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║                      QUICK START MENU                       ║
    ╠════════════════════════════════════════════════════════════╣
    ║  1. Run Stance Analysis                                    ║
    ║  2. Start Dashboard (Streamlit)                            ║
    ║  3. Start API Server (FastAPI)                             ║
    ║  4. View Analysis Results                                  ║
    ║  5. Install All Dependencies                               ║
    ║  0. Exit                                                   ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    while True:
        choice = input("Enter your choice (0-5): ").strip()
        
        if choice == "1":
            run_command(
                f"python -m plugins.stance_analyzer",
                "Run Stance Analysis"
            )
        
        elif choice == "2":
            print("\n📊 Starting Streamlit Dashboard...")
            print("   Open your browser to: http://localhost:8501")
            print("   Navigate to 'Stance Analysis' in the sidebar")
            run_command(
                f"streamlit run dashboard/app.py",
                "Start Streamlit Dashboard"
            )
        
        elif choice == "3":
            print("\n🚀 Starting FastAPI Server...")
            print("   API Documentation: http://localhost:8000/docs")
            print("   Stance endpoints: http://localhost:8000/docs#/Stance%20Analysis")
            run_command(
                f"python api/server.py",
                "Start API Server"
            )
        
        elif choice == "4":
            results_file = results_dir / "stance_analysis.json"
            if results_file.exists():
                print(f"\n📄 Results file: {results_file}")
                import json
                with open(results_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                total_posts = len(data)
                total_comments = sum(sum(post['stance_counts'].values()) for post in data.values())
                
                print(f"\n📊 Analysis Summary:")
                print(f"   Total posts analyzed: {total_posts}")
                print(f"   Total comments analyzed: {total_comments}")
                
                stance_totals = {'contradiction': 0, 'entailment': 0, 'neutral': 0}
                for post in data.values():
                    for stance in stance_totals:
                        stance_totals[stance] += post['stance_counts'][stance]
                
                print(f"\n   Stance Distribution:")
                for stance, count in stance_totals.items():
                    pct = (count / total_comments * 100) if total_comments > 0 else 0
                    print(f"   - {stance:15} {count:4} ({pct:5.1f}%)")
            else:
                print(f"\n⚠️  No results found at {results_file}")
                print("   Run 'option 1' to analyze first")
        
        elif choice == "5":
            run_command(
                f"pip install pandas sentence-transformers fastapi uvicorn streamlit numpy torch",
                "Install All Dependencies"
            )
        
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
