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

# constants
WAITING_FOR_PLAYERS     = 1
GAME_START              = 2
GAME_END                = 3
PLAYER_SIZE             = 50
ARROW_SIZE              = 20
WIDTH                   = 500
HEIGHT                  = 500
GAME_DURATION           = 300 # in seconds
RESPAWN_TIME            = 10
ARROW_COOLDOWN          = 4.0
LEAP_COOLDOWN           = 4.0

# dictionaries
players                 = {}
arrows                  = {}

init_pos = [(0,0),(WIDTH,HEIGHT),(WIDTH,0),(0,HEIGHT)]

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (socket.gethostbyname(socket.getfqdn()), 10000)
server_socket.bind(server_address)

# show host ip address
print("Hosting at {}".format(server_address[0]))

try:
    num_players=int(sys.argv[1])
except IndexError:
    print("Correct usage: python3 server.py <num_of_players>")
    raise SystemExit

gameState = WAITING_FOR_PLAYERS

# send data to all clients including the sender
def broadcast(keyword, data):
    for k,v in players.items():
        server_socket.sendto(pickle.dumps((keyword,data),pickle.HIGHEST_PROTOCOL),v.address)

# condition to stop player thread
def playerCheck(playerId):
    global players
    if not(players[playerId].xpos>players[playerId].destx+50 or players[playerId].xpos+PLAYER_SIZE<players[playerId].destx or players[playerId].ypos>players[playerId].desty+50 or players[playerId].ypos+PLAYER_SIZE<players[playerId].desty):
        return False
    if players[playerId].leaping:
        return False
    # if(0 > plac
    return True

# thread to move player
def playerMoving(playerId):
    global players
    players[playerId].moving = True
    while playerCheck(playerId):
        players[playerId].move()
        broadcast("PLAYER",(playerId,players[playerId].xpos,players[playerId].ypos))
        time.sleep(0.01)
    players[playerId].moving = False

def playerLeaping(playerId):
    global players
    players[playerId].leaping = True
    for i in range(0,10):
        players[playerId].leap()
        broadcast("PLAYER",(playerId,players[playerId].xpos,players[playerId].ypos))
        time.sleep(0.01)
    players[playerId].leaping = False
    
def leapCooldown(playerId):
    global players
    players[playerId].leapCd = False
    broadcast("LEAP_READY",playerId)

def playerRespawning(playerId):
    global players
    players[playerId].dead = False
    players[playerId].xpos = init_pos[playerId][0]
    players[playerId].ypos = init_pos[playerId][1]
    players[playerId].hp = 100
    print("%s respawned." % (players[playerId].name))
    broadcast("PLAYER_RESPAWNED",(playerId,players[playerId].xpos,players[playerId].ypos,players[playerId].hp))

def canLevelUp(playerId):
    if players[playerId].xp % 100 == 0:
        # print for debug
        print("CAN LEVEL UP!")
        return True
    # print for debug
    print("SORRY CANNOT BE YET")
    return False

# condition to stop arrow thread
def arrowCheck(playerId):
    global players
    # check if boundary
    if 0 > arrows[playerId].xpos or arrows[playerId].xpos > WIDTH or 0 > arrows[playerId].ypos or arrows[playerId].ypos > HEIGHT:
        return False
    # check if maximum distance
    elif math.sqrt((arrows[playerId].xpos-arrows[playerId].startx)**2 + (arrows[playerId].ypos-arrows[playerId].starty)**2) > arrows[playerId].distance*100+500:
        return False
    # check if it hits player
    for k,v in players.items():
        if k == playerId or v.dead == True:
            continue
        if not (arrows[playerId].xpos>v.xpos+PLAYER_SIZE or arrows[playerId].xpos+ARROW_SIZE<v.xpos or arrows[playerId].ypos>v.ypos+PLAYER_SIZE or arrows[playerId].ypos+ARROW_SIZE<v.ypos):
            v.decreaseHP(math.sqrt(players[playerId].power) * 34)
            players[playerId].increaseHits(1)
            players[playerId].increaseXP(20)
            if canLevelUp(playerId):
                players[playerId].levelUp()
            # print for debug
            print("Player %s's arrow hit player %s.\nPlayer %s's hp: %d" % (players[playerId].name, v.name, v.name, v.hp))
            # playerId's arrow killed their opponent player
            if(v.hp < 0):
                players[playerId].increaseXP(30)
                if canLevelUp(playerId):
                    players[playerId].levelUp()
                players[playerId].increaseKills(1)
                # print for debug
                print("%s died.\nRespawning in 10 seconds...." % v.name)
                respawnTimer = threading.Timer(RESPAWN_TIME,playerRespawning,[k])
                respawnTimer.start()
                players[k].dead = True
                broadcast("PLAYER_KILLED",k)
            # print for debug
            print("Player "+players[playerId].name+" new XP: "+str(players[playerId].xp))
            broadcast("ARROW_HIT",(playerId,players[playerId].hits,players[playerId].xp,k,v.hp))
            return False
    return True 

