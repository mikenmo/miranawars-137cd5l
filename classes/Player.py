
class Mirana:
    def __init__(self,playerName):
        self.xpos = random.randInt()
        self.ypos = random.randInt()
        #insert checker if conflicts
        self.playerName = playerName
        self.hp = 100
        self.xp = 0
        self.level = 1
        self.arrDamage = 1
        self.arrSpeed = 1
        self.arrRange = 1