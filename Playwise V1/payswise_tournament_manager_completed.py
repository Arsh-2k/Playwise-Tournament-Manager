import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import uuid
import os
import random
import csv
from datetime import datetime

# ==============================================================================
# SECTION 1: CONFIGURATION & ASSETS
# ==============================================================================

# File path for saving data
DATA_FILE = "playwise_data.json"

# UI Color Palette (Dark Theme / Esports Style)
COLORS = {
    "bg_dark": "#1e1e2e",      # Main Background
    "bg_panel": "#313244",     # Card/Panel Background
    "accent": "#89b4fa",       # Primary Blue
    "accent_hov": "#b4befe",   # Lighter Blue (Hover)
    "text_main": "#cdd6f4",    # Primary Text
    "text_sub": "#a6adc8",     # Secondary Text
    "success": "#a6e3a1",      # Green
    "danger": "#f38ba8",       # Red
    "warning": "#f9e2af",      # Yellow
    "header": "#45475a"        # Table Headers
}

# Intelligent Game Configurations (Expanded for EWC 2025)
GAME_CONFIGS = {
    # --- MOBA ---
    "League of Legends": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["Top", "Jungle", "Mid", "ADC", "Support"],
        "role_constraints": {}, 
        "rec_format": "Knockout", "rec_limit": "8 - 16 Teams",
        "official_label": "Referee", "tiebreaker": "Silver Scrapes (Decider Game)",
        "desc": "5v5 MOBA. Standard Summoner's Rift rules."
    },
    "Dota 2": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["Carry", "Mid", "Offlane", "Soft Supp", "Hard Supp"],
        "role_constraints": {},
        "rec_format": "Knockout", "rec_limit": "8 - 16 Teams",
        "official_label": "Admin", "tiebreaker": "Bo3 Decider",
        "desc": "5v5 MOBA. Captain's Mode."
    },
    
    # --- FPS ---
    "Counter-Strike 2": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["IGL", "AWPer", "Rifler", "Entry", "Support"],
        "role_constraints": {"IGL": 1},
        "rec_format": "Swiss", "rec_limit": "16 Teams",
        "official_label": "Admin", "tiebreaker": "MR12 Overtime",
        "desc": "Tactical Shooter. MR12 format recommended."
    },
    "Valorant": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["IGL", "Duelist", "Controller", "Initiator", "Sentinel"],
        "role_constraints": {"IGL": 1},
        "rec_format": "Knockout", "rec_limit": "8 - 16 Teams",
        "official_label": "Observer", "tiebreaker": "Overtime (Win by 2)",
        "desc": "5v5 Tactical Shooter."
    },
    "Rainbow Six Siege": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["IGL", "Entry", "Flex", "Support", "Roamer"],
        "role_constraints": {},
        "rec_format": "League", "rec_limit": "8 Teams",
        "official_label": "Admin", "tiebreaker": "Overtime Match Point",
        "desc": "5v5 Tactical Shooter."
    },

    # --- BATTLE ROYALE ---
    "Apex Legends": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["IGL", "Fragger", "Anchor"], # 3-man squads
        "role_constraints": {"IGL": 1},
        "rec_format": "League", "rec_limit": "20 Teams",
        "official_label": "Admin", "tiebreaker": "Total Kills",
        "desc": "Trios Battle Royale. Points for placement + kills."
    },
    "PUBG / BGMI": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["IGL", "Assaulter", "Sniper", "Support"],
        "role_constraints": {"IGL": 1},
        "rec_format": "League", "rec_limit": "16 Teams",
        "official_label": "Admin", "tiebreaker": "Kill Points",
        "desc": "Squad Battle Royale."
    },
    "Fortnite": {
        "type": "individual", "has_elo": False, "has_roles": False, # Usually duos/solos
        "roles": [],
        "role_constraints": {},
        "rec_format": "League", "rec_limit": "100 Players",
        "official_label": "Admin", "tiebreaker": "Victory Royales",
        "desc": "Battle Royale. Supports Solos/Duos."
    },

    # --- FIGHTING GAMES ---
    "Street Fighter 6": {
        "type": "individual", "has_elo": True, "has_roles": False,
        "roles": [], "role_constraints": {},
        "rec_format": "Knockout", "rec_limit": "Double Elimination",
        "official_label": "TO", "tiebreaker": "Final Round",
        "desc": "1v1 Fighting Game. First to 2 or 3."
    },
    "Tekken 8": {
        "type": "individual", "has_elo": True, "has_roles": False,
        "roles": [], "role_constraints": {},
        "rec_format": "Knockout", "rec_limit": "Double Elimination",
        "official_label": "TO", "tiebreaker": "Final Round",
        "desc": "1v1 Fighting Game."
    },

    # --- SPORTS/STRATEGY ---
    "Rocket League": {
        "type": "team", "has_elo": False, "has_roles": False,
        "roles": [], "role_constraints": {},
        "rec_format": "Knockout", "rec_limit": "3v3 Teams",
        "official_label": "Admin", "tiebreaker": "Golden Goal Overtime",
        "desc": "Car Soccer. Standard 3v3."
    },
    "Chess": {
        "type": "individual", "has_elo": True, "has_roles": False,
        "roles": [], "role_constraints": {},
        "rec_format": "Swiss", "rec_limit": "Unlimited",
        "official_label": "Arbiter", "tiebreaker": "Armageddon / Blitz",
        "desc": "Classic Strategy. Elo is key for pairings."
    },
    "Cricket": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["Captain", "Batsman", "Bowler", "All-Rounder", "WK"],
        "role_constraints": {"Captain": 1, "WK": 1},
        "rec_format": "Knockout", "rec_limit": "16 Teams",
        "default_count": 11,
        "official_label": "Umpire", "tiebreaker": "Super Over",
        "desc": "Gentleman's Game."
    },
    "Football": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["Captain", "Striker", "Mid", "Def", "GK"],
        "role_constraints": {"Captain": 1, "GK": 1},
        "rec_format": "League", "rec_limit": "20 Teams",
        "official_label": "Referee", "tiebreaker": "Penalties",
        "desc": "The Beautiful Game."
    },

    # --- CUSTOM ---
    "Custom (1v1)": {
        "type": "individual", "has_elo": True, "has_roles": False,
        "roles": [], "role_constraints": {},
        "rec_format": "Any", "rec_limit": "Any",
        "official_label": "Official", "tiebreaker": "Sudden Death",
        "desc": "Generic 1v1 format with Elo rating."
    },
    "Custom (Team)": {
        "type": "team", "has_elo": False, "has_roles": True,
        "roles": ["Captain", "Player", "Sub"],
        "role_constraints": {"Captain": 1},
        "rec_format": "Any", "rec_limit": "Any",
        "official_label": "Official", "tiebreaker": "Sudden Death",
        "desc": "Generic Team format with roles."
    }
}

