"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ DATA MODELS MODULE                                                        ║
║ Developer: Arshpreet Singh (S25CSEU0980)                                  ║
║ Role: Data structures, JSON save/load, backup system, and MVP tracking    ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import json
import uuid
import os
from datetime import datetime
from config import DATA_FILE, DEFAULT_ELO


# ==============================================================================
# PARTICIPANT CLASS
# ==============================================================================

class Participant:
    """Stores player or team data"""
    
    def __init__(self, name, rating=DEFAULT_ELO, role="", team=""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.rating = rating
        self.role = role
        self.team = team
        self.active = True
        
        # Statistics
        self.matches_played = 0
        self.won = 0
        self.drawn = 0
        self.lost = 0
        self.points = 0.0
        self.score_for = 0
        self.score_against = 0
        
        # NEW: MVP and K/D tracking
        self.kills = 0
        self.deaths = 0
        self.mvp_count = 0
        
        # For Swiss format (avoid playing same person twice)
        self.opponent_history = []
    
    def add_opponent(self, opponent_id):
        """Remember who you played against"""
        if opponent_id not in self.opponent_history:
            self.opponent_history.append(opponent_id)
    
    def has_played(self, opponent_id):
        """Check if already played this person"""
        return opponent_id in self.opponent_history
    
    def get_score_diff(self):
        """Calculate goal difference"""
        return self.score_for - self.score_against
    
    def get_kd_ratio(self):
        """Calculate K/D ratio for shooters"""
        if self.deaths == 0:
            return self.kills if self.kills > 0 else 0.0
        return round(self.kills / self.deaths, 2)
    
    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            'id': self.id,
            'name': self.name,
            'rating': self.rating,
            'role': self.role,
            'team': self.team,
            'active': self.active,
            'matches_played': self.matches_played,
            'won': self.won,
            'drawn': self.drawn,
            'lost': self.lost,
            'points': self.points,
            'score_for': self.score_for,
            'score_against': self.score_against,
            'kills': self.kills,
            'deaths': self.deaths,
            'mvp_count': self.mvp_count,
            'opponent_history': self.opponent_history
        }


# ==============================================================================
# MATCH CLASS
# ==============================================================================

class Match:
    """Stores single match data"""
    
    def __init__(self, player1_id, player2_id, round_num):
        self.id = str(uuid.uuid4())
        self.player1_id = player1_id
        self.player2_id = player2_id  # None = BYE match
        self.round = round_num
        self.played = False
        self.score1 = 0
        self.score2 = 0
        
        # NEW: MVP tracking
        self.mvp_id = None
        self.mvp_name = ""
    
    def is_bye(self):
        """Check if this is a BYE match"""
        return self.player2_id is None
    
    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            'id': self.id,
            'player1_id': self.player1_id,
            'player2_id': self.player2_id,
            'round': self.round,
            'played': self.played,
            'score1': self.score1,
            'score2': self.score2,
            'mvp_id': self.mvp_id,
            'mvp_name': self.mvp_name
        }


# ==============================================================================
# TOURNAMENT CLASS
# ==============================================================================

class Tournament:
    """Main tournament container"""
    
    def __init__(self, name, game, format_type):
        self.id = str(uuid.uuid4())
        self.name = name
        self.game = game
        self.format = format_type
        self.current_round = 1
        self.finished = False
        self.created = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        self.participants = {}  # ID -> Participant object
        self.matches = []       # List of Match objects
    
    def add_participant(self, participant):
        """Add player/team to tournament"""
        self.participants[participant.id] = participant
    
    def get_active_participants(self):
        """Get all active players sorted by points"""
        active = [p for p in self.participants.values() if p.active]
        return sorted(active, key=lambda x: (x.points, x.get_score_diff(), x.rating), reverse=True)
    
    def get_current_matches(self):
        """Get matches for current round"""
        return [m for m in self.matches if m.round == self.current_round]
    
    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            'id': self.id,
            'name': self.name,
            'game': self.game,
            'format': self.format,
            'current_round': self.current_round,
            'finished': self.finished,
            'created': self.created,
            'participants': {pid: p.to_dict() for pid, p in self.participants.items()},
            'matches': [m.to_dict() for m in self.matches]
        }


# ==============================================================================
# DATA STORAGE
# ==============================================================================

class DataStore:
    """Handles saving and loading tournaments"""
    
    @staticmethod
    def save(tournaments):
        """Save all tournaments to JSON file"""
        data = [t.to_dict() for t in tournaments.values()]
        
        try:
            # Create backup first
            if os.path.exists(DATA_FILE):
                backup_name = DATA_FILE.replace('.json', '_backup.json')
                os.replace(DATA_FILE, backup_name)
            
            # Save new data
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    @staticmethod
    def load():
        """Load tournaments from JSON file"""
        if not os.path.exists(DATA_FILE):
            return {}
        
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            
            tournaments = {}
            
            for item in data:
                # Recreate tournament
                t = Tournament(item['name'], item['game'], item['format'])
                t.id = item['id']
                t.current_round = item.get('current_round', 1)
                t.finished = item.get('finished', False)
                t.created = item.get('created', '')
                
                # Recreate participants
                for pid, pdata in item.get('participants', {}).items():
                    p = Participant(
                        pdata['name'],
                        pdata.get('rating', DEFAULT_ELO),
                        pdata.get('role', ''),
                        pdata.get('team', '')
                    )
                    p.id = pdata['id']
                    p.active = pdata.get('active', True)
                    p.matches_played = pdata.get('matches_played', 0)
                    p.won = pdata.get('won', 0)
                    p.drawn = pdata.get('drawn', 0)
                    p.lost = pdata.get('lost', 0)
                    p.points = pdata.get('points', 0.0)
                    p.score_for = pdata.get('score_for', 0)
                    p.score_against = pdata.get('score_against', 0)
                    p.kills = pdata.get('kills', 0)
                    p.deaths = pdata.get('deaths', 0)
                    p.mvp_count = pdata.get('mvp_count', 0)
                    p.opponent_history = pdata.get('opponent_history', [])
                    t.participants[pid] = p
                
                # Recreate matches
                for mdata in item.get('matches', []):
                    m = Match(mdata['player1_id'], mdata.get('player2_id'), mdata['round'])
                    m.id = mdata['id']
                    m.played = mdata.get('played', False)
                    m.score1 = mdata.get('score1', 0)
                    m.score2 = mdata.get('score2', 0)
                    m.mvp_id = mdata.get('mvp_id')
                    m.mvp_name = mdata.get('mvp_name', '')
                    t.matches.append(m)
                
                tournaments[t.id] = t
            
            return tournaments
            
        except Exception as e:
            print(f"Load error: {e}")
            return {}
