#!/usr/bin/env python3
import json
import random
import sys
import uuid
import os
import time
import itertools

# ===============================================================
#  PLAYWISE TOURNAMENT MANAGER (v6.0 Final Stable)
#  Team: Data Drifters
#  Status: Evaluation Ready
# ===============================================================

# ==========================================
# MODULE 0: UI & AESTHETICS
# ==========================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def boot_sequence():
    clear_screen()
    print("Initializing Playwise Core Systems...")
    sys.stdout.write("[")
    for i in range(20):
        sys.stdout.write("=")
        sys.stdout.flush()
        time.sleep(0.02) 
    sys.stdout.write("] OK\n")
    time.sleep(0.2)
    clear_screen()
    
    print(r"""
    ____  __    ___  __  __ _       __  ____  _____    ______
   / __ \/ /   /   | \ \/ /| |     / / /  _/ / ___/   / ____/
  / /_/ / /   / /| |  \  / | | /| / /  / /   \__ \   / __/   
 / ____/ /___/ ___ |  / /  | |/ |/ / _/ /   ___/ /  / /___   
/_/   /_____/_/  |_| /_/   |__/|__/ /___/  /____/  /_____/   
    """)
    print("="*70)
    print(" PROJECT: Playwise Tournament Manager")
    print(" TEAM:    DATA DRIFTERS")
    print("="*70)
    print(f"{'ROLE':<20} {'NAME':<25} {'CONTRIBUTION'}")
    print("-" * 70)
    print(f"{'Team Lead':<20} {'Shimon Pandey':<25} {'System Architecture'}")
    print(f"{'Data Engineer':<20} {'Arshpreet Singh':<25} {'Data Models & Seeding'}")
    print(f"{'Algo Engineer':<20} {'Krish Agarwal':<25} {'Fixture Algorithms'}")
    print(f"{'Analytics Lead':<20} {'Adityan':<25} {'Leaderboard & Stats'}")
    print(f"{'UI/UX Lead':<20} {'Deepak Bisht':<25} {'Interface & Presets'}")
    print("-" * 70)
    print(" IDs: S25CSEU0993, S25CSEU0980, S25CSEU0985, S25CSEU0977, S25CSEU0986")
    print("="*70)
    print("\n[Press Enter to Launch]")
    input()

# ==========================================
# MODULE 1: DATA MODELS
# ==========================================

class Participant:
    def __init__(self, name, rating=1000, p_id=None):
        self.id = p_id if p_id else str(uuid.uuid4())
        self.name = name
        self.rating = int(rating)
        self.score = 0.0
        self.opponents_played = [] 
        self.active = True 

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
    def __init__(self, p1_id, p2_id, round_num):
        self.id = str(uuid.uuid4())
        self.p1_id = p1_id
        self.p2_id = p2_id # None = BYE
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
    def __init__(self, name, sport_name, format_type, t_id=None):
        self.id = t_id if t_id else str(uuid.uuid4())
        self.name = name
        self.sport_name = sport_name
        self.format_type = format_type
        self.participants = {} 
        self.matches = []
        self.round = 1
        self.is_finished = False
    
    def to_dict(self):
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
# MODULE 2: ALGORITHMS 
# ==========================================

