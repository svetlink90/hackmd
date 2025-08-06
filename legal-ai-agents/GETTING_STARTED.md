# Getting Started with Legal Research AI Agents

Welcome to Legal Research AI Agents! This guide will help you get started with building, testing, and deploying AI agents for legal research purposes.

## 🎯 What You'll Learn

By following this guide, you'll learn how to:
- Set up a complete AI agent development environment
- Build specialized legal research agents
- Test and validate your agents
- Deploy agents locally for production use
- Analyze legal documents and contracts
- Perform legal research queries
- Extract key information from legal texts

## 📋 Prerequisites

Before you begin, make sure you have:
- **Python 3.8 or higher** installed on your system
- **Basic Python knowledge** (variables, functions, classes)
- **Command line familiarity** (running commands in terminal)
- **Text editor or IDE** (VS Code, PyCharm, etc.)
- **Internet connection** for downloading dependencies

Optional but recommended:
- **OpenAI API key** for GPT models
- **Anthropic API key** for Claude models
- **Basic understanding of legal concepts**

## 🚀 Quick Start (5 Minutes)

### Step 1: Automatic Setup
Run the automated setup script:

```bash
# Navigate to the project directory
cd legal-ai-agents

# Run the setup script
python deployment/local_setup.py
```

This script will:
- ✅ Check your Python version
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Set up configuration files
- ✅ Run tests to verify installation
- ✅ Create convenience launch scripts

### Step 2: Try the Basic Demo
```bash
# Activate the virtual environment (if not already active)
source legal-ai-env/bin/activate  # On Linux/Mac
# OR
legal-ai-env\Scripts\activate     # On Windows

# Run the basic demo
python examples/basic_usage.py
```

### Step 3: Analyze Your Own Documents
```bash
# Run the advanced demo with your documents
python examples/document_analysis_demo.py
```

## 📖 Manual Setup (If Automatic Setup Fails)

### Step 1: Create Virtual Environment
```bash
python -m venv legal-ai-env
source legal-ai-env/bin/activate  # Linux/Mac
# OR
legal-ai-env\Scripts\activate     # Windows
```

### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
cp .env.example .env
# Edit .env file with your API keys
```

### Step 4: Test Installation
```bash
python -m pytest tests/ -v
```

## 🏗️ Project Structure Overview

```
legal-ai-agents/
├── agents/                 # Core AI agent implementations
│   ├── base_agent.py      # Base class for all agents
│   ├── legal_research_agent.py  # Legal research specialist
│   └── document_analyzer.py     # Document analysis agent
├── config/                # Configuration and settings
├── examples/              # Example usage scripts
├── tests/                 # Test suite
├── tools/                 # Utility functions
├── deployment/            # Deployment scripts
└── README.md             # Full documentation
```

## 🤖 Your First Agent

Let's create a simple legal document analyzer:

```python
from agents.legal_research_agent import LegalResearchAgent

# Initialize the agent
agent = LegalResearchAgent()

# Analyze a contract
contract_text = """
This Agreement is between Company A and Company B.
The term is 12 months with automatic renewal.
Payment terms are Net 30 days.
"""

request = {
    'action': 'analyze_contract',
    'content': contract_text,
    'parameters': {}
}

response = agent.process_request(request)
print(response.content)
```

## 📚 Core Concepts

### 1. Agents
Agents are specialized AI systems that perform specific tasks:
- **LegalResearchAgent**: Analyzes legal documents, contracts, and research queries
- **DocumentAnalyzer**: Extracts structure, entities, and key information

### 2. Actions
Each agent supports different actions:
- `analyze_document`: General legal document analysis
- `analyze_contract`: Specialized contract review
- `research_query`: Legal research guidance
- `extract_entities`: Find dates, amounts, parties, etc.
- `summarize_content`: Create document summaries

### 3. Responses
All agents return structured responses with:
- **Content**: The main analysis or answer
- **Metadata**: Additional information and statistics
- **Confidence Score**: How confident the agent is
- **Processing Time**: How long the analysis took

## 🎯 Common Use Cases

### Contract Analysis
```python
# Analyze a service agreement
response = legal_agent.process_request({
    'action': 'analyze_contract',
    'content': contract_text,
    'parameters': {}
})

