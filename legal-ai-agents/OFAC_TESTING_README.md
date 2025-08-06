# Testing with Real OFAC Sanctions Data

This guide shows you how to test the **Compliance Checker Agent** with real, publicly accessible OFAC sanctions data from the US Treasury Department.

## 🚀 Quick Start

### Option 1: One-Click Test Runner
```bash
python run_ofac_test.py
```

### Option 2: Direct Test Execution
```bash
python examples/test_ofac_integration.py
```

## 📋 What the Test Does

The OFAC integration test performs the following steps:

### 1. **Real Data Download** 🌐
- Downloads the actual **OFAC SDN List** (XML format) from treasury.gov
- Downloads **OFAC Crypto Addresses** (JSON format) from treasury.gov
- Validates data format and structure
- Shows statistics about downloaded data

### 2. **Database Population** 💾
- Parses XML and JSON data using production parsers
- Stores entities in local SQLite database with full-text search
- Creates indexes for fast searching
- Shows before/after database statistics

### 3. **Known Entity Testing** 🎯
Tests sanctions screening against publicly known sanctioned entities:
- **Tornado Cash** (sanctioned crypto mixer)
- **Blender.io** (sanctioned crypto mixer)  
- **Lazarus Group** (North Korean hacking group)
- **Garantex** (sanctioned crypto exchange)
- **Uniswap** (legitimate protocol - should be clean)

### 4. **Crypto Address Screening** 🔗
Tests specific crypto addresses including:
- Known sanctioned Tornado Cash addresses
- Known sanctioned Blender.io addresses
- Clean addresses (should not match)

### 5. **Real Workflow Simulation** 🔄
- Simulates screening a new DeFi protocol
- Checks protocol name and team members
- Generates compliance recommendations
- Shows decision-making process

### 6. **Comprehensive Reporting** 📊
- Pass/fail status for each test
- Detailed error reporting
- Performance metrics
- Recommendations for improvements

## 📊 Expected Results

### ✅ **Successful Test Results**
When working correctly, you should see:

```
🟢 EXCELLENT - System is working well with real OFAC data

📊 Test Summary:
   OFAC Data Download: ✅ SUCCESS
   Sanctions Data Update: ✅ SUCCESS  
   Entity Screening Tests: 5/5 passed
   Workflow Test: ✅ SUCCESS

🎉 All tests passed! The Compliance Checker Agent is working correctly with real OFAC data.
```

### 📈 **Data Statistics**
Typical OFAC data volumes:
- **SDN List**: ~8,000-12,000 entities
- **Crypto Addresses**: ~500-1,000 addresses
- **Database Size**: ~5-10 MB
- **Processing Time**: 30-60 seconds

## 🔧 Prerequisites

### Required Dependencies
```bash
pip install requests aiohttp
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### System Requirements
- **Python 3.8+**
- **Internet connection** (for downloading OFAC data)
- **~50 MB disk space** (for sanctions database)
- **No API keys required** (uses public data)

## 🌐 Data Sources Used

### OFAC SDN List
- **URL**: `https://www.treasury.gov/ofac/downloads/sdn.xml`
- **Format**: XML
- **Content**: Specially Designated Nationals and Blocked Persons
- **Update Frequency**: Daily

### OFAC Crypto Addresses  
- **URL**: `https://home.treasury.gov/system/files/126/digital_currency_addresses.json`
- **Format**: JSON
- **Content**: Sanctioned cryptocurrency addresses
- **Update Frequency**: As needed

## 🎯 Test Scenarios

### High-Risk Entities (Should Match)
```python
# These should trigger HIGH/CRITICAL risk levels
test_entities = [
    "Tornado Cash",      # Sanctioned mixer
    "Blender.io",        # Sanctioned mixer
    "Lazarus Group",     # NK hacking group
    "Garantex"           # Sanctioned exchange
]
```

### Low-Risk Entities (Should Not Match)
```python
# These should show LOW risk levels
clean_entities = [
    "Uniswap",           # Legitimate DeFi protocol
    "Ethereum",          # Legitimate blockchain
    "Coinbase"           # Regulated exchange
]
```

### Sanctioned Crypto Addresses
```python
# Known sanctioned addresses (public information)
sanctioned_addresses = [
    "0x8589427373D6D84E98730D7795D8f6f8731FDA16",  # Tornado Cash
    "0x722122dF12D4e14e13Ac3b6895a86e84145b6967",  # Tornado Cash
    "1ES14c7qLb5CYhLMUekctxLgc1FV2Ti9DA"          # Blender.io
]
```

## 🔍 Understanding Test Results

### Risk Level Interpretation
- **CRITICAL**: Exact match on sanctions list
- **HIGH**: Strong fuzzy match or known sanctioned entity
- **MEDIUM**: Weak match or potential false positive
- **LOW**: No matches found

### Match Types
- **exact**: Perfect name match
- **fuzzy**: Similar name (>80% similarity)
- **alias**: Known alternative name
- **crypto**: Crypto address match

## 🛠️ Troubleshooting

### Common Issues

#### "Network Error" or "HTTP 404"
```bash
# OFAC data sources may be temporarily unavailable
# Try again later or check:
curl -I https://www.treasury.gov/ofac/downloads/sdn.xml
```

#### "XML Parsing Error"
```bash
# OFAC may have changed XML format
# Check the downloaded file manually
```

#### "No Matches Found for Known Sanctioned Entities"
```bash
# Check if data was downloaded and parsed correctly
# Verify database was populated
```

#### "Import Errors"
```bash
# Install missing dependencies
pip install -r requirements.txt
```

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Next Steps After Testing

### If Tests Pass ✅
1. **Integrate with your workflow**: Use the agent in production
2. **Set up monitoring**: Implement continuous sanctions checking
3. **Customize risk scoring**: Adjust parameters for your use case
4. **Add more data sources**: Integrate additional sanctions lists

### If Tests Fail ❌
1. **Check network connectivity**: Ensure OFAC sites are accessible
2. **Verify dependencies**: Install all required packages
3. **Review error messages**: Look for specific failure points
4. **Check data formats**: OFAC may have changed their data structure

## 🔄 Continuous Testing

### Daily Monitoring
```bash
# Set up a cron job to test daily
0 6 * * * cd /path/to/legal-ai-agents && python run_ofac_test.py
```

### Automated Alerts
```python
# Get notified when tests fail
if not test_success:
    send_alert("OFAC integration test failed - manual review required")
```

## 📊 Performance Benchmarks

### Typical Performance Metrics
- **Data Download**: 5-15 seconds
- **Database Update**: 10-30 seconds  
- **Entity Screening**: <1 second per entity
- **Full Workflow**: 2-5 seconds
- **Memory Usage**: ~100-200 MB during processing

### Optimization Tips
- **Cache data locally** to reduce download time
- **Use batch processing** for multiple entities
- **Implement rate limiting** for API calls
- **Monitor database size** and optimize queries

---

## ⚠️ Important Legal Notice

This testing framework uses **publicly available OFAC sanctions data** for compliance screening purposes. The data is provided by the US Treasury Department and is in the public domain.

**Key Points**:
- ✅ **Legal to use**: OFAC data is public and intended for compliance use
- ✅ **No API keys required**: Direct access to public data sources  
- ✅ **Real-time updates**: Downloads current sanctions data
- ⚠️ **Not legal advice**: Always consult with legal counsel for compliance decisions
- ⚠️ **Data accuracy**: Verify critical matches with official sources

---

**Ready to test?** Run: `python run_ofac_test.py`