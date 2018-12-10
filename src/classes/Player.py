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
        #only for client
        self.deadTime = 0
        self.moveTime = 0
        self.leapTime = 0
        self.idleTime = 0

        
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

    def setAddress(self, address):
        self.address = address

    def setLeapCd(self, leapCd):
        self.leapCd = leapCd

    def setArrowCd(self, arrowCd):
        self.arrowCd = arrowCd

    def setDestX(self, destx):
        self.destx = destx

    def setDestY(self, desty):
        self.desty = desty

    def setAngle(self, angle):
        self.angle = angle

    def decreaseUpgrades(self):
        self.upgrades -= 1

    def setXPos(self, xpos):
        self.xpos = xpos

    def setYPos(self, ypos):
        self.ypos = ypos

    def setHits(self, hits):
        self.hits = hits

    def setUpgrades(self, upgrades):
        self.upgrades = upgrades

    def setHP(self, hp):
        self.hp = hp

    def setXP(self, xp):
        self.xp = xp

    def setPower(self, power):
        self.power = power

    def setDistance(self, distance):
        self.distance = distance

    def setSpeed(self, speed):
        self.speed = speed

    def setMoving(self, moving):
        self.moving = moving

    def setLeaping(self, leaping):
        self.leaping = leaping

    def isMoving(self):
        return self.moving

    def getXP(self):
        return self.xp