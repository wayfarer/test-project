# test-project

A full-stack baseball player statistics application with a Flask backend and Vue.js frontend. Displays player data from an external API, allows sorting by hits or home runs, generates LLM-powered player descriptions, and enables editing player statistics.

## Tech Stack

- **Backend**: Flask (Python) with Poetry for dependency management
- **Frontend**: Vue.js 3 with TypeScript and Vite
- **Database**: PostgreSQL
- **CORS**: Enabled for cross-origin requests between frontend and backend

## Prerequisites

- Python 3.10+
- Poetry
- Node.js 20.19.0+ or 22.12.0+
- npm
- PostgreSQL

## Setup

### Backend Setup

1. Navigate to the server directory:
   ```bash
   cd server
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Create a `.env` file (optional, uses defaults if not present):
   ```bash
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5000
   FLASK_DEBUG=True
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Set up the database:
   ```bash
   # Create the database (in psql)
   CREATE DATABASE test_project;
   
   # Initialize the schema
   poetry run python -m server.init_db
   
   # Sync players from the external API
   poetry run python -m server.sync_players
   ```

### Frontend Setup

1. Navigate to the client directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (optional, uses defaults if not present):
   ```bash
   VITE_API_URL=http://localhost:5000
   ```

## Running the Application

From the project root directory, run:

```bash
make run
```

This will start both the Flask server and Vue.js development server concurrently. The output from both servers will be displayed in your terminal.

- **Backend API**: http://localhost:5000
- **Frontend**: http://localhost:5173 (or the next available port)

Press `Ctrl+C` to stop both servers.

### Other Make Commands

- `make stop` - Stop both server and client processes
- `make clean` - Stop services and clean up PID files
- `make help` - Show available commands

## Project Structure

```
test-project/
├── client/          # Vue.js frontend
│   ├── src/
│   └── package.json
├── server/          # Flask backend
│   ├── src/server/
│   └── pyproject.toml
└── Makefile        # Convenience commands
```

## API Endpoints

- `GET /` - Returns `{"message": "Hello World"}`
- `GET /api/players?sort_by=hits|home_runs` - Get all players, sorted by hits or home runs
- `GET /api/players/<id>` - Get a single player by ID
- `GET /api/players/<id>/description` - Get or generate LLM description for a player
- `PUT /api/players/<id>` - Update a player's data
- `POST /api/players/sync` - Sync players from external API to database

## Environment Variables

### Backend (`server/.env`)
- `FLASK_HOST` - Server host (default: `0.0.0.0`)
- `FLASK_PORT` - Server port (default: `5000`)
- `FLASK_DEBUG` - Enable debug mode (default: `True`)
- `OPENAI_API_KEY` - OpenAI API key for LLM-generated player descriptions (required)
- `DB_HOST` - Database host (default: `localhost`)
- `DB_PORT` - Database port (default: `5432`)
- `DB_NAME` - Database name (default: `test_project`)
- `DB_USER` - Database user (default: current system user)
- `DB_PASSWORD` - Database password (optional, uses passwordless auth if not set)

### Frontend (`client/.env`)
- `VITE_API_URL` - Backend API base URL (default: `http://localhost:5000`)

## Development

The application is configured for development with:
- Hot module replacement in Vue.js
- Flask debug mode enabled
- CORS enabled for local development

## Features

- **Player List**: View all baseball players with key statistics
- **Sorting**: Sort players by hits or home runs
- **Player Details**: Click on any player to see their full statistics and an AI-generated description
- **Edit Players**: Edit player data with changes persisted to the database
- **LLM Descriptions**: Automatically generates player descriptions using OpenAI's API (cached for performance)
