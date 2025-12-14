import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import psutil
import winsound
from plyer import notification
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
import traceback

from app.ui.responsive_bg import ResponsiveGradientBackground
from app.core.responsive import ResponsiveDesign
from app.core.theme import ThemeManager
from app.core.logger import LogManager
from app.ui.live_log import LiveLogWindow
from app.services.storage_reader import StorageTemperatureReader

class TemperatureMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Temperature Monitor")
        
        # Initialize components
        self.responsive_design = ResponsiveDesign(root)
        self.scaling_factors = self.responsive_design.get_scaling_factors()
        
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_theme()
        
        # Monitoring state
        self.is_monitoring = True
        self.alert_monitoring_active = True
        self.monitor_thread = None
        self.email_thread = None
        
        # Alert tracking
        self.last_warning_alert = 0
        self.last_critical_alert = 0
        self.warning_cooldown = 3600  # 1 hour cooldown for alerts
        
        # Temperature thresholds
        self.critical_temp = 30
        self.warning_temp = 25
        
        # Temperature history
        self.temp_history = deque(maxlen=100)
        self.time_history = deque(maxlen=100)
        
        # For statistics
        self.min_temp = float('inf')
        self.max_temp = float('-inf')
        
        # Initialize components
        self.temp_reader = StorageTemperatureReader()
        
        # Email configuration
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'nxpisian@gmail.com',
            'sender_password': 'aqkz uykr cmfu oqbm',
            'receiver_email': 'supercompnxp@gmail.com, ian.tolentino.bp@j-display.com, ferrerasroyce@gmail.com'
        }
        
        self.log_manager = LogManager()
        
        # Create background and setup UI
        self.setup_background()
        self.setup_modern_styles()
        self.load_settings()
        self.setup_ui()
        
        # Start OpenHardwareMonitor
        self.start_openhardware_monitor()
        
        # Start monitoring
        self.start_realtime_updates()
        self.start_email_scheduler()
        
        # Initial log
        self.log_manager.log_system_event("System Start", "Temperature Monitor initialized")
    
    def start_openhardware_monitor(self):
        """Start OpenHardwareMonitor"""
        print("🚀 Initializing OpenHardwareMonitor...")
        success = self.temp_reader.run_openhardware_monitor()
        
        if success:
            print("✅ OpenHardwareMonitor is ready")
            time.sleep(3)
            self.temp_reader.initialize_wmi()
        else:
            print("⚠️ Could not start OpenHardwareMonitor")
            messagebox.showwarning(
                "OpenHardwareMonitor Warning",
                "OpenHardwareMonitor could not be started automatically.\n\n"
                "Please ensure:\n"
                "1. OpenHardwareMonitor.exe is in the same directory\n"
                "2. Run it manually as Administrator\n\n"
                "Download from: https://openhardwaremonitor.org/"
            )
    
    def setup_background(self):
        """Setup the responsive gradient background"""
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
        """Handle window resize"""
        if event.widget == self.root:
            self.responsive_bg.width = event.width
            self.responsive_bg.height = event.height
            self.responsive_bg.create_responsive_background()
            self.scaling_factors = self.responsive_design.get_scaling_factors()
    
    def setup_modern_styles(self):
        """Configure modern professional styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Modern.TFrame', background=self.colors['surface'])
        style.configure('Card.TFrame', background=self.colors['card_bg'], relief='flat', borderwidth=0)
        
        style.configure('Card.TLabelframe', 
                       background=self.colors['card_bg'],
                       relief='flat',
                       borderwidth=1,
                       bordercolor=self.colors['border'])
        
        style.configure('Card.TLabelframe.Label',
                       background=self.colors['card_bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Button styles
        base_font_size = int(9 * self.scaling_factors['font_scale'])
        base_padding = int(6 * self.scaling_factors['padding_scale'])
        
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       font=('Segoe UI', base_font_size, 'bold'),
                       padding=(12, base_padding))
        
        style.configure('Secondary.TButton',
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       bordercolor=self.colors['border'],
                       font=('Segoe UI', base_font_size),
                       padding=(10, base_padding-1))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['secondary']),
                           ('pressed', self.colors['secondary'])])
        
        style.map('Secondary.TButton',
                 background=[('active', self.colors['hover']),
                           ('pressed', self.colors['hover'])])
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.colors = self.theme_manager.toggle_theme()
        self.update_theme()
    
    def update_theme(self):
        """Update the entire UI with new theme"""
        self.responsive_bg.update_theme(self.colors)
        self.update_graph_theme()
        self.setup_modern_styles()
        self.setup_ui()
    
    def update_graph_theme(self):
        """Update matplotlib graph with current theme"""
        plt.rcParams['axes.facecolor'] = self.colors['card_bg']
        plt.rcParams['figure.facecolor'] = self.colors['card_bg']
        plt.rcParams['axes.edgecolor'] = self.colors['border']
        plt.rcParams['axes.labelcolor'] = self.colors['text_primary']
        plt.rcParams['text.color'] = self.colors['text_primary']
        plt.rcParams['xtick.color'] = self.colors['text_secondary']
        plt.rcParams['ytick.color'] = self.colors['text_secondary']
        plt.rcParams['font.size'] = 9
        
        if hasattr(self, 'canvas'):
            self.update_graph()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('temperature_monitor_settings.json'):
                with open('temperature_monitor_settings.json', 'r') as f:
                    settings = json.load(f)
                    self.critical_temp = settings.get('critical_temp', 30)
                    self.warning_temp = settings.get('warning_temp', 25)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
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
        """Setup the main user interface"""
        # Clear existing UI
        for widget in self.bg_canvas.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.destroy()
        
        # Calculate responsive padding
        base_padding = int(20 * self.scaling_factors['padding_scale'])
        
        # Create main frame
        main_frame = ttk.Frame(self.bg_canvas, style='Modern.TFrame', padding=f"{base_padding}")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header section
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, base_padding))
        header_frame.columnconfigure(0, weight=1)
        
        # Title with centered layout
        title_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        title_frame.grid(row=0, column=0, sticky='ew')
        title_frame.columnconfigure(0, weight=1)
        
        # Title font size
        title_font_size = int(20 * self.scaling_factors['font_scale'])
        
        # Left side - Title
        title_label = ttk.Label(title_frame, text="Enhanced Temperature Monitor", 
                               background=self.colors['surface'],
                               foreground=self.colors['text_primary'],
                               font=("Segoe UI", title_font_size, "bold"))
        title_label.grid(row=0, column=0, sticky='w')
        
        # Right side - Theme toggle and Live Log button
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
        
        # Main content area
        content_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        content_frame.grid(row=1, column=0, sticky='nsew')
        content_frame.columnconfigure(0, weight=7)  # Left column
        content_frame.columnconfigure(1, weight=3)  # Right column
        content_frame.rowconfigure(0, weight=1)
        
        # Left column - Metrics and Graph
        left_column = ttk.Frame(content_frame, style='Modern.TFrame')
        left_column.grid(row=0, column=0, sticky='nsew', padx=(0, base_padding//2))
        left_column.columnconfigure(0, weight=1)
        left_column.rowconfigure(1, weight=1)
        
        # Metrics cards
        metrics_frame = ttk.Frame(left_column, style='Modern.TFrame')
        metrics_frame.grid(row=0, column=0, sticky='ew', pady=(0, base_padding))
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)
        metrics_frame.columnconfigure(2, weight=1)
        
        # Card padding
        card_padding = int(20 * self.scaling_factors['padding_scale'])
        
        # Current temperature card
        current_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding=f"{card_padding}")
        current_card.grid(row=0, column=0, sticky='nsew', padx=(0, base_padding//2))
        
        ttk.Label(current_card, text="Current Temperature", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_secondary'],
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.CENTER)
        
        self.current_temp_var = tk.StringVar(value="--°C")
        temp_font_size = int(24 * self.scaling_factors['font_scale'])
        self.current_temp_display = ttk.Label(current_card, textvariable=self.current_temp_var, 
                                             background=self.colors['card_bg'],
                                             foreground=self.colors['primary'],
                                             font=("Segoe UI", temp_font_size, "bold"))
        self.current_temp_display.pack(anchor=tk.CENTER, pady=(8, 0))
        
        # Source card
        source_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding=f"{card_padding}")
        source_card.grid(row=0, column=1, sticky='nsew', padx=(base_padding//2, base_padding//2))
        
        ttk.Label(source_card, text="Temperature Source", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_secondary'],
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.CENTER)
        
        self.source_var = tk.StringVar(value="Unknown")
        source_label = ttk.Label(source_card, textvariable=self.source_var,
                                background=self.colors['card_bg'],
                                foreground=self.colors['text_primary'],
                                font=("Segoe UI", 12, "bold"))
        source_label.pack(anchor=tk.CENTER, pady=(8, 0))
        
        # Status card
        status_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding=f"{card_padding}")
        status_card.grid(row=0, column=2, sticky='nsew', padx=(base_padding//2, 0))
        
        ttk.Label(status_card, text="Status", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_secondary'],
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.CENTER)
        
        self.status_var = tk.StringVar(value="Initializing...")
        status_font_size = int(12 * self.scaling_factors['font_scale'])
        status_label = ttk.Label(status_card, textvariable=self.status_var,
                                background=self.colors['card_bg'],
                                foreground=self.colors['text_primary'],
                                font=("Segoe UI", status_font_size, "bold"))
        status_label.pack(anchor=tk.CENTER, pady=(8, 0))
        
        # Graph frame
        graph_frame = ttk.Frame(left_column, style='Card.TFrame', padding="15")
        graph_frame.grid(row=1, column=0, sticky='nsew')
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.update_graph_theme()
        
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.tight_layout(pad=4.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        
        # Right column - Controls and Settings
        right_column = ttk.Frame(content_frame, style='Modern.TFrame')
        right_column.grid(row=0, column=1, sticky='nsew', padx=(base_padding//2, 0))
        right_column.columnconfigure(0, weight=1)
        
        # Alert Controls Section
        alert_frame = ttk.LabelFrame(right_column, text="ALERT CONTROLS", 
                                    style='Card.TLabelframe', padding="15")
        alert_frame.grid(row=0, column=0, sticky='ew', pady=(0, base_padding))
        
        # Alert status
        alert_status_frame = ttk.Frame(alert_frame, style='Card.TFrame')
        alert_status_frame.grid(row=0, column=0, sticky='ew', pady=(0, 12))
        
        ttk.Label(alert_status_frame, text="Alert Status:", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_primary'],
                 font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w')
        
        self.alert_status_var = tk.StringVar(value="Alerts: ACTIVE")
        alert_status_label = ttk.Label(alert_status_frame, textvariable=self.alert_status_var,
                                      background=self.colors['card_bg'],
                                      foreground=self.colors['success'],
                                      font=('Segoe UI', 11, 'bold'))
        alert_status_label.grid(row=1, column=0, sticky='w', pady=(5, 0))
        
        # Alert control buttons
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
        
        # Monitoring Controls
        monitor_frame = ttk.LabelFrame(right_column, text="MONITORING CONTROLS", 
                                      style='Card.TLabelframe', padding="15")
        monitor_frame.grid(row=1, column=0, sticky='ew', pady=(0, base_padding))
        
        # Refresh rate control
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
                                    state="readonly")
        refresh_combo.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        refresh_button = ttk.Button(refresh_frame, text="Refresh Now", 
                                   command=self.manual_refresh, 
                                   style='Primary.TButton')
        refresh_button.grid(row=2, column=0, sticky='ew')
        
        # Utility buttons
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
        
        # Temperature Settings
        settings_frame = ttk.LabelFrame(right_column, text="TEMPERATURE SETTINGS", 
                                       style='Card.TLabelframe', padding="15")
        settings_frame.grid(row=2, column=0, sticky='ew', pady=(0, base_padding))
        
        # Warning temperature
        warning_frame = ttk.Frame(settings_frame, style='Card.TFrame')
        warning_frame.grid(row=0, column=0, sticky='ew', pady=(0, 12))
        
        ttk.Label(warning_frame, text="Warning Threshold (°C):", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_primary'],
                 font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w')
        
        self.warning_var = tk.StringVar(value=str(self.warning_temp))
        warning_entry = ttk.Entry(warning_frame, textvariable=self.warning_var, 
                                 width=8,
                                 font=('Segoe UI', 10),
                                 justify=tk.CENTER)
        warning_entry.grid(row=1, column=0, sticky='w', pady=(8, 0))
        
        # Critical temperature
        critical_frame = ttk.Frame(settings_frame, style='Card.TFrame')
        critical_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        ttk.Label(critical_frame, text="Critical Threshold (°C):", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_primary'],
                 font=('Segoe UI', 9)).grid(row=0, column=0, sticky='w')
        
        self.critical_var = tk.StringVar(value=str(self.critical_temp))
        critical_entry = ttk.Entry(critical_frame, textvariable=self.critical_var, 
                                  width=8,
                                  font=('Segoe UI', 10),
                                  justify=tk.CENTER)
        critical_entry.grid(row=1, column=0, sticky='w', pady=(8, 0))
        
        # Save Settings button
        update_button = ttk.Button(settings_frame, text="Save Settings", 
                                  command=self.update_settings, 
                                  style='Primary.TButton')
        update_button.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        # Footer
        footer_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        footer_frame.grid(row=2, column=0, sticky='ew', pady=(base_padding, 0))
        footer_frame.columnconfigure(0, weight=1)
        
        # Last update
        self.last_update_var = tk.StringVar(value="Last update: --")
        last_update_label = ttk.Label(footer_frame, textvariable=self.last_update_var,
                                     background=self.colors['surface'],
                                     foreground=self.colors['text_secondary'],
                                     font=("Segoe UI", 9))
        last_update_label.grid(row=0, column=0, sticky='w')
        
        # Current time
        self.time_var = tk.StringVar(value="--:--:--")
        time_label = ttk.Label(footer_frame, textvariable=self.time_var,
                              background=self.colors['surface'],
                              foreground=self.colors['text_secondary'],
                              font=("Segoe UI", 9))
        time_label.grid(row=0, column=1, sticky='w', padx=(20, 0))
        
        # Next email
        self.next_email_var = tk.StringVar(value="Next report: --")
        next_email_label = ttk.Label(footer_frame, textvariable=self.next_email_var,
                                    background=self.colors['surface'],
                                    foreground=self.colors['text_secondary'],
                                    font=("Segoe UI", 9))
        next_email_label.grid(row=0, column=2, sticky='e')
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.root.update_idletasks()
    
    def show_live_log(self):
        """Show the Live Log window"""
        LiveLogWindow(self.root, self.log_manager, self.theme_manager, self.responsive_design)
    
    def start_realtime_updates(self):
        """Start real-time temperature updates"""
        self.is_monitoring = True
        self.update_time_display()
        self.monitor_thread = threading.Thread(target=self.monitor_temperature, daemon=True)
        self.monitor_thread.start()
    
    def start_email_scheduler(self):
        """Start the email scheduler"""
        self.email_thread = threading.Thread(target=self.email_scheduler, daemon=True)
        self.email_thread.start()
    
    def update_time_display(self):
        """Update the current time display"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_var.set(f"Time: {current_time}")
        
        # Update next email report time
        next_email_time = self.last_email_time if hasattr(self, 'last_email_time') else 0
        next_email_time += 3600  # 1 hour interval
        time_until_next = next_email_time - time.time()
        
        if time_until_next > 0:
            minutes = int(time_until_next // 60)
            seconds = int(time_until_next % 60)
            self.next_email_var.set(f"Next report: {minutes:02d}:{seconds:02d}")
        else:
            self.next_email_var.set("Next report: Soon")
        
        self.root.after(1000, self.update_time_display)
    
    def monitor_temperature(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Get primary temperature with priority-based fallback
                current_temp = self.temp_reader.get_primary_temperature()
                temp_source = self.temp_reader.get_temperature_source()
                
                if current_temp is not None:
                    # Update statistics
                    if current_temp < self.min_temp:
                        self.min_temp = current_temp
                    if current_temp > self.max_temp:
                        self.max_temp = current_temp
                    
                    # Update display
                    self.root.after(0, self.update_display, current_temp, temp_source)
                    
                    # Update history
                    self.temp_history.append(current_temp)
                    self.time_history.append(time.time())
                    
                    # Intelligent logging
                    status = self.get_temperature_status(current_temp)
                    is_alert = status in ["Warning", "Critical"]
                    
                    self.log_manager.log_temperature(
                        temp=current_temp,
                        source=temp_source,
                        status=status,
                        is_alert=is_alert
                    )
                    
                    # Handle alerts with 1-hour cooldown
                    if self.alert_monitoring_active:
                        self.handle_temperature_alert(current_temp, temp_source, status)
                
                else:
                    # No temperature data
                    self.root.after(0, self.update_display, None, "No sensor data")
                    
                    self.log_manager.log_system_event(
                        "Sensor Error",
                        "No temperature data available"
                    )
                
                # Get refresh rate
                try:
                    refresh_delay = max(1, float(self.refresh_rate_var.get()))
                except:
                    refresh_delay = 2
                
                time.sleep(refresh_delay)
            
            except Exception as e:
                print(f"Monitoring error: {e}")
                self.log_manager.log_system_event("Monitoring Error", str(e))
                time.sleep(5)
    
    def handle_temperature_alert(self, temp, source, status):
        """Handle temperature alerts with 1-hour cooldown"""
        current_time = time.time()
        
        if status == "Critical":
            # Check 1-hour cooldown
            if current_time - self.last_critical_alert > self.warning_cooldown:
                # Send desktop notification
                self.root.after(0, self.send_desktop_notification,
                              "🔥 CRITICAL TEMPERATURE ALERT!",
                              f"Temperature: {temp:.1f}°C\nSource: {source}",
                              temp)
                
                # Check if we should send email (1-hour cooldown)
                if self.log_manager.should_send_alert_email("CRITICAL", temp):
                    self.send_alert_email("CRITICAL", temp, source)
                
                self.last_critical_alert = current_time
        
        elif status == "Warning":
            # Check 1-hour cooldown
            if current_time - self.last_warning_alert > self.warning_cooldown:
                # Send desktop notification
                self.root.after(0, self.send_desktop_notification,
                              "⚠️ HIGH TEMPERATURE WARNING",
                              f"Temperature: {temp:.1f}°C\nSource: {source}",
                              temp)
                
                # Check if we should send email (1-hour cooldown)
                if self.log_manager.should_send_alert_email("WARNING", temp):
                    self.send_alert_email("WARNING", temp, source)
                
                self.last_warning_alert = current_time
    
    def send_desktop_notification(self, title, message, temp):
        """Send system desktop notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=10,
                app_name="Temperature Monitor"
            )
            print(f"Desktop notification sent: {title}")
            
        except Exception as e:
            print(f"Error sending desktop notification: {e}")
        
        # Play sound alert
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            pass
    
    def send_alert_email(self, alert_type, temp, source):
        """Send alert email for critical/warning temperatures"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['receiver_email']
            
            if alert_type == "CRITICAL":
                msg['Subject'] = f"🚨 CRITICAL Temperature Alert - {temp:.1f}°C"
                color = "🔴"
                urgency = "IMMEDIATE ACTION REQUIRED"
            else:
                msg['Subject'] = f"⚠️ Warning Temperature Alert - {temp:.1f}°C"
                color = "🟡"
                urgency = "Monitor Closely"
            
            # Build email body
            body = f"""
{color} TEMPERATURE ALERT
=====================================

Alert Type: {alert_type} {color}
Temperature: {temp:.1f}°C
Source: {source}
Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Urgency: {urgency}

Current Thresholds:
• Warning: {self.warning_temp}°C
• Critical: {self.critical_temp}°C

Recommended Actions:
1. Check cooling system
2. Ensure proper ventilation
3. Monitor temperature trends
4. Consider reducing system load

This is an automated alert from the Temperature Monitoring System.
The system will continue to monitor and send updates every hour if the issue persists.

Device: {os.environ.get('COMPUTERNAME', 'Unknown Device')}
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ {alert_type} alert email sent")
            
            self.log_manager.log_system_event(f"{alert_type} Alert Email", f"Sent for {temp:.1f}°C")
            
            return True
        
        except Exception as e:
            print(f"❌ Error sending alert email: {e}")
            self.log_manager.log_system_event("Email Error", f"Failed to send {alert_type} alert: {e}")
            return False
    
    def send_test_email(self):
        """Send a test email"""
        try:
            success = self.send_alert_email("TEST", 25.0, "Test Source")
            if success:
                messagebox.showinfo("Success", "Test email sent successfully!")
            else:
                messagebox.showerror("Error", "Failed to send test email")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send test email: {str(e)}")
    
    def email_scheduler(self):
        """Email scheduler for periodic reports"""
        self.last_email_time = time.time()
        
        while self.is_monitoring:
            try:
                current_time = time.time()
                
                # Send email every hour
                if current_time - self.last_email_time >= 3600:
                    print("🕒 Sending scheduled email report...")
                    self.send_daily_report()
                    self.last_email_time = current_time
                    
                    # Reset min/max for next period
                    self.min_temp = float('inf')
                    self.max_temp = float('-inf')
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Email scheduler error: {e}")
                time.sleep(60)
    
    def send_daily_report(self):
        """Send daily temperature report"""
        try:
            current_temp = self.temp_reader.get_primary_temperature()
            source = self.temp_reader.get_temperature_source()
            
            if current_temp is None:
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['receiver_email']
            msg['Subject'] = f"Temperature Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Build email body
            body = f"""
Temperature Monitoring Report
=====================================

Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Current Status:
• Current Temperature: {current_temp:.1f}°C
• Temperature Source: {source}
• Status: {self.get_temperature_status(current_temp)}

Hourly Statistics:
• Minimum Temperature: {self.min_temp if self.min_temp != float('inf') else 'N/A':.1f}°C
• Maximum Temperature: {self.max_temp if self.max_temp != float('-inf') else 'N/A':.1f}°C

Threshold Settings:
• Warning Threshold: {self.warning_temp}°C
• Critical Threshold: {self.critical_temp}°C

This is an automated report from the Temperature Monitoring System.
No response is required unless alerts are indicated above.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Daily report sent at {datetime.datetime.now().strftime('%H:%M:%S')}")
            
            self.log_manager.log_system_event("Daily Report", "Email report sent")
            
            return True
        
        except Exception as e:
            print(f"❌ Error sending daily report: {e}")
            self.log_manager.log_system_event("Report Error", f"Failed to send daily report: {e}")
            return False
    
    def update_display(self, temp, source):
        """Update the UI display"""
        if temp is not None:
            self.current_temp_var.set(f"{temp:.1f}°C")
            self.source_var.set(source)
            
            # Update status
            status = self.get_temperature_status(temp)
            self.status_var.set(f"{status}")
            
            # Update colors based on status
            if status == "Critical":
                self.current_temp_display.config(foreground=self.colors['error'])
                self.status_var.set(f"🔴 {status}")
            elif status == "Warning":
                self.current_temp_display.config(foreground=self.colors['warning'])
                self.status_var.set(f"🟡 {status}")
            else:
                self.current_temp_display.config(foreground=self.colors['success'])
                self.status_var.set(f"🟢 {status}")
        else:
            self.current_temp_var.set("--°C")
            self.source_var.set(source)
            self.status_var.set("No data")
            self.current_temp_display.config(foreground=self.colors['text_secondary'])
        
        # Update time
        update_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.last_update_var.set(f"Updated: {update_time}")
        
        # Update graph
        self.update_graph()
    
    def get_temperature_status(self, temp):
        """Get temperature status string"""
        if temp is None:
            return "Unknown"
        elif temp >= self.critical_temp:
            return "Critical"
        elif temp >= self.warning_temp:
            return "Warning"
        else:
            return "Normal"
    
    def update_graph(self):
        """Update the temperature history graph"""
        self.ax.clear()
        
        if len(self.temp_history) > 0:
            # Convert time history to minutes
            if len(self.time_history) > 0:
                start_time = self.time_history[0]
                time_minutes = [(t - start_time) / 60 for t in self.time_history]
            else:
                time_minutes = list(range(len(self.temp_history)))
            
            # Plot temperature history
            self.ax.plot(time_minutes, self.temp_history, 
                        color=self.colors['primary'], 
                        linewidth=2, 
                        marker='o',
                        markersize=3,
                        label="Temperature (°C)")
            
            # Add threshold lines
            self.ax.axhline(y=self.warning_temp, color='yellow', linestyle='--', 
                          alpha=0.6, label=f'Warning ({self.warning_temp}°C)')
            self.ax.axhline(y=self.critical_temp, color='red', linestyle='--', 
                          alpha=0.6, label=f'Critical ({self.critical_temp}°C)')
            
            # Labels and title
            self.ax.set_xlabel('Time (Minutes)', fontsize=10, fontweight='bold')
            self.ax.set_ylabel('Temperature (°C)', fontsize=10, fontweight='bold')
            self.ax.set_title('Temperature History', fontsize=12, fontweight='bold', pad=20)
            
            # Legend
            self.ax.legend(fontsize=9, framealpha=0.9)
            
            # Grid
            self.ax.grid(True, alpha=0.2, linestyle='-')
            
            # Auto-adjust y-axis
            if self.temp_history:
                current_min = min(self.temp_history)
                current_max = max(self.temp_history)
                padding = max(2, (current_max - current_min) * 0.1)
                self.ax.set_ylim(max(0, current_min - padding), current_max + padding)
        
        else:
            # No data message
            self.ax.text(0.5, 0.5, 'Collecting temperature data...', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=self.ax.transAxes, fontsize=11,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['hover']))
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        
        # Note about temperature adjustment
        note_text = "Note: Temperatures are adjusted for ambient conditions"
        self.ax.text(0.5, -0.15, note_text, transform=self.ax.transAxes, 
                    fontsize=8, color=self.colors['text_secondary'],
                    horizontalalignment='center', verticalalignment='top',
                    style='italic')
        
        self.fig.tight_layout(rect=[0, 0.05, 1, 0.95])
        self.canvas.draw()
    
    def start_alert_monitoring(self):
        """Start alert monitoring"""
        self.alert_monitoring_active = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.alert_status_var.set("Alerts: ACTIVE")
        self.alert_status_var.set("Alerts: ACTIVE")
        
        self.log_manager.log_system_event("Alert Monitoring", "Enabled")
        
        messagebox.showinfo("Alerts Enabled", "Temperature alert monitoring is now active!")
    
    def stop_alert_monitoring(self):
        """Stop alert monitoring"""
        self.alert_monitoring_active = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.alert_status_var.set("Alerts: INACTIVE")
        
        self.log_manager.log_system_event("Alert Monitoring", "Disabled")
        
        messagebox.showinfo("Alerts Disabled", "Temperature alert monitoring is now inactive.")
    
    def manual_refresh(self):
        """Force an immediate temperature refresh"""
        current_temp = self.temp_reader.get_primary_temperature()
        source = self.temp_reader.get_temperature_source()
        
        if current_temp is not None:
            self.update_display(current_temp, source)
    
    def show_sensor_info(self):
        """Show detailed sensor information"""
        info = self.temp_reader.get_all_sensor_info()
        
        # Create a centered popup
        popup = tk.Toplevel(self.root)
        popup.title("Sensor Information")
        
        # Center the popup
        popup_width = 800
        popup_height = 600
        self.responsive_design.center_window(popup, popup_width, popup_height)
        
        popup.minsize(600, 400)
        
        # Set background
        if self.colors['background'] == '#0f172a':
            bg_color = '#1e293b'
            text_bg = '#1e293b'
        else:
            bg_color = '#ffffff'
            text_bg = '#ffffff'
        
        popup.configure(bg=bg_color)
        
        # Make window modal
        popup.transient(self.root)
        popup.grab_set()
        
        # Create scrollable text area
        text_frame = ttk.Frame(popup, style='Modern.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            bg=text_bg,
            fg=self.colors['text_primary'],
            font=("Consolas", 9),
            state='normal'
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Insert sensor info
        text_widget.insert(tk.END, info)
        text_widget.config(state='disabled')
        
        # Close button
        button_frame = ttk.Frame(popup, style='Modern.TFrame')
        button_frame.pack(pady=(0, 20))
        
        close_button = ttk.Button(button_frame, text="Close", 
                                 command=popup.destroy,
                                 style='Primary.TButton')
        close_button.pack()
    
    def update_settings(self):
        """Update temperature threshold settings"""
        try:
            new_warning = float(self.warning_var.get())
            new_critical = float(self.critical_var.get())
            
            if new_warning >= new_critical:
                messagebox.showerror("Error", "Warning temperature must be lower than critical temperature")
                return
            
            self.warning_temp = new_warning
            self.critical_temp = new_critical
            self.save_settings()
            
            self.log_manager.log_system_event("Settings Update", 
                                            f"Thresholds updated: Warning={new_warning}°C, Critical={new_critical}°C")
            
            messagebox.showinfo("Success", "Temperature settings updated successfully")
        
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for temperature thresholds")
    
    def on_closing(self):
        """Clean up when closing"""
        self.is_monitoring = False
        
        self.log_manager.log_system_event("System Shutdown", "Temperature Monitor shutting down")
        
        self.save_settings()
        self.root.destroy()