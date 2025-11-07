import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from server.utils import (
    get_all_players_from_db,
    get_player_by_id,
    get_or_generate_player_description,
    update_player_in_db,
    sync_players_from_api,
    BaseballPlayer,
)
from server.db import init_db

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return jsonify({"message": "Hello World"}), 200


@app.route('/api/players', methods=['GET'])
def get_players():
    """Get all players, optionally sorted by hits or home_runs."""
    sort_by = request.args.get('sort_by', 'hits')
    
    # Validate sort_by parameter
    if sort_by not in ['hits', 'home_runs', 'hits_per_game']:
        return jsonify({"error": "sort_by must be 'hits', 'home_runs', or 'hits_per_game'"}), 400
    
    try:
        players = get_all_players_from_db(sort_by=sort_by)
        return jsonify([player.to_dict() for player in players]), 200
    except Exception as e:
        import traceback
        print(f"Error in get_players: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    """Get a single player by ID."""
    try:
        player = get_player_by_id(player_id)
        if not player:
            return jsonify({"error": "Player not found"}), 404
        return jsonify(player.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/players/<int:player_id>/description', methods=['GET'])
def get_player_description(player_id):
    """Get or generate a player description."""
    try:
        player = get_player_by_id(player_id)
        if not player:
            return jsonify({"error": "Player not found"}), 404
        
        description = get_or_generate_player_description(player_id)
        return jsonify({"description": description}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/players/<int:player_id>', methods=['PUT'])
def update_player(player_id):
    """Update a player's data."""
    try:
        player = get_player_by_id(player_id)
        if not player:
            return jsonify({"error": "Player not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update player fields from request data (exclude computed fields)
        computed_fields = {'id', 'hits_per_game'}  # Fields that shouldn't be updated directly
        for key, value in data.items():
            if hasattr(player, key) and key not in computed_fields:
                # Handle None values - convert to appropriate defaults
                if value is None:
                    if key in ['games', 'at_bats', 'runs', 'hits', 'doubles', 'triples', 
                              'home_runs', 'rbis', 'walks', 'strikeouts', 'stolen_bases', 
                              'caught_stealing']:
                        value = 0
                    elif key in ['batting_average', 'on_base_percentage', 'slugging_percentage', 
                                'ops']:
                        value = 0.0
                    elif key == 'is_edited':
                        value = False
                setattr(player, key, value)
        
        player.is_edited = True
        player.id = player_id
        
        updated = update_player_in_db(player)
        if not updated:
            return jsonify({"error": "Failed to update player"}), 500
        
        return jsonify(player.to_dict()), 200
    except ValueError as e:
        import traceback
        print(f"ValueError in update_player: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        print(f"Error in update_player: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/players/sync', methods=['POST'])
def sync_players():
    """Sync players from the external API to the database."""
    try:
        sync_players_from_api()
        return jsonify({"message": "Players synced successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host=host, port=port)

