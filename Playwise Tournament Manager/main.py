"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ PLAYWISE - TOURNAMENT MANAGEMENT SYSTEM                                   ║
║                                                                           ║
║ Main Application Controller                                               ║
║ Created by: Team DATA DRIFTERS (All Members)                              ║
║                                                                           ║
║ Team Members:                                                             ║
║ - Shimon Pandey (S25CSEU0993) - Team Lead                                 ║
║ - Arshpreet Singh (S25CSEU0980) - Data Models                             ║
║ - Krish Agarwal (S25CSEU0985) - Tournament Logic                          ║
║ - Adityan (S25CSEU0977) - Analytics                                       ║
║ - Deepak Bisht (S25CSEU0986) - UI Components                              ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sys

# Import all modules
from config import WINDOW_WIDTH, WINDOW_HEIGHT, GAME_CONFIGS
from data_models import Tournament, Participant, DataStore
from tournament_logic import TournamentEngine
from analytics import LeaderboardSystem, AnalyticsEngine
from ui_components import UIManager


# ==============================================================================
# MAIN APPLICATION CLASS
# ==============================================================================

class PlaywiseApp:
    """Main application controller"""
    
    def __init__(self):
        """Initialize application"""
        self.version = "2.0"
        self.team = "DATA DRIFTERS"
        
        # Show startup banner
        self.show_banner()
        
        # Load data
        print("\n📂 Loading tournament data...")
        self.tournaments = DataStore.load()
        print(f"✅ Loaded {len(self.tournaments)} tournament(s)\n")
        
        self.current_tournament = None
        
        # Create GUI
        self.create_window()
    
    def show_banner(self):
        """Display team banner"""
        print("=" * 80)
        print(r"""
    ____  __    ___  __  __ _       __  ____  _____  ______
   / __ \/ /   /   | \ \/ /| |     / / /  _/ / ___/ / ____/
  / /_/ / /   / /| |  \  / | | /| / /  / /   \__ \ / __/   
 / ____/ /___/ ___ |  / /  | |/ |/ / _/ /   ___/ // /___   
/_/   /_____/_/  |_| /_/   |__/|__/ /___/  /____//_____/   
        """)
        print("=" * 80)
        print(f"  PLAYWISE TOURNAMENT MANAGER v{self.version}")
        print(f"  TEAM: {self.team}")
        print("=" * 80)
        print(f"{'NAME':<30} {'STUDENT ID':<15} {'ROLE'}")
        print("-" * 80)
        print(f"{'Shimon Pandey (Lead)':<30} {'S25CSEU0993':<15} {'System Integration & PPT'}")
        print(f"{'Arshpreet Singh':<30} {'S25CSEU0980':<15} {'Data Models & Report'}")
        print(f"{'Krish Agarwal':<30} {'S25CSEU0985':<15} {'Tournament Logic'}")
        print(f"{'Adityan':<30} {'S25CSEU0977':<15} {'Analytics & Leaderboard'}")
        print(f"{'Deepak Bisht':<30} {'S25CSEU0986':<15} {'UI Components'}")
        print("-" * 80)
        print(f"\n🐍 Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ All modules loaded successfully!")
        print("=" * 80)
    
    def create_window(self):
        """Create main window"""
        print("\n🎨 Initializing GUI...\n")
        
        self.root = tk.Tk()
        self.root.title(f"Playwise v{self.version} - Tournament Manager")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # Set background
        from config import COLORS
        self.root.configure(bg=COLORS["bg_dark"])
        
        # Create UI
        self.ui = UIManager(self.root, self)
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        print("✅ GUI ready!\n")
        print("=" * 80)
        print("🚀 Application started successfully!")
        print("=" * 80)
    
    def run(self):
        """Start application"""
        self.root.mainloop()
    
    def save_data(self):
        """Save all tournaments"""
        DataStore.save(self.tournaments)
    
    def on_close(self):
        """Handle window close"""
        if messagebox.askokcancel("Quit", "Exit Playwise?"):
            print("\n" + "=" * 80)
            print("  THANK YOU FOR USING PLAYWISE!")
            print(f"  Team: {self.team}")
            print("=" * 80)
            self.save_data()
            self.root.destroy()
    
    # ==========================================================================
    # TOURNAMENT OPERATIONS
    # ==========================================================================
    
    def create_tournament(self, name, game, format_type, participants_data):
        """Create new tournament"""
        try:
            # Create tournament
            tournament = Tournament(name, game, format_type)
            
            # Add participants
            participant_list = []
            for pdata in participants_data:
                p = Participant(
                    pdata['name'],
                    pdata.get('rating', 1000),
                    pdata.get('role', ''),
                    pdata.get('team', '')
                )
                tournament.add_participant(p)
                participant_list.append(p)
            
            # Validate
            if len(tournament.participants) < 2:
                return False, "Need at least 2 participants"
            
            # Check role constraints
            game_config = GAME_CONFIGS[game]
            errors = TournamentEngine.validate_roles(participant_list, game_config)
            if errors:
                return False, "\n".join(errors)
            
            # Save
            self.tournaments[tournament.id] = tournament
            self.current_tournament = tournament
            self.save_data()
            
            return True, "Tournament created successfully!"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def load_tournament(self, tournament_id):
        """Load tournament"""
        if tournament_id in self.tournaments:
            self.current_tournament = self.tournaments[tournament_id]
            return True
        return False
    
    def delete_tournament(self, tournament_id):
        """Delete tournament"""
        if tournament_id in self.tournaments:
            del self.tournaments[tournament_id]
            self.save_data()
            return True
        return False


# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    try:
        app = PlaywiseApp()
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
