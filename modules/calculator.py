"""
Calculator Module for LightBerry OS
"""

import pygame
import math
from config.constants import *
# BlackBerry keyboard support (Alt + key combinations)
BLACKBERRY_KEYS = {
    pygame.K_w: '1', pygame.K_e: '2', pygame.K_r: '3',
    pygame.K_s: '4', pygame.K_d: '5', pygame.K_f: '6',
    pygame.K_z: '7', pygame.K_x: '8', pygame.K_c: '9',
    pygame.K_v: '0'  # Assuming microphone key is mapped to V
}


class Calculator:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_calculator()
    
    def init_calculator(self):
        """Initialize calculator state"""
        self.display = "0"
        self.previous_value = 0
        self.current_value = 0
        self.operation = None
        self.new_input = True
        self.decimal_entered = False
        self.error = False
        self.history = []
        self.memory = 0
        self.advanced_mode = False
        self.show_info = False
        
        # Button animation
        self.button_press_time = 0
        self.pressed_button = -1
        
        # Navigation
        self.selected_button = 0
        self.setup_buttons()
    
    def setup_buttons(self):
        """Setup calculator buttons based on mode"""
        if self.advanced_mode:
            self.buttons = [
                # Row 0
                ["sin", "cos", "tan", "log"],
                # Row 1
                ["MC", "MR", "M+", "M-"],
                # Row 2
                ["C", "CE", "√", "÷"],
                # Row 3
                ["7", "8", "9", "×"],
                # Row 4
                ["4", "5", "6", "-"],
                # Row 5
                ["1", "2", "3", "+"],
                # Row 6
                ["0", ".", "=", "π"]
            ]
        else:
            self.buttons = [
                # Row 0
                ["C", "CE", "√", "÷"],
                # Row 1
                ["7", "8", "9", "×"],
                # Row 2
                ["4", "5", "6", "-"],
                # Row 3
                ["1", "2", "3", "+"],
                # Row 4
                ["0", ".", "=", "Mode"]
            ]
        
        self.rows = len(self.buttons)
        self.cols = len(self.buttons[0]) if self.buttons else 0
        
        # Calculate button dimensions based on mode
        if self.advanced_mode:
            # Advanced mode: one square wider than before
            display_width = 400  # Increased width
            self.button_width = (display_width - 20) // self.cols
            self.button_height = 18  # Smaller for advanced mode
            self.grid_start_y = 80
        else:
            # Basic mode: larger size (400x240)
            display_width = 400
            self.button_width = (display_width - 20) // self.cols
            self.button_height = 28  # Larger for basic mode
            self.grid_start_y = 70
    
    def handle_events(self, event):
        """Handle calculator events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            elif event.key == pygame.K_i:
                self.show_info = not self.show_info
            elif event.key == pygame.K_UP:
                self.selected_button = max(0, self.selected_button - self.cols)
            elif event.key == pygame.K_DOWN:
                max_button = self.rows * self.cols - 1
                self.selected_button = min(max_button, self.selected_button + self.cols)
            elif event.key == pygame.K_LEFT:
                if self.selected_button % self.cols > 0:
                    self.selected_button -= 1
            elif event.key == pygame.K_RIGHT:
                if self.selected_button % self.cols < self.cols - 1:
                    max_button = self.rows * self.cols - 1
                    if self.selected_button < max_button:
                        self.selected_button += 1
            elif event.key == pygame.K_RETURN:
                self.press_button(self.selected_button)
            elif event.key == pygame.K_m:
                self.advanced_mode = not self.advanced_mode
                self.setup_buttons()
                self.selected_button = 0
            # Direct number input
            elif event.key >= pygame.K_0 and event.key <= pygame.K_9:
                number = str(event.key - pygame.K_0)
                self.input_number(number)
            elif event.key == pygame.K_PERIOD:
                self.input_decimal()
            elif event.key == pygame.K_PLUS:
                self.input_operation("+")
            elif event.key == pygame.K_MINUS:
                self.input_operation("-")
            elif event.key == pygame.K_ASTERISK:
                self.input_operation("×")
            elif event.key == pygame.K_SLASH:
                self.input_operation("÷")
            elif event.key == pygame.K_EQUALS:
                self.calculate()
            elif event.key in BLACKBERRY_KEYS and (event.mod & pygame.KMOD_ALT):
                number = BLACKBERRY_KEYS[event.key]
                self.input_number(number)
        
        return None
    
    def press_button(self, button_index):
        """Press a button by index"""
        if 0 <= button_index < self.rows * self.cols:
            row = button_index // self.cols
            col = button_index % self.cols
            
            if row < len(self.buttons) and col < len(self.buttons[row]):
                button_text = self.buttons[row][col]
                self.handle_button_press(button_text)
                
                # Animation
                self.pressed_button = button_index
                self.button_press_time = pygame.time.get_ticks()
    
    def handle_button_press(self, button_text):
        """Handle button press"""
        if button_text.isdigit():
            self.input_number(button_text)
        elif button_text == ".":
            self.input_decimal()
        elif button_text in ["+", "-", "×", "÷"]:
            self.input_operation(button_text)
        elif button_text == "=":
            self.calculate()
        elif button_text == "C":
            self.clear_all()
        elif button_text == "CE":
            self.clear_entry()
        elif button_text == "Mode":
            self.advanced_mode = not self.advanced_mode
            self.setup_buttons()
            self.selected_button = 0
        elif button_text == "√":
            self.square_root()
        elif button_text == "π":
            self.display = str(round(math.pi, 8))
            self.new_input = True
        elif button_text == "sin":
            self.trigonometric("sin")
        elif button_text == "cos":
            self.trigonometric("cos")
        elif button_text == "tan":
            self.trigonometric("tan")
        elif button_text == "log":
            self.logarithm()
        elif button_text == "MC":
            self.memory = 0
        elif button_text == "MR":
            self.display = str(self.memory)
            self.new_input = True
        elif button_text == "M+":
            self.memory += float(self.display)
        elif button_text == "M-":
            self.memory -= float(self.display)
    
    def input_number(self, number):
        """Input a number"""
        if self.error:
            self.clear_all()
        
        if self.new_input:
            self.display = number
            self.new_input = False
        else:
            if len(self.display) < 10:
                self.display = self.display + number
    
    def input_decimal(self):
        """Input decimal point"""
        if self.error:
            self.clear_all()
        
        if self.new_input:
            self.display = "0."
            self.new_input = False
            self.decimal_entered = True
        elif not self.decimal_entered:
            self.display += "."
            self.decimal_entered = True
    
    def input_operation(self, op):
        """Input operation"""
        if self.error:
            self.clear_all()
        
        if self.operation is not None:
            self.calculate()
        
        self.previous_value = float(self.display)
        self.operation = op
        self.new_input = True
        self.decimal_entered = False
    
    def calculate(self):
        """Perform calculation"""
        if self.operation is None:
            return
        
        try:
            current = float(self.display)
            
            if self.operation == "+":
                result = self.previous_value + current
            elif self.operation == "-":
                result = self.previous_value - current
            elif self.operation == "×":
                result = self.previous_value * current
            elif self.operation == "÷":
                if current == 0:
                    self.display = "Error"
                    self.error = True
                    return
                result = self.previous_value / current
            
            # Add to history
            history_entry = f"{self.previous_value} {self.operation} {current} = {result}"
            self.history.append(history_entry)
            if len(self.history) > 10:
                self.history.pop(0)
            
            # Format result
            if result == int(result):
                self.display = str(int(result))
            else:
                self.display = str(round(result, 8))
            
            self.operation = None
            self.new_input = True
            self.decimal_entered = False
            
        except:
            self.display = "Error"
            self.error = True
    
    def clear_all(self):
        """Clear all"""
        self.display = "0"
        self.previous_value = 0
        self.current_value = 0
        self.operation = None
        self.new_input = True
        self.decimal_entered = False
        self.error = False
    
    def clear_entry(self):
        """Clear current entry"""
        self.display = "0"
        self.new_input = True
        self.decimal_entered = False
        self.error = False
    
    def square_root(self):
        """Square root function"""
        try:
            value = float(self.display)
            if value < 0:
                self.display = "Error"
                self.error = True
            else:
                result = math.sqrt(value)
                self.display = str(round(result, 8))
                self.new_input = True
        except:
            self.display = "Error"
            self.error = True
    
    def trigonometric(self, func):
        """Trigonometric functions"""
        try:
            value = float(self.display)
            radians = math.radians(value)
            
            if func == "sin":
                result = math.sin(radians)
            elif func == "cos":
                result = math.cos(radians)
            elif func == "tan":
                result = math.tan(radians)
            
            self.display = str(round(result, 8))
            self.new_input = True
        except:
            self.display = "Error"
            self.error = True
    
    def logarithm(self):
        """Logarithm function"""
        try:
            value = float(self.display)
            if value <= 0:
                self.display = "Error"
                self.error = True
            else:
                result = math.log10(value)
                self.display = str(round(result, 8))
                self.new_input = True
        except:
            self.display = "Error"
            self.error = True
    
    def update(self):
        """Update calculator state"""
        # Reset button animation
        if pygame.time.get_ticks() - self.button_press_time > 200:
            self.pressed_button = -1
    
    def draw(self, screen):
        """Draw calculator interface"""
        # Header
        header_text = "Calculator"
        if self.advanced_mode:
            header_text += " (Advanced)"
        
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Display
        display_width = 400  # Both modes use 400 width now
        display_rect = pygame.Rect(10, 30, display_width - 20, 35)
        pygame.draw.rect(screen, BUTTON_COLOR, display_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, display_rect, 2)
        
        # Display text
        display_text = self.display
        if len(display_text) > 12:
            display_text = display_text[:12] + "..."
        
        display_surface = self.os.font_l.render(display_text, True, TEXT_COLOR)
        display_x = display_rect.right - display_surface.get_width() - 10
        display_y = display_rect.centery - display_surface.get_height() // 2
        screen.blit(display_surface, (display_x, display_y))
        
        # Buttons
        for row in range(self.rows):
            for col in range(self.cols):
                if row < len(self.buttons) and col < len(self.buttons[row]):
                    button_index = row * self.cols + col
                    button_text = self.buttons[row][col]
                    
                    # Button position
                    x = 10 + col * self.button_width
                    y = self.grid_start_y + row * (self.button_height + 2)
                    
                    # Button rectangle
                    button_rect = pygame.Rect(x, y, self.button_width - 2, self.button_height)
                    
                    # Button color
                    if button_index == self.pressed_button:
                        button_color = BUTTON_ACTIVE_COLOR
                    elif button_index == self.selected_button:
                        button_color = BUTTON_HOVER_COLOR
                    else:
                        button_color = BUTTON_COLOR
                    
                    # Special colors for operation buttons
                    if button_text in ["+", "-", "×", "÷", "="]:
                        button_color = tuple(min(255, c + 30) for c in button_color)
                    
                    pygame.draw.rect(screen, button_color, button_rect)
                    
                    # Button border
                    border_color = BUTTON_SELECTED_BORDER if button_index == self.selected_button else BUTTON_BORDER_COLOR
                    pygame.draw.rect(screen, border_color, button_rect, 2)
                    
                    # Button text
                    text_surface = self.os.font_s.render(button_text, True, TEXT_COLOR)
                    text_x = button_rect.centerx - text_surface.get_width() // 2
                    text_y = button_rect.centery - text_surface.get_height() // 2
                    screen.blit(text_surface, (text_x, text_y))
        
        # Info display removed - h key disabled
    
    
    def load_data(self, data):
        """Load calculator data"""
        self.history = data.get("history", [])
        self.memory = data.get("memory", 0)
        self.advanced_mode = data.get("advanced_mode", False)
        self.setup_buttons()
