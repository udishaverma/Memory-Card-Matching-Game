"""
Theme configuration for the Memory Match Game.
Contains colors, fonts, and layout constants with responsive design support.
"""

import pygame
import os

# Color scheme (exact hex specifications)
COLORS = {
    'background': (10, 17, 40),      # Dark Blue #0A1128
    'accent': (255, 215, 0),         # Golden Yellow #FFD700
    'card_front': (240, 240, 240),   # Light background #F0F0F0
    'card_back': (26, 45, 90),       # Muted blue #1A2D5A
    'text': (255, 255, 255),         # White #FFFFFF
    'shadow': (0, 0, 0, 50),         # Drop shadow
    'overlay': (0, 0, 0, 153),       # Semi-transparent overlay (rgba(0,0,0,0.6))
}

# Display settings
DEFAULT_WINDOW_SIZE = (800, 800)
GRID_ROWS = 6
GRID_COLS = 6
GRID_SIZE = GRID_ROWS  # For backward compatibility
CARD_COUNT = GRID_ROWS * GRID_COLS
PAIRS_COUNT = CARD_COUNT // 2

# Layout constants (responsive) - Updated with 16px baseline grid
CARD_SPACING = 16  # 16px between cards as specified
CARD_PADDING = 16  # Internal card padding for symbol placement
GRID_MARGIN = 40   # Margin around the grid
BUTTON_HEIGHT_RATIO = 0.06  # Button height as ratio of window height
BUTTON_WIDTH_RATIO = 0.2    # Button width as ratio of window width
BUTTON_Y_RATIO = 0.05       # Button Y position (5% from top)

# Animation settings
FLIP_DURATION = 200  # milliseconds (200ms as specified)
MISMATCH_DELAY = 1000  # milliseconds (1 second)
SHADOW_OFFSET = (4, 4)  # Drop shadow offset
SHADOW_ALPHA = 50       # Drop shadow alpha
BORDER_RADIUS = 12      # Rounded rectangle radius (12px as specified)

# Responsive grid settings
GRID_FILL_RATIO = 0.8   # Grid fills 80% of smaller window dimension

# Font settings - Arcade-style fonts
ARCADE_FONT_NAME = "Luckiest Guy"  # Primary arcade font (bold, bouncy)
ARCADE_FONTS = [
    "Luckiest Guy",      # Bold, bouncy arcade style
    "Bangers",           # Comic book energy
    "Press Start 2P",    # Pixel-art retro
    "Arcade Classic",    # Nostalgic arcade
    "Impact",            # Bold fallback
    "Arial Black",       # Bold sans-serif fallback
]
FALLBACK_FONTS = ["Arial", "Helvetica", "DejaVu Sans", None]  # Final fallbacks

# Font sizing constants for start screen (responsive base sizes)
START_FONT_SIZES = {
    'title': 48,        # Reduced from 64px
    'subtitle': 20,     # Reduced from 32px  
    'button': 24,       # Reduced from 28px
    'instructions': 20, # Same as subtitle
}

# Base window width for responsive scaling
BASE_WINDOW_WIDTH = 800

# Card design specifications
CARD_BORDER_WIDTH = 3           # 3px border as specified

# Card layout constants for split design - Enhanced for larger elements
CARD_CORNER_PADDING = 8     # Reduced padding to make room for larger elements
RANK_FONT_MIN_SIZE = 40     # Increased minimum from 32px to 40px
RANK_FONT_SIZE_RATIO = 0.35 # Increased from 30% to 35% of card height
SUIT_SYMBOL_SIZE_RATIO = 0.4 # Increased from 35% to 40% of card height

# High-quality rendering settings
SYMBOL_QUALITY_MULTIPLIER = 2.0  # 2x resolution for crisp rendering
FONT_QUALITY_MULTIPLIER = 1.5    # 1.5x font rendering quality

# Font specifications for card elements - Enhanced for clarity
CARD_FONTS = [
    "Luckiest Guy",     # Primary fun font
    "Bangers",          # Secondary fun font
    "Impact",           # High-impact bold font
    "Arial Black",      # Very bold fallback
    "Verdana",          # Clear, readable fallback
    "Arial",            # Final fallback
]

