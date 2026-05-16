import os
import datetime

# Set the directory you want to scan
SCAN_DIR = os.path.abspath(os.path.dirname(__file__))

# Set the time window for 'evening' (e.g., 16:00 to now)
EVENING_START = datetime.time(16, 0, 0)
EVENING_END = datetime.datetime.now().time()

# Get today's date
TODAY = datetime.date.today()

code_extensions = ['.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.yaml', '.yml']
modified_code_files = []

for root, dirs, files in os.walk(SCAN_DIR):
    for file in files:
        if any(file.lower().endswith(ext) for ext in code_extensions):
            file_path = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(file_path)
                mtime_dt = datetime.datetime.fromtimestamp(mtime)
                if mtime_dt.date() == TODAY and EVENING_START <= mtime_dt.time() <= EVENING_END:
                    modified_code_files.append((file_path, mtime_dt.strftime('%H:%M:%S')))
            except Exception as e:
                pass

if modified_code_files:
    print('Code files modified today evening:')
    for path, time in modified_code_files:
        print(f'{path} (at {time})')
else:
    print('No code files modified today evening.')
