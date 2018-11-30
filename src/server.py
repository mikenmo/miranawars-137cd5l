import socket
import sys
import pickle
from classes.Player import *
from classes.Arrow import *



WAITING_FOR_PLAYERS = 1
GAME_START = 2
IN_PROGRESS = 3


players={}
arrow_arr=[]
num_players=2
num_arrows=0

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
server_socket.bind(server_address)

def broadcast(keyword, data):
    for k,v in players.items():
        server_socket.sendto(pickle.dumps((keyword,data)),v.address)

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
            print(len(players))
            print(num_players)
            
            if(len(players)==num_players):
                print("Game State: START")
                gameState = GAME_START
    elif gameState == GAME_START:
        gameState=IN_PROGRESS
        
    elif gameState == IN_PROGRESS:
        if(keyword == "PLAYER"):
            players[data.id].xpos = data.xpos
            players[data.id].ypos = data.ypos



