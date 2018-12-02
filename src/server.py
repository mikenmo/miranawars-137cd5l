import socket
import sys
try:
   import cPickle as pickle
except:
   import pickle
from classes.Player import *
from classes.Arrow import *



WAITING_FOR_PLAYERS = 1
GAME_START = 2
IN_PROGRESS = 3


players={}
arrows={}
num_players=4
num_arrows=0

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
server_socket.bind(server_address)

def broadcast(keyword, data):
    for k,v in players.items():
        server_socket.sendto(pickle.dumps((keyword,data),pickle.HIGHEST_PROTOCOL),v.address)

gameState = WAITING_FOR_PLAYERS
print("SERVER START")
while True:
    data, address = server_socket.recvfrom(4096)
    keyword, data = pickle.loads(data)
    if gameState == WAITING_FOR_PLAYERS:
        if(keyword == "CONNECT"):
            data.id = len(players)
            data.address = address
            players[data.id]=data
            broadcast("CONNECTED",data)
            print('%s connected....' % data.name)
            
            if(len(players)==num_players):
                print("Game State: START")
                gameState = GAME_START
                broadcast("GAME_STATE",([(p.id,p.xpos,p.ypos) for k,p in players.items()],[(a.playerId,a.xpos,a.ypos) for k,a in arrows.items()]))   

    elif gameState == GAME_START:
        if(keyword == "PLAYER"):
            players[data.id].xpos = data.xpos
            players[data.id].ypos = data.ypos
        if(keyword == "ARROW"):
            arrows[data.playerId] = data
        if(keyword == "ARROW_MOVE"):
            arrows[data.playerId].xpos = data.xpos
            arrows[data.playerId].ypos = data.ypos
        if(keyword == "ARROW_END"):
            arrows.pop(data,None)
        broadcast("GAME_STATE",([(p.id,p.xpos,p.ypos) for k,p in players.items()],[(a.playerId,a.xpos,a.ypos) for k,a in arrows.items()]))


