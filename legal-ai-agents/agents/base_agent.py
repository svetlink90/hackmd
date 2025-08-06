"""
Base Agent Class for Legal Research AI Agents

This module provides the foundational class that all specialized legal AI agents inherit from.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import openai
from anthropic import Anthropic

from config.settings import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Standardized response format for all agents"""
    success: bool
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    agent_type: str
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None
    sources: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format"""
        return {
            'success': self.success,
            'content': self.content,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'agent_type': self.agent_type,
            'processing_time': self.processing_time,
            'confidence_score': self.confidence_score,
            'sources': self.sources or []
        }

class BaseAgent(ABC):
    """
    Abstract base class for all legal research AI agents.
    
    This class provides common functionality including:
    - AI model integration (OpenAI, Anthropic)
    - Logging and monitoring
    - Response formatting
    - Error handling
    - Configuration management
    """
    
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the base agent.
        
        Args:
            model_name: Name of the AI model to use
            api_key: API key for the AI service
        """
        self.model_name = model_name or settings.DEFAULT_MODEL
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.agent_type = self.__class__.__name__
        
        # Initialize AI clients
        self._init_ai_clients()
        
        # Agent configuration
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        
        logger.info(f"Initialized {self.agent_type} with model {self.model_name}")
    
    def _init_ai_clients(self):
        """Initialize AI service clients"""
        try:
            if self.api_key and "gpt" in self.model_name.lower():
                openai.api_key = self.api_key
                self.client_type = "openai"
            elif settings.ANTHROPIC_API_KEY and "claude" in self.model_name.lower():
                self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.client_type = "anthropic"
            else:
                logger.warning("No valid API key found. Agent will run in mock mode.")
                self.client_type = "mock"
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
            self.client_type = "mock"
    
    def _call_ai_model(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Call the configured AI model with the given prompt.
        
        Args:
            prompt: The prompt to send to the AI model
            system_message: Optional system message for context
            
        Returns:
            AI model response as string
        """
        try:
            if self.client_type == "openai":
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})
                
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content
                
            elif self.client_type == "anthropic":
                full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
                response = self.anthropic_client.messages.create(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                return response.content[0].text
                
            else:  # Mock mode
                return f"Mock response for prompt: {prompt[:100]}..."
                
        except Exception as e:
            logger.error(f"AI model call failed: {e}")
            return f"Error: Unable to process request - {str(e)}"
    
    def _create_response(self, 
                        content: str, 
                        success: bool = True, 
                        metadata: Optional[Dict[str, Any]] = None,
                        processing_time: Optional[float] = None,
                        confidence_score: Optional[float] = None,
                        sources: Optional[List[str]] = None) -> AgentResponse:
        """
        Create a standardized agent response.
        
        Args:
            content: Main response content
            success: Whether the operation was successful
            metadata: Additional metadata
            processing_time: Time taken to process in seconds
            confidence_score: Confidence in the response (0-1)
            sources: List of sources used
            
        Returns:
            AgentResponse object
        """
        return AgentResponse(
            success=success,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now(),
            agent_type=self.agent_type,
            processing_time=processing_time,
            confidence_score=confidence_score,
            sources=sources
        )
    
    def _validate_input(self, text: str, max_length: Optional[int] = None) -> bool:
        """
        Validate input text.
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length
            
        Returns:
            True if valid, False otherwise
        """
        if not text or not isinstance(text, str):
            return False
        
        if max_length and len(text) > max_length:
            return False
            
        return True
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key legal terms from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of key terms
        """
        # Simple keyword extraction (can be enhanced with NLP libraries)
        legal_keywords = [
            'contract', 'agreement', 'clause', 'provision', 'statute', 
            'regulation', 'liability', 'damages', 'breach', 'obligation',
            'rights', 'duties', 'jurisdiction', 'precedent', 'case law'
        ]
        
        text_lower = text.lower()
        found_terms = [term for term in legal_keywords if term in text_lower]
        return found_terms
    
    @abstractmethod
    def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process a request and return a response.
        
        This method must be implemented by all subclasses.
        
        Args:
            request: Request dictionary containing the query and parameters
            
        Returns:
            AgentResponse object
        """
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities and configuration.
        
        Returns:
            Dictionary describing agent capabilities
        """
        return {
            'agent_type': self.agent_type,
            'model_name': self.model_name,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'client_type': self.client_type,
            'supported_formats': ['text', 'json'],
            'features': self._get_features()
        }
    
    def _get_features(self) -> List[str]:
        """
        Get list of features supported by this agent.
        Override in subclasses to specify agent-specific features.
        
        Returns:
            List of supported features
        """
        return ['text_analysis', 'ai_integration', 'structured_responses']
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the agent.
        
        Returns:
            Health status dictionary
        """
        status = {
            'agent_type': self.agent_type,
            'status': 'healthy',
            'client_type': self.client_type,
            'timestamp': datetime.now().isoformat()
        }
        
        # Test AI client connection
        try:
            test_response = self._call_ai_model("Test connection", "Respond with 'OK'")
            if "error" in test_response.lower():
                status['status'] = 'degraded'
                status['issues'] = ['AI client connection issues']
        except Exception as e:
            status['status'] = 'unhealthy'
            status['error'] = str(e)
        
        return status