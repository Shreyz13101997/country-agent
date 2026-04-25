"""
Tool Invocation Node Module.

This module contains the second node in the LangGraph workflow - Tool Invocation.

This node is responsible for:
    1. Receiving the extracted country name from Node 1
    2. Calling the REST Countries API to fetch country data
    3. Returning the raw API response for processing
    
API Integration:
    - UsesCountriesAPIClient for REST Countries API
    - Handles all API errors gracefully
    - Converts response to dictionary format
    
Error Handling:
    - CountryNotFoundError: Invalid country name
    - MultipleCountriesError: Ambiguous country name  
    - General API errors
    
Flow:
    AgentState(country_name) → Get Countries Client → Call API 
                                    → Return API Response
                                    → Handle Errors Gracefully

Typical Input:
    AgentState(
        user_query="Population of Germany?",
        country_name="Germany",
        identified_fields=["population"]
    )
    
Typical Output:
    AgentState(
        user_query="Population of Germany?",
        country_name="Germany",
        identified_fields=["population"],
        api_response={"name": "Germany", "population": 83491249, ...}
    )
"""

import json
import logging
import time

from src.clients.countries import get_countries_client
from src.models import AgentState

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RETRY_DELAY = 1.5


def invoke_tool(state: AgentState) -> AgentState:
    """
    Fetch country data using tool - Node 2 of LangGraph workflow.
    
    This function calls the REST Countries API to fetch
    country information based on the extracted country name.
    
    Process:
        1. Validate country name exists
        2. Call REST Countries API
        3. Handle errors gracefully
        4. Return state with API response
        
    Args:
        state: AgentState with country_name from Node 1
        
    Returns:
        Updated AgentState with:
            - api_response: Dictionary with country data
            - error: Error message if something went wrong
            
    Example:
        >>> state = AgentState(country_name="Germany")
        >>> result = invoke_tool(state)
        >>> print(result.api_response["population"])
        83491249
    """
    logger.info("=" * 60)
    logger.info("NODE 2 - TOOL INVOCATION")
    logger.info(f"Requesting data for: {state.country_name}")
    
    country = state.country_name
    
    if not country:
        logger.error("No country name provided")
        return AgentState(
            user_query=state.user_query,
            error="Please specify a country name"
        )
    
    # Retry loop
    last_error = None
    client = get_countries_client()
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"API attempt {attempt}/{MAX_RETRIES}...")
            data = client.get_country(country)
            
            logger.info(f"API SUCCESS - Country: {data.name}")
            logger.info(f"  Population: {data.population:,}" if data.population else "  Population: N/A")
            logger.info(f"  Capital: {data.capital}" if data.capital else "  Capital: N/A")
            
            return AgentState(
                user_query=state.user_query,
                country_name=state.country_name,
                identified_fields=state.identified_fields,
                api_response=data.to_dict()
            )
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Attempt {attempt} failed: {last_error}")
            
            if attempt < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
    
    # All retries failed - return friendly error
    logger.error(f"All {MAX_RETRIES} attempts failed")
    
    error_msg = _user_friendly_error(last_error, state.country_name)
    return AgentState(
        user_query=state.user_query,
        country_name=state.country_name,
        identified_fields=state.identified_fields,
        error=error_msg
    )


def _user_friendly_error(error: str, country_name: str = "") -> str:
    """Convert technical errors to friendly messages."""
    error_lower = error.lower()
    
    if "timeout" in error_lower or "timed out" in error_lower:
        return "The country service is taking too long to respond. Please try again."
    if "connection" in error_lower:
        return "Unable to connect to the country service. Please check your internet."
    if "not found" in error_lower:
        return f"Country '{country_name}' was not found." if country_name else "Country was not found."
    if "multiple" in error_lower:
        return f"Multiple countries match '{country_name}'. Please be more specific." if country_name else "Multiple countries found. Please be more specific."
    if "rate limit" in error_lower:
        return "Too many requests. Please wait a moment and try again."
    
    return f"Unable to fetch country data: {error}"