"""
Configuration Module for Shree Ganesha Silk System
Contains all application settings, colors, and constants for the premium light theme
"""

# Application Information
APP_NAME = "Shree Ganesha Silk"
APP_SUBTITLE = "Developed by VedStacK Industries"
VERSION = "2.2.0"
COMPANY = "Pro Edition"

# Database Configuration
DB_NAME = "boutique_database.db"
ADMIN_PIN = "1234"  # Change in production
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"

# Business Configuration
GST_RATE = 0  # GST Disabled
LOW_STOCK_THRESHOLD = 5
BILL_PREFIX = "ESB"
LOGO_PATH = "logo.jpg"

# Premium Light Theme - Color Palette
# Primary Colors (Purple/Lavender)
COLOR_PRIMARY = "#7C3AED"           # Vibrant Purple (buttons, accents)
COLOR_PRIMARY_LIGHT = "#A78BFA"     # Light Purple (hover, secondary)
COLOR_PRIMARY_DARK = "#5B21B6"      # Dark Purple (text accents)
COLOR_SECONDARY = "#EC4899"         # Pink accent
COLOR_SECONDARY_DARK = "#DB2777"    # Dark Pink (hover)

# Background Colors
COLOR_BG_MAIN = "#F5F3FF"          # Light Lavender (main background)
COLOR_BG_CARD = "#FFFFFF"          # White (cards, panels)
COLOR_BG_SIDEBAR = "#FFFFFF"       # White (sidebar)
COLOR_BG_HOVER = "#F3F4F6"         # Light gray (hover states)

# Text Colors
COLOR_TEXT_PRIMARY = "#1F2937"     # Dark Gray (main text)
COLOR_TEXT_SECONDARY = "#6B7280"   # Medium Gray (secondary text)
COLOR_TEXT_LIGHT = "#9CA3AF"       # Light Gray (labels)
COLOR_TEXT_WHITE = "#FFFFFF"       # White (on dark backgrounds)

# Semantic Colors
COLOR_SUCCESS = "#10B981"          # Green (success states)
COLOR_WARNING = "#F59E0B"          # Amber (warnings, low stock)
COLOR_DANGER = "#EF4444"           # Red (errors, critical)
COLOR_INFO = "#3B82F6"             # Blue (information)

# UI Element Colors
COLOR_BORDER = "#E5E7EB"           # Light Gray (borders)
COLOR_BORDER_FOCUS = COLOR_PRIMARY # Purple (focused borders)
COLOR_SHADOW = "#E5E7EB"           # Light gray for shadows

# Chart Colors (Purple-Pink Gradient Palette)
CHART_COLORS = [
    "#7C3AED",  # Vibrant Purple
    "#A78BFA",  # Light Purple
    "#EC4899",  # Pink
    "#F472B6",  # Light Pink
    "#C084FC",  # Purple
    "#E879F9",  # Magenta
    "#8B5CF6",  # Purple Variant
    "#D946EF",  # Fuchsia
]

# Gradient Definitions
GRADIENT_PRIMARY = ["#7C3AED", "#A78BFA"]  # Purple gradient
GRADIENT_ACCENT = ["#EC4899", "#F472B6"]   # Pink gradient
GRADIENT_SUCCESS = ["#10B981", "#34D399"]  # Green gradient

# Typography
FONT_FAMILY = "Segoe UI"  # System font (Windows)
FONT_SIZE_HEADING_1 = 32
FONT_SIZE_HEADING_2 = 24
FONT_SIZE_HEADING_3 = 18
FONT_SIZE_BODY = 14
FONT_SIZE_SMALL = 12
FONT_SIZE_METRIC = 36

# Spacing
SPACING_XS = 5
SPACING_SM = 10
SPACING_MD = 15
SPACING_LG = 20
SPACING_XL = 30

# Border Radius
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 15
RADIUS_XL = 20

# Component Sizes
SIDEBAR_WIDTH = 260
BUTTON_HEIGHT = 40
BUTTON_HEIGHT_LG = 50
INPUT_HEIGHT = 40
INPUT_HEIGHT_LG = 50

