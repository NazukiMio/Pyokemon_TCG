# Pyokemon TCG – Pokémon Card Game Simulator (Python/PyGame)

This README is also available in 简体中文 [here](README_CN.md) and Español [here](README.md).

## Introduction

**Pyokemon TCG** is an educational, non-commercial Pokémon Trading Card Game simulator built with Python and PyGame. This project recreates the essence of the Pokémon TCG in a digital format as a learning exercise, demonstrating game architecture, turn-based logic, and use of public APIs. It is designed as a didactic tool – applying programming concepts from database management to GUI development – rather than a commercial game. By focusing on clean structure and documentation, Pyokemon TCG serves as both a playable prototype and a teaching resource for Python game development.

## Features Overview

- **User Registration & Login**: Create a local player profile with username/password, and manage authentication. User data (profile, progress) is stored in a local SQLite database.

- **Pokédex (Card Collection)**: View a graphical collection of Pokémon cards unlocked by the user. Cards are displayed in a gallery with filtering options, and an image caching system ensures smooth performance even with many cards.

- **Navigation & Scenes**: Move between game sections using a persistent navigation bar. The interface provides smooth transitions between the main menu, collection, store, battle setup, etc., implemented via a modular scene system.

- **Card Pack Opening**: Acquire new cards through an interactive booster pack opening system. Players can visit the in-game store to obtain card packs (using in-game currency) and open them with a visual “unwrapping” animation to reveal random cards.

- **Local Data Persistence**: All progress (unlocked cards, decks, achievements, etc.) is saved locally. The game uses SQLite to persist user profiles and collection data between sessions. This allows offline play once initial data is downloaded.

- **Card Import Tool**: An external `fetch_card_gui` utility is provided to populate the game’s card database with real card data. This tool fetches card information and images from the Pokémon TCG API and saves them into a local JSON and image set, with configurable rarity distribution.

- **Deck Building (In Development)**: A deck editor is planned for assembling custom decks from the player’s card collection. Players will be able to save multiple decks to use in battles.

- **Turn-Based Battle (In Development)**: A local single-player battle system is being integrated, featuring turn-by-turn gameplay using `pygame-cards` for visual card interactions. The battle logic backend is functional, and a PyGame GUI frontend is in progress. Future updates will allow player vs AI matches entirely offline.

- **Planned Expansions**: The project’s architecture is modular, allowing future additions such as an expanded shop with items or quests, online multiplayer and trading (scaffolded), and social features. These are not yet implemented in the current version.

## Screenshot Showcase

### Welcome Screen

The entry screen of Pyokemon TCG greets players with a stylized Pokémon-themed background and title. This interface is built with PyGame and `pygame-gui`, featuring an animated backdrop and a “Press Start” prompt to proceed into the login/registration flow.

### Login & Registration Screens

The login interface includes fields for username and password, with input validation and user feedback. If the user doesn’t have an account, they can switch to the registration form which ensures unique usernames and password confirmation. User data is saved to a local SQLite database.

### Main Interface (Home)

After logging in, players arrive at the home screen, featuring a top navigation bar, a dynamic content area, and quick-access widgets (e.g., card packs, store, tips). The persistent bottom navigation bar highlights the current section. The UI uses translucent panels and responsive layouts.

### Card Pack Opening

When a player acquires a booster pack, they can open it with an interactive animation. The contents are revealed randomly with visual effects. The background dims to focus attention, enhancing the excitement of discovery.

### Collection – Pokédex

Displays all cards in the game, highlighting collected ones. Filters are available by collected status, rarity, or type. Card images are cached for performance, and a progress indicator shows collection progress.

### Card Data Fetcher Tool

A Tkinter-based developer GUI that fetches card data from the Pokémon TCG API. The user configures how many cards to generate and where to save them. The tool saves JSON metadata and images locally for offline use.

## Installation & Dependencies

**Requirements**: Python 3.10 or higher is required. Use a virtual environment if possible. Install dependencies via:

```
pip install -r requirements.txt
```

### Key Libraries:

- `pygame` – game rendering and loop  
- `pygame-gui` – GUI widgets  
- `pygame-cards` – visual card handling (in battle)  
- `requests` – API fetching  
- `Pillow` – image processing  
- `sqlite3` – local database (builtin)  
- `tkinter` – card import GUI (builtin)  
- `opencv-python`, `graphviz`, `tqdm` – used in dev tools  

Make sure your environment supports a GUI display (PyGame window). No special setup needed for Windows/Mac/Linux beyond installing dependencies.

## How to Run

Run the main game with:

```
python main.py
```

To run the card import GUI:

```
python development/fetch_card/fetch_card_gui.py
```

This opens a Tkinter GUI that fetches and caches card data from the API for offline use.

## Project Structure

```
├── main.py
├── requirements.txt
├── README.md
├── game/
│   ├── core/         # Game logic, backend, auth, database
│   ├── scenes/       # Screens: login, home, pokedex, battle, etc.
│   ├── ui/           # Reusable UI elements
│   └── utils/        # Utilities and helpers
├── assets/           # Images, sounds, fonts
├── data/             # SQLite DB, card data, cache
├── development/
│   ├── fetch_card/   # Card data fetch tool (GUI)
│   ├── generate_tree.py
│   └── ...
└── docs/             # Design notes, diagrams, etc.
```

- `game/` contains modular game code by function.  
- `assets/` holds static media (backgrounds, cards, UI).  
- `data/` stores persistent progress and card data.  
- `development/` includes tools for devs (e.g. card fetcher).  
- `main.py` is the entry point.

## Development Background & License

This project was developed as a final academic project to demonstrate software development and Python game techniques. It is **unofficial**, **non-commercial**, and intended purely for **learning and fun**.

It is not affiliated with or endorsed by Nintendo, The Pokémon Company, or Wizards of the Coast. All Pokémon assets remain their intellectual property and are used here under **fair use** for educational purposes only.

**License**: Open-source for personal and educational use. **Commercial use is strictly prohibited.**

---

**Happy coding, and enjoy exploring the world of Pokémon TCG through this Python project!**
