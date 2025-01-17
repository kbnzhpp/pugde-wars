from config import *
from classes import *
import socket
import pickle
import random as rd
from client import get_spawn_position
from player import *

def connect_to_server(players, ip_, skin_player, skin_hook):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_, 5555))
        sock.settimeout(0.3)
        
        data = sock.recv(1024)
        init_data = pickle.loads(data)
        
        if "your_id" in init_data:
            player_id = init_data["your_id"]
            print(f"[DEBUG] Got player_id: {player_id}")
            
            # Debug spawn position
            spawn_data = get_spawn_position(player_id)
            print(f"[DEBUG] Spawn data: {spawn_data}")
            
            try:
                # Create player with explicit parameters
                local_player = Player(
                    x=spawn_data["pos"][0],
                    y=spawn_data["pos"][1],
                    group=players,
                    team=spawn_data["team"],
                    skin=skin_player,
                    skin_hook=skin_hook
                )
                print(f"[DEBUG] Player created: {local_player}")
                
                local_player.set_id(player_id)
                print(f"[DEBUG] Player ID set: {local_player.id_p}")
                
                # Add to group with error checking
                if players is None:
                    print("[ERROR] Players group is None!")
                    return None, None
                    
                players.add(local_player)
                print(f"[DEBUG] Player added to group. Group size: {len(players)}")
                
                return sock, local_player
                
            except Exception as e:
                print(f"[ERROR] Player creation failed: {e}")
                return None, None
        else:
            print("[ERROR] No ID in init data")
            return None, None
            
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None, None