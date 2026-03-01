# Quick Start Guide - Shree Ganesha SilkManagement System

## ⚡ 5-Minute Setup

### Step 1: Install Python (if not already installed)
1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ **CHECK**: "Add Python to PATH" during installation
4. Click "Install Now"

### Step 2: Extract Files
1. Extract all files to a folder (e.g., `C:\BoutiqueManagement`)
2. You should see:
   - `boutique_management_system.py`
   - `requirements.txt`
   - `README.md`
   - `USER_MANUAL.md`
   - `compile.bat`

### Step 3: Install Dependencies
**Option A - Easy Way (Windows):**
1. Right-click in the folder
2. Select "Open PowerShell window here" or "Open command window here"
3. Type: `pip install -r requirements.txt`
4. Press Enter
5. Wait for installation to complete

**Option B - Manual:**
```
pip install customtkinter==5.2.1
pip install reportlab==4.0.7
pip install Pillow==10.1.0
pip install pyinstaller==6.3.0
```

### Step 4: Run the Application
```
python boutique_management_system.py
```

### Step 5: Login
- Username: `admin`
- Password: `admin123`

**🎉 You're Ready!**

---

## 🚀 Creating .exe File (Optional)

### Super Easy Method - Use the Batch File
1. Double-click `compile.bat`
2. Wait 2-5 minutes
3. Find your .exe in `dist\BoutiqueManagement.exe`

### Manual Method
```bash
pyinstaller --onefile --windowed --name "BoutiqueManagement" --collect-all customtkinter boutique_management_system.py
```

---

## 🎯 First Time Setup Checklist

After logging in for the first time:

### Immediate Tasks (5 minutes)
- [ ] Go to Settings
- [ ] Update Shop Name
- [ ] Update Shop Address
- [ ] Update Phone Number
- [ ] Update Email
- [ ] Update GST Number
- [ ] Change Bill Prefix (optional)
- [ ] Click "Save Settings"

### Security Setup (2 minutes)
- [ ] Change admin password (see below)
- [ ] Change Admin PIN in code (see README.md)

### Initial Inventory (15-30 minutes)
- [ ] Click "New Stock Entry"
- [ ] Enter Admin PIN: `1234`
- [ ] Add 5-10 sample items to test
- [ ] Verify items in "Stock Management"

### Test Run (5 minutes)
- [ ] Create a test bill
- [ ] Add items to cart
- [ ] Complete sale
- [ ] Verify invoice generation
- [ ] Check invoice PDF in `invoices/` folder

---

## 🔧 Quick Configuration Changes

### Change Admin Password

