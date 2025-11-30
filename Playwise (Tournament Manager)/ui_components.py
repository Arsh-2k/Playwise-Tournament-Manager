"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ UI COMPONENTS MODULE                                                      ║
║ Developer: Deepak Bisht (S25CSEU0986)                                     ║
║ Contribution: User Interface, Visual Components, Victory Screen           ║
║ Role: Complete UI/UX implementation and user interaction management       ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random

from config import (COLORS, GAME_CONFIGS, TOURNAMENT_FORMATS, FONT_FAMILY, 
                   FONT_SIZES, LABELS, RESULT_BUTTONS, VICTORY_MESSAGES,
                   RANK_MEDALS, MATCH_STATUS_ICONS)
from data_models import Participant
from tournament_logic import TournamentEngine
from analytics import LeaderboardSystem, AnalyticsEngine


class UIManager:
    """
    Main UI Manager
    Coordinates all UI components and views
    """
    
    def __init__(self, root, app):
        """Initialize UI Manager"""
        self.root = root
        self.app = app
        self.sheet_entries = []
        
        # Setup styles
        self.setup_styles()
        
        # Create main layout
        self.create_layout()
        
        # Show home by default
        self.show_home()
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Frame styles
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("Card.TFrame", background=COLORS["bg_card"], relief="flat")
        style.configure("Panel.TFrame", background=COLORS["bg_panel"])
        
        # Label styles
        style.configure("TLabel", background=COLORS["bg_dark"], 
                       foreground=COLORS["text_main"], font=(FONT_FAMILY, FONT_SIZES["body"]))
        style.configure("Header.TLabel", font=(FONT_FAMILY, FONT_SIZES["header"], "bold"), 
                       foreground=COLORS["accent_bright"])
        style.configure("Card.TLabel", background=COLORS["bg_card"], 
                       foreground=COLORS["text_main"])
        
        # Button styles
        style.configure("TButton", padding=10, background=COLORS["accent"], 
                       font=(FONT_FAMILY, FONT_SIZES["button"], "bold"))
        style.configure("Accent.TButton", background=COLORS["accent_bright"])
        style.configure("Danger.TButton", background=COLORS["danger"])
        style.configure("Success.TButton", background=COLORS["success"])
        
        # Treeview styles
        style.configure("Treeview", background=COLORS["bg_card"], 
                       foreground=COLORS["text_main"], fieldbackground=COLORS["bg_card"], 
                       rowheight=32, borderwidth=0)
        style.configure("Treeview.Heading", background=COLORS["header"], 
                       foreground=COLORS["text_main"], font=(FONT_FAMILY, FONT_SIZES["body"], "bold"))
        style.map("Treeview", background=[("selected", COLORS["accent"])])
    
    def create_layout(self):
        """Create main application layout"""
        # Sidebar
        self.sidebar = self.create_sidebar()
        self.sidebar.pack(side="left", fill="y")
        
        # Main content area
        self.main_area = ttk.Frame(self.root)
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = ttk.Frame(self.root, style="Panel.TFrame")
        
        # Logo
        logo_frame = ttk.Frame(sidebar, style="Panel.TFrame")
        logo_frame.pack(pady=30)
        
        tk.Label(logo_frame, text="⚡ PLAYWISE", font=("Impact", FONT_SIZES["logo"]),
                bg=COLORS["bg_panel"], fg=COLORS["accent_bright"]).pack()
        tk.Label(logo_frame, text="Tournament Manager", font=(FONT_FAMILY, 9),
                bg=COLORS["bg_panel"], fg=COLORS["text_sub"]).pack()
        
        # Navigation buttons
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=20, pady=10)
        
        self.create_nav_button(sidebar, "🏠 Dashboard", self.show_home)
        self.create_nav_button(sidebar, "➕ New Tournament", self.show_create)
        
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=20, pady=10)
        
        self.manage_btn = self.create_nav_button(sidebar, "⚙️ Manage", self.show_manage)
        self.manage_btn.config(state="disabled")
        
        # Footer
        footer = ttk.Frame(sidebar, style="Panel.TFrame")
        footer.pack(side="bottom", pady=20)
        tk.Label(footer, text="© 2025 DATA DRIFTERS", font=(FONT_FAMILY, 8),
                bg=COLORS["bg_panel"], fg=COLORS["text_sub"]).pack()
        
        return sidebar
    
    def create_nav_button(self, parent, text, command):
        """Create styled navigation button"""
        btn = tk.Button(parent, text=text, command=command, bg=COLORS["bg_panel"],
                       fg=COLORS["text_main"], activebackground=COLORS["accent"],
                       activeforeground=COLORS["text_main"], relief="flat",
                       font=(FONT_FAMILY, FONT_SIZES["body"], "bold"),
                       cursor="hand2", padx=20, pady=12, anchor="w")
        btn.pack(fill="x", padx=10, pady=3)
        
        # Hover effects
        btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["accent"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["bg_panel"]))
        
        return btn
    
    def clear_main(self):
        """Clear main content area"""
        for widget in self.main_area.winfo_children():
            widget.destroy()
    
    # ==========================================================================
    # HOME VIEW - DASHBOARD
    # ==========================================================================
    
    def show_home(self):
        """Display tournament dashboard"""
        self.clear_main()
        self.app.current_tournament = None
        self.manage_btn.config(state="disabled")
        
        # Header
        ttk.Label(self.main_area, text="Tournament Dashboard", 
                 style="Header.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Tournament list
        if not self.app.tournaments:
            self.show_empty_state()
            return
        
        # Create tournament table
        cols = ("name", "game", "format", "round", "status")
        tree = ttk.Treeview(self.main_area, columns=cols, show="headings", height=12)
        
        tree.heading("name", text="Tournament Name")
        tree.heading("game", text="Game")
        tree.heading("format", text="Format")
        tree.heading("round", text="Round")
        tree.heading("status", text="Status")
        
        tree.column("name", width=280)
        tree.column("game", width=180)
        tree.column("format", width=120)
        tree.column("round", width=100, anchor="center")
        tree.column("status", width=120, anchor="center")
        
        # Populate data
        for t in self.app.tournaments.values():
            status = f"{MATCH_STATUS_ICONS['completed']} Finished" if t.is_finished else f"{MATCH_STATUS_ICONS['pending']} Active"
            tree.insert("", "end", values=(t.name, t.game_type, t.format_type, 
                                          f"Round {t.current_round}", status), iid=t.id)
        
        tree.pack(fill="both", expand=True, pady=10)
        tree.bind("<Double-1>", lambda e: self.load_tournament(tree))
        
        # Action buttons
        btn_frame = ttk.Frame(self.main_area)
        btn_frame.pack(pady=20, fill="x")
        
        ttk.Button(btn_frame, text="📂 Load Selected", 
                  command=lambda: self.load_tournament(tree), 
                  style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete", 
                  command=lambda: self.delete_tournament(tree),
                  style="Danger.TButton").pack(side="left", padx=5)
    
    def show_empty_state(self):
        """Show empty state when no tournaments exist"""
        empty_frame = ttk.Frame(self.main_area, style="Card.TFrame", padding=50)
        empty_frame.pack(fill="both", expand=True)
        
        tk.Label(empty_frame, text="📋", font=(FONT_FAMILY, 64),
                bg=COLORS["bg_card"]).pack(pady=20)
        tk.Label(empty_frame, text="No Tournaments Yet", 
                font=(FONT_FAMILY, FONT_SIZES["subheader"], "bold"),
                bg=COLORS["bg_card"], fg=COLORS["text_main"]).pack()
        tk.Label(empty_frame, text="Create your first tournament to get started!",
                bg=COLORS["bg_card"], fg=COLORS["text_sub"]).pack(pady=10)
        
        ttk.Button(empty_frame, text="➕ Create Tournament", 
                  command=self.show_create, style="Accent.TButton").pack(pady=20)
    
    def load_tournament(self, tree):
        """Load selected tournament"""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a tournament first")
            return
        
        self.app.load_tournament(sel[0])
        self.manage_btn.config(state="normal")
        self.show_manage()
    
    def delete_tournament(self, tree):
        """Delete selected tournament"""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a tournament first")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                               "Are you sure you want to delete this tournament?\nThis cannot be undone."):
            self.app.delete_tournament(sel[0])
            self.show_home()
    
    # ==========================================================================
    # CREATE TOURNAMENT VIEW
    # ==========================================================================
    
    def show_create(self):
        """Tournament creation wizard"""
        self.clear_main()
        
        ttk.Label(self.main_area, text="Create New Tournament", 
                 style="Header.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Configuration card
        config_card = ttk.Frame(self.main_area, style="Card.TFrame", padding=20)
        config_card.pack(fill="x", pady=10)
        
        # Tournament name
        ttk.Label(config_card, text=LABELS["tournament_name"], 
                 style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        name_entry = ttk.Entry(config_card, width=35, font=(FONT_FAMILY, FONT_SIZES["body"]))
        name_entry.grid(row=0, column=1, padx=10, pady=8, sticky="w")
        
        # Game type
        ttk.Label(config_card, text=LABELS["game_type"], 
                 style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=10, pady=8)
        game_cb = ttk.Combobox(config_card, values=list(GAME_CONFIGS.keys()),
                              state="readonly", width=20, font=(FONT_FAMILY, FONT_SIZES["body"]))
        game_cb.current(0)
        game_cb.grid(row=0, column=3, padx=10, pady=8)
        
        # Format
        ttk.Label(config_card, text=LABELS["format"], 
                 style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        format_cb = ttk.Combobox(config_card, values=TOURNAMENT_FORMATS,
                                state="readonly", width=33, font=(FONT_FAMILY, FONT_SIZES["body"]))
        format_cb.current(0)
        format_cb.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        
        # Number of players
        ttk.Label(config_card, text=LABELS["num_players"], 
                 style="Card.TLabel").grid(row=1, column=2, sticky="w", padx=10, pady=8)
        count_entry = ttk.Entry(config_card, width=10, font=(FONT_FAMILY, FONT_SIZES["body"]))
        count_entry.insert(0, "4")
        count_entry.grid(row=1, column=3, padx=10, pady=8, sticky="w")
        
        # Recommendation label
        rec_label = tk.Label(config_card, text="", bg=COLORS["bg_card"],
                            fg=COLORS["warning"], font=(FONT_FAMILY, FONT_SIZES["small"], "italic"),
                            wraplength=800, justify="left")
        rec_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=10, pady=8)
        
        # Generate button
        ttk.Button(config_card, text="🎲 Generate Player Sheet",
                  command=lambda: self.generate_sheet(game_cb, count_entry, sheet_frame)).grid(
                      row=3, column=0, columnspan=4, pady=15)
        
        # Spreadsheet container
        sheet_container = ttk.Frame(self.main_area)
        sheet_container.pack(fill="both", expand=True, pady=10)
        
        canvas = tk.Canvas(sheet_container, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(sheet_container, orient="vertical", command=canvas.yview)
        sheet_frame = ttk.Frame(canvas, style="Card.TFrame")
        
        sheet_frame.bind("<Configure>", 
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sheet_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Update recommendations on game change
        def update_recommendations(event=None):
            game = game_cb.get()
            conf = GAME_CONFIGS[game]
            rec_text = f"💡 {conf['rec_format']} format recommended. {conf['rec_players']}.\n{conf['desc']}"
            rec_label.config(text=rec_text)
        
        game_cb.bind("<<ComboboxSelected>>", update_recommendations)
        update_recommendations()
        
        # Create tournament button
        ttk.Button(self.main_area, text="✅ Create Tournament",
                  command=lambda: self.save_tournament(name_entry, game_cb, format_cb),
                  style="Success.TButton").pack(fill="x", pady=15)
    
    def generate_sheet(self, game_cb, count_entry, sheet_frame):
        """Generate dynamic player entry sheet"""
        for widget in sheet_frame.winfo_children():
            widget.destroy()
        self.sheet_entries = []
        
        try:
            count = int(count_entry.get())
            if count < 2 or count > 128:
                messagebox.showwarning("Invalid Input", "Enter between 2 and 128 players")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return
        
        game = game_cb.get()
        conf = GAME_CONFIGS[game]
        
        # Define columns
        headers = ["#", "Player/Team Name"]
        if conf['has_elo']:
            headers.append("Elo Rating")
        if conf['has_roles']:
            headers.append("Team Name")
            headers.append("Role")
        
        # Draw headers
        for col, text in enumerate(headers):
            tk.Label(sheet_frame, text=text, bg=COLORS["header"], fg=COLORS["text_main"],
                    font=(FONT_FAMILY, FONT_SIZES["small"], "bold"), 
                    padx=10, pady=8).grid(row=0, column=col, sticky="ew", padx=1, pady=1)
        
        # Draw entry rows
        roles = conf.get('roles', [])
        
        for i in range(count):
            row_data = {}
            
            # Row number
            tk.Label(sheet_frame, text=f"{i+1}", bg=COLORS["bg_card"], 
                    fg=COLORS["text_sub"], width=4).grid(row=i+1, column=0, padx=1, pady=1)
            
            col_idx = 1
            
            # Name field
            e_name = ttk.Entry(sheet_frame, width=25, font=(FONT_FAMILY, FONT_SIZES["body"]))
            e_name.grid(row=i+1, column=col_idx, padx=1, pady=1)
            row_data['name'] = e_name
            col_idx += 1
            
            # Elo field (only for Chess)
            if conf['has_elo']:
                e_elo = ttk.Entry(sheet_frame, width=12, font=(FONT_FAMILY, FONT_SIZES["body"]))
                e_elo.insert(0, "1000")
                e_elo.grid(row=i+1, column=col_idx, padx=1, pady=1)
                row_data['elo'] = e_elo
                col_idx += 1
            
            # Team & Role fields
            if conf['has_roles']:
                e_team = ttk.Entry(sheet_frame, width=20, font=(FONT_FAMILY, FONT_SIZES["body"]))
                e_team.grid(row=i+1, column=col_idx, padx=1, pady=1)
                row_data['team'] = e_team
                col_idx += 1
                
                e_role = ttk.Combobox(sheet_frame, values=roles, state="readonly", 
                                     width=18, font=(FONT_FAMILY, FONT_SIZES["body"]))
                if roles:
                    e_role.current(0)
                e_role.grid(row=i+1, column=col_idx, padx=1, pady=1)
                row_data['role'] = e_role
                col_idx += 1
            
            self.sheet_entries.append(row_data)
    
    def save_tournament(self, name_entry, game_cb, format_cb):
        """Save and create tournament"""
        t_name = name_entry.get().strip()
        if not t_name:
            messagebox.showerror("Error", "Please enter tournament name")
            return
        
        if not self.sheet_entries:
            messagebox.showerror("Error", "Please generate player sheet first")
            return
        
        # Collect participant data
        participants_data = []
        for entry_row in self.sheet_entries:
            name = entry_row['name'].get().strip()
            if not name:
                continue
            
            p_data = {'name': name}
            p_data['rating'] = entry_row['elo'].get() if 'elo' in entry_row else 1000
            p_data['team'] = entry_row['team'].get().strip() if 'team' in entry_row else ""
            p_data['role'] = entry_row['role'].get() if 'role' in entry_row else ""
            
            participants_data.append(p_data)
        
        # Create tournament
        success, message = self.app.create_tournament(
            t_name, game_cb.get(), format_cb.get(), participants_data
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.manage_btn.config(state="normal")
            self.show_manage()
        else:
            messagebox.showerror("Error", message)
    
    # ==========================================================================
    # MANAGE TOURNAMENT VIEW
    # ==========================================================================
    
    def show_manage(self):
        """Tournament management interface"""
        self.clear_main()
        
        if not self.app.current_tournament:
            self.show_home()
            return
        
        t = self.app.current_tournament
        
        # Check if tournament is finished
        if t.is_finished:
            self.show_victory_screen()
            return
        
        # Header
        header = ttk.Frame(self.main_area)
        header.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header, text=t.name, style="Header.TLabel").pack(side="left")
        
        info_text = f"{t.game_type} | {t.format_type} | Round {t.current_round}"
        tk.Label(header, text=info_text, bg=COLORS["accent"], fg="white",
                font=(FONT_FAMILY, FONT_SIZES["body"], "bold"), 
                padx=15, pady=8).pack(side="right")
        
        # Tabs
        notebook = ttk.Notebook(self.main_area)
        notebook.pack(fill="both", expand=True)
        
        self.create_standings_tab(notebook, t)
        self.create_matches_tab(notebook, t)
        self.create_statistics_tab(notebook, t)
    
    def create_standings_tab(self, notebook, tournament):
        """Create standings/leaderboard tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="🏆 Leaderboard")
        
        # Get leaderboard
        leaderboard = LeaderboardSystem.get_leaderboard(tournament)
        game_config = GAME_CONFIGS[tournament.game_type]
        
        # Define columns
        cols = ["rank", "name", "played", "won", "drawn", "lost", "pts", "gd"]
        if game_config.get('has_elo'):
            cols.insert(2, "rating")
        if game_config.get('has_roles'):
            cols.insert(2, "team")
        
        tree = ttk.Treeview(tab, columns=cols, show="headings", height=15)
        
        # Configure columns
        tree.column("rank", width=60, anchor="center")
        tree.column("name", width=200, anchor="w")
        if "team" in cols:
            tree.column("team", width=120, anchor="center")
        if "rating" in cols:
            tree.column("rating", width=80, anchor="center")
        for c in ["played", "won", "drawn", "lost", "pts", "gd"]:
            tree.column(c, width=60, anchor="center")
        
        # Headings
        tree.heading("rank", text="Rank")
        tree.heading("name", text="Player/Team")
        if "team" in cols:
            tree.heading("team", text="Team")
        if "rating" in cols:
            tree.heading("rating", text="Elo")
        tree.heading("played", text="P")
        tree.heading("won", text="W")
        tree.heading("drawn", text="D")
        tree.heading("lost", text="L")
        tree.heading("pts", text="Pts")
        tree.heading("gd", text="GD")
        
        # Populate data
        for entry in leaderboard:
            rank_display = f"{entry['medal']} {entry['rank']}" if entry['medal'] else entry['rank']
            
            vals = [rank_display, entry['name'], entry['played'], entry['won'], 
                   entry['drawn'], entry['lost'], entry['points'], entry['gd']]
            
            if "team" in cols:
                vals.insert(2, entry['team'])
            if "rating" in cols:
                vals.insert(2, entry['rating'])
            
            tree.insert("", "end", values=vals)
        
        tree.pack(fill="both", expand=True, pady=10, padx=10)
        
        # Export button
        ttk.Button(tab, text="📤 Export to CSV", 
                  command=self.export_standings).pack(pady=10)
    
    def create_matches_tab(self, notebook, tournament):
        """Create matches management tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⚔️ Matches")
        
        # Toolbar
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", pady=10, padx=10)
        
        ttk.Button(toolbar, text="🎲 Generate Fixtures",
                  command=self.generate_fixtures).pack(side="left", padx=5)
        ttk.Button(toolbar, text="⏭️ Next Round",
                  command=self.advance_round).pack(side="left", padx=5)
        ttk.Button(toolbar, text="🏁 Finish Tournament",
                  command=self.finish_tournament, 
                  style="Success.TButton").pack(side="right", padx=5)
        
        # Match list
        self.render_match_list(tab, tournament)
    
    def render_match_list(self, parent, tournament):
        """Render list of matches"""
        canvas = tk.Canvas(parent, bg=COLORS["bg_dark"], highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        
        canvas.pack(side="left", fill="both", expand=True, pady=10)
        scroll.pack(side="right", fill="y")
        
        matches = tournament.get_current_matches()
        
        if not matches:
            tk.Label(frame, text="No matches yet. Click 'Generate Fixtures'",
                    font=(FONT_FAMILY, FONT_SIZES["subheader"]),
                    bg=COLORS["bg_dark"], fg=COLORS["text_sub"]).pack(pady=50)
            return
        
        for match in matches:
            self.create_match_card(frame, match, tournament)
    
    def create_match_card(self, parent, match, tournament):
        """Create individual match card"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.pack(fill="x", pady=5, padx=10)
        
        p1, p2 = TournamentEngine.get_match_participants(tournament, match)
        p2_name = p2.name if p2 else "🎁 BYE"
        
        # Match info
        match_text = f"{p1.name}  vs  {p2_name}"
        tk.Label(card, text=match_text, font=(FONT_FAMILY, FONT_SIZES["subheader"]),
                bg=COLORS["bg_card"], fg=COLORS["text_main"]).pack(side="left")
        
        if match.is_played:
            # Show score
            score_text = f"  [{match.p1_score} - {match.p2_score}]"
            tk.Label(card, text=score_text, font=(FONT_FAMILY, FONT_SIZES["subheader"], "bold"),
                    bg=COLORS["bg_card"], fg=COLORS["success"]).pack(side="left", padx=10)
        elif p2:
            # Show result entry buttons
            self.create_result_buttons(card, match, tournament)
    
    def create_result_buttons(self, parent, match, tournament):
        """Create 3-button result entry system"""
        btn_frame = ttk.Frame(parent, style="Card.TFrame")
        btn_frame.pack(side="right")
        
        game_config = GAME_CONFIGS[tournament.game_type]
        allows_draw = game_config.get('allows_draw', True) and tournament.format_type != "Knockout"
        
        # Player 1 Win button
        tk.Button(btn_frame, text=RESULT_BUTTONS["player1_win"], 
                 command=lambda: self.quick_result(match.id, 'p1'),
                 bg=COLORS["success"], fg="white", font=(FONT_FAMILY, FONT_SIZES["button"]),
                 relief="flat", padx=15, pady=8, cursor="hand2").pack(side="left", padx=3)
        
        # Player 2 Win button  
        tk.Button(btn_frame, text=RESULT_BUTTONS["player2_win"],
                 command=lambda: self.quick_result(match.id, 'p2'),
                 bg=COLORS["danger"], fg="white", font=(FONT_FAMILY, FONT_SIZES["button"]),
                 relief="flat", padx=15, pady=8, cursor="hand2").pack(side="left", padx=3)
        
        # Draw button (if allowed)
        if allows_draw:
            tk.Button(btn_frame, text=RESULT_BUTTONS["draw"],
                     command=lambda: self.quick_result(match.id, 'draw'),
                     bg=COLORS["warning"], fg="black", font=(FONT_FAMILY, FONT_SIZES["button"]),
                     relief="flat", padx=15, pady=8, cursor="hand2").pack(side="left", padx=3)
    
    def quick_result(self, match_id, winner):
        """Record quick result"""
        success = TournamentEngine.record_result_quick(
            self.app.current_tournament, match_id, winner
        )
        
        if success:
            self.app.save_application_data()
            self.show_manage()
        else:
            messagebox.showerror("Error", "Failed to record result")
    
    def create_statistics_tab(self, notebook, tournament):
        """Create statistics tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📊 Statistics")
        
        stats = AnalyticsEngine.get_tournament_stats(tournament)
        
        # Statistics cards
        cards_frame = ttk.Frame(tab)
        cards_frame.pack(fill="x", pady=20, padx=20)
        
        self.create_stat_card(cards_frame, "Participants", 
                             f"{stats['active_participants']}/{stats['total_participants']}", 
                             "👥").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(cards_frame, "Matches", 
                             f"{stats['completed_matches']}/{stats['total_matches']}", 
                             "⚔️").pack(side="left", padx=10, fill="x", expand=True)
        self.create_stat_card(cards_frame, "Avg Goals", 
                             str(stats['avg_goals_per_match']), 
                             "⚽").pack(side="left", padx=10, fill="x", expand=True)
    
    def create_stat_card(self, parent, title, value, icon):
        """Create statistic display card"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        
        tk.Label(card, text=icon, font=(FONT_FAMILY, 32),
                bg=COLORS["bg_card"]).pack()
        tk.Label(card, text=value, font=(FONT_FAMILY, FONT_SIZES["header"], "bold"),
                bg=COLORS["bg_card"], fg=COLORS["accent_bright"]).pack()
        tk.Label(card, text=title, font=(FONT_FAMILY, FONT_SIZES["body"]),
                bg=COLORS["bg_card"], fg=COLORS["text_sub"]).pack()
        
        return card
    
    # ==========================================================================
    # VICTORY SCREEN
    # ==========================================================================
    
    def show_victory_screen(self):
        """Show tournament victory/finish screen"""
        self.clear_main()
        t = self.app.current_tournament
        
        # Victory container
        victory_frame = ttk.Frame(self.main_area, style="Card.TFrame", padding=40)
        victory_frame.pack(fill="both", expand=True)
        
        # Animated title
        title = random.choice(VICTORY_MESSAGES)
        tk.Label(victory_frame, text=title, font=("Impact", 42),
                bg=COLORS["bg_card"], fg=COLORS["gold"]).pack(pady=20)
        
        # Winner info
        winner = t.get_winner()
        if winner:
            tk.Label(victory_frame, text=winner.name, 
                    font=(FONT_FAMILY, 32, "bold"),
                    bg=COLORS["bg_card"], fg=COLORS["accent_bright"]).pack(pady=10)
            
            stats_text = f"{winner.won}W - {winner.drawn}D - {winner.lost}L | {winner.points} Points"
            tk.Label(victory_frame, text=stats_text, font=(FONT_FAMILY, FONT_SIZES["subheader"]),
                    bg=COLORS["bg_card"], fg=COLORS["text_main"]).pack()
        
        # Podium
        tk.Label(victory_frame, text="🏆 PODIUM 🏆", 
                font=(FONT_FAMILY, FONT_SIZES["header"], "bold"),
                bg=COLORS["bg_card"], fg=COLORS["accent_bright"]).pack(pady=30)
        
        podium_frame = ttk.Frame(victory_frame, style="Card.TFrame")
        podium_frame.pack(pady=10)
        
        top_three = t.get_top_three()
        for i, p in enumerate(top_three, 1):
            medal = RANK_MEDALS.get(i, '')
            self.create_podium_card(podium_frame, i, medal, p).pack(side="left", padx=15)
        
        # Action buttons
        btn_frame = ttk.Frame(victory_frame, style="Card.TFrame")
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="📊 View Full Standings",
                  command=self.show_final_standings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🏠 Back to Dashboard",
                  command=self.show_home, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📤 Export Results",
                  command=self.export_standings).pack(side="left", padx=5)
    
    def create_podium_card(self, parent, rank, medal, participant):
        """Create podium position card"""
        colors = {1: COLORS["gold"], 2: COLORS["silver"], 3: COLORS["bronze"]}
        
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        
        tk.Label(card, text=medal, font=(FONT_FAMILY, 48),
                bg=COLORS["bg_card"]).pack()
        tk.Label(card, text=f"#{rank}", font=(FONT_FAMILY, FONT_SIZES["header"]),
                bg=COLORS["bg_card"], fg=colors.get(rank, COLORS["text_sub"])).pack()
        tk.Label(card, text=participant.name, font=(FONT_FAMILY, FONT_SIZES["subheader"], "bold"),
                bg=COLORS["bg_card"], fg=COLORS["text_main"]).pack()
        tk.Label(card, text=f"{participant.points} pts", 
                bg=COLORS["bg_card"], fg=COLORS["text_sub"]).pack()
        
        return card
    
    def show_final_standings(self):
        """Show final standings after tournament"""
        self.app.current_tournament.is_finished = False  # Temporarily unmark
        self.show_manage()
        self.app.current_tournament.is_finished = True  # Remark
    
    # ==========================================================================
    # ACTIONS
    # ==========================================================================
    
    def generate_fixtures(self):
        """Generate fixtures for current round"""
        success, message = self.app.generate_fixtures()
        if success:
            messagebox.showinfo("Success", message)
            self.show_manage()
        else:
            messagebox.showwarning("Info", message)
    
    def advance_round(self):
        """Advance to next round"""
        success, message = self.app.advance_round()
        if success:
            messagebox.showinfo("Success", message)
            self.show_manage()
        else:
            messagebox.showerror("Error", message)
    
    def finish_tournament(self):
        """Finish the tournament"""
        if not messagebox.askyesno("Confirm", "Mark this tournament as finished?"):
            return
        
        success, message = self.app.finish_tournament()
        if success:
            self.show_victory_screen()
        else:
            messagebox.showerror("Error", message)
    
    def export_standings(self):
        """Export standings to CSV"""
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("CSV Files", "*.csv")])
        if path:
            success, message = self.app.export_standings(path)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
