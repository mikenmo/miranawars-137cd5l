import pygame
import math
import socket
import pickle
import sys
import select
from classes.Player import *
from threading import Thread

import chat_window

# initialize chat module
chat_thread = Thread( target=chat_window.main )
chat_thread.start()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
client_socket.connect(server_address)

player = Player(input("Enter name: "),0,0)

player_sprites = {}
player_sprites[0] = pygame.Surface((50, 50))
player_sprites[0].fill((0, 255, 255))

arrow_sprite = pygame.Surface((20,20))
arrow_sprite.fill((255,0,0))



connected = False

def receive(socks):
    global connected, player
    data = socks.recv(4096)
    keyword, data = pickle.loads(data)

    if keyword == "CONNECTED":
        if connected == False:
            player = data
            connected = True
            print(data.id)
    elif keyword == "PLAYER":
        screen.fill((0, 0, 0))
        for k,v in data.items():
            player_sprites[v.id] = pygame.Surface((50, 50))
            player_sprites[v.id].fill((0, 255, 255))
            screen.blit(player_sprites[v.id], (v.xpos-12.5, v.ypos-12.5))
            print(v.id,v.xpos,v.ypos)


pygame.init()
screen = pygame.display.set_mode((500,500),pygame.HWSURFACE)
clock = pygame.time.Clock()
w, h = pygame.display.get_surface().get_size()
player_move = False
player_shoot = False
player_leap = False
running = True

while running:
    if not connected:
        print("Connecting.....")
        client_socket.sendall(pickle.dumps(("CONNECT",player))) 
    if connected:
        i=0
        arrow = ''
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player_shoot = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    #compute the angle
                    dx = mouse_x - player.xpos
                    dy = mouse_y - player.ypos
                    arrow = Arrow(player.id,player.xpos,player.ypos,math.atan2(dy, dx),player.power,player.distance,player.speed)
                if event.button == 3:
                    print('here')
                    player_move = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    #compute the angle
                    dx = mouse_x - player.xpos
                    dy = mouse_y - player.ypos
                    player.angle = math.atan2(dy, dx)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_e:
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
            client_socket.sendall(pickle.dumps(("PLAYER",player)))
            if mouse_x-1.0 < player.xpos < mouse_x+1.0 or mouse_y-1.0 < player.ypos < mouse_y+1.0:
                player_move = False
        if player_shoot:
            arrow.move()
            if -20 > arrow.xpos or arrow.xpos > w or -20 > arrow.ypos or arrow.ypos > h:
                player_shoot = False
                arrow = ''
            elif math.sqrt((arrow.xpos-arrow.startx)**2 + (arrow.ypos-arrow.starty)**2) > arrow.distance*100+500:
                player_shoot = False
                arrow = ''
        if player_leap:
            player.leap()
            client_socket.sendall(pickle.dumps(("PLAYER",player)))
            if i==8:
                player_leap = False
            i+=1        
        
        
        if(arrow!=''):
            screen.blit(arrow_sprite, (arrow.xpos+2.5, arrow.ypos+2.5))
    
    sockets_list = [sys.stdin, client_socket]
    read_sockets, write_socket, error_socket = select.select(sockets_list,[],[],1)
    for socks in read_sockets:
        if socks == client_socket:
            receive(socks)
    pygame.display.update()

pygame.quit()
chat_thread.join()