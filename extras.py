import pygame
import os
import matplotlib as mpl
import numpy as np

filepath = os.getcwd()+"\\Textures\\gameSection\\"
TILESIZE = 25
WIDTH = TILESIZE*40
HEIGHT = TILESIZE*20
WORLDLENGTH=3
WORLDHEIGHT=3

class Spritesheet:
    def __init__(self, filename, scale, colour, width, height):
        self.filename = filename
        self.spriteSheet = pygame.image.load(os.path.expanduser(filepath + filename)).convert_alpha()
        self.scale=scale
        self.colour=colour
        self.width=width
        self.height=height
        
    def getImage(self, frame, right):
        image = pygame.Surface((self.width, self.height)).convert_alpha()
        image.blit(self.spriteSheet,(0,0),((frame*self.width), 0, self.width, self.height))
        image = pygame.transform.scale(image, (int(self.width * self.scale), int(self.height * self.scale)))
        image = pygame. transform. flip(image, right, 0)
        image.set_colorkey(self.colour)
        
        return(image)
    
    
class colourFader:
    def __init__(self):
        self.c1="#060735"#night
        self.c2="#13e0fe" #morning
        self.n=500
        
    def mix(self, mix): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
        c1=np.array(mpl.colors.to_rgb(self.c1))
        c2=np.array(mpl.colors.to_rgb(self.c2))
        
        return mpl.colors.to_hex((1-mix)*c1 + mix*c2)
    
    
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image