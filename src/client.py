# disable intro message of pygame
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
try:
   import cPickle as pickle
except:
   import pickle
import math
import socket
import threading
import sys
import select
from pathlib import Path
from classes.Player import *
from classes.Arrow import *
from chat import chat_box

# constants
WAITING         = 0
GAME_START      = 1
GAME_END        = 2

WIDTH = 1200
HEIGHT = 800

# dictionaries
playerId        = -1
players         = {}
arrows          = {}
sounds          = {}

# flags and state identifier
scoreboardActive    = False
leveled_up          = False
connected           = False
arrReady            = False
exited              = False
running             = True
gameState           = WAITING

try:
  server_ip_address = sys.argv[1]
  name = sys.argv[2]
except IndexError:
  print("Correct usage: python3 client.py <server_ip_address> <player_name>")
  raise SystemExit
  

# establish connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (server_ip_address, 10000)

def resolvePath(path):
    return str(Path(path))

def canLevelUp(playerId):
    if players[playerId].getXP() % 100 == 0:
        return True
    return False

def hideLevelUpText():
    global leveled_up
    leveled_up = False

def receiver():
    global exited, leveled_up
    while not exited:
        global connected, playerId, players, arrows, gameState, client_socket
        try:
            data = client_socket.recv(4096)
        except ConnectionRefusedError:
            print("Lost connection to the Server.")
            raise SystemExit
        keyword, data = pickle.loads(data)
        # print(keyword)
        if keyword == "CONNECTED":
            if connected == False:
                playerId = data[0]
                connected = True
            players = data[1]
            print("%s connected. player ID: %i" % (players[data[0]].name, data[0]))
        if keyword == "GAME_START":
            gameState = GAME_START
        if keyword == "MOVING":
            p_id,xpos,ypos,destx,desty = data
            players[p_id].setXPos(xpos)
            players[p_id].setYPos(ypos)
            players[p_id].destx = destx
            players[p_id].desty = desty
            if not players[p_id].moving:
                players[p_id].moveTime = 0
                players[p_id].moving = True
            players[p_id].moveTime +=0.7
        if keyword == "MOVE_DONE":
            p_id = data
            players[p_id].moving = False
            players[p_id].idleTime = 0
        if keyword == "PLAYER_DIED":
            p_id,k_id = data
            players[p_id].increaseKills(1)
            players[k_id].playerDied()
            players[k_id].deadTime = 0
            sounds["ninja-death"].play(0)
        if keyword == "PLAYER_RESPAWNED":
            p_id,xpos,ypos = data
            players[p_id].playerRespawned(xpos,ypos)
            players[p_id].idleTime = 0
        if keyword == "PLAYER_RECOVERED":
            players[data].stunDuration = 0
            players[p_id].idleTime = 0
        if keyword == "ARROW":
            p_id,xpos,ypos = data
            arrows[p_id].setXPos(xpos)
            arrows[p_id].setYPos(ypos)
            arrows[p_id].moveTime+=1
        if keyword == "ARROW_ADDED":
            p_id, arrow = data
            arrows[p_id] = arrow
            players[p_id].setArrowCd(True)
            # play sound effect
            sounds["shuriken-throw"].play(0)
        if keyword == "ARROW_HIT":
            p_id,hits,xp,k_id,hp,stunDuration = data
            players[p_id].setHits(hits)
            players[p_id].setXP(xp)
            if canLevelUp(p_id):
                players[p_id].levelUp()
            players[k_id].setHP(hp)
            players[k_id].setStunDuration(stunDuration)
            # play sound effect
            sounds["shuriken-hit"].play(0)
        if keyword == "ARROW_DONE":
            arrows.pop(data)
        if keyword == "ARROW_READY":
            p_id = data
            players[p_id].setArrowCd(False)
        if keyword == "LEAPING":
            p_id,xpos,ypos = data
            players[p_id].setXPos(xpos)
            players[p_id].setYPos(ypos)
            players[p_id].leaping = True
            players[p_id].leapTime+=1
        if keyword == "LEAP_CD":
            p_id = data
            players[p_id].setLeapCd(True)
        if keyword == "LEAP_READY":
            p_id = data
            players[p_id].setLeapCd(False)
        if keyword == "LEAP_DONE":
            p_id = data
            players[p_id].leaping = False
        if keyword == "GAME_END":
            gameState = GAME_END
        if keyword == "UPGRADED_POWER":
            # unpack/retrieve data
            p_id, power, upgrades = data
            # upgrade this player's arrow power
            players[p_id].setPower(power)
            players[p_id].setUpgrades(upgrades)
            # print for debug
            print(str(p_id) + "upgaded Power: " + str(players[p_id].power))
        if keyword == "UPGRADED_DISTANCE":
            # unpack/retrieve data
            p_id, distance, upgrades = data
            # upgrade this player's arrow distance
            players[p_id].setDistance(distance)
            players[p_id].setUpgrades(upgrades)
            # print for debug
            print(str(p_id) + "upgaded Distance: " + str(players[p_id].distance))
        if keyword == "UPGRADED_SPEED":
            # unpack/retrieve data
            p_id, speed, upgrades = data
            # upgrade this player's arrow speed
            players[p_id].setSpeed(speed)
            players[p_id].setUpgrades(upgrades)
            # print for debug
            print(str(p_id) + "upgraded Speed: " + str(players[p_id].speed))
        if keyword == "INCREASE_XP":
            p_id, xp = data
            players[p_id].setXP(xp)
            if canLevelUp(p_id):
                players[p_id].levelUp()
                print("{} levels up!".format(players[p_id].getName()))
        if keyword == "LEVEL_UP":
            p_id, xp, lvl, upgrades = data
            players[p_id].setXP(xp)
            players[p_id].setLvl(lvl)
            players[p_id].setUpgrades(upgrades)
            if (playerId == p_id):
                leveled_up = True
                level_up_thread = threading.Timer(2, hideLevelUpText, [])
                level_up_thread.start()

