#!/usr/bin/env python3
#
# ===============================================================
#  Playwise Tournament Management System
#  Modular, scalable esports, chess, & sports tournament manager
#  Version 2.1 - Polished & Verified
# ===============================================================
#

import itertools
import random
import sys
from collections import defaultdict

# === MODULE 1: MODELS ===
# Contains the data classes for Players, Teams, and Sports.

class Sport:
    """
    Defines a sport, its team size, and scoring rules.
    """
    def __init__(self, name, team_size=1, allow_draws=True):
        self.name = name
        self.team_size = team_size  # 1 for individual (Chess), 5 for Valorant, 3 for Basketball
        self.allow_draws = allow_draws

    def __str__(self):
        if self.team_size == 1:
            return f"{self.name} (Individual)"
        return f"{self.name} ({self.team_size}v{self.team_size})"


class Player:
    """
    Player for esports/chess with role, rating, and stats.
    """
    def __init__(self, name, sport_name, role="Player", rating=1000):
        self.name = name
        self.sport_name = sport_name # The name of the sport, e.g., "Chess"
        self.role = role
        self.rating = rating
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def record_result(self, result):
        if result == 'win': self.wins += 1
        elif result == 'loss': self.losses += 1
        elif result == 'draw': self.draws += 1

    def __str__(self):
        return f"{self.name} ({self.sport_name}) - Role: {self.role} - Rating: {self.rating}"

