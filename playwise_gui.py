#!/usr/bin/env python3
#
# ===============================================================
#  Playwise Tournament Management System - Full GUI Edition
#  Version 4.0 - (Full-Featured CLI Backend + Full-Featured GUI)
# ===============================================================
#
#  This script implements the *entire* functionality of the
#  Playwise CLI backend within a comprehensive Tkinter GUI.
#
#  Features:
#  - Manages multiple Sports (individual and team)
#  - Registers Players and multi-player Teams
#  - Creates multiple, distinct Tournaments
#  - Supports League, Knockout, AND Swiss formats
#  - Dedicated window to manage each tournament's fixtures
#  - Includes Matplotlib analytics for each tournament
#

import itertools
import random
import sys
from collections import defaultdict

# --- GUI Imports ---
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
try:
    import matplotlib.pyplot as plt # pyright: ignore[reportMissingModuleSource]
    import importlib
    try:
        # Import the TkAgg backend dynamically to avoid static-import resolution errors
        FigureCanvasTkAgg = importlib.import_module("matplotlib.backends.backend_tkagg").FigureCanvasTkAgg
    except Exception:
        # Backend module not available or can't be resolved at runtime/static analysis time
        FigureCanvasTkAgg = None
except Exception:
    # Backend not available in some environments (e.g., headless or missing tkinter support).
    plt = None  # type: ignore
    FigureCanvasTkAgg = None  # type: ignore
from typing import Optional

# ===============================================================
# === MODULE 1: MODELS (From CLI App) ===
# ===============================================================

class Sport:
    """
    Defines a sport, its team size, and scoring rules.
    """
    def __init__(self, name, team_size=1, allow_draws=True):
        self.name = name
        self.team_size = team_size
        self.allow_draws = allow_draws

    def __str__(self):
        if self.team_size == 1:
            return f"{self.name} (Individual)"
        return f"{self.name} ({self.team_size}v{self.team_size})"


class Player:
    """
    Player for esports/chess with role, rating, and stats.
    NOTE: Stats (wins/losses) are global. We reset them
    when a player is added to a new tournament.
    """
    def __init__(self, name, sport_name, role="Player", rating=1000):
        self.name = name
        self.sport_name = sport_name
        self.role = role
        self.rating = rating
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def record_result(self, result):
        if result == 'win': self.wins += 1
        elif result == 'loss': self.losses += 1
        elif result == 'draw': self.draws += 1
        
    def reset_stats(self):
        """Resets stats for a new tournament."""
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def __str__(self):
        return f"{self.name} ({self.sport_name}) - Role: {self.role} - Rating: {self.rating}"

class Team:
    """
    Team class for team-based e-sports.
    """
    def __init__(self, team_name, sport_obj: Sport):
        self.team_name = team_name
        self.sport_name = sport_obj.name
        self.sport = sport_obj
        self.max_players = sport_obj.team_size
        self.players = []
        self.matches_played = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def add_player(self, player: Player):
        if len(self.players) >= self.max_players:
            # GUI will handle showing this error
            return (False, f"Team {self.team_name} is full.")
        if player.sport_name != self.sport_name:
            return (False, f"Player {player.name} plays {player.sport_name}, not {self.sport_name}.")
        if player in self.players:
            return (False, f"Player {player.name} is already in this team.")
        
        self.players.append(player)
        return (True, f"Added {player.name} to {self.team_name}.")

    def record_match(self, result):
        self.matches_played += 1
        if result == 'win': self.wins += 1
        elif result == 'loss': self.losses += 1
        elif result == 'draw': self.draws += 1
        
    def reset_stats(self):
        """Resets stats for a new tournament."""
        self.matches_played = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def __str__(self):
        names = ', '.join(p.name for p in self.players)
        if not names:
            names = "No players yet"
        return f"Team {self.team_name} ({self.sport_name}) [{len(self.players)}/{self.max_players}]"

# ===============================================================
# === MODULE 2: FORMAT MANAGEMENT (From CLI App) ===
# ===============================================================

class FormatManager:
    """
    Manage tournament formats and their fixture-generation handlers.
    (Backend logic, print statements will go to console)
    """
    def __init__(self):
        self.formats = {
            'League': self.league_format,
            'Knockout': self.knockout_format,
            'Swiss': self.swiss_format
        }

    def league_format(self, tournament):
        print("✅ [Info] Generating Round-Robin League fixtures...")
        contestants = tournament.get_active_contestants()
        tournament.matches = list(itertools.combinations(contestants, 2))

    def knockout_format(self, tournament):
        print("✅ [Info] Generating Knockout fixtures...")
        active = tournament.get_active_contestants()
        random.shuffle(active)
        tournament.matches = []
        
        while len(active) > 1:
            c1 = active.pop()
            c2 = active.pop()
            tournament.matches.append((c1, c2))
        
        if active:
            bye_contestant = active.pop()
            tournament.matches.append((bye_contestant, None))
            # Automatically record the bye result
            tournament.record_result((bye_contestant, None), tournament._contestant_name(bye_contestant))

    def swiss_format(self, tournament):
        print(f"✅ [Info] Generating Swiss fixtures for Round {tournament.round}...")
        active = tournament.get_active_contestants()
        tournament.matches = []

        if tournament.round == 1:
            random.shuffle(active)
        else:
            # Sort by points, then rating
            active.sort(key=lambda c: (
                tournament.points[tournament._contestant_name(c)],
                c.rating if isinstance(c, Player) else sum(p.rating for p in c.players)
            ), reverse=True)

        paired_contestants = set()
        
        for i in range(len(active)):
            c1 = active[i]
            if c1 in paired_contestants:
                continue

            opponent_found = False
            for j in range(i + 1, len(active)):
                c2 = active[j]
                if c2 in paired_contestants:
                    continue
                
                if c2 not in tournament.opponents_played[c1]:
                    tournament.matches.append((c1, c2))
                    paired_contestants.add(c1)
                    paired_contestants.add(c2)
                    opponent_found = True
                    break
            
            if not opponent_found and c1 not in paired_contestants:
                tournament.matches.append((c1, None))
                paired_contestants.add(c1)
                tournament.record_result((c1, None), tournament._contestant_name(c1))

        print(f"✅ [Info] {len(tournament.matches)} matches generated for Round {tournament.round}.")


