import player_pb2 as PlayerModule
import tcp_packet_pb2 as TcpPacketModule
import socket as Socket
import select
import sys

BUFFER_SIZE = 1024

#global client socket
server_address = ("202.92.144.45", 80)
client_socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
client_socket.connect(server_address)

def createLobby(max_players=4):
    #instantiate attributes
    create_lobby_packet = TcpPacketModule.TcpPacket.CreateLobbyPacket()
    create_lobby_packet.type = TcpPacketModule.TcpPacket.CREATE_LOBBY
    create_lobby_packet.max_players = max_players
    
    #send then receive
    client_socket.sendall(create_lobby_packet.SerializeToString())
    data = client_socket.recv(BUFFER_SIZE)
    #parse received data
    create_lobby_packet = TcpPacketModule.TcpPacket.CreateLobbyPacket()
    create_lobby_packet.ParseFromString(data)
    
    #debug
    print(create_lobby_packet)

    #auto join creator
    joinLobby(create_lobby_packet.lobby_id)

def joinLobby(lobby_id):
    #instantiate player
    player = PlayerModule.Player()
    player.name = input("Enter name: ")

    #instantiate attributes
    connect_packet = TcpPacketModule.TcpPacket.ConnectPacket()
    connect_packet.type = TcpPacketModule.TcpPacket.CONNECT
    connect_packet.player.name = player.name
    connect_packet.lobby_id = lobby_id
    
    #send then receive
    client_socket.sendall(connect_packet.SerializeToString())
    data = client_socket.recv(BUFFER_SIZE)
    #parse received data
    connect_packet = TcpPacketModule.TcpPacket.ConnectPacket()
    connect_packet.ParseFromString(data)

    #debug
    print(connect_packet)

def sendMessage():
    #instantiate attributes
    chat_packet = TcpPacketModule.TcpPacket.ChatPacket()
    chat_packet.type = TcpPacketModule.TcpPacket.CHAT
    chat_packet.message = sys.stdin.readline()

    #send then receive
    client_socket.sendall(chat_packet.SerializeToString())
    data = client_socket.recv(BUFFER_SIZE)
    #parse received data
    chat_packet = TcpPacketModule.TcpPacket.ChatPacket()
    chat_packet.ParseFromString(data)

    sys.stdout.write("<You>") 
    sys.stdout.write(chat_packet.message)
    sys.stdout.flush()
    #debug
    #print(chat_packet)

def receiveMessage(socks):
    #instantiate attributes
    data = socks.recv(BUFFER_SIZE)
    
    chat_packet = TcpPacketModule.TcpPacket.ChatPacket()
    chat_packet.ParseFromString(data)

    sys.stdout.write(str(chat_packet))

def quitLobby():
    #instantiate attributes
    disconnect_packet = TcpPacketModule.TcpPacket.DisconnectPacket()
    disconnect_packet.type = TcpPacketModule.TcpPacket.DISCONNECT
    
    #send then receive
    client_socket.sendall(disconnect_packet.SerializeToString())
    data = client_socket.recv(BUFFER_SIZE)
    #parse received data
    disconnect_packet = TcpPacketModule.TcpPacket.DisconnectPacket()
    disconnect_packet.ParseFromString(data)

    #debug
    #print(disconnect_packet)

def showAllPlayers():
    #instantiate attributes
    player_list_packet = TcpPacketModule.TcpPacket.PlayerListPacket()
    player_list_packet.type = TcpPacketModule.TcpPacket.PLAYER_LIST

    #get data from server
    client_socket.sendall(player_list_packet.SerializeToString())
    data = client_socket.recv(BUFFER_SIZE)
    #parse received data
    player_list_packet = TcpPacketModule.TcpPacket.PlayerListPacket()
    player_list_packet.ParseFromString(data)
    print(player_list_packet)

# test functions
# createLobby()
# showAllPlayers()
# sendMessage()

choice = 0

while choice != "3":
    print("Mirana Wars Chat Program")
    print("[1] Create Lobby")
    print("[2] Join Lobby")
    print("[3] Exit Program")
    choice = input(">> ")

    if choice == "1":
        createLobby()
    elif choice == "2":
        lobby_id = input("Enter Lobby ID: ")
        joinLobby(lobby_id)
    elif choice == "3":
        break
    else:
        print("Invalid input")

    while True: 
        # maintains a list of possible input streams 
        sockets_list = [sys.stdin, client_socket] 
        
        # """ There are two possible input situations. Either the 
        # user wants to give  manual input to send to other people, 
        # or the server is sending a message  to be printed on the 
        # screen. Select returns from sockets_list, the stream that 
        # is reader for input. So for example, if the server wants 
        # to send a message, then the if condition will hold true 
        # below.If the user wants to send a message, the else 
        # condition will evaluate as true"""
        read_sockets, write_socket, error_socket = select.select(sockets_list,[],[]) 
        
        for socks in read_sockets: 
            if socks == client_socket: 
                receiveMessage(socks)
                sys.stdout.flush() # display written message
            else:
                sendMessage()
                
    

