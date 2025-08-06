"""
Document Parser Utilities

This module provides utilities for parsing various document formats
commonly used in legal practice.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)

class DocumentParser:
    """
    A utility class for parsing various document formats
    """
    
    def __init__(self):
        """Initialize the document parser"""
        self.supported_formats = ['.txt', '.md', '.pdf', '.docx', '.doc', '.rtf']
        self._setup_parsers()
    
    def _setup_parsers(self):
        """Set up parsers for different formats"""
        # This would typically import and configure various parsing libraries
        # For now, we'll implement basic text parsing
        logger.info("Document parser initialized")
    
    def parse_file(self, file_path: Union[str, Path]) -> Dict[str, str]:
        """
        Parse a document file and extract text content
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        try:
            if file_extension in ['.txt', '.md']:
                return self._parse_text_file(file_path)
            elif file_extension == '.pdf':
                return self._parse_pdf_file(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._parse_word_file(file_path)
            elif file_extension == '.rtf':
                return self._parse_rtf_file(file_path)
            else:
                raise ValueError(f"Parser not implemented for: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return {
                'content': '',
                'metadata': {'error': str(e)},
                'success': False
            }
    
    def _parse_text_file(self, file_path: Path) -> Dict[str, str]:
        """Parse plain text and markdown files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'content': content,
                'metadata': {
                    'file_type': 'text',
                    'file_size': file_path.stat().st_size,
                    'line_count': len(content.splitlines()),
                    'word_count': len(content.split()),
                    'char_count': len(content)
                },
                'success': True
            }
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                
                return {
                    'content': content,
                    'metadata': {
                        'file_type': 'text',
                        'encoding': 'latin-1',
                        'file_size': file_path.stat().st_size,
                        'word_count': len(content.split())
                    },
                    'success': True
                }
            except Exception as e:
                raise Exception(f"Could not decode file: {e}")
    
    def _parse_pdf_file(self, file_path: Path) -> Dict[str, str]:
        """Parse PDF files (placeholder implementation)"""
        # In a real implementation, you would use libraries like PyPDF2, pdfplumber, or pymupdf
        logger.warning("PDF parsing not fully implemented - returning placeholder")
        
        return {
            'content': f"[PDF parsing not implemented for {file_path.name}]",
            'metadata': {
                'file_type': 'pdf',
                'file_size': file_path.stat().st_size,
                'note': 'PDF parsing requires additional libraries'
            },
            'success': False
        }
    
    def _parse_word_file(self, file_path: Path) -> Dict[str, str]:
        """Parse Word documents (placeholder implementation)"""
        # In a real implementation, you would use python-docx
        logger.warning("Word document parsing not fully implemented - returning placeholder")
        
        return {
            'content': f"[Word document parsing not implemented for {file_path.name}]",
            'metadata': {
                'file_type': 'word',
                'file_size': file_path.stat().st_size,
                'note': 'Word document parsing requires additional libraries'
            },
            'success': False
        }
    
    def _parse_rtf_file(self, file_path: Path) -> Dict[str, str]:
        """Parse RTF files (placeholder implementation)"""
        logger.warning("RTF parsing not fully implemented - returning placeholder")
        
        return {
            'content': f"[RTF parsing not implemented for {file_path.name}]",
            'metadata': {
                'file_type': 'rtf',
                'file_size': file_path.stat().st_size,
                'note': 'RTF parsing requires additional libraries'
            },
            'success': False
        }
    
    def extract_metadata(self, file_path: Union[str, Path]) -> Dict[str, any]:
        """
        Extract metadata from a document file
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing file metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = file_path.stat()
        
        return {
            'filename': file_path.name,
            'file_extension': file_path.suffix,
            'file_size': stat.st_size,
            'created_time': stat.st_ctime,
            'modified_time': stat.st_mtime,
            'is_readable': os.access(file_path, os.R_OK),
            'absolute_path': str(file_path.absolute())
        }
    
    def batch_parse(self, directory: Union[str, Path], 
                   file_pattern: str = "*") -> Dict[str, Dict[str, str]]:
        """
        Parse multiple documents in a directory
        
        Args:
            directory: Directory containing documents
            file_pattern: File pattern to match (default: all files)
            
        Returns:
            Dictionary mapping filenames to parsed content
        """
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory: {directory}")
        
        results = {}
        
        for file_path in directory.glob(file_pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    results[file_path.name] = self.parse_file(file_path)
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                    results[file_path.name] = {
                        'content': '',
                        'metadata': {'error': str(e)},
                        'success': False
                    }
        
        return results
    
    def clean_text(self, text: str, 
                   remove_extra_whitespace: bool = True,
                   remove_empty_lines: bool = True,
                   normalize_quotes: bool = True) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Text to clean
            remove_extra_whitespace: Remove extra spaces and tabs
            remove_empty_lines: Remove empty lines
            normalize_quotes: Normalize quote characters
            
        Returns:
            Cleaned text
        """
        if not text:
            return text
        
        cleaned = text
        
        if normalize_quotes:
            # Normalize various quote characters
            cleaned = re.sub(r'["""]', '"', cleaned)
            cleaned = re.sub(r'[''']', "'", cleaned)
        
        if remove_extra_whitespace:
            # Remove extra spaces and tabs
            cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        
        if remove_empty_lines:
            # Remove empty lines
            lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
            cleaned = '\n'.join(lines)
        
        return cleaned.strip()
    
    def extract_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Extract sections from document text based on common patterns
        
        Args:
            text: Document text to analyze
            
        Returns:
            List of sections with titles and content
        """
        sections = []
        
        # Common section patterns in legal documents
        section_patterns = [
            r'^([IVX]+)\.\s+(.+)$',  # Roman numerals (I. II. III.)
            r'^(\d+)\.\s+(.+)$',     # Arabic numerals (1. 2. 3.)
            r'^([A-Z][A-Z\s]{2,}):?\s*$',  # All caps headings
            r'^#{1,6}\s+(.+)$',      # Markdown headers
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):?\s*$'  # Title case headings
        ]
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_content:
                    current_content.append('')
                continue
            
            # Check if line matches any section pattern
            is_section_header = False
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous section
                    if current_section:
                        sections.append({
                            'title': current_section,
                            'content': '\n'.join(current_content).strip()
                        })
                    
                    # Start new section
                    current_section = line
                    current_content = []
                    is_section_header = True
                    break
            
            if not is_section_header:
                current_content.append(line)
        
        # Add the last section
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })
        
        return sections
    
    def get_document_stats(self, text: str) -> Dict[str, int]:
        """
        Get basic statistics about a document
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with document statistics
        """
        if not text:
            return {
                'characters': 0,
                'words': 0,
                'lines': 0,
                'paragraphs': 0,
                'sentences': 0
            }
        
        # Basic counts
        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.splitlines())
        
        # Paragraph count (separated by double newlines)
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # Sentence count (approximate)
        sentence_count = len(re.findall(r'[.!?]+', text))
        
        return {
            'characters': char_count,
            'words': word_count,
            'lines': line_count,
            'paragraphs': paragraph_count,
            'sentences': sentence_count
        }

# Convenience functions
def parse_document(file_path: Union[str, Path]) -> Dict[str, str]:
    """
    Convenience function to parse a single document
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Parsed document content and metadata
    """
    parser = DocumentParser()
    return parser.parse_file(file_path)

def parse_directory(directory: Union[str, Path]) -> Dict[str, Dict[str, str]]:
    """
    Convenience function to parse all documents in a directory
    
    Args:
        directory: Directory containing documents
        
    Returns:
        Dictionary mapping filenames to parsed content
    """
    parser = DocumentParser()
    return parser.batch_parse(directory)