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
PLAYER_SIZE_W           = 60
PLAYER_SIZE_H           = 100
PLAYER_ADJUST_X         = 30
PLAYER_ADJUST_Y         = 50
ARROW_ADJUST_X          = 15
ARROW_ADJUST_Y          = 15
ARROW_SIZE              = 30
WIDTH                   = 1200
HEIGHT                  = 800
GAME_DURATION           = 300 # in seconds
XP_TIMER                = 1
XP_AMOUNT               = 10
RESPAWN_TIME            = 10
ARROW_COOLDOWN          = 3.0
LEAP_COOLDOWN           = 2.5

# dictionaries
players                 = {}
arrows                  = {}

init_pos = [(30,60),(WIDTH-30,HEIGHT-60),(WIDTH-30,60),(30,HEIGHT-60)]

gameState = WAITING_FOR_PLAYERS

# send data to all clients including the sender
def broadcast(keyword, data):
    for k,v in players.items():
        server_socket.sendto(pickle.dumps((keyword,data),pickle.HIGHEST_PROTOCOL),v.getAddress())

# condition to stop player thread
def playerCheck(playerId):
    global players
    if not(players[playerId].getXPos()>players[playerId].getDestX()+50 or players[playerId].getXPos()+PLAYER_SIZE_W<players[playerId].getDestX() or players[playerId].getYPos()>players[playerId].getDestY()+50 or players[playerId].getYPos()+PLAYER_SIZE_H<players[playerId].getDestY()):
        return False
    if players[playerId].leaping:
        return False
    if not players[playerId].moving:
        return False
    # if(0 > plac
    return True

# thread to move player
def playerMoving(playerId):
    global players
    players[playerId].setMoving(True)
    while playerCheck(playerId):
        players[playerId].move()
        broadcast("MOVING",(playerId,players[playerId].getXPos(),players[playerId].getYPos(),players[playerId].getDestX(),players[playerId].getDestY()))
        time.sleep(0.02)
    players[playerId].setMoving(False)
    broadcast("MOVE_DONE",playerId)

def playerLeaping(playerId):
    global players
    players[playerId].setLeaping(True)
    for i in range(0,15):
        players[playerId].leap()
        broadcast("LEAPING",(playerId,players[playerId].getXPos(),players[playerId].getYPos()))
        time.sleep(0.02)
    players[playerId].setLeaping(False)
    broadcast("LEAP_DONE",playerId)
    
def leapCooldown(playerId):
    global players
    players[playerId].setLeapCd(False)
    broadcast("LEAP_READY",playerId)

def playerRespawning(playerId):
    global players
    players[playerId].playerRespawned(init_pos[playerId][0],init_pos[playerId][1])
    print("%s respawned." % (players[playerId].getName()))
    broadcast("PLAYER_RESPAWNED",(playerId,players[playerId].getXPos(),players[playerId].getYPos()))
    
def playerRecovering(playerId):
    global players
    while players[playerId].getStunDuration() > 0:
        print(players[playerId].stunDuration)
        time.sleep(0.01)
        players[playerId].decreaseStunDuration(0.01)
    players[playerId].setStunDuration(0)
    print("%s not stunned anymore." % (players[playerId].getName()))
    broadcast("PLAYER_RECOVERED",(playerId))

def canLevelUp(playerId):
    if players[playerId].getXP() % 100 == 0:
        return True
    return False

