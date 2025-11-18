#!/usr/bin/env python3
import json
import random
import sys
import uuid
import os
import time

# ===============================================================
#  PLAYWISE TOURNAMENT MANAGER (v4.0 Evaluation Build)
#  Team: Data Drifters
#  Target: Pre-Project Evaluation (80% Completion)
# ===============================================================

# ==========================================
# MODULE 0: STARTUP (UI/UX - Deepak & Shimon)
# ==========================================

def boot_sequence():
    """
    Displays team details. This runs first to impress evaluators.
    """
    os.system('cls' if os.name == 'nt' else 'clear') # Clears terminal
    print("System Check: [OK]")
    time.sleep(0.2)
    print("Loading Modules... [OK]")
    time.sleep(0.2)
    
    print(r"""
    ____  _     ___  __  __        __  _  ____  ____ 
   / __ \| |   /   | \ \/ /       | | | |/ ___|| ____|
  / / _` | |  / /| |  \  /  _____ | | | |\___ \|  _|  
 | | (_| | | / ___ |  /  \ |_____|| |_| | ___) | |___ 
  \ \__,_|_|/_/  |_| /_/\_\        \___/ |____/|_____|
   \____/                                             
    """)
    print("="*65)
    print(" TEAM: DATA DRIFTERS | PROJECT: TOURNAMENT MANAGER")
    print("="*65)
    print(f"{'ROLE':<20} {'NAME':<20} {'ID':<15}")
    print("-" * 65)
    print(f"{'Team Lead':<20} {'Shimon Pandey':<20} {'S25CSEU0993':<15}")
    print(f"{'Data Models':<20} {'Arshpreet Singh':<20} {'S25CSEU0980':<15}")
    print(f"{'Algorithms':<20} {'Krish Agarwal':<20} {'S25CSEU0985':<15}")
    print(f"{'Analytics/Stats':<20} {'Adityan':<20} {'S25CSEU0977':<15}")
    print(f"{'UI/UX':<20} {'Deepak Bisht':<20} {'S25CSEU0986':<15}")
    print("="*65)
    print("\n[Press Enter to Initialize System...]")
    input()

# ==========================================
# MODULE 1: DATA MODELS (Arshpreet's Code)
# ==========================================
# Concepts: OOP, Classes, Encapsulation

class Participant:
    """
    Represents a single player or team. 
    We use a Dictionary conversion (to_dict) for saving to files.
    """
    def __init__(self, name, rating=1000, p_id=None):
        self.id = p_id if p_id else str(uuid.uuid4()) # Unique ID generator
        self.name = name
        self.rating = int(rating)
        self.score = 0.0
        self.opponents_played = [] # Keeps track of history for Swiss format
        self.active = True # False if eliminated in Knockout

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        p = cls(data['name'], data['rating'], data['id'])
        p.score = data['score']
        p.opponents_played = data['opponents_played']
        p.active = data.get('active', True)
        return p

class Match:
    """
    Represents a single game between two participants.
    """
    def __init__(self, p1_id, p2_id, round_num):
        self.id = str(uuid.uuid4())
        self.p1_id = p1_id
        self.p2_id = p2_id # If None, it means a "BYE" (Automatic win)
        self.round = round_num
        self.winner_id = None
        self.is_draw = False
        self.is_played = False

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        m = cls(data['p1_id'], data['p2_id'], data['round'])
        m.id = data['id']
        m.winner_id = data['winner_id']
        m.is_draw = data['is_draw']
        m.is_played = data['is_played']
        return m

class Tournament:
    """
    The container for all players and matches.
    """
    def __init__(self, name, sport_name, format_type, t_id=None):
        self.id = t_id if t_id else str(uuid.uuid4())
        self.name = name
        self.sport_name = sport_name
        self.format_type = format_type
        self.participants = {} # Dictionary: { uuid : Participant_Object }
        self.matches = []      # List of Match Objects
        self.round = 1
        self.is_finished = False
    
    def to_dict(self):
        # Convert complex objects to simple data for JSON saving
        return {
            "id": self.id, "name": self.name, "sport_name": self.sport_name,
            "format_type": self.format_type, "round": self.round, "is_finished": self.is_finished,
            "participants": {k: v.to_dict() for k, v in self.participants.items()},
            "matches": [m.to_dict() for m in self.matches]
        }

    @classmethod
    def from_dict(cls, data):
        t = cls(data['name'], data['sport_name'], data['format_type'], data['id'])
        t.participants = {k: Participant.from_dict(v) for k, v in data['participants'].items()}
        t.matches = [Match.from_dict(m) for m in data['matches']]
        t.round = data['round']
        t.is_finished = data.get('is_finished', False)
        return t

