"""
AWS Nova (Bedrock) integration for research proposal generation.
Analyzes papers and generates research gaps, questions, and methodology suggestions.
"""

import os
import json
import re
import boto3
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from utils import retry_with_backoff, format_paper_for_prompt, logger

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Nova model ID - using nova-lite for balanced performance
NOVA_MODEL_ID = os.getenv("NOVA_MODEL_ID", "amazon.nova-lite-v1:0")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    logger.warning("AWS credentials not found in environment variables")

# Initialize Bedrock client
def get_bedrock_client():
    """Get or create Bedrock runtime client."""
    return boto3.client(
        'bedrock-runtime',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )


class NovaError(Exception):
    """Custom exception for Nova API errors."""
    pass


# Keep GeminiError as alias for backward compatibility
GeminiError = NovaError


def create_analysis_prompt(topic: str, papers: List[dict]) -> str:
    """
    Create the prompt for Nova analysis.

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


@retry_with_backoff(max_retries=3, base_delay=2.0, exceptions=(ClientError, NovaError))
def analyze_papers(topic: str, papers: List[dict]) -> dict:
    """
    Send papers to Nova for analysis and get research proposals.

    Args:
        topic: Research topic
        papers: List of paper dictionaries

    Returns:
        Dictionary with research_gaps, research_questions, methodology_suggestions, novelty_assessment

    Raises:
        NovaError: If API request fails or response parsing fails
    """
    if not papers:
        raise NovaError("No papers provided for analysis")

    # Create the prompt
    prompt = create_analysis_prompt(topic, papers)

    logger.info(f"Sending {len(papers)} papers to Nova for analysis")

    # Prepare request payload for Nova
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 4096,
            "temperature": 0.7,
            "topP": 0.9
        }
    }

    try:
        client = get_bedrock_client()

        response = client.invoke_model(
            modelId=NOVA_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )

        # Parse the response
        response_body = json.loads(response['body'].read())

        # Extract the generated text from Nova response
        if 'output' not in response_body or 'message' not in response_body['output']:
            raise NovaError("Invalid Nova response structure")

        message = response_body['output']['message']
        if 'content' not in message or not message['content']:
            raise NovaError("No content in Nova response")

        generated_text = message['content'][0].get('text', '')

        if not generated_text:
            raise NovaError("Empty response from Nova")

        # Parse the JSON response
        analysis = parse_response(generated_text)

        logger.info("Successfully received and parsed Nova analysis")

        return analysis

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        if error_code == 'ThrottlingException':
            raise NovaError(f"Nova rate limit exceeded: {error_message}")
        elif error_code == 'ValidationException':
            raise NovaError(f"Invalid request to Nova: {error_message}")
        else:
            raise NovaError(f"Nova API error ({error_code}): {error_message}")


def parse_response(response_text: str) -> dict:
    """
    Parse the JSON response from Nova.

    Args:
        response_text: Raw text response from Nova

    Returns:
        Parsed dictionary with analysis results

    Raises:
        NovaError: If JSON parsing fails
    """
    # Try to extract JSON from the response
    # Sometimes the model wraps JSON in markdown code blocks
    json_match = re.search(r'\{[\s\S]*\}', response_text)

    if not json_match:
        raise NovaError("Could not find JSON in Nova response")

    json_str = json_match.group()

    try:
        analysis = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Nova JSON: {e}")
        logger.debug(f"Raw response: {response_text}")
        raise NovaError(f"Failed to parse Nova response as JSON: {str(e)}")

    # Validate required fields
    required_fields = ["research_gaps", "research_questions", "methodology_suggestions", "novelty_assessment"]

    for field in required_fields:
        if field not in analysis:
            logger.warning(f"Missing field '{field}' in Nova response, using default")
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


# Keep old function name as alias for backward compatibility
parse_gemini_response = parse_response


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


@retry_with_backoff(max_retries=3, base_delay=2.0, exceptions=(ClientError, NovaError))
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
        NovaError: If API request fails
    """
    if not papers or not analysis:
        raise NovaError("Papers and analysis required for proposal generation")

    prompt = create_proposal_prompt(topic, papers, analysis)

    logger.info("Generating research proposal with Nova...")

    # Prepare request payload for Nova
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 8192,
            "temperature": 0.7,
            "topP": 0.9
        }
    }

    try:
        client = get_bedrock_client()

        response = client.invoke_model(
            modelId=NOVA_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )

        # Parse the response
        response_body = json.loads(response['body'].read())

        # Extract the generated text from Nova response
        if 'output' not in response_body or 'message' not in response_body['output']:
            raise NovaError("Invalid Nova response structure for proposal")

        message = response_body['output']['message']
        if 'content' not in message or not message['content']:
            raise NovaError("No content in Nova proposal response")

        generated_text = message['content'][0].get('text', '')

        if not generated_text:
            raise NovaError("Empty proposal response from Nova")

        # Parse the JSON response
        proposal = parse_proposal_response(generated_text)

        logger.info("Successfully generated research proposal")

        return proposal

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        raise NovaError(f"Proposal generation failed ({error_code}): {error_message}")


def parse_proposal_response(response_text: str) -> dict:
    """
    Parse the proposal JSON response from Nova.

    Args:
        response_text: Raw text response

    Returns:
        Parsed proposal dictionary
    """
    json_match = re.search(r'\{[\s\S]*\}', response_text)

    if not json_match:
        raise NovaError("Could not find JSON in proposal response")

    try:
        proposal = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise NovaError(f"Failed to parse proposal JSON: {str(e)}")

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
