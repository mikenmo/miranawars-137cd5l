import pygame
import math
import socket
import threading
try:
   import cPickle as pickle
except:
   import pickle
import sys
import select
from classes.Player import *
from classes.Arrow import *


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
client_socket.connect(server_address)

arrow = ''

playerId = -1
players = {}
arrows = {}


player_sprite = ''
arrow_sprite = ''
colors=[(255, 0, 0),(0, 255, 0),(0, 0, 255),(0, 255, 255)]
player_sprites = [pygame.Surface((50, 50)),pygame.Surface((50, 50)),pygame.Surface((50, 50)),pygame.Surface((50, 50))]
arrow_sprites = [pygame.Surface((20, 20)),pygame.Surface((20, 20)),pygame.Surface((20, 20)),pygame.Surface((20, 20))]
for i in range(0,4):
    player_sprites[i].fill(colors[i])
    arrow_sprites[i].fill(colors[i])



connected = False
gameStart = False
exited = False
def receiver():
    global exited
    while not exited:
        global connected, playerId, players, arrows, gameStart, client_socket
        data = client_socket.recv(4096)
        keyword, data = pickle.loads(data)
        if keyword == "CONNECTED":
            if connected == False:
                playerId = data[0]
                connected = True
            players = data[1]
            print("%s connected." % players[data[0]].name)
        if keyword == "GAME_START":
            gameStart = True
        if keyword == "PLAYER":
            p_id,xpos,ypos = data
            players[p_id].xpos = xpos
            players[p_id].ypos = ypos
        if keyword == "ARROW":
            p_id,xpos,ypos = data
            arrows[p_id].xpos = xpos
            arrows[p_id].ypos = ypos
        if keyword == "ARROW_ADDED":
            arrows[data[0]] = data[1]
            print(data[0])
            players[data[0]].arrowCd = True
            print(players[data[0]].arrowCd)
        if keyword == "ARROW_DONE":
            arrows.pop(data)
        if keyword == "ARROW_READY":
            players[data].arrowCd = False
    
    
        


pygame.init()
screen = pygame.display.set_mode((500,500),pygame.HWSURFACE)
clock = pygame.time.Clock()
w, h = pygame.display.get_surface().get_size()
player_shoot = False
player_leap = False
running = True
i=0
leapCd = 0
# font = pygame.font.SysFont(None, 25)
# chatbox = pygame.Surface([640,480], pygame.SRCALPHA, 32)
# chatbox = chatbox.convert_alpha()

# def openChatbox():
#     screen_text = font.render(msg,True,(255,255,255))
#     screen.blit(screen_text,)

receiverThread = threading.Thread(target=receiver, name = "receiveThread", args = [])
receiverThread.start()


arrReady = False
client_socket.sendall(pickle.dumps(("CONNECT",input("Enter name: ")),pickle.HIGHEST_PROTOCOL))
while running:
    if connected:
        if gameStart:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exited = True
                    raise SystemExit
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        print(players[playerId].arrowCd)
                        if arrReady and not players[playerId].arrowCd:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            client_socket.sendall(pickle.dumps(("ARROW",(playerId,mouse_x,mouse_y)),pickle.HIGHEST_PROTOCOL))
                            arrReady = False
                    if event.button == 3:
                        if arrReady:
                            arrReady = False
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        print(playerId)
                        client_socket.sendall(pickle.dumps(("PLAYER",(playerId,mouse_x,mouse_y)),pickle.HIGHEST_PROTOCOL))

                elif event.type == pygame.KEYDOWN:
                    if arrReady and event.key != pygame.K_w:
                        arrReady = False
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_e and leapCd==0:
                        leapCd = 500
                        player_move = False
                        player_leap = True
                        i=0
                    elif event.key == pygame.K_s:
                        player_move = False
                    elif event.key == pygame.K_w:
                        arrReady = True
                    
                    # elif event.key == pygame.K_z:
                    #     player.power +=1
                    # elif event.key == pygame.K_x:
                    #     player.distance +=1
                    # elif event.key == pygame.K_c:
                    #     player.speed +=1
                        
            if player_leap:
                player_move = False
                player.leap()
                client_socket.sendall(pickle.dumps(("PLAYER",player),pickle.HIGHEST_PROTOCOL))
                if i==8:
                    player_leap = False
                    i = 0
                i+=1
            screen.fill((0, 0, 0))
            for k,v in players.items():
                screen.blit(player_sprites[k], (v.xpos, v.ypos))
            for k,v in arrows.items():
                screen.blit(arrow_sprites[k], (v.xpos, v.ypos))
    pygame.display.update()
