"""
Semantic Scholar API wrapper for fetching academic papers.
Implements rate limiting and retry logic.
"""

import os
import requests
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
from utils import semantic_scholar_limiter, retry_with_backoff, logger

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# API Configuration
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

if not SEMANTIC_SCHOLAR_API_KEY:
    logger.warning("SEMANTIC_SCHOLAR_API_KEY not found in environment variables")
BASE_URL = "https://api.semanticscholar.org/graph/v1"
PAPERS_PER_REQUEST = 50

# Fields to retrieve for each paper
PAPER_FIELDS = "title,abstract,year,citationCount,authors,url,externalIds,venue,journal"


class SemanticScholarError(Exception):
    """Custom exception for Semantic Scholar API errors."""
    pass


@retry_with_backoff(max_retries=3, base_delay=2.0, exceptions=(requests.RequestException, SemanticScholarError))
def search_papers(topic: str, limit: int = PAPERS_PER_REQUEST) -> List[dict]:
    """
    Search for papers on a given topic using Semantic Scholar API.

    Args:
        topic: Research topic to search for
        limit: Maximum number of papers to retrieve (default:25)

    Returns:
        List of paper dictionaries with title, abstract, year, citationCount, authors

    Raises:
        SemanticScholarError: If API request fails after retries
    """
    # Wait for rate limiter
    semantic_scholar_limiter.wait()

    url = f"{BASE_URL}/paper/search"
    headers = {
        "x-api-key": SEMANTIC_SCHOLAR_API_KEY
    }
    params = {
        "query": topic,
        "limit": limit,
        "fields": PAPER_FIELDS
    }

    logger.info(f"Searching Semantic Scholar for: {topic}")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 429:
            raise SemanticScholarError("Rate limit exceeded. Please wait before retrying.")
        elif response.status_code == 400:
            raise SemanticScholarError(f"Bad request: {response.text}")
        elif response.status_code != 200:
            raise SemanticScholarError(
                f"API request failed with status {response.status_code}: {response.text}"
            )

        data = response.json()

        if "data" not in data:
            logger.warning("No 'data' field in API response")
            return []

        papers = data["data"]
        logger.info(f"Retrieved {len(papers)} papers from Semantic Scholar")

        return papers

    except requests.Timeout:
        raise SemanticScholarError("Request timed out")
    except requests.RequestException as e:
        raise SemanticScholarError(f"Request failed: {str(e)}")


def fetch_and_process_papers(topic: str) -> List[dict]:
    """
    Fetch papers and process them for analysis.

    - Fetches up to 50 papers
    - Filters out papers without essential fields
    - Sorts by year (most recent first), then by citation count

    Args:
        topic: Research topic

    Returns:
        Processed list of paper dictionaries
    """
    # Fetch papers from API
    raw_papers = search_papers(topic)

    if not raw_papers:
        logger.warning(f"No papers found for topic: {topic}")
        return []

    # Filter and process papers
    processed_papers = []
    current_year = 2025

    for paper in raw_papers:
        # Skip papers without title
        if not paper.get("title"):
            continue

        # Extract DOI and URL for references
        external_ids = paper.get("externalIds", {}) or {}
        doi = external_ids.get("DOI", "")
        paper_url = paper.get("url", "")

        # Build reference URL (prefer DOI, fallback to Semantic Scholar URL)
        if doi:
            ref_url = f"https://doi.org/{doi}"
        else:
            ref_url = paper_url

        # Extract venue/journal information
        journal_info = paper.get("journal", {}) or {}
        venue = paper.get("venue", "") or journal_info.get("name", "")
        volume = journal_info.get("volume", "")
        pages = journal_info.get("pages", "")

        # Create processed paper entry
        processed = {
            "title": paper.get("title", ""),
            "abstract": paper.get("abstract", ""),
            "year": paper.get("year"),
            "citationCount": paper.get("citationCount", 0),
            "authors": paper.get("authors", []),
            "doi": doi,
            "url": ref_url,
            "venue": venue,
            "volume": volume,
            "pages": pages
        }

        # Calculate sort score: prioritize year first, then citations
        year = processed["year"] or 0
        citations = processed["citationCount"] or 0

        # Year as primary sort (multiply by 10000 to ensure it dominates)
        # Then add normalized citation count as secondary
        processed["_sort_score"] = (year * 10000) + min(citations, 9999)

        processed_papers.append(processed)

    # Sort by year (descending) then citations (descending)
    processed_papers.sort(key=lambda x: x.get("_sort_score", 0), reverse=True)

    # Remove internal sort score before returning
    for paper in processed_papers:
        paper.pop("_sort_score", None)

    logger.info(f"Processed {len(processed_papers)} papers for topic: {topic}")

    return processed_papers


def get_paper_summary(papers: List[dict]) -> dict:
    """
    Generate a summary of the retrieved papers.

    Args:
        papers: List of paper dictionaries

    Returns:
        Summary dictionary with counts and statistics
    """
    if not papers:
        return {
            "total_papers": 0,
            "year_range": None,
            "total_citations": 0,
            "avg_citations": 0
        }

    years = [p["year"] for p in papers if p.get("year")]
    citations = [p.get("citationCount", 0) for p in papers]

    return {
        "total_papers": len(papers),
        "year_range": {
            "min": min(years) if years else None,
            "max": max(years) if years else None
        },
        "total_citations": sum(citations),
        "avg_citations": round(sum(citations) / len(citations), 1) if citations else 0
    }
