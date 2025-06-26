BACKUP MANAGER - README
========================

OVERVIEW
--------
Automated backup script for external hard drives. Copies only new or modified files to save time and space.

SETUP
-----
1. Install required dependencies:
   pip3 install -r requirements.txt

2. Make sure both external drives are connected and mounted

USAGE COMMANDS
--------------

Run backup immediately (one-time):
  python3 backup_manager.py '/Volumes/Working HD' '/Volumes/Luke'\''s HD' --run-now

Schedule daily backups at 2:00 AM:
  python3 backup_manager.py '/Volumes/Working HD' '/Volumes/Luke'\''s HD'

Schedule daily backups at custom time (e.g., 3:30 AM):
  python3 backup_manager.py '/Volumes/Working HD' '/Volumes/Luke'\''s HD' --time 03:30

Run scheduled backup in background (survives terminal close):
  nohup python3 backup_manager.py '/Volumes/Working HD' '/Volumes/Luke'\''s HD' &

MONITORING
----------

Check if scheduler is running:
  ps aux | grep backup_manager

View logs (when using nohup):
  tail -f nohup.out

Stop background scheduler:
  kill [process_id]

FEATURES
--------
- Only copies new or modified files (incremental backup)
- Validates drive connections before starting
- Checks available space before copying
- Progress tracking with file counts and sizes
- Detailed logging of all operations
- Handles large files (shows progress for files >100MB)
- Error handling and recovery

TROUBLESHOOTING
---------------
- If you get "permission denied" errors, run with sudo
- Make sure drive paths are correct (check /Volumes/ for mounted drives)
- Use quotes around drive names with spaces
- Logs show detailed error messages for debugging

DRIVE PATHS
-----------
Source: /Volumes/Working HD
Destination: /Volumes/Luke's HD

Replace with your actual drive names as needed.