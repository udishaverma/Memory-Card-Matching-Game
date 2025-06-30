"""
Board class for the Memory Match Game.
Handles grid logic, pair checking, win conditions, and proper flip-back timing.
"""

import pygame
import time
import random
from .card import Card, CardState
from .assets import SuitDifferentiatedCardGenerator
from ui.theme import GRID_ROWS, GRID_COLS, CARD_SPACING, GRID_MARGIN, MISMATCH_DELAY, PAIRS_COUNT

class Board:
    """Manages the 4x4 game board with playing card symbols."""
    
    def __init__(self, layout, grid_size=6, pairs_count=18):
        self.layout = layout
        self.grid_size = grid_size  # 4 for 4x4, 6 for 6x6
        self.pairs_count = pairs_count  # 8 for 4x4, 18 for 6x6
        self.cards = []
        self.flipped_cards = []  # Currently face-up cards (max 2)
        self.matched_pairs = 0
        self.card_generator = SuitDifferentiatedCardGenerator(size=320)  # Larger cards with bigger elements
        
        # Timing for mismatch handling
        self.mismatch_timer = 0
        self.cards_to_flip_back = []
        self.clicks_disabled = False
        
        # Win condition timing
        self.game_won = False
        self.win_timer = 0  # Add delay before showing win screen
        self.win_delay = 1000  # 1 second delay to show final match
        
        # Rendering state to prevent artifacts
        self.is_rendering = False
        
        self.initialize_board()
    
    def initialize_board(self):
        """Initialize the game board with shuffled playing cards based on grid size."""
        # Clear existing state
        self.cards.clear()
        self.flipped_cards.clear()
        self.cards_to_flip_back.clear()
        self.matched_pairs = 0
        self.mismatch_timer = 0
        self.clicks_disabled = False
        self.game_won = False
        self.win_timer = 0  # Reset win timer
        
        # Generate playing card symbol pairs based on pairs count
        symbol_pairs, symbol_surfaces = self.card_generator.get_symbol_pairs(self.pairs_count)
        
        # Create cards in grid layout
        card_index = 0
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                symbol = symbol_pairs[card_index]
                symbol_surface = symbol_surfaces[symbol]
                
                card = Card(row, col, symbol, symbol_surface, self.layout, self.grid_size)
                self.cards.append(card)
                card_index += 1
    
    def update_layout(self, layout):
        """Update layout for all cards (for responsive design)."""
        self.layout = layout
        for card in self.cards:
            card.layout = layout
    
    def handle_event(self, event):
        """Handle events for the board with proper click prevention."""
        # Don't allow clicks during mismatch delay or when game is won
        if self.clicks_disabled or self.game_won:
            # Still handle hover events for visual feedback
            if event.type == pygame.MOUSEMOTION:
                for card in self.cards:
                    card.handle_event(event)
            return
        
        # Don't allow more than 2 cards to be flipped at once
        if len(self.flipped_cards) >= 2:
            return
        
        # Handle card clicks
        for card in self.cards:
            if card.handle_event(event):
                self.flip_card(card)
                break
    
    def flip_card(self, card):
        """Flip a card with complete artifact prevention."""
        if not card.is_clickable() or card in self.flipped_cards:
            return
        
        # Prevent clicks during rendering or transitions
        if self.clicks_disabled or self.win_timer > 0 or self.is_rendering:
            return
        
        # Set rendering flag to prevent interference
        self.is_rendering = True
        
        # Flip the card
        card.flip_to_visible()
        self.flipped_cards.append(card)
        
        # Clear rendering flag
        self.is_rendering = False
        
        # Check for matches when two cards are flipped
        if len(self.flipped_cards) == 2:
            self.check_match()
    
    def check_match(self):
        """Check if the two flipped cards match with proper timing."""
        if len(self.flipped_cards) != 2:
            return
        
        card1, card2 = self.flipped_cards
        
        if card1.symbol == card2.symbol:
            # Match found - mark cards as matched
            card1.set_matched()
            card2.set_matched()
            self.matched_pairs += 1
            self.flipped_cards.clear()
            
            # Check win condition with delay for final pair
            if self.matched_pairs == self.pairs_count:
                # Start win timer to allow final match animation to be seen
                self.win_timer = time.time() * 1000 + self.win_delay
                self.clicks_disabled = True  # Prevent clicks during win transition
        else:
            # No match - schedule cards to flip back after delay
            self.mismatch_timer = time.time() * 1000 + MISMATCH_DELAY
            self.cards_to_flip_back = self.flipped_cards.copy()
            self.clicks_disabled = True  # Prevent further clicks during delay
    
    def update(self):
        """Update the board state and handle timing."""
        # Update all card animations
        for card in self.cards:
            card.update()
        
        # Handle mismatch timer
        if self.mismatch_timer > 0:
            current_time = time.time() * 1000
            if current_time >= self.mismatch_timer:
                # Time to flip mismatched cards back
                for card in self.cards_to_flip_back:
                    if card.state == CardState.VISIBLE:  # Only flip if still visible
                        card.flip_to_hidden()
                
                # Clear state
                self.flipped_cards.clear()
                self.cards_to_flip_back.clear()
                self.mismatch_timer = 0
                self.clicks_disabled = False
        
        # Handle win timer - delay before showing win screen
        if self.win_timer > 0:
            current_time = time.time() * 1000
            if current_time >= self.win_timer:
                # Now it's safe to show the win screen
                self.game_won = True
                self.win_timer = 0
    
    def draw(self, surface):
        """Draw the board with rendering state management."""
        self.is_rendering = True
        
        try:
            # Draw each card
            for card in self.cards:
                card.draw(surface)
        except Exception as e:
            print(f"Board draw error: {e}")
        finally:
            self.is_rendering = False
    
    def reset(self):
        """Reset the board for a new game."""
        self.initialize_board()
    
    def is_game_won(self):
        """Check if the game has been won."""
        return self.game_won
    
    def get_score_text(self):
        """Get the current score as formatted text."""
        return f"Pairs Found: {self.matched_pairs}/{self.pairs_count}"
    
    def get_clickable_cards_count(self):
        """Get the number of cards that can currently be clicked."""
        return len([card for card in self.cards if card.is_clickable()])
    
    def get_visible_cards_count(self):
        """Get the number of currently visible (face-up) cards."""
        return len([card for card in self.cards if card.is_face_up()])