# High-quality font rendering options
FONT_RENDER_OPTIONS = {
    'antialias': True,
    'bold': True,
    'italic': False,
}

# Card color specifications - All red for visibility on colored backgrounds
CARD_COLORS = {
    'hearts': (255, 0, 0),      # Red #FF0000
    'diamonds': (255, 0, 0),    # Red #FF0000  
    'spades': (255, 0, 0),      # Red #FF0000 (changed from black)
    'clubs': (255, 0, 0),       # Red #FF0000 (changed from black)
}

# Card background colors - Darker pastels for better visibility
CARD_BACKGROUNDS = {
    'hearts': (200, 230, 200),      # Darker pastel green (was 240,255,240)
    'diamonds': (200, 220, 240),    # Darker pastel blue (was 240,248,255)
    'spades': (220, 220, 180),      # Darker beige (was 245,245,220)
    'clubs': (240, 200, 220),       # Darker baby pink (was 255,240,245)
}

class ResponsiveLayout:
    """Handles responsive layout calculations."""
    
    def __init__(self, window_size):
        self.window_width, self.window_height = window_size
        self.update_layout()
    
    def update_layout(self):
        """Update layout calculations with responsive font sizing."""
        # Calculate grid dimensions (80% of smaller dimension)
        smaller_dimension = min(self.window_width, self.window_height)
        self.grid_area_size = int(smaller_dimension * GRID_FILL_RATIO)
        
        # Calculate card size for 4x4 grid with 16px spacing
        available_space = self.grid_area_size - (GRID_ROWS - 1) * CARD_SPACING
        self.card_size = max(48, available_space // GRID_ROWS)  # Minimum 48px for better symbols
        
        # Ensure card size aligns to 16px baseline grid
        self.card_size = (self.card_size // 16) * 16
        
        # Calculate actual grid size with proper spacing
        actual_grid_size = GRID_ROWS * self.card_size + (GRID_ROWS - 1) * CARD_SPACING
        
        # Center the grid with 16px baseline alignment
        self.grid_x = ((self.window_width - actual_grid_size) // 32) * 16  # Align to 16px grid
        self.grid_y = ((self.window_height - actual_grid_size) // 32) * 16
        
        # Button dimensions aligned to 16px grid
        self.button_width = ((int(self.window_width * BUTTON_WIDTH_RATIO) // 16) * 16)
        self.button_height = ((int(self.window_height * BUTTON_HEIGHT_RATIO) // 16) * 16)
        self.button_y = ((int(self.window_height * BUTTON_Y_RATIO) // 16) * 16)
        
        # Responsive font scaling factor
        scale_factor = self.window_width / BASE_WINDOW_WIDTH
        
        # Font sizes with responsive scaling for start screen
        self.font_sizes = {
            'title': int(START_FONT_SIZES['title'] * scale_factor),
            'subtitle': int(START_FONT_SIZES['subtitle'] * scale_factor),
            'button': int(START_FONT_SIZES['button'] * scale_factor),
            'instructions': int(START_FONT_SIZES['instructions'] * scale_factor),
            'message': max(28, int(self.window_width // 18)),    # Game over messages
            'score': max(18, int(self.window_width // 40)),      # Score display
            'card_rank': max(16, int(self.card_size // 6)),      # Card rank text
        }
    
    def resize(self, new_size):
        """Handle window resize."""
        self.window_width, self.window_height = new_size
        self.update_layout()
    
    def get_card_position(self, row, col, grid_size=6):
        """Get the position of a card in the grid with variable grid size."""
        # Use the stored grid size if available, otherwise default to 6
        actual_grid_size = getattr(self, 'current_grid_size', grid_size)
        
        # Calculate card size based on grid size
        available_width = self.window_width - 2 * GRID_MARGIN
        available_height = self.window_height - 2 * GRID_MARGIN - 100  # Reserve space for UI
        
        # Calculate maximum card size that fits
        max_card_size_width = (available_width - (actual_grid_size - 1) * CARD_SPACING) // actual_grid_size
        max_card_size_height = (available_height - (actual_grid_size - 1) * CARD_SPACING) // actual_grid_size
        
        # Use the smaller dimension and cap at reasonable size
        card_size = min(max_card_size_width, max_card_size_height, 120)
        card_size = max(card_size, 40)  # Minimum 40px
        
        # Calculate total grid dimensions
        grid_width = actual_grid_size * card_size + (actual_grid_size - 1) * CARD_SPACING
        grid_height = actual_grid_size * card_size + (actual_grid_size - 1) * CARD_SPACING
        
        # Center the grid on screen
        grid_x = (self.window_width - grid_width) // 2
        grid_y = (self.window_height - grid_height) // 2
        
        # Calculate individual card position
        x = grid_x + col * (card_size + CARD_SPACING)
        y = grid_y + row * (card_size + CARD_SPACING)
        
        return x, y
    
    def set_grid_size(self, grid_size):
        """Set the current grid size for layout calculations."""
        self.current_grid_size = grid_size
        self.update_layout()

def get_arcade_font(size, font_name=ARCADE_FONT_NAME):
    """Get an arcade-style font with the specified size, with safety limits."""
    # Apply safety limits to prevent oversized fonts
    safe_size = max(12, min(size, 200))  # Between 12px and 200px
    
    fonts_to_try = ARCADE_FONTS + FALLBACK_FONTS
    
    for font in fonts_to_try:
        try:
            if font is None:
                return pygame.font.Font(None, safe_size)
            else:
                # Try to load system font
                return pygame.font.SysFont(font, safe_size, bold=True)  # Bold for arcade feel
        except:
            continue
    
    # Final fallback
    return pygame.font.Font(None, safe_size)

def get_font(size, font_name=ARCADE_FONT_NAME, stylish=True):
    """Get a font with arcade styling by default."""
    if stylish:
        return get_arcade_font(size, font_name)
    else:
        # Non-stylish fallback
        fonts_to_try = FALLBACK_FONTS
        for font in fonts_to_try:
            try:
                if font is None:
                    return pygame.font.Font(None, size)
                else:
                    return pygame.font.SysFont(font, size)
            except:
                continue
        return pygame.font.Font(None, size)

def get_card_font(size):
    """Get a bold, clear font for card elements with enhanced quality."""
    # Apply quality multiplier for sharper rendering
    enhanced_size = int(size * FONT_QUALITY_MULTIPLIER)
    
    for font_name in CARD_FONTS:
        try:
            font = pygame.font.SysFont(font_name, enhanced_size, bold=True)
            return font
        except:
            continue
    
    # Final fallback with enhanced size
    return pygame.font.Font(None, enhanced_size)

def draw_rounded_rect(surface, color, rect, radius=BORDER_RADIUS):
    """Draw a rounded rectangle with specified radius."""
    if radius <= 0:
        pygame.draw.rect(surface, color, rect)
        return
    
    # Ensure radius doesn't exceed half the smallest dimension
    radius = min(radius, rect.width // 2, rect.height // 2)
    
    # Draw rounded rectangle using pygame's built-in function
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_shadow_rect(surface, rect, offset=SHADOW_OFFSET, radius=BORDER_RADIUS):
    """Draw a drop shadow effect for rectangles."""
    shadow_rect = rect.copy()
    shadow_rect.x += offset[0]
    shadow_rect.y += offset[1]
    
    # Create a temporary surface for the shadow with per-pixel alpha
    shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    shadow_color = (*COLORS['shadow'][:3], SHADOW_ALPHA)
    
    # Draw the shadow shape
    pygame.draw.rect(shadow_surface, shadow_color, 
                    (0, 0, rect.width, rect.height), border_radius=radius)
    
    # Blit the shadow to the main surface
    surface.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))

def draw_overlay(surface, alpha=153):
    """Draw a semi-transparent overlay over the entire surface."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((*COLORS['overlay'][:3], alpha))
    surface.blit(overlay, (0, 0))
