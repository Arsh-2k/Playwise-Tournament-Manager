"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ DATA MODELS & PERSISTENCE MODULE                                          ║
║ Developer: Arshpreet Singh (S25CSEU0980)                                  ║
║ Contribution: Data Structures, Seeding, BYE Handling, Report Generation   ║
║ Role: Database management, JSON persistence, and data integrity           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import json
import uuid
import os
from datetime import datetime
from config import DATA_FILE, DEFAULT_ELO, BACKUP_FILE


class Participant:
    """
    Represents a player or team in the tournament
    Handles individual participant data and statistics
    """
    
    def __init__(self, name, rating=DEFAULT_ELO, role="", team="", p_id=None, 
                 active=True, matches=0, won=0, drawn=0, lost=0, points=0.0, 
                 s_for=0, s_against=0):
        """Initialize participant with default statistics"""
        self.id = p_id if p_id else str(uuid.uuid4())
        self.name = name
        self.rating = int(rating) if str(rating).isdigit() else DEFAULT_ELO
        self.role = role
        self.team = team
        self.active = active
        
        # Match statistics
        self.matches_played = matches
        self.won = won
        self.drawn = drawn
        self.lost = lost
        self.points = points
        self.score_for = s_for
        self.score_against = s_against
        
        # Seeding information (for advanced tournaments)
        self.seed_number = 0
        self.opponent_history = []  # Track previous opponents for Swiss

    @property
    def score_diff(self):
        """Calculate goal/score difference"""
        return self.score_for - self.score_against
    
    @property
    def win_rate(self):
        """Calculate win percentage"""
        if self.matches_played == 0:
            return 0.0
        return round((self.won / self.matches_played) * 100, 1)
    
    @property
    def points_per_match(self):
        """Calculate average points per match"""
        if self.matches_played == 0:
            return 0.0
        return round(self.points / self.matches_played, 2)
    
    def add_opponent(self, opponent_id):
        """Track opponent for Swiss pairing (avoid rematches)"""
        if opponent_id and opponent_id not in self.opponent_history:
            self.opponent_history.append(opponent_id)
    
    def has_played_against(self, opponent_id):
        """Check if already played against opponent"""
        return opponent_id in self.opponent_history
    
    def reset_statistics(self):
        """Reset all statistics (useful for new tournament phase)"""
        self.matches_played = 0
        self.won = 0
        self.drawn = 0
        self.lost = 0
        self.points = 0.0
        self.score_for = 0
        self.score_against = 0
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
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
            'seed_number': self.seed_number,
            'opponent_history': self.opponent_history
        }


class Match:
    """
    Represents a match between two participants
    Handles BYE matches and match state
    """
    
    def __init__(self, p1_id, p2_id, round_num, m_id=None, is_played=False, 
                 p1_score=0, p2_score=0):
        """Initialize match with participants and round info"""
        self.id = m_id if m_id else str(uuid.uuid4())
        self.p1_id = p1_id
        self.p2_id = p2_id  # None indicates BYE match
        self.round = round_num
        self.is_played = is_played
        self.p1_score = p1_score
        self.p2_score = p2_score
        self.match_date = None
        self.is_bye_match = (p2_id is None)

    def is_bye(self):
        """Check if this is a BYE match"""
        return self.p2_id is None
    
    def get_winner_id(self):
        """Get winner's participant ID"""
        if not self.is_played:
            return None
        if self.is_bye():
            return self.p1_id  # BYE = automatic win
        if self.p1_score > self.p2_score:
            return self.p1_id
        elif self.p2_score > self.p1_score:
            return self.p2_id
        return None  # Draw
    
    def get_loser_id(self):
        """Get loser's participant ID"""
        if not self.is_played or self.is_bye():
            return None
        if self.p1_score < self.p2_score:
            return self.p1_id
        elif self.p2_score < self.p1_score:
            return self.p2_id
        return None  # Draw
    
    def is_draw(self):
        """Check if match ended in a draw"""
        return self.is_played and self.p1_score == self.p2_score and not self.is_bye()
    
    def get_score_display(self):
        """Get formatted score string"""
        if not self.is_played:
            return "Not Played"
        if self.is_bye():
            return "BYE (1-0)"
        return f"{self.p1_score}-{self.p2_score}"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'p1_id': self.p1_id,
            'p2_id': self.p2_id,
            'round': self.round,
            'is_played': self.is_played,
            'p1_score': self.p1_score,
            'p2_score': self.p2_score,
            'is_bye_match': self.is_bye_match,
            'match_date': self.match_date
        }


