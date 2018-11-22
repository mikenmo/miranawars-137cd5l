"""
CMSC 137 CD-5L Final Project: Milestone #2
Group: Quartet Mirana
    Crisostomo, Albert Dominic
    Fortes, Patricia
    Mojar, Kenneth
    Umali, Harold
"""
import chat as Chat
import select as Select
import sys as Sys

player_name = input("Enter your name: ")
choice = 0
message = ""

while choice != "3":
    print("Mirana Wars Chat Program")
    print("[1] Create Lobby")
    print("[2] Join Lobby")
    print("[3] Exit Program")
    choice = input(">> ")

    if choice == "1":
        lobby_id = Chat.createLobby(player_name)
        print("Welcome to the chat lobby, {}! The Lobby ID is {}.".format(player_name, lobby_id))

    elif choice == "2":
        lobby_id = input("Enter Lobby ID: ")
        result = Chat.joinLobby(lobby_id, player_name)

        if result == Chat.LOBBY_DNE:
            print("Joining unsuccessful. The chat lobby does not exist.")
            continue
        elif result == Chat.LOBBY_FULL:
            print("Joining unsuccessful. The chat lobby is already full.")
            continue
        elif result == Chat.UNSUCCESSFUL:
            print("Joining unsuccessful.")
            continue
        else:
            print("Welcome to the chat lobby, {}!".format(player_name))

    elif choice == "3":
        break

    else:
        print("Invalid input")


    while message != "/exit\n":
        sockets_list = [Sys.stdin, Chat.client_socket] 
        read_sockets, write_socket, error_socket = Select.select(sockets_list,[],[]) 
        # check each socket to determine source of data input
        for socks in read_sockets:
            # input came from server
            if socks == Chat.client_socket: 
                Chat.receive(socks, player_name)
            # input came from client
            else:
                message = Sys.stdin.readline()
                Chat.send(message)