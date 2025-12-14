class ThemeManager:
    
    def __init__(self):
        # Set default theme to "light" instead of "dark"
        self.current_theme = "light"  # Default theme is now light
        self.themes = {
            "dark": {
                'primary': '#3b82f6',      # Professional Blue
                'secondary': '#60a5fa',    # Medium Blue
                'accent': '#93c5fd',       # Light Blue
                'background': '#0f172a',   # Dark blue background
                'surface': '#1e293b',      # Card surface
                'card_bg': '#1e293b',      # Card background
                'text_primary': '#f8fafc', # Light text
                'text_secondary': '#cbd5e1', # Medium light text
                'success': '#10b981',      # Green
                'warning': '#f59e0b',      # Amber
                'error': '#ef4444',        # Red
                'border': '#334155',       # Dark border
                'hover': '#374151',        # Hover state
                'grid_color': '#2d3748',   # Grid pattern color
                'input_bg': '#1e293b',     # Input background
                'input_fg': '#f8fafc',     # Input foreground
            },
            "light": {
                'primary': '#2563eb',      # Professional Blue
                'secondary': '#3b82f6',    # Medium Blue
                'accent': '#60a5fa',       # Light Blue
                'background': '#f8fafc',   # Light background
                'surface': '#ffffff',      # Card surface
                'card_bg': '#ffffff',      # Card background
                'text_primary': '#1e293b', # Dark text
                'text_secondary': '#475569', # Medium dark text
                'success': '#059669',      # Green
                'warning': '#d97706',      # Amber
                'error': '#dc2626',        # Red
                'border': '#e2e8f0',       # Light border
                'hover': '#f1f5f9',        # Hover state
                'grid_color': '#e2e8f0',   # Grid pattern color
                'input_bg': '#ffffff',     # Input background
                'input_fg': '#1e293b',     # Input foreground,
            }
        }
    
    def get_theme(self):
        """Get current theme colors"""
        return self.themes[self.current_theme]
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        return self.get_theme()
    
    def set_theme(self, theme_name):
        """Set specific theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
        return self.get_theme()