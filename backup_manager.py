#!/usr/bin/env python3
"""
Automated External Hard Drive Backup Manager
Syncs files from source external drive to destination external drive
"""

import os
import sys
import shutil
import logging
import argparse
from datetime import datetime
from pathlib import Path
import schedule
import time

class BackupManager:
    def __init__(self, source_path, destination_path, log_file=None):
        self.source_path = Path(source_path)
        self.destination_path = Path(destination_path)
        self.setup_logging(log_file)
        
    def setup_logging(self, log_file=None):
        if log_file is None:
            log_file = f"backup_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_drives(self):
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source drive not found: {self.source_path}")
        
        if not self.destination_path.exists():
            raise FileNotFoundError(f"Destination drive not found: {self.destination_path}")
        
        if not os.access(self.source_path, os.R_OK):
            raise PermissionError(f"Cannot read from source: {self.source_path}")
        
        if not os.access(self.destination_path, os.W_OK):
            raise PermissionError(f"Cannot write to destination: {self.destination_path}")
        
        self.logger.info(f"Source drive validated: {self.source_path}")
        self.logger.info(f"Destination drive validated: {self.destination_path}")
    
    def get_drive_space(self, path):
        statvfs = os.statvfs(path)
        free_bytes = statvfs.f_frsize * statvfs.f_bavail
        total_bytes = statvfs.f_frsize * statvfs.f_blocks
        return free_bytes, total_bytes
    
    def calculate_backup_size(self):
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(self.source_path):
            for file in files:
                source_file = Path(root) / file
                relative_path = source_file.relative_to(self.source_path)
                dest_file = self.destination_path / relative_path
                
                try:
                    should_copy = False
                    
                    if not dest_file.exists():
                        should_copy = True
                    else:
                        source_stat = source_file.stat()
                        dest_stat = dest_file.stat()
                        
                        if (source_stat.st_mtime > dest_stat.st_mtime or 
                            source_stat.st_size != dest_stat.st_size):
                            should_copy = True
                    
                    if should_copy:
                        total_size += source_file.stat().st_size
                        file_count += 1
                        
                except (OSError, FileNotFoundError):
                    self.logger.warning(f"Could not stat file: {source_file}")
        
        return total_size, file_count
    
    def sync_files(self):
        try:
            self.logger.info("Starting backup sync...")
            backup_size, file_count = self.calculate_backup_size()
            
            free_space, _ = self.get_drive_space(self.destination_path)
            
            if backup_size > free_space:
                raise RuntimeError(f"Insufficient space. Need {backup_size / (1024**3):.2f}GB, "
                                 f"have {free_space / (1024**3):.2f}GB")
            
            self.logger.info(f"Backing up {file_count} files ({backup_size / (1024**3):.2f}GB)")
            
            copied_files = 0
            copied_size = 0
            
            for root, dirs, files in os.walk(self.source_path):
                for file in files:
                    source_file = Path(root) / file
                    relative_path = source_file.relative_to(self.source_path)
                    dest_file = self.destination_path / relative_path
                    
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        should_copy = False
                        
                        if not dest_file.exists():
                            should_copy = True
                        else:
                            source_stat = source_file.stat()
                            dest_stat = dest_file.stat()
                            
                            # Check if file is newer or different size
                            if (source_stat.st_mtime > dest_stat.st_mtime or 
                                source_stat.st_size != dest_stat.st_size):
                                should_copy = True
                        
                        if should_copy:
                            file_size = source_file.stat().st_size
                            if file_size > 100 * 1024 * 1024:  # Log large files (>100MB)
                                self.logger.info(f"Copying large file: {source_file} ({file_size / (1024**2):.1f}MB)")
                            
                            shutil.copy2(source_file, dest_file)
                            copied_files += 1
                            copied_size += file_size
                            
                            if copied_files % 100 == 0:
                                self.logger.info(f"Progress: {copied_files}/{file_count} files "
                                               f"({copied_size / (1024**3):.2f}GB)")
                        else:
                            if copied_files % 1000 == 0:  # Show skipped progress too
                                self.logger.info(f"Skipped {copied_files} duplicate files so far")
                    
                    except Exception as e:
                        self.logger.error(f"Failed to copy {source_file}: {e}")
            
            self.logger.info(f"Backup completed: {copied_files} files copied "
                           f"({copied_size / (1024**3):.2f}GB)")
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            raise
    
    def run_backup(self):
        start_time = datetime.now()
        self.logger.info(f"Starting backup at {start_time}")
        
        try:
            self.validate_drives()
            self.sync_files()
            
            end_time = datetime.now()
            duration = end_time - start_time
            self.logger.info(f"Backup completed successfully in {duration}")
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
        
        return True

def schedule_daily_backup(source_path, destination_path, backup_time="02:00"):
    backup_manager = BackupManager(source_path, destination_path)
    
    schedule.every().day.at(backup_time).do(backup_manager.run_backup)
    
    print(f"Backup scheduled daily at {backup_time}")
    print(f"Source: {source_path}")
    print(f"Destination: {destination_path}")
    print("Press Ctrl+C to stop the scheduler")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")

def main():
    parser = argparse.ArgumentParser(description='External Hard Drive Backup Manager')
    parser.add_argument('source', help='Source external drive path')
    parser.add_argument('destination', help='Destination external drive path')
    parser.add_argument('--time', default='02:00', help='Daily backup time (HH:MM format)')
    parser.add_argument('--run-now', action='store_true', help='Run backup immediately')
    parser.add_argument('--log-file', help='Custom log file path')
    
    args = parser.parse_args()
    
    if args.run_now:
        backup_manager = BackupManager(args.source, args.destination, args.log_file)
        success = backup_manager.run_backup()
        sys.exit(0 if success else 1)
    else:
        schedule_daily_backup(args.source, args.destination, args.time)

if __name__ == "__main__":
    main()