# ==============================================================================
# SECTION 2: DATA MODELS
# ==============================================================================

class Participant:
    """Stores data for a single player or team."""
    def __init__(self, name, rating=1000, role="", team="", p_id=None, active=True, 
                 matches=0, won=0, drawn=0, lost=0, points=0.0, s_for=0, s_against=0):
        self.id = p_id if p_id else str(uuid.uuid4())
        self.name = name
        self.rating = int(rating) if str(rating).isdigit() else 1000
        self.role = role
        self.team = team 
        self.active = active
        self.matches_played = matches
        self.won = won
        self.drawn = drawn
        self.lost = lost
        self.points = points
        self.score_for = s_for
        self.score_against = s_against

    @property
    def score_diff(self):
        return self.score_for - self.score_against

    def to_dict(self):
        return self.__dict__

class Match:
    """Stores data for a single match."""
    def __init__(self, p1_id, p2_id, round_num, m_id=None, is_played=False, p1_score=0, p2_score=0):
        self.id = m_id if m_id else str(uuid.uuid4())
        self.p1_id = p1_id
        self.p2_id = p2_id # If None, this is a BYE (Automatic win)
        self.round = round_num
        self.is_played = is_played
        self.p1_score = p1_score
        self.p2_score = p2_score

    def is_bye(self):
        return self.p2_id is None

    def to_dict(self):
        return self.__dict__

class Tournament:
    """The main container for all tournament data."""
    def __init__(self, name, game_type, format_type, t_id=None, current_round=1, is_finished=False, created_at=None, referees=None):
        self.id = t_id if t_id else str(uuid.uuid4())
        self.name = name
        self.game_type = game_type
        self.format_type = format_type
        self.current_round = current_round
        self.is_finished = is_finished
        self.created_at = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M")
        self.referees = referees if referees else []
        self.participants = {} # Dict: ID -> Participant
        self.matches = []      # List: Match objects

    def get_active_participants(self):
        """Returns active players sorted by Points, then Rating (Elo)."""
        return sorted([p for p in self.participants.values() if p.active], 
                      key=lambda x: (x.points, x.rating), reverse=True)

    def get_winner(self):
        if not self.is_finished: return None
        standings = self.get_active_participants()
        return standings[0] if standings else None

    def get_current_matches(self):
        return [m for m in self.matches if m.round == self.current_round]
    
    def get_matches_by_round(self, r):
        return [m for m in self.matches if m.round == r]

    def get_all_rounds(self):
        return max([m.round for m in self.matches], default=0)

