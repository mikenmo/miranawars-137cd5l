class Arrow:
    def __init__(self,ownerId,xpos,ypos):
        self.ownerId = ownerId
        self.xpos = xpos
        self.ypos = ypos
        self.sprite = pygame.Surface((20,20))
        self.sprite.fill((255,0,0))