# Window Configuration
WINDOW_DEFAULT_WIDTH = 1280
WINDOW_DEFAULT_HEIGHT = 720
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 700

# Icons (Unicode Emoji)
ICON_DASHBOARD = "📊"
ICON_BILLING = "💰"
ICON_STOCK = "📦"
ICON_NEW_STOCK = "📥"
ICON_SEARCH = "🔍"
ICON_REPORTS = "📈"
ICON_SETTINGS = "⚙️"
ICON_LOGOUT = "🚪"
ICON_USER = "👤"
ICON_LOGO = "💎"

# Metric Card Icons
ICON_SALES = "💰"
ICON_REVENUE = "📈"
ICON_WARNING = "⚠️"
ICON_TRANSACTIONS = "🧾"
ICON_INVENTORY = "📦"

# Category Icons
ICON_SILK = "🌟"
ICON_DESIGNER = "👗"
ICON_COTTON = "🍃"
ICON_ACCESSORIES = "✨"

# Animation Timing (milliseconds)
ANIMATION_FAST = 100
ANIMATION_NORMAL = 300
ANIMATION_SLOW = 500

# File Paths
INVOICES_DIR = "invoices"
LOGO_PATH = "logo.jpg"  # Actual logo file

# Settings Keys
SETTING_SHOP_NAME = "shop_name"
SETTING_SHOP_ADDRESS = "shop_address"
SETTING_SHOP_PHONE = "shop_phone"
SETTING_SHOP_EMAIL = "shop_email"
SETTING_GST_NUMBER = "gst_number"
SETTING_BILL_PREFIX = "bill_prefix"
SETTING_THEME_MODE = "theme_mode"
SETTING_REQUIRE_LOGIN_PASSWORD = "require_login_password"
SETTING_REQUIRE_ADMIN_PIN = "require_admin_pin"
SETTING_PIN_STOCK = "pin_stock"
SETTING_PIN_NEW_STOCK = "pin_new_stock"
SETTING_PIN_BILLS = "pin_bills"
SETTING_PIN_REPORTS = "pin_reports"
SETTING_PIN_SETTINGS = "pin_settings"

# Default Shop Details
DEFAULT_SHOP_NAME = "Shree Ganesha Silk"
DEFAULT_SHOP_ADDRESS = "123 Fashion Street, City, State - 000000"
DEFAULT_SHOP_PHONE = "+91 9876543210"
DEFAULT_SHOP_EMAIL = "info@elitesarees.com"
DEFAULT_GST_NUMBER = ""

# Payment Methods
PAYMENT_METHODS = ["Cash", "Card", "UPI", "Net Banking", "Other"]

# Stock Categories
STOCK_CATEGORIES = [
    "Silk Sarees",
    "Designer Wear",
    "Cotton Collection",
    "Party Wear",
    "Accessories",
    "Blouses",
    "Other"
]

# Saree Types
SAREE_TYPES = [
    "Kanjivaram Silk",
    "Banarasi Silk",
    "Cotton Saree",
    "Georgette Saree",
    "Chiffon Saree",
    "Net Saree",
    "Designer Saree",
    "Printed Saree",
    "Embroidered Saree",
    "Other"
]

# Material Types
MATERIAL_TYPES = [
    "Pure Silk",
    "Art Silk",
    "Cotton",
    "Georgette",
    "Chiffon",
    "Net",
    "Crepe",
    "Satin",
    "Mixed",
    "Other"
]

# Helper Functions
def get_greeting():
    """Get time-appropriate greeting"""
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"

def get_category_icon(category: str) -> str:
    """Get icon for category"""
    category_lower = category.lower()
    if "silk" in category_lower:
        return ICON_SILK
    elif "designer" in category_lower:
        return ICON_DESIGNER
    elif "cotton" in category_lower:
        return ICON_COTTON
    elif "access" in category_lower:
        return ICON_ACCESSORIES
    else:
        return ICON_INVENTORY
