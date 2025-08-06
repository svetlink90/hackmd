"""
Document Analyzer Agent

Specialized agent for parsing, extracting, and analyzing content from legal documents.
"""

import time
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .base_agent import BaseAgent, AgentResponse
from config.settings import settings

class DocumentAnalyzer(BaseAgent):
    """
    Specialized agent for document parsing and content extraction.
    
    Capabilities:
    - Text extraction and cleaning
    - Structure analysis
    - Entity extraction
    - Content summarization
    - Key information identification
    - Document comparison
    """
    
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the Document Analyzer Agent"""
        super().__init__(model_name, api_key)
        self.supported_formats = ['txt', 'md', 'pdf', 'docx']
        self.extraction_patterns = self._init_extraction_patterns()
    
    def _init_extraction_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for information extraction"""
        return {
            'dates': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            'amounts': r'\$[\d,]+\.?\d*|\b\d+\.\d{2}\b',
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone_numbers': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'legal_citations': r'\b\d+\s+[A-Za-z.]+\s+\d+\b',
            'section_references': r'[Ss]ection\s+\d+(\.\d+)*',
            'party_names': r'(?:Party\s+[A-Z]|Plaintiff|Defendant|Grantor|Grantee):\s*([^\n]+)',
            'addresses': r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct)'
        }
    
    def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process a document analysis request.
        
        Args:
            request: Dictionary with keys:
                - action: Type of analysis ('extract_text', 'analyze_structure', etc.)
                - content: Document text or file path
                - parameters: Additional parameters for the request
                
        Returns:
            AgentResponse with document analysis results
        """
        start_time = time.time()
        
        try:
            action = request.get('action', 'analyze_structure')
            content = request.get('content', '')
            parameters = request.get('parameters', {})
            
            if not self._validate_input(content):
                return self._create_response(
                    "Invalid input provided",
                    success=False,
                    metadata={'error': 'Invalid or empty content'}
                )
            
            # Route to appropriate handler
            if action == 'analyze_structure':
                result = self._analyze_structure(content, parameters)
            elif action == 'extract_entities':
                result = self._extract_entities(content, parameters)
            elif action == 'summarize_content':
                result = self._summarize_content(content, parameters)
            elif action == 'extract_key_info':
                result = self._extract_key_information(content, parameters)
            elif action == 'compare_documents':
                result = self._compare_documents(content, parameters)
            elif action == 'clean_text':
                result = self._clean_and_format_text(content, parameters)
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
    
    def _analyze_structure(self, document_text: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the structure of a legal document.
        
        Args:
            document_text: The document text to analyze
            parameters: Analysis parameters
            
        Returns:
            Structure analysis results
        """
        # Analyze document structure
        sections = self._identify_sections(document_text)
        headings = self._extract_headings(document_text)
        paragraphs = self._count_paragraphs(document_text)
        lists = self._identify_lists(document_text)
        
        # Calculate readability metrics
        readability = self._calculate_readability_metrics(document_text)
        
        # Get AI-powered structure analysis
        structure_prompt = f"""
        Analyze the structure of this legal document and identify:
        1. Main sections and their purposes
        2. Document organization and flow
        3. Any structural issues or recommendations
        
        Document text:
        {document_text[:2000]}...
        """
        
        ai_analysis = self._call_ai_model(
            structure_prompt,
            "You are a document structure expert. Analyze document organization."
        )
        
        structure_analysis = {
            'sections_found': len(sections),
            'section_titles': sections,
            'headings_count': len(headings),
            'headings': headings,
            'paragraph_count': paragraphs,
            'lists_count': len(lists),
            'readability_metrics': readability,
            'ai_structure_analysis': ai_analysis,
            'document_length': len(document_text.split())
        }
        
        return {
            'success': True,
            'content': self._format_structure_analysis(structure_analysis),
            'metadata': {
                'sections': len(sections),
                'headings': len(headings),
                'paragraphs': paragraphs,
                'readability_score': readability.get('flesch_score', 0)
            },
            'confidence_score': 0.90,
            'sources': ['Document Structure Analysis', 'AI Analysis']
        }
    
    def _extract_entities(self, document_text: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract various entities from the document.
        
        Args:
            document_text: The document text to analyze
            parameters: Extraction parameters
            
        Returns:
            Entity extraction results
        """
        entities = {}
        
        # Extract using regex patterns
        for entity_type, pattern in self.extraction_patterns.items():
            matches = re.findall(pattern, document_text, re.IGNORECASE)
            entities[entity_type] = list(set(matches))  # Remove duplicates
        
        # Extract legal-specific entities
        legal_entities = self._extract_legal_entities(document_text)
        entities.update(legal_entities)
        
        # Get AI-powered entity extraction
        entity_prompt = f"""
        Extract and identify important entities from this legal document including:
        1. People and organizations
        2. Legal concepts and terms
        3. Important dates and deadlines
        4. Financial amounts and obligations
        5. Geographic locations
        
        Document text:
        {document_text[:1500]}...
        """
        
        ai_entities = self._call_ai_model(
            entity_prompt,
            "You are an expert at extracting entities from legal documents."
        )
        
        return {
            'success': True,
            'content': self._format_entity_extraction(entities, ai_entities),
            'metadata': {
                'total_entities': sum(len(v) for v in entities.values()),
                'entity_types': list(entities.keys())
            },
            'confidence_score': 0.85,
            'sources': ['Regex Pattern Matching', 'AI Entity Extraction']
        }
    
    def _summarize_content(self, document_text: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of the document content.
        
        Args:
            document_text: The document text to summarize
            parameters: Summarization parameters
            
        Returns:
            Content summary results
        """
        summary_length = parameters.get('summary_length', 'medium')
        focus_areas = parameters.get('focus_areas', [])
        
        # Determine summary prompt based on length
        if summary_length == 'brief':
            max_words = 100
            detail_level = "very concise"
        elif summary_length == 'detailed':
            max_words = 500
            detail_level = "comprehensive"
        else:  # medium
            max_words = 250
            detail_level = "balanced"
        
        summary_prompt = f"""
        Create a {detail_level} summary of this legal document in approximately {max_words} words.
        
        {"Focus particularly on: " + ", ".join(focus_areas) if focus_areas else ""}
        
        Document text:
        {document_text}
        
        Provide a clear, professional summary that captures the key points and legal implications.
        """
        
        ai_summary = self._call_ai_model(
            summary_prompt,
            "You are a legal document summarization expert."
        )
        
        # Extract key statistics
        word_count = len(document_text.split())
        key_terms = self._extract_key_terms(document_text)
        
        summary_data = {
            'ai_summary': ai_summary,
            'original_word_count': word_count,
            'summary_length': summary_length,
            'key_terms_found': key_terms[:10],  # Top 10 key terms
            'compression_ratio': f"{max_words}/{word_count} words"
        }
        
        return {
            'success': True,
            'content': self._format_content_summary(summary_data),
            'metadata': {
                'original_length': word_count,
                'summary_type': summary_length,
                'key_terms_count': len(key_terms)
            },
            'confidence_score': 0.88,
            'sources': ['AI Summarization']
        }
    
    def _extract_key_information(self, document_text: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key information from the document.
        
        Args:
            document_text: The document text to analyze
            parameters: Extraction parameters
            
        Returns:
            Key information extraction results
        """
        # Extract various types of key information
        key_info = {
            'important_dates': self._find_important_dates(document_text),
            'monetary_amounts': self._extract_monetary_amounts(document_text),
            'deadlines': self._identify_deadlines(document_text),
            'obligations': self._extract_obligations(document_text),
            'rights': self._extract_rights(document_text),
            'conditions': self._extract_conditions(document_text)
        }
        
        # Get AI analysis of key information
        key_info_prompt = f"""
        Identify and extract the most important information from this legal document:
        1. Critical dates and deadlines
        2. Key obligations and responsibilities
        3. Important rights and privileges
        4. Conditions and requirements
        5. Financial terms and amounts
        6. Contact information and parties
        
        Document text:
        {document_text[:2000]}...
        
        Present the information in a clear, organized format.
        """
        
        ai_key_info = self._call_ai_model(
            key_info_prompt,
            "You are an expert at identifying critical information in legal documents."
        )
        
        return {
            'success': True,
            'content': self._format_key_information(key_info, ai_key_info),
            'metadata': {
                'dates_found': len(key_info['important_dates']),
                'amounts_found': len(key_info['monetary_amounts']),
                'obligations_found': len(key_info['obligations'])
            },
            'confidence_score': 0.87,
            'sources': ['Pattern Matching', 'AI Analysis']
        }
    
    def _compare_documents(self, content: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two documents (if second document provided in parameters).
        
        Args:
            content: First document text
            parameters: Should contain 'second_document' key
            
        Returns:
            Document comparison results
        """
        second_doc = parameters.get('second_document', '')
        
        if not second_doc:
            return {
                'success': False,
                'content': 'Second document required for comparison',
                'metadata': {'error': 'Missing second document'}
            }
        
        # Basic comparison metrics
        doc1_words = set(content.lower().split())
        doc2_words = set(second_doc.lower().split())
        
        common_words = doc1_words.intersection(doc2_words)
        unique_to_doc1 = doc1_words - doc2_words
        unique_to_doc2 = doc2_words - doc1_words
        
        similarity_ratio = len(common_words) / len(doc1_words.union(doc2_words))
        
        # Get AI-powered comparison
        comparison_prompt = f"""
        Compare these two legal documents and identify:
        1. Key similarities and differences
        2. Changes in terms or conditions
        3. Added or removed clauses
        4. Significance of any differences
        
        Document 1:
        {content[:1000]}...
        
        Document 2:
        {second_doc[:1000]}...
        
        Provide a detailed comparison analysis.
        """
        
        ai_comparison = self._call_ai_model(
            comparison_prompt,
            "You are an expert at comparing legal documents."
        )
        
        comparison_results = {
            'similarity_score': round(similarity_ratio, 3),
            'common_words_count': len(common_words),
            'unique_to_first': len(unique_to_doc1),
            'unique_to_second': len(unique_to_doc2),
            'ai_comparison': ai_comparison
        }
        
        return {
            'success': True,
            'content': self._format_document_comparison(comparison_results),
            'metadata': {
                'similarity_score': similarity_ratio,
                'documents_compared': 2
            },
            'confidence_score': 0.85,
            'sources': ['Text Analysis', 'AI Comparison']
        }
    
    def _clean_and_format_text(self, document_text: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and format document text.
        
        Args:
            document_text: The document text to clean
            parameters: Cleaning parameters
            
        Returns:
            Text cleaning results
        """
        original_length = len(document_text)
        
        # Basic text cleaning
        cleaned_text = self._perform_text_cleaning(document_text, parameters)
        
        # Calculate cleaning statistics
        cleaned_length = len(cleaned_text)
        reduction_percentage = ((original_length - cleaned_length) / original_length) * 100
        
        cleaning_stats = {
            'original_length': original_length,
            'cleaned_length': cleaned_length,
            'reduction_percentage': round(reduction_percentage, 2),
            'cleaning_operations': self._get_cleaning_operations_performed(parameters)
        }
        
        return {
            'success': True,
            'content': self._format_text_cleaning_results(cleaned_text, cleaning_stats),
            'metadata': cleaning_stats,
            'confidence_score': 0.95,
            'sources': ['Text Processing']
        }
    
    # Helper methods for document analysis
    
    def _identify_sections(self, text: str) -> List[str]:
        """Identify document sections"""
        section_patterns = [
            r'^[IVX]+\.\s+([^\n]+)',  # Roman numerals
            r'^\d+\.\s+([^\n]+)',     # Arabic numerals
            r'^[A-Z][A-Z\s]+:',      # All caps headers
            r'^##?\s+([^\n]+)'       # Markdown headers
        ]
        
        sections = []
        for pattern in section_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            sections.extend(matches)
        
        return sections[:20]  # Limit to first 20 sections
    
    def _extract_headings(self, text: str) -> List[str]:
        """Extract document headings"""
        heading_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headings
            r'^([A-Z][A-Z\s]{3,}):?\s*$',  # All caps headings
            r'^\s*([A-Z][a-z\s]{5,})\s*$'  # Title case headings
        ]
        
        headings = []
        for pattern in heading_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            headings.extend(matches)
        
        return headings[:15]  # Limit to first 15 headings
    
    def _count_paragraphs(self, text: str) -> int:
        """Count paragraphs in the document"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return len(paragraphs)
    
    def _identify_lists(self, text: str) -> List[str]:
        """Identify lists in the document"""
        list_patterns = [
            r'^\s*[-*+]\s+(.+)$',  # Bullet points
            r'^\s*\d+[\.)]\s+(.+)$',  # Numbered lists
            r'^\s*[a-z][\.)]\s+(.+)$'  # Lettered lists
        ]
        
        lists = []
        for pattern in list_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            lists.extend(matches)
        
        return lists
    
    def _calculate_readability_metrics(self, text: str) -> Dict[str, float]:
        """Calculate basic readability metrics"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        if not words or not sentences:
            return {'flesch_score': 0, 'avg_word_length': 0, 'avg_sentence_length': 0}
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)
        
        # Simplified Flesch reading ease score
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (avg_word_length / 4.7))
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0-100
        
        return {
            'flesch_score': round(flesch_score, 2),
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2)
        }
    
    def _extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract legal-specific entities"""
        legal_patterns = {
            'case_names': r'([A-Z][a-z]+\s+v\.?\s+[A-Z][a-z]+)',
            'statutes': r'(\d+\s+U\.S\.C\.?\s+§?\s*\d+)',
            'courts': r'(Supreme Court|Court of Appeals|District Court|[A-Z][a-z]+\s+Court)',
            'legal_terms': r'\b(plaintiff|defendant|appellant|appellee|petitioner|respondent)\b'
        }
        
        legal_entities = {}
        for entity_type, pattern in legal_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            legal_entities[entity_type] = list(set(matches))
        
        return legal_entities
    
    def _find_important_dates(self, text: str) -> List[str]:
        """Find important dates in the document"""
        date_contexts = [
            r'(?:due|deadline|expires?|effective|termination|commencement).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}).*?(?:due|deadline|expires?|effective)'
        ]
        
        important_dates = []
        for pattern in date_contexts:
            matches = re.findall(pattern, text, re.IGNORECASE)
            important_dates.extend(matches)
        
        return list(set(important_dates))
    
    def _extract_monetary_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts from the document"""
        money_patterns = [
            r'\$[\d,]+\.?\d*',
            r'\b\d+\.\d{2}\s*dollars?',
            r'\b\d+\s*USD\b'
        ]
        
        amounts = []
        for pattern in money_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            amounts.extend(matches)
        
        return list(set(amounts))
    
    def _identify_deadlines(self, text: str) -> List[str]:
        """Identify deadlines in the document"""
        deadline_patterns = [
            r'(?:deadline|due date|must be completed by|no later than):\s*([^\n.]+)',
            r'([^\n.]*(?:deadline|due date)[^\n.]*)',
        ]
        
        deadlines = []
        for pattern in deadline_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            deadlines.extend(matches)
        
        return list(set(deadlines))
    
    def _extract_obligations(self, text: str) -> List[str]:
        """Extract obligations from the document"""
        obligation_patterns = [
            r'(?:shall|must|required to|obligated to)\s+([^.]+)',
            r'([^.]*(?:responsibility|obligation|duty)[^.]*)'
        ]
        
        obligations = []
        for pattern in obligation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            obligations.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return obligations[:10]  # Limit to first 10
    
    def _extract_rights(self, text: str) -> List[str]:
        """Extract rights from the document"""
        rights_patterns = [
            r'(?:right to|entitled to|may)\s+([^.]+)',
            r'([^.]*(?:rights?|entitlement)[^.]*)'
        ]
        
        rights = []
        for pattern in rights_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            rights.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return rights[:10]  # Limit to first 10
    
    def _extract_conditions(self, text: str) -> List[str]:
        """Extract conditions from the document"""
        condition_patterns = [
            r'(?:if|provided that|subject to|conditional upon)\s+([^.]+)',
            r'([^.]*(?:condition|requirement|prerequisite)[^.]*)'
        ]
        
        conditions = []
        for pattern in condition_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            conditions.extend([match.strip() for match in matches if len(match.strip()) > 10])
        
        return conditions[:10]  # Limit to first 10
    
    def _perform_text_cleaning(self, text: str, parameters: Dict[str, Any]) -> str:
        """Perform text cleaning operations"""
        cleaned_text = text
        
        # Remove extra whitespace
        if parameters.get('remove_extra_whitespace', True):
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Remove special characters
        if parameters.get('remove_special_chars', False):
            cleaned_text = re.sub(r'[^\w\s\.\,\;\:\!\?]', '', cleaned_text)
        
        # Normalize line breaks
        if parameters.get('normalize_line_breaks', True):
            cleaned_text = re.sub(r'\n+', '\n\n', cleaned_text)
        
        # Remove empty lines
        if parameters.get('remove_empty_lines', True):
            lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
        
        return cleaned_text.strip()
    
    def _get_cleaning_operations_performed(self, parameters: Dict[str, Any]) -> List[str]:
        """Get list of cleaning operations performed"""
        operations = []
        
        if parameters.get('remove_extra_whitespace', True):
            operations.append('Removed extra whitespace')
        if parameters.get('remove_special_chars', False):
            operations.append('Removed special characters')
        if parameters.get('normalize_line_breaks', True):
            operations.append('Normalized line breaks')
        if parameters.get('remove_empty_lines', True):
            operations.append('Removed empty lines')
        
        return operations
    
    # Formatting methods
    
    def _format_structure_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format structure analysis results"""
        return f"""
# Document Structure Analysis

## Structure Overview:
- Sections Found: {analysis['sections_found']}
- Headings Count: {analysis['headings_count']}
- Paragraphs: {analysis['paragraph_count']}
- Lists: {analysis['lists_count']}
- Total Words: {analysis['document_length']}

## Section Titles:
{chr(10).join(f"- {title}" for title in analysis['section_titles'][:10]) if analysis['section_titles'] else 'No clear sections identified'}

## Readability Metrics:
- Flesch Reading Ease: {analysis['readability_metrics']['flesch_score']}/100
- Average Word Length: {analysis['readability_metrics']['avg_word_length']} characters
- Average Sentence Length: {analysis['readability_metrics']['avg_sentence_length']} words

## AI Structure Analysis:
{analysis['ai_structure_analysis']}
"""
    
    def _format_entity_extraction(self, entities: Dict[str, List[str]], ai_entities: str) -> str:
        """Format entity extraction results"""
        result = "# Entity Extraction Results\n\n"
        
        for entity_type, entity_list in entities.items():
            if entity_list:
                result += f"## {entity_type.replace('_', ' ').title()}:\n"
                for entity in entity_list[:5]:  # Show first 5 of each type
                    result += f"- {entity}\n"
                result += "\n"
        
        result += "## AI-Identified Entities:\n"
        result += ai_entities
        
        return result
    
    def _format_content_summary(self, summary_data: Dict[str, Any]) -> str:
        """Format content summary results"""
        return f"""
# Document Summary

## Summary ({summary_data['summary_length'].title()}):
{summary_data['ai_summary']}

## Document Statistics:
- Original Length: {summary_data['original_word_count']} words
- Compression Ratio: {summary_data['compression_ratio']}

## Key Terms Found:
{', '.join(summary_data['key_terms_found']) if summary_data['key_terms_found'] else 'None identified'}
"""
    
    def _format_key_information(self, key_info: Dict[str, List[str]], ai_analysis: str) -> str:
        """Format key information extraction results"""
        result = "# Key Information Extraction\n\n"
        
        for info_type, info_list in key_info.items():
            if info_list:
                result += f"## {info_type.replace('_', ' ').title()}:\n"
                for item in info_list[:5]:  # Show first 5 of each type
                    result += f"- {item}\n"
                result += "\n"
        
        result += "## AI Analysis of Key Information:\n"
        result += ai_analysis
        
        return result
    
    def _format_document_comparison(self, results: Dict[str, Any]) -> str:
        """Format document comparison results"""
        return f"""
# Document Comparison Results

## Similarity Analysis:
- Similarity Score: {results['similarity_score']} ({results['similarity_score']*100:.1f}%)
- Common Words: {results['common_words_count']}
- Unique to First Document: {results['unique_to_first']}
- Unique to Second Document: {results['unique_to_second']}

## AI Comparison Analysis:
{results['ai_comparison']}
"""
    
    def _format_text_cleaning_results(self, cleaned_text: str, stats: Dict[str, Any]) -> str:
        """Format text cleaning results"""
        return f"""
# Text Cleaning Results

## Cleaning Statistics:
- Original Length: {stats['original_length']} characters
- Cleaned Length: {stats['cleaned_length']} characters
- Reduction: {stats['reduction_percentage']}%

## Operations Performed:
{chr(10).join(f"- {op}" for op in stats['cleaning_operations'])}

## Cleaned Text:
{cleaned_text[:1000]}{'...' if len(cleaned_text) > 1000 else ''}
"""
    
    def _get_features(self) -> List[str]:
        """Get document analyzer specific features"""
        base_features = super()._get_features()
        analyzer_features = [
            'structure_analysis',
            'entity_extraction',
            'content_summarization',
            'document_comparison',
            'text_cleaning',
            'readability_analysis'
        ]
        return base_features + analyzer_features