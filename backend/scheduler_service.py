from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class DailyReportScheduler:
    def __init__(self, report_callback):
        self.scheduler = AsyncIOScheduler()
        self.report_callback = report_callback
        self.is_running = False
    
    def start(self, hour: int = 23, minute: int = 59):
        """Start the scheduler to send daily reports"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        # Schedule daily report at specified time (UTC)
        self.scheduler.add_job(
            self.report_callback,
            CronTrigger(hour=hour, minute=minute),
            id="daily_report",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info(f"Daily report scheduler started - will run at {hour:02d}:{minute:02d} UTC")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Daily report scheduler stopped")
    
    async def trigger_report_now(self):
        """Manually trigger the daily report"""
        logger.info("Manually triggering daily report")
        await self.report_callback()
