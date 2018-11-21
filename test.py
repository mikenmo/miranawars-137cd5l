import player_pb2 as PlayerModule
import tcp_packet_pb2 as TcpPacketModule
import socket as Socket
import threading as Thread
server_address = ("202.92.144.45", 80)
client_socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
client_socket.connect(server_address)

def createLobby(max_players=5):
    create_lobby_packet = TcpPacketModule.TcpPacket.CreateLobbyPacket()
    create_lobby_packet.type = TcpPacketModule.TcpPacket.CREATE_LOBBY
    create_lobby_packet.max_players = max_players
    
    client_socket.sendall(create_lobby_packet.SerializeToString())
    data = client_socket.recv(1024)

    create_lobby_packet = TcpPacketModule.TcpPacket.CreateLobbyPacket()
    create_lobby_packet.ParseFromString(data)
    
    joinLobby(create_lobby_packet.lobby_id)

def joinLobby(lobby_id):
    player = PlayerModule.Player()
    player.name = input("Enter name: ")

    connect_packet = TcpPacketModule.TcpPacket.ConnectPacket()
    connect_packet.type = TcpPacketModule.TcpPacket.CONNECT
    connect_packet.player.name = player.name
    connect_packet.lobby_id = lobby_id
    connect_packet.update = TcpPacketModule.TcpPacket.ConnectPacket.SELF
    
    client_socket.sendall(connect_packet.SerializeToString())
    data = client_socket.recv(1024)

    connect_packet = TcpPacketModule.TcpPacket.ConnectPacket()
    connect_packet.ParseFromString(data)

    
# def sendMessage():



# lobby = createLobby()