# ==============================================================================
# SECTION 3: BUSINESS LOGIC
# ==============================================================================

class TournamentManager:
    """Handles pairing logic, scoring, and round transitions."""
    
    @staticmethod
    def generate_fixtures(tournament):
        # Prevent re-generating if matches exist for current round
        if tournament.get_current_matches(): return False
        
        active = tournament.get_active_participants()
        
        # Check for winner (Edge Case: Only 1 player left)
        if len(active) < 2:
            tournament.is_finished = True
            return False
            
        # Specific Knockout Check: Don't regen if only 2 people left and they played
        if tournament.format_type == "Knockout" and len(active) == 2 and tournament.matches:
             if any(m.round == tournament.current_round for m in tournament.matches):
                 return False

        # Seeding Logic
        if tournament.format_type == "League":
            random.shuffle(active) # Random pairings for variety
        elif tournament.format_type in ["Swiss", "Knockout"]:
            # Strong vs Strong logic (sorted by points, then rating)
            active.sort(key=lambda x: (x.points, x.rating), reverse=True)
        
        # Pairing Loop
        pool = active.copy()
        while len(pool) > 1:
            p1 = pool.pop(0)
            p2 = pool.pop(0)
            tournament.matches.append(Match(p1.id, p2.id, tournament.current_round))
        
        # BYE Handling (Odd number of players)
        if pool:
            bye_match = Match(pool[0].id, None, tournament.current_round)
            tournament.matches.append(bye_match)
            # Auto-record BYE result immediately to prevent pending state
            TournamentManager.record_result(tournament, bye_match.id, 1, 0)
        
        return True

    @staticmethod
    def record_result(tournament, match_id, s1, s2):
        match = next((m for m in tournament.matches if m.id == match_id), None)
        if not match or match.is_played: return
        
        match.p1_score, match.p2_score = s1, s2
        match.is_played = True
        
        p1 = tournament.participants[match.p1_id]
        
        # BYE Logic
        if match.is_bye():
            p1.matches_played += 1; p1.won += 1; p1.points += 1.0
            return

        p2 = tournament.participants[match.p2_id]
        p1.matches_played += 1; p2.matches_played += 1
        p1.score_for += s1; p1.score_against += s2
        p2.score_for += s2; p2.score_against += s1
        
        # Scoring Logic
        if s1 > s2:
            p1.won += 1; p2.lost += 1; p1.points += 1.0
            if tournament.format_type == "Knockout": p2.active = False
        elif s2 > s1:
            p2.won += 1; p1.lost += 1; p2.points += 1.0
            if tournament.format_type == "Knockout": p1.active = False
        else:
            # Draw
            p1.drawn += 1; p2.drawn += 1; p1.points += 0.5; p2.points += 0.5

# ==============================================================================
# SECTION 4: DATA PERSISTENCE
# ==============================================================================

class DataStore:
    """Handles saving and loading JSON data."""
    
    @staticmethod
    def save(tournaments):
        data = []
        for t in tournaments.values():
            t_dict = t.__dict__.copy()
            t_dict['participants'] = {pid: p.to_dict() for pid, p in t.participants.items()}
            t_dict['matches'] = [m.to_dict() for m in t.matches]
            data.append(t_dict)
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception: return False

    @staticmethod
    def load():
        if not os.path.exists(DATA_FILE): return {}
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            tournaments = {}
            for item in raw_data:
                # Reconstruct Tournament Object
                t = Tournament(item['name'], item['game_type'], item['format_type'], 
                             item['id'], item['current_round'], item['is_finished'])
                if 'created_at' in item: t.created_at = item['created_at']
                if 'referees' in item: t.referees = item['referees']

                # Reconstruct Participants
                for pid, p_data in item['participants'].items():
                    role = p_data.get('role', '')
                    team = p_data.get('team', '')
                    p = Participant(p_data['name'], p_data['rating'], role, team, p_data['id'], 
                                  p_data['active'], p_data['matches_played'], p_data['won'], 
                                  p_data['drawn'], p_data['lost'], p_data['points'], 
                                  p_data['score_for'], p_data['score_against'])
                    t.participants[pid] = p
                
                # Reconstruct Matches
                for m_data in item['matches']:
                    m = Match(m_data['p1_id'], m_data['p2_id'], m_data['round'], 
                            m_data['id'], m_data['is_played'], m_data['p1_score'], m_data['p2_score'])
                    t.matches.append(m)
                tournaments[t.id] = t
            return tournaments
        except Exception: return {}

