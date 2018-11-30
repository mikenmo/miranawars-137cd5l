import socket
import sys
import pickle
from classes.Player import *
from classes.Arrow import *

players=[]
arrow_arr=[]
num_players=0
num_arrows=0

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
server_socket.bind(server_address)

def broadcast(data):
    for player in players.iteritems():
        server_socket.send()

print("SERVER START")
while True:
    data, address = server_socket.recvfrom(4096)
    keyword, data = pickle.loads(data)
    if(keyword == "CONNECT"):
        data.id = num_players
        data.address = address
        num_players+=1
        # broadcast()
        players.append(data)
        server_socket.sendto(pickle.dumps(("CONNECTED",data)),address)
        print('%s connected....' % data.name)