# condition to stop arrow thread
def arrowCheck(playerId):
    global players
    travelDistance = math.sqrt((arrows[playerId].getXPos()-arrows[playerId].getStartX())**2 + (arrows[playerId].getYPos()-arrows[playerId].getStartY())**2)
    # check if boundary
    if 0 > arrows[playerId].getXPos() or arrows[playerId].getXPos() > WIDTH or 0 > arrows[playerId].getYPos() or arrows[playerId].getYPos() > HEIGHT:
        return False
    # check if maximum distance
    elif travelDistance > arrows[playerId].getDistance()*125+250:
        return False
    # check if it hits player
    for k,v in players.items():
        if k == playerId or v.isDead() == True:
            continue
        if not (arrows[playerId].xpos-ARROW_ADJUST_X>v.xpos+PLAYER_SIZE_W-PLAYER_ADJUST_X or arrows[playerId].xpos+ARROW_SIZE-ARROW_ADJUST_X<v.xpos-PLAYER_ADJUST_X or arrows[playerId].ypos-ARROW_ADJUST_Y>v.ypos+PLAYER_SIZE_H-PLAYER_ADJUST_Y or arrows[playerId].ypos-ARROW_ADJUST_Y+ARROW_SIZE<v.ypos-PLAYER_ADJUST_Y):
            v.decreaseHP(players[playerId].power * 10)
            if not v.stunDuration:
                v.stunDuration = round(travelDistance/500,2)
                v.moving = False
                print("%s stunned again for %f seconds" % (v.name,v.stunDuration))
                stunTimer = threading.Thread(target = playerRecovering,name = "stunTimer",args = [k])
                stunTimer.start()
            else:
                v.setStunDuration(round(travelDistance/500,2))
                print("%s stunned for %f seconds" % (v.getName(),v.getStunDuration()))
            players[playerId].increaseHits(1)
            players[playerId].increaseXP(20)
            if canLevelUp(playerId):
                players[playerId].levelUp()
            # print for debug
            print("Player %s's arrow hit player %s.\nPlayer %s's hp: %d" % (players[playerId].getName(), v.getName(), v.getName(), v.getHP()))
            # playerId's arrow killed their opponent player
            if(v.getHP() <= 0):
                players[playerId].increaseXP(30)
                if canLevelUp(playerId):
                    players[playerId].levelUp()
                players[playerId].increaseKills(1)
                # print for debug
                print("%s died.\nRespawning in 10 seconds...." % v.getName())
                respawnTimer = threading.Timer(RESPAWN_TIME,playerRespawning,[k])
                respawnTimer.start()
                players[k].playerDied()
                broadcast("PLAYER_DIED",(playerId,k))
            # print for debug
            print("Player "+players[playerId].getName()+" new XP: "+str(players[playerId].getXP()))
            broadcast("ARROW_HIT",(playerId,players[playerId].getHits(),players[playerId].getXP(),k,v.getHP(),v.getStunDuration()))
            return False
    return True 

# thread to move arrow
def arrowMoving(playerId,mouse_x,mouse_y):
    global players,arrows
    # compute the angle
    dx = mouse_x - players[playerId].getXPos()
    dy = mouse_y - players[playerId].getYPos()
    arrows[playerId].angle = math.atan2(dy, dx)
    while arrowCheck(playerId):
        arrows[playerId].move()
        broadcast("ARROW",(playerId,arrows[playerId].getXPos(),arrows[playerId].getYPos()))
        time.sleep(0.01)
    #r emove arrow from game
    arrows.pop(playerId)
    broadcast("ARROW_DONE",playerId)

# set cooldown for arrow
def arrowCooldown(playerId):
    global players
    players[playerId].setArrowCd(False)
    broadcast("ARROW_READY",playerId)

def increaseXPAll():
    global players
    while gameState == GAME_START:
        # give XP_AMOUNT to all players every XP_TIMER second(s)
        time.sleep(XP_TIMER)
        for k, v in players.items():
            # do not give dead players XP
            if v.isDead():
                continue
            v.increaseXP(XP_AMOUNT)
            if canLevelUp(k):
                players[k].levelUp()
                broadcast("LEVEL_UP", (k, v.getXP(), v.getLvl(), v.getUpgrades()))
            else:
                broadcast("INCREASE_XP", (k, XP_AMOUNT))

def endGame():
    global gameState
    gameState = GAME_END
    print("Game has ended...")
    broadcast("GAME_END","")

