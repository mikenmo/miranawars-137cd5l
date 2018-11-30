import pygame
import math
from classes.Player import *

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
clock = pygame.time.Clock()
w, h = pygame.display.get_surface().get_size()

player = Player("kenneth",w/2,h/2)
x,y = w/2,h/2

# x, y, dx, dy = w/2,h/2 , 0, 0

# bulletspeed = 15

# def shoot(mouse_x, mouse_y):
#     global target_x,target_y,dxs,dxy,bullet_x,bullet_y
#     dxs = mouse_x - target_x
#     dys = mouse_y - target_y
#     angle = math.atan2(dys, dxs)
#     bullet_x += bulletspeed * math.cos(angle)
#     bullet_y += bulletspeed * math.sin(angle)
    
# def leaping():
#     global player_x, player_y, bullet_x, bullet_y, angle, i
#     player_x += 20 * math.cos(angle)
#     player_y += 20 * math.sin(angle)
#     if not player_shoot:
#         bullet_x += 20 * math.cos(angle)
#         bullet_y += 20 * math.sin(angle)
#     i+=1

player_move = False
player_shoot = False
player_leap = False
running = True
i=0
arrow = ''
while running:
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
        if mouse_x-1.0 < player.xpos < mouse_x+1.0 or mouse_y-1.0 < player.ypos < mouse_y+1.0:
            player_move = False
            x,y = mouse_x, mouse_y
    if player_shoot:
        arrow.move()
        if -20 > arrow.xpos or arrow.xpos > w or -20 > arrow.ypos or arrow.ypos > h:
            arrow.xpos, arrow.ypos = player_x,player_y
            player_shoot = False
        if math.sqrt((arrow.xpos-arrow.startx)**2 + (arrow.ypos-arrow.starty)**2) > arrow.distance*100+500:
            player_shoot = False
            arrow = ''
    if player_leap:
        player.leap()
        if i==8:
            player_leap = False
        i+=1        
    screen.fill((0, 0, 0))
    screen.blit(player.sprite, (player.xpos-12.5, player.ypos-12.5))
    if(arrow!=''):
        screen.blit(arrow.sprite, (arrow.xpos+2.5, arrow.ypos+2.5))
    pygame.display.update()
