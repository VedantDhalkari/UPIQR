"""
Developer Key Generator Tool
Used exclusively by the software owner to provision clients onto their machines.
"""

import sys
import hashlib
import base64

def generate_commercial_license(client_hwid):
    # This must perfectly match the seed in license_manager.py
    secret_seed = "SHREE_GANESHA_SILK_COMMERCIAL_SEED_2026_V1"
    
    # 1. Sign
    payload = f"{client_hwid}|AUTHORIZED|{secret_seed}"
    signature = hashlib.sha512(payload.encode()).hexdigest()[:40]
    
    # 2. Package
    final_payload = f"{client_hwid}::{signature}"
    license_key = base64.b64encode(final_payload.encode()).decode()
    return license_key

if __name__ == "__main__":
    print("\n" + "="*50)
    print("      🌟 SHREE GANESHA SILK - LICENSE GENERATOR 🌟")
    print("="*50)
    
    import os
    
    if len(sys.argv) > 1:
        client_id = sys.argv[1]
    else:
        print("\n[PROMPT] Please enter the Client Machine ID (from activation screen):")
        client_id = input(" > ").strip()
        
    if not client_id:
        print("\n[ERROR] No Machine ID provided. Exiting.")
        sys.exit(1)
        
    key = generate_commercial_license(client_id)
    
    print("\n" + "-"*50)
    print(f" TARGET MACHINE : {client_id}")
    print("-"*50)
    print("\n🔑 GENERATED LICENSE KEY:\n")
    print(key)
    print("\n" + "-"*50)
    
    # Also save to a file automatically for convenience
    try:
        with open("license.key", "w") as f:
            f.write(key)
        print(f"\n[SUCCESS] 'license.key' has been generated in: {os.getcwd()}")
    except:
        pass
        
    print("\nINSTRUCTIONS FOR CLIENT:")
    print("1. Send the 'license.key' file to the client.")
    print("2. Ask them to place it in the SAME FOLDER as the software.")
    print("3. Restart the software.")
    print("="*50 + "\n")

