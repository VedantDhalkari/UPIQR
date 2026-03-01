
import customtkinter as ctk
import config
from search import GlobalSearchModule
from unittest.mock import MagicMock

# Mock DB Manager
class MockDB:
    def execute_query(self, query, params=()):
        return []

def test_card_creation():
    app = ctk.CTk()
    
    # Setup
    db = MockDB()
    search_module = GlobalSearchModule(app, db)
    search_module.pack(fill="both", expand=True)
    
    # Test Data (bill_no, name, phone, amount, date)
    sample_bill = ("BILL-001", "John Doe", "9876543210", 1500.50, "2023-10-25 14:30:00")
    
    print("Testing _create_bill_card...")
    try:
        search_module._create_bill_card(sample_bill)
        print("Success: Bill card created without error.")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

    # app.mainloop() # Don't run mainloop to exit after test
    app.destroy()

if __name__ == "__main__":
    test_card_creation()
