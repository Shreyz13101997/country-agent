"""
Intent Identification Node Module.

This module contains the first node in the LangGraph workflow - Intent Identification.

This node is responsible for:
    1. Receiving the user's query
    2. Extracting the country name from the query
    3. Identifying what information fields are requested (population, capital, etc.)
    
The node uses a two-stage approach:
    1. Try LLM first for intent extraction
    2. Fall back to pattern matching if LLM fails
    
Architecture:
    - Uses LLM client for intelligent extraction
    - Pattern matching as reliable fallback
    - Logging at each step for debugging

Flow:
    User Query → LLM Attempt → Success? → Yes: Return 
                                  No: Pattern Match → Return

Typical Input:
    "What is the population of Germany?"
    
Typical Output:
    AgentState(
        user_query="What is the population of Germany?",
        country_name="Germany",
        identified_fields=["population"]
    )
"""

import json
import re
import logging
from unittest.mock import Mock

from src.clients.llm import get_llm_client
from src.models import AgentState

# Configure module logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========================================================================
# System Prompt for LLM
# ========================================================================

SYSTEM_PROMPT = """You must respond with ONLY valid JSON. No other text.

Extract country and fields from the question.
Format: {"country": "name", "fields": ["field1", "field2"]}

Available fields: population, capital, currency, language, region, area, flag
Example: {"country": "Germany", "fields": ["population"]}"""


# ========================================================================
# Main Node Function
# ========================================================================

def identify_intent(state: AgentState) -> AgentState:
    """
    Identify intent from user query - Node 1 of LangGraph workflow.
    
    This function extracts the country name and requested information
    fields from the user's natural language query.
    
    Process:
        1. Try LLM first to extract country and fields
        2. Extract JSON from response (handle extra text)
        3. If LLM fails, use pattern matching fallback
        
    Args:
        state: Current agent state containing user_query
        
    Returns:
        Updated AgentState with:
            - country_name: Extracted country name
            - identified_fields: List of requested fields
            
    Example:
        >>> state = AgentState(user_query="What is Germany's population?")
        >>> result = identify_intent(state)
        >>> print(result.country_name)
        Germany
    """
    query = state.user_query
    logger.info("=" * 60)
    logger.info("NODE 1 - INTENT IDENTIFICATION")
    logger.info(f"Input query: {query}")
    
    # ========================================================================
    # Stage 1: Try LLM
    # ========================================================================
    llm = get_llm_client()
    response = llm.generate(SYSTEM_PROMPT, f"Question: {query}")
    
    if response:
        # Parse LLM response - handle extra text like "Here is JSON:"
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from text using regex
            match = re.search(r'\{[^{}]*\}', response)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    data = None
            else:
                data = None
        
        if data:
            # Extract country (safely handle None)
            country = data.get("country") or ""
            fields = data.get("fields") or ["capital", "population"]
            
            if country and isinstance(country, str):
                country = country.strip()
            
            if country:
                logger.info(f"LLM SUCCESS - Extracted country: {country}, fields: {fields}")
                return AgentState(
                    user_query=query,
                    country_name=country,
                    identified_fields=fields
                )
            else:
                logger.warning("LLM returned empty country, using fallback")
        else:
            logger.warning("LLM response invalid JSON, using fallback")
    
    # ========================================================================
    # Stage 2: Pattern Matching Fallback
    # ========================================================================
    logger.info("Using PATTERN MATCHING FALLBACK")
    result = _fallback_intent(query)
    logger.info(f"  Extracted country: {result.country_name}")
    logger.info(f"  Extracted fields: {result.identified_fields}")
    
    return result


# ========================================================================
# Pattern Matching Fallback
# ========================================================================

def _fallback_intent(query: str) -> AgentState:
    """
    Pattern matching fallback for intent extraction.
    
    This function uses simple pattern matching to extract country
    names and fields when the LLM is unavailable or fails.
    
    Known Countries:
        A predefined list of common countries is checked first.
        Additional extraction using regex patterns.
        
    Args:
        query: User's question
        
    Returns:
        AgentState with extracted information
        
    Example:
        >>> result = _fallback_intent("What currency does Japan use?")
        >>> print(result.country_name)
        Japan
    """
    q = query.lower()
    
    # Known countries list (expanding this improves coverage)
    known = {
        "germany", "japan", "brazil", "france", "canada", "italy", "spain",
        "china", "india", "australia", "mexico", "usa", "uk", "russia",
        "south korea", "north korea", "egypt", "nigeria", "south africa"
    }
    
    country = ""
    
    # Check known countries first
    for c in known:
        if c in q:
            country = c.title()
            break
    
    # Try regex patterns
    if not country:
        match = re.search(r"of\s+(\w+)", q)
        if match:
            country = match.group(1).title()
    
    # Last resort: extract any word longer than 3 chars
    if not country:
        words = query.split()
        stop = {"what", "is", "the", "of", "for", "capital", "population", 
                "tell", "me", "about", "currency", "language"}
        for w in words:
            w = w.strip("?.,!")
            if w.lower() not in stop and len(w) > 3:
                country = w.title()
                break
    
    # Identify requested fields
    fields = []
    if "population" in q: fields.append("population")
    if "capital" in q: fields.append("capital")
    if "currency" in q: fields.append("currency")
    if "language" in q: fields.append("language")
    if "region" in q or "about" in q: fields.append("region")
    
    # Default fields
    if not fields:
        fields = ["capital", "population"]
    
    return AgentState(
        user_query=query,
        country_name=country or "",
        identified_fields=fields
    )