"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ MAIN APPLICATION CONTROLLER                                               ║
║ Developer: Shimon Pandey (S25CSEU0993) - Team Lead                        ║
║ Contribution: System Integration, PPT Presentation, Main Controller       ║
║ Role: Coordinates all modules and manages application lifecycle           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import sys
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Import all team modules
from data_models import Tournament, Participant, DataStore
from tournament_logic import TournamentEngine
from analytics import AnalyticsEngine, LeaderboardSystem
from ui_components import UIManager
from config import COLORS, DATA_FILE, GAME_CONFIGS, WINDOW_WIDTH, WINDOW_HEIGHT


class PlaywiseApplication:
    """
    Main Application Controller
    Integrates all team contributions into a cohesive system
    """
    
    def __init__(self):
        """Initialize the Playwise Tournament Manager"""
        self.version = "2.0"
        self.team_name = "DATA DRIFTERS"
        self.tournaments = {}
        self.current_tournament = None
        
        # Display startup banner
        self.show_startup_banner()
        
        # Load existing data
        self.load_application_data()
        
        # Initialize GUI
        self.initialize_gui()
    
    def show_startup_banner(self):
        """Display team information and startup banner"""
        print("=" * 80)
        print(r"""
    ____  __    ___  __  __ _       __  ____  _____    ______
   / __ \/ /   /   | \ \/ /| |     / / /  _/ / ___/   / ____/
  / /_/ / /   / /| |  \  / | | /| / /  / /   \__ \   / __/   
 / ____/ /___/ ___ |  / /  | |/ |/ / _/ /   ___/ /  / /___   
/_/   /_____/_/  |_| /_/   |__/|__/ /___/  /____/  /_____/   
        """)
        print("=" * 80)
        print(f" PLAYWISE TOURNAMENT MANAGER v{self.version}")
        print(f" TEAM: {self.team_name}")
        print("=" * 80)
        print(f"{'MEMBER':<30} {'STUDENT ID':<20} {'CONTRIBUTION'}")
        print("-" * 80)
        print(f"{'Shimon Pandey (Lead)':<30} {'S25CSEU0993':<20} {'System Integration & PPT'}")
        print(f"{'Arshpreet Singh':<30} {'S25CSEU0980':<20} {'Data Models & Report'}")
        print(f"{'Krish Agarwal':<30} {'S25CSEU0985':<20} {'Tournament Logic'}")
        print(f"{'Adityan':<30} {'S25CSEU0977':<20} {'Analytics & Leaderboard'}")
        print(f"{'Deepak Bisht':<30} {'S25CSEU0986':<20} {'UI Components'}")
        print("-" * 80)
        print(f"\n🐍 Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ All modules loaded successfully!")
        print("=" * 80)
        print("\n[Press Enter to start application...]")
        input()
    
    def load_application_data(self):
        """Load tournament data from JSON file"""
        print("\n📂 Loading tournament data...")
        try:
            self.tournaments = DataStore.load(DATA_FILE)
            print(f"✅ Loaded {len(self.tournaments)} tournament(s)")
        except Exception as e:
            print(f"⚠️  No previous data found or error: {e}")
            self.tournaments = {}
    
    def save_application_data(self):
        """Save tournament data to JSON file"""
        try:
            DataStore.save(self.tournaments, DATA_FILE)
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def initialize_gui(self):
        """Initialize the graphical user interface"""
        print("\n🎨 Initializing user interface...")
        self.root = tk.Tk()
        self.root.title(f"Playwise v{self.version} - Tournament Manager")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=COLORS["bg_dark"])
        
        # Center window
        self.center_window()
        
        # Initialize UI Manager (Deepak's contribution)
        self.ui_manager = UIManager(self.root, self)
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        print("✅ GUI initialized successfully!")
    
    def center_window(self):
        """Center application window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.root.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    
    def create_tournament(self, name, game_type, format_type, participants_data):
        """
        Create new tournament
        Called from UI Manager (Deepak's component)
        """
        try:
            # Create tournament using Arshpreet's data models
            tournament = Tournament(name, game_type, format_type)
            
            # Add participants
            for p_data in participants_data:
                participant = Participant(
                    p_data['name'],
                    p_data.get('rating', 1000),
                    p_data.get('role', ''),
                    p_data.get('team', '')
                )
                tournament.participants[participant.id] = participant
            
            # Validate tournament
            if len(tournament.participants) < 2:
                return False, "Need at least 2 participants"
            
            # Validate roles using Krish's logic
            if GAME_CONFIGS[game_type].get('role_constraints'):
                errors = TournamentEngine.validate_roles(
                    self._group_by_team(tournament),
                    GAME_CONFIGS[game_type]['role_constraints']
                )
                if errors:
                    return False, "\n".join(errors)
            
            # Save tournament
            self.tournaments[tournament.id] = tournament
            self.save_application_data()
            
            return True, "Tournament created successfully!"
        
        except Exception as e:
            return False, f"Error creating tournament: {str(e)}"
    
    def _group_by_team(self, tournament):
        """Helper to group participants by team for validation"""
        teams = {}
        for p in tournament.participants.values():
            if p.team:
                if p.team not in teams:
                    teams[p.team] = {}
                teams[p.team][p.role] = teams[p.team].get(p.role, 0) + 1
        return teams
    
    def load_tournament(self, tournament_id):
        """Load a tournament for management"""
        if tournament_id in self.tournaments:
            self.current_tournament = self.tournaments[tournament_id]
            return True
        return False
    
    def delete_tournament(self, tournament_id):
        """Delete a tournament"""
        if tournament_id in self.tournaments:
            del self.tournaments[tournament_id]
            self.save_application_data()
            return True
        return False
    
    def generate_fixtures(self):
        """Generate fixtures for current round using Krish's engine"""
        if not self.current_tournament:
            return False, "No tournament loaded"
        
        try:
            success = TournamentEngine.generate_fixtures(self.current_tournament)
            if success:
                self.save_application_data()
                return True, "Fixtures generated successfully!"
            return False, "Fixtures already exist or not enough players"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def record_match_result(self, match_id, score1, score2):
        """Record match result using Krish's engine"""
        if not self.current_tournament:
            return False, "No tournament loaded"
        
        try:
            success = TournamentEngine.record_result(
                self.current_tournament, match_id, score1, score2
            )
            if success:
                self.save_application_data()
                return True, "Result recorded successfully!"
            return False, "Failed to record result"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def advance_round(self):
        """Advance to next round"""
        if not self.current_tournament:
            return False, "No tournament loaded"
        
        try:
            success = TournamentEngine.advance_round(self.current_tournament)
            if success:
                self.save_application_data()
                return True, f"Advanced to Round {self.current_tournament.current_round}"
            return False, "Complete all matches first"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def finish_tournament(self):
        """Finish the tournament and show victory screen"""
        if not self.current_tournament:
            return False, "No tournament loaded"
        
        try:
            TournamentEngine.finish_tournament(self.current_tournament)
            self.save_application_data()
            return True, "Tournament finished!"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_leaderboard(self):
        """Get leaderboard using Adityan's analytics"""
        if not self.current_tournament:
            return []
        
        return LeaderboardSystem.get_leaderboard(self.current_tournament)
    
    def export_standings(self, filepath):
        """Export standings using Adityan's analytics"""
        if not self.current_tournament:
            return False, "No tournament loaded"
        
        try:
            success = AnalyticsEngine.export_standings_csv(
                self.current_tournament, filepath
            )
            return success, "Exported successfully!" if success else "Export failed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_tournament_stats(self):
        """Get tournament statistics using Adityan's analytics"""
        if not self.current_tournament:
            return {}
        
        return AnalyticsEngine.get_tournament_stats(self.current_tournament)
    
    def get_winner(self):
        """Get tournament winner"""
        if not self.current_tournament or not self.current_tournament.is_finished:
            return None
        
        standings = self.current_tournament.get_active_participants()
        return standings[0] if standings else None
    
    def on_closing(self):
        """Handle application close"""
        if messagebox.askokcancel("Quit", "Do you want to quit Playwise?"):
            print("\n" + "=" * 80)
            print(" THANK YOU FOR USING PLAYWISE!")
            print(f" Team: {self.team_name}")
            print("=" * 80)
            self.save_application_data()
            self.root.destroy()
    
    def run(self):
        """Start the application main loop"""
        print("\n🚀 Starting application...")
        print("=" * 80)
        self.root.mainloop()


# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    try:
        app = PlaywiseApplication()
        app.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
