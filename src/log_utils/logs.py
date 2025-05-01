import os
import shutil
import logging
from datetime import datetime

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class LogHandler:
    def __init__(self, log_dir='./log'):
        self.log_dir = log_dir
        self.current_month_year = datetime.now().strftime('%b_%y')  # e.g., 'Apr_25'
        self.log_file_path = os.path.join(self.log_dir, f"{self.current_month_year}.log")
        
        # Make sure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _reset_logs_if_new_month(self):
        # Check current month
        now = datetime.now().strftime('%b_%y')
        if now != self.current_month_year:
            # New month detected
            logger.info("New month detected. Cleaning up logs...")
            shutil.rmtree(self.log_dir)  # Remove the entire log directory
            os.makedirs(self.log_dir, exist_ok=True)  # Recreate empty log directory
            
            # Update month-year and file path
            self.current_month_year = now
            self.log_file_path = os.path.join(self.log_dir, f"{self.current_month_year}.log")

    def store_log(self, log_message):
        # Check if it's a new month and reset if needed
        self._reset_logs_if_new_month()
        
        # Append the log to the file
        with open(self.log_file_path, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {log_message}\n")