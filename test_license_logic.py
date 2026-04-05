import os
import sys
from license_manager import EnterpriseProtector
from keygen import generate_commercial_license

def test_license():
    protector = EnterpriseProtector()
    mach_id = protector.get_hardware_uuid()
    print(f"Current Machine ID: {mach_id}")
    
    # Generate a key for this machine
    key = generate_commercial_license(mach_id)
    print("Generated Key for this machine.")
    
    # Save to license.key
    with open("license.key", "w", encoding="utf-8") as f:
        f.write(key)
    
    # Verify
    is_valid, msg = protector.verify_offline_license(key)
    print(f"Verification Result: {is_valid} ({msg})")
    
    if is_valid:
        print("SUCCESS: License logic is working perfectly.")
    else:
        print("FAILURE: License logic failed.")
    
    # Clean up
    if os.path.exists("license.key"):
        os.remove("license.key")

if __name__ == "__main__":
    test_license()
