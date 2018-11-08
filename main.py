import pygame
import math

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
w, h = pygame.display.get_surface().get_size()

x, y, dx, dy = w/2,h/2 , 0, 0

player_x, player_y = w/2,h/2 
movespeed = 8
player = pygame.Surface((50, 50))
player.fill((0, 255, 255))

bullet_x, bullet_y = w/2,h/2
bulletspeed = 15
bullet = pygame.Surface((20,20))
bullet.fill((255,0,0))
angle = 0
def moving(mouse_x, mouse_y):
    global x, y, dx, dy, player_x,player_y,bullet_x,bullet_y,angle
    dx = mouse_x - x
    dy = mouse_y - y
    angle = math.atan2(dy, dx)
    player_x += movespeed * math.cos(angle)
    player_y += movespeed * math.sin(angle)
    if not player_shoot:
        bullet_x += movespeed * math.cos(angle)
        bullet_y += movespeed * math.sin(angle)

def shoot(mouse_x, mouse_y):
    global target_x,target_y,dxs,dxy,bullet_x,bullet_y
    dxs = mouse_x - target_x
    dys = mouse_y - target_y
    angle = math.atan2(dys, dxs)
    bullet_x += bulletspeed * math.cos(angle)
    bullet_y += bulletspeed * math.sin(angle)
    
def leaping():
    global player_x, player_y, bullet_x, bullet_y, angle, i
    player_x += 20 * math.cos(angle)
    player_y += 20 * math.sin(angle)
    if not player_shoot:
        bullet_x += 20 * math.cos(angle)
        bullet_y += 20 * math.sin(angle)
    i+=1

player_move = False
player_shoot = False
player_leap = False
prev_x,prev_y = 0,0
i=0
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not player_shoot:
                    target_x,target_y = player_x, player_y
                    player_shoot = True
                    shoot_mouse_x, shoot_mouse_y = pygame.mouse.get_pos()
            elif event.button == 3:
                x,y = player_x,player_y
                player_move = True
                mouse_x, mouse_y = pygame.mouse.get_pos()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_e:
                player_move = False
                player_leap = True
                prev_x,prev_y = player_x, player_y
                i=0
            elif event.key == pygame.K_s:
                player_move = False
                
    if player_move:
        moving(mouse_x, mouse_y)
        if mouse_x-1.0 < player_x < mouse_x+1.0 or mouse_y-1.0 < player_y < mouse_y+1.0:
            player_move = False
            x,y = mouse_x, mouse_y
    if player_shoot:
        shoot(shoot_mouse_x,shoot_mouse_y)
        if -20 > bullet_x or bullet_x > w or -20 > bullet_y or bullet_y > h:
            bullet_x, bullet_y = player_x,player_y
            player_shoot = False
    if player_leap:
        leaping()
        if i==8:
            player_leap = False          
    screen.fill((0, 0, 0))
    screen.blit(player, (player_x-12.5, player_y-12.5))
    screen.blit(bullet, (bullet_x+2.5, bullet_y+2.5))
    pygame.display.update()
