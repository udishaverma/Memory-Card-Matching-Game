"""
Memory Match Game - Main Entry Point
A responsive card-matching memory game with full-screen support.
"""

import pygame
import sys
from enum import Enum

from game.board import Board
from ui.button import Button, ButtonAnchor
from ui.theme import (
    COLORS, DEFAULT_WINDOW_SIZE, ResponsiveLayout, 
    get_font, draw_overlay
)

class GameState(Enum):
    """Game states for the application."""
    MENU = 1
    GRID_SELECTION = 2
    PLAYING = 3
    GAME_OVER = 4

class MemoryMatchGame:
    """Main game class with full-screen and responsive support."""
    
    def __init__(self):
        pygame.init()
        
        # Display setup with proper flags to eliminate artifacts
        self.is_fullscreen = False
        display_flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | display_flags)
        else:
            self.screen = pygame.display.set_mode(DEFAULT_WINDOW_SIZE, display_flags)
        
        pygame.display.set_caption("Memory Match - Playing Cards")
        
        # Create a dedicated render buffer to prevent artifacts
        self.render_buffer = pygame.Surface(self.screen.get_size()).convert()
        
        # Responsive layout system
        self.layout = ResponsiveLayout(self.screen.get_size())
        
        # Game state
        self.state = GameState.MENU
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Grid size configuration
        self.grid_size = None  # Will be set by user choice (4 or 6)
        self.pairs_count = None  # Will be calculated based on grid size
        
        # Game components (will be initialized after grid selection)
        self.board = None
        
        # UI elements
        self.setup_ui()
        
        # Fonts will be managed by layout system
        self.title_font = None
        self.message_font = None
        self.score_font = None
        self.update_fonts()
    
    def setup_ui(self):
        """Set up UI buttons with responsive anchoring and proper spacing."""
        # Start Game button (for menu)
        self.start_button = Button("Start Game", ButtonAnchor.CENTER)
        
        # Grid size selection buttons
        self.grid_4x4_button = Button("4x4 Grid (8 Pairs)", ButtonAnchor.CENTER, offset_y=-30)
        self.grid_6x6_button = Button("6x6 Grid (18 Pairs)", ButtonAnchor.CENTER, offset_y=30)
        self.back_button = Button("Back to Menu", ButtonAnchor.CENTER, offset_y=80)
        
        # Reset Game button (for during gameplay) - anchored to top
        self.reset_button = Button("Reset Game", ButtonAnchor.TOP_CENTER)
        
        # Play Again button (for game over) - will be positioned dynamically
        self.play_again_button = Button("Play Again", ButtonAnchor.CENTER, offset_y=0)
        
        # Update layout for all buttons
        self.update_ui_layout()
    
    def get_safe_font_size(self, base_size, max_height_ratio=0.15):
        """Get a safe font size that won't cause overlap based on window height."""
        max_allowed_height = int(self.layout.window_height * max_height_ratio)
        safe_size = min(base_size, max_allowed_height)
        return max(16, safe_size)  # Minimum readable size
    
    def update_fonts(self):
        """Update fonts based on current layout with arcade-style fonts."""
        from ui.theme import get_arcade_font
        self.title_font = get_arcade_font(self.layout.font_sizes['title'])
        self.message_font = get_arcade_font(self.layout.font_sizes['message'])
        self.score_font = get_arcade_font(self.layout.font_sizes['score'])
    
    def update_ui_layout(self):
        """Update UI layout for responsive design."""
        self.start_button.update_layout(self.layout)
        self.grid_4x4_button.update_layout(self.layout)
        self.grid_6x6_button.update_layout(self.layout)
        self.back_button.update_layout(self.layout)
        self.reset_button.update_layout(self.layout)
        self.play_again_button.update_layout(self.layout)
    
    def handle_resize(self, new_size):
        """Handle window resize events and ensure high-quality cards render properly."""
        self.layout.resize(new_size)
        
        # Regenerate cards with new layout to ensure proper scaling
        self.board.update_layout(self.layout)
        
        # Update UI layout
        self.update_ui_layout()
        self.update_fonts()
        
        # Force high-quality card regeneration for new size if game is active
        if self.state == GameState.PLAYING and hasattr(self.board, 'card_generator'):
            # Update card generator size based on new layout (larger for better visibility)
            new_card_size = max(320, int(self.layout.card_size * 1.4))  # 40% larger for quality
            self.board.card_generator = type(self.board.card_generator)(size=new_card_size)
            
            # Regenerate all card symbols with enhanced quality
            for card in self.board.cards:
                try:
                    new_symbol = self.board.card_generator.generate_symbol(card.symbol)
                    card.symbol_surface = new_symbol
                except:
                    pass  # Keep existing symbol if regeneration fails
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            # Switch to fullscreen
            self.screen = pygame.display.set_mode(
                (0, 0), 
                pygame.FULLSCREEN | pygame.RESIZABLE
            )
        else:
            # Switch to windowed mode
            self.screen = pygame.display.set_mode(
                DEFAULT_WINDOW_SIZE, 
                pygame.RESIZABLE
            )
        
        # Update layout for new screen size
        self.handle_resize(self.screen.get_size())
    
    def handle_events(self):
        """Handle all game events including full-screen controls."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.is_fullscreen:
                        self.toggle_fullscreen()
                    else:
                        self.running = False
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_RETURN and pygame.key.get_pressed()[pygame.K_LALT]:
                    # Alt+Enter for fullscreen toggle
                    self.toggle_fullscreen()
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.handle_resize(event.size)
            
            # Handle state-specific events
            if self.state == GameState.MENU:
                self.handle_menu_events(event)
            elif self.state == GameState.GRID_SELECTION:
                self.handle_grid_selection_events(event)
            elif self.state == GameState.PLAYING:
                self.handle_playing_events(event)
            elif self.state == GameState.GAME_OVER:
                self.handle_game_over_events(event)
    
    def handle_menu_events(self, event):
        """Handle events in the menu state."""
        if self.start_button.handle_event(event):
            self.state = GameState.GRID_SELECTION
    
    def handle_grid_selection_events(self, event):
        """Handle events in the grid selection state."""
        if self.grid_4x4_button.handle_event(event):
            self.setup_game(4)  # 4x4 grid with 8 pairs
        elif self.grid_6x6_button.handle_event(event):
            self.setup_game(6)  # 6x6 grid with 18 pairs
        elif self.back_button.handle_event(event):
            self.state = GameState.MENU
    
    def handle_playing_events(self, event):
        """Handle events during gameplay with optimized artifact prevention."""
        if self.reset_button.handle_event(event):
            self.reset_game()
        else:
            # Handle board events normally
            self.board.handle_event(event)
    
    def handle_game_over_events(self, event):
        """Handle events in the game over state."""
        if self.play_again_button.handle_event(event):
            self.start_game()
        
        # Add keyboard support for game over screen
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # Space or Enter to play again
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                # ESC to quit
                if self.is_fullscreen:
                    self.toggle_fullscreen()
                else:
                    self.running = False
    
    def setup_game(self, grid_size):
        """Setup game with specified grid size."""
        self.grid_size = grid_size
        self.pairs_count = (grid_size * grid_size) // 2
        
        # Update layout for new grid size
        self.layout.set_grid_size(grid_size)
        
        # Create board with specified grid size
        self.board = Board(self.layout, grid_size, self.pairs_count)
        self.state = GameState.PLAYING
    
    def start_game(self):
        """Start a new game with current settings."""
        if self.board:
            self.board.reset()
            self.state = GameState.PLAYING
        else:
            # No grid selected, go to grid selection
            self.state = GameState.GRID_SELECTION
    
    def reset_game(self):
        """Reset the current game."""
        self.board.reset()
    
    def update(self):
        """Update game state."""
        if self.state == GameState.PLAYING:
            self.board.update()
            
            # Check for win condition
            if self.board.is_game_won():
                self.state = GameState.GAME_OVER
    
    def draw(self):
        """Ultra-optimized rendering to eliminate all lag."""
        try:
            # Use the most efficient rendering path
            if hasattr(self, 'render_buffer') and self.render_buffer:
                # Buffer-based rendering for stability
                self.render_buffer.fill(COLORS['background'])
                
                # Draw to buffer with minimal operations
                original_screen = self.screen
                self.screen = self.render_buffer
                
                if self.state == GameState.MENU:
                    self.draw_menu()
                elif self.state == GameState.GRID_SELECTION:
                    self.draw_grid_selection()
                elif self.state == GameState.PLAYING:
                    self.draw_game()
                elif self.state == GameState.GAME_OVER:
                    self.draw_game_over()
                
                self.screen = original_screen
                
                # Single blit operation
                self.screen.blit(self.render_buffer, (0, 0))
            else:
                # Direct rendering fallback
                self.screen.fill(COLORS['background'])
                if self.state == GameState.MENU:
                    self.draw_menu()
                elif self.state == GameState.GRID_SELECTION:
                    self.draw_grid_selection()
                elif self.state == GameState.PLAYING:
                    self.draw_game()
                elif self.state == GameState.GAME_OVER:
                    self.draw_game_over()
        
        except Exception as e:
            # Ultra-fast error recovery
            self.screen.fill(COLORS['background'])
        
        # Single display update
        pygame.display.flip()
    
    def draw_menu_to_buffer(self):
        """Draw menu to render buffer."""
        # Temporarily redirect screen to buffer
        original_screen = self.screen
        self.screen = self.render_buffer
        self.draw_menu()
        self.screen = original_screen
    
    def draw_game_to_buffer(self):
        """Draw game to render buffer."""
        original_screen = self.screen
        self.screen = self.render_buffer
        self.draw_game()
        self.screen = original_screen
    
    def draw_game_over_to_buffer(self):
        """Draw game over to render buffer."""
        original_screen = self.screen
        self.screen = self.render_buffer
        self.draw_game_over()
        self.screen = original_screen
    
    def draw_menu(self):
        """Draw the main menu with enhanced fonts and proper button positioning."""
        from ui.theme import get_arcade_font
        
        # Calculate safe font sizes based on screen dimensions
        screen_height = self.layout.window_height
        screen_width = self.layout.window_width
        
        # Enhanced title font - much larger but safe
        max_title_height = int(screen_height * 0.10)  # Reduced from 12% to 10%
        title_font_size = min(max_title_height, 64)   # Reduced cap from 72px to 64px
        title_font_size = max(title_font_size, 32)    # Minimum 32px
        
        # Enhanced subtitle font - larger but proportional
        max_subtitle_height = int(screen_height * 0.05)  # Reduced from 6% to 5%
        subtitle_font_size = min(max_subtitle_height, 32)  # Reduced cap from 36px to 32px
        subtitle_font_size = max(subtitle_font_size, 18)   # Minimum 18px
        
        # Enhanced instruction font - readable but compact
        max_instruction_height = int(screen_height * 0.035)  # Reduced from 4% to 3.5%
        instruction_font_size = min(max_instruction_height, 20)  # Reduced cap from 24px to 20px
        instruction_font_size = max(instruction_font_size, 14)   # Minimum 14px
        
        # Create fonts with calculated sizes
        title_font = get_arcade_font(title_font_size)
        subtitle_font = get_arcade_font(subtitle_font_size)
        instruction_font = get_arcade_font(instruction_font_size)
        
        # Enhanced title positioning
        title_text = title_font.render("PLAYING CARD MEMORY", True, COLORS['text'])
        title_width = title_text.get_width()
        
        # Ensure title fits on screen
        if title_width > screen_width * 0.9:
            while title_width > screen_width * 0.9 and title_font_size > 24:
                title_font_size -= 2
                title_font = get_arcade_font(title_font_size)
                title_text = title_font.render("PLAYING CARD MEMORY", True, COLORS['text'])
                title_width = title_text.get_width()
        
        # Position title higher to make room for content
        title_y = screen_height // 4  # Changed from // 3 to // 4
        title_rect = title_text.get_rect(center=(screen_width // 2, title_y))
        self.screen.blit(title_text, title_rect)
        
        # Enhanced subtitle positioning with proper spacing
        subtitle_y = title_rect.bottom + max(15, screen_height // 50)  # Reduced spacing
        subtitle_text = subtitle_font.render("MATCH ALL 18 PAIRS!", True, COLORS['accent'])
        subtitle_rect = subtitle_text.get_rect(center=(screen_width // 2, subtitle_y))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Enhanced instructions with better spacing
        instructions = [
            "Click cards to reveal suit-differentiated symbols",
            "Match pairs: A♠ K♥ Q♦ J♣ 10♠ 10♥ 9♦ 9♣ 8♠ 8♥ etc.",
            "Colored backgrounds & crowns for royalty!",
            "",
            "F11 or Alt+Enter: Toggle fullscreen",
            "SPACE/Enter: Play Again (on win screen)",
            "ESC: Quit game (or exit fullscreen)"
        ]
        
        # Calculate instruction area with reserved space for button
        button_height = self.layout.button_height
        button_margin = max(40, screen_height // 20)  # Space above button
        available_height = screen_height - subtitle_rect.bottom - button_height - button_margin - 40
        
        instruction_start_y = subtitle_rect.bottom + max(20, screen_height // 40)
        line_spacing = max(6, screen_height // 100)  # Reduced line spacing
        current_y = instruction_start_y
        
        for i, instruction in enumerate(instructions):
            if instruction:  # Skip empty lines for spacing
                color = COLORS['accent'] if i == 1 else COLORS['text']  # Highlight card list
                
                # Check if we have room for this line
                if current_y + instruction_font_size > instruction_start_y + available_height:
                    break  # Stop adding instructions if we run out of room
                
                # Check if instruction fits on screen width
                test_text = instruction_font.render(instruction, True, color)
                if test_text.get_width() > screen_width * 0.9:
                    # Split long instructions into multiple lines
                    words = instruction.split()
                    lines = []
                    current_line = ""
                    
                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        test_surface = instruction_font.render(test_line, True, color)
                        if test_surface.get_width() <= screen_width * 0.9:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines.append(current_line)
                    
                    # Draw split lines
                    for line in lines:
                        if current_y + instruction_font_size > instruction_start_y + available_height:
                            break
                        line_text = instruction_font.render(line, True, color)
                        line_rect = line_text.get_rect(center=(screen_width // 2, current_y))
                        self.screen.blit(line_text, line_rect)
                        current_y += instruction_font_size + line_spacing
                else:
                    # Draw single line
                    instruction_text = instruction_font.render(instruction, True, color)
                    instruction_rect = instruction_text.get_rect(center=(screen_width // 2, current_y))
                    self.screen.blit(instruction_text, instruction_rect)
                    current_y += instruction_font_size + line_spacing
            else:
                # Add extra spacing for empty lines (but only if we have room)
                if current_y + line_spacing <= instruction_start_y + available_height:
                    current_y += line_spacing
        
        # Position start button at bottom with proper margin
        button_y = screen_height - button_height - 20  # 20px from bottom
        self.start_button.offset_y = button_y - screen_height // 2
        self.start_button.update_layout(self.layout)
        self.start_button.draw(self.screen)
    
        # Draw start button with enhanced positioning
        self.start_button.draw(self.screen)
    
    def draw_grid_selection(self):
        """Draw the grid selection screen with proper spacing."""
        from ui.theme import get_arcade_font
        
        screen_height = self.layout.window_height
        screen_width = self.layout.window_width
        
        # Calculate safe font sizes to prevent overlap
        title_font_size = min(int(screen_height * 0.06), 36)  # Reduced from 0.08
        title_font = get_arcade_font(title_font_size)
        title_text = title_font.render("CHOOSE GRID SIZE", True, COLORS['text'])
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 5))  # Higher position
        self.screen.blit(title_text, title_rect)
        
        # Subtitle with proper spacing
        subtitle_font_size = min(int(screen_height * 0.03), 20)  # Reduced from 0.04
        subtitle_font = get_arcade_font(subtitle_font_size)
        subtitle_text = subtitle_font.render("Select your preferred difficulty level", True, COLORS['accent'])
        subtitle_rect = subtitle_text.get_rect(center=(screen_width // 2, title_rect.bottom + 20))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Calculate button area to ensure no overlap
        available_height = screen_height - subtitle_rect.bottom - 100  # Reserve space at bottom
        button_spacing = max(20, available_height // 8)  # Dynamic spacing
        
        # Position buttons with calculated spacing
        button_start_y = subtitle_rect.bottom + button_spacing
        
        # Update button positions to prevent overlap
        self.grid_4x4_button.offset_y = button_start_y - screen_height // 2
        self.grid_6x6_button.offset_y = button_start_y + button_spacing * 2 - screen_height // 2
        self.back_button.offset_y = button_start_y + button_spacing * 4 - screen_height // 2
        
        # Update button layouts
        self.grid_4x4_button.update_layout(self.layout)
        self.grid_6x6_button.update_layout(self.layout)
        self.back_button.update_layout(self.layout)
        
        # Draw buttons
        self.grid_4x4_button.draw(self.screen)
        self.grid_6x6_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # Add descriptions with safe positioning
        desc_font_size = min(int(screen_height * 0.025), 16)  # Reduced from 0.03
        desc_font = get_arcade_font(desc_font_size)
        
        # 4x4 description - positioned below button
        desc_4x4 = desc_font.render("Easier - Perfect for quick games", True, COLORS['text'])
        desc_4x4_y = self.grid_4x4_button.rect.bottom + 8
        desc_4x4_rect = desc_4x4.get_rect(center=(screen_width // 2, desc_4x4_y))
        self.screen.blit(desc_4x4, desc_4x4_rect)
        
        # 6x6 description - positioned below button
        desc_6x6 = desc_font.render("Challenging - Full memory workout", True, COLORS['text'])
        desc_6x6_y = self.grid_6x6_button.rect.bottom + 8
        desc_6x6_rect = desc_6x6.get_rect(center=(screen_width // 2, desc_6x6_y))
        self.screen.blit(desc_6x6, desc_6x6_rect)

    def draw_game(self):
        """Draw the game board and UI."""
        # Draw board
        self.board.draw(self.screen)
        
        # Draw score
        score_text = self.board.get_score_text()
        score_surface = self.score_font.render(score_text, True, COLORS['text'])
        self.screen.blit(score_surface, (20, 20))
        
        # Draw reset button
        self.reset_button.draw(self.screen)
    
    def draw_game_over(self):
        """Draw the game over screen with proper spacing to prevent font overlap."""
        try:
            # Draw the board (still visible)
            self.board.draw(self.screen)
            
            # Draw semi-transparent overlay
            draw_overlay(self.screen)
            
            # Calculate proper spacing based on window size
            center_x = self.layout.window_width // 2
            center_y = self.layout.window_height // 2
            
            # Use safe font sizes to prevent overlap - ensure integers
            message_font_size = int(self.layout.font_sizes['message'])
            title_font_size = self.get_safe_font_size(message_font_size, 0.08)
            subtitle_font_size = self.get_safe_font_size(int(message_font_size * 0.8), 0.06)
            
            # Create fonts with safe sizes
            from ui.theme import get_arcade_font
            title_font = get_arcade_font(title_font_size)
            subtitle_font = get_arcade_font(subtitle_font_size)
            
            # Create text surfaces with dynamic pair count
            pairs_text = f"ALL {self.pairs_count} PAIRS MATCHED!" if self.pairs_count else "ALL PAIRS MATCHED!"
            title_text = title_font.render("GAME COMPLETE!", True, COLORS['text'])
            subtitle_text = subtitle_font.render(pairs_text, True, COLORS['accent'])
            
            # Calculate dimensions
            title_height = title_text.get_height()
            subtitle_height = subtitle_text.get_height()
            
            # Calculate safe spacing (minimum 15px, scales with window)
            text_spacing = max(15, self.layout.window_height // 30)
            button_spacing = max(30, self.layout.window_height // 15)
            
            # Calculate total content height
            total_content_height = title_height + text_spacing + subtitle_height + button_spacing + self.layout.button_height
            
            # Start positioning from top of content area
            content_start_y = center_y - total_content_height // 2
            
            # Position title
            title_y = content_start_y
            title_rect = title_text.get_rect(center=(center_x, title_y + title_height // 2))
            self.screen.blit(title_text, title_rect)
            
            # Position subtitle with spacing
            subtitle_y = title_y + title_height + text_spacing
            subtitle_rect = subtitle_text.get_rect(center=(center_x, subtitle_y + subtitle_height // 2))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            # Position play again button with extra spacing
            button_y = subtitle_y + subtitle_height + button_spacing
            self.play_again_button.offset_y = button_y - center_y
            
            # Update button layout to ensure it's positioned correctly
            self.play_again_button.update_layout(self.layout)
            
            # Draw play again button
            self.play_again_button.draw(self.screen)
            
        except Exception as e:
            print(f"Error drawing game over screen: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback simple game over screen with keyboard instructions
            try:
                font = pygame.font.Font(None, 48)
                title_text = font.render("GAME COMPLETE!", True, COLORS['text'])
                title_rect = title_text.get_rect(center=(self.layout.window_width // 2, self.layout.window_height // 2 - 80))
                self.screen.blit(title_text, title_rect)
                
                # Dynamic pair count message
                pairs_message = f"All {self.pairs_count} pairs matched!" if self.pairs_count else "All pairs matched!"
                subtitle_text = font.render(pairs_message, True, COLORS['accent'])
                subtitle_rect = subtitle_text.get_rect(center=(self.layout.window_width // 2, self.layout.window_height // 2 - 30))
                self.screen.blit(subtitle_text, subtitle_rect)
                
                # Keyboard instructions
                instruction_font = pygame.font.Font(None, 36)
                space_text = instruction_font.render("Press SPACE to Play Again", True, COLORS['text'])
                space_rect = space_text.get_rect(center=(self.layout.window_width // 2, self.layout.window_height // 2 + 30))
                self.screen.blit(space_text, space_rect)
                
                esc_text = instruction_font.render("Press ESC to Quit", True, COLORS['text'])
                esc_rect = esc_text.get_rect(center=(self.layout.window_width // 2, self.layout.window_height // 2 + 70))
                self.screen.blit(esc_text, esc_rect)
                
            except Exception as fallback_error:
                print(f"Fallback error: {fallback_error}")
                # Ultimate fallback
                simple_font = pygame.font.Font(None, 36)
                simple_text = simple_font.render("Game Complete! Press ESC to quit", True, (255, 255, 255))
                simple_rect = simple_text.get_rect(center=(self.layout.window_width // 2, self.layout.window_height // 2))
                self.screen.blit(simple_text, simple_rect)
    
    def run(self):
        """Main game loop with proper frame timing to prevent artifacts."""
        while self.running:
            try:
                # Handle events
                self.handle_events()
                
                # Update game state
                self.update()
                
                # Draw everything
                self.draw()
                
                # Control frame rate precisely
                self.clock.tick(60)  # Exactly 60 FPS
                
            except Exception as e:
                print(f"Game loop error: {e}")
                # Clear screen on error
                self.screen.fill(COLORS['background'])
                pygame.display.flip()
                continue
        
        pygame.quit()
        sys.exit()

def main():
    """Entry point for the game."""
    try:
        game = MemoryMatchGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
