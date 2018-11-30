import pygame
import math
import socket
import select
import pickle
from classes.Player import *


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 10000)
client_socket.connect(server_address)

player = Player(input("Enter name: "),0,0)

player_sprite = pygame.Surface((50, 50))
player_sprite.fill((255, 255, 255))

arrow_sprite = pygame.Surface((20,20))
arrow_sprite.fill((255,0,0))

connected = False
keyword = ''
while True:
    if not connected and keyword == 'CONNECTED':
        connected = True
        keyword = ''
        print("Connected.....")
    elif not connected:
        print("Connecting.....")
        client_socket.sendto(pickle.dumps(("CONNECT",player)), server_address)
        data = client_socket.recv(4096)
        keyword, player = pickle.loads(data)
    elif connected:
        pygame.init()
        screen = pygame.display.set_mode((500,500),pygame.HWSURFACE)
        clock = pygame.time.Clock()
        w, h = pygame.display.get_surface().get_size()
        screen.blit(player_sprite, (0, 0))
        player_move = False
        player_shoot = False
        player_leap = False
        i=0
        arrow = ''
        running = True

        sockets = [ client_socket ]
        
        while running:
            clock.tick(60)
            print("here")
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
                client_socket.sendto(pickle.dumps(("PLAYER",player)), server_address)

                if mouse_x-1.0 < player.xpos < mouse_x+1.0 or mouse_y-1.0 < player.ypos < mouse_y+1.0:
                    player_move = False

            if player_leap:
                player.leap()
                client_socket.sendto(pickle.dumps(("PLAYER",player)), server_address)
                
                if i==8:
                    player_leap = False
                i+=1        

            if player_shoot:
                arrow.move()
                if -20 > arrow.xpos or arrow.xpos > w or -20 > arrow.ypos or arrow.ypos > h:
                    player_shoot = False
                    arrow = ''
                elif math.sqrt((arrow.xpos-arrow.startx)**2 + (arrow.ypos-arrow.starty)**2) > arrow.distance*100+500:
                    player_shoot = False
                    arrow = ''

            screen.fill((0, 0, 0))

            read, write, err = select.select( sockets, [], [], 0.1 )

            for socks in read:
                if socks == client_socket:
                    if player_move or player_leap:
                        data = socks.recv(4096)
                        keyword, players = pickle.loads(data)
                        for k,v in players.items():
                                screen.blit(player_sprite, (v.xpos-12.5, v.ypos-12.5))
            if(arrow!=''):
                screen.blit(arrow_sprite, (arrow.xpos+2.5, arrow.ypos+2.5))

            pygame.display.update()
