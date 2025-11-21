# ResearchLens

A research analysis tool that analyzes academic papers to identify research trends, gaps, and generate research proposal suggestions.

## Features

- Fetches and analyzes 25 relevant papers for any research topic
- Calculates citation trend analysis with visualization
- Generates research gaps, questions, and methodology suggestions
- APA 7 formatted references with expandable abstracts
- On-demand research proposal generation
- Simple caching system (24-hour expiration)
- Clean, responsive web interface with Nunito font

## Project Structure

```
research-intelligence-agent/
├── backend/
│   ├── app.py                  # Flask application with /analyze and /generate-proposal endpoints
│   ├── semantic_scholar.py     # Paper fetching with rate limiting
│   ├── gemini_analyzer.py      # AI analysis and proposal generation
│   ├── cache.py                # Simple dict-based cache
│   └── utils.py                # Helper functions (rate limiter, APA formatting)
├── frontend/
│   └── index.html              # Single page application
├── requirements.txt
├── .env.example
└── README.md
```

## Setup & Installation

### 1. Install Python Dependencies

```bash
cd research-intelligence-agent
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

### 3. Open the Frontend

Open `frontend/index.html` in your web browser.

Or serve it with a simple HTTP server:

```bash
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080`

## Usage

1. Enter a research topic in the search box (e.g., "machine learning in healthcare")
2. Click "Analyze"
3. Wait 30-40 seconds for analysis to complete
4. View results:
   - Citation trend chart
   - Research gaps with proper citations
   - Novel research questions
   - Methodology suggestions
   - References sidebar with expandable abstracts
5. Click "Generate Research Proposal" to create a full proposal

## API Endpoints

### POST /analyze

Analyze a research topic.

**Request:**
```json
{
  "topic": "machine learning in healthcare"
}
```

**Response:**
```json
{
  "status": "success",
  "topic": "machine learning in healthcare",
  "paper_summary": {
    "total_papers": 60,
    "avg_citations": 42.5
  },
  "trend_analysis": {
    "trend_direction": "heating_up",
    "growth_percentage": 35.2,
    "chart_data": {...}
  },
  "research_gaps": [...],
  "research_questions": [...],
  "methodology_suggestions": [...],
  "novelty_assessment": "...",
  "references": [...],
  "from_cache": false
}
```

### POST /generate-proposal

Generate a research proposal based on previous analysis.

**Request:**
```json
{
  "topic": "machine learning in healthcare",
  "research_gaps": [...],
  "research_questions": [...],
  "methodology_suggestions": [...]
}
```

**Response:**
```json
{
  "status": "success",
  "proposal": {
    "title": "...",
    "introduction": "...",
    "literature_review": "...",
    "research_questions": [...],
    "methodology": "...",
    "expected_outcomes": "...",
    "timeline": "..."
  }
}
```

### GET /health

Health check endpoint.

### POST /cache/clear

Clear all cached results.

## Features Detail

### References Sidebar

- Displays all 25 analyzed papers in APA 7 format
- Collapsible with toggle button
- Each reference includes:
  - Numbered citation [1], [2], etc.
  - Full APA 7 formatted reference with venue/journal
  - Clickable link to paper (opens in new tab)
  - "View Abstract" button with expandable accordion

### Citation Format

All analysis sections use proper in-text citations:
- Single author: (Smith, 2024)
- Two authors: (Smith & Jones, 2024)
- Three or more: (Smith et al., 2024)

### Research Proposal

- Generated on-demand (separate API call)
- 7-section academic format
- Times New Roman, 12pt, double-spaced
- 800-1200 words
- Includes proper citations throughout

### Typography

- **Main App**: Nunito font (Google Fonts)
- **Research Proposal**: Times New Roman, 12pt, double-spaced

## Technical Details

- **Rate Limiting**: 1 request per second for Semantic Scholar API
- **Caching**: In-memory dict-based cache with 24-hour expiration
- **Retry Logic**: Up to 3 retries with exponential backoff for API failures
- **Paper Fields**: title, abstract, year, citationCount, authors, url, externalIds, venue, journal

## Test Topics

Try these topics to test the application:

- "machine learning in healthcare"
- "climate change mitigation strategies"
- "quantum computing applications"
- "natural language processing"
- "computer vision medical imaging"

## Troubleshooting

### CORS Errors

If you get CORS errors, make sure the Flask server is running and the frontend is accessing `http://localhost:5000`.

### API Rate Limits

The application implements proper rate limiting, but if you exceed limits, wait a few minutes before trying again.

### Empty Results

If no papers are found, try a broader search term or check that the topic is at least 3 characters.

## Limitations (MVP)

- No user authentication
- No persistent database
- No paper PDF downloading
- No save/export features
- In-memory cache only (cleared on restart)
