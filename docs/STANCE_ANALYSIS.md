# Stance Analysis Feature Documentation

## Overview

The Stance Analysis feature analyzes the relationship between Reddit discussion posts and their comments using RoBERTa-based Natural Language Inference (NLI) model. It categorizes each comment's stance relative to the post it responds to.

## Stance Categories

- **Entailment (✅)**: The comment supports, agrees with, or logically follows from the post
- **Contradiction (❌)**: The comment disagrees with or contradicts the post
- **Neutral (➖)**: The comment neither supports nor contradicts the post

## Components

### 1. Core Analysis Module (`analytics/roBerta.py`)

Enhanced RoBERTa analyzer with batch processing capabilities.

**Key Classes:**
- `RobertaAnalyzer`: Main analyzer class using CrossEncoder model
- Functions: `analyze_stance()` and `analyze_batch()`

**Usage:**
```python
from analytics.roBerta import analyzer

# Single stance analysis
stance = analyzer.analyze_stance("Post text", "Comment text")

# Batch analysis
text_pairs = [
    ("Post text", "Comment 1"),
    ("Post text", "Comment 2"),
]
stances = analyzer.analyze_batch(text_pairs)
```

### 2. Plugin: Stance Analyzer (`plugins/stance_analyzer.py`)

Orchestrates the full analysis workflow:
1. Loads posts.csv and comments.csv
2. Filters for posts with 'discussion' flair
3. Gets root-level comments (depth=0)
4. Analyzes stance between posts and comments
5. Saves results to JSON

**Running the plugin:**
```bash
python -m plugins.stance_analyzer
```

**Output:**
- Saves results to `data/r_Valorant/stance_results/stance_analysis.json`
- Contains post metadata and comment-level stance annotations

### 3. Dashboard Page (`dashboard/pages/stance_analysis.py`)

Streamlit web interface for viewing and exploring stance analysis results.

**Features:**
- Overall statistics (total posts, comments, stance distribution)
- Bar charts and pie charts of stance distribution
- Post browser with sorting options
- Detailed view of comments grouped by stance
- Export results as JSON

**Running the dashboard:**
```bash
streamlit run dashboard/app.py
```

Then navigate to "Stance Analysis" page in the sidebar.

### 4. API Endpoints (`api/server.py`)

RESTful API for programmatic access to stance analysis data.

**Available endpoints:**

#### Get Overall Statistics
```
GET /stance/stats
```
Returns total posts/comments and stance distribution with percentages.

#### Get All Posts Summary
```
GET /stance/posts
```
Returns list of all analyzed posts with stance summaries, sorted by total comments.

#### Get Specific Post Details
```
GET /stance/posts/{post_id}
```
Returns complete stance analysis for a specific post, including all comments grouped by stance.

#### Get Comments by Stance
```
GET /stance/posts/{post_id}/{stance}
```
Returns comments for a post filtered by stance (entailment, contradiction, or neutral).

**Example API Usage:**
```bash
# Get statistics
curl http://localhost:8000/stance/stats

# Get all posts
curl http://localhost:8000/stance/posts

# Get specific post
curl http://localhost:8000/stance/posts/1srepds

# Get contradiction comments for post
curl http://localhost:8000/stance/posts/1srepds/contradiction
```

## Workflow

### Initial Setup

1. Ensure you have the required dependencies:
```bash
pip install sentence-transformers numpy pandas fastapi streamlit
```

2. Prepare your data:
   - `data/r_Valorant/posts.csv` (with 'flair' column)
   - `data/r_Valorant/comments.csv` (with 'depth' and 'post_permalink' columns)

### Running Analysis

#### Option 1: Command Line
```bash
# Run the plugin
cd reddit-universal-scraper
python -m plugins.stance_analyzer
```

#### Option 2: Via Dashboard
1. Start the dashboard: `streamlit run dashboard/app.py`
2. Navigate to "Stance Analysis" page
3. Click "Run Analysis" button

#### Option 3: Via API
The API can trigger analysis (if you add an endpoint for it).

### Viewing Results

#### In Dashboard
1. Go to Streamlit dashboard: `http://localhost:8501`
2. Navigate to "Stance Analysis" page
3. View statistics and browse posts
4. Click on any post to see its comments grouped by stance

#### Via API
1. Start API server: `python api/server.py`
2. Access endpoints at `http://localhost:8000/stance/...`
3. View API documentation at `http://localhost:8000/docs`

## Data Output Format

### JSON Structure
```json
{
  "post_id": {
    "post_title": "Post title",
    "post_text": "Post content (truncated)",
    "stance_counts": {
      "contradiction": 5,
      "entailment": 10,
      "neutral": 3
    },
    "comments_by_stance": {
      "entailment": [
        {
          "comment_id": "abc123",
          "author": "username",
          "body": "Comment text",
          "score": 42,
          "created_utc": "2026-04-21T13:39:29"
        }
      ],
      "contradiction": [...],
      "neutral": [...]
    },
    "analyzed_at": "2026-05-01T12:34:56.789123"
  }
}
```

## Performance Considerations

- Model loading: ~2-3 seconds on first run (cached thereafter)
- Analysis speed: ~10-50 comments/second depending on text length
- Memory usage: ~2-4 GB with batch processing
- Batch size: Currently processes all comments at once; can be optimized with smaller batches

## Troubleshooting

### No analysis results found
- Run the analysis first using the plugin or dashboard button
- Check that `data/r_Valorant/stance_results/stance_analysis.json` exists

### Model download fails
- Ensure you have internet connection
- Model will be cached in `~/.cache/huggingface/`
- First run requires downloading the model (~500MB)

### Out of memory
- Process fewer posts at once
- Modify `stance_analyzer.py` to process in smaller batches
- Filter to specific posts before analysis

## Future Enhancements

- [ ] Batch processing with configurable chunk sizes
- [ ] Async API endpoints
- [ ] Background task scheduling
- [ ] Results caching with TTL
- [ ] Comment-to-comment stance analysis
- [ ] Export to multiple formats (CSV, Parquet, etc.)
- [ ] Real-time analysis streaming
- [ ] Custom thresholds for stance classification

## Technical Details

### Model Information
- **Model**: `cross-encoder/nli-roberta-base`
- **Type**: RoBERTa-based Natural Language Inference
- **Task**: Determines if Text A entails, contradicts, or is neutral with respect to Text B
- **Framework**: sentence-transformers (Hugging Face)

### Dependencies
- `sentence-transformers`: NLI model
- `numpy`: Numerical operations
- `pandas`: Data processing
- `fastapi`: API framework
- `streamlit`: Dashboard UI
- `torch`: Deep learning backend (installed with sentence-transformers)
