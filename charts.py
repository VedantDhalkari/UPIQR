"""
Charts Module
Data visualization components using Tkinter Canvas for earnings and analytics
(Removed matplotlib to eliminate 50MB+ dependency and numpy crashes)
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Tuple
import config


class EarningsBarChart(ctk.CTkFrame):
    """Bar chart for earnings visualization using native drawing"""
    
    def __init__(self, parent, data: List[Tuple], period: str = "Today", **kwargs):
        super().__init__(parent, fg_color=config.COLOR_BG_CARD, 
                        corner_radius=config.RADIUS_LG, **kwargs)
        
        self.configure(border_width=1, border_color=config.COLOR_BORDER)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Earnings",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_label.pack(side="left")
        
        period_label = ctk.CTkLabel(
            header_frame,
            text=period,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        period_label.pack(side="right")
        
        # Chart frame
        self.chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, pady=(0, config.SPACING_LG))
        
        self._create_chart(self.chart_frame, data)
    
    def _create_chart(self, parent, data: List[Tuple]):
        """Create the bar chart using Tkinter Canvas"""
        if not data or len(data) == 0:
            lbl = ctk.CTkLabel(parent, text="No data available", text_color=config.COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=14))
            lbl.pack(expand=True)
            return
            
        labels = [str(item[0]) for item in data]
        values = [float(item[1] if item[1] else 0) for item in data]
        max_val = max(values) if values else 0
        if max_val == 0:
            max_val = 1
            
        canvas = tk.Canvas(parent, bg=config.COLOR_BG_CARD, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        def draw(event=None):
            canvas.delete("all")
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                return
                
            padding_left = 60
            padding_bottom = 30
            padding_top = 20
            padding_right = 20
            
            graph_width = width - padding_left - padding_right
            graph_height = height - padding_top - padding_bottom
            
            # Draw axes
            canvas.create_line(padding_left, padding_top, padding_left, height - padding_bottom, fill=config.COLOR_BORDER)
            canvas.create_line(padding_left, height - padding_bottom, width - padding_right, height - padding_bottom, fill=config.COLOR_BORDER)
            
            # Y-axis labels
            y_ticks = 4
            for i in range(y_ticks + 1):
                y = height - padding_bottom - (i * graph_height / y_ticks)
                val = (max_val / y_ticks) * i
                canvas.create_line(padding_left - 5, y, width - padding_right, y, fill=config.COLOR_BORDER, dash=(2, 4))
                canvas.create_text(padding_left - 10, y, text=f"₹{int(val):,}", anchor="e", fill=config.COLOR_TEXT_SECONDARY, font=("Arial", 9))
                
            n = len(values)
            bar_spacing = graph_width / (n * 1.5 + 0.5)
            bar_width = bar_spacing
            
            for i, (val, lbl) in enumerate(zip(values, labels)):
                x0 = padding_left + bar_spacing * 0.5 + i * 1.5 * bar_spacing
                x1 = x0 + bar_width
                
                bar_h = (val / max_val) * graph_height
                y0 = height - padding_bottom - bar_h
                y1 = height - padding_bottom
                
                color = config.COLOR_PRIMARY if i % 2 == 0 else config.COLOR_PRIMARY_LIGHT
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=config.COLOR_PRIMARY_DARK)
                
                # Label
                # Try to fit label if too many
                if n < 15 or i % 2 == 0:
                    canvas.create_text(x0 + bar_width/2, height - padding_bottom + 10, text=lbl, anchor="n", fill=config.COLOR_TEXT_SECONDARY, font=("Arial", 9))
                    
        canvas.bind("<Configure>", draw)


class CategoryList(ctk.CTkFrame):
    """List of top categories with icons and amounts"""
    
    def __init__(self, parent, categories: List[Tuple], **kwargs):
        super().__init__(parent, fg_color=config.COLOR_BG_CARD, corner_radius=config.RADIUS_LG, **kwargs)
        self.configure(border_width=1, border_color=config.COLOR_BORDER)
        
        header_label = ctk.CTkLabel(
            self, text="Top Categories", font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        header_label.pack(pady=config.SPACING_LG, padx=config.SPACING_LG, anchor="w")
        
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, pady=(0, config.SPACING_LG))
        
        colors = [config.COLOR_PRIMARY, config.COLOR_SUCCESS, config.COLOR_WARNING, config.COLOR_INFO, config.COLOR_SECONDARY]
        
        if not categories or len(categories) == 0:
            no_data_label = ctk.CTkLabel(
                content_frame, text="No category data available", font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
                text_color=config.COLOR_TEXT_SECONDARY
            )
            no_data_label.pack(pady=config.SPACING_XL)
        else:
            for idx, (category, amount) in enumerate(categories):
                color = colors[idx % len(colors)]
                self._create_category_item(content_frame, category, amount, color)
    
    def _create_category_item(self, parent, category: str, amount: float, color: str):
        item_frame = ctk.CTkFrame(parent, fg_color="transparent", height=50)
        item_frame.pack(fill="x", pady=config.SPACING_XS)
        item_frame.pack_propagate(False)
        
        icon = config.get_category_icon(category)
        icon_frame = ctk.CTkFrame(item_frame, width=40, height=40, fg_color=color, corner_radius=20)
        icon_frame.pack(side="left", padx=(0, config.SPACING_SM))
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(icon_frame, text=icon, font=ctk.CTkFont(size=18))
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        category_label = ctk.CTkLabel(
            info_frame, text=category or "Other", font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"), text_color=config.COLOR_TEXT_PRIMARY
        )
        category_label.pack(anchor="w")
        
        amount_label = ctk.CTkLabel(
            info_frame, text=f"₹{amount:,.2f}", font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"), text_color=color
        )
        amount_label.pack(anchor="w")


def create_empty_chart_placeholder(parent) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(parent, fg_color=config.COLOR_BG_CARD, corner_radius=config.RADIUS_LG)
    frame.configure(border_width=1, border_color=config.COLOR_BORDER)
    
    label = ctk.CTkLabel(
        frame, text="📊\n\nNo chart data available", font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
        text_color=config.COLOR_TEXT_SECONDARY
    )
    label.pack(expand=True, pady=config.SPACING_XL)
    return frame
