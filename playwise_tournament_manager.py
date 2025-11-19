#!/usr/bin/env python3
import json       # For saving data
import random     # For shuffling players
import sys        # For exiting the program
import uuid       # For unique IDs
import os         # For clearing the screen
import time       # For animations
import itertools  # For creating match combinations

# ===============================================================
#  PLAYWISE TOURNAMENT MANAGER (v17.3 ASCII CLEANED)
#  Fixes: Guaranteed removal of all non-standard space characters.
# ===============================================================

# --- CONFIGURATION ---
TEAM_SIZES = {
    "Valorant": 5,
    "CS:GO": 5,
    "BGMI": 4,
    "PUBG": 4,
    "FIFA": 1,
    "Chess": 1,
    "Table Tennis": 1,
    "Carrom": 2,
    "Badminton": 2
}

# ==========================================
# MODULE 0: UI & AESTHETICS
# ==========================================

def clear_screen():
    """Clears the terminal window for a fresh view."""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Mac/Linux
        os.system('clear')

def get_valid_int(prompt, min_val=None, max_val=None):
    """Reusable function for safe number input."""
    while True:
        try:
            val_str = input(prompt).strip()
            # Allow empty input to return 0, unless min_val dictates otherwise
            if not val_str:
                if min_val is not None and min_val > 0:
                    print(f"⚠️ Input required, must be at least {min_val}.")
                    continue
                return 0
            val = int(val_str)

            if min_val is not None and val < min_val:
                print(f"⚠️ Number must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"⚠️ Number must be at most {max_val}.")
                continue
            return val
        except ValueError:
            print("❌ That wasn't a valid number. Please try again.")

def boot_sequence():
    """Displays the startup animation and team credits."""
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
    print(" STATUS:  SYSTEM ONLINE")
    print("="*70)
    print(f"{'ROLE':<20} {'NAME':<25} {'CONTRIBUTION'}")
    print("-" * 70)
    print(f"{'Team Lead':<20} {'Shimon Pandey':<25} {'System Architecture'}")
    print(f"{'Data Architect':<20} {'Arshpreet Singh':<25} {'Data Models & Seeding'}")
    print(f"{'Logic Developer':<20} {'Krish Agarwal':<25} {'Fixture Algorithms'}")
    print(f"{'Analytics & Stats':<20} {'Adityan':<25} {'Leaderboard Logic'}")
    print(f"{'Interface Designer':<20} {'Deepak Bisht':<25} {'Menus & Validation'}")
    print("-" * 70)
    print(" IDs: S25CSEU0993, S25CSEU0980, S25CSEU0985, S25CSEU0977, S25CSEU0986")
    print("="*70)
    print("\n[Press Enter to Launch]")
    input()

# ==========================================
# MODULE 1: DATA MODELS
# ==========================================

class Participant:
    """Stores info about a player or a team."""
    def __init__(self, name, rating=1000, p_id=None):
        self.id = p_id if p_id else str(uuid.uuid4())
        self.name = name
        self.rating = int(rating)
        self.score = 0.0
        self.opponents_played = []
        self.active = True

        # Team Stats (Kills/Goals - total)
        self.stat_primary = 0
        self.stat_secondary = 0
        self.performance_ratio = 0.0
        # Roster is a list of dicts: [{'name': 'Player', 'role': 'IGL', 'stats': {'p': 0, 's': 0}}]
        self.roster = []

    def update_performance(self):
        """Calculates team K/D or Goal ratio."""
        if self.stat_secondary > 0:
            self.performance_ratio = round(self.stat_primary / self.stat_secondary, 2)
        else:
            self.performance_ratio = float(self.stat_primary)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        p = cls(data['name'], data['rating'], data['id'])
        p.score = data['score']
        p.opponents_played = data['opponents_played']
        p.active = data.get('active', True)
        p.roster = data.get('roster', [])
        p.stat_primary = data.get('stat_primary', 0)
        p.stat_secondary = data.get('stat_secondary', 0)
        p.performance_ratio = data.get('performance_ratio', 0.0)
        return p

class Match:
    """Stores data for a single game."""
    def __init__(self, p1_id, p2_id, round_num):
        self.id = str(uuid.uuid4())
        self.p1_id = p1_id
        self.p2_id = p2_id
        self.round = round_num
        self.winner_id = None
        self.is_draw = False
        self.is_played = False
        self.match_mvp = None

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        m = cls(data['p1_id'], data['p2_id'], data['round'])
        m.id = data['id']
        m.winner_id = data['winner_id']
        m.is_draw = data['is_draw']
        m.is_played = data['is_played']
        m.match_mvp = data.get('match_mvp')
        return m

class Tournament:
    """The main container for the event."""
    def __init__(self, name, sport_name, format_type, t_id=None):
        self.id = t_id if t_id else str(uuid.uuid4())
        self.name = name
        self.sport_name = sport_name
        self.format_type = format_type
        self.participants = {}
        self.matches = []
        self.round = 1
        self.is_finished = False
        self.history = []

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "sport_name": self.sport_name,
            "format_type": self.format_type, "round": self.round, "is_finished": self.is_finished,
            "participants": {k: v.to_dict() for k, v in self.participants.items()},
            "matches": [m.to_dict() for m in self.matches],
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data):
        t = cls(data['name'], data['sport_name'], data['format_type'], data['id'])
        t.participants = {k: Participant.from_dict(v) for k, v in data['participants'].items()}
        t.matches = [Match.from_dict(m) for m in data['matches']]
        t.round = data['round']
        t.is_finished = data.get('is_finished', False)
        t.history = data.get('history', [])
        return t