class Tournament:
    """
    Main tournament container
    Manages all tournament data and state
    """
    
    def __init__(self, name, game_type, format_type, t_id=None, current_round=1, 
                 is_finished=False, created_at=None):
        """Initialize tournament with basic information"""
        self.id = t_id if t_id else str(uuid.uuid4())
        self.name = name
        self.game_type = game_type
        self.format_type = format_type
        self.current_round = current_round
        self.is_finished = is_finished
        self.created_at = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.finished_at = None
        
        # Tournament data
        self.participants = {}  # Dict: ID -> Participant
        self.matches = []       # List of Match objects
        
        # Seeding configuration
        self.seeding_complete = False
        self.total_rounds = 0
        self.winner_id = None

    def get_active_participants(self):
        """Get active participants sorted by ranking (leaderboard order)"""
        return sorted(
            [p for p in self.participants.values() if p.active],
            key=lambda x: (x.points, x.score_diff, x.rating),
            reverse=True
        )
    
    def get_all_participants_sorted(self):
        """Get ALL participants (including eliminated) sorted by ranking"""
        return sorted(
            self.participants.values(),
            key=lambda x: (x.points, x.score_diff, x.rating),
            reverse=True
        )
    
    def get_eliminated_participants(self):
        """Get eliminated participants (for knockout tournaments)"""
        return [p for p in self.participants.values() if not p.active]
    
    def get_current_matches(self):
        """Get matches for current round"""
        return [m for m in self.matches if m.round == self.current_round]
    
    def get_matches_by_round(self, round_num):
        """Get matches for specific round"""
        return [m for m in self.matches if m.round == round_num]
    
    def get_all_rounds(self):
        """Get total number of rounds played"""
        return max([m.round for m in self.matches], default=0)
    
    def get_bye_matches(self):
        """Get all BYE matches in tournament"""
        return [m for m in self.matches if m.is_bye()]
    
    def get_completed_matches(self):
        """Get all completed matches"""
        return [m for m in self.matches if m.is_played]
    
    def get_pending_matches(self):
        """Get all pending matches"""
        return [m for m in self.matches if not m.is_played]
    
    def count_bye_matches(self):
        """Count total BYE matches"""
        return len(self.get_bye_matches())
    
    def apply_seeding(self):
        """
        Apply seeding to participants based on rating
        Higher rating = better seed (lower seed number)
        """
        participants = sorted(
            self.participants.values(),
            key=lambda x: x.rating,
            reverse=True
        )
        for i, p in enumerate(participants, 1):
            p.seed_number = i
        self.seeding_complete = True
    
    def get_winner(self):
        """Get tournament winner (top of leaderboard)"""
        if not self.is_finished:
            return None
        standings = self.get_all_participants_sorted()
        return standings[0] if standings else None
    
    def get_top_three(self):
        """Get top 3 finishers (for podium display)"""
        standings = self.get_all_participants_sorted()
        return standings[:3] if len(standings) >= 3 else standings
    
    def mark_finished(self):
        """Mark tournament as finished and record timestamp"""
        self.is_finished = True
        self.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        winner = self.get_winner()
        if winner:
            self.winner_id = winner.id
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'game_type': self.game_type,
            'format_type': self.format_type,
            'current_round': self.current_round,
            'is_finished': self.is_finished,
            'created_at': self.created_at,
            'finished_at': self.finished_at,
            'seeding_complete': self.seeding_complete,
            'total_rounds': self.total_rounds,
            'winner_id': self.winner_id,
            'participants': {pid: p.to_dict() for pid, p in self.participants.items()},
            'matches': [m.to_dict() for m in self.matches]
        }


