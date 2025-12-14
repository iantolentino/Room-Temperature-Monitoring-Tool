import tkinter as tk

class ResponsiveDesign:
    """Handles responsive design and screen adaptation"""
    
    def __init__(self, root):
        self.root = root
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.setup_fullscreen_geometry()
    
    def setup_fullscreen_geometry(self):
        """Set up fullscreen window using geometry and zoomed state"""
        # Set window to full screen using geometry and zoomed state
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.state('zoomed')
        self.root.minsize(1000, 700)
    
    def get_scaling_factors(self):
        """Calculate scaling factors based on screen resolution"""
        base_width = 1920  # Base resolution for scaling
        base_height = 1080
        
        width_scale = self.screen_width / base_width
        height_scale = self.screen_height / base_height
        
        # Use the smaller scale to ensure everything fits
        scale_factor = min(width_scale, height_scale, 1.5)  # Cap at 1.5x
        
        return {
            'font_scale': max(0.8, min(scale_factor, 1.2)),
            'padding_scale': max(0.8, min(scale_factor, 1.3)),
            'widget_scale': max(0.9, min(scale_factor, 1.4))
        }