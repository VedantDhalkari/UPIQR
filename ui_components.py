"""
UI Components Library
Reusable premium UI components for the Shree Ganesha Silk system
"""

import customtkinter as ctk
from typing import Optional, Callable
from datetime import datetime
import config


class StatCard(ctk.CTkFrame):
    """Premium metric/statistic card with icon and hover effect"""
    
    def __init__(self, parent, title: str, value: str, subtitle: str, 
                 icon: str, icon_color: str, **kwargs):
        """
        Create a statistic card
        
        Args:
            parent: Parent widget
            title: Card title
            value: Main value to display
            subtitle: Subtitle text
            icon: Icon emoji
            icon_color: Color for icon background
        """
        super().__init__(parent, fg_color=config.COLOR_BG_CARD, 
                        corner_radius=config.RADIUS_LG, **kwargs)
        
        self.configure(border_width=2, border_color=config.COLOR_BORDER, cursor="hand2")
        self.default_border = config.COLOR_BORDER
        self.hover_border = icon_color
        
        # Bind hover events
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        
        # Icon circle
        icon_frame = ctk.CTkFrame(
            self, 
            width=60, 
            height=60, 
            fg_color=icon_color,
            corner_radius=30
        )
        icon_frame.pack(pady=(config.SPACING_LG, config.SPACING_SM), padx=config.SPACING_LG)
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=28)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        title_label.pack(pady=(0, config.SPACING_XS), padx=config.SPACING_LG)
        
        # Value
        value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=config.FONT_SIZE_METRIC, weight="bold"),
            text_color=icon_color
        )
        value_label.pack(pady=config.SPACING_XS, padx=config.SPACING_LG)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_LIGHT
        )
        subtitle_label.pack(pady=(config.SPACING_XS, config.SPACING_LG), padx=config.SPACING_LG)
    
    def _on_hover(self, event):
        """Handle mouse enter"""
        self.configure(border_color=self.hover_border)
    
    def _on_leave(self, event):
        """Handle mouse leave"""
        self.configure(border_color=self.default_border)


class GreetingCard(ctk.CTkFrame):
    """Large greeting card with gradient background and quick actions"""
    
    def __init__(self, parent, username: str, on_new_bill: Callable = None, 
                 on_view_stock: Callable = None, **kwargs):
        """
        Create greeting card
        
        Args:
            parent: Parent widget
            username: User's name
            on_new_bill: Callback for New Bill button
            on_view_stock: Callback for View Stock button
        """
        super().__init__(parent, fg_color=config.COLOR_PRIMARY, 
                        corner_radius=config.RADIUS_LG, **kwargs)
        
        # Content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=config.SPACING_XL, pady=config.SPACING_XL)
        
        # Left side - Greeting
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Greeting
        greeting = config.get_greeting()
        greeting_label = ctk.CTkLabel(
            left_frame,
            text=f"{greeting}, {username}!",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=config.COLOR_TEXT_WHITE
        )
        greeting_label.pack(anchor="w", pady=(0, config.SPACING_SM))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            left_frame,
            text="Here's what's happening with your Shree Ganesha Silktoday",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            text_color=config.COLOR_TEXT_WHITE
        )
        subtitle_label.pack(anchor="w", pady=(0, config.SPACING_MD))
        
        # Date
        date_str = datetime.now().strftime("%A, %d %B %Y")
        date_label = ctk.CTkLabel(
            left_frame,
            text=date_str,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_WHITE
        )
        date_label.pack(anchor="w", pady=(0, config.SPACING_LG))
        
        # Quick action buttons
        buttons_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        buttons_frame.pack(anchor="w")
        
        if on_new_bill:
            new_bill_btn = ctk.CTkButton(
                buttons_frame,
                text="💰 New Bill",
                width=140,
                height=40,
                fg_color=config.COLOR_SUCCESS,
                hover_color="#059669",
                text_color=config.COLOR_TEXT_WHITE,
                font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
                corner_radius=config.RADIUS_MD,
                command=on_new_bill
            )
            new_bill_btn.pack(side="left", padx=(0, config.SPACING_SM))
        
        if on_view_stock:
            view_stock_btn = ctk.CTkButton(
                buttons_frame,
                text="📦 View Stock",
                width=140,
                height=40,
                fg_color=config.COLOR_INFO,
                hover_color="#2563EB",
                text_color=config.COLOR_TEXT_WHITE,
                font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
                corner_radius=config.RADIUS_MD,
                command=on_view_stock
            )
            view_stock_btn.pack(side="left")


