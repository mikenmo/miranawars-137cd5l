import math
from classes.Arrow import *

class Player:
    #constants
    POWER = 1
    DISTANCE = 2
    SPEED = 3
    def __init__(self,name,xy):
        self.address = ''
        self.name = name
        self.hp = 100
        self.xp = 0
        self.lvl = 1
        self.upgrades = 1
        self.kills = 0
        self.hits = 0
        self.xpos = xy[0]
        self.ypos = xy[1]
        self.destx = xy[0]
        self.desty = xy[1]
        self.angle = 0
        self.ms = 5
        self.power = 1
        self.distance = 1
        self.speed = 1
        self.arrowCd = False
        self.leapCd = False
        self.moving = False
        self.leaping = False
        self.dead = False
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
        self.xpos += 10 * math.cos(self.angle)
        self.ypos += 10 * math.sin(self.angle)
        