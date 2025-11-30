"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ TOURNAMENT LOGIC & ALGORITHMS MODULE                                      ║
║ Developer: Krish Agarwal (S25CSEU0985)                                    ║
║ Contribution: Fixture Generation, Match Logic, Tournament Rules           ║
║ Role: Core tournament algorithms and business logic implementation        ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import random
from datetime import datetime
from data_models import Match
from config import GAME_CONFIGS


class TournamentEngine:
    """
    Core tournament engine with fixture generation algorithms
    Implements League, Swiss, and Knockout formats with proper seeding
    """
    
    @staticmethod
    def generate_fixtures(tournament):
        """
        Generate fixtures for current round based on tournament format
        Implements different pairing algorithms for each format
        """
        # Check if fixtures already exist for current round
        if tournament.get_current_matches():
            return False
        
        active = tournament.get_active_participants()
        if len(active) < 2:
            tournament.is_finished = True
            return False
        
        # Apply seeding if first round
        if tournament.current_round == 1 and not tournament.seeding_complete:
            tournament.apply_seeding()
        
        # Apply format-specific sorting and pairing
        if tournament.format_type == "League":
            active = TournamentEngine._round_robin_sort(active, tournament.current_round)
        elif tournament.format_type == "Swiss":
            active = TournamentEngine._swiss_sort(active)
        elif tournament.format_type == "Knockout":
            active = TournamentEngine._knockout_sort(active)
        
        # Generate pairings
        TournamentEngine._create_pairings(tournament, active)
        
        return True
    
    @staticmethod
    def _round_robin_sort(participants, round_num):
        """
        Sort participants for round-robin using circle method
        Ensures every player plays every other player once
        """
        # Sort by rating initially for fair first-round pairings
        participants = sorted(participants, key=lambda x: x.rating, reverse=True)
        
        if round_num > 1:
            # Circle/rotation method for round-robin
            # Fix first player, rotate others
            fixed = participants[0:1]
            rotating = participants[1:]
            rotation_steps = (round_num - 1) % len(rotating) if rotating else 0
            rotating = rotating[rotation_steps:] + rotating[:rotation_steps]
            participants = fixed + rotating
        
        return participants
    
    @staticmethod
    def _swiss_sort(participants):
        """
        Sort participants for Swiss system
        Pairs players with similar points who haven't played each other
        """
        # Primary sort by points, secondary by goal difference, tertiary by rating
        return sorted(
            participants,
            key=lambda x: (x.points, x.score_diff, x.rating),
            reverse=True
        )
    
    @staticmethod
    def _knockout_sort(participants):
        """
        Sort participants for knockout tournament
        Uses seeding to create balanced bracket (1 vs lowest, 2 vs 2nd lowest, etc.)
        """
        # Ensure seeding is applied
        if not all(p.seed_number > 0 for p in participants):
            sorted_by_rating = sorted(participants, key=lambda x: x.rating, reverse=True)
            for i, p in enumerate(sorted_by_rating, 1):
                p.seed_number = i
        
        # Sort by seed number
        return sorted(participants, key=lambda x: x.seed_number)
    
    @staticmethod
    def _create_pairings(tournament, participants):
        """
        Create match pairings from sorted participant list
        Handles BYE matches for odd number of participants
        Special logic for Swiss to avoid rematches
        """
        pool = participants.copy()
        
        # Swiss format needs special pairing to avoid rematches
        if tournament.format_type == "Swiss":
            TournamentEngine._create_swiss_pairings(tournament, pool)
        else:
            # Standard adjacent pairing
            while len(pool) > 1:
                p1 = pool.pop(0)
                p2 = pool.pop(0)
                match = Match(p1.id, p2.id, tournament.current_round)
                tournament.matches.append(match)
                # Track opponents for future reference
                p1.add_opponent(p2.id)
                p2.add_opponent(p1.id)
            
            # Handle BYE for odd number
            if pool:
                TournamentEngine._handle_bye_match(tournament, pool[0])
    
    @staticmethod
    def _create_swiss_pairings(tournament, participants):
        """
        Create Swiss pairings avoiding rematches
        Uses opponent history to prevent repeated matchups
        """
        unpaired = participants.copy()
        
        while len(unpaired) > 1:
            p1 = unpaired.pop(0)
            opponent = None
            
            # Find first valid opponent who hasn't been played before
            for i, candidate in enumerate(unpaired):
                if not p1.has_played_against(candidate.id):
                    opponent = unpaired.pop(i)
                    break
            
            # If no valid opponent found (all rematches), pair anyway
            if not opponent and unpaired:
                opponent = unpaired.pop(0)
            
            if opponent:
                match = Match(p1.id, opponent.id, tournament.current_round)
                tournament.matches.append(match)
                p1.add_opponent(opponent.id)
                opponent.add_opponent(p1.id)
        
        # Handle BYE
        if unpaired:
            TournamentEngine._handle_bye_match(tournament, unpaired[0])
    
    @staticmethod
    def _handle_bye_match(tournament, participant):
        """
        Handle BYE match - create match and auto-record win
        """
        bye_match = Match(participant.id, None, tournament.current_round)
        tournament.matches.append(bye_match)
        # Auto-record BYE win
        TournamentEngine.record_result(tournament, bye_match.id, 1, 0)
    
    @staticmethod
    def record_result(tournament, match_id, score1, score2):
        """
        Record match result and update participant statistics
        Implements knockout elimination and draw validation
        """
        match = next((m for m in tournament.matches if m.id == match_id), None)
        if not match or match.is_played:
            return False
        
        # Validate scores
        if score1 < 0 or score2 < 0:
            return False
        
        # Check if draw is allowed for this game in knockout
        game_config = GAME_CONFIGS.get(tournament.game_type, {})
        if tournament.format_type == "Knockout" and score1 == score2:
            # Knockout NEVER allows draws - one must win
            return False
        
        # Check if draw is allowed in other formats
        if score1 == score2 and not game_config.get('allows_draw', True):
            return False
        
        # Update match
        match.p1_score = score1
        match.p2_score = score2
        match.is_played = True
        match.match_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get participants
        p1 = tournament.participants[match.p1_id]
        
        # Handle BYE match
        if match.is_bye():
            p1.matches_played += 1
            p1.won += 1
            p1.points += 1.0
            return True
        
        p2 = tournament.participants[match.p2_id]
        
        # Update statistics for both players
        p1.matches_played += 1
        p2.matches_played += 1
        p1.score_for += score1
        p1.score_against += score2
        p2.score_for += score2
        p2.score_against += score1
        
        # Determine winner and apply format-specific rules
        if score1 > score2:
            # Player 1 wins
            p1.won += 1
            p2.lost += 1
            p1.points += 1.0
            
            # Knockout: eliminate loser
            if tournament.format_type == "Knockout":
                p2.active = False
        
        elif score2 > score1:
            # Player 2 wins
            p2.won += 1
            p1.lost += 1
            p2.points += 1.0
            
            # Knockout: eliminate loser
            if tournament.format_type == "Knockout":
                p1.active = False
        
        else:
            # Draw (only in League/Swiss and if game allows)
            p1.drawn += 1
            p2.drawn += 1
            p1.points += 0.5
            p2.points += 0.5
        
        return True
    
    @staticmethod
    def record_result_quick(tournament, match_id, winner_choice):
        """
        Quick result recording with button choice
        winner_choice: 'p1' or 'p2' or 'draw'
        """
        match = next((m for m in tournament.matches if m.id == match_id), None)
        if not match or match.is_played:
            return False
        
        # Validate draw option
        game_config = GAME_CONFIGS.get(tournament.game_type, {})
        if winner_choice == 'draw':
            if tournament.format_type == "Knockout":
                return False  # No draws in knockout
            if not game_config.get('allows_draw', True):
                return False  # Game doesn't allow draws
        
        # Set scores based on choice
        if winner_choice == 'p1':
            score1, score2 = 1, 0
        elif winner_choice == 'p2':
            score1, score2 = 0, 1
        elif winner_choice == 'draw':
            score1, score2 = 1, 1
        else:
            return False
        
        return TournamentEngine.record_result(tournament, match_id, score1, score2)
    
    @staticmethod
    def undo_last_match(tournament):
        """
        Undo the last played match
        Reverts all statistics and reactivates eliminated players
        """
        played = tournament.get_completed_matches()
        if not played:
            return False
        
        # Get last match
        last_match = played[-1]
        p1 = tournament.participants[last_match.p1_id]
        
        # Handle BYE undo
        if last_match.is_bye():
            p1.matches_played -= 1
            p1.won -= 1
            p1.points -= 1.0
            last_match.is_played = False
            last_match.match_date = None
            return True
        
        p2 = tournament.participants[last_match.p2_id]
        
        # Revert statistics
        p1.matches_played -= 1
        p2.matches_played -= 1
        p1.score_for -= last_match.p1_score
        p1.score_against -= last_match.p2_score
        p2.score_for -= last_match.p2_score
        p2.score_against -= last_match.p1_score
        
        # Revert results and reactivate eliminated players
        if last_match.p1_score > last_match.p2_score:
            p1.won -= 1
            p2.lost -= 1
            p1.points -= 1.0
            if tournament.format_type == "Knockout":
                p2.active = True  # Reactivate eliminated player
        
        elif last_match.p2_score > last_match.p1_score:
            p2.won -= 1
            p1.lost -= 1
            p2.points -= 1.0
            if tournament.format_type == "Knockout":
                p1.active = True  # Reactivate eliminated player
        
        else:
            # Draw
            p1.drawn -= 1
            p2.drawn -= 1
            p1.points -= 0.5
            p2.points -= 0.5
        
        # Clear match
        last_match.is_played = False
        last_match.p1_score = 0
        last_match.p2_score = 0
        last_match.match_date = None
        
        return True
    
    @staticmethod
    def validate_roles(teams, role_constraints):
        """
        Validate team role constraints
        Ensures teams have required roles (e.g., 1 Captain, 1 Goalkeeper)
        """
        errors = []
        for team_name, role_counts in teams.items():
            for role_req, count_req in role_constraints.items():
                actual = role_counts.get(role_req, 0)
                if actual != count_req:
                    errors.append(
                        f"Team '{team_name}' must have exactly {count_req} "
                        f"{role_req}(s). Found {actual}."
                    )
        return errors
    
    @staticmethod
    def is_round_complete(tournament):
        """Check if all matches in current round are completed"""
        current_matches = tournament.get_current_matches()
        if not current_matches:
            return False
        return all(m.is_played for m in current_matches)
    
    @staticmethod
    def advance_round(tournament):
        """Advance tournament to next round if current round is complete"""
        if not TournamentEngine.is_round_complete(tournament):
            return False
        
        # Check if tournament should end
        active_count = len(tournament.get_active_participants())
        
        if tournament.format_type == "Knockout" and active_count == 1:
            # Knockout ends when only 1 player remains
            tournament.mark_finished()
            return True
        
        tournament.current_round += 1
        return True
    
    @staticmethod
    def finish_tournament(tournament):
        """Mark tournament as finished and record winner"""
        tournament.mark_finished()
        return True
    
    @staticmethod
    def can_finish_tournament(tournament):
        """Check if tournament can be finished (all matches played)"""
        if tournament.is_finished:
            return False
        
        # For knockout, check if only 1 active player
        if tournament.format_type == "Knockout":
            return len(tournament.get_active_participants()) == 1
        
        # For other formats, check if all matches are complete
        return TournamentEngine.is_round_complete(tournament)
    
    @staticmethod
    def calculate_total_rounds(num_participants, format_type):
        """Calculate total rounds needed for tournament completion"""
        import math
        
        if format_type == "Knockout":
            # Knockout needs log2(n) rounds
            return math.ceil(math.log2(num_participants))
        elif format_type == "League":
            # Round-robin: everyone plays everyone
            return num_participants - 1 if num_participants % 2 == 0 else num_participants
        elif format_type == "Swiss":
            # Swiss: typically log2(n) + 1 rounds
            return math.ceil(math.log2(num_participants)) + 1
        return 1
    
    @staticmethod
    def get_match_participants(tournament, match):
        """Get participant objects for a match"""
        p1 = tournament.participants.get(match.p1_id)
        p2 = tournament.participants.get(match.p2_id) if match.p2_id else None
        return p1, p2
    
    @staticmethod
    def get_remaining_matches_count(tournament):
        """Get count of remaining matches to be played"""
        return len(tournament.get_pending_matches())
    
    @staticmethod
    def is_elimination_match(tournament, match):
        """Check if this is an elimination match (knockout)"""
        return tournament.format_type == "Knockout" and match.p2_id is not None
    
    @staticmethod
    def predict_next_round_count(tournament):
        """Predict number of matches in next round"""
        if tournament.format_type == "Knockout":
            active = len(tournament.get_active_participants())
            return active // 2
        return len(tournament.participants) // 2
    
    @staticmethod
    def get_tournament_progress(tournament):
        """Get tournament progress percentage"""
        total_matches = len(tournament.matches)
        if total_matches == 0:
            return 0.0
        completed = len(tournament.get_completed_matches())
        return round((completed / total_matches) * 100, 1)
