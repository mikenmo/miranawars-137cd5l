# Shuriken Wars
Shuriken Wars is a game created using Pygame and Protobuf. It has the same mechanics as the Warcraft 3 custom map Mirana Wars. The game also has its own build in chat system that runs with TCP sockets and the game state with UDP sockets. The manual for the hotkeys of the game can be found in the repository.
### Setting up
1. Install pygame and protobuf packages using the command "pip3 <package>"
2. Run server using the command "python3 server.py <num_of_clients>"
3. Run client(s) using the command "python3 client.py <server_ip_address> <player_name>"
