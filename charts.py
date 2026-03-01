"""
Charts Module
Data visualization components using matplotlib for earnings and analytics
"""

import matplotlib
matplotlib.use('TkAgg')  # Use Tkinter interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import customtkinter as ctk
from typing import List, Tuple
import config


class EarningsBarChart(ctk.CTkFrame):
    """Bar chart for earnings visualization"""
    
    def __init__(self, parent, data: List[Tuple], period: str = "Today", **kwargs):
        """
        Create earnings bar chart
        
        Args:
            parent: Parent widget
            data: List of (label, value) tuples
            period: Period label ("Today", "This Week", "This Month")
        """
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
        
        # Period selector (you can extend this with clickable buttons)
        period_label = ctk.CTkLabel(
            header_frame,
            text=period,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        period_label.pack(side="right")
        
        # Chart frame
        chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, 
                        pady=(0, config.SPACING_LG))
        
        # Create matplotlib figure
        self._create_chart(chart_frame, data)
    
    def _create_chart(self, parent, data: List[Tuple]):
        """Create the bar chart"""
        # Create figure with transparent background
        fig = Figure(figsize=(8, 4), facecolor=config.COLOR_BG_CARD, dpi=100)
        ax = fig.add_subplot(111)
        
        if not data or len(data) == 0:
            # No data - show message
            ax.text(0.5, 0.5, 'No data available', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   fontsize=14,
                   color=config.COLOR_TEXT_SECONDARY)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            # Extract labels and values
            labels = [item[0] for item in data]
            values = [item[1] if item[1] else 0 for item in data]
            
            # Create bars with purple gradient
            bars = ax.bar(range(len(labels)), values, 
                         color=config.COLOR_PRIMARY,
                         alpha=0.8,
                         edgecolor=config.COLOR_PRIMARY_DARK,
                         linewidth=1)
            
            # Gradient effect on bars
            for i, bar in enumerate(bars):
                # Alternate colors for visual interest
                if i % 2 == 0:
                    bar.set_color(config.COLOR_PRIMARY)
                else:
                    bar.set_color(config.COLOR_PRIMARY_LIGHT)
            
            # Customize axes
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=0, fontsize=9, 
                              color=config.COLOR_TEXT_SECONDARY)
            ax.set_ylabel('Amount (₹)', fontsize=10, 
                         color=config.COLOR_TEXT_SECONDARY)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, p: f'₹{int(x):,}'
            ))
            
            # Grid
            ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
            ax.set_axisbelow(True)
            
            # Remove top and right spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(config.COLOR_BORDER)
            ax.spines['bottom'].set_color(config.COLOR_BORDER)
            
            # Tick colors
            ax.tick_params(colors=config.COLOR_TEXT_SECONDARY, labelsize=9)
        
        # Tight layout
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


class CategoryList(ctk.CTkFrame):
    """List of top categories with icons and amounts"""
    
    def __init__(self, parent, categories: List[Tuple], **kwargs):
        """
        Create category list
        
        Args:
            parent: Parent widget
            categories: List of (category_name, amount) tuples
        """
        super().__init__(parent, fg_color=config.COLOR_BG_CARD, 
                        corner_radius=config.RADIUS_LG, **kwargs)
        
        self.configure(border_width=1, border_color=config.COLOR_BORDER)
        
        # Header
        header_label = ctk.CTkLabel(
            self,
            text="Top Categories",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        header_label.pack(pady=config.SPACING_LG, padx=config.SPACING_LG, anchor="w")
        
        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, 
                          pady=(0, config.SPACING_LG))
        
        # Category colors
        colors = [
            config.COLOR_PRIMARY,
            config.COLOR_SUCCESS,
            config.COLOR_WARNING,
            config.COLOR_INFO,
            config.COLOR_SECONDARY
        ]
        
        if not categories or len(categories) == 0:
            no_data_label = ctk.CTkLabel(
                content_frame,
                text="No category data available",
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
                text_color=config.COLOR_TEXT_SECONDARY
            )
            no_data_label.pack(pady=config.SPACING_XL)
        else:
            for idx, (category, amount) in enumerate(categories):
                color = colors[idx % len(colors)]
                self._create_category_item(content_frame, category, amount, color)
    
    def _create_category_item(self, parent, category: str, amount: float, color: str):
        """Create a category item"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent", height=50)
        item_frame.pack(fill="x", pady=config.SPACING_XS)
        item_frame.pack_propagate(False)
        
        # Icon circle
        icon = config.get_category_icon(category)
        icon_frame = ctk.CTkFrame(
            item_frame,
            width=40,
            height=40,
            fg_color=color,
            corner_radius=20
        )
        icon_frame.pack(side="left", padx=(0, config.SPACING_SM))
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=18)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Category info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        category_label = ctk.CTkLabel(
            info_frame,
            text=category or "Other",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        category_label.pack(anchor="w")
        
        amount_label = ctk.CTkLabel(
            info_frame,
            text=f"₹{amount:,.2f}",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=color
        )
        amount_label.pack(anchor="w")


def create_empty_chart_placeholder(parent) -> ctk.CTkFrame:
    """Create a placeholder for when chart data is not available"""
    frame = ctk.CTkFrame(parent, fg_color=config.COLOR_BG_CARD, 
                        corner_radius=config.RADIUS_LG)
    frame.configure(border_width=1, border_color=config.COLOR_BORDER)
    
    label = ctk.CTkLabel(
        frame,
        text="📊\n\nNo chart data available",
        font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
        text_color=config.COLOR_TEXT_SECONDARY
    )
    label.pack(expand=True, pady=config.SPACING_XL)
    
    return frame
