"""
Test Suite for Legal Research AI Agents

Comprehensive tests for all agent functionality including unit tests and integration tests.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the project root to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent, AgentResponse
from agents.legal_research_agent import LegalResearchAgent
from agents.document_analyzer import DocumentAnalyzer
from config.settings import settings

class TestBaseAgent:
    """Test cases for the BaseAgent class"""
    
    def test_agent_initialization(self):
        """Test that agents initialize correctly"""
        # Create a concrete implementation for testing
        class TestAgent(BaseAgent):
            def process_request(self, request):
                return self._create_response("Test response")
        
        agent = TestAgent()
        assert agent.agent_type == "TestAgent"
        assert agent.model_name == settings.DEFAULT_MODEL
        assert agent.max_tokens == settings.MAX_TOKENS
        assert agent.temperature == settings.TEMPERATURE
    
    def test_agent_response_creation(self):
        """Test AgentResponse creation and serialization"""
        class TestAgent(BaseAgent):
            def process_request(self, request):
                return self._create_response("Test response")
        
        agent = TestAgent()
        response = agent._create_response(
            "Test content",
            success=True,
            metadata={'test': 'data'},
            confidence_score=0.95
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success == True
        assert response.content == "Test content"
        assert response.metadata['test'] == 'data'
        assert response.confidence_score == 0.95
        assert response.agent_type == "TestAgent"
        
        # Test serialization
        response_dict = response.to_dict()
        assert isinstance(response_dict, dict)
        assert response_dict['success'] == True
        assert response_dict['content'] == "Test content"
    
    def test_input_validation(self):
        """Test input validation functionality"""
        class TestAgent(BaseAgent):
            def process_request(self, request):
                return self._create_response("Test response")
        
        agent = TestAgent()
        
        # Valid input
        assert agent._validate_input("Valid text input") == True
        
        # Invalid inputs
        assert agent._validate_input("") == False
        assert agent._validate_input(None) == False
        assert agent._validate_input(123) == False
        
        # Length validation
        assert agent._validate_input("Short", max_length=10) == True
        assert agent._validate_input("This is too long", max_length=5) == False
    
    def test_key_terms_extraction(self):
        """Test legal key terms extraction"""
        class TestAgent(BaseAgent):
            def process_request(self, request):
                return self._create_response("Test response")
        
        agent = TestAgent()
        text = "This contract contains liability clauses and breach provisions."
        
        key_terms = agent._extract_key_terms(text)
        assert 'contract' in key_terms
        assert 'liability' in key_terms
        assert 'breach' in key_terms
    
    def test_agent_capabilities(self):
        """Test agent capabilities reporting"""
        class TestAgent(BaseAgent):
            def process_request(self, request):
                return self._create_response("Test response")
        
        agent = TestAgent()
        capabilities = agent.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'agent_type' in capabilities
        assert 'model_name' in capabilities
        assert 'features' in capabilities
        assert capabilities['agent_type'] == 'TestAgent'
    
    def test_health_check(self):
        """Test agent health check functionality"""
        class TestAgent(BaseAgent):
            def process_request(self, request):
                return self._create_response("Test response")
        
        agent = TestAgent()
        health = agent.health_check()
        
        assert isinstance(health, dict)
        assert 'agent_type' in health
        assert 'status' in health
        assert 'timestamp' in health

class TestLegalResearchAgent:
    """Test cases for the LegalResearchAgent class"""
    
    @pytest.fixture
    def legal_agent(self):
        """Create a LegalResearchAgent instance for testing"""
        return LegalResearchAgent()
    
    def test_legal_agent_initialization(self, legal_agent):
        """Test legal research agent initialization"""
        assert legal_agent.agent_type == "LegalResearchAgent"
        assert hasattr(legal_agent, 'legal_specializations')
        assert 'contract_analysis' in legal_agent.legal_specializations
        assert 'case_law_research' in legal_agent.legal_specializations
    
    def test_document_analysis_request(self, legal_agent):
        """Test document analysis functionality"""
        sample_contract = """
        This Agreement is entered into between Party A and Party B.
        The parties agree to the following terms and conditions:
        1. Payment terms: Net 30 days
        2. Liability is limited to direct damages
        3. This agreement shall terminate on December 31, 2024
        """
        
        request = {
            'action': 'analyze_document',
            'content': sample_contract,
            'parameters': {}
        }
        
        with patch.object(legal_agent, '_call_ai_model', return_value="Mock AI analysis"):
            response = legal_agent.process_request(request)
        
        assert isinstance(response, AgentResponse)
        assert response.success == True
        assert response.agent_type == "LegalResearchAgent"
        assert 'metadata' in response.to_dict()
    
    def test_contract_analysis_request(self, legal_agent):
        """Test specialized contract analysis"""
        sample_contract = """
        SERVICE AGREEMENT
        
        This Service Agreement is between Company A (Client) and Company B (Service Provider).
        
        Services: The Service Provider shall provide consulting services.
        Payment: $5,000 per month, payable within 30 days.
        Term: This agreement is effective from January 1, 2024 to December 31, 2024.
        Termination: Either party may terminate with 30 days written notice.
        """
        
        request = {
            'action': 'analyze_contract',
            'content': sample_contract,
            'parameters': {}
        }
        
        with patch.object(legal_agent, '_call_ai_model', return_value="Mock contract analysis"):
            response = legal_agent.process_request(request)
        
        assert response.success == True
        assert 'contract_type' in response.content.lower() or 'service' in response.content.lower()
    
    def test_research_query_request(self, legal_agent):
        """Test legal research query functionality"""
        request = {
            'action': 'research_query',
            'content': 'What are the requirements for breach of contract claims?',
            'parameters': {'jurisdiction': 'Federal'}
        }
        
        with patch.object(legal_agent, '_call_ai_model', return_value="Mock research guidance"):
            response = legal_agent.process_request(request)
        
        assert response.success == True
        assert 'research' in response.content.lower()
    
    def test_legal_concept_extraction(self, legal_agent):
        """Test legal concept extraction"""
        legal_text = """
        The defendant breached the contract by failing to perform due diligence.
        This constitutes negligence and may result in liability for damages.
        The plaintiff seeks indemnification under the force majeure clause.
        """
        
        request = {
            'action': 'extract_concepts',
            'content': legal_text,
            'parameters': {}
        }
        
        with patch.object(legal_agent, '_call_ai_model', return_value="Mock concept explanation"):
            response = legal_agent.process_request(request)
        
        assert response.success == True
        assert 'concept' in response.content.lower()
    
    def test_document_type_classification(self, legal_agent):
        """Test document type classification"""
        contract_text = "This agreement contains terms and conditions for the parties."
        doc_type = legal_agent._classify_document_type(contract_text)
        assert doc_type == 'contract'
        
        case_text = "The court held that the plaintiff and defendant..."
        doc_type = legal_agent._classify_document_type(case_text)
        assert doc_type == 'case_law'
    
    def test_legal_concepts_identification(self, legal_agent):
        """Test identification of legal concepts"""
        text = "This contract includes force majeure, liability, and indemnification clauses."
        concepts = legal_agent._identify_legal_concepts(text)
        
        assert 'force majeure' in concepts
        assert 'liability' in concepts
        assert 'indemnification' in concepts
    
    def test_complexity_score_calculation(self, legal_agent):
        """Test document complexity scoring"""
        simple_text = "This is a simple contract with basic terms."
        complex_text = "Notwithstanding the aforementioned provisions and pursuant to the heretofore established obligations, the parties shall indemnify and hold harmless each other from any and all liabilities, damages, costs, and expenses."
        
        simple_score = legal_agent._calculate_complexity_score(simple_text)
        complex_score = legal_agent._calculate_complexity_score(complex_text)
        
        assert isinstance(simple_score, float)
        assert isinstance(complex_score, float)
        assert 0 <= simple_score <= 1
        assert 0 <= complex_score <= 1
        # Complex text should generally have higher complexity score
        assert complex_score >= simple_score
    
    def test_contract_party_extraction(self, legal_agent):
        """Test extraction of contract parties"""
        contract_text = """
        This agreement is between ABC Corporation and XYZ LLC.
        Party A: ABC Corporation
        Party B: XYZ LLC
        """
        
        parties = legal_agent._extract_parties(contract_text)
        assert len(parties) > 0
        # Should find some form of the party names
    
    def test_contract_risk_assessment(self, legal_agent):
        """Test contract risk assessment"""
        risky_contract = "This agreement includes unlimited liability and automatic renewal clauses."
        safe_contract = "This agreement has standard terms and conditions."
        
        risky_assessment = legal_agent._assess_contract_risks(risky_contract)
        safe_assessment = legal_agent._assess_contract_risks(safe_contract)
        
        assert 'unlimited liability' in risky_assessment or 'risks identified' in risky_assessment
        assert 'no obvious' in safe_assessment.lower() or 'no' in safe_assessment.lower()
    
    def test_invalid_action_handling(self, legal_agent):
        """Test handling of invalid actions"""
        request = {
            'action': 'invalid_action',
            'content': 'Some content',
            'parameters': {}
        }
        
        response = legal_agent.process_request(request)
        assert response.success == False
        assert 'unknown action' in response.content.lower()
    
    def test_empty_content_handling(self, legal_agent):
        """Test handling of empty content"""
        request = {
            'action': 'analyze_document',
            'content': '',
            'parameters': {}
        }
        
        response = legal_agent.process_request(request)
        assert response.success == False
        assert 'invalid input' in response.content.lower()

class TestDocumentAnalyzer:
    """Test cases for the DocumentAnalyzer class"""
    
    @pytest.fixture
    def doc_analyzer(self):
        """Create a DocumentAnalyzer instance for testing"""
        return DocumentAnalyzer()
    
    def test_document_analyzer_initialization(self, doc_analyzer):
        """Test document analyzer initialization"""
        assert doc_analyzer.agent_type == "DocumentAnalyzer"
        assert hasattr(doc_analyzer, 'supported_formats')
        assert hasattr(doc_analyzer, 'extraction_patterns')
        assert 'pdf' in doc_analyzer.supported_formats
        assert 'dates' in doc_analyzer.extraction_patterns
    
    def test_structure_analysis(self, doc_analyzer):
        """Test document structure analysis"""
        document_text = """
        # Main Heading
        
        ## Section 1: Introduction
        This is the introduction paragraph.
        
        ## Section 2: Terms
        1. First term
        2. Second term
        3. Third term
        
        ### Subsection 2.1
        Additional details here.
        """
        
        request = {
            'action': 'analyze_structure',
            'content': document_text,
            'parameters': {}
        }
        
        with patch.object(doc_analyzer, '_call_ai_model', return_value="Mock structure analysis"):
            response = doc_analyzer.process_request(request)
        
        assert response.success == True
        assert 'structure' in response.content.lower()
        assert response.metadata['sections'] > 0
        assert response.metadata['headings'] > 0
    
    def test_entity_extraction(self, doc_analyzer):
        """Test entity extraction functionality"""
        document_text = """
        Contact: john.doe@example.com
        Phone: 555-123-4567
        Amount: $10,000.00
        Date: 12/31/2024
        Address: 123 Main Street
        """
        
        request = {
            'action': 'extract_entities',
            'content': document_text,
            'parameters': {}
        }
        
        with patch.object(doc_analyzer, '_call_ai_model', return_value="Mock entity extraction"):
            response = doc_analyzer.process_request(request)
        
        assert response.success == True
        assert response.metadata['total_entities'] > 0
    
    def test_content_summarization(self, doc_analyzer):
        """Test content summarization"""
        long_document = """
        This is a comprehensive legal document that contains multiple sections and clauses.
        The document outlines various terms and conditions for a business agreement.
        It includes provisions for payment, termination, liability, and dispute resolution.
        The parties involved have specific obligations and rights under this agreement.
        This document serves as a binding contract between the involved parties.
        """ * 5  # Make it longer
        
        request = {
            'action': 'summarize_content',
            'content': long_document,
            'parameters': {'summary_length': 'brief'}
        }
        
        with patch.object(doc_analyzer, '_call_ai_model', return_value="Brief summary of the document"):
            response = doc_analyzer.process_request(request)
        
        assert response.success == True
        assert 'summary' in response.content.lower()
        assert response.metadata['summary_type'] == 'brief'
    
    def test_key_information_extraction(self, doc_analyzer):
        """Test key information extraction"""
        document_text = """
        Payment due: 01/15/2024
        Amount: $5,000
        The party must complete all obligations by the deadline.
        The client has the right to terminate with 30 days notice.
        """
        
        request = {
            'action': 'extract_key_info',
            'content': document_text,
            'parameters': {}
        }
        
        with patch.object(doc_analyzer, '_call_ai_model', return_value="Key information analysis"):
            response = doc_analyzer.process_request(request)
        
        assert response.success == True
        assert response.metadata['dates_found'] >= 0
        assert response.metadata['amounts_found'] >= 0
    
    def test_document_comparison(self, doc_analyzer):
        """Test document comparison functionality"""
        doc1 = "This is the first version of the document with original terms."
        doc2 = "This is the second version of the document with modified terms."
        
        request = {
            'action': 'compare_documents',
            'content': doc1,
            'parameters': {'second_document': doc2}
        }
        
        with patch.object(doc_analyzer, '_call_ai_model', return_value="Document comparison analysis"):
            response = doc_analyzer.process_request(request)
        
        assert response.success == True
        assert 'similarity' in response.content.lower()
        assert 'similarity_score' in response.metadata
    
    def test_text_cleaning(self, doc_analyzer):
        """Test text cleaning functionality"""
        messy_text = """
        This   is   a    messy     document    with
        
        
        extra    whitespace   and   
        
        empty lines.
        """
        
        request = {
            'action': 'clean_text',
            'content': messy_text,
            'parameters': {
                'remove_extra_whitespace': True,
                'remove_empty_lines': True
            }
        }
        
        response = doc_analyzer.process_request(request)
        
        assert response.success == True
        assert response.metadata['reduction_percentage'] >= 0
    
    def test_regex_pattern_extraction(self, doc_analyzer):
        """Test regex pattern extraction"""
        text = """
        Email: test@example.com
        Phone: 555-123-4567
        Date: 12/31/2024
        Amount: $1,500.00
        """
        
        # Test email extraction
        emails = doc_analyzer.extraction_patterns['emails']
        import re
        found_emails = re.findall(emails, text)
        assert len(found_emails) > 0
        
        # Test phone extraction
        phones = doc_analyzer.extraction_patterns['phone_numbers']
        found_phones = re.findall(phones, text)
        assert len(found_phones) > 0
    
    def test_readability_calculation(self, doc_analyzer):
        """Test readability metrics calculation"""
        simple_text = "This is simple. Easy to read. Short sentences."
        complex_text = "Notwithstanding the aforementioned considerations and pursuant to the established precedential framework, the comprehensive analysis of multifaceted legal implications necessitates careful examination."
        
        simple_metrics = doc_analyzer._calculate_readability_metrics(simple_text)
        complex_metrics = doc_analyzer._calculate_readability_metrics(complex_text)
        
        assert 'flesch_score' in simple_metrics
        assert 'avg_word_length' in simple_metrics
        assert 'avg_sentence_length' in simple_metrics
        
        # Simple text should generally have higher readability score
        assert simple_metrics['flesch_score'] >= complex_metrics['flesch_score']
    
    def test_section_identification(self, doc_analyzer):
        """Test section identification"""
        text_with_sections = """
        I. Introduction
        II. Terms and Conditions
        1. First Term
        2. Second Term
        
        ## Section A
        Content here
        
        DEFINITIONS:
        Content here
        """
        
        sections = doc_analyzer._identify_sections(text_with_sections)
        assert len(sections) > 0
    
    def test_list_identification(self, doc_analyzer):
        """Test list identification in documents"""
        text_with_lists = """
        Requirements:
        - First requirement
        - Second requirement
        * Third requirement
        
        Steps:
        1. First step
        2. Second step
        3. Third step
        
        Options:
        a) Option A
        b) Option B
        """
        
        lists = doc_analyzer._identify_lists(text_with_lists)
        assert len(lists) > 0
    
    def test_missing_second_document_comparison(self, doc_analyzer):
        """Test document comparison without second document"""
        request = {
            'action': 'compare_documents',
            'content': 'First document',
            'parameters': {}  # Missing second_document
        }
        
        response = doc_analyzer.process_request(request)
        assert response.success == False
        assert 'second document required' in response.content.lower()

class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_agent_workflow(self):
        """Test complete workflow with multiple agents"""
        # Sample legal document
        sample_document = """
        CONSULTING AGREEMENT
        
        This Consulting Agreement is entered into between TechCorp Inc. (Client) 
        and Legal Advisors LLC (Consultant) on January 1, 2024.
        
        Services: The Consultant shall provide legal research services.
        Compensation: $200 per hour, invoiced monthly.
        Term: 12 months from the effective date.
        Termination: Either party may terminate with 30 days written notice.
        
        Liability: Consultant's liability is limited to the amount of fees paid.
        Confidentiality: All information shared shall remain confidential.
        """
        
        # Initialize agents
        legal_agent = LegalResearchAgent()
        doc_analyzer = DocumentAnalyzer()
        
        # Test document analysis
        with patch.object(legal_agent, '_call_ai_model', return_value="Mock analysis"):
            legal_response = legal_agent.process_request({
                'action': 'analyze_contract',
                'content': sample_document,
                'parameters': {}
            })
        
        with patch.object(doc_analyzer, '_call_ai_model', return_value="Mock structure analysis"):
            structure_response = doc_analyzer.process_request({
                'action': 'analyze_structure',
                'content': sample_document,
                'parameters': {}
            })
        
        # Both agents should successfully process the document
        assert legal_response.success == True
        assert structure_response.success == True
        
        # Responses should contain relevant information
        assert 'contract' in legal_response.content.lower() or 'agreement' in legal_response.content.lower()
        assert 'structure' in structure_response.content.lower()
    
    def test_error_handling_across_agents(self):
        """Test error handling consistency across different agents"""
        agents = [LegalResearchAgent(), DocumentAnalyzer()]
        
        for agent in agents:
            # Test with invalid input
            response = agent.process_request({
                'action': 'test_action',
                'content': '',
                'parameters': {}
            })
            
            assert isinstance(response, AgentResponse)
            assert response.success == False
            assert response.agent_type == agent.agent_type
    
    def test_response_format_consistency(self):
        """Test that all agents return consistent response formats"""
        agents = [LegalResearchAgent(), DocumentAnalyzer()]
        
        for agent in agents:
            # Mock successful response
            with patch.object(agent, '_call_ai_model', return_value="Mock response"):
                response = agent.process_request({
                    'action': 'analyze_document' if hasattr(agent, '_analyze_document') else 'analyze_structure',
                    'content': 'Sample legal text for testing purposes.',
                    'parameters': {}
                })
            
            # Check response format
            assert isinstance(response, AgentResponse)
            assert hasattr(response, 'success')
            assert hasattr(response, 'content')
            assert hasattr(response, 'metadata')
            assert hasattr(response, 'timestamp')
            assert hasattr(response, 'agent_type')
            
            # Check serialization
            response_dict = response.to_dict()
            assert isinstance(response_dict, dict)
            assert all(key in response_dict for key in ['success', 'content', 'metadata', 'timestamp', 'agent_type'])

# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def setup_test_environment():
    """Set up test environment"""
    # Ensure we're using mock mode for AI calls during testing
    import os
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['ANTHROPIC_API_KEY'] = 'test-key'
    yield
    # Cleanup if needed

# Test runner configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])