# ==========================================
# MODULE 2: ALGORITHMS (Krish's Code)
# ==========================================
# Concepts: Sorting, Recursion, List Manipulation

class AlgorithmEngine:
    
    @staticmethod
    def generate_fixtures(tournament):
        """
        Decides who plays who based on the Tournament Format.
        """
        # Filter only active players (important for Knockouts)
        active_ids = [p.id for p in tournament.participants.values() if p.active]
        
        if not active_ids: 
            print("❌ Error: No active participants found.")
            return 0

        new_matches = []

        # --- LEAGUE FORMAT (Round Robin) ---
        if tournament.format_type == "League":
            if tournament.round == 1: 
                # In League, we generate all matches at the start
                import itertools
                # Combinations(n, 2) gives all unique pairs
                for p1, p2 in itertools.combinations(active_ids, 2):
                    new_matches.append(Match(p1, p2, 1))
        
        # --- KNOCKOUT FORMAT (Seeding) ---
        elif tournament.format_type == "Knockout":
            # Sort by Rating (Highest vs Lowest concept)
            players = [tournament.participants[x] for x in active_ids]
            players.sort(key=lambda x: x.rating, reverse=True)
            sorted_ids = [p.id for p in players]
            
            # Pair Top vs Bottom until list is empty
            while len(sorted_ids) > 1:
                top_seed = sorted_ids.pop(0)
                bottom_seed = sorted_ids.pop(-1)
                new_matches.append(Match(top_seed, bottom_seed, tournament.round))
            
            # If one player left, they get a BYE
            if sorted_ids:
                new_matches.append(Match(sorted_ids[0], None, tournament.round))

        # --- SWISS FORMAT (Backtracking Logic) ---
        elif tournament.format_type == "Swiss":
            # 1. Sort players by Score (High to Low)
            players = [tournament.participants[x] for x in active_ids]
            players.sort(key=lambda x: (x.score, x.rating), reverse=True)
            
            # 2. Use recursive logic to find valid pairs
            paired = AlgorithmEngine._swiss_backtrack(players, [])
            
            # 3. Fallback if logic fails (Rare edge case)
            if not paired: 
                random.shuffle(players) # Last resort: Random
                while len(players) > 1:
                    new_matches.append(Match(players.pop(0).id, players.pop(0).id, tournament.round))
                if players: new_matches.append(Match(players[0].id, None, tournament.round))
            else:
                for p1, p2 in paired:
                    new_matches.append(Match(p1.id, p2.id if p2 else None, tournament.round))

        tournament.matches.extend(new_matches)
        return len(new_matches)

    @staticmethod
    def _swiss_backtrack(players, current_pairs):
        """
        Recursive helper to find pairs that haven't played each other yet.
        """
        if not players: return current_pairs # Base case: Everyone paired
        
        p1 = players[0]
        
        # Try to find a valid opponent for p1
        for i in range(1, len(players)):
            p2 = players[i]
            # Check history: Have they played?
            if p2.id not in p1.opponents_played:
                # Tentatively pair them and recurse
                res = AlgorithmEngine._swiss_backtrack(players[1:i] + players[i+1:], current_pairs + [(p1, p2)])
                if res: return res # If solution found, return it
        
        # Bye handling (if player is left alone)
        if len(players) == 1 and None not in p1.opponents_played:
             return current_pairs + [(p1, None)]
        
        return None # No solution in this branch

    @staticmethod
    def update_scores(tournament, match_id, winner_id, is_draw):
        """
        Updates scores and eliminates players if necessary.
        """
        # Search for the match
        match = next((m for m in tournament.matches if m.id == match_id), None)
        
        if not match: return False
        
        match.is_played = True
        match.winner_id = winner_id
        match.is_draw = is_draw
        
        p1 = tournament.participants[match.p1_id]
        p2 = tournament.participants[match.p2_id] if match.p2_id else None

        # Update History
        if p2:
            p1.opponents_played.append(p2.id)
            p2.opponents_played.append(p1.id)

        # Update Points
        if not p2: # Bye
            p1.score += 1.0
            match.winner_id = p1.id
        elif is_draw:
            p1.score += 0.5
            p2.score += 0.5
        else:
            winner = p1 if p1.id == winner_id else p2
            loser = p2 if winner == p1 else p1
            winner.score += 1.0
            
            # Logic for Elimination
            if tournament.format_type == "Knockout":
                loser.active = False
        return True

