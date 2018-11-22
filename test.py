import player_pb2 as PlayerModule
import tcp_packet_pb2 as TcpPacketModule
import socket as Socket
import select
import sys

BUFFER_SIZE = 1024

# global client socket
server_address = ("202.92.144.45", 80)
client_socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
client_socket.connect(server_address)

def createLobby(max_players=4):
    # instantiate attributes
    create_lobby_packet = TcpPacketModule.TcpPacket.CreateLobbyPacket()
    create_lobby_packet.type = TcpPacketModule.TcpPacket.CREATE_LOBBY
    create_lobby_packet.max_players = max_players
    
    # send then receive
    client_socket.sendall(create_lobby_packet.SerializeToString())
    data = client_socket.recv(BUFFER_SIZE)
    # parse received data
    create_lobby_packet = TcpPacketModule.TcpPacket.CreateLobbyPacket()
    create_lobby_packet.ParseFromString(data)
    
    # debug
    print( "Lobby created! Your lobby ID is \"{}\"".format(create_lobby_packet.lobby_id) )
    print( "Auto joining lobby..." )

    #auto join creator
    joinLobby(create_lobby_packet.lobby_id)

def joinLobby(lobby_id):
    # instantiate player
    player = PlayerModule.Player()
    player.name = input("Enter name: ")

    # instantiate attributes
    connect_packet = TcpPacketModule.TcpPacket.ConnectPacket()
    connect_packet.type = TcpPacketModule.TcpPacket.CONNECT
    connect_packet.player.name = player.name
    connect_packet.lobby_id = lobby_id
    
    # send then receive
    client_socket.sendall(connect_packet.SerializeToString())
    data = client_socket.recv(BUFFER_SIZE)
    #parse received data
    connect_packet = TcpPacketModule.TcpPacket.ConnectPacket()
    connect_packet.ParseFromString(data)

    # debug
    # print(connect_packet)

def send(message):
    # instantiate attributes
    chat_packet = TcpPacketModule.TcpPacket.ChatPacket()
    chat_packet.type = TcpPacketModule.TcpPacket.CHAT
    chat_packet.message = message

    if chat_packet.message == "/exit\n":
        quitLobby()
    elif chat_packet.message == "/show_players\n":
        showAllPlayers()
    elif chat_packet.message == "\n":
        return
    else:
        client_socket.sendall(chat_packet.SerializeToString())

def receive(socks):
    tcp_packet = TcpPacketModule.TcpPacket()

    # instantiate attributes
    data = socks.recv(BUFFER_SIZE)
    tcp_packet.ParseFromString(data)

    # receive message
    if tcp_packet.type == TcpPacketModule.TcpPacket.CHAT:
        chat_packet = TcpPacketModule.TcpPacket.ChatPacket()
        chat_packet.ParseFromString(data)

        sys.stdout.write("<"+chat_packet.player.name+"> ")
        sys.stdout.write(chat_packet.message)
        sys.stdout.flush() # display written message
    # receive disconnect packet
    elif tcp_packet.type == TcpPacketModule.TcpPacket.DISCONNECT:
        disconnect_packet = TcpPacketModule.TcpPacket.DisconnectPacket()
        disconnect_packet.ParseFromString(data)

        sys.stdout.write(disconnect_packet.player.name+" has disconnected from the chat room.\n")
        sys.stdout.flush() # display written message
    # receive connect packet
    elif tcp_packet.type == TcpPacketModule.TcpPacket.CONNECT:
        connect_packet = TcpPacketModule.TcpPacket.ConnectPacket()
        connect_packet.ParseFromString(data)

        sys.stdout.write(connect_packet.player.name+" has connected to the chat room.\n")
        sys.stdout.flush() # display written message

def quitLobby():
    # instantiate attributes
    disconnect_packet = TcpPacketModule.TcpPacket.DisconnectPacket()
    disconnect_packet.type = TcpPacketModule.TcpPacket.DISCONNECT

    client_socket.sendall(disconnect_packet.SerializeToString())

def showAllPlayers():
    # instantiate attributes
    player_list_packet = TcpPacketModule.TcpPacket.PlayerListPacket()
    player_list_packet.type = TcpPacketModule.TcpPacket.PLAYER_LIST

    # get data from server
    client_socket.sendall(player_list_packet.SerializeToString())
    data = client_socket.recv(BUFFER_SIZE)
    # parse received data
    player_list_packet = TcpPacketModule.TcpPacket.PlayerListPacket()
    player_list_packet.ParseFromString(data)
    print(player_list_packet)

choice = 0
message = ""

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
        continue


    while message != "/exit\n":
        # maintains a list of possible input streams 
        sockets_list = [sys.stdin, client_socket] 

        read_sockets, write_socket, error_socket = select.select(sockets_list,[],[]) 
        
        for socks in read_sockets: 
            if socks == client_socket: 
                receive(socks)
            else:
                message = sys.stdin.readline()
                send(message)