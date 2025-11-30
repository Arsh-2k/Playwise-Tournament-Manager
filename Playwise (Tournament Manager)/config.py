"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ CONFIGURATION MODULE                                                      ║
║ Developer: Shimon Pandey (S25CSEU0993) - Team Lead                        ║
║ Contribution: Game Configurations, Constants & Application Settings       ║
║ Role: Centralized configuration for all game types and UI settings        ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

# ==============================================================================
# INTELLIGENT GAME CONFIGURATIONS
# ==============================================================================

GAME_CONFIGS = {
    "Chess": {
        "type": "individual",
        "metric": "Points",
        "has_elo": True,  # Only Chess has Elo
        "has_roles": False,
        "rec_format": "Swiss",
        "rec_players": "4-16 players recommended",
        "min_players": 2,
        "max_players": 64,
        "desc": "Strategy board game. Elo rating determines seeding.",
        "score_type": "Points",
        "allows_draw": True
    },
    "Valorant": {
        "type": "team",
        "metric": "Rounds Won",
        "has_elo": False,
        "has_roles": True,
        "roles": ["IGL", "Duelist", "Controller", "Initiator", "Sentinel"],
        "role_constraints": {"IGL": 1},
        "rec_format": "Knockout",
        "rec_players": "4-16 teams (5 players each) recommended",
        "min_players": 4,
        "max_players": 32,
        "desc": "5v5 tactical shooter. Teams need 1 IGL (In-Game Leader).",
        "score_type": "Rounds",
        "allows_draw": False
    },
    "PUBG Mobile": {
        "type": "team",
        "metric": "Points",
        "has_elo": False,
        "has_roles": True,
        "roles": ["IGL", "Assaulter", "Sniper", "Support"],
        "role_constraints": {"IGL": 1},
        "rec_format": "League",
        "rec_players": "8-16 teams (4 players each) recommended",
        "min_players": 4,
        "max_players": 32,
        "desc": "Battle Royale. Teams earn points based on kills and placement.",
        "score_type": "Points",
        "allows_draw": False
    },
    "Cricket": {
        "type": "team",
        "metric": "Runs",
        "has_elo": False,
        "has_roles": True,
        "roles": ["Captain", "Batsman", "Bowler", "All-Rounder", "Wicket Keeper"],
        "role_constraints": {"Captain": 1, "Wicket Keeper": 1},
        "rec_format": "Knockout",
        "rec_players": "4-16 teams (11 players each) recommended",
        "min_players": 2,
        "max_players": 32,
        "desc": "Team sport. Requires 1 Captain and 1 Wicket Keeper per team.",
        "score_type": "Runs",
        "allows_draw": False
    },
    "Football": {
        "type": "team",
        "metric": "Goals",
        "has_elo": False,
        "has_roles": True,
        "roles": ["Captain", "Striker", "Midfielder", "Defender", "Goalkeeper"],
        "role_constraints": {"Captain": 1, "Goalkeeper": 1},
        "rec_format": "League",
        "rec_players": "4-20 teams (11 players each) recommended",
        "min_players": 4,
        "max_players": 32,
        "desc": "Team sport. Each team needs 1 Captain and 1 Goalkeeper.",
        "score_type": "Goals",
        "allows_draw": True
    },
    "Table Tennis": {
        "type": "individual",
        "metric": "Sets",
        "has_elo": False,
        "has_roles": False,
        "rec_format": "Knockout",
        "rec_players": "4-32 players recommended",
        "min_players": 2,
        "max_players": 64,
        "desc": "Fast-paced racquet sport. Best of 3 or 5 sets.",
        "score_type": "Sets",
        "allows_draw": False
    },
    "Badminton": {
        "type": "individual",
        "metric": "Sets",
        "has_elo": False,
        "has_roles": False,
        "rec_format": "Knockout",
        "rec_players": "4-32 players recommended (Singles or Doubles)",
        "min_players": 2,
        "max_players": 64,
        "desc": "Racquet sport. Can be played as singles (1v1) or doubles (2v2).",
        "score_type": "Sets",
        "allows_draw": False
    },
    "Counter-Strike 2": {
        "type": "team",
        "metric": "Rounds Won",
        "has_elo": False,
        "has_roles": True,
        "roles": ["IGL", "AWPer", "Entry Fragger", "Support", "Lurker"],
        "role_constraints": {"IGL": 1},
        "rec_format": "Swiss",
        "rec_players": "8-16 teams (5 players each) recommended",
        "min_players": 4,
        "max_players": 32,
        "desc": "5v5 tactical FPS. Teams need strategic role distribution.",
        "score_type": "Rounds",
        "allows_draw": False
    },
    "Basketball": {
        "type": "team",
        "metric": "Points",
        "has_elo": False,
        "has_roles": True,
        "roles": ["Captain", "Point Guard", "Shooting Guard", "Small Forward", "Power Forward", "Center"],
        "role_constraints": {"Captain": 1},
        "rec_format": "Knockout",
        "rec_players": "4-16 teams (5 players each) recommended",
        "min_players": 4,
        "max_players": 32,
        "desc": "Team sport. Fast-paced court game with 5 players per team.",
        "score_type": "Points",
        "allows_draw": False
    },
    "Volleyball": {
        "type": "team",
        "metric": "Sets",
        "has_elo": False,
        "has_roles": True,
        "roles": ["Captain", "Setter", "Outside Hitter", "Middle Blocker", "Libero"],
        "role_constraints": {"Captain": 1, "Libero": 1},
        "rec_format": "League",
        "rec_players": "4-12 teams (6 players each) recommended",
        "min_players": 4,
        "max_players": 24,
        "desc": "Team sport. 6 players per team, requires 1 Captain and 1 Libero.",
        "score_type": "Sets",
        "allows_draw": False
    },
    "Custom": {
        "type": "individual",
        "metric": "Points",
        "has_elo": False,
        "has_roles": True,
        "roles": ["Player", "Captain", "Leader", "Support"],
        "role_constraints": {},
        "rec_format": "League",
        "rec_players": "Any number of players",
        "min_players": 2,
        "max_players": 128,
        "desc": "Fully customizable tournament for any sport or game.",
        "score_type": "Points",
        "allows_draw": True
    }
}

