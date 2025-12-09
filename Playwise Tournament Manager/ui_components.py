"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ UI COMPONENTS MODULE                                                      ║
║ Developer: Deepak Bisht (S25CSEU0986)                                     ║
║ Role: User interface, MVP display, K/D stats, forms, and victory screen   ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random

from config import COLORS, GAME_CONFIGS, FORMATS, WINDOW_WIDTH, WINDOW_HEIGHT
from data_models import Participant
from tournament_logic import TournamentEngine
from analytics import LeaderboardSystem, AnalyticsEngine


# ==============================================================================
# UI MANAGER
# ==============================================================================

class UIManager:
    """Manages all screens and user interactions"""
    
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.sheet_entries = []
        
        self.setup_styles()
        self.create_layout()
        self.show_home()
    
    def setup_styles(self):
        """Configure UI colors and fonts"""
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_main"])
        style.configure("TButton", background=COLORS["accent"], font=("Arial", 10, "bold"))
        
        style.configure("Treeview", background=COLORS["bg_card"], foreground=COLORS["text_main"], 
                       fieldbackground=COLORS["bg_card"], rowheight=30)
        style.configure("Treeview.Heading", background=COLORS["accent"], foreground="white", 
                       font=("Arial", 10, "bold"))
    
    def create_layout(self):
        """Create sidebar and main area"""
        
        # Sidebar
        sidebar = ttk.Frame(self.root, width=200)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        tk.Label(sidebar, text="⚡ PLAYWISE", font=("Impact", 24), 
                bg=COLORS["bg_dark"], fg=COLORS["accent"]).pack(pady=20)
        
        self.btn_home = tk.Button(sidebar, text="🏠 Dashboard", command=self.show_home,
                                  bg=COLORS["accent"], fg="white", font=("Arial", 11), 
                                  width=18, pady=10, relief="flat", cursor="hand2")
        self.btn_home.pack(pady=5)
        
        self.btn_create = tk.Button(sidebar, text="➕ New Tournament", command=self.show_create,
                                    bg=COLORS["accent"], fg="white", font=("Arial", 11), 
                                    width=18, pady=10, relief="flat", cursor="hand2")
        self.btn_create.pack(pady=5)
        
        self.btn_manage = tk.Button(sidebar, text="⚙️ Manage", command=self.show_manage,
                                    bg=COLORS["accent"], fg="white", font=("Arial", 11), 
                                    width=18, pady=10, relief="flat", cursor="hand2", state="disabled")
        self.btn_manage.pack(pady=5)
        
        # Main area
        self.main_area = ttk.Frame(self.root)
        self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    
    def clear_main(self):
        """Clear main area"""
        for widget in self.main_area.winfo_children():
            widget.destroy()
    
    # ==========================================================================
    # HOME SCREEN
    # ==========================================================================
    
    def show_home(self):
        """Show tournament dashboard"""
        self.clear_main()
        self.app.current_tournament = None
        self.btn_manage.config(state="disabled")
        
        tk.Label(self.main_area, text="Tournament Dashboard", font=("Arial", 20, "bold"),
                bg=COLORS["bg_dark"], fg=COLORS["accent"]).pack(anchor="w", pady=20)
        
        if not self.app.tournaments:
            tk.Label(self.main_area, text="No tournaments yet. Create one to get started!",
                    font=("Arial", 14), bg=COLORS["bg_dark"], fg=COLORS["text_sub"]).pack(pady=50)
            return
        
        # Tournament table
        cols = ("name", "game", "format", "round", "status")
        tree = ttk.Treeview(self.main_area, columns=cols, show="headings", height=15)
        
        tree.heading("name", text="Tournament Name")
        tree.heading("game", text="Game")
        tree.heading("format", text="Format")
        tree.heading("round", text="Round")
        tree.heading("status", text="Status")
        
        tree.column("name", width=300)
        tree.column("game", width=150)
        tree.column("format", width=100)
        tree.column("round", width=80)
        tree.column("status", width=100)
        
        for t in self.app.tournaments.values():
            status = "🏆 Finished" if t.finished else "⚡ Active"
            tree.insert("", "end", values=(t.name, t.game, t.format, f"R{t.current_round}", status), iid=t.id)
        
        tree.pack(fill="both", expand=True, pady=10)
        tree.bind("<Double-1>", lambda e: self.load_tournament(tree))
        
        # Buttons
        btn_frame = ttk.Frame(self.main_area)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Load Selected", command=lambda: self.load_tournament(tree),
                 bg=COLORS["success"], fg="white", font=("Arial", 10), padx=20, pady=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=lambda: self.delete_tournament(tree),
                 bg=COLORS["danger"], fg="white", font=("Arial", 10), padx=20, pady=8).pack(side="left", padx=5)
    
    def load_tournament(self, tree):
        """Load selected tournament"""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a tournament")
            return
        
        self.app.current_tournament = self.app.tournaments[sel[0]]
        self.btn_manage.config(state="normal")
        self.show_manage()
    
    def delete_tournament(self, tree):
        """Delete selected tournament"""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a tournament")
            return
        
        if messagebox.askyesno("Confirm", "Delete this tournament?"):
            del self.app.tournaments[sel[0]]
            self.app.save_data()
            self.show_home()
    
    # ==========================================================================
    # CREATE TOURNAMENT SCREEN
    # ==========================================================================
    
    def show_create(self):
        """Show tournament creation form"""
        self.clear_main()
        
        tk.Label(self.main_area, text="Create New Tournament", font=("Arial", 20, "bold"),
                bg=COLORS["bg_dark"], fg=COLORS["accent"]).pack(anchor="w", pady=20)
        
        # Form
        form = ttk.Frame(self.main_area)
        form.pack(fill="x", pady=10)
        
        tk.Label(form, text="Tournament Name:", bg=COLORS["bg_dark"], fg=COLORS["text_main"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        name_entry = tk.Entry(form, width=30, font=("Arial", 11))
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(form, text="Game:", bg=COLORS["bg_dark"], fg=COLORS["text_main"]).grid(row=0, column=2, sticky="w", padx=10, pady=10)
        game_combo = ttk.Combobox(form, values=list(GAME_CONFIGS.keys()), state="readonly", width=20)
        game_combo.current(0)
        game_combo.grid(row=0, column=3, padx=10, pady=10)
        
        tk.Label(form, text="Format:", bg=COLORS["bg_dark"], fg=COLORS["text_main"]).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        format_combo = ttk.Combobox(form, values=FORMATS, state="readonly", width=28)
        format_combo.current(0)
        format_combo.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(form, text="Players:", bg=COLORS["bg_dark"], fg=COLORS["text_main"]).grid(row=1, column=2, sticky="w", padx=10, pady=10)
        count_entry = tk.Entry(form, width=10, font=("Arial", 11))
        count_entry.insert(0, "4")
        count_entry.grid(row=1, column=3, sticky="w", padx=10, pady=10)
        
        # Info label
        info_label = tk.Label(form, text="", bg=COLORS["bg_dark"], fg=COLORS["warning"], 
                             font=("Arial", 9, "italic"), wraplength=800)
        info_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=10, pady=5)
        
        def update_info(event=None):
            game = game_combo.get()
            conf = GAME_CONFIGS[game]
            info_label.config(text=f"💡 {conf['desc']}")
        
        game_combo.bind("<<ComboboxSelected>>", update_info)
        update_info()
        
        # Generate button
        tk.Button(form, text="Generate Player Sheet", command=lambda: self.generate_sheet(game_combo, count_entry, sheet_frame),
                 bg=COLORS["accent"], fg="white", font=("Arial", 10), padx=20, pady=8).grid(row=3, column=0, columnspan=4, pady=15)
        
        # Sheet area
        sheet_container = ttk.Frame(self.main_area)
        sheet_container.pack(fill="both", expand=True, pady=10)
        
        canvas = tk.Canvas(sheet_container, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(sheet_container, orient="vertical", command=canvas.yview)
        sheet_frame = ttk.Frame(canvas)
        
        sheet_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sheet_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create button
        tk.Button(self.main_area, text="✅ Create Tournament", 
                 command=lambda: self.save_tournament(name_entry, game_combo, format_combo),
                 bg=COLORS["success"], fg="white", font=("Arial", 12, "bold"), 
                 padx=30, pady=12).pack(pady=20)
    
    def generate_sheet(self, game_combo, count_entry, sheet_frame):
        """Generate player entry fields"""
        for widget in sheet_frame.winfo_children():
            widget.destroy()
        self.sheet_entries = []
        
        try:
            count = int(count_entry.get())
            if count < 2 or count > 128:
                messagebox.showwarning("Invalid", "Enter 2-128 players")
                return
        except:
            messagebox.showerror("Error", "Enter valid number")
            return
        
        game = game_combo.get()
        config = GAME_CONFIGS[game]
        
        # Headers
        headers = ["#", "Name"]
        if config['has_elo']:
            headers.append("Elo")
        if config['has_roles']:
            headers.append("Team")
            headers.append("Role")
        
        for col, text in enumerate(headers):
            tk.Label(sheet_frame, text=text, bg=COLORS["accent"], fg="white", 
                    font=("Arial", 9, "bold"), padx=10, pady=8).grid(row=0, column=col, sticky="ew", padx=1, pady=1)
        
        # Entry rows
        for i in range(count):
            row_data = {}
            
            tk.Label(sheet_frame, text=str(i+1), bg=COLORS["bg_card"], fg=COLORS["text_sub"], width=4).grid(row=i+1, column=0, padx=1, pady=1)
            
            col_idx = 1
            
            e_name = tk.Entry(sheet_frame, width=25, font=("Arial", 10))
            e_name.grid(row=i+1, column=col_idx, padx=1, pady=1)
            row_data['name'] = e_name
            col_idx += 1
            
            if config['has_elo']:
                e_elo = tk.Entry(sheet_frame, width=12, font=("Arial", 10))
                e_elo.insert(0, "1000")
                e_elo.grid(row=i+1, column=col_idx, padx=1, pady=1)
                row_data['elo'] = e_elo
                col_idx += 1
            
            if config['has_roles']:
                e_team = tk.Entry(sheet_frame, width=20, font=("Arial", 10))
                e_team.grid(row=i+1, column=col_idx, padx=1, pady=1)
                row_data['team'] = e_team
                col_idx += 1
                
                e_role = ttk.Combobox(sheet_frame, values=config['roles'], state="readonly", width=18)
                if config['roles']:
                    e_role.current(0)
                e_role.grid(row=i+1, column=col_idx, padx=1, pady=1)
                row_data['role'] = e_role
                col_idx += 1
            
            self.sheet_entries.append(row_data)
    
    def save_tournament(self, name_entry, game_combo, format_combo):
        """Create and save tournament"""
        name = name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter tournament name")
            return
        
        if not self.sheet_entries:
            messagebox.showerror("Error", "Generate player sheet first")
            return
        
        # Collect participants
        participants = []
        for entry_row in self.sheet_entries:
            pname = entry_row['name'].get().strip()
            if not pname:
                continue
            
            pdata = {'name': pname}
            pdata['rating'] = int(entry_row['elo'].get()) if 'elo' in entry_row else 1000
            pdata['team'] = entry_row['team'].get().strip() if 'team' in entry_row else ""
            pdata['role'] = entry_row['role'].get() if 'role' in entry_row else ""
            
            participants.append(pdata)
        
        success, msg = self.app.create_tournament(name, game_combo.get(), format_combo.get(), participants)
        
        if success:
            messagebox.showinfo("Success", msg)
            self.btn_manage.config(state="normal")
            self.show_manage()
        else:
            messagebox.showerror("Error", msg)
    
    # ==========================================================================
    # MANAGE TOURNAMENT SCREEN
    # ==========================================================================
    
    def show_manage(self):
        """Show tournament management"""
        self.clear_main()
        
        if not self.app.current_tournament:
            self.show_home()
            return
        
        t = self.app.current_tournament
        
        if t.finished:
            self.show_victory()
            return
        
        # Header
        tk.Label(self.main_area, text=t.name, font=("Arial", 20, "bold"),
                bg=COLORS["bg_dark"], fg=COLORS["accent"]).pack(anchor="w", pady=10)
        
        info = f"{t.game} | {t.format} | Round {t.current_round}"
        tk.Label(self.main_area, text=info, bg=COLORS["accent"], fg="white",
                font=("Arial", 11, "bold"), padx=15, pady=8).pack(anchor="w", pady=5)
        
        # Tabs
        notebook = ttk.Notebook(self.main_area)
        notebook.pack(fill="both", expand=True, pady=10)
        
        self.create_leaderboard_tab(notebook, t)
        self.create_matches_tab(notebook, t)
        self.create_stats_tab(notebook, t)
    
    def create_leaderboard_tab(self, notebook, tournament):
        """Create leaderboard tab with MVP and K/D"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="🏆 Leaderboard")
        
        leaderboard = LeaderboardSystem.get_leaderboard(tournament)
        config = GAME_CONFIGS[tournament.game]
        is_shooter = AnalyticsEngine.is_shooter_game(tournament.game)
        
        # Build columns
        cols = ["rank", "name", "played", "won", "drawn", "lost", "pts", "mvps"]
        
        if is_shooter:
            cols.extend(["kills", "deaths", "kd"])
        else:
            cols.extend(["gf", "ga", "gd"])
        
        if config['has_elo']:
            cols.insert(2, "elo")
        if config['has_roles']:
            cols.insert(2, "team")
        
        tree = ttk.Treeview(tab, columns=cols, show="headings", height=15)
        
        # Headers
        tree.heading("rank", text="Rank")
        tree.heading("name", text="Player/Team")
        if "elo" in cols:
            tree.heading("elo", text="Elo")
        if "team" in cols:
            tree.heading("team", text="Team")
        tree.heading("played", text="P")
        tree.heading("won", text="W")
        tree.heading("drawn", text="D")
        tree.heading("lost", text="L")
        tree.heading("pts", text="Pts")
        tree.heading("mvps", text="⭐ MVPs")
        
        if is_shooter:
            tree.heading("kills", text="K")
            tree.heading("deaths", text="D")
            tree.heading("kd", text="K/D")
        else:
            tree.heading("gf", text="GF")
            tree.heading("ga", text="GA")
            tree.heading("gd", text="GD")
        
        # Column widths
        tree.column("rank", width=60, anchor="center")
        tree.column("name", width=180, anchor="w")
        if "elo" in cols:
            tree.column("elo", width=70, anchor="center")
        if "team" in cols:
            tree.column("team", width=110, anchor="center")
        for c in ["played", "won", "drawn", "lost", "pts", "mvps"]:
            tree.column(c, width=50, anchor="center")
        
        if is_shooter:
            for c in ["kills", "deaths", "kd"]:
                tree.column(c, width=60, anchor="center")
        else:
            for c in ["gf", "ga", "gd"]:
                tree.column(c, width=60, anchor="center")
        
        # Data
        for entry in leaderboard:
            rank_text = f"{entry['medal']} {entry['rank']}" if entry['medal'] else entry['rank']
            
            vals = [rank_text, entry['name'], entry['played'], entry['won'], 
                   entry['drawn'], entry['lost'], entry['points'], entry['mvp_count']]
            
            if is_shooter:
                vals.extend([entry['kills'], entry['deaths'], entry['kd']])
            else:
                vals.extend([entry['gf'], entry['ga'], entry['gd']])
            
            if "elo" in cols:
                vals.insert(2, entry['rating'])
            if "team" in cols:
                vals.insert(2, entry['team'])
            
            tree.insert("", "end", values=vals)
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Button(tab, text="📤 Export CSV", command=self.export_csv,
                 bg=COLORS["accent"], fg="white", font=("Arial", 10), padx=20, pady=8).pack(pady=10)
    
    def create_stats_tab(self, notebook, tournament):
        """Create statistics tab with MVP leaderboard"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📊 Statistics")
        
        # Tournament stats
        stats = AnalyticsEngine.get_stats(tournament)
        is_shooter = AnalyticsEngine.is_shooter_game(tournament.game)
        
        stats_frame = tk.Frame(tab, bg=COLORS["bg_card"], padx=20, pady=15)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(stats_frame, text="Tournament Statistics", font=("Arial", 16, "bold"),
                bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 10))
        
        info_text = f"""
📊 Total Matches: {stats['completed_matches']} / {stats['total_matches']}
⏳ Pending: {stats['pending_matches']}
⚽ Total Scores: {stats['total_goals']}
📈 Average per Match: {stats['avg_goals']}
⭐ MVP Matches: {stats['mvp_matches']}
🏆 Tournament MVP: {stats['tournament_mvp']}
        """
        
        tk.Label(stats_frame, text=info_text, font=("Arial", 11), bg=COLORS["bg_card"],
                fg=COLORS["text_main"], justify="left").pack(anchor="w")
        
        # MVP Leaderboard
        mvp_frame = tk.Frame(tab, bg=COLORS["bg_card"], padx=20, pady=15)
        mvp_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(mvp_frame, text="⭐ MVP Leaderboard", font=("Arial", 14, "bold"),
                bg=COLORS["bg_card"], fg=COLORS["gold"]).pack(pady=(0, 10))
        
        mvp_board = LeaderboardSystem.get_mvp_leaderboard(tournament)
        
        if mvp_board:
            mvp_cols = ("rank", "name", "team", "mvps", "matches")
            mvp_tree = ttk.Treeview(mvp_frame, columns=mvp_cols, show="headings", height=10)
            
            mvp_tree.heading("rank", text="Rank")
            mvp_tree.heading("name", text="Player")
            mvp_tree.heading("team", text="Team")
            mvp_tree.heading("mvps", text="⭐ MVP Awards")
            mvp_tree.heading("matches", text="Matches")
            
            mvp_tree.column("rank", width=60, anchor="center")
            mvp_tree.column("name", width=200, anchor="w")
            mvp_tree.column("team", width=150, anchor="center")
            mvp_tree.column("mvps", width=120, anchor="center")
            mvp_tree.column("matches", width=100, anchor="center")
            
            for entry in mvp_board:
                mvp_tree.insert("", "end", values=(
                    entry['rank'], entry['name'], entry['team'], 
                    entry['mvp_count'], entry['matches']
                ))
            
            mvp_tree.pack(fill="both", expand=True)
        else:
            tk.Label(mvp_frame, text="No MVP data yet. Play some matches!",
                    bg=COLORS["bg_card"], fg=COLORS["text_sub"], font=("Arial", 11)).pack(pady=20)
        
        # K/D Leaderboard for shooters
        if is_shooter:
            kd_frame = tk.Frame(tab, bg=COLORS["bg_card"], padx=20, pady=15)
            kd_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            tk.Label(kd_frame, text="🎯 K/D Leaderboard", font=("Arial", 14, "bold"),
                    bg=COLORS["bg_card"], fg=COLORS["success"]).pack(pady=(0, 10))
            
            kd_board = LeaderboardSystem.get_kd_leaderboard(tournament)
            
            if kd_board:
                kd_cols = ("rank", "name", "team", "kills", "deaths", "kd")
                kd_tree = ttk.Treeview(kd_frame, columns=kd_cols, show="headings", height=10)
                
                kd_tree.heading("rank", text="Rank")
                kd_tree.heading("name", text="Player")
                kd_tree.heading("team", text="Team")
                kd_tree.heading("kills", text="Kills")
                kd_tree.heading("deaths", text="Deaths")
                kd_tree.heading("kd", text="K/D Ratio")
                
                kd_tree.column("rank", width=60, anchor="center")
                kd_tree.column("name", width=200, anchor="w")
                kd_tree.column("team", width=150, anchor="center")
                kd_tree.column("kills", width=100, anchor="center")
                kd_tree.column("deaths", width=100, anchor="center")
                kd_tree.column("kd", width=100, anchor="center")
                
                for entry in kd_board:
                    kd_tree.insert("", "end", values=(
                        entry['rank'], entry['name'], entry['team'],
                        entry['kills'], entry['deaths'], entry['kd']
                    ))
                
                kd_tree.pack(fill="both", expand=True)
    
    def create_matches_tab(self, notebook, tournament):
        """Create matches tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⚔️ Matches")
        
        # Toolbar
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", padx=10, pady=10)
        
        tk.Button(toolbar, text="🎲 Generate Fixtures", command=self.generate_fixtures,
                 bg=COLORS["accent"], fg="white", font=("Arial", 10), padx=15, pady=8).pack(side="left", padx=5)
        tk.Button(toolbar, text="⏭️ Next Round", command=self.advance_round,
                 bg=COLORS["accent"], fg="white", font=("Arial", 10), padx=15, pady=8).pack(side="left", padx=5)
        tk.Button(toolbar, text="🏁 Finish", command=self.finish_tournament,
                 bg=COLORS["success"], fg="white", font=("Arial", 10), padx=15, pady=8).pack(side="right", padx=5)
        
        # Matches
        self.render_matches(tab, tournament)
    
    def render_matches(self, parent, tournament):
        """Display match list with MVP"""
        canvas = tk.Canvas(parent, bg=COLORS["bg_dark"], highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)
        
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scroll.pack(side="right", fill="y")
        
        matches = tournament.get_current_matches()
        
        if not matches:
            tk.Label(frame, text="No matches. Click 'Generate Fixtures'", 
                    font=("Arial", 14), bg=COLORS["bg_dark"], fg=COLORS["text_sub"]).pack(pady=50)
            return
        
        for match in matches:
            self.create_match_card(frame, match, tournament)
    
    def create_match_card(self, parent, match, tournament):
        """Create match display card with MVP"""
        card = tk.Frame(parent, bg=COLORS["bg_card"], padx=15, pady=12)
        card.pack(fill="x", pady=5, padx=10)
        
        p1 = tournament.participants[match.player1_id]
        p2_name = tournament.participants[match.player2_id].name if match.player2_id else "🎁 BYE"
        
        match_text = f"{p1.name}  vs  {p2_name}"
        tk.Label(card, text=match_text, font=("Arial", 13), bg=COLORS["bg_card"], 
                fg=COLORS["text_main"]).pack(side="left")
        
        if match.played:
            score = f"  [{match.score1} - {match.score2}]"
            tk.Label(card, text=score, font=("Arial", 13, "bold"), bg=COLORS["bg_card"], 
                    fg=COLORS["success"]).pack(side="left", padx=10)
            
            # NEW: Show MVP
            if match.mvp_name:
                mvp_label = f"⭐ MVP: {match.mvp_name}"
                tk.Label(card, text=mvp_label, font=("Arial", 10, "italic"), bg=COLORS["bg_card"],
                        fg=COLORS["gold"]).pack(side="left", padx=10)
        
        elif match.player2_id:
            btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
            btn_frame.pack(side="right")
            
            tk.Button(btn_frame, text="P1 Win", command=lambda: self.record_result(match.id, 1, 0),
                     bg=COLORS["success"], fg="white", font=("Arial", 9), padx=12, pady=6).pack(side="left", padx=2)
            tk.Button(btn_frame, text="P2 Win", command=lambda: self.record_result(match.id, 0, 1),
                     bg=COLORS["danger"], fg="white", font=("Arial", 9), padx=12, pady=6).pack(side="left", padx=2)
            
            config = GAME_CONFIGS[tournament.game]
            if config['allows_draw'] and tournament.format != "Knockout":
                tk.Button(btn_frame, text="Draw", command=lambda: self.record_result(match.id, 1, 1),
                         bg=COLORS["warning"], fg="black", font=("Arial", 9), padx=12, pady=6).pack(side="left", padx=2)
    
    def record_result(self, match_id, score1, score2):
        """Record match result"""
        success = TournamentEngine.record_result(self.app.current_tournament, match_id, score1, score2)
        if success:
            self.app.save_data()
            self.show_manage()
        else:
            messagebox.showerror("Error", "Cannot record result")
    
    # ==========================================================================
    # VICTORY SCREEN
    # ==========================================================================
    
    def show_victory(self):
        """Show tournament finished screen with MVP"""
        self.clear_main()
        t = self.app.current_tournament
        
        victory_frame = tk.Frame(self.main_area, bg=COLORS["bg_card"], padx=40, pady=40)
        victory_frame.pack(fill="both", expand=True)
        
        messages = ["🏆 CHAMPION! 🏆", "👑 VICTORY! 👑", "⭐ WINNER! ⭐"]
        title = random.choice(messages)
        tk.Label(victory_frame, text=title, font=("Impact", 36), bg=COLORS["bg_card"], 
                fg=COLORS["gold"]).pack(pady=20)
        
        winner = LeaderboardSystem.get_winner(t)
        if winner:
            tk.Label(victory_frame, text=winner.name, font=("Arial", 28, "bold"),
                    bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=10)
            
            stats = f"{winner.won}W - {winner.drawn}D - {winner.lost}L | {winner.points} Points"
            tk.Label(victory_frame, text=stats, font=("Arial", 14), bg=COLORS["bg_card"], 
                    fg=COLORS["text_main"]).pack(pady=5)
            
            # NEW: Show MVP count
            if winner.mvp_count > 0:
                mvp_text = f"⭐ {winner.mvp_count} MVP Awards"
                tk.Label(victory_frame, text=mvp_text, font=("Arial", 12, "italic"), 
                        bg=COLORS["bg_card"], fg=COLORS["gold"]).pack(pady=5)
        
        tk.Label(victory_frame, text="🏆 PODIUM 🏆", font=("Arial", 18, "bold"),
                bg=COLORS["bg_card"], fg=COLORS["accent"]).pack(pady=30)
        
        podium_frame = tk.Frame(victory_frame, bg=COLORS["bg_card"])
        podium_frame.pack()
        
        top_three = LeaderboardSystem.get_top_three(t)
        medal_colors = {1: COLORS["gold"], 2: COLORS["silver"], 3: COLORS["bronze"]}
        
        for i, p in enumerate(top_three, 1):
            card = tk.Frame(podium_frame, bg=COLORS["bg_card"], padx=20, pady=15)
            card.pack(side="left", padx=15)
            
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}[i]
            tk.Label(card, text=medal, font=("Arial", 48), bg=COLORS["bg_card"]).pack()
            tk.Label(card, text=f"#{i}", font=("Arial", 16), bg=COLORS["bg_card"], 
                    fg=medal_colors[i]).pack()
            tk.Label(card, text=p.name, font=("Arial", 14, "bold"), bg=COLORS["bg_card"], 
                    fg=COLORS["text_main"]).pack()
            tk.Label(card, text=f"{p.points} pts", bg=COLORS["bg_card"], 
                    fg=COLORS["text_sub"]).pack()
            
            # NEW: Show MVP count
            if p.mvp_count > 0:
                tk.Label(card, text=f"⭐ {p.mvp_count} MVPs", font=("Arial", 9),
                        bg=COLORS["bg_card"], fg=COLORS["gold"]).pack()
        
        btn_frame = tk.Frame(victory_frame, bg=COLORS["bg_card"])
        btn_frame.pack(pady=30)
        
        tk.Button(btn_frame, text="🏠 Dashboard", command=self.show_home,
                 bg=COLORS["accent"], fg="white", font=("Arial", 11), padx=20, pady=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📤 Export", command=self.export_csv,
                 bg=COLORS["success"], fg="white", font=("Arial", 11), padx=20, pady=10).pack(side="left", padx=5)
    
    # ==========================================================================
    # ACTIONS
    # ==========================================================================
    
    def generate_fixtures(self):
        """Generate matches"""
        success = TournamentEngine.generate_fixtures(self.app.current_tournament)
        if success:
            self.app.save_data()
            self.show_manage()
        else:
            messagebox.showinfo("Info", "Fixtures already generated")
    
    def advance_round(self):
        """Move to next round"""
        success = TournamentEngine.advance_round(self.app.current_tournament)
        if success:
            self.app.save_data()
            if self.app.current_tournament.finished:
                self.show_victory()
            else:
                self.show_manage()
        else:
            messagebox.showerror("Error", "Complete all matches first")
    
    def finish_tournament(self):
        """Mark tournament finished"""
        if messagebox.askyesno("Confirm", "Finish this tournament?"):
            self.app.current_tournament.finished = True
            self.app.save_data()
            self.show_victory()
    
    def export_csv(self):
        """Export to CSV"""
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if path:
            success = AnalyticsEngine.export_csv(self.app.current_tournament, path)
            if success:
                messagebox.showinfo("Success", "Exported successfully!")
            else:
                messagebox.showerror("Error", "Export failed")
