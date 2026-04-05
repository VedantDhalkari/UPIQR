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
            # Important: _prompt_activation will sys.exit(0) if not activated
            
        # 3. Read and verify local license payload
        try:
            with open(license_path, "r", encoding="utf-8") as f:
                key = f.read().strip()
                
            is_valid, err_msg = self.verify_offline_license(key)
        except Exception as e:
            is_valid, err_msg = False, f"File Error: {str(e)}"
        
        if not is_valid:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Activation Failed", f"License Verification Failed!\n\nReason: {err_msg}\n\nYour Machine ID is: {mach_id}")
            # If the license is invalid, show the activation prompt again to allow the user to fix it
            self._prompt_activation(mach_id, ui_parent)
            sys.exit(0)
            
        return True
        
    def _prompt_activation(self, mach_id, ui_parent=None):
        """Render a standalone Activation window if no license file is found."""
        root = tk.Tk() if ui_parent is None else tk.Toplevel(ui_parent)
        root.title("Software Activation Required")
        root.geometry("550x450")
        root.resizable(False, False)
        
        # Bring to front
        root.attributes('-topmost', True)
        
        # Center Window
        root.update_idletasks()
        x = (root.winfo_screenwidth() - 550) // 2
        y = (root.winfo_screenheight() - 450) // 2
        root.geometry(f"+{x}+{y}")
        
        root.configure(bg="#F8FAFC") 
        
        main_frame = tk.Frame(root, bg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#E2E8F0")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title with Icon
        tk.Label(main_frame, text="🔒", font=("Segoe UI Emoji", 48), bg="#FFFFFF").pack(pady=(20, 10))
        tk.Label(main_frame, text="Commercial Activation Required", font=("Arial", 18, "bold"), bg="#FFFFFF", fg="#1E293B").pack(pady=(0, 10))
        
        guidance = ("This software is locked to this specific hardware. To activate, please send the "
                   "Machine ID below to the software provider to receive your 'license.key'.")
        tk.Label(main_frame, text=guidance, font=("Arial", 10), bg="#FFFFFF", fg="#64748B", wraplength=450, justify="center").pack(pady=5)
        
        # ID Box
        id_frame = tk.Frame(main_frame, bg="#F1F5F9", padx=15, pady=15)
        id_frame.pack(pady=20, fill="x", padx=40)
        
        tk.Label(id_frame, text="YOUR MACHINE IDENTIFIER:", font=("Arial", 9, "bold"), bg="#F1F5F9", fg="#475569").pack(anchor="w")
        
        txt_id = tk.Entry(id_frame, font=("Consolas", 14, "bold"), bg="#F1F5F9", fg="#EF4444", relief="flat", justify="center")
        txt_id.insert(0, mach_id)
        txt_id.configure(state="readonly")
        txt_id.pack(pady=10, fill="x")
        
        def copy_hwid():
            root.clipboard_clear()
            root.clipboard_append(mach_id)
            btn_copy.config(text="✓ Copied!", fg="#10B981")
            root.after(2000, lambda: btn_copy.config(text="📋 Copy Machine ID", fg="#3B82F6"))
            
        btn_copy = tk.Button(id_frame, text="📋 Copy Machine ID", command=copy_hwid, bg="#F1F5F9", fg="#3B82F6", 
                           font=("Arial", 10, "bold"), relief="flat", cursor="hand2", activebackground="#F1F5F9")
        btn_copy.pack(pady=2)
        
        # Footer
        footer_text = "Once you have the 'license.key' file, place it in the same\nfolder as this software and restart the application."
        tk.Label(main_frame, text=footer_text, font=("Arial", 9, "italic"), bg="#FFFFFF", fg="#94A3B8").pack(pady=20)
        
        if ui_parent is None:
            root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
            root.mainloop()
        else:
            root.grab_set()
            root.wait_window()
            sys.exit(0)

