"""Unit tests for the full agent graph."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.workflows.graph import run_agent, get_workflow
from src.models import AgentState


class TestAgentGraph:
    """Test the complete agent graph."""
    
    @pytest.fixture
    def mock_workflow(self):
        """Mock the workflow."""
        with patch('src.workflows.graph.get_workflow') as mock:
            workflow = Mock()
            workflow.invoke.return_value = MagicMock(
                final_answer="Germany\n\n- Population: 83,491,249"
            )
            mock.return_value = workflow
            yield workflow
    
    def test_run_agent_germany_query(self, mock_workflow):
        """Test running agent with Germany query."""
        result = run_agent("What is the population of Germany?")
        
        assert "Germany" in result
        assert "Population" in result
    
    def test_run_agent_japan_query(self, mock_workflow):
        """Test running agent with Japan query."""
        result = run_agent("What currency does Japan use?")
        
        assert result is not None
    
    def test_workflow_creates_successfully(self):
        """Test that workflow compiles successfully."""
        workflow = get_workflow()
        
        assert workflow is not None


class TestAgentFlow:
    """Test the agent flow with mocked components."""
    
    @patch('src.workflows.graph.get_workflow')
    def test_invalid_country_handled(self, mock_get_workflow):
        """Test that invalid country returns error message."""
        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {"final_answer": "Error: Country 'InvalidCountry' not found."}
        mock_get_workflow.return_value = mock_workflow
        
        result = run_agent("What is the population of InvalidCountry?")
        
        assert "Error" in result or "not found" in result.lower()
    
    @patch('src.workflows.graph.get_workflow')
    def test_empty_query_handled(self, mock_get_workflow):
        """Test that empty query returns error."""
        mock_workflow = Mock()
        mock_workflow.invoke.return_value = {"final_answer": "Error: Could not identify a country."}
        mock_get_workflow.return_value = mock_workflow
        
        result = run_agent("")
        
        assert "Error" in result or "country" in result.lower()


class TestAgentIntegration:
    """Integration tests (requires actual API)."""
    
    @pytest.mark.integration
    def test_germany_population(self):
        """Test Germany population query."""
        result = run_agent("What is the population of Germany?")
        
        assert "Germany" in result
        assert "83" in result.replace(",", "") or "8349" in result
    
    @pytest.mark.integration
    def test_japan_currency(self):
        """Test Japan currency query."""
        result = run_agent("What currency does Japan use?")
        
        assert "Japan" in result
        assert "yen" in result.lower()
    
    @pytest.mark.integration
    def test_brazil_capital(self):
        """Test Brazil capital query."""
        result = run_agent("What is the capital of Brazil?")
        
        assert "Brazil" in result
        assert "Bras" in result
    
    @pytest.mark.integration
    def test_invalid_country_returns_error(self):
        """Test invalid country error handling."""
        result = run_agent("What is the population of InvalidCountry12345?")
        
        assert "not found" in result.lower() or "Error" in result
    
    @pytest.mark.integration
    def test_empty_query_error(self):
        """Test empty query error handling."""
        result = run_agent("")
        
        # Empty query should still try to extract
        assert result is not None or result == ""