import os
import datetime

# Set the directory you want to scan
SCAN_DIR = os.path.abspath(os.path.dirname(__file__))

# Set the time window for 'evening' (e.g., 16:00 to 23:59)
EVENING_START = datetime.time(16, 0, 0)
EVENING_END = datetime.time(23, 59, 59)

# Get today's date
TODAY = datetime.date.today()

modified_files = []

for root, dirs, files in os.walk(SCAN_DIR):
    for file in files:
        file_path = os.path.join(root, file)
        try:
            mtime = os.path.getmtime(file_path)
            mtime_dt = datetime.datetime.fromtimestamp(mtime)
            if mtime_dt.date() == TODAY and EVENING_START <= mtime_dt.time() <= EVENING_END:
                modified_files.append((file_path, mtime_dt.strftime('%H:%M:%S')))
        except Exception as e:
            pass

if modified_files:
    print('Files modified today evening:')
    for path, time in modified_files:
        print(f'{path} (at {time})')
else:
    print('No files modified today evening.')
