"""
Custom button component with responsive anchoring and modern styling.
"""

import pygame
from ui.theme import COLORS, get_arcade_font, draw_rounded_rect, draw_shadow_rect, BORDER_RADIUS

class ButtonAnchor:
    """Button anchor positions for responsive layout."""
    TOP_CENTER = "top_center"
    CENTER = "center"
    BOTTOM_CENTER = "bottom_center"

class Button:
    """A responsive button with modern styling and anchoring."""
    
    def __init__(self, text, anchor=ButtonAnchor.CENTER, offset_y=0):
        self.text = text
        self.anchor = anchor
        self.offset_y = offset_y
        
        # State
        self.is_hovered = False
        self.is_pressed = False
        
        # Will be set by update_layout
        self.rect = pygame.Rect(0, 0, 100, 40)
        self.font = None
        
        # Colors
        self.normal_color = COLORS['accent']
        self.hover_color = tuple(max(0, c - 30) for c in COLORS['accent'])
        self.text_color = COLORS['background']  # Dark text on golden background
    
    def update_layout(self, layout):
        """Update button position and size based on layout with arcade fonts."""
        # Update font with arcade styling
        from ui.theme import get_arcade_font
        self.font = get_arcade_font(layout.font_sizes['button'])
        
        # Set button dimensions
        width = layout.button_width
        height = layout.button_height
        
        # Calculate position based on anchor
        if self.anchor == ButtonAnchor.TOP_CENTER:
            x = (layout.window_width - width) // 2
            y = layout.button_y + self.offset_y
        elif self.anchor == ButtonAnchor.CENTER:
            x = (layout.window_width - width) // 2
            y = (layout.window_height - height) // 2 + self.offset_y
        elif self.anchor == ButtonAnchor.BOTTOM_CENTER:
            x = (layout.window_width - width) // 2
            y = layout.window_height - height - 20 + self.offset_y
        else:
            # Default to center
            x = (layout.window_width - width) // 2
            y = (layout.window_height - height) // 2 + self.offset_y
        
        self.rect = pygame.Rect(x, y, width, height)
    
    def handle_event(self, event):
        """Handle mouse events for the button."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                was_pressed = self.is_pressed
                self.is_pressed = False
                if was_pressed and self.rect.collidepoint(event.pos):
                    return True  # Button was clicked
        return False
    
    def draw(self, surface):
        """Draw the button with modern styling."""
        if not self.font:
            return  # Layout not set yet
        
        # Draw shadow (unless pressed)
        if not self.is_pressed:
            draw_shadow_rect(surface, self.rect)
        
        # Choose color based on state
        color = self.hover_color if self.is_hovered else self.normal_color
        
        # Adjust position if pressed (pressed effect)
        draw_rect = self.rect.copy()
        if self.is_pressed:
            draw_rect.x += 2
            draw_rect.y += 2
        
        # Draw button background
        draw_rounded_rect(surface, color, draw_rect)
        
        # Draw button border
        pygame.draw.rect(surface, COLORS['text'], draw_rect, 
                        width=2, border_radius=BORDER_RADIUS)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        surface.blit(text_surface, text_rect)
    
    def set_text(self, text):
        """Update button text."""
        self.text = text
