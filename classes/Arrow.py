from math import sqrt
class Arrow:
    def __init__(self,xpos,ypos,angle,maxDist,arrDamage):
        self.xpos = xpos
        self.ypos = ypos
        move(angle,maxDist)
        self.damage = sqrt(2*arrDamage)*35 - 5
    