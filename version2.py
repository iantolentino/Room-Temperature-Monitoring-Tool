import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import psutil
import winsound
from plyer import notification
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import csv
import pandas as pd
from tkinter import scrolledtext
import subprocess
import sys
import traceback
import ctypes
import tkinter.filedialog as filedialog


class ResponsiveDesign:
    """Handles responsive design and screen adaptation"""
    
    def __init__(self, root):
        self.root = root
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.setup_fullscreen_geometry()
        
    def setup_fullscreen_geometry(self):
        """Set up fullscreen window using geometry and zoomed state"""
        # Condition 2: Improved responsive sizing for all devices
        # Use percentage of screen size for better responsiveness
        width_percentage = 0.95  # Use 95% of screen width
        height_percentage = 0.95  # Use 95% of screen height
        
        window_width = int(self.screen_width * width_percentage)
        window_height = int(self.screen_height * height_percentage)
        
        # Center window on screen
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.state('normal')  # Changed from 'zoomed' for better control
        self.root.minsize(800, 600)  # Reduced minimum size for smaller screens
        
    def get_scaling_factors(self):
        """Calculate scaling factors based on screen resolution"""
        # Condition 2: Improved scaling for different screen sizes
        base_width = 1366  # Lower base resolution for better compatibility
        base_height = 768
        
        width_scale = self.screen_width / base_width
        height_scale = self.screen_height / base_height
        
        # Use dynamic scaling based on screen size
        if self.screen_width < 1280:  # Small screens
            scale_factor = min(width_scale, height_scale, 0.9)
        elif self.screen_width < 1920:  # Medium screens
            scale_factor = min(width_scale, height_scale, 1.1)
        else:  # Large screens
            scale_factor = min(width_scale, height_scale, 1.3)
        
        # Ensure minimum scaling
        scale_factor = max(0.8, scale_factor)
        
        return {
            'font_scale': scale_factor,
            'padding_scale': scale_factor * 0.9,
            'widget_scale': scale_factor,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height
        }

class ThemeManager:
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "dark": {
                'primary': '#3b82f6',
                'secondary': '#60a5fa',
                'accent': '#93c5fd',
                'background': '#0f172a',
                'surface': '#1e293b',
                'card_bg': '#1e293b',
                'text_primary': '#f8fafc',
                'text_secondary': '#cbd5e1',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'border': '#334155',
                'hover': '#374151',
                'grid_color': '#2d3748',
                'input_bg': '#1e293b',
                'input_fg': '#f8fafc',
            },
            "light": {
                'primary': '#2563eb',
                'secondary': '#3b82f6',
                'accent': '#60a5fa',
                'background': '#f8fafc',
                'surface': '#ffffff',
                'card_bg': '#ffffff',
                'text_primary': '#1e293b',
                'text_secondary': '#475569',
                'success': '#059669',
                'warning': '#d97706',
                'error': '#dc2626',
                'border': '#e2e8f0',
                'hover': '#f1f5f9',
                'grid_color': '#e2e8f0',
                'input_bg': '#ffffff',
                'input_fg': '#1e293b',
            }
        }
    
    def get_theme(self):
        return self.themes[self.current_theme]
    
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        return self.get_theme()
    
    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
        return self.get_theme()

class ResponsiveGradientBackground:
    def __init__(self, canvas, width, height, theme_colors):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.theme_colors = theme_colors
        self.gradient_ids = []
        self.create_responsive_background()
        
    def create_responsive_background(self):
        for grad_id in self.gradient_ids:
            self.canvas.delete(grad_id)
        self.gradient_ids = []
        
        self.canvas.configure(bg=self.theme_colors['background'])
        
        if self.theme_colors['background'] == '#f8fafc':
            self.create_light_background()
        else:
            self.create_dark_background()
    
    def create_light_background(self):
        colors = [
            self.theme_colors['background'],
            '#f1f5f9',
            self.theme_colors['background']
        ]
        
        for i in range(3):
            color_index = i % len(colors)
            grad_id = self.canvas.create_rectangle(
                0, i * self.height // 3,
                self.width, (i + 1) * self.height // 3,
                fill=colors[color_index],
                outline='',
                width=0
            )
            self.gradient_ids.append(grad_id)
        
        self.create_subtle_grid()
        
    def create_dark_background(self):
        colors = [
            self.theme_colors['background'],
            '#1e293b',
            '#334155',
            self.theme_colors['background']
        ]
        
        for i in range(4):
            color_index = i % len(colors)
            grad_id = self.canvas.create_rectangle(
                0, i * self.height // 4,
                self.width, (i + 1) * self.height // 4,
                fill=colors[color_index],
                outline='',
                width=0
            )
            self.gradient_ids.append(grad_id)
        
        self.create_subtle_grid()
        self.create_minimal_decorations()
    
    def create_subtle_grid(self):
        grid_color = self.theme_colors['grid_color']
        
        # Dynamic spacing based on window size
        spacing = max(50, min(150, self.width // 20))
        
        if self.width > 400:
            for x in range(0, self.width, spacing):
                line_id = self.canvas.create_line(
                    x, 0, x, self.height,
                    fill=grid_color, 
                    width=0.5, 
                    dash=(2, 4)
                )
                self.gradient_ids.append(line_id)
        
        if self.height > 300:
            for y in range(0, self.height, spacing):
                line_id = self.canvas.create_line(
                    0, y, self.width, y,
                    fill=grid_color, 
                    width=0.5, 
                    dash=(2, 4)
                )
                self.gradient_ids.append(line_id)
    
    def create_minimal_decorations(self):
        if self.theme_colors['background'] == '#f8fafc':
            accent_color = self.theme_colors['accent']
            for i in range(3):
                size = 40 + i * 10
                x = self.width * (i % 3) / 3 + 30
                y = self.height * (i // 3) / 2 + 30
                
                circle_id = self.canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill='', 
                    outline=accent_color,
                    width=0.5,
                    dash=(4, 8)
                )
                self.gradient_ids.append(circle_id)
        else:
            accent_color = self.theme_colors['accent']
            for i in range(4):
                size = 30 + i * 15
                x = self.width * (i % 4) / 4 + 50
                y = self.height * (i // 4) / 2 + 50
                
                circle_id = self.canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill='', 
                    outline=accent_color,
                    width=1,
                    dash=(6, 10)
                )
                self.gradient_ids.append(circle_id)
    
    def update_theme(self, theme_colors):
        self.theme_colors = theme_colors
        self.create_responsive_background()

class LogManager:
    def __init__(self):
        self.daily_logs_dir = "Daily logs"
        self.current_log_file = None
        self.log_buffer = []
        self.last_log_index = 0
        self.setup_logging()
    
    def setup_logging(self):
        if not os.path.exists(self.daily_logs_dir):
            os.makedirs(self.daily_logs_dir)
            print(f"✅ Created Daily logs directory: {self.daily_logs_dir}")
        
        self.current_log_file = self.get_current_log_file()
        print(f"✅ Logging to: {self.current_log_file}")
    
    def get_current_log_file(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.daily_logs_dir, f"temperature_logs_{current_date}.logs")
    
    def log_temperature(self, temp_type, value, message=""):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if message:
            log_entry = f"[{timestamp}] {message}"
        else:
            log_entry = f"[{timestamp}] {temp_type}: {value}°C"
        
        self.log_buffer.append(log_entry)
        
        threading.Thread(target=self._write_to_file, 
                        args=(log_entry,),
                        daemon=True).start()
        
        print(log_entry)
    
    def _write_to_file(self, log_entry):
        try:
            current_file = self.get_current_log_file()
            if current_file != self.current_log_file:
                self.current_log_file = current_file
            
            with open(self.current_log_file, 'a', encoding='utf-8', errors='replace') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def get_all_logs(self):
        all_logs = []
        
        try:
            if not os.path.exists(self.daily_logs_dir):
                print(f"⚠️ Daily logs directory '{self.daily_logs_dir}' not found")
                return all_logs
            
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
                
            log_files.sort()
            
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
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    logs = f.readlines()
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
        current_logs = self.get_all_logs()
        new_logs = current_logs[self.last_log_index:]
        self.last_log_index = len(current_logs)
        return new_logs
    
    def get_logs_for_date_range(self, start_date, end_date):
        logs = []
        
        try:
            if not os.path.exists(self.daily_logs_dir):
                print(f"❌ Daily logs directory '{self.daily_logs_dir}' not found")
                return logs
            
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
        logs = []
        
        try:
            if not os.path.exists(self.daily_logs_dir):
                print(f"❌ Daily logs directory '{self.daily_logs_dir}' not found")
                return logs
            
            current_date = start_datetime.date()
            end_date = end_datetime.date()
            
            while current_date <= end_date:
                log_file = os.path.join(self.daily_logs_dir, f"temperature_logs_{current_date.strftime('%Y-%m-%d')}.logs")
                
                if os.path.exists(log_file):
                    file_logs = self._read_log_file_with_encoding(log_file)
                    if file_logs:
                        for log_entry in file_logs:
                            try:
                                timestamp_str = log_entry.split(']')[0][1:]
                                log_datetime = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                                
                                if start_datetime <= log_datetime <= end_datetime:
                                    logs.append(log_entry)
                            except ValueError:
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
        logs = self.get_logs_for_date_range(start_date, end_date)
        
        if not logs:
            print("❌ No logs to export")
            messagebox.showinfo("No Data", "No logs found to export for the specified date range.")
            return False
        
        try:
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            if start_str == end_str:
                export_filename = f"temperature_export_{start_str}.logs"
            else:
                export_filename = f"temperature_export_{start_str}_to_{end_str}.logs"
            
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", export_filename)
            
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
        logs = self.get_logs_for_time_range(start_datetime, end_datetime)
        
        if not logs:
            print("❌ No logs to export")
            messagebox.showinfo("No Data", "No logs found to export for the specified time range.")
            return False
        
        try:
            start_str = start_datetime.strftime("%Y-%m-%d_%H-%M")
            end_str = end_datetime.strftime("%Y-%m-%d_%H-%M")
            
            export_filename = f"temperature_export_{start_str}_to_{end_str}.logs"
            
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", export_filename)
            
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

class LiveLogWindow:
    def __init__(self, parent, log_manager, theme_manager, responsive_design):
        self.parent = parent
        self.log_manager = log_manager
        self.theme_manager = theme_manager
        self.responsive_design = responsive_design
        self.colors = self.theme_manager.get_theme()
        self.window = None
        self.is_running = True
        self.create_window()
        
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Live Temperature Log")
        
        # Condition 2: Improved responsive sizing for modal windows
        screen_info = self.responsive_design.get_scaling_factors()
        window_width = min(1000, int(screen_info['screen_width'] * 0.85))
        window_height = min(700, int(screen_info['screen_height'] * 0.8))
        self.window.geometry(f"{window_width}x{window_height}")
        
        self.window.minsize(600, 400)  # Reduced minimum size for smaller screens
        
        x = (screen_info['screen_width'] - window_width) // 2
        y = (screen_info['screen_height'] - window_height) // 2
        self.window.geometry(f"+{x}+{y}")
        
        if self.colors['background'] == '#0f172a':
            bg_color = '#1e293b'
            text_bg = '#1e293b'
        else:
            bg_color = '#ffffff'
            text_bg = '#ffffff'
            
        self.window.configure(bg=bg_color)
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        
        self.window.transient(self.parent)
        self.window.grab_set()
        
        header_frame = ttk.Frame(self.window, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=15)
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="Live Temperature Log", 
                               background=bg_color,
                               foreground=self.colors['text_primary'],
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, sticky='w')
        
        button_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        button_frame.grid(row=0, column=1, sticky='e')
        
        search_export_button = ttk.Button(button_frame, text="Search & Export by Time Range", 
                                         command=self.show_time_search_modal,
                                         style='Secondary.TButton')
        search_export_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.status_var = tk.StringVar(value="Showing: Live Logs")
        status_label = ttk.Label(header_frame, textvariable=self.status_var,
                                background=bg_color,
                                foreground=self.colors['text_secondary'],
                                font=("Segoe UI", 9))
        status_label.grid(row=1, column=0, sticky='w', pady=(5, 0))
        
        log_frame = ttk.Frame(self.window, style='Modern.TFrame')
        log_frame.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=120,
            height=30,
            bg=text_bg,
            fg=self.colors['text_primary'],
            font=("Consolas", 9),
            insertbackground=self.colors['text_primary'],
            state='disabled'
        )
        self.log_text.grid(row=0, column=0, sticky='nsew')
        
        self.refresh_log_display()
        self.update_live_log()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def show_time_search_modal(self):
        TimeRangeSearchWindow(self.window, self.log_manager, self.theme_manager, self.responsive_design)
    
    def refresh_log_display(self):
        logs = self.log_manager.get_all_logs()
        
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        
        if logs:
            for log_entry in logs[-1000:]:
                self.log_text.insert(tk.END, log_entry + "\n")
            
            self.log_text.see(tk.END)
        else:
            self.log_text.insert(tk.END, "No logs available yet...\n")
        
        self.log_text.config(state='disabled')
    
    def update_live_log(self):
        if self.is_running and self.window.winfo_exists():
            new_logs = self.log_manager.get_new_logs()
            
            if new_logs:
                self.log_text.config(state='normal')
                
                for log_entry in new_logs:
                    self.log_text.insert(tk.END, log_entry + "\n")
                
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
            
            self.window.after(1000, self.update_live_log)
    
    def on_close(self):
        self.is_running = False
        self.window.destroy()

