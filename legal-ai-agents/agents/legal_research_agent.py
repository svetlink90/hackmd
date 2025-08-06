"""
Legal Research Agent

Specialized AI agent for legal research, document analysis, and case law research.
"""

import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import re

from .base_agent import BaseAgent, AgentResponse
from config.settings import settings, LEGAL_DOCUMENT_TYPES

class LegalResearchAgent(BaseAgent):
    """
    Specialized agent for legal research and document analysis.
    
    Capabilities:
    - Legal document analysis
    - Contract review
    - Case law research
    - Statute interpretation
    - Legal concept extraction
    - Risk assessment
    """
    
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the Legal Research Agent"""
        super().__init__(model_name, api_key)
        self.legal_specializations = [
            'contract_analysis',
            'case_law_research', 
            'statute_interpretation',
            'regulatory_compliance',
            'risk_assessment',
            'legal_concept_extraction'
        ]
    
    def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process a legal research request.
        
        Args:
            request: Dictionary with keys:
                - action: Type of analysis ('analyze_document', 'research_query', etc.)
                - content: Document text or research query
                - parameters: Additional parameters for the request
                
        Returns:
            AgentResponse with legal analysis
        """
        start_time = time.time()
        
        try:
            action = request.get('action', 'analyze_document')
            content = request.get('content', '')
            parameters = request.get('parameters', {})
            
            if not self._validate_input(content):
                return self._create_response(
                    "Invalid input provided",
                    success=False,
                    metadata={'error': 'Invalid or empty content'}
                )
            
            # Route to appropriate handler
            if action == 'analyze_document':
                result = self._analyze_document(content, parameters)
            elif action == 'research_query':
                result = self._research_query(content, parameters)
            elif action == 'analyze_contract':
                result = self._analyze_contract(content, parameters)
            elif action == 'extract_concepts':
                result = self._extract_legal_concepts(content, parameters)
            else:
                return self._create_response(
                    f"Unknown action: {action}",
                    success=False,
                    metadata={'error': 'Unsupported action'}
                )
            
            processing_time = time.time() - start_time
            
            return self._create_response(
                result['content'],
                success=result['success'],
                metadata=result.get('metadata', {}),
                processing_time=processing_time,
                confidence_score=result.get('confidence_score'),
                sources=result.get('sources')
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return self._create_response(
                f"Error processing request: {str(e)}",
                success=False,
                metadata={'error': str(e)},
                processing_time=processing_time
            )
    
    def _analyze_document(self, document_text: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a legal document comprehensively.
        
        Args:
            document_text: The document text to analyze
            parameters: Analysis parameters
            
        Returns:
            Analysis results dictionary
        """
        # Determine document type
        doc_type = self._classify_document_type(document_text)
        
        # Prepare analysis prompt
        prompt = settings.LEGAL_ANALYSIS_PROMPT.format(document_text=document_text)
        
        # Add document-type specific analysis
        if doc_type in LEGAL_DOCUMENT_TYPES:
            focus_areas = LEGAL_DOCUMENT_TYPES[doc_type]['analysis_focus']
            prompt += f"\n\nPay special attention to: {', '.join(focus_areas)}"
        
        # Get AI analysis
        ai_response = self._call_ai_model(
            prompt,
            "You are an expert legal research assistant specializing in document analysis."
        )
        
        # Extract key terms and concepts
        key_terms = self._extract_key_terms(document_text)
        legal_concepts = self._identify_legal_concepts(document_text)
        
        # Structure the analysis
        analysis = {
            'document_type': doc_type,
            'ai_analysis': ai_response,
            'key_legal_terms': key_terms,
            'legal_concepts': legal_concepts,
            'document_length': len(document_text.split()),
            'complexity_score': self._calculate_complexity_score(document_text)
        }
        
        return {
            'success': True,
            'content': self._format_document_analysis(analysis),
            'metadata': {
                'document_type': doc_type,
                'key_terms_count': len(key_terms),
                'complexity_score': analysis['complexity_score']
            },
            'confidence_score': 0.85,
            'sources': ['AI Analysis', 'Legal Term Database']
        }
    
    def _research_query(self, query: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct legal research based on a query.
        
        Args:
            query: Legal research question
            parameters: Research parameters
            
        Returns:
            Research results dictionary
        """
        # Prepare research prompt
        prompt = settings.CASE_LAW_RESEARCH_PROMPT.format(query=query)
        
        # Add jurisdiction if specified
        jurisdiction = parameters.get('jurisdiction', 'General')
        if jurisdiction != 'General':
            prompt += f"\n\nFocus on {jurisdiction} jurisdiction."
        
        # Get AI research guidance
        ai_response = self._call_ai_model(
            prompt,
            "You are a legal research expert. Provide comprehensive research guidance."
        )
        
        # Identify relevant legal areas
        legal_areas = self._identify_legal_areas(query)
        search_terms = self._generate_search_terms(query)
        
        research_results = {
            'research_guidance': ai_response,
            'legal_areas': legal_areas,
            'suggested_search_terms': search_terms,
            'jurisdiction': jurisdiction,
            'research_strategy': self._create_research_strategy(query, legal_areas)
        }
        
        return {
            'success': True,
            'content': self._format_research_results(research_results),
            'metadata': {
                'legal_areas': legal_areas,
                'jurisdiction': jurisdiction,
                'search_terms_count': len(search_terms)
            },
            'confidence_score': 0.80,
            'sources': ['Legal Research Database', 'AI Analysis']
        }
    
    def _analyze_contract(self, contract_text: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Specialized contract analysis.
        
        Args:
            contract_text: Contract text to analyze
            parameters: Analysis parameters
            
        Returns:
            Contract analysis results
        """
        # Prepare contract analysis prompt
        prompt = settings.CONTRACT_ANALYSIS_PROMPT.format(contract_text=contract_text)
        
        # Get AI analysis
        ai_response = self._call_ai_model(
            prompt,
            "You are a contract law expert. Provide detailed contract analysis."
        )
        
        # Extract contract elements
        parties = self._extract_parties(contract_text)
        key_clauses = self._identify_key_clauses(contract_text)
        risk_factors = self._assess_contract_risks(contract_text)
        
        contract_analysis = {
            'ai_analysis': ai_response,
            'identified_parties': parties,
            'key_clauses': key_clauses,
            'risk_assessment': risk_factors,
            'contract_type': self._determine_contract_type(contract_text),
            'completeness_score': self._assess_contract_completeness(contract_text)
        }
        
        return {
            'success': True,
            'content': self._format_contract_analysis(contract_analysis),
            'metadata': {
                'parties_count': len(parties),
                'key_clauses_count': len(key_clauses),
                'risk_level': self._calculate_overall_risk_level(risk_factors)
            },
            'confidence_score': 0.88,
            'sources': ['Contract Analysis AI', 'Legal Clause Database']
        }
    
    def _extract_legal_concepts(self, text: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and explain legal concepts from text.
        
        Args:
            text: Text to analyze for legal concepts
            parameters: Extraction parameters
            
        Returns:
            Legal concepts extraction results
        """
        concepts = self._identify_legal_concepts(text)
        explanations = {}
        
        # Get explanations for key concepts
        for concept in concepts[:5]:  # Limit to top 5 concepts
            explanation_prompt = f"Provide a clear, concise explanation of the legal concept '{concept}' in the context of: {text[:500]}..."
            explanation = self._call_ai_model(
                explanation_prompt,
                "You are a legal educator. Explain legal concepts clearly and accurately."
            )
            explanations[concept] = explanation
        
        return {
            'success': True,
            'content': self._format_concepts_analysis(concepts, explanations),
            'metadata': {
                'total_concepts': len(concepts),
                'explained_concepts': len(explanations)
            },
            'confidence_score': 0.82,
            'sources': ['Legal Concept Database', 'AI Analysis']
        }
    
    def _classify_document_type(self, text: str) -> str:
        """Classify the type of legal document"""
        text_lower = text.lower()
        
        for doc_type, characteristics in LEGAL_DOCUMENT_TYPES.items():
            keyword_matches = sum(1 for keyword in characteristics['keywords'] 
                                if keyword in text_lower)
            if keyword_matches >= 2:  # Require at least 2 keyword matches
                return doc_type
        
        return 'general_legal'
    
    def _identify_legal_concepts(self, text: str) -> List[str]:
        """Identify legal concepts in the text"""
        # Enhanced legal concept identification
        legal_concepts = [
            'force majeure', 'breach of contract', 'due process', 'negligence',
            'liability', 'indemnification', 'jurisdiction', 'arbitration',
            'intellectual property', 'confidentiality', 'non-disclosure',
            'termination clause', 'governing law', 'damages', 'remedy'
        ]
        
        text_lower = text.lower()
        found_concepts = []
        
        for concept in legal_concepts:
            if concept in text_lower:
                found_concepts.append(concept)
        
        # Also look for legal phrases with regex
        legal_patterns = [
            r'pursuant to',
            r'whereas',
            r'heretofore',
            r'in consideration of',
            r'subject to the terms'
        ]
        
        for pattern in legal_patterns:
            if re.search(pattern, text_lower):
                found_concepts.append(pattern.replace(r'\\', ''))
        
        return list(set(found_concepts))  # Remove duplicates
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate document complexity score (0-1)"""
        # Simple complexity scoring based on various factors
        words = text.split()
        sentences = text.split('.')
        
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        legal_terms_ratio = len(self._extract_key_terms(text)) / len(words) if words else 0
        
        # Normalize and combine factors
        complexity = min(1.0, (avg_word_length / 10 + avg_sentence_length / 30 + legal_terms_ratio * 5) / 3)
        return round(complexity, 2)
    
    def _format_document_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format document analysis results"""
        return f"""
# Legal Document Analysis

## Document Type: {analysis['document_type'].title()}

## AI Analysis:
{analysis['ai_analysis']}

## Key Legal Terms Found:
{', '.join(analysis['key_legal_terms']) if analysis['key_legal_terms'] else 'None identified'}

## Legal Concepts Identified:
{', '.join(analysis['legal_concepts']) if analysis['legal_concepts'] else 'None identified'}

## Document Statistics:
- Word Count: {analysis['document_length']}
- Complexity Score: {analysis['complexity_score']}/1.0
- Legal Term Density: {len(analysis['key_legal_terms'])}/{analysis['document_length']} words

## Recommendations:
Based on the analysis, consider reviewing the document for completeness and clarity of legal terms.
"""
    
    def _format_research_results(self, results: Dict[str, Any]) -> str:
        """Format legal research results"""
        return f"""
# Legal Research Results

## Research Guidance:
{results['research_guidance']}

## Relevant Legal Areas:
{', '.join(results['legal_areas']) if results['legal_areas'] else 'General Legal Research'}

## Suggested Search Terms:
{', '.join(results['suggested_search_terms'])}

## Jurisdiction: {results['jurisdiction']}

## Research Strategy:
{results['research_strategy']}

## Next Steps:
1. Use the suggested search terms in legal databases
2. Focus on the identified legal areas
3. Consider jurisdictional variations
4. Review recent case law and statutory changes
"""
    
    def _format_contract_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format contract analysis results"""
        return f"""
# Contract Analysis Report

## Contract Type: {analysis.get('contract_type', 'Unknown')}

## AI Analysis:
{analysis['ai_analysis']}

## Identified Parties:
{', '.join(analysis['identified_parties']) if analysis['identified_parties'] else 'Not clearly identified'}

## Key Clauses Found:
{', '.join(analysis['key_clauses']) if analysis['key_clauses'] else 'Standard clauses identified'}

## Risk Assessment:
{analysis['risk_assessment']}

## Completeness Score: {analysis.get('completeness_score', 'N/A')}

## Recommendations:
Review the identified risks and ensure all necessary clauses are present and clearly defined.
"""
    
    def _format_concepts_analysis(self, concepts: List[str], explanations: Dict[str, str]) -> str:
        """Format legal concepts analysis"""
        result = "# Legal Concepts Analysis\n\n"
        
        if concepts:
            result += "## Identified Legal Concepts:\n"
            for concept in concepts:
                result += f"- {concept.title()}\n"
            
            if explanations:
                result += "\n## Detailed Explanations:\n\n"
                for concept, explanation in explanations.items():
                    result += f"### {concept.title()}\n{explanation}\n\n"
        else:
            result += "No specific legal concepts identified in the provided text.\n"
        
        return result
    
    def _get_features(self) -> List[str]:
        """Get legal research agent specific features"""
        base_features = super()._get_features()
        legal_features = [
            'document_classification',
            'contract_analysis', 
            'legal_concept_extraction',
            'risk_assessment',
            'case_law_research',
            'statute_interpretation'
        ]
        return base_features + legal_features
    
    # Helper methods for contract analysis
    def _extract_parties(self, contract_text: str) -> List[str]:
        """Extract party names from contract"""
        # Simple pattern matching for common contract party patterns
        patterns = [
            r'between\s+([^,]+),?\s+and\s+([^,\n]+)',
            r'Party A[:\s]+([^\n]+)',
            r'Party B[:\s]+([^\n]+)'
        ]
        
        parties = []
        for pattern in patterns:
            matches = re.findall(pattern, contract_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    parties.extend(match)
                else:
                    parties.append(match)
        
        return [party.strip() for party in parties if party.strip()]
    
    def _identify_key_clauses(self, contract_text: str) -> List[str]:
        """Identify key contract clauses"""
        clause_patterns = [
            'termination', 'liability', 'indemnification', 'confidentiality',
            'intellectual property', 'payment terms', 'governing law',
            'dispute resolution', 'force majeure', 'assignment'
        ]
        
        text_lower = contract_text.lower()
        found_clauses = [clause for clause in clause_patterns if clause in text_lower]
        return found_clauses
    
    def _assess_contract_risks(self, contract_text: str) -> str:
        """Assess contract risks"""
        risk_indicators = [
            'unlimited liability', 'no limitation', 'broad indemnification',
            'automatic renewal', 'exclusive rights', 'non-compete'
        ]
        
        text_lower = contract_text.lower()
        risks_found = [risk for risk in risk_indicators if risk in text_lower]
        
        if risks_found:
            return f"Potential risks identified: {', '.join(risks_found)}"
        else:
            return "No obvious high-risk clauses identified in preliminary review."
    
    def _determine_contract_type(self, contract_text: str) -> str:
        """Determine the type of contract"""
        contract_types = {
            'service agreement': ['service', 'services', 'perform', 'deliverables'],
            'employment contract': ['employee', 'employment', 'salary', 'benefits'],
            'nda': ['non-disclosure', 'confidential', 'confidentiality'],
            'license agreement': ['license', 'licensing', 'intellectual property'],
            'purchase agreement': ['purchase', 'buy', 'sale', 'goods']
        }
        
        text_lower = contract_text.lower()
        
        for contract_type, keywords in contract_types.items():
            if sum(1 for keyword in keywords if keyword in text_lower) >= 2:
                return contract_type
        
        return 'general contract'
    
    def _assess_contract_completeness(self, contract_text: str) -> str:
        """Assess contract completeness"""
        essential_elements = [
            'parties', 'consideration', 'terms', 'duration', 'termination'
        ]
        
        text_lower = contract_text.lower()
        present_elements = [element for element in essential_elements if element in text_lower]
        
        completeness = len(present_elements) / len(essential_elements)
        
        if completeness >= 0.8:
            return "High - Most essential elements present"
        elif completeness >= 0.6:
            return "Medium - Some essential elements may be missing"
        else:
            return "Low - Several essential elements appear to be missing"
    
    def _calculate_overall_risk_level(self, risk_assessment: str) -> str:
        """Calculate overall risk level"""
        if "no obvious" in risk_assessment.lower():
            return "Low"
        elif "potential risks" in risk_assessment.lower():
            return "Medium"
        else:
            return "Unknown"
    
    def _identify_legal_areas(self, query: str) -> List[str]:
        """Identify relevant legal areas for research"""
        legal_areas = {
            'contract law': ['contract', 'agreement', 'breach', 'consideration'],
            'tort law': ['negligence', 'liability', 'damages', 'injury'],
            'employment law': ['employment', 'workplace', 'discrimination', 'wages'],
            'intellectual property': ['patent', 'trademark', 'copyright', 'trade secret'],
            'corporate law': ['corporation', 'business', 'merger', 'acquisition'],
            'real estate law': ['property', 'real estate', 'lease', 'mortgage']
        }
        
        query_lower = query.lower()
        relevant_areas = []
        
        for area, keywords in legal_areas.items():
            if any(keyword in query_lower for keyword in keywords):
                relevant_areas.append(area)
        
        return relevant_areas or ['general legal research']
    
    def _generate_search_terms(self, query: str) -> List[str]:
        """Generate search terms for legal research"""
        # Extract key terms from query
        words = query.lower().split()
        
        # Remove common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add legal variations
        search_terms = meaningful_words.copy()
        
        # Add related legal terms
        legal_expansions = {
            'contract': ['agreement', 'covenant'],
            'liability': ['responsibility', 'damages'],
            'rights': ['entitlements', 'privileges']
        }
        
        for term in meaningful_words:
            if term in legal_expansions:
                search_terms.extend(legal_expansions[term])
        
        return list(set(search_terms))  # Remove duplicates
    
    def _create_research_strategy(self, query: str, legal_areas: List[str]) -> str:
        """Create a research strategy"""
        strategy = f"Research Strategy for: {query}\n\n"
        strategy += "1. Primary Sources:\n"
        strategy += "   - Relevant statutes and regulations\n"
        strategy += "   - Recent case law\n\n"
        strategy += "2. Secondary Sources:\n"
        strategy += "   - Legal treatises and commentaries\n"
        strategy += "   - Law review articles\n\n"
        strategy += f"3. Focus Areas: {', '.join(legal_areas)}\n\n"
        strategy += "4. Research Sequence:\n"
        strategy += "   - Start with primary sources\n"
        strategy += "   - Review recent developments\n"
        strategy += "   - Check for jurisdictional variations\n"
        strategy += "   - Consult secondary sources for analysis"
        
        return strategy

    def analyze_document(self, file_path: str) -> AgentResponse:
        """
        Convenience method to analyze a document from file path.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            AgentResponse with analysis results
        """
        try:
            # This would need to be implemented with actual file reading
            # For now, return a placeholder
            return self._create_response(
                "Document analysis from file path not yet implemented. Please use process_request with document text.",
                success=False,
                metadata={'error': 'File reading not implemented'}
            )
        except Exception as e:
            return self._create_response(
                f"Error reading file: {str(e)}",
                success=False,
                metadata={'error': str(e)}
            )