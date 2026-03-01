"""
Enterprise Licensing and Protection Interface
Provides Node-Locked Hardware verification, Anti-Debugging strings, and Cryptographic licensing
"""

import os
import sys
import hashlib
import subprocess
import base64
import ctypes
import json
import urllib.request
from tkinter import messagebox
import tkinter as tk

class EnterpriseProtector:
    def __init__(self):
        # Master private seed for signature mathematical verifications
        self.secret_seed = "SHREE_GANESHA_SILK_COMMERCIAL_SEED_2026_V1"
        
        # Free remote kill-switch architecture (e.g., GitHub Gist raw URL containing banned JSON ids)
        # For professional distribution, supply a private server URL here
        self.remote_kill_url = None 
        
    def secure_runtime(self):
        """Phase 1: Anti-Debugging and Environment Protection"""
        # Block standard python traceback injection and debugging (PyCharm/VSCode)
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            self._critical_exit("Intrusion Detected: Debugger tracing runtime.")
            
        # Block Windows Native Debuggers (OllyDbg, x64dbg)
        try:
            if ctypes.windll.kernel32.IsDebuggerPresent():
                self._critical_exit("Intrusion Detected: Native Windows debugger active.")
        except Exception:
            pass

    def _critical_exit(self, message):
        """Immediate process termination for critical security violations"""
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Security Violation", message)
        sys.exit(-1)

    def get_hardware_uuid(self):
        """Phase 2: Extract encrypted node-locked hardware signature using Motherboard metrics"""
        try:
            # WMI query for SMBIOS UUID
            cmd = 'wmic csproduct get uuid'
            # CREATE_NO_WINDOW = 0x08000000 flags to hide console flashing
            uuid_raw = subprocess.check_output(cmd, shell=True, creationflags=0x08000000).decode()
            clean_uuid = uuid_raw.split('\n')[1].strip()
            
            # Formulate the deterministic SHA256 hardware identity
            hw_string = f"{clean_uuid}_{self.secret_seed}"
            return hashlib.sha256(hw_string.encode()).hexdigest()[:20].upper()
        except Exception:
            # Fallback if WMI fails
            return "UNKNOWN_FALLBACK_HWID"

    def verify_offline_license(self, license_payload):
        """Phase 3: Cryptographically validate the offline commercial license payload"""
        try:
            decoded = base64.b64decode(license_payload).decode()
            target_hwid, signature = decoded.split("::")
            
            # Validation Step A: Compare Hardware
            current_hwid = self.get_hardware_uuid()
            if target_hwid != current_hwid:
                return False, "This software is licensed to a different machine/hardware."
                
            # Validation Step B: Reconstruct Signature
            expected_sig = hashlib.sha512(f"{target_hwid}|AUTHORIZED|{self.secret_seed}".encode()).hexdigest()[:40]
            if expected_sig != signature:
                return False, "License signature is invalid or tampered (Corruption)."
                
            return True, "Authorized"
        except Exception:
            return False, "License format is invalid or corrupted."

    def enforce_commercial_license(self, ui_parent=None):
        """Boot sequence enforcement. Fails aggressively if unauthorized."""
        # 1. Enforce Memory Protection
        self.secure_runtime()
        
        mach_id = self.get_hardware_uuid()
        
        # 2. Check local license file presence
        license_path = "license.key"
        if not os.path.exists(license_path):
            self._prompt_activation(mach_id, ui_parent)
            
        # 3. Read and verify local license payload
        with open(license_path, "r", encoding="utf-8") as f:
            key = f.read().strip()
            
        is_valid, err_msg = self.verify_offline_license(key)
        
        if not is_valid:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Activation Failed", f"License Verification Failed!\n\nReason: {err_msg}\n\nYour Machine ID is: {mach_id}")
            sys.exit(0)
            
        return True
        
    def _prompt_activation(self, mach_id, ui_parent=None):
        """Render a standalone Activation window if no license file is found."""
        root = tk.Tk() if ui_parent is None else tk.Toplevel(ui_parent)
        if ui_parent is None:
            root.title("Software Activation Required")
            
        root.geometry("500x350")
        root.resizable(False, False)
        
        # Center Window
        root.update_idletasks()
        x = (root.winfo_screenwidth() - 500) // 2
        y = (root.winfo_screenheight() - 350) // 2
        root.geometry(f"+{x}+{y}")
        
        root.configure(bg="#F5F3FF") # config.COLOR_BG_MAIN visually
        
        import tkinter as ttk
        main_frame = tk.Frame(root, bg="#FFFFFF", bd=1, relief="ridge")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="🔒 Commercial License Required", font=("Arial", 16, "bold"), bg="#FFFFFF", fg="#7C3AED").pack(pady=(20, 10))
        
        guidance = ("This software is Node-Locked. You must obtain a valid 'license.key' file "
                   "specifically generated for this machine's Hardware ID to proceed.")
        tk.Label(main_frame, text=guidance, font=("Arial", 10), bg="#FFFFFF", fg="#6B7280", wraplength=400, justify="center").pack(pady=5)
        
        tk.Label(main_frame, text="YOUR MACHINE IDENTIFIER:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#1F2937").pack(pady=(15, 0))
        
        txt_id = tk.Text(main_frame, height=1, width=25, font=("Consolas", 14, "bold"), bg="#F3F4F6", fg="#EF4444", relief="flat")
        txt_id.insert("1.0", mach_id)
        txt_id.configure(state="disabled")
        txt_id.pack(pady=5)
        
        def copy_hwid():
            root.clipboard_clear()
            root.clipboard_append(mach_id)
            messagebox.showinfo("Copied", "Machine ID copied to clipboard!", parent=root)
            
        tk.Button(main_frame, text="Copy ID", command=copy_hwid, bg="#E5E7EB", fg="black", font=("Arial", 9), cursor="hand2").pack(pady=2)
        
        tk.Label(main_frame, text="Please contact Shree Ganesha Silk support with this ID.", font=("Arial", 9), bg="#FFFFFF", fg="#9CA3AF").pack(side="bottom", pady=15)
        
        if ui_parent is None:
            root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
            root.mainloop()
        else:
            root.grab_set()
            sys.exit(0) # Block flow