client_socket.sendto(pickle.dumps(("CONNECT",name),pickle.HIGHEST_PROTOCOL), server_address)

receiverThread = threading.Thread(target=receiver, name = "receiveThread", args = [])
receiverThread.start()

icon = pygame.image.load(resolvePath("img/icon.png"))

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.display.set_caption("Shuriken Wars")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((WIDTH,HEIGHT),pygame.HWSURFACE)

chat_display = chat_box.Chat_Display( font_size = chat_box.DEF_FONTSIZE )
chat_input   = chat_box.Chat_In( 0, HEIGHT, name, chat_display, font_size = chat_box.DEF_FONTSIZE )

                        
player_sprites  =   [   
                        {
                            "dead":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/1/dead/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                            "idle":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/1/idle/"+str(img)+".png")).convert_alpha(),(60,100)) for img in range(0,10)],
                            "run":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/1/run/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                            "slide":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/1/slide/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                        },
                        {
                            "dead":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/2/dead/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                            "idle":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/2/idle/"+str(img)+".png")).convert_alpha(),(60,100)) for img in range(0,10)],
                            "run":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/2/run/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                            "slide":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/2/slide/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                        },
                        {
                            "dead":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/3/dead/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                            "idle":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/3/idle/"+str(img)+".png")).convert_alpha(),(60,100)) for img in range(0,10)],
                            "run":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/3/run/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                            "slide":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/3/slide/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                        },
                        {
                            "dead":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/4/dead/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                            "idle":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/4/idle/"+str(img)+".png")).convert_alpha(),(60,100)) for img in range(0,10)],
                            "run":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/4/run/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                            "slide":[pygame.transform.scale(pygame.image.load(resolvePath("img/players/4/slide/"+str(img)+".png")).convert_alpha(),(100,100)) for img in range(0,10)],
                        }
                    ]