class AlgorithmEngine:
    
    @staticmethod
    def generate_fixtures(tournament):
        # Get active players
        active_players = [p for p in tournament.participants.values() if p.active]
        active_ids = [p.id for p in active_players]
        
        if len(active_ids) < 2: return 0 

        new_matches = []

        # LEAGUE
        if tournament.format_type == "League":
            if tournament.round == 1: 
                for p1, p2 in itertools.combinations(active_ids, 2):
                    new_matches.append(Match(p1, p2, 1))
        
        # KNOCKOUT
        elif tournament.format_type == "Knockout":
            active_players.sort(key=lambda x: x.rating, reverse=True)
            sorted_ids = [p.id for p in active_players]
            
            while len(sorted_ids) > 1:
                top = sorted_ids.pop(0)
                bot = sorted_ids.pop(-1)
                new_matches.append(Match(top, bot, tournament.round))
            
            if sorted_ids: 
                new_matches.append(Match(sorted_ids[0], None, tournament.round))

        # SWISS
        elif tournament.format_type == "Swiss":
            active_players.sort(key=lambda x: (x.score, x.rating), reverse=True)
            pool = active_players.copy()
            
            while pool:
                p1 = pool.pop(0)
                if not pool: 
                    new_matches.append(Match(p1.id, None, tournament.round))
                    break
                
                found = False
                for i in range(len(pool)):
                    p2 = pool[i]
                    if p2.id not in p1.opponents_played:
                        new_matches.append(Match(p1.id, p2.id, tournament.round))
                        pool.pop(i)
                        found = True
                        break
                
                if not found:
                    p2 = pool.pop(0)
                    new_matches.append(Match(p1.id, p2.id, tournament.round))

        tournament.matches.extend(new_matches)
        return len(new_matches)

    @staticmethod
    def process_result(tournament, match_id, winner_id, is_draw):
        match = next((m for m in tournament.matches if m.id == match_id), None)
        if not match: return False
        
        if tournament.format_type == "Knockout" and is_draw:
            print("\n❌ ERROR: Draws are forbidden in Knockout matches!")
            return False

        match.is_played = True
        match.winner_id = winner_id
        match.is_draw = is_draw
        
        p1 = tournament.participants[match.p1_id]
        p2 = tournament.participants[match.p2_id] if match.p2_id else None

        if p2:
            p1.opponents_played.append(p2.id)
            p2.opponents_played.append(p1.id)

        if not p2: # Bye
            p1.score += 1.0
            match.winner_id = p1.id
        elif is_draw:
            p1.score += 0.5
            p2.score += 0.5
        else:
            if p1.id == winner_id:
                p1.score += 1.0
                loser = p2
            else:
                p2.score += 1.0
                loser = p1
            
            if tournament.format_type == "Knockout":
                loser.active = False
                
        return True

# ==========================================
# MODULE 3: DATA MANAGER
# ==========================================

