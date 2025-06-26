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

## Key Implementation Details

- **Incremental Logic**: Files are copied only if they don't exist at destination OR if source file has newer modification time OR different file size
- **Space Validation**: Pre-calculates required space by checking only files that need copying, not entire source drive
- **Progress Tracking**: Reports progress every 100 copied files, with special logging for large files
- **Error Handling**: Continues backup on individual file failures, logging errors without stopping the entire process
- **macOS Compatibility**: Uses `statvfs.f_bavail` instead of `f_available` for disk space calculation on macOS

## External Drive Path Handling

Drive paths must be quoted when containing spaces. Typical macOS external drive paths are `/Volumes/Drive Name`. The system validates both read access to source and write access to destination before starting.

## Logging

Automatic daily log files are created with format `backup_YYYYMMDD.log`. When using background scheduling with `nohup`, output is redirected to `nohup.out`.