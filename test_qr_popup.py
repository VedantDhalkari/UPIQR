import threading
import time
import customtkinter as ctk
from PIL import Image, ImageTk
import io
import qrcode
import tkinter as tk

app = ctk.CTk()
app.geometry("200x200")

def show_popup():
    print("Showing popup")
    d = ctk.CTkToplevel(app)
    d.title(f"UPI Payment")
    d.geometry("460x580")
    
    amount = 100.50
    upi_id = "test@ybl"
    payee_name = "Test Shop"
    bill_number = "123"
    upi_link = f"upi://pay?pa={upi_id}&pn={payee_name.replace(' ', '%20')}&am={amount:.2f}&cu=INR&tn=Bill%20{bill_number}"
    
    try:
        d.update() 
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=2)
        qr.add_data(upi_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#4a0082", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        pil_img = Image.open(buf).resize((220, 220), Image.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=pil_img, size=(220, 220))
        qr_lbl = ctk.CTkLabel(d, image=ctk_img, text="")
        qr_lbl.image = ctk_img  # Keep reference
        qr_lbl.pack(pady=5)
        print("QR generated successfully")
        
        # Close after 2 seconds
        def close_app():
            print("Closing...")
            app.quit()
        app.after(2000, close_app)
        
    except Exception as e:
        print(f"Error: {e}")
        app.quit()

app.after(500, show_popup)
app.mainloop()
print("Done")
