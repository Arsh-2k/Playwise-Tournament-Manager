"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ ANALYTICS & LEADERBOARD MODULE                                            ║
║ Developer: Adityan (S25CSEU0977)                                          ║
║ Contribution: Statistics, Leaderboard System, CSV Export, Visualizations  ║
║ Role: Data analysis, reporting, and tournament statistics generation      ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import csv
from datetime import datetime
from config import GAME_CONFIGS, RANK_MEDALS


class LeaderboardSystem:
    """
    Advanced leaderboard system with ranking and statistics
    Provides comprehensive tournament standings
    """
    
    @staticmethod
    def get_leaderboard(tournament):
        """
        Get complete leaderboard with rankings
        Returns sorted list of participants with rank information
        """
        participants = tournament.get_all_participants_sorted()
        
        leaderboard = []
        for rank, p in enumerate(participants, 1):
            entry = {
                'rank': rank,
                'medal': RANK_MEDALS.get(rank, ''),
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
                'gd': p.score_diff,
                'rating': p.rating,
                'win_rate': p.win_rate,
                'active': p.active,
                'id': p.id
            }
            leaderboard.append(entry)
        
        return leaderboard
    
    @staticmethod
    def get_top_n(tournament, n=3):
        """Get top N performers"""
        leaderboard = LeaderboardSystem.get_leaderboard(tournament)
        return leaderboard[:n]
    
    @staticmethod
    def get_player_rank(tournament, player_id):
        """Get specific player's rank"""
        leaderboard = LeaderboardSystem.get_leaderboard(tournament)
        for entry in leaderboard:
            if entry['id'] == player_id:
                return entry['rank']
        return None
    
    @staticmethod
    def get_form_guide(tournament, player_id, last_n=5):
        """
        Get recent form (last N matches)
        Returns string like "WWLWD" (Win/Draw/Loss)
        """
        participant = tournament.participants.get(player_id)
        if not participant:
            return ""
        
        # Get all matches involving this player
        player_matches = []
        for match in tournament.matches:
            if match.is_played and (match.p1_id == player_id or match.p2_id == player_id):
                player_matches.append(match)
        
        # Sort by round (most recent first)
        player_matches.sort(key=lambda x: x.round, reverse=True)
        player_matches = player_matches[:last_n]
        
        form = ""
        for match in reversed(player_matches):
            if match.is_bye():
                form += "W"
            elif match.p1_id == player_id:
                if match.p1_score > match.p2_score:
                    form += "W"
                elif match.p1_score < match.p2_score:
                    form += "L"
                else:
                    form += "D"
            else:
                if match.p2_score > match.p1_score:
                    form += "W"
                elif match.p2_score < match.p1_score:
                    form += "L"
                else:
                    form += "D"
        
        return form if form else "N/A"