print(f"Risk Level: {response.metadata['risk_level']}")
print(f"Contract Type: {response.metadata['contract_type']}")
```

### Legal Research
```python
# Research a legal question
response = legal_agent.process_request({
    'action': 'research_query',
    'content': 'What are the requirements for a valid contract?',
    'parameters': {'jurisdiction': 'New York'}
})

print(response.content)
```

### Document Comparison
```python
# Compare two contract versions
response = doc_analyzer.process_request({
    'action': 'compare_documents',
    'content': original_contract,
    'parameters': {'second_document': modified_contract}
})

print(f"Similarity: {response.metadata['similarity_score']:.2%}")
```

## 🧪 Testing Your Agents

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Test Specific Functionality
```bash
# Test legal research agent
python -m pytest tests/test_agents.py::TestLegalResearchAgent -v

# Test document analyzer
python -m pytest tests/test_agents.py::TestDocumentAnalyzer -v
```

### Create Your Own Tests
```python
def test_my_use_case():
    agent = LegalResearchAgent()
    
    response = agent.process_request({
        'action': 'analyze_document',
        'content': 'My test document...',
        'parameters': {}
    })
    
    assert response.success == True
    assert 'contract' in response.content.lower()
```

## 🔧 Configuration

### Environment Variables (.env file)
```bash
# AI Service API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Model Configuration
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=4000
TEMPERATURE=0.1

# Processing Settings
CHUNK_SIZE=1000
MAX_CONCURRENT_REQUESTS=5
```

### Custom Settings (config/settings.py)
```python
# Modify prompts, add new document types, etc.
LEGAL_DOCUMENT_TYPES = {
    "my_custom_type": {
        "keywords": ["custom", "special"],
        "analysis_focus": ["key_points", "requirements"]
    }
}
```

## 🚀 Deployment Options

### Local Development
```bash
# Run examples directly
python examples/basic_usage.py

# Use convenience scripts
./run_basic_demo.sh      # Linux/Mac
run_basic_demo.bat       # Windows
```

### Production Deployment
```bash
# Use the deployment script
python deployment/local_setup.py

# Or set up manually for production
pip install -e .
```

## 🆘 Troubleshooting

### Common Issues

**"No module named 'agents'"**
- Make sure you're in the project directory
- Activate the virtual environment
- Install dependencies: `pip install -r requirements.txt`

**"API key not found"**
- Set up your `.env` file with API keys
- The agents will work in mock mode without API keys

**Tests failing**
- This is normal without API keys
- Tests will pass in mock mode
- Check the specific error messages

**Import errors**
- Make sure all dependencies are installed
- Try: `pip install --upgrade -r requirements.txt`

### Getting Help

1. **Check the logs**: Look in the `logs/` directory
2. **Run diagnostics**: Use `agent.health_check()`
3. **Review examples**: Check `examples/` for usage patterns
4. **Read the tests**: See `tests/` for expected behavior

## 📈 Next Steps

Once you're comfortable with the basics:

1. **Explore Advanced Features**:
   - Document comparison
   - Batch processing
   - Custom prompts

2. **Integrate with Your Workflow**:
   - Add file upload capabilities
   - Create web interfaces
   - Build automation scripts

3. **Extend the System**:
   - Add new agent types
   - Implement custom document parsers
   - Create specialized legal tools

4. **Production Deployment**:
   - Set up monitoring
   - Implement caching
   - Add security measures

## 🎉 You're Ready!

Congratulations! You now have a complete legal research AI agent system. Start with the examples, experiment with your own documents, and build amazing legal AI applications!

## 📚 Additional Resources

- **Full Documentation**: `README.md`
- **API Reference**: Code comments and docstrings
- **Examples**: `examples/` directory
- **Test Suite**: `tests/` directory
- **Configuration**: `config/settings.py`

Happy coding! 🚀