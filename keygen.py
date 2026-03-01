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
    print("=======================================")
    print(" ENTERPRISE LICENSE GENERATOR ")
    print("=======================================")
    
    if len(sys.argv) < 2:
        print("\n[ERROR] Missing Machine ID")
        print("Usage: python keygen.py <CLIENT_MACHINE_ID>")
        print("\nExample:")
        print("python keygen.py ABCDE12345FGHIJ67890")
        sys.exit(1)
        
    client_id = sys.argv[1]
    key = generate_commercial_license(client_id)
    
    print(f"\nTarget Machine ID : {client_id}")
    print("\n--- BEGIN LICENSE KEY ---")
    print(key)
    print("--- END LICENSE KEY ---")
    print("\nInstructions:")
    print("Save the entire key string above into a file named 'license.key'")
    print("and place it in the same directory as the executable on the client machine.")
    print("=======================================\n")
