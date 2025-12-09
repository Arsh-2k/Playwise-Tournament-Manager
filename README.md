# 🏆 Playwise - Intelligent Tournament Management System

> **Academic Project** | Computational Thinking & Programming (2025CSET100)  
> **Team:** DATA DRIFTERS | **Institution:** Bennett University | **Batch:** 33

---

## 🎯 Overview

**Playwise** is a comprehensive desktop tournament management system built with Python that supports 11+ sports and esports with intelligent algorithms for fixture generation, bracket seeding, Swiss pairing, and real-time analytics. Designed for schools, colleges, gaming clubs, and amateur tournament organizers managing 2-128 participants.

### Key Highlights
- ⚡ **Smart Algorithms** - Automated fixture generation with collision-free pairing
- 🎮 **Multi-Sport** - 11 games from Chess to Valorant with game-specific configurations
- 📊 **Live Analytics** - Real-time leaderboards, MVP tracking, K/D statistics
- 💾 **Auto-Save** - JSON-based persistence with automatic backup system
- 🏆 **Victory Screen** - Podium display with top 3 finishers and awards

---

## ✨ Features

### Tournament Formats
- **League (Round-Robin)** - Everyone plays everyone, fairest format
- **Knockout (Elimination)** - Single elimination bracket, fastest format
- **Swiss System** - Balanced pairing based on points, no rematches

### Supported Games
| Sport | Type | Special Features |
|-------|------|------------------|
| ♟️ Chess | 1v1 | Elo rating system |
| 🎮 Valorant | Team (5v5) | K/D tracking, roles |
| 🏏 Cricket | Team (11v11) | Captain/Wicket Keeper roles |
| ⚽ Football | Team (11v11) | Goal difference tiebreaker |
| 🏀 Basketball | Team (5v5) | Score tracking |
| 🏓 Table Tennis | 1v1 | Individual competition |
| 🎯 CS:GO/CS2 | Team (5v5) | K/D tracking |
| 📱 PUBG Mobile | Squad | Kill statistics |
| 🎾 Badminton | 1v1/2v2 | Flexible formats |
| 🏐 Volleyball | Team (6v6) | Set scoring |
| 🥊 Other Sports | Custom | Configurable |

### Analytics & Reporting
- 🥇 **Medal System** - Gold/Silver/Bronze for top 3
- 📈 **Leaderboard** - Sorted by points, goal difference, rating
- ⭐ **MVP Tracking** - Match MVPs with award counts
- 💀 **K/D Statistics** - For shooter games (Valorant, CS2, PUBG)
- 📊 **Top Scorers** - Highest scoring players
- 📁 **CSV Export** - Complete tournament report for Excel

### Smart Features
- **BYE System** - Automatic handling for odd number of players
- **Role Validation** - Enforces team composition rules (e.g., 1 Captain per team)
- **Draw Controls** - Game-specific draw allowance (e.g., no draws in Valorant)
- **Data Backup** - Automatic backup before each save
- **Multi-Tournament** - Run multiple tournaments simultaneously

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.7+ | Core application logic |
| **GUI** | Tkinter | Desktop interface |
| **Data Storage** | JSON | Persistent tournament data |
| **ID Generation** | UUID | Unique player/match identifiers |
| **Export** | CSV | Tournament reports |

**No External Dependencies** - Uses only Python standard library for maximum compatibility

---

## 📁 Project Structure

playwise/
├── main.py # Entry point, PlaywiseApp class
├── config.py # Game configs, colors, constants
├── data_models.py # Participant, Match, Tournament classes
├── tournament_logic.py # TournamentEngine, pairing algorithms
├── analytics.py # Leaderboard, stats, CSV export
├── ui_components.py # UIManager, all screens
├── playwise_data.json # Tournament database
├── playwise_data_backup.json # Automatic backup
└── README.md # This file


---

## 👥 Team DATA DRIFTERS

| Member | Student ID | Role | Key Contributions |
|--------|-----------|------|-------------------|
| **Shimon Pandey** | S25CSEU0993 | 🎖️ Team Lead | System integration, main.py, presentation, testing |
| **Arshpreet Singh** | S25CSEU0980 | 💾 Data Engineer | Data models, JSON persistence, backup system, report |
| **Krish Agarwal** | S25CSEU0985 | 🧠 Algorithm Engineer | Tournament formats, pairing logic, BYE handling |
| **Adityan** | S25CSEU0977 | 📊 Analytics Lead | Leaderboards, MVP tracking, statistics, CSV export |
| **Deepak Bisht** | S25CSEU0986 | 🎨 UI/UX Lead | Complete interface, match cards, victory screen |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- No pip installations required (uses standard library only)

### Installation

1. **Clone/Download** the project

git clone <https://github.com/Arsh-2k/Playwise-Tournament-Manager>
cd playwise

2. **Verify Python version**

python --version Python 3.x

3. **Run the application**

python main.py


### First Tournament

1. Click **"Create Tournament"** button
2. Enter tournament name
3. Select game type (e.g., Football, Valorant)
4. Choose format (League/Knockout/Swiss)
5. Generate player sheet and enter participant details
6. Click **"Save & Start"**
7. Navigate to **"Manage Tournament"**
8. Click **"Generate Fixtures"** to create matches
9. Record match results using quick buttons (P1 Win/P2 Win/Draw)
10. View live leaderboard and statistics
11. Export results to CSV when complete

---

## 📖 User Guide

### Creating a Tournament

**Step 1: Basic Info**
- Tournament Name: e.g., "Bennett Premier League 2025"
- Game: Select from dropdown
- Format: Choose based on time/fairness needs