# ==============================================================================
# SECTION 5: GUI HELPERS
# ==============================================================================

class StyleMixin:
    """Configures the look and feel of the application."""
    @staticmethod
    def setup_styles():
        style = ttk.Style()
        style.theme_use("clam")
        
        # General Frames
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("Card.TFrame", background=COLORS["bg_panel"])
        
        # Labels
        style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_main"], font=("Segoe UI", 11))
        style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground=COLORS["accent"])
        style.configure("Card.TLabel", background=COLORS["bg_panel"], foreground=COLORS["text_main"])
        
        # Buttons
        style.configure("TButton", padding=8, background=COLORS["accent"], foreground="#1e1e2e", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", COLORS["accent_hov"])])
        style.configure("Danger.TButton", background=COLORS["danger"], foreground="#1e1e2e")
        
        # Treeview (Tables)
        style.configure("Treeview", background=COLORS["bg_panel"], foreground=COLORS["text_main"], 
                        fieldbackground=COLORS["bg_panel"], rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=COLORS["header"], foreground="#ffffff", font=("Segoe UI", 10, "bold"))

    @staticmethod
    def create_card(parent, padding=20, **kwargs):
        """
        Returns a styled ttk.Frame. 
        FIX: Accepts **kwargs to pass 'style' or other options down to ttk.Frame, 
        resolving Pylance strict argument checking errors.
        """
        if "style" not in kwargs:
            kwargs["style"] = "Card.TFrame"
        return ttk.Frame(parent, padding=padding, **kwargs)

    @staticmethod
    def center_window(window, width, height):
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

# ==============================================================================
# SECTION 6: MAIN APPLICATION GUI
# ==============================================================================

class PlaywiseGUI(tk.Tk, StyleMixin):
    def __init__(self):
        super().__init__()
        self.title("Playwise - Esports & Sports Tournament Manager")
        self.geometry("1280x850")
        self.center_window(self, 1280, 850)
        self.configure(bg=COLORS["bg_dark"])
        
        self.tournaments = DataStore.load()
        self.current_tournament = None
        
        self.setup_styles()
        self.create_menu()
        self.create_ui()
        self.show_home()
        
    def create_menu(self):
        menubar = tk.Menu(self, bg=COLORS["bg_panel"], fg=COLORS["text_main"])
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Tournament", command=self.show_create, accelerator="Ctrl+N")
        file_menu.add_command(label="Export Standings", command=self.export_standings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        self.bind("<Control-n>", lambda e: self.show_create())

    def create_ui(self):
        # Sidebar
        self.sidebar = self.create_card(self, padding=0)
        self.sidebar.pack(side="left", fill="y")
        
        # App Logo/Title
        tk.Label(self.sidebar, text="PLAYWISE", font=("Impact", 28), 
                bg=COLORS["bg_panel"], fg=COLORS["accent"]).pack(pady=40)
        
        # Navigation Buttons
        self.create_nav_button("🏠  Dashboard", self.show_home)
        self.create_nav_button("➕  New Event", self.show_create)
        ttk.Separator(self.sidebar).pack(fill="x", pady=20, padx=20)
        self.manage_btn = self.create_nav_button("⚙️  Manage Event", self.show_manage)
        self.manage_btn.config(state="disabled")
        
        # Main Content Area
        self.main_area = ttk.Frame(self)
        self.main_area.pack(side="right", fill="both", expand=True, padx=30, pady=30)

    def create_nav_button(self, text, command):
        btn = ttk.Button(self.sidebar, text=text, command=command)
        btn.pack(fill="x", padx=20, pady=8)
        return btn

    def clear_main(self):
        for w in self.main_area.winfo_children(): w.destroy()

    # ==========================
    # VIEW: HOME DASHBOARD
    # ==========================
    def show_home(self):
        self.clear_main()
        self.current_tournament = None
        self.manage_btn.config(state="disabled")
        
        ttk.Label(self.main_area, text="Tournament Dashboard", style="Header.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Tournament List
        cols = ("name", "game", "format", "round", "status")
        tree = ttk.Treeview(self.main_area, columns=cols, show="headings", height=15)
        
        tree.heading("name", text="Event Name", anchor="w"); tree.column("name", width=250)
        tree.heading("game", text="Game", anchor="w"); tree.column("game", width=180)
        tree.heading("format", text="Format", anchor="center"); tree.column("format", width=100, anchor="center")
        tree.heading("round", text="Round", anchor="center"); tree.column("round", width=80, anchor="center")
        tree.heading("status", text="Status", anchor="center"); tree.column("status", width=100, anchor="center")
            
        for t in self.tournaments.values():
            status = "🏆 FINISHED" if t.is_finished else "⚡ ACTIVE"
            tree.insert("", "end", values=(t.name, t.game_type, t.format_type, f"R{t.current_round}", status), iid=t.id)
            
        tree.pack(fill="both", expand=True)
        tree.bind("<Double-1>", lambda e: self.load_tournament(tree))
        
        # Action Buttons
        btn_frame = ttk.Frame(self.main_area)
        btn_frame.pack(pady=20, fill="x")
        ttk.Button(btn_frame, text="Load Selected", command=lambda: self.load_tournament(tree)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Event", style="Danger.TButton", command=lambda: self.delete_tournament(tree)).pack(side="right", padx=5)

    def load_tournament(self, tree):
        sel = tree.selection()
        if not sel: return
        self.current_tournament = self.tournaments[sel[0]]
        self.manage_btn.config(state="normal")
        self.show_manage()

    def delete_tournament(self, tree):
        sel = tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this tournament?\nThis cannot be undone."):
            del self.tournaments[sel[0]]
            DataStore.save(self.tournaments)
            self.show_home()

    # ==========================
    # VIEW: CREATE TOURNAMENT
    # ==========================
    def show_create(self):
        self.clear_main()
        ttk.Label(self.main_area, text="Create New Tournament", style="Header.TLabel").pack(anchor="w", pady=(0, 20))
        
        # [Step 1] Configuration Panel
        config_frame = self.create_card(self.main_area)
        config_frame.pack(fill="x", pady=10)
        
        # Grid Layout for inputs
        ttk.Label(config_frame, text="Event Name:", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        name_entry = ttk.Entry(config_frame, width=35)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(config_frame, text="Game Title:", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=10, pady=10)
        game_cb = ttk.Combobox(config_frame, values=sorted(list(GAME_CONFIGS.keys())), state="readonly", width=25)
        game_cb.current(0)
        game_cb.grid(row=0, column=3, padx=10, pady=10)
        
        ttk.Label(config_frame, text="Format:", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        format_cb = ttk.Combobox(config_frame, values=["League", "Knockout", "Swiss"], state="readonly", width=33)
        format_cb.current(0)
        format_cb.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(config_frame, text="Count:", style="Card.TLabel").grid(row=1, column=2, sticky="w", padx=10, pady=10)
        count_entry = ttk.Entry(config_frame, width=10)
        count_entry.insert(0, "4")
        count_entry.grid(row=1, column=3, sticky="w", padx=10, pady=10)
        
        # Dynamic Help Text
        rec_label = tk.Label(config_frame, text="", bg=COLORS["bg_panel"], fg=COLORS["warning"], font=("Segoe UI", 9, "italic"))
        rec_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=10, pady=5)

        # [Step 2] Officials/Referees Panel
        ref_frame = self.create_card(self.main_area, padding=10)
        ref_frame.pack(fill="x", pady=5)
        
        official_lbl = ttk.Label(ref_frame, text="Officials:", style="Card.TLabel")
        official_lbl.pack(side="left", padx=10)
        
        ref_count_entry = ttk.Entry(ref_frame, width=5)
        ref_count_entry.insert(0, "0")
        ref_count_entry.pack(side="left")
        
        ttk.Button(ref_frame, text="Set Officials", command=lambda: generate_ref_grid()).pack(side="left", padx=10)
        
        ref_grid_frame = ttk.Frame(ref_frame, style="Card.TFrame")
        ref_grid_frame.pack(side="left", padx=10, fill="x")
        self.ref_entries = []

        # [Step 3] Spreadsheet Area
        sheet_container = ttk.Frame(self.main_area)
        sheet_container.pack(fill="both", expand=True, pady=10)
        
        # Scrollable Canvas
        canvas = tk.Canvas(sheet_container, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(sheet_container, orient="vertical", command=canvas.yview)
        sheet_frame = ttk.Frame(canvas) 
        
        sheet_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sheet_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.sheet_entries = [] 

        # --- Helper Functions for Create View ---
        def update_recommendations(event=None):
            game = game_cb.get()
            conf = GAME_CONFIGS[game]
            rec_text = f"💡 Info: {conf['rec_format']} recommended. {conf['rec_limit']}. {conf['desc']}"
            rec_label.config(text=rec_text)
            
            # Update default player count if specified (e.g., Cricket = 11)
            if "default_count" in conf:
                count_entry.delete(0, tk.END)
                count_entry.insert(0, str(conf["default_count"]))
            
            official_lbl.config(text=f"Number of {conf['official_label']}s:")

        def generate_ref_grid():
            for w in ref_grid_frame.winfo_children(): w.destroy()
            self.ref_entries = []
            try:
                cnt = int(ref_count_entry.get())
                game = game_cb.get()
                lbl = GAME_CONFIGS[game]["official_label"]
                for i in range(cnt):
                    e = ttk.Entry(ref_grid_frame, width=15)
                    e.insert(0, f"{lbl} {i+1}")
                    e.pack(side="left", padx=2)
                    self.ref_entries.append(e)
            except ValueError: pass

        def generate_spreadsheet():
            for w in sheet_frame.winfo_children(): w.destroy()
            self.sheet_entries = []
            
            try:
                count = int(count_entry.get())
                if count < 2 or count > 128:
                    messagebox.showwarning("Limit", "Please enter a number between 2 and 128.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid number.")
                return

            game = game_cb.get()
            conf = GAME_CONFIGS[game]
            
            # Headers
            headers = ["Name"]
            if conf['has_elo']: headers.append("Elo Rating")
            if conf['has_roles']: 
                headers.append("Team Name")
                headers.append("Role")
            
            for col, text in enumerate(headers):
                tk.Label(sheet_frame, text=text, bg=COLORS["header"], fg="white", 
                        width=20, font=("Segoe UI", 9, "bold")).grid(row=0, column=col, padx=1, pady=1)

            roles = conf.get('roles', [])
            
            # Generate Rows
            for i in range(count):
                row_data = {}
                e_name = ttk.Entry(sheet_frame, width=20)
                e_name.grid(row=i+1, column=0, padx=1, pady=1)
                row_data['name'] = e_name
                
                col_idx = 1
                if conf['has_elo']:
                    e_elo = ttk.Entry(sheet_frame, width=20)
                    e_elo.insert(0, "1000")
                    e_elo.grid(row=i+1, column=col_idx, padx=1, pady=1)
                    row_data['elo'] = e_elo
                    col_idx += 1
                
                if conf['has_roles']:
                    e_team = ttk.Entry(sheet_frame, width=20)
                    e_team.grid(row=i+1, column=col_idx, padx=1, pady=1)
                    row_data['team'] = e_team
                    col_idx += 1
                    e_role = ttk.Combobox(sheet_frame, values=roles, state="readonly", width=18)
                    if roles: e_role.current(0)
                    e_role.grid(row=i+1, column=col_idx, padx=1, pady=1)
                    row_data['role'] = e_role
                    col_idx += 1
                    
                self.sheet_entries.append(row_data)

        # Trigger logic
        game_cb.bind("<<ComboboxSelected>>", update_recommendations)
        ttk.Button(config_frame, text="Generate Sheet", command=generate_spreadsheet).grid(row=2, column=2, padx=10)
        
        # Initial call
        update_recommendations()
        
        def save_tournament():
            t_name = name_entry.get().strip()
            if not t_name: 
                messagebox.showerror("Error", "Tournament name required."); return
            if not self.sheet_entries:
                messagebox.showerror("Error", "Please generate the player sheet first."); return

            game = game_cb.get()
            conf = GAME_CONFIGS[game]
            
            # Save Referees
            referees = [e.get().strip() for e in self.ref_entries if e.get().strip()]

            t = Tournament(t_name, game, format_cb.get(), referees=referees)
            teams = {} 
            seen_names = set() # Edge Case: Duplicate names
            
            for entry_row in self.sheet_entries:
                name = entry_row['name'].get().strip()
                if not name: continue 
                
                if name.lower() in seen_names:
                    messagebox.showerror("Error", f"Duplicate name detected: '{name}'. Names must be unique.")
                    return
                seen_names.add(name.lower())
                
                elo = entry_row['elo'].get() if 'elo' in entry_row else 1000
                team = entry_row['team'].get().strip() if 'team' in entry_row else ""
                role = entry_row['role'].get() if 'role' in entry_row else ""
                
                if team:
                    if team not in teams: teams[team] = {}
                    teams[team][role] = teams[team].get(role, 0) + 1

                p = Participant(name, elo, role, team)
                t.participants[p.id] = p

            if len(t.participants) < 2:
                messagebox.showerror("Error", "At least 2 players/teams required."); return

            # Role Validation
            if conf.get('role_constraints'):
                for team_name, role_counts in teams.items():
                    for role_req, count_req in conf['role_constraints'].items():
                        actual = role_counts.get(role_req, 0)
                        if actual != count_req:
                            messagebox.showerror("Role Error", f"Team '{team_name}' must have exactly {count_req} {role_req}(s). Found {actual}.")
                            return

            self.tournaments[t.id] = t
            DataStore.save(self.tournaments)
            self.current_tournament = t
            self.manage_btn.config(state="normal")
            self.show_manage()

        ttk.Button(self.main_area, text="Create Tournament", command=save_tournament).pack(pady=10)

    # ==========================
    # VIEW: MANAGE TOURNAMENT
    # ==========================
    def show_manage(self):
        self.clear_main()
        if not self.current_tournament: return self.show_home()
        t = self.current_tournament
        
        # Header Area
        header = ttk.Frame(self.main_area)
        header.pack(fill="x", pady=(0, 20))
        
        if t.is_finished:
            winner = t.get_winner()
            win_txt = f"🏆 WINNER: {winner.name} 🏆" if winner else "🏆 FINISHED"
            tk.Label(header, text=win_txt, font=("Impact", 28), fg=COLORS["success"], bg=COLORS["bg_dark"]).pack(side="top", pady=5)
            
            # Finished Stats Summary
            stats_frame = self.create_card(self.main_area)
            stats_frame.pack(fill="x", pady=5)
            
            s_txt = f"Total Rounds: {t.get_all_rounds()}  |  Matches Played: {len(t.matches)}  |  Participants: {len(t.participants)}"
            tk.Label(stats_frame, text=s_txt, style="Card.TLabel", font=("Segoe UI", 12)).pack(pady=5) # pyright: ignore[reportCallIssue]
            
            if t.referees:
                ref_lbl = GAME_CONFIGS[t.game_type]["official_label"] + "s: " + ", ".join(t.referees)
                tk.Label(stats_frame, text=ref_lbl, fg=COLORS["accent"], bg=COLORS["bg_panel"]).pack(pady=5)

        else:
            ttk.Label(header, text=t.name, style="Header.TLabel").pack(side="left")
            info = f"{t.game_type} | {t.format_type}"
            tk.Label(header, text=info, bg=COLORS["accent"], fg="black", padx=15, pady=5, font=("Segoe UI", 10, "bold")).pack(side="right")

        # Tabs
        nb = ttk.Notebook(self.main_area)
        nb.pack(fill="both", expand=True)
        
        self.create_standings_tab(nb, t)
        self.create_matches_tab(nb, t)
        self.create_history_tab(nb, t)

    def create_standings_tab(self, nb, t):
        tab = ttk.Frame(nb)
        nb.add(tab, text="🏆 Standings")
        cols = ["rank", "name", "played", "won", "lost", "pts"]
        if GAME_CONFIGS[t.game_type]['has_elo']: cols.insert(2, "rating")
        if GAME_CONFIGS[t.game_type]['has_roles']: cols.insert(2, "team")
        
        tree = ttk.Treeview(tab, columns=cols, show="headings", height=15)
        for c in cols: 
            tree.heading(c, text=c.title())
            tree.column(c, width=70, anchor="center")
        tree.column("name", width=200, anchor="w")
        
        standings = t.get_active_participants()
        for i, p in enumerate(standings, 1):
            vals = [i, p.name, p.matches_played, p.won, p.lost, p.points]
            if GAME_CONFIGS[t.game_type]['has_elo']: vals.insert(2, p.rating)
            if GAME_CONFIGS[t.game_type]['has_roles']: vals.insert(2, p.team)
            tree.insert("", "end", values=vals)
        tree.pack(fill="both", expand=True, pady=10)

    def create_matches_tab(self, nb, t):
        tab = ttk.Frame(nb)
        nb.add(tab, text="⚔️ Matches")
        
        # Toolbar
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", pady=10)
        
        def gen():
            if t.is_finished: return
            if TournamentManager.generate_fixtures(t):
                DataStore.save(self.tournaments)
                self.show_manage()
            else: messagebox.showinfo("Info", "Fixtures are already up to date.")

        def next_r():
            if t.is_finished: return
            if any(not m.is_played for m in t.get_current_matches()):
                messagebox.showerror("Error", "Finish all matches in this round first."); return
            
            # Check for Knockout Final
            if t.format_type == "Knockout":
                active = t.get_active_participants()
                if len(active) == 1:
                    t.is_finished = True
                    DataStore.save(self.tournaments)
                    self.show_manage()
                    return

            t.current_round += 1
            DataStore.save(self.tournaments)
            self.show_manage()

        if not t.is_finished:
            ttk.Button(toolbar, text="Generate Matches", command=gen).pack(side="left", padx=5)
            ttk.Button(toolbar, text="Finish Round ⏩", command=next_r).pack(side="right", padx=5)
        
        self.render_match_list(tab, t.get_current_matches(), t, editable=not t.is_finished)

    def create_history_tab(self, nb, t):
        tab = ttk.Frame(nb)
        nb.add(tab, text="📜 History")
        
        canvas = tk.Canvas(tab, bg=COLORS["bg_dark"], highlightthickness=0)
        scroll = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        rounds = t.get_all_rounds()
        if rounds == 0: ttk.Label(frame, text="No match history.").pack(pady=20)

        for r in range(1, rounds + 1):
            rf = self.create_card(frame, padding=10)
            rf.pack(fill="x", pady=5, padx=10)
            tk.Label(rf, text=f"Round {r}", fg=COLORS["accent"], bg=COLORS["bg_panel"], font=("Segoe UI", 12, "bold")).pack(anchor="w")
            matches = t.get_matches_by_round(r)
            for m in matches:
                p1 = t.participants[m.p1_id].name
                p2 = t.participants[m.p2_id].name if m.p2_id else "BYE"
                score = f"{m.p1_score} - {m.p2_score}" if m.is_played else "Pending"
                tk.Label(rf, text=f"{p1} vs {p2}   [{score}]", bg=COLORS["bg_panel"], fg="white").pack(anchor="w", padx=20)

    def render_match_list(self, parent, matches, t, editable):
        # Helper to render a list of matches inside a scrollable area
        canvas = tk.Canvas(parent, bg=COLORS["bg_dark"], highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        if not matches: ttk.Label(frame, text="No matches scheduled. Click Generate Matches.").pack(pady=20)

        for m in matches:
            card = self.create_card(frame, padding=10)
            card.pack(fill="x", pady=5, padx=10)
            
            p1 = t.participants[m.p1_id].name
            p2 = t.participants[m.p2_id].name if m.p2_id else "BYE"
            
            txt = f"{p1}  vs  {p2}"
            if m.is_played: txt += f"    [ {m.p1_score} - {m.p2_score} ]"
            
            ttk.Label(card, text=txt, style="Card.TLabel", font=("Segoe UI", 11, "bold")).pack(side="left")
            
            if editable and not m.is_played and m.p2_id:
                ttk.Button(card, text="Enter Result", command=lambda m=m: self.show_result_dialog(m, t)).pack(side="right")
            elif m.is_played:
                tk.Label(card, text="✅ Completed", bg=COLORS["bg_panel"], fg=COLORS["success"]).pack(side="right")

    def show_result_dialog(self, m, t):
        d = tk.Toplevel(self)
        d.title("Match Result")
        self.center_window(d, 350, 300)
        d.configure(bg=COLORS["bg_panel"])
        
        p1 = t.participants[m.p1_id].name
        p2 = t.participants[m.p2_id].name
        
        tk.Label(d, text=f"{p1} Score:", bg=COLORS["bg_panel"], fg="white", font=("Segoe UI", 10)).pack(pady=(20, 5))
        e1 = ttk.Entry(d, width=10, font=("Segoe UI", 12), justify="center"); e1.pack()
        
        tk.Label(d, text=f"{p2} Score:", bg=COLORS["bg_panel"], fg="white", font=("Segoe UI", 10)).pack(pady=5)
        e2 = ttk.Entry(d, width=10, font=("Segoe UI", 12), justify="center"); e2.pack()
        e1.focus()
        
        def save():
            try:
                s1, s2 = int(e1.get()), int(e2.get())
                # Knockout Tie-Breaker Enforcement
                if t.format_type == "Knockout" and s1 == s2:
                    tie_rule = GAME_CONFIGS[t.game_type].get("tiebreaker", "Tie-breaker")
                    messagebox.showwarning("Knockout Rule", 
                        f"Knockout matches cannot end in a draw.\n\nRequired: {tie_rule}.\n\nPlease play the tie-breaker and enter the winner.")
                    return 
                
                TournamentManager.record_result(t, m.id, s1, s2)
                DataStore.save(self.tournaments)
                d.destroy()
                self.show_manage()
            except ValueError: messagebox.showerror("Error", "Please enter valid numbers.")
        
        # Chess Specific Draw Button
        if t.game_type == "Chess":
             def set_draw():
                 TournamentManager.record_result(t, m.id, 0, 0) # Logic handles Draw
                 DataStore.save(self.tournaments)
                 d.destroy()
                 self.show_manage()
             
             ttk.Button(d, text="Draw (½ - ½)", command=set_draw).pack(pady=5)

        ttk.Button(d, text="Submit Result", command=save).pack(pady=20)
        d.bind("<Return>", lambda e: save())

    def export_standings(self):
        if not self.current_tournament: return
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Points", "Won", "Lost"])
                for p in self.current_tournament.get_active_participants():
                    writer.writerow([p.name, p.points, p.won, p.lost])
            messagebox.showinfo("Success", "Exported successfully!")

if __name__ == "__main__":
    app = PlaywiseGUI()
    app.mainloop()