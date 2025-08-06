# Mac Setup Guide - Compliance Checker Agent

Complete guide for setting up and keeping the Compliance Checker Agent active on your Mac, integrated with Cursor for daily compliance tasks.

## 🍎 **Mac Terminal Setup**

### **Step 1: Initial Setup**

```bash
# Navigate to your project
cd /path/to/legal-ai-agents

# Install dependencies
pip3 install -r requirements.txt

# Test the agent works with real OFAC data
python3 run_ofac_test.py
```

### **Step 2: Create Virtual Environment (Recommended)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies in virtual environment
pip install -r requirements.txt

# Test the installation
python run_ofac_test.py
```

## 🎯 **Cursor Integration**

### **Open Project in Cursor**

```bash
# From your project directory
cursor .
```

### **Daily Interactive Tasks in Cursor**

Once in Cursor, you can run daily compliance tasks interactively:

```bash
# In Cursor's integrated terminal
python3 daily_compliance_tasks.py
```

This gives you a menu-driven interface:

```
🔍 DAILY COMPLIANCE TASKS
Choose a compliance task:
1. 🎯 Screen Single Entity
2. 📋 Batch Screen Multiple Entities  
3. 🔄 Update Sanctions Database
4. 📊 Quick Entity Risk Assessment
5. 🌐 Full Protocol Due Diligence
6. 🔗 Screen Crypto Addresses
7. 📈 Database Statistics
8. 🧪 Test Known Sanctioned Entities
9. 📝 Generate Compliance Report
0. ❌ Exit
```

### **Quick Tasks from Cursor Terminal**

```bash
# Screen a single entity quickly
python3 -c "
from agents.compliance_checker_agent import ComplianceCheckerAgent
agent = ComplianceCheckerAgent()
result = agent.process_request({
    'action': 'sanctions_screening',
    'target': 'Tornado Cash',
    'parameters': {}
})
print(f'Risk: {result.metadata.get(\"risk_level\")}')
print(f'Matches: {result.metadata.get(\"matches_found\")}')
"
```

## 🤖 **Automated Background Tasks**

### **Option 1: Background Scheduler (Recommended)**

Run the automated scheduler in the background:

```bash
# Start the background scheduler
python3 automated_compliance_scheduler.py &

# Check if it's running
ps aux | grep automated_compliance_scheduler

# View logs
tail -f compliance_scheduler.log
```

### **Option 2: macOS Launch Agents (System Integration)**

Create a Launch Agent for automatic startup:

```bash
# Create launch agent directory
mkdir -p ~/Library/LaunchAgents

# Create launch agent file
cat > ~/Library/LaunchAgents/com.compliance.checker.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.compliance.checker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/legal-ai-agents/automated_compliance_scheduler.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/legal-ai-agents</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/path/to/legal-ai-agents/scheduler.out.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/legal-ai-agents/scheduler.err.log</string>
</dict>
</plist>
EOF

# Load the launch agent
launchctl load ~/Library/LaunchAgents/com.compliance.checker.plist

# Start the service
launchctl start com.compliance.checker

# Check status
launchctl list | grep compliance
```

### **Option 3: Cron Jobs (Simple Scheduling)**

Set up cron jobs for specific tasks:

```bash
# Edit crontab
crontab -e

# Add these lines for automated tasks:

# Update sanctions database daily at 6 AM
0 6 * * * cd /path/to/legal-ai-agents && python3 -c "
import asyncio
from tools.sanctions_data_manager import create_sanctions_manager
async def update(): 
    manager = create_sanctions_manager()
    await manager.update_all_sources(force_update=True)
asyncio.run(update())
" >> sanctions_update.log 2>&1

# Daily entity monitoring at 8 AM (customize entities list)
0 8 * * * cd /path/to/legal-ai-agents && python3 -c "
from agents.compliance_checker_agent import ComplianceCheckerAgent
agent = ComplianceCheckerAgent()
entities = ['Tornado Cash', 'Uniswap', 'Your Protocol Name']
for entity in entities:
    result = agent.process_request({'action': 'sanctions_screening', 'target': entity, 'parameters': {}})
    if result.metadata.get('matches_found', 0) > 0:
        print(f'ALERT: {entity} has {result.metadata.get(\"matches_found\")} sanctions matches')
