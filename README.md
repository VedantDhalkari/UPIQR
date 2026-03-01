# Shree Ganesha Silk - Developed by VedStacK Industries

## 🌟 Overview

A comprehensive, professional-grade inventory management and billing system designed specifically for women's ethnic wear boutiques. Built with Python, featuring a modern CustomTkinter GUI with an elegant design theme perfect for saree boutiques.

## ✨ Key Features

### 🔐 Security
- **Secure Login System**: Username and password authentication with SHA-256 encryption
- **Admin PIN Protection**: Secondary PIN verification for sensitive sections (Stock Management, New Stock Entry)
- **Role-based Access**: Admin and user role management

### 📊 Modern Dashboard
- Real-time metrics display (Today's Sales, Inventory Value, Low Stock Alerts)
- Recent transactions overview
- Quick access navigation sidebar
- Elegant dark/light theme support with boutique-themed colors (Deep Maroon, Gold, Rose Gold)

### 🛒 Advanced Billing System
- Quick search functionality by SKU, item name, or color
- Visual shopping cart with quantity management
- Real-time discount calculations
- Automatic GST (5%) calculation for textiles
- Customer information capture (optional)
- Instant PDF invoice generation with professional formatting
- Automatic invoice saving and organization

### 📦 Stock Management (Admin Protected)
- Comprehensive inventory table view
- Edit and delete capabilities
- Visual low-stock alerts (red highlight)
- Real-time stock updates
- Search and filter functionality
- Display: SKU, Type, Material, Color, Quantity, Prices, Supplier

### ➕ New Stock Entry (Admin Protected)
- Dedicated form for adding new inventory
- Fields: SKU, Saree Type, Material, Color, Design, Quantity, Purchase Price, Selling Price, Supplier, Category
- Input validation
- Duplicate SKU prevention

### 🔍 Global Search
- Unified search across all bills, customers, and inventory
- Search by bill number, customer name, phone, SKU, item details
- Instant results display with categorization

### 📈 Reports & Analytics
- Today's sales report with detailed breakdown
- Monthly sales summary
- Low stock items report
- GST collection tracking
- Discount analysis

### ⚙️ Settings
- Shop information management (Name, Address, Phone, Email, GST Number)
- Bill prefix customization
- Easy configuration interface

## 🎨 UI/UX Features

### Theme & Design
- **Premium Shree Ganesha SilkTheme**: Deep Maroon (#8B0000), Gold (#FFD700), Rose Gold (#C76D7E)
- **Modern Dark Mode**: Professional dark interface with excellent contrast
- **Responsive Layout**: Adapts to different screen sizes
- **Smooth Transitions**: Enhanced user experience with fluid animations
- **Professional Typography**: Clear, readable fonts with proper hierarchy

### Branding
- Logo placeholder support (place your logo as 'logo.png')
- Shop name prominently displayed
- Professional invoice templates
- Consistent branding throughout the application

## 💾 Technical Specifications

### Technology Stack
- **Language**: Python 3.10+
- **GUI Framework**: CustomTkinter (Modern, premium look)
- **Database**: SQLite (Local, file-based storage)
- **PDF Generation**: ReportLab (Professional invoices)
- **Architecture**: Modular, object-oriented design

### Database Schema
```
users
- user_id (PK)
- username (Unique)
- password_hash
- role
- created_at

inventory
- item_id (PK)
- sku_code (Unique)
- saree_type
- material
- color
- design
- quantity
- purchase_price
- selling_price
- supplier_name
- category
- added_date
- last_updated

sales
- sale_id (PK)
- bill_number (Unique)
- customer_name
- customer_phone
- total_amount
- discount_percent
- discount_amount
- gst_amount
- final_amount
- payment_method
- sale_date
- created_by

sale_items
- sale_item_id (PK)
- sale_id (FK)
- item_id (FK)
- sku_code
- item_name
- quantity
- unit_price
- total_price

settings
- setting_key (PK)
- setting_value
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Windows 10/11 (for .exe compilation)
- 500 MB free disk space

### Step-by-Step Installation

#### 1. Install Python
Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/)

**Important**: During installation, check "Add Python to PATH"

#### 2. Extract the Application Files
Extract all files to a folder, e.g., `C:\BoutiqueManagement`

#### 3. Open Command Prompt in the Folder
- Navigate to the folder containing the files
- Shift + Right-click in the folder
- Select "Open PowerShell window here" or "Open command window here"

#### 4. Install Dependencies
Run the following command:
```bash
pip install -r requirements.txt
```

This will install:
- customtkinter (Modern GUI framework)
- Pillow (Image processing)
- reportlab (PDF generation)
- python-dateutil (Date utilities)
- pyinstaller (For creating .exe)

#### 5. Run the Application
```bash
python boutique_management_system.py
```

### Default Credentials
- **Username**: admin
- **Password**: admin123
- **Admin PIN**: 1234

**⚠️ IMPORTANT**: Change these credentials in production!

## 📦 Creating a Single .exe File

### Method 1: Using PyInstaller (Recommended)

#### 1. Install PyInstaller
```bash
pip install pyinstaller
```

#### 2. Create the Executable
Run this command in your project folder:

```bash
pyinstaller --onefile --windowed --name "BoutiqueManagement" --icon=logo.ico boutique_management_system.py
```

**Explanation of flags**:
- `--onefile`: Creates a single executable file
- `--windowed`: No console window (clean GUI-only app)
- `--name`: Name of the executable
- `--icon`: Application icon (optional - create logo.ico if you have one)

#### 3. Advanced Compilation (Recommended)
For a more complete package with all dependencies:

```bash
pyinstaller --onefile --windowed ^
    --name "BoutiqueManagement" ^
    --icon=logo.ico ^
    --add-data "logo.png;." ^
    --hidden-import=reportlab.graphics.barcode ^
    --hidden-import=reportlab.graphics.charts ^
    --collect-all customtkinter ^
    boutique_management_system.py
```

#### 4. Locate Your Executable
After compilation (takes 2-5 minutes):
- The .exe file will be in the `dist` folder
- File name: `BoutiqueManagement.exe`
- Size: Approximately 40-60 MB

### Method 2: Using Auto-py-to-exe (GUI Method)

#### 1. Install Auto-py-to-exe
```bash
pip install auto-py-to-exe
```

#### 2. Launch the GUI
```bash
auto-py-to-exe
```

#### 3. Configure Settings
- **Script Location**: Browse and select `boutique_management_system.py`
- **Onefile**: Select "One File"
- **Console Window**: Select "Window Based (hide the console)"
- **Icon**: Browse and select your icon file (optional)

#### 4. Click "Convert .py to .exe"
Wait for the process to complete. The .exe will be in the `output` folder.

## 📁 File Structure

```
BoutiqueManagement/
│
├── boutique_management_system.py    # Main application file
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── USER_MANUAL.md                   # User guide
├── logo.png                         # Your shop logo (optional)
│
├── boutique_database.db            # Database (created on first run)
│
├── invoices/                       # Auto-created folder
│   ├── ESB20240101120000.pdf      # Sample invoice
│   └── ...
│
└── dist/                           # After compilation
    └── BoutiqueManagement.exe     # Your executable
```

## 🔧 Configuration

### Changing Admin PIN
Edit `boutique_management_system.py`, line 48:
```python
ADMIN_PIN = "1234"  # Change this to your desired PIN
```

### Customizing Colors
Edit the Config class (lines 44-51):
```python
COLOR_PRIMARY = "#8B0000"    # Deep Maroon
COLOR_SECONDARY = "#FFD700"  # Gold
COLOR_ACCENT = "#C76D7E"     # Rose Gold
```

### Adjusting GST Rate
Edit line 54:
```python
GST_RATE = 5  # Change to your applicable GST rate
```

### Low Stock Threshold
Edit line 57:
```python
LOW_STOCK_THRESHOLD = 5  # Items with quantity <= this will be highlighted
```

## 🎯 Usage Guide

### First Time Setup
1. Run the application
2. Login with default credentials
3. Go to Settings and update shop information
4. Change default admin password in the database
5. Add your initial inventory via "New Stock Entry"

### Daily Operations
1. **Morning**: Check Dashboard for overview and low stock alerts
2. **Sales**: Use "New Bill" to process customer purchases
3. **Stock Updates**: Add new arrivals via "New Stock Entry"
4. **Reports**: Review daily sales at end of day

### Weekly Tasks
- Review low stock items and place orders
- Analyze weekly sales reports
- Update prices if needed
- Backup database file

### Monthly Tasks
- Generate monthly sales report
- Review inventory valuation
- Update supplier information
- Clean up old invoices (optional)

## 📱 Features in Detail

### Bill Generation Process
1. Click "New Bill" from dashboard
2. Search for items using the search bar
3. Add items to cart
4. Enter customer details (optional)
5. Apply discount if needed
6. Review summary (Subtotal, Discount, GST, Total)
7. Click "Complete Sale & Generate Invoice"
8. Invoice is automatically saved to `invoices/` folder
9. Option to open the invoice immediately

### Invoice Features
- Professional PDF format
- Company branding and details
- Itemized product list
- GST breakdown
- Unique bill number
- Date and time stamp
- Customer information
- Terms & conditions placeholder

### Stock Management Workflow
1. Enter Admin PIN when prompted
2. View all inventory in table format
3. Search/filter items as needed
4. Click "Edit" to modify item details
5. Click "Delete" to remove items (with confirmation)
6. Low stock items highlighted in red

### Search Capabilities
- **Billing Search**: Find items by SKU, name, type, color, material
- **Stock Search**: Filter inventory using any field
- **Global Search**: Find bills by number, customer name/phone; find items by any attribute
- **Real-time**: Results update as you type

## 🔒 Security Features

### Password Security
- All passwords stored as SHA-256 hashes
- No plain-text password storage
- Cannot be reverse-engineered

### Admin Protection
- Critical sections require PIN verification
- Stock management access controlled
- New stock entry protected

### Data Integrity
- SQLite transactions ensure data consistency
- Foreign key constraints prevent orphaned records
- Unique constraints on SKU and bill numbers

## 🐛 Troubleshooting

### Application Won't Start
**Issue**: Double-clicking .exe does nothing
**Solution**: 
- Run from command prompt to see error messages
- Check if antivirus is blocking the application
- Ensure all dependencies are included in compilation

### "Module Not Found" Error
**Issue**: Missing Python packages
**Solution**: 
```bash
pip install -r requirements.txt
```

### Database Locked Error
**Issue**: Database is being accessed by another process
**Solution**: 
- Close all instances of the application
- Restart your computer
- Check if database file is read-only

### PDF Generation Fails
**Issue**: Invoice not creating
**Solution**: 
- Ensure `invoices/` folder exists
- Check write permissions on folder
- Verify ReportLab is installed: `pip install reportlab`

### Low Memory Warning
**Issue**: Large database causing slowdown
**Solution**: 
- Archive old sales records
- Compact database: Copy data to new database
- Increase system RAM if possible

## 📊 Database Backup

### Manual Backup
Simply copy `boutique_database.db` to a safe location

### Automated Backup (Advanced)
Create a batch file `backup.bat`:
```batch
@echo off
set date=%date:~-4,4%%date:~-10,2%%date:~-7,2%
copy boutique_database.db backups\boutique_database_%date%.db
echo Backup created: boutique_database_%date%.db
pause
```

Run this daily/weekly to create timestamped backups

## 🔄 Updates & Maintenance

### Updating the Application
1. Backup your database file
2. Replace `boutique_management_system.py` with new version
3. Check if new dependencies are needed
4. Run `pip install -r requirements.txt`
5. Recompile to .exe if needed

### Database Migration
If database structure changes:
1. Export your data (contact developer for migration script)
2. Create new database with updated schema
3. Import old data

## 💡 Tips & Best Practices

### Performance
- Regular database cleanup (archive old records)
- Keep inventory below 10,000 items for optimal performance
- Use SSD for faster database operations

### Data Entry
- Use consistent naming conventions for saree types
- Maintain proper SKU format (e.g., SAR001, SAR002)
- Fill in supplier information for better tracking

### Customer Service
- Always provide printed/email invoices
- Keep customer phone numbers for marketing
- Use discount feature strategically

### Inventory Management
- Regular stock audits (monthly recommended)
- Update purchase prices when they change
- Monitor low stock alerts daily

## 🆘 Support

### Common Questions
**Q: Can I use this on multiple computers?**
A: Yes, but you'll need separate database files or set up network sharing

**Q: Can I customize the invoice template?**
A: Yes, modify the `InvoiceGenerator` class in the code

**Q: How many items can I store?**
A: SQLite can handle millions of records, but 10,000+ items may slow down the interface

**Q: Can I add more users?**
A: Yes, insert new users into the `users` table with hashed passwords

### Getting Help
- Review this README thoroughly
- Check the USER_MANUAL.md for step-by-step guides
- Examine error messages carefully
- Test with sample data first

## 📄 License & Credits

**Developer**: Python Desktop Applications Team
**Framework**: CustomTkinter by Tom Schimansky
**PDF Library**: ReportLab

## 🔮 Future Enhancements (Potential)

- Multi-user access with role management
- SMS/Email invoice delivery
- Barcode scanning support
- Mobile app companion
- Cloud backup integration
- Sales analytics & graphs
- Supplier management module
- Purchase order system
- Employee commission tracking
- Customer loyalty program

## ⚠️ Important Notes

1. **ALWAYS backup your database before major changes**
2. **Change default credentials immediately in production**
3. **Test thoroughly with sample data first**
4. **Keep invoice folder organized**
5. **Run on a computer with adequate specifications** (4GB RAM minimum)

## 🎓 Learning Resources

### Python Development
- [Python Official Documentation](https://docs.python.org/3/)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)

### SQLite
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [DB Browser for SQLite](https://sqlitebrowser.org/) - Visual database management

### PDF Generation
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)

---

## 🙏 Thank You

Thank you for choosing this Shree Ganesha SilkManagement System. This application has been designed with care to meet the specific needs of ethnic wear boutiques. We wish you success in your business!

For any critical issues or enhancement requests, please document them thoroughly with screenshots and steps to reproduce.

**Version**: 1.0.0  
**Last Updated**: February 2025  
**Compatibility**: Windows 10/11, Python 3.10+

---

*"Empowering Shree Ganesha Silkbusinesses with modern technology"*