class TimeRangeSearchWindow:
    def __init__(self, parent, log_manager, theme_manager, responsive_design):
        self.parent = parent
        self.log_manager = log_manager
        self.theme_manager = theme_manager
        self.responsive_design = responsive_design
        self.colors = self.theme_manager.get_theme()
        self.window = None
        self.current_logs = []
        self.create_window()
        
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Search and Export Logs by Time Range")
        
        # Condition 2: Improved responsive sizing for modal windows
        screen_info = self.responsive_design.get_scaling_factors()
        window_width = min(1100, int(screen_info['screen_width'] * 0.9))
        window_height = min(700, int(screen_info['screen_height'] * 0.85))
        self.window.geometry(f"{window_width}x{window_height}")
        
        self.window.minsize(700, 500)  # Reduced minimum size
        
        x = (screen_info['screen_width'] - window_width) // 2
        y = (screen_info['screen_height'] - window_height) // 2
        self.window.geometry(f"+{x}+{y}")
        
        if self.colors['background'] == '#0f172a':
            bg_color = '#1e293b'
            text_bg = '#1e293b'
        else:
            bg_color = '#ffffff'
            text_bg = '#ffffff'
            
        self.window.configure(bg=bg_color)
        
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        
        header_frame = ttk.Frame(self.window, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=15)
        header_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="Search and Export Logs by Time Range", 
                               background=bg_color,
                               foreground=self.colors['text_primary'],
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, sticky='w')
        
        controls_frame = ttk.Frame(self.window, style='Modern.TFrame')
        controls_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)
        
        datetime_frame = ttk.Frame(controls_frame, style='Modern.TFrame')
        datetime_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        datetime_frame.columnconfigure(1, weight=1)
        datetime_frame.columnconfigure(3, weight=1)
        
        start_frame = ttk.Frame(datetime_frame, style='Modern.TFrame')
        start_frame.grid(row=0, column=0, sticky='w', padx=(0, 20))
        
        ttk.Label(start_frame, text="Start Date & Time:", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w', columnspan=2)
        
        ttk.Label(start_frame, text="Date (YYYY-MM-DD):", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 8)).grid(row=1, column=0, sticky='w', pady=(5, 2))
        
        self.start_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        start_date_entry = ttk.Entry(start_frame, textvariable=self.start_date_var, width=12, font=('Segoe UI', 8))
        start_date_entry.grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        ttk.Label(start_frame, text="Time (HH:MM):", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 8)).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(5, 2))
        
        self.start_time_var = tk.StringVar(value="00:00")
        start_time_entry = ttk.Entry(start_frame, textvariable=self.start_time_var, width=8, font=('Segoe UI', 8))
        start_time_entry.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=(0, 5))
        
        end_frame = ttk.Frame(datetime_frame, style='Modern.TFrame')
        end_frame.grid(row=0, column=1, sticky='w', padx=(0, 20))
        
        ttk.Label(end_frame, text="End Date & Time:", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w', columnspan=2)
        
        ttk.Label(end_frame, text="Date (YYYY-MM-DD):", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 8)).grid(row=1, column=0, sticky='w', pady=(5, 2))
        
        self.end_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        end_date_entry = ttk.Entry(end_frame, textvariable=self.end_date_var, width=12, font=('Segoe UI', 8))
        end_date_entry.grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        ttk.Label(end_frame, text="Time (HH:MM):", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 8)).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(5, 2))
        
        self.end_time_var = tk.StringVar(value="23:59")
        end_time_entry = ttk.Entry(end_frame, textvariable=self.end_time_var, width=8, font=('Segoe UI', 8))
        end_time_entry.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=(0, 5))
        
        quick_buttons_frame = ttk.Frame(datetime_frame, style='Modern.TFrame')
        quick_buttons_frame.grid(row=0, column=2, sticky='w')
        
        ttk.Label(quick_buttons_frame, text="Quick Ranges:", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w', columnspan=2)
        
        button_frame = ttk.Frame(quick_buttons_frame, style='Modern.TFrame')
        button_frame.grid(row=1, column=0, sticky='w', pady=(5, 0))
        
        ttk.Button(button_frame, text="Last Hour", 
                  command=lambda: self.set_quick_range(1),
                  style='Secondary.TButton', width=10).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(button_frame, text="Last 6 Hours", 
                  command=lambda: self.set_quick_range(6),
                  style='Secondary.TButton', width=10).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(button_frame, text="Last 24 Hours", 
                  command=lambda: self.set_quick_range(24),
                  style='Secondary.TButton', width=10).grid(row=0, column=2, padx=(0, 5))
        
        ttk.Button(button_frame, text="Today", 
                  command=self.set_today_range,
                  style='Secondary.TButton', width=10).grid(row=1, column=0, padx=(0, 5), pady=(5, 0))
        
        ttk.Button(button_frame, text="Yesterday", 
                  command=self.set_yesterday_range,
                  style='Secondary.TButton', width=10).grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        
        ttk.Button(button_frame, text="Last 7 Days", 
                  command=lambda: self.set_quick_range(7*24),
                  style='Secondary.TButton', width=10).grid(row=1, column=2, padx=(0, 5), pady=(5, 0))
        
        action_frame = ttk.Frame(controls_frame, style='Modern.TFrame')
        action_frame.grid(row=1, column=0, sticky='ew')
        action_frame.columnconfigure(0, weight=1)
        
        search_button = ttk.Button(action_frame, text="Search Logs", 
                                  command=self.search_logs,
                                  style='Primary.TButton')
        search_button.grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        self.export_button = ttk.Button(action_frame, text="Export Results", 
                                       command=self.export_logs,
                                       style='Secondary.TButton',
                                       state="disabled")
        self.export_button.grid(row=0, column=1, sticky='w', padx=(0, 10))
        
        self.graph_button = ttk.Button(action_frame, text="Show History Graph", 
                                      command=self.show_history_graph,
                                      style='Secondary.TButton',
                                      state="disabled")
        self.graph_button.grid(row=0, column=2, sticky='w')
        
        info_frame = ttk.Frame(controls_frame, style='Modern.TFrame')
        info_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        self.results_var = tk.StringVar(value="Enter time range and click 'Search Logs'")
        results_label = ttk.Label(info_frame, textvariable=self.results_var,
                                background=bg_color,
                                foreground=self.colors['text_secondary'],
                                font=("Segoe UI", 9))
        results_label.pack(anchor='w')
        
        content_frame = ttk.Frame(self.window, style='Modern.TFrame')
        content_frame.grid(row=2, column=0, sticky='nsew', padx=15, pady=(0, 15))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            width=100,
            height=25,
            bg=text_bg,
            fg=self.colors['text_primary'],
            font=("Consolas", 9),
            insertbackground=self.colors['text_primary'],
            state='disabled'
        )
        self.log_text.grid(row=0, column=0, sticky='nsew')
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def set_quick_range(self, hours):
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=hours)
        
        self.start_date_var.set(start_time.strftime("%Y-%m-%d"))
        self.start_time_var.set(start_time.strftime("%H:%M"))
        self.end_date_var.set(end_time.strftime("%Y-%m-%d"))
        self.end_time_var.set(end_time.strftime("%H:%M"))
    
    def set_today_range(self):
        today = datetime.datetime.now()
        self.start_date_var.set(today.strftime("%Y-%m-%d"))
        self.start_time_var.set("00:00")
        self.end_date_var.set(today.strftime("%Y-%m-%d"))
        self.end_time_var.set("23:59")
    
    def set_yesterday_range(self):
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        self.start_date_var.set(yesterday.strftime("%Y-%m-%d"))
        self.start_time_var.set("00:00")
        self.end_date_var.set(yesterday.strftime("%Y-%m-%d"))
        self.end_time_var.set("23:59")
    
    def search_logs(self):
        try:
            start_datetime_str = f"{self.start_date_var.get()} {self.start_time_var.get()}"
            end_datetime_str = f"{self.end_date_var.get()} {self.end_time_var.get()}"
            
            try:
                start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
                end_datetime = datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
                
                if start_datetime > end_datetime:
                    messagebox.showerror("Error", "Start time cannot be after end time")
                    return
                    
            except ValueError:
                messagebox.showerror("Error", "Invalid datetime format. Please use YYYY-MM-DD for date and HH:MM for time")
                return
            
            self.current_logs = self.log_manager.get_logs_for_time_range(start_datetime, end_datetime)
            
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            
            if self.current_logs:
                for log_entry in self.current_logs:
                    self.log_text.insert(tk.END, log_entry + "\n")
                
                self.log_text.see(1.0)
                
                log_count = len(self.current_logs)
                self.results_var.set(f"Found {log_count} log entries from {start_datetime_str} to {end_datetime_str}")
                
                self.export_button.config(state="normal")
                self.graph_button.config(state="normal")
                
            else:
                self.log_text.insert(tk.END, "No logs found for the specified time range.\n")
                self.results_var.set("No logs found for the specified time range")
                self.export_button.config(state="disabled")
                self.graph_button.config(state="disabled")
            
            self.log_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search logs: {str(e)}")
    
    def show_history_graph(self):
        if not self.current_logs:
            messagebox.showinfo("No Data", "No logs to generate graph. Please search for logs first.")
            return
        
        try:
            start_datetime_str = f"{self.start_date_var.get()} {self.start_time_var.get()}"
            end_datetime_str = f"{self.end_date_var.get()} {self.end_time_var.get()}"
            
            try:
                start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
                end_datetime = datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid datetime format in fields")
                return
            
            SearchResultModal(self.window, start_datetime, end_datetime, self.current_logs, self.theme_manager, self.responsive_design)
            
        except Exception as e:
            messagebox.showerror("Graph Error", f"Failed to generate graph: {str(e)}")
    
    def export_logs(self):
        if not self.current_logs:
            messagebox.showinfo("No Data", "No logs to export. Please search for logs first.")
            return
        
        try:
            start_datetime_str = f"{self.start_date_var.get()} {self.start_time_var.get()}"
            end_datetime_str = f"{self.end_date_var.get()} {self.end_time_var.get()}"
            
            try:
                start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
                end_datetime = datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid datetime format in fields")
                return
            
            success = self.log_manager.export_logs_to_file_with_time_range(start_datetime, end_datetime)
            
            if success:
                messagebox.showinfo("Export Successful", 
                                  "Logs exported successfully to Downloads folder!")
            else:
                messagebox.showinfo("Export Failed", "Failed to export logs")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")
    
    def on_close(self):
        self.window.destroy()

