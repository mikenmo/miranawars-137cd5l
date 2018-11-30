# -*- coding: utf-8 -*-
"""
Desc: Game Classes
@author: Patricia Jo Fortes
"""

class Player:
  def __init__(self, ID, name,xpos,ypos):
    #info
    self.name = name
    self.ID = ID
    #stats
    self.num_arrows = 20
    self.health = 50
    self.expLevel = 10
    self.kills = 0
    #movement
    self.xpos = xpos
    self.ypos = ypos
    self.speed = 2
    

class Arrow:
    def __init__(self):
        self.power = 5
        self.range = 8
        self.speed = 2
        self.xpos = 0
        self.ypos = 0
        
class Trees:
    def __init__(self,xpos,ypos):
        self.xpos = xpos
        self.ypos = ypos
        
class Rocks:
    def __init__(self,xpos,ypos):
        self.xpos = xpos
        self.ypos = ypos

class Playfield:
    def __init__(self,players=[],trees = [], rocks = []):
        #list of players, trees and rocks
        self.players = players
        self.trees = trees
        self.rocks = rocks
    
    
