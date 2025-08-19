#!/usr/bin/env python3
"""
Standalone Python script that calls the sync_prop_firms endpoint every 5 seconds.
This script can run independently of the main application.
"""

import requests
import time
import json
import logging
import sys
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class PropFirmSyncScheduler:
    def __init__(self, base_url: str = "http://localhost:5000", interval: int = 5):
        """
        Initialize the sync scheduler.
        
        Args:
            base_url: The base URL of your Flask application
            interval: Sync interval in seconds (default: 5)
        """
        self.base_url = base_url.rstrip('/')
        self.sync_url = f"{self.base_url}/prop_firms/sync_public"
        self.interval = interval
        self.running = False
        
    def sync_prop_firms(self, prop_firm_id: Optional[int] = None) -> dict:
        """
        Call the sync endpoint.
        
        Args:
            prop_firm_id: Optional specific prop firm ID to sync. If None, syncs all active firms.
            
        Returns:
            Response dictionary from the API
        """
        try:
            payload = {}
            if prop_firm_id:
                payload["prop_firm_id"] = prop_firm_id
                
            response = requests.post(
                self.sync_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Sync successful: {result.get('message', 'No message')}")
                return result
            else:
                logger.error(f"Sync failed with status {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during sync: {str(e)}")
            return {"success": False, "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return {"success": False, "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Unexpected error during sync: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def start_scheduler(self):
        """
        Start the sync scheduler loop.
        """
        self.running = True
        logger.info(f"Starting prop firm sync scheduler (interval: {self.interval}s)")
        logger.info(f"Sync endpoint: {self.sync_url}")
        
        # Initial sync
        logger.info("Performing initial sync...")
        self.sync_prop_firms()
        
        try:
            while self.running:
                time.sleep(self.interval)
                if self.running:  # Check again in case stop was called during sleep
                    self.sync_prop_firms()
                    
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, stopping scheduler...")
            self.stop_scheduler()
        except Exception as e:
            logger.error(f"Unexpected error in scheduler loop: {str(e)}")
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """
        Stop the sync scheduler.
        """
        self.running = False
        logger.info("Sync scheduler stopped")

def main():
    """
    Main function to run the scheduler.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Prop Firm Sync Scheduler')
    parser.add_argument(
        '--url', 
        default='http://localhost:5000',
        help='Base URL of the Flask application (default: http://localhost:5000)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Sync interval in seconds (default: 5)'
    )
    parser.add_argument(
        '--prop-firm-id',
        type=int,
        help='Specific prop firm ID to sync (optional, syncs all active firms if not provided)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run sync once and exit (no scheduling)'
    )
    
    args = parser.parse_args()
    
    scheduler = PropFirmSyncScheduler(base_url=args.url, interval=args.interval)
    
    if args.once:
        logger.info("Running single sync operation...")
        result = scheduler.sync_prop_firms(args.prop_firm_id)
        if result.get('success'):
            logger.info("Single sync completed successfully")
            sys.exit(0)
        else:
            logger.error("Single sync failed")
            sys.exit(1)
    else:
        logger.info(f"Starting continuous sync scheduler...")
        scheduler.start_scheduler()

if __name__ == "__main__":
    main()