class ModernTable(ctk.CTkFrame):
    """Modern table with headers and clean styling"""
    
    def __init__(self, parent, headers: list, rows: list = None, **kwargs):
        """
        Create modern table
        
        Args:
            parent: Parent widget
            headers: List of header strings
            rows: Optional list of rows to add immediately
        """
        super().__init__(parent, fg_color=config.COLOR_BG_CARD, 
                        corner_radius=config.RADIUS_LG, **kwargs)
        
        self.configure(border_width=1, border_color=config.COLOR_BORDER)
        
        # Header frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header_frame.pack(fill="x", padx=config.SPACING_LG, pady=(config.SPACING_LG, config.SPACING_SM))
        header_frame.pack_propagate(False)
        
        # Column weights for equal distribution
        for i in range(len(headers)):
            header_frame.grid_columnconfigure(i, weight=1)
        
        # Create headers
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
                text_color=config.COLOR_TEXT_SECONDARY
            )
            label.grid(row=0, column=i, sticky="w", padx=config.SPACING_SM)
        
        # Scrollable content frame
        self.content_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=config.COLOR_PRIMARY,
            scrollbar_button_hover_color=config.COLOR_PRIMARY_LIGHT
        )
        self.content_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, 
                               pady=(0, config.SPACING_LG))
        
        # Configure grid columns
        for i in range(len(headers)):
            self.content_frame.grid_columnconfigure(i, weight=1)
        
        self.row_count = 0
        self.num_columns = len(headers)
        
        # Add initial rows if provided
        if rows:
            for row in rows:
                self.add_row(row)
    
    def add_row(self, data: list, amount_color: str = None):
        """
        Add a row to the table
        
        Args:
            data: List of values for each column
            amount_color: Optional color for amount column
        """
        # Alternate row background
        bg_color = config.COLOR_BG_HOVER if self.row_count % 2 == 0 else "transparent"
        
        row_frame = ctk.CTkFrame(self.content_frame, fg_color=bg_color, height=40)
        row_frame.grid(row=self.row_count, column=0, columnspan=self.num_columns, 
                      sticky="ew", pady=1)
        row_frame.grid_propagate(False)
        
        for i in range(self.num_columns):
            row_frame.grid_columnconfigure(i, weight=1)
        
        for i, value in enumerate(data):
            text_color = config.COLOR_TEXT_PRIMARY
            
            # Apply special color to amount column if specified
            if amount_color and i == 2:  # Assuming column 2 is amount
                text_color = amount_color
            
            label = ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
                text_color=text_color
            )
            label.grid(row=0, column=i, sticky="w", padx=config.SPACING_SM)
        
        self.row_count += 1
    
    def clear_rows(self):
        """Clear all rows from table"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.row_count = 0


class StatusBadge(ctk.CTkLabel):
    """Colored status badge"""
    
    def __init__(self, parent, text: str, status_type: str = "success", **kwargs):
        """
        Create status badge
        
        Args:
            parent: Parent widget
            text: Badge text
            status_type: "success", "warning", "danger", or "info"
        """
        color_map = {
            "success": config.COLOR_SUCCESS,
            "warning": config.COLOR_WARNING,
            "danger": config.COLOR_DANGER,
            "info": config.COLOR_INFO
        }
        
        bg_color = color_map.get(status_type, config.COLOR_INFO)
        
        super().__init__(
            parent,
            text=text,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
            text_color=config.COLOR_TEXT_WHITE,
            fg_color=bg_color,
            corner_radius=12,
            **kwargs
        )
        self.configure(padx=12, pady=4)


class AnimatedButton(ctk.CTkButton):
    """Button with enhanced hover effects"""
    
    def __init__(self, parent, **kwargs):
        """Create animated button"""
        # Set defaults
        if 'corner_radius' not in kwargs:
            kwargs['corner_radius'] = config.RADIUS_MD
        if 'height' not in kwargs:
            kwargs['height'] = config.BUTTON_HEIGHT
        if 'font' not in kwargs:
            kwargs['font'] = ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold")
        
        super().__init__(parent, **kwargs)
        self.configure(cursor="hand2")


class SidebarButton(ctk.CTkButton):
    """Sidebar navigation button with icon"""
    
    def __init__(self, parent, text: str, icon: str, command: Callable, **kwargs):
        """
        Create sidebar button
        
        Args:
            parent: Parent widget
            text: Button text
            icon: Icon emoji
            command: Click callback
        """
        # Set defaults if not provided
        width = kwargs.pop('width', 220)
        height = kwargs.pop('height', 45)
        fg_color = kwargs.pop('fg_color', "transparent")
        text_color = kwargs.pop('text_color', config.COLOR_TEXT_PRIMARY)
        
        super().__init__(
            parent,
            text=f"{icon}  {text}",
            width=width,
            height=height,
            font=ctk.CTkFont(size=13),
            fg_color=fg_color,
            text_color=text_color,
            hover_color=config.COLOR_BG_HOVER,
            anchor="w",
            corner_radius=config.RADIUS_MD,
            command=command,
            **kwargs
        )
        self.configure(cursor="hand2")
        self.default_fg = "transparent"
        self.active_fg = config.COLOR_PRIMARY
    
    def set_active(self, active: bool):
        """Set button active state"""
        if active:
            self.configure(
                fg_color=self.active_fg,
                text_color=config.COLOR_TEXT_WHITE
            )
        else:
            self.configure(
                fg_color=self.default_fg,
                text_color=config.COLOR_TEXT_PRIMARY
            )


class SearchBar(ctk.CTkFrame):
    """Modern search bar with icon"""
    
    def __init__(self, parent, placeholder: str = "Search...", 
                 on_search: Callable = None, **kwargs):
        """
        Create search bar
        
        Args:
            parent: Parent widget
            placeholder: Placeholder text
            on_search: Search callback function
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=config.INPUT_HEIGHT,
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            border_color=config.COLOR_BORDER,
            border_width=2
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, config.SPACING_SM))
        
        if on_search:
            search_btn = ctk.CTkButton(
                self,
                text="🔍 Search",
                width=120,
                height=config.INPUT_HEIGHT,
                fg_color=config.COLOR_PRIMARY,
                hover_color=config.COLOR_PRIMARY_LIGHT,
                font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
                command=lambda: on_search(self.entry.get())
            )
            search_btn.pack(side="left")
            
            # Bind Enter key
            self.entry.bind("<Return>", lambda e: on_search(self.entry.get()))
    
    def get(self) -> str:
        """Get search text"""
        return self.entry.get()
    
    def clear(self):
        """Clear search text"""
        self.entry.delete(0, "end")


class PageHeader(ctk.CTkFrame):
    """Header with title and live clock"""
    
    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_1, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        self.title_label.pack(side="left", anchor="w")
        
        # Clock
        self.clock_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        self.clock_label.pack(side="right", anchor="e")
        
        self._update_clock()
    
    def set_title(self, title: str):
        """Update header title"""
        self.title_label.configure(text=title)
        
    def _update_clock(self):
        """Update clock label"""
        now = datetime.now().strftime("%A, %d %b %Y | %H:%M:%S")
        self.clock_label.configure(text=now)
        self.after(1000, self._update_clock)
