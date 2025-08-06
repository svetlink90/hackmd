#!/usr/bin/env python3
"""
Compliance Checker Agent Demo

Comprehensive demonstration of the ComplianceCheckerAgent for DeFi protocol
and crypto asset sanctions screening and compliance checking.
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.compliance_checker_agent import ComplianceCheckerAgent
from tools.sanctions_data_manager import SanctionsDataManager, create_sanctions_manager
from config.settings import settings

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"🔍 {title}")
    print("="*70)

def print_section(title: str):
    """Print a section header"""
    print(f"\n📋 {title}")
    print("-" * 50)

async def demo_sanctions_data_setup():
    """Demo setting up and updating sanctions data"""
    print_header("SANCTIONS DATA SETUP")
    
    # Create sanctions data manager
    print("🔧 Creating sanctions data manager...")
    sanctions_manager = create_sanctions_manager()
    
    # Get current statistics
    stats = sanctions_manager.get_statistics()
    print(f"📊 Current database statistics:")
    print(f"   Total entities: {stats['total_entities']}")
    print(f"   Database size: {stats['database_size']} bytes")
    
    if stats['entities_by_source']:
        print(f"   Entities by source:")
        for source, count in stats['entities_by_source'].items():
            print(f"     {source}: {count}")
    
    # In a real implementation, you would update from actual sources
    print("\n⚠️  Note: In production, this would update from real sanctions sources:")
    print("   - OFAC SDN List")
    print("   - OFAC Crypto Addresses")
    print("   - UN Security Council Sanctions")
    print("   - EU Sanctions List")
    print("   - UK HMT Sanctions")
    
    return sanctions_manager

def demo_basic_compliance_check():
    """Demo basic compliance checking functionality"""
    print_header("BASIC COMPLIANCE SCREENING")
    
    # Initialize the compliance agent
    print("🤖 Initializing Compliance Checker Agent...")
    compliance_agent = ComplianceCheckerAgent()
    
    # Test cases for DeFi protocols and crypto projects
    test_cases = [
        {
            'name': 'Uniswap Protocol',
            'type': 'DeFi Protocol',
            'description': 'Decentralized exchange protocol'
        },
        {
            'name': 'Tornado Cash',
            'type': 'Privacy Protocol',
            'description': 'Privacy-focused mixing protocol (known sanctioned)'
        },
        {
            'name': 'Compound Finance',
            'type': 'DeFi Lending',
            'description': 'Decentralized lending protocol'
        },
        {
            'name': 'Ethereum Foundation',
            'type': 'Crypto Organization',
            'description': 'Ethereum blockchain foundation'
        }
    ]
    
    print(f"🎯 Testing {len(test_cases)} entities for compliance...")
    
    for i, test_case in enumerate(test_cases, 1):
        print_section(f"Test Case {i}: {test_case['name']}")
        
        try:
            # Perform sanctions screening
            screening_request = {
                'action': 'sanctions_screening',
                'target': test_case['name'],
                'parameters': {
                    'entity_type': test_case['type'],
                    'check_aliases': True,
                    'check_crypto_addresses': True
                }
            }
            
            response = compliance_agent.process_request(screening_request)
            
            print(f"✅ Screening completed for {test_case['name']}")
            print(f"📊 Success: {response.success}")
            print(f"⏱️  Processing time: {response.processing_time:.2f}s")
            print(f"🎯 Confidence score: {response.confidence_score}")
            
            if response.metadata:
                print(f"📈 Matches found: {response.metadata.get('matches_found', 0)}")
                print(f"🚨 Risk level: {response.metadata.get('risk_level', 'UNKNOWN')}")
                print(f"📋 Lists checked: {response.metadata.get('lists_checked', 0)}")
            
            # Show first part of analysis
            content_preview = response.content[:300] + "..." if len(response.content) > 300 else response.content
            print(f"📝 Analysis preview:\n{content_preview}")
            
        except Exception as e:
            print(f"❌ Error screening {test_case['name']}: {e}")

def demo_full_compliance_check():
    """Demo comprehensive compliance checking"""
    print_header("COMPREHENSIVE COMPLIANCE CHECK")
    
    compliance_agent = ComplianceCheckerAgent()
    
    # Test a DeFi protocol with affiliated entities
    protocol_name = "SampleDeFi Protocol"
    affiliated_entities = [
        "SampleDeFi Foundation",
        "SampleDeFi Labs",
        "John Smith",  # Fictional founder
        "Jane Doe"     # Fictional contributor
    ]
    
    print(f"🔍 Performing full compliance check for: {protocol_name}")
    print(f"👥 Including {len(affiliated_entities)} affiliated entities")
    
    try:
        full_check_request = {
            'action': 'full_compliance_check',
            'target': protocol_name,
            'parameters': {
                'affiliated_entities': affiliated_entities,
                'check_enforcement_actions': True,
                'check_jurisdiction_restrictions': True,
                'include_risk_assessment': True
            }
        }
        
        response = compliance_agent.process_request(full_check_request)
        
        print(f"\n✅ Full compliance check completed")
        print(f"📊 Success: {response.success}")
        print(f"⏱️  Processing time: {response.processing_time:.2f}s")
        print(f"🎯 Confidence score: {response.confidence_score}")
        
        if response.metadata:
            print(f"\n📈 Results Summary:")
            print(f"   Overall risk level: {response.metadata.get('overall_risk_level', 'UNKNOWN')}")
            print(f"   Sanctions matches: {response.metadata.get('sanctions_matches', 0)}")
            print(f"   Enforcement actions: {response.metadata.get('enforcement_actions', 0)}")
            print(f"   Affiliated entities checked: {response.metadata.get('affiliated_entities_checked', 0)}")
        
        print(f"\n📝 Full Analysis Report:")
        print(response.content)
        
    except Exception as e:
        print(f"❌ Error in full compliance check: {e}")

def demo_enforcement_tracking():
    """Demo enforcement action tracking"""
    print_header("ENFORCEMENT ACTION TRACKING")
    
    compliance_agent = ComplianceCheckerAgent()
    
    # Test cases for enforcement tracking
    enforcement_test_cases = [
        "Binance",
        "Coinbase",
        "DeFi Protocol XYZ",
        "Crypto Exchange ABC"
    ]
    
    print("🔍 Checking enforcement actions for crypto entities...")
    
    for entity in enforcement_test_cases:
        print_section(f"Enforcement Check: {entity}")
        
        try:
            enforcement_request = {
                'action': 'enforcement_check',
                'target': entity,
                'parameters': {
                    'agencies': ['SEC', 'CFTC', 'DOJ', 'FINRA', 'FINCEN'],
                    'include_court_records': True,
                    'date_range': '2020-2024'
                }
            }
            
            response = compliance_agent.process_request(enforcement_request)
            
            print(f"✅ Enforcement check completed for {entity}")
            print(f"📊 Actions found: {response.metadata.get('actions_found', 0)}")
            print(f"🚨 Risk level: {response.metadata.get('risk_level', 'UNKNOWN')}")
            print(f"🏛️  Agencies checked: {response.metadata.get('agencies_checked', 0)}")
            
            # Show preview of results
            if response.content:
                preview = response.content[:400] + "..." if len(response.content) > 400 else response.content
                print(f"📝 Results preview:\n{preview}")
            
        except Exception as e:
            print(f"❌ Error checking enforcement for {entity}: {e}")

def demo_jurisdiction_analysis():
    """Demo jurisdiction restriction analysis"""
    print_header("JURISDICTION ANALYSIS")
    
    compliance_agent = ComplianceCheckerAgent()
    
    # Test different types of crypto projects
    jurisdiction_test_cases = [
        {
            'name': 'Global DeFi Protocol',
            'type': 'DeFi Protocol',
            'target_jurisdictions': ['US', 'EU', 'UK', 'JP']
        },
        {
            'name': 'Privacy Coin Project',
            'type': 'Crypto Asset',
            'target_jurisdictions': ['US', 'KR', 'JP', 'AU']
        },
        {
            'name': 'Centralized Exchange',
            'type': 'Crypto Exchange',
            'target_jurisdictions': ['US', 'EU', 'SG', 'HK']
        }
    ]
    
    print("🌍 Analyzing jurisdiction restrictions...")
    
    for test_case in jurisdiction_test_cases:
        print_section(f"Jurisdiction Analysis: {test_case['name']}")
        
        try:
            jurisdiction_request = {
                'action': 'jurisdiction_analysis',
                'target': test_case['name'],
                'parameters': {
                    'entity_type': test_case['type'],
                    'target_jurisdictions': test_case['target_jurisdictions'],
                    'include_regulatory_requirements': True
                }
            }
            
            response = compliance_agent.process_request(jurisdiction_request)
            
            print(f"✅ Jurisdiction analysis completed")
            print(f"🚨 Risk level: {response.metadata.get('risk_level', 'UNKNOWN')}")
            print(f"🌍 Restricted jurisdictions: {response.metadata.get('restricted_jurisdictions', 0)}")
            print(f"📋 Recommendations: {response.metadata.get('recommendations', 0)}")
            
            # Show analysis preview
            if response.content:
                preview = response.content[:500] + "..." if len(response.content) > 500 else response.content
                print(f"📝 Analysis preview:\n{preview}")
            
        except Exception as e:
            print(f"❌ Error in jurisdiction analysis: {e}")

def demo_risk_assessment():
    """Demo comprehensive risk assessment"""
    print_header("COMPREHENSIVE RISK ASSESSMENT")
    
    compliance_agent = ComplianceCheckerAgent()
    
    # High-risk scenario
    high_risk_case = {
        'name': 'HighRisk DeFi Protocol',
        'affiliated_entities': [
            'HighRisk Foundation',
            'Sanctioned Individual',  # This would trigger sanctions
            'HighRisk Labs'
        ],
        'description': 'A DeFi protocol with potential compliance issues'
    }
    
    print(f"⚠️  Assessing high-risk scenario: {high_risk_case['name']}")
    
    try:
        risk_request = {
            'action': 'risk_assessment',
            'target': high_risk_case['name'],
            'parameters': {
                'affiliated_entities': high_risk_case['affiliated_entities'],
                'assessment_depth': 'comprehensive',
                'include_mitigation_strategies': True,
                'generate_monitoring_plan': True
            }
        }
        
        response = compliance_agent.process_request(risk_request)
        
        print(f"✅ Risk assessment completed")
        print(f"🚨 Overall risk score: {response.metadata.get('overall_risk_score', 'N/A')}")
        print(f"🔴 Overall risk level: {response.metadata.get('overall_risk_level', 'UNKNOWN')}")
        print(f"⚠️  High risk factors: {response.metadata.get('high_risk_factors', 0)}")
        
        print(f"\n📊 Detailed Risk Assessment:")
        print(response.content)
        
    except Exception as e:
        print(f"❌ Error in risk assessment: {e}")

def demo_entity_resolution():
    """Demo entity resolution and alias detection"""
    print_header("ENTITY RESOLUTION & ALIAS DETECTION")
    
    compliance_agent = ComplianceCheckerAgent()
    
    # Test entity resolution
    entity_test_cases = [
        "Uniswap",
        "Compound",
        "Ethereum",
        "Binance Smart Chain"
    ]
    
    print("🔍 Performing entity resolution and alias detection...")
    
    for entity in entity_test_cases:
        print_section(f"Entity Resolution: {entity}")
        
        try:
            resolution_request = {
                'action': 'entity_resolution',
                'target': entity,
                'parameters': {
                    'find_aliases': True,
                    'find_related_entities': True,
                    'include_crypto_addresses': True
                }
            }
            
            response = compliance_agent.process_request(resolution_request)
            
            print(f"✅ Entity resolution completed")
            print(f"🏷️  Entity type: {response.metadata.get('entity_type', 'UNKNOWN')}")
            print(f"📝 Aliases found: {response.metadata.get('aliases_found', 0)}")
            print(f"🔗 Related entities: {response.metadata.get('related_entities', 0)}")
            print(f"🎯 Confidence score: {response.metadata.get('confidence_score', 0.0):.2f}")
            
            # Show resolution results
            if response.content:
                preview = response.content[:400] + "..." if len(response.content) > 400 else response.content
                print(f"📝 Resolution results:\n{preview}")
            
        except Exception as e:
            print(f"❌ Error in entity resolution: {e}")

def demo_agent_capabilities():
    """Demo agent capabilities and health check"""
    print_header("AGENT CAPABILITIES & HEALTH CHECK")
    
    compliance_agent = ComplianceCheckerAgent()
    
    # Show agent capabilities
    print("🔧 Compliance Checker Agent Capabilities:")
    capabilities = compliance_agent.get_capabilities()
    
    for key, value in capabilities.items():
        if isinstance(value, list):
            print(f"   {key}: {', '.join(value)}")
        else:
            print(f"   {key}: {value}")
    
    # Health check
    print("\n🏥 Agent Health Check:")
    health = compliance_agent.health_check()
    
    for key, value in health.items():
        print(f"   {key}: {value}")
    
    # Show data sources
    print("\n📊 Available Data Sources:")
    data_sources = compliance_agent._get_data_sources()
    for i, source in enumerate(data_sources, 1):
        print(f"   {i}. {source}")

def demo_real_world_scenarios():
    """Demo real-world compliance scenarios"""
    print_header("REAL-WORLD COMPLIANCE SCENARIOS")
    
    scenarios = [
        {
            'name': 'New DeFi Protocol Launch',
            'description': 'Pre-launch compliance screening for a new DeFi protocol',
            'steps': [
                '1. Screen protocol name and team members',
                '2. Check for sanctions matches',
                '3. Analyze jurisdiction restrictions',
                '4. Review enforcement history',
                '5. Generate compliance report'
            ]
        },
        {
            'name': 'Exchange Listing Due Diligence',
            'description': 'Compliance check before listing a new crypto asset',
            'steps': [
                '1. Screen asset and issuer',
                '2. Check affiliated entities',
                '3. Review regulatory status',
                '4. Assess enforcement risks',
                '5. Document compliance decision'
            ]
        },
        {
            'name': 'Ongoing Monitoring',
            'description': 'Continuous compliance monitoring for existing relationships',
            'steps': [
                '1. Daily sanctions list updates',
                '2. Monitor enforcement actions',
                '3. Track regulatory changes',
                '4. Alert on risk changes',
                '5. Update risk assessments'
            ]
        },
        {
            'name': 'Investigation Response',
            'description': 'Compliance review triggered by regulatory inquiry',
            'steps': [
                '1. Comprehensive entity screening',
                '2. Historical transaction analysis',
                '3. Document compliance procedures',
                '4. Prepare regulatory response',
                '5. Implement enhanced monitoring'
            ]
        }
    ]
    
    print("🌍 Real-world compliance scenarios:")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        print("🔄 Process steps:")
        for step in scenario['steps']:
            print(f"   {step}")

async def main():
    """Main demo function"""
    print_header("COMPLIANCE CHECKER AGENT - COMPREHENSIVE DEMO")
    
    print("🏛️  Welcome to the Compliance Checker Agent Demo!")
    print("This demo showcases comprehensive sanctions screening and compliance")
    print("checking capabilities for DeFi protocols and crypto assets.")
    
    # Run all demo sections
    try:
        # Setup sanctions data
        await demo_sanctions_data_setup()
        
        # Basic compliance screening
        demo_basic_compliance_check()
        
        # Comprehensive compliance check
        demo_full_compliance_check()
        
        # Enforcement tracking
        demo_enforcement_tracking()
        
        # Jurisdiction analysis
        demo_jurisdiction_analysis()
        
        # Risk assessment
        demo_risk_assessment()
        
        # Entity resolution
        demo_entity_resolution()
        
        # Agent capabilities
        demo_agent_capabilities()
        
        # Real-world scenarios
        demo_real_world_scenarios()
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    # Summary and next steps
    print_header("DEMO SUMMARY & NEXT STEPS")
    
    print("🎉 Compliance Checker Agent Demo completed successfully!")
    
    print("\n📚 What you learned:")
    print("   ✅ Sanctions screening for DeFi protocols")
    print("   ✅ Enforcement action tracking")
    print("   ✅ Jurisdiction restriction analysis")
    print("   ✅ Comprehensive risk assessment")
    print("   ✅ Entity resolution and alias detection")
    print("   ✅ Real-world compliance scenarios")
    
    print("\n🚀 Next steps:")
    print("   1. Configure real sanctions data sources")
    print("   2. Set up automated monitoring")
    print("   3. Integrate with your compliance workflow")
    print("   4. Customize risk scoring parameters")
    print("   5. Implement continuous monitoring")
    
    print("\n📖 Additional resources:")
    print("   - Review the ComplianceCheckerAgent source code")
    print("   - Check the SanctionsDataManager for data integration")
    print("   - Explore configuration options in settings.py")
    print("   - Run tests to validate functionality")
    
    print("\n⚠️  Important notes:")
    print("   - This demo uses mock data for demonstration")
    print("   - In production, integrate with real sanctions sources")
    print("   - Always validate results with legal counsel")
    print("   - Implement proper data security measures")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(main())