# Complete Installation Guide
## Shree Ganesha SilkDeveloped by VedStacK Industries

---

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Pre-Installation Checklist](#pre-installation-checklist)
3. [Installing Python](#installing-python)
4. [Setting Up the Application](#setting-up-the-application)
5. [Running the Application](#running-the-application)
6. [Creating the Executable](#creating-the-executable)
7. [Deployment to Other Computers](#deployment-to-other-computers)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 or Windows 11
- **Processor**: Intel Core i3 or equivalent
- **RAM**: 4 GB
- **Storage**: 500 MB free space (1 GB recommended)
- **Display**: 1366 x 768 resolution (1920 x 1080 recommended)

### Recommended Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Processor**: Intel Core i5 or better
- **RAM**: 8 GB or more
- **Storage**: 2 GB free space
- **Display**: 1920 x 1080 or higher
- **Internet**: For initial setup and updates only

---

## Pre-Installation Checklist

Before you begin, ensure you have:

- [ ] Administrator access to your computer
- [ ] Internet connection (for downloading Python and packages)
- [ ] Antivirus temporarily disabled (it may block the installer)
- [ ] At least 1 GB free disk space
- [ ] The application files (extracted to a folder)

---

## Installing Python

### Step 1: Download Python

1. Open your web browser
2. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
3. Click the yellow "Download Python 3.x.x" button
4. Wait for the installer to download (approximately 25-30 MB)

### Step 2: Run Python Installer

1. Locate the downloaded file (usually in Downloads folder)
   - File name: `python-3.x.x-amd64.exe` or similar
2. Double-click the installer
3. **⚠️ CRITICAL**: Check the box "Add Python to PATH"
   - This is at the bottom of the installer window
   - Without this, commands won't work
4. Click "Install Now"
5. Wait for installation (2-5 minutes)
6. Click "Close" when finished

### Step 3: Verify Python Installation

1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. In the black window (Command Prompt), type:
   ```
   python --version
   ```
4. Press Enter
5. You should see something like: `Python 3.10.x` or `Python 3.11.x`

**If you see an error**:
- Python may not be in PATH
- Reinstall Python and ensure you check "Add Python to PATH"

---

## Setting Up the Application

### Step 1: Extract Application Files

1. Locate the ZIP file containing the application
2. Right-click the ZIP file
3. Select "Extract All..."
4. Choose a location (e.g., `C:\BoutiqueManagement`)
5. Click "Extract"

**You should now see these files:**
- `boutique_management_system.py`
- `requirements.txt`
- `README.md`
- `USER_MANUAL.md`
- `QUICK_START.md`
- `compile.bat`
- `generate_sample_data.py`

### Step 2: Open Command Prompt in Folder

**Method 1 - Using File Explorer (Recommended)**:
1. Open the folder with the extracted files
2. Hold `Shift` key and right-click in empty space
3. Select "Open PowerShell window here" or "Open command window here"

**Method 2 - Manual**:
1. Open Command Prompt (Windows Key + R, type `cmd`, Enter)
2. Type: `cd C:\BoutiqueManagement` (or your folder path)
3. Press Enter

### Step 3: Install Dependencies

In the Command Prompt/PowerShell window, type:

```bash
pip install -r requirements.txt
```

Press Enter and wait.

**What you should see:**
```
Collecting customtkinter==5.2.1
  Downloading customtkinter-5.2.1-py3-none-any.whl (...)
Collecting reportlab==4.0.7
  Downloading reportlab-4.0.7-py3-none-any.whl (...)
...
Successfully installed customtkinter-5.2.1 Pillow-10.1.0 reportlab-4.0.7 ...
```

**If you see errors**:
- Check your internet connection
- Try: `pip install --upgrade pip` first, then retry
- Make sure Python was installed correctly

### Step 4: Verify Installation

Type this command to check if all packages are installed:

```bash
pip list
```

You should see these packages (among others):
- customtkinter (5.2.1)
- reportlab (4.0.7)
- Pillow (10.1.0)
- pyinstaller (6.3.0)

---

## Running the Application

### First Run

In the Command Prompt (in your application folder), type:

```bash
python boutique_management_system.py
```

Press Enter.

**What happens:**
1. A window opens showing the login screen
2. Database file (`boutique_database.db`) is created automatically
3. Default admin user is created

### Login

**Default credentials:**
- Username: `admin`
- Password: `admin123`

1. Type `admin` in the Username field
2. Type `admin123` in the Password field
3. Click "Login" or press Enter

**Success**: You'll see the Dashboard

### First-Time Configuration

1. Click "Settings" from the left sidebar
2. Update the following:
   - Shop Name: Your Shree Ganesha Silkname
   - Address: Your complete address
   - Phone: Your contact number
   - Email: Your email address
   - GST Number: Your GST registration number
   - Bill Prefix: 3-4 letter code (e.g., "ABC")
3. Click "Save Settings"
4. Confirmation message appears

### Adding Sample Data (Optional but Recommended)

To test the application with sample data:

1. Close the application
2. In Command Prompt, type:
   ```bash
   python generate_sample_data.py
   ```
3. Press Enter
4. Wait for the script to complete
5. You'll see a summary of generated data

**This creates:**
- 50 sample inventory items
- 30 days of sample sales
- Various customers and transactions

---

## Creating the Executable

### Why Create an .exe?

Benefits:
- ✅ No need for Python on other computers
- ✅ Double-click to run
- ✅ Professional distribution
- ✅ Easier for non-technical users

### Method 1: Using the Batch File (Easiest)

1. Locate `compile.bat` in your folder
2. Double-click `compile.bat`
3. A black window opens
4. Wait 2-5 minutes
5. Process completes automatically

**Result**: `BoutiqueManagement.exe` in `dist` folder

### Method 2: Manual Compilation

In Command Prompt (in application folder):

```bash
pyinstaller --onefile --windowed --name "BoutiqueManagement" --collect-all customtkinter boutique_management_system.py
```

Press Enter and wait 2-5 minutes.

**What you'll see:**
```
Building EXE...
Building PKG...
Building EXE from PKG complete!
```

### After Compilation

1. Go to the `dist` folder
2. You'll find `BoutiqueManagement.exe`
3. File size: approximately 40-60 MB

**Test the executable:**
1. Double-click `BoutiqueManagement.exe`
2. Application should open
3. Login with admin credentials

---

## Deployment to Other Computers

### Preparing for Distribution

**What to copy:**
```
📁 BoutiqueManagement/
├── 📄 BoutiqueManagement.exe (from dist folder)
├── 📄 README.md (documentation)
├── 📄 USER_MANUAL.md (user guide)
└── 📄 QUICK_START.md (quick reference)
```

**⚠️ Do NOT copy:**
- `boutique_database.db` (contains your data - create fresh on target)
- `__pycache__` folder
- `.spec` files
- `build` folder

### Installing on Another Computer

**Requirements on target computer:**
- ❌ Python NOT required
- ✅ Windows 10 or 11
- ✅ No special software needed

**Steps:**
1. Copy `BoutiqueManagement.exe` to any folder
2. Double-click to run
3. Database created automatically on first run
4. Configure settings

### First Run on New Computer

When running for the first time:
1. Windows SmartScreen may appear
   - Click "More info"
   - Click "Run anyway"
2. Antivirus may scan the file (this is normal)
3. Application opens and creates database
4. Login with default credentials
5. Update settings immediately

---

## Troubleshooting

### Issue: Python Command Not Found

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**
1. Reinstall Python with "Add to PATH" checked
2. Restart Command Prompt
3. Restart computer

**Verify:**
```bash
python --version
```

### Issue: pip Command Not Found

**Symptoms:**
```
'pip' is not recognized as an internal or external command
```

**Solution:**
```bash
python -m pip install -r requirements.txt
```

### Issue: Permission Denied

**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError: [WinError 5] Access denied
```

**Solutions:**
1. Run Command Prompt as Administrator
2. Or add `--user` flag:
   ```bash
   pip install --user -r requirements.txt
   ```

### Issue: Module Import Error After Compilation

**Symptoms:**
Application .exe crashes or shows errors about missing modules

**Solution:**
Recompile with more explicit includes:
```bash
pyinstaller --onefile --windowed ^
    --name "BoutiqueManagement" ^
    --collect-all customtkinter ^
    --collect-all reportlab ^
    --hidden-import=PIL ^
    boutique_management_system.py
```

### Issue: Application Freezes on Launch

**Possible Causes:**
1. Antivirus blocking
2. Corrupted database
3. Missing dependencies

**Solutions:**
1. Add exception in antivirus
2. Delete `boutique_database.db` and restart
3. Reinstall dependencies

### Issue: Cannot Generate Invoice

**Symptoms:**
Error when completing sale, no PDF created

**Solutions:**
1. Check if `invoices` folder exists (create manually if needed)
2. Verify ReportLab installed:
   ```bash
   pip install --force-reinstall reportlab
   ```
3. Check disk space
4. Check folder write permissions

### Issue: Database Locked Error

**Symptoms:**
```
database is locked
```

**Solutions:**
1. Close all instances of the application
2. Restart computer
3. Check if file is read-only:
   - Right-click `boutique_database.db`
   - Properties → Uncheck "Read-only"

### Issue: Slow Performance

**Symptoms:**
Application is laggy, slow to respond

**Solutions:**
1. Archive old sales records
2. Reduce inventory to <5000 items
3. Run on SSD instead of HDD
4. Increase computer RAM
5. Close other applications

### Issue: Windows SmartScreen Warning

**When deploying .exe:**
```
Windows protected your PC
Microsoft Defender SmartScreen prevented an unrecognized app from starting
```

**Solution:**
1. Click "More info"
2. Click "Run anyway"
3. This is normal for new/unsigned applications

**For production:**
- Consider code signing certificate (advanced)
- Or distribute with clear instructions

---

## Advanced Configuration

### Changing Application Colors

Edit `boutique_management_system.py`:

```python
# Lines 44-51 in Config class
COLOR_PRIMARY = "#8B0000"    # Deep Maroon - Change this
COLOR_SECONDARY = "#FFD700"  # Gold - Change this
COLOR_ACCENT = "#C76D7E"     # Rose Gold - Change this
```

Popular color schemes:
- **Blue Theme**: Primary=#1E3A8A, Secondary=#3B82F6, Accent=#60A5FA
- **Green Theme**: Primary=#065F46, Secondary=#10B981, Accent=#34D399
- **Purple Theme**: Primary=#5B21B6, Secondary=#A855F7, Accent=#C084FC

### Changing Admin PIN

Edit `boutique_management_system.py`:

```python
# Line 48 in Config class
ADMIN_PIN = "1234"  # Change to your preferred PIN
```

Save and restart application.

### Customizing Invoice Template

The invoice generation is in the `InvoiceGenerator` class (starts around line 250).

You can customize:
- Colors
- Fonts
- Layout
- Additional fields
- Footer text

Requires knowledge of ReportLab library.

### Enabling Debug Mode

For troubleshooting, add this at the start of `boutique_management_system.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG, filename='app.log')
```

Errors will be written to `app.log` file.

---

## Security Best Practices

### Initial Setup Security

1. **Change default password immediately**
   - Use strong password (8+ characters, mixed case, numbers)
   - Store securely

2. **Change Admin PIN**
   - Don't use 1234, 0000, 1111
   - Make it memorable but not obvious

3. **Protect database file**
   - Store in secure location
   - Regular backups
   - Don't share on public networks

### Ongoing Security

1. **Regular backups**
   - Weekly: Copy database to external drive
   - Monthly: Full system backup
   - Test restore process

2. **Access control**
   - Limit who has admin PIN
   - Individual user accounts for staff (future enhancement)

3. **Physical security**
   - Lock computer when away
   - Screen privacy filter (optional)
   - Secure workspace

---

## Backup and Recovery

### Creating Backups

**Daily Backup** (Quick):
1. Close application
2. Copy `boutique_database.db` file
3. Paste to USB drive or cloud storage
4. Rename with date: `boutique_database_2024-02-09.db`

**Weekly Backup** (Full):
1. Close application
2. Copy entire application folder
3. Include:
   - `boutique_database.db`
   - `invoices` folder
   - Settings (if customized)

**Automated Backup** (Advanced):
Create `backup.bat`:
```batch
@echo off
set today=%date:~-4,4%%date:~-10,2%%date:~-7,2%
mkdir "backups\%today%"
copy boutique_database.db "backups\%today%\"
xcopy /E /I invoices "backups\%today%\invoices"
echo Backup complete for %today%
```

Run this weekly.

### Restoring from Backup

1. Close application
2. Locate backup file
3. Copy backup file
4. Paste and rename to `boutique_database.db`
5. Replace existing file
6. Start application

---

## Performance Optimization

### Database Optimization

**When to optimize:**
- After 10,000+ sales
- Application becomes slow
- Database file >100 MB

**How to optimize:**
1. Export important data
2. Create fresh database
3. Import recent data
4. Archive old data separately

### System Optimization

1. **Use SSD**: Faster database operations
2. **Increase RAM**: Better multitasking
3. **Close background apps**: More resources available
4. **Regular cleanup**: Delete temporary files

---

## Getting Help

### Before Seeking Help

1. ✅ Read this installation guide completely
2. ✅ Check README.md for technical details
3. ✅ Review USER_MANUAL.md for feature help
4. ✅ Try Quick Start guide
5. ✅ Test with sample data

### Reporting Issues

When reporting problems, include:
- Python version (`python --version`)
- Operating System (Windows 10/11)
- Error message (exact text)
- Steps to reproduce
- Screenshots if applicable

---

## Next Steps

After successful installation:

1. ✅ Complete initial configuration
2. ✅ Add sample data and test
3. ✅ Review USER_MANUAL.md
4. ✅ Practice with test bills
5. ✅ Train staff if applicable
6. ✅ Set up backup routine
7. ✅ Go live with real data!

---

## Appendix: Command Reference

### Python Commands
```bash
python --version                    # Check Python version
python boutique_management_system.py # Run application
python generate_sample_data.py      # Generate test data
```

### Pip Commands
```bash
pip --version                       # Check pip version
pip install -r requirements.txt     # Install dependencies
pip list                           # Show installed packages
pip install --upgrade pip           # Update pip itself
```

### PyInstaller Commands
```bash
pyinstaller --version               # Check PyInstaller version
pyinstaller --onefile --windowed [script.py]  # Basic compilation
```

### File Management
```bash
dir                                # List files (Windows)
cd [folder]                        # Change directory
mkdir [name]                       # Create folder
copy [source] [dest]               # Copy file
```

---

## Glossary

**Python**: Programming language used to build this application

**Pip**: Package installer for Python (installs libraries)

**PyInstaller**: Tool to convert Python scripts to .exe files

**Database**: SQLite file storing all your data

**GUI**: Graphical User Interface (the visual design)

**CustomTkinter**: Modern UI framework used for the interface

**ReportLab**: Library for generating PDF invoices

**SKU**: Stock Keeping Unit (unique item identifier)

**.exe**: Executable file (program that runs on Windows)

**Virtual Environment**: Isolated Python setup (not used here, but good to know)

---

**Installation Guide Version**: 1.0.0  
**Application Version**: 1.0.0  
**Last Updated**: February 2025

---

**🎉 Congratulations on completing the installation!**

You now have a professional Shree Ganesha Silkmanagement system ready to use. Take time to explore all features, test thoroughly, and customize to your needs.

For detailed feature usage, please refer to the **USER_MANUAL.md**.

Good luck with your Shree Ganesha Silkbusiness! 🌟
