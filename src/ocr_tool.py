import tkinter as tk
from tkinter import ttk, messagebox, font
import pytesseract
from PIL import Image, ImageTk, ImageDraw, ImageEnhance, ImageFilter
import pyautogui
import pyperclip
import threading
import time
import numpy as np
import requests
import json
import base64
from io import BytesIO

class ModernScreenOCR:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen OCR Tool - Chemistry Edition")
        self.root.geometry("550x700")
        self.root.configure(bg='#1e1e1e')
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # Variables
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.last_screenshot = None
        
        # OCR Engine selection
        self.ocr_engine = tk.StringVar(value="tesseract")
        
        # Configure styles
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()
        
        # Center window
        self.center_window()
        
    def setup_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = '#1e1e1e'
        fg_color = '#ffffff'
        button_bg = '#2d2d2d'
        button_hover = '#3d3d3d'
        accent_color = '#0e7490'
        
        style.configure('Modern.TFrame', background=bg_color)
        style.configure('Modern.TLabel', background=bg_color, foreground=fg_color)
        style.configure('Title.TLabel', background=bg_color, foreground=fg_color, 
                       font=('Segoe UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', background=bg_color, foreground='#888888',
                       font=('Segoe UI', 9))
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title section
        title_frame = tk.Frame(main_frame, bg='#1e1e1e')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(title_frame, text="Chemistry OCR Scanner", 
                font=('Segoe UI', 24, 'bold'), 
                bg='#1e1e1e', fg='#ffffff').pack(anchor='w')
        
        tk.Label(title_frame, text="Capture chemical equations, formulas with charges, and LaTeX notation", 
                font=('Segoe UI', 11), 
                bg='#1e1e1e', fg='#888888').pack(anchor='w', pady=(5, 0))
        
        # OCR Engine Selection
        engine_frame = tk.Frame(main_frame, bg='#1e1e1e')
        engine_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(engine_frame, text="OCR Engine:", 
                font=('Segoe UI', 10, 'bold'), 
                bg='#1e1e1e', fg='#ffffff').pack(side=tk.LEFT, padx=(0, 10))
        
        engines = [
            ("Tesseract (Basic)", "tesseract"),
            ("Enhanced Chemistry", "chemistry"),
            ("MathPix API", "mathpix")
        ]
        
        for text, value in engines:
            rb = tk.Radiobutton(engine_frame, 
                               text=text,
                               variable=self.ocr_engine,
                               value=value,
                               font=('Segoe UI', 9),
                               bg='#1e1e1e',
                               fg='#ffffff',
                               selectcolor='#2d2d2d',
                               activebackground='#1e1e1e',
                               activeforeground='#ffffff',
                               cursor='hand2')
            rb.pack(side=tk.LEFT, padx=(0, 15))
        
        # API Key input for MathPix (initially hidden)
        self.api_frame = tk.Frame(main_frame, bg='#1e1e1e')
        
        tk.Label(self.api_frame, text="MathPix API Key:", 
                font=('Segoe UI', 9), 
                bg='#1e1e1e', fg='#888888').pack(anchor='w')
        
        self.api_key_entry = tk.Entry(self.api_frame,
                                     bg='#2d2d2d',
                                     fg='white',
                                     font=('Segoe UI', 9),
                                     show='*')
        self.api_key_entry.pack(fill=tk.X, pady=(2, 10))
        
        # Snip button (main action)
        snip_frame = tk.Frame(main_frame, bg='#1e1e1e')
        snip_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.snip_button = tk.Button(snip_frame, 
                                     text="📷  Capture Screen", 
                                     command=self.start_capture,
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='#0e7490',
                                     fg='white',
                                     activebackground='#0c5f75',
                                     activeforeground='white',
                                     relief=tk.FLAT,
                                     cursor='hand2',
                                     padx=30,
                                     pady=12)
        self.snip_button.pack(fill=tk.X)
        
        # Add hover effect
        self.snip_button.bind('<Enter>', lambda e: self.snip_button.config(bg='#0c5f75'))
        self.snip_button.bind('<Leave>', lambda e: self.snip_button.config(bg='#0e7490'))
        
        # Shortcut hint
        tk.Label(main_frame, text="Tip: Press ESC to cancel capture", 
                font=('Segoe UI', 9), 
                bg='#1e1e1e', fg='#666666').pack(pady=(0, 15))
        
        # Preview section
        preview_label = tk.Label(main_frame, text="Preview", 
                                font=('Segoe UI', 11, 'bold'), 
                                bg='#1e1e1e', fg='#ffffff')
        preview_label.pack(anchor='w', pady=(10, 5))
        
        # Preview frame
        self.preview_frame = tk.Frame(main_frame, bg='#2d2d2d', height=120)
        self.preview_frame.pack(fill=tk.X, pady=(0, 15))
        self.preview_frame.pack_propagate(False)
        
        self.preview_label = tk.Label(self.preview_frame, 
                                     text="No screenshot captured yet",
                                     bg='#2d2d2d', 
                                     fg='#666666',
                                     font=('Segoe UI', 10))
        self.preview_label.pack(expand=True)
        
        # Result section with tabs
        result_label = tk.Label(main_frame, text="Results", 
                               font=('Segoe UI', 11, 'bold'), 
                               bg='#1e1e1e', fg='#ffffff')
        result_label.pack(anchor='w', pady=(10, 5))
        
        # Tab control for different formats
        self.tab_control = ttk.Notebook(main_frame)
        
        # Text tab
        text_tab = tk.Frame(self.tab_control, bg='#2d2d2d')
        self.tab_control.add(text_tab, text='Text')
        
        self.result_text = tk.Text(text_tab, 
                                  height=8, 
                                  wrap=tk.WORD,
                                  bg='#2d2d2d',
                                  fg='#ffffff',
                                  font=('Consolas', 10),
                                  insertbackground='#ffffff',
                                  selectbackground='#0e7490',
                                  relief=tk.FLAT,
                                  padx=10,
                                  pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # LaTeX tab
        latex_tab = tk.Frame(self.tab_control, bg='#2d2d2d')
        self.tab_control.add(latex_tab, text='LaTeX')
        
        self.latex_text = tk.Text(latex_tab, 
                                 height=8, 
                                 wrap=tk.WORD,
                                 bg='#2d2d2d',
                                 fg='#00ff00',
                                 font=('Consolas', 10),
                                 insertbackground='#00ff00',
                                 selectbackground='#0e7490',
                                 relief=tk.FLAT,
                                 padx=10,
                                 pady=10)
        self.latex_text.pack(fill=tk.BOTH, expand=True)
        
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#1e1e1e')
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Copy button
        self.copy_button = tk.Button(button_frame, 
                                     text="📋 Copy", 
                                     command=self.copy_to_clipboard,
                                     font=('Segoe UI', 10),
                                     bg='#2d2d2d',
                                     fg='white',
                                     activebackground='#3d3d3d',
                                     activeforeground='white',
                                     relief=tk.FLAT,
                                     cursor='hand2',
                                     padx=20,
                                     pady=8)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_button = tk.Button(button_frame, 
                                      text="🗑️ Clear", 
                                      command=self.clear_text,
                                      font=('Segoe UI', 10),
                                      bg='#2d2d2d',
                                      fg='white',
                                      activebackground='#3d3d3d',
                                      activeforeground='white',
                                      relief=tk.FLAT,
                                      cursor='hand2',
                                      padx=20,
                                      pady=8)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Format options
        self.format_var = tk.StringVar(value="unicode")
        formats = [("Unicode", "unicode"), ("LaTeX", "latex")]
        
        tk.Label(button_frame, text="Output:", 
                font=('Segoe UI', 10), 
                bg='#1e1e1e', fg='#888888').pack(side=tk.LEFT, padx=(20, 5))
        
        for text, value in formats:
            rb = tk.Radiobutton(button_frame,
                              text=text,
                              variable=self.format_var,
                              value=value,
                              font=('Segoe UI', 9),
                              bg='#1e1e1e',
                              fg='#ffffff',
                              selectcolor='#2d2d2d',
                              cursor='hand2')
            rb.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add hover effects for buttons
        for btn in [self.copy_button, self.clear_button]:
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#3d3d3d'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#2d2d2d'))
        
        # Status bar
        self.status_label = tk.Label(main_frame, 
                                    text="Ready", 
                                    font=('Segoe UI', 9),
                                    bg='#1e1e1e', 
                                    fg='#666666')
        self.status_label.pack(side=tk.BOTTOM, anchor='w', pady=(10, 0))
        
        # Update API frame visibility
        self.ocr_engine.trace('w', self.on_engine_change)
    
    def on_engine_change(self, *args):
        """Show/hide API key input based on engine selection"""
        if self.ocr_engine.get() == "mathpix":
            self.api_frame.pack(after=self.api_frame.master.winfo_children()[1], fill=tk.X, pady=(0, 15))
        else:
            self.api_frame.pack_forget()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def start_capture(self):
        """Start screen capture"""
        self.status_label.config(text="Capturing screen...")
        self.root.withdraw()
        time.sleep(0.3)
        self.create_capture_window()
    
    def create_capture_window(self):
        """Create fullscreen overlay for selection"""
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Create fullscreen window
        self.capture_window = tk.Toplevel()
        self.capture_window.attributes('-fullscreen', True)
        self.capture_window.attributes('-topmost', True)
        self.capture_window.configure(bg='black')
        
        # Create canvas
        self.canvas = tk.Canvas(self.capture_window, 
                              highlightthickness=0,
                              cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Display screenshot with darkened overlay
        self.screenshot = screenshot
        self.screenshot_image = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.screenshot_image)
        
        # Add dark overlay
        overlay = Image.new('RGBA', screenshot.size, (0, 0, 0, 100))
        self.overlay_image = ImageTk.PhotoImage(overlay)
        self.overlay_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.overlay_image)
        
        # Instructions
        instruction_text = "Click and drag to select chemical equation • Press ESC to cancel"
        self.canvas.create_text(screenshot.width//2, 30, 
                              text=instruction_text, 
                              fill="white", 
                              font=("Segoe UI", 12, "bold"),
                              tags="instruction")
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.capture_window.bind("<Escape>", self.cancel_capture)
        
        self.selection_rect = None
        self.coordinates_text = None
    
    def on_click(self, event):
        """Handle mouse click"""
        self.start_x = event.x
        self.start_y = event.y
        
    def on_drag(self, event):
        """Handle mouse drag"""
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        if self.coordinates_text:
            self.canvas.delete(self.coordinates_text)
        
        if self.start_x and self.start_y:
            # Draw selection rectangle
            self.selection_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline="#0e7490", width=2, fill="#0e7490", stipple="gray50"
            )
            
            # Show dimensions
            width = abs(event.x - self.start_x)
            height = abs(event.y - self.start_y)
            coord_text = f"{width} × {height}"
            
            text_x = min(self.start_x, event.x) + width // 2
            text_y = min(self.start_y, event.y) - 10
            
            if text_y < 20:
                text_y = max(self.start_y, event.y) + 10
            
            self.coordinates_text = self.canvas.create_text(
                text_x, text_y,
                text=coord_text,
                fill="white",
                font=("Segoe UI", 10, "bold"),
                anchor="center"
            )
    
    def on_release(self, event):
        """Handle mouse release"""
        self.end_x = event.x
        self.end_y = event.y
        
        # Ensure coordinates are in correct order
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        # Check if selection is valid
        if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
            # Close capture window
            self.capture_window.destroy()
            
            # Perform OCR in thread
            threading.Thread(target=self.perform_ocr, args=(x1, y1, x2, y2), daemon=True).start()
        
        # Show main window again
        self.root.deiconify()
        self.root.attributes('-topmost', True)
    
    def cancel_capture(self, event):
        """Cancel capture operation"""
        self.capture_window.destroy()
        self.root.deiconify()
        self.root.attributes('-topmost', True)
        self.status_label.config(text="Capture cancelled")
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        gray = image.convert('L')
        
        # Increase size for better recognition
        width, height = gray.size
        gray = gray.resize((width * 3, height * 3), Image.Resampling.LANCZOS)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(2.5)
        
        # Apply sharpening
        gray = gray.filter(ImageFilter.SHARPEN)
        
        # Convert to numpy array for advanced processing
        img_array = np.array(gray)
        
        # Apply threshold
        threshold = 127
        img_array = ((img_array > threshold) * 255).astype(np.uint8)
        
        return Image.fromarray(img_array)
    
    def chemistry_post_process(self, text):
        """Enhanced post-processing for chemistry notation"""
        import re
        
        # Phase 1: Fix common OCR mistakes
        replacements = {
            # Arrows
            '—>': '→', '-->': '→', '->': '→', '=>': '→',
            '—»': '→', '-»': '→', '>>': '→',
            '<->': '↔', '<=>': '⇌', '<==>': '⇌', '==': '⇌',
            
            # Mathematical symbols
            '+-': '±', '+/-': '±',
            'delta': 'Δ', 'Delta': 'Δ',
            'alpha': 'α', 'beta': 'β', 'gamma': 'γ',
            
            # Fix common letter confusion
            'S04': 'SO₄', 'H20': 'H₂O', 'C02': 'CO₂',
            'NH3': 'NH₃', 'CH4': 'CH₄', 'H2S04': 'H₂SO₄',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Phase 2: Handle subscripts and superscripts
        
        # Convert subscript patterns (e.g., H2 -> H₂)
        subscript_map = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
        
        # Find chemical formulas and fix subscripts
        def fix_subscripts(match):
            formula = match.group(0)
            # Replace numbers after letters with subscripts
            result = re.sub(r'([A-Z][a-z]?)(\d+)', 
                          lambda m: m.group(1) + m.group(2).translate(subscript_map), 
                          formula)
            return result
        
        # Apply to common patterns
        text = re.sub(r'\b[A-Z][a-z]?\d*(?:\([a-z]+\))?(?:[A-Z][a-z]?\d*)*\b', 
                     fix_subscripts, text)
        
        # Handle superscripts for charges
        superscript_map = str.maketrans('0123456789+-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻')
        
        # Fix ion charges (e.g., Na+ -> Na⁺, SO4 2- -> SO₄²⁻)
        text = re.sub(r'(\w+)\s*(\d*)\s*([+-])', 
                     lambda m: m.group(1) + m.group(2).translate(superscript_map) + m.group(3).translate(superscript_map),
                     text)
        
        # Fix charges at the beginning (e.g., 2+ -> ²⁺)
        text = re.sub(r'\b(\d+)([+-])', 
                     lambda m: m.group(1).translate(superscript_map) + m.group(2).translate(superscript_map),
                     text)
        
        # Phase 3: Clean up spacing
        text = re.sub(r'\s*([\+→⇌↔])\s*', r' \1 ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def perform_ocr(self, x1, y1, x2, y2):
        """Perform OCR on selected region"""
        try:
            self.root.after(0, lambda: self.status_label.config(text="Processing..."))
            
            # Take screenshot of selected area
            screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            self.last_screenshot = screenshot
            
            # Update preview
            self.update_preview(screenshot)
            
            engine = self.ocr_engine.get()
            
            if engine == "tesseract":
                # Basic Tesseract OCR with preprocessing
                processed_image = self.preprocess_image(screenshot)
                text = pytesseract.image_to_string(processed_image)
                text = self.chemistry_post_process(text)
                latex = self.text_to_latex(text)
                
            elif engine == "chemistry":
                # Enhanced chemistry processing
                processed_image = self.preprocess_image(screenshot)
                
                # Use Tesseract with custom config
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(processed_image, config=custom_config)
                
                # Apply aggressive chemistry post-processing
                text = self.chemistry_post_process(text)
                latex = self.text_to_latex(text)
                
            elif engine == "mathpix":
                # Use MathPix API
                api_key = self.api_key_entry.get()
                if not api_key:
                    raise Exception("Please enter your MathPix API key")
                
                text, latex = self.call_mathpix_api(screenshot, api_key)
            
            else:
                text = "Unknown OCR engine"
                latex = ""
            
            # Update results
            self.root.after(0, lambda: self.update_results(text, latex))
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"OCR failed: {str(e)}"))
    
    def text_to_latex(self, text):
        """Convert text to LaTeX format"""
        import re
        
        # Basic LaTeX conversion
        latex = text
        
        # Convert arrows
        latex = latex.replace('→', r'\rightarrow')
        latex = latex.replace('←', r'\leftarrow')
        latex = latex.replace('↔', r'\leftrightarrow')
        latex = latex.replace('⇌', r'\rightleftharpoons')
        
        # Convert subscripts
        latex = re.sub(r'([A-Z][a-z]?)([₀-₉]+)', 
                      lambda m: m.group(1) + '_{' + m.group(2).translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')) + '}',
                      latex)
        
        # Convert superscripts
        latex = re.sub(r'([A-Z][a-z]?\d*)([⁰-⁹⁺⁻]+)', 
                      lambda m: m.group(1) + '^{' + m.group(2).translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻', '0123456789+-')) + '}',
                      latex)
        
        # Wrap in math mode if not already
        if not latex.startswith('$'):
            latex = '$' + latex + '$'
        
        return latex
    
    def call_mathpix_api(self, image, api_key):
        """Call MathPix API for OCR"""
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Prepare request
        url = "https://api.mathpix.com/v3/text"
        headers = {
            "app_id": "your_app_id",  # Replace with your app_id
            "app_key": api_key,
            "Content-type": "application/json"
        }
        
        data = {
            "src": f"data:image/png;base64,{img_base64}",
            "formats": ["text", "latex_styled"],
            "ocr": ["math", "text", "chemistry"]
        }
        
        # Make request
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('text', '')
            latex = result.get('latex_styled', '')
            return text, latex
        else:
            raise Exception(f"MathPix API error: {response.status_code}")
    
    def update_preview(self, image):
        """Update preview image"""
        # Resize image to fit preview
        preview_width = 510
        preview_height = 100
        
        # Calculate aspect ratio
        aspect = image.width / image.height
        
        if aspect > preview_width / preview_height:
            new_width = preview_width
            new_height = int(preview_width / aspect)
        else:
            new_height = preview_height
            new_width = int(preview_height * aspect)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        
        # Update preview
        self.preview_label.config(image=photo, text="")
        self.preview_label.image = photo
    
    def update_results(self, text, latex):
        """Update result text areas"""
        # Update text tab
        self.result_text.delete(1.0, tk.END)
        if text:
            self.result_text.insert(1.0, text)
            self.status_label.config(text=f"Extracted {len(text)} characters")
        else:
            self.result_text.insert(1.0, "No text detected")
            self.status_label.config(text="No text found")
        
        # Update LaTeX tab
        self.latex_text.delete(1.0, tk.END)
        if latex:
            self.latex_text.insert(1.0, latex)
    
    def copy_to_clipboard(self):
        """Copy text to clipboard based on selected format"""
        if self.format_var.get() == "latex":
            text = self.latex_text.get(1.0, tk.END).strip()
        else:
            text = self.result_text.get(1.0, tk.END).strip()
        
        if text and text != "No text detected":
            pyperclip.copy(text)
            self.status_label.config(text="Copied to clipboard!")
            self.root.after(2000, lambda: self.status_label.config(text="Ready"))
        else:
            self.status_label.config(text="No text to copy")
    
    def clear_text(self):
        """Clear all text and preview"""
        self.result_text.delete(1.0, tk.END)
        self.latex_text.delete(1.0, tk.END)
        self.preview_label.config(image="", text="No screenshot captured yet")
        self.status_label.config(text="Cleared")
    
    def show_error(self, message):
        """Show error message"""
        self.status_label.config(text=f"Error: {message}")
        messagebox.showerror("Error", message)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import pytesseract
        import pyautogui
        import pyperclip
        from PIL import Image, ImageTk
        import numpy
    except ImportError as e:
        print(f"Missing package: {e}")
        print("Please install required packages:")
        print("pip install pytesseract pillow pyautogui pyperclip numpy requests")
        exit(1)
    
    # Set Tesseract path for Windows (uncomment and modify if needed)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Check if Tesseract is installed
    try:
        pytesseract.get_tesseract_version()
    except:
        print("Tesseract not found!")
        print("Please install Tesseract OCR:")
        print("Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("Mac: brew install tesseract")
        print("Linux: sudo apt-get install tesseract-ocr")
        print("\nIf installed, uncomment and set the path in the script:")
        print("pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        exit(1)
    
    # Create and run the OCR tool
    app = ModernScreenOCR()
    app.run()