# ==============================================================================
# APPLICATION CONSTANTS
# ==============================================================================

# File Storage
DATA_FILE = "playwise_data.json"
BACKUP_FILE = "playwise_backup.json"

# UI Colors (Dark Cyberpunk Theme)
COLORS = {
    "bg_dark": "#0f0f23",
    "bg_panel": "#1a1a2e",
    "bg_card": "#16213e",
    "accent": "#0f4c75",
    "accent_bright": "#3282b8",
    "accent_hover": "#bbe1fa",
    "text_main": "#e4e4e4",
    "text_sub": "#a0a0a0",
    "success": "#00d9ff",
    "danger": "#ff2e63",
    "warning": "#feca57",
    "header": "#162447",
    "border": "#1f4068",
    "gold": "#ffd700",
    "silver": "#c0c0c0",
    "bronze": "#cd7f32"
}

# Tournament Settings
TOURNAMENT_FORMATS = ["League", "Knockout", "Swiss"]
MIN_PARTICIPANTS = 2
MAX_PARTICIPANTS = 128
DEFAULT_ELO = 1000

# Window Settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 820
SIDEBAR_WIDTH = 240

# Font Settings
FONT_FAMILY = "Segoe UI"
FONT_SIZES = {
    "logo": 28,
    "header": 22,
    "subheader": 16,
    "body": 11,
    "small": 9,
    "button": 10
}

# Result Entry Button Labels
RESULT_BUTTONS = {
    "player1_win": "Player 1 Wins",
    "player2_win": "Player 2 Wins",
    "draw": "Draw"
}

# Victory Screen Messages
VICTORY_MESSAGES = [
    "🏆 CONGRATULATIONS! 🏆",
    "🎉 CHAMPION! 🎉",
    "👑 VICTORY! 👑",
    "⭐ WINNER! ⭐"
]

# Animation Settings
ANIMATION_SPEED = 50  # milliseconds
CONFETTI_COUNT = 100

# Export Settings
CSV_DELIMITER = ","
CSV_ENCODING = "utf-8"

# Validation Rules
VALIDATION = {
    "min_tournament_name_length": 3,
    "max_tournament_name_length": 50,
    "min_player_name_length": 2,
    "max_player_name_length": 30,
    "min_team_name_length": 2,
    "max_team_name_length": 30
}

# Help Text
HELP_TEXT = {
    "league": "Round-robin format where every team plays every other team once.",
    "knockout": "Single elimination format. Lose once and you're out!",
    "swiss": "Pairs teams with similar records. No elimination until final rounds.",
    "elo": "Rating system used in Chess to measure player strength (1000-2500).",
    "bye": "When there's an odd number of players, one gets a free win (BYE).",
    "seeding": "Higher rated players/teams get favorable matchups in early rounds."
}

# Status Messages
STATUS = {
    "creating": "Creating tournament...",
    "loading": "Loading tournament...",
    "generating": "Generating fixtures...",
    "saving": "Saving data...",
    "exporting": "Exporting standings...",
    "finishing": "Finalizing tournament..."
}

# Error Messages
ERRORS = {
    "no_tournament": "No tournament selected. Please load a tournament first.",
    "incomplete_matches": "Please complete all matches before advancing.",
    "invalid_score": "Invalid score entered. Please enter valid numbers.",
    "duplicate_name": "A participant with this name already exists.",
    "insufficient_players": "Need at least 2 participants to create tournament.",
    "role_violation": "Team role requirements not met. Check role constraints.",
    "file_error": "Error reading/writing file. Check permissions."
}

# Success Messages
SUCCESS = {
    "tournament_created": "Tournament created successfully!",
    "fixtures_generated": "Fixtures generated for current round!",
    "result_recorded": "Match result recorded successfully!",
    "round_advanced": "Advanced to next round!",
    "tournament_finished": "Tournament finished! View the results.",
    "export_success": "Data exported successfully!",
    "data_saved": "All changes saved!"
}

# UI Labels
LABELS = {
    "tournament_name": "Tournament Name:",
    "game_type": "Select Game:",
    "format": "Tournament Format:",
    "num_players": "Number of Players:",
    "player_name": "Player Name:",
    "team_name": "Team Name:",
    "role": "Role:",
    "elo_rating": "Elo Rating:",
    "generate": "Generate Sheet",
    "create": "Create Tournament",
    "load": "Load Tournament",
    "delete": "Delete Tournament",
    "export": "Export Standings",
    "finish": "Finish Tournament"
}

# Keyboard Shortcuts
SHORTCUTS = {
    "new_tournament": "<Control-n>",
    "save": "<Control-s>",
    "export": "<Control-e>",
    "quit": "<Control-q>",
    "refresh": "<F5>"
}

# Match Status Icons
MATCH_STATUS_ICONS = {
    "pending": "⏳",
    "in_progress": "▶️",
    "completed": "✅",
    "bye": "🎁"
}

# Tournament Status Icons
TOURNAMENT_STATUS_ICONS = {
    "active": "⚡",
    "finished": "🏆",
    "paused": "⏸️"
}

# Rank Medals
RANK_MEDALS = {
    1: "🥇",
    2: "🥈",
    3: "🥉"
}