class AnalyticsEngine:
    """
    Comprehensive analytics engine
    Provides detailed statistics and reporting
    """
    
    @staticmethod
    def get_tournament_stats(tournament):
        """Get comprehensive tournament statistics"""
        participants = list(tournament.participants.values())
        matches = tournament.matches
        
        completed_matches = [m for m in matches if m.is_played]
        total_goals = sum(m.p1_score + m.p2_score for m in completed_matches)
        
        # Calculate additional stats
        bye_count = len([m for m in matches if m.is_bye()])
        draw_count = len([m for m in completed_matches if m.is_draw()])
        
        return {
            'tournament_name': tournament.name,
            'game_type': tournament.game_type,
            'format': tournament.format_type,
            'status': 'Finished' if tournament.is_finished else 'Ongoing',
            'created_at': tournament.created_at,
            'finished_at': tournament.finished_at,
            'total_participants': len(participants),
            'active_participants': len([p for p in participants if p.active]),
            'eliminated': len([p for p in participants if not p.active]),
            'total_matches': len(matches),
            'completed_matches': len(completed_matches),
            'pending_matches': len([m for m in matches if not m.is_played]),
            'bye_matches': bye_count,
            'draws': draw_count,
            'total_goals': total_goals,
            'avg_goals_per_match': round(total_goals / len(completed_matches), 2) if completed_matches else 0,
            'current_round': tournament.current_round,
            'total_rounds': tournament.get_all_rounds(),
            'winner': tournament.get_winner().name if tournament.is_finished and tournament.get_winner() else 'TBD'
        }
    
    @staticmethod
    def get_player_stats(tournament, player_id):
        """Get detailed player statistics"""
        participant = tournament.participants.get(player_id)
        if not participant:
            return None
        
        rank = LeaderboardSystem.get_player_rank(tournament, player_id)
        form = LeaderboardSystem.get_form_guide(tournament, player_id)
        
        return {
            'name': participant.name,
            'team': participant.team,
            'role': participant.role,
            'rank': rank,
            'rating': participant.rating,
            'seed': participant.seed_number,
            'matches': participant.matches_played,
            'wins': participant.won,
            'draws': participant.drawn,
            'losses': participant.lost,
            'points': participant.points,
            'win_rate': participant.win_rate,
            'points_per_match': participant.points_per_match,
            'goals_for': participant.score_for,
            'goals_against': participant.score_against,
            'goal_diff': participant.score_diff,
            'active': participant.active,
            'form': form
        }
    
    @staticmethod
    def get_top_scorers(tournament, limit=5):
        """Get top scoring players/teams"""
        participants = list(tournament.participants.values())
        sorted_scorers = sorted(participants, key=lambda x: x.score_for, reverse=True)
        
        top_scorers = []
        for i, p in enumerate(sorted_scorers[:limit], 1):
            top_scorers.append({
                'rank': i,
                'name': p.name,
                'goals': p.score_for,
                'matches': p.matches_played
            })
        
        return top_scorers
    
    @staticmethod
    def get_best_defense(tournament, limit=5):
        """Get teams/players with best defense (least goals conceded)"""
        participants = [p for p in tournament.participants.values() if p.matches_played > 0]
        sorted_defense = sorted(participants, key=lambda x: x.score_against)
        
        best_defense = []
        for i, p in enumerate(sorted_defense[:limit], 1):
            best_defense.append({
                'rank': i,
                'name': p.name,
                'goals_against': p.score_against,
                'matches': p.matches_played
            })
        
        return best_defense
    
    @staticmethod
    def get_highest_win_rate(tournament, min_matches=3):
        """Get players with highest win rate (minimum matches played)"""
        participants = [p for p in tournament.participants.values() if p.matches_played >= min_matches]
        sorted_win_rate = sorted(participants, key=lambda x: x.win_rate, reverse=True)
        
        return [{
            'name': p.name,
            'win_rate': p.win_rate,
            'record': f"{p.won}W-{p.drawn}D-{p.lost}L"
        } for p in sorted_win_rate[:5]]
    
    @staticmethod
    def get_match_history(tournament, player_id):
        """Get complete match history for a player"""
        history = []
        for match in tournament.matches:
            if not match.is_played:
                continue
            
            if match.p1_id == player_id or match.p2_id == player_id:
                p1 = tournament.participants[match.p1_id]
                p2 = tournament.participants.get(match.p2_id) if match.p2_id else None
                
                if match.p1_id == player_id:
                    opponent = p2.name if p2 else "BYE"
                    my_score = match.p1_score
                    opp_score = match.p2_score
                    result = "W" if match.p1_score > match.p2_score else ("L" if match.p1_score < match.p2_score else "D")
                else:
                    opponent = p1.name
                    my_score = match.p2_score
                    opp_score = match.p1_score
                    result = "W" if match.p2_score > match.p1_score else ("L" if match.p2_score < match.p1_score else "D")
                
                history.append({
                    'round': match.round,
                    'opponent': opponent,
                    'result': result,
                    'score': f"{my_score}-{opp_score}"
                })
        
        return history
    
    @staticmethod
    def export_standings_csv(tournament, filepath):
        """Export tournament standings to CSV file"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write tournament info
                writer.writerow(['PLAYWISE TOURNAMENT REPORT'])
                writer.writerow(['Tournament', tournament.name])
                writer.writerow(['Game', tournament.game_type])
                writer.writerow(['Format', tournament.format_type])
                writer.writerow(['Date', datetime.now().strftime("%Y-%m-%d %H:%M")])
                writer.writerow([])
                
                # Write standings header
                game_config = GAME_CONFIGS.get(tournament.game_type, {})
                headers = ['Rank', 'Name', 'Team', 'Role', 'Played', 'Won', 'Drawn', 'Lost', 
                          'Points', 'GF', 'GA', 'GD']
                
                # Add Elo column only for Chess
                if game_config.get('has_elo'):
                    headers.append('Elo')
                
                writer.writerow(headers)
                
                # Write standings data
                leaderboard = LeaderboardSystem.get_leaderboard(tournament)
                for entry in leaderboard:
                    row = [
                        entry['rank'],
                        entry['name'],
                        entry['team'],
                        entry['role'],
                        entry['played'],
                        entry['won'],
                        entry['drawn'],
                        entry['lost'],
                        entry['points'],
                        entry['gf'],
                        entry['ga'],
                        entry['gd']
                    ]
                    
                    if game_config.get('has_elo'):
                        row.append(entry['rating'])
                    
                    writer.writerow(row)
            
            return True
        except Exception as e:
            print(f"❌ Export error: {e}")
            return False
    
    @staticmethod
    def export_matches_csv(tournament, filepath):
        """Export all matches to CSV file"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Headers
                writer.writerow(['Round', 'Player 1', 'Player 2', 'Score', 'Winner', 'Date', 'Status'])
                
                # Data
                for match in tournament.matches:
                    p1 = tournament.participants[match.p1_id]
                    p2 = tournament.participants[match.p2_id] if match.p2_id else None
                    
                    p1_name = p1.name
                    p2_name = p2.name if p2 else "BYE"
                    
                    if match.is_played:
                        score = match.get_score_display()
                        winner_id = match.get_winner_id()
                        winner = tournament.participants[winner_id].name if winner_id else "Draw"
                        status = "Completed"
                        date = match.match_date or "N/A"
                    else:
                        score = "Not Played"
                        winner = "TBD"
                        status = "Pending"
                        date = "N/A"
                    
                    writer.writerow([match.round, p1_name, p2_name, score, winner, date, status])
            
            return True
        except Exception as e:
            print(f"❌ Export error: {e}")
            return False
    
    @staticmethod
    def generate_text_report(tournament):
        """Generate comprehensive text report"""
        stats = AnalyticsEngine.get_tournament_stats(tournament)
        leaderboard = LeaderboardSystem.get_top_n(tournament, 10)
        
        report = []
        report.append("=" * 80)
        report.append(f" TOURNAMENT REPORT: {stats['tournament_name']}")
        report.append("=" * 80)
        report.append(f"Game: {stats['game_type']} | Format: {stats['format']}")
        report.append(f"Status: {stats['status']} | Round: {stats['current_round']}/{stats['total_rounds']}")
        report.append(f"Created: {stats['created_at']}")
        if stats['finished_at']:
            report.append(f"Finished: {stats['finished_at']}")
        report.append("")
        
        # Statistics
        report.append("TOURNAMENT STATISTICS:")
        report.append("-" * 80)
        report.append(f"Total Participants: {stats['total_participants']}")
        report.append(f"Active: {stats['active_participants']} | Eliminated: {stats['eliminated']}")
        report.append(f"Matches: {stats['completed_matches']}/{stats['total_matches']} completed")
        report.append(f"Total Goals: {stats['total_goals']} | Average: {stats['avg_goals_per_match']} per match")
        report.append(f"BYE Matches: {stats['bye_matches']} | Draws: {stats['draws']}")
        report.append("")
        
        # Leaderboard
        report.append("TOP 10 STANDINGS:")
        report.append("-" * 80)
        report.append(f"{'Rank':<6} {'Name':<25} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'Pts':<6} {'GD':<6}")
        report.append("-" * 80)
        
        for entry in leaderboard:
            report.append(
                f"{entry['rank']:<6} {entry['name']:<25} {entry['played']:<4} "
                f"{entry['won']:<4} {entry['drawn']:<4} {entry['lost']:<4} "
                f"{entry['points']:<6} {entry['gd']:<6}"
            )
        
        report.append("=" * 80)
        
        if stats['status'] == 'Finished':
            report.append(f"\n🏆 CHAMPION: {stats['winner']} 🏆\n")
            report.append("=" * 80)
        
        return "\n".join(report)
    
    @staticmethod
    def get_statistics_summary(tournament):
        """Get statistics summary for dashboard display"""
        stats = AnalyticsEngine.get_tournament_stats(tournament)
        
        return {
            'completion': f"{stats['completed_matches']}/{stats['total_matches']}",
            'progress': round((stats['completed_matches'] / stats['total_matches']) * 100, 1) if stats['total_matches'] > 0 else 0,
            'participants': f"{stats['active_participants']}/{stats['total_participants']}",
            'round': f"Round {stats['current_round']}",
            'avg_goals': stats['avg_goals_per_match'],
            'status': stats['status']
        }
