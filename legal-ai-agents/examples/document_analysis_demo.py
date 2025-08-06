#!/usr/bin/env python3
"""
Advanced Document Analysis Demo

This script demonstrates advanced document analysis capabilities using
the existing legal documents in the workspace and shows real-world usage scenarios.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.legal_research_agent import LegalResearchAgent
from agents.document_analyzer import DocumentAnalyzer
from config.settings import settings

def load_sample_documents():
    """Load sample documents from the workspace"""
    workspace_root = Path(__file__).parent.parent.parent
    documents = {}
    
    # Look for markdown files in the workspace
    for file_path in workspace_root.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content.strip()) > 100:  # Only include substantial documents
                    documents[file_path.name] = content
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
    
    return documents

def analyze_document_batch(documents, legal_agent, doc_analyzer):
    """Analyze multiple documents and compare results"""
    print("\n📊 BATCH DOCUMENT ANALYSIS")
    print("="*50)
    
    results = {}
    
    for doc_name, content in documents.items():
        print(f"\n📄 Analyzing: {doc_name}")
        print("-" * 30)
        
        try:
            # Legal analysis
            legal_request = {
                'action': 'analyze_document',
                'content': content,
                'parameters': {}
            }
            legal_response = legal_agent.process_request(legal_request)
            
            # Structure analysis
            structure_request = {
                'action': 'analyze_structure',
                'content': content,
                'parameters': {}
            }
            structure_response = doc_analyzer.process_request(structure_request)
            
            # Entity extraction
            entity_request = {
                'action': 'extract_entities',
                'content': content,
                'parameters': {}
            }
            entity_response = doc_analyzer.process_request(entity_request)
            
            # Store results
            results[doc_name] = {
                'legal_analysis': legal_response,
                'structure_analysis': structure_response,
                'entity_extraction': entity_response,
                'word_count': len(content.split()),
                'char_count': len(content)
            }
            
            # Display summary
            print(f"✅ Legal Analysis: {legal_response.success}")
            print(f"📊 Document Type: {legal_response.metadata.get('document_type', 'Unknown')}")
            print(f"📈 Complexity: {legal_response.metadata.get('complexity_score', 'N/A')}")
            print(f"📄 Structure: {structure_response.metadata.get('sections', 0)} sections, {structure_response.metadata.get('paragraphs', 0)} paragraphs")
            print(f"🔍 Entities: {entity_response.metadata.get('total_entities', 0)} total")
            print(f"📝 Length: {len(content.split())} words, {len(content)} characters")
            
        except Exception as e:
            print(f"❌ Error analyzing {doc_name}: {e}")
            results[doc_name] = {'error': str(e)}
    
    return results

def demonstrate_advanced_features(legal_agent, doc_analyzer):
    """Demonstrate advanced features like document comparison and specialized analysis"""
    print("\n🚀 ADVANCED FEATURES DEMO")
    print("="*50)
    
    # Create two versions of a document for comparison
    original_doc = """
    PARTNERSHIP AGREEMENT
    
    This Partnership Agreement is entered into between John Smith and Jane Doe
    for the purpose of operating a consulting business.
    
    1. CAPITAL CONTRIBUTIONS
    Each partner shall contribute $10,000 in initial capital.
    
    2. PROFIT SHARING
    Profits and losses shall be shared equally between the partners.
    
    3. MANAGEMENT
    Both partners shall have equal management rights.
    """
    
    modified_doc = """
    PARTNERSHIP AGREEMENT
    
    This Partnership Agreement is entered into between John Smith and Jane Doe
    for the purpose of operating a consulting and legal services business.
    
    1. CAPITAL CONTRIBUTIONS
    John Smith shall contribute $15,000 and Jane Doe shall contribute $10,000 in initial capital.
    
    2. PROFIT SHARING
    Profits and losses shall be shared 60% to John Smith and 40% to Jane Doe.
    
    3. MANAGEMENT
    John Smith shall be the managing partner with primary decision-making authority.
    
    4. TERMINATION
    Either partner may terminate this agreement with 90 days written notice.
    """
    
    # Document comparison
    print("\n1️⃣  Document Comparison Analysis...")
    try:
        comparison_request = {
            'action': 'compare_documents',
            'content': original_doc,
            'parameters': {'second_document': modified_doc}
        }
        
        comparison_response = doc_analyzer.process_request(comparison_request)
        
        print(f"✅ Comparison completed")
        print(f"📊 Similarity Score: {comparison_response.metadata.get('similarity_score', 'N/A'):.3f}")
        print("\n📝 Comparison Results:")
        print(comparison_response.content[:800] + "..." if len(comparison_response.content) > 800 else comparison_response.content)
        
    except Exception as e:
        print(f"❌ Error during document comparison: {e}")
    
    # Legal concept extraction with explanations
    print("\n2️⃣  Legal Concept Extraction with Explanations...")
    try:
        concept_text = """
        The plaintiff alleges breach of contract and seeks damages for lost profits.
        The defendant claims force majeure due to the pandemic and argues for
        impossibility of performance. The contract contains an arbitration clause
        requiring disputes to be resolved through binding arbitration.
        """
        
        concept_request = {
            'action': 'extract_concepts',
            'content': concept_text,
            'parameters': {}
        }
        
        concept_response = legal_agent.process_request(concept_request)
        
        print(f"✅ Concept extraction completed")
        print(f"📊 Concepts Found: {concept_response.metadata.get('total_concepts', 0)}")
        print("\n📝 Legal Concepts Analysis:")
        print(concept_response.content[:800] + "..." if len(concept_response.content) > 800 else concept_response.content)
        
    except Exception as e:
        print(f"❌ Error during concept extraction: {e}")
    
    # Multi-length summarization
    print("\n3️⃣  Multi-Length Summarization...")
    long_document = """
    COMPREHENSIVE EMPLOYMENT AGREEMENT
    
    This Employment Agreement is entered into between MegaCorp Inc., a Delaware corporation
    ("Company"), and Sarah Johnson ("Employee") on March 1, 2024.
    
    RECITALS
    WHEREAS, Company desires to employ Employee in the position of Senior Legal Counsel;
    WHEREAS, Employee desires to accept such employment subject to the terms herein;
    
    NOW, THEREFORE, in consideration of the mutual covenants contained herein:
    
    1. EMPLOYMENT AND DUTIES
    Company hereby employs Employee as Senior Legal Counsel. Employee shall perform
    all duties customarily associated with such position and such other duties as
    may be assigned by the Chief Legal Officer.
    
    2. TERM
    This Agreement shall commence on March 1, 2024, and continue for a period of
    three (3) years, unless terminated earlier in accordance with the provisions hereof.
    
    3. COMPENSATION
    Company shall pay Employee an annual base salary of $150,000, payable in accordance
    with Company's standard payroll practices. Employee shall also be eligible for
    an annual bonus of up to 20% of base salary based on performance metrics.
    
    4. BENEFITS
    Employee shall be entitled to participate in all employee benefit plans generally
    available to Company's senior executives, including health insurance, dental insurance,
    vision insurance, life insurance, disability insurance, and retirement plans.
    
    5. VACATION
    Employee shall be entitled to four (4) weeks of paid vacation per year.
    
    6. CONFIDENTIALITY
    Employee acknowledges that during employment, Employee will have access to
    confidential information. Employee agrees to maintain strict confidentiality
    and not disclose such information to third parties.
    
    7. NON-COMPETE
    During employment and for one (1) year thereafter, Employee shall not engage
    in any business that competes with Company's business.
    
    8. TERMINATION
    This Agreement may be terminated by Company with or without cause upon thirty (30)
    days written notice. Employee may terminate employment upon sixty (60) days notice.
    
    9. SEVERANCE
    If terminated without cause, Employee shall receive six (6) months base salary
    as severance pay.
    
    10. GOVERNING LAW
    This Agreement shall be governed by Delaware law.
    """
    
    summary_lengths = ['brief', 'medium', 'detailed']
    
    for length in summary_lengths:
        try:
            summary_request = {
                'action': 'summarize_content',
                'content': long_document,
                'parameters': {'summary_length': length}
            }
            
            summary_response = doc_analyzer.process_request(summary_request)
            
            print(f"\n📄 {length.title()} Summary:")
            print(f"📊 Original: {summary_response.metadata.get('original_length', 0)} words")
            print("📝 Summary:")
            print(summary_response.content)
            
        except Exception as e:
            print(f"❌ Error creating {length} summary: {e}")

def demonstrate_real_world_scenarios():
    """Demonstrate real-world usage scenarios"""
    print("\n🌍 REAL-WORLD SCENARIOS")
    print("="*50)
    
    scenarios = [
        {
            'name': 'Contract Review Workflow',
            'description': 'Typical workflow for reviewing a new contract',
            'steps': [
                '1. Initial document analysis to understand type and complexity',
                '2. Specialized contract analysis for risk assessment',
                '3. Entity extraction to identify parties and key terms',
                '4. Structure analysis to ensure completeness',
                '5. Generate summary for stakeholder review'
            ]
        },
        {
            'name': 'Legal Research Project',
            'description': 'Research workflow for legal questions',
            'steps': [
                '1. Formulate research query with jurisdiction',
                '2. Extract legal concepts from source documents',
                '3. Analyze document structure for research organization',
                '4. Compare multiple legal documents for consistency',
                '5. Summarize findings for legal brief'
            ]
        },
        {
            'name': 'Document Comparison Audit',
            'description': 'Comparing contract versions for changes',
            'steps': [
                '1. Load original and modified documents',
                '2. Run document comparison analysis',
                '3. Extract entities from both versions',
                '4. Identify structural changes',
                '5. Generate change summary report'
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"📝 {scenario['description']}")
        print("🔄 Workflow Steps:")
        for step in scenario['steps']:
            print(f"   {step}")

def generate_analysis_report(results):
    """Generate a comprehensive analysis report"""
    print("\n📊 COMPREHENSIVE ANALYSIS REPORT")
    print("="*50)
    
    if not results:
        print("No documents were successfully analyzed.")
        return
    
    # Summary statistics
    total_docs = len(results)
    successful_analyses = sum(1 for r in results.values() if 'error' not in r)
    total_words = sum(r.get('word_count', 0) for r in results.values() if 'error' not in r)
    
    print(f"\n📈 Summary Statistics:")
    print(f"   Total Documents: {total_docs}")
    print(f"   Successful Analyses: {successful_analyses}")
    print(f"   Total Words Processed: {total_words:,}")
    
    # Document type distribution
    doc_types = {}
    complexity_scores = []
    
    for doc_name, result in results.items():
        if 'error' not in result and result.get('legal_analysis'):
            doc_type = result['legal_analysis'].metadata.get('document_type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            complexity = result['legal_analysis'].metadata.get('complexity_score')
            if complexity is not None:
                complexity_scores.append(complexity)
    
    print(f"\n📋 Document Types:")
    for doc_type, count in doc_types.items():
        print(f"   {doc_type.title()}: {count}")
    
    if complexity_scores:
        avg_complexity = sum(complexity_scores) / len(complexity_scores)
        print(f"\n📈 Average Complexity Score: {avg_complexity:.3f}")
    
    # Detailed results
    print(f"\n📄 Detailed Analysis Results:")
    for doc_name, result in results.items():
        print(f"\n   📄 {doc_name}:")
        if 'error' in result:
            print(f"      ❌ Error: {result['error']}")
        else:
            print(f"      📊 Words: {result.get('word_count', 0)}")
            if result.get('legal_analysis'):
                print(f"      🏷️  Type: {result['legal_analysis'].metadata.get('document_type', 'Unknown')}")
                print(f"      📈 Complexity: {result['legal_analysis'].metadata.get('complexity_score', 'N/A')}")
            if result.get('structure_analysis'):
                print(f"      📋 Sections: {result['structure_analysis'].metadata.get('sections', 0)}")
            if result.get('entity_extraction'):
                print(f"      🔍 Entities: {result['entity_extraction'].metadata.get('total_entities', 0)}")

def main():
    """Main function for the advanced demo"""
    print("🏛️  Legal Research AI Agents - Advanced Document Analysis Demo")
    print("="*70)
    
    # Initialize agents
    print("\n🤖 Initializing AI Agents...")
    legal_agent = LegalResearchAgent()
    doc_analyzer = DocumentAnalyzer()
    
    print(f"✅ Agents initialized successfully")
    
    # Load sample documents from workspace
    print("\n📂 Loading sample documents from workspace...")
    documents = load_sample_documents()
    
    if documents:
        print(f"✅ Found {len(documents)} documents:")
        for doc_name in documents.keys():
            print(f"   📄 {doc_name}")
        
        # Batch analysis
        results = analyze_document_batch(documents, legal_agent, doc_analyzer)
        
        # Generate comprehensive report
        generate_analysis_report(results)
        
    else:
        print("⚠️  No suitable documents found in workspace")
        print("   Using built-in sample documents for demo...")
    
    # Demonstrate advanced features
    demonstrate_advanced_features(legal_agent, doc_analyzer)
    
    # Show real-world scenarios
    demonstrate_real_world_scenarios()
    
    # Performance and optimization tips
    print("\n⚡ PERFORMANCE & OPTIMIZATION TIPS")
    print("="*50)
    
    tips = [
        "Process documents in batches for better efficiency",
        "Use appropriate summary lengths based on document size",
        "Cache results for frequently analyzed documents",
        "Monitor confidence scores and processing times",
        "Use document comparison for version control",
        "Combine multiple analysis types for comprehensive insights",
        "Set up monitoring for agent health in production",
        "Consider document preprocessing for better accuracy"
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"   {i}. {tip}")
    
    print("\n" + "="*70)
    print("🎉 Advanced demo completed!")
    print("\n📚 Additional Resources:")
    print("   - Check the tests/ directory for more usage examples")
    print("   - Review config/settings.py for customization options")
    print("   - See deployment/ directory for production setup")
    print("   - Read the full API documentation in the code")
    print("="*70)

if __name__ == "__main__":
    main()