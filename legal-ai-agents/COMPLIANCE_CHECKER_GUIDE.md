# Compliance Checker Agent - User Guide

## Overview

The **Compliance Checker Agent** is a specialized AI agent designed for comprehensive sanctions screening and compliance checking of DeFi protocols, crypto projects, and digital assets. It performs automated checks against multiple sanctions lists, tracks enforcement actions, and provides detailed risk assessments.

## 🎯 Key Features

### ✅ **Sanctions Screening**
- OFAC SDN List screening
- UN Security Council sanctions
- EU sanctions list checking
- UK HMT sanctions
- Crypto-specific sanctions (OFAC crypto addresses)

### ✅ **Enforcement Tracking**
- SEC enforcement actions
- CFTC regulatory actions
- DOJ criminal cases
- FINRA disciplinary actions
- Court records and lawsuits

### ✅ **Jurisdiction Analysis**
- Geographic restriction analysis
- Regulatory compliance requirements
- Cross-border compliance assessment
- Risk-based jurisdiction classification

### ✅ **Entity Resolution**
- Alias and variation detection
- Related entity identification
- Fuzzy name matching
- Crypto address linkage

### ✅ **Risk Assessment**
- Multi-factor risk scoring
- Comprehensive risk reports
- Mitigation strategy recommendations
- Continuous monitoring setup

## 🚀 Quick Start

### Basic Usage

```python
from agents.compliance_checker_agent import ComplianceCheckerAgent

# Initialize the agent
compliance_agent = ComplianceCheckerAgent()

# Basic sanctions screening
response = compliance_agent.process_request({
    'action': 'sanctions_screening',
    'target': 'DeFi Protocol Name',
    'parameters': {}
})

print(f"Risk Level: {response.metadata['risk_level']}")
print(f"Matches Found: {response.metadata['matches_found']}")
```

### Comprehensive Compliance Check

```python
# Full compliance check with affiliated entities
response = compliance_agent.process_request({
    'action': 'full_compliance_check',
    'target': 'DeFi Protocol Name',
    'parameters': {
        'affiliated_entities': [
            'Protocol Foundation',
            'Development Team',
            'Founder Name'
        ]
    }
})

print(response.content)  # Detailed compliance report
```

## 📋 Available Actions

### 1. **Full Compliance Check** (`full_compliance_check`)
Comprehensive screening including sanctions, enforcement, and jurisdiction analysis.

```python
request = {
    'action': 'full_compliance_check',
    'target': 'Protocol Name',
    'parameters': {
        'affiliated_entities': ['Entity1', 'Entity2'],
        'check_enforcement_actions': True,
        'check_jurisdiction_restrictions': True
    }
}
```

### 2. **Sanctions Screening** (`sanctions_screening`)
Screen against multiple sanctions lists.

```python
request = {
    'action': 'sanctions_screening',
    'target': 'Entity Name',
    'parameters': {
        'check_aliases': True,
        'check_crypto_addresses': True
    }
}
```

### 3. **Enforcement Check** (`enforcement_check`)
Check for regulatory enforcement actions.

```python
request = {
    'action': 'enforcement_check',
    'target': 'Entity Name',
    'parameters': {
        'agencies': ['SEC', 'CFTC', 'DOJ'],
        'include_court_records': True
    }
}
```

### 4. **Jurisdiction Analysis** (`jurisdiction_analysis`)
Analyze geographic and regulatory restrictions.

```python
request = {
    'action': 'jurisdiction_analysis',
    'target': 'Protocol Name',
    'parameters': {
        'target_jurisdictions': ['US', 'EU', 'UK'],
        'include_regulatory_requirements': True
    }
}
```

### 5. **Entity Resolution** (`entity_resolution`)
Resolve entity names and find related entities.

```python
request = {
    'action': 'entity_resolution',
    'target': 'Entity Name',
    'parameters': {
        'find_aliases': True,
        'find_related_entities': True
    }
}
```

### 6. **Risk Assessment** (`risk_assessment`)
Comprehensive risk evaluation and scoring.

