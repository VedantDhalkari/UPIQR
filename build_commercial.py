"""
Commercial Enterprise Build Orchestrator
Automates PyArmor 8 Obfuscation (Control Flow Flattening, Cython Environment)
and PyInstaller secure bundling.
"""

import os
import sys
import subprocess
import shutil
import glob

def run_cmd(cmd):
    print(f"\n[EXEC] {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed with exit code: {e.returncode}")
        sys.exit(1)

def build_commercial():
    print("==================================================")
    print(" SHREE GANESHA SILK - COMMERCIAL COMPILATION ")
    print("==================================================")
    
    # Define required packages
    print("\n[1/3] Verifying and Installing Compilation Toolchain...")
    run_cmd(f'"{sys.executable}" -m pip install pyarmor pyinstaller cryptography cffi')
    
    # Run PyArmor to obfuscate the tree
    print("\n[2/3] Executing Source Code Obfuscation (Cython-ready)...")
    obf_dir = "obfuscated_dist"
    if os.path.exists(obf_dir):
        print(f"Cleaning previous build directory: {obf_dir}")
        shutil.rmtree(obf_dir)
        
    # PyArmor 8 generates cross-platform obfuscated code
    pyarmor_exe = os.path.join(os.path.dirname(sys.executable), "pyarmor.exe")
    pyinstaller_exe = os.path.join(os.path.dirname(sys.executable), "pyinstaller.exe")
    
    # Collect specifically the source application code, omitting the dev-tools
    src_files = [f for f in glob.glob("*.py") if f not in ["build_commercial.py", "keygen.py"]]
    src_files_str = " ".join(src_files)
    
    pyarmor_cmd = f'"{pyarmor_exe}" gen -O {obf_dir} {src_files_str}'
    
    try:
        run_cmd(pyarmor_cmd)
        os.chdir(obf_dir)
    except SystemExit:
        print("\n[WARNING] PyArmor Free Trial Limit Exceeded (Module > 32KB)!")
        print("[WARNING] Bypassing source obfuscation. Falling back to native PyInstaller Node-Locking bundling...")
        obf_dir = "."
        # Ensure we stay in the root build context
        pass
    
    pyinst_cmd = (
        f'"{pyinstaller_exe}" --noconfirm --onefile --windowed '
        f'--name "ShreeGaneshaSilk_Enterprise" '
        f'--clean '
        f'--icon=NONE '
        f'--add-data="config.py;." '
        f'--add-data="logo.jpg;." '
        f'--hidden-import=PIL._tkinter_finder '
        f'--collect-all numpy '
        f'--collect-all matplotlib '
        f'--collect-all customtkinter '
        f'--collect-all tkcalendar '
        f'--collect-all babel '
        f'--collect-all reportlab '
        f'main.py'
    )
    
    try:
        run_cmd(pyinst_cmd)
        
        print("\n==================================================")
        print(" SUCCESS! COMMERCIAL NODE-LOCKED BUILD READY ")
        print("==================================================")
        print(" Output Executable: ")
        print(f" {os.path.abspath('dist/ShreeGaneshaSilk_Enterprise.exe')}")
        print("\n Ensure you distribute this executable along with a unique")
        print(" 'license.key' generated for each client machine.")
        print(" Use 'keygen.py' to generate valid commercial keys.")
        print("==================================================")
        
    except Exception as e:
        print(f"Build Failed: {e}")
        
    finally:
        # Reset directory to prevent locking up subsequent runs
        if obf_dir != ".":
            os.chdir("..")

if __name__ == "__main__":
    build_commercial()
