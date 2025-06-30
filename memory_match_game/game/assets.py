"""
Enhanced 6x6 grid with suit-differentiated number cards and colored backgrounds.
Includes proper number cards with different suits and royal crowns for K/Q.
"""

import pygame
import numpy as np
from skimage import draw, filters, morphology
from skimage.transform import resize
import random

class SuitDifferentiatedCardGenerator:
    """Generates 18 different playing cards with darker backgrounds and larger elements."""
    
    def __init__(self, size=320):  # Increased from 280 to 320 for larger cards
        self.size = size
        
        # 18 playing card combinations for 6x6 grid (18 pairs = 36 cards)
        self.card_definitions = [
            # Face cards - one of each suit (4 cards)
            ('A', 'spades'),     ('K', 'hearts'),     ('Q', 'diamonds'),   ('J', 'clubs'),
            
            # Number cards with suit differentiation for variety (14 cards)
            ('10', 'spades'),    ('10', 'hearts'),    # Two different 10s
            ('9', 'diamonds'),   ('9', 'clubs'),      # Two different 9s
            ('8', 'spades'),     ('8', 'hearts'),     # Two different 8s
            ('7', 'diamonds'),   ('7', 'clubs'),      # Two different 7s
            ('6', 'spades'),     ('6', 'hearts'),     # Two different 6s
            ('5', 'diamonds'),   ('5', 'clubs'),      # Two different 5s
            ('4', 'spades'),     ('4', 'hearts'),     # Two different 4s
            ('3', 'diamonds'),   ('3', 'clubs'),      # Two different 3s
            ('2', 'spades'),     ('2', 'hearts'),     # Two different 2s
        ]
        
        # Create suit assignments from definitions
        self.suit_assignments = {}
        for i, (rank, suit) in enumerate(self.card_definitions):
            # Create unique identifiers for same numbers with different suits
            if rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
                card_id = f"{rank}_{suit}"
            else:
                card_id = f"{rank}_{suit}"
            
            suit_symbols = {
                'spades': '♠',
                'hearts': '♥', 
                'diamonds': '♦',
                'clubs': '♣'
            }
            
            self.suit_assignments[card_id] = (suit_symbols[suit], suit)
        
        # Import enhanced constants from theme
        from ui.theme import (CARD_CORNER_PADDING, RANK_FONT_MIN_SIZE, 
                             RANK_FONT_SIZE_RATIO, SUIT_SYMBOL_SIZE_RATIO, 
                             CARD_COLORS, CARD_BACKGROUNDS, SYMBOL_QUALITY_MULTIPLIER)
        
        self.corner_padding = CARD_CORNER_PADDING
        self.rank_font_min_size = RANK_FONT_MIN_SIZE
        self.rank_font_size_ratio = RANK_FONT_SIZE_RATIO
        self.suit_symbol_size_ratio = SUIT_SYMBOL_SIZE_RATIO
        self.card_colors = CARD_COLORS
        self.card_backgrounds = CARD_BACKGROUNDS
        self.quality_multiplier = SYMBOL_QUALITY_MULTIPLIER
        
        # Calculate enhanced sizes based on card dimensions
        self.rank_font_size = max(self.rank_font_min_size, int(size * self.rank_font_size_ratio))
        self.suit_symbol_size = int(size * self.suit_symbol_size_ratio)
        
        # High-quality rendering sizes (2x resolution)
        self.hq_suit_size = int(self.suit_symbol_size * self.quality_multiplier)
        self.stroke_width = max(8, int(self.hq_suit_size / 12))  # Thicker strokes for larger symbols
        
        # All symbols are red for visibility
        self.symbol_color = (255, 0, 0)
        
        # Generate the actual ranks list for compatibility
        self.ranks = list(self.suit_assignments.keys())
    
    def get_card_font(self, size):
        """Get a high-quality, bold font for card elements."""
        from ui.theme import CARD_FONTS, FONT_QUALITY_MULTIPLIER
        
        enhanced_size = int(size * FONT_QUALITY_MULTIPLIER)
        
        for font_name in CARD_FONTS:
            try:
                font = pygame.font.SysFont(font_name, enhanced_size, bold=True)
                return font
            except:
                continue
        
        return pygame.font.Font(None, enhanced_size)
    
    def create_crown_decoration(self, size, color=(255, 215, 0)):
        """Create a crown decoration for K and Q cards."""
        img = np.zeros((size, size, 3), dtype=np.uint8)
        center_x, center_y = size // 2, size // 2
        
        # Crown parameters
        crown_width = int(size * 0.6)
        crown_height = int(size * 0.4)
        
        # Crown base
        base_y = center_y + crown_height // 4
        base_height = crown_height // 4
        
        # Draw crown base rectangle
        for y in range(base_y, base_y + base_height):
            for x in range(center_x - crown_width//2, center_x + crown_width//2):
                if 0 <= x < size and 0 <= y < size:
                    img[y, x] = color
        
        # Crown points (5 points)
        points_y = base_y - crown_height // 2
        point_width = crown_width // 6
        
        for i in range(5):
            point_x = center_x - crown_width//2 + i * (crown_width // 4)
            point_height = crown_height // 3 if i % 2 == 0 else crown_height // 4
            
            # Draw crown point
            for y in range(points_y, points_y + point_height):
                for x in range(point_x - point_width//2, point_x + point_width//2):
                    if 0 <= x < size and 0 <= y < size:
                        img[y, x] = color
        
        # Add jewels (small circles)
        jewel_radius = max(2, size // 20)
        jewel_positions = [
            (center_x - crown_width//4, points_y + crown_height//6),
            (center_x, points_y + crown_height//8),
            (center_x + crown_width//4, points_y + crown_height//6)
        ]
        
        for jewel_x, jewel_y in jewel_positions:
            try:
                rr, cc = draw.disk((int(jewel_y), int(jewel_x)), jewel_radius, shape=img.shape[:2])
                img[rr, cc] = (255, 100, 100)  # Red jewels
            except:
                pass
        
        return img
    
    def create_high_quality_heart(self, size, color=(255, 0, 0)):
        """Create a high-quality heart symbol."""
        img = np.zeros((size, size, 3), dtype=np.uint8)
        center_x, center_y = size // 2, size // 2
        
        heart_radius = size // 3
        
        # Left circle
        rr, cc = draw.disk((center_y - heart_radius//3, center_x - heart_radius//2), 
                          heart_radius//2, shape=img.shape[:2])
        img[rr, cc] = color
        
        # Right circle
        rr, cc = draw.disk((center_y - heart_radius//3, center_x + heart_radius//2), 
                          heart_radius//2, shape=img.shape[:2])
        img[rr, cc] = color
        
        # Bottom triangle
        triangle_points = np.array([
            [center_y - heart_radius//6, center_x - heart_radius*0.8],
            [center_y - heart_radius//6, center_x + heart_radius*0.8],
            [center_y + heart_radius*0.9, center_x]
        ])
        
        rr, cc = draw.polygon(triangle_points[:, 0], triangle_points[:, 1], img.shape[:2])
        img[rr, cc] = color
        
        self._add_thick_outline(img, color, self.stroke_width)
        return img
    
    def create_high_quality_diamond(self, size, color=(255, 0, 0)):
        """Create a high-quality diamond symbol."""
        img = np.zeros((size, size, 3), dtype=np.uint8)
        center_x, center_y = size // 2, size // 2
        diamond_size = int(size * 0.4)
        
        points = np.array([
            [center_y - diamond_size, center_x],
            [center_y, center_x + diamond_size],
            [center_y + diamond_size, center_x],
            [center_y, center_x - diamond_size],
        ])
        
        rr, cc = draw.polygon(points[:, 0], points[:, 1], img.shape[:2])
        img[rr, cc] = color
        
        self._add_thick_outline(img, color, self.stroke_width)
        return img
    
    def create_high_quality_club(self, size, color=(255, 0, 0)):
        """Create a high-quality club symbol."""
        img = np.zeros((size, size, 3), dtype=np.uint8)
        center_x, center_y = size // 2, size // 2
        circle_radius = size // 6
        
        circles = [
            (center_y - circle_radius*1.2, center_x),
            (center_y + circle_radius*0.3, center_x - circle_radius*1.1),
            (center_y + circle_radius*0.3, center_x + circle_radius*1.1),
        ]
        
        for cy, cx in circles:
            rr, cc = draw.disk((int(cy), int(cx)), circle_radius, shape=img.shape[:2])
            img[rr, cc] = color
        
        # Stem
        stem_width = self.stroke_width
        stem_height = int(circle_radius * 1.5)
        stem_top = int(center_y + circle_radius * 0.8)
        stem_bottom = min(stem_top + stem_height, img.shape[0])
        
        for y in range(stem_top, stem_bottom):
            for x in range(center_x - stem_width//2, center_x + stem_width//2 + 1):
                if 0 <= x < img.shape[1]:
                    img[y, x] = color
        
        self._add_thick_outline(img, color, self.stroke_width)
        return img
    
    def create_high_quality_spade(self, size, color=(255, 0, 0)):
        """Create a high-quality spade symbol."""
        img = np.zeros((size, size, 3), dtype=np.uint8)
        center_x, center_y = size // 2, size // 2
        spade_size = int(size * 0.4)
        
        spade_points = np.array([
            [center_y - spade_size, center_x],
            [center_y - spade_size*0.6, center_x - spade_size*0.7],
            [center_y - spade_size*0.1, center_x - spade_size*0.5],
            [center_y - spade_size*0.1, center_x + spade_size*0.5],
            [center_y - spade_size*0.6, center_x + spade_size*0.7],
        ])
        
        rr, cc = draw.polygon(spade_points[:, 0], spade_points[:, 1], img.shape[:2])
        img[rr, cc] = color
        
        # Stem
        stem_width = self.stroke_width
        stem_height = int(spade_size * 0.6)
        stem_top = int(center_y - spade_size * 0.1)
        stem_bottom = min(stem_top + stem_height, img.shape[0])
        
        for y in range(stem_top, stem_bottom):
            for x in range(center_x - stem_width//2, center_x + stem_width//2 + 1):
                if 0 <= x < img.shape[1]:
                    img[y, x] = color
        
        self._add_thick_outline(img, color, self.stroke_width)
        return img
    
    def _add_thick_outline(self, img, color, thickness):
        """Add a thick outline to shapes."""
        shape_mask = np.any(img != [0, 0, 0], axis=2)
        
        try:
            dilated = morphology.binary_dilation(shape_mask, morphology.disk(thickness//2))
            outline = dilated & ~shape_mask
            img[outline] = color
        except:
            # Fallback outline
            height, width = img.shape[:2]
            for dy in range(-thickness//2, thickness//2 + 1):
                for dx in range(-thickness//2, thickness//2 + 1):
                    if dy == 0 and dx == 0:
                        continue
                    
                    shifted_mask = np.zeros_like(shape_mask)
                    y_start = max(0, dy)
                    y_end = min(height, height + dy)
                    x_start = max(0, dx)
                    x_end = min(width, width + dx)
                    
                    orig_y_start = max(0, -dy)
                    orig_y_end = min(height, height - dy)
                    orig_x_start = max(0, -dx)
                    orig_x_end = min(width, width - dx)
                    
                    shifted_mask[y_start:y_end, x_start:x_end] = \
                        shape_mask[orig_y_start:orig_y_end, orig_x_start:orig_x_end]
                    
                    outline_mask = shifted_mask & ~shape_mask
                    img[outline_mask] = color
    
    def create_suit_surface(self, suit_type, size, color):
        """Create a pygame surface for the suit symbol."""
        hq_size = int(size * self.quality_multiplier)
        
        if suit_type == 'hearts':
            suit_array = self.create_high_quality_heart(hq_size, color)
        elif suit_type == 'diamonds':
            suit_array = self.create_high_quality_diamond(hq_size, color)
        elif suit_type == 'clubs':
            suit_array = self.create_high_quality_club(hq_size, color)
        else:  # spades
            suit_array = self.create_high_quality_spade(hq_size, color)
        
        hq_surface = pygame.Surface((hq_size, hq_size), pygame.SRCALPHA)
        pygame.surfarray.blit_array(hq_surface, suit_array.swapaxes(0, 1))
        
        final_surface = pygame.transform.smoothscale(hq_surface, (size, size))
        return final_surface
    
    def create_rank_surface(self, rank, font_size, color):
        """Create a pygame surface for the rank text."""
        font = self.get_card_font(font_size)
        
        # Extract just the rank part (remove suit suffix)
        display_rank = rank.split('_')[0] if '_' in rank else rank
        
        rank_surface = font.render(display_rank, True, color)
        
        if rank_surface.get_width() > 50:
            temp_size = (rank_surface.get_width() * 2, rank_surface.get_height() * 2)
            temp_surface = pygame.transform.smoothscale(rank_surface, temp_size)
            rank_surface = pygame.transform.smoothscale(temp_surface, 
                                                      (rank_surface.get_width(), rank_surface.get_height()))
        
        return rank_surface
    
    def create_suit_differentiated_card(self, card_id):
        """Create a card with suit-specific background color and royal crowns."""
        # Get suit information
        suit_char, suit_type = self.suit_assignments[card_id]
        
        # Create main card surface with suit-specific background color
        card_surface = pygame.Surface((self.size, self.size))
        background_color = self.card_backgrounds[suit_type]
        card_surface.fill(background_color)
        
        # All symbols are red for visibility
        color = self.symbol_color
        
        # Create suit symbol surface
        suit_surface = self.create_suit_surface(suit_type, self.suit_symbol_size, color)
        
        # Create rank text surface
        rank_surface = self.create_rank_surface(card_id, self.rank_font_size, color)
        
        # Position suit symbol in top-right corner
        suit_x = self.size - self.suit_symbol_size - self.corner_padding
        suit_y = self.corner_padding
        
        # Position rank text in bottom-left corner
        rank_x = self.corner_padding
        rank_y = self.size - rank_surface.get_height() - self.corner_padding
        
        # Blit suit symbol to top-right
        card_surface.blit(suit_surface, (suit_x, suit_y))
        
        # Blit rank text to bottom-left
        card_surface.blit(rank_surface, (rank_x, rank_y))
        
        # Add crown for K and Q cards
        display_rank = card_id.split('_')[0] if '_' in card_id else card_id
        if display_rank in ['K', 'Q']:
            crown_size = self.suit_symbol_size // 2
            crown_array = self.create_crown_decoration(crown_size)
            
            crown_surface = pygame.Surface((crown_size, crown_size), pygame.SRCALPHA)
            pygame.surfarray.blit_array(crown_surface, crown_array.swapaxes(0, 1))
            
            # Position crown above the suit symbol
            crown_x = suit_x + (self.suit_symbol_size - crown_size) // 2
            crown_y = suit_y - crown_size - 5  # 5px gap above suit
            
            if crown_y >= 0:  # Only draw if it fits
                card_surface.blit(crown_surface, (crown_x, crown_y))
        
        return card_surface
    
    def generate_symbol(self, card_id):
        """Generate a suit-differentiated card symbol."""
        return self.create_suit_differentiated_card(card_id)
    
    def numpy_to_pygame_surface(self, img_array):
        """Convert numpy array to pygame surface (for compatibility)."""
        if isinstance(img_array, pygame.Surface):
            return img_array
        
        if img_array.dtype != np.uint8:
            img_array = img_array.astype(np.uint8)
        
        surface = pygame.Surface((img_array.shape[1], img_array.shape[0]))
        pygame.surfarray.blit_array(surface, img_array.swapaxes(0, 1))
        return surface
    
    def get_symbol_pairs(self, count=18):
        """Get pairs of suit-differentiated playing card symbols."""
        selected_cards = self.ranks[:count]
        symbol_surfaces = {}
        
        for card_id in selected_cards:
            symbol_surface = self.generate_symbol(card_id)
            symbol_surfaces[card_id] = symbol_surface
        
        # Create pairs
        pairs = []
        for card_id in selected_cards:
            pairs.extend([card_id, card_id])
        
        random.shuffle(pairs)
        return pairs, symbol_surfaces

# Backward compatibility aliases
Enhanced6x6CardGenerator = SuitDifferentiatedCardGenerator
HighQualityCardGenerator = SuitDifferentiatedCardGenerator
SplitLayoutCardGenerator = SuitDifferentiatedCardGenerator
CompleteCardGenerator = SuitDifferentiatedCardGenerator
ProfessionalCardGenerator = SuitDifferentiatedCardGenerator
PlayingCardGenerator = SuitDifferentiatedCardGenerator
SymbolGenerator = SuitDifferentiatedCardGenerator
