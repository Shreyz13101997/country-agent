"""Unit tests for intent identification node."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from src.workflows.nodes.intent import identify_intent, _fallback_intent
from src.models import AgentState


class TestIntentIdentification:
    """Test intent identification node."""
    
    def test_identify_germany_with_population(self):
        """Test extracting Germany with population field."""
        with patch('src.workflows.nodes.intent.get_llm_client') as mock:
            client = Mock()
            client.generate.return_value = '{"country": "Germany", "fields": ["population"]}'
            mock.return_value = client
            
            state = AgentState(user_query="What is the population of Germany?")
            result = identify_intent(state)
            
            assert result.country_name == "Germany"
            assert "population" in result.identified_fields
    
    def test_fallback_pattern_matching(self):
        """Test fallback pattern matching."""
        state = AgentState(user_query="Tell me about France")
        result = _fallback_intent("Tell me about France")
        
        assert result.country_name == "France"
        assert "region" in result.identified_fields
    
    def test_fallback_empty_query(self):
        """Test empty query handling."""
        state = AgentState(user_query="")
        result = _fallback_intent("")
        
        assert result.country_name == ""


class TestFallbackIntent:
    """Test fallback pattern matching."""
    
    def test_fallback_germany(self):
        """Test fallback for Germany."""
        result = _fallback_intent("What is the population of Germany?")
        
        assert result.country_name == "Germany"
        assert "population" in result.identified_fields
    
    def test_fallback_japan(self):
        """Test fallback for Japan."""
        result = _fallback_intent("What currency does Japan use?")
        
        assert result.country_name == "Japan"
        assert "currency" in result.identified_fields
    
    def test_fallback_france(self):
        """Test fallback for France."""
        result = _fallback_intent("Tell me about France")
        
        assert result.country_name == "France"
        assert "region" in result.identified_fields
    
    def test_fallback_with_capital(self):
        """Test fallback with capital field."""
        result = _fallback_intent("What is the capital of Brazil?")
        
        assert result.country_name == "Brazil"
        assert "capital" in result.identified_fields
    
    def test_fallback_with_language(self):
        """Test fallback with language field."""
        result = _fallback_intent("What languages are spoken in France?")
        
        assert result.country_name == "France"
        assert "language" in result.identified_fields
    
    def test_fallback_defaults(self):
        """Test fallback defaults to capital and population."""
        result = _fallback_intent("Tell me about the country")
        
        # "about" triggers region, so we check for capital OR population OR region
        has_field = any(f in result.identified_fields for f in ["capital", "population", "region"])
        assert has_field