# ==========================================
# MODULE 3: PERSISTENCE (File Handling)
# ==========================================
# Concepts: JSON, File I/O, Error Handling

class DataManager:
    FILE_NAME = "playwise_db.json"

    @staticmethod
    def save(tournaments):
        # List Comprehension to process data
        data = [t.to_dict() for t in tournaments.values()]
        try:
            with open(DataManager.FILE_NAME, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            print("⚠️  Error: Could not save data. Check permissions.")

    @staticmethod
    def load():
        if not os.path.exists(DataManager.FILE_NAME): return {}
        try:
            with open(DataManager.FILE_NAME, 'r') as f:
                data = json.load(f)
                return {d['id']: Tournament.from_dict(d) for d in data}
        except (json.JSONDecodeError, IOError):
            return {}

# ==========================================
# MODULE 4: UI & ANALYTICS (Deepak & Adityan)
# ==========================================
# Concepts: Input Validation, Formatting, String Manipulation

class ConsoleUI:
    def __init__(self):
        self.tournaments = DataManager.load()

    def run(self):
        boot_sequence() 
        while True:
            print(f"\n=== 🏆 MAIN MENU 🏆 ===")
            print("1. New Tournament")
            print("2. Load Tournament")
            print("3. Exit")
            
            choice = input("Select Option: ").strip()
            
            if choice == '1': self.create_flow()
            elif choice == '2': self.manage_flow()
            elif choice == '3': 
                print("Shutting down system... Goodbye!")
                sys.exit()
            else:
                print("Invalid choice, try again.")

    def create_flow(self):
        print("\n--- ⚙️  SETUP WIZARD ---")
        name = input("Tournament Name: ").strip()
        if not name:
            print("❌ Name cannot be empty.")
            return

        print("\nSelect Sport:")
        print("1. Chess")
        print("2. Valorant")
        print("3. Custom")
        s = input("> ").strip()
        sport = "Chess" if s=='1' else "Valorant" if s=='2' else input("Enter Sport Name: ")

        print("\nSelect Format:")
        print("1. League (Round Robin)")
        print("2. Knockout (Elimination)")
        print("3. Swiss (Balanced Pairing)")
        f = input("> ").strip()
        fmt = "League" if f=='1' else "Knockout" if f=='2' else "Swiss"

        # Create Object
        t = Tournament(name, sport, fmt)
        self.tournaments[t.id] = t
        
        print("\n--- 👥 ADD PARTICIPANTS ---")
        print("(Type 'done' when finished)")
        count = 1
        while True:
            p_name = input(f"Player {count} Name: ").strip()
            if p_name.lower() == 'done': 
                if len(t.participants) < 2:
                    print("❌ Need at least 2 players.")
                    continue
                break
            
            # Try/Except for integer validation
            try:
                rating_input = input(f"Rating (Def 1000): ").strip()
                rating = int(rating_input) if rating_input else 1000
            except ValueError:
                print("⚠️  Invalid number, setting to 1000.")
                rating = 1000
            
            pt = Participant(p_name, rating)
            t.participants[pt.id] = pt
            count += 1
        
        DataManager.save(self.tournaments)
        print("✅ Tournament Saved Successfully.")

    def display_leaderboard(self, t):
        """
        Adityan's Component: The 'Cool' Leaderboard.
        Uses formatted strings for a table-like look.
        """
        print(f"\n📊 LEADERBOARD: {t.name.upper()}")
        print("+" + "-"*48 + "+")
        print(f"| {'Rank':<4} | {'Player Name':<20} | {'Score':<6} | {'Status':<8} |")
        print("+" + "-"*48 + "+")
        
        # Sorting Logic
        sorted_p = sorted(t.participants.values(), key=lambda x: x.score, reverse=True)
        
        for idx, p in enumerate(sorted_p, 1):
            status = "Active" if p.active else "Out"
            # Conditional formatting for the leader
            prefix = "👑" if idx == 1 else "  "
            name_display = f"{prefix} {p.name}"
            
            print(f"| {idx:<4} | {name_display:<20} | {p.score:<6} | {status:<8} |")
        
        print("+" + "-"*48 + "+")

    def manage_flow(self):
        if not self.tournaments: 
            print("❌ No tournaments found.")
            return
        
        print("\n--- LOAD TOURNAMENT ---")
        t_list = list(self.tournaments.values())
        for i, t in enumerate(t_list):
            print(f"{i+1}. {t.name} ({t.sport_name}) [{t.format_type}]")
        
        try:
            sel = int(input("Enter ID: ")) - 1
            if sel < 0 or sel >= len(t_list): raise ValueError
            t = t_list[sel]
        except ValueError: 
            print("❌ Invalid selection.")
            return
        
        while True:
            print(f"\n--- MENU: {t.name} (Round {t.round}) ---")
            print("1. Generate Fixtures")
            print("2. Enter Results")
            print("3. View Leaderboard (Adityan's Module)")
            print("4. Next Round")
            print("5. Back")
            
            act = input("> ").strip()
            
            if act == '1':
                count = AlgorithmEngine.generate_fixtures(t)
                DataManager.save(self.tournaments)
                print(f"✅ Generated {count} matches.")
            
            elif act == '2':
                # Filter unplayed matches
                matches = [m for m in t.matches if m.round == t.round and not m.is_played]
                if not matches: 
                    print("✅ All matches played!")
                else:
                    for i, m in enumerate(matches):
                        p1 = t.participants[m.p1_id].name
                        p2 = t.participants[m.p2_id].name if m.p2_id else "BYE"
                        print(f"{i+1}. {p1} vs {p2}")
                    
                    try:
                        mid = int(input("Select Match #: ")) - 1
                        target = matches[mid]
                        
                        if not target.p2_id:
                            AlgorithmEngine.update_scores(t, target.id, None, False)
                            print("✅ Bye Recorded.")
                        else:
                            p1n = t.participants[target.p1_id].name
                            p2n = t.participants[target.p2_id].name
                            print(f"Who won? 1.{p1n} 2.{p2n} 3.Draw")
                            res = input("> ")
                            
                            wid = target.p1_id if res=='1' else target.p2_id if res=='2' else None
                            is_d = (res == '3')
                            AlgorithmEngine.update_scores(t, target.id, wid, is_d)
                            print("✅ Result Recorded.")
                            
                        DataManager.save(self.tournaments)
                    except (ValueError, IndexError):
                        print("❌ Invalid Input.")

            elif act == '3':
                self.display_leaderboard(t)

            elif act == '4':
                # Validation: Are all matches done?
                current_round_matches = [m for m in t.matches if m.round == t.round]
                if not current_round_matches:
                    print("⚠️  No matches generated for this round yet.")
                elif not all(m.is_played for m in current_round_matches):
                    print("⚠️  Cannot advance: Complete all matches first.")
                else:
                    # Check if tournament is over
                    active_count = len([p for p in t.participants.values() if p.active])
                    if active_count <= 1 and t.format_type == "Knockout":
                        print("🏆 Tournament Complete! Check Leaderboard for Winner.")
                        t.is_finished = True
                    else:
                        t.round += 1
                        print(f"⏩ Advanced to Round {t.round}")
                    DataManager.save(self.tournaments)
            
            elif act == '5': break

if __name__ == "__main__":
    app = ConsoleUI()
    app.run()