**Step 2: Add Players**
- Enter number of participants (2-128)
- Click "Generate Sheet"
- Fill in player details:
  - Name (required)
  - Elo/Rating (for seeding in Knockout)
  - Team (for team-based games)
  - Role (if game requires specific roles)

**Step 3: Start Tournament**
- System validates role constraints
- Creates tournament with all participants
- Ready to generate fixtures

### Managing Matches

**Fixture Generation**
- Click "Generate Fixtures" for current round
- System auto-pairs based on format:
  - **League**: Random pairing each round
  - **Swiss**: Similar-strength pairing, no rematches
  - **Knockout**: Seeded bracket (best vs worst)

**Recording Results**
- Use quick buttons: **P1 Win** / **P2 Win** / **Draw**
- System automatically:
  - Updates player statistics
  - Calculates MVP (highest scorer)
  - Tracks K/D (for shooter games)
  - Handles eliminations (Knockout)
  - Updates leaderboard

**BYE Handling**
- Automatically assigned if odd number of players
- Auto-recorded as 1-0 win
- Fair rotation in League format

### Viewing Analytics

**Leaderboard Tab**
- Ranked by: Points → Goal Difference → Rating
- Shows: Matches played, W/D/L, Points, Goals, MVP count
- Medal emojis for top 3 🥇🥈🥉

**Statistics Tab**
- Total/Completed/Pending matches
- Average goals per match
- Tournament MVP (most awards)
- Top 5 scorers

**MVP Leaderboard** (separate view)
- Top 10 players by MVP awards
- Useful for identifying consistent performers

**K/D Leaderboard** (shooter games only)
- Top 10 by Kill/Death ratio
- Shows kills, deaths, K/D ratio

### Exporting Results

1. Click **"Export CSV"** button
2. Choose save location
3. File contains:
   - Tournament information
   - Complete standings table
   - MVP leaderboard
   - K/D statistics (if applicable)
4. Open in Excel/Google Sheets for analysis

---

## 🧪 Testing

The system has been tested with:
- ✅ 4, 8, 16, 32, 64, 128 player tournaments
- ✅ All 3 formats across multiple games
- ✅ 100+ match results recorded
- ✅ Edge cases: BYEs, draws, eliminations
- ✅ File corruption recovery
- ✅ CSV export validation in Excel
- ✅ Data persistence across application restarts

---

## 🎓 Learning Outcomes

This project demonstrates:
- **Modular Architecture** - 5 independent modules with clear interfaces
- **Data Structures** - Efficient use of dictionaries, lists, sorting
- **Algorithm Design** - Swiss pairing, bracket generation, seeding
- **File I/O** - JSON serialization, backup strategies, error handling
- **GUI Development** - Event-driven programming, dynamic UI updates
- **Team Collaboration** - Distributed development, integration, version control
- **Testing** - Edge case handling, data validation, user acceptance testing
- **Software Engineering** - Clean code, documentation, maintainability

---

## 🔮 Future Enhancements

### Planned Features
- 🌐 **Web Interface** - React/Vue frontend with REST API backend
- 🔐 **User Authentication** - Login system with admin panel
- ☁️ **Cloud Storage** - PostgreSQL/MongoDB with real-time sync
- 📱 **Mobile App** - React Native for iOS/Android
- 🎥 **Live Streaming** - Integration with tournament broadcasts
- 📧 **Email Notifications** - Match reminders, results updates
- 🤖 **AI Predictions** - Match outcome probabilities
- 📊 **Advanced Analytics** - Win streaks, head-to-head records, performance trends
- 🎨 **Bracket Visualization** - Interactive tournament tree for Knockout
- 🌍 **Internationalization** - Multi-language support

### Potential Improvements
- Double elimination format
- Custom scoring systems (3-1-0 for football)
- Undo/edit match results
- Player profile pages with history
- Dark/light theme toggle
- Tournament templates for quick setup
- Drag-and-drop player seeding
- Print-friendly bracket layouts

---

## 📜 License

**Academic Project** - Bennett University  
Course: Computational Thinking & Programming (2025CSET100)

*Free to use for educational purposes. Attribution appreciated.*

---

## 🤝 Contributing

This is an academic project, but we welcome:
- 🐛 Bug reports
- 💡 Feature suggestions
- 📖 Documentation improvements
- 🧪 Test cases

---

## 📞 Contact

**Team DATA DRIFTERS**
- **Team Lead:** Shimon Pandey (S25CSEU0993)
- **Institution:** Bennett University
- **Course:** Computational Thinking & Programming
- **Batch:** 33 (2025)

---

## 🙏 Acknowledgments

- **Bennett University** - For the learning opportunity
- **CT&P Faculty** - For guidance and support
- **Open Source Community** - For Python and documentation
- **Our Team** - For dedication and collaboration

---

## 📊 Project Statistics

- **Lines of Code:** ~2000+
- **Modules:** 5 independent files
- **Classes:** 7 core classes
- **Functions:** 50+ methods
- **Games Supported:** 11
- **Tournament Formats:** 3
- **Development Time:** 3 weeks
- **Team Size:** 5 developers

---

## 🏆 Why Playwise?

> "Better than spreadsheets, simpler than enterprise tools, perfect for schools and amateur tournaments."

- ✅ **No Installation Hassles** - Pure Python, no dependencies
- ✅ **Offline Ready** - Works without internet
- ✅ **Fast Setup** - Create tournament in 2 minutes
- ✅ **Automatic Everything** - No manual calculations
- ✅ **Professional Output** - CSV reports for organizers
- ✅ **Free & Open** - No licensing costs

---

**Built with ❤️ by Team DATA DRIFTERS | Bennett University | 2025**