# ===============================================================
# === MODULE 3: TOURNAMENT CORE (From CLI App) ===
# ===============================================================

class Tournament:
    """
    The main Tournament class.
    (Backend logic, print statements will go to console)
    """
    def __init__(self, name: str, sport_obj: Sport, format_name: str, format_manager: FormatManager):
        self.name = name
        self.sport = sport_obj
        self.format_name = format_name
        self.format_manager = format_manager
        
        self.players = []
        self.teams = []
        
        self.matches = []
        self.results = {} 
        self.points = defaultdict(float)
        self.eliminated = set()
        self.opponents_played = defaultdict(set) 
        
        self.round = 1
        
        if format_name == 'Swiss':
            self.points_for_win = 1.0
            self.points_for_draw = 0.5
            self.points_for_bye = 1.0
        else: 
            self.points_for_win = 3
            self.points_for_draw = 1
            self.points_for_bye = 3 # A bye in Knockout is a win

    def add_contestant(self, contestant):
        """Adds a Player or a Team to the tournament."""
        if isinstance(contestant, Player):
            if contestant.sport_name != self.sport.name:
                return (False, f"Player {contestant.name} does not play {self.sport.name}!")
            if self.sport.team_size > 1:
                return (False, "This is a team tournament. Cannot add individual player.")
            if contestant in self.players:
                return (False, f"Player {contestant.name} is already in this tournament.")
            self.players.append(contestant)
            
        elif isinstance(contestant, Team):
            if contestant.sport_name != self.sport.name:
                return (False, f"Team {contestant.team_name} does not play {self.sport.name}!")
            if self.sport.team_size == 1:
                 return (False, "This is an individual tournament. Cannot add team.")
            if contestant in self.teams:
                return (False, f"Team {contestant.team_name} is already in this tournament.")
            self.teams.append(contestant)
        
        # Reset stats for this specific tournament
        contestant.reset_stats()
        self.points[self._contestant_name(contestant)] = 0.0 # Initialize points
        return (True, f"Added contestant: {self._contestant_name(contestant)}")

    def get_contestants(self):
        """Returns the list of all contestants in this tournament."""
        return self.teams if self.sport.team_size > 1 else self.players

    def get_active_contestants(self):
        """Returns a list of contestants who are not eliminated."""
        base_list = self.get_contestants()
        if self.format_name == 'Knockout':
            return [c for c in base_list if c not in self.eliminated]
        return base_list

    def generate_fixtures(self):
        print(f"✅ [Info] Generating fixtures for {self.format_name} format...")
        handler = self.format_manager.formats.get(self.format_name)
        if not handler:
            return (False, "Format handler not found!")
        self.matches.clear()
        self.results.clear()
        handler(self)
        return (True, f"Fixtures generated for Round {self.round}.")

    def record_result(self, match, winner_name, is_draw=False):
        """Records the result of a match. Returns (True/False, message)."""
        if match in self.results:
            return (False, "Result for this match already recorded.")

        c1, c2 = match
        c1_name = self._contestant_name(c1)
        c2_name = self._contestant_name(c2) if c2 else "BYE"

        # Handle Bye
        if c2 is None:
            self.results[match] = c1_name
            if self.format_name == 'Swiss':
                self.points[c1_name] += self.points_for_bye
            elif self.format_name == 'Knockout':
                # In Knockout, a bye is just an advancement, not points
                pass
            return (True, f"{c1_name} advances by bye.")
        
        self.results[match] = winner_name if not is_draw else "DRAW"

        if self.format_name == 'Swiss':
            self.opponents_played[c1].add(c2)
            self.opponents_played[c2].add(c1)

        # Handle Draw
        if is_draw:
            if not self.sport.allow_draws:
                self.results.pop(match)
                return (False, "This sport does not allow draws.")
            if self.format_name in ['League', 'Swiss']:
                self.points[c1_name] += self.points_for_draw
                self.points[c2_name] += self.points_for_draw
                self._record_draw(c1)
                self._record_draw(c2)
                return (True, f"Match {c1_name} vs {c2_name} ended in a draw.")
            else:
                self.results.pop(match)
                return (False, "Knockout matches cannot be a draw.")
        
        # Handle Win/Loss
        else:
            if self.format_name in ['League', 'Swiss']:
                self.points[winner_name] += self.points_for_win
            
            winner, loser = (c1, c2) if c1_name == winner_name else (c2, c1)
            
            self._record_win(winner)
            self._record_loss(loser)
            
            if self.format_name == 'Knockout':
                self.eliminated.add(loser)
                return (True, f"Winner: {winner_name}. {self._contestant_name(loser)} eliminated.")
            
            return (True, f"Winner: {winner_name}.")
    
    def next_round(self):
        """Advances the tournament to the next round. Returns (True/False, message)"""
        if self.format_name not in ['Knockout', 'Swiss']:
            return (False, "Only Knockout and Swiss formats support multiple rounds.")
        
        if len(self.matches) > len(self.results):
            return (False, "Cannot generate next round. Not all matches from this round are recorded.")

        active_contestants = self.get_active_contestants()
        if len(active_contestants) <= 1:
            winner_name = "None"
            if active_contestants:
                winner_name = self._contestant_name(active_contestants[0])
            return (False, f"Tournament over! Winner: {winner_name}")

        self.round += 1
        self.generate_fixtures()
        return (True, f"Advanced to Round {self.round}. New fixtures generated.")

    # --- Helper Methods ---
    def _contestant_name(self, c):
        if c is None: return "BYE"
        return c.name if isinstance(c, Player) else c.team_name

    def _record_win(self, contestant):
        if isinstance(contestant, Player): contestant.record_result('win')
        else: contestant.record_match('win')

    def _record_loss(self, contestant):
        if isinstance(contestant, Player): contestant.record_result('loss')
        else: contestant.record_match('loss')
    
    def _record_draw(self, contestant):
        if isinstance(contestant, Player): contestant.record_result('draw')
        else: contestant.record_match('draw')
        
    def get_unplayed_matches(self):
        return [m for m in self.matches if m not in self.results]
        
    def get_leaderboard_data(self):
        """Returns a list of tuples for the leaderboard."""
        contestants = self.get_contestants()
        data = []
        for c in contestants:
            name = self._contestant_name(c)
            points = self.points.get(name, 0.0)
            wins = c.wins
            losses = c.losses
            draws = c.draws
            data.append((name, points, wins, losses, draws))
            
        # Sort by points (descending)
        data.sort(key=lambda x: x[1], reverse=True)
        return data

