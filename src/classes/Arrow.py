from classes.Player import *
import math
class Arrow:
    def __init__(self,playerId,xpos,ypos, power, distance, speed):
        self.playerId = playerId
        self.arrowId = ''
        self.xpos = xpos
        self.startx = xpos
        self.ypos = ypos
        self.starty = ypos
        self.angle = ''
        self.power = power
        self.distance = distance
        self.speed = speed
        self.moveTime = 0
        
    def move(self):
        self.xpos += math.log(self.speed*10,10) * 6 * math.cos(self.angle)
        self.ypos += math.log(self.speed*10,10) * 6 * math.sin(self.angle)

    def setXPos(self, xpos):
        self.xpos = xpos

    def setYPos(self, ypos):
        self.ypos = ypos

    def getXPos(self):
        return self.xpos

    def getYPos(self):
        return self.ypos

    def getStartX(self):
        return self.startx

    def getStartY(self):
        return self.starty

    def getPower(self):
        return self.power

    def getSpeed(self):
        return self.speed

    def getDistance(self):
        return self.distance