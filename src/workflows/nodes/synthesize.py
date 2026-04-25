"""
Answer Synthesis Node Module.

This module contains the third and final node in the LangGraph workflow - Answer Synthesis.

This node is responsible for:
    1. Receiving API response data from Node 2
    2. Generating a natural language answer using LLM
    3. Falling back to template if LLM fails
    
LLM Synthesis:
    - Uses the LLM to generate conversational responses
    - Provides context-aware answers
    - Handles missing data gracefully
    
Fallback Template:
    - Used when LLM is unavailable or fails
    - Generates structured bullet-point answers
    - Always includes country name and available data
    
Flow:
    AgentState(api_response) → Try LLM
                                    → Success: Return LLM Answer
                                    → Fail: Use Template → Return

Typical Input:
    AgentState(
        user_query="Population of Germany?",
        country_name="Germany",
        identified_fields=["population"],
        api_response={"name": "Germany", "population": 83491249, ...}
    )
    
Typical Output:
    AgentState(
        user_query="Population of Germany?",
        country_name="Germany",
        identified_fields=["population"],
        api_response={...},
        final_answer="Germany has a population of 83,491,249 people."
    )
"""

from typing import Iterator
import json
import logging

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

SYSTEM_PROMPT = """You are a helpful country information assistant.
Answer the user's question based on the provided data.
Be conversational and use commas for numbers.
If data is missing, say so."""


def synthesize_answer(state: AgentState) -> AgentState:
    """
    Synthesize answer from data - Node 3 of LangGraph workflow.
    
    This function generates a natural language answer from
    the API data. It tries LLM first for better
    responses, then falls back to a template.
    
    Process:
        1. Check for errors in state
        2. Try LLM for natural response
        3. Fall back to template if LLM fails
        4. Return final answer
        
    Args:
        state: AgentState with api_response from Node 2
        
    Returns:
        Updated AgentState with final_answer
        
    Example:
        >>> state = AgentState(
        ...     user_query="Population of Germany?",
        ...     api_response={"population": 83491249}
        ... )
        >>> result = synthesize_answer(state)
        >>> print(result.final_answer)
        The population of Germany is 83,491,249.
    """
    logger.info("=" * 60)
    logger.info("NODE 3 - ANSWER SYNTHESIS")
    
    if state.error:
        logger.error(f"Error from previous node: {state.error}")
        return AgentState(
            user_query=state.user_query,
            country_name=state.country_name,
            identified_fields=state.identified_fields,
            final_answer=f"Error: {state.error}"
        )
    
    data = state.api_response
    if not data:
        logger.error("No API data available")
        return AgentState(
            user_query=state.user_query,
            country_name=state.country_name,
            identified_fields=state.identified_fields,
            final_answer="No data available for the requested country."
        )
    
    logger.info(f"Country data received: {data.get('name')}")
    
    llm = get_llm_client()
    user_prompt = f"""Question: {state.user_query}
Country: {data.get('name')}
Data: {json.dumps(data)}"""
    
    response = llm.generate(SYSTEM_PROMPT, user_prompt)
    
    if response:
        logger.info(f"LLM SYNTHESIS SUCCESS ({len(response)} chars)")
        return AgentState(
            user_query=state.user_query,
            country_name=state.country_name,
            identified_fields=state.identified_fields,
            api_response=data,
            final_answer=response
        )
    
    logger.info("Using TEMPLATE FALLBACK")
    result = _template_answer(state, data)
    logger.info(f"Template answer generated")
    
    return result


def synthesize_answer_stream(state: AgentState) -> Iterator[str]:
    """
    Synthesize answer from data with streaming - Node 3 of LangGraph workflow.
    
    Yields chunks of the answer as they are generated (like ChatGPT).
    
    Args:
        state: AgentState with api_response from Node 2
        
    Yields:
        Text chunks as they are generated
    """
    logger.info("=" * 60)
    logger.info("NODE 3 - ANSWER SYNTHESIS (STREAMING)")
    
    if state.error:
        yield f"Error: {state.error}"
        return
    
    data = state.api_response
    if not data:
        yield "No data available for the requested country."
        return
    
    logger.info(f"Country data received: {data.get('name')}")
    
    llm = get_llm_client()
    user_prompt = f"""Question: {state.user_query}
Country: {data.get('name')}
Data: {json.dumps(data)}"""
    
    try:
        for chunk in llm.generate_stream(SYSTEM_PROMPT, user_prompt):
            yield chunk
        logger.info(f"LLM STREAMING COMPLETE")
    except Exception as e:
        logger.warning(f"Streaming failed, using template: {e}")
        for chunk in _template_stream(state, data):
            yield chunk


def _template_answer(state: AgentState, data: dict) -> AgentState:
    """
    Generate answer using template when LLM is unavailable.
    
    This function creates a structured answer from the
    available country data when the LLM cannot be used.
    
    Args:
        state: Current agent state
        data: Country data dictionary
        
    Returns:
        AgentState with template-generated answer
    """
    parts = []
    
    # Add available information as bullet points
    if data.get("population"):
        parts.append(f"Population: {data['population']:,}")
    if data.get("capital"):
        parts.append(f"Capital: {data['capital']}")
    if data.get("currency"):
        parts.append(f"Currency: {data['currency']}")
    if data.get("languages"):
        parts.append(f"Languages: {data['languages']}")
    if data.get("region"):
        parts.append(f"Region: {data['region']}")
    
    # Build answer
    answer = f"**{data.get('name', state.country_name)}**\n\n"
    answer += "\n".join(f"- {p}" for p in parts) if parts else "No information available"
    
    return AgentState(
        user_query=state.user_query,
        country_name=state.country_name,
        identified_fields=state.identified_fields,
        api_response=data,
        final_answer=answer
    )


def _template_stream(state: AgentState, data: dict) -> Iterator[str]:
    """Generate answer using template - streaming version."""
    name = data.get('name', state.country_name)
    yield f"**{name}**\n\n"
    
    parts = []
    if data.get("population"):
        parts.append(f"Population: {data['population']:,}")
    if data.get("capital"):
        parts.append(f"Capital: {data['capital']}")
    if data.get("currency"):
        parts.append(f"Currency: {data['currency']}")
    if data.get("languages"):
        parts.append(f"Languages: {data['languages']}")
    if data.get("region"):
        parts.append(f"Region: {data['region']}")
    
    if parts:
        for p in parts:
            yield f"- {p}\n"
    else:
        yield "No information available"