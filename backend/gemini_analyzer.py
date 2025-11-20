"""
Gemini API integration for research proposal generation.
Analyzes papers and generates research gaps, questions, and methodology suggestions.
"""

import os
import requests
import json
import re
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from utils import retry_with_backoff, format_paper_for_prompt, logger

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


class GeminiError(Exception):
    """Custom exception for Gemini API errors."""
    pass


def create_analysis_prompt(topic: str, papers: List[dict]) -> str:
    """
    Create the prompt for Gemini analysis.

    Args:
        topic: Research topic
        papers: List of paper dictionaries

    Returns:
        Formatted prompt string
    """
    # Format each paper for the prompt with reference numbers
    paper_list = ""
    for i, paper in enumerate(papers, 1):
        paper_list += f"\n--- Paper [{i}] ---"
        paper_list += format_paper_for_prompt(paper, i)

    prompt = f'''You are a research intelligence assistant. Analyze the following academic papers on the topic: "{topic}"

Papers analyzed ({len(papers)} papers):
{paper_list}

Each paper includes:
- Reference number [1], [2], etc.
- Title
- Abstract
- Publication Year
- Citation Count
- Authors

Based on this analysis, provide the following in JSON format:

{{
  "research_gaps": [
    "Gap description with proper citation (Author et al., Year)",
    "Gap description with proper citation (Author, Year)",
    "Gap description with proper citation (Author & Author, Year)"
  ],
  "research_questions": [
    "Research question based on findings (Author et al., Year)",
    "Research question based on findings (Author, Year)",
    "Research question based on findings (Author & Author, Year)"
  ],
  "methodology_suggestions": [
    "Method approach based on (Author et al., Year)",
    "Method approach based on (Author, Year)",
    "Method approach based on (Author & Author, Year)"
  ],
  "novelty_assessment": "Brief explanation with citations to relevant papers (Author, Year)"
}}

IMPORTANT CITATION RULES:
1. When referencing specific papers, cite them as (Author, Year) or (Author et al., Year) for 3+ authors
2. NEVER use "Paper 1" or "Paper 12" - always use proper author citations
3. Every factual claim must reference at least one paper from the list
4. Use "et al." for papers with 3 or more authors

Example:
WRONG: "Paper 12 mentions improved accuracy..."
CORRECT: "Recent studies show improved accuracy in detection (Smith et al., 2023)..."

Focus on:
1. Identifying clear gaps in current research
2. Proposing actionable research questions
3. Suggesting proven methodologies from the analyzed papers
4. Assessing true novelty vs. incremental improvements

IMPORTANT: Return ONLY the JSON object, no additional text or markdown formatting.'''

    return prompt