# ===============================================================
# === MODULE 4: GUI - TOURNAMENT MANAGER WINDOW (Toplevel) ===
# ===============================================================

class TournamentManagerWindow(tk.Toplevel):
    """
    A separate window for managing a single tournament instance.
    """
    def __init__(self, parent, main_app: 'PlaywiseApp', tournament: Tournament):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        
        self.main_app = main_app
        self.tournament = tournament
        
        self.title(f"Manage: {self.tournament.name} ({self.tournament.sport.name})")
        self.geometry("900x700")

        # This will hold the (c1, c2) tuple of the selected match
        self.selected_match_tuple: Optional[tuple] = None

        # --- Create Notebook ---
        self.notebook = ttk.Notebook(self)
        
        self.tab_contestants = ttk.Frame(self.notebook, padding=10)
        self.tab_fixtures = ttk.Frame(self.notebook, padding=10)
        self.tab_leaderboard = ttk.Frame(self.notebook, padding=10)
        self.tab_analytics = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.tab_contestants, text="📥 Contestants")
        self.notebook.add(self.tab_fixtures, text="🗓️ Fixtures & Results")
        self.notebook.add(self.tab_leaderboard, text="📊 Leaderboard")
        self.notebook.add(self.tab_analytics, text="📈 Analytics")
        
        self.notebook.pack(expand=True, fill="both")
        
        # --- Build Tabs ---
        self.create_contestants_tab()
        self.create_fixtures_tab()
        self.create_leaderboard_tab()
        self.create_analytics_tab()
        
        # --- Populate initial data ---
        self.update_contestant_lists()
        self.update_fixtures_tree()
        self.update_leaderboard_tree()
        
    
    ### --- Tab 1: Contestants ---
    def create_contestants_tab(self):
        main_frame = ttk.Frame(self.tab_contestants)
        main_frame.pack(fill="both", expand=True)
        
        # --- Available Contestants Frame ---
        available_frame = ttk.LabelFrame(main_frame, text="Available from Registry")
        available_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.available_tree = ttk.Treeview(available_frame, columns=("Name", "Sport"), show="headings")
        self.available_tree.heading("Name", text="Name")
        self.available_tree.heading("Sport", text="Sport")
        self.available_tree.pack(fill="both", expand=True)
        
        # --- Middle Button Frame ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side="left", fill="y", padx=10)
        
        ttk.Button(button_frame, text="Add >>", command=self.add_contestant).pack(pady=10)
        # Note: Removing contestants is complex (messes up fixtures)
        # We will disable it for simplicity.
        # ttk.Button(button_frame, text="<< Remove", command=self.remove_contestant).pack(pady=10)
        
        # --- Added Contestants Frame ---
        added_frame = ttk.LabelFrame(main_frame, text="Added to this Tournament")
        added_frame.pack(side="right", fill="both", expand=True, padx=5)

        self.added_tree = ttk.Treeview(added_frame, columns=("Name",), show="headings")
        self.added_tree.heading("Name", text="Name")
        self.added_tree.pack(fill="both", expand=True)

    def update_contestant_lists(self):
        # Clear trees
        self.available_tree.delete(*self.available_tree.get_children())
        self.added_tree.delete(*self.added_tree.get_children())

        # Get all contestants of the correct sport from the main app
        is_team_sport = self.tournament.sport.team_size > 1
        all_contestants = self.main_app.registered_teams if is_team_sport else self.main_app.registered_players
        
        tournament_contestants = self.tournament.get_contestants()
        
        for c in all_contestants:
            # Only show those that match the sport
            if c.sport_name == self.tournament.sport.name:
                name = self.tournament._contestant_name(c)
                if c not in tournament_contestants:
                    # Add to available list, using the object 'c' as the item ID
                    self.available_tree.insert("", "end", iid=name, values=(name, c.sport_name))
        
        for c in tournament_contestants:
            name = self.tournament._contestant_name(c)
            self.added_tree.insert("", "end", iid=name, values=(name,))
            
    def add_contestant(self):
        selected_iid = self.available_tree.selection()
        if not selected_iid:
            return
            
        name = selected_iid[0]
        # Find the object from the main app's registry
        is_team_sport = self.tournament.sport.team_size > 1
        all_contestants = self.main_app.registered_teams if is_team_sport else self.main_app.registered_players
        
        contestant_obj = None
        for c in all_contestants:
            if self.tournament._contestant_name(c) == name:
                contestant_obj = c
                break
        
        if contestant_obj:
            success, message = self.tournament.add_contestant(contestant_obj)
            if not success:
                messagebox.showerror("Error", message)
            else:
                self.update_contestant_lists()
                self.update_leaderboard_tree() # Show new contestant with 0 points
                

    ### --- Tab 2: Fixtures & Results ---
    def create_fixtures_tab(self):
        top_frame = ttk.Frame(self.tab_fixtures)
        top_frame.pack(fill="x", pady=5)
        
        self.generate_fixtures_button = ttk.Button(top_frame, text="Generate Fixtures (Round 1)", command=self.generate_or_advance)
        self.generate_fixtures_button.pack(side="left")
        
        self.round_label = ttk.Label(top_frame, text=f"Round: {self.tournament.round}", font=('Helvetica', 10, 'bold'))
        self.round_label.pack(side="left", padx=20)
        
        # --- Fixtures List ---
        fixture_frame = ttk.LabelFrame(self.tab_fixtures, text="Matches")
        fixture_frame.pack(fill="both", expand=True, pady=10)
        
        cols = ('P1', 'P2', 'Result')
        self.fixtures_tree = ttk.Treeview(fixture_frame, columns=cols, show='headings')
        self.fixtures_tree.heading("P1", text="Contestant 1")
        self.fixtures_tree.heading("P2", text="Contestant 2")
        self.fixtures_tree.heading("Result", text="Result")
        self.fixtures_tree.column("Result", width=100, anchor="center")
        self.fixtures_tree.pack(fill="both", expand=True)
        
        self.fixtures_tree.bind('<<TreeviewSelect>>', self.on_match_select)
        
        # --- Record Result Frame ---
        results_frame = ttk.LabelFrame(self.tab_fixtures, text="Record Result")
        results_frame.pack(pady=10, fill="x")

        self.selected_match_label = ttk.Label(results_frame, text="Selected Match: (None)", font=('Helvetica', 10, 'bold'))
        self.selected_match_label.pack(pady=5)
        
        self.winner_var = tk.StringVar()
        self.p1_win_radio = ttk.Radiobutton(results_frame, text="P1 Wins", variable=self.winner_var, value="p1", state="disabled")
        self.p2_win_radio = ttk.Radiobutton(results_frame, text="P2 Wins", variable=self.winner_var, value="p2", state="disabled")
        self.draw_radio = ttk.Radiobutton(results_frame, text="Draw", variable=self.winner_var, value="draw", state="disabled")
        
        self.p1_win_radio.pack(side=tk.LEFT, padx=10)
        self.p2_win_radio.pack(side=tk.LEFT, padx=10)
        
        if self.tournament.sport.allow_draws and self.tournament.format_name != 'Knockout':
             self.draw_radio.pack(side=tk.LEFT, padx=10)

        self.submit_result_button = ttk.Button(results_frame, text="Submit Result", command=self.record_result, state="disabled")
        self.submit_result_button.pack(side=tk.RIGHT, padx=10)
        
    def generate_or_advance(self):
        # Check if it's round 1
        if self.tournament.round == 1 and not self.tournament.matches:
            success, message = self.tournament.generate_fixtures()
            if not success:
                messagebox.showerror("Error", message)
            else:
                messagebox.showinfo("Success", message)
                self.generate_fixtures_button.config(text=f"Advance to Round {self.tournament.round + 1}")
        else:
            # This is for "Next Round"
            success, message = self.tournament.next_round()
            if not success:
                messagebox.showwarning("Info", message) # Could be "Tourn. over"
            else:
                messagebox.showinfo("Success", message)
                self.generate_fixtures_button.config(text=f"Advance to Round {self.tournament.round + 1}")
        
        self.update_fixtures_tree()
        self.update_leaderboard_tree()
        self.round_label.config(text=f"Round: {self.tournament.round}")
        
    def update_fixtures_tree(self):
        self.fixtures_tree.delete(*self.fixtures_tree.get_children())
        
        for match in self.tournament.matches:
            c1_name = self.tournament._contestant_name(match[0])
            c2_name = self.tournament._contestant_name(match[1])
            
            result = "Pending..."
            if match in self.tournament.results:
                result = self.tournament.results[match]
            
            # Use the match tuple itself as the IID (string-formatted)
            iid_str = f"{c1_name}_vs_{c2_name}"
            self.fixtures_tree.insert("", "end", iid=iid_str, values=(c1_name, c2_name, result))

    def on_match_select(self, event):
        selected_iid = self.fixtures_tree.selection()
        if not selected_iid:
            return
            
        values = self.fixtures_tree.item(selected_iid[0], 'values')
        c1_name, c2_name, result = values
        
        # Find the actual match tuple
        match_found = None
        for match in self.tournament.matches:
            if (self.tournament._contestant_name(match[0]) == c1_name and
                self.tournament._contestant_name(match[1]) == c2_name):
                match_found = match
                break
        
        if not match_found:
            self.selected_match_tuple = None
            return
            
        self.selected_match_tuple = match_found
        
        if result != "Pending...":
            # Match already played
            self.selected_match_label.config(text=f"Played: {c1_name} vs {c2_name} (Result: {result})")
            self.p1_win_radio.config(state="disabled")
            self.p2_win_radio.config(state="disabled")
            self.draw_radio.config(state="disabled")
            self.submit_result_button.config(state="disabled")
            self.winner_var.set("")
        else:
            # Match is pending
            self.selected_match_label.config(text=f"Selected: {c1_name} vs {c2_name}")
            self.p1_win_radio.config(text=f"{c1_name} Wins", state="normal")
            self.p2_win_radio.config(text=f"{c2_name} Wins", state="normal")
            if self.tournament.sport.allow_draws and self.tournament.format_name != 'Knockout':
                self.draw_radio.config(state="normal")
            self.submit_result_button.config(state="normal")
            self.winner_var.set("")

    def record_result(self):
        if self.selected_match_tuple is None:
            messagebox.showerror("Error", "No match selected.")
            return
            
        winner_choice = self.winner_var.get()
        if not winner_choice:
            messagebox.showerror("Error", "Please select a result.")
            return
            
        c1_name = self.tournament._contestant_name(self.selected_match_tuple[0])
        c2_name = self.tournament._contestant_name(self.selected_match_tuple[1])
        
        winner_name = ""
        is_draw = False

        if winner_choice == "p1":
            winner_name = c1_name
        elif winner_choice == "p2":
            winner_name = c2_name
        elif winner_choice == "draw":
            is_draw = True

        success, message = self.tournament.record_result(self.selected_match_tuple, winner_name, is_draw)
        
        if not success:
            messagebox.showerror("Error", message)
        else:
            print(message) # Log to console
            
        # Refresh everything
        self.update_fixtures_tree()
        self.update_leaderboard_tree()
        self.update_analytics_chart()
        
        # Clear selection
        self.selected_match_label.config(text="Selected Match: (None)")
        self.p1_win_radio.config(state="disabled")
        self.p2_win_radio.config(state="disabled")
        self.draw_radio.config(state="disabled")
        self.submit_result_button.config(state="disabled")
        self.winner_var.set("")
        self.selected_match_tuple = None

    ### --- Tab 3: Leaderboard ---
    def create_leaderboard_tab(self):
        refresh_button = ttk.Button(self.tab_leaderboard, text="Refresh", command=self.update_leaderboard_tree)
        refresh_button.pack(pady=5)
        
        # --- Special frame for Knockout ---
        self.knockout_frame = ttk.Frame(self.tab_leaderboard)
        # We will pack this *only* if it's a Knockout tournament
        
        self.active_list_frame = ttk.LabelFrame(self.knockout_frame, text="Active Contestants")
        self.active_list_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.active_listbox = tk.Listbox(self.active_list_frame)
        self.active_listbox.pack(fill="both", expand=True)
        
        self.elim_list_frame = ttk.LabelFrame(self.knockout_frame, text="Eliminated")
        self.elim_list_frame.pack(side="right", fill="both", expand=True, padx=5)
        self.elim_listbox = tk.Listbox(self.elim_list_frame)
        self.elim_listbox.pack(fill="both", expand=True)
        
        # --- Standard frame for League/Swiss ---
        self.leaderboard_frame = ttk.Frame(self.tab_leaderboard)
        # We will pack this *only* if it's League/Swiss
        
        cols = ('Rank', 'Name', 'Points', 'W', 'L', 'D')
        self.leaderboard_tree = ttk.Treeview(self.leaderboard_frame, columns=cols, show="headings")
        for col in cols:
            self.leaderboard_tree.heading(col, text=col)
            self.leaderboard_tree.column(col, width=80, anchor="center")
        self.leaderboard_tree.column('Name', anchor="w", width=200)
        self.leaderboard_tree.pack(fill="both", expand=True)
        
        # Now, pack the correct frame
        if self.tournament.format_name == 'Knockout':
            self.knockout_frame.pack(fill="both", expand=True)
        else:
            self.leaderboard_frame.pack(fill="both", expand=True)
            
    def update_leaderboard_tree(self):
        if self.tournament.format_name == 'Knockout':
            self.active_listbox.delete(0, "end")
            self.elim_listbox.delete(0, "end")
            
            for c in self.tournament.get_active_contestants():
                self.active_listbox.insert("end", self.tournament._contestant_name(c))
            for c in self.tournament.eliminated:
                self.elim_listbox.insert("end", self.tournament._contestant_name(c))
        
        else: # League or Swiss
            self.leaderboard_tree.delete(*self.leaderboard_tree.get_children())
            leaderboard_data = self.tournament.get_leaderboard_data()
            
            for i, (name, points, w, l, d) in enumerate(leaderboard_data, 1):
                self.leaderboard_tree.insert("", "end", values=(i, name, f"{points:.1f}", w, l, d))

    ### --- Tab 4: Analytics ---
    def create_analytics_tab(self):
        action_frame = ttk.Frame(self.tab_analytics)
        action_frame.pack(pady=5, fill="x")
        
        analytics_button = ttk.Button(action_frame, text="Generate/Update Analytics Chart", command=self.update_analytics_chart)
        analytics_button.pack()

        self.chart_frame = ttk.Frame(self.tab_analytics)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chart_canvas = None # Placeholder
        self.update_analytics_chart() # Initial draw

    def update_analytics_chart(self):
        if not self.tournament or not self.tournament.get_contestants():
            return # No data to chart

        # If matplotlib or its Tk backend is unavailable, warn and return early
        if plt is None or FigureCanvasTkAgg is None:
            messagebox.showwarning(
                "Analytics Unavailable",
                "Matplotlib with Tk backend is not available in this environment.\n"
                "Install matplotlib with Tk support or run in an environment with tkinter to view charts."
            )
            return

        # Clear any existing chart
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        contestants = self.tournament.get_contestants()
        
        player_names = [self.tournament._contestant_name(c) for c in contestants]
        wins = [c.wins for c in contestants]
        losses = [c.losses for c in contestants]
        draws = [c.draws for c in contestants]
        
        fig, ax = plt.subplots()

        ax.bar(player_names, wins, label='Wins', color='green')
        ax.bar(player_names, losses, bottom=wins, label='Losses', color='red')
        bottom_draws = [w + l for w, l in zip(wins, losses)]
        ax.bar(player_names, draws, bottom=bottom_draws, label='Draws', color='gray')

        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# ===============================================================
