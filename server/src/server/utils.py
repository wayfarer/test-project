import os
import requests
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from .db import get_db_connection


@dataclass
class BaseballPlayer:
    """Model representing a baseball player with normalized field names."""
    id: Optional[int] = None  # Database ID, None if not saved
    player_name: str = ""
    position: str = ""
    games: int = 0
    at_bats: int = 0
    runs: int = 0
    hits: int = 0
    doubles: int = 0
    triples: int = 0
    home_runs: int = 0
    rbis: int = 0
    walks: int = 0
    strikeouts: int = 0
    stolen_bases: int = 0
    caught_stealing: int = 0
    batting_average: float = 0.0
    on_base_percentage: float = 0.0
    slugging_percentage: float = 0.0
    ops: float = 0.0
    is_edited: bool = False

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "BaseballPlayer":
        """
        Create a BaseballPlayer from raw API data.
        
        Handles the API's inconsistent field naming:
        - "third baseman" -> triples (3B)
        - "a walk" -> walks (BB)
        """
        return cls(
            player_name=raw["Player name"],
            position=raw["position"],
            games=raw["Games"],
            at_bats=raw["At-bat"],
            runs=raw["Runs"],
            hits=raw["Hits"],
            doubles=raw["Double (2B)"],
            triples=raw["third baseman"],  # API incorrectly names this field
            home_runs=raw["home run"],
            rbis=raw["run batted in"],
            walks=raw["a walk"],  # API incorrectly names this field
            strikeouts=raw["Strikeouts"],
            stolen_bases=raw["stolen base"],
            caught_stealing=raw["Caught stealing"],
            batting_average=float(raw["AVG"]),
            on_base_percentage=float(raw["On-base Percentage"]),
            slugging_percentage=float(raw["Slugging Percentage"]),
            ops=float(raw["On-base Plus Slugging"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "player_name": self.player_name,
            "position": self.position,
            "games": self.games,
            "at_bats": self.at_bats,
            "runs": self.runs,
            "hits": self.hits,
            "doubles": self.doubles,
            "triples": self.triples,
            "home_runs": self.home_runs,
            "rbis": self.rbis,
            "walks": self.walks,
            "strikeouts": self.strikeouts,
            "stolen_bases": self.stolen_bases,
            "caught_stealing": self.caught_stealing,
            "batting_average": self.batting_average,
            "on_base_percentage": self.on_base_percentage,
            "slugging_percentage": self.slugging_percentage,
            "ops": self.ops,
            "is_edited": self.is_edited,
        }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "BaseballPlayer":
        """Create a BaseballPlayer from a database row."""
        return cls(
            id=row["id"],
            player_name=row["player_name"],
            position=row["position"],
            games=row["games"],
            at_bats=row["at_bats"],
            runs=row["runs"],
            hits=row["hits"],
            doubles=row["doubles"],
            triples=row["triples"],
            home_runs=row["home_runs"],
            rbis=row["rbis"],
            walks=row["walks"],
            strikeouts=row["strikeouts"],
            stolen_bases=row["stolen_bases"],
            caught_stealing=row["caught_stealing"],
            batting_average=float(row["batting_average"]),
            on_base_percentage=float(row["on_base_percentage"]),
            slugging_percentage=float(row["slugging_percentage"]),
            ops=float(row["ops"]),
            is_edited=row.get("is_edited", False),
        )


BASEBALL_API_URL = "https://api.hirefraction.com/api/test/baseball"


def fetch_baseball_players_from_api() -> List[BaseballPlayer]:
    """
    Fetch baseball player data from the external API.
    
    Returns:
        List of BaseballPlayer objects with normalized field names.
        
    Raises:
        requests.RequestException: If the API request fails.
        ValueError: If the API response is not valid JSON or missing expected fields.
    """
    response = requests.get(BASEBALL_API_URL, timeout=10)
    response.raise_for_status()
    
    raw_data: List[Dict[str, Any]] = response.json()
    
    players = []
    for raw_player in raw_data:
        try:
            player = BaseballPlayer.from_raw(raw_player)
            players.append(player)
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid player data structure: {e}") from e
    
    return players


def save_player_to_db(player: BaseballPlayer) -> int:
    """
    Save a player to the database. Returns the player's ID.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO players (
            player_name, position, games, at_bats, runs, hits, doubles,
            triples, home_runs, rbis, walks, strikeouts, stolen_bases,
            caught_stealing, batting_average, on_base_percentage,
            slugging_percentage, ops, is_edited
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
    """, (
        player.player_name, player.position, player.games, player.at_bats,
        player.runs, player.hits, player.doubles, player.triples,
        player.home_runs, player.rbis, player.walks, player.strikeouts,
        player.stolen_bases, player.caught_stealing, player.batting_average,
        player.on_base_percentage, player.slugging_percentage, player.ops,
        player.is_edited
    ))
    
    player_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return player_id


def get_all_players_from_db(sort_by: str = "hits") -> List[BaseballPlayer]:
    """
    Get all players from the database.
    
    Args:
        sort_by: Either "hits" or "home_runs" to sort the results.
    
    Returns:
        List of BaseballPlayer objects sorted by the specified field.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Validate sort_by to prevent SQL injection
    valid_sorts = {"hits", "home_runs"}
    if sort_by not in valid_sorts:
        sort_by = "hits"
    
    cur.execute(f"""
        SELECT * FROM players
        ORDER BY {sort_by} DESC
    """)
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [BaseballPlayer.from_db_row(dict(row)) for row in rows]


def get_player_by_id(player_id: int) -> Optional[BaseballPlayer]:
    """
    Get a player by their database ID.
    
    Returns:
        BaseballPlayer if found, None otherwise.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM players WHERE id = %s", (player_id,))
    row = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if row:
        return BaseballPlayer.from_db_row(dict(row))
    return None


def update_player_in_db(player: BaseballPlayer) -> bool:
    """
    Update a player in the database. Returns True if successful.
    
    Requires player.id to be set.
    """
    if not player.id:
        raise ValueError("Player ID is required for update")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE players SET
            player_name = %s, position = %s, games = %s, at_bats = %s,
            runs = %s, hits = %s, doubles = %s, triples = %s,
            home_runs = %s, rbis = %s, walks = %s, strikeouts = %s,
            stolen_bases = %s, caught_stealing = %s, batting_average = %s,
            on_base_percentage = %s, slugging_percentage = %s, ops = %s,
            is_edited = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (
        player.player_name, player.position, player.games, player.at_bats,
        player.runs, player.hits, player.doubles, player.triples,
        player.home_runs, player.rbis, player.walks, player.strikeouts,
        player.stolen_bases, player.caught_stealing, player.batting_average,
        player.on_base_percentage, player.slugging_percentage, player.ops,
        player.is_edited, player.id
    ))
    
    updated = cur.rowcount > 0
    conn.commit()
    cur.close()
    conn.close()
    
    return updated


