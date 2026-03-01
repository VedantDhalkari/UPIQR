# Shree Ganesha Silk - User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Login & Authentication](#login-authentication)
3. [Dashboard Overview](#dashboard-overview)
4. [Creating New Bills](#creating-new-bills)
5. [Stock Management](#stock-management)
6. [Adding New Stock](#adding-new-stock)
7. [Global Search](#global-search)
8. [Reports & Analytics](#reports-analytics)
9. [Settings Configuration](#settings-configuration)
10. [Common Workflows](#common-workflows)
11. [Tips & Tricks](#tips-tricks)

---

## Getting Started

### Launching the Application

**Method 1: Running from Python**
```
python boutique_management_system.py
```

**Method 2: Using the .exe**
- Double-click `BoutiqueManagement.exe`
- Application will open in full screen

### First Launch
When you first launch the application:
1. The database will be automatically created
2. Default admin user will be set up
3. Default settings will be initialized
4. You'll see the login screen

---

## Login & Authentication

### Login Screen

The login screen features:
- Shop name prominently displayed
- Username field
- Password field (masked)
- Login button

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

### Login Process
1. Enter your username
2. Enter your password
3. Click "Login" or press Enter
4. On successful login, you'll be taken to the Dashboard

### Security Features
- Passwords are encrypted (SHA-256)
- Invalid login attempts are rejected
- No password hints for security

⚠️ **Important**: Change the default password immediately!

---

## Dashboard Overview

### Main Layout

The dashboard consists of:

#### Left Sidebar (Navigation)
- Shop Name & Logo
- Welcome message with username
- Navigation buttons:
  - 🏠 Dashboard
  - 🛒 New Bill
  - 📦 Stock Management (Admin PIN required)
  - ➕ New Stock Entry (Admin PIN required)
  - 🔍 Global Search
  - 📊 Reports
  - ⚙️ Settings
  - 🚪 Logout

#### Main Content Area

**Metric Cards:**
1. **Today's Sales**
   - Total sales amount today
   - Number of bills generated

2. **Inventory Value**
   - Total value of all stock
   - Number of items in inventory

3. **Low Stock Alert**
   - Number of items below threshold
   - Color-coded (Green = OK, Red = Action needed)

**Recent Transactions Table:**
- Shows last 10 sales
- Displays: Bill Number, Customer Name, Amount, Date
- Automatically refreshes

---

## Creating New Bills

### Billing Interface Layout

**Left Panel: Item Selection**
- Search bar for finding items
- Item cards showing available products

**Right Panel: Cart & Checkout**
- Cart items list
- Customer information form
- Discount field
- Payment summary
- Complete Sale button

### Step-by-Step Billing Process

#### Step 1: Search for Items
1. Click on "New Bill" from the sidebar
2. In the search bar, type:
   - SKU code (e.g., SAR001)
   - Saree type (e.g., Silk)
   - Color (e.g., Red)
   - Material (e.g., Cotton)
3. Results appear automatically as you type
4. Minimum 2 characters required

#### Step 2: Add Items to Cart
1. Click "Add to Cart" on any item
2. Item appears in the right panel cart
3. Default quantity: 1

#### Step 3: Adjust Quantities
- Click `-` to decrease quantity
- Click `+` to increase quantity
- Click `✕` to remove item from cart
- Cannot exceed available stock

#### Step 4: Enter Customer Details (Optional)
- **Customer Name**: Enter customer's name
- **Phone**: Enter 10-digit mobile number
- Both fields are optional (for walk-in customers)

#### Step 5: Apply Discount
1. Enter discount percentage in the "Discount %" field
2. Summary updates automatically
3. Shows: Subtotal, Discount amount, GST, Total

#### Step 6: Review Summary
The summary shows:
- **Subtotal**: Total before discount and GST
- **Discount (X%)**: Amount deducted
- **GST (5%)**: Tax amount
- **Total**: Final amount to be paid

#### Step 7: Complete Sale
1. Click "Complete Sale & Generate Invoice"
2. System will:
   - Deduct items from inventory
   - Save transaction to database
   - Generate PDF invoice
   - Show confirmation message
3. Invoice saved in `invoices/` folder
4. Option to open invoice immediately

### Understanding the Invoice

**Invoice Components:**
- **Header**: Shop name, address, contact details, GST number
- **Bill Information**: Bill number, date
- **Customer Information**: Name and phone (if provided)
- **Items Table**: SKU, description, quantity, rate, amount
- **Summary**: Subtotal, discount, GST, grand total
- **Footer**: Thank you message, terms & conditions

**Bill Number Format:** `ESB20240115143022`
- ESB = Bill Prefix (configurable)
- YYYYMMDDHHmmss = Timestamp

### Cart Management Tips

**Adding Same Item Twice:**
- Automatically increases quantity
- Doesn't create duplicate entries

**Removing Items:**
- Click the ✕ button
- No confirmation required
- Can be re-added anytime

**Maximum Quantity:**
- Limited to available stock
- System prevents over-selling
- Warning shown if limit reached

---

## Stock Management

### Accessing Stock Management

1. Click "Stock Management" from sidebar
2. **Admin PIN Required**: Enter `1234` (default)
3. Stock table appears

### Stock Table View

**Columns Displayed:**
- SKU Code
- Saree Type
- Material
- Color
- Quantity (current stock)
- Purchase Price
- Selling Price
- Supplier Name
- Actions (Edit/Delete buttons)

### Features

**Low Stock Highlighting:**
- Items with quantity ≤ 5 appear in red
- Red border for quick identification
- Helps prioritize restocking

**Search & Filter:**
- Type in search box to filter items
- Searches: SKU, Type, Material, Color
- Real-time filtering

**Refresh Button:**
- Reloads entire stock list
- Useful after making changes

### Editing Stock Items

#### Edit Process:
1. Click "Edit" button on any item
2. Edit dialog appears
3. Modify any field:
   - SKU Code
   - Saree Type
   - Material
   - Color
   - Design
   - Quantity
   - Purchase Price
   - Selling Price
   - Supplier Name
   - Category
4. Click "Save Changes"
5. Table updates automatically

**Important Notes:**
- Cannot change SKU to one that already exists
- All prices must be positive numbers
- Quantity must be a whole number

### Deleting Stock Items

#### Delete Process:
1. Click "Delete" button on item
2. Confirmation dialog appears
3. Click "Yes" to confirm
4. Item permanently removed

⚠️ **Warning**: Deletion is permanent and cannot be undone!

**When to Delete:**
- Discontinued items
- Incorrect entries
- Duplicate records

**When NOT to Delete:**
- Items temporarily out of stock (set quantity to 0 instead)
- Items with sales history

---

## Adding New Stock

### Accessing New Stock Entry

1. Click "New Stock Entry" from sidebar
2. **Admin PIN Required**: Enter PIN
3. Stock entry form appears

### Stock Entry Form Fields

#### Required Fields (marked with *)
1. **SKU Code***: Unique identifier (e.g., SAR001)
2. **Saree Type***: Category (e.g., Silk, Cotton, Georgette)
3. **Material***: Fabric type
4. **Color***: Primary color
5. **Quantity***: Number of items
6. **Purchase Price***: Cost price per item
7. **Selling Price***: Retail price per item

#### Optional Fields
1. **Design**: Pattern or design name
2. **Supplier Name**: Vendor/wholesaler name
3. **Category**: Additional classification

### Adding New Stock Step-by-Step

#### Step 1: Fill Required Fields
1. Enter unique SKU code
2. Enter saree type
3. Enter material
4. Enter color
5. Enter quantity (whole number)
6. Enter purchase price (numbers only)
7. Enter selling price

#### Step 2: Fill Optional Fields
- Add design details if applicable
- Enter supplier name for record keeping
- Specify category for better organization

#### Step 3: Save Stock
1. Click "Save Stock" button
2. System validates all entries
3. If successful:
   - Confirmation message shown
   - Form automatically cleared
   - Ready for next entry
4. If error:
   - Error message displayed
   - Fix issue and try again

### Input Validation

**SKU Code:**
- Must be unique
- Cannot be empty
- Error if duplicate found

**Quantity:**
- Must be a whole number
- Cannot be negative
- No decimals allowed

**Prices:**
- Must be valid numbers
- Can have decimals (e.g., 1299.99)
- Must be positive

### Common Errors & Solutions

**Error: "SKU Code already exists"**
- **Cause**: SKU is already in database
- **Solution**: Use a different SKU code

**Error: "Please enter valid numbers"**
- **Cause**: Non-numeric value in price/quantity field
- **Solution**: Enter numbers only, no text

**Error: "X is required"**
- **Cause**: Required field left empty
- **Solution**: Fill in all fields marked with *

### Batch Entry Tips

1. **Prepare data beforehand**: Create a list/spreadsheet
2. **Use consistent naming**: Establish SKU patterns
3. **Clear form after each entry**: Click "Clear Form" button
4. **Verify before saving**: Double-check prices
5. **Keep supplier list**: Maintain consistent supplier names

---

## Global Search

### Overview
Global Search allows you to find:
- Bills by number, customer name, or phone
- Inventory items by any attribute
- Transactions across entire database

### Using Global Search

#### Step 1: Access Search
1. Click "Global Search" from sidebar
2. Search interface appears

#### Step 2: Enter Search Query
1. Type in the search box
2. Minimum 2 characters recommended
3. Can search for:
   - Bill numbers
   - Customer names
   - Phone numbers
   - SKU codes
   - Item names
   - Colors
   - Materials

#### Step 3: Click Search
1. Click "Search" button or press Enter
2. Results appear in two sections:
   - Bills/Invoices
   - Inventory Items

#### Step 4: Review Results
**Bills Section:**
- Shows up to 10 matching bills
- Displays: Bill number, customer, amount, date
- Most recent results first

**Inventory Section:**
- Shows up to 10 matching items
- Displays: SKU, type, material, color, stock, price

### Search Examples

**Finding a Customer's Bill:**
```
Search: "Priya" or "9876543210"
→ Shows all bills for customer Priya
```

**Finding an Item:**
```
Search: "Red Silk"
→ Shows all red silk sarees
```

**Finding by SKU:**
```
Search: "SAR001"
→ Shows item with SKU SAR001
```

**Finding Bills by Date:**
```
Note: Use Reports for date-based searches
Global Search is for specific terms
```

### Search Tips

✅ **Do:**
- Use specific terms
- Try partial matches (e.g., "SAR" finds all SAR* SKUs)
- Search phone numbers for customer lookup
- Use color or type for item discovery

❌ **Don't:**
- Use too many filters at once
- Expect exact date range searches
- Use special characters

---

## Reports & Analytics

### Accessing Reports
1. Click "Reports" from sidebar
2. Reports dashboard appears

### Available Reports

#### 1. Today's Sales Report

**Shows:**
- Total number of bills today
- Gross amount (before discount)
- Total discount given
- GST collected
- Net sales (final amount)

**Use Cases:**
- End-of-day reconciliation
- Daily performance tracking
- Cash register verification

#### 2. This Month's Report

**Shows:**
- Total bills this month
- Total sales amount
- Average bill value

**Use Cases:**
- Monthly performance review
- Trend analysis
- Target tracking

#### 3. Low Stock Items Report

**Shows:**
- All items with quantity ≤ threshold (default: 5)
- Sorted by lowest quantity first
- Limited to 10 items for quick view

**Color Coding:**
- Red text = Low stock items
- Green message = All items well stocked

**Use Cases:**
- Reorder planning
- Inventory management
- Preventing stock-outs

### Understanding the Metrics

**Average Bill Value:**
```
Formula: Total Sales / Number of Bills
Example: ₹50,000 / 20 bills = ₹2,500 average
```

**Net Sales:**
```
Formula: Gross Sales - Discounts + GST
```

**GST Collected:**
```
Formula: (Amount after discount) × GST Rate
Current GST Rate: 5%
```

### Using Reports Effectively

**Daily Routine:**
1. Morning: Check yesterday's sales
2. Evening: Review today's performance
3. Check low stock alerts
4. Plan next day's activities

**Weekly Review:**
1. Compare week-over-week performance
2. Analyze discount patterns
3. Review inventory levels
4. Update supplier orders

**Monthly Analysis:**
1. Calculate monthly growth
2. Identify best-selling items
3. Review profit margins
4. Plan promotional activities

---

## Settings Configuration

### Accessing Settings
1. Click "Settings" from sidebar
2. Settings form appears

### Configurable Settings

#### Shop Details

**Shop Name:**
- Appears on dashboard
- Printed on invoices
- Default: "Shree Ganesha Silk"

**Address:**
- Complete shop address
- Appears on invoices
- Example: "123 Fashion Street, City - 400001"

**Phone:**
- Contact number
- Format: +91 XXXXXXXXXX
- Appears on invoices

**Email:**
- Shop email address
- For customer communications
- Appears on invoices

**GST Number:**
- Your GST registration number
- Format: 22AAAAA0000A1Z5
- Mandatory on invoices

**Bill Prefix:**
- Customizes bill number prefix
- Default: "ESB"
- Example bill: ESB20240115143022

### Saving Settings

1. Modify any field
2. Click "Save Settings"
3. Confirmation message appears
4. Changes take effect immediately

**Important:**
- Invoice changes apply to new bills only
- Existing invoices remain unchanged
- No need to restart application

### Settings Best Practices

✅ **Recommendations:**
- Use accurate GST number
- Keep contact details updated
- Use short, memorable bill prefix (3-4 characters)
- Verify address spelling

❌ **Avoid:**
- Special characters in bill prefix
- Very long shop names (affects invoice formatting)
- Temporary phone numbers

---

## Common Workflows

### Workflow 1: Morning Opening Routine

1. **Login** to application
2. **Check Dashboard**:
   - Review yesterday's sales
   - Check low stock alerts
3. **Review Reports**:
   - Today's starting point
   - Pending reorders
4. **Prepare for Day**:
   - Keep invoice folder accessible
   - Ensure printer is ready

### Workflow 2: Processing a Sale

1. **New Bill** → Click from sidebar
2. **Search Item** → Enter SKU or name
3. **Add to Cart** → Click for each item
4. **Adjust Quantity** → Use +/- buttons
5. **Enter Customer** → Name & phone (optional)
6. **Apply Discount** → If applicable
7. **Review Total** → Verify amount
8. **Complete Sale** → Generate invoice
9. **Print** → If customer requests

### Workflow 3: Receiving New Stock

1. **Verify Stock** → Check invoice from supplier
2. **Access New Stock Entry** → Enter Admin PIN
3. **Add Items** → One by one:
   - Generate unique SKU
   - Enter all details
   - Verify prices
4. **Save Each Item** → Click Save Stock
5. **Verify** → Check in Stock Management
6. **Update Records** → Note supplier details

### Workflow 4: End of Day Closure

1. **Generate Report** → Check Today's Sales
2. **Count Cash** → Match with report
3. **Review Transactions** → Check all bills
4. **Backup** → Copy database file
5. **Check Low Stock** → Plan tomorrow's orders
6. **Logout** → Secure application

### Workflow 5: Weekly Stock Audit

1. **Stock Management** → Open section
2. **Review All Items** → Check quantities
3. **Physical Count** → Match with system
4. **Update Discrepancies** → Edit as needed
5. **Check Low Stock** → Place orders
6. **Update Prices** → If changed

### Workflow 6: Monthly Reporting

1. **Reports Section** → Open
2. **Month's Summary** → Note total sales
3. **Low Stock Items** → Plan major restock
4. **Database Backup** → Create monthly backup
5. **Review Settings** → Update if needed
6. **Clean Up** → Archive old invoices (optional)

---

## Tips & Tricks

### General Tips

**1. Keyboard Shortcuts:**
- Press `Enter` in any field to move to next
- `Tab` to navigate between fields
- `Esc` to close dialogs

**2. Quick SKU Generation:**
Pattern: `CATEGORY + NUMBER`
- Silk Sarees: SLK001, SLK002...
- Cotton: COT001, COT002...
- Georgette: GEO001, GEO002...

**3. Consistent Naming:**
- Always capitalize first letter
- Use standard color names
- Maintain uniform material names

**4. Customer Data Entry:**
- Always collect phone numbers for marketing
- Use consistent name format (First Last)
- Optional for walk-in, mandatory for credit sales

### Performance Tips

**1. Regular Maintenance:**
- Backup database weekly
- Clear old invoices monthly
- Keep stock count under 5000 items for best performance

**2. Search Efficiency:**
- Use specific terms
- Minimum 3 characters for best results
- Use SKU for fastest search

**3. Data Entry Speed:**
- Use Tab to move between fields
- Prepare data before entry
- Use copy-paste for repeating values

### Inventory Management Tips

**1. SKU Strategy:**
```
Format: [TYPE][MATERIAL][COLOR][NUMBER]
Example: SLK-RED-001 = Silk Red Saree #1
```

**2. Pricing Strategy:**
- Keep 30-40% margin
- Round to nearest ₹10 or ₹50
- Use psychological pricing (₹999 instead of ₹1000)

**3. Stock Levels:**
- High-demand items: Minimum 10 pieces
- Medium-demand: Minimum 5 pieces
- Slow-moving: 2-3 pieces
- Set alerts accordingly

### Customer Service Tips

**1. Professional Invoicing:**
- Always offer printed invoice
- Mention return policy verbally
- Thank customer by name

**2. Discount Management:**
- Standard discount: 5-10%
- Bulk purchase: 15-20%
- Loyal customers: Special rates
- Record reason for large discounts

**3. Communication:**
- Save customer phone numbers
- Use for new arrival notifications
- Festival offers
- Clearance sales

### Security Tips

**1. Password Management:**
- Change default password immediately
- Use strong password (8+ characters)
- Mix letters, numbers, symbols
- Don't share with everyone

**2. Admin PIN:**
- Change default PIN (1234)
- Share only with trusted staff
- Change if compromised

**3. Data Protection:**
- Daily database backups
- Store backups in different location
- Test restore process monthly

### Troubleshooting Tips

**Issue: Application Slow**
- Too many items? Archive old data
- Low disk space? Clean up disk
- Multiple instances running? Close duplicates

**Issue: Can't Find Item**
- Check spelling
- Try partial match
- Use Global Search
- Verify item was added

**Issue: Invoice Not Generated**
- Check `invoices/` folder exists
- Check write permissions
- Verify ReportLab installed
- Check disk space

**Issue: Discount Not Applying**
- Enter percentage only (no % symbol)
- Use numbers only
- Press Tab or Enter to apply
- Check summary updates

---

## Appendix: Keyboard Reference

### Navigation
- `Tab` - Move to next field
- `Shift+Tab` - Move to previous field
- `Enter` - Submit form / Next field
- `Esc` - Close dialog

### Text Entry
- `Ctrl+A` - Select all
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+X` - Cut

### Application
- `Alt+F4` - Close application
- No other shortcuts currently implemented

---

## Glossary

**SKU**: Stock Keeping Unit - Unique identifier for each item

**GST**: Goods and Services Tax - 5% for textiles

**Bill Number**: Unique invoice identifier (PREFIX + TIMESTAMP)

**Low Stock**: Items with quantity at or below threshold

**Walk-in Customer**: Customer without recorded details

**Admin PIN**: Secondary security for protected sections

**Cart**: Selected items before checkout

**Subtotal**: Total before discount and GST

**Net Sales**: Final amount after all calculations

---

## Contact & Support

For technical support:
1. Review this manual thoroughly
2. Check README.md for troubleshooting
3. Test with sample data
4. Document error messages with screenshots

---

**User Manual Version**: 1.0.0  
**Application Version**: 1.0.0  
**Last Updated**: February 2025

---

*This manual is designed to help you get the most out of your Shree Ganesha SilkManagement System. For best results, refer to it regularly and keep it accessible.*
