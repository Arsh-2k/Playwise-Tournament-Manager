"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ ANALYTICS MODULE                                                          ║
║ Developer: Adityan (S25CSEU0977)                                          ║
║ Role: Leaderboard, statistics, MVP tracking, K/D stats, and CSV export    ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import csv
from datetime import datetime
from config import MEDALS, GAME_CONFIGS


# ==============================================================================
# LEADERBOARD SYSTEM
# ==============================================================================

class LeaderboardSystem:
    """Creates rankings and standings"""
    
    @staticmethod
    def get_leaderboard(tournament):
        """Get sorted standings with ranks"""
        
        # Get all participants sorted by points
        participants = tournament.get_active_participants()
        
        leaderboard = []
        for rank, p in enumerate(participants, 1):
            entry = {
                'rank': rank,
                'medal': MEDALS.get(rank, ''),
                'name': p.name,
                'team': p.team,
                'role': p.role,
                'played': p.matches_played,
                'won': p.won,
                'drawn': p.drawn,
                'lost': p.lost,
                'points': p.points,
                'gf': p.score_for,
                'ga': p.score_against,
                'gd': p.get_score_diff(),
                'rating': p.rating,
                'active': p.active,
                'kills': p.kills,
                'deaths': p.deaths,
                'kd': p.get_kd_ratio(),
                'mvp_count': p.mvp_count
            }
            leaderboard.append(entry)
        
        return leaderboard
    
    @staticmethod
    def get_winner(tournament):
        """Get tournament winner"""
        if not tournament.finished:
            return None
        
        standings = tournament.get_active_participants()
        return standings[0] if standings else None
    
    @staticmethod
    def get_top_three(tournament):
        """Get podium finishers"""
        standings = tournament.get_active_participants()
        return standings[:3]
    
    @staticmethod
    def get_mvp_leaderboard(tournament):
        """Get players ranked by MVP count"""
        all_players = list(tournament.participants.values())
        sorted_by_mvp = sorted(all_players, key=lambda x: x.mvp_count, reverse=True)
        
        mvp_board = []
        for rank, p in enumerate(sorted_by_mvp[:10], 1):
            if p.mvp_count > 0:  # Only show players with at least 1 MVP
                mvp_board.append({
                    'rank': rank,
                    'name': p.name,
                    'team': p.team,
                    'mvp_count': p.mvp_count,
                    'matches': p.matches_played
                })
        
        return mvp_board
    
    @staticmethod
    def get_kd_leaderboard(tournament):
        """Get players ranked by K/D ratio (for shooters)"""
        all_players = [p for p in tournament.participants.values() if p.kills > 0]
        sorted_by_kd = sorted(all_players, key=lambda x: x.get_kd_ratio(), reverse=True)
        
        kd_board = []
        for rank, p in enumerate(sorted_by_kd[:10], 1):
            kd_board.append({
                'rank': rank,
                'name': p.name,
                'team': p.team,
                'kills': p.kills,
                'deaths': p.deaths,
                'kd': p.get_kd_ratio()
            })
        
        return kd_board


# ==============================================================================
# STATISTICS ENGINE
# ==============================================================================

