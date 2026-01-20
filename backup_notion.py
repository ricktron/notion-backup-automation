#!/usr/bin/env python3
"""
Notion Backup Automation Script

This script backs up specified Notion databases to CSV format.
Designed to run via GitHub Actions with scheduled workflows.

Author: Rick Garnett
Created: January 2026
"""

import os
import sys
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

try:
    from notion_client import Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required package. Run: pip install -r requirements.txt")
    print(f"Details: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backup.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
CAPTAINS_LOG_DB_ID = os.getenv('CAPTAINS_LOG_DB_ID')
PROJECTS_TRACKER_DB_ID = os.getenv('PROJECTS_TRACKER_DB_ID')
BACKUP_DIR = Path('backups')


class NotionBackup:
    """Handle Notion database backups."""
    
    def __init__(self, token: str):
        """Initialize Notion client.
        
        Args:
            token: Notion integration token
        """
        if not token:
            raise ValueError("Notion token is required")
        
        self.client = Client(auth=token)
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
        logger.info("Notion client initialized successfully")
    
    def get_database_pages(self, database_id: str) -> List[Dict[str, Any]]:
        """Retrieve all pages from a Notion database.
        
        Args:
            database_id: The Notion database ID
            
        Returns:
            List of page objects
        """
        logger.info(f"Fetching pages from database: {database_id}")
        pages = []
        has_more = True
        start_cursor = None
        
        try:
            while has_more:
                response = self.client.databases.query(
                    database_id=database_id,
                    start_cursor=start_cursor
                )
                pages.extend(response.get('results', []))
                has_more = response.get('has_more', False)
                start_cursor = response.get('next_cursor')
                
            logger.info(f"Retrieved {len(pages)} pages")
            return pages
            
        except Exception as e:
            logger.error(f"Error fetching database pages: {e}")
            raise
    
    def extract_property_value(self, prop: Dict[str, Any]) -> str:
        """Extract value from Notion property based on its type.
        
        Args:
            prop: Notion property object
            
        Returns:
            Formatted string value
        """
        prop_type = prop.get('type')
        
        try:
            if prop_type == 'title':
                return ' '.join([t.get('plain_text', '') for t in prop.get('title', [])])
            elif prop_type == 'rich_text':
                return ' '.join([t.get('plain_text', '') for t in prop.get('rich_text', [])])
            elif prop_type == 'number':
                return str(prop.get('number', ''))
            elif prop_type == 'select':
                select = prop.get('select')
                return select.get('name', '') if select else ''
            elif prop_type == 'multi_select':
                return ', '.join([s.get('name', '') for s in prop.get('multi_select', [])])
            elif prop_type == 'date':
                date = prop.get('date')
                if date:
                    start = date.get('start', '')
                    end = date.get('end')
                    return f"{start} - {end}" if end else start
                return ''
            elif prop_type == 'checkbox':
                return 'Yes' if prop.get('checkbox') else 'No'
            elif prop_type == 'url':
                return prop.get('url', '')
            elif prop_type == 'email':
                return prop.get('email', '')
            elif prop_type == 'phone_number':
                return prop.get('phone_number', '')
            elif prop_type == 'status':
                status = prop.get('status')
                return status.get('name', '') if status else ''
            elif prop_type == 'people':
                return ', '.join([p.get('name', '') for p in prop.get('people', [])])
            elif prop_type == 'files':
                return ', '.join([f.get('name', '') for f in prop.get('files', [])])
            elif prop_type == 'relation':
                return f"{len(prop.get('relation', []))} relations"
            elif prop_type == 'created_time':
                return prop.get('created_time', '')
            elif prop_type == 'last_edited_time':
                return prop.get('last_edited_time', '')
            else:
                return str(prop)
        except Exception as e:
            logger.warning(f"Error extracting property type '{prop_type}': {e}")
            return ''
    
    def export_to_csv(self, database_id: str, database_name: str) -> Path:
        """Export Notion database to CSV file.
        
        Args:
            database_id: The Notion database ID
            database_name: Name for the backup file
            
        Returns:
            Path to created CSV file
        """
        logger.info(f"Starting export of '{database_name}'")
        
        try:
            # Get all pages
            pages = self.get_database_pages(database_id)
            
            if not pages:
                logger.warning(f"No pages found in database '{database_name}'")
                return None
            
            # Extract headers from first page
            headers = ['ID', 'Created', 'Last Edited']
            properties = pages[0].get('properties', {})
            headers.extend(properties.keys())
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{database_name}_{timestamp}.csv"
            filepath = self.backup_dir / filename
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                for page in pages:
                    row = [
                        page.get('id', ''),
                        page.get('created_time', ''),
                        page.get('last_edited_time', '')
                    ]
                    
                    for prop_name in properties.keys():
                        prop = page.get('properties', {}).get(prop_name, {})
                        value = self.extract_property_value(prop)
                        row.append(value)
                    
                    writer.writerow(row)
            
            logger.info(f"✓ Successfully exported {len(pages)} pages to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"✗ Failed to export '{database_name}': {e}")
            raise
    
    def backup_databases(self, databases: Dict[str, str]) -> List[Path]:
        """Backup multiple Notion databases.
        
        Args:
            databases: Dictionary mapping database names to IDs
            
        Returns:
            List of created backup file paths
        """
        backup_files = []
        errors = []
        
        for name, db_id in databases.items():
            try:
                if not db_id:
                    logger.warning(f"Skipping '{name}': No database ID provided")
                    continue
                
                filepath = self.export_to_csv(db_id, name)
                if filepath:
                    backup_files.append(filepath)
                    
            except Exception as e:
                error_msg = f"Failed to backup '{name}': {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Backup Summary")
        logger.info(f"{'='*60}")
        logger.info(f"Successful backups: {len(backup_files)}")
        logger.info(f"Failed backups: {len(errors)}")
        
        if backup_files:
            logger.info(f"\nBackup files created:")
            for filepath in backup_files:
                logger.info(f"  - {filepath}")
        
        if errors:
            logger.error(f"\nErrors encountered:")
            for error in errors:
                logger.error(f"  - {error}")
            raise Exception(f"{len(errors)} backup(s) failed")
        
        return backup_files


def send_notification(success: bool, message: str):
    """Send notification about backup status.
    
    Args:
        success: Whether backup was successful
        message: Notification message
    """
    # Add your notification logic here (email, Slack, Discord, etc.)
    # Example for Slack:
    # webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    # if webhook_url:
    #     import requests
    #     requests.post(webhook_url, json={"text": message})
    
    status = "✓ SUCCESS" if success else "✗ FAILED"
    logger.info(f"\n{status}: {message}")


def main():
    """Main execution function."""
    logger.info("="*60)
    logger.info("Notion Backup Automation Started")
    logger.info("="*60)
    
    # Validate configuration
    if not NOTION_TOKEN:
        logger.error("NOTION_TOKEN environment variable is not set")
        send_notification(False, "Backup failed: Missing NOTION_TOKEN")
        sys.exit(1)
    
    databases = {
        'captains_log': CAPTAINS_LOG_DB_ID,
        'projects_tracker': PROJECTS_TRACKER_DB_ID
    }
    
    # Remove None values
    databases = {k: v for k, v in databases.items() if v}
    
    if not databases:
        logger.error("No database IDs configured")
        send_notification(False, "Backup failed: No databases configured")
        sys.exit(1)
    
    try:
        # Initialize backup handler
        backup = NotionBackup(NOTION_TOKEN)
        
        # Perform backups
        backup_files = backup.backup_databases(databases)
        
        # Send success notification
        message = f"Successfully backed up {len(backup_files)} database(s)"
        send_notification(True, message)
        
        logger.info("\nBackup completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"\nBackup failed with error: {e}")
        send_notification(False, f"Backup failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
