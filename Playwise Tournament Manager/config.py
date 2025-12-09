"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ CONFIGURATION MODULE                                                      ║
║ Developer: Shimon Pandey (S25CSEU0993) - Team Lead                        ║
║ Role: Game configurations, constants, and application settings            ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

# ==============================================================================
# FILE PATHS
# ==============================================================================
DATA_FILE = "playwise_data.json"

# ==============================================================================
# DEFAULT VALUES
# ==============================================================================
DEFAULT_ELO = 1000
MIN_PLAYERS = 2
MAX_PLAYERS = 128

# ==============================================================================
# UI COLORS (Dark Theme)
# ==============================================================================
COLORS = {
    "bg_dark": "#0f0f23",
    "bg_card": "#1a1a2e",
    "accent": "#3282b8",
    "text_main": "#e4e4e4",
    "text_sub": "#a0a0a0",
    "success": "#00d9ff",
    "danger": "#ff2e63",
    "warning": "#feca57",
    "gold": "#ffd700",
    "silver": "#c0c0c0",
    "bronze": "#cd7f32"
}

# ==============================================================================
# WINDOW SETTINGS
# ==============================================================================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 820

# ==============================================================================
# GAME CONFIGURATIONS
# ==============================================================================
GAME_CONFIGS = {
    "Chess": {
        "type": "individual",
        "has_elo": True,
        "has_roles": False,
        "roles": [],
        "role_constraints": {},
        "allows_draw": True,
        "desc": "Strategy game with Elo ratings"
    },
    "Valorant": {
        "type": "team",
        "has_elo": False,
        "has_roles": True,
        "roles": ["IGL", "Duelist", "Controller", "Initiator", "Sentinel"],
        "role_constraints": {"IGL": 1},
        "allows_draw": False,
        "desc": "5v5 tactical shooter, needs 1 IGL"
    },
    "PUBG Mobile": {
        "type": "team",
        "has_elo": False,
        "has_roles": True,
        "roles": ["IGL", "Assaulter", "Sniper", "Support"],
        "role_constraints": {"IGL": 1},
        "allows_draw": False,
        "desc": "Battle Royale, needs 1 IGL"
    },
    "Cricket": {
        "type": "team",
        "has_elo": False,
        "has_roles": True,
        "roles": ["Captain", "Batsman", "Bowler", "All-Rounder", "Wicket Keeper"],
        "role_constraints": {"Captain": 1, "Wicket Keeper": 1},
        "allows_draw": False,
        "desc": "11v11, needs Captain and Wicket Keeper"
    },
    "Football": {
        "type": "team",
        "has_elo": False,
        "has_roles": True,
        "roles": ["Captain", "Striker", "Midfielder", "Defender", "Goalkeeper"],
        "role_constraints": {"Captain": 1, "Goalkeeper": 1},
        "allows_draw": True,
        "desc": "11v11, needs Captain and Goalkeeper"
    },
    "Basketball": {
        "type": "team",
        "has_elo": False,
        "has_roles": True,
        "roles": ["Captain", "Point Guard", "Shooting Guard", "Forward", "Center"],
        "role_constraints": {"Captain": 1},
        "allows_draw": False,
        "desc": "5v5, needs 1 Captain"
    },
    "Table Tennis": {
        "type": "individual",
        "has_elo": False,
        "has_roles": False,
        "roles": [],
        "role_constraints": {},
        "allows_draw": False,
        "desc": "1v1 racquet sport"
    },
    "Badminton": {
        "type": "individual",
        "has_elo": False,
        "has_roles": False,
        "roles": [],
        "role_constraints": {},
        "allows_draw": False,
        "desc": "1v1 or 2v2 racquet sport"
    },
    "Counter-Strike 2": {
        "type": "team",
        "has_elo": False,
        "has_roles": True,
        "roles": ["IGL", "AWPer", "Entry", "Support", "Lurker"],
        "role_constraints": {"IGL": 1},
        "allows_draw": False,
        "desc": "5v5 FPS, needs 1 IGL"
    },
    "Volleyball": {
        "type": "team",
        "has_elo": False,
        "has_roles": True,
        "roles": ["Captain", "Setter", "Hitter", "Blocker", "Libero"],
        "role_constraints": {"Captain": 1, "Libero": 1},
        "allows_draw": False,
        "desc": "6v6, needs Captain and Libero"
    },
    "Custom": {
        "type": "individual",
        "has_elo": False,
        "has_roles": False,
        "roles": [],
        "role_constraints": {},
        "allows_draw": True,
        "desc": "Fully customizable"
    }
}

# ==============================================================================
# TOURNAMENT FORMATS
# ==============================================================================
FORMATS = ["League", "Knockout", "Swiss"]

# ==============================================================================
# RANK MEDALS
# ==============================================================================
MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
