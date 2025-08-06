#!/usr/bin/env python3
"""
OFAC Integration Test Script

This script tests the Compliance Checker Agent with real OFAC sanctions data.
It downloads the actual OFAC SDN list and crypto addresses list to perform
real-world sanctions screening tests.
"""

import sys
import os
import asyncio
import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.compliance_checker_agent import ComplianceCheckerAgent
from tools.sanctions_data_manager import SanctionsDataManager, create_sanctions_manager

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"🔍 {title}")
    print("="*70)

def print_section(title: str):
    """Print a section header"""
    print(f"\n📋 {title}")
    print("-" * 50)

async def test_ofac_data_download():
    """Test downloading real OFAC data"""
    print_header("OFAC DATA DOWNLOAD TEST")
    
    # OFAC data sources
    ofac_sources = {
        'SDN_LIST': 'https://www.treasury.gov/ofac/downloads/sdn.xml',
        'CRYPTO_ADDRESSES': 'https://home.treasury.gov/system/files/126/digital_currency_addresses.json'
    }
    
    results = {}
    
    for source_name, url in ofac_sources.items():
        print_section(f"Testing {source_name}")
        
        try:
            print(f"🌐 Downloading from: {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                content_size = len(response.content)
                print(f"✅ Successfully downloaded {source_name}")
                print(f"📊 Data size: {content_size:,} bytes")
                
                # Basic content validation
                if source_name == 'SDN_LIST':
                    # Validate XML structure
                    try:
                        root = ET.fromstring(response.content)
                        sdn_entries = root.findall('.//sdnEntry')
                        print(f"📋 Found {len(sdn_entries)} SDN entries")
                        
                        # Show sample entry
                        if sdn_entries:
                            sample_entry = sdn_entries[0]
                            first_name = sample_entry.findtext('firstName', '')
                            last_name = sample_entry.findtext('lastName', '')
                            name = f"{first_name} {last_name}".strip()
                            if not name:
                                name = sample_entry.findtext('title', 'Unknown')
                            print(f"📝 Sample entry: {name}")
                        
                        results[source_name] = {
                            'success': True,
                            'entries': len(sdn_entries),
                            'size_bytes': content_size
                        }
                        
                    except ET.ParseError as e:
                        print(f"❌ XML parsing error: {e}")
                        results[source_name] = {'success': False, 'error': 'XML parsing failed'}
                
                elif source_name == 'CRYPTO_ADDRESSES':
                    # Validate JSON structure
                    try:
                        data = response.json()
                        entries = data.get('entries', [])
                        print(f"📋 Found {len(entries)} crypto entries")
                        
                        # Count total addresses
                        total_addresses = 0
                        for entry in entries:
                            addresses = entry.get('addresses', [])
                            total_addresses += len(addresses)
                        
                        print(f"🔗 Total crypto addresses: {total_addresses}")
                        
                        # Show sample entry
                        if entries:
                            sample_entry = entries[0]
                            print(f"📝 Sample entry: {sample_entry.get('name', 'Unknown')}")
                        
                        results[source_name] = {
                            'success': True,
                            'entries': len(entries),
                            'addresses': total_addresses,
                            'size_bytes': content_size
                        }
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parsing error: {e}")
                        results[source_name] = {'success': False, 'error': 'JSON parsing failed'}
            
            else:
                print(f"❌ HTTP Error {response.status_code}")
                results[source_name] = {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            results[source_name] = {'success': False, 'error': str(e)}
    
    return results

async def test_sanctions_data_manager():
    """Test the sanctions data manager with real OFAC data"""
    print_header("SANCTIONS DATA MANAGER TEST")
    
    # Create sanctions data manager
    print("🔧 Creating sanctions data manager...")
    sanctions_manager = create_sanctions_manager()
    
    # Get initial statistics
    initial_stats = sanctions_manager.get_statistics()
    print(f"📊 Initial database state:")
    print(f"   Total entities: {initial_stats['total_entities']}")
    print(f"   Database size: {initial_stats['database_size']} bytes")
    
    # Update data from real sources
    print("\n🔄 Updating sanctions data from real OFAC sources...")
    try:
        update_results = await sanctions_manager.update_all_sources(force_update=True)
        
        print("📈 Update results:")
        for source, result in update_results.items():
            if result.get('success'):
                print(f"   ✅ {source}: {result.get('entities_count', 0)} entities")
            else:
                print(f"   ❌ {source}: {result.get('error', 'Unknown error')}")
        
        # Get updated statistics
        updated_stats = sanctions_manager.get_statistics()
        print(f"\n📊 Updated database state:")
        print(f"   Total entities: {updated_stats['total_entities']}")
        print(f"   Database size: {updated_stats['database_size']} bytes")
        
        if updated_stats['entities_by_source']:
            print(f"   Entities by source:")
            for source, count in updated_stats['entities_by_source'].items():
                print(f"     {source}: {count}")
        
        return updated_stats['total_entities'] > 0
        
    except Exception as e:
        print(f"❌ Error updating sanctions data: {e}")
        return False

def test_known_sanctioned_entities():
    """Test with known sanctioned entities"""
    print_header("KNOWN SANCTIONED ENTITIES TEST")
    
    # Known sanctioned entities (these are publicly known)
    test_entities = [
        {
            'name': 'Tornado Cash',
            'type': 'Crypto Mixer',
            'expected_risk': 'HIGH',
            'reason': 'OFAC sanctioned crypto mixer'
        },
        {
            'name': 'Blender.io',
            'type': 'Crypto Mixer', 
            'expected_risk': 'HIGH',
            'reason': 'OFAC sanctioned crypto mixer'
        },
        {
            'name': 'Lazarus Group',
            'type': 'Criminal Organization',
            'expected_risk': 'HIGH',
            'reason': 'North Korean hacking group'
        },
        {
            'name': 'Garantex',
            'type': 'Crypto Exchange',
            'expected_risk': 'HIGH',
            'reason': 'OFAC sanctioned exchange'
        },
        {
            'name': 'Uniswap',  # Should be clean
            'type': 'DeFi Protocol',
            'expected_risk': 'LOW',
            'reason': 'Legitimate DeFi protocol'
        }
    ]
    
    compliance_agent = ComplianceCheckerAgent()
    test_results = []
    
    for entity in test_entities:
        print_section(f"Testing: {entity['name']}")
        
        try:
            # Test sanctions screening
            response = compliance_agent.process_request({
                'action': 'sanctions_screening',
                'target': entity['name'],
                'parameters': {
                    'check_crypto_addresses': True,
                    'check_aliases': True
                }
            })
            
            risk_level = response.metadata.get('risk_level', 'UNKNOWN')
            matches_found = response.metadata.get('matches_found', 0)
            
            print(f"📊 Results for {entity['name']}:")
            print(f"   Risk Level: {risk_level}")
            print(f"   Matches Found: {matches_found}")
            print(f"   Expected: {entity['expected_risk']}")
            print(f"   Success: {response.success}")
            
            # Check if result matches expectation
            result_correct = (
                (entity['expected_risk'] == 'HIGH' and risk_level in ['HIGH', 'CRITICAL']) or
                (entity['expected_risk'] == 'LOW' and risk_level == 'LOW')
            )
            
            status = "✅ PASS" if result_correct else "❌ FAIL"
            print(f"   Test Status: {status}")
            
            if matches_found > 0:
                print(f"   📝 Analysis preview:")
                preview = response.content[:300] + "..." if len(response.content) > 300 else response.content
                print(f"   {preview}")
            
            test_results.append({
                'entity': entity['name'],
                'expected': entity['expected_risk'],
                'actual': risk_level,
                'matches': matches_found,
                'correct': result_correct,
                'success': response.success
            })
            
        except Exception as e:
            print(f"❌ Error testing {entity['name']}: {e}")
            test_results.append({
                'entity': entity['name'],
                'expected': entity['expected_risk'],
                'actual': 'ERROR',
                'matches': 0,
                'correct': False,
                'success': False,
                'error': str(e)
            })
    
    return test_results

def test_crypto_address_screening():
    """Test crypto address screening"""
    print_header("CRYPTO ADDRESS SCREENING TEST")
    
    # Known sanctioned crypto addresses (these are public)
    sanctioned_addresses = [
        # Tornado Cash addresses (publicly sanctioned)
        "0x8589427373D6D84E98730D7795D8f6f8731FDA16",
        "0x722122dF12D4e14e13Ac3b6895a86e84145b6967",
        "0xDD4c48C0B24039969fC16D1cdF626eaB821d3384",
        # Blender.io addresses  
        "1ES14c7qLb5CYhLMUekctxLgc1FV2Ti9DA",
        # Test with clean address (should not match)
        "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's address (clean)
    ]
    
    compliance_agent = ComplianceCheckerAgent()
    
    for address in sanctioned_addresses:
        print_section(f"Testing Address: {address[:20]}...")
        
        try:
            response = compliance_agent.process_request({
                'action': 'sanctions_screening',
                'target': address,
                'parameters': {
                    'check_crypto_addresses': True
                }
            })
            
            risk_level = response.metadata.get('risk_level', 'UNKNOWN')
            matches_found = response.metadata.get('matches_found', 0)
            
            print(f"📊 Address screening results:")
            print(f"   Risk Level: {risk_level}")
            print(f"   Matches Found: {matches_found}")
            print(f"   Success: {response.success}")
            
            if matches_found > 0:
                print(f"   🚨 SANCTIONED ADDRESS DETECTED!")
                print(f"   📝 Details: {response.content[:200]}...")
            else:
                print(f"   ✅ No sanctions matches found")
            
        except Exception as e:
            print(f"❌ Error screening address: {e}")

async def test_real_time_compliance_workflow():
    """Test a realistic compliance workflow"""
    print_header("REAL-TIME COMPLIANCE WORKFLOW TEST")
    
    # Simulate a real compliance scenario
    defi_protocol = {
        'name': 'TestDeFi Protocol',
        'founders': ['Alice Johnson', 'Bob Smith'],
        'contributors': ['Charlie Brown', 'Diana Prince'],
        'website': 'testdefi.com',
        'description': 'Decentralized lending protocol'
    }
    
    compliance_agent = ComplianceCheckerAgent()
    
    print(f"🔍 Screening DeFi Protocol: {defi_protocol['name']}")
    print(f"👥 Team members: {len(defi_protocol['founders'] + defi_protocol['contributors'])}")
    
    try:
        # Full compliance check
        response = compliance_agent.process_request({
            'action': 'full_compliance_check',
            'target': defi_protocol['name'],
            'parameters': {
                'affiliated_entities': defi_protocol['founders'] + defi_protocol['contributors'],
                'check_enforcement_actions': True,
                'check_jurisdiction_restrictions': True,
                'include_risk_assessment': True
            }
        })
        
        print(f"\n📊 Compliance Check Results:")
        print(f"   Success: {response.success}")
        print(f"   Overall Risk: {response.metadata.get('overall_risk_level', 'UNKNOWN')}")
        print(f"   Processing Time: {response.processing_time:.2f}s")
        print(f"   Confidence Score: {response.confidence_score}")
        
        metadata = response.metadata
        print(f"\n📈 Detailed Results:")
        print(f"   Sanctions Matches: {metadata.get('sanctions_matches', 0)}")
        print(f"   Enforcement Actions: {metadata.get('enforcement_actions', 0)}")
        print(f"   Affiliated Entities Checked: {metadata.get('affiliated_entities_checked', 0)}")
        
        # Generate compliance decision
        risk_level = metadata.get('overall_risk_level', 'UNKNOWN')
        
        if risk_level in ['CRITICAL', 'HIGH']:
            decision = "🚨 REJECT - High compliance risk detected"
            action = "Escalate to compliance officer for review"
        elif risk_level == 'MEDIUM':
            decision = "⚠️ CONDITIONAL APPROVAL - Enhanced monitoring required"
            action = "Implement additional due diligence measures"
        else:
            decision = "✅ APPROVE - Low compliance risk"
            action = "Proceed with standard monitoring"
        
        print(f"\n🎯 Compliance Decision: {decision}")
        print(f"📋 Recommended Action: {action}")
        
        # Show detailed report
        print(f"\n📝 Detailed Compliance Report:")
        print(response.content)
        
        return {
            'protocol': defi_protocol['name'],
            'risk_level': risk_level,
            'decision': decision,
            'success': response.success
        }
        
    except Exception as e:
        print(f"❌ Error in compliance workflow: {e}")
        return None

def generate_test_report(download_results, sanctions_update_success, entity_test_results, workflow_result):
    """Generate a comprehensive test report"""
    print_header("COMPREHENSIVE TEST REPORT")
    
    # Summary statistics
    total_tests = len(entity_test_results)
    passed_tests = sum(1 for result in entity_test_results if result['correct'])
    failed_tests = total_tests - passed_tests
    
    print("📊 Test Summary:")
    print(f"   OFAC Data Download: {'✅ SUCCESS' if all(r.get('success') for r in download_results.values()) else '❌ FAILED'}")
    print(f"   Sanctions Data Update: {'✅ SUCCESS' if sanctions_update_success else '❌ FAILED'}")
    print(f"   Entity Screening Tests: {passed_tests}/{total_tests} passed")
    print(f"   Workflow Test: {'✅ SUCCESS' if workflow_result and workflow_result['success'] else '❌ FAILED'}")
    
    # Detailed results
    print(f"\n📋 Detailed Test Results:")
    
    print(f"\n🌐 OFAC Data Download Results:")
    for source, result in download_results.items():
        status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
        print(f"   {source}: {status}")
        if result.get('success'):
            if 'entries' in result:
                print(f"     Entries: {result['entries']}")
            if 'addresses' in result:
                print(f"     Addresses: {result['addresses']}")
            print(f"     Size: {result['size_bytes']:,} bytes")
        else:
            print(f"     Error: {result.get('error', 'Unknown')}")
    
    print(f"\n🎯 Entity Screening Test Results:")
    for result in entity_test_results:
        status = "✅ PASS" if result['correct'] else "❌ FAIL"
        print(f"   {result['entity']}: {status}")
        print(f"     Expected: {result['expected']}, Actual: {result['actual']}")
        print(f"     Matches: {result['matches']}")
        if 'error' in result:
            print(f"     Error: {result['error']}")
    
    if workflow_result:
        print(f"\n🔄 Workflow Test Result:")
        print(f"   Protocol: {workflow_result['protocol']}")
        print(f"   Risk Level: {workflow_result['risk_level']}")
        print(f"   Decision: {workflow_result['decision']}")
    
    # Recommendations
    print(f"\n🚀 Recommendations:")
    
    if not all(r.get('success') for r in download_results.values()):
        print("   ⚠️ Some OFAC data sources failed - check network connectivity")
    
    if not sanctions_update_success:
        print("   ⚠️ Sanctions data update failed - verify data sources and parsing")
    
    if failed_tests > 0:
        print(f"   ⚠️ {failed_tests} entity tests failed - review matching algorithms")
    
    if passed_tests == total_tests and sanctions_update_success:
        print("   🎉 All tests passed! The Compliance Checker Agent is working correctly with real OFAC data.")
    
    print(f"\n📈 Overall Assessment:")
    if passed_tests >= total_tests * 0.8 and sanctions_update_success:
        print("   🟢 EXCELLENT - System is working well with real OFAC data")
    elif passed_tests >= total_tests * 0.6:
        print("   🟡 GOOD - System is functional but may need fine-tuning")
    else:
        print("   🔴 NEEDS WORK - System requires debugging and improvements")

async def main():
    """Main test function"""
    print_header("OFAC INTEGRATION TEST SUITE")
    
    print("🏛️ Testing Compliance Checker Agent with Real OFAC Data")
    print("This test suite validates the agent using publicly accessible OFAC sanctions lists.")
    
    try:
        # Test 1: Download OFAC data
        print("\n🔄 Step 1: Testing OFAC data download...")
        download_results = await test_ofac_data_download()
        
        # Test 2: Update sanctions database
        print("\n🔄 Step 2: Testing sanctions data manager...")
        sanctions_update_success = await test_sanctions_data_manager()
        
        # Test 3: Test known sanctioned entities
        print("\n🔄 Step 3: Testing known sanctioned entities...")
        entity_test_results = test_known_sanctioned_entities()
        
        # Test 4: Test crypto address screening
        print("\n🔄 Step 4: Testing crypto address screening...")
        test_crypto_address_screening()
        
        # Test 5: Test real-world workflow
        print("\n🔄 Step 5: Testing real-time compliance workflow...")
        workflow_result = await test_real_time_compliance_workflow()
        
        # Generate comprehensive report
        generate_test_report(download_results, sanctions_update_success, entity_test_results, workflow_result)
        
    except Exception as e:
        print(f"❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 OFAC Integration Test Suite Complete!")
    print(f"📝 Review the results above to verify the Compliance Checker Agent is working correctly.")
    print(f"🔧 If tests failed, check network connectivity, API keys, and data source availability.")

if __name__ == "__main__":
    asyncio.run(main())