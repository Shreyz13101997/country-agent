"""
LangGraph Workflow Definition Module.

This module creates and manages the LangGraph workflow for the Country Information Agent.

The workflow consists of 3 sequential nodes:
    1. Intent Identification - Extract country and fields from query
    2. Tool Invocation - Fetch country data from API
    3. Answer Synthesis - Generate natural language answer

Graph Structure:
    START → identify_intent → invoke_tool → synthesize_answer → END
    
Each node:
    - Receives AgentState as input
    - Returns updated AgentState
    - Passes data to the next node

Architecture:
    - StateGraph from langgraph library
    - Sequential edges between nodes
    - Singleton pattern for workflow instance

Typical Usage:
    >>> from src.workflows.graph import run_agent
    >>> result = run_agent("What is Germany's population?")
    >>> print(result)
    Germany has a population of 83,491,249.
"""

import logging
from langgraph.graph import StateGraph, END

from src.models import AgentState
from src.workflows.nodes import identify_intent, invoke_tool, synthesize_answer

# Configure module logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow.
    
    This function builds the complete workflow graph with:
    - 3 nodes (identify, fetch, synthesize)
    - Sequential edges
    - Entry point at identify
    
    Returns:
        Compiled StateGraph ready for execution
        
    Example:
        >>> workflow = create_workflow()
        >>> print(workflow)
        <langgraph.graph.StateGraph object>
    """
    logger.info("Creating LangGraph workflow...")
    
    # Create the state graph
    graph = StateGraph(AgentState)
    
    # Add the 3 nodes
    graph.add_node("identify", identify_intent)
    graph.add_node("fetch", invoke_tool)
    graph.add_node("synthesize", synthesize_answer)
    
    # Set entry point
    graph.set_entry_point("identify")
    
    # Define sequential flow
    graph.add_edge("identify", "fetch")
    graph.add_edge("fetch", "synthesize")
    graph.add_edge("synthesize", END)
    
    # Compile the graph
    compiled = graph.compile()
    logger.info("Workflow compiled successfully")
    
    return compiled


# ========================================================================
# Singleton Workflow Instance
# ========================================================================

_workflow = None


def get_workflow() -> StateGraph:
    """
    Get the singleton workflow instance.
    
    This ensures the workflow is compiled only once,
    which is more efficient for production.
    
    Returns:
        Compiled StateGraph
        
    Example:
        >>> workflow = get_workflow()
        >>> result = workflow.invoke({"user_query": "Germany?"})
    """
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow


def run_agent(query: str) -> str:
    """
    Run the complete agent with a user query.
    
    This is the main entry point for running the agent.
    It handles the full workflow and returns the final answer.
    
    Process:
        1. Create initial state from query
        2. Invoke the workflow
        3. Extract and return final answer
        
    Args:
        query: User's question about a country
        
    Returns:
        Natural language answer string
        
    Example:
        >>> answer = run_agent("What is Germany's population?")
        >>> print(answer)
        Germany has a population of 83,491,249.
    """
    logger.info("=" * 60)
    logger.info("STARTING AGENT")
    logger.info(f"User query: {query}")
    logger.info("=" * 60)
    
    # Create initial state
    state = {"user_query": query}
    
    # Run the workflow
    result = get_workflow().invoke(state)
    
    logger.info("=" * 60)
    logger.info("AGENT COMPLETE")
    logger.info("=" * 60)
    
    # Extract final answer
    if hasattr(result, "final_answer"):
        return result.final_answer
    return result.get("final_answer", "No answer generated")