# test-project

A full-stack application with a Flask backend and Vue.js frontend.

## Tech Stack

- **Backend**: Flask (Python) with Poetry for dependency management
- **Frontend**: Vue.js 3 with TypeScript and Vite
- **CORS**: Enabled for cross-origin requests between frontend and backend

## Prerequisites

- Python 3.10+
- Poetry
- Node.js 20.19.0+ or 22.12.0+
- npm

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

## Environment Variables

### Backend (`server/.env`)
- `FLASK_HOST` - Server host (default: `0.0.0.0`)
- `FLASK_PORT` - Server port (default: `5000`)
- `FLASK_DEBUG` - Enable debug mode (default: `True`)

### Frontend (`client/.env`)
- `VITE_API_URL` - Backend API base URL (default: `http://localhost:5000`)

## Development

The application is configured for development with:
- Hot module replacement in Vue.js
- Flask debug mode enabled
- CORS enabled for local development
