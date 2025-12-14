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
        self.root.title("Storage Temperature Monitor")
        
        # Initialize responsive design with fullscreen using geometry and zoomed state
        self.responsive_design = ResponsiveDesign(root)
        self.scaling_factors = self.responsive_design.get_scaling_factors()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_theme()
        
        # Monitoring state
        self.is_monitoring = True
        self.alert_monitoring_active = True
        self.monitor_thread = None
        self.email_thread = None
        
        # Alert tracking
        self.last_warning_time = 0
        self.warning_cooldown = 30
        self.last_email_time = 0
        self.email_interval = 3600  
        
        # Temperature thresholds 
        self.critical_temp = 30  
        self.warning_temp = 25   
        
        # Temperature history for graphing
        self.temp_history = deque(maxlen=50)
        self.time_history = deque(maxlen=50)
        
        # For email statistics
        self.min_temp = float('inf')
        self.max_temp = float('-inf')
        
        # Storage temperatures storage
        self.storage_temperatures = {}
        
        # Storage temperature reader
        self.temp_reader = StorageTemperatureReader()
        
        # Email configuration
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'nxpisian@gmail.com',
            'sender_password': 'aqkz uykr cmfu oqbm',
            'receiver_email': 'supercompnxp@gmail.com, ian.tolentino.bp@j-display.com, ferrerasroyce@gmail.com'
        }

        # Initialize log manager for persistent logging
        self.log_manager = LogManager()
        
        # Create background and setup UI
        self.setup_background()
        self.setup_modern_styles()
        self.load_settings()
        self.setup_ui()
        
        # Run OpenHardwareMonitor before starting monitoring
        self.start_openhardware_monitor()
        
        self.start_realtime_updates()
        self.start_email_scheduler()
        
        # Start automatic logging when program runs
        self.log_manager.log_temperature("System", "N/A", "Storage Temperature Monitor started - logging initialized")
    
    def start_openhardware_monitor(self):
        """Start OpenHardwareMonitor before monitoring temperatures"""
        print("🚀 Initializing OpenHardwareMonitor...")
        success = self.temp_reader.run_openhardware_monitor()
        
        if success:
            print("✅ OpenHardwareMonitor is ready")
            # Give it a moment to fully initialize
            time.sleep(3)
            # Re-initialize WMI connection after OHM starts
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
        """Setup the responsive gradient background"""
        # Create a canvas that covers the entire window
        self.bg_canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
            bg=self.colors['background']
        )
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Update the canvas size after window is created
        self.root.update()
        
        # Create responsive gradient background
        self.responsive_bg = ResponsiveGradientBackground(
            self.bg_canvas, 
            self.root.winfo_width(), 
            self.root.winfo_height(),
            self.colors
        )
        
        # Bind to window resize events
        self.root.bind('<Configure>', self.on_resize)
    
    def on_resize(self, event):
        """Handle window resize events - responsive design"""
        if event.widget == self.root:
            # Update background size
            self.responsive_bg.width = event.width
            self.responsive_bg.height = event.height
            self.responsive_bg.create_responsive_background()
            
            # Update scaling factors when window is resized
            self.scaling_factors = self.responsive_design.get_scaling_factors()
    
    def setup_modern_styles(self):
        """Configure modern professional styling with theme support"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern styles with current theme
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
        
        # Modern button styles with responsive scaling
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
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['input_bg'],
                       foreground=self.colors['input_fg'],
                       borderwidth=1,
                       focusthickness=2,
                       focuscolor=self.colors['primary'])
        
        # Redesigned combobox for better visibility
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
        """Toggle between dark and light themes"""
        self.colors = self.theme_manager.toggle_theme()
        self.update_theme()
    
    def update_theme(self):
        """Update the entire UI with new theme colors"""
        # Update background
        self.responsive_bg.update_theme(self.colors)
        
        # Update matplotlib graph theme
        self.update_graph_theme()
        
        # Recreate the UI with new theme
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
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        
        # Redraw graph if it exists
        if hasattr(self, 'canvas'):
            self.update_graph()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('temperature_monitor_settings.json'):
                with open('temperature_monitor_settings.json', 'r') as f:
                    settings = json.load(f)
                    self.critical_temp = settings.get('critical_temp', 30)
                    self.warning_temp = settings.get('warning_temp', 27)
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
        
        # Create main frame on top of background canvas
        main_frame = ttk.Frame(self.bg_canvas, style='Modern.TFrame', padding=f"{base_padding}")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsiveness - critical for proper scaling
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header section - Centered and professional
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, base_padding))
        header_frame.columnconfigure(0, weight=1)
        
        # Title with centered layout
        title_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        title_frame.grid(row=0, column=0, sticky='ew')
        title_frame.columnconfigure(0, weight=1)
        
        # Calculate responsive font sizes
        title_font_size = int(20 * self.scaling_factors['font_scale'])
        
        # Left side - Title
        title_label = ttk.Label(title_frame, text="Storage Temperature Monitor", 
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
        
        # Main content area - Two column layout with proper weights
        content_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        content_frame.grid(row=1, column=0, sticky='nsew')
        # Left column gets more weight (70%), right column less (30%)
        content_frame.columnconfigure(0, weight=7)  # Left column (70%)
        content_frame.columnconfigure(1, weight=3)  # Right column (30%)
        content_frame.rowconfigure(0, weight=1)
        
        # Left column - Metrics and Graph (70% width)
        left_column = ttk.Frame(content_frame, style='Modern.TFrame')
        left_column.grid(row=0, column=0, sticky='nsew', padx=(0, base_padding//2))
        left_column.columnconfigure(0, weight=1)
        left_column.rowconfigure(1, weight=1)  # Graph gets most space
        
        # Metrics cards in a compact row
        metrics_frame = ttk.Frame(left_column, style='Modern.TFrame')
        metrics_frame.grid(row=0, column=0, sticky='ew', pady=(0, base_padding))
        # Equal weight for all three metric cards
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)
        metrics_frame.columnconfigure(2, weight=1)
        
        # Calculate card padding
        card_padding = int(20 * self.scaling_factors['padding_scale'])
        
        # Average temperature card
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
        
        # Max temperature card
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
        
        # Sensor status card
        sensor_card = ttk.Frame(metrics_frame, style='Card.TFrame', padding=f"{card_padding}")
        sensor_card.grid(row=0, column=2, sticky='nsew', padx=(base_padding//2, 0))
        
        ttk.Label(sensor_card, text="Sensor Status", 
                 background=self.colors['card_bg'],
                 foreground=self.colors['text_secondary'],
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.CENTER)
        
        # Sensor connection status
        self.sensor_status_var = tk.StringVar()
        status_font_size = int(12 * self.scaling_factors['font_scale'])
        sensor_status_label = ttk.Label(sensor_card, textvariable=self.sensor_status_var,
                                  background=self.colors['card_bg'],
                                  foreground=self.colors['text_primary'],
                                  font=("Segoe UI", status_font_size, "bold"))
        sensor_status_label.pack(anchor=tk.CENTER, pady=(8, 0))
        
        # System status
        self.status_var = tk.StringVar(value="Initializing...")
        small_font_size = int(9 * self.scaling_factors['font_scale'])
        status_label = ttk.Label(sensor_card, textvariable=self.status_var,
                            background=self.colors['card_bg'],
                            foreground=self.colors['text_secondary'],
                            font=("Segoe UI", small_font_size))
        status_label.pack(anchor=tk.CENTER, pady=(4, 0))
        
        self.update_sensor_status()
        
        # Graph frame - takes most space in left column
        graph_frame = ttk.Frame(left_column, style='Card.TFrame', padding="15")
        graph_frame.grid(row=1, column=0, sticky='nsew')
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        
        # Create professional matplotlib figure with current theme
        self.update_graph_theme()
        
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.tight_layout(pad=4.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        
        # Right column - Controls and Settings (30% width)
        right_column = ttk.Frame(content_frame, style='Modern.TFrame')
        right_column.grid(row=0, column=1, sticky='nsew', padx=(base_padding//2, 0))
        right_column.columnconfigure(0, weight=1)
        
        # Alert Controls Section
        alert_frame = ttk.LabelFrame(right_column, text="ALERT CONTROLS", 
                                style='Card.TLabelframe', padding="15")
        alert_frame.grid(row=0, column=0, sticky='ew', pady=(0, base_padding))
        
        # Alert status display
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
        
        # Alert control buttons in a row
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
        
        # Monitoring Controls Section - Improved spacing and sizing
        monitor_frame = ttk.LabelFrame(right_column, text="MONITORING CONTROLS", 
                                  style='Card.TLabelframe', padding="15")
        monitor_frame.grid(row=1, column=0, sticky='ew', pady=(0, base_padding))
        
        # Refresh rate control - Improved layout
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
        
        # Utility buttons grid - Improved spacing
        utils_frame = ttk.Frame(monitor_frame, style='Card.TFrame')
        utils_frame.grid(row=1, column=0, sticky='ew', pady=(15, 0))
        
        # First row of utility buttons
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
        
        # Temperature Settings Section
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
                             style='Modern.TEntry',
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
                              style='Modern.TEntry',
                              font=('Segoe UI', 10),
                              justify=tk.CENTER)
        critical_entry.grid(row=1, column=0, sticky='w', pady=(8, 0))
        
        # Save Settings button
        update_button = ttk.Button(settings_frame, text="Save Settings", 
                              command=self.update_settings, 
                              style='Primary.TButton')
        update_button.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        # Footer with status information
        footer_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        footer_frame.grid(row=2, column=0, sticky='ew', pady=(base_padding, 0))
        footer_frame.columnconfigure(0, weight=1)
        
        # Left footer - Update time
        self.last_update_var = tk.StringVar(value="Last update: --")
        last_update_label = ttk.Label(footer_frame, textvariable=self.last_update_var,
                                 background=self.colors['surface'],
                                 foreground=self.colors['text_secondary'],
                                 font=("Segoe UI", 9))
        last_update_label.grid(row=0, column=0, sticky='w')
        
        # Center footer - Current time
        self.time_var = tk.StringVar(value="--:--:--")
        time_label = ttk.Label(footer_frame, textvariable=self.time_var,
                          background=self.colors['surface'],
                          foreground=self.colors['text_secondary'],
                          font=("Segoe UI", 9))
        time_label.grid(row=0, column=1, sticky='w', padx=(20, 0))
        
        # Right footer - Next email
        self.next_email_var = tk.StringVar(value="Next report: --")
        next_email_label = ttk.Label(footer_frame, textvariable=self.next_email_var,
                                background=self.colors['surface'],
                                foreground=self.colors['text_secondary'],
                                font=("Segoe UI", 9))
        next_email_label.grid(row=0, column=2, sticky='e')
        
        # Configure grid weights for resizing - essential for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Force update to ensure proper rendering
        self.root.update_idletasks()
    
    def show_live_log(self):
        """Show the Live Log window"""
        LiveLogWindow(self.root, self.log_manager, self.theme_manager, self.responsive_design)
    
    def update_sensor_status(self):
        """Update sensor status display"""
        if self.temp_reader.ohm_available:
            status = "✅ Connected"
            color = self.colors['success']
        else:
            status = "❌ Not Available"
            color = self.colors['error']
        
        self.sensor_status_var.set(status)
    
    def show_sensor_info(self):
        """Show detailed sensor information"""
        info = self.temp_reader.get_detailed_sensor_info()
        messagebox.showinfo("Storage Sensor Information", info)
    
    def start_realtime_updates(self):
        """Start real-time temperature updates immediately"""
        self.is_monitoring = True
        self.update_time_display()
        self.monitor_thread = threading.Thread(target=self.monitor_temperature, daemon=True)
        self.monitor_thread.start()
    
    def start_email_scheduler(self):
        """Start the email scheduler thread"""
        self.email_thread = threading.Thread(target=self.email_scheduler, daemon=True)
        self.email_thread.start()
    
    def update_time_display(self):
        """Update the current time display"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_var.set(f"Time: {current_time}")
        
        # Update next email report time
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
        """Get system usage info"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            return cpu_percent, memory_percent
        except:
            return None, None
    
    def send_desktop_notification(self, title, message, temp):
        """Send system desktop notification"""
        try:
            notification.notify(
                title=title,
                message=f"{message}\nHottest storage: {temp:.1f}°C",
                timeout=10,
                app_name="Storage Temperature Monitor"
            )
            print(f"Desktop notification sent: {title}")
            
            # Log the notification
            self.log_manager.log_temperature("Alert", temp, f"Alert: {title} - {message}")
        
        except Exception as e:
            print(f"Error sending desktop notification: {e}")
        
        # Play sound alert
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            pass
    
    def send_email_report(self):
        """Send email report with temperature statistics"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['receiver_email']
            msg['Subject'] = f"Storage Temperature Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Get current temperatures
            current_temps = self.storage_temperatures
            current_max = self.temp_reader.get_max_storage_temperature()
            
            # Prepare actions based on temperature
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
            
            # Build email body
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
            
            # Connect to server and send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email report sent successfully at {datetime.datetime.now().strftime('%H:%M:%S')}")
            
            # Log email sent
            self.log_manager.log_temperature("Email", current_max if current_max else 0, "Scheduled email report sent")
            
            return True
        
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            
            # Log email error
            self.log_manager.log_temperature("Error", 0, f"Failed to send email: {e}")
            
            return False
    
    def send_test_email(self):
        """Send a test email"""
        try:
            success = self.send_email_report()
            if success:
                messagebox.showinfo("Success", "Test email sent successfully!")
            else:
                messagebox.showerror("Error", "Failed to send test email. Check your email configuration.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send test email: {str(e)}")
    
    def email_scheduler(self):
        """Email scheduler that sends reports every 5 minutes"""
        while self.is_monitoring:
            try:
                current_time = time.time()
                
                # Send email every 5 minutes
                if current_time - self.last_email_time >= self.email_interval:
                    if self.storage_temperatures:  # Only send if we have data
                        print("🕒 Sending scheduled email report...")
                        self.send_email_report()
                        self.last_email_time = current_time
                    
                    # Reset min/max for next period
                    self.min_temp = float('inf')
                    self.max_temp = float('-inf')
                
                time.sleep(30)  # Check every 30 seconds
            
            except Exception as e:
                print(f"Email scheduler error: {e}")
                time.sleep(60)
    
    def update_graph(self):
        """Update the temperature history graph with professional design"""
        self.ax.clear()
        
        if len(self.temp_history) > 0:
            time_minutes = [t/60 for t in self.time_history]
            
            # Create colored line segments based on temperature thresholds
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
            
            # X-axis label now clearly visible
            self.ax.set_xlabel('Time (Minutes)', fontsize=10, fontweight='bold')
            
            # Add "Temperature Trend" title
            self.ax.set_title('Temperature', 
                            fontsize=12, fontweight='bold', pad=20)
            
            # Professional grid
            self.ax.grid(True, alpha=0.2, linestyle='-')
            
            # Set professional y-axis limits
            if self.temp_history:
                current_min = min(self.temp_history)
                current_max = max(self.temp_history)
                padding = max(2, (current_max - current_min) * 0.1)
                self.ax.set_ylim(max(0, current_min - padding), current_max + padding)
            
            # Professional spine styling
            for spine in self.ax.spines.values():
                spine.set_color(self.colors['border'])
                spine.set_linewidth(1)
        
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
        """Get color based on temperature value"""
        if temperature >= critical_temp:
            return 'red'  # Critical
        elif temperature >= warning_temp:
            return 'yellow'  # Warning
        else:
            return 'blue'  # Normal
    
    def monitor_temperature(self):
        """Main monitoring loop"""
        start_time = time.time()
        
        while self.is_monitoring:
            try:
                # Get all storage temperatures
                self.storage_temperatures = self.temp_reader.get_storage_temperatures()
                max_temp = self.temp_reader.get_max_storage_temperature()
                avg_temp = self.temp_reader.get_average_storage_temperature()
                cpu_percent, memory_percent = self.get_system_info()
                
                if max_temp is not None:
                    current_time = time.time() - start_time
                    
                    # Update min/max for email reports
                    if max_temp < self.min_temp:
                        self.min_temp = max_temp
                    if max_temp > self.max_temp:
                        self.max_temp = max_temp
                    
                    # Update display immediately
                    self.root.after(0, self.update_display, max_temp, avg_temp, cpu_percent, memory_percent, current_time)
                    
                    # Update history with max temperature
                    self.temp_history.append(max_temp)
                    self.time_history.append(current_time)
                    
                    # Log temperature data persistently
                    if avg_temp is not None:
                        self.log_manager.log_temperature("Average Temperature", avg_temp)
                    if max_temp is not None:
                        self.log_manager.log_temperature("Max Temperature", max_temp)
                    if self.storage_temperatures:
                        storage_details = ", ".join([f"{device}: {temp:.1f}°C" for device, temp in self.storage_temperatures.items()])
                        self.log_manager.log_temperature("Storage Details", 0, f"Storage temperatures: {storage_details}")
                    
                    # Check for alerts only if alert monitoring is active
                    if self.alert_monitoring_active:
                        current_absolute_time = time.time()
                        
                        if max_temp >= self.critical_temp:
                            # Send critical alerts (with cooldown)
                            if current_absolute_time - self.last_warning_time > self.warning_cooldown:
                                self.root.after(0, self.send_desktop_notification,
                                              "🔥 CRITICAL STORAGE TEMPERATURE ALERT!",
                                              "Storage temperature is critically high!",
                                              max_temp)
                                self.last_warning_time = current_absolute_time
                        
                        elif max_temp >= self.warning_temp:
                            # Send warning alerts (with cooldown)
                            if current_absolute_time - self.last_warning_time > self.warning_cooldown:
                                self.root.after(0, self.send_desktop_notification,
                                              "⚠️ HIGH STORAGE TEMPERATURE WARNING",
                                              "Storage temperature is above normal",
                                              max_temp)
                                self.last_warning_time = current_absolute_time
                else:
                    # No temperature data available
                    current_time = time.time() - start_time
                    self.root.after(0, self.update_display, None, None, None, None, current_time)
                    
                    # Log sensor unavailability
                    self.log_manager.log_temperature("Error", 0, "No temperature data available from sensors")
                
                # Get refresh rate from UI
                try:
                    refresh_delay = max(1, float(self.refresh_rate_var.get()))
                except:
                    refresh_delay = 2
                
                time.sleep(refresh_delay)
            
            except Exception as e:
                print(f"Monitoring error: {e}")
                
                # Log monitoring errors
                self.log_manager.log_temperature("Error", 0, f"Monitoring error: {e}")
                
                time.sleep(5)
    
    def update_display(self, max_temp, avg_temp, cpu_percent, memory_percent, current_time):
        """Update the UI display with current readings"""
        # Update average and max temperatures
        if avg_temp is not None:
            self.avg_temp_var.set(f"{avg_temp:.1f}°C")
        else:
            self.avg_temp_var.set("--°C")
        
        if max_temp is not None:
            self.max_temp_var.set(f"{max_temp:.1f}°C")
        else:
            self.max_temp_var.set("--°C")
        
        # Update system status in sensor status section
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
        
        # Add alert status to display
        if self.alert_monitoring_active:
            status_text += " | Alerts ON"
        else:
            status_text += " | Alerts OFF"
        
        self.status_var.set(status_text)
        
        update_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.last_update_var.set(f"Updated: {update_time}")
        
        self.update_graph()
    
    def start_alert_monitoring(self):
        """Start alert monitoring (notifications)"""
        self.alert_monitoring_active = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Log alert status change
        self.log_manager.log_temperature("System", 0, "Alert monitoring enabled")
        
        messagebox.showinfo("Alerts Enabled", "Storage temperature alert monitoring is now active!\n\nYou will receive notifications when storage temperatures exceed thresholds.")
    
    def stop_alert_monitoring(self):
        """Stop alert monitoring (notifications)"""
        self.alert_monitoring_active = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        # Log alert status change
        self.log_manager.log_temperature("System", 0, "Alert monitoring disabled")
        
        messagebox.showinfo("Alerts Disabled", "Storage temperature alert monitoring is now inactive.")
    
    def manual_refresh(self):
        """Force an immediate temperature refresh"""
        self.storage_temperatures = self.temp_reader.get_storage_temperatures()
        max_temp = self.temp_reader.get_max_storage_temperature()
        avg_temp = self.temp_reader.get_average_storage_temperature()
        cpu_percent, memory_percent = self.get_system_info()
        if max_temp is not None:
            self.update_display(max_temp, avg_temp, cpu_percent, memory_percent, 
                              len(self.time_history) * float(self.refresh_rate_var.get()))
    
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
            
            # Log settings change
            self.log_manager.log_temperature("System", 0, f"Settings updated: Warning={new_warning}°C, Critical={new_critical}°C")
            
            messagebox.showinfo("Success", "Temperature settings updated successfully")
        
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for temperature thresholds")
    
    def on_closing(self):
        """Clean up when closing the application"""
        self.is_monitoring = False
        
        # Log application shutdown
        self.log_manager.log_temperature("System", "N/A", "Storage Temperature Monitor shutting down")
        
        self.save_settings()
        self.root.destroy()