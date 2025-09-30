import tkinter as tk
from tkinter import ttk, filedialog
import os
import threading
import subprocess
import sys
from pathlib import Path

# Import the restool functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from restool import dump_res_to_folder


class ModernButton(tk.Canvas):
    """Custom modern button with hover effects"""
    def __init__(self, parent, text, command, **kwargs):
        self.bg_color = kwargs.pop('bg_color', '#3b82f6')
        self.hover_color = kwargs.pop('hover_color', '#2563eb')
        self.text_color = kwargs.pop('fg_color', '#ffffff')
        self.height = kwargs.pop('height', 50)
        width = kwargs.pop('width', 300)
        
        super().__init__(parent, height=self.height, width=width, highlightthickness=0, **kwargs)
        
        self.command = command
        self.text = text
        self.is_hovered = False
        self.width = width
        
        self.rect = self.create_rounded_rect(0, 0, width, self.height, 12, fill=self.bg_color, outline='')
        self.text_id = self.create_text(width//2, self.height//2, text=text, fill=self.text_color, 
                                        font=('Segoe UI', 11, 'bold'))
        
        self.bind('<Button-1>', lambda e: self.command())
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        self.config(cursor='hand2')
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_color)
        self.is_hovered = True
    
    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.bg_color)
        self.is_hovered = False


