#!/usr/bin/env python3
"""
Basic Usage Example for Legal Research AI Agents

This script demonstrates the basic functionality of the legal AI agents
and serves as a starting point for beginners.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.legal_research_agent import LegalResearchAgent
from agents.document_analyzer import DocumentAnalyzer
from config.settings import settings

def main():
    """Main function demonstrating basic agent usage"""
    
    print("🏛️  Legal Research AI Agents - Basic Usage Demo")
    print("=" * 50)
    
    # Sample legal document for testing
    sample_contract = """
    CONSULTING SERVICES AGREEMENT
    
    This Consulting Services Agreement ("Agreement") is entered into on January 1, 2024,
    between TechCorp Inc., a Delaware corporation ("Client"), and Legal Advisors LLC,
    a New York limited liability company ("Consultant").
    
    1. SERVICES
    Consultant agrees to provide legal research and advisory services to Client
    as described in Exhibit A attached hereto and incorporated by reference.
    
    2. COMPENSATION
    Client shall pay Consultant $200 per hour for services performed.
    Payment is due within 30 days of invoice receipt.
    
    3. TERM
    This Agreement shall commence on January 1, 2024, and continue for
    twelve (12) months unless terminated earlier in accordance with this Agreement.
    
    4. TERMINATION
    Either party may terminate this Agreement with thirty (30) days written notice.
    
    5. CONFIDENTIALITY
    Consultant agrees to maintain confidentiality of all Client information
    and not to disclose such information to third parties.
    
    6. LIABILITY
    Consultant's liability under this Agreement shall not exceed the total
    amount of fees paid by Client to Consultant in the preceding twelve months.
    
    7. GOVERNING LAW
    This Agreement shall be governed by the laws of the State of New York.
    """
    
    # Initialize agents
    print("\n🤖 Initializing AI Agents...")
    legal_agent = LegalResearchAgent()
    doc_analyzer = DocumentAnalyzer()
    
    print(f"✅ Legal Research Agent initialized: {legal_agent.agent_type}")
    print(f"✅ Document Analyzer initialized: {doc_analyzer.agent_type}")
    
    # Demonstrate Legal Research Agent capabilities
    print("\n" + "="*50)
    print("📋 LEGAL RESEARCH AGENT DEMO")
    print("="*50)
    
    # 1. Document Analysis
    print("\n1️⃣  Analyzing Legal Document...")
    try:
        analysis_request = {
            'action': 'analyze_document',
            'content': sample_contract,
            'parameters': {}
        }
        
        analysis_response = legal_agent.process_request(analysis_request)
        
        print(f"✅ Analysis completed in {analysis_response.processing_time:.2f} seconds")
        print(f"📊 Confidence Score: {analysis_response.confidence_score}")
        print(f"🏷️  Document Type: {analysis_response.metadata.get('document_type', 'Unknown')}")
        print(f"📈 Complexity Score: {analysis_response.metadata.get('complexity_score', 'N/A')}")
        print("\n📝 Analysis Results:")
        print(analysis_response.content[:500] + "..." if len(analysis_response.content) > 500 else analysis_response.content)
        
    except Exception as e:
        print(f"❌ Error during document analysis: {e}")
    
    # 2. Contract Analysis
    print("\n2️⃣  Specialized Contract Analysis...")
    try:
        contract_request = {
            'action': 'analyze_contract',
            'content': sample_contract,
            'parameters': {}
        }
        
        contract_response = legal_agent.process_request(contract_request)
        
        print(f"✅ Contract analysis completed")
        print(f"📊 Risk Level: {contract_response.metadata.get('risk_level', 'Unknown')}")
        print(f"👥 Parties Found: {contract_response.metadata.get('parties_count', 0)}")
        print(f"📋 Key Clauses: {contract_response.metadata.get('key_clauses_count', 0)}")
        print("\n📝 Contract Analysis:")
        print(contract_response.content[:500] + "..." if len(contract_response.content) > 500 else contract_response.content)
        
    except Exception as e:
        print(f"❌ Error during contract analysis: {e}")
    
    # 3. Legal Research Query
    print("\n3️⃣  Legal Research Query...")
    try:
        research_query = "What are the key elements required for a valid contract under New York law?"
        
        research_request = {
            'action': 'research_query',
            'content': research_query,
            'parameters': {'jurisdiction': 'New York'}
        }
        
        research_response = legal_agent.process_request(research_request)
        
        print(f"✅ Research query completed")
        print(f"📍 Jurisdiction: {research_response.metadata.get('jurisdiction', 'General')}")
        print(f"🏛️  Legal Areas: {', '.join(research_response.metadata.get('legal_areas', []))}")
        print("\n📝 Research Guidance:")
        print(research_response.content[:500] + "..." if len(research_response.content) > 500 else research_response.content)
        
    except Exception as e:
        print(f"❌ Error during research query: {e}")
    
    # Demonstrate Document Analyzer capabilities
    print("\n" + "="*50)
    print("📄 DOCUMENT ANALYZER DEMO")
    print("="*50)
    
    # 1. Structure Analysis
    print("\n1️⃣  Document Structure Analysis...")
    try:
        structure_request = {
            'action': 'analyze_structure',
            'content': sample_contract,
            'parameters': {}
        }
        
        structure_response = doc_analyzer.process_request(structure_request)
        
        print(f"✅ Structure analysis completed")
        print(f"📊 Sections Found: {structure_response.metadata.get('sections', 0)}")
        print(f"📋 Headings: {structure_response.metadata.get('headings', 0)}")
        print(f"📄 Paragraphs: {structure_response.metadata.get('paragraphs', 0)}")
        print(f"📈 Readability Score: {structure_response.metadata.get('readability_score', 'N/A')}")
        print("\n📝 Structure Analysis:")
        print(structure_response.content[:500] + "..." if len(structure_response.content) > 500 else structure_response.content)
        
    except Exception as e:
        print(f"❌ Error during structure analysis: {e}")
    
    # 2. Entity Extraction
    print("\n2️⃣  Entity Extraction...")
    try:
        entity_request = {
            'action': 'extract_entities',
            'content': sample_contract,
            'parameters': {}
        }
        
        entity_response = doc_analyzer.process_request(entity_request)
        
        print(f"✅ Entity extraction completed")
        print(f"🔍 Total Entities: {entity_response.metadata.get('total_entities', 0)}")
        print(f"📋 Entity Types: {', '.join(entity_response.metadata.get('entity_types', []))}")
        print("\n📝 Extracted Entities:")
        print(entity_response.content[:500] + "..." if len(entity_response.content) > 500 else entity_response.content)
        
    except Exception as e:
        print(f"❌ Error during entity extraction: {e}")
    
    # 3. Content Summarization
    print("\n3️⃣  Content Summarization...")
    try:
        summary_request = {
            'action': 'summarize_content',
            'content': sample_contract,
            'parameters': {'summary_length': 'medium'}
        }
        
        summary_response = doc_analyzer.process_request(summary_request)
        
        print(f"✅ Summarization completed")
        print(f"📊 Original Length: {summary_response.metadata.get('original_length', 0)} words")
        print(f"📋 Summary Type: {summary_response.metadata.get('summary_type', 'N/A')}")
        print("\n📝 Document Summary:")
        print(summary_response.content)
        
    except Exception as e:
        print(f"❌ Error during summarization: {e}")
    
    # Agent Capabilities and Health Check
    print("\n" + "="*50)
    print("🔧 AGENT CAPABILITIES & HEALTH")
    print("="*50)
    
    # Legal Research Agent capabilities
    print("\n📋 Legal Research Agent Capabilities:")
    legal_capabilities = legal_agent.get_capabilities()
    for key, value in legal_capabilities.items():
        if isinstance(value, list):
            print(f"  {key}: {', '.join(value)}")
        else:
            print(f"  {key}: {value}")
    
    # Document Analyzer capabilities
    print("\n📋 Document Analyzer Capabilities:")
    doc_capabilities = doc_analyzer.get_capabilities()
    for key, value in doc_capabilities.items():
        if isinstance(value, list):
            print(f"  {key}: {', '.join(value)}")
        else:
            print(f"  {key}: {value}")
    
    # Health checks
    print("\n🏥 Health Checks:")
    legal_health = legal_agent.health_check()
    doc_health = doc_analyzer.health_check()
    
    print(f"  Legal Research Agent: {legal_health['status']}")
    print(f"  Document Analyzer: {doc_health['status']}")
    
    # Tips for beginners
    print("\n" + "="*50)
    print("💡 TIPS FOR BEGINNERS")
    print("="*50)
    
    tips = [
        "Start with simple documents to understand agent responses",
        "Use the 'analyze_document' action for general legal document analysis",
        "Try 'analyze_contract' for specialized contract review",
        "Use 'research_query' to get guidance on legal research topics",
        "Experiment with different summary lengths: 'brief', 'medium', 'detailed'",
        "Check agent health and capabilities before processing large documents",
        "Review the metadata in responses for additional insights",
        "Use the confidence scores to gauge the reliability of responses"
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"  {i}. {tip}")
    
    print("\n" + "="*50)
    print("🎉 Demo completed successfully!")
    print("📚 Next steps:")
    print("  - Try with your own legal documents")
    print("  - Explore other examples in the examples/ directory")
    print("  - Read the full documentation in README.md")
    print("  - Run the test suite: python -m pytest tests/")
    print("="*50)

if __name__ == "__main__":
    main()