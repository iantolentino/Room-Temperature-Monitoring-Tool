import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import datetime

class LiveLogWindow:
    """Live Log window for displaying real-time temperature logs"""
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
        """Create the Live Log window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Live Temperature Log")
        
        # Use responsive design for modal
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = min(1000, screen_width - 100)
        window_height = min(700, screen_height - 100)
        self.window.geometry(f"{window_width}x{window_height}")
        
        # Make window responsive with minimum size
        self.window.minsize(800, 600)
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Set proper background color
        if self.colors['background'] == '#0f172a':  # Dark mode
            bg_color = '#1e293b'
            text_bg = '#1e293b'
        else:  # Light mode
            bg_color = '#ffffff'
            text_bg = '#ffffff'
        
        self.window.configure(bg=bg_color)
        
        # Configure grid for responsiveness
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        
        # Make the window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Header
        header_frame = ttk.Frame(self.window, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=15)
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="Live Temperature Log", 
                               background=bg_color,
                               foreground=self.colors['text_primary'],
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, sticky='w')
        
        # Buttons frame
        button_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        button_frame.grid(row=0, column=1, sticky='e')
        
        # Updated button text to reflect time range functionality
        search_export_button = ttk.Button(button_frame, text="Search & Export by Time Range", 
                                         command=self.show_time_search_modal,
                                         style='Secondary.TButton')
        search_export_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Status info
        self.status_var = tk.StringVar(value="Showing: Live Logs")
        status_label = ttk.Label(header_frame, textvariable=self.status_var,
                                background=bg_color,
                                foreground=self.colors['text_secondary'],
                                font=("Segoe UI", 9))
        status_label.grid(row=1, column=0, sticky='w', pady=(5, 0))
        
        # Log display area
        log_frame = ttk.Frame(self.window, style='Modern.TFrame')
        log_frame.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Create scrollable text area for logs
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
        
        # Load existing logs
        self.refresh_log_display()
        
        # Start live updates
        self.update_live_log()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def show_time_search_modal(self):
        """Show the time range search and export modal window"""
        TimeRangeSearchWindow(self.window, self.log_manager, self.theme_manager, self.responsive_design)
    
    def refresh_log_display(self):
        """Refresh the log display with current logs"""
        logs = self.log_manager.get_all_logs()
        
        # Enable text widget for update
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        
        if logs:
            for log_entry in logs[-1000:]:  # Show last 1000 entries to prevent UI lag
                self.log_text.insert(tk.END, log_entry + "\n")
            
            # Scroll to bottom
            self.log_text.see(tk.END)
        else:
            self.log_text.insert(tk.END, "No logs available yet...\n")
        
        # Set back to read-only after updating content
        self.log_text.config(state='disabled')
    
    def update_live_log(self):
        """Update the log display with new entries"""
        if self.is_running and self.window.winfo_exists():
            # Get only new logs since last update
            new_logs = self.log_manager.get_new_logs()
            
            if new_logs:
                # Enable text widget for update
                self.log_text.config(state='normal')
                
                for log_entry in new_logs:
                    self.log_text.insert(tk.END, log_entry + "\n")
                
                # Auto-scroll to bottom
                self.log_text.see(tk.END)
                
                # Set back to read-only after updating content
                self.log_text.config(state='disabled')
            
            # Schedule next update
            self.window.after(1000, self.update_live_log)
    
    def on_close(self):
        """Handle window close"""
        self.is_running = False
        self.window.destroy()


class TimeRangeSearchWindow:
    """Modal window for time range search and export with graph generation"""
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
        """Create the time search and export modal window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Search and Export Logs by Time Range")
        
        # Use responsive design for modal
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = min(1100, screen_width - 100)
        window_height = min(700, screen_height - 100)
        self.window.geometry(f"{window_width}x{window_height}")
        
        # Make window responsive
        self.window.minsize(900, 600)
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Set proper background color
        if self.colors['background'] == '#0f172a':  # Dark mode
            bg_color = '#1e293b'
            text_bg = '#1e293b'
        else:  # Light mode
            bg_color = '#ffffff'
            text_bg = '#ffffff'
        
        self.window.configure(bg=bg_color)
        
        # Make the window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Configure grid weights for responsiveness
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(self.window, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=15)
        header_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="Search and Export Logs by Time Range", 
                               background=bg_color,
                               foreground=self.colors['text_primary'],
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, sticky='w')
        
        # Search and Export controls frame
        controls_frame = ttk.Frame(self.window, style='Modern.TFrame')
        controls_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)
        
        # Date and time range selection
        datetime_frame = ttk.Frame(controls_frame, style='Modern.TFrame')
        datetime_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        datetime_frame.columnconfigure(1, weight=1)
        datetime_frame.columnconfigure(3, weight=1)
        
        # Start date and time
        start_frame = ttk.Frame(datetime_frame, style='Modern.TFrame')
        start_frame.grid(row=0, column=0, sticky='w', padx=(0, 20))
        
        ttk.Label(start_frame, text="Start Date & Time:", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w', columnspan=2)
        
        # Date entry
        ttk.Label(start_frame, text="Date (YYYY-MM-DD):", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 8)).grid(row=1, column=0, sticky='w', pady=(5, 2))
        
        self.start_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        start_date_entry = ttk.Entry(start_frame, textvariable=self.start_date_var, width=12, font=('Segoe UI', 8))
        start_date_entry.grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        # Time entry
        ttk.Label(start_frame, text="Time (HH:MM):", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 8)).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(5, 2))
        
        self.start_time_var = tk.StringVar(value="00:00")
        start_time_entry = ttk.Entry(start_frame, textvariable=self.start_time_var, width=8, font=('Segoe UI', 8))
        start_time_entry.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=(0, 5))
        
        # End date and time
        end_frame = ttk.Frame(datetime_frame, style='Modern.TFrame')
        end_frame.grid(row=0, column=1, sticky='w', padx=(0, 20))
        
        ttk.Label(end_frame, text="End Date & Time:", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w', columnspan=2)
        
        # Date entry
        ttk.Label(end_frame, text="Date (YYYY-MM-DD):", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 8)).grid(row=1, column=0, sticky='w', pady=(5, 2))
        
        self.end_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        end_date_entry = ttk.Entry(end_frame, textvariable=self.end_date_var, width=12, font=('Segoe UI', 8))
        end_date_entry.grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        # Time entry
        ttk.Label(end_frame, text="Time (HH:MM):", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 8)).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(5, 2))
        
        self.end_time_var = tk.StringVar(value="23:59")
        end_time_entry = ttk.Entry(end_frame, textvariable=self.end_time_var, width=8, font=('Segoe UI', 8))
        end_time_entry.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=(0, 5))
        
        # Quick time range buttons
        quick_buttons_frame = ttk.Frame(datetime_frame, style='Modern.TFrame')
        quick_buttons_frame.grid(row=0, column=2, sticky='w')
        
        ttk.Label(quick_buttons_frame, text="Quick Ranges:", 
                 background=bg_color,
                 foreground=self.colors['text_secondary'],
                 font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w', columnspan=2)
        
        # Quick range buttons
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
        
        # Buttons frame
        action_frame = ttk.Frame(controls_frame, style='Modern.TFrame')
        action_frame.grid(row=1, column=0, sticky='ew')
        action_frame.columnconfigure(0, weight=1)
        
        # Search button
        search_button = ttk.Button(action_frame, text="Search Logs", 
                                  command=self.search_logs,
                                  style='Primary.TButton')
        search_button.grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        # Export button
        self.export_button = ttk.Button(action_frame, text="Export Results", 
                                       command=self.export_logs,
                                       style='Secondary.TButton',
                                       state="disabled")
        self.export_button.grid(row=0, column=1, sticky='w', padx=(0, 10))
        
        # Show History Graph button
        self.graph_button = ttk.Button(action_frame, text="Show History Graph", 
                                      command=self.show_history_graph,
                                      style='Secondary.TButton',
                                      state="disabled")
        self.graph_button.grid(row=0, column=2, sticky='w')
        
        # Results info frame
        info_frame = ttk.Frame(controls_frame, style='Modern.TFrame')
        info_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        self.results_var = tk.StringVar(value="Enter time range and click 'Search Logs'")
        results_label = ttk.Label(info_frame, textvariable=self.results_var,
                                background=bg_color,
                                foreground=self.colors['text_secondary'],
                                font=("Segoe UI", 9))
        results_label.pack(anchor='w')
        
        # Main content area - Logs
        content_frame = ttk.Frame(self.window, style='Modern.TFrame')
        content_frame.grid(row=2, column=0, sticky='nsew', padx=15, pady=(0, 15))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Create scrollable text area for logs
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
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def set_quick_range(self, hours):
        """Set time range for last N hours"""
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=hours)
        
        self.start_date_var.set(start_time.strftime("%Y-%m-%d"))
        self.start_time_var.set(start_time.strftime("%H:%M"))
        self.end_date_var.set(end_time.strftime("%Y-%m-%d"))
        self.end_time_var.set(end_time.strftime("%H:%M"))
    
    def set_today_range(self):
        """Set time range for today"""
        today = datetime.datetime.now()
        self.start_date_var.set(today.strftime("%Y-%m-%d"))
        self.start_time_var.set("00:00")
        self.end_date_var.set(today.strftime("%Y-%m-%d"))
        self.end_time_var.set("23:59")
    
    def set_yesterday_range(self):
        """Set time range for yesterday"""
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        self.start_date_var.set(yesterday.strftime("%Y-%m-%d"))
        self.start_time_var.set("00:00")
        self.end_date_var.set(yesterday.strftime("%Y-%m-%d"))
        self.end_time_var.set("23:59")
    
    def search_logs(self):
        """Search logs for the selected time range"""
        try:
            start_datetime_str = f"{self.start_date_var.get()} {self.start_time_var.get()}"
            end_datetime_str = f"{self.end_date_var.get()} {self.end_time_var.get()}"
            
            # Validate datetime
            try:
                start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
                end_datetime = datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
                
                if start_datetime > end_datetime:
                    messagebox.showerror("Error", "Start time cannot be after end time")
                    return
                
            except ValueError:
                messagebox.showerror("Error", "Invalid datetime format. Please use YYYY-MM-DD for date and HH:MM for time")
                return
            
            # Get logs for the time range
            self.current_logs = self.log_manager.get_logs_for_time_range(start_datetime, end_datetime)
            
            # Clear and update log display
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            
            if self.current_logs:
                for log_entry in self.current_logs:
                    self.log_text.insert(tk.END, log_entry + "\n")
                
                # Scroll to top
                self.log_text.see(1.0)
                
                # Update results info
                log_count = len(self.current_logs)
                self.results_var.set(f"Found {log_count} log entries from {start_datetime_str} to {end_datetime_str}")
                
                # Enable export and graph buttons
                self.export_button.config(state="normal")
                self.graph_button.config(state="normal")
            
            else:
                self.log_text.insert(tk.END, "No logs found for the specified time range.\n")
                self.results_var.set("No logs found for the specified time range")
                self.export_button.config(state="disabled")
                self.graph_button.config(state="disabled")
            
            # Set back to read-only after updating content
            self.log_text.config(state='disabled')
        
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search logs: {str(e)}")
    
    def show_history_graph(self):
        """Show the history graph in a modal window"""
        if not self.current_logs:
            messagebox.showinfo("No Data", "No logs to generate graph. Please search for logs first.")
            return
        
        try:
            start_datetime_str = f"{self.start_date_var.get()} {self.start_time_var.get()}"
            end_datetime_str = f"{self.end_date_var.get()} {self.end_time_var.get()}"
            
            # Validate datetime
            try:
                start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
                end_datetime = datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid datetime format in fields")
                return
            
            # Create and show the search result modal
            SearchResultModal(self.window, start_datetime, end_datetime, self.current_logs, self.theme_manager, self.responsive_design)
        
        except Exception as e:
            messagebox.showerror("Graph Error", f"Failed to generate graph: {str(e)}")
    
    def export_logs(self):
        """Export the currently displayed logs to file"""
        if not self.current_logs:
            messagebox.showinfo("No Data", "No logs to export. Please search for logs first.")
            return
        
        try:
            start_datetime_str = f"{self.start_date_var.get()} {self.start_time_var.get()}"
            end_datetime_str = f"{self.end_date_var.get()} {self.end_time_var.get()}"
            
            # Validate datetime
            try:
                start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
                end_datetime = datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid datetime format in fields")
                return
            
            # Export logs using LogManager
            success = self.log_manager.export_logs_to_file_with_time_range(start_datetime, end_datetime)
            
            if success:
                messagebox.showinfo("Export Successful", 
                                  "Logs exported successfully to Downloads folder!")
            else:
                messagebox.showinfo("Export Failed", "Failed to export logs")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")
    
    def on_close(self):
        """Handle window close"""
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
        """Create the search result modal window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Search Results - Temperature History")
        
        # Use responsive design for modal
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = min(1200, screen_width - 100)
        window_height = min(800, screen_height - 100)
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.minsize(1000, 700)
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Set proper background color
        if self.colors['background'] == '#0f172a':  # Dark mode
            bg_color = '#1e293b'
            text_bg = '#1e293b'
        else:  # Light mode
            bg_color = '#ffffff'
            text_bg = '#ffffff'
        
        self.window.configure(bg=bg_color)
        
        # Make the window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Configure grid weights for responsiveness
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        
        # Header with search range information
        header_frame = ttk.Frame(self.window, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=20)
        header_frame.columnconfigure(0, weight=1)
        
        # Title with search range
        title_text = f"Temperature History: {self.start_datetime.strftime('%Y-%m-%d %H:%M')} to {self.end_datetime.strftime('%Y-%m-%d %H:%M')}"
        title_label = ttk.Label(header_frame, text=title_text,
                               background=bg_color,
                               foreground=self.colors['text_primary'],
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, sticky='w')
        
        # Statistics frame
        stats_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        stats_frame.grid(row=1, column=0, sticky='ew', pady=(10, 0))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        
        # Parse temperature data for statistics
        temperatures = self.parse_temperature_data()
        
        if temperatures:
            avg_temp = sum(temperatures) / len(temperatures)
            max_temp = max(temperatures)
            min_temp = min(temperatures)
            
            # Average temperature
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
            
            # Max temperature
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
            
            # Min temperature
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
        
        # Main content area - Graph
        content_frame = ttk.Frame(self.window, style='Modern.TFrame')
        content_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 20))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure for graph
        self.setup_graph(content_frame)
        
        # Close button
        button_frame = ttk.Frame(self.window, style='Modern.TFrame')
        button_frame.grid(row=2, column=0, sticky='ew', padx=20, pady=(0, 20))
        
        close_button = ttk.Button(button_frame, text="Close", 
                                 command=self.window.destroy,
                                 style='Primary.TButton')
        close_button.pack(side=tk.RIGHT)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
    
    def parse_temperature_data(self):
        """Parse temperature data from logs"""
        temperatures = []
        
        for log_entry in self.logs:
            if '°C' in log_entry:
                try:
                    # Extract temperature value
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
        """Setup the matplotlib graph with your exact style using actual log data"""
        # Parse temperature data from logs
        temperature_entries = []
        
        for log_entry in self.logs:
            if '°C' in log_entry:
                try:
                    # Extract timestamp
                    timestamp_str = log_entry.split(']')[0][1:]
                    timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    # Extract temperature value
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
        
        # If no temperature data found in logs
        if not temperature_entries:
            # Create a no data message frame
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
        
        # Sort entries by timestamp
        temperature_entries.sort(key=lambda x: x['timestamp'])
        
        # Extract dates and temperatures for plotting
        dates = [entry['timestamp'] for entry in temperature_entries]
        temperatures = [entry['temperature'] for entry in temperature_entries]
        
        # Create figure with your exact style
        self.fig = plt.figure(figsize=(12, 6))
        self.fig.patch.set_facecolor(self.colors['card_bg'])
        
        # Set colors based on theme
        if self.colors['background'] == '#0f172a':  # Dark theme
            text_color = 'white'
            grid_color = '#2d3748'
            line_color = '#60a5fa'  # Light blue for dark theme
        else:  # Light theme
            text_color = 'black'
            grid_color = '#e2e8f0'
            line_color = '#2563eb'  # Blue for light theme
        
        # ----- Plot Graph with your exact style -----
        plt.plot(dates, temperatures, marker='o', label="Temperature (°C)", 
                color=line_color, linewidth=2, markersize=6)
        
        plt.xlabel("Date", color=text_color, fontsize=12)
        plt.ylabel("Temperature (°C)", color=text_color, fontsize=12)
        plt.title(f"Temperature History: {self.start_datetime.strftime('%Y-%m-%d %H:%M')} to {self.end_datetime.strftime('%Y-%m-%d %H:%M')}", 
                 color=text_color, fontsize=14, fontweight='bold', pad=15)
        
        # Apply your exact styling
        plt.legend(fontsize=11, framealpha=0.9)
        plt.grid(True, linestyle="--", alpha=0.5, color=grid_color)
        plt.xticks(rotation=45, color=text_color)
        plt.yticks(color=text_color)
        
        # Set axis colors and facecolor
        ax = plt.gca()
        ax.set_facecolor(self.colors['card_bg'])
        ax.spines['bottom'].set_color(text_color)
        ax.spines['top'].set_color(text_color)
        ax.spines['right'].set_color(text_color)
        ax.spines['left'].set_color(text_color)
        
        # Format x-axis dates nicely
        date_format = mdates.DateFormatter('%Y-%m-%d %H:%M')
        ax.xaxis.set_major_formatter(date_format)
        
        # Auto-adjust y-axis limits with some padding
        if temperatures:
            min_temp = min(temperatures)
            max_temp = max(temperatures)
            padding = (max_temp - min_temp) * 0.1 if max_temp > min_temp else 1
            plt.ylim(min_temp - padding, max_temp + padding)
        
        # Add statistics to the plot if we have data
        if temperatures:
            avg_temp = sum(temperatures) / len(temperatures)
            max_temp_val = max(temperatures)
            min_temp_val = min(temperatures)
            
            # Add horizontal lines for statistics
            plt.axhline(y=avg_temp, color=self.colors['accent'], linestyle=':', 
                       alpha=0.7, label=f'Average: {avg_temp:.1f}°C')
            plt.axhline(y=max_temp_val, color=self.colors['error'], linestyle=':', 
                       alpha=0.5, label=f'Max: {max_temp_val:.1f}°C')
            plt.axhline(y=min_temp_val, color=self.colors['success'], linestyle=':', 
                       alpha=0.5, label=f'Min: {min_temp_val:.1f}°C')
            
            # Add legend for statistics
            plt.legend(fontsize=10, framealpha=0.9)
        
        # Adjust layout
        plt.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')