class ModernMessageBox:
    """Custom modern message box dialog"""
    @staticmethod
    def show(parent, title, message, msg_type="info"):
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("600x300")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        colors = {
            'bg': '#0f172a',
            'surface': '#1e293b',
            'text': '#f1f5f9',
            'text_muted': '#94a3b8',
            'primary': '#3b82f6',
            'success': '#10b981',
            'error': '#ef4444'
        }
        
        type_config = {
            'info': {'icon': 'i', 'color': colors['primary']},
            'success': {'icon': '✓', 'color': colors['success']},
            'error': {'icon': '✗', 'color': colors['error']}
        }
        
        config = type_config.get(msg_type, type_config['info'])
        
        dialog.configure(bg=colors['bg'])
        
        main_frame = tk.Frame(dialog, bg=colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(main_frame, bg=colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        icon_canvas = tk.Canvas(header_frame, width=50, height=50, bg=colors['bg'], 
                               highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 15))
        icon_canvas.create_rounded_rectangle(0, 0, 50, 50, radius=25, 
                                            fill=config['color'], outline='')
        icon_canvas.create_text(25, 25, text=config['icon'], 
                               font=('Segoe UI', 20), fill='white')
        
        title_label = tk.Label(
            header_frame,
            text=title,
            font=("Segoe UI", 16, "bold"),
            bg=colors['bg'],
            fg=colors['text'],
            anchor='w'
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        message_label = tk.Label(
            main_frame,
            text=message,
            font=("Segoe UI", 11),
            bg=colors['bg'],
            fg=colors['text_muted'],
            wraplength=400,
            justify=tk.LEFT,
            anchor='w'
        )
        message_label.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        button_frame = tk.Frame(main_frame, bg=colors['bg'])
        button_frame.pack(side=tk.BOTTOM)
        
        def close_dialog():
            dialog.destroy()
        
        ok_button = tk.Button(
            button_frame,
            text="OK",
            command=close_dialog,
            bg=config['color'],
            fg='white',
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=40,
            pady=10,
            borderwidth=0
        )
        ok_button.pack()
        
        def on_enter(e):
            if msg_type == 'success':
                ok_button.config(bg='#059669')
            elif msg_type == 'error':
                ok_button.config(bg='#dc2626')
            else:
                ok_button.config(bg='#2563eb')
        
        def on_leave(e):
            ok_button.config(bg=config['color'])
        
        ok_button.bind('<Enter>', on_enter)
        ok_button.bind('<Leave>', on_leave)
        
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        dialog.bind('<Escape>', lambda e: close_dialog())
        dialog.bind('<Return>', lambda e: close_dialog())
        
        dialog.focus_set()
        dialog.wait_window()


class UnifiedToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Battalion Wars Unified Tool")
        self.root.geometry("1600x1000")
        self.root.resizable(False, False)
        
        # Determine the application directory correctly for both frozen and unfrozen states
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set window icon
        icon_path = os.path.join(self.app_dir, "BWUT.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"Warning: Could not set window icon: {e}")
        
        # Create batch output folder if it doesn't exist
        self.batch_output_folder = os.path.join(self.app_dir, "converted_batch_res_files")
        self.batch_res_bw1 = os.path.join(self.batch_output_folder, "bw1")
        self.batch_res_bw2 = os.path.join(self.batch_output_folder, "bw2")
        try:
            os.makedirs(self.batch_res_bw1, exist_ok=True)
            os.makedirs(self.batch_res_bw2, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create batch output folders: {e}")
        
        # Create repacked output folders
        self.repacked_output_folder = os.path.join(self.app_dir, "repacked_res_files")
        self.repacked_bw1 = os.path.join(self.repacked_output_folder, "bw1")
        self.repacked_bw2 = os.path.join(self.repacked_output_folder, "bw2")
        try:
            os.makedirs(self.repacked_bw1, exist_ok=True)
            os.makedirs(self.repacked_bw2, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create repacked output folders: {e}")
        
        # Create single file output folders (converted_res_files/bw1 and bw2)
        self.single_res_output = os.path.join(self.app_dir, "converted_res_files")
        self.single_res_bw1 = os.path.join(self.single_res_output, "bw1")
        self.single_res_bw2 = os.path.join(self.single_res_output, "bw2")
        try:
            os.makedirs(self.single_res_bw1, exist_ok=True)
            os.makedirs(self.single_res_bw2, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create single res output folders: {e}")
        
        self.colors = {
            'bg': '#0f172a',
            'surface': '#1e293b',
            'surface_light': '#334155',
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'success': '#10b981',
            'text': '#f1f5f9',
            'text_muted': '#94a3b8',
            'border': '#475569',
            'purple': '#8b5cf6',
            'purple_hover': '#7c3aed'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.layout('Modern.Horizontal.TProgressbar', 
                    [('Horizontal.Progressbar.trough',
                      {'children': [('Horizontal.Progressbar.pbar',
                                    {'side': 'left', 'sticky': 'ns'})],
                       'sticky': 'nswe'})])
        
        style.configure("Modern.Horizontal.TProgressbar",
                       troughcolor=self.colors['surface_light'],
                       bordercolor=self.colors['surface'],
                       background=self.colors['success'],
                       lightcolor=self.colors['success'],
                       darkcolor=self.colors['success'],
                       borderwidth=0,
                       thickness=8,
                       troughrelief='flat')
        
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       padding=[20, 10],
                       borderwidth=0)
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', self.colors['text'])])
        
        main_container = tk.Frame(root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        header_frame = tk.Frame(main_container, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        icon_canvas = tk.Canvas(header_frame, width=50, height=50, bg=self.colors['bg'], 
                                highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 15))
        icon_canvas.create_rounded_rectangle(5, 5, 45, 45, radius=12, 
                                            fill=self.colors['primary'], outline='')
        icon_canvas.create_text(25, 25, text="BW", fill='white', 
                               font=('Segoe UI', 18, 'bold'))
        
        title_label = tk.Label(
            header_frame,
            text="Battalion Wars Unified Tool",
            font=("Segoe UI", 26, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack(side=tk.LEFT)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.res_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.texture_tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        self.notebook.add(self.res_tab, text='  RES Converter  ')
        self.notebook.add(self.texture_tab, text='  Texture Converter  ')
        
        self.setup_res_tab()
        self.setup_texture_tab()
        
    def setup_res_tab(self):
        """Setup the RES converter tab"""
        # Top row - Extract cards
        top_cards_container = tk.Frame(self.res_tab, bg=self.colors['bg'])
        top_cards_container.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        left_card_frame = tk.Frame(top_cards_container, bg=self.colors['bg'])
        left_card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_card_frame = tk.Frame(top_cards_container, bg=self.colors['bg'])
        right_card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_res_card(
            left_card_frame,
            "Convert Single File",
            "Extract a single .res or .res.gz file",
            self.select_single_res,
            is_single=True
        )
        
        self.create_res_card(
            right_card_frame,
            "Batch Convert",
            "Search folders and convert all .res files found",
            self.select_batch_res,
            is_single=False
        )
        
        # Bottom row - Repack cards
        bottom_cards_container = tk.Frame(self.res_tab, bg=self.colors['bg'])
        bottom_cards_container.pack(fill=tk.X, pady=(10, 20), padx=20)
        
        repack_left_card = tk.Frame(bottom_cards_container, bg=self.colors['bg'])
        repack_left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        repack_right_card = tk.Frame(bottom_cards_container, bg=self.colors['bg'])
        repack_right_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_res_card(
            repack_left_card,
            "Repack Single Folder",
            "Pack an extracted folder back into a .res file",
            self.select_single_repack,
            is_single=True,
            button_color=self.colors['success'],
            button_text="Select Folder"
        )
        
        self.create_res_card(
            repack_right_card,
            "Batch Repack",
            "Pack multiple extracted folders back into .res files",
            self.select_batch_repack,
            is_single=False,
            button_color=self.colors['success']
        )
        
        progress_container = tk.Frame(self.res_tab, bg=self.colors['surface'], 
                                     relief=tk.FLAT, bd=0)
        progress_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        progress_inner = tk.Frame(progress_container, bg=self.colors['surface'])
        progress_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        progress_content = tk.Frame(progress_inner, bg=self.colors['surface'])
        progress_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        status_header = tk.Frame(progress_content, bg=self.colors['surface'])
        status_header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            status_header,
            text="Status",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['surface'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        self.res_progress_label = tk.Label(
            status_header,
            text="Ready",
            font=("Segoe UI", 10),
            bg=self.colors['surface'],
            fg=self.colors['text_muted']
        )
        self.res_progress_label.pack(side=tk.RIGHT)
        
        self.res_progress_bar = ttk.Progressbar(
            progress_content,
            style="Modern.Horizontal.TProgressbar",
            mode='determinate',
            length=400,
            maximum=100
        )
        self.res_progress_bar.pack(fill=tk.X, pady=(0, 20))
        
        log_label = tk.Label(
            progress_content,
            text="Activity Log",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            anchor='w'
        )
        log_label.pack(fill=tk.X, pady=(0, 8))
        
        log_frame = tk.Frame(progress_content, bg=self.colors['surface_light'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(log_frame, bg=self.colors['surface_light'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.res_log_text = tk.Text(
            log_frame,
            height=10,
            bg=self.colors['surface_light'],
            fg=self.colors['text'],
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            borderwidth=0,
            selectbackground=self.colors['primary']
        )
        self.res_log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.res_log_text.yview)
    
    def create_res_card(self, parent, title, description, command, is_single=False, button_color=None, button_text=None):
        """Create a modern card-style section for RES converter"""
        card_frame = tk.Frame(parent, bg=self.colors['surface'], relief=tk.FLAT)
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        card_inner = tk.Frame(card_frame, bg=self.colors['surface'])
        card_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        card_content = tk.Frame(card_inner, bg=self.colors['surface'])
        card_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        title_label = tk.Label(
            card_content,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            anchor='w'
        )
        title_label.pack(fill=tk.X, pady=(0, 5))
        
        desc_label = tk.Label(
            card_content,
            text=description,
            font=("Segoe UI", 10),
            bg=self.colors['surface'],
            fg=self.colors['text_muted'],
            anchor='w',
            wraplength=350
        )
        desc_label.pack(fill=tk.X, pady=(0, 15))
        
        btn_frame = tk.Frame(card_content, bg=self.colors['surface'])
        btn_frame.pack(fill=tk.X)
        
        if button_color is None:
            bg_color = self.colors['primary']
            hover_color = self.colors['primary_hover']
        else:
            bg_color = button_color
            hover_color = '#059669' if button_color == self.colors['success'] else self.colors['primary_hover']
        
        if button_text is None:
            button_text = f"Select {'File' if is_single else 'Folder'}"
        
        btn = ModernButton(
            btn_frame,
            text=button_text,
            command=command,
            bg_color=bg_color,
            hover_color=hover_color,
            fg_color='white',
            bg=self.colors['surface'],
            width=300
        )
        btn.pack(anchor='w')
        
        if is_single:
            self.single_res_label = tk.Label(
                card_content,
                text="",
                font=("Segoe UI", 9),
                bg=self.colors['surface'],
                fg=self.colors['text_muted'],
                anchor='w',
                wraplength=350
            )
            self.single_res_label.pack(fill=tk.X, pady=(10, 0))
    
    def setup_texture_tab(self):
        """Setup the texture converter tab with 8 cards in 4x2 layout (4 columns, 2 rows)"""
        # Main cards container
        cards_container = tk.Frame(self.texture_tab, bg=self.colors['bg'])
        cards_container.pack(fill=tk.X, pady=(20, 20), padx=20)
        
        # Top row - 4 cards
        top_row = tk.Frame(cards_container, bg=self.colors['bg'])
        top_row.pack(fill=tk.X, pady=(0, 10))
        
        # Top row cards
        top_col1 = tk.Frame(top_row, bg=self.colors['bg'])
        top_col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        top_col2 = tk.Frame(top_row, bg=self.colors['bg'])
        top_col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        top_col3 = tk.Frame(top_row, bg=self.colors['bg'])
        top_col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        top_col4 = tk.Frame(top_row, bg=self.colors['bg'])
        top_col4.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # BW1 Cards - Top Row
        self.create_texture_card(
            top_col1,
            "BW1: Texture to PNG",
            "Convert single BW1 texture file to PNG",
            lambda: self.convert_texture_direct("bw1", "to_png", False),
            self.colors['primary'],
            self.colors['primary_hover'],
            is_batch=False
        )
        
        self.create_texture_card(
            top_col2,
            "BW1: PNG to Texture",
            "Convert single PNG to BW1 texture",
            lambda: self.convert_texture_direct("bw1", "to_texture", False),
            self.colors['primary'],
            self.colors['primary_hover'],
            is_batch=False
        )
        
        # BW2 Cards - Top Row
        self.create_texture_card(
            top_col3,
            "BW2: Texture to PNG",
            "Convert single BW2 texture file to PNG",
            lambda: self.convert_texture_direct("bw2", "to_png", False),
            self.colors['purple'],
            self.colors['purple_hover'],
            is_batch=False
        )
        
        self.create_texture_card(
            top_col4,
            "BW2: PNG to Texture",
            "Convert single PNG to BW2 texture",
            lambda: self.convert_texture_direct("bw2", "to_texture", False),
            self.colors['purple'],
            self.colors['purple_hover'],
            is_batch=False
        )
        
        # Bottom row - 4 cards
        bottom_row = tk.Frame(cards_container, bg=self.colors['bg'])
        bottom_row.pack(fill=tk.X)
        
        # Bottom row cards
        bottom_col1 = tk.Frame(bottom_row, bg=self.colors['bg'])
        bottom_col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        bottom_col2 = tk.Frame(bottom_row, bg=self.colors['bg'])
        bottom_col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        bottom_col3 = tk.Frame(bottom_row, bg=self.colors['bg'])
        bottom_col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        bottom_col4 = tk.Frame(bottom_row, bg=self.colors['bg'])
        bottom_col4.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # BW1 Batch Cards - Bottom Row
        self.create_texture_card(
            bottom_col1,
            "BW1: Batch Texture to PNG",
            "Convert multiple BW1 textures to PNG",
            lambda: self.convert_texture_batch("bw1", "to_png"),
            self.colors['primary'],
            self.colors['primary_hover'],
            is_batch=True
        )
        
        self.create_texture_card(
            bottom_col2,
            "BW1: Batch PNG to Texture",
            "Convert multiple PNGs to BW1 textures",
            lambda: self.convert_texture_batch("bw1", "to_texture"),
            self.colors['primary'],
            self.colors['primary_hover'],
            is_batch=True
        )
        
        # BW2 Batch Cards - Bottom Row
        self.create_texture_card(
            bottom_col3,
            "BW2: Batch Texture to PNG",
            "Convert multiple BW2 textures to PNG",
            lambda: self.convert_texture_batch("bw2", "to_png"),
            self.colors['purple'],
            self.colors['purple_hover'],
            is_batch=True
        )
        
        self.create_texture_card(
            bottom_col4,
            "BW2: Batch PNG to Texture",
            "Convert multiple PNGs to BW2 textures",
            lambda: self.convert_texture_batch("bw2", "to_texture"),
            self.colors['purple'],
            self.colors['purple_hover'],
            is_batch=True
        )
        
        # Progress section (shared for all texture conversions)
        progress_container = tk.Frame(self.texture_tab, bg=self.colors['surface'], 
                                     relief=tk.FLAT, bd=0)
        progress_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        progress_inner = tk.Frame(progress_container, bg=self.colors['surface'])
        progress_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        progress_content = tk.Frame(progress_inner, bg=self.colors['surface'])
        progress_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        status_header = tk.Frame(progress_content, bg=self.colors['surface'])
        status_header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            status_header,
            text="Status",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['surface'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        self.texture_progress_label = tk.Label(
            status_header,
            text="Ready",
            font=("Segoe UI", 10),
            bg=self.colors['surface'],
            fg=self.colors['text_muted']
        )
        self.texture_progress_label.pack(side=tk.RIGHT)
        
        self.texture_progress_bar = ttk.Progressbar(
            progress_content,
            style="Modern.Horizontal.TProgressbar",
            mode='determinate',
            length=400,
            maximum=100
        )
        self.texture_progress_bar.pack(fill=tk.X, pady=(0, 20))
        
        log_label = tk.Label(
            progress_content,
            text="Activity Log",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            anchor='w'
        )
        log_label.pack(fill=tk.X, pady=(0, 8))
        
        log_frame = tk.Frame(progress_content, bg=self.colors['surface_light'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(log_frame, bg=self.colors['surface_light'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.texture_log_text = tk.Text(
            log_frame,
            height=10,
            bg=self.colors['surface_light'],
            fg=self.colors['text'],
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            borderwidth=0,
            selectbackground=self.colors['primary']
        )
        self.texture_log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.texture_log_text.yview)
    
    def create_texture_card(self, parent, title, description, command, bg_color, hover_color, is_batch=False):
        """Create a modern card-style section for texture converter"""
        card_frame = tk.Frame(parent, bg=self.colors['surface'], relief=tk.FLAT)
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        card_inner = tk.Frame(card_frame, bg=self.colors['surface'])
        card_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        card_content = tk.Frame(card_inner, bg=self.colors['surface'])
        card_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        title_label = tk.Label(
            card_content,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            anchor='w'
        )
        title_label.pack(fill=tk.X, pady=(0, 5))
        
        desc_label = tk.Label(
            card_content,
            text=description,
            font=("Segoe UI", 10),
            bg=self.colors['surface'],
            fg=self.colors['text_muted'],
            anchor='w',
            wraplength=250
        )
        desc_label.pack(fill=tk.X, pady=(0, 15))
        
        btn_frame = tk.Frame(card_content, bg=self.colors['surface'])
        btn_frame.pack(fill=tk.X)
        
        button_text = "Select Folder" if is_batch else "Select File"
        
        btn = ModernButton(
            btn_frame,
            text=button_text,
            command=command,
            bg_color=bg_color,
            hover_color=hover_color,
            fg_color='white',
            bg=self.colors['surface'],
            width=240
        )
        btn.pack(anchor='w')
    
    def texture_log(self, message):
        """Log message to texture tab"""
        self.texture_log_text.config(state=tk.NORMAL)
        self.texture_log_text.insert(tk.END, message + "\n")
        self.texture_log_text.see(tk.END)
        self.texture_log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def reset_texture_ui(self):
        """Reset the texture UI to fresh state"""
        self.texture_progress_bar['value'] = 0
        self.texture_progress_label.config(text="Ready", fg=self.colors['text_muted'])
        self.texture_log_text.config(state=tk.NORMAL)
        self.texture_log_text.delete(1.0, tk.END)
        self.texture_log_text.config(state=tk.DISABLED)
    
    def convert_texture_direct(self, game_version, direction, is_batch=False):
        """Convert single texture file using convert_bw1.bat or convert_bw2.bat"""
        self.reset_texture_ui()
        
        if direction == "to_png":
            filetypes = [("Texture files", "*.texture"), ("All files", "*.*")]
            file_desc = "texture file"
        else:
            filetypes = [("PNG files", "*.png"), ("All files", "*.*")]
            file_desc = "PNG file"
        
        input_file = filedialog.askopenfilename(
            title=f"Select {file_desc} for {game_version.upper()}",
            filetypes=filetypes
        )
        
        if not input_file:
            return
        
        self.texture_log(f"Selected: {os.path.basename(input_file)}")
        self.texture_log(f"Game: {game_version.upper()}, Direction: {direction}")
        self.texture_log("-" * 60)
        
        def process():
            try:
                self.texture_progress_label.config(text="Converting...", fg=self.colors['primary'])
                self.texture_progress_bar['value'] = 25
                
                # Determine which batch file to use
                if game_version == "bw1":
                    bat_file = "convert_bw1.bat"
                else:  # bw2
                    bat_file = "convert_bw2.bat"
                
                bat_path = os.path.join(self.app_dir, bat_file)
                
                if not os.path.exists(bat_path):
                    self.texture_progress_bar['value'] = 0
                    self.texture_progress_label.config(text="Error", fg='#ef4444')
                    self.texture_log(f"Error: {bat_file} not found at {bat_path}")
                    ModernMessageBox.show(
                        self.root,
                        "Error",
                        f"Batch file not found: {bat_file}\n\nExpected location: {bat_path}",
                        "error"
                    )
                    return
                
                input_dir = os.path.dirname(input_file)
                input_basename = os.path.basename(input_file)
                filename, ext = os.path.splitext(input_basename)
                
                if direction == "to_png":
                    output_file = os.path.join(input_dir, f"{filename}.png")
                else:
                    output_file = os.path.join(input_dir, f"{filename}.texture")
                
                self.texture_progress_bar['value'] = 50
                self.texture_log(f"Using batch file: {bat_file}")
                self.texture_log(f"Running conversion...")
                
                # Run the batch file with input and output file paths
                result = subprocess.run(
                    [bat_path, input_file, output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.app_dir
                )
                
                self.texture_progress_bar['value'] = 90
                
                if result.returncode == 0:
                    self.texture_progress_bar['value'] = 100
                    self.texture_progress_label.config(text="Complete!", fg=self.colors['success'])
                    self.texture_log(f"Success! Output: {output_file}")
                    if result.stdout:
                        self.texture_log(f"Output: {result.stdout}")
                    self.texture_log("-" * 60)
                    ModernMessageBox.show(
                        self.root,
                        "Success",
                        f"Texture converted successfully!\n\nOutput: {output_file}",
                        "success"
                    )
                else:
                    self.texture_progress_bar['value'] = 0
                    self.texture_progress_label.config(text="Failed", fg='#ef4444')
                    error_msg = result.stderr if result.stderr else result.stdout
                    self.texture_log(f"Error: {error_msg}")
                    ModernMessageBox.show(
                        self.root,
                        "Error",
                        f"Conversion failed:\n{error_msg}",
                        "error"
                    )
            except Exception as e:
                self.texture_progress_bar['value'] = 0
                self.texture_progress_label.config(text="Error", fg='#ef4444')
                self.texture_log(f"Exception: {str(e)}")
                ModernMessageBox.show(
                    self.root,
                    "Error",
                    f"Error during conversion:\n{str(e)}",
                    "error"
                )
        
        thread = threading.Thread(target=process)
        thread.start()
    
    def convert_texture_batch(self, game_version, direction):
        """Batch convert textures using the respective massconvert .bat files"""
        self.reset_texture_ui()
        
        if direction == "to_png":
            file_desc = "texture files (.texture)"
        else:
            file_desc = "PNG files (.png)"
        
        input_folder = filedialog.askdirectory(
            title=f"Select root folder to search for 'Textures' folders"
        )
        
        if not input_folder:
            return
        
        self.texture_log(f"Selected folder: {input_folder}")
        self.texture_log(f"Searching for 'Textures' subfolders...")
        self.texture_log(f"Game: {game_version.upper()}, Direction: {direction}")
        self.texture_log("-" * 60)
        
        def process():
            try:
                self.texture_progress_label.config(text="Searching for Textures folders...", 
                                                   fg=self.colors['primary'])
                self.texture_progress_bar['value'] = 5
                
                # Find all 'Textures' folders in subdirectories
                textures_folders = []
                for root, dirs, files in os.walk(input_folder):
                    for dir_name in dirs:
                        if dir_name.lower() == 'textures':
                            textures_path = os.path.join(root, dir_name)
                            textures_folders.append(textures_path)
                            self.texture_log(f"Found: {textures_path}")
                
                if not textures_folders:
                    self.texture_progress_bar['value'] = 0
                    self.texture_progress_label.config(text="No folders found", fg='#ef4444')
                    self.texture_log("No 'Textures' folders found in the selected directory")
                    ModernMessageBox.show(
                        self.root,
                        "No Folders Found",
                        "No 'Textures' folders found in the selected directory or its subdirectories.",
                        "info"
                    )
                    return
                
                self.texture_log(f"Total 'Textures' folders found: {len(textures_folders)}")
                self.texture_log("-" * 60)
                
                self.texture_progress_bar['value'] = 10
                
                # Determine which batch file to use based on the correct naming
                if game_version == "bw1":
                    if direction == "to_png":
                        bat_file = "massconvert_bw1_to_png.bat"
                    else:
                        bat_file = "massconvert_png_to_bw1.bat"
                else:  # bw2
                    if direction == "to_png":
                        bat_file = "massconvert_bw2_to_png.bat"
                    else:
                        bat_file = "massconvert_png_to_bw2.bat"
                
                bat_path = os.path.join(self.app_dir, bat_file)
                
                if not os.path.exists(bat_path):
                    self.texture_progress_bar['value'] = 0
                    self.texture_progress_label.config(text="Error", fg='#ef4444')
                    self.texture_log(f"Error: {bat_file} not found at {bat_path}")
                    ModernMessageBox.show(
                        self.root,
                        "Error",
                        f"Batch file not found: {bat_file}\n\nExpected location: {bat_path}",
                        "error"
                    )
                    return
                
                self.texture_log(f"Using batch file: {bat_file}")
                self.texture_log(f"Running batch conversion on {len(textures_folders)} folder(s)...")
                
                # Process each Textures folder
                total = len(textures_folders)
                for i, textures_folder in enumerate(textures_folders, 1):
                    progress_percent = 10 + ((i / total) * 80)
                    self.texture_progress_bar['value'] = progress_percent
                    self.texture_progress_label.config(
                        text=f"Processing folder {i}/{total}...",
                        fg=self.colors['primary']
                    )
                    self.texture_log(f"[{i}/{total}] Processing: {textures_folder}")
                    
                    # Use Popen instead of run to handle interactive batch files
                    # Hide the console window when running as frozen executable
                    startupinfo = None
                    if getattr(sys, 'frozen', False):
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                    
                    process = subprocess.Popen(
                        [bat_path, textures_folder],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        text=True,
                        cwd=self.app_dir,
                        startupinfo=startupinfo
                    )
                    
                    # Send Enter key to bypass any pause commands
                    stdout, stderr = process.communicate(input='\n')
                    result_code = process.returncode
                    
                    # Log all output for debugging
                    if stdout and stdout.strip():
                        self.texture_log(f"  Output: {stdout.strip()}")
                    if stderr and stderr.strip():
                        self.texture_log(f"  Error output: {stderr.strip()}")
                    
                    if result_code == 0:
                        self.texture_log(f"  Batch file completed with code 0")
                    else:
                        self.texture_log(f"  Batch file failed with code {result_code}")
                
                self.texture_progress_bar['value'] = 100
                self.texture_progress_label.config(text="Batch conversion complete!", 
                                                   fg=self.colors['success'])
                self.texture_log("-" * 60)
                self.texture_log(f"Batch processing complete! Processed {total} 'Textures' folder(s).")
                
                ModernMessageBox.show(
                    self.root,
                    "Batch Complete",
                    f"Successfully processed {total} 'Textures' folder(s)!",
                    "success"
                )
            except Exception as e:
                self.texture_progress_bar['value'] = 0
                self.texture_progress_label.config(text="Error", fg='#ef4444')
                self.texture_log(f"Exception: {str(e)}")
                ModernMessageBox.show(
                    self.root,
                    "Error",
                    f"Error during batch conversion:\n{str(e)}",
                    "error"
                )
        
        thread = threading.Thread(target=process)
        thread.start()
    
    def res_log(self, message):
        """Log message to RES tab"""
        self.res_log_text.config(state=tk.NORMAL)
        self.res_log_text.insert(tk.END, message + "\n")
        self.res_log_text.see(tk.END)
        self.res_log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def reset_res_ui(self):
        """Reset the RES UI to fresh state"""
        self.res_progress_bar['value'] = 0
        self.res_progress_label.config(text="Ready", fg=self.colors['text_muted'])
        self.single_res_label.config(text="", fg=self.colors['text_muted'])
        self.res_log_text.config(state=tk.NORMAL)
        self.res_log_text.delete(1.0, tk.END)
        self.res_log_text.config(state=tk.DISABLED)
    
    def select_single_res(self):
        self.reset_res_ui()
        
        file_path = filedialog.askopenfilename(
            title="Select .res or .res.gz file",
            filetypes=[
                ("RES files", "*.res *.res.gz"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Auto-detect game version based on file extension
            if file_path.endswith('.res.gz'):
                game_version = "bw2"
            else:  # .res
                game_version = "bw1"
            
            self.single_res_label.config(
                text=f"{os.path.basename(file_path)} ({game_version.upper()})",
                fg=self.colors['success']
            )
            self.process_single_res(file_path, game_version)
    
    def process_single_res(self, file_path, game_version):
        # Output to the appropriate game version folder
        filename = os.path.basename(file_path)
        
        if game_version == "bw1":
            output_folder = os.path.join(self.single_res_bw1, filename + "_Folder")
        else:  # bw2
            output_folder = os.path.join(self.single_res_bw2, filename + "_Folder")
        
        def process():
            try:
                self.res_progress_label.config(text="Processing...", fg=self.colors['primary'])
                self.res_progress_bar['value'] = 0
                self.res_log(f"Processing: {os.path.basename(file_path)} ({game_version.upper()})")
                
                self.res_progress_bar['value'] = 50
                dump_res_to_folder(file_path, output_folder)
                
                self.res_progress_bar['value'] = 100
                self.res_progress_label.config(text="Complete!", fg=self.colors['success'])
                self.res_log(f"Extracted to: {output_folder}")
                self.res_log("-" * 60)
                
                ModernMessageBox.show(
                    self.root,
                    "Success",
                    f"File extracted successfully!\n\nOutput: {output_folder}",
                    "success"
                )
            except Exception as e:
                self.res_progress_bar['value'] = 0
                self.res_progress_label.config(text="Error", fg='#ef4444')
                self.res_log(f"Error: {str(e)}")
                ModernMessageBox.show(
                    self.root,
                    "Error",
                    f"Failed to process file:\n{str(e)}",
                    "error"
                )
        
        thread = threading.Thread(target=process)
        thread.start()
    
    def select_batch_res(self):
        self.reset_res_ui()
        
        input_folder = filedialog.askdirectory(
            title="Select folder to search for .res files"
        )
        
        if not input_folder:
            return
        
        res_files = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.endswith('.res') or file.endswith('.res.gz'):
                    res_files.append(os.path.join(root, file))
        
        if not res_files:
            ModernMessageBox.show(
                self.root,
                "No Files Found",
                "No .res or .res.gz files found in the selected folder.",
                "info"
            )
            return
        
        # Auto-create output folder in the app directory
        output_base = self.batch_output_folder
        
        self.res_log(f"Output folder: {output_base}")
        
        self.process_batch_res(res_files, output_base)
    
    def process_batch_res(self, res_files_bw1, res_files_bw2):
        def process():
            try:
                total = len(res_files_bw1) + len(res_files_bw2)
                current = 0
                
                self.res_progress_label.config(text=f"Processing 0/{total} files...", 
                                          fg=self.colors['primary'])
                self.res_progress_bar['value'] = 0
                self.res_log(f"Starting batch processing of {total} files...")
                self.res_log("-" * 60)
                
                # Process BW1 files
                if res_files_bw1:
                    self.res_log(f"Processing {len(res_files_bw1)} BW1 files...")
                    for file_path in res_files_bw1:
                        current += 1
                        filename = os.path.basename(file_path)
                        output_folder = os.path.join(self.batch_res_bw1, filename + "_Folder")
                        
                        progress_percent = (current / total) * 100
                        self.res_progress_bar['value'] = progress_percent
                        self.res_progress_label.config(
                            text=f"Processing {current}/{total}: {filename} (BW1)",
                            fg=self.colors['primary']
                        )
                        self.res_log(f"[{current}/{total}] Processing: {filename} (BW1)")
                        
                        try:
                            dump_res_to_folder(file_path, output_folder)
                            self.res_log(f"  Extracted to: {output_folder}")
                        except Exception as e:
                            self.res_log(f"  Error: {str(e)}")
                
                # Process BW2 files
                if res_files_bw2:
                    self.res_log(f"Processing {len(res_files_bw2)} BW2 files...")
                    for file_path in res_files_bw2:
                        current += 1
                        filename = os.path.basename(file_path)
                        output_folder = os.path.join(self.batch_res_bw2, filename + "_Folder")
                        
                        progress_percent = (current / total) * 100
                        self.res_progress_bar['value'] = progress_percent
                        self.res_progress_label.config(
                            text=f"Processing {current}/{total}: {filename} (BW2)",
                            fg=self.colors['primary']
                        )
                        self.res_log(f"[{current}/{total}] Processing: {filename} (BW2)")
                        
                        try:
                            dump_res_to_folder(file_path, output_folder)
                            self.res_log(f"  Extracted to: {output_folder}")
                        except Exception as e:
                            self.res_log(f"  Error: {str(e)}")
                
                self.res_progress_bar['value'] = 100
                self.res_progress_label.config(text="Batch processing complete!", 
                                          fg=self.colors['success'])
                self.res_log("-" * 60)
                self.res_log(f"Batch processing complete! Processed {total} files.")
                self.res_log(f"BW1 output: {self.batch_res_bw1}")
                self.res_log(f"BW2 output: {self.batch_res_bw2}")
                
                ModernMessageBox.show(
                    self.root,
                    "Batch Complete",
                    f"Successfully processed {total} files!\n\nBW1: {len(res_files_bw1)} files\nBW2: {len(res_files_bw2)} files",
                    "success"
                )
            except Exception as e:
                self.res_progress_bar['value'] = 0
                self.res_progress_label.config(text="Error", fg='#ef4444')
                self.res_log(f"Batch error: {str(e)}")
                ModernMessageBox.show(
                    self.root,
                    "Error",
                    f"Batch processing failed:\n{str(e)}",
                    "error"
                )
        
        thread = threading.Thread(target=process)
        thread.start()
    
    def select_single_repack(self):
        """Select a single extracted folder to repack into RES"""
        self.reset_res_ui()
        
        folder_path = filedialog.askdirectory(
            title="Select extracted folder to repack"
        )
        
        if not folder_path:
            return
        
        # Check if resinfo.txt exists to verify it's an extracted folder
        resinfo_path = os.path.join(folder_path, "resinfo.txt")
        if not os.path.exists(resinfo_path):
            ModernMessageBox.show(
                self.root,
                "Invalid Folder",
                "Selected folder doesn't appear to be an extracted RES folder.\n\nMissing resinfo.txt file.",
                "error"
            )
            return
        
        self.process_single_repack(folder_path)
    
    def process_single_repack(self, folder_path):
        """Repack a single folder back into RES file"""
        def process():
            try:
                self.res_progress_label.config(text="Repacking...", fg=self.colors['primary'])
                self.res_progress_bar['value'] = 25
                self.res_log(f"Repacking: {os.path.basename(folder_path)}")
                
                # Read resinfo.txt to determine game version
                import json
                with open(os.path.join(folder_path, "resinfo.txt"), "r") as f:
                    resinfo = json.load(f)
                
                is_bw2 = resinfo["Game"] == "Battalion Wars 2"
                game_version = "bw2" if is_bw2 else "bw1"
                
                # Determine output location based on game version
                if is_bw2:
                    output_dir = self.repacked_bw2
                    extension = ".res.gz"
                else:
                    output_dir = self.repacked_bw1
                    extension = ".res"
                
                # Get the base filename
                folder_name = os.path.basename(folder_path)
                if folder_name.endswith("_Folder"):
                    base_name = folder_name[:-7]  # Remove "_Folder" suffix
                else:
                    base_name = folder_name
                
                # Remove extension if it's there
                if base_name.endswith(".res.gz"):
                    base_name = base_name[:-7]
                elif base_name.endswith(".res"):
                    base_name = base_name[:-4]
                
                output_file = os.path.join(output_dir, base_name + extension)
                
                self.res_progress_bar['value'] = 50
                self.res_log(f"Output file: {output_file}")
                self.res_log(f"Game version: {game_version.upper()}")
                
                # Run restool.py to repack
                restool_path = os.path.join(self.app_dir, "restool.py")
                
                result = subprocess.run(
                    [sys.executable, restool_path, folder_path, output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.app_dir
                )
                
                self.res_progress_bar['value'] = 90
                
                if result.returncode == 0:
                    self.res_progress_bar['value'] = 100
                    self.res_progress_label.config(text="Complete!", fg=self.colors['success'])
                    self.res_log(f"Repacked to: {output_file}")
                    self.res_log("-" * 60)
                    ModernMessageBox.show(
                        self.root,
                        "Success",
                        f"Folder repacked successfully!\n\nOutput: {output_file}",
                        "success"
                    )
                else:
                    self.res_progress_bar['value'] = 0
                    self.res_progress_label.config(text="Error", fg='#ef4444')
                    error_msg = result.stderr if result.stderr else result.stdout
                    self.res_log(f"Error: {error_msg}")
                    ModernMessageBox.show(
                        self.root,
                        "Error",
                        f"Failed to repack folder:\n{error_msg}",
                        "error"
                    )
            except Exception as e:
                self.res_progress_bar['value'] = 0
                self.res_progress_label.config(text="Error", fg='#ef4444')
                self.res_log(f"Error: {str(e)}")
                ModernMessageBox.show(
                    self.root,
                    "Error",
                    f"Failed to repack folder:\n{str(e)}",
                    "error"
                )
        
        thread = threading.Thread(target=process)
        thread.start()
    
    def select_batch_repack(self):
        """Select a folder containing multiple extracted folders to repack"""
        self.reset_res_ui()
        
        root_folder = filedialog.askdirectory(
            title="Select folder containing extracted folders"
        )
        
        if not root_folder:
            return
        
        # Find all folders with resinfo.txt (indicating they're extracted RES folders)
        folders_to_repack = []
        for item in os.listdir(root_folder):
            item_path = os.path.join(root_folder, item)
            if os.path.isdir(item_path):
                resinfo_path = os.path.join(item_path, "resinfo.txt")
                if os.path.exists(resinfo_path):
                    folders_to_repack.append(item_path)
        
        if not folders_to_repack:
            ModernMessageBox.show(
                self.root,
                "No Folders Found",
                "No extracted RES folders found in the selected directory.",
                "info"
            )
            return
        
        self.res_log(f"Found {len(folders_to_repack)} folders to repack")
        self.process_batch_repack(folders_to_repack)
    
    def process_batch_repack(self, folders_to_repack):
        """Repack multiple folders back into RES files"""
        def process():
            try:
                import json
                total = len(folders_to_repack)
                self.res_progress_label.config(text=f"Repacking 0/{total} folders...", 
                                          fg=self.colors['primary'])
                self.res_progress_bar['value'] = 0
                self.res_log(f"Starting batch repacking of {total} folders...")
                self.res_log("-" * 60)
                
                restool_path = os.path.join(self.app_dir, "restool.py")
                
                for i, folder_path in enumerate(folders_to_repack, 1):
                    folder_name = os.path.basename(folder_path)
                    
                    progress_percent = (i / total) * 100
                    self.res_progress_bar['value'] = progress_percent
                    self.res_progress_label.config(
                        text=f"Repacking {i}/{total}: {folder_name}",
                        fg=self.colors['primary']
                    )
                    self.res_log(f"[{i}/{total}] Repacking: {folder_name}")
                    
                    try:
                        # Read resinfo.txt to determine game version
                        with open(os.path.join(folder_path, "resinfo.txt"), "r") as f:
                            resinfo = json.load(f)
                        
                        is_bw2 = resinfo["Game"] == "Battalion Wars 2"
                        game_version = "bw2" if is_bw2 else "bw1"
                        
                        # Determine output location based on game version
                        if is_bw2:
                            output_dir = self.repacked_bw2
                            extension = ".res.gz"
                        else:
                            output_dir = self.repacked_bw1
                            extension = ".res"
                        
                        # Get the base filename
                        if folder_name.endswith("_Folder"):
                            base_name = folder_name[:-7]
                        else:
                            base_name = folder_name
                        
                        # Remove extension if it's there
                        if base_name.endswith(".res.gz"):
                            base_name = base_name[:-7]
                        elif base_name.endswith(".res"):
                            base_name = base_name[:-4]
                        
                        output_file = os.path.join(output_dir, base_name + extension)
                        
                        result = subprocess.run(
                            [sys.executable, restool_path, folder_path, output_file],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            cwd=self.app_dir
                        )
                        
                        if result.returncode == 0:
                            self.res_log(f"  Repacked to: {output_file} ({game_version.upper()})")
                        else:
                            error_msg = result.stderr if result.stderr else result.stdout
                            self.res_log(f"  Error: {error_msg}")
                    except Exception as e:
                        self.res_log(f"  Error: {str(e)}")
                
                self.res_progress_bar['value'] = 100
                self.res_progress_label.config(text="Batch repacking complete!", 
                                          fg=self.colors['success'])
                self.res_log("-" * 60)
                self.res_log(f"Batch repacking complete! Processed {total} folders.")
                self.res_log(f"BW1 output: {self.repacked_bw1}")
                self.res_log(f"BW2 output: {self.repacked_bw2}")
                
                ModernMessageBox.show(
                    self.root,
                    "Batch Complete",
                    f"Successfully repacked {total} folders!",
                    "success"
                )
            except Exception as e:
                self.res_progress_bar['value'] = 0
                self.res_progress_label.config(text="Error", fg='#ef4444')
                self.res_log(f"Batch error: {str(e)}")
                ModernMessageBox.show(
                    self.root,
                    "Error",
                    f"Batch repacking failed:\n{str(e)}",
                    "error"
                )
        
        thread = threading.Thread(target=process)
        thread.start()


# Add method to Canvas for rounded rectangles
def _create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = [x1+radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1]
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle


def main():
    root = tk.Tk()
    app = UnifiedToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()