"""Script to sync players from the external API to the database."""
from server.utils import sync_players_from_api

if __name__ == "__main__":
    print("Syncing players from API...")
    try:
        sync_players_from_api()
        print("Players synced successfully!")
    except Exception as e:
        print(f"Error syncing players: {e}")
        exit(1)

