import os
import datetime
import threading
import json
from tkinter import messagebox

class LogManager:
    """Manages persistent logging of temperature data with .logs files"""
    def __init__(self):
        # Condition 1: Daily logs in "Daily logs" folder
        self.daily_logs_dir = "Daily logs"
        self.current_log_file = None
        self.log_buffer = []
        self.last_log_index = 0
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging infrastructure with Daily logs folder"""
        # Create Daily logs directory if it doesn't exist
        if not os.path.exists(self.daily_logs_dir):
            os.makedirs(self.daily_logs_dir)
            print(f"✅ Created Daily logs directory: {self.daily_logs_dir}")
        
        # Create or get current log file
        self.current_log_file = self.get_current_log_file()
        print(f"✅ Logging to: {self.current_log_file}")
    
    def get_current_log_file(self):
        """Get the current log file path based on current date"""
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.daily_logs_dir, f"temperature_logs_{current_date}.logs")
    
    def log_temperature(self, temp_type, value, message=""):
        """Log temperature data with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create log entry
        if message:
            log_entry = f"[{timestamp}] {message}"
        else:
            log_entry = f"[{timestamp}] {temp_type}: {value}°C"
        
        # Add to buffer for live display
        self.log_buffer.append(log_entry)
        
        # Persist to file (non-blocking)
        threading.Thread(target=self._write_to_file, 
                        args=(log_entry,),
                        daemon=True).start()
        
        print(log_entry)  # Also print to console
    
    def _write_to_file(self, log_entry):
        """Write log entry to file in a separate thread"""
        try:
            # Check if we need to rotate to a new daily file
            current_file = self.get_current_log_file()
            if current_file != self.current_log_file:
                self.current_log_file = current_file
            
            # Use UTF-8 encoding with error handling
            with open(self.current_log_file, 'a', encoding='utf-8', errors='replace') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def get_all_logs(self):
        """Get all logs from all .logs files"""
        all_logs = []
        
        try:
            # Check if Daily logs directory exists
            if not os.path.exists(self.daily_logs_dir):
                print(f"⚠️ Daily logs directory '{self.daily_logs_dir}' not found")
                return all_logs
            
            # Get all temperature_logs_*.logs files in the Daily logs directory
            log_files = []
            try:
                log_files = [f for f in os.listdir(self.daily_logs_dir) 
                           if f.startswith('temperature_logs_') and f.endswith('.logs')]
            except FileNotFoundError:
                print(f"❌ Directory '{self.daily_logs_dir}' not found")
                return all_logs
            except PermissionError:
                print(f"❌ Permission denied accessing '{self.daily_logs_dir}'")
                return all_logs
            
            if not log_files:
                print("ℹ️ No log files found in Daily logs directory")
                return all_logs
            
            log_files.sort()  # Sort by filename (which includes date)
            
            # Read all log files with multiple encoding attempts
            for log_file in log_files:
                log_path = os.path.join(self.daily_logs_dir, log_file)
                file_logs = self._read_log_file_with_encoding(log_path)
                if file_logs:
                    all_logs.extend(file_logs)
                    print(f"📖 Read {len(file_logs)} entries from {log_file}")
            
            print(f"📊 Total logs loaded: {len(all_logs)} entries")
        
        except Exception as e:
            print(f"❌ Error reading Daily logs directory: {e}")
        
        return all_logs
    
    def _read_log_file_with_encoding(self, file_path):
        """Read log file trying multiple encodings to handle encoding issues"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    logs = f.readlines()
                    # Filter out empty lines and clean the logs
                    cleaned_logs = [log.strip() for log in logs if log.strip()]
                    return cleaned_logs
            except UnicodeDecodeError:
                print(f"⚠️ Encoding {encoding} failed for {os.path.basename(file_path)}, trying next...")
                continue
            except Exception as e:
                print(f"⚠️ Error reading {os.path.basename(file_path)} with {encoding}: {e}")
                continue
        
        print(f"❌ All encoding attempts failed for {os.path.basename(file_path)}")
        return []
    
    def get_new_logs(self):
        """Get new logs since last check"""
        current_logs = self.get_all_logs()
        new_logs = current_logs[self.last_log_index:]
        self.last_log_index = len(current_logs)
        return new_logs
    
    def get_logs_for_date_range(self, start_date, end_date):
        """Get logs for a specific date range"""
        logs = []
        
        try:
            # Check if directory exists
            if not os.path.exists(self.daily_logs_dir):
                print(f"❌ Daily logs directory '{self.daily_logs_dir}' not found")
                return logs
            
            # Generate all dates in the range
            current_date = start_date
            while current_date <= end_date:
                log_file = os.path.join(self.daily_logs_dir, f"temperature_logs_{current_date.strftime('%Y-%m-%d')}.logs")
                
                if os.path.exists(log_file):
                    file_logs = self._read_log_file_with_encoding(log_file)
                    if file_logs:
                        logs.extend(file_logs)
                        print(f"📖 Read {len(file_logs)} entries from {os.path.basename(log_file)}")
                    else:
                        print(f"⚠️ No readable content in: {os.path.basename(log_file)}")
                else:
                    print(f"ℹ️ No log file for date: {current_date}")
                
                current_date += datetime.timedelta(days=1)
            
            print(f"📊 Found {len(logs)} total log entries for date range {start_date} to {end_date}")
        
        except Exception as e:
            print(f"❌ Error reading logs for date range: {e}")
        
        return logs

    def get_logs_for_time_range(self, start_datetime, end_datetime):
        """Get logs for a specific time range"""
        logs = []
        
        try:
            # Check if directory exists
            if not os.path.exists(self.daily_logs_dir):
                print(f"❌ Daily logs directory '{self.daily_logs_dir}' not found")
                return logs
            
            # Generate all dates in the range
            current_date = start_datetime.date()
            end_date = end_datetime.date()
            
            while current_date <= end_date:
                log_file = os.path.join(self.daily_logs_dir, f"temperature_logs_{current_date.strftime('%Y-%m-%d')}.logs")
                
                if os.path.exists(log_file):
                    file_logs = self._read_log_file_with_encoding(log_file)
                    if file_logs:
                        # Filter logs by time range
                        for log_entry in file_logs:
                            try:
                                # Extract timestamp from log entry
                                timestamp_str = log_entry.split(']')[0][1:]
                                log_datetime = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                                
                                # Check if log datetime is within the specified range
                                if start_datetime <= log_datetime <= end_datetime:
                                    logs.append(log_entry)
                            except ValueError:
                                # Skip entries with invalid timestamps
                                continue
                        
                        print(f"📖 Filtered entries from {os.path.basename(log_file)}")
                    else:
                        print(f"⚠️ No readable content in: {os.path.basename(log_file)}")
                else:
                    print(f"ℹ️ No log file for date: {current_date}")
                
                current_date += datetime.timedelta(days=1)
            
            print(f"📊 Found {len(logs)} total log entries for time range {start_datetime} to {end_datetime}")
        
        except Exception as e:
            print(f"❌ Error reading logs for time range: {e}")
        
        return logs
    
    def export_logs_to_file(self, start_date, end_date):
        """Export logs to .logs file in Downloads folder only"""
        logs = self.get_logs_for_date_range(start_date, end_date)
        
        if not logs:
            print("❌ No logs to export")
            messagebox.showinfo("No Data", "No logs found to export for the specified date range.")
            return False
        
        try:
            # Create filename with date range for EXPORT file
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            if start_str == end_str:
                export_filename = f"temperature_export_{start_str}.logs"
            else:
                export_filename = f"temperature_export_{start_str}_to_{end_str}.logs"
            
            # Export only to Downloads folder
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", export_filename)
            
            # Use UTF-8 encoding for export
            with open(downloads_path, 'w', encoding='utf-8') as f:
                f.write("# Temperature Logs Export\n")
                f.write(f"# Date Range: {start_str} to {end_str}\n")
                f.write(f"# Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# Format: [TIMESTAMP] LOG_ENTRY\n")
                f.write("# Source: Storage Temperature Monitor\n")
                f.write("=" * 60 + "\n")
                for log_entry in logs:
                    f.write(log_entry + "\n")
            
            print(f"✅ Daily logs stored in: {self.daily_logs_dir}/")
            print(f"✅ Export file created: {downloads_path}")
            print(f"✅ Exported {len(logs)} log entries")
            return True
        
        except Exception as e:
            print(f"❌ Error exporting logs: {e}")
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")
            return False

    def export_logs_to_file_with_time_range(self, start_datetime, end_datetime):
        """Export logs with time range to .logs file in Downloads folder"""
        logs = self.get_logs_for_time_range(start_datetime, end_datetime)
        
        if not logs:
            print("❌ No logs to export")
            messagebox.showinfo("No Data", "No logs found to export for the specified time range.")
            return False
        
        try:
            # Create filename with time range for EXPORT file
            start_str = start_datetime.strftime("%Y-%m-%d_%H-%M")
            end_str = end_datetime.strftime("%Y-%m-%d_%H-%M")
            
            export_filename = f"temperature_export_{start_str}_to_{end_str}.logs"
            
            # Export only to Downloads folder
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", export_filename)
            
            # Use UTF-8 encoding for export
            with open(downloads_path, 'w', encoding='utf-8') as f:
                f.write("# Temperature Logs Export\n")
                f.write(f"# Time Range: {start_datetime.strftime('%Y-%m-%d %H:%M')} to {end_datetime.strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"# Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# Format: [TIMESTAMP] LOG_ENTRY\n")
                f.write("# Source: Storage Temperature Monitor\n")
                f.write("=" * 60 + "\n")
                for log_entry in logs:
                    f.write(log_entry + "\n")
            
            print(f"✅ Daily logs stored in: {self.daily_logs_dir}/")
            print(f"✅ Export file created: {downloads_path}")
            print(f"✅ Exported {len(logs)} log entries")
            return True
        
        except Exception as e:
            print(f"❌ Error exporting logs: {e}")
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")
            return False