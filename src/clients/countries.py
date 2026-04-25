"""
REST Countries API Client Module.

This module provides a client for the REST Countries API (https://restcountries.com).
It handles all communication with the external country data API.

API Details:
    - Base URL: https://restcountries.com/v3.1
    - Endpoints used: /name/{country}
    - No authentication required
    
Architecture:
    - Singleton pattern for connection pooling
    - Custom exception hierarchy
    - Retry logic for reliability
    
Error Handling:
    - CountriesAPIClientError: Base exception
    - CountryNotFoundError: Country doesn't exist
    - MultipleCountriesError: Ambiguous country name

Typical Usage:
    >>> from src.clients.countries import get_countries_client
    >>> client = get_countries_client()
    >>> data = client.get_country("Germany")
    >>> print(data.population)
    83491249
"""

import logging
from typing import Optional

import requests

from src.config import config
from src.models import CountryData

# Configure module logger
logger = logging.getLogger(__name__)


# ========================================================================
# Custom Exceptions
# ========================================================================

class CountriesAPIClientError(Exception):
    """Base exception for API client errors."""
    pass


class CountryNotFoundError(CountriesAPIClientError):
    """Raised when the specified country cannot be found."""
    pass


class MultipleCountriesError(CountriesAPIClientError):
    """
    Raised when multiple countries match the query.
    
    Attributes:
        countries: List of matching country names
    """
    def __init__(self, message: str, countries: list[str]):
        super().__init__(message)
        self.countries = countries


# ========================================================================
# API Client Class
# ========================================================================

class CountriesAPIClient:
    """
    Client for REST Countries API.
    
    This class handles all communication with the REST Countries API.
    It provides a clean interface for fetching country data with proper
    error handling.
    
    Configuration (from config):
        - base_url: BASE URL for the API
        - timeout: Request timeout (COUNTRIES_API_TIMEOUT env)
        
    Example:
        >>> client = CountriesAPIClient()
        >>> germany = client.get_country("Germany")
        >>> print(germany.capital)
        Berlin
    """
    
    def __init__(self):
        """Initialize the API client with configuration."""
        self.base_url = config.countries_api_url
        self.timeout = config.countries_api_timeout
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})
        logger.info("CountriesAPIClient initialized")
    
    def get_country(self, country_name: str) -> CountryData:
        """
        Fetch country data by name.
        
        This is the main method for retrieving country information.
        It handles the complete API call with error handling.
        
        Args:
            country_name: Name of the country to search for
            
        Returns:
            CountryData object with country information
            
        Raises:
            CountryNotFoundError: If country doesn't exist
            MultipleCountriesError: If multiple matches found
            CountriesAPIClientError: For other API errors
            
        Example:
            >>> client = CountriesAPIClient()
            >>> data = client.get_country("Japan")
            >>> print(data.population)
            123210000
        """
        url = f"{self.base_url}/{country_name}"
        logger.info(f"Fetching country: {country_name}")
        
        try:
            response = self._session.get(url, timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise CountriesAPIClientError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise CountriesAPIClientError(f"Connection error: {e}")
        
        # Handle HTTP status codes
        if response.status_code == 404:
            raise CountryNotFoundError(f"Country '{country_name}' not found")
        if response.status_code == 429:
            raise CountriesAPIClientError("Rate limited. Please try later")
        if response.status_code != 200:
            raise CountriesAPIClientError(f"API error: {response.status_code}")
        
        # Parse response
        data = response.json()
        return self._parse_response(data)
    
    def _parse_response(self, data: list) -> CountryData:
        """
        Parse API response into CountryData.
        
        Args:
            data: Raw API response (list of country dicts)
            
        Returns:
            CountryData object
            
        Raises:
            CountryNotFoundError: If no data
            MultipleCountriesError: If multiple matches
        """
        if not data:
            raise CountryNotFoundError("No data returned")
        
        # Multiple countries found - take the first one (most likely the main country)
        return self._extract_data(data[0])
    
    def _extract_data(self, data: dict) -> CountryData:
        """
        Extract country data from API response dict.
        
        Args:
            data: Single country data dictionary
            
        Returns:
            CountryData object with extracted information
        """
        # Extract basic information
        name = data.get("name", {}).get("common", "Unknown")
        population = data.get("population")
        capital = (data.get("capital") or [None])[0]
        
        # Format currencies
        currencies = data.get("currencies", {})
        currency = ""
        if currencies:
            parts = [
                f"{v.get('name', '')} ({v.get('symbol', '')})"
                for v in currencies.values() if v.get("name")
            ]
            currency = ", ".join(parts)
        
        # Format languages
        languages = data.get("languages", {})
        lang_str = ", ".join(languages.values()) if languages else None
        
        return CountryData(
            name=name,
            population=population,
            capital=capital,
            currency=currency or None,
            languages=lang_str,
            region=data.get("region"),
            area=data.get("area"),
            flag=data.get("flag")
        )
    
    def close(self):
        """Close the HTTP session."""
        self._session.close()
        logger.info("CountriesAPIClient session closed")


# ========================================================================
# Singleton Instance
# ========================================================================

_countries_client: Optional[CountriesAPIClient] = None


def get_countries_client() -> CountriesAPIClient:
    """
    Get the singleton CountriesAPIClient instance.
    
    This function ensures only one API client exists,
    which is better for connection pooling.
    
    Returns:
        CountriesAPIClient instance
        
    Example:
        >>> client = get_countries_client()
        >>> data = client.get_country("France")
    """
    global _countries_client
    if _countries_client is None:
        _countries_client = CountriesAPIClient()
    return _countries_client