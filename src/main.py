import pygame
import math
import socket
try:
   import cPickle as pickle
except:
   import pickle
import sys
import select
import json
from classes.Player import *

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
client_socket.connect(server_address)

player = Player(input("Enter name: "),0,0)
arrow = ''
player_sprite = ''
arrow_sprite = ''
colors=[(255, 0, 0),(0, 255, 0),(0, 0, 255),(0, 255, 255)]
player_sprites = [pygame.Surface((50, 50)),pygame.Surface((50, 50)),pygame.Surface((50, 50)),pygame.Surface((50, 50))]
arrow_sprites = [pygame.Surface((20, 20)),pygame.Surface((20, 20)),pygame.Surface((20, 20)),pygame.Surface((20, 20))]
for i in range(0,4):
    player_sprites[i].fill(colors[i])
    arrow_sprites[i].fill(colors[i])

connected = False

def receive(socks):
    global connected, player
    data = socks.recv(4096)
    keyword, data = pickle.loads(data)
    if keyword == "CONNECTED":
        if connected == False:
            player = data
            connected = True
    elif keyword == "ARROW_HIT":
        player_shoot = False
    elif keyword == "GAME_STATE":
        screen.fill((0, 0, 0))
        players,arrows = data
        for i in players:
            screen.blit(player_sprites[i[0]], (i[1], i[2]))
        for i in arrows:
            screen.blit(arrow_sprites[i[0]], (i[1], i[2]))


pygame.init()
screen = pygame.display.set_mode((500,500),pygame.HWSURFACE)
clock = pygame.time.Clock()
w, h = pygame.display.get_surface().get_size()
player_move = False
player_shoot = False
player_leap = False
running = True
i=0
arrowCd = 0
leapCd = 0
while running:
    sockets_list = [sys.stdin, client_socket]
    read_sockets, write_socket, error_socket = select.select(sockets_list,[],[],0.001)
    for socks in read_sockets:
        if socks == client_socket:
            receive(socks)

    if not connected:
        print("Connecting.....")
        client_socket.sendall(pickle.dumps(("CONNECT",player),pickle.HIGHEST_PROTOCOL)) 
    if connected: 
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and arrowCd == 0:
                    arrowCd = 250
                    player_shoot = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    #compute the angle
                    dx = mouse_x - player.xpos
                    dy = mouse_y - player.ypos
                    arrow = Arrow(player.id,player.xpos,player.ypos,math.atan2(dy, dx),player.power,player.distance,player.speed)
                    client_socket.sendall(pickle.dumps(("ARROW",arrow),pickle.HIGHEST_PROTOCOL))
                if event.button == 3:
                    player_move = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    #compute the angle
                    dx = mouse_x - player.xpos
                    dy = mouse_y - player.ypos
                    player.angle = math.atan2(dy, dx)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_e and leapCd==0:
                    leapCd = 500
                    player_move = False
                    player_leap = True
                    i=0
                elif event.key == pygame.K_s:
                    player_move = False
                elif event.key == pygame.K_z:
                    player.power +=1
                elif event.key == pygame.K_x:
                    player.distance +=1
                elif event.key == pygame.K_c:
                    player.speed +=1
                    
        if player_move:
            player.move()
            client_socket.sendall(pickle.dumps(("PLAYER",player),pickle.HIGHEST_PROTOCOL))
            if mouse_x-1.0 < player.xpos < mouse_x+1.0 or mouse_y-1.0 < player.ypos < mouse_y+1.0:
                player_move = False
        if player_shoot:
            arrow.move()
            client_socket.sendall(pickle.dumps(("ARROW_MOVE",arrow),pickle.HIGHEST_PROTOCOL))
            if -20 > arrow.xpos or arrow.xpos > w or -20 > arrow.ypos or arrow.ypos > h:
                client_socket.sendall(pickle.dumps(("ARROW_END",arrow.playerId)))
                player_shoot = False
            elif math.sqrt((arrow.xpos-arrow.startx)**2 + (arrow.ypos-arrow.starty)**2) > arrow.distance*100+500:
                client_socket.sendall(pickle.dumps(("ARROW_END",arrow.playerId),pickle.HIGHEST_PROTOCOL))
                player_shoot = False
        if player_leap:
            player_move = False
            player.leap()
            client_socket.sendall(pickle.dumps(("PLAYER",player),pickle.HIGHEST_PROTOCOL))
            if i==8:
                player_leap = False
                i = 0
            i+=1
        if(arrowCd!=0):
            arrowCd-=1
        if(leapCd!=0):
            leapCd-=1
        
    pygame.display.update()