# === MODULE 5: GUI - TEAM EDITOR WINDOW (Toplevel) ===
# ===============================================================

class TeamEditorWindow(tk.Toplevel):
    """
    A Toplevel window to create a new team and add players.
    """
    def __init__(self, parent, main_app: 'PlaywiseApp', team_name: str, sport_obj: Sport):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        
        self.main_app = main_app
        self.team_name = team_name
        self.sport_obj = sport_obj
        
        self.team_in_progress = Team(team_name, sport_obj)
        self.selected_players = [] # Holds Player objects
        
        self.title(f"Create Team: {team_name}")
        self.geometry("600x400")
        
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text=f"Select {sport_obj.team_size} players for {team_name} ({sport_obj.name})").pack()

        # --- Player Lists Frame ---
        lists_frame = ttk.Frame(main_frame)
        lists_frame.pack(fill="both", expand=True, pady=10)
        
        available_frame = ttk.LabelFrame(lists_frame, text="Available Players")
        available_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.available_listbox = tk.Listbox(available_frame, selectmode="extended")
        self.available_listbox.pack(fill="both", expand=True)
        
        added_frame = ttk.LabelFrame(lists_frame, text="Added to Team")
        added_frame.pack(side="right", fill="both", expand=True, padx=5)
        self.added_listbox = tk.Listbox(added_frame)
        self.added_listbox.pack(fill="both", expand=True)
        
        # --- Buttons ---
        self.available_listbox.bind("<Double-Button-1>", self.add_player)
        self.added_listbox.bind("<Double-Button-1>", self.remove_player)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        self.status_label = ttk.Label(button_frame, text=f"Added 0 / {sport_obj.team_size}")
        self.status_label.pack(side="left")
        
        self.save_button = ttk.Button(button_frame, text="Save Team", command=self.save_team, state="disabled")
        self.save_button.pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right")
        
        self.populate_available_players()

    def populate_available_players(self):
        self.available_listbox.delete(0, "end")
        # Find available players for this sport
        available = self.main_app.get_unassigned_players(self.sport_obj.name)
        
        for player in available:
            # Store the player object itself in the list
            self.available_listbox.insert("end", player.name)
            self.available_listbox.itemconfig("end", {'data': player})
            
    def add_player(self, event=None):
        selection_indices = self.available_listbox.curselection()
        if not selection_indices:
            return
            
        # Check if team is full
        if len(self.selected_players) >= self.sport_obj.team_size:
            messagebox.showwarning("Team Full", f"Team can only have {self.sport_obj.team_size} players.")
            return

        # Get the first selected player
        idx = selection_indices[0]
        name = self.available_listbox.get(idx)
        
        # Find the player object
        player_obj = None
        for p in self.main_app.get_unassigned_players(self.sport_obj.name):
            if p.name == name and p not in self.selected_players:
                player_obj = p
                break
        
        if player_obj:
            self.selected_players.append(player_obj)
            self.update_listboxes()

    def remove_player(self, event=None):
        selection_indices = self.added_listbox.curselection()
        if not selection_indices:
            return
            
        idx = selection_indices[0]
        name = self.added_listbox.get(idx)
        
        # Find the player object in self.selected_players
        player_obj = next((p for p in self.selected_players if p.name == name), None)
        
        if player_obj:
            self.selected_players.remove(player_obj)
            self.update_listboxes()

    def update_listboxes(self):
        self.available_listbox.delete(0, "end")
        self.added_listbox.delete(0, "end")
        
        available = self.main_app.get_unassigned_players(self.sport_obj.name)
        
        for player in available:
            if player not in self.selected_players:
                self.available_listbox.insert("end", player.name)
                
        for player in self.selected_players:
            self.added_listbox.insert("end", player.name)
            
        # Update status
        count = len(self.selected_players)
        self.status_label.config(text=f"Added {count} / {self.sport_obj.team_size}")
        
        if count == self.sport_obj.team_size:
            self.save_button.config(state="normal")
        else:
            self.save_button.config(state="disabled")

    def save_team(self):
        if len(self.selected_players) != self.sport_obj.team_size:
            messagebox.showerror("Error", f"Team must have exactly {self.sport_obj.team_size} players.")
            return
            
        # Add players to the actual Team object
        for player in self.selected_players:
            self.team_in_progress.add_player(player)
            
        # Add team to main app
        self.main_app.registered_teams.append(self.team_in_progress)
        self.main_app.update_team_registry_tree()
        
        messagebox.showinfo("Success", f"Team '{self.team_name}' created successfully.")
        self.destroy()

