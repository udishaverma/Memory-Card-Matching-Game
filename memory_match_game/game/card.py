"""
Card class for the Memory Match Game.
Handles card state machine, animations, and drawing with proper flip logic.
"""

import pygame
import time
from enum import Enum
from ui.theme import COLORS, FLIP_DURATION, draw_rounded_rect, draw_shadow_rect, BORDER_RADIUS

class CardState(Enum):
    """Card states for the state machine."""
    HIDDEN = "hidden"           # Face down, not flipping
    FLIPPING_TO_VISIBLE = "flipping_to_visible"  # Animating from hidden to visible
    VISIBLE = "visible"         # Face up, not flipping
    FLIPPING_TO_HIDDEN = "flipping_to_hidden"    # Animating from visible to hidden
    MATCHED = "matched"         # Permanently matched

class Card:
    """Represents a single card with proper state machine and animations."""
    
    def __init__(self, row, col, symbol, symbol_surface, layout, grid_size=6):
        self.row = row
        self.col = col
        self.symbol = symbol
        self.symbol_surface = symbol_surface
        self.layout = layout
        self.grid_size = grid_size  # Store grid size for positioning
        
        # Position and size (will be updated by layout)
        self.update_position()
        
        # Card state machine
        self.state = CardState.HIDDEN
        self.is_hovered = False
        
        # Animation properties
        self.animation_start_time = 0
        self.animation_progress = 0.0  # 0.0 to 1.0
        
    def update_position(self):
        """Update card position based on current layout."""
        x, y = self.layout.get_card_position(self.row, self.col, self.grid_size)
        
        # Calculate card size based on grid size
        available_width = self.layout.window_width - 2 * 40  # GRID_MARGIN
        available_height = self.layout.window_height - 2 * 40 - 100
        
        max_card_size_width = (available_width - (self.grid_size - 1) * 16) // self.grid_size  # CARD_SPACING
        max_card_size_height = (available_height - (self.grid_size - 1) * 16) // self.grid_size
        
        card_size = min(max_card_size_width, max_card_size_height, 120)
        card_size = max(card_size, 40)  # Minimum size
        
        self.rect = pygame.Rect(x, y, card_size, card_size)
    
    def handle_event(self, event):
        """Handle mouse events for the card."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                # Only allow clicks on hidden cards
                if self.state == CardState.HIDDEN:
                    return True  # Card was clicked
        return False
    
    def flip_to_visible(self):
        """Start animation to flip card to visible state."""
        if self.state == CardState.HIDDEN:
            self.state = CardState.FLIPPING_TO_VISIBLE
            self.animation_start_time = time.time() * 1000
            self.animation_progress = 0.0
    
    def flip_to_hidden(self):
        """Start animation to flip card back to hidden state."""
        if self.state == CardState.VISIBLE:
            self.state = CardState.FLIPPING_TO_HIDDEN
            self.animation_start_time = time.time() * 1000
            self.animation_progress = 0.0
    
    def set_matched(self):
        """Mark the card as permanently matched."""
        self.state = CardState.MATCHED
    
    def is_face_up(self):
        """Check if card is currently showing its face (visible or matched)."""
        return self.state in [CardState.VISIBLE, CardState.MATCHED]
    
    def is_clickable(self):
        """Check if card can be clicked."""
        return self.state == CardState.HIDDEN
    
    def is_animating(self):
        """Check if card is currently animating."""
        return self.state in [CardState.FLIPPING_TO_VISIBLE, CardState.FLIPPING_TO_HIDDEN]
    
    def update(self):
        """Update card animation state."""
        if not self.is_animating():
            return
        
        current_time = time.time() * 1000
        elapsed = current_time - self.animation_start_time
        
        if elapsed >= FLIP_DURATION:
            # Animation complete
            if self.state == CardState.FLIPPING_TO_VISIBLE:
                self.state = CardState.VISIBLE
            elif self.state == CardState.FLIPPING_TO_HIDDEN:
                self.state = CardState.HIDDEN
            self.animation_progress = 0.0
        else:
            # Calculate animation progress (0.0 to 1.0)
            self.animation_progress = elapsed / FLIP_DURATION
    
    def get_scale_factor(self):
        """Get the current scale factor for flip animation."""
        if not self.is_animating():
            return 1.0
        
        # Scale X from 1→0→1 over the animation duration
        # First half: scale down to 0, second half: scale back up to 1
        if self.animation_progress <= 0.5:
            # First half: 1.0 → 0.0
            return 1.0 - (self.animation_progress * 2.0)
        else:
            # Second half: 0.0 → 1.0
            return (self.animation_progress - 0.5) * 2.0
    
    def should_show_front(self):
        """Determine if we should show the front or back of the card."""
        if self.state == CardState.HIDDEN:
            return False
        elif self.state in [CardState.VISIBLE, CardState.MATCHED]:
            return True
        elif self.state == CardState.FLIPPING_TO_VISIBLE:
            # Show front in second half of animation
            return self.animation_progress > 0.5
        elif self.state == CardState.FLIPPING_TO_HIDDEN:
            # Show back in second half of animation
            return self.animation_progress <= 0.5
        
        return False
    
    def draw(self, surface):
        """Draw the card with proper borders and symbol display."""
        # Update position in case layout changed
        self.update_position()
        
        # Calculate scaled rectangle for animation
        scale_factor = self.get_scale_factor()
        scaled_width = max(1, int(self.rect.width * scale_factor))
        scaled_rect = pygame.Rect(
            self.rect.x + (self.rect.width - scaled_width) // 2,
            self.rect.y,
            scaled_width,
            self.rect.height
        )
        
        # Draw shadow if hovered and not matched
        if self.is_hovered and self.state != CardState.MATCHED:
            draw_shadow_rect(surface, self.rect)
        
        # Draw card based on current state
        if self.should_show_front():
            self._draw_front(surface, scaled_rect)
        else:
            self._draw_back(surface, scaled_rect)
        
        # Draw border with proper colors and width (3px as specified)
        from ui.theme import CARD_BORDER_WIDTH
        
        if self.state == CardState.MATCHED:
            border_color = COLORS['accent']  # #FFD700 when matched
            border_width = CARD_BORDER_WIDTH
        elif self.is_hovered:
            border_color = COLORS['accent']  # #FFD700 when hovered
            border_width = CARD_BORDER_WIDTH
        else:
            border_color = COLORS['card_back']  # #1A2D5A when hidden
            border_width = CARD_BORDER_WIDTH
        
        if scaled_width > 2:  # Only draw border if card is wide enough
            pygame.draw.rect(surface, border_color, scaled_rect, 
                           width=border_width, border_radius=BORDER_RADIUS)
    
    def _draw_front(self, surface, rect):
        """Draw the front (revealed) side with split-layout symbol."""
        # Card background (#F0F0F0 as specified)
        draw_rounded_rect(surface, COLORS['card_front'], rect)
        
        # Draw split-layout symbol if card is wide enough and symbol exists
        if rect.width > 40 and rect.height > 40 and self.symbol_surface:
            # Calculate scale factor to fit within card while maintaining aspect ratio
            symbol_rect = self.symbol_surface.get_rect()
            
            # Calculate scale factor with some padding
            padding = 4  # Small padding around symbol
            available_width = rect.width - (2 * padding)
            available_height = rect.height - (2 * padding)
            
            scale_x = available_width / symbol_rect.width
            scale_y = available_height / symbol_rect.height
            scale_factor = min(scale_x, scale_y, 1.0)  # Don't scale up beyond original size
            
            if scale_factor > 0.2:  # Only draw if reasonably sized
                try:
                    new_width = int(symbol_rect.width * scale_factor)
                    new_height = int(symbol_rect.height * scale_factor)
                    
                    if new_width > 0 and new_height > 0:
                        scaled_symbol = pygame.transform.scale(
                            self.symbol_surface, (new_width, new_height)
                        )
                        
                        # Center the scaled symbol
                        symbol_x = rect.x + (rect.width - new_width) // 2
                        symbol_y = rect.y + (rect.height - new_height) // 2
                        
                        surface.blit(scaled_symbol, (symbol_x, symbol_y))
                except Exception as e:
                    # Fallback: draw original symbol if scaling fails
                    if symbol_rect.width <= rect.width and symbol_rect.height <= rect.height:
                        symbol_x = rect.x + (rect.width - symbol_rect.width) // 2
                        symbol_y = rect.y + (rect.height - symbol_rect.height) // 2
                        surface.blit(self.symbol_surface, (symbol_x, symbol_y))
    
    def _draw_back(self, surface, rect):
        """Draw the back (hidden) side of the card."""
        # Card background
        draw_rounded_rect(surface, COLORS['card_back'], rect)
        
        # Add decorative pattern if card is large enough
        if rect.width > 20 and rect.height > 20:
            # Draw a diamond pattern in the center
            center_x, center_y = rect.center
            diamond_size = min(rect.width, rect.height) // 6
            
            if diamond_size > 2:
                diamond_points = [
                    (center_x, center_y - diamond_size),
                    (center_x + diamond_size, center_y),
                    (center_x, center_y + diamond_size),
                    (center_x - diamond_size, center_y)
                ]
                
                try:
                    pygame.draw.polygon(surface, COLORS['accent'], diamond_points)
                except:
                    # Fallback to simple circle if polygon fails
                    pygame.draw.circle(surface, COLORS['accent'], 
                                     (center_x, center_y), diamond_size // 2)