" >> entity_monitoring.log 2>&1
```

## 📋 **Configuration for Daily Use**

### **Create Entity Watchlist**

```bash
# Create a file with entities to monitor
cat > entities_to_monitor.txt << 'EOF'
Your DeFi Protocol
Partner Protocol Name
Competitor Protocol
Vendor Company
Service Provider
EOF
```

### **Configure Automated Scheduler**

The scheduler will create `scheduler_config.json` automatically. Edit it to customize:

```json
{
  "sanctions_update": {
    "enabled": true,
    "schedule": "daily",
    "time": "06:00"
  },
  "entity_monitoring": {
    "enabled": true,
    "schedule": "daily",
    "time": "08:00",
    "entities": [
      "Your Protocol Name",
      "Partner Protocol",
      "Competitor Protocol"
    ]
  },
  "batch_screening": {
    "enabled": true,
    "schedule": "weekly",
    "day": "monday",
    "time": "09:00",
    "entities_file": "entities_to_monitor.txt"
  },
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password",
      "recipients": ["compliance@yourcompany.com"]
    }
  }
}
```

## 🔄 **Daily Workflow Examples**

### **Morning Compliance Check**

```bash
# Quick morning compliance routine
cd /path/to/legal-ai-agents

# 1. Update sanctions database
python3 -c "
import asyncio
from tools.sanctions_data_manager import create_sanctions_manager
async def main():
    manager = create_sanctions_manager()
    results = await manager.update_all_sources()
    for source, result in results.items():
        print(f'{source}: {\"✅\" if result.get(\"success\") else \"❌\"} {result.get(\"entities_count\", 0)} entities')
asyncio.run(main())
"

# 2. Screen your key entities
python3 -c "
from agents.compliance_checker_agent import ComplianceCheckerAgent
agent = ComplianceCheckerAgent()

entities = ['Your Protocol', 'Partner Protocol', 'New Entity']
for entity in entities:
    result = agent.process_request({
        'action': 'sanctions_screening',
        'target': entity,
        'parameters': {}
    })
    risk = result.metadata.get('risk_level', 'UNKNOWN')
    matches = result.metadata.get('matches_found', 0)
    print(f'{entity}: {risk} risk ({matches} matches)')
"
```

### **Weekly Due Diligence**

```bash
# Comprehensive weekly check
python3 daily_compliance_tasks.py

# Select option 5 (Full Protocol Due Diligence)
# Enter protocol name and team members
# Get comprehensive compliance report
```

### **On-Demand Screening**

```bash
# Screen a new entity immediately
python3 -c "
from agents.compliance_checker_agent import ComplianceCheckerAgent
import sys

entity = sys.argv[1] if len(sys.argv) > 1 else input('Entity name: ')
agent = ComplianceCheckerAgent()

result = agent.process_request({
    'action': 'full_compliance_check',
    'target': entity,
    'parameters': {
        'check_enforcement_actions': True,
        'check_jurisdiction_restrictions': True
    }
})

print(f'Entity: {entity}')
print(f'Risk Level: {result.metadata.get(\"overall_risk_level\", \"UNKNOWN\")}')
print(f'Sanctions Matches: {result.metadata.get(\"sanctions_matches\", 0)}')
print(f'Enforcement Actions: {result.metadata.get(\"enforcement_actions\", 0)}')

if result.metadata.get('overall_risk_level') in ['HIGH', 'CRITICAL']:
    print('🚨 HIGH RISK - REQUIRES REVIEW')
else:
    print('✅ Low risk - proceed with caution')
" "$1"

# Usage: python3 quick_screen.py "New Protocol Name"
```

## 📊 **Monitoring and Maintenance**

### **Check System Status**

```bash
# Check if scheduler is running
ps aux | grep automated_compliance_scheduler

