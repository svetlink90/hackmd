"""
Legal Research AI Agents Package

This package contains AI agents specialized for legal research and document analysis.
"""

from .base_agent import BaseAgent, AgentResponse
from .legal_research_agent import LegalResearchAgent
from .document_analyzer import DocumentAnalyzer
from .compliance_checker_agent import ComplianceCheckerAgent

__all__ = [
    'BaseAgent',
    'AgentResponse', 
    'LegalResearchAgent',
    'DocumentAnalyzer',
    'ComplianceCheckerAgent'
]

__version__ = '1.0.0'