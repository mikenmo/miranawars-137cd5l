import socket
import sys
import math
import threading
import time
try:
   import cPickle as pickle
except:
   import pickle

   
from classes.Player import *
from classes.Arrow import *

WAITING_FOR_PLAYERS = 1
GAME_START = 2
IN_PROGRESS = 3

PLAYER_SIZE = 50
ARROW_SIZE = 20

HEIGHT = 500
WIDTH = 500

players={}
arrows={}
init_pos = [(0,0),(WIDTH,HEIGHT),(WIDTH,0),(0,HEIGHT)]

num_players=4
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
server_socket.bind(server_address)
gameState = WAITING_FOR_PLAYERS


def broadcast(keyword, data):
    for k,v in players.items():
        server_socket.sendto(pickle.dumps((keyword,data),pickle.HIGHEST_PROTOCOL),v.address)

#condition to stop player thread
def playerCheck(playerId):
    global players
    if not(players[playerId].xpos>players[playerId].destx+50 or players[playerId].xpos+PLAYER_SIZE<players[playerId].destx or players[playerId].ypos>players[playerId].desty+50 or players[playerId].ypos+PLAYER_SIZE<players[playerId].desty):
        print(players[playerId].xpos,players[playerId].destx,players[playerId].ypos,players[playerId].desty)
        print("HERE")
        return False
    # if(0 > plac
    return True

#thread to move player
def playerMoving(playerId):
    global players
    players[playerId].moving = True
    while playerCheck(playerId):
        players[playerId].move()
        broadcast("PLAYER",(playerId,players[playerId].xpos,players[playerId].ypos))
        time.sleep(0.01)
    players[playerId].moving = False


#condition to stop arrow thread
def arrowCheck(arrow):
    global players
    #check if boundary
    if 0 > arrow.xpos or arrow.xpos > WIDTH or 0 > arrow.ypos or arrow.ypos > HEIGHT:
        return(False)
    #check if maximum distance
    elif math.sqrt((arrow.xpos-arrow.startx)**2 + (arrow.ypos-arrow.starty)**2) > arrow.distance*100+500:
        return(False)
    #check if it hits player
    for k,v in players.items():
        if k == data.playerId:
            continue
        if not (data.xpos>v.xpos+PLAYER_SIZE or data.xpos+ARROW_SIZE<v.xpos or data.ypos>v.ypos+PLAYER_SIZE or data.ypos+ARROW_SIZE<v.ypos):
            v.hp -= math.sqrt(players[data.playerId].power) * 34
            print(v.hp)
            return False
    return(True)


#thread to move arrow
def arrowMoving(playerId,mouse_x,mouse_y):
    global players,arrows
    #compute the angle
    dx = mouse_x - players[playerId].xpos
    dy = mouse_y - players[playerId].ypos
    arrows[playerId].angle = math.atan2(dy, dx)
    while arrowCheck(arrows[playerId]):
        arrows[playerId].move()
        broadcast("ARROW",(playerId,arrows[playerId].xpos,arrows[playerId].ypos))
        time.sleep(0.1)
    #remove arrow from game
    arrows.pop(playerId)
    broadcast("ARROW_DONE",playerId)
#set cooldown for arrow
def arrowCooldown(playerId):
    global players
    players[playerId].arrowCd = False
    broadcast("ARROW_READY",playerId)



def receiver():
    while True:
        global players,arrows,gameState
        data, address = server_socket.recvfrom(4096)
        keyword, data = pickle.loads(data)
        if gameState == WAITING_FOR_PLAYERS:
            if(keyword == "CONNECT"):
                playerId = len(players)
                player = Player(data,init_pos[playerId])
                players[playerId] = player
                players[playerId].address = address
                broadcast("CONNECTED",(playerId,players))
                print('%s connected....' % player.name)
            
                if(len(players)==num_players):
                    print("Game State: START")
                    gameState = GAME_START
                    broadcast("GAME_START",'')

        elif gameState == GAME_START:
            if(keyword == "PLAYER"):
                playerId, mouse_x, mouse_y = data
                #compute the angle
                dx = mouse_x - players[playerId].xpos
                dy = mouse_y - players[playerId].ypos
                players[playerId].destx = mouse_x
                players[playerId].desty = mouse_y
                players[playerId].angle = math.atan2(dy, dx)
                if(not players[playerId].moving):
                    pThread = threading.Thread(target=playerMoving,name="pThread",args=[playerId])
                    pThread.start()

            if(keyword == "ARROW"):
                playerId, mouse_x, mouse_y = data
                #initialize arrow
                arrow = Arrow(playerId,players[playerId].xpos,players[playerId].ypos, players[playerId].power, players[playerId].distance, players[playerId].speed)
                #change arrow lists
                arrows[playerId] = arrow
                broadcast("ARROW_ADDED",(playerId,arrow))
                #arrow thread
                aThread = threading.Thread(target=arrowMoving,name="aThread",args=[playerId,mouse_x,mouse_y])
                aThread.start()
                #arrow cooldown
                players[playerId].arrowCd = True
                cdTimer = threading.Timer(5.0,arrowCooldown(playerId))
                cdTimer.start()

receiverThread = threading.Thread(target=receiver, name = "receiveThread", args = [])
receiverThread.start()
print("SERVER START")

        


