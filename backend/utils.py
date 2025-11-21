"""
Utility functions including rate limiter  and retry logic.
"""

import time
import logging
from functools import wraps
from typing import Callable, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple rate limiter that ensures minimum time between calls.
    Used to comply with Semantic Scholar's 1 request per second limit.
    """

    def __init__(self, min_interval: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            min_interval: Minimum seconds between calls (default: 1.0)
        """
        self.min_interval = min_interval
        self.last_call_time = 0

    def wait(self) -> None:
        """
        Wait if necessary to maintain rate limit.
        Blocks until it's safe to make another request.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_call_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiter sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_call_time = time.time()

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to apply rate limiting to a function.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = base_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}"
                        )

            raise last_exception

        return wrapper
    return decorator


def calculate_trend_score(papers: list) -> dict:
    """
    Calculate trend score based on citation patterns.

    Compares average citations per year for recent papers (2022-2024)
    vs older papers (2019-2021).

    Args:
        papers: List of paper dictionaries with 'year' and 'citationCount'

    Returns:
        Dictionary with trend direction, percentage, and yearly data
    """
    current_year = 2024

    # Group papers by year and calculate averages
    yearly_citations = {}
    yearly_counts = {}

    for paper in papers:
        year = paper.get('year')
        citations = paper.get('citationCount', 0)

        if year and year >= 2019:
            if year not in yearly_citations:
                yearly_citations[year] = 0
                yearly_counts[year] = 0
            yearly_citations[year] += citations
            yearly_counts[year] += 1

    # Calculate average citations per year
    yearly_averages = {}
    for year in yearly_citations:
        if yearly_counts[year] > 0:
            yearly_averages[year] = yearly_citations[year] / yearly_counts[year]
        else:
            yearly_averages[year] = 0

    # Calculate averages for recent (2022-2024) vs older (2019-2021)
    recent_citations = []
    older_citations = []

    for year, avg in yearly_averages.items():
        if year >= 2022:
            recent_citations.append(avg)
        elif year >= 2019:
            older_citations.append(avg)

    # Calculate trend
    recent_avg = sum(recent_citations) / len(recent_citations) if recent_citations else 0
    older_avg = sum(older_citations) / len(older_citations) if older_citations else 0

    # Calculate growth percentage
    if older_avg > 0:
        growth_percentage = ((recent_avg - older_avg) / older_avg) * 100
    elif recent_avg > 0:
        growth_percentage = 100  # New topic, showing growth
    else:
        growth_percentage = 0

    # Determine trend direction
    if growth_percentage > 20:
        trend_direction = "heating_up"
    elif growth_percentage < -20:
        trend_direction = "cooling_down"
    else:
        trend_direction = "stable"

    # Prepare chart data (sorted by year)
    chart_data = {
        'years': sorted(yearly_averages.keys()),
        'citations': [yearly_averages[y] for y in sorted(yearly_averages.keys())]
    }

    return {
        'trend_direction': trend_direction,
        'growth_percentage': round(growth_percentage, 1),
        'recent_avg_citations': round(recent_avg, 1),
        'older_avg_citations': round(older_avg, 1),
        'chart_data': chart_data,
        'total_papers_analyzed': len(papers)
    }


def format_paper_for_prompt(paper: dict, ref_number: int = None) -> str:
    """
    Format a single paper for inclusion in the Gemini prompt.

    Args:
        paper: Paper dictionary
        ref_number: Reference number for citation purposes

    Returns:
        Formatted string representation
    """
    title = paper.get('title', 'Unknown Title')
    year = paper.get('year', 'Unknown')
    citations = paper.get('citationCount', 0)
    abstract = paper.get('abstract', 'No abstract available')

    # Truncate abstract if too long
    if abstract and len(abstract) > 500:
        abstract = abstract[:497] + "..."

    # Format authors
    authors = paper.get('authors', [])
    if authors:
        author_names = [a.get('name', 'Unknown') for a in authors[:3]]
        if len(authors) > 3:
            author_names.append(f"et al. ({len(authors)} total)")
        author_str = ", ".join(author_names)

        # Create citation format (First Author et al., Year)
        first_author_last = authors[0].get('name', 'Unknown').split()[-1] if authors else 'Unknown'
        if len(authors) >= 3:
            citation_format = f"{first_author_last} et al., {year}"
        elif len(authors) == 2:
            second_author_last = authors[1].get('name', 'Unknown').split()[-1]
            citation_format = f"{first_author_last} & {second_author_last}, {year}"
        else:
            citation_format = f"{first_author_last}, {year}"
    else:
        author_str = "Unknown authors"
        citation_format = f"Unknown, {year}"

    ref_str = f"[{ref_number}] " if ref_number else ""

    return f"""
{ref_str}Title: {title}
Authors: {author_str}
Citation format: ({citation_format})
Year: {year}
Citations: {citations}
Abstract: {abstract}
"""


def format_apa_reference(paper: dict, ref_number: int) -> dict:
    """
    Format a paper as an APA 7 reference.

    Args:
        paper: Paper dictionary
        ref_number: Reference number

    Returns:
        Dictionary with formatted reference, URL, and abstract
    """
    title = paper.get('title', 'Unknown Title')
    year = paper.get('year', 'n.d.')
    url = paper.get('url', '')
    venue = paper.get('venue', '')
    volume = paper.get('volume', '')
    pages = paper.get('pages', '')
    abstract = paper.get('abstract', '')

    # Format authors in APA style
    authors = paper.get('authors', [])
    if authors:
        author_parts = []
        for i, author in enumerate(authors[:20]):  # APA 7 lists up to 20 authors
            name = author.get('name', 'Unknown')
            name_parts = name.split()
            if len(name_parts) >= 2:
                # Last, F. M. format
                last_name = name_parts[-1]
                initials = '. '.join([n[0] for n in name_parts[:-1]]) + '.'
                author_parts.append(f"{last_name}, {initials}")
            else:
                author_parts.append(name)

        if len(authors) > 20:
            # APA 7 style: first 19, ..., last
            author_str = ', '.join(author_parts[:19]) + ', ... ' + author_parts[-1]
        elif len(authors) == 2:
            author_str = ' & '.join(author_parts)
        elif len(authors) > 2:
            author_str = ', '.join(author_parts[:-1]) + ', & ' + author_parts[-1]
        else:
            author_str = author_parts[0] if author_parts else 'Unknown'
    else:
        author_str = 'Unknown'

    # Format the reference with venue/journal info
    reference = f"{author_str} ({year}). {title}."

    # Add venue/journal information if available
    if venue:
        reference += f" {venue}"
        if volume:
            reference += f", {volume}"
        if pages:
            reference += f", {pages}"
        reference += "."

    # Add DOI/URL
    if url:
        reference += f" {url}"

    return {
        'number': ref_number,
        'reference': reference,
        'url': url,
        'abstract': abstract if abstract else 'Abstract not available',
        'title': title,
        'year': year,
        'first_author': authors[0].get('name', 'Unknown').split()[-1] if authors else 'Unknown'
    }


# Global rate limiter instance for Semantic Scholar API
semantic_scholar_limiter = RateLimiter(min_interval=1.0)