class DataStore:
    """
    Handles JSON file operations for data persistence
    Manages save/load operations and backup creation
    """
    
    @staticmethod
    def save(tournaments, filepath=DATA_FILE):
        """
        Save all tournaments to JSON file
        Creates automatic backup before saving
        """
        # Create backup of existing file
        if os.path.exists(filepath):
            DataStore.create_backup(filepath)
        
        data = [t.to_dict() for t in tournaments.values()]
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False

    @staticmethod
    def load(filepath=DATA_FILE):
        """Load tournaments from JSON file"""
        if not os.path.exists(filepath):
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            tournaments = {}
            for item in raw_data:
                # Reconstruct tournament
                t = Tournament(
                    item['name'],
                    item['game_type'],
                    item['format_type'],
                    item['id'],
                    item.get('current_round', 1),
                    item.get('is_finished', False),
                    item.get('created_at')
                )
                
                t.finished_at = item.get('finished_at')
                t.seeding_complete = item.get('seeding_complete', False)
                t.total_rounds = item.get('total_rounds', 0)
                t.winner_id = item.get('winner_id')
                
                # Reconstruct participants
                for pid, p_data in item.get('participants', {}).items():
                    p = Participant(
                        p_data['name'],
                        p_data.get('rating', DEFAULT_ELO),
                        p_data.get('role', ''),
                        p_data.get('team', ''),
                        p_data['id'],
                        p_data.get('active', True),
                        p_data.get('matches_played', 0),
                        p_data.get('won', 0),
                        p_data.get('drawn', 0),
                        p_data.get('lost', 0),
                        p_data.get('points', 0.0),
                        p_data.get('score_for', 0),
                        p_data.get('score_against', 0)
                    )
                    p.seed_number = p_data.get('seed_number', 0)
                    p.opponent_history = p_data.get('opponent_history', [])
                    t.participants[pid] = p
                
                # Reconstruct matches
                for m_data in item.get('matches', []):
                    m = Match(
                        m_data['p1_id'],
                        m_data.get('p2_id'),
                        m_data['round'],
                        m_data['id'],
                        m_data.get('is_played', False),
                        m_data.get('p1_score', 0),
                        m_data.get('p2_score', 0)
                    )
                    m.match_date = m_data.get('match_date')
                    t.matches.append(m)
                
                tournaments[t.id] = t
            
            return tournaments
        except Exception as e:
            print(f"❌ Load error: {e}")
            return {}

    @staticmethod
    def create_backup(filepath):
        """Create timestamped backup of current data file"""
        try:
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = filepath.replace('.json', f'_backup_{timestamp}.json')
            shutil.copy2(filepath, backup_path)
            
            # Keep only last 5 backups
            DataStore.cleanup_old_backups(filepath)
            return True
        except Exception as e:
            print(f"⚠️  Backup error: {e}")
            return False
    
    @staticmethod
    def cleanup_old_backups(filepath, keep_count=5):
        """Keep only the most recent backup files"""
        try:
            import glob
            directory = os.path.dirname(filepath) or '.'
            filename = os.path.basename(filepath).replace('.json', '')
            pattern = os.path.join(directory, f"{filename}_backup_*.json")
            
            backups = sorted(glob.glob(pattern), reverse=True)
            
            # Delete old backups
            for old_backup in backups[keep_count:]:
                os.remove(old_backup)
                print(f"🗑️  Deleted old backup: {os.path.basename(old_backup)}")
        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")
    
    @staticmethod
    def restore_backup(backup_filepath, target_filepath=DATA_FILE):
        """Restore data from specific backup file"""
        try:
            import shutil
            shutil.copy2(backup_filepath, target_filepath)
            print(f"✅ Restored from backup: {os.path.basename(backup_filepath)}")
            return True
        except Exception as e:
            print(f"❌ Restore error: {e}")
            return False
    
    @staticmethod
    def export_tournament_json(tournament, filepath):
        """Export single tournament to separate JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tournament.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Export error: {e}")
            return False