# ==========================================
# MODULE 2: ALGORITHMS
# ==========================================

class AlgorithmEngine:

    @staticmethod
    def generate_fixtures(tournament):
        """Logic to pair players based on format."""
        active_players = [p for p in tournament.participants.values() if p.active]
        # Seed players by score, then rating
        active_players.sort(key=lambda x: (x.score, x.rating), reverse=True)
        active_ids = [p.id for p in active_players]

        if len(active_ids) < 2: return 0

        new_matches = []
        is_odd = len(active_ids) % 2 != 0

        # LEAGUE (Round Robin) - Gives BYE to highest seed if odd
        if tournament.format_type == "League":
            if is_odd:
                # Highest seeded player gets the bye
                bye_player_id = active_ids.pop(0)
                new_matches.append(Match(bye_player_id, None, tournament.round))

            num = len(active_ids) # Now guaranteed even
            if num > 0:
                # Standard Round Robin rotation
                rotation = (tournament.round - 1) % (num - 1)
                fixed = active_ids[0]
                moving = active_ids[1:]

                rotated = moving[rotation:] + moving[:rotation]
                order = [fixed] + rotated

                for i in range(num // 2):
                    p1, p2 = order[i], order[num - 1 - i]
                    new_matches.append(Match(p1, p2, tournament.round))

        # KNOCKOUT (Seeded)
        elif tournament.format_type == "Knockout":
            sorted_ids = [p.id for p in active_players]
            while len(sorted_ids) > 1:
                # Top vs Bottom pairing
                new_matches.append(Match(sorted_ids.pop(0), sorted_ids.pop(-1), tournament.round))
            if sorted_ids: new_matches.append(Match(sorted_ids[0], None, tournament.round))

        # SWISS (Fair Pairing)
        elif tournament.format_type == "Swiss":
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
                    # Pair with the next available opponent even if previously played
                    p2 = pool.pop(0)
                    new_matches.append(Match(p1.id, p2.id, tournament.round))

        tournament.matches.extend(new_matches)
        tournament.history.append(f"Round {tournament.round}: Generated {len(new_matches)} matches.")
        return len(new_matches)

    @staticmethod
    def process_result(tournament, match_id, winner_id, is_draw, p1_stats_list, p2_stats_list):
        """Updates scores, stats, and history log. pX_stats_list is list of {'p': k, 's': d}."""
        match = next((m for m in tournament.matches if m.id == match_id), None)
        if not match: return False

        if tournament.format_type == "Knockout" and is_draw:
            print("\n❌ ERROR: Draws are forbidden in Knockout matches!")
            return False

        match.is_played = True
        match.winner_id = winner_id
        match.is_draw = is_draw

        p1 = tournament.participants[match.p1_id]

        # --- 1. Update P1 Stats and Calculate MVP ---
        p1_p_total = sum(d['p'] for d in p1_stats_list)
        p1_s_total = sum(d['s'] for d in p1_stats_list)

        p1.stat_primary += p1_p_total
        p1.stat_secondary += p1_s_total

        for i, member in enumerate(p1.roster):
            if i < len(p1_stats_list):
                member['stats']['p'] += p1_stats_list[i]['p']
                member['stats']['s'] += p1_stats_list[i]['s']

        p1.update_performance()

        cat = ConsoleUI()._get_game_category(tournament.sport_name)
        all_player_stats = []

        # Compile all player stats for MVP calculation (only for current match, not career)
        for i, member in enumerate(p1.roster):
            if i < len(p1_stats_list):
                p, s = p1_stats_list[i]['p'], p1_stats_list[i]['s']
                ratio = p / s if s > 0 and cat == "SHOOTER" else p
                all_player_stats.append({'name': member['name'], 'ratio': ratio, 'team': p1.name})

        # --- 2. Update P2 Stats and Calculate MVP ---
        p2 = None
        if match.p2_id:
            p2 = tournament.participants[match.p2_id]
            p2_p_total = sum(d['p'] for d in p2_stats_list)
            p2_s_total = sum(d['s'] for d in p2_stats_list)

            p2.stat_primary += p2_p_total
            p2.stat_secondary += p2_s_total

            for i, member in enumerate(p2.roster):
                if i < len(p2_stats_list):
                    member['stats']['p'] += p2_stats_list[i]['p']
                    member['stats']['s'] += p2_stats_list[i]['s']

            p2.update_performance()

            for i, member in enumerate(p2.roster):
                if i < len(p2_stats_list):
                    p, s = p2_stats_list[i]['p'], p2_stats_list[i]['s']
                    ratio = p / s if s > 0 and cat == "SHOOTER" else p
                    all_player_stats.append({'name': member['name'], 'ratio': ratio, 'team': p2.name})

        # --- 3. Determine Final MVP ---
        if cat != "STRATEGY" and all_player_stats:
            mvp_player = max(all_player_stats, key=lambda x: x['ratio'])
            stat_label = "K/D" if cat == "SHOOTER" else "Goals"
            match.match_mvp = f"MVP: {mvp_player['name']} ({mvp_player['team']}) [{stat_label}: {round(mvp_player['ratio'], 2)}]"
        else:
            match.match_mvp = None

        # --- 4. Update Score and History ---
        log_entry = f"R{tournament.round}: {p1.name} vs {p2.name if p2 else 'BYE'} -> "

        if not p2:
            p1.score += 1.0; match.winner_id = p1.id; log_entry += "Winner: BYE"
        elif is_draw:
            p1.score += 0.5; p2.score += 0.5
            p1.opponents_played.append(p2.id); p2.opponents_played.append(p1.id)
            log_entry += "Draw"
        else:
            p1.opponents_played.append(p2.id); p2.opponents_played.append(p1.id)
            if p1.id == winner_id:
                p1.score += 1.0; loser = p2; log_entry += f"Winner: {p1.name}"
            else:
                p2.score += 1.0; loser = p1; log_entry += f"Winner: {p2.name}"

            if tournament.format_type == "Knockout": loser.active = False

        if match.match_mvp: log_entry += f" ({match.match_mvp})"
        tournament.history.append(log_entry)
        return True

# ==========================================
# MODULE 3: DATA MANAGER
# ==========================================

class DataManager:
    FILE_NAME = "playwise_data.json"

    @staticmethod
    def save(tournaments):
        """Saves all data to JSON. Shows error if fails."""
        data = [t.to_dict() for t in tournaments.values()]
        try:
            with open(DataManager.FILE_NAME, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"\n❌ CRITICAL ERROR: COULD NOT SAVE DATA! ({e})")

    @staticmethod
    def load():
        """Loads data safely from JSON."""
        if not os.path.exists(DataManager.FILE_NAME): return {}
        try:
            with open(DataManager.FILE_NAME, 'r') as f:
                data = json.load(f)
                return {d['id']: Tournament.from_dict(d) for d in data}
        except Exception as e:
            print(f"⚠️ Warning: Failed to load data from JSON ({e}). Starting fresh.")
            return {}

# ==========================================
# MODULE 4: UI & ANALYTICS
# ==========================================

class ConsoleUI:
    def __init__(self):
        self.tournaments = DataManager.load()
        self.presets = [
            "Valorant", "BGMI", "CS:GO", "FIFA", "Chess",
            "Table Tennis", "Carrom", "Badminton", "PUBG", "Custom"
        ]

    def run(self):
        """Main loop of the application."""
        boot_sequence()
        while True:
            print(f"\n=== 🏆 MAIN MENU 🏆 ===")
            print(f"Total Tournaments: {len(self.tournaments)}")
            print("1. Create Tournament")
            print("2. Manage Tournament")
            print("3. Delete Tournament")
            print("4. Help")
            print("5. Exit")

            choice = input("Choice: ").strip()
            if choice == '1': self.create_tournament()
            elif choice == '2': self.manage_tournament()
            elif choice == '3': self.delete_tournament()
            elif choice == '4': self.show_help()
            elif choice == '5':
                if input("Are you sure? (y/n): ").lower() == 'y':
                    print("Goodbye! Data saved.")
                    sys.exit()

    def show_help(self):
        print("\n--- 📖 HELP ---")
        print("1. **League**: Everyone plays everyone. Highest seed gets BYE if player count is odd.")
        print("2. **Knockout**: Elimination based on seeding (1st vs Last, 2nd vs 2nd Last, etc.).")
        print("3. **Swiss**: Score-based pairing, attempting to avoid opponents you've played.")
        print("4. **Shooter Games**: Require Kills (Primary) and Deaths (Secondary) stats. Only **one IGL** allowed.")
        input("\n[Press Enter]")

    def _get_game_category(self, game_name):
        """Returns: SHOOTER, SPORT, or STRATEGY"""
        shooters = ["Valorant", "BGMI", "PUBG", "CS:GO", "COD", "Fortnite"]
        normalized_name = game_name.upper()
        if any(s.upper() in normalized_name for s in shooters): return "SHOOTER"
        if "CHESS" in normalized_name: return "STRATEGY"
        return "SPORT"

    def _get_team_size(self, game_name):
        """Helper to get team size."""
        if "Custom" in game_name:
            return get_valid_int("Players per Team (1 for Solo): ", 1, 100)

        for key, val in TEAM_SIZES.items():
            if key in game_name:
                return val
        return 1 # Default to solo

    def _get_roster_input(self, game_name, team_name):
        """Asks for team members and enforces IGL constraint."""
        size = self._get_team_size(game_name)

        if size <= 1: return []

        print(f"\n--- 📝 Roster for {team_name} (Size: {size}) ---")
        roster_list = []
        igl_count = 0
        is_shooter = self._get_game_category(game_name) == "SHOOTER"

        for i in range(size):
            while True:
                member_name = input(f"Member {i+1} Name: ").strip()
                if not member_name: continue

                role = input(f"   Role (e.g., IGL, Entry, Goalie): ").strip() or "Player"

                is_igl_candidate = "IGL" in role.upper()

                if is_shooter and is_igl_candidate and igl_count >= 1:
                    print("❌ Shooter teams can only have **ONE IGL**. Please re-enter the role.")
                    continue

                if is_shooter and is_igl_candidate:
                    igl_count += 1

                roster_list.append({
                    'name': member_name,
                    'role': role,
                    'stats': {'p': 0, 's': 0}
                })
                break
        return roster_list

    def _collect_stats(self, participant, category):
        """Gets Kills/Deaths or Goals for all team members in the match."""

        if category == "STRATEGY": return [], 0, 0

        p_label = "Kills" if category == "SHOOTER" else "Goals/Pts"
        s_label = "Deaths" if category == "SHOOTER" else "Secondary Metric (e.g., Assists)"

        print(f"\n📊 Enter Match Stats for Team: **{participant.name}**")

        roster_to_use = participant.roster if participant.roster else [{'name': participant.name, 'role': 'Solo', 'stats': {'p': 0, 's': 0}}]

        match_stats_list = []
        team_p_total, team_s_total = 0, 0

        for member in roster_to_use:
            print(f" > {member['name']} ({member['role']})")
            p = get_valid_int(f"   {p_label}: ", 0)

            s = get_valid_int(f"   {s_label}: ", 0)

            if category == "SHOOTER":
                val_str = p / s if s > 0 else float(p)
                print(f"   [K/D: {round(val_str, 2)}]")

            team_p_total += p
            team_s_total += s
            match_stats_list.append({'p': p, 's': s})

        return match_stats_list, team_p_total, team_s_total

    def delete_tournament(self):
        t = self._select_tournament()
        if t:
            if input(f"❌ Delete '{t.name}'? (yes/no): ").lower() == 'yes':
                del self.tournaments[t.id]
                DataManager.save(self.tournaments)
                print("✅ Deleted.")

    def _select_tournament(self):
        if not self.tournaments: print("No tournament data loaded."); return None
        t_list = list(self.tournaments.values())
        print("\n--- Available Tournaments ---")
        for i, t in enumerate(t_list):
            status = "🏆 FINISHED" if t.is_finished else f"R{t.round}"
            print(f"{i+1}. {t.name:<20} ({t.sport_name}) - {status}")
        try:
            idx = get_valid_int("Enter ID to manage (0 for back): ", 0, len(t_list)) - 1
            if idx < 0: return None
            return t_list[idx]
        except: return None

    def create_tournament(self):
        print("\n--- ⚙️ SETUP ---")
        name = input("Tournament Name: ").strip()
        if not name: print("❌ Name required."); return

        print("\nSelect Game:")
        for i, game in enumerate(self.presets, 1): print(f"{i}. {game}")

        idx = get_valid_int("Choice: ", 1, len(self.presets)) - 1
        sport = self.presets[idx]
        if sport == "Custom":
            sport = input("Enter Game Name: ").strip() + " (Custom)"

        print("\nSelect Format: 1.League 2.Knockout 3.Swiss")
        f = get_valid_int("Choice: ", 1, 3)
        fmt = "League" if f == 1 else "Knockout" if f == 2 else "Swiss"

        t = Tournament(name, sport, fmt)
        self.tournaments[t.id] = t

        print(f"\n--- REGISTER PARTICIPANTS ---")
        c = 1
        existing_names = {p.name.lower() for p in t.participants.values()}
        while True:
            n = input(f"Participant {c} Name: ").strip()
            if n.lower() == 'done':
                if len(t.participants) < 2: print("Need 2+ participants to start."); continue
                break
            if not n: continue
            if n.lower() in existing_names:
                print("❌ Name already exists in this tournament. Please use a unique name."); continue

            r = 1000
            if "Chess" in sport:
                r = get_valid_int("Rating (1000): ", 0) or 1000

            p = Participant(n, r)
            p.roster = self._get_roster_input(sport, n)

            t.participants[p.id] = p
            existing_names.add(n.lower())
            c += 1

        DataManager.save(self.tournaments)
        print("✅ Tournament created and saved!")

    def display_leaderboard(self, t):
        print(f"\n📊 LEADERBOARD: {t.name}")
        sorted_p = sorted(t.participants.values(), key=lambda x: (x.score, x.performance_ratio, x.rating), reverse=True)

        cat = self._get_game_category(t.sport_name)
        label = "Rating" if cat == "STRATEGY" else "Tm K/D" if cat == "SHOOTER" else "Goals"

        print("+" + "-"*60 + "+")
        print(f"| {'#':<3} | {'Name':<25} | {'Pts':<5} | {label:<6} | {'Sts':<3} |")
        print("+" + "-"*60 + "+")
        for i, p in enumerate(sorted_p, 1):
            nm = f"👑 {p.name}" if i == 1 and t.is_finished else p.name
            st = "IN" if p.active else "OUT"

            if cat == "STRATEGY": val = p.rating
            elif cat == "SHOOTER": val = p.performance_ratio
            else: val = p.stat_primary # Display total goals/primary stat

            val_str = f"{val:.2f}" if isinstance(val, float) else str(val)

            print(f"| {i:<3} | {nm:<25} | {p.score:<5.1f} | {val_str:<6} | {st:<3} |")
        print("+" + "-"*60 + "+")

    def manage_tournament(self):
        t = self._select_tournament()
        if not t: return

        cat = self._get_game_category(t.sport_name)

        while True:
            if t.is_finished: print(f"\n--- {t.name} (🏆 FINISHED) ---")
            else: print(f"\n--- {t.name} [Round {t.round}] ---")

            print("1.Generate Matches  2.Enter Results  3.Leaderboard  4.Next Round  5.History  6.Back")
            act = input("> ")

            if act == '1':
                if t.is_finished: print("Tournament is finished."); continue
                curr = [m for m in t.matches if m.round == t.round]

                if curr and all(m.is_played for m in curr):
                    print("All matches for this round are played. Go to option 4 to start the next round.")
                    continue
                elif curr:
                    print(f"{len(curr)} matches for Round {t.round} already generated. Use option 2 to enter results.")
                    continue

                c = AlgorithmEngine.generate_fixtures(t)
                DataManager.save(self.tournaments)
                print(f"✅ {c} Matches Generated for Round {t.round}.")

            elif act == '2':
                if t.is_finished: print("Tournament is finished."); continue

                matches = [m for m in t.matches if not m.is_played and (m.round == t.round or t.format_type == "League")]

                if not matches:
                    print("No pending matches found. Generate matches (Option 1) first.")
                    continue

                for i, m in enumerate(matches):
                    p1 = t.participants[m.p1_id]
                    p2 = t.participants[m.p2_id] if m.p2_id else None
                    print(f"{i+1}. R{m.round}: {p1.name} vs {p2.name if p2 else 'BYE'}")

                idx = get_valid_int("Match # (0 cancel): ", 0, len(matches)) - 1
                if idx < 0: continue
                tgt = matches[idx]

                if not tgt.p2_id:
                    AlgorithmEngine.process_result(t, tgt.id, None, False, [], [])
                    print("✅ Bye recorded. Player receives win point.")
                else:
                    p1 = t.participants[tgt.p1_id]
                    p2 = t.participants[tgt.p2_id]

                    p1_stats_list, _, _ = self._collect_stats(p1, cat)
                    p2_stats_list, _, _ = self._collect_stats(p2, cat)

                    print(f"\nWho won? 1.{p1.name} 2.{p2.name} 3.Draw")
                    r = input("> ")
                    wid = p1.id if r == '1' else p2.id if r == '2' else None

                    if AlgorithmEngine.process_result(t, tgt.id, wid, r == '3', p1_stats_list, p2_stats_list):
                        mvp_msg = f" {t.matches[-1].match_mvp}" if t.matches[-1].match_mvp else ''
                        print(f"✅ Result saved.{mvp_msg}")
                    DataManager.save(self.tournaments)

            elif act == '3': self.display_leaderboard(t)
            elif act == '4':
                if t.is_finished: print("Tournament is already finished. See the leaderboard."); continue

                curr = [m for m in t.matches if m.round == t.round]

                if not curr or not all(m.is_played for m in curr):
                    print("❌ Finish all pending matches for the current round first (Option 2).")
                    continue
                else:
                    actv = len([p for p in t.participants.values() if p.active])
                    if t.format_type == "Knockout" and actv <= 1:
                        winner = next((p.name for p in t.participants.values() if p.active), "Unknown")
                        print(f"🏆 WINNER FOUND: {winner}!"); t.is_finished = True
                        t.history.append(f"🏆 Tournament Finished. Winner: {winner}.")
                    else:
                        t.round += 1; print("⏩ Next Round initiated. Generate fixtures (Option 1).")
                    DataManager.save(self.tournaments)

            elif act == '5':
                print("\n📜 MATCH HISTORY")
                for log in t.history: print(f" - {log}")
                if input("Export history to a file? (y/n): ").lower() == 'y':
                    try:
                        filename = f"{t.name.replace(' ', '_')}_history.txt"
                        with open(filename, "w") as f:
                            for log in t.history: f.write(log + "\n")
                        print(f"✅ Saved to {filename}")
                    except IOError:
                        print("❌ Error saving file.")

            elif act == '6': break

if __name__ == "__main__":
    app = ConsoleUI()
    app.run()