class Team:
    """
    Team class for team-based e-sports.
    Size is determined by the Sport object.
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
        self.draws = 0 # Added for sports that allow draws

    def add_player(self, player: Player):
        if len(self.players) >= self.max_players:
            print(f"❌ [Error] Team {self.team_name} is full ({self.max_players} players).")
            return False
        if player.sport_name != self.sport_name:
            print(f"❌ [Error] Player {player.name} plays {player.sport_name}, can't join {self.sport_name} team.")
            return False
        if player in self.players:
            print(f"⚠️ [Warning] Player {player.name} already in team.")
            return False
        
        self.players.append(player)
        print(f"✅ [Info] Added {player.name} to {self.team_name}.")
        return True

    def record_match(self, result):
        self.matches_played += 1
        if result == 'win': self.wins += 1
        elif result == 'loss': self.losses += 1
        elif result == 'draw': self.draws += 1

    def __str__(self):
        names = ', '.join(p.name for p in self.players)
        if not names:
            names = "No players yet"
        return f"Team {self.team_name} ({self.sport_name}) [{len(self.players)}/{self.max_players}]: {names}"

# === MODULE 2: FORMAT MANAGEMENT ===
# Manages tournament format logic (League, Knockout, Swiss).

class FormatManager:
    """
    Manage tournament formats and their fixture-generation handlers.
    """
    def __init__(self):
        self.formats = {
            'League': self.league_format,
            'Knockout': self.knockout_format,
            'Swiss': self.swiss_format
        }

    def add_format(self, name, handler):
        self.formats[name] = handler

    def league_format(self, tournament):
        """
        Generate league fixtures: all-play-all combination.
        """
        print("✅ [Info] Generating Round-Robin League fixtures...")
        contestants = tournament.get_active_contestants()
        tournament.matches = list(itertools.combinations(contestants, 2))

    def knockout_format(self, tournament):
        """
        Knockout fixtures: random pairing, with handling for byes.
        Only pairs contestants who have not been eliminated.
        """
        print("✅ [Info] Generating Knockout fixtures...")
        active = tournament.get_active_contestants()
        random.shuffle(active)
        tournament.matches = []
        
        while len(active) > 1:
            c1 = active.pop()
            c2 = active.pop()
            tournament.matches.append((c1, c2))
        
        if active:  # Handle a bye
            bye_contestant = active.pop()
            tournament.matches.append((bye_contestant, None))
            # Automatically record the bye result
            tournament.record_result((bye_contestant, None), tournament._contestant_name(bye_contestant))

    def swiss_format(self, tournament):
        """
        Generate Swiss system fixtures.
        - Round 1 is random.
        - Subsequent rounds pair players with similar scores.
        - Avoids rematches.
        """
        print(f"✅ [Info] Generating Swiss fixtures for Round {tournament.round}...")
        active = tournament.get_active_contestants()
        tournament.matches = []

        if tournament.round == 1:
            # Round 1: Pair randomly
            random.shuffle(active)
        else:
            # Subsequent rounds: Sort by points (descending), then rating (descending)
            active.sort(key=lambda c: (tournament.points[tournament._contestant_name(c)], c.rating), reverse=True)

        # Create pairings
        paired_contestants = set()
        
        for i in range(len(active)):
            c1 = active[i]
            if c1 in paired_contestants:
                continue

            # Find an opponent
            opponent_found = False
            for j in range(i + 1, len(active)):
                c2 = active[j]
                if c2 in paired_contestants:
                    continue
                
                # Check if they have played before
                if c2 not in tournament.opponents_played[c1]:
                    tournament.matches.append((c1, c2))
                    paired_contestants.add(c1)
                    paired_contestants.add(c2)
                    opponent_found = True
                    break
            
            if not opponent_found and c1 not in paired_contestants:
                # If no opponent found (or odd number), assign a bye
                tournament.matches.append((c1, None))
                paired_contestants.add(c1)
                # Automatically record the bye result
                tournament.record_result((c1, None), tournament._contestant_name(c1))

        print(f"✅ [Info] {len(tournament.matches)} matches generated for Round {tournament.round}.")

# === MODULE 3: TOURNAMENT CORE ===
# The main Tournament class that manages state, contestants, and results.

class Tournament:
    def __init__(self, name: str, sport_obj: Sport, format_name: str, format_manager: FormatManager):
        self.name = name
        self.sport = sport_obj
        self.format_name = format_name
        self.format_manager = format_manager
        
        self.players = []
        self.teams = []
        
        self.matches = []
        self.results = {} # Stores results of completed matches
        self.points = defaultdict(float) # Use float for 0.5 points in Swiss
        self.eliminated = set()
        self.opponents_played = defaultdict(set) # For Swiss: {player_obj: {opponent1_obj, ...}}
        
        self.round = 1
        
        # Set scoring rules based on format
        if format_name == 'Swiss':
            self.points_for_win = 1.0
            self.points_for_draw = 0.5
            self.points_for_bye = 1.0 # Points for receiving a bye
        else: # League, etc.
            self.points_for_win = 3
            self.points_for_draw = 1
            self.points_for_bye = 0 # Byes in League/Knockout don't typically award points, just advancement

    def add_contestant(self, contestant):
        """Adds a Player or a Team to the tournament."""
        if isinstance(contestant, Player):
            if contestant.sport_name != self.sport.name:
                print(f"❌ [Error] Player {contestant.name} does not play {self.sport.name}!")
                return False
            if self.sport.team_size > 1:
                print(f"❌ [Error] This is a team tournament. Cannot add individual player {contestant.name}.")
                return False
            if contestant in self.players:
                print(f"⚠️ [Warning] Player {contestant.name} is already in this tournament.")
                return False
            self.players.append(contestant)
            
        elif isinstance(contestant, Team):
            if contestant.sport_name != self.sport.name:
                print(f"❌ [Error] Team {contestant.team_name} does not play {self.sport.name}!")
                return False
            if self.sport.team_size == 1:
                 print(f"❌ [Error] This is an individual tournament. Cannot add team {contestant.team_name}.")
                 return False
            if contestant in self.teams:
                print(f"⚠️ [Warning] Team {contestant.team_name} is already in this tournament.")
                return False
            self.teams.append(contestant)
        
        print(f"✅ [Info] Added contestant: {self._contestant_name(contestant)}")
        return True

    def get_active_contestants(self):
        """Returns a list of contestants who are not eliminated."""
        base_list = self.teams if self.sport.team_size > 1 else self.players
        if self.format_name == 'Knockout':
            return [c for c in base_list if c not in self.eliminated]
        return base_list

    def generate_fixtures(self):
        print(f"✅ [Info] Generating fixtures for {self.format_name} format...")
        handler = self.format_manager.formats.get(self.format_name)
        if not handler:
            print("❌ [Error] Format handler not found!")
            return
        # Clear old matches before generating new ones (for next rounds)
        self.matches.clear()
        self.results.clear()
        handler(self)

    def record_result(self, match, winner_name, is_draw=False):
        """Records the result of a match."""
        if match in self.results:
            print("⚠️ [Warning] Result for this match already recorded.")
            return

        c1, c2 = match
        c1_name = self._contestant_name(c1)
        c2_name = self._contestant_name(c2) if c2 else "BYE"

        # Handle Bye
        if c2 is None:
            self.results[match] = c1_name
            if self.format_name == 'Swiss':
                # Bye-winner gets points
                self.points[c1_name] += self.points_for_bye
                print(f"✅ [Info] {c1_name} receives {self.points_for_bye} points for a bye.")
            else:
                 print(f"✅ [Info] {c1_name} advances by bye.")
            return
        
        # Mark match as played
        self.results[match] = winner_name if not is_draw else "DRAW"

        # Update opponent lists for Swiss
        if self.format_name == 'Swiss':
            self.opponents_played[c1].add(c2)
            self.opponents_played[c2].add(c1)

        # Handle Draw
        if is_draw:
            if not self.sport.allow_draws:
                print("❌ [Error] This sport does not allow draws. Please record a winner.")
                self.results.pop(match) # Remove invalid result
                return
            if self.format_name in ['League', 'Swiss']:
                self.points[c1_name] += self.points_for_draw
                self.points[c2_name] += self.points_for_draw
                self._record_draw(c1)
                self._record_draw(c2)
                print(f"✅ [Info] Match {c1_name} vs {c2_name} ended in a draw.")
            else:
                 print("❌ [Error] Knockout matches cannot be a draw.")
                 self.results.pop(match) # Remove invalid result
                 return
        
        # Handle Win/Loss
        else:
            if self.format_name in ['League', 'Swiss']:
                self.points[winner_name] += self.points_for_win
            
            winner, loser = (c1, c2) if c1_name == winner_name else (c2, c1)
            
            self._record_win(winner)
            self._record_loss(loser)
            print(f"✅ [Info] Winner: {winner_name}")
            
            if self.format_name == 'Knockout':
                self.eliminated.add(loser)
                print(f"🚫 [Info] {self._contestant_name(loser)} has been eliminated.")
    
    def next_round(self):
        """Advances the tournament to the next round (Knockout and Swiss)."""
        if self.format_name not in ['Knockout', 'Swiss']:
            print("❌ [Error] Only Knockout and Swiss formats support multiple rounds.")
            return
        
        # Check if all matches from the current round are played
        if len(self.matches) > len(self.results):
             print("❌ [Error] Cannot generate next round. Not all matches from this round are recorded.")
             return

        active_contestants = self.get_active_contestants()
        if len(active_contestants) <= 1:
            if active_contestants:
                print(f"\n=========================")
                print(f"🏆 WINNER: {self._contestant_name(active_contestants[0])} 🏆")
                print(f"=========================")
            else:
                print("⚠️ [Warning] No active contestants left to determine a winner.")
            return

        self.round += 1
        print(f"\n✅ [Info] Advancing to Round {self.round}...")
        self.generate_fixtures()
        self.show_fixtures()

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

    # --- Display Methods ---

    def show_fixtures(self):
        print(f"\n--- 🗓️ Fixtures for {self.name} - Round {self.round} ---")
        if not self.matches:
            print("  [Info] Fixtures not generated yet.")
            return
            
        unplayed_matches = [m for m in self.matches if m not in self.results]
        
        if not unplayed_matches:
            print("  [Info] All matches for this round have been played.")
        
        for idx, match in enumerate(unplayed_matches, 1):
            c1 = self._contestant_name(match[0])
            c2 = self._contestant_name(match[1])
            print(f"  {idx}. {c1} VS {c2}")
            
        if self.results and unplayed_matches:
             print("  --- Completed Matches ---")
             for match, result in self.results.items():
                 c1_name = self._contestant_name(match[0])
                 c2_name = self._contestant_name(match[1])
                 if c2_name == "BYE":
                     print(f"  ✓ {c1_name} had a BYE")
                 elif result == "DRAW":
                     print(f"  ✓ {c1_name} vs {c2_name}: DRAW")
                 else:
                     print(f"  ✓ {c1_name} vs {c2_name}: {result} Won")


    def show_leaderboard(self):
        print(f"\n--- 📊 Leaderboard for {self.name} ({self.format_name.upper()}) ---")
        if self.format_name == 'Knockout':
            print("  Active (Not Eliminated):")
            for c in self.get_active_contestants():
                print(f"    - {self._contestant_name(c)}")
            if self.eliminated:
                print("\n  Eliminated:")
                for c in self.eliminated:
                    print(f"    - {self._contestant_name(c)}")
        else:
            # Sort by points (descending)
            sorted_pts = sorted(self.points.items(), key=lambda item: item[1], reverse=True)
            if not sorted_pts:
                print("  [Info] No results recorded yet.")
                return
            
            print(f"  {'Pos':<5} {'Name':<25} {'Points':<10}")
            print(f"  {'-'*4} {'-'*24} {'-'*9}")
            for idx, (name, pts) in enumerate(sorted_pts, 1):
                # Format points to 1 decimal place
                print(f"  {idx:<5} {name:<25} {pts:<10.1f}")

# === MODULE 4: UI MANAGER ===
# Handles all user interface logic, menus, and prompts.

def input_int(prompt, min_val=None, max_val=None):
    """Utility function to get validated integer input."""
    while True:
        try:
            val_str = input(prompt).strip()
            val = int(val_str)
            if (min_val is not None and val < min_val) or \
               (max_val is not None and val > max_val):
                print(f"❌ [Error] Input must be between {min_val} and {max_val}. Try again.")
                continue
            return val
        except ValueError:
            print("❌ [Error] Invalid input. Please enter a number.")

class MainMenu:
    def __init__(self):
        self.format_manager = FormatManager()
        self.registered_players = []
        self.registered_teams = []
        self.tournaments = []
        
        # Pre-populate available sports
        self.available_sports = {
            '1': Sport("Chess", team_size=1, allow_draws=True),
            '2': Sport("Valorant", team_size=5, allow_draws=False),
            '3': Sport("CSGO", team_size=5, allow_draws=False),
            '4': Sport("PUBG", team_size=4, allow_draws=False), # <-- [FIX #1] Corrected '4::' to '4'
            '5': Sport("3v3 Basketball", team_size=3, allow_draws=False),
        }

    def run(self):
        """Starts the main application loop."""
        print(r"""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║            PLAYWISE TOURNAMENT MANAGEMENT SYSTEM               ║
    ║                                                                ║
    ║                   Welcome to Playwise                          ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
        while True:
            print("\n--- Main Menu---")
            print("1. 👤 Register Player")
            print("2. 👥 Register Team")
            print("3. 🏆 Manage Tournaments")
            print("4. 🚪 Exit")
            choice = input("Choice: ").strip()
            
            if choice == '1':
                self.register_player_interface()
            elif choice == '2':
                self.register_team_interface()
            elif choice == '3':
                self.tournament_menu()
            elif choice == '4':
                print("\nExiting Playwise. Goodbye! 👋\n")
                sys.exit(0)
            else:
                print("❌ [Error] Invalid choice. Please try again.")

    def _select_sport(self):
        """Helper to prompt user to select a sport."""
        print("Available Sports:")
        for k, sport in self.available_sports.items():
            print(f"  {k}. {sport}")
        
        while True:
            choice = input("Select sport: ").strip()
            if choice in self.available_sports:
                return self.available_sports[choice]
            else:
                print("❌ [Error] Invalid sport choice.")

    def register_player_interface(self):
        print("\n--- 👤 Register New Player ---")
        name = input("Enter player name/gamer tag: ").strip()
        if not name:
            print("❌ [Error] Name cannot be empty.")
            return
            
        # --- [FIX #3] Check for player name uniqueness ---
        if name in [p.name for p in self.registered_players]:
            print(f"❌ [Error] A player with the name '{name}' already exists.")
            return
            
        sport_obj = self._select_sport()
        sport_name = sport_obj.name
        
        role = "Player"
        if sport_name.lower() != 'chess':
            role = input(f"Enter player role (e.g., IGL, Sniper, Point Guard): ").strip()
            if not role:
                role = "Player" # Default role
            
        rating = input_int("Enter rating (e.g., 1000): ", 0)
        
        player = Player(name, sport_name, role, rating)
        self.registered_players.append(player)
        print(f"\n✅ Registered: {player}")

    def register_team_interface(self):
        print("\n--- 👥 Register New Team ---")
        sport_obj = self._select_sport()
        
        if sport_obj.team_size == 1:
            print(f"❌ [Error] {sport_obj.name} is an individual sport. Cannot create a team.")
            return

        team_name = input(f"Enter team name for {sport_obj.name}: ").strip()
        if not team_name:
            print("❌ [Error] Team name cannot be empty.")
            return

        # --- [FIX #3] Check for team name uniqueness ---
        if team_name in [t.team_name for t in self.registered_teams]:
            print(f"❌ [Error] A team with the name '{team_name}' already exists.")
            return

        # Find available players for this sport
        available_players = [
            p for p in self.registered_players 
            if p.sport_name == sport_obj.name
            and not any(p in t.players for t in self.registered_teams if t.sport_name == sport_obj.name)
        ]

        # --- [FIX #9] Prevent team creation if not enough players are available ---
        if len(available_players) < sport_obj.team_size:
            print(f"\n❌ [Error] Not enough available players ({len(available_players)}) to form a full {sport_obj.team_size}-player team.")
            print("✅ [Info] Please register more players for this sport first.")
            return
        
        print(f"\nAvailable unassigned players (Need {sport_obj.team_size}):")
        for idx, p in enumerate(available_players, 1):
            print(f"  {idx}. {p.name} ({p.role})")
        
        team = Team(team_name, sport_obj)
        selected_players_for_this_team = []

        while len(team.players) < team.max_players:
            # Re-filter list to show remaining players
            display_available = [p for p in available_players if p not in selected_players_for_this_team]
            if not display_available:
                print("✅ [Info] No more available players to add.")
                break

            for idx, p in enumerate(display_available, 1):
                print(f"  {idx}. {p.name} ({p.role})")

            choice = input_int(f"Select player {len(team.players) + 1} by number (or 0 to finish): ", 0, len(display_available))
            if choice == 0:
                break
                
            player_to_add = display_available[choice - 1]
            
            if team.add_player(player_to_add):
                selected_players_for_this_team.append(player_to_add)
        
        # --- [FIX #9 Follow-up] Only create team if full ---
        if len(team.players) < team.max_players:
            print(f"\n❌ [Error] Team creation cancelled. A full team of {team.max_players} players is required.")
            return # Team object is discarded, players remain available

        self.registered_teams.append(team)
        print(f"\n✅ Created team: {team}")

    def _select_tournament(self):
        """Helper to select a tournament from the list."""
        if not self.tournaments:
            print("✅ [Info] No tournaments exist.")
            return None
        
        print("\nSelect Tournament:")
        for idx, t in enumerate(self.tournaments, 1):
            print(f"  {idx}. {t.name} ({t.sport.name} - {t.format_name})")
        
        t_idx = input_int("Choice: ", 1, len(self.tournaments))
        return self.tournaments[t_idx - 1]

    def tournament_menu(self):
        """Display the menu for managing tournaments."""
        while True:
            print("\n--- 🏆 Tournament Menu 🏆 ---")
            print("1. Create New Tournament")
            print("2. Add Contestants to Tournament")
            print("3. Generate Fixtures")
            print("4. Show Fixtures")
            print("5. Record Match Result")
            print("6. Show Leaderboard/Bracket")
            print("7. Advance to Next Round")
            print("8. Back to Main Menu")
            choice = input("Select an option: ").strip()

            if choice == '1':
                self.create_tournament()
            elif choice == '2':
                self.add_contestants_to_tournament()
            elif choice == '3':
                t = self._select_tournament()
                if t: t.generate_fixtures()
            elif choice == '4':
                t = self._select_tournament()
                if t: t.show_fixtures()
            elif choice == '5':
                self.record_match_result()
            elif choice == '6':
                t = self._select_tournament()
                if t: t.show_leaderboard()
            elif choice == '7':
                t = self._select_tournament()
                if t: t.next_round()
            elif choice == '8':
                break
            else:
                print("❌ [Error] Invalid option.")

    def create_tournament(self):
        print("\n--- ✨ Create New Tournament ---")
        t_name = input("Tournament name: ").strip()
        if not t_name:
            print("❌ [Error] Name cannot be empty.")
            return
            
        sport_obj = self._select_sport()
        
        print("Choose format:")
        formats = list(self.format_manager.formats.keys())
        valid_formats = []
        
        for fmt in formats:
            # Don't allow Swiss for team sports (it's complex)
            if fmt == 'Swiss' and sport_obj.team_size > 1:
                continue
            valid_formats.append(fmt)
        
        for k, fmt_name in enumerate(valid_formats, 1):
             print(f"  {k}. {fmt_name}")
        
        f_choice = input_int("Format choice: ", 1, len(valid_formats))
        format_name = valid_formats[f_choice - 1]
        
        tournament = Tournament(t_name, sport_obj, format_name, self.format_manager)
        self.tournaments.append(tournament)
        print(f"\n✅ Tournament '{t_name}' created with {format_name} format for {sport_obj.name}.")

    def add_contestants_to_tournament(self):
        tournament = self._select_tournament()
        if not tournament:
            return

        print(f"\n--- ＋ Add Contestants to {tournament.name} ---")
        
        available_contestants = []
        if tournament.sport.team_size > 1:
            # Get teams for this sport
            available_contestants = [
                t for t in self.registered_teams 
                if t.sport_name == tournament.sport.name
                and t not in tournament.teams
            ]
            print("Available Teams:")
        else:
            # Get players for this sport
            available_contestants = [
                p for p in self.registered_players
                if p.sport_name == tournament.sport.name
                and p not in tournament.players
            ]
            print("Available Players:")

        if not available_contestants:
            print("  None available.")
            return

        for idx, c in enumerate(available_contestants, 1):
            print(f"  {idx}. {tournament._contestant_name(c)}")
        
        while True:
            if not available_contestants:
                print("✅ [Info] All available contestants have been added.")
                break
                
            choice_str = input("Select contestant by number (or 'done' to finish): ").strip().lower()
            if choice_str == 'done':
                break
            try:
                choice = int(choice_str)
                if 1 <= choice <= len(available_contestants):
                    contestant_to_add = available_contestants[choice - 1]
                    
                    # add_contestant returns True on success
                    if tournament.add_contestant(contestant_to_add):
                        # Remove from list to prevent re-adding
                        available_contestants.pop(choice - 1)
                        # Re-print remaining
                        print("\nRemaining available contestants:")
                        if not available_contestants:
                            print("  None.")
                        for idx, c in enumerate(available_contestants, 1):
                            print(f"  {idx}. {tournament._contestant_name(c)}")
                else:
                    print("❌ [Error] Invalid number.")
            except ValueError:
                print("❌ [Error] Invalid input. Enter a number or 'done'.")

    def record_match_result(self):
        tournament = self._select_tournament()
        if not tournament:
            return

        if not tournament.matches:
            print("❌ [Error] No fixtures generated yet!")
            return
        
        unplayed_matches = [m for m in tournament.matches if m not in tournament.results]
        
        if not unplayed_matches:
            print("✅ [Info] All matches for this round have been played.")
            return

        print("\nSelect Match to Record:")
        for idx, match in enumerate(unplayed_matches, 1):
            c1 = tournament._contestant_name(match[0])
            c2 = tournament._contestant_name(match[1])
            print(f"  {idx}. {c1} VS {c2}")
        
        m_idx = input_int("Match number: ", 1, len(unplayed_matches))
        selected_match = unplayed_matches[m_idx - 1]
        
        c1_name = tournament._contestant_name(selected_match[0])
        c2_name = tournament._contestant_name(selected_match[1])

        print("\nSelect Result:")
        print(f"1. {c1_name} (Winner)")
        print(f"2. {c2_name} (Winner)")
        
        options = 2
        # --- [FIX #4] Only show draw if sport allows AND it's not Knockout ---
        if tournament.sport.allow_draws and tournament.format_name != 'Knockout':
            print("3. Match was a Draw")
            options = 3
        
        res_choice = input_int("Result: ", 1, options)
        
        if res_choice == 1:
            tournament.record_result(selected_match, c1_name, is_draw=False)
        elif res_choice == 2:
            tournament.record_result(selected_match, c2_name, is_draw=False)
        elif res_choice == 3 and tournament.sport.allow_draws and tournament.format_name != 'Knockout':
            tournament.record_result(selected_match, "", is_draw=True)


# === MODULE 5: MAIN ===
# The main entry point for the application.
# To run the program, save as playwise.py and execute: python playwise.py

def main():
    """
    Initializes and runs the main application menu.
    """
    app = MainMenu()
    app.run()

if __name__ == "__main__":
    main()