class SearchResultModal:
    """Modal window to display search results with time range and history graph"""
    def __init__(self, parent, start_datetime, end_datetime, logs, theme_manager, responsive_design):
        self.parent = parent
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.logs = logs
        self.theme_manager = theme_manager
        self.responsive_design = responsive_design
        self.colors = self.theme_manager.get_theme()
        self.window = None
        self.create_modal()
    
    def create_modal(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Search Results - Temperature History")
        
        # Condition 2: Improved responsive sizing for modal windows
        screen_info = self.responsive_design.get_scaling_factors()
        window_width = min(1200, int(screen_info['screen_width'] * 0.92))
        window_height = min(800, int(screen_info['screen_height'] * 0.85))
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.minsize(800, 500)  # Reduced minimum size
        
        x = (screen_info['screen_width'] - window_width) // 2
        y = (screen_info['screen_height'] - window_height) // 2
        self.window.geometry(f"+{x}+{y}")
        
        if self.colors['background'] == '#0f172a':
            bg_color = '#1e293b'
            text_bg = '#1e293b'
        else:
            bg_color = '#ffffff'
            text_bg = '#ffffff'
            
        self.window.configure(bg=bg_color)
        
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        
        header_frame = ttk.Frame(self.window, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=20)
        header_frame.columnconfigure(0, weight=1)
        
        title_text = f"Temperature History: {self.start_datetime.strftime('%Y-%m-%d %H:%M')} to {self.end_datetime.strftime('%Y-%m-%d %H:%M')}"
        title_label = ttk.Label(header_frame, text=title_text,
                               background=bg_color,
                               foreground=self.colors['text_primary'],
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, sticky='w')
        
        stats_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        stats_frame.grid(row=1, column=0, sticky='ew', pady=(10, 0))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        
        temperatures = self.parse_temperature_data()
        
        if temperatures:
            avg_temp = sum(temperatures) / len(temperatures)
            max_temp = max(temperatures)
            min_temp = min(temperatures)
            
            avg_frame = ttk.Frame(stats_frame, style='Card.TFrame', padding="10")
            avg_frame.grid(row=0, column=0, sticky='ew', padx=(0, 10))
            
            ttk.Label(avg_frame, text="Average Temp", 
                     background=self.colors['card_bg'],
                     foreground=self.colors['text_secondary'],
                     font=("Segoe UI", 9)).pack(anchor=tk.CENTER)
            ttk.Label(avg_frame, text=f"{avg_temp:.1f}°C", 
                     background=self.colors['card_bg'],
                     foreground=self.colors['primary'],
                     font=("Segoe UI", 14, "bold")).pack(anchor=tk.CENTER)
            
            max_frame = ttk.Frame(stats_frame, style='Card.TFrame', padding="10")
            max_frame.grid(row=0, column=1, sticky='ew', padx=5)
            
            ttk.Label(max_frame, text="Max Temp", 
                     background=self.colors['card_bg'],
                     foreground=self.colors['text_secondary'],
                     font=("Segoe UI", 9)).pack(anchor=tk.CENTER)
            ttk.Label(max_frame, text=f"{max_temp:.1f}°C", 
                     background=self.colors['card_bg'],
                     foreground=self.colors['error'],
                     font=("Segoe UI", 14, "bold")).pack(anchor=tk.CENTER)
            
            min_frame = ttk.Frame(stats_frame, style='Card.TFrame', padding="10")
            min_frame.grid(row=0, column=2, sticky='ew', padx=(10, 0))
            
            ttk.Label(min_frame, text="Min Temp", 
                     background=self.colors['card_bg'],
                     foreground=self.colors['text_secondary'],
                     font=("Segoe UI", 9)).pack(anchor=tk.CENTER)
            ttk.Label(min_frame, text=f"{min_temp:.1f}°C", 
                     background=self.colors['card_bg'],
                     foreground=self.colors['success'],
                     font=("Segoe UI", 14, "bold")).pack(anchor=tk.CENTER)
        
        content_frame = ttk.Frame(self.window, style='Modern.TFrame')
        content_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 20))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        self.setup_graph(content_frame)
        
        button_frame = ttk.Frame(self.window, style='Modern.TFrame')
        button_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=(0, 20))
        
        close_button = ttk.Button(button_frame, text="Close", 
                                 command=self.window.destroy,
                                 style='Primary.TButton')
        close_button.pack(side=tk.RIGHT)
        
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
    
    def parse_temperature_data(self):
        temperatures = []
        
        for log_entry in self.logs:
            if '°C' in log_entry:
                try:
                    temp_part = log_entry.split('°C')[0]
                    if ':' in temp_part:
                        temp_str = temp_part.split(':')[-1].strip()
                        try:
                            temperature = float(temp_str)
                            temperatures.append(temperature)
                        except ValueError:
                            continue
                except Exception:
                    continue
        
        return temperatures
    
    def setup_graph(self, parent):
        temperature_entries = []
        
        for log_entry in self.logs:
            if '°C' in log_entry:
                try:
                    timestamp_str = log_entry.split(']')[0][1:]
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    temp_part = log_entry.split('°C')[0]
                    if ':' in temp_part:
                        temp_str = temp_part.split(':')[-1].strip()
                        try:
                            temperature = float(temp_str)
                            temperature_entries.append({
                                'timestamp': timestamp,
                                'temperature': temperature,
                                'log_entry': log_entry
                            })
                        except ValueError:
                            continue
                except Exception:
                    continue
        
        if not temperature_entries:
            no_data_frame = ttk.Frame(parent, style='Modern.TFrame')
            no_data_frame.grid(row=0, column=0, sticky='nsew')
            no_data_frame.columnconfigure(0, weight=1)
            no_data_frame.rowconfigure(0, weight=1)
            
            no_data_label = ttk.Label(no_data_frame, 
                                    text="No temperature data found in the selected time range",
                                    background=self.colors['surface'],
                                    foreground=self.colors['text_secondary'],
                                    font=("Segoe UI", 14))
            no_data_label.grid(row=0, column=0, sticky='')
            return
        
        temperature_entries.sort(key=lambda x: x['timestamp'])
        
        # Condition 3: Filter to show only every 5 minutes interval for cleaner graph
        filtered_entries = self.filter_5_minute_intervals(temperature_entries)
        
        dates = [entry['timestamp'] for entry in filtered_entries]
        temperatures = [entry['temperature'] for entry in filtered_entries]
        
        self.fig = plt.figure(figsize=(12, 6))
        self.fig.patch.set_facecolor(self.colors['card_bg'])
        
        if self.colors['background'] == '#0f172a':
            text_color = 'white'
            grid_color = '#2d3748'
            line_color = '#60a5fa'
        else:
            text_color = 'black'
            grid_color = '#e2e8f0'
            line_color = '#2563eb'
        
        # Plot graph with filtered data (every 5 minutes)
        plt.plot(dates, temperatures, marker='o', label="Temperature (°C)", 
                color=line_color, linewidth=2, markersize=6)
        
        plt.xlabel("Date and Time", color=text_color, fontsize=12)
        plt.ylabel("Temperature (°C)", color=text_color, fontsize=12)
        
        # Add note about 5-minute intervals
        plt.title(f"Temperature History (5-minute intervals): {self.start_datetime.strftime('%Y-%m-%d %H:%M')} to {self.end_datetime.strftime('%Y-%m-%d %H:%M')}", 
                 color=text_color, fontsize=14, fontweight='bold', pad=15)
        
        plt.legend(fontsize=11, framealpha=0.9)
        plt.grid(True, linestyle="--", alpha=0.5, color=grid_color)
        
        # IMPROVED: Better x-axis formatting for history graph
        ax = plt.gca()
        
        if dates:
            # Calculate time range for better formatting
            time_range = (dates[-1] - dates[0]).total_seconds()
            
            if time_range <= 3600:  # 1 hour or less
                date_format = mdates.DateFormatter('%H:%M')
                plt.xticks(rotation=45, color=text_color)
                # Set ticks every 5 minutes
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
                
            elif time_range <= 86400:  # 1 day or less
                date_format = mdates.DateFormatter('%H:%M\n%m/%d')
                plt.xticks(rotation=0, color=text_color)
                # Set ticks every hour
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                
            elif time_range <= 604800:  # 1 week or less
                date_format = mdates.DateFormatter('%m/%d\n%H:%M')
                plt.xticks(rotation=45, color=text_color)
                # Set ticks every 6 hours
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
                
            else:  # More than 1 week
                date_format = mdates.DateFormatter('%Y-%m-%d\n%H:%M')
                plt.xticks(rotation=45, color=text_color)
                # Set ticks every day
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            
            ax.xaxis.set_major_formatter(date_format)
            
            # Set reasonable number of ticks
            if len(dates) > 20:
                # Use matplotlib's AutoDateLocator for optimal tick placement
                ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10))
        
        plt.yticks(color=text_color)
        
        ax.set_facecolor(self.colors['card_bg'])
        ax.spines['bottom'].set_color(text_color)
        ax.spines['top'].set_color(text_color)
        ax.spines['right'].set_color(text_color)
        ax.spines['left'].set_color(text_color)
        
        if temperatures:
            min_temp = min(temperatures)
            max_temp = max(temperatures)
            padding = (max_temp - min_temp) * 0.1 if max_temp > min_temp else 1
            plt.ylim(min_temp - padding, max_temp + padding)
            
            # Set y-axis ticks at reasonable intervals
            y_range = max_temp - min_temp
            if y_range <= 10:
                y_interval = 1
            elif y_range <= 20:
                y_interval = 2
            elif y_range <= 50:
                y_interval = 5
            else:
                y_interval = 10
            
            y_ticks = []
            y_val = round(min_temp / y_interval) * y_interval
            while y_val <= max_temp + padding:
                y_ticks.append(y_val)
                y_val += y_interval
            
            ax.set_yticks(y_ticks)
        
        if temperatures:
            avg_temp = sum(temperatures) / len(temperatures)
            max_temp_val = max(temperatures)
            min_temp_val = min(temperatures)
            
            plt.axhline(y=avg_temp, color=self.colors['accent'], linestyle=':', 
                       alpha=0.7, label=f'Average: {avg_temp:.1f}°C')
            plt.axhline(y=max_temp_val, color=self.colors['error'], linestyle=':', 
                       alpha=0.5, label=f'Max: {max_temp_val:.1f}°C')
            plt.axhline(y=min_temp_val, color=self.colors['success'], linestyle=':', 
                       alpha=0.5, label=f'Min: {min_temp_val:.1f}°C')
            
            plt.legend(fontsize=10, framealpha=0.9)
        
        # Add data point count annotation
        if filtered_entries:
            total_points = len(temperature_entries)
            filtered_points = len(filtered_entries)
            ax.annotate(f'Showing {filtered_points} of {total_points} data points\n(5-minute intervals)',
                       xy=(0.02, 0.98), xycoords='axes fraction',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                       fontsize=8,
                       ha='left', va='top')
        
        plt.tight_layout()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    
    def filter_5_minute_intervals(self, temperature_entries):
        """Filter temperature entries to show only every 5 minutes interval"""
        if not temperature_entries:
            return []
        
        filtered_entries = []
        last_selected_time = None
        
        for entry in temperature_entries:
            current_time = entry['timestamp']
            
            # Select first entry
            if last_selected_time is None:
                filtered_entries.append(entry)
                last_selected_time = current_time
            # Check if 5 minutes have passed since last selected entry
            elif (current_time - last_selected_time).total_seconds() >= 300:  # 300 seconds = 5 minutes
                filtered_entries.append(entry)
                last_selected_time = current_time
        
        # Always include the last entry
        if filtered_entries and temperature_entries:
            if filtered_entries[-1] != temperature_entries[-1]:
                filtered_entries.append(temperature_entries[-1])
        
        print(f"📊 Graph data: {len(temperature_entries)} total entries -> {len(filtered_entries)} entries (5-min intervals)")
        return filtered_entries