# thread to move arrow
def arrowMoving(playerId,mouse_x,mouse_y):
    global players,arrows
    # compute the angle
    dx = mouse_x - players[playerId].xpos
    dy = mouse_y - players[playerId].ypos
    arrows[playerId].angle = math.atan2(dy, dx)
    while arrowCheck(playerId):
        arrows[playerId].move()
        broadcast("ARROW",(playerId,arrows[playerId].xpos,arrows[playerId].ypos))
        time.sleep(0.01)
    #r emove arrow from game
    arrows.pop(playerId)
    broadcast("ARROW_DONE",playerId)

# set cooldown for arrow
def arrowCooldown(playerId):
    global players
    players[playerId].arrowCd = False
    broadcast("ARROW_READY",playerId)

def increaseXPAll():
    global players
    for k, v in players.items():
        v.increaseXP(100)
        print("{} XP up by 100!".format(k))
        if canLevelUp(k):
            players[k].levelUp()
            print("{} level up!".format(k))
        broadcast("INCREASE_XP", (k, 100))

def endGame():
    global gameState
    gameState = GAME_END
    print("Game has ended...")

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
                    gameTimer = threading.Timer(GAME_DURATION,endGame,[])
                                # Note: HARD CODED TIMER FOR NOW
                    xpAddTimer = threading.Timer(5, increaseXPAll, [])
                    gameTimer.start()
                    xpAddTimer.start()

        elif gameState == GAME_START:
            if(keyword == "PLAYER"):
                playerId, mouse_x, mouse_y = data
                # compute the angle
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
                # initialize arrow
                arrow = Arrow(playerId,players[playerId].xpos,players[playerId].ypos, players[playerId].power, players[playerId].distance, players[playerId].speed)
                # change arrow lists
                arrows[playerId] = arrow
                players[playerId].arrowCd = True
                broadcast("ARROW_ADDED",(playerId,arrow))
                # arrow thread
                aThread = threading.Thread(target=arrowMoving,name="aThread",args=[playerId,mouse_x,mouse_y])
                aThread.start()
                # arrow cooldown
                cdTimer = threading.Timer(ARROW_COOLDOWN,arrowCooldown,[playerId])
                cdTimer.start()
            if(keyword == "LEAP"):
                playerId = data
                players[playerId].leapCd = True
                broadcast("LEAP_CD",playerId)
                lThread = threading.Thread(target=playerLeaping,name="lThread",args=[playerId])
                lThread.start()
                cdTimer = threading.Timer(LEAP_COOLDOWN,leapCooldown,[playerId])
                cdTimer.start()
            if(keyword == "UPGRADE_POWER"):
                # unpack/retrieve data
                playerId = data
                # upgrade this player's arrow power
                players[playerId].power += 1
                players[playerId].upgrades -= 1
                # inform all other clients (including the client holding this player) the upgrade
                broadcast("UPGRADED_POWER", (playerId, players[playerId].power, players[playerId].upgrades))
            if(keyword == "UPGRADE_DISTANCE"):
                # unpack/retrieve data
                playerId = data
                # upgrade this player's arrow distance
                players[playerId].distance += 1
                players[playerId].upgrades -= 1
                # inform all other clients (including the client holding this player) the upgrade
                broadcast("UPGRADED_DISTANCE", (playerId, players[playerId].distance, players[playerId].upgrades))
            if(keyword == "UPGRADE_SPEED"):
                # unpack/retrieve data
                playerId = data
                # upgrade this player's arrow speed
                players[playerId].speed += 1
                players[playerId].upgrades -= 1
                # inform all other clients (including the client holding this player) the upgrade
                broadcast("UPGRADED_SPEED", (playerId, players[playerId].speed, players[playerId].upgrades))

        elif gameState == GAME_END:
            broadcast("GAME_END",players)

receiverThread = threading.Thread(target=receiver, name = "receiveThread", args = [])
receiverThread.start()
print("SERVER START")

        


