import tkinter as tk
from tkinter import messagebox
import pytesseract
from PIL import Image, ImageTk
import pyautogui
import pyperclip

class ScreenOCR:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen OCR Tool")
        self.root.geometry("300x150")
        
        # Variables for selection
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        tk.Label(self.root, text="Screen OCR Tool", font=("Arial", 16)).pack(pady=10)
        
        tk.Button(self.root, text="Capture Screen Area", 
                 command=self.start_capture, 
                 font=("Arial", 12), 
                 bg="#4CAF50", 
                 fg="white", 
                 width=20, 
                 height=2).pack(pady=10)
        
        tk.Label(self.root, text="Click and drag to select area", 
                font=("Arial", 10)).pack()
        
        # Result text area
        self.result_text = tk.Text(self.root, height=8, width=40)
        self.result_text.pack(pady=10)
        
        tk.Button(self.root, text="Copy to Clipboard", 
                 command=self.copy_to_clipboard, 
                 font=("Arial", 10)).pack(pady=5)
    
    def start_capture(self):
        self.root.withdraw()  # Hide main window
        self.create_capture_window()
    
    def create_capture_window(self):
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Create fullscreen window for selection
        self.capture_window = tk.Toplevel()
        self.capture_window.attributes('-fullscreen', True)
        self.capture_window.attributes('-alpha', 0.3)
        self.capture_window.configure(bg='grey')
        self.capture_window.attributes('-topmost', True)
        
        # Convert screenshot to PhotoImage
        self.screenshot_image = ImageTk.PhotoImage(screenshot)
        
        # Create canvas
        self.canvas = tk.Canvas(self.capture_window, 
                              width=screenshot.width, 
                              height=screenshot.height)
        self.canvas.pack()
        
        # Display screenshot
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.screenshot_image)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Bind escape key to cancel
        self.capture_window.bind("<Escape>", self.cancel_capture)
        
        # Instructions
        self.canvas.create_text(screenshot.width//2, 50, 
                              text="Click and drag to select area. Press ESC to cancel.", 
                              fill="red", font=("Arial", 16))
    
    def on_click(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
    def on_drag(self, event):
        # Clear previous rectangle
        self.canvas.delete("selection")
        
        # Draw new rectangle
        if self.start_x and self.start_y:
            self.canvas.create_rectangle(self.start_x, self.start_y, 
                                       event.x, event.y, 
                                       outline="red", width=2, 
                                       tags="selection")
    
    def on_release(self, event):
        self.end_x = event.x
        self.end_y = event.y
        
        # Ensure coordinates are in correct order
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        # Close capture window
        self.capture_window.destroy()
        
        # Perform OCR
        self.perform_ocr(x1, y1, x2, y2)
        
        # Show main window again
        self.root.deiconify()
    
    def cancel_capture(self, event):
        self.capture_window.destroy()
        self.root.deiconify()
    
    def perform_ocr(self, x1, y1, x2, y2):
        try:
            # Take screenshot of selected area
            screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            
            # Perform OCR
            text = pytesseract.image_to_string(screenshot)
            
            # Display result
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, text.strip())
            
            # Also print to console
            print("OCR Result:")
            print(text.strip())
            
        except Exception as e:
            messagebox.showerror("Error", f"OCR failed: {str(e)}")
    
    def copy_to_clipboard(self):
        text = self.result_text.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Success", "Text copied to clipboard!")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import pytesseract
        import pyautogui
        import pyperclip
        from PIL import Image, ImageTk
    except ImportError as e:
        print(f"Missing package: {e}")
        print("Please install required packages:")
        print("pip install pytesseract pillow pyautogui pyperclip")
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
    app = ScreenOCR()
    app.run()