**Method 1 - Using Database (Recommended):**
1. Download [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open `boutique_database.db`
3. Go to "Browse Data" → `users` table
4. Double-click password_hash cell for admin
5. Replace with new hash:
   - Use online SHA-256 generator
   - Hash your new password
   - Paste the hash
6. Save changes

**Method 2 - Using Code:**
1. Open `boutique_management_system.py`
2. Find line ~180 (in `initialize_database`)
3. Change `"admin123"` to your password
4. Delete `boutique_database.db`
5. Run application again (new database created)

### Change Admin PIN
1. Open `boutique_management_system.py`
2. Find line 48: `ADMIN_PIN = "1234"`
3. Change `"1234"` to your desired PIN
4. Save file

### Change Colors
1. Open `boutique_management_system.py`
2. Find lines 44-51 (Config class)
3. Modify hex color codes:
   ```python
   COLOR_PRIMARY = "#8B0000"    # Your color
   COLOR_SECONDARY = "#FFD700"  # Your color
   COLOR_ACCENT = "#C76D7E"     # Your color
   ```
4. Save and restart

---

## 📱 Daily Usage Workflow

### Opening (2 minutes)
1. Open application
2. Login
3. Check Dashboard metrics
4. Review low stock alerts

### During Day (per sale: 1-2 minutes)
1. Click "New Bill"
2. Search items → Add to cart
3. Enter customer details
4. Apply discount if needed
5. Complete sale
6. Print/Email invoice

### Closing (3 minutes)
1. Go to Reports
2. Review Today's Sales
3. Note total for cash register
4. Backup database (copy file)
5. Logout

---

## 🆘 Quick Troubleshooting

### Application Won't Start
```
Problem: Nothing happens when double-clicking .exe
Solution: 
1. Run from command prompt to see errors
2. Check antivirus isn't blocking
3. Recompile with compile.bat
```

### "Module Not Found" Error
```
Problem: Error about missing module
Solution: 
pip install -r requirements.txt
```

### Can't Login
```
Problem: Invalid username/password
Solution:
1. Use default: admin / admin123
2. If changed, reset database (delete .db file)
```

### Invoice Not Generating
```
Problem: No PDF created
Solution:
1. Check if 'invoices' folder exists (create it)
2. Run: pip install reportlab
3. Check disk space
```

### Slow Performance
```
Problem: Application is laggy
Solution:
1. Too many items in database? Archive old data
2. Check disk space
3. Close other applications
```

---

## 💡 Pro Tips

### Keyboard Shortcuts
- **Enter**: Submit form / Next field
- **Tab**: Move between fields
- **Esc**: Close dialogs

### SKU Naming
Use this pattern for easy management:
```
[TYPE]-[MATERIAL]-[NUMBER]
Examples:
- SLK-001 (Silk Saree #1)
- COT-RED-001 (Cotton Red #1)
- GEO-BLU-001 (Georgette Blue #1)
```

### Customer Data
Always collect phone numbers:
- Marketing campaigns
- New arrivals notification
- Festival offers

### Backup Strategy
**Daily**: Not needed for small shops
**Weekly**: Copy database file to USB/Cloud
**Monthly**: Full backup with invoices folder

---

## 📊 Understanding the Interface

### Dashboard Cards
```
Today's Sales = How much money made today
Inventory Value = Total worth of all stock
Low Stock Alert = Items to reorder
```

### Bill Summary
```
Subtotal = Price × Quantity (all items)
Discount = Subtotal × Discount %
After Discount = Subtotal - Discount
GST = After Discount × 5%
Final Total = After Discount + GST
```

### Stock Colors
```
Green = Sufficient stock
Red = Low stock (≤5 items)
Red Border = Needs immediate attention
```

---

## 🎓 Learning Path

### Day 1: Basics
- [ ] Login/Logout
- [ ] Navigate dashboard
- [ ] Create test bill
- [ ] View reports

### Day 2: Stock Management
- [ ] Add new items
- [ ] Edit existing items
- [ ] Search functionality
- [ ] Delete items

### Day 3: Advanced
- [ ] Apply discounts
- [ ] Customer management
- [ ] Global search
- [ ] Settings configuration

### Week 1 Goal
- [ ] Comfortable with daily operations
- [ ] Can handle 10+ bills per day
- [ ] Understand all reports
- [ ] Know how to backup

---

## 📞 Support Resources

### Documentation
1. **README.md** - Complete technical guide
2. **USER_MANUAL.md** - Detailed feature explanations
3. **This Guide** - Quick reference

### Common Files
```
boutique_database.db = Your data (BACKUP THIS!)
invoices/ = All generated invoices
boutique_management_system.py = Main program
requirements.txt = Dependencies list
```

### Backup Files
```
boutique_database.db → Copy weekly
invoices/ folder → Copy monthly
```

---

## ✅ Pre-Launch Checklist

Before going live with real data:

### Configuration
- [ ] Updated all shop details in Settings
- [ ] Changed default admin password
- [ ] Changed Admin PIN in code
- [ ] Tested invoice generation
- [ ] Verified GST number is correct

### Testing
- [ ] Created test bills
- [ ] Applied discounts
- [ ] Checked calculations
- [ ] Generated invoices
- [ ] Verified invoice content

### Preparation
- [ ] Printer setup complete
- [ ] Invoice paper available
- [ ] Staff trained on basics
- [ ] Backup strategy in place
- [ ] Emergency contact ready

### Data Entry
- [ ] Initial inventory added
- [ ] SKU system finalized
- [ ] Prices verified
- [ ] Suppliers recorded
- [ ] Categories organized

---

## 🎯 Success Metrics

### Week 1
- Process 50+ bills
- 0 calculation errors
- <2 minutes per bill
- Staff comfortable with system

### Month 1
- 200+ bills processed
- Accurate inventory tracking
- Regular backups
- Using reports for decisions

### Month 3
- Full adoption
- Historical data analysis
- Optimized workflows
- Happy customers

---

## 🚀 Next Steps

After mastering the basics:

1. **Explore Advanced Features**
   - Global search shortcuts
   - Report analysis
   - Discount strategies

2. **Optimize Workflows**
   - Faster data entry
   - Better SKU organization
   - Customer categorization

3. **Scale Up**
   - Add more inventory
   - Multiple users (advanced)
   - Integration possibilities

---

## 📄 File Reference

```
📁 Your Folder/
├── 📄 boutique_management_system.py (Main program)
├── 📄 requirements.txt (Dependencies)
├── 📄 README.md (Full documentation)
├── 📄 USER_MANUAL.md (User guide)
├── 📄 QUICK_START.md (This file)
├── 📄 compile.bat (Compilation script)
├── 💾 boutique_database.db (Database - created on first run)
└── 📁 invoices/ (Invoice PDFs - created automatically)
```

---

## 🎉 You're All Set!

This system is designed to:
- ✅ Save time
- ✅ Reduce errors
- ✅ Track inventory
- ✅ Generate professional invoices
- ✅ Provide insights through reports

**Remember**: Start small, test thoroughly, then go live!

---

**Quick Start Guide Version**: 1.0.0  
**Last Updated**: February 2025

For detailed information, see **README.md** and **USER_MANUAL.md**
