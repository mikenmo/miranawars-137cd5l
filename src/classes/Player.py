import math
import threading
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
        self.deaths = 0
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
        self.stunDuration = 0
        
    def arrowStats(self):
        return({"power":self.power,"distance":self.distance,"speed":self.speed})

    def upgradePower(self):
        self.power += 1

    def upgradeDistance(self):
        self.distance += 1

    def upgradeSpeed(self):
        self.speed += 1

    def move(self):
        self.xpos += self.ms * math.cos(self.angle)
        self.ypos += self.ms * math.sin(self.angle)

    def leap(self):
        self.xpos += 15 * math.cos(self.angle)
        self.ypos += 15 * math.sin(self.angle)
        
    def increaseXP(self, xp):
        self.xp += xp

    def increaseHits(self, hits):
        self.hits += hits

    def increaseKills(self, kills):
        self.kills += kills

    def levelUp(self):
        self.upgrades += 1

    def decreaseHP(self, hp):
        self.hp -= hp

    def playerDied(self):
        self.deaths += 1
        self.dead = True
    
    def playerRespawned(self,xpos,ypos):
        self.xpos = xpos
        self.ypos = ypos
        self.hp = 100
        self.dead = False