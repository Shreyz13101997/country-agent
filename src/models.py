"""
Data Models Module.

This module defines all data models used by the Country Information AI Agent.
It provides type-safe data classes for representing countries, intents, and agent state.

Data Models:
    - CountryData: Represents country information from REST Countries API
    - AgentState: Represents the state of the LangGraph agent
    
Architecture:
    - Uses dataclasses for clean, type-annotated data structures
    - Includes serialization methods for API compatibility
    - Provides default values where appropriate

Typical Usage:
    >>> from src.models import CountryData, AgentState
    >>> country = CountryData(name="Germany", population=83491249)
    >>> state = AgentState(user_query="Population of Germany?")
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class CountryData:
    """
    Data model for country information.
    
    This class represents the data structure returned by the REST Countries API.
    It provides type-safe access to country information with sensible defaults.
    
    Attributes:
        name: Common name of the country (e.g., "Germany")
        population: Population count (e.g., 83491249)
        capital: Capital city name (e.g., "Berlin")
        currency: Currency information with symbol (e.g., "euro (€)")
        languages: Comma-separated language names
        region: Geographic region (e.g., "Europe")
        area: Land area in square kilometers
    
    Example:
        >>> country = CountryData(
        ...     name="Germany",
        ...     population=83491249,
        ...     capital="Berlin"
        ... )
        >>> print(country.name)
        Germany
    """
    name: str
    population: Optional[int] = None
    capital: Optional[str] = None
    currency: Optional[str] = None
    languages: Optional[str] = None
    region: Optional[str] = None
    area: Optional[float] = None
    flag: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert country data to dictionary.
        
        This method serializes the CountryData object to a dictionary,
        which is useful for JSON serialization and state management.
        
        Returns:
            Dict with country information as key-value pairs
        """
        return {
            "name": self.name,
            "population": self.population,
            "capital": self.capital,
            "currency": self.currency,
            "languages": self.languages,
            "region": self.region,
            "area": self.area,
            "flag": self.flag
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CountryData":
        """
        Create CountryData from dictionary.
        
        Args:
            data: Dictionary containing country information
            
        Returns:
            CountryData instance
        """
        return cls(**data)


@dataclass
class AgentState:
    """
    Data model for LangGraph agent state.
    
    This class represents the state that flows through the LangGraph workflow.
    Each node can read from and write to this state as the agent processes a query.
    
    Attributes:
        user_query: The original user question
        country_name: Extracted country name from the query
        identified_fields: List of requested information fields
        api_response: Raw API response data
        final_answer: Generated natural language answer
        error: Error message if something went wrong
        
    Example:
        >>> state = AgentState(
        ...     user_query="Population of Germany?",
        ...     country_name="Germany",
        ...     identified_fields=["population"]
        ... )
        >>> print(state.country_name)
        Germany
    """
    user_query: str
    country_name: str = ""
    identified_fields: List[str] = None
    api_response: Optional[Dict] = None
    final_answer: str = ""
    error: Optional[str] = None
    
    def __post_init__(self):
        """
        Post-initialization processing.
        
        Sets default value for identified_fields if not provided.
        """
        if self.identified_fields is None:
            self.identified_fields = []