# View recent logs
tail -20 compliance_scheduler.log

# Check database status
python3 -c "
from tools.sanctions_data_manager import create_sanctions_manager
manager = create_sanctions_manager()
stats = manager.get_statistics()
print(f'Database: {stats[\"total_entities\"]:,} entities')
print(f'Size: {stats[\"database_size\"]:,} bytes')
for source, count in stats.get('entities_by_source', {}).items():
    print(f'{source}: {count:,}')
"
```

### **Database Maintenance**

```bash
# Force update all sanctions data
python3 -c "
import asyncio
from tools.sanctions_data_manager import create_sanctions_manager
async def main():
    manager = create_sanctions_manager()
    print('Updating all sanctions sources...')
    results = await manager.update_all_sources(force_update=True)
    for source, result in results.items():
        if result.get('success'):
            print(f'✅ {source}: {result.get(\"entities_count\", 0)} entities')
        else:
            print(f'❌ {source}: {result.get(\"error\", \"Unknown error\")}')
asyncio.run(main())
"

# Clean old log files (keep last 30 days)
find . -name "*.log" -mtime +30 -delete
find . -name "compliance_report_*.txt" -mtime +90 -delete
```

## 🚨 **Alerts and Notifications**

### **Set Up Email Alerts**

1. **Enable 2FA on Gmail**
2. **Create App Password**
3. **Update scheduler_config.json**:

```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "password": "your-16-char-app-password",
      "recipients": [
        "compliance@yourcompany.com",
        "legal@yourcompany.com"
      ]
    }
  }
}
```

### **Webhook Integration**

For Slack/Discord/Teams integration:

```json
{
  "notifications": {
    "webhook": {
      "enabled": true,
      "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
```

## 🔧 **Troubleshooting**

### **Common Issues**

```bash
# If Python path issues
which python3
# Make sure it points to the right Python

# If permission denied
chmod +x *.py

# If modules not found
pip3 install -r requirements.txt
# Or activate virtual environment first

# If database locked
rm data/sanctions/sanctions.db
# Then run update again

# If network issues
curl -I https://www.treasury.gov/ofac/downloads/sdn.xml
# Should return 200 OK
```

### **Restart Services**

```bash
# Restart launch agent
launchctl unload ~/Library/LaunchAgents/com.compliance.checker.plist
launchctl load ~/Library/LaunchAgents/com.compliance.checker.plist

# Restart background scheduler
pkill -f automated_compliance_scheduler
python3 automated_compliance_scheduler.py &
```

## 🎯 **Quick Reference Commands**

```bash
# Test OFAC integration
python3 run_ofac_test.py

# Interactive daily tasks
python3 daily_compliance_tasks.py

# Start background scheduler
python3 automated_compliance_scheduler.py &

# Quick entity screen
python3 -c "from agents.compliance_checker_agent import ComplianceCheckerAgent; agent = ComplianceCheckerAgent(); result = agent.process_request({'action': 'sanctions_screening', 'target': 'ENTITY_NAME', 'parameters': {}}); print(f'Risk: {result.metadata.get(\"risk_level\")}, Matches: {result.metadata.get(\"matches_found\")}')"

# Update sanctions database
python3 -c "import asyncio; from tools.sanctions_data_manager import create_sanctions_manager; asyncio.run(create_sanctions_manager().update_all_sources(force_update=True))"

# Check system status
ps aux | grep compliance && tail -5 compliance_scheduler.log
```

---

## 🎉 **You're All Set!**

Your Compliance Checker Agent is now:
- ✅ **Integrated with Cursor** for interactive daily tasks
- ✅ **Running automated background checks** 
- ✅ **Monitoring your entities** for sanctions changes
- ✅ **Generating compliance reports** automatically
- ✅ **Sending alerts** when risks are detected

**Start with**: `python3 daily_compliance_tasks.py` in Cursor's terminal!