# ===============================================================
# === MODULE 6: GUI - MAIN APPLICATION ===
# ===============================================================

class PlaywiseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Playwise Tournament Management System v4.0")
        self.root.geometry("1000x600")
        
        # --- Initialize Backend ---
        self.format_manager = FormatManager()
        
        # --- Global Registries ---
        self.registered_players = []
        self.registered_teams = []
        self.tournaments = []
        
        # Pre-populate available sports
        self.available_sports = {
            'Chess': Sport("Chess", team_size=1, allow_draws=True),
            'Valorant': Sport("Valorant", team_size=5, allow_draws=False),
            'CSGO': Sport("CSGO", team_size=5, allow_draws=False),
            'PUBG': Sport("PUBG", team_size=4, allow_draws=False),
            '3v3 Basketball': Sport("3v3 Basketball", team_size=3, allow_draws=False),
        }
        self.sport_names = list(self.available_sports.keys())
        self.format_names = list(self.format_manager.formats.keys())

        # --- Create GUI ---
        self.notebook = ttk.Notebook(self.root)
        
        self.tab_registry = ttk.Frame(self.notebook, padding=10)
        self.tab_tournaments = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.tab_registry, text="🌎 System Registry (Players & Teams)")
        self.notebook.add(self.tab_tournaments, text="🏆 Tournament Hub")
        
        self.notebook.pack(expand=True, fill="both")
        
        self.create_registry_tab()
        self.create_tournament_hub_tab()
    
    def create_registry_tab(self):
        """Creates the player and team registry tab."""
        main_frame = ttk.Frame(self.tab_registry)
        main_frame.pack(fill="both", expand=True)
        
        # --- Player Management Frame ---
        player_frame = ttk.LabelFrame(main_frame, text="Player Management")
        player_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        player_input_frame = ttk.Frame(player_frame)
        player_input_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(player_input_frame, text="Player Name:").pack(side="left", padx=5)
        self.player_name_entry = ttk.Entry(player_input_frame, width=15)
        self.player_name_entry.pack(side="left", padx=5)
        
        ttk.Label(player_input_frame, text="Sport:").pack(side="left", padx=5)
        self.player_sport_var = tk.StringVar(value=self.sport_names[0] if self.sport_names else "")
        self.player_sport_combo = ttk.Combobox(player_input_frame, textvariable=self.player_sport_var, values=self.sport_names, state="readonly", width=15)
        self.player_sport_combo.pack(side="left", padx=5)
        
        ttk.Label(player_input_frame, text="Rating:").pack(side="left", padx=5)
        self.player_rating_entry = ttk.Entry(player_input_frame, width=10)
        self.player_rating_entry.insert(0, "1000")
        self.player_rating_entry.pack(side="left", padx=5)
        
        ttk.Button(player_input_frame, text="Register Player", command=self.register_player).pack(side="left", padx=5)
        
        player_list_frame = ttk.Frame(player_frame)
        player_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        cols = ('Name', 'Sport', 'Rating', 'W-L-D')
        self.player_registry_tree = ttk.Treeview(player_list_frame, columns=cols, show='headings')
        self.player_registry_tree.heading("Name", text="Name")
        self.player_registry_tree.heading("Sport", text="Sport")
        self.player_registry_tree.heading("Rating", text="Rating")
        self.player_registry_tree.heading("W-L-D", text="W-L-D")
        self.player_registry_tree.pack(fill="both", expand=True)
        
        # --- Team Management Frame ---
        team_frame = ttk.LabelFrame(main_frame, text="Team Management")
        team_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        team_input_frame = ttk.Frame(team_frame)
        team_input_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(team_input_frame, text="Team Name:").pack(side="left", padx=5)
        self.team_name_entry = ttk.Entry(team_input_frame, width=15)
        self.team_name_entry.pack(side="left", padx=5)
        
        ttk.Label(team_input_frame, text="Sport:").pack(side="left", padx=5)
        self.team_sport_var = tk.StringVar(value=self.sport_names[0] if self.sport_names else "")
        self.team_sport_combo = ttk.Combobox(team_input_frame, textvariable=self.team_sport_var, values=self.sport_names, state="readonly", width=15)
        self.team_sport_combo.pack(side="left", padx=5)
        
        ttk.Button(team_input_frame, text="Create Team", command=self.create_team_dialog).pack(side="left", padx=5)
        
        team_list_frame = ttk.Frame(team_frame)
        team_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        cols = ('Name', 'Sport', 'Players')
        self.team_registry_tree = ttk.Treeview(team_list_frame, columns=cols, show='headings')
        self.team_registry_tree.heading("Name", text="Team Name")
        self.team_registry_tree.heading("Sport", text="Sport")
        self.team_registry_tree.heading("Players", text="Players")
        self.team_registry_tree.pack(fill="both", expand=True)
        
        self.update_player_registry_tree()
        self.update_team_registry_tree()
    
    def register_player(self):
        """Registers a new player."""
        name = self.player_name_entry.get().strip()
        sport_name = self.player_sport_var.get()
        
        try:
            rating = int(self.player_rating_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Rating must be a number.")
            return
        
        if not name:
            messagebox.showerror("Error", "Please enter a player name.")
            return
        if not sport_name:
            messagebox.showerror("Error", "Please select a sport.")
            return
        
        player = Player(name, sport_name, rating=rating)
        self.registered_players.append(player)
        self.update_player_registry_tree()
        
        self.player_name_entry.delete(0, "end")
        self.player_rating_entry.delete(0, "end")
        self.player_rating_entry.insert(0, "1000")
        messagebox.showinfo("Success", f"Player '{name}' registered successfully.")
    
    def update_player_registry_tree(self):
        """Refreshes the player registry tree view."""
        self.player_registry_tree.delete(*self.player_registry_tree.get_children())
        for player in self.registered_players:
            record = f"{player.wins}-{player.losses}-{player.draws}"
            self.player_registry_tree.insert("", "end", values=(player.name, player.sport_name, player.rating, record))
    
    def create_team_dialog(self):
        """Opens the team editor window."""
        name = self.team_name_entry.get().strip()
        sport_name = self.team_sport_var.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter a team name.")
            return
        if not sport_name:
            messagebox.showerror("Error", "Please select a sport.")
            return
        
        sport_obj = self.available_sports.get(sport_name)
        if not sport_obj or sport_obj.team_size == 1:
            messagebox.showerror("Error", f"'{sport_name}' is not a team sport.")
            return
        
        self.team_name_entry.delete(0, "end")
        TeamEditorWindow(self.root, self, name, sport_obj)
        
    def create_tournament_hub_tab(self):
        """Creates the tournament management hub tab."""
        main_frame = ttk.Frame(self.tab_tournaments)
        main_frame.pack(fill="both", expand=True)
        
        # --- Create Tournament Frame ---
        create_frame = ttk.LabelFrame(main_frame, text="Create New Tournament")
        create_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(create_frame, text="Tournament Name:").pack(side="left", padx=5)
        self.tourn_name_entry = ttk.Entry(create_frame, width=20)
        self.tourn_name_entry.pack(side="left", padx=5)
        
        ttk.Label(create_frame, text="Sport:").pack(side="left", padx=5)
        self.tourn_sport_var = tk.StringVar(value=self.sport_names[0] if self.sport_names else "")
        self.tourn_sport_combo = ttk.Combobox(create_frame, textvariable=self.tourn_sport_var, values=self.sport_names, state="readonly", width=15)
        self.tourn_sport_combo.pack(side="left", padx=5)
        
        ttk.Label(create_frame, text="Format:").pack(side="left", padx=5)
        self.tourn_format_var = tk.StringVar(value=self.format_names[0] if self.format_names else "")
        self.tourn_format_combo = ttk.Combobox(create_frame, textvariable=self.tourn_format_var, values=self.format_names, state="readonly", width=15)
        self.tourn_format_combo.pack(side="left", padx=5)
        
        ttk.Button(create_frame, text="Create Tournament", command=self.create_tournament).pack(side="left", padx=5)
        
        # --- Tournaments List ---
        list_frame = ttk.LabelFrame(main_frame, text="Active Tournaments")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        cols = ('Name', 'Sport', 'Format', 'Round')
        self.tournaments_tree = ttk.Treeview(list_frame, columns=cols, show='headings')
        self.tournaments_tree.heading("Name", text="Tournament Name")
        self.tournaments_tree.heading("Sport", text="Sport")
        self.tournaments_tree.heading("Format", text="Format")
        self.tournaments_tree.heading("Round", text="Round")
        self.tournaments_tree.pack(fill="both", expand=True)
        
        self.tournaments_tree.bind('<Double-Button-1>', self.open_tournament_manager)
        
        self.update_tournaments_tree()
    
    def create_tournament(self):
        """Creates a new tournament."""
        name = self.tourn_name_entry.get().strip()
        sport_name = self.tourn_sport_var.get()
        format_name = self.tourn_format_var.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter a tournament name.")
            return
        if not sport_name or not format_name:
            messagebox.showerror("Error", "Please select a sport and format.")
            return
        
        sport_obj = self.available_sports.get(sport_name)
        if not sport_obj:
            messagebox.showerror("Error", f"Sport '{sport_name}' not found.")
            return
        
        tournament = Tournament(name, sport_obj, format_name, self.format_manager)
        self.tournaments.append(tournament)
        self.update_tournaments_tree()
        
        self.tourn_name_entry.delete(0, "end")
        messagebox.showinfo("Success", f"Tournament '{name}' created successfully.")
    
    def update_tournaments_tree(self):
        """Refreshes the tournaments list."""
        self.tournaments_tree.delete(*self.tournaments_tree.get_children())
        for tourn in self.tournaments:
            self.tournaments_tree.insert("", "end", values=(tourn.name, tourn.sport.name, tourn.format_name, tourn.round))
    
    def open_tournament_manager(self, event=None):
        """Opens the tournament manager window for the selected tournament."""
        selected_iid = self.tournaments_tree.selection()
        if not selected_iid:
            return
        
        values = self.tournaments_tree.item(selected_iid[0], 'values')
        tourn_name = values[0]
        
        tournament = next((t for t in self.tournaments if t.name == tourn_name), None)
        if tournament:
            TournamentManagerWindow(self.root, self, tournament)
        
    def get_unassigned_players(self, sport_name: str) -> list[Player]:
        """Finds players of a sport who are not yet on a team."""
        unassigned = []
        assigned_players = set()
        
        for team in self.registered_teams:
            for player in team.players:
                assigned_players.add(player)
        
        for player in self.registered_players:
            if player.sport_name == sport_name and player not in assigned_players:
                unassigned.append(player)
        
        return unassigned
    
    def update_team_registry_tree(self):
        """Refreshes the team registry tree view in the Registry tab."""
        self.team_registry_tree.delete(*self.team_registry_tree.get_children())
        for team in self.registered_teams:
            self.team_registry_tree.insert("", "end", values=(team.team_name, team.sport_name, f"{len(team.players)}/{team.max_players}"))