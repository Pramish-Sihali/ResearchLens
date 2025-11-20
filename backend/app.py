"""
ResearchLens - Main Flask Application

Provides endpoints to analyze research topics and generate
research proposals using academic paper analysis.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from cache import cache
from semantic_scholar import fetch_and_process_papers, get_paper_summary, SemanticScholarError
from gemini_analyzer import analyze_papers, get_default_analysis, generate_proposal, get_default_proposal, GeminiError
from utils import calculate_trend_score, format_apa_reference, logger

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend access
CORS(app)

# Store papers temporarily for proposal generation
papers_store = {}


@app.route('/analyze', methods=['POST'])
def analyze_topic():
    """
    Analyze a research topic and identify gaps, questions, and methodologies.

    Request Body:
        {
            "topic": "research topic string"
        }

    Returns:
        JSON with trend analysis, research analysis, and references
    """
    # Validate request
    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON",
            "status": "error"
        }), 400

    data = request.get_json()
    topic = data.get('topic', '').strip()

    if not topic:
        return jsonify({
            "error": "Topic is required",
            "status": "error"
        }), 400

    if len(topic) < 3:
        return jsonify({
            "error": "Topic must be at least 3 characters",
            "status": "error"
        }), 400

    if len(topic) > 200:
        return jsonify({
            "error": "Topic must be less than 200 characters",
            "status": "error"
        }), 400

    logger.info(f"Received analysis request for topic: {topic}")

    # Check cache first
    cached_result = cache.get(topic)
    if cached_result:
        logger.info(f"Returning cached result for topic: {topic}")
        cached_result['from_cache'] = True
        return jsonify(cached_result)

    try:
        # Step 1: Fetch papers from Semantic Scholar
        logger.info("Fetching papers from Semantic Scholar...")
        papers = fetch_and_process_papers(topic)

        if not papers:
            return jsonify({
                "error": f"No papers found for topic: {topic}",
                "status": "error",
                "suggestion": "Try a broader or different search term"
            }), 404

        # Store papers for later proposal generation
        topic_key = topic.lower().strip()
        papers_store[topic_key] = papers

        # Step 2: Calculate trend analysis
        logger.info("Calculating trend analysis...")
        trend_analysis = calculate_trend_score(papers)

        # Step 3: Get paper summary
        paper_summary = get_paper_summary(papers)

        # Step 4: Analyze with Gemini
        logger.info("Analyzing papers with Gemini...")
        try:
            gemini_analysis = analyze_papers(topic, papers)
        except GeminiError as e:
            logger.error(f"Gemini analysis failed: {e}")
            gemini_analysis = get_default_analysis()
            gemini_analysis['error'] = str(e)

        # Step 5: Format references in APA style
        references = []
        for i, paper in enumerate(papers, 1):
            ref = format_apa_reference(paper, i)
            references.append(ref)

        # Compile results (without proposal - that's separate now)
        result = {
            "status": "success",
            "topic": topic,
            "paper_summary": paper_summary,
            "trend_analysis": trend_analysis,
            "research_gaps": gemini_analysis.get("research_gaps", []),
            "research_questions": gemini_analysis.get("research_questions", []),
            "methodology_suggestions": gemini_analysis.get("methodology_suggestions", []),
            "novelty_assessment": gemini_analysis.get("novelty_assessment", ""),
            "references": references,
            "from_cache": False
        }

        # Cache the result
        cache.set(topic, result)
        logger.info(f"Analysis complete and cached for topic: {topic}")

        return jsonify(result)

    except SemanticScholarError as e:
        logger.error(f"Semantic Scholar error: {e}")
        return jsonify({
            "error": f"Failed to fetch papers: {str(e)}",
            "status": "error"
        }), 503

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({
            "error": "An unexpected error occurred. Please try again.",
            "status": "error"
        }), 500


@app.route('/generate-proposal', methods=['POST'])
def generate_research_proposal():
    """
    Generate a research proposal based on previous analysis.

    Request Body:
        {
            "topic": "research topic string",
            "research_gaps": [...],
            "research_questions": [...],
            "methodology_suggestions": [...]
        }

    Returns:
        JSON with the generated proposal
    """
    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON",
            "status": "error"
        }), 400

    data = request.get_json()
    topic = data.get('topic', '').strip()
    research_gaps = data.get('research_gaps', [])
    research_questions = data.get('research_questions', [])
    methodology_suggestions = data.get('methodology_suggestions', [])

    if not topic:
        return jsonify({
            "error": "Topic is required",
            "status": "error"
        }), 400

    logger.info(f"Generating proposal for topic: {topic}")

    # Get stored papers
    topic_key = topic.lower().strip()
    papers = papers_store.get(topic_key, [])

    if not papers:
        # Try to fetch papers if not stored
        try:
            papers = fetch_and_process_papers(topic)
        except:
            papers = []

    # Create analysis dict for proposal generation
    analysis = {
        "research_gaps": research_gaps,
        "research_questions": research_questions,
        "methodology_suggestions": methodology_suggestions
    }

    try:
        proposal = generate_proposal(topic, papers, analysis)
        logger.info(f"Proposal generated successfully for topic: {topic}")

        return jsonify({
            "status": "success",
            "proposal": proposal
        })

    except GeminiError as e:
        logger.error(f"Proposal generation failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "proposal": get_default_proposal()
        }), 500

    except Exception as e:
        logger.error(f"Unexpected error in proposal generation: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "Failed to generate proposal",
            "proposal": get_default_proposal()
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "cache_size": cache.size()
    })


@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cached results (for debugging)."""
    cache.clear_all()
    papers_store.clear()
    return jsonify({
        "status": "success",
        "message": "Cache cleared"
    })


if __name__ == '__main__':
    logger.info("Starting ResearchLens...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