```python
request = {
    'action': 'risk_assessment',
    'target': 'Protocol Name',
    'parameters': {
        'assessment_depth': 'comprehensive',
        'include_mitigation_strategies': True
    }
}
```

## 🛠️ Configuration

### Environment Variables

```bash
# AI Service Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Compliance-Specific Settings
SANCTIONS_UPDATE_FREQUENCY=24  # Hours
ENFORCEMENT_CHECK_DEPTH=comprehensive
DEFAULT_RISK_THRESHOLD=0.7
```

### Custom Configuration

```python
# In config/settings.py, you can customize:

# Restricted jurisdictions
RESTRICTED_JURISDICTIONS = {
    'HIGH_RISK': ['AF', 'BY', 'CN', 'CU', 'IR', 'KP', 'RU'],
    'MEDIUM_RISK': ['BD', 'BO', 'KH', 'EC'],
    'REGULATORY_RESTRICTED': ['US', 'CN', 'KR', 'JP']
}

# Data source URLs
SANCTIONS_SOURCES = {
    'OFAC_SDN': 'https://www.treasury.gov/ofac/downloads/sdn.xml',
    'OFAC_CRYPTO': 'https://home.treasury.gov/system/files/126/digital_currency_addresses.json'
}
```

## 📊 Understanding Results

### Response Structure

```python
response = compliance_agent.process_request(request)

# Response attributes
response.success          # True/False
response.content          # Formatted report
response.metadata         # Additional data
response.confidence_score # 0.0 to 1.0
response.processing_time  # Seconds
response.sources          # Data sources used
```

### Risk Levels

- **CRITICAL**: Exact sanctions match or active enforcement
- **HIGH**: Strong fuzzy match or recent enforcement action
- **MEDIUM**: Weak match or historical enforcement
- **LOW**: No matches found

### Metadata Fields

```python
metadata = {
    'overall_risk_level': 'HIGH',
    'sanctions_matches': 2,
    'enforcement_actions': 1,
    'affiliated_entities_checked': 3,
    'restricted_jurisdictions': 5,
    'confidence_score': 0.85
}
```

## 🔄 Real-World Workflows

### 1. **New Protocol Screening**

```python
def screen_new_protocol(protocol_name, team_members):
    compliance_agent = ComplianceCheckerAgent()
    
    # Step 1: Screen the protocol
    protocol_result = compliance_agent.process_request({
        'action': 'full_compliance_check',
        'target': protocol_name,
        'parameters': {
            'affiliated_entities': team_members
        }
    })
    
    # Step 2: Generate recommendations
    if protocol_result.metadata['overall_risk_level'] in ['HIGH', 'CRITICAL']:
        return {
            'recommendation': 'REJECT',
            'reason': 'High compliance risk identified',
            'details': protocol_result.content
        }
    
    return {
        'recommendation': 'APPROVE',
        'monitoring_required': True,
        'details': protocol_result.content
    }
```

### 2. **Continuous Monitoring**

```python
async def continuous_monitoring(entities_to_monitor):
    compliance_agent = ComplianceCheckerAgent()
    
    for entity in entities_to_monitor:
        # Daily sanctions check
        result = compliance_agent.process_request({
            'action': 'sanctions_screening',
            'target': entity,
            'parameters': {}
        })
        
        # Alert on new risks
        if result.metadata['risk_level'] != entity.previous_risk_level:
            send_alert(f"Risk level changed for {entity}: {result.metadata['risk_level']}")
```

### 3. **Due Diligence Report**

```python
def generate_due_diligence_report(target_entity):
    compliance_agent = ComplianceCheckerAgent()
    
    # Comprehensive assessment
    assessment = compliance_agent.process_request({
        'action': 'risk_assessment',
        'target': target_entity,
        'parameters': {
            'assessment_depth': 'comprehensive',
            'include_mitigation_strategies': True
        }
    })
    
    # Generate formal report
    report = {
        'entity': target_entity,
        'assessment_date': datetime.now(),
        'risk_score': assessment.metadata['overall_risk_score'],
        'risk_level': assessment.metadata['overall_risk_level'],
        'detailed_analysis': assessment.content,
        'recommendations': extract_recommendations(assessment.content)
    }
    
    return report
```