class AnalyticsEngine:
    """Calculates tournament statistics"""
    
    @staticmethod
    def get_stats(tournament):
        """Get tournament overview statistics"""
        
        total_participants = len(tournament.participants)
        active = len([p for p in tournament.participants.values() if p.active])
        total_matches = len(tournament.matches)
        completed = len([m for m in tournament.matches if m.played])
        
        # Calculate total goals
        total_goals = 0
        for match in tournament.matches:
            if match.played:
                total_goals += match.score1 + match.score2
        
        avg_goals = round(total_goals / completed, 2) if completed > 0 else 0
        
        # NEW: Count total MVPs awarded
        mvp_matches = len([m for m in tournament.matches if m.played and m.mvp_id])
        
        # NEW: Get tournament MVP (most MVP awards)
        all_players = list(tournament.participants.values())
        tournament_mvp = max(all_players, key=lambda x: x.mvp_count) if all_players else None
        
        return {
            'name': tournament.name,
            'game': tournament.game,
            'format': tournament.format,
            'status': 'Finished' if tournament.finished else 'Active',
            'round': tournament.current_round,
            'total_participants': total_participants,
            'active_participants': active,
            'total_matches': total_matches,
            'completed_matches': completed,
            'pending_matches': total_matches - completed,
            'total_goals': total_goals,
            'avg_goals': avg_goals,
            'mvp_matches': mvp_matches,
            'tournament_mvp': tournament_mvp.name if tournament_mvp and tournament_mvp.mvp_count > 0 else 'TBD'
        }
    
    @staticmethod
    def get_top_scorers(tournament, limit=5):
        """Get highest scoring players"""
        
        all_players = list(tournament.participants.values())
        sorted_players = sorted(all_players, key=lambda x: x.score_for, reverse=True)
        
        top_scorers = []
        for i, p in enumerate(sorted_players[:limit], 1):
            top_scorers.append({
                'rank': i,
                'name': p.name,
                'goals': p.score_for,
                'mvps': p.mvp_count
            })
        
        return top_scorers
    
    @staticmethod
    def is_shooter_game(game_name):
        """Check if game is a shooter (for K/D display)"""
        shooters = ["Valorant", "Counter-Strike 2", "PUBG Mobile"]
        return game_name in shooters
    
    @staticmethod
    def export_csv(tournament, filepath):
        """Export standings to CSV file with MVP and K/D stats"""
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow(['PLAYWISE TOURNAMENT REPORT'])
                writer.writerow(['Tournament', tournament.name])
                writer.writerow(['Game', tournament.game])
                writer.writerow(['Format', tournament.format])
                writer.writerow(['Date', datetime.now().strftime("%Y-%m-%d %H:%M")])
                writer.writerow([])
                
                # Get stats
                stats = AnalyticsEngine.get_stats(tournament)
                writer.writerow(['Tournament MVP', stats['tournament_mvp']])
                writer.writerow([])
                
                # Standings header
                game_config = GAME_CONFIGS[tournament.game]
                is_shooter = AnalyticsEngine.is_shooter_game(tournament.game)
                
                headers = ['Rank', 'Name', 'Played', 'Won', 'Drawn', 'Lost', 'Points', 'GF', 'GA', 'GD', 'MVPs']
                
                # Add K/D for shooters
                if is_shooter:
                    headers.extend(['Kills', 'Deaths', 'K/D'])
                
                # Add Elo for Chess
                if game_config.get('has_elo'):
                    headers.append('Elo')
                
                # Add Team/Role for team games
                if game_config.get('has_roles'):
                    headers.insert(2, 'Team')
                    headers.insert(3, 'Role')
                
                writer.writerow(headers)
                
                # Standings data
                leaderboard = LeaderboardSystem.get_leaderboard(tournament)
                for entry in leaderboard:
                    row = [
                        entry['rank'],
                        entry['name'],
                        entry['played'],
                        entry['won'],
                        entry['drawn'],
                        entry['lost'],
                        entry['points'],
                        entry['gf'],
                        entry['ga'],
                        entry['gd'],
                        entry['mvp_count']
                    ]
                    
                    # Add K/D for shooters
                    if is_shooter:
                        row.extend([entry['kills'], entry['deaths'], entry['kd']])
                    
                    # Add Elo for Chess
                    if game_config.get('has_elo'):
                        row.append(entry['rating'])
                    
                    # Add Team/Role for team games
                    if game_config.get('has_roles'):
                        row.insert(2, entry['team'])
                        row.insert(3, entry['role'])
                    
                    writer.writerow(row)
                
                # MVP Leaderboard section
                writer.writerow([])
                writer.writerow(['MVP LEADERBOARD'])
                writer.writerow(['Rank', 'Name', 'Team', 'MVP Awards', 'Matches'])
                
                mvp_board = LeaderboardSystem.get_mvp_leaderboard(tournament)
                for entry in mvp_board:
                    writer.writerow([entry['rank'], entry['name'], entry['team'], 
                                   entry['mvp_count'], entry['matches']])
                
                # K/D Leaderboard for shooters
                if is_shooter:
                    writer.writerow([])
                    writer.writerow(['K/D LEADERBOARD'])
                    writer.writerow(['Rank', 'Name', 'Team', 'Kills', 'Deaths', 'K/D'])
                    
                    kd_board = LeaderboardSystem.get_kd_leaderboard(tournament)
                    for entry in kd_board:
                        writer.writerow([entry['rank'], entry['name'], entry['team'], 
                                       entry['kills'], entry['deaths'], entry['kd']])
            
            return True
            
        except Exception as e:
            print(f"Export error: {e}")
            return False
