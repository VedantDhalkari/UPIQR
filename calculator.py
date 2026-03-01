"""
Scientific Calculator Module
Premium scientific calculator for the dashboard
"""

import customtkinter as ctk
import math
import config

class ScientificCalculator(ctk.CTkToplevel):
    """Scientific Calculator Window"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Scientific Calculator")
        self.geometry("350x500")
        self.resizable(False, False)
        self.transient(parent)
        
        # Bind Keyboard Events - Use bind_all when focused or grab_set
        self.bind("<Key>", self._on_key_press)
        self.bind("<Return>", lambda e: self._on_click('='))
        self.bind("<BackSpace>", lambda e: self._on_click('⌫'))
        self.bind("<Escape>", lambda e: self.destroy())
        
        # Make calculator modal-like or just stay on top
        self.attributes("-topmost", True)
        self.focus_force()
        
        # Focus window
        self.after(100, self.focus_force)
        
        # Display
        self.result_var = ctk.StringVar(value="0")
        
        display_frame = ctk.CTkFrame(self, fg_color=config.COLOR_BG_CARD, height=80)
        display_frame.pack(fill="x", padx=10, pady=10)
        display_frame.pack_propagate(False)
        
        self.display = ctk.CTkLabel(
            display_frame,
            textvariable=self.result_var,
            font=("Consolas", 32, "bold"),
            anchor="e",
            text_color=config.COLOR_PRIMARY
        )
        self.display.pack(fill="both", expand=True, padx=10)
        
        # Buttons
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Grid layout
        buttons = [
            ('C', '⌫', '%', '/'),
            ('7', '8', '9', '*'),
            ('4', '5', '6', '-'),
            ('1', '2', '3', '+'),
            ('0', '.', '(', ')'),
            ('sin', 'cos', 'tan', 'sqrt'),
            ('^', 'log', 'π', '=')
        ]
        
        for i in range(7):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            buttons_frame.grid_columnconfigure(i, weight=1)
            
        for row_idx, row in enumerate(buttons):
            for col_idx, text in enumerate(row):
                btn_color = config.COLOR_PRIMARY
                hover_color = config.COLOR_PRIMARY_LIGHT
                text_color = "white"
                
                if text in ['C', '⌫']:
                    btn_color = config.COLOR_DANGER
                elif text in ['=', '+', '-', '*', '/', '%', '^']:
                    btn_color = config.COLOR_SECONDARY
                    hover_color = config.COLOR_SECONDARY_DARK
                elif text in ['sin', 'cos', 'tan', 'log', 'sqrt', 'π', '(', ')']:
                     btn_color = config.COLOR_INFO
                else:
                    btn_color = config.COLOR_BG_CARD
                    text_color = config.COLOR_TEXT_PRIMARY
                    hover_color = config.COLOR_BG_HOVER
                
                cmd = lambda t=text: self._on_click(t)
                
                ctk.CTkButton(
                    buttons_frame,
                    text=text,
                    font=("Arial", 14, "bold"),
                    fg_color=btn_color,
                    hover_color=hover_color,
                    text_color=text_color,
                    command=cmd,
                    width=60,
                    height=45
                ).grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="nsew")
                
        self.expression = ""
        self.new_calculation = True

    def _on_click(self, char):
        if char == 'C':
            self.expression = ""
            self.result_var.set("0")
            self.new_calculation = True
        elif char == '⌫':
            self.expression = self.expression[:-1]
            self.result_var.set(self.expression or "0")
        elif char == '=':
            self._evaluate()
        elif char == 'sqrt':
            self._evaluate_func(math.sqrt)
        elif char == 'sin':
            self._evaluate_func(math.sin)
        elif char == 'cos':
            self._evaluate_func(math.cos)
        elif char == 'tan':
            self._evaluate_func(math.tan)
        elif char == 'log':
            self._evaluate_func(math.log10)
        elif char == 'π':
            self._append(str(math.pi))
        elif char == '^':
            self._append('**')
        elif char == '%':
            self._append('/100')
        else:
            self._append(char)
            
    def _append(self, char):
        if self.new_calculation:
            self.expression = ""
            self.new_calculation = False
            
        self.expression += char
        self.result_var.set(self.expression)
        
    def _evaluate(self):
        try:
            # Safe evaluation? well, it's a calculator locally.
            # Using eval regarding `math` functions needs scope
            allowed_names = {"sin": math.sin, "cos": math.cos, "tan": math.tan, 
                             "sqrt": math.sqrt, "log": math.log10, "pi": math.pi}
            result = eval(self.expression, {"__builtins__": None}, allowed_names)
            self.result_var.set(str(result))
            self.expression = str(result)
            self.new_calculation = True
        except Exception:
            self.result_var.set("Error")
            self.expression = ""
            self.new_calculation = True

    def _evaluate_func(self, func):
        try:
            if not self.expression:
                val = 0
            else:
                val = float(eval(self.expression))
            
            res = func(val)
            self.result_var.set(str(res))
            self.expression = str(res)
            self.new_calculation = True
        except:
            self.result_var.set("Error")

    def _on_key_press(self, event):
        """Handle keyboard input"""
        key = event.char
        if key in '0123456789.+-*/^%()':
            self._on_click(key)
        elif key.lower() == 's': self._on_click('sin')
        elif key.lower() == 'c' and key != 'C': self._on_click('cos') # Avoid conflict with Clear? No, C is usually Shift+c. strict check.
        elif key.lower() == 't': self._on_click('tan')
        elif key.lower() == 'l': self._on_click('log')
        elif key.lower() == 'p': self._on_click('π')
        elif key.lower() == 'r': self._on_click('sqrt') # r for root
        
        # Mapping Enter to = is handled by specific bind