class DataManager:
    FILE_NAME = "playwise_data.json"

    @staticmethod
    def save(tournaments):
        data = [t.to_dict() for t in tournaments.values()]
        try:
            with open(DataManager.FILE_NAME, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass

    @staticmethod
    def load():
        if not os.path.exists(DataManager.FILE_NAME): return {}
        try:
            with open(DataManager.FILE_NAME, 'r') as f:
                data = json.load(f)
                return {d['id']: Tournament.from_dict(d) for d in data}
        except Exception:
            return {}

# ==========================================
# MODULE 4: UI & ANALYTICS
# ==========================================

class ConsoleUI:
    def __init__(self):
        self.tournaments = DataManager.load()
        self.presets = {
            "1": "Valorant (5v5)",
            "2": "BGMI (Squad)",
            "3": "FIFA (1v1)",
            "4": "Chess",
            "5": "Table Tennis",
            "6": "Carrom",
            "7": "Custom"
        }

    def run(self):
        boot_sequence()
        while True:
            print(f"\n=== 🏆 MAIN MENU 🏆 ===")
            print("1. Create Tournament")
            print("2. Manage Tournament")
            print("3. Exit")
            
            choice = input("Choice: ").strip()
            
            if choice == '1': self.create_t()
            elif choice == '2': self.manage_t()
            elif choice == '3': 
                print("Exiting...")
                sys.exit()

    def create_t(self):
        print("\n--- ⚙️  SETUP ---")
        name = input("Tournament Name: ").strip()
        if not name: return

        print("\nSelect Game:")
        for k, v in self.presets.items():
            print(f"{k}. {v}")
        g = input("> ")
        sport = self.presets.get(g, "Unknown")
        if g == '7': sport = input("Enter Game Name: ")

        print("\nSelect Format:")
        print("1. League")
        print("2. Knockout")
        print("3. Swiss")
        f = input("> ")
        fmt = "League" if f=='1' else "Knockout" if f=='2' else "Swiss"

        t = Tournament(name, sport, fmt)
        self.tournaments[t.id] = t
        
        print("\n--- REGISTER PLAYERS (Type 'done' to finish) ---")
        c = 1
        while True:
            n = input(f"Player {c}: ").strip()
            if n.lower() == 'done':
                if len(t.participants) < 2:
                    print("Need 2+ players.")
                    continue
                break
            if not n: continue
            
            try:
                r = int(input(f"Rating (1000): ") or 1000)
            except: r = 1000
            
            p = Participant(n, r)
            t.participants[p.id] = p
            c += 1
        
        DataManager.save(self.tournaments)
        print("✅ Saved!")

    def display_leaderboard(self, t):
        print(f"\n📊 LEADERBOARD: {t.name}")
        sorted_p = sorted(t.participants.values(), key=lambda x: x.score, reverse=True)
        print("+" + "-"*40 + "+")
        print(f"| {'#':<3} | {'Name':<20} | {'Pts':<5} | {'Sts':<3} |")
        print("+" + "-"*40 + "+")
        for i, p in enumerate(sorted_p, 1):
            nm = f"👑 {p.name}" if i==1 else p.name
            st = "IN" if p.active else "OUT"
            print(f"| {i:<3} | {nm:<20} | {p.score:<5} | {st:<3} |")
        print("+" + "-"*40 + "+")

    def manage_t(self):
        if not self.tournaments: 
            print("No data.")
            return

        t_list = list(self.tournaments.values())
        for i, t in enumerate(t_list):
            print(f"{i+1}. {t.name} ({t.sport_name})")
        
        try:
            sel = int(input("ID: ")) - 1
            t = t_list[sel]
        except: return

        while True:
            # Calculate match stats
            total_matches = len(t.matches)
            played_matches = len([m for m in t.matches if m.is_played])
            
            print(f"\n--- {t.name} [Round {t.round}] ---")
            print(f"Matches: {played_matches}/{total_matches}")
            print("1. Generate Matches")
            print("2. View Matches & Result")
            print("3. Leaderboard")
            print("4. Next Round")
            print("5. Back")
            
            act = input("> ")
            
            if act == '1':
                # Only generate if current round has no matches
                curr = [m for m in t.matches if m.round == t.round]
                if curr:
                    print("⚠️  Matches already generated for this round.")
                else:
                    c = AlgorithmEngine.generate_fixtures(t)
                    DataManager.save(self.tournaments)
                    print(f"✅ {c} Matches Generated.")
            
            elif act == '2':
                # Filter matches to show
                matches = [m for m in t.matches if not m.is_played]
                # For Knockout/Swiss only show current round
                if t.format_type != "League":
                    matches = [m for m in matches if m.round == t.round]
                
                if not matches:
                    print("✅ No pending matches.")
                else:
                    print("\n--- PENDING MATCHES ---")
                    for i, m in enumerate(matches):
                        p1 = t.participants[m.p1_id].name
                        p2 = t.participants[m.p2_id].name if m.p2_id else "BYE"
                        print(f"{i+1}. {p1} vs {p2}")
                    
                    try:
                        sel_idx = int(input("\nEnter Match # to result (0 to cancel): ")) - 1
                        if sel_idx == -1: continue
                        
                        target = matches[sel_idx]
                        
                        if not target.p2_id:
                            AlgorithmEngine.process_result(t, target.id, None, False)
                            print("✅ Bye Auto-processed.")
                        else:
                            p1 = t.participants[target.p1_id]
                            p2 = t.participants[target.p2_id]
                            print(f"\nWinner?\n1. {p1.name}\n2. {p2.name}\n3. Draw")
                            r = input("> ")
                            
                            wid = p1.id if r=='1' else p2.id if r=='2' else None
                            is_d = (r == '3')
                            
                            if AlgorithmEngine.process_result(t, target.id, wid, is_d):
                                print("✅ Saved.")
                        DataManager.save(self.tournaments)
                    except: print("Invalid Input.")

            elif act == '3':
                self.display_leaderboard(t)

            elif act == '4':
                curr = [m for m in t.matches if m.round == t.round]
                if not curr:
                    print("⚠️  Generate matches first.")
                elif not all(m.is_played for m in curr):
                    print("⚠️  Finish all matches first.")
                else:
                    active = len([p for p in t.participants.values() if p.active])
                    if t.format_type == "Knockout" and active <= 1:
                        print("🏆 TOURNAMENT OVER!")
                        t.is_finished = True
                    else:
                        t.round += 1
                        print(f"⏩ Round {t.round} Started.")
                    DataManager.save(self.tournaments)

            elif act == '5': break

if __name__ == "__main__":
    app = ConsoleUI()
    app.run()