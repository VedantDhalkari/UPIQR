"""
Sample Data Generator for Shree Ganesha SilkManagement System
Run this script to populate the database with sample data for testing
"""

import sqlite3
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample inventory and sales data"""
    
    conn = sqlite3.connect('boutique_database.db')
    cursor = conn.cursor()
    
    print("🎨 Generating Sample Data for Shree Ganesha SilkManagement System")
    print("="*60)
    
    # Sample inventory data
    saree_types = ['Silk', 'Cotton', 'Georgette', 'Chiffon', 'Banarasi', 'Kanjivaram', 'Chanderi', 'Tussar']
    materials = ['Pure Silk', 'Cotton Blend', 'Georgette', 'Chiffon', 'Art Silk', 'Handloom']
    colors = ['Red', 'Blue', 'Green', 'Yellow', 'Pink', 'Purple', 'Orange', 'Maroon', 'Navy', 'Gold', 
              'Silver', 'White', 'Black', 'Cream', 'Peach', 'Turquoise']
    designs = ['Floral', 'Geometric', 'Traditional', 'Contemporary', 'Paisley', 'Abstract', 'Temple Border', 
               'Zari Work']
    suppliers = ['Surat Textiles', 'Bangalore Silk House', 'Chennai Sarees', 'Mumbai Fashion', 'Delhi Fabrics']
    categories = ['Bridal', 'Party Wear', 'Casual', 'Office Wear', 'Festival Special', 'Designer']
    
    # Generate 50 sample inventory items
    print("\n📦 Adding Sample Inventory Items...")
    inventory_count = 0
    
    for i in range(1, 51):
        try:
            sku = f"SAR{i:03d}"
            saree_type = random.choice(saree_types)
            material = random.choice(materials)
            color = random.choice(colors)
            design = random.choice(designs)
            quantity = random.randint(1, 20)
            purchase_price = random.randint(500, 3000)
            selling_price = purchase_price + random.randint(500, 2000)
            supplier = random.choice(suppliers)
            category = random.choice(categories)
            
            cursor.execute("""
                INSERT INTO inventory (sku_code, saree_type, material, color, design, 
                                     quantity, purchase_price, selling_price, supplier_name, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sku, saree_type, material, color, design, quantity, 
                  purchase_price, selling_price, supplier, category))
            
            inventory_count += 1
            
            if inventory_count % 10 == 0:
                print(f"  ✓ Added {inventory_count} items...")
                
        except sqlite3.IntegrityError:
            # SKU already exists, skip
            pass
    
    print(f"  ✅ Total Inventory Items Added: {inventory_count}")
    
    # Generate some sample sales (last 30 days)
    print("\n💰 Generating Sample Sales Data...")
    sales_count = 0
    
    customer_names = [
        'Priya Sharma', 'Anita Desai', 'Kavita Patel', 'Sneha Reddy', 'Divya Kumar',
        'Riya Singh', 'Meera Iyer', 'Pooja Gupta', 'Sanya Mehta', 'Anjali Verma',
        None, None, None  # Walk-in customers
    ]
    
    # Get all inventory items for sales
    cursor.execute("SELECT item_id, sku_code, saree_type, material, color, selling_price FROM inventory")
    inventory_items = cursor.fetchall()
    
    if not inventory_items:
        print("  ⚠️  No inventory items found. Please add inventory first.")
        conn.commit()
        conn.close()
        return
    
    for day in range(30):
        # Generate 1-5 sales per day
        num_sales = random.randint(1, 5)
        
        for sale_num in range(num_sales):
            sale_date = datetime.now() - timedelta(days=30-day, hours=random.randint(9, 20))
            
            # Random customer
            customer_name = random.choice(customer_names)
            customer_phone = f"+91 {random.randint(7000000000, 9999999999)}" if customer_name else None
            
            # Random 1-3 items per sale
            num_items = random.randint(1, 3)
            selected_items = random.sample(inventory_items, min(num_items, len(inventory_items)))
            
            total_amount = 0
            items_data = []
            
            for item in selected_items:
                quantity = random.randint(1, 2)
                price = item[5]
                item_total = quantity * price
                total_amount += item_total
                items_data.append((item[0], item[1], f"{item[2]} - {item[3]} ({item[4]})", 
                                 quantity, price, item_total))
            
            # Random discount
            discount_percent = random.choice([0, 0, 0, 5, 10])  # Most sales have no discount
            discount_amount = total_amount * (discount_percent / 100)
            after_discount = total_amount - discount_amount
            gst_amount = after_discount * 0.05  # 5% GST
            final_amount = after_discount + gst_amount
            
            # Generate bill number
            timestamp = sale_date.strftime("%Y%m%d%H%M%S")
            bill_number = f"ESB{timestamp}{random.randint(10,99)}"
            
            try:
                # Insert sale
                cursor.execute("""
                    INSERT INTO sales (bill_number, customer_name, customer_phone,
                                     total_amount, discount_percent, discount_amount,
                                     gst_amount, final_amount, payment_method, sale_date, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (bill_number, customer_name, customer_phone, total_amount,
                      discount_percent, discount_amount, gst_amount, final_amount,
                      'Cash', sale_date, 'admin'))
                
                sale_id = cursor.lastrowid
                
                # Insert sale items
                for item_data in items_data:
                    cursor.execute("""
                        INSERT INTO sale_items (sale_id, item_id, sku_code, item_name,
                                              quantity, unit_price, total_price)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (sale_id, *item_data))
                
                sales_count += 1
                
            except sqlite3.IntegrityError:
                # Bill number collision, skip
                pass
    
    print(f"  ✅ Total Sales Records Added: {sales_count}")
    
    # Commit all changes
    conn.commit()
    
    # Display summary
    print("\n" + "="*60)
    print("📊 SAMPLE DATA GENERATION COMPLETE!")
    print("="*60)
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM inventory")
    total_items = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sales")
    total_sales = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(final_amount) FROM sales")
    total_revenue = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE quantity <= 5")
    low_stock = cursor.fetchone()[0]
    
    print(f"\n📦 Inventory Items: {total_items}")
    print(f"💰 Sales Transactions: {total_sales}")
    print(f"💵 Total Revenue: ₹{total_revenue:,.2f}")
    print(f"⚠️  Low Stock Items: {low_stock}")
    
    print("\n✨ Your database is now populated with sample data!")
    print("🚀 You can now test all features of the application.")
    print("\nDefault Login Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("  Admin PIN: 1234")
    
    conn.close()

if __name__ == "__main__":
    try:
        generate_sample_data()
    except Exception as e:
        print(f"\n❌ Error generating sample data: {str(e)}")
        print("Make sure the database exists. Run the main application once to create it.")
