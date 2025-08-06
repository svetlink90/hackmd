#!/usr/bin/env python3
"""
Daily Compliance Tasks Runner

Interactive script for running daily compliance checks from Cursor.
Easy-to-use interface for common compliance screening tasks.
"""

import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.compliance_checker_agent import ComplianceCheckerAgent
from tools.sanctions_data_manager import create_sanctions_manager

class DailyComplianceRunner:
    """Interactive compliance task runner for daily operations"""
    
    def __init__(self):
        self.compliance_agent = ComplianceCheckerAgent()
        self.sanctions_manager = create_sanctions_manager()
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"🔍 {title}")
        print("="*60)
    
    def print_menu(self):
        """Print main menu options"""
        self.print_header("DAILY COMPLIANCE TASKS")
        print("Choose a compliance task:")
        print("1. 🎯 Screen Single Entity")
        print("2. 📋 Batch Screen Multiple Entities")
        print("3. 🔄 Update Sanctions Database")
        print("4. 📊 Quick Entity Risk Assessment")
        print("5. 🌐 Full Protocol Due Diligence")
        print("6. 🔗 Screen Crypto Addresses")
        print("7. 📈 Database Statistics")
        print("8. 🧪 Test Known Sanctioned Entities")
        print("9. 📝 Generate Compliance Report")
        print("0. ❌ Exit")
    
    async def screen_single_entity(self):
        """Screen a single entity interactively"""
        self.print_header("SINGLE ENTITY SCREENING")
        
        entity_name = input("🎯 Enter entity name to screen: ").strip()
        if not entity_name:
            print("❌ No entity name provided")
            return
        
        print(f"🔍 Screening: {entity_name}")
        
        try:
            response = self.compliance_agent.process_request({
                'action': 'sanctions_screening',
                'target': entity_name,
                'parameters': {
                    'check_crypto_addresses': True,
                    'check_aliases': True
                }
            })
            
            print(f"\n📊 Results for {entity_name}:")
            print(f"   ✅ Success: {response.success}")
            print(f"   🚨 Risk Level: {response.metadata.get('risk_level', 'UNKNOWN')}")
            print(f"   📈 Matches Found: {response.metadata.get('matches_found', 0)}")
            print(f"   ⏱️  Processing Time: {response.processing_time:.2f}s")
            print(f"   🎯 Confidence: {response.confidence_score}")
            
            if response.metadata.get('matches_found', 0) > 0:
                print(f"\n🚨 SANCTIONS MATCHES DETECTED!")
                print(f"📝 Analysis:")
                print(response.content)
            else:
                print(f"\n✅ No sanctions matches found - Entity appears clean")
            
        except Exception as e:
            print(f"❌ Error screening entity: {e}")
    
    async def batch_screen_entities(self):
        """Screen multiple entities from user input"""
        self.print_header("BATCH ENTITY SCREENING")
        
        print("📋 Enter entities to screen (one per line, empty line to finish):")
        entities = []
        while True:
            entity = input("Entity name: ").strip()
            if not entity:
                break
            entities.append(entity)
        
        if not entities:
            print("❌ No entities provided")
            return
        
        print(f"\n🔍 Screening {len(entities)} entities...")
        results = []
        
        for i, entity in enumerate(entities, 1):
            print(f"\n📋 [{i}/{len(entities)}] Screening: {entity}")
            
            try:
                response = self.compliance_agent.process_request({
                    'action': 'sanctions_screening',
                    'target': entity,
                    'parameters': {}
                })
                
                risk_level = response.metadata.get('risk_level', 'UNKNOWN')
                matches = response.metadata.get('matches_found', 0)
                
                result = {
                    'entity': entity,
                    'risk_level': risk_level,
                    'matches': matches,
                    'success': response.success
                }
                results.append(result)
                
                status = "🚨 HIGH RISK" if risk_level in ['HIGH', 'CRITICAL'] else "✅ CLEAN"
                print(f"   Result: {status} ({matches} matches)")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    'entity': entity,
                    'risk_level': 'ERROR',
                    'matches': 0,
                    'success': False,
                    'error': str(e)
                })
        
        # Summary report
        print(f"\n📊 BATCH SCREENING SUMMARY")
        print(f"   Total entities screened: {len(entities)}")
        
        high_risk = [r for r in results if r.get('risk_level') in ['HIGH', 'CRITICAL']]
        clean = [r for r in results if r.get('risk_level') == 'LOW']
        errors = [r for r in results if not r.get('success')]
        
        print(f"   🚨 High risk entities: {len(high_risk)}")
        print(f"   ✅ Clean entities: {len(clean)}")
        print(f"   ❌ Errors: {len(errors)}")
        
        if high_risk:
            print(f"\n🚨 HIGH RISK ENTITIES REQUIRING REVIEW:")
            for result in high_risk:
                print(f"   - {result['entity']} ({result['matches']} matches)")
    
    async def update_sanctions_database(self):
        """Update sanctions database with latest data"""
        self.print_header("SANCTIONS DATABASE UPDATE")
        
        print("🔄 Updating sanctions database with latest OFAC data...")
        
        try:
            # Get current stats
            current_stats = self.sanctions_manager.get_statistics()
            print(f"📊 Current database: {current_stats['total_entities']} entities")
            
            # Update from sources
            update_results = await self.sanctions_manager.update_all_sources(force_update=True)
            
            print(f"\n📈 Update Results:")
            for source, result in update_results.items():
                if result.get('success'):
                    print(f"   ✅ {source}: {result.get('entities_count', 0)} entities")
                else:
                    print(f"   ❌ {source}: {result.get('error', 'Unknown error')}")
            
            # Get updated stats
            updated_stats = self.sanctions_manager.get_statistics()
            print(f"\n📊 Updated database: {updated_stats['total_entities']} entities")
            print(f"📈 Change: {updated_stats['total_entities'] - current_stats['total_entities']} entities")
            
        except Exception as e:
            print(f"❌ Error updating database: {e}")
    
    async def quick_risk_assessment(self):
        """Perform quick risk assessment on an entity"""
        self.print_header("QUICK RISK ASSESSMENT")
        
        entity_name = input("🎯 Enter entity name for risk assessment: ").strip()
        if not entity_name:
            print("❌ No entity name provided")
            return
        
        # Ask for affiliated entities
        print(f"\n👥 Enter affiliated entities for {entity_name} (optional, empty line to skip):")
        affiliated = []
        while True:
            affiliate = input("Affiliated entity: ").strip()
            if not affiliate:
                break
            affiliated.append(affiliate)
        
        print(f"\n🔍 Performing risk assessment for: {entity_name}")
        if affiliated:
            print(f"👥 Including {len(affiliated)} affiliated entities")
        
        try:
            response = self.compliance_agent.process_request({
                'action': 'risk_assessment',
                'target': entity_name,
                'parameters': {
                    'affiliated_entities': affiliated,
                    'assessment_depth': 'quick'
                }
            })
            
            print(f"\n📊 Risk Assessment Results:")
            print(f"   🚨 Overall Risk Level: {response.metadata.get('overall_risk_level', 'UNKNOWN')}")
            print(f"   📈 Risk Score: {response.metadata.get('overall_risk_score', 'N/A')}")
            print(f"   ⚠️  High Risk Factors: {response.metadata.get('high_risk_factors', 0)}")
            
            print(f"\n📝 Detailed Assessment:")
            print(response.content)
            
        except Exception as e:
            print(f"❌ Error in risk assessment: {e}")
    
    async def full_protocol_due_diligence(self):
        """Comprehensive due diligence for DeFi protocols"""
        self.print_header("FULL PROTOCOL DUE DILIGENCE")
        
        protocol_name = input("🏛️ Enter DeFi protocol name: ").strip()
        if not protocol_name:
            print("❌ No protocol name provided")
            return
        
        # Collect team information
        print(f"\n👥 Enter team members for {protocol_name}:")
        print("(Include founders, core contributors, advisors)")
        team_members = []
        while True:
            member = input("Team member name (empty to finish): ").strip()
            if not member:
                break
            team_members.append(member)
        
        print(f"\n🔍 Performing comprehensive due diligence...")
        print(f"   Protocol: {protocol_name}")
        print(f"   Team members: {len(team_members)}")
        
        try:
            response = self.compliance_agent.process_request({
                'action': 'full_compliance_check',
                'target': protocol_name,
                'parameters': {
                    'affiliated_entities': team_members,
                    'check_enforcement_actions': True,
                    'check_jurisdiction_restrictions': True,
                    'include_risk_assessment': True
                }
            })
            
            print(f"\n📊 Due Diligence Results:")
            print(f"   ✅ Success: {response.success}")
            print(f"   🚨 Overall Risk: {response.metadata.get('overall_risk_level', 'UNKNOWN')}")
            print(f"   📈 Sanctions Matches: {response.metadata.get('sanctions_matches', 0)}")
            print(f"   🏛️ Enforcement Actions: {response.metadata.get('enforcement_actions', 0)}")
            print(f"   👥 Team Members Checked: {response.metadata.get('affiliated_entities_checked', 0)}")
            
            # Generate recommendation
            risk_level = response.metadata.get('overall_risk_level', 'UNKNOWN')
            if risk_level in ['CRITICAL', 'HIGH']:
                recommendation = "🚨 REJECT - High compliance risk detected"
                action = "Escalate to legal counsel for review"
            elif risk_level == 'MEDIUM':
                recommendation = "⚠️ CONDITIONAL APPROVAL - Enhanced monitoring required"
                action = "Implement additional due diligence measures"
            else:
                recommendation = "✅ APPROVE - Low compliance risk"
                action = "Proceed with standard monitoring"
            
            print(f"\n🎯 Compliance Recommendation: {recommendation}")
            print(f"📋 Suggested Action: {action}")
            
            print(f"\n📝 Full Due Diligence Report:")
            print(response.content)
            
        except Exception as e:
            print(f"❌ Error in due diligence: {e}")
    
    async def screen_crypto_addresses(self):
        """Screen cryptocurrency addresses"""
        self.print_header("CRYPTO ADDRESS SCREENING")
        
        print("🔗 Enter crypto addresses to screen (one per line, empty line to finish):")
        addresses = []
        while True:
            address = input("Crypto address: ").strip()
            if not address:
                break
            addresses.append(address)
        
        if not addresses:
            print("❌ No addresses provided")
            return
        
        print(f"\n🔍 Screening {len(addresses)} crypto addresses...")
        
        for i, address in enumerate(addresses, 1):
            print(f"\n📋 [{i}/{len(addresses)}] Screening: {address[:20]}...")
            
            try:
                response = self.compliance_agent.process_request({
                    'action': 'sanctions_screening',
                    'target': address,
                    'parameters': {
                        'check_crypto_addresses': True
                    }
                })
                
                risk_level = response.metadata.get('risk_level', 'UNKNOWN')
                matches = response.metadata.get('matches_found', 0)
                
                if matches > 0:
                    print(f"   🚨 SANCTIONED ADDRESS DETECTED!")
                    print(f"   Risk Level: {risk_level}")
                    print(f"   Matches: {matches}")
                else:
                    print(f"   ✅ Clean address - no sanctions matches")
                
            except Exception as e:
                print(f"   ❌ Error screening address: {e}")
    
    def show_database_statistics(self):
        """Show sanctions database statistics"""
        self.print_header("DATABASE STATISTICS")
        
        try:
            stats = self.sanctions_manager.get_statistics()
            
            print(f"📊 Sanctions Database Statistics:")
            print(f"   Total entities: {stats['total_entities']:,}")
            print(f"   Database size: {stats['database_size']:,} bytes")
            
            if stats['entities_by_source']:
                print(f"\n📋 Entities by Source:")
                for source, count in stats['entities_by_source'].items():
                    print(f"   {source}: {count:,}")
            
            if stats['entities_by_type']:
                print(f"\n🏷️ Entities by Type:")
                for entity_type, count in stats['entities_by_type'].items():
                    print(f"   {entity_type}: {count:,}")
            
            if stats['last_updates']:
                print(f"\n🕐 Last Updates:")
                for source, update_time in stats['last_updates'].items():
                    if update_time:
                        print(f"   {source}: {update_time}")
                    else:
                        print(f"   {source}: Never updated")
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    async def test_known_sanctioned_entities(self):
        """Test with known sanctioned entities"""
        self.print_header("TEST KNOWN SANCTIONED ENTITIES")
        
        known_entities = [
            {'name': 'Tornado Cash', 'expected': 'HIGH'},
            {'name': 'Blender.io', 'expected': 'HIGH'},
            {'name': 'Lazarus Group', 'expected': 'HIGH'},
            {'name': 'Uniswap', 'expected': 'LOW'}
        ]
        
        print(f"🧪 Testing {len(known_entities)} known entities...")
        
        for entity in known_entities:
            print(f"\n🎯 Testing: {entity['name']}")
            
            try:
                response = self.compliance_agent.process_request({
                    'action': 'sanctions_screening',
                    'target': entity['name'],
                    'parameters': {}
                })
                
                actual_risk = response.metadata.get('risk_level', 'UNKNOWN')
                matches = response.metadata.get('matches_found', 0)
                
                # Check if result matches expectation
                correct = (
                    (entity['expected'] == 'HIGH' and actual_risk in ['HIGH', 'CRITICAL']) or
                    (entity['expected'] == 'LOW' and actual_risk == 'LOW')
                )
                
                status = "✅ PASS" if correct else "❌ FAIL"
                print(f"   Expected: {entity['expected']}, Actual: {actual_risk}")
                print(f"   Matches: {matches}")
                print(f"   Status: {status}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    async def generate_compliance_report(self):
        """Generate a comprehensive compliance report"""
        self.print_header("GENERATE COMPLIANCE REPORT")
        
        entity_name = input("📝 Enter entity name for compliance report: ").strip()
        if not entity_name:
            print("❌ No entity name provided")
            return
        
        report_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_file = f"compliance_report_{entity_name.replace(' ', '_')}_{report_date}.txt"
        
        print(f"📄 Generating compliance report for: {entity_name}")
        
        try:
            response = self.compliance_agent.process_request({
                'action': 'full_compliance_check',
                'target': entity_name,
                'parameters': {
                    'check_enforcement_actions': True,
                    'check_jurisdiction_restrictions': True,
                    'include_risk_assessment': True
                }
            })
            
            # Save report to file
            with open(report_file, 'w') as f:
                f.write(f"COMPLIANCE REPORT\n")
                f.write(f"Entity: {entity_name}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"{'='*60}\n\n")
                f.write(response.content)
                f.write(f"\n\n{'='*60}\n")
                f.write(f"Metadata: {json.dumps(response.metadata, indent=2)}\n")
            
            print(f"✅ Report generated successfully!")
            print(f"📁 Saved to: {report_file}")
            print(f"🚨 Risk Level: {response.metadata.get('overall_risk_level', 'UNKNOWN')}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    async def run(self):
        """Main interactive loop"""
        print("🏛️ Welcome to Daily Compliance Tasks Runner")
        print("Interactive compliance screening for DeFi protocols and crypto assets")
        
        while True:
            try:
                self.print_menu()
                choice = input("\n🔄 Select option (0-9): ").strip()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    await self.screen_single_entity()
                elif choice == '2':
                    await self.batch_screen_entities()
                elif choice == '3':
                    await self.update_sanctions_database()
                elif choice == '4':
                    await self.quick_risk_assessment()
                elif choice == '5':
                    await self.full_protocol_due_diligence()
                elif choice == '6':
                    await self.screen_crypto_addresses()
                elif choice == '7':
                    self.show_database_statistics()
                elif choice == '8':
                    await self.test_known_sanctioned_entities()
                elif choice == '9':
                    await self.generate_compliance_report()
                else:
                    print("❌ Invalid option. Please choose 0-9.")
                
                input("\n⏸️  Press Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                input("\n⏸️  Press Enter to continue...")

async def main():
    """Main function"""
    runner = DailyComplianceRunner()
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())