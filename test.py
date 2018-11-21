import player_pb2 as PlayerModule
import tcp_packet_pb2 as TcpPacketModule
import socket as Socket
# import threading as Thread

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
    data = client_socket.recv(1024)
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
    data = client_socket.recv(1024)
    #parse received data
    connect_packet = TcpPacketModule.TcpPacket.ConnectPacket()
    connect_packet.ParseFromString(data)

    #debug
    print(connect_packet)

def sendMessage():
    #instantiate attributes
    chat_packet = TcpPacketModule.TcpPacket.ChatPacket()
    chat_packet.type = TcpPacketModule.TcpPacket.CHAT
    chat_packet.message = input("Enter message: ")

    #send then receive
    client_socket.sendall(chat_packet.SerializeToString())
    data = client_socket.recv(1024)
    #parse received data
    chat_packet = TcpPacketModule.TcpPacket.ChatPacket()
    chat_packet.ParseFromString(data)

    #debug
    #print(chat_packet)

def quitLobby():
    #instantiate attributes
    disconnect_packet = TcpPacketModule.TcpPacket.DisconnectPacket()
    disconnect_packet.type = TcpPacketModule.TcpPacket.DISCONNECT
    
    #send then receive
    client_socket.sendall(disconnect_packet.SerializeToString())
    data = client_socket.recv(1024)
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
    data = client_socket.recv(1024)
    #parse received data
    player_list_packet = TcpPacketModule.TcpPacket.PlayerListPacket()
    player_list_packet.ParseFromString(data)
    print(player_list_packet)

# test functions
# createLobby()
# showAllPlayers()
# sendMessage()
