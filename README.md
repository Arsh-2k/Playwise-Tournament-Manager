# Playwise Tournament Manager

A robust, console-based Python application for managing tournaments in esports, sports, and board games, built by Team Data Drifters. This system supports multiple games, flexible team sizes, three tournament formats, advanced fixture algorithms, and live player statistics, with persistent data storage via JSON.

---

## 🚀 Features

- **Game Presets:** Supports Valorant, BGMI, CS:GO, FIFA, Chess, Table Tennis, Carrom, Badminton, PUBG, and Custom.
- **Team Size Handling:** Each game preset has customizable team sizes.
- **Tournament Formats:** Includes League (Round Robin), Knockout (Elimination), and Swiss system.
- **Intelligent Fixtures:** Automatic pairing for each round, with BYE assignment, seeding, and fair Swiss pairing logic.
- **Stats & MVP Calculation:** Real-time team and individual performance tracking (K/D ratio, goals, ratings, MVP selection).
- **Leaderboard:** Sorted live by points, performance metrics, and ratings.
- **JSON Data Persistence:** All tournament data and history saved securely across sessions.
- **Clean Console UI:** Animated boot sequence, guided inputs, error handling, and help screens.

---

## 🛠️ Installation

git clone https://github.com/yourusername/playwise-tournament-manager.git
cd playwise-tournament-manager
python playwise_tourn_manager.py


> **Requirements:** Uses only standard Python 3 libraries (uuid, json, sys, os, time, itertools, random). No external dependencies.

---

## 📦 File Guide

- `playwise_tourn_manager.py` : Main project script containing all modules.
- `playwise_data.json` : Automatically generated file for tournament data persistence.
- (Optional) `README.md` : Documentation and usage instructions.

---

## 🧐 Usage

1. **Startup:** Run the script to launch the boot animation and project intro.
2. **Main Menu Options:**
    - Create Tournament: Set up a new event, select game, format, register participants.
    - Manage Tournament: Generate matches, enter results with detailed team/player stats, view leaderboard and history, progress through rounds.
    - Delete Tournament: Permanently remove an event from storage.
    - Help: Display tournament format rules and suggestions.
    - Exit: Save and safely close the program.
3. **Statistics:** Input kills/deaths for shooters, goals/assists for sports, ratings for chess. Track MVPs and leaderboard rankings live.

---

## 📑 Tournament Formats Explained

| Format    | Description                                               |
|-----------|----------------------------------------------------------|
| League    | Everyone plays everyone, BYEs for odd count rounds.      |
| Knockout  | Single elimination, top seed vs last seed, etc.          |
| Swiss     | Fair score-based pairing, avoid repeat matches if possible.|

---

## 👥 Team Credits

| Role               | Name              | Contribution               |
|--------------------|-------------------|----------------------------|
| Team Lead          | Shimon Pandey     | System Architecture        |
| Data Architect     | Arshpreet Singh   | Data Models & Seeding      |
| Logic Developer    | Krish Agarwal     | Fixture Algorithms         |
| Analytics & Stats  | Adityan           | Leaderboard Logic          |
| Interface Designer | Deepak Bisht      | Menus & Validation         |

---

## 💡 Tech Stack

- **Language:** Python 3
- **Libraries:** uuid, json, sys, os, time, random, itertools
- **Persistence:** JSON file storage

---

## 🎓 How It Works (Quick Overview)

- **Object-oriented Design**: All major entities are classes (`Tournament`, `Participant`, `Match`).
- **Fixture Generation**: Algorithms generate matches round-by-round based on tournament format.
- **Results & Stats**: Supports detailed stat entry per team and player, performance ratios, and MVP selection.
- **Leaderboard**: Automatic sorting and display based on live results.
- **Data Management**: Persistent, robust error-handling for save/load operations.
- **Console UI**: Clean navigation, animated intro, guided input queries.

---

## 📜 Example Demo

1. **Create new tournament**: Choose your game, format, input participant names and (for teams) assign roles and members.
2. **Generate fixtures**: Get automatic pairing for each round.
3. **Enter results**: Input team/player stats, select match winners/DRAW (except in Knockout).
4. **View leaderboard**: Instantly see rankings, team metrics, and top performers.
5. **Export history**: Save full match history to text (.txt) for reporting.

---

*Built with pride by Data Drifters for Bennett University and the esports community!*

