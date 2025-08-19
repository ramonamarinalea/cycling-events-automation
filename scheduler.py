#!/usr/bin/env python3
"""
Scheduler for running the cycling event automation periodically
"""

import schedule
import time
import logging
from datetime import datetime
from event_scraper import CyclingEventAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_automation():
    """Run the cycling event automation"""
    try:
        logger.info("=" * 50)
        logger.info(f"Starting scheduled run at {datetime.now()}")
        
        automation = CyclingEventAutomation()
        events_added = automation.run()
        
        logger.info(f"Scheduled run complete. Processed {events_added} events")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Error in scheduled run: {e}")


def main():
    """Main scheduler function"""
    logger.info("Starting cycling event automation scheduler...")
    
    # Schedule the automation to run daily at 3 AM
    schedule.every().day.at("03:00").do(run_automation)
    
    # Also run every Sunday for a weekly comprehensive update
    schedule.every().sunday.at("02:00").do(run_automation)
    
    # Run once on startup
    logger.info("Running initial automation...")
    run_automation()
    
    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    logger.info(f"Next run scheduled for: {schedule.next_run()}")
    
    # Keep the scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying


if __name__ == "__main__":
    main()