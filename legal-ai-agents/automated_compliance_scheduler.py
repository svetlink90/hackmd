#!/usr/bin/env python3
"""
Automated Compliance Scheduler

Background service for automated compliance tasks including:
- Daily sanctions database updates
- Periodic entity monitoring
- Automated report generation
- Alert notifications
"""

import asyncio
import json
import logging
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import sys
sys.path.insert(0, str(Path(__file__).parent))

from agents.compliance_checker_agent import ComplianceCheckerAgent
from tools.sanctions_data_manager import create_sanctions_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('compliance_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComplianceScheduler:
    """Automated compliance task scheduler"""
    
    def __init__(self, config_file: str = "scheduler_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        self.compliance_agent = ComplianceCheckerAgent()
        self.sanctions_manager = create_sanctions_manager()
        
        # Track last execution times
        self.last_executions = {}
        
        logger.info("Compliance Scheduler initialized")
    
    def load_config(self) -> Dict[str, Any]:
        """Load scheduler configuration"""
        default_config = {
            "sanctions_update": {
                "enabled": True,
                "schedule": "daily",
                "time": "06:00"
            },
            "entity_monitoring": {
                "enabled": True,
                "schedule": "daily", 
                "time": "08:00",
                "entities": []
            },
            "batch_screening": {
                "enabled": False,
                "schedule": "weekly",
                "day": "monday",
                "time": "09:00",
                "entities_file": "entities_to_monitor.txt"
            },
            "report_generation": {
                "enabled": False,
                "schedule": "weekly",
                "day": "friday",
                "time": "17:00"
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipients": []
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {}
                }
            },
            "retention": {
                "logs_days": 30,
                "reports_days": 90
            }
        }
        
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
                    logger.info(f"Loaded configuration from {self.config_file}")
            else:
                # Create default config file
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default configuration: {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        
        return default_config
    
    async def update_sanctions_database(self):
        """Automated sanctions database update"""
        logger.info("Starting automated sanctions database update")
        
        try:
            # Get current stats
            current_stats = self.sanctions_manager.get_statistics()
            logger.info(f"Current database: {current_stats['total_entities']} entities")
            
            # Update from sources
            update_results = await self.sanctions_manager.update_all_sources(force_update=True)
            
            # Log results
            success_count = 0
            error_count = 0
            
            for source, result in update_results.items():
                if result.get('success'):
                    entities_count = result.get('entities_count', 0)
                    logger.info(f"✅ {source}: {entities_count} entities updated")
                    success_count += 1
                else:
                    error = result.get('error', 'Unknown error')
                    logger.error(f"❌ {source}: {error}")
                    error_count += 1
            
            # Get updated stats
            updated_stats = self.sanctions_manager.get_statistics()
            change = updated_stats['total_entities'] - current_stats['total_entities']
            
            logger.info(f"Database update completed: {updated_stats['total_entities']} entities ({change:+d} change)")
            
            # Send notification if configured
            if success_count > 0 or error_count > 0:
                await self.send_notification(
                    subject="Sanctions Database Update",
                    message=f"Update completed: {success_count} sources succeeded, {error_count} failed. Total entities: {updated_stats['total_entities']} ({change:+d})"
                )
            
            self.last_executions['sanctions_update'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in sanctions database update: {e}")
            await self.send_notification(
                subject="Sanctions Database Update Failed",
                message=f"Error: {str(e)}"
            )
    
    async def monitor_entities(self):
        """Monitor configured entities for changes"""
        entities = self.config.get('entity_monitoring', {}).get('entities', [])
        
        if not entities:
            logger.info("No entities configured for monitoring")
            return
        
        logger.info(f"Starting entity monitoring for {len(entities)} entities")
        
        alerts = []
        
        for entity in entities:
            try:
                logger.info(f"Monitoring entity: {entity}")
                
                response = self.compliance_agent.process_request({
                    'action': 'sanctions_screening',
                    'target': entity,
                    'parameters': {
                        'check_crypto_addresses': True,
                        'check_aliases': True
                    }
                })
                
                risk_level = response.metadata.get('risk_level', 'UNKNOWN')
                matches = response.metadata.get('matches_found', 0)
                
                # Check if risk level has changed
                previous_risk = self.get_previous_risk_level(entity)
                
                if risk_level != previous_risk:
                    alert_msg = f"Risk level changed for {entity}: {previous_risk} → {risk_level} ({matches} matches)"
                    logger.warning(alert_msg)
                    alerts.append(alert_msg)
                    
                    # Update stored risk level
                    self.store_risk_level(entity, risk_level)
                
                elif matches > 0:
                    logger.info(f"Entity {entity}: {risk_level} risk ({matches} matches) - no change")
                else:
                    logger.info(f"Entity {entity}: Clean - no sanctions matches")
                
            except Exception as e:
                error_msg = f"Error monitoring {entity}: {str(e)}"
                logger.error(error_msg)
                alerts.append(error_msg)
        
        # Send alerts if any
        if alerts:
            await self.send_notification(
                subject=f"Entity Monitoring Alerts ({len(alerts)})",
                message="\n".join(alerts)
            )
        
        self.last_executions['entity_monitoring'] = datetime.now()
    
    async def batch_screen_entities(self):
        """Batch screen entities from file"""
        entities_file = self.config.get('batch_screening', {}).get('entities_file', 'entities_to_monitor.txt')
        
        if not Path(entities_file).exists():
            logger.warning(f"Entities file not found: {entities_file}")
            return
        
        try:
            with open(entities_file, 'r') as f:
                entities = [line.strip() for line in f if line.strip()]
            
            if not entities:
                logger.info("No entities found in file")
                return
            
            logger.info(f"Starting batch screening for {len(entities)} entities")
            
            results = []
            high_risk_entities = []
            
            for entity in entities:
                try:
                    response = self.compliance_agent.process_request({
                        'action': 'sanctions_screening',
                        'target': entity,
                        'parameters': {}
                    })
                    
                    risk_level = response.metadata.get('risk_level', 'UNKNOWN')
                    matches = response.metadata.get('matches_found', 0)
                    
                    results.append({
                        'entity': entity,
                        'risk_level': risk_level,
                        'matches': matches,
                        'success': response.success
                    })
                    
                    if risk_level in ['HIGH', 'CRITICAL']:
                        high_risk_entities.append(f"{entity} ({risk_level}, {matches} matches)")
                    
                    logger.info(f"Screened {entity}: {risk_level} ({matches} matches)")
                    
                except Exception as e:
                    logger.error(f"Error screening {entity}: {e}")
                    results.append({
                        'entity': entity,
                        'risk_level': 'ERROR',
                        'matches': 0,
                        'success': False,
                        'error': str(e)
                    })
            
            # Generate summary
            total = len(results)
            successful = len([r for r in results if r['success']])
            high_risk = len([r for r in results if r.get('risk_level') in ['HIGH', 'CRITICAL']])
            
            summary = f"Batch screening completed: {successful}/{total} successful, {high_risk} high-risk entities"
            logger.info(summary)
            
            # Send notification with results
            message = summary
            if high_risk_entities:
                message += f"\n\nHigh-risk entities requiring review:\n" + "\n".join(high_risk_entities)
            
            await self.send_notification(
                subject="Batch Entity Screening Results",
                message=message
            )
            
            self.last_executions['batch_screening'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error in batch screening: {e}")
            await self.send_notification(
                subject="Batch Screening Failed",
                message=f"Error: {str(e)}"
            )
    
    async def generate_reports(self):
        """Generate periodic compliance reports"""
        logger.info("Generating periodic compliance reports")
        
        try:
            # Database statistics report
            stats = self.sanctions_manager.get_statistics()
            
            report_date = datetime.now().strftime("%Y-%m-%d")
            report_file = f"compliance_summary_{report_date}.txt"
            
            with open(report_file, 'w') as f:
                f.write(f"COMPLIANCE SUMMARY REPORT\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"{'='*50}\n\n")
                
                f.write(f"SANCTIONS DATABASE STATISTICS\n")
                f.write(f"Total entities: {stats['total_entities']:,}\n")
                f.write(f"Database size: {stats['database_size']:,} bytes\n\n")
                
                if stats['entities_by_source']:
                    f.write(f"ENTITIES BY SOURCE\n")
                    for source, count in stats['entities_by_source'].items():
                        f.write(f"{source}: {count:,}\n")
                    f.write("\n")
                
                if stats['last_updates']:
                    f.write(f"LAST UPDATES\n")
                    for source, update_time in stats['last_updates'].items():
                        f.write(f"{source}: {update_time or 'Never'}\n")
                    f.write("\n")
                
                f.write(f"SCHEDULER STATUS\n")
                for task, last_run in self.last_executions.items():
                    f.write(f"{task}: {last_run.isoformat() if last_run else 'Never'}\n")
            
            logger.info(f"Report generated: {report_file}")
            
            await self.send_notification(
                subject="Weekly Compliance Report",
                message=f"Compliance report generated: {report_file}\n\nDatabase: {stats['total_entities']:,} entities"
            )
            
            self.last_executions['report_generation'] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
    
    def get_previous_risk_level(self, entity: str) -> str:
        """Get previously stored risk level for entity"""
        risk_file = Path("entity_risk_levels.json")
        
        if not risk_file.exists():
            return "UNKNOWN"
        
        try:
            with open(risk_file, 'r') as f:
                risk_data = json.load(f)
                return risk_data.get(entity, "UNKNOWN")
        except Exception:
            return "UNKNOWN"
    
    def store_risk_level(self, entity: str, risk_level: str):
        """Store risk level for entity"""
        risk_file = Path("entity_risk_levels.json")
        
        try:
            risk_data = {}
            if risk_file.exists():
                with open(risk_file, 'r') as f:
                    risk_data = json.load(f)
            
            risk_data[entity] = risk_level
            
            with open(risk_file, 'w') as f:
                json.dump(risk_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error storing risk level: {e}")
    
    async def send_notification(self, subject: str, message: str):
        """Send notification via configured channels"""
        try:
            # Email notification
            email_config = self.config.get('notifications', {}).get('email', {})
            if email_config.get('enabled', False):
                await self.send_email_notification(subject, message, email_config)
            
            # Webhook notification
            webhook_config = self.config.get('notifications', {}).get('webhook', {})
            if webhook_config.get('enabled', False):
                await self.send_webhook_notification(subject, message, webhook_config)
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    async def send_email_notification(self, subject: str, message: str, config: Dict[str, Any]):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = config['username']
            msg['To'] = ', '.join(config['recipients'])
            msg['Subject'] = f"[Compliance Alert] {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            
            text = msg.as_string()
            server.sendmail(config['username'], config['recipients'], text)
            server.quit()
            
            logger.info(f"Email notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
    
    async def send_webhook_notification(self, subject: str, message: str, config: Dict[str, Any]):
        """Send webhook notification"""
        try:
            import aiohttp
            
            payload = {
                'subject': subject,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config['url'],
                    json=payload,
                    headers=config.get('headers', {})
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent: {subject}")
                    else:
                        logger.error(f"Webhook failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
    
    def setup_schedule(self):
        """Setup scheduled tasks"""
        config = self.config
        
        # Sanctions database update
        if config.get('sanctions_update', {}).get('enabled', True):
            schedule_time = config['sanctions_update'].get('time', '06:00')
            schedule.every().day.at(schedule_time).do(self.run_async_task, self.update_sanctions_database)
            logger.info(f"Scheduled sanctions update daily at {schedule_time}")
        
        # Entity monitoring
        if config.get('entity_monitoring', {}).get('enabled', True):
            schedule_time = config['entity_monitoring'].get('time', '08:00')
            schedule.every().day.at(schedule_time).do(self.run_async_task, self.monitor_entities)
            logger.info(f"Scheduled entity monitoring daily at {schedule_time}")
        
        # Batch screening
        if config.get('batch_screening', {}).get('enabled', False):
            day = config['batch_screening'].get('day', 'monday')
            schedule_time = config['batch_screening'].get('time', '09:00')
            getattr(schedule.every(), day).at(schedule_time).do(self.run_async_task, self.batch_screen_entities)
            logger.info(f"Scheduled batch screening every {day} at {schedule_time}")
        
        # Report generation
        if config.get('report_generation', {}).get('enabled', False):
            day = config['report_generation'].get('day', 'friday')
            schedule_time = config['report_generation'].get('time', '17:00')
            getattr(schedule.every(), day).at(schedule_time).do(self.run_async_task, self.generate_reports)
            logger.info(f"Scheduled report generation every {day} at {schedule_time}")
    
    def run_async_task(self, task_func):
        """Run async task in sync context"""
        try:
            asyncio.run(task_func())
        except Exception as e:
            logger.error(f"Error running scheduled task: {e}")
    
    def run(self):
        """Run the scheduler"""
        logger.info("Starting Compliance Scheduler")
        
        self.setup_schedule()
        
        logger.info("Scheduler is running. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")

def main():
    """Main function"""
    scheduler = ComplianceScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()