## 🛡️ Data Sources

### Sanctions Lists
- **OFAC SDN**: US Treasury Specially Designated Nationals
- **OFAC Consolidated**: US Treasury Consolidated Sanctions
- **OFAC Crypto**: US Treasury Digital Currency Addresses
- **UN Security Council**: UN Sanctions List
- **EU Sanctions**: European Union Sanctions
- **UK HMT**: UK Treasury Sanctions

### Enforcement Agencies
- **SEC**: Securities and Exchange Commission
- **CFTC**: Commodity Futures Trading Commission
- **DOJ**: Department of Justice
- **FINRA**: Financial Industry Regulatory Authority
- **FinCEN**: Financial Crimes Enforcement Network

## ⚠️ Important Considerations

### Legal Compliance
- **Always validate results with legal counsel**
- **Implement proper data security measures**
- **Maintain audit trails for compliance decisions**
- **Update sanctions data regularly**

### Data Privacy
- **Encrypt sensitive compliance data**
- **Implement access controls**
- **Follow data retention policies**
- **Ensure GDPR/CCPA compliance**

### Operational Best Practices
- **Set up automated monitoring**
- **Establish escalation procedures**
- **Document compliance procedures**
- **Train staff on proper usage**

## 🚀 Advanced Features

### Custom Risk Scoring

```python
def custom_risk_scoring(compliance_results):
    risk_factors = {
        'sanctions_risk': 0.4,      # 40% weight
        'enforcement_risk': 0.3,    # 30% weight
        'jurisdiction_risk': 0.2,   # 20% weight
        'entity_risk': 0.1         # 10% weight
    }
    
    weighted_score = sum(
        compliance_results[factor] * weight
        for factor, weight in risk_factors.items()
    )
    
    return weighted_score
```

### Integration with External Systems

```python
class ComplianceWorkflow:
    def __init__(self):
        self.compliance_agent = ComplianceCheckerAgent()
        self.case_management = CaseManagementSystem()
        self.alert_system = AlertSystem()
    
    def process_entity(self, entity):
        # Screen entity
        result = self.compliance_agent.process_request({
            'action': 'full_compliance_check',
            'target': entity,
            'parameters': {}
        })
        
        # Create case if high risk
        if result.metadata['overall_risk_level'] == 'HIGH':
            case_id = self.case_management.create_case(entity, result)
            self.alert_system.send_alert(f"High-risk entity detected: {entity}")
        
        return result
```

## 📚 Additional Resources

- **Source Code**: `/agents/compliance_checker_agent.py`
- **Data Manager**: `/tools/sanctions_data_manager.py`
- **Examples**: `/examples/compliance_checker_demo.py`
- **Tests**: `/tests/test_agents.py`
- **Configuration**: `/config/settings.py`

## 🆘 Troubleshooting

### Common Issues

**"No sanctions data found"**
- Run sanctions data update: `python tools/update_sanctions_data.py`
- Check data directory permissions
- Verify internet connectivity for data downloads

**"API rate limit exceeded"**
- Implement request throttling
- Use caching to reduce API calls
- Consider upgrading API plan

**"Low confidence scores"**
- Check input data quality
- Verify entity name spelling
- Use entity resolution to find variations

### Getting Help

1. **Check the logs**: Look in `logs/compliance.log`
2. **Run diagnostics**: Use `agent.health_check()`
3. **Review examples**: Check practical usage patterns
4. **Test functionality**: Run the test suite

## 📈 Performance Optimization

- **Cache sanctions data locally**
- **Implement batch processing for multiple entities**
- **Use async processing for large datasets**
- **Monitor and optimize API usage**
- **Set up data preprocessing pipelines**

---

**Ready to start?** Run the demo: `python examples/compliance_checker_demo.py`