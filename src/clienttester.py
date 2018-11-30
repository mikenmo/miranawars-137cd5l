import socket
import sys
import pickle
from classes.Player import *
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
client_socket.connect(server_address)

player = Player("kenneth",2,2)

client_socket.sendall(pickle.dumps(player))
data = client_socket.recv(4096)
data = pickle.loads(data)
print(data.name,data.id)