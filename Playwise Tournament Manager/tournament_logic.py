"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ TOURNAMENT LOGIC MODULE                                                   ║
║ Developer: Krish Agarwal (S25CSEU0985)                                    ║
║ Role: Fixture generation, match recording, MVP calculation, algorithms    ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import random
from data_models import Match
from config import GAME_CONFIGS


# ==============================================================================
# TOURNAMENT ENGINE
# ==============================================================================

class TournamentEngine:
    """Handles all tournament logic"""
    
    @staticmethod
    def generate_fixtures(tournament):
        """Generate matches for current round"""
        
        # Check if fixtures already exist
        if tournament.get_current_matches():
            return False
        
        # Get active players
        active = tournament.get_active_participants()
        
        if len(active) < 2:
            tournament.finished = True
            return False
        
        # Sort based on format
        if tournament.format == "League":
            # Round-robin: rotate players
            random.shuffle(active)
        
        elif tournament.format == "Swiss":
            # Swiss: pair by points (already sorted)
            pass
        
        elif tournament.format == "Knockout":
            # Knockout: seed by rating
            active.sort(key=lambda x: x.rating, reverse=True)
        
        # Create pairs
        TournamentEngine._create_pairs(tournament, active)
        
        return True
    
    @staticmethod
    def _create_pairs(tournament, players):
        """Create match pairings from player list"""
        
        pool = players.copy()
        
        # Swiss format: avoid rematches
        if tournament.format == "Swiss":
            while len(pool) > 1:
                p1 = pool.pop(0)
                opponent = None
                
                # Find someone p1 hasn't played yet
                for i, candidate in enumerate(pool):
                    if not p1.has_played(candidate.id):
                        opponent = pool.pop(i)
                        break
                
                # If everyone already played, just pair anyway
                if not opponent and pool:
                    opponent = pool.pop(0)
                
                if opponent:
                    match = Match(p1.id, opponent.id, tournament.current_round)
                    tournament.matches.append(match)
                    p1.add_opponent(opponent.id)
                    opponent.add_opponent(p1.id)
        
        else:
            # Standard pairing: pair adjacent players
            while len(pool) > 1:
                p1 = pool.pop(0)
                p2 = pool.pop(0)
                match = Match(p1.id, p2.id, tournament.current_round)
                tournament.matches.append(match)
        
        # Handle BYE (odd player)
        if pool:
            bye_match = Match(pool[0].id, None, tournament.current_round)
            tournament.matches.append(bye_match)
            # Auto-record BYE win
            TournamentEngine.record_result(tournament, bye_match.id, 1, 0)
    
    @staticmethod
    def record_result(tournament, match_id, score1, score2):
        """Record match result and calculate MVP"""
        
        # Find match
        match = None
        for m in tournament.matches:
            if m.id == match_id:
                match = m
                break
        
        if not match or match.played:
            return False
        
        # Validate scores
        if score1 < 0 or score2 < 0:
            return False
        
        # Check draw rules
        game_config = GAME_CONFIGS[tournament.game]
        
        if score1 == score2:
            # Knockout NEVER allows draws
            if tournament.format == "Knockout":
                return False
            # Check if game allows draws
            if not game_config.get('allows_draw', True):
                return False
        
        # Update match
        match.score1 = score1
        match.score2 = score2
        match.played = True
        
        # Get participants
        p1 = tournament.participants[match.player1_id]
        
        # Handle BYE
        if match.is_bye():
            p1.matches_played += 1
            p1.won += 1
            p1.points += 1.0
            return True
        
        p2 = tournament.participants[match.player2_id]
        
        # NEW: Update K/D for shooters (Valorant, CS2, PUBG Mobile)
        shooter_games = ["Valorant", "Counter-Strike 2", "PUBG Mobile"]
        if tournament.game in shooter_games:
            p1.kills += score1
            p1.deaths += score2
            p2.kills += score2
            p2.deaths += score1
        
        # Update statistics
        p1.matches_played += 1
        p2.matches_played += 1
        p1.score_for += score1
        p1.score_against += score2
        p2.score_for += score2
        p2.score_against += score1
        
        # NEW: Calculate and assign MVP (highest score wins)
        if score1 > score2:
            match.mvp_id = p1.id
            match.mvp_name = p1.name
            p1.mvp_count += 1
        elif score2 > score1:
            match.mvp_id = p2.id
            match.mvp_name = p2.name
            p2.mvp_count += 1
        # If draw, no MVP
        
        # Determine winner
        if score1 > score2:
            # Player 1 wins
            p1.won += 1
            p2.lost += 1
            p1.points += 1.0
            if tournament.format == "Knockout":
                p2.active = False  # Eliminate loser
        
        elif score2 > score1:
            # Player 2 wins
            p2.won += 1
            p1.lost += 1
            p2.points += 1.0
            if tournament.format == "Knockout":
                p1.active = False  # Eliminate loser
        
        else:
            # Draw
            p1.drawn += 1
            p2.drawn += 1
            p1.points += 0.5
            p2.points += 0.5
        
        return True
    
    @staticmethod
    def advance_round(tournament):
        """Move to next round"""
        
        # Check all matches are done
        current = tournament.get_current_matches()
        if not all(m.played for m in current):
            return False
        
        # Check if tournament should end
        if tournament.format == "Knockout":
            active = tournament.get_active_participants()
            if len(active) == 1:
                tournament.finished = True
                return True
        
        tournament.current_round += 1
        return True
    
    @staticmethod
    def validate_roles(participants, game_config):
        """Check if team roles are correct"""
        
        constraints = game_config.get('role_constraints', {})
        if not constraints:
            return []  # No rules to check
        
        # Group by team
        teams = {}
        for p in participants:
            if p.team:
                if p.team not in teams:
                    teams[p.team] = {}
                role = p.role
                teams[p.team][role] = teams[p.team].get(role, 0) + 1
        
        # Check each team
        errors = []
        for team_name, role_counts in teams.items():
            for required_role, required_count in constraints.items():
                actual = role_counts.get(required_role, 0)
                if actual != required_count:
                    errors.append(f"Team '{team_name}' needs exactly {required_count} {required_role}(s), found {actual}")
        
        return errors
