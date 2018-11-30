import pygame
import math
from classes.Arrow import *

class Player:
    #constants
    POWER = 1
    DISTANCE = 2
    SPEED = 3

    num_players = 0
    def __init__(self,name,xpos,ypos):
        Player.num_players += 1
        self.name = name
        self.id = Player.num_players+1
        self.hp = 100
        self.xp = 0
        self.lvl = 1
        self.upgrades = 1
        self.kills = 0
        self.xpos = xpos
        self.ypos = ypos
        self.angle = 0
        self.ms = 5
        self.power = 1
        self.distance = 1
        self.speed = 1
        #temp
        self.sprite = pygame.Surface((50, 50))
        self.sprite.fill((0, 255, 255))

    def arrowStats(self):
        return({"power":self.power,"distance":self.distance,"speed":self.speed})

    def upgradeArrow(self,upgradeType):
        self.upgrade-=1
        if upgradeType == Arrow.POWER:
            self.arrow.power+=1
        elif upgradeType == Arrow.DISTANCE:
            self.arrow.distance+=1
        elif upgradeType == Arrow.SPEED:
            self.arrow.speed+=1

    def move(self):
        self.xpos += self.ms * math.cos(self.angle)
        self.ypos += self.ms * math.sin(self.angle)

    def leap(self):
        self.xpos += 20 * math.cos(self.angle)
        self.ypos += 20 * math.sin(self.angle)
        