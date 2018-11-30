from classes.Player import *
class Arrow:
    def __init__(self,playerId,xpos,ypos,angle, power, distance, speed):
        self.playerId = playerId
        self.arrowId = ''
        self.xpos = xpos
        self.startx = xpos
        self.ypos = ypos
        self.starty = ypos
        self.angle = angle
        self.power = power
        self.distance = distance
        self.speed = speed
    def move(self):
        self.xpos += self.speed * 6 * math.cos(self.angle)
        self.ypos += self.speed * 6 * math.sin(self.angle)