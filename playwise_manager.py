#!/usr/bin/env python3
import json
import random
import sys
import uuid
import os
import itertools

# ===============================================================
#  PLAYWISE TOURNAMENT MANAGER (v10.0 Final Evaluation Build)
#  Team: Data Drifters
#  Status: 100% Stable & Logic Verified
# ===============================================================

# ==========================================
# MODULE 0: UI & AESTHETICS
# ==========================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def boot_sequence():
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
    print(" STATUS:  SYSTEM ONLINE")
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
        # Stats Storage
        self.total_kills = 0
        self.total_deaths = 0
        self.kd_ratio = 0.0
        self.roster = [] # List of member names

    def calculate_kd(self):
        """Updates the K/D ratio based on total kills/deaths."""
        # FIX: Prevent division by zero crash
        if self.total_deaths == 0:
            self.kd_ratio = float(self.total_kills)
        else:
            self.kd_ratio = round(self.total_kills / self.total_deaths, 2)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        p = cls(data['name'], data['rating'], data['id'])
        p.score = data['score']
        p.opponents_played = data['opponents_played']
        p.active = data.get('active', True)
        p.roster = data.get('roster', [])
        p.total_kills = data.get('total_kills', 0)
        p.total_deaths = data.get('total_deaths', 0)
        p.kd_ratio = data.get('kd_ratio', 0.0)
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
        active_players = [p for p in tournament.participants.values() if p.active]
        active_ids = [p.id for p in active_players]
        
        if len(active_ids) < 2: return 0 

        new_matches = []

        # LEAGUE
        if tournament.format_type == "League":
            if len(active_ids) % 2 != 0: active_ids.append(None)
            num = len(active_ids)
            rotation = (tournament.round - 1) % (num - 1)
            moving = active_ids[1:]
            rotated = moving[rotation:] + moving[:rotation]
            order = [active_ids[0]] + rotated
            
            for i in range(num // 2):
                p1, p2 = order[i], order[num - 1 - i]
                if p1 and p2: new_matches.append(Match(p1, p2, tournament.round))
                elif p1: new_matches.append(Match(p1, None, tournament.round))
        
        # KNOCKOUT
        elif tournament.format_type == "Knockout":
            active_players.sort(key=lambda x: (x.score, x.rating), reverse=True)
            sorted_ids = [p.id for p in active_players]
            while len(sorted_ids) > 1:
                new_matches.append(Match(sorted_ids.pop(0), sorted_ids.pop(-1), tournament.round))
            if sorted_ids: new_matches.append(Match(sorted_ids[0], None, tournament.round))

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
    def process_result(tournament, match_id, winner_id, is_draw, k1=0, d1=0, k2=0, d2=0):
        match = next((m for m in tournament.matches if m.id == match_id), None)
        if not match: return False
        
        if tournament.format_type == "Knockout" and is_draw:
            print("\n❌ ERROR: Draws are forbidden in Knockout matches!")
            return False

        match.is_played = True
        match.winner_id = winner_id
        match.is_draw = is_draw
        
        p1 = tournament.participants[match.p1_id]
        # Update Stats P1
        p1.total_kills += k1
        p1.total_deaths += d1
        p1.calculate_kd()
        
        p2 = None
        if match.p2_id:
            p2 = tournament.participants[match.p2_id]
            # Update Stats P2
            p2.total_kills += k2
            p2.total_deaths += d2
            p2.calculate_kd()

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
        except IOError as e:
            print(f"\n❌ CRITICAL ERROR: COULD NOT SAVE DATA! ({e})")

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
            "3": "CS:GO 2 (5v5)",
            "4": "Chess",
            "5": "FIFA",
            "6": "Custom"
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

    def _get_roster_input(self, game_name, team_name):
        """Collects member names for a team."""
        roster = []
        # Logic: Team games get 5/4 players, others get 1 (single player)
        size = 5 if "Valorant" in game_name or "CS" in game_name else 4 if "BGMI" in game_name else 1
        
        # If it's effectively a single player game, skip roster
        if size == 1: return []
        
        print(f"\n--- 📝 Roster for {team_name} ---")
        for i in range(size):
            m = input(f"Member {i+1} Name (Role): ").strip()
            roster.append(m)
        return roster

    def _collect_stats(self, participant):
        """Loops through roster to collect individual Kills/Deaths."""
        # FIX: Handle cases with no roster (Custom game treated as single player)
        if not participant.roster: 
            # If no roster, ask for the entity stats directly
            try:
                print(f" > {participant.name}")
                k = int(input(f"   Total Kills/Points: ") or 0)
                if k < 0: k = 0
                d = int(input(f"   Total Deaths: ") or 0)
                if d < 0: d = 0
                return k, d
            except ValueError:
                return 0, 0
            
        print(f"\n📊 Enter Stats for Team: {participant.name}")
        team_k = 0
        team_d = 0
        
        for member in participant.roster:
            try:
                print(f" > {member}")
                k = int(input(f"   Kills/Finishes: ") or 0)
                if k < 0: k = 0 # FIX: Prevent negative stats
                d = int(input(f"   Deaths: ") or 0)
                if d < 0: d = 0
                
                # Show individual K/D immediately
                kd = k if d == 0 else round(k/d, 2)
                print(f"   [Player K/D: {kd}]")
                
                team_k += k
                team_d += d
            except ValueError:
                print("   Invalid input, counting as 0.")
        
        print(f"--- Team Total: {team_k} Kills / {team_d} Deaths ---")
        return team_k, team_d

    def create_t(self):
        print("\n--- ⚙️  SETUP ---")
        name = input("Tournament Name: ").strip()
        if not name: return

        print("\nSelect Game:")
        for k, v in self.presets.items(): print(f"{k}. {v}")
        g = input("> ")
        sport = self.presets.get(g, "Unknown")
        if g == '6': sport = input("Enter Game Name: ")

        print("\nSelect Format: 1.League 2.Knockout 3.Swiss")
        f = input("> ")
        fmt = "League" if f=='1' else "Knockout" if f=='2' else "Swiss"

        t = Tournament(name, sport, fmt)
        self.tournaments[t.id] = t
        
        print(f"\n--- REGISTER {'TEAMS' if 'Chess' not in sport else 'PLAYERS'} ---")
        c = 1
        while True:
            n = input(f"Participant {c} Name: ").strip()
            if n.lower() == 'done':
                if len(t.participants) < 2: print("Need 2+."); continue
                break
            if not n: continue
            
            r = 1000
            if "Chess" in sport:
                try: r = int(input("Rating (1000): ") or 1000)
                except: pass
            
            p = Participant(n, r)
            if "Chess" not in sport:
                p.roster = self._get_roster_input(sport, n)
                
            t.participants[p.id] = p
            c += 1
        
        DataManager.save(self.tournaments)
        print("✅ Saved!")

    def display_leaderboard(self, t):
        print(f"\n📊 LEADERBOARD: {t.name}")
        sorted_p = sorted(t.participants.values(), key=lambda x: x.score, reverse=True)
        label = "Rating" if "Chess" in t.sport_name else "Tm K/D"
        
        print("+" + "-"*60 + "+")
        print(f"| {'#':<3} | {'Name':<25} | {'Pts':<5} | {label:<6} | {'Sts':<3} |")
        print("+" + "-"*60 + "+")
        for i, p in enumerate(sorted_p, 1):
            nm = f"👑 {p.name}" if i==1 else p.name
            st = "IN" if p.active else "OUT"
            val = p.rating if "Chess" in t.sport_name else p.kd_ratio
            print(f"| {i:<3} | {nm:<25} | {p.score:<5} | {val:<6} | {st:<3} |")
        print("+" + "-"*60 + "+")

    def manage_t(self):
        if not self.tournaments: print("No data."); return
        t_list = list(self.tournaments.values())
        for i, t in enumerate(t_list): print(f"{i+1}. {t.name} ({t.sport_name})")
        try:
            t = t_list[int(input("ID: ")) - 1]
        except: return

        while True:
            print(f"\n--- {t.name} [Round {t.round}] ---")
            print("1. Generate Matches  2. Enter Results  3. Leaderboard  4. Next Round  5. Back")
            act = input("> ")
            
            if act == '1':
                curr = [m for m in t.matches if m.round == t.round]
                if curr: print("Matches ready.")
                else:
                    c = AlgorithmEngine.generate_fixtures(t)
                    DataManager.save(self.tournaments)
                    print(f"✅ {c} Generated.")
            
            elif act == '2':
                matches = [m for m in t.matches if not m.is_played]
                if t.format_type != "League": matches = [m for m in matches if m.round == t.round]
                
                if not matches: print("No pending matches.")
                else:
                    for i, m in enumerate(matches):
                        p1 = t.participants[m.p1_id]
                        p2 = t.participants[m.p2_id] if m.p2_id else None
                        p2_name = p2.name if p2 else "BYE"
                        print(f"{i+1}. {p1.name} vs {p2_name}")
                    
                    try:
                        idx = int(input("Match #: ")) - 1
                        if idx < 0: continue
                        tgt = matches[idx]
                        
                        if not tgt.p2_id:
                            AlgorithmEngine.process_result(t, tgt.id, None, False)
                            print("✅ Bye.")
                        else:
                            p1 = t.participants[tgt.p1_id]
                            p2 = t.participants[tgt.p2_id]
                            
                            # Collect Stats
                            k1, d1 = 0, 0
                            k2, d2 = 0, 0
                            
                            if "Chess" not in t.sport_name:
                                k1, d1 = self._collect_stats(p1)
                                k2, d2 = self._collect_stats(p2)

                            print(f"\nWinner? 1.{p1.name} 2.{p2.name} 3.Draw")
                            r = input("> ")
                            wid = p1.id if r=='1' else p2.id if r=='2' else None
                            
                            AlgorithmEngine.process_result(t, tgt.id, wid, r=='3', k1, d1, k2, d2)
                            print("✅ Saved.")
                        DataManager.save(self.tournaments)
                    except Exception as e: print(f"Error: {e}")

            elif act == '3': self.display_leaderboard(t)
            elif act == '4':
                curr = [m for m in t.matches if m.round == t.round]
                if not curr or not all(m.is_played for m in curr): print("Finish matches first.")
                else:
                    actv = len([p for p in t.participants.values() if p.active])
                    if t.format_type == "Knockout" and actv <= 1:
                        print("🏆 WINNER FOUND!"); t.is_finished = True
                    else:
                        t.round += 1; print("⏩ Next Round.")
                    DataManager.save(self.tournaments)
            elif act == '5': break

if __name__ == "__main__":
    app = ConsoleUI()
    app.run()