def receiver():
    while True:
        global players,arrows,gameState
        data, address = server_socket.recvfrom(4096)
        keyword, data = pickle.loads(data)
        if gameState == WAITING_FOR_PLAYERS:
            if(keyword == "CONNECT"):
                playerId = len(players)
                # initialize new Player
                player = Player(data,init_pos[playerId])
                players[playerId] = player
                players[playerId].setAddress(address)
                broadcast("CONNECTED",(playerId,players))
                print('%s connected....' % player.getName())
                if(len(players)==num_players):
                    print("Game State: START")
                    gameState = GAME_START
                    broadcast("GAME_START",'')
                    gameTimer = threading.Timer(GAME_DURATION,endGame,[])
                                # Note: HARD CODED TIMER FOR NOW
                    xpThread = threading.Thread(target=increaseXPAll, name="xpThread", args=[])
                    gameTimer.start()
                    xpThread.start()

        elif gameState == GAME_START:
            if(keyword == "PLAYER"):
                playerId, mouse_x, mouse_y = data
                # compute the angle
                dx = mouse_x - players[playerId].getXPos()
                dy = mouse_y - players[playerId].getYPos()
                players[playerId].setDestX(mouse_x)
                players[playerId].setDestY(mouse_y)
                players[playerId].setAngle(math.atan2(dy, dx))
                if(not players[playerId].isMoving()):
                    pThread = threading.Thread(target=playerMoving,name="pThread",args=[playerId])
                    pThread.start()
            if(keyword == "ARROW"):
                playerId, mouse_x, mouse_y = data
                # initialize arrow
                arrow = Arrow(playerId,players[playerId].getXPos(),players[playerId].getYPos(), players[playerId].getPower(), players[playerId].getDistance(), players[playerId].getSpeed())
                # change arrow lists
                arrows[playerId] = arrow
                players[playerId].setArrowCd(True)
                broadcast("ARROW_ADDED",(playerId,arrow))
                # arrow thread
                aThread = threading.Thread(target=arrowMoving,name="aThread",args=[playerId,mouse_x,mouse_y])
                aThread.start()
                # arrow cooldown
                cdTimer = threading.Timer(ARROW_COOLDOWN,arrowCooldown,[playerId])
                cdTimer.start()
            if(keyword == "LEAP"):
                playerId = data
                players[playerId].setLeapCd(True)
                broadcast("LEAP_CD",playerId)
                lThread = threading.Thread(target=playerLeaping,name="lThread",args=[playerId])
                lThread.start()
                cdTimer = threading.Timer(LEAP_COOLDOWN,leapCooldown,[playerId])
                cdTimer.start()
            if(keyword == "STOP"):
                playerId = data
                players[playerId].setMoving(False)

            if(keyword == "UPGRADE_POWER"):
                # unpack/retrieve data
                playerId = data
                # upgrade this player's arrow power
                players[playerId].upgradePower()
                players[playerId].decreaseUpgrades()
                # inform all other clients (including the client holding this player) the upgrade
                broadcast("UPGRADED_POWER", (playerId, players[playerId].getPower(), players[playerId].getUpgrades()))
            if(keyword == "UPGRADE_DISTANCE"):
                # unpack/retrieve data
                playerId = data
                # upgrade this player's arrow distance
                players[playerId].upgradeDistance()
                players[playerId].decreaseUpgrades()
                # inform all other clients (including the client holding this player) the upgrade
                broadcast("UPGRADED_DISTANCE", (playerId, players[playerId].getDistance(), players[playerId].getUpgrades()))
            if(keyword == "UPGRADE_SPEED"):
                # unpack/retrieve data
                playerId = data
                # upgrade this player's arrow speed
                players[playerId].upgradeSpeed()
                players[playerId].decreaseUpgrades()
                # inform all other clients (including the client holding this player) the upgrade
                broadcast("UPGRADED_SPEED", (playerId, players[playerId].getSpeed(), players[playerId].getUpgrades()))

        elif gameState == GAME_END:
            broadcast("GAME_END",players)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('', 10000)
server_socket.bind(server_address)

# show host ip address
print("Hosting at {}".format(server_address[0]))

try:
    num_players=int(sys.argv[1])
except IndexError:
    print("Correct usage: python3 server.py <num_of_players>")
    raise SystemExit

receiverThread = threading.Thread(target=receiver, name = "receiveThread", args = [])
receiverThread.start()
print("SERVER START")

        