arrow_sprites   =   [
                        [pygame.transform.scale(pygame.image.load(resolvePath("img/shuriken/"+str(img)+".png")).convert_alpha(),(30,30)) for img in range(0,10)],
                        [pygame.transform.scale(pygame.image.load(resolvePath("img/shuriken/"+str(img)+".png")).convert_alpha(),(30,30)) for img in range(0,10)],
                        [pygame.transform.scale(pygame.image.load(resolvePath("img/shuriken/"+str(img)+".png")).convert_alpha(),(30,30)) for img in range(0,10)],
                        [pygame.transform.scale(pygame.image.load(resolvePath("img/shuriken/"+str(img)+".png")).convert_alpha(),(30,30)) for img in range(0,10)]
                    ]

background = pygame.transform.scale(pygame.image.load(resolvePath("img/bg.png")).convert_alpha(),(WIDTH,HEIGHT))
shurikenActive = pygame.transform.scale(pygame.image.load(resolvePath("img/indicators/shuriken.png")).convert_alpha(),(50,50))
shurikenInactive = pygame.transform.scale(pygame.image.load(resolvePath("img/indicators/shurikenInactive.png")).convert_alpha(),(50,50))
slideActive = pygame.transform.scale(pygame.image.load(resolvePath("img/indicators/slide.png")).convert_alpha(),(50,50))
slideInactive = pygame.transform.scale(pygame.image.load(resolvePath("img/indicators/slideInactive.png")).convert_alpha(),(50,50))

clock = pygame.time.Clock()
chat_box.PYGAME_SCREEN = screen
scoreboardbg = pygame.Surface((WIDTH-400, HEIGHT-200))
scoreboardbg.fill((0,0,0))
# setup in-game music
pygame.mixer.music.load(resolvePath("audio/bgm.mp3"))
pygame.mixer.music.set_volume(0.50)
sounds["shuriken-throw"] = pygame.mixer.Sound(resolvePath("audio/shuriken-throw.ogg"))
sounds["shuriken-hit"] = pygame.mixer.Sound(resolvePath("audio/shuriken-hit.ogg"))
sounds["ninja-death"] = pygame.mixer.Sound(resolvePath("audio/ninja-death.ogg"))

i = 0

