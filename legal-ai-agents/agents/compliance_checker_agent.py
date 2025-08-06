"""
Compliance Checker Agent

Specialized AI agent for sanctions screening and compliance checking of DeFi protocols,
crypto projects, and digital assets. Performs comprehensive checks against sanctions lists,
enforcement actions, and regulatory restrictions.
"""

import time
import re
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import requests
from urllib.parse import quote

from .base_agent import BaseAgent, AgentResponse
from config.settings import settings

@dataclass
class SanctionsMatch:
    """Data class for sanctions screening results"""
    entity_name: str
    match_type: str  # 'exact', 'fuzzy', 'alias'
    sanctions_list: str  # 'OFAC_SDN', 'UN_SC', 'EU_SANCTIONS', etc.
    match_score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    risk_level: str  # 'HIGH', 'MEDIUM', 'LOW'

@dataclass
class EnforcementAction:
    """Data class for enforcement actions"""
    agency: str
    action_type: str
    date: str
    description: str
    url: str
    severity: str

@dataclass
class ComplianceRisk:
    """Data class for compliance risk assessment"""
    risk_category: str
    risk_level: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    description: str
    recommendations: List[str]
    sources: List[str]

class ComplianceCheckerAgent(BaseAgent):
    """
    Specialized agent for sanctions screening and compliance checking.
    
    Capabilities:
    - OFAC SDN List screening
    - UN Security Council sanctions screening
    - EU sanctions list checking
    - Enforcement action tracking
    - Jurisdiction restriction analysis
    - Entity resolution and fuzzy matching
    - Continuous monitoring and alerts
    """
    
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the Compliance Checker Agent"""
        super().__init__(model_name, api_key)
        
        # Sanctions data sources
        self.sanctions_sources = {
            'OFAC_SDN': 'https://www.treasury.gov/ofac/downloads/sdn.xml',
            'OFAC_CONS': 'https://www.treasury.gov/ofac/downloads/cons.xml',
            'UN_SC': 'https://scsanctions.un.org/resources/xml/en/consolidated.xml',
            'EU_SANCTIONS': 'https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content',
            'UK_HMT': 'https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.json'
        }
        
        # Enforcement agencies and their APIs/sources
        self.enforcement_sources = {
            'SEC': 'https://www.sec.gov/litigation/litreleases',
            'CFTC': 'https://www.cftc.gov/LawRegulation/Enforcement',
            'DOJ': 'https://www.justice.gov/criminal-fraud',
            'FINRA': 'https://www.finra.org/rules-guidance/oversight-enforcement',
            'FINCEN': 'https://www.fincen.gov/news/enforcement-actions'
        }
        
        # Restricted jurisdictions for crypto/DeFi
        self.restricted_jurisdictions = {
            'HIGH_RISK': ['AF', 'BY', 'MM', 'CF', 'CN', 'CU', 'IR', 'IQ', 'LB', 'LY', 'ML', 'NI', 'KP', 'RU', 'SO', 'SS', 'SD', 'SY', 'UA', 'VE', 'YE', 'ZW'],
            'MEDIUM_RISK': ['BD', 'BO', 'KH', 'EC', 'EG', 'GH', 'GT', 'HT', 'JM', 'JO', 'KE', 'LA', 'MV', 'MZ', 'NP', 'NI', 'PK', 'PH', 'LK', 'TZ', 'TH', 'TN', 'TR', 'UG', 'VN', 'ZM'],
            'REGULATORY_RESTRICTED': ['US', 'CN', 'KR', 'JP', 'IN']  # Countries with specific DeFi/crypto restrictions
        }
        
        # Cache for sanctions data
        self.sanctions_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 3600  # 1 hour
        
        self.compliance_specializations = [
            'sanctions_screening',
            'enforcement_tracking',
            'jurisdiction_analysis',
            'entity_resolution',
            'risk_assessment',
            'continuous_monitoring'
        ]
    
    def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process a compliance checking request.
        
        Args:
            request: Dictionary with keys:
                - action: Type of compliance check
                - target: Entity/protocol/asset to check
                - parameters: Additional parameters
                
        Returns:
            AgentResponse with compliance analysis
        """
        start_time = time.time()
        
        try:
            action = request.get('action', 'full_compliance_check')
            target = request.get('target', '')
            parameters = request.get('parameters', {})
            
            if not self._validate_input(target):
                return self._create_response(
                    "Invalid target provided for compliance check",
                    success=False,
                    metadata={'error': 'Invalid or empty target'}
                )
            
            # Route to appropriate handler
            if action == 'full_compliance_check':
                result = self._full_compliance_check(target, parameters)
            elif action == 'sanctions_screening':
                result = self._sanctions_screening(target, parameters)
            elif action == 'enforcement_check':
                result = self._enforcement_action_check(target, parameters)
            elif action == 'jurisdiction_analysis':
                result = self._jurisdiction_analysis(target, parameters)
            elif action == 'entity_resolution':
                result = self._entity_resolution(target, parameters)
            elif action == 'risk_assessment':
                result = self._risk_assessment(target, parameters)
            else:
                return self._create_response(
                    f"Unknown compliance action: {action}",
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
                f"Error processing compliance request: {str(e)}",
                success=False,
                metadata={'error': str(e)},
                processing_time=processing_time
            )
    
    def _full_compliance_check(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive compliance check including sanctions, enforcement, and jurisdiction analysis.
        
        Args:
            target: Entity/protocol/asset to check
            parameters: Additional parameters
            
        Returns:
            Comprehensive compliance analysis results
        """
        try:
            # Initialize results structure
            compliance_results = {
                'target': target,
                'check_date': datetime.now().isoformat(),
                'sanctions_screening': None,
                'enforcement_actions': None,
                'jurisdiction_analysis': None,
                'affiliated_entities': [],
                'overall_risk_level': 'UNKNOWN',
                'recommendations': []
            }
            
            # 1. Sanctions Screening
            sanctions_result = self._sanctions_screening(target, parameters)
            compliance_results['sanctions_screening'] = sanctions_result.get('data', {})
            
            # 2. Enforcement Action Check
            enforcement_result = self._enforcement_action_check(target, parameters)
            compliance_results['enforcement_actions'] = enforcement_result.get('data', {})
            
            # 3. Jurisdiction Analysis
            jurisdiction_result = self._jurisdiction_analysis(target, parameters)
            compliance_results['jurisdiction_analysis'] = jurisdiction_result.get('data', {})
            
            # 4. Check affiliated entities (founders, contributors, etc.)
            affiliated_entities = parameters.get('affiliated_entities', [])
            if affiliated_entities:
                for entity in affiliated_entities:
                    entity_check = self._sanctions_screening(entity, {})
                    compliance_results['affiliated_entities'].append({
                        'name': entity,
                        'sanctions_check': entity_check.get('data', {}),
                        'risk_level': self._calculate_entity_risk_level(entity_check.get('data', {}))
                    })
            
            # 5. Calculate overall risk level
            compliance_results['overall_risk_level'] = self._calculate_overall_risk_level(compliance_results)
            
            # 6. Generate recommendations
            compliance_results['recommendations'] = self._generate_compliance_recommendations(compliance_results)
            
            # 7. Get AI-powered analysis
            ai_analysis = self._get_ai_compliance_analysis(target, compliance_results)
            
            formatted_report = self._format_compliance_report(compliance_results, ai_analysis)
            
            return {
                'success': True,
                'content': formatted_report,
                'data': compliance_results,
                'metadata': {
                    'target': target,
                    'overall_risk_level': compliance_results['overall_risk_level'],
                    'sanctions_matches': len(compliance_results['sanctions_screening'].get('matches', [])),
                    'enforcement_actions': len(compliance_results['enforcement_actions'].get('actions', [])),
                    'affiliated_entities_checked': len(compliance_results['affiliated_entities'])
                },
                'confidence_score': 0.90,
                'sources': self._get_data_sources()
            }
            
        except Exception as e:
            return {
                'success': False,
                'content': f"Error in full compliance check: {str(e)}",
                'metadata': {'error': str(e)}
            }
    
    def _sanctions_screening(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform sanctions screening against multiple sanctions lists.
        
        Args:
            target: Entity to screen
            parameters: Screening parameters
            
        Returns:
            Sanctions screening results
        """
        try:
            matches = []
            screening_results = {
                'target': target,
                'screening_date': datetime.now().isoformat(),
                'lists_checked': [],
                'matches': [],
                'risk_level': 'LOW'
            }
            
            # Check against each sanctions list
            for list_name, list_url in self.sanctions_sources.items():
                try:
                    # Get sanctions data (with caching)
                    sanctions_data = self._get_sanctions_data(list_name, list_url)
                    screening_results['lists_checked'].append(list_name)
                    
                    # Perform matching
                    list_matches = self._match_against_sanctions_list(target, sanctions_data, list_name)
                    matches.extend(list_matches)
                    
                except Exception as e:
                    # Log error but continue with other lists
                    screening_results[f'{list_name}_error'] = str(e)
            
            # Process matches
            screening_results['matches'] = [match.__dict__ for match in matches]
            screening_results['risk_level'] = self._calculate_sanctions_risk_level(matches)
            
            # Additional checks for crypto-specific sanctions
            crypto_matches = self._check_crypto_specific_sanctions(target)
            if crypto_matches:
                screening_results['matches'].extend([match.__dict__ for match in crypto_matches])
                screening_results['crypto_specific_matches'] = True
            
            formatted_results = self._format_sanctions_screening_results(screening_results)
            
            return {
                'success': True,
                'content': formatted_results,
                'data': screening_results,
                'metadata': {
                    'matches_found': len(screening_results['matches']),
                    'risk_level': screening_results['risk_level'],
                    'lists_checked': len(screening_results['lists_checked'])
                },
                'confidence_score': 0.95,
                'sources': list(self.sanctions_sources.keys())
            }
            
        except Exception as e:
            return {
                'success': False,
                'content': f"Error in sanctions screening: {str(e)}",
                'metadata': {'error': str(e)}
            }
    
    def _enforcement_action_check(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for enforcement actions and lawsuits against the target entity.
        
        Args:
            target: Entity to check
            parameters: Check parameters
            
        Returns:
            Enforcement action results
        """
        try:
            enforcement_results = {
                'target': target,
                'check_date': datetime.now().isoformat(),
                'actions': [],
                'agencies_checked': [],
                'risk_level': 'LOW'
            }
            
            # Search for enforcement actions across different agencies
            for agency, source_info in self.enforcement_sources.items():
                try:
                    # Simulate enforcement action search (in production, would use actual APIs)
                    actions = self._search_enforcement_actions(target, agency, source_info)
                    enforcement_results['actions'].extend(actions)
                    enforcement_results['agencies_checked'].append(agency)
                    
                except Exception as e:
                    enforcement_results[f'{agency}_error'] = str(e)
            
            # Check court records and legal databases
            court_actions = self._search_court_records(target)
            if court_actions:
                enforcement_results['actions'].extend(court_actions)
                enforcement_results['court_records_checked'] = True
            
            # Calculate risk level based on enforcement actions
            enforcement_results['risk_level'] = self._calculate_enforcement_risk_level(enforcement_results['actions'])
            
            # Get AI analysis of enforcement patterns
            ai_analysis = self._get_ai_enforcement_analysis(target, enforcement_results)
            
            formatted_results = self._format_enforcement_results(enforcement_results, ai_analysis)
            
            return {
                'success': True,
                'content': formatted_results,
                'data': enforcement_results,
                'metadata': {
                    'actions_found': len(enforcement_results['actions']),
                    'risk_level': enforcement_results['risk_level'],
                    'agencies_checked': len(enforcement_results['agencies_checked'])
                },
                'confidence_score': 0.85,
                'sources': list(self.enforcement_sources.keys())
            }
            
        except Exception as e:
            return {
                'success': False,
                'content': f"Error in enforcement action check: {str(e)}",
                'metadata': {'error': str(e)}
            }
    
    def _jurisdiction_analysis(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze jurisdiction restrictions and regulatory compliance.
        
        Args:
            target: Entity to analyze
            parameters: Analysis parameters
            
        Returns:
            Jurisdiction analysis results
        """
        try:
            jurisdiction_results = {
                'target': target,
                'analysis_date': datetime.now().isoformat(),
                'restricted_jurisdictions': [],
                'regulatory_requirements': {},
                'compliance_recommendations': [],
                'risk_level': 'LOW'
            }
            
            # Analyze jurisdiction restrictions
            for risk_level, jurisdictions in self.restricted_jurisdictions.items():
                for jurisdiction in jurisdictions:
                    restriction_info = self._analyze_jurisdiction_restriction(target, jurisdiction, risk_level)
                    if restriction_info:
                        jurisdiction_results['restricted_jurisdictions'].append(restriction_info)
            
            # Check specific regulatory requirements
            regulatory_reqs = self._check_regulatory_requirements(target, parameters)
            jurisdiction_results['regulatory_requirements'] = regulatory_reqs
            
            # Generate compliance recommendations
            recommendations = self._generate_jurisdiction_recommendations(jurisdiction_results)
            jurisdiction_results['compliance_recommendations'] = recommendations
            
            # Calculate overall jurisdiction risk
            jurisdiction_results['risk_level'] = self._calculate_jurisdiction_risk_level(jurisdiction_results)
            
            # Get AI analysis
            ai_analysis = self._get_ai_jurisdiction_analysis(target, jurisdiction_results)
            
            formatted_results = self._format_jurisdiction_analysis(jurisdiction_results, ai_analysis)
            
            return {
                'success': True,
                'content': formatted_results,
                'data': jurisdiction_results,
                'metadata': {
                    'restricted_jurisdictions': len(jurisdiction_results['restricted_jurisdictions']),
                    'risk_level': jurisdiction_results['risk_level'],
                    'recommendations': len(jurisdiction_results['compliance_recommendations'])
                },
                'confidence_score': 0.88,
                'sources': ['Regulatory Databases', 'Jurisdiction Analysis']
            }
            
        except Exception as e:
            return {
                'success': False,
                'content': f"Error in jurisdiction analysis: {str(e)}",
                'metadata': {'error': str(e)}
            }
    
    def _entity_resolution(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve entity names and find related entities, aliases, and variations.
        
        Args:
            target: Entity to resolve
            parameters: Resolution parameters
            
        Returns:
            Entity resolution results
        """
        try:
            resolution_results = {
                'target': target,
                'resolution_date': datetime.now().isoformat(),
                'aliases': [],
                'related_entities': [],
                'entity_type': 'UNKNOWN',
                'confidence_score': 0.0
            }
            
            # Identify entity type (DeFi protocol, crypto project, individual, etc.)
            entity_type = self._identify_entity_type(target)
            resolution_results['entity_type'] = entity_type
            
            # Find aliases and variations
            aliases = self._find_entity_aliases(target, entity_type)
            resolution_results['aliases'] = aliases
            
            # Find related entities (founders, contributors, parent companies)
            related_entities = self._find_related_entities(target, entity_type)
            resolution_results['related_entities'] = related_entities
            
            # Calculate confidence score
            resolution_results['confidence_score'] = self._calculate_resolution_confidence(resolution_results)
            
            formatted_results = self._format_entity_resolution_results(resolution_results)
            
            return {
                'success': True,
                'content': formatted_results,
                'data': resolution_results,
                'metadata': {
                    'entity_type': entity_type,
                    'aliases_found': len(aliases),
                    'related_entities': len(related_entities),
                    'confidence_score': resolution_results['confidence_score']
                },
                'confidence_score': resolution_results['confidence_score'],
                'sources': ['Entity Databases', 'Crypto Registries']
            }
            
        except Exception as e:
            return {
                'success': False,
                'content': f"Error in entity resolution: {str(e)}",
                'metadata': {'error': str(e)}
            }
    
    def _risk_assessment(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment based on all compliance factors.
        
        Args:
            target: Entity to assess
            parameters: Assessment parameters
            
        Returns:
            Risk assessment results
        """
        try:
            # Perform all compliance checks
            full_check = self._full_compliance_check(target, parameters)
            
            if not full_check['success']:
                return full_check
            
            compliance_data = full_check['data']
            
            # Calculate detailed risk scores
            risk_factors = {
                'sanctions_risk': self._calculate_sanctions_risk_score(compliance_data.get('sanctions_screening', {})),
                'enforcement_risk': self._calculate_enforcement_risk_score(compliance_data.get('enforcement_actions', {})),
                'jurisdiction_risk': self._calculate_jurisdiction_risk_score(compliance_data.get('jurisdiction_analysis', {})),
                'entity_risk': self._calculate_entity_risk_score(compliance_data.get('affiliated_entities', []))
            }
            
            # Calculate overall risk score
            overall_risk_score = self._calculate_weighted_risk_score(risk_factors)
            overall_risk_level = self._risk_score_to_level(overall_risk_score)
            
            risk_assessment = {
                'target': target,
                'assessment_date': datetime.now().isoformat(),
                'risk_factors': risk_factors,
                'overall_risk_score': overall_risk_score,
                'overall_risk_level': overall_risk_level,
                'risk_breakdown': self._create_risk_breakdown(risk_factors),
                'mitigation_strategies': self._generate_mitigation_strategies(risk_factors),
                'monitoring_recommendations': self._generate_monitoring_recommendations(compliance_data)
            }
            
            # Get AI-powered risk analysis
            ai_risk_analysis = self._get_ai_risk_analysis(target, risk_assessment)
            
            formatted_assessment = self._format_risk_assessment(risk_assessment, ai_risk_analysis)
            
            return {
                'success': True,
                'content': formatted_assessment,
                'data': risk_assessment,
                'metadata': {
                    'overall_risk_score': overall_risk_score,
                    'overall_risk_level': overall_risk_level,
                    'high_risk_factors': len([f for f, score in risk_factors.items() if score > 0.7])
                },
                'confidence_score': 0.92,
                'sources': ['Comprehensive Compliance Analysis']
            }
            
        except Exception as e:
            return {
                'success': False,
                'content': f"Error in risk assessment: {str(e)}",
                'metadata': {'error': str(e)}
            }
    
    # Helper methods for data retrieval and processing
    
    def _get_sanctions_data(self, list_name: str, list_url: str) -> Dict[str, Any]:
        """Get sanctions data with caching"""
        # Check cache first
        if (list_name in self.sanctions_cache and 
            list_name in self.cache_expiry and 
            datetime.now().timestamp() < self.cache_expiry[list_name]):
            return self.sanctions_cache[list_name]
        
        # In production, this would fetch actual sanctions data
        # For now, return mock data structure
        mock_data = {
            'entities': [
                {'name': 'Sample Sanctioned Entity', 'type': 'individual', 'program': 'SDGT'},
                {'name': 'Another Sanctioned Entity', 'type': 'entity', 'program': 'IRAN'}
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        # Cache the data
        self.sanctions_cache[list_name] = mock_data
        self.cache_expiry[list_name] = datetime.now().timestamp() + self.cache_duration
        
        return mock_data
    
    def _match_against_sanctions_list(self, target: str, sanctions_data: Dict[str, Any], list_name: str) -> List[SanctionsMatch]:
        """Match target against sanctions list"""
        matches = []
        
        # Simple fuzzy matching implementation
        target_lower = target.lower()
        
        for entity in sanctions_data.get('entities', []):
            entity_name = entity.get('name', '').lower()
            
            # Exact match
            if target_lower == entity_name:
                matches.append(SanctionsMatch(
                    entity_name=entity.get('name'),
                    match_type='exact',
                    sanctions_list=list_name,
                    match_score=1.0,
                    details=entity,
                    risk_level='HIGH'
                ))
            
            # Fuzzy match (simplified)
            elif target_lower in entity_name or entity_name in target_lower:
                similarity_score = self._calculate_similarity(target_lower, entity_name)
                if similarity_score > 0.8:
                    matches.append(SanctionsMatch(
                        entity_name=entity.get('name'),
                        match_type='fuzzy',
                        sanctions_list=list_name,
                        match_score=similarity_score,
                        details=entity,
                        risk_level='MEDIUM' if similarity_score > 0.9 else 'LOW'
                    ))
        
        return matches
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity (simplified Levenshtein distance)"""
        if not str1 or not str2:
            return 0.0
        
        # Simple similarity calculation
        common_chars = sum(1 for c in str1 if c in str2)
        max_len = max(len(str1), len(str2))
        
        return common_chars / max_len if max_len > 0 else 0.0
    
    def _check_crypto_specific_sanctions(self, target: str) -> List[SanctionsMatch]:
        """Check against crypto-specific sanctions (e.g., OFAC crypto addresses)"""
        # In production, this would check against OFAC's Specially Designated Nationals
        # crypto address list and other crypto-specific sanctions
        matches = []
        
        # Mock crypto-specific check
        crypto_sanctions = [
            'tornado.cash',
            'blender.io',
            'mixer.money'
        ]
        
        target_lower = target.lower()
        for sanctioned_service in crypto_sanctions:
            if sanctioned_service in target_lower:
                matches.append(SanctionsMatch(
                    entity_name=sanctioned_service,
                    match_type='exact',
                    sanctions_list='OFAC_CRYPTO',
                    match_score=1.0,
                    details={'service': sanctioned_service, 'type': 'crypto_service'},
                    risk_level='HIGH'
                ))
        
        return matches
    
    def _search_enforcement_actions(self, target: str, agency: str, source_info: str) -> List[EnforcementAction]:
        """Search for enforcement actions from specific agency"""
        # In production, this would query actual enforcement databases
        actions = []
        
        # Mock enforcement action search
        if 'defi' in target.lower() or 'crypto' in target.lower():
            actions.append(EnforcementAction(
                agency=agency,
                action_type='Investigation',
                date='2024-01-15',
                description=f'Ongoing investigation into {target} for potential securities violations',
                url=f'{source_info}/case-{target.lower()}',
                severity='MEDIUM'
            ))
        
        return actions
    
    def _search_court_records(self, target: str) -> List[EnforcementAction]:
        """Search court records for lawsuits"""
        # Mock court records search
        court_actions = []
        
        # In production, would search PACER, state court databases, etc.
        return court_actions
    
    # Risk calculation methods
    
    def _calculate_sanctions_risk_level(self, matches: List[SanctionsMatch]) -> str:
        """Calculate risk level based on sanctions matches"""
        if not matches:
            return 'LOW'
        
        high_risk_matches = [m for m in matches if m.risk_level == 'HIGH']
        if high_risk_matches:
            return 'CRITICAL'
        
        medium_risk_matches = [m for m in matches if m.risk_level == 'MEDIUM']
        if medium_risk_matches:
            return 'HIGH'
        
        return 'MEDIUM'
    
    def _calculate_enforcement_risk_level(self, actions: List[EnforcementAction]) -> str:
        """Calculate risk level based on enforcement actions"""
        if not actions:
            return 'LOW'
        
        high_severity = [a for a in actions if a.severity == 'HIGH']
        if high_severity:
            return 'HIGH'
        
        medium_severity = [a for a in actions if a.severity == 'MEDIUM']
        if medium_severity:
            return 'MEDIUM'
        
        return 'LOW'
    
    def _calculate_overall_risk_level(self, compliance_results: Dict[str, Any]) -> str:
        """Calculate overall compliance risk level"""
        risk_factors = []
        
        # Sanctions risk
        sanctions_risk = compliance_results.get('sanctions_screening', {}).get('risk_level', 'LOW')
        risk_factors.append(sanctions_risk)
        
        # Enforcement risk
        enforcement_risk = compliance_results.get('enforcement_actions', {}).get('risk_level', 'LOW')
        risk_factors.append(enforcement_risk)
        
        # Jurisdiction risk
        jurisdiction_risk = compliance_results.get('jurisdiction_analysis', {}).get('risk_level', 'LOW')
        risk_factors.append(jurisdiction_risk)
        
        # Calculate overall risk
        if 'CRITICAL' in risk_factors:
            return 'CRITICAL'
        elif 'HIGH' in risk_factors:
            return 'HIGH'
        elif 'MEDIUM' in risk_factors:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    # AI analysis methods
    
    def _get_ai_compliance_analysis(self, target: str, compliance_results: Dict[str, Any]) -> str:
        """Get AI-powered compliance analysis"""
        prompt = f"""
        Analyze the compliance screening results for {target} and provide professional insights:
        
        Sanctions Screening: {compliance_results.get('sanctions_screening', {})}
        Enforcement Actions: {compliance_results.get('enforcement_actions', {})}
        Jurisdiction Analysis: {compliance_results.get('jurisdiction_analysis', {})}
        
        Provide a comprehensive compliance assessment including:
        1. Key compliance risks identified
        2. Regulatory implications
        3. Recommended risk mitigation strategies
        4. Ongoing monitoring requirements
        
        Focus on practical, actionable recommendations for a DeFi/crypto context.
        """
        
        return self._call_ai_model(
            prompt,
            "You are a compliance expert specializing in crypto/DeFi regulatory requirements."
        )
    
    def _get_ai_enforcement_analysis(self, target: str, enforcement_results: Dict[str, Any]) -> str:
        """Get AI analysis of enforcement patterns"""
        prompt = f"""
        Analyze the enforcement action history for {target}:
        
        {json.dumps(enforcement_results, indent=2)}
        
        Provide analysis on:
        1. Enforcement pattern trends
        2. Regulatory agency focus areas
        3. Potential future enforcement risks
        4. Recommended compliance strategies
        """
        
        return self._call_ai_model(
            prompt,
            "You are a regulatory enforcement expert with deep knowledge of crypto/DeFi enforcement trends."
        )
    
    # Formatting methods
    
    def _format_compliance_report(self, compliance_results: Dict[str, Any], ai_analysis: str) -> str:
        """Format comprehensive compliance report"""
        return f"""
# Compliance Screening Report

## Target Entity: {compliance_results['target']}
## Overall Risk Level: {compliance_results['overall_risk_level']}
## Report Date: {compliance_results['check_date']}

## Executive Summary
{ai_analysis}

## Sanctions Screening Results
- **Risk Level**: {compliance_results['sanctions_screening'].get('risk_level', 'UNKNOWN')}
- **Matches Found**: {len(compliance_results['sanctions_screening'].get('matches', []))}
- **Lists Checked**: {', '.join(compliance_results['sanctions_screening'].get('lists_checked', []))}

### Sanctions Matches
{self._format_sanctions_matches(compliance_results['sanctions_screening'].get('matches', []))}

## Enforcement Actions
- **Risk Level**: {compliance_results['enforcement_actions'].get('risk_level', 'UNKNOWN')}
- **Actions Found**: {len(compliance_results['enforcement_actions'].get('actions', []))}
- **Agencies Checked**: {', '.join(compliance_results['enforcement_actions'].get('agencies_checked', []))}

## Jurisdiction Analysis
- **Risk Level**: {compliance_results['jurisdiction_analysis'].get('risk_level', 'UNKNOWN')}
- **Restricted Jurisdictions**: {len(compliance_results['jurisdiction_analysis'].get('restricted_jurisdictions', []))}

## Affiliated Entities
{self._format_affiliated_entities(compliance_results.get('affiliated_entities', []))}

## Recommendations
{chr(10).join(f"- {rec}" for rec in compliance_results.get('recommendations', []))}

## Next Steps
1. Review all identified risks with legal counsel
2. Implement recommended risk mitigation measures
3. Establish ongoing monitoring procedures
4. Document compliance procedures and decisions
"""
    
    def _format_sanctions_matches(self, matches: List[Dict[str, Any]]) -> str:
        """Format sanctions matches for display"""
        if not matches:
            return "No sanctions matches found."
        
        formatted = ""
        for match in matches:
            formatted += f"""
- **Entity**: {match.get('entity_name', 'Unknown')}
- **Match Type**: {match.get('match_type', 'Unknown')}
- **Sanctions List**: {match.get('sanctions_list', 'Unknown')}
- **Match Score**: {match.get('match_score', 0.0):.2f}
- **Risk Level**: {match.get('risk_level', 'Unknown')}

"""
        return formatted
    
    def _format_affiliated_entities(self, entities: List[Dict[str, Any]]) -> str:
        """Format affiliated entities results"""
        if not entities:
            return "No affiliated entities checked."
        
        formatted = ""
        for entity in entities:
            formatted += f"""
- **Name**: {entity.get('name', 'Unknown')}
- **Risk Level**: {entity.get('risk_level', 'Unknown')}
- **Sanctions Matches**: {len(entity.get('sanctions_check', {}).get('matches', []))}

"""
        return formatted
    
    def _get_data_sources(self) -> List[str]:
        """Get list of data sources used"""
        return list(self.sanctions_sources.keys()) + list(self.enforcement_sources.keys()) + ['AI Analysis']
    
    def _get_features(self) -> List[str]:
        """Get compliance checker specific features"""
        base_features = super()._get_features()
        compliance_features = [
            'sanctions_screening',
            'enforcement_tracking',
            'jurisdiction_analysis',
            'entity_resolution',
            'risk_assessment',
            'continuous_monitoring',
            'crypto_compliance',
            'defi_analysis'
        ]
        return base_features + compliance_features
    
    # Placeholder methods for additional functionality
    # These would be fully implemented in production
    
    def _identify_entity_type(self, target: str) -> str:
        """Identify the type of entity (DeFi protocol, crypto project, etc.)"""
        target_lower = target.lower()
        if any(term in target_lower for term in ['defi', 'protocol', 'swap', 'dex']):
            return 'DEFI_PROTOCOL'
        elif any(term in target_lower for term in ['token', 'coin', 'crypto']):
            return 'CRYPTO_ASSET'
        elif any(term in target_lower for term in ['dao', 'foundation']):
            return 'CRYPTO_ORGANIZATION'
        else:
            return 'UNKNOWN'
    
    def _find_entity_aliases(self, target: str, entity_type: str) -> List[str]:
        """Find aliases and variations of the entity name"""
        # Mock implementation
        return [f"{target} Protocol", f"{target} Token", f"{target} DAO"]
    
    def _find_related_entities(self, target: str, entity_type: str) -> List[Dict[str, str]]:
        """Find related entities (founders, contributors, etc.)"""
        # Mock implementation
        return [
            {'name': f'{target} Foundation', 'relationship': 'parent_organization'},
            {'name': f'{target} Labs', 'relationship': 'development_team'}
        ]
    
    def _analyze_jurisdiction_restriction(self, target: str, jurisdiction: str, risk_level: str) -> Optional[Dict[str, Any]]:
        """Analyze jurisdiction-specific restrictions"""
        # Mock implementation
        if jurisdiction in ['US', 'CN']:
            return {
                'jurisdiction': jurisdiction,
                'risk_level': risk_level,
                'restrictions': ['KYC requirements', 'Licensing requirements'],
                'compliance_requirements': ['AML procedures', 'Regulatory reporting']
            }
        return None
    
    def _check_regulatory_requirements(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Check specific regulatory requirements"""
        # Mock implementation
        return {
            'securities_law': 'May require securities registration',
            'aml_requirements': 'AML compliance required for US operations',
            'licensing': 'Money transmitter license may be required'
        }
    
    def _generate_compliance_recommendations(self, compliance_results: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations based on results"""
        recommendations = []
        
        if compliance_results['overall_risk_level'] in ['HIGH', 'CRITICAL']:
            recommendations.append("Immediate legal review required")
            recommendations.append("Consider enhanced due diligence procedures")
        
        if compliance_results['sanctions_screening'].get('matches'):
            recommendations.append("Review sanctions matches with compliance officer")
            recommendations.append("Implement sanctions screening procedures")
        
        if compliance_results['enforcement_actions'].get('actions'):
            recommendations.append("Monitor ongoing enforcement developments")
            recommendations.append("Consider regulatory engagement strategy")
        
        recommendations.append("Implement continuous monitoring system")
        recommendations.append("Document compliance procedures and decisions")
        
        return recommendations
    
    # Additional helper methods would be implemented here for:
    # - Jurisdiction analysis
    # - Risk scoring
    # - Monitoring setup
    # - Report generation
    # - Data source integration