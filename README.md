# Country Information AI Agent

A production-grade AI agent that answers questions about countries using LangGraph.
Built with proper software engineering practices for deployment readiness.

## Features

- **3-Stage LangGraph Workflow**: Intent Identification → Tool Invocation → Answer Synthesis
- **Multiple LLM Support**: Uses DeepSeek via OpenRouter (configurable via .env)
- **Production Design**: Proper error handling, logging, configuration management
- **Modern UI**: Streamlit-based interface with dark theme
- **Unit Tests**: Comprehensive test coverage
- **Docker Ready**: Containerized for production deployment

## Quick Start

### Local Setup

```bash
# Clone or download the project
cd country-agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Edit .env with your API key (get from https://openrouter.ai/settings)
# Then run:
streamlit run app.py
```

### Open in Browser

Visit: http://localhost:8501

## Configuration (.env)

All configuration is managed via environment variables in `.env`:

```bash
# ========================================================================
# Required
# ========================================================================
OPENAI_API_KEY=your_openrouter_key  # Get from https://openrouter.ai/settings

# ========================================================================
# LLM Configuration (Optional - defaults work)
# ========================================================================
OPENROUTER_MODEL=deepseek/deepseek-chat   # See https://openrouter.ai/models
LLM_TEMPERATURE=0.1                      # 0.0 (factual) to 1.0 (creative)
LLM_MAX_TOKENS=500                       # Max response length

# ========================================================================
# API Configuration (Optional - rarely need to change)
# ========================================================================
COUNTRIES_API_URL=https://restcountries.com/v3.1/name
COUNTRIES_API_TIMEOUT=10
```

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t country-agent .

# Run with environment variables
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  -e OPENROUTER_MODEL=deepseek/deepseek-chat \
  country-agent
```

### Using Docker Compose

```bash
# Create .env file with your settings
# Then run:
docker-compose up --build
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_nodes.py -v
```

## Deployment to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Country Information AI Agent v1.0"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/country-agent.git
   git push -u origin main
   ```

2. **Deploy**:
   - Go to https://share.streamlit.io
   - Connect your GitHub account
   - Select your repository
   - Set main file: `app.py`
   - Add environment variable: `OPENAI_API_KEY`

3. **Access**: Get your deployed URL

## Project Structure

```
country-agent/
├── app.py                      # Streamlit UI entry point
├── Dockerfile                  # Production Docker
├── docker-compose.yml         # Docker Compose
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── README.md                  # This file
├── src/
│   ├── __init__.py           # Package exports
│   ├── config.py             # Configuration (loads from .env)
│   ├── models.py            # Data models (CountryData, AgentState)
│   ├── tools.py             # LangGraph tools
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── countries.py   # REST Countries API client
│   │   └── llm.py         # OpenRouter LLM client
│   └── workflows/
│       ├── __init__.py
│       ├── graph.py       # LangGraph workflow
│       └── nodes/
│           ├── __init__.py
│           ├── intent.py      # Node 1: Intent identification
│           ├── tool.py        # Node 2: Tool invocation (API call)
│           └── synthesize.py  # Node 3: Answer synthesis
└── tests/
    ├── __init__.py
    ├── test_nodes.py
    └── test_graph.py
```

## Example Questions

- "What is the population of Germany?"
- "What currency does Japan use?"
- "What is the capital and population of Brazil?"
- "What languages are spoken in France?"
- "Tell me about Canada"

## Tech Stack

| Component | Technology |
|-----------|-------------|
| Framework | LangGraph |
| UI | Streamlit |
| LLM | DeepSeek (via OpenRouter) |
| Data | REST Countries API |
| Testing | Pytest |
| Docker | Multi-stage build |

## Architecture

The agent uses a 3-node LangGraph workflow:

```
User Query
    │
    ▼
┌─────────────────────────────────┐
│  NODE 1: INTENT IDENTIFICATION  │
│  - Extract country name        │
│  - Identify requested fields   │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│  NODE 2: TOOL INVOCATION        │
│  - Call REST Countries API     │
│  - Fetch country data         │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│  NODE 3: ANSWER SYNTHESIS       │
│  - Generate natural response  │
│  - Format output               │
└───────────────┬─────────────────┘
                │
                ▼
          Final Answer
```

## License

MIT