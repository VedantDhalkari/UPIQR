# Build Instructions

This project is a modular Python application using CustomTkinter. To create a standalone `.exe` file, follow these instructions.

## Prerequisites

1.  **Python 3.10+** installed.
2.  **Pip** installed.

## Setup

1.  Open a terminal in the project directory.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    pip install pyinstaller
    ```

## Compilation

You can use the included `compile.bat` script, or run the command manually.

### Using compile.bat (Recommended)
Double-click `compile.bat` or run it from the terminal:
```cmd
compile.bat
```

### Manual Compilation
Run the following command in your terminal:
```bash
pyinstaller --onefile --windowed --name "BoutiqueManagerPro" --collect-all customtkinter main.py
```

**Explanation of flags:**
*   `--onefile`: Packages everything into a single `.exe` file.
*   `--windowed`: Hides the console window when the app runs.
*   `--name`: Sets the name of the executable.
*   `--collect-all customtkinter`: Ensures all CustomTkinter assets (themes, fonts) are included.

## Output

The compiled executable will be in the `dist` folder:
`dist/BoutiqueManagerPro.exe`

## Deployment

To distribute the application:
1.  Copy `dist/BoutiqueManagerPro.exe` to a new folder on the target machine.
2.  Run the `.exe`.
3.  The app will automatically create:
    *   `boutique_database.db` (Database)
    *   `invoices/` (Directory for generated PDFs)

> [!NOTE]
> If you have a `logo.png` or `assets` folder, place it next to the `.exe` (unless you modify the build command to bundle it).