def sync_players_from_api():
    """
    Fetch players from API and sync them to the database.
    If a player already exists (by name), update them. Otherwise, insert new.
    """
    api_players = fetch_baseball_players_from_api()
    conn = get_db_connection()
    cur = conn.cursor()
    
    for player in api_players:
        # Check if player exists
        cur.execute("SELECT id FROM players WHERE player_name = %s", (player.player_name,))
        existing = cur.fetchone()
        
        if existing:
            # Update existing player (but preserve is_edited flag if it was edited)
            cur.execute("SELECT is_edited FROM players WHERE player_name = %s", (player.player_name,))
            was_edited = cur.fetchone()[0]
            
            player.id = existing[0]
            player.is_edited = was_edited  # Preserve edit status
            update_player_in_db(player)
        else:
            # Insert new player
            save_player_to_db(player)
    
    conn.close()


def get_player_description(player_id: int) -> Optional[str]:
    """
    Get cached description for a player from the database.
    
    Returns:
        Description string if found, None otherwise.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT description FROM player_descriptions WHERE player_id = %s", (player_id,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return result[0]
    return None


def save_player_description(player_id: int, description: str):
    """
    Save or update a player description in the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO player_descriptions (player_id, description)
        VALUES (%s, %s)
        ON CONFLICT (player_id) DO UPDATE SET description = EXCLUDED.description
    """, (player_id, description))
    
    conn.commit()
    cur.close()
    conn.close()


def generate_player_description(player: BaseballPlayer) -> str:
    """
    Generate a description for a player using OpenAI's API.
    
    Args:
        player: BaseballPlayer object to generate description for.
    
    Returns:
        Generated description string.
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set.
        requests.RequestException: If the API request fails.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Build prompt with player statistics
    stats_text = f"""
    {player.player_name} was a {player.position} who played in {player.games} games.
    Career statistics:
    - At-bats: {player.at_bats:,}
    - Hits: {player.hits:,}
    - Home runs: {player.home_runs:,}
    - RBIs: {player.rbis:,}
    - Batting average: {player.batting_average:.3f}
    - On-base percentage: {player.on_base_percentage:.3f}
    - Slugging percentage: {player.slugging_percentage:.3f}
    - OPS: {player.ops:.3f}
    - Stolen bases: {player.stolen_bases}
    """
    
    prompt = f"""Write a brief, engaging description (2-3 sentences) about this baseball player based on their statistics:

{stats_text}

Focus on their most notable achievements and career highlights. Make it interesting and informative."""
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a knowledgeable baseball historian and writer."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.7,
        },
        timeout=30
    )
    
    response.raise_for_status()
    result = response.json()
    
    description = result["choices"][0]["message"]["content"].strip()
    return description


def get_or_generate_player_description(player_id: int) -> str:
    """
    Get player description from cache, or generate and cache it if not found.
    
    Args:
        player_id: Database ID of the player.
    
    Returns:
        Player description string.
    """
    # Try to get from cache
    cached = get_player_description(player_id)
    if cached:
        return cached
    
    # Generate new description
    player = get_player_by_id(player_id)
    if not player:
        raise ValueError(f"Player with ID {player_id} not found")
    
    description = generate_player_description(player)
    
    # Cache it
    save_player_description(player_id, description)
    
    return description