while running:
    clock.tick(60)
    if connected:
        if gameState == WAITING:
            screen.fill((0,0,0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    exited = True
                chat_input.handle_event( event )
        if gameState == GAME_START:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    exited = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if players[playerId].dead:
                        print("You are still dead...")
                        break
                    if players[playerId].stunDuration:
                        print("You are still stunned...")
                        break
                    if scoreboardActive:
                        break
                    # left click detected
                    if event.button == 1:
                        if arrReady and not players[playerId].arrowCd:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            client_socket.sendto(pickle.dumps(("ARROW",(playerId,mouse_x,mouse_y)),pickle.HIGHEST_PROTOCOL), server_address)
                            arrReady = False
                    # right click detected
                    if event.button == 3:
                        if arrReady:
                            arrReady = False
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        client_socket.sendto(pickle.dumps(("PLAYER",(playerId,mouse_x,mouse_y)),pickle.HIGHEST_PROTOCOL), server_address)

                elif event.type == pygame.KEYDOWN:
                    if chat_input.chat_mode:
                        chat_input.handle_event( event )
                        break
                    if scoreboardActive:
                        if event.key == pygame.K_TAB:
                            scoreboardActive = False
                            break
                        else:
                            break
                    if event.key == pygame.K_TAB and not scoreboardActive:
                        scoreboardActive = True
                    if players[playerId].dead:
                        print("You are still dead...")
                        break
                    if players[playerId].stunDuration:
                        print("You are still stunned...")
                        break
                    if arrReady and event.key != pygame.K_w:
                        arrReady = False
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_e and not players[playerId].leapCd and not players[playerId].stunDuration:
                        client_socket.sendto(pickle.dumps(("LEAP",playerId),pickle.HIGHEST_PROTOCOL), server_address)
                    elif event.key == pygame.K_s:
                        client_socket.sendto(pickle.dumps(("STOP",playerId),pickle.HIGHEST_PROTOCOL), server_address)
                    elif event.key == pygame.K_w and not players[playerId].stunDuration:
                        arrReady = True
                    if players[playerId].upgrades > 0:
                        if event.key == pygame.K_z:
                            # immediately decrement current upgrade points to avoid spamming
                            players[playerId].decreaseUpgrades()
                            # request upgrade from server
                            client_socket.sendto(pickle.dumps(("UPGRADE_POWER", (playerId)), pickle.HIGHEST_PROTOCOL), server_address)
                        elif event.key == pygame.K_x:
                            players[playerId].decreaseUpgrades()
                            client_socket.sendto(pickle.dumps(("UPGRADE_SPEED", (playerId)), pickle.HIGHEST_PROTOCOL), server_address)
                        elif event.key == pygame.K_c:
                            players[playerId].decreaseUpgrades()
                            client_socket.sendto(pickle.dumps(("UPGRADE_DISTANCE", (playerId)), pickle.HIGHEST_PROTOCOL), server_address)
                    chat_input.handle_event( event )
            # clear screen
            screen.blit(background,(0,0))
            # repaint player sprites
            for k,v in players.items():
                if v.dead:
                    if(v.xpos>v.destx):
                        screen.blit(pygame.transform.flip(player_sprites[k]["dead"][v.deadTime],True,False), (v.xpos-30, v.ypos-50))
                    else:
                        screen.blit(player_sprites[k]["dead"][v.deadTime], (v.xpos-30, v.ypos-50))
                    if(v.deadTime<9):
                        v.deadTime += 1
                    continue
                elif v.stunDuration>0:
                    if(v.xpos>v.destx):
                        screen.blit(pygame.transform.flip(player_sprites[k]["dead"][1],True,False), (v.xpos-30, v.ypos-50))
                    else:
                        screen.blit(player_sprites[k]["dead"][1], (v.xpos-30, v.ypos-50))
                elif v.leaping:
                    if(v.xpos>v.destx):
                        screen.blit(pygame.transform.flip(player_sprites[k]["slide"][v.leapTime%10],True,False), (v.xpos-30, v.ypos-50))
                    else:
                        screen.blit(player_sprites[k]["slide"][v.leapTime%10], (v.xpos-30, v.ypos-50))
                elif v.moving:
                    if(v.xpos>v.destx):
                        screen.blit(pygame.transform.flip(player_sprites[k]["run"][round(v.moveTime)%10],True,False), (v.xpos-30, v.ypos-50))
                    else:
                        screen.blit(player_sprites[k]["run"][round(v.moveTime)%10], (v.xpos-30, v.ypos-50))
                else:
                    if(v.xpos>v.destx):
                        screen.blit(pygame.transform.flip(player_sprites[k]["idle"][round(v.idleTime)%10],True,False), (v.xpos-30, v.ypos-50))
                    else:
                        screen.blit(player_sprites[k]["idle"][round(v.idleTime)%10], (v.xpos-30, v.ypos-50))
                    v.idleTime += 0.5
            # repaint shuriken sprites
            for k,v in arrows.items():
                screen.blit(arrow_sprites[k][v.moveTime%10], (v.xpos-15, v.ypos-15))
            
            # repaint shuriken icon based on its cooldown
            if not players[playerId].arrowCd:
                # colored icon
                screen.blit(shurikenActive, (WIDTH/2-35,HEIGHT-50))
            else:
                # B&W icon
                screen.blit(shurikenInactive, (WIDTH/2-35,HEIGHT-50))

            # repaint slide icon based on its cooldown
            if not players[playerId].leapCd:
                screen.blit(slideActive, (WIDTH/2+35,HEIGHT-50))
            else:
                screen.blit(slideInactive, (WIDTH/2+35,HEIGHT-50))

            if leveled_up:
                screen.blit(pygame.font.Font( None, 48 ).render("You leveled up!",False,pygame.Color( 'white' )),((WIDTH/2)-135, 20))

            # display scoreboard
            if scoreboardActive:
                ite = 1
                screen.blit(scoreboardbg,(200,100))
                screen.blit(pygame.font.Font( None, 72 ).render("NAME",False,pygame.Color( 'white' )),(300,120))
                screen.blit(pygame.font.Font( None, 72 ).render("K/D/H",False,pygame.Color( 'white' )),(750,120))
                for k,v in players.items():
                    screen.blit(pygame.font.Font( None, 72 ).render("%s" % v.name,False,pygame.Color( 'white' )),(300,120+80*ite))
                    screen.blit(pygame.font.Font( None, 72 ).render("%d/%d/%d" % (v.kills, v.deaths, v.hits),False,pygame.Color( 'white' )),(750,120+80*ite))
                    ite += 1

            # display hotkeys for each ability
            screen.blit(pygame.font.Font( None, 32 ).render("W",False,pygame.Color( 'white' )),(WIDTH/2-30,HEIGHT-50))
            screen.blit(pygame.font.Font( None, 32 ).render("E",False,pygame.Color( 'white' )),(WIDTH/2+38,HEIGHT-50))

            # display this player's power, speed, distance, hp
            health = round(players[playerId].getHP())
            if (health < 0):
                health = 0
            screen.blit(pygame.font.Font( None, 20 ).render(("Power: {}".format(players[playerId].getPower())),False,pygame.Color( 'white' )),((WIDTH/2)-200, HEIGHT-50))
            screen.blit(pygame.font.Font( None, 20 ).render(("Speed: {}".format(players[playerId].getSpeed())),False,pygame.Color( 'white' )),((WIDTH/2)-200, HEIGHT-35))
            screen.blit(pygame.font.Font( None, 20 ).render(("Distance: {}".format(players[playerId].getDistance())),False,pygame.Color( 'white' )),((WIDTH/2)-200, HEIGHT-20))
            screen.blit(pygame.font.Font( None, 20 ).render(("Health: {}".format(health)),False,pygame.Color( 'white' )),((WIDTH/2)-115, HEIGHT-50))
            screen.blit(pygame.font.Font( None, 20 ).render(("Upgrades: {}".format(players[playerId].getUpgrades())),False,pygame.Color( 'white' )),((WIDTH/2)-115, HEIGHT-35))

            # display all other players' hp
            h_pos = HEIGHT-50
            for p_id, player in players.items():
                if playerId != p_id:
                    health = round(player.getHP())
                    if (health < 0):
                        health = 0
                    screen.blit(pygame.font.Font( None, 20 ).render(("{} HP: {}".format(player.getName(), health)),False,pygame.Color( 'white' )),((WIDTH/2)+100, h_pos))
                    h_pos += 15

        if gameState == GAME_END:
            screen.blit(background,(0,0))
            ite = 1
            screen.blit(scoreboardbg,(200,100))
            screen.blit(pygame.font.Font( None, 72 ).render("FINAL SCORE",False,pygame.Color( 'white' )),(450,25))
            screen.blit(pygame.font.Font( None, 72 ).render("NAME",False,pygame.Color( 'white' )),(300,120))
            screen.blit(pygame.font.Font( None, 72 ).render("K/D/H",False,pygame.Color( 'white' )),(750,120))
            for k,v in players.items():
                screen.blit(pygame.font.Font( None, 72 ).render("%s" % v.name,False,pygame.Color( 'white' )),(300,120+80*ite))
                screen.blit(pygame.font.Font( None, 72 ).render("%d/%d/%d" % (v.kills, v.deaths, v.hits),False,pygame.Color( 'white' )),(750,120+80*ite))
                ite += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    exited = True
                chat_input.handle_event( event )
            
    chat_input.update_width()
    chat_input.draw_chat_input()
    chat_display.print_buffer()
    pygame.display.flip()
pygame.quit()
sys.exit(0)