@retry_with_backoff(max_retries=3, base_delay=2.0, exceptions=(requests.RequestException, GeminiError))
def analyze_papers(topic: str, papers: List[dict]) -> dict:
    """
    Send papers to Gemini for analysis and get research proposals.

    Args:
        topic: Research topic
        papers: List of paper dictionaries

    Returns:
        Dictionary with research_gaps, research_questions, methodology_suggestions, novelty_assessment

    Raises:
        GeminiError: If API request fails or response parsing fails
    """
    if not papers:
        raise GeminiError("No papers provided for analysis")

    # Create the prompt
    prompt = create_analysis_prompt(topic, papers)

    logger.info(f"Sending {len(papers)} papers to Gemini for analysis")

    # Prepare request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    try:
        response = requests.post(
            GEMINI_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 429:
            raise GeminiError("Gemini rate limit exceeded. Please try again later.")
        elif response.status_code == 400:
            raise GeminiError(f"Bad request to Gemini: {response.text}")
        elif response.status_code != 200:
            raise GeminiError(
                f"Gemini API request failed with status {response.status_code}: {response.text}"
            )

        data = response.json()

        # Extract the generated text
        if "candidates" not in data or not data["candidates"]:
            raise GeminiError("No candidates in Gemini response")

        candidate = data["candidates"][0]

        if "content" not in candidate or "parts" not in candidate["content"]:
            raise GeminiError("Invalid Gemini response structure")

        generated_text = candidate["content"]["parts"][0].get("text", "")

        if not generated_text:
            raise GeminiError("Empty response from Gemini")

        # Parse the JSON response
        analysis = parse_gemini_response(generated_text)

        logger.info("Successfully received and parsed Gemini analysis")

        return analysis

    except requests.Timeout:
        raise GeminiError("Gemini request timed out")
    except requests.RequestException as e:
        raise GeminiError(f"Gemini request failed: {str(e)}")


def parse_gemini_response(response_text: str) -> dict:
    """
    Parse the JSON response from Gemini.

    Args:
        response_text: Raw text response from Gemini

    Returns:
        Parsed dictionary with analysis results

    Raises:
        GeminiError: If JSON parsing fails
    """
    # Try to extract JSON from the response
    # Sometimes Gemini wraps JSON in markdown code blocks
    json_match = re.search(r'\{[\s\S]*\}', response_text)

    if not json_match:
        raise GeminiError("Could not find JSON in Gemini response")

    json_str = json_match.group()

    try:
        analysis = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON: {e}")
        logger.debug(f"Raw response: {response_text}")
        raise GeminiError(f"Failed to parse Gemini response as JSON: {str(e)}")

    # Validate required fields
    required_fields = ["research_gaps", "research_questions", "methodology_suggestions", "novelty_assessment"]

    for field in required_fields:
        if field not in analysis:
            logger.warning(f"Missing field '{field}' in Gemini response, using default")
            if field == "novelty_assessment":
                analysis[field] = "Analysis unavailable"
            else:
                analysis[field] = []

    # Ensure lists are actually lists
    for field in ["research_gaps", "research_questions", "methodology_suggestions"]:
        if not isinstance(analysis.get(field), list):
            analysis[field] = []

    # Ensure novelty_assessment is a string
    if not isinstance(analysis.get("novelty_assessment"), str):
        analysis["novelty_assessment"] = str(analysis.get("novelty_assessment", ""))

    return analysis


def get_default_analysis() -> dict:
    """
    Return a default analysis structure when API fails.

    Returns:
        Default analysis dictionary
    """
    return {
        "research_gaps": [
            "Unable to analyze research gaps due to API error"
        ],
        "research_questions": [
            "Unable to generate research questions due to API error"
        ],
        "methodology_suggestions": [
            "Unable to suggest methodologies due to API error"
        ],
        "novelty_assessment": "Analysis could not be completed. Please try again."
    }


def create_proposal_prompt(topic: str, papers: List[dict], analysis: dict) -> str:
    """
    Create the prompt for generating a research proposal.

    Args:
        topic: Research topic
        papers: List of paper dictionaries
        analysis: Previous analysis results

    Returns:
        Formatted prompt string
    """
    from utils import format_paper_for_prompt

    # Format papers for reference
    paper_list = ""
    for i, paper in enumerate(papers, 1):
        paper_list += f"\n--- Paper [{i}] ---"
        paper_list += format_paper_for_prompt(paper, i)

    # Include the previous analysis
    gaps = "\n".join([f"- {g}" for g in analysis.get('research_gaps', [])])
    questions = "\n".join([f"- {q}" for q in analysis.get('research_questions', [])])
    methods = "\n".join([f"- {m}" for m in analysis.get('methodology_suggestions', [])])

    prompt = f'''You are a research proposal writer. Based on the following analysis of academic papers on "{topic}", generate a complete sample research proposal.

ANALYZED PAPERS ({len(papers)} papers):
{paper_list}

PREVIOUS ANALYSIS:
Research Gaps:
{gaps}

Research Questions:
{questions}

Methodology Suggestions:
{methods}

Generate a research proposal in the following JSON format:

{{
  "title": "Proposed research title based on identified gaps",
  "introduction": "2-3 paragraphs covering: background on the topic, problem statement, and research significance. Include citations to analyzed papers.",
  "literature_review": "3-4 paragraphs summarizing current research state and identified gaps. MUST cite multiple papers from the list using (Author, Year) or (Author et al., Year) format.",
  "research_questions": [
    "Question 1 from analysis",
    "Question 2 from analysis",
    "Question 3 from analysis"
  ],
  "methodology": "2-3 paragraphs describing: proposed approach, data collection methods, and analysis techniques. Reference methodologies from analyzed papers.",
  "expected_outcomes": "1-2 paragraphs on anticipated contributions to the field",
  "timeline": "Brief project timeline (e.g., 12-18 months with phases)"
}}

IMPORTANT REQUIREMENTS:
1. Total length: 800-1200 words
2. Use proper in-text citations: (Author, Year) or (Author et al., Year) for 3+ authors
3. NEVER reference "Paper 1" or "Paper 12" - always use author citations
4. The proposal should be academically rigorous but concise
5. Ensure all sections flow logically
6. Make the research sound feasible and impactful

Return ONLY the JSON object, no additional text or markdown formatting.'''

    return prompt


@retry_with_backoff(max_retries=3, base_delay=2.0, exceptions=(requests.RequestException, GeminiError))
def generate_proposal(topic: str, papers: List[dict], analysis: dict) -> dict:
    """
    Generate a research proposal based on the analysis.

    Args:
        topic: Research topic
        papers: List of paper dictionaries
        analysis: Previous analysis results

    Returns:
        Dictionary with proposal sections

    Raises:
        GeminiError: If API request fails
    """
    if not papers or not analysis:
        raise GeminiError("Papers and analysis required for proposal generation")

    prompt = create_proposal_prompt(topic, papers, analysis)

    logger.info("Generating research proposal with Gemini...")

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    try:
        response = requests.post(
            GEMINI_URL,
            headers=headers,
            json=payload,
            timeout=90  # Longer timeout for proposal generation
        )

        if response.status_code != 200:
            raise GeminiError(
                f"Proposal generation failed with status {response.status_code}: {response.text}"
            )

        data = response.json()

        if "candidates" not in data or not data["candidates"]:
            raise GeminiError("No candidates in Gemini response for proposal")

        generated_text = data["candidates"][0]["content"]["parts"][0].get("text", "")

        if not generated_text:
            raise GeminiError("Empty proposal response from Gemini")

        # Parse the JSON response
        proposal = parse_proposal_response(generated_text)

        logger.info("Successfully generated research proposal")

        return proposal

    except requests.Timeout:
        raise GeminiError("Proposal generation timed out")
    except requests.RequestException as e:
        raise GeminiError(f"Proposal generation failed: {str(e)}")


def parse_proposal_response(response_text: str) -> dict:
    """
    Parse the proposal JSON response from Gemini.

    Args:
        response_text: Raw text response

    Returns:
        Parsed proposal dictionary
    """
    json_match = re.search(r'\{[\s\S]*\}', response_text)

    if not json_match:
        raise GeminiError("Could not find JSON in proposal response")

    try:
        proposal = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise GeminiError(f"Failed to parse proposal JSON: {str(e)}")

    # Validate required fields
    required_fields = ["title", "introduction", "literature_review", "research_questions",
                       "methodology", "expected_outcomes"]

    for field in required_fields:
        if field not in proposal:
            if field == "research_questions":
                proposal[field] = []
            else:
                proposal[field] = "Section not generated"

    return proposal


def get_default_proposal() -> dict:
    """
    Return a default proposal structure when generation fails.

    Returns:
        Default proposal dictionary
    """
    return {
        "title": "Research Proposal",
        "introduction": "Unable to generate introduction due to API error.",
        "literature_review": "Unable to generate literature review due to API error.",
        "research_questions": [],
        "methodology": "Unable to generate methodology due to API error.",
        "expected_outcomes": "Unable to generate expected outcomes due to API error.",
        "timeline": "Unable to generate timeline due to API error."
    }
