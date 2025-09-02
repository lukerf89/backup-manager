# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based automated backup manager for external hard drives. The system performs incremental backups by only copying new or modified files, with built-in scheduling capabilities for automated daily backups.

## Core Architecture

The project consists of a single main module with three key components:

1. **BackupManager Class**: Core backup logic with methods for drive validation, space calculation, incremental file sync, and progress tracking
2. **Scheduling System**: Uses the `schedule` library to run daily automated backups at specified times
3. **CLI Interface**: Command-line argument parsing for immediate runs vs scheduled operations

The backup process follows this flow:
- Validate source and destination drives exist and are accessible
- Calculate space requirements by checking only files that need copying (new/modified)
- Perform incremental sync using file modification time and size comparison
- Log detailed progress with special handling for large files (>100MB)

## Common Commands

**Setup:**
```bash
pip3 install -r requirements.txt
```

**Run immediate backup:**
```bash
python3 backup_manager.py '/Volumes/SourceDrive' '/Volumes/DestinationDrive' --run-now
```

**Schedule daily backup:**
```bash
python3 backup_manager.py '/Volumes/SourceDrive' '/Volumes/DestinationDrive' --time 02:00
```

**Background scheduling:**
```bash
nohup python3 backup_manager.py '/Volumes/SourceDrive' '/Volumes/DestinationDrive' &
```

**Monitor background process:**
```bash
ps aux | grep backup_manager
tail -f nohup.out
```

**Find large files needing backup:**
```bash
python3 find_large_files.py '/Volumes/SourceDrive' '/Volumes/DestinationDrive'
```

**Stop background scheduler:**
```bash
kill $(ps aux | grep 'backup_manager.py' | grep -v grep | awk '{print $2}')
```

## Key Implementation Details

- **Incremental Logic**: Files are copied only if they don't exist at destination OR if source file has newer modification time OR different file size
- **Space Validation**: Pre-calculates required space by checking only files that need copying, not entire source drive
- **Progress Tracking**: Reports progress every 100 copied files, with special logging for large files
- **Error Handling**: Continues backup on individual file failures, logging errors without stopping the entire process
- **macOS Compatibility**: Uses `statvfs.f_bavail` instead of `f_available` for disk space calculation on macOS
- **Symbolic Link Handling**: Automatically detects and skips symbolic links (common in Python venv directories) to prevent copy failures
- **Permission Error Handling**: Gracefully handles permission-denied errors with warnings, allowing backup to continue

## External Drive Path Handling

Drive paths must be quoted when containing spaces. Typical macOS external drive paths are `/Volumes/Drive Name`. The system validates both read access to source and write access to destination before starting.

## Project Files

- `backup_manager.py`: Main backup script with BackupManager class (backup_manager.py:17)
- `find_large_files.py`: Utility to identify and analyze large files needing backup
- `requirements.txt`: Python dependencies (currently just `schedule==1.2.0`)
- `readme.txt`: User documentation with example commands

## Logging

Automatic daily log files are created with format `backup_YYYYMMDD.log`. When using background scheduling with `nohup`, output is redirected to `nohup.out`.

The backup process now provides enhanced reporting:
- Summary of files copied with total size
- Count of skipped symbolic links (if any)
- Count of permission errors encountered (if any)

## Testing Backup Without Copying

To verify what would be backed up without actually copying files, use the `find_large_files.py` utility which performs the same checks as the main backup but only reports what would be copied.

## Common Issues and Solutions

**Symbolic Link Errors in Python Virtual Environments**
- The backup manager automatically skips symbolic links, preventing errors with `venv/bin/python` files
- These are safely ignored as they're recreated when virtual environments are rebuilt

**Permission Denied Errors**
- Files with restricted permissions are logged as warnings but don't stop the backup
- Review permission error count in the summary to identify protected files