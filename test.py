import player_pb2 as Player
import tcp_packet_pb2 as TcpPacket

def createLobby(max_players):
    clPacket = TcpPacket.CreateLobbyPacket()
    clPacket.type = TcpPacket.PacketType.CREATE_LOBBY
    clPacket.max_players = max_players

    player = Player()
    player.name = input("Enter name: ")
    connectPacket = TcpPacket.ConnectPacket()
    connectPacket.type = TcpPacket.PacketType.CONNECT
    connectPacket.player = player
    connectPacket.update = TcpPacket.ConnectPacket.SELF