class StorageTemperatureReader:
    def __init__(self):
        self.wmi_available = False
        self.ohm_available = True
        self.initialize_wmi()
    
    def initialize_wmi(self):
        try:
            import wmi
            self.wmi_available = True
            print("✅ WMI support initialized")
            
            try:
                w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                sensors = w.Sensor()
                self.ohm_available = True
                print("✅ OpenHardwareMonitor detected and accessible")
                print(f"📊 Found {len(sensors)} sensors")
                
                temp_sensors = [s for s in sensors if s.SensorType == "Temperature"]
                print("🌡️ All temperature sensors:")
                for sensor in temp_sensors:
                    print(f"  - {sensor.Name}: {sensor.Value}°C (Parent: {sensor.Parent})")
                    
            except Exception as e:
                print("❌ OpenHardwareMonitor not detected or not running")
                print("💡 Please run OpenHardwareMonitor as Administrator")
                self.ohm_available = False
                
        except ImportError:
            print("❌ WMI not available - install: pip install wmi")
            self.wmi_available = False
            self.ohm_available = False
    
    def run_openhardware_monitor(self):
        """Condition 1: Run OpenHardwareMonitor automatically"""
        print("\n" + "="*60)
        print("STARTING OPENHARDWAREMONITOR")
        print("="*60)
        
        try:
            # Check if already running
            print("🔍 Checking if OpenHardwareMonitor is already running...")
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and 'OpenHardwareMonitor' in proc.info['name']:
                        print("✅ OpenHardwareMonitor is already running")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print("❌ OpenHardwareMonitor is not running")
            
            # Condition 1: Try the specific path first, then common locations
            specific_path = r"C:\Users\Admin\Documents\Projects\Room-Temperature-Monitoring-Tool-main\openhardwaremonitor-v0.9.6\OpenHardwareMonitor\OpenHardwareMonitor.exe"
            possible_paths = [
                specific_path,  # Your specific path
                "OpenHardwareMonitor.exe",
                os.path.join(os.getcwd(), "OpenHardwareMonitor.exe"),
                os.path.join(os.path.expanduser("~"), "Desktop", "OpenHardwareMonitor.exe"),
                os.path.join(os.path.expanduser("~"), "Downloads", "OpenHardwareMonitor.exe"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "OpenHardwareMonitor.exe"),
                r"C:\Program Files\OpenHardwareMonitor\OpenHardwareMonitor.exe",
                r"C:\Program Files (x86)\OpenHardwareMonitor\OpenHardwareMonitor.exe",
            ]
            
            found_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    found_path = path
                    print(f"✅ Found OpenHardwareMonitor.exe at: {path}")
                    break
            
            if not found_path:
                print("⚠️ OpenHardwareMonitor.exe not found in common locations")
                print("📁 Current directory:", os.getcwd())
                print("📁 Script directory:", os.path.dirname(os.path.abspath(__file__)))
                print("💡 Please ensure OpenHardwareMonitor.exe is available")
                return False
            
            # Try to run OpenHardwareMonitor
            print(f"🚀 Attempting to launch OpenHardwareMonitor: {found_path}")
            
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                
                if is_admin:
                    print("📝 Running as administrator")
                    try:
                        process = subprocess.Popen(
                            [found_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        print(f"✅ Process started with PID: {process.pid}")
                    except Exception as e:
                        print(f"❌ Failed to start process: {e}")
                        os.startfile(found_path)
                        print("✅ Started OpenHardwareMonitor using os.startfile")
                else:
                    print("⚠️ Not running as administrator")
                    print("💡 Note: OpenHardwareMonitor may require admin privileges")
                    
                    try:
                        process = subprocess.Popen(
                            [found_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        print(f"✅ Process started with PID: {process.pid}")
                    except Exception as e:
                        print(f"❌ Failed to start process: {e}")
                        os.startfile(found_path)
                        print("✅ Started OpenHardwareMonitor using os.startfile")
                
                # Wait for OpenHardwareMonitor to start
                print("⏳ Waiting for OpenHardwareMonitor to start...")
                time.sleep(5)
                
                # Verify it's running
                for _ in range(10):
                    for proc in psutil.process_iter(['name', 'pid']):
                        try:
                            if proc.info['name'] and 'OpenHardwareMonitor' in proc.info['name']:
                                print(f"✅ OpenHardwareMonitor is now running (PID: {proc.info['pid']})")
                                print("✅ Please ensure OpenHardwareMonitor is running as Administrator for full functionality")
                                return True
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    time.sleep(1)
                
                print("⚠️ OpenHardwareMonitor may have started but couldn't be verified")
                print("💡 Please check if OpenHardwareMonitor window opened")
                return True
                    
            except Exception as e:
                print(f"❌ Failed to launch OpenHardwareMonitor: {e}")
                traceback.print_exc()
                print("💡 Please run OpenHardwareMonitor manually as Administrator")
                return False
                
        except Exception as e:
            print(f"❌ Error in run_openhardware_monitor: {e}")
            traceback.print_exc()
            return False
    
    def _is_storage_sensor(self, sensor_name, parent_name):
        storage_keywords = [
            'hdd', 'ssd', 'disk', 'drive', 'nvme', 'sata', 
            'hard disk', 'solid state', 'samsung', 'crucial',
            'western digital', 'seagate', 'kingston', 'adata',
            'sandisk', 'intel ssd', 'toshiba', 'hitachi'
        ]
        
        sensor_lower = sensor_name.lower()
        parent_lower = parent_name.lower() if parent_name else ""
        
        if "temperature" in sensor_lower:
            if any(keyword in parent_lower for keyword in storage_keywords):
                return True
            
            if any(keyword in sensor_lower for keyword in storage_keywords):
                return True
        
        return False
    
    def get_storage_temperatures(self):
        storage_temps = {}
        
        if not self.ohm_available:
            print("❌ OpenHardwareMonitor not available - no temperature data")
            return None
        
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = w.Sensor()
            
            all_temp_sensors = []
            for sensor in sensors:
                if (sensor.SensorType == "Temperature" and 
                    sensor.Value is not None):
                    
                    all_temp_sensors.append({
                        'name': sensor.Name,
                        'value': float(sensor.Value),
                        'parent': sensor.Parent if hasattr(sensor, 'Parent') else "Unknown"
                    })
            
            print(f"🔍 Found {len(all_temp_sensors)} temperature sensors total")
            
            storage_sensors = []
            for sensor in all_temp_sensors:
                if self._is_storage_sensor(sensor['name'], sensor['parent']):
                    storage_sensors.append(sensor)
                else:
                    print(f"  Skipping non-storage: {sensor['name']} (Parent: {sensor['parent']})")
            
            print(f"💾 Found {len(storage_sensors)} storage temperature sensors")
            
            for sensor in storage_sensors:
                if sensor['parent'] and sensor['parent'] != "Unknown":
                    device_name = sensor['parent']
                else:
                    device_name = sensor['name']
                
                raw_temp = sensor['value']
                adjusted_temp = raw_temp - 13
                storage_temps[device_name] = adjusted_temp
                
                print(f"  {device_name}: {raw_temp}°C")
            
            if storage_temps:
                print("📊 Storage temperatures found:")
                for device, temp in storage_temps.items():
                    print(f"  {device}: {temp}°C")
                return storage_temps
            else:
                print("❌ No storage temperatures found in OpenHardwareMonitor")
                return self._find_storage_temps_alternative(sensors)
            
        except Exception as e:
            print(f"❌ Error reading storage temperatures: {e}")
            self.ohm_available = False
            return None
    
    def _find_storage_temps_alternative(self, sensors):
        print("🔄 Trying alternative storage detection method...")
        storage_temps = {}
        
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            hardware_items = w.Hardware()
            
            storage_devices = []
            for hardware in hardware_items:
                hw_name = hardware.Name if hardware.Name else ""
                hw_lower = hw_name.lower()
                
                storage_keywords = ['ssd', 'hdd', 'disk', 'drive', 'samsung', 'crucial', 'wd', 'seagate']
                if any(keyword in hw_lower for keyword in storage_keywords):
                    storage_devices.append(hw_name)
                    print(f"  Found storage device: {hw_name}")
            
            for sensor in sensors:
                if (sensor.SensorType == "Temperature" and 
                    sensor.Value is not None and
                    hasattr(sensor, 'Parent') and
                    sensor.Parent in storage_devices):
                    
                    raw_temp = float(sensor.Value)
                    adjusted_temp = raw_temp - 13
                    storage_temps[sensor.Parent] = adjusted_temp
                    print(f"  Found temperature for {sensor.Parent}: {raw_temp}°C -> {adjusted_temp}°C")
        
        except Exception as e:
            print(f"❌ Alternative method failed: {e}")
        
        return storage_temps if storage_temps else None
    
    def get_average_storage_temperature(self):
        storage_temps = self.get_storage_temperatures()
        if storage_temps:
            avg_temp = sum(storage_temps.values()) / len(storage_temps)
            print(f"📈 Average storage temperature: {avg_temp:.1f}°C")
            return avg_temp
        else:
            return None
    
    def get_max_storage_temperature(self):
        storage_temps = self.get_storage_temperatures()
        if storage_temps:
            max_temp = max(storage_temps.values())
            max_device = max(storage_temps, key=storage_temps.get)
            print(f"🔥 Hottest storage: {max_device} at {max_temp:.1f}°C")
            return max_temp
        else:
            return None
    
    def get_detailed_sensor_info(self):
        if not self.wmi_available:
            return "WMI not available"
        
        try:
            import wmi
            info = []
            
            if self.ohm_available:
                try:
                    w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                    sensors = w.Sensor()
                    info.append("=== OpenHardwareMonitor All Temperature Sensors ===")
                    
                    temp_sensors = [s for s in sensors if s.SensorType == "Temperature" and s.Value is not None]
                    
                    if temp_sensors:
                        for sensor in temp_sensors:
                            parent_info = sensor.Parent if hasattr(sensor, 'Parent') else "No parent"
                            raw_temp = float(sensor.Value)
                            adjusted_temp = raw_temp - 13
                            info.append(f"  {sensor.Name}: {raw_temp}°C -> {adjusted_temp}°C (Parent: {parent_info})")
                    else:
                        info.append("No temperature sensors found")
                        
                except Exception as e:
                    info.append(f"OpenHardwareMonitor error: {e}")
            
            return "\n".join(info) if info else "No sensor information available"
            
        except Exception as e:
            return f"Error getting sensor info: {e}"

class TemperatureMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Storage Temperature Monitor")
        
        # Condition 2: Initialize responsive design
        self.responsive_design = ResponsiveDesign(root)
        self.scaling_factors = self.responsive_design.get_scaling_factors()
        
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_theme()
        
        self.is_monitoring = True
        self.alert_monitoring_active = True
        self.monitor_thread = None
        self.email_thread = None
        
        self.last_warning_time = 0
        self.warning_cooldown = 30
        self.last_email_time = 0
        self.email_interval = 3600  
        
        self.critical_temp = 30  
        self.warning_temp = 25   
        
        self.temp_history = deque(maxlen=50)
        self.time_history = deque(maxlen=50)
        
        self.min_temp = float('inf')
        self.max_temp = float('-inf')
        
        self.storage_temperatures = {}
        
        self.temp_reader = StorageTemperatureReader()
        
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'nxpisian@gmail.com',
            'sender_password': 'aqkz uykr cmfu oqbm',
            'receiver_email': 'supercompnxp@gmail.com, ian.tolentino.bp@j-display.com, ferrerasroyce@gmail.com'
        }

        self.log_manager = LogManager()
        
        self.setup_background()
        self.setup_modern_styles()
        self.load_settings()
        self.setup_ui()
        
        # Condition 1: Start OpenHardwareMonitor automatically
        self.start_openhardware_monitor()
        
        self.start_realtime_updates()
        self.start_email_scheduler()
        
        self.log_manager.log_temperature("System", "N/A", "Storage Temperature Monitor started - logging initialized")
        
    def start_openhardware_monitor(self):
        """Condition 1: Start OpenHardwareMonitor automatically"""
        print("🚀 Initializing OpenHardwareMonitor...")
        success = self.temp_reader.run_openhardware_monitor()
        
        if success:
            print("✅ OpenHardwareMonitor is ready")
            time.sleep(3)
            self.temp_reader.initialize_wmi()
        else:
            print("⚠️ Could not start OpenHardwareMonitor. Some features may not work.")
            messagebox.showwarning(
                "OpenHardwareMonitor Warning",
                "OpenHardwareMonitor could not be started automatically.\n\n"
                "Please ensure:\n"
                "1. OpenHardwareMonitor.exe is in the same directory as this program\n"
                "2. Run it manually as Administrator\n\n"
                "You can download it from: https://openhardwaremonitor.org/"
            )
    
    def setup_background(self):
        self.bg_canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
            bg=self.colors['background']
        )
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.root.update()
        
        self.responsive_bg = ResponsiveGradientBackground(
            self.bg_canvas, 
            self.root.winfo_width(), 
            self.root.winfo_height(),
            self.colors
        )
        
        self.root.bind('<Configure>', self.on_resize)
    
    def on_resize(self, event):
        if event.widget == self.root:
            self.responsive_bg.width = event.width
            self.responsive_bg.height = event.height
            self.responsive_bg.create_responsive_background()
            
            self.scaling_factors = self.responsive_design.get_scaling_factors()
    
    def setup_modern_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Modern.TFrame', 
                       background=self.colors['surface'])
        
        style.configure('Card.TFrame', 
                       background=self.colors['card_bg'],
                       relief='flat', 
                       borderwidth=0)
        
        style.configure('Card.TLabelframe', 
                       background=self.colors['card_bg'],
                       relief='flat',
                       borderwidth=1,
                       bordercolor=self.colors['border'])
        
        style.configure('Card.TLabelframe.Label',
                       background=self.colors['card_bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Condition 2: Responsive font sizes
        base_font_size = int(9 * self.scaling_factors['font_scale'])
        base_padding = int(6 * self.scaling_factors['padding_scale'])
        
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', base_font_size, 'bold'),
                       padding=(12, base_padding))
        
        style.configure('Secondary.TButton',
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       bordercolor=self.colors['border'],
                       focuscolor='none',
                       font=('Segoe UI', base_font_size),
                       padding=(10, base_padding-1))
        
        style.configure('Theme.TButton',
                       background=self.colors['secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', base_font_size-1, 'bold'),
                       padding=(8, base_padding-2))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['secondary']),
                           ('pressed', self.colors['secondary'])])
        
        style.map('Secondary.TButton',
                 background=[('active', self.colors['hover']),
                           ('pressed', self.colors['hover'])])
        
        style.map('Theme.TButton',
                 background=[('active', self.colors['accent']),
                           ('pressed', self.colors['accent'])])
        
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['input_bg'],
                       foreground=self.colors['input_fg'],
                       borderwidth=1,
                       focusthickness=2,
                       focuscolor=self.colors['primary'])
        
        style.configure('Modern.TCombobox',
                       fieldbackground=self.colors['input_bg'],
                       foreground=self.colors['input_fg'],
                       background=self.colors['input_bg'],
                       borderwidth=1,
                       focusthickness=2,
                       focuscolor=self.colors['primary'],
                       selectbackground=self.colors['primary'],
                       selectforeground=self.colors['text_primary'],
                       arrowcolor=self.colors['text_primary'])
        
        style.map('Modern.TCombobox',
                 fieldbackground=[('readonly', self.colors['input_bg']),
                                ('active', self.colors['input_bg'])],
                 background=[('readonly', self.colors['input_bg']),
                           ('active', self.colors['input_bg'])],
                 foreground=[('readonly', self.colors['input_fg']),
                           ('active', self.colors['input_fg'])],
                 selectbackground=[('readonly', self.colors['primary']),
                                 ('active', self.colors['primary'])],
                 selectforeground=[('readonly', self.colors['text_primary']),
                                 ('active', self.colors['text_primary'])])
    
    def toggle_theme(self):
        self.colors = self.theme_manager.toggle_theme()
        self.update_theme()
    
    def update_theme(self):
        self.responsive_bg.update_theme(self.colors)
        self.update_graph_theme()
        self.setup_modern_styles()
        self.setup_ui()
    
    def update_graph_theme(self):
        plt.rcParams['axes.facecolor'] = self.colors['card_bg']
        plt.rcParams['figure.facecolor'] = self.colors['card_bg']
        plt.rcParams['axes.edgecolor'] = self.colors['border']
        plt.rcParams['axes.labelcolor'] = self.colors['text_primary']
        plt.rcParams['text.color'] = self.colors['text_primary']
        plt.rcParams['xtick.color'] = self.colors['text_secondary']
        plt.rcParams['ytick.color'] = self.colors['text_secondary']
        plt.rcParams['font.size'] = 9
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        
        if hasattr(self, 'canvas'):
            self.update_graph()
    
    def load_settings(self):
        try:
            if os.path.exists('temperature_monitor_settings.json'):
                with open('temperature_monitor_settings.json', 'r') as f:
                    settings = json.load(f)
                    self.critical_temp = settings.get('critical_temp', 30)
                    self.warning_temp = settings.get('warning_temp', 27)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        try:
            settings = {
                'critical_temp': self.critical_temp,
                'warning_temp': self.warning_temp
            }
            with open('temperature_monitor_settings.json', 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
        
    def setup_ui(self):
        for widget in self.bg_canvas.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()
        
        # Condition 2: Responsive padding based on screen size
        if self.scaling_factors['screen_width'] < 1280:
            base_padding = 10
        elif self.scaling_factors['screen_width'] < 1920:
            base_padding = 15
        else:
            base_padding = 20
        
        main_frame = ttk.Frame(self.bg_canvas, style='Modern.TFrame', padding=f"{base_padding}")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, base_padding))
        header_frame.columnconfigure(0, weight=1)
        
        title_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        title_frame.grid(row=0, column=0, sticky='ew')
        title_frame.columnconfigure(0, weight=1)
        
        title_font_size = int(20 * self.scaling_factors['font_scale'])
        
        title_label = ttk.Label(title_frame, text="Storage Temperature Monitor", 
                               background=self.colors['surface'],
                               foreground=self.colors['text_primary'],
                               font=("Segoe UI", title_font_size, "bold"))
        title_label.grid(row=0, column=0, sticky='w')
        
        header_buttons_frame = ttk.Frame(title_frame, style='Modern.TFrame')
        header_buttons_frame.grid(row=0, column=1, sticky='e')
        
        live_log_button = ttk.Button(header_buttons_frame, text="Live Log", 
                                command=self.show_live_log,
                                style='Primary.TButton')
        live_log_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        theme_button = ttk.Button(header_buttons_frame, text="Theme", 
                             command=self.toggle_theme,
                             style='Secondary.TButton')
        theme_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        content_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        content_frame.grid(row=1, column=0, sticky='nsew')
        
        # Condition 2: Adjust column weights based on screen size
        if self.scaling_factors['screen_width'] < 1280:
            content_frame.columnconfigure(0, weight=6)
            content_frame.columnconfigure(1, weight=4)
        else:
            content_frame.columnconfigure(0, weight=7)
            content_frame.columnconfigure(1, weight=3)
        
        content_frame.rowconfigure(0, weight=1)
        
        left_column = ttk.Frame(content_frame, style='Modern.TFrame')
        left_column.grid(row=0, column=0, sticky='nsew', padx=(0, base_padding//2))
        left_column.columnconfigure(0, weight=1)
        left_column.rowconfigure(1, weight=1)
        
        metrics_frame = ttk.Frame(left_column, style='Modern.TFrame')
        metrics_frame.grid(row=0, column=0, sticky='ew', pady=(0, base_padding))
        
        # Condition 2: Adjust metric cards layout for small screens
        if self.scaling_factors['screen_width'] < 1280:
            metrics_frame.columnconfigure(0, weight=1)
            metrics_frame.columnconfigure(1, weight=1)
            metrics_frame.columnconfigure(2, weight=1)
            card_padding = 10
        else:
            metrics_frame.columnconfigure(0, weight=1)
            metrics_frame.columnconfigure(1, weight=1)
            metrics_frame.columnconfigure(2, weight=1)
            card_padding = int(20 * self.scaling_factors['padding_scale'])
        
        avg_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding=f"{card_padding}")
        avg_card.grid(row=0, column=0, sticky='nsew', padx=(0, base_padding//2))
        
        ttk.Label(avg_card, text="Average Temperature", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_secondary'],
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.CENTER)
        
        self.avg_temp_var = tk.StringVar(value="--°C")
        temp_font_size = int(24 * self.scaling_factors['font_scale'])
        self.avg_temp_display = ttk.Label(avg_card, textvariable=self.avg_temp_var, 
                                         background=self.colors['card_bg'],
                                         foreground=self.colors['primary'],
                                         font=("Segoe UI", temp_font_size, "bold"))
        self.avg_temp_display.pack(anchor=tk.CENTER, pady=(8, 0))
        
        max_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding=f"{card_padding}")
        max_card.grid(row=0, column=1, sticky='nsew', padx=(base_padding//2, base_padding//2))
        
        ttk.Label(max_card, text="Max Temperature", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_secondary'],
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.CENTER)
        
        self.max_temp_var = tk.StringVar(value="--°C")
        self.max_temp_display = ttk.Label(max_card, textvariable=self.max_temp_var, 
                                     background=self.colors['card_bg'],
                                     foreground=self.colors['primary'],
                                     font=("Segoe UI", temp_font_size, "bold"))
        self.max_temp_display.pack(anchor=tk.CENTER, pady=(8, 0))
        
        sensor_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding=f"{card_padding}")
        sensor_card.grid(row=0, column=2, sticky='nsew', padx=(base_padding//2, 0))
        
        ttk.Label(sensor_card, text="Sensor Status", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_secondary'],
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.CENTER)
        
        self.sensor_status_var = tk.StringVar()
        status_font_size = int(12 * self.scaling_factors['font_scale'])
        sensor_status_label = ttk.Label(sensor_card, textvariable=self.sensor_status_var,
                                  background=self.colors['card_bg'],
                                  foreground=self.colors['text_primary'],
                                  font=("Segoe UI", status_font_size, "bold"))
        sensor_status_label.pack(anchor=tk.CENTER, pady=(8, 0))
        
        self.status_var = tk.StringVar(value="Initializing...")
        small_font_size = int(9 * self.scaling_factors['font_scale'])
        status_label = ttk.Label(sensor_card, textvariable=self.status_var,
                            background=self.colors['card_bg'],
                            foreground=self.colors['text_secondary'],
                            font=("Segoe UI", small_font_size))
        status_label.pack(anchor=tk.CENTER, pady=(4, 0))
        
        self.update_sensor_status()
        
        graph_frame = ttk.Frame(left_column, style='Card.TFrame', padding="15")
        graph_frame.grid(row=1, column=0, sticky='nsew')
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        
        self.update_graph_theme()
        
        # Condition 2: Adjust graph size based on screen
        if self.scaling_factors['screen_width'] < 1280:
            figsize = (8, 4)
        else:
            figsize = (10, 6)
        
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.tight_layout(pad=4.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        
        right_column = ttk.Frame(content_frame, style='Modern.TFrame')
        right_column.grid(row=0, column=1, sticky='nsew', padx=(base_padding//2, 0))
        right_column.columnconfigure(0, weight=1)
        
        alert_frame = ttk.LabelFrame(right_column, text="ALERT CONTROLS", 
                                style='Card.TLabelframe', padding="15")
        alert_frame.grid(row=0, column=0, sticky='ew', pady=(0, base_padding))
        
        alert_status_frame = ttk.Frame(alert_frame, style='Card.TFrame')
        alert_status_frame.grid(row=0, column=0, sticky='ew', pady=(0, 12))
        
        ttk.Label(alert_status_frame, text="Current Status:", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_primary'],
                 font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w')
        
        self.alert_status_var = tk.StringVar(value="Alerts: ACTIVE")
        alert_status_label = ttk.Label(alert_status_frame, textvariable=self.alert_status_var,
                                 background=self.colors['card_bg'],
                                 foreground=self.colors['success'],
                                 font=('Segoe UI', 11, 'bold'))
        alert_status_label.grid(row=1, column=0, sticky='w', pady=(5, 0))
        
        alert_buttons_frame = ttk.Frame(alert_frame, style='Card.TFrame')
        alert_buttons_frame.grid(row=1, column=0, sticky='ew')
        alert_buttons_frame.columnconfigure(0, weight=1)
        alert_buttons_frame.columnconfigure(1, weight=1)
        
        self.start_button = ttk.Button(alert_buttons_frame, text="Enable Alerts", 
                                  command=self.start_alert_monitoring, 
                                  style='Primary.TButton')
        self.start_button.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        self.stop_button = ttk.Button(alert_buttons_frame, text="Disable Alerts", 
                                 command=self.stop_alert_monitoring, 
                                 state="disabled", 
                                 style='Secondary.TButton')
        self.stop_button.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        
        monitor_frame = ttk.LabelFrame(right_column, text="MONITORING CONTROLS", 
                                  style='Card.TLabelframe', padding="15")
        monitor_frame.grid(row=1, column=0, sticky='ew', pady=(0, base_padding))
        
        refresh_frame = ttk.Frame(monitor_frame, style='Card.TFrame')
        refresh_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        
        ttk.Label(refresh_frame, text="Update Interval (seconds):", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_primary'],
                 font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 8))
        
        self.refresh_rate_var = tk.StringVar(value="2")
        refresh_combo = ttk.Combobox(refresh_frame, textvariable=self.refresh_rate_var,
                                values=["1", "2", "5", "10"], 
                                width=12,
                                state="readonly",
                                style='Modern.TCombobox',
                                height=4)
        refresh_combo.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        refresh_button = ttk.Button(refresh_frame, text="Refresh Now", 
                              command=self.manual_refresh, 
                              style='Primary.TButton')
        refresh_button.grid(row=2, column=0, sticky='ew')
        
        utils_frame = ttk.Frame(monitor_frame, style='Card.TFrame')
        utils_frame.grid(row=1, column=0, sticky='ew', pady=(15, 0))
        
        utils_row1 = ttk.Frame(utils_frame, style='Card.TFrame')
        utils_row1.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        utils_row1.columnconfigure(0, weight=1)
        utils_row1.columnconfigure(1, weight=1)
        
        sensor_button = ttk.Button(utils_row1, text="Sensor Info", 
                              command=self.show_sensor_info, 
                              style='Secondary.TButton')
        sensor_button.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        email_button = ttk.Button(utils_row1, text="Test Email", 
                             command=self.send_test_email, 
                             style='Secondary.TButton')
        email_button.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        
        settings_frame = ttk.LabelFrame(right_column, text="TEMPERATURE SETTINGS", 
                                   style='Card.TLabelframe', padding="15")
        settings_frame.grid(row=2, column=0, sticky='ew', pady=(0, base_padding))
        
        warning_frame = ttk.Frame(settings_frame, style='Card.TFrame')
        warning_frame.grid(row=0, column=0, sticky='ew', pady=(0, 12))
        
        ttk.Label(warning_frame, text="Warning Threshold (°C):", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_primary'],
                 font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w')
        
        self.warning_var = tk.StringVar(value=str(self.warning_temp))
        warning_entry = ttk.Entry(warning_frame, textvariable=self.warning_var, 
                             width=8,
                             style='Modern.TEntry',
                             font=('Segoe UI', 10),
                             justify=tk.CENTER)
        warning_entry.grid(row=1, column=0, sticky='w', pady=(8, 0))
        
        critical_frame = ttk.Frame(settings_frame, style='Card.TFrame')
        critical_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        ttk.Label(critical_frame, text="Critical Threshold (°C):", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_primary'],
                 font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w')
        
        self.critical_var = tk.StringVar(value=str(self.critical_temp))
        critical_entry = ttk.Entry(critical_frame, textvariable=self.critical_var, 
                              width=8,
                              style='Modern.TEntry',
                              font=('Segoe UI', 10),
                              justify=tk.CENTER)
        critical_entry.grid(row=1, column=0, sticky='w', pady=(8, 0))
        
        update_button = ttk.Button(settings_frame, text="Save Settings", 
                              command=self.update_settings, 
                              style='Primary.TButton')
        update_button.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        footer_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        footer_frame.grid(row=2, column=0, sticky='ew', pady=(base_padding, 0))
        footer_frame.columnconfigure(0, weight=1)
        
        self.last_update_var = tk.StringVar(value="Last update: --")
        last_update_label = ttk.Label(footer_frame, textvariable=self.last_update_var,
                                 background=self.colors['surface'],
                                 foreground=self.colors['text_secondary'],
                                 font=("Segoe UI", 9))
        last_update_label.grid(row=0, column=0, sticky='w')
        
        self.time_var = tk.StringVar(value="--:--:--")
        time_label = ttk.Label(footer_frame, textvariable=self.time_var,
                          background=self.colors['surface'],
                          foreground=self.colors['text_secondary'],
                          font=("Segoe UI", 9))
        time_label.grid(row=0, column=1, sticky='w', padx=(20, 0))
        
        self.next_email_var = tk.StringVar(value="Next report: --")
        next_email_label = ttk.Label(footer_frame, textvariable=self.next_email_var,
                                background=self.colors['surface'],
                                foreground=self.colors['text_secondary'],
                                font=("Segoe UI", 9))
        next_email_label.grid(row=0, column=2, sticky='e')
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.root.update_idletasks()
    
    def show_live_log(self):
        LiveLogWindow(self.root, self.log_manager, self.theme_manager, self.responsive_design)
    
    def update_sensor_status(self):
        if self.temp_reader.ohm_available:
            status = "✅ Connected"
            color = self.colors['success']
        else:
            status = "❌ Not Available"
            color = self.colors['error']
        
        self.sensor_status_var.set(status)
    
    def show_sensor_info(self):
        info = self.temp_reader.get_detailed_sensor_info()
        messagebox.showinfo("Storage Sensor Information", info)
    
    def start_realtime_updates(self):
        self.is_monitoring = True
        self.update_time_display()
        self.monitor_thread = threading.Thread(target=self.monitor_temperature, daemon=True)
        self.monitor_thread.start()
        
    def start_email_scheduler(self):
        self.email_thread = threading.Thread(target=self.email_scheduler, daemon=True)
        self.email_thread.start()
        
    def update_time_display(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_var.set(f"Time: {current_time}")
        
        next_email_time = self.last_email_time + self.email_interval
        time_until_next = next_email_time - time.time()
        if time_until_next > 0:
            minutes = int(time_until_next // 60)
            seconds = int(time_until_next % 60)
            self.next_email_var.set(f"Next report: {minutes:02d}:{seconds:02d}")
        else:
            self.next_email_var.set("Next report: Soon")
            
        self.root.after(1000, self.update_time_display)
        
    def get_system_info(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            return cpu_percent, memory_percent
        except:
            return None, None
    
    def update_status_indicator(self, temperature):
        pass
    
    def send_desktop_notification(self, title, message, temp):
        try:
            notification.notify(
                title=title,
                message=f"{message}\nHottest storage: {temp:.1f}°C",
                timeout=10,
                app_name="Storage Temperature Monitor"
            )
            print(f"Desktop notification sent: {title}")
            
            self.log_manager.log_temperature("Alert", temp, f"Alert: {title} - {message}")
            
        except Exception as e:
            print(f"Error sending desktop notification: {e}")
        
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            pass
    
    def send_email_report(self):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['receiver_email']
            msg['Subject'] = f"Storage Temperature Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            current_temps = self.storage_temperatures
            current_max = self.temp_reader.get_max_storage_temperature()
            
            actions = []
            if current_max is not None:
                if current_max >= self.critical_temp:
                    actions = [
                        "🚨 IMMEDIATE ACTION REQUIRED:",
                        "- Check cooling system immediately",
                        "- Consider reducing server load",
                        "- Ensure proper ventilation around storage devices",
                        "- Monitor temperatures closely",
                        "- Consider temporary shutdown if temperatures continue to rise"
                    ]
                elif current_max >= self.warning_temp:
                    actions = [
                        "⚠️ WARNING - Monitoring Required:",
                        "- Check ventilation around storage devices",
                        "- Monitor temperature trends",
                        "- Ensure cooling system is functioning properly",
                        "- Consider optimizing server load"
                    ]
                else:
                    actions = [
                        "✅ System operating normally:",
                        "- No immediate action required",
                        "- Continue regular monitoring"
                    ]
            
            storage_details = "\n".join([f"  - {device}: {temp:.1f}°C" for device, temp in current_temps.items()]) if current_temps else "  No storage temperature data available"
            
            body = f"""
Temperature Monitoring Report
=====================================

Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This automated report provides an overview of the current room temperature status.

Temperature Statistics:
• Current Temperature: {current_max if current_max else 'N/A':.1f}°C
• Estimated IDRAC Temperature: {(current_max -2) if current_max else 'N/A':.1f}°C
• Minimum Temperature: {self.min_temp if self.min_temp != float('inf') else 'N/A':.1f}°C
• Maximum Temperature: {self.max_temp if self.max_temp != float('-inf') else 'N/A':.1f}°C

System Status Overview:
• Warning Threshold: {self.warning_temp}°C
• Critical Threshold: {self.critical_temp}°C
• Current Status: {'CRITICAL' if current_max and current_max >= self.critical_temp else 'WARNING' if current_max and current_max >= self.warning_temp else 'NORMAL'}

Recommended Actions:
{chr(10).join(actions)}

Monitoring Details:
• Device: {os.environ.get('COMPUTERNAME', 'Unknown Device')}
• Report Type: Automated Temperature Monitoring
• Monitoring Interval: 60 Minutes

This is an automated notification from the Temperature Monitoring System.
No response is required unless immediate action is indicated above.
"""
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email report sent successfully at {datetime.datetime.now().strftime('%H:%M:%S')}")
            
            self.log_manager.log_temperature("Email", current_max if current_max else 0, "Scheduled email report sent")
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            
            self.log_manager.log_temperature("Error", 0, f"Failed to send email: {e}")
            
            return False
    
    def send_test_email(self):
        try:
            success = self.send_email_report()
            if success:
                messagebox.showinfo("Success", "Test email sent successfully!")
            else:
                messagebox.showerror("Error", "Failed to send test email. Check your email configuration.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send test email: {str(e)}")
    
    def email_scheduler(self):
        while self.is_monitoring:
            try:
                current_time = time.time()
                
                if current_time - self.last_email_time >= self.email_interval:
                    if self.storage_temperatures:
                        print("🕒 Sending scheduled email report...")
                        self.send_email_report()
                        self.last_email_time = current_time
                    
                    self.min_temp = float('inf')
                    self.max_temp = float('-inf')
                
                time.sleep(30)
                
            except Exception as e:
                print(f"Email scheduler error: {e}")
                time.sleep(60)
    
    def update_storage_display(self):
        pass
    
    def update_graph(self):
        """Update the temperature history graph with professional design and clear time axis"""
        self.ax.clear()
        
        if len(self.temp_history) > 0:
            # Convert time from seconds to minutes for x-axis
            time_minutes = [t/60 for t in self.time_history]
            
            # Calculate time range for better axis formatting
            time_range = max(time_minutes) - min(time_minutes) if time_minutes else 0
            
            critical_temp = 30
            warning_temp = 27
            
            if len(time_minutes) > 1:
                # Create segments for different temperature ranges
                segments = []
                current_segment = {'times': [time_minutes[0]], 'temps': [self.temp_history[0]], 'color': self.get_temperature_color(self.temp_history[0], critical_temp, warning_temp)}
                
                for i in range(1, len(time_minutes)):
                    current_color = self.get_temperature_color(self.temp_history[i], critical_temp, warning_temp)
                    
                    if current_color == current_segment['color']:
                        # Continue current segment
                        current_segment['times'].append(time_minutes[i])
                        current_segment['temps'].append(self.temp_history[i])
                    else:
                        # End current segment and start new one
                        segments.append(current_segment)
                        current_segment = {'times': [time_minutes[i]], 'temps': [self.temp_history[i]], 'color': current_color}
                
                segments.append(current_segment)
                
                # Plot each segment with its respective color
                for segment in segments:
                    if len(segment['times']) > 1:
                        self.ax.plot(segment['times'], segment['temps'], 
                                    color=segment['color'], 
                                    linewidth=2.5, 
                                    marker='o',
                                    markersize=3,
                                    alpha=0.9)
            
            # Add legend for temperature ranges
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='blue', lw=3, label='Normal Temperature (<27°C)'),
                Line2D([0], [0], color='yellow', lw=3, label='Warning (27-30°C)'),
                Line2D([0], [0], color='red', lw=3, label='Critical (>30°C)')
            ]
            self.ax.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.95)
            
            # Professional labels and title
            self.ax.set_ylabel('Temperature (°C)', fontsize=10, fontweight='bold')
            
            # CLEARER X-axis labeling
            self.ax.set_xlabel('Elapsed Time (Minutes)', fontsize=10, fontweight='bold')
            
            # Add "Temperature Trend" title
            self.ax.set_title('Temperature Trend Over Time', 
                            fontsize=12, fontweight='bold', pad=20)
            
            # IMPROVED: Better x-axis formatting with clear numbering
            if time_minutes:
                # Set reasonable tick spacing based on time range
                if time_range < 10:  # Less than 10 minutes
                    tick_interval = 1  # Every minute
                elif time_range < 30:  # Less than 30 minutes
                    tick_interval = 5  # Every 5 minutes
                elif time_range < 120:  # Less than 2 hours
                    tick_interval = 10  # Every 10 minutes
                else:  # More than 2 hours
                    tick_interval = max(15, int(time_range / 8))  # 8 ticks max
                
                # Generate tick positions
                min_time = min(time_minutes)
                max_time = max(time_minutes)
                
                # Create ticks at regular intervals
                tick_positions = []
                tick_labels = []
                
                # Start from the first data point or rounded value
                start_tick = 0  # Since we're showing elapsed time from start
                while start_tick <= max_time:
                    tick_positions.append(start_tick)
                    
                    # Format label based on time value
                    if start_tick < 60:  # Less than 1 hour
                        tick_labels.append(f'{int(start_tick)} min')
                    else:  # 1 hour or more
                        hours = int(start_tick // 60)
                        minutes = int(start_tick % 60)
                        if minutes == 0:
                            tick_labels.append(f'{hours} hr')
                        else:
                            tick_labels.append(f'{hours}h{minutes}m')
                    
                    start_tick += tick_interval
                
                # Ensure last data point is included
                if tick_positions[-1] < max_time:
                    tick_positions.append(max_time)
                    if max_time < 60:
                        tick_labels.append(f'{int(max_time)} min')
                    else:
                        hours = int(max_time // 60)
                        minutes = int(max_time % 60)
                        if minutes == 0:
                            tick_labels.append(f'{hours} hr')
                        else:
                            tick_labels.append(f'{hours}h{minutes}m')
                
                self.ax.set_xticks(tick_positions)
                self.ax.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            # Professional grid
            self.ax.grid(True, alpha=0.2, linestyle='-', which='both')
            
            # Add minor grid for better readability
            self.ax.grid(True, alpha=0.1, linestyle=':', which='minor')
            
            # Set professional y-axis limits
            if self.temp_history:
                current_min = min(self.temp_history)
                current_max = max(self.temp_history)
                padding = max(2, (current_max - current_min) * 0.1)
                self.ax.set_ylim(max(0, current_min - padding), current_max + padding)
                
                # Set y-axis ticks at reasonable intervals
                y_min, y_max = self.ax.get_ylim()
                y_range = y_max - y_min
                
                if y_range <= 10:
                    y_interval = 1
                elif y_range <= 20:
                    y_interval = 2
                elif y_range <= 50:
                    y_interval = 5
                else:
                    y_interval = 10
                
                y_ticks = []
                y_val = round(y_min / y_interval) * y_interval
                while y_val <= y_max:
                    y_ticks.append(y_val)
                    y_val += y_interval
                
                self.ax.set_yticks(y_ticks)
            
            # Professional spine styling
            for spine in self.ax.spines.values():
                spine.set_color(self.colors['border'])
                spine.set_linewidth(1)
            
            # Add current time annotation
            if time_minutes:
                last_time = time_minutes[-1]
                last_temp = self.temp_history[-1]
                
                # Format time annotation
                if last_time < 60:
                    time_text = f'{last_time:.1f} min'
                else:
                    hours = int(last_time // 60)
                    minutes = int(last_time % 60)
                    if minutes == 0:
                        time_text = f'{hours} hr'
                    else:
                        time_text = f'{hours}h{minutes}m'
                
                # Add annotation for last data point
                self.ax.annotate(f'Current: {last_temp:.1f}°C\nTime: {time_text}',
                               xy=(last_time, last_temp),
                               xytext=(10, 10),
                               textcoords='offset points',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8),
                               fontsize=8,
                               ha='left')
        
        else:
            # Professional no-data message
            self.ax.text(0.5, 0.5, 'Collecting temperature data...', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes, fontsize=11,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['hover']))
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        
        # Moved note further down with more spacing
        note_text = "Note: Temperatures shown are adjusted for room temperature (not actual device readings)"
        self.ax.text(0.5, -0.35, note_text, transform=self.ax.transAxes, 
                    fontsize=8, color=self.colors['text_secondary'],
                    horizontalalignment='center', verticalalignment='top',
                    style='italic')
        
        # Adjust layout to make more room for the note
        self.fig.tight_layout(rect=[0, 0.12, 1, 0.95])
        
        self.canvas.draw()
    
    def get_temperature_color(self, temperature, critical_temp, warning_temp):
        if temperature >= critical_temp:
            return 'red'  # Critical
        elif temperature >= warning_temp:
            return 'yellow'  # Warning
        else:
            return 'blue'  # Normal
    
    def monitor_temperature(self):
        start_time = time.time()
        
        while self.is_monitoring:
            try:
                self.storage_temperatures = self.temp_reader.get_storage_temperatures()
                max_temp = self.temp_reader.get_max_storage_temperature()
                avg_temp = self.temp_reader.get_average_storage_temperature()
                cpu_percent, memory_percent = self.get_system_info()
                
                if max_temp is not None:
                    current_time = time.time() - start_time
                    
                    if max_temp < self.min_temp:
                        self.min_temp = max_temp
                    if max_temp > self.max_temp:
                        self.max_temp = max_temp
                    
                    self.root.after(0, self.update_display, max_temp, avg_temp, cpu_percent, memory_percent, current_time)
                    
                    self.temp_history.append(max_temp)
                    self.time_history.append(current_time)
                    
                    if avg_temp is not None:
                        self.log_manager.log_temperature("Average Temperature", avg_temp)
                    if max_temp is not None:
                        self.log_manager.log_temperature("Max Temperature", max_temp)
                    if self.storage_temperatures:
                        storage_details = ", ".join([f"{device}: {temp:.1f}°C" for device, temp in self.storage_temperatures.items()])
                        self.log_manager.log_temperature("Storage Details", 0, f"Storage temperatures: {storage_details}")
                    
                    if self.alert_monitoring_active:
                        current_absolute_time = time.time()
                        
                        if max_temp >= self.critical_temp:
                            if current_absolute_time - self.last_warning_time > self.warning_cooldown:
                                self.root.after(0, self.send_desktop_notification,
                                              "🔥 CRITICAL STORAGE TEMPERATURE ALERT!",
                                              "Storage temperature is critically high!",
                                              max_temp)
                                self.last_warning_time = current_absolute_time
                                
                        elif max_temp >= self.warning_temp:
                            if current_absolute_time - self.last_warning_time > self.warning_cooldown:
                                self.root.after(0, self.send_desktop_notification,
                                              "⚠️ HIGH STORAGE TEMPERATURE WARNING",
                                              "Storage temperature is above normal",
                                              max_temp)
                                self.last_warning_time = current_absolute_time
                else:
                    current_time = time.time() - start_time
                    self.root.after(0, self.update_display, None, None, None, None, current_time)
                    
                    self.log_manager.log_temperature("Error", 0, "No temperature data available from sensors")
                
                try:
                    refresh_delay = max(1, float(self.refresh_rate_var.get()))
                except:
                    refresh_delay = 2
                    
                time.sleep(refresh_delay)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                
                self.log_manager.log_temperature("Error", 0, f"Monitoring error: {e}")
                
                time.sleep(5)
    
    def update_display(self, max_temp, avg_temp, cpu_percent, memory_percent, current_time):
        if avg_temp is not None:
            self.avg_temp_var.set(f"{avg_temp:.1f}°C")
        else:
            self.avg_temp_var.set("--°C")
            
        if max_temp is not None:
            self.max_temp_var.set(f"{max_temp:.1f}°C")
        else:
            self.max_temp_var.set("--°C")
        
        if max_temp is None:
            status_text = "No sensor data"
            self.max_temp_display.config(foreground=self.colors['error'])
            self.avg_temp_display.config(foreground=self.colors['error'])
        elif max_temp >= self.critical_temp:
            status_text = f"CRITICAL {max_temp:.1f}°C"
            self.max_temp_display.config(foreground=self.colors['error'])
            self.avg_temp_display.config(foreground=self.colors['error'])
        elif max_temp >= self.warning_temp:
            status_text = f"WARNING {max_temp:.1f}°C"
            self.max_temp_display.config(foreground=self.colors['warning'])
            self.avg_temp_display.config(foreground=self.colors['warning'])
        else:
            status_text = f"Normal {max_temp:.1f}°C"
            self.max_temp_display.config(foreground=self.colors['success'])
            self.avg_temp_display.config(foreground=self.colors['success'])
        
        if self.alert_monitoring_active:
            status_text += " | Alerts ON"
        else:
            status_text += " | Alerts OFF"
            
        self.status_var.set(status_text)
        
        update_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.last_update_var.set(f"Updated: {update_time}")
        
        self.update_graph()
    
    def start_alert_monitoring(self):
        self.alert_monitoring_active = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        self.log_manager.log_temperature("System", 0, "Alert monitoring enabled")
        
        messagebox.showinfo("Alerts Enabled", "Storage temperature alert monitoring is now active!\n\nYou will receive notifications when storage temperatures exceed thresholds.")
    
    def stop_alert_monitoring(self):
        self.alert_monitoring_active = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        self.log_manager.log_temperature("System", 0, "Alert monitoring disabled")
        
        messagebox.showinfo("Alerts Disabled", "Storage temperature alert monitoring is now inactive.")
    
    def manual_refresh(self):
        self.storage_temperatures = self.temp_reader.get_storage_temperatures()
        max_temp = self.temp_reader.get_max_storage_temperature()
        avg_temp = self.temp_reader.get_average_storage_temperature()
        cpu_percent, memory_percent = self.get_system_info()
        if max_temp is not None:
            self.update_display(max_temp, avg_temp, cpu_percent, memory_percent, 
                              len(self.time_history) * float(self.refresh_rate_var.get()))
    
    def update_settings(self):
        try:
            new_warning = float(self.warning_var.get())
            new_critical = float(self.critical_var.get())
            
            if new_warning >= new_critical:
                messagebox.showerror("Error", "Warning temperature must be lower than critical temperature")
                return
            
            self.warning_temp = new_warning
            self.critical_temp = new_critical
            self.save_settings()
            
            self.log_manager.log_temperature("System", 0, f"Settings updated: Warning={new_warning}°C, Critical={new_critical}°C")
            
            messagebox.showinfo("Success", "Temperature settings updated successfully")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for temperature thresholds")
    
    def on_closing(self):
        self.is_monitoring = False
        
        self.log_manager.log_temperature("System", "N/A", "Storage Temperature Monitor shutting down")
        
        self.save_settings()
        self.root.destroy()

def main():
    try:
        import psutil
        from plyer import notification
        try:
            import wmi
            print("✅ WMI support available")
        except ImportError:
            print("❌ WMI not available - install with: pip install wmi")
            messagebox.showerror("Missing Dependency", "WMI is required for this application.\n\nPlease install it with: pip install wmi")
            return
            
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install psutil plyer matplotlib wmi")
        messagebox.showerror("Missing Dependencies", f"Missing required packages:\n\nPlease install: pip install psutil plyer matplotlib wmi")
        return
    
    root = tk.Tk()
    app = TemperatureMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()
