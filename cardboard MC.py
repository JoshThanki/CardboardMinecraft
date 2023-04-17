import pygame
import os
import sys
from time import time
import datetime
import random
from pygame.locals import *
from math import*
import json
from extras import *

filepathG = os.getcwd()+"\\Textures\\gameSection\\"
filepathM = os.getcwd()+"\\Textures\\Menu\\"
filepathW = os.getcwd()+"\\Worlds\\"
filepathJ = os.getcwd()+"\\Config\\"

TILESIZE = 25
WIDTH = TILESIZE*40
HEIGHT = TILESIZE*20
WORLDLENGTH=3
WORLDHEIGHT=3

pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode([1000, 500])
pygame.display.set_caption("Cardboard Minecraft")

#game fuction
def game(screen, worldName="New World", difficulty="Normal", prevTime=0):
    
    class Game:
        def __init__(self, screen, worldName, difficulty, prevTime):
            pygame.init()
            #initialise variables
            self.clock = pygame.time.Clock()
            self.screen = screen
            self.worldName=worldName
            self.difficulty=difficulty
            self.time=self.startTime=prevTime
            self.timeStopped=False
            
            self.noclip=True if self.difficulty == "Creative" else False

            self.tick=0
            self.timePeriod=60*10
            self.colorFader=colourFader()
            self.font = pygame.font.SysFont("AndyBold",28)
            
            #load spritesheets
            self.load()
            
            #def sprite groups
            self.hudSprites = HudGroup(self)
            self.camSprites = CameraGroup(self)
            self.personSprites = CameraGroup(self)
            self.backSprites = CameraGroup(self)
            self.backgroundSprites = pygame.sprite.Group()
            self.colSprites = pygame.sprite.Group() # sprites that collide with the player
            self.itemSprites = pygame.sprite.Group()
            self.treeSprites = pygame.sprite.Group()
            self.wallSprites = pygame.sprite.Group()
            self.tileSprites = pygame.sprite.Group()
            self.enemySprites = pygame.sprite.Group()
            
            #try to load the world
            self.loadWorld()
            
            #load player
            self.player = Player(self, *self.playerPos, self.playerInventory, *self.playerHealth)
            
            #darkness
            for block in self.colSprites:          
                self.updateDarkness(block)
            
            #load healthbar
            self.healthBar=HealthBar(self, 700, 50, 2, self.player.maxHealth, self.player.health)
            
            #load inventory objects 
            self.hand=None
            self.inv=Inventory(self)
            
            #start time
            self.FPS = FPS
            self.prevTime = time()
            self.initTime = time()
            self.dt = 0
        
        def load(self):
            #loading the blocks
            blockSheet=Spritesheet("blocks.png", 1, (0,0,0), 25, 25)
            self.blockImageDict=dict()
            self.blockStatDict=dict()
            
            with open(os.path.expanduser(f"{filepathJ}blocks.json")) as f:
                data=json.load(f)
                
            self.blockStatDict=data
            
            for index, block in enumerate(self.blockStatDict.keys()):
                self.blockImageDict[block]=blockSheet.getImage(index, 0)

            #loading the tools
            toolSheet=Spritesheet("tools.png", 1, (0,0,0), 50, 50)
            self.toolImageDict=dict()
            self.toolStatDict=dict()
            
            with open(os.path.expanduser(f"{filepathJ}tools.json")) as f:
                data=json.load(f)
                
            self.toolStatDict=data

            for index, tool in enumerate(data.keys()):
                self.toolImageDict[tool]=toolSheet.getImage(index, 0)



            #loading background
            backSheet=Spritesheet("background.png", 1, (0,0,0), 25, 25)
            backList=["dirt","stone"]
            self.backImageDict=dict()
            
            for index, back in enumerate(backList):
                self.backImageDict[back]=backSheet.getImage(index, 0)
                
                
                
            #loading walls
            wallSheet=Spritesheet("walls.png", 1, (0,0,0), 25, 25)
            wallList=["wood wall", "copper wall", "tin wall", "lead wall", "tungsten wall", "platinum wall", "mithril wall", "adamantite wall", "uru wall"]
            self.wallImageDict=dict()
            
            for index, wall in enumerate(wallList):
                self.wallImageDict[wall]=wallSheet.getImage(index, 0)
            
            
            
            #loading materials
            materialSheet=Spritesheet("materials.png", 1, (0,0,0), 30, 24)
            materialList=["copper bar","tin bar","lead bar","tungsten bar","platinum bar","mithril bar","adamantite bar","uru bar"]
            self.materialImageDict=dict()
            
            for index, material in enumerate(materialList):
                self.materialImageDict[material]=materialSheet.getImage(index, 0)
            
            
            
            #loading tiles
            tileSheet=Spritesheet("tiles.png", 1, (0,0,0), 50, 50)
            tileList=["crafting bench", "anvil", "furnace", "chest"]
            self.tileImageDict=dict()
            
            for index, tile in enumerate(tileList):
                self.tileImageDict[tile]=tileSheet.getImage(index, 0)
                

            self.itemImageDict={**self.toolImageDict, **self.blockImageDict,  **self.wallImageDict, **self.materialImageDict, **self.tileImageDict}
            
        def saveWorld(self):
            with open(os.path.expanduser(f"{filepathW}{self.worldName}.json"), "w") as file:
                #take all the thing i need to save the instance of the world: world name, difficulty, timeplayed, player pos,health,inv, all the object positions
                save={
                    "Name":self.worldName,
                    "TimePlayed":self.time,
                    "Difficulty":self.difficulty,
                    "Inventory":self.player.inventory,
                    "Health": (self.player.health, self.player.maxHealth),
                    "Position": (self.player.rect.x//TILESIZE, self.player.rect.y//TILESIZE),
                    "backDict":{obj:[self.backDict[obj].x,self.backDict[obj].y,self.backDict[obj].name] for obj in self.backDict},
                    "gridDict":{obj:[self.gridDict[obj].x,self.gridDict[obj].y,self.gridDict[obj].name] for obj in self.gridDict},
                    "wallDict":{obj:[self.wallDict[obj].x,self.wallDict[obj].y,self.wallDict[obj].name] for obj in self.wallDict},
                    "treeList":[(obj.x,obj.y) for obj in self.treeSprites]
                }
                json.dump(save, file)
                
        def loadWorld(self):
            try:
                with open(os.path.expanduser(f"{filepathW}{self.worldName}.json")) as file:
                    save = json.load(file)
                    #load from json dictionary
                    self.playerInventory=save["Inventory"]
                    self.playerHealth=save["Health"]
                    self.playerPos=save["Position"]
                    backDict=save["backDict"]
                    gridDict=save["gridDict"]
                    wallDict=save["wallDict"]
                    treeList=save["treeList"]
                    
                    self.backDict = dict()
                    self.gridDict = dict()
                    self.wallDict = dict()
                    
                    #for each key in the dictionary I am accessing the dictionary at that key which gives me the list I need to pass into the intialisation for each object
                    
                    for sp in backDict:
                        sp=backDict[sp]
                        Background(self, sp[0], sp[1], sp[2])
                
                    for sp in gridDict:
                        sp=gridDict[sp]
                        
                        if sp[2] in self.blockImageDict:
                            Block(self, sp[0], sp[1], sp[2])
                        elif sp[2] in self.tileImageDict:
                            Tile(self, sp[0], sp[1], sp[2])
                            
                    for sp in wallDict:
                        sp=wallDict[sp]
                        
                        Wall(self, sp[0], sp[1], sp[2])
                        
                    for sp in treeList:
                        Tree(self, sp[0], sp[1])
                
                
                #delete overlapping sprites
                pygame.sprite.groupcollide(self.colSprites, self.backgroundSprites, False, True)
                pygame.sprite.groupcollide(self.colSprites, self.wallSprites, False, True)
                pygame.sprite.groupcollide(self.wallSprites, self.backgroundSprites, False, True)
                
            except:
                #if loading fails
                self.makeWorld()
                self.makePlayer()
        
        def makePlayer(self):
            
            #intialises the player inventory, health and postion. Also gives starting gear
            self.playerInventory=[[i,"empty",0] for i in range(43)]
            
            startingGear=["copper sword", "copper pickaxe", "copper axe", "copper hammer"]
            
            for index, tool in enumerate(startingGear):
                self.playerInventory[index]=[index, tool, 1]
                
            self.playerHealth=(100,100)
            self.playerPos = (20 , 0)
                
                
        def makeWorld(self):
            #FLOORMAP maps the blocks
            #BACKMAP maps the background
            self.FLOORMAP = [["" for row in range(WORLDLENGTH*WIDTH//25)] for column in range(WORLDHEIGHT*HEIGHT//25)]
            self.BACKMAP = [["" for row in range(WORLDLENGTH*WIDTH//25)] for column in range(WORLDHEIGHT*HEIGHT//25)]
            
            #intialise the 3 tile dictionaries
            self.backDict = dict()
            self.gridDict = dict()
            self.wallDict = dict()
            
            #dirt to stone 1:2 ratio
            for i,row in enumerate(self.FLOORMAP):
                for j,col in enumerate(row):
                    if i<((20*WORLDHEIGHT)//3):
                        self.FLOORMAP[i][j]="dirt"
                        self.BACKMAP[i][j]="dirt"
                    else:
                        self.FLOORMAP[i][j]="stone"
                        self.BACKMAP[i][j]="stone"
            
            #draw the random ore veins
            self.squiggle((2,3,3), (8,2), (6,1), (10,5), (10,1), (2,1), (5,2), "stone") #stone
            self.squiggle((2,3,3), (6,2), (2,1), (10,5), (10,25), (3,2), (10,2), "dirt")#dirt
            self.squiggle((2,3,3), (8,2), (6,1), (10,2), (10,10), (2,1), (2,1), "copper")#copper
            self.squiggle((2,3,3), (6,2), (6,1), (10,2), (10,10), (2,1), (2,1), "tin")#tin
            self.squiggle((1,2,3), (8,2), (6,1), (10,2), (10,10), (2,1), (2,1), "lead")#lead
            self.squiggle((1,2,2), (4,2), (6,1), (10,5), (10,25), (2,1), (2,1), "tungsten")#tungsten
            self.squiggle((1,2,2), (4,1), (4,1), (10,5), (10,35), (2,1), (2,1), "platinum")#tungsten
            self.squiggle((1,2), (4,1), (2,1), (10,5), (10,40), (2,1), (2,1), "mithril")#mithril
            
            self.squiggle((2,3,4), (6,2), (2,1), (10,5), (10,10), (5,2), (5,2), "air")#caves
             #adamantium and uru are not found naturally, found by killing skeleton/zombie
            
            #make the top section air
            for i,row in enumerate(self.FLOORMAP):
                for j,col in enumerate(row):
                    if i<((5*WORLDHEIGHT)//3):
                        self.FLOORMAP[i][j]="air"
                        self.BACKMAP[i][j]=None
                        
    #         self.drawGrass((0,7),(1,random.uniform(0,0.5)),(1,random.uniform(0.5,1)),(1.5,random.uniform(5,6)),(1,random.uniform(5,10)),(1,random.uniform(2,3)))
            self.drawGrass((0,7),(1,random.uniform(0,0.1)),(1,random.uniform(0,0.1)),(1.5,random.uniform(0,0.1)),(1,random.uniform(0,0.1)),(1,random.uniform(0,0.1)))
            
            for j,row in enumerate(self.FLOORMAP):
                for i,col in enumerate(row):
                    try:
                        if self.FLOORMAP[j][i]=="dirt" and self.FLOORMAP[j-1][i]=="air":
                            self.FLOORMAP[j][i]="grass"
                    except:
                        pass
            
            
            #world layered with bedrock and blocks are placed where there is no air (empty space)
            for j,row in enumerate(self.FLOORMAP):
                for i,col in enumerate(row):

                    if i==((WORLDLENGTH*1000)//TILESIZE-1) or i==0 or j==((WORLDHEIGHT*500)//TILESIZE-1):
                        Block(self, i , j, "bedrock")
                        
                    elif self.FLOORMAP[j][i] != "air":
                        Block(self, i, j, self.FLOORMAP[j][i])
                        
            #background is made from the backmap
            for j,row in enumerate(self.FLOORMAP):
                for i,col in enumerate(row):
                    if self.BACKMAP[j][i]:
                        Background(self, i, j, self.BACKMAP[j][i])
                
            #if blocks collide with background then kill the backgrounds
            pygame.sprite.groupcollide(self.colSprites, self.backgroundSprites, False, True)
            
            #trees
            for sprite in self.colSprites:
                if sprite.name=="grass":
                    x=sprite.rect.x
                    y=sprite.rect.top
                    
                    #spawn tree ontop of grass
                    tree=Tree(self,x,y)
                    #kill tree if it colldies with blocks
                    if pygame.sprite.spritecollideany(tree, self.colSprites):
                        if tree:
                            tree.kill()
                            tree=None
                    else:
                        #kill other trees around that tree and respawn the tree in
                        pygame.sprite.spritecollide(tree, self.treeSprites, True)
                        tree=Tree(self,x,y)
                    
                    #kill trees are random to get a random effect
                    if random.uniform(0,1)<=0.3:
                        if tree:
                            tree.kill()
                            tree=None
                        
            
        #takes worldPos as a parameter and draws a certain block at a certain magnitude around a cetain point like a brush does
        def brushDraw(self, pos, brush, fill):
            rectCorner=(pos[0]-(brush-1),pos[1]-(brush-1))
            for x in range(brush*2-1):
                for y in range(brush*2-1):
                     testPos=(rectCorner[0]+x,rectCorner[1]+y)
                     distance=pygame.math.Vector2()
                     distance[0]=testPos[0]-pos[0]
                     distance[1]=testPos[1]-pos[1]
                     
                     if distance.magnitude() <= (brush-1):
                        try:
                            self.FLOORMAP[int(testPos[1])][int(testPos[0])]=fill
                        except:
                            pass
                    
        #only world pos
        def squiggle (self, brushChoice, numberOnX, numberOnY, posRange, initPos, widthRange, depthRange, fill):
                    # self  (3,4,5), (n, range),(n, range),(xRange,yRange), (x,y),  (w, range), (d, range), (block)
                
            #random number of ore veins
            xNum=numberOnX[0]+random.randint(-numberOnX[1],numberOnX[1])
            yNum=numberOnY[0]+random.randint(-numberOnY[1],numberOnY[1])
            
            #random offset for the starting pos of ore veins
            xOffset=((WORLDLENGTH*1000//TILESIZE) - initPos[0]) // xNum
            yOffset=((WORLDHEIGHT*500//TILESIZE) - initPos[1]) // yNum
            
            #decide the the random pos
            for x in range(xNum):
                for y in range(yNum):
                    pos=(initPos[0]+x*(xOffset)+random.randint(-posRange[0],posRange[0]),initPos[1]+y*(yOffset)+random.randint(-posRange[1],posRange[1]))
                    #decide whether to go left or right
                    left = random.uniform(0,1)<=0.5
                    brush = random.choice(brushChoice)
                    
                    #draw that vein instance
                    self.drawSquiggle(pos, widthRange, depthRange, left, brush, fill)
                    
                    
        
        #draw vein instance                        
        def drawSquiggle(self, pos, widthRange, depthRange, left, brush, fill):
            for depth in range(depthRange[0]+random.randint(-depthRange[1],depthRange[1])):
                for width in range(widthRange[0]+random.randint(-widthRange[1],widthRange[1])):
                    #draw using brush around block
                    self.brushDraw(pos, brush, fill)
                    
                    side = random.uniform(0,1)<=0.5
                    #choose whether to go to the side or diagnoally down
                    
                    #based on these choices choose the next postion
                    if left:
                        pos = (pos[0]-1,pos[1]) if side else (pos[0]-1,pos[1]+1)
                    else:
                        pos = (pos[0]+1,pos[1]) if side else (pos[0]+1,pos[1]+1)

                left = not(left)
        
        
        #draw the grass by superposing 5 random sine functions 
        def drawGrass(self, initPos, sine1, sine2, sine3, sin4, sin5):
            for x in range(initPos[0], ((WORLDLENGTH*1000)//25)):
                y=round((sine1[0]*sin(2*pi*sine1[1]*x))+(sine2[0]*sin(2*pi*sine2[1]*x))+(sine3[0]*sin(2*pi*sine3[1]*x))+(sin4[0]*sin(2*pi*sin4[1]*x))+(sin5[0]*sin(2*pi*sin5[1]*x)))+initPos[1]
                self.brushDraw((x,y), 3, "dirt")
        
        
        #grow a single tree by using the logic the same as earlier
        def growTree(self):
            for sprite in self.colSprites:
                if sprite.name=="grass" and self.calcDistanceSP(sprite, self.player) > 600:
                    x=sprite.rect.x
                    y=sprite.rect.top
                    
                    tree=Tree(self,x,y)
                    if pygame.sprite.spritecollideany(tree, self.colSprites):
                        if tree:
                            tree.kill()
                            tree=None
                        
                    else:
                        pygame.sprite.spritecollide(tree, self.treeSprites, True)
                        tree=Tree(self,x,y)

                    break
        
        #if there is empty space above a dirt block then it turns into a grass block
        def growGrass(self):
            for sprite in self.colSprites:
                try:
                    if sprite.name=="dirt" and self.gridDict[str((sprite.x,sprite.y-1))]=="air" and self.calcDistanceSP(sprite, self.player) > 300:
                        self.gridDict[(sprite.x,sprite.y)]==Block(self,sprite.x,sprite.y,"grass")
                        sprite.kill()
                except:
                    pass

        #spawn a single enemy depending on the time of day 
        def spawnEnemy(self):
            enemyDay=[Slime]
            enemyNight=[Zombie,Skeleton]
            
            if self.lux <0.3:
                enemy=random.choice(enemyNight)(self, self.player.rect.x//TILESIZE+random.randint(20,32) * (-1 if random.uniform(0,1) <=0.5 else 1), 0)
            else:
                enemy=random.choice(enemyDay)(self, self.player.rect.x//TILESIZE+random.randint(20,32) * (-1 if random.uniform(0,1) <=0.5 else 1), 0)
                
                      
        def events(self):
            
            for event in pygame.event.get():

                #save word on quit
                if event.type == pygame.QUIT:
                    self.saveWorld()
                    menu(self.screen)
                 
                #on keypress 
                if event.type==KEYDOWN:
                    #if a num key is pressed 
                    if event.key in [K_1,K_2,K_3,K_4,K_5,K_6,K_7,K_8,K_9,K_0]:
                        #change the hotbar selection
                        self.inv.changeSelected(event.key-49)
                        
                    #jump
                    if self.player.grounded and event.key == K_SPACE and not self.noclip:
                        self.player.vel.y = -self.player.jumpSpeed
                        self.player.grounded = False
                    
                    #toggle the inventory and refresh crafting
                    if event.key == K_ESCAPE:
                        self.inv.toggleInv()
                        
                        if self.inv.inventoryVisible:
                            self.inv.updateCrafting()

                if event.type==MOUSEBUTTONDOWN:
                    #use a tool/weapon/item/place a block
                    if not self.hudEvent(event):
                        if event.button==1:
                            self.player.use(event)
                   
                   #scroll the hotbar selection
                    if event.button==4:
                        self.inv.scroll(0)
                    
                    if event.button==5:
                        self.inv.scroll(1)
                        
                        
                        
                        
        def hudEvent(self, event):
            hudClicked=False
            if event.button==1:
                #if you left click on a inventory object
                for sp in self.hudSprites:
                    if sp.rect.collidepoint(event.pos):
                        
                        if sp.__class__.__name__=="invUnit":
                            hudClicked=True
                            
                            #if that object is an empty unit
                            if sp.itemName=="empty":
                                #and you are holding something in hand 
                                if self.hand:
                                    self.player.invChange(sp.index, self.hand.itemName, self.hand.itemCount)
                                    self.hand.kill()
                                    self.hand=None
                                    #deposit
                                    
                            else:
                                #if the object is not an empty unit
                                if self.hand:
                                    #and you are holding something in hand 
                                    if self.hand.itemName==sp.itemName:
                                        #if it is an item of the same name then try to combine the items
                                        if self.player.invChange(sp.index, self.hand.itemName, self.hand.itemCount+sp.itemCount):
                                            self.hand.kill()
                                            self.hand=None
                                        else:
                                            #if this is not possible then try to fill the inv slot as much as possible
                                            if sp.itemCount==32:
                                                #if the inventory slot is full then swap your hand and inv slot
                                                self.player.invChange(sp.index, self.hand.itemName, self.hand.itemCount)
                                                self.hand.kill()
                                                self.hand=Hand(self, sp)
                                            else:
                                                sp.itemCount=self.hand.itemCount+sp.itemCount - self.player.maxItemCount
                                                self.player.invChange(sp.index, self.hand.itemName, self.player.maxItemCount)
                                                self.hand.kill()
                                                self.hand=Hand(self, sp)
                                    
                                    #otherwise swap hand and inv slot
                                    else:
                                        self.player.invChange(sp.index, self.hand.itemName, self.hand.itemCount)
                                        self.hand.kill()
                                        self.hand=Hand(self, sp)
                                        
                                #otherwise pick everything to hand
                                else:
                                    self.player.invChange(sp.index,"empty",0)
                                    self.hand=Hand(self, sp)
                                    
                        elif sp.__class__.__name__=="craftUnit":
                            hudClicked=True
                            #if instead you left click on the crafting menu and you click on a non empty cell then it will allow you to craft said item
                            if sp.itemName=="empty":
                                pass
                            
                            else:
                                self.player.craft(sp.itemName)
                                        
                #place item back where it was found                                  
                if hudClicked==False and self.hand:
                    intialCount=self.player.inventory[self.hand.index][2]
                    self.player.invChange(self.hand.index,self.hand.itemName,intialCount+self.hand.itemCount)
                    self.hand.kill()
                    self.hand=None
                    hudClicked=True

            #right click on inventory
            if event.button==3:
                hudClicked=False
                for sp in self.hudSprites:
                    if sp.rect.collidepoint(event.pos):
                        if sp.__class__.__name__=="invUnit":
                            hudClicked=True
                            #if you right click on empty unit 
                            if sp.itemName=="empty":
                                
                                if self.hand:
                                    self.player.invChange(sp.index,self.hand.itemName,1)
                                    self.hand.decrement()
                                    #drop one item into the unit from hand
                                    
                            elif self.hand:
                                #still drop a unit
                                if self.hand.itemName==sp.itemName:
                                    sp.itemCount+=1
                                    self.player.invChange(sp.index,sp.itemName,sp.itemCount)
                                    self.hand.decrement()
                                    
                                else:
                                    #swap 
                                    self.player.invChange(sp.index,self.hand.itemName,self.hand.itemCount)
                                    self.hand.kill()
                                    self.hand=Hand(self, sp)

                            else:
                                #pick up an item
                                sp.itemCount-=1
                                self.player.invChange(sp.index,sp.itemName,sp.itemCount)
                                sp.itemCount=1
                                self.hand=Hand(self, sp)
                                
                        #no nothing for crafting       
                        elif sp.__class__.__name__=="craftUnit":
                            hudClicked=True
                
                #drop item on right click
                if hudClicked==False and self.hand:
                    for item in range(self.hand.itemCount):
                        Item(self, self.hand.rect.x-self.off[0], self.hand.rect.y-self.off[1], self.hand.itemName)
                    self.hand.kill()
                    self.hand=None
                    hudClicked=True

                    
            return hudClicked 
        #damage a block if there is a block at mouse Pos and it is within the players range     
        def destroyBlock(self, event, tool):
            pos = event.pos - self.off
            worldPos = (pos[0] //TILESIZE,pos[1] //TILESIZE)

            if self.calcDistance(pos, self.player) < self.player.range:
                for sp in self.colSprites:
                    if (sp.x,sp.y) == worldPos:
                        sp.damage(tool.power) 
                        break
                    
        #damage a tree if there is a block at mouse Pos and it is within the players range  
        def destroyTree(self, event, tool):
            pos = event.pos - self.off
            worldPos = (pos[0] //TILESIZE,pos[1] //TILESIZE)
        
            if self.calcDistance(pos, self.player) < self.player.range:
                for sp in self.treeSprites:
                    posInMask=(pos[0] - sp.rect.x, pos[1] - sp.rect.y)
                    if sp.rect.collidepoint(pos) and sp.mask.get_at((int(posInMask[0]),int(posInMask[1]))):
                        sp.damage(tool.power)
                        
                        break
                    
        #damage a wall if there is a block at mouse Pos and it is within the players range  
        def destroyWall(self, event, tool):
            pos = event.pos - self.off
            worldPos = (pos[0] //TILESIZE,pos[1] //TILESIZE)
        
            if self.calcDistance(pos, self.player) < self.player.range:
                for sp in self.wallSprites:
                    if sp.rect.collidepoint(pos):
                        sp.damage(tool.power)
                            
                        break
        
        #place a tile if there is a non solid block at mouse Pos (or no block) and it is within the players range
        #decrement inventory if you place a block
        def place(self, event):
            pos = event.pos - self.off
            worldPos = (pos[0] //TILESIZE,pos[1] //TILESIZE)
            
            colliding=False
            for sprite in self.colSprites:
                if sprite.rect.collidepoint(pos):
                    colliding=True
            
            for sprite in self.treeSprites:
                if sprite.rect.collidepoint(pos):
                    colliding=True
            
            if self.calcDistance(pos, self.player) < self.player.range and not colliding:
                accessed=False
                unit=self.player.inventory[self.player.selectedIndex]
                
                if unit[1] in self.blockImageDict.keys():
                    Block(self,*worldPos,unit[1])
                    
                    if str((worldPos[0],worldPos[1])) in self.wallDict:
                        self.wallDict[str((worldPos[0],worldPos[1]))].kill
                        
                    elif str((worldPos[0],worldPos[1])) in self.backDict:
                        self.backDict[str((worldPos[0],worldPos[1]))].kill
                            
                    accessed=True
                
                elif unit[1] in self.wallImageDict.keys():
                    Wall(self, *worldPos, unit[1])
                    
                    if str((worldPos[0],worldPos[1])) in self.backDict:
                        self.backDict[str((worldPos[0],worldPos[1]))].kill
                        
                    accessed=True
                
                elif unit[1] in self.tileImageDict.keys():
                    
                    Tile(self,worldPos[0],worldPos[1]-1, unit[1])
                    
                    accessed=True
            
            
                if accessed:
                    unit[2]-=1
                    self.player.invChange(*unit)
                
                
                
        #calculates the distance between a sprite and mouse position
        def calcDistance(self, position, sprite):
            distance=pygame.math.Vector2()
            distance[0]=(position[0])-(sprite.rect.centerx)
            distance[1]=(position[1])-(sprite.rect.centery)
            return distance.magnitude()
        
        #calculates the distance between a sprite and another sprite
        def calcDistanceSP(self, sprite1, sprite2):
            distance=pygame.math.Vector2()
            distance[0]=(sprite1.rect.centerx)-(sprite2.rect.centerx)
            distance[1]=(sprite1.rect.centery)-(sprite2.rect.centery)
            
            return distance.magnitude()
            
        #update
        def update(self):
            #update the time
            self.time = time() - self.initTime +  self.startTime
            #update the colour of the sky
            self.lux=0.5*cos((2*pi)/self.timePeriod*self.time)+0.5
            # if there are too few trees then grow one
            if len(self.treeSprites) < 3:
                self.growTree()
            
            #on tick grow trees/grass/enemy
            if self.tick==0:
                self.tick=500
                self.growTree()
                self.growGrass()
                if len(self.enemySprites)<3:
                    self.spawnEnemy()
                    
            if self.difficulty != "Casual" and self.tick==250 and len(self.enemySprites)<3:
                print("spawmn")
                self.spawnEnemy()
                
            #decrement tick
            self.tick-=1

            #update the HUD
            self.healthBar.displayMessage()
            if self.hand:
                self.hand.update()
            if self.player.healthChange:
                self.healthBar.update(self.player.health, self.player.maxHealth)
                self.player.healthChange=False
            if self.player.inventoryChange:
                self.inv.update(self.player.inventory)
                self.player.inventoryChange=False
            
            #update the camera sprite groups
            ...
            self.camSprites.update()
            self.personSprites.update()
            self.backSprites.update()
            
            
            #update the FPS and delta time
            self.clock.tick(self.FPS)
            now = time()
            self.dt = now - self.prevTime
            self.prevTime = now
        
        
        #fill find all blocks in a 5 block radius and call update darkness
        def updateDarknessAR(self, block):
            brush=5
            pos=(block.x,block.y)
            rectCorner=(pos[0]-(brush-1),pos[1]-(brush-1))
            for x in range(brush*2-1):
                for y in range(brush*2-1):
                     testPos=(rectCorner[0]+x,rectCorner[1]+y)
                     distance=pygame.math.Vector2()
                     distance[0]=testPos[0]-pos[0]
                     distance[1]=testPos[1]-pos[1]
                         
                     if distance.magnitude() <= (brush-1) and str((testPos[0],testPos[1])) in self.gridDict:
                         self.updateDarkness(self.gridDict[str((testPos[0],testPos[1]))])
                                

        #will determine the level of darkness that a block needs by the number of other blocks around it.
        def updateDarkness(self, block):
            if block:
            
                spaceFound=False
                brush=1
                pos=(block.x,block.y)
                while not spaceFound and brush < 5:
                    brush+=1
                    rectCorner=(pos[0]-(brush-1),pos[1]-(brush-1))
                    for x in range(brush*2-1):
                        for y in range(brush*2-1):
                             testPos=(rectCorner[0]+x,rectCorner[1]+y)
                             distance=pygame.math.Vector2()
                             distance[0]=testPos[0]-pos[0]
                             distance[1]=testPos[1]-pos[1]
                             
                             if (brush-2) < distance.magnitude() <= (brush-1):
                                 if str((testPos[0],testPos[1])) in self.gridDict:
                                     if self.gridDict[str((testPos[0],testPos[1]))].name=="bedrock":
                                         brush=5
                                 else:
                                     spaceFound=True

                block.updateDarkness((brush-2))
                                

            
        def draw(self):
            ...
            #draw the sprite grroups
            self.screen.fill(self.colorFader.mix(self.lux))
            self.backSprites.customDraw()
            self.camSprites.customDraw()
            self.personSprites.customDraw()
            self.hudSprites.customDraw()
            

            #draw the FPS
            text = self.font.render("FPS: "+str(self.clock.get_fps())[:5],1,(255, 226, 18))
            self.screen.blit(text, (700,20))


            #update the display
            pygame.display.update()

        def main(self):  # this is the main game loop
            while True:
                self.events()
                self.update()
                self.draw()
    
    #hand class which is for holding items temeporarily when you need to shift items around the inventory
    class Hand(pygame.sprite.Sprite):
        def __init__(self, game, sprite):
            pos = pygame.mouse.get_pos()
            self.game=game
            self.groups = self.game.hudSprites
            pygame.sprite.Sprite.__init__(self, self.groups)
            #intialise groups
            
            #takes on characteristics of invUnit
            self.index=sprite.index
            self.itemName=sprite.itemName
            self.itemCount=sprite.itemCount
            self.itemImage=self.game.itemImageDict[self.itemName]
            
            #adusts the size of the image so it fits within 25x25
            sizeChange=False
            size=self.itemImage.get_size()
            sfx=1
            sfy=1
            if size[0] > TILESIZE:
                sfx=size[0]//TILESIZE
                sizeChange=True
            if size[1] > TILESIZE:
                sfy=size[1]//TILESIZE
                sizeChange=True
            
            
            if sizeChange:
                sf=max(sfy,sfx)
                self.itemImage=pygame.transform.scale(self.itemImage, (size[0]//sf, size[1]//sf))
                self.itemImage.set_colorkey((0,0,0))
                
                
            #blit the item image and item count to surface
            self.image=pygame.Surface((50,50)).convert_alpha()
            self.image.set_colorkey((0,0,0))
            self.image.blit(self.itemImage, (10,10))
            self.image.blit(self.game.font.render(str(self.itemCount), 1, (255,255,255)).convert_alpha(), (10,35))
            
            #rect
            self.rect=self.image.get_rect()
            self.rect.x=pos[0]
            self.rect.y=pos[1]
            
        def update(self):
            #stick it to the mouse position
            pos = pygame.mouse.get_pos()
            self.rect.x=pos[0]
            self.rect.y=pos[1]
            
        def decrement(self):
            #decrease item count by one and update image
            self.itemCount-=1
            self.image=pygame.Surface((50,50)).convert_alpha()
            self.image.set_colorkey((0,0,0))
            self.image.blit(self.itemImage, (10,10))
            self.image.blit(self.game.font.render(str(self.itemCount), 1, (255,255,255)).convert_alpha(), (10,35))
            if self.itemCount==0:
                self.game.hand.kill()
                self.game.hand=None
            
    #will blit text for a small amount of time - is used as an interrupt message  
    class Text(pygame.sprite.Sprite):
        def __init__(self, game, text, x, y):
            self.game = game
            self.groups = (self.game.hudSprites)
            pygame.sprite.Sprite.__init__(self, self.groups)
            self.text=text
            
            self.image=self.game.font.render(str(self.text), 1, (255,226,18)).convert_alpha()
            self.rect=self.image.get_rect()
            self.rect.x=x*TILESIZE
            self.rect.y=y*TILESIZE
    
    #healthbar hud class
    class HealthBar(pygame.sprite.Sprite):
        def __init__(self, game, x, y, scale, maxHealth, health):
            self.game = game
            self.groups = (self.game.hudSprites)
            pygame.sprite.Sprite.__init__(self, self.groups)
            
            self.colour=(0,0,0)
            self.scale=scale
            #load the maxHealth and health
            self.maxHealth=maxHealth
            self.health=health
            #load the images from sprite sheet
            self.healthSheet=Spritesheet("health.png", self.scale, self.colour, 26, 24)
            self.healthList=[self.healthSheet.getImage(i, 0) for i in range(21)]
            self.healthMessage=None
            
            #print onto surface while enlarging it to scale
            self.image=pygame.Surface(((self.maxHealth/20)*26*self.scale, 24*self.scale)).convert_alpha()
            self.image.set_colorkey(self.colour)
            self.rect=self.image.get_rect()
            self.rect.x=x
            self.rect.y=y
            #call update
            self.updateHealth()
        
        #passes player health into the HUD for update 
        def update(self, health, maxHealth):
            self.health=health
            self.maxHealth=maxHealth
            
            self.updateHealth()
        
        #displays exact health if you hover over the rect
        def displayMessage(self):
            pos = pygame.mouse.get_pos()
            
            if self.rect.collidepoint(pos):
                if self.healthMessage:
                    self.healthMessage.kill()
                    
                self.healthMessage=Text(self.game, f"{str(int(self.health))}/{str(self.maxHealth)}", pos[0]+20, pos[1]+10)
                
            else:
                if self.healthMessage:
                    self.healthMessage.kill()
                    
        #updates the number of hearts in the health bar key
        def updateHealth(self):
            health=int(self.health)
                
            for i in range(int(self.maxHealth/20)):
                if health>=20:
                    heart=20
                    health-=20
                elif health>0:
                    heart=health
                    health=0
                else:
                    heart=0
                    
                self.image.blit(self.healthList[heart], (26*i*self.scale, 0, 26*self.scale,24*self.scale))
            
            
            
    #inventory unit      
    class invUnit(pygame.sprite.Sprite):
        def __init__(self, game, index, x, y):
            self.game = game
            self.groups = (self.game.hudSprites)
            pygame.sprite.Sprite.__init__(self, self.groups)
            
            #loads base and selected image
            self.invBase=pygame.image.load(os.path.expanduser(filepathG + "invunit.png")).convert_alpha()
            self.invSelected=pygame.image.load(os.path.expanduser(filepathG + "invunitSelected.png")).convert_alpha()
            self.font = pygame.font.SysFont("AndyBold",30)
            
            #loads image/rect and position
            self.selected=False
            self.image = pygame.Surface((50,50)).convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            
            #starts as an empty unit
            self.index=index
            self.itemName="empty"
            self.itemCount=0
        
        #function to allow hotbar selected to change
        def updateStatus(self, selected):
            self.selected=selected
        
        #allows the invUnit to change 
        def changeItem(self, index, item, count):
            self.index=index
            self.itemName=item
            self.itemCount=count
        
        #draw the inventory unit 
        def draw(self):
            self.game.hudSprites.add(self)        
            self.image = pygame.Surface((50,50)).convert_alpha()
            self.image.set_colorkey((0,0,0))
            self.image.blit((self.invSelected if self.selected else self.invBase), (0,0))
            self.image.blit(self.font.render(str(self.index+1), 1, (255,255,255)).convert_alpha(), (0,0))
            
            if self.itemCount > 0:
                image=self.game.itemImageDict[self.itemName]
                #transform the scale so it fits
                size=self.image.get_size()
                if size[0] > TILESIZE:
                    sfx=size[0]//TILESIZE
                if size[1] > TILESIZE:
                    sfy=size[1]//TILESIZE
                sf=max(sfy,sfx)
                image=pygame.transform.scale(image, (size[0]//sf, size[1]//sf))
                image.set_colorkey((0,0,0))
                
                #blit the item image on the inventory unit
                self.image.blit(image, (10,10))
                self.image.blit(self.font.render(str(self.itemCount), 1, (255,255,255)).convert_alpha(), (10,35))
        
        #clear that unit
        def clear(self):
            self.kill()
            
        def __str__(self):
                return [self.index,self.itemName,self.itemCount]
    
    #crafting unit
    class craftUnit(pygame.sprite.Sprite):
        def __init__(self, game, index, x, y):
            #init group and call inheritance
            self.game = game
            self.groups = (self.game.hudSprites)
            pygame.sprite.Sprite.__init__(self, self.groups)
            
            #init image
            self.unit=pygame.image.load(os.path.expanduser(filepathG + "craftunit.png")).convert_alpha()
            self.font = pygame.font.SysFont("AndyBold",30)
            
            self.image = pygame.Surface((50,50)).convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            
            #empty unit
            self.index=index
            self.itemName="empty"
            self.itemCount=0
            
        #allow for changing  
        def changeItem(self, index, item, count):
            self.index=index
            self.itemName=item
            self.itemCount=count
            
        #draw to the crafting unit   
        def draw(self):
            self.game.hudSprites.add(self)        
            self.image = pygame.Surface((50,50)).convert_alpha()
            self.image.set_colorkey((0,0,0))
            self.image.blit((self.unit), (0,0))
            self.image.blit(self.font.render(str(self.index+1), 1, (255,255,255)).convert_alpha(), (0,0))
            
            if self.itemCount > 0:
                image=self.game.itemImageDict[self.itemName]
                #tranform scale
                size=self.image.get_size()
                if size[0] > TILESIZE:
                    sfx=size[0]//TILESIZE
                if size[1] > TILESIZE:
                    sfy=size[1]//TILESIZE
                sf=max(sfy,sfx)
                image=pygame.transform.scale(image, (size[0]//sf, size[1]//sf))
                image.set_colorkey((0,0,0))
                
                self.image.blit(image, (10,10))
                self.image.blit(self.font.render(str(self.itemCount), 1, (255,255,255)).convert_alpha(), (10,35))
                
        def clear(self):
            self.kill()
            
        def __str__(self):
                return f"{self.index}, {self.itemName} , {self.itemCount}"
            
         
    class Inventory(pygame.sprite.Sprite):
        def __init__(self, game):
            self.game = game
            #create hotbar 
            self.hotbar=[invUnit(game, i, 5+60*i, 50) for i in range(10)]
            self.hotbar[0].selected=True
            
            #create the storage and armour sections
            self.storage=[invUnit(game, i+10, 5+60*(i%10), 150 + 60*(i//10)) for i in range(30)]
            self.armour=[invUnit(game, i+40, 800, 150 + 60*i) for i in range(3)]
            self.inventory=self.storage+self.armour
            #create the crafting section
            self.crafting=[craftUnit(game, i, 5+60*(i%15), 350 + 60*(i//15)) for i in range(30)]
            self.inventoryVisible=False
            
            #load the recipe dictionary
            self.recipeDict=dict()
            with open(os.path.expanduser(f"{filepathJ}recipe.json")) as f:
                data=json.load(f)
                
            self.recipeDict=data

            self.draw()
            
    #     def updateHotbar(self):
    #         self.hotbarImage=pygame.Surface(590, 50).convert_alpha()
    #         for item in self.hotbar:
    #             item.draw()
    #             self.hotbarImage.blit(item.image, (item.rect.x, item.rect.y))
         
        # if esc pressed and inventory closed then open it, if the inventory is open then close it
        def toggleInv(self):
            if self.inventoryVisible:
                self.inventoryVisible=False
            else:
                self.inventoryVisible=True
                
            self.draw()
                    
        #scroll the hotbar up and down, making sure it wraps around the edge by using %
        def scroll(self, up):
            for index, item in enumerate(self.hotbar):
                if item.selected:
                    item.selected=False
                    if up:
                        newIndex=(index+1)%len(self.hotbar)
                        self.hotbar[newIndex].selected=True
                    else:
                        newIndex=(index-1)%len(self.hotbar)
                        self.hotbar[newIndex].selected=True
                        
                    self.game.player.selectedIndex=newIndex
                    break
                
            self.draw()
           
        #changes what hotbar index is selected by using the num keys 
        def changeSelected(self, key):
            for i in range(len(self.hotbar)):
                self.hotbar[i].selected=False
                
            self.hotbar[key].selected=True
            
            self.game.player.selectedIndex=key
            
            self.draw()
            
        
        #passes the player invetory in the inventory HUD 
        def update(self, playerInv):
            
            #the first 10 are hotbar units the last 30 are storage units
            for unit in playerInv:
                if unit[0]<10:
                    self.hotbar[unit[0]].changeItem(unit[0],unit[1],unit[2])
                    
                elif unit[0]<40:
                    self.inventory[unit[0]-10].changeItem(unit[0],unit[1],unit[2])
        
            self.draw()
            
        #updates the crafting menu on refresh
        def updateCrafting(self):
            self.clearCrafting()
            
            #depending on what tile a player is colliding with
            if self.game.player.touching:
                self.tile=self.game.player.touching
                
            else:
                self.tile="nothing"
             
            #accesses the recipeDict from the json file and looks under the tile which the player is colliding with
            for key in self.recipeDict[self.tile]:
                #for every recipe which is in this part of the dictionary 
                ingList=list(self.recipeDict[self.tile][key].keys())
                itemCounts=[]
                #gets the list of ingredients and the list of the amound of those ingredients
                for ing in ingList:
                    materialCount=0
                    for unit in self.game.player.inventory:
                        if ing==unit[1]:
                            materialCount+=unit[2]
                    
                    #rounds up all of the relevant matrials
                    itemCounts.append(materialCount//self.recipeDict[self.tile][key][ing])
    #                     break
                #if in creative ignore material costs
                if self.game.difficulty !="Creative":
                    numItems=min(itemCounts)
                    if numItems>=1:    
                        self.addRecipe(key,numItems)
                        
                #add the recipe to the crafting menu depending on the number of items the player can make
                else:
                    self.addRecipe(key,float("inf"))  
                    
                
            #update the inventory     
            self.draw()
        
        #adds the recipe to the crafting menu if more than 1 can be made
        def addRecipe(self,key,numItems):
            for unit in self.crafting:
                if unit.itemCount==0:
                    self.crafting[unit.index].changeItem(unit.index,key,numItems)
                    break
                    
        #clears the crafting window          
        def clearCrafting(self):
            for unit in self.crafting:
                self.crafting[unit.index].changeItem(unit.index,"empty",0)
        
        #redrwas all of the units in the inventory
        def draw(self):
            if self.inventoryVisible:
                for item in self.inventory:
                    item.draw()
                for item in self.crafting:
                    item.draw()
            else:
                for item in self.inventory:
                    item.clear()
                for item in self.crafting:
                    item.clear()
                    
            for item in self.hotbar:
                item.draw()
    
    #tool class
    class Tool(pygame.sprite.Sprite):
        def __init__(self, game, tool):
            self.game=game
            self.groups = (self.game.camSprites)
            pygame.sprite.Sprite.__init__(self, self.groups)
            
            #intialises the sprites hit as none
            self.spritesHit=[]
            #gets the tool name
            self.tool=tool
            #gets the image and reverse image of the tool
            
            self.initImage=self.game.toolImageDict[self.tool]
            self.reverseImage=pygame.transform.flip(self.initImage, True, False)
            
            #gets the stats of tool from dictionary
            self.speed=self.game.toolStatDict[self.tool]["speed"]
            self.damage=self.game.toolStatDict[self.tool]["damage"]
            self.type=self.game.toolStatDict[self.tool]["type"]
            self.power=self.game.toolStatDict[self.tool]["power"]
            
            #if the tool is a high level sword then allow it to shoot projectiles
            if self.tool.split(" ")[1]=="sword" and self.tool.split(" ")[0] in ["mithril", "adamantite", "uru"]:
                Fireball(self.game, self.game.player.rect.x, self.game.player.rect.y, -500 if self.game.player.lookingLeft else 500, 0, True, self.power)
            
            #init image/rect and position
            self.image=pygame.Surface((50,50)).convert_alpha()
            self.image.set_colorkey((0,0,0))
            self.mask=pygame.mask.from_surface(self.image)
            self.rect=self.image.get_rect()
            self.center=self.game.player.rect.center
            
                
        def updateFrame(self, frame, left):
            self.center=self.game.player.rect.center
            
            #stick the tool onto the player using animation, depending on whether the player is facing right or left 
            if left:
                if frame==1:
                    self.image=pygame.transform.rotate(self.reverseImage, 0).convert_alpha()
                    self.rect.center=(self.center[0]-30, self.center[1]-35)
                    self.mask=pygame.mask.from_surface(self.image)
                if frame==2:
                    self.image=pygame.transform.rotate(self.reverseImage, 30).convert_alpha()
                    self.rect.center=(self.center[0]-50, self.center[1]-20)
                    self.mask=pygame.mask.from_surface(self.image)
                if frame==3:
                    self.image=pygame.transform.rotate(self.reverseImage, 50).convert_alpha()
                    self.rect.center=(self.center[0]-50, self.center[1]+2)
                    self.mask=pygame.mask.from_surface(self.image)
                if frame==4:
                    self.image=pygame.transform.rotate(self.reverseImage, 80).convert_alpha()
                    self.rect.center=(self.center[0]-37, self.center[1]+30)
                    self.mask=pygame.mask.from_surface(self.image)
            
            else:
                if frame==1:
                    self.image=pygame.transform.rotate(self.initImage, -5).convert_alpha()
                    self.rect.center=(self.center[0]+30, self.center[0]-35)
                    self.mask=pygame.mask.from_surface(self.image)
                if frame==2:
                    self.image=pygame.transform.rotate(self.initImage, -35).convert_alpha()
                    self.rect.center=(self.center[0]+30, self.center[1]-17)
                    self.mask=pygame.mask.from_surface(self.image)
                if frame==3:
                    self.image=pygame.transform.rotate(self.initImage, -50).convert_alpha()
                    self.rect.center=(self.center[0]+30, self.center[1]+1)
                    self.mask=pygame.mask.from_surface(self.image)
                if frame==4:
                    self.image=pygame.transform.rotate(self.initImage, -70).convert_alpha()
                    self.rect.center=(self.center[0]+25, self.center[1]+20)
                    self.mask=pygame.mask.from_surface(self.image)
                    
            self.checkCollision()
        
        #check a collision between the tool and enemySprites, if there is one then deal damage to that enemy based on the tools damage and knock the enemy back based on which direction the player is looking
        def checkCollision(self):
            hits = pygame.sprite.spritecollide(self, self.game.enemySprites, False)
            for hit in hits:
                if hit not in self.spritesHit:
                    
                    if self.game.player.lookingLeft:
                        hit.takeDamage(self.damage, "left")
                    else:
                        hit.takeDamage(self.damage, "right")
                        
                    self.spritesHit.append(hit)
    
    #player
    class Player(pygame.sprite.Sprite):
        def __init__(self, game, x, y, inventory, health, maxHealth): # this x,y coord is a world coord (not pixels)
            self.game = game
            self.groups = (self.game.personSprites)
            pygame.sprite.Sprite.__init__(self, self.groups)
            
            #initialise constants and variables 
            self.vel = pygame.math.Vector2()
            
            if self.game.noclip:
                self.speed=1000
            else:
                self.speed = 200
            
        
            self.jumpSpeed=800 
            self.grav = 2500  #gravity a player experiences 
            self.range=100  #how far a player can reach
            self.grounded = True  #on the ground
            self.lookingLeft=True  
            self.walking=False
            self.using=False
            self.jumpHeight=0   
            
            self.maxHealth=maxHealth #init maxHealth
            self.health=(health if health > 0 else maxHealth)  #init the Health
            self.intHealth=self.health
            self.regen= 4 if self.game.difficulty == "Casual" else 2 #set regen amount
            self.regenTimer=25  #set regen timer
            self.regenCooldown=0  #set regen cooldown
            self.damageRed= 2 if self.game.difficulty == "Casual" else 1  #give damage reduction in casual mode
            self.healthChange=False
            
            #init inventory
            self.inventory=inventory
            self.inventoryChange=True
            self.maxItemCount=32
            self.selectedIndex=0
            
            
            self.touching=None  #not touching a tile
            self.tool=None   #not having a tool 
            self.event=None  #no tool event
            
            #initialise player images for animation
            self.playerSheet=Spritesheet("playersheet.png",3, (0,0,0), 16, 25)
            self.walkingLeft=[self.playerSheet.getImage(i, 0) for i in range(13)]
            self.walkingRight=[self.playerSheet.getImage(i, 1) for i in range(13)]
            self.fallingLeft=self.playerSheet.getImage(13, 0)
            self.fallingRight=self.playerSheet.getImage(13, 1)
            self.usingLeft=[self.playerSheet.getImage(i, 0) for i in range(14, 19)]
            self.usingRight=[self.playerSheet.getImage(i, 1) for i in range(14, 19)]

            #initialise the image/rect and position 
            self.x,self.y = x,y
            self.currentSprite=4
            self.image=self.walkingRight[self.currentSprite]
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y=x*TILESIZE, y*TILESIZE
            
        
        #update the player 
            
        def update(self):
            self.updateInput()
            self.updateHealth()
            self.updateMotion()
            self.animate()
        
        #make player move due to inputs
        def updateInput(self):
            keys = pygame.key.get_pressed()
            if not(self.using):
                if keys[K_d]:
                    self.vel.x = self.speed
                    self.lookingLeft=False
                    self.walking=True
                elif keys[K_a]:
                    self.vel.x = -self.speed
                    self.lookingLeft=True
                    self.walking=True
                else:
                    self.vel.x = 0
                    self.walking=False
                
                if self.game.noclip:
                    if keys[K_w]:
                        self.vel.y=-self.speed
                    elif keys[K_s]:
                        self.vel.y=self.speed
                    else:
                        self.vel.y=0
                    
                
                    
        #regen the health of the player if cooldowns are zero, decerment cooldowns and timers, kill if health is zero or lower          
        def updateHealth(self):
            if self.regenCooldown>0:
                self.regenCooldown-=1
                
            if self.regenTimer>0:
                self.regenTimer-=1
        
            if self.health<self.maxHealth and self.regenCooldown==0 and self.regenTimer==0:
                self.regenTimer=25
                self.heal(self.regen*max((self.health/self.maxHealth), 0.5))
                
            if self.health<=0:
                self.kill()
        
        #deal damage if not in create mode and set a cooldown for the regen, flag health change for the HUD
        def takeDamage(self, damage):
            if self.game.difficulty != "Creative":
                self.health-= round(damage/self.damageRed)
                self.healthChange=True
                self.regenCooldown=200
                
                self.updateHealth()
        
        #heal an amount, flag health change for the HUD
        def heal(self, amount):
            self.health += round(amount)
            
            if self.health> self.maxHealth:
                self.health=self.maxHealth
                
            self.healthChange=True
            
            self.updateHealth()
            
        
        #update the motion and collisions
        def updateMotion(self):
            self.fallVelocity=self.vel.y
            if not(self.game.noclip):
                self.vel.y += (self.grav * self.game.dt)   #add gravity
                self.rect.y += round(self.vel.y * self.game.dt)  #change y
                self.grounded=False#make not grounded before checking the collsion
                self.collision("y")#collsion in y
                self.rect.x += round(self.vel.x * self.game.dt) #change x
                self.collision("x")#collision in x
            else:
                self.rect.y += round(self.vel.y * self.game.dt) #change y
                self.rect.x += round(self.vel.x * self.game.dt)#change x
            self.itemCollide()
            self.tileCollide()
         
        #animate the player depending on what state they are in 
        def animate(self):
            if not(self.grounded):
                self.using=False
                self.event=False
                
                if self.tool:
                    self.tool.kill()
                    self.tool=None
                    
                self.currentSprite=4
                
                if self.lookingLeft:
                    self.image=self.fallingLeft
                else:
                    self.image=self.fallingRight
                    
                    
                    
            elif self.using:
                if self.inventory[self.selectedIndex][1] in self.game.toolImageDict:
                    if not self.tool:
                        self.tool=Tool(self.game, self.inventory[self.selectedIndex][1])

                    
                self.currentSprite+=(self.tool.speed if self.tool else 0.4)*(60//self.game.FPS)
                if self.currentSprite >= len(self.usingRight):
                    self.using=False
                    self.finishUse()
            
                    if self.tool:
                        self.tool.kill()
                        self.tool=None
                        
                    self.currentSprite=0
                    
                if self.lookingLeft:
                    self.image = self.usingLeft[int(self.currentSprite)]
                    if self.tool:
                        self.tool.updateFrame(int(self.currentSprite), True)
                        
                else:
                    self.image = self.usingRight[int(self.currentSprite)]
                    if self.tool:
                        self.tool.updateFrame(int(self.currentSprite), False)
                    
                    
                    
                    
            elif self.walking:
                self.currentSprite+=0.25*(60//self.game.FPS)
                
                if self.currentSprite >= len(self.walkingRight):
                    self.currentSprite=0
                
                if self.lookingLeft:
                    self.image = self.walkingLeft[int(self.currentSprite)]
                    
                else:
                    self.image = self.walkingRight[int(self.currentSprite)]
                    
            else:
                self.currentSprite=4
            
                if self.lookingLeft:
                    self.image = self.walkingLeft[int(self.currentSprite)]
                    
                else:
                    self.image = self.walkingRight[int(self.currentSprite)]
            
            
                

                
        #if the player collides then make it so the player is moved to just outside of the intersection      
        def collision(self,dire):
            hits = pygame.sprite.spritecollide(self, self.game.colSprites, False, collided=pygame.sprite.collide_rect)

            if len(hits) == 0:
                return

            if dire == "y":
                for hit in hits:
                    if self.vel.y > 0:
                        if hit.rect.top < self.rect.bottom:
                            
                            if self.fallVelocity>1000:
                               self.takeDamage(self.fallVelocity/100)
                               
                            self.vel.y = 0
                            self.rect.y = hit.rect.top - self.rect.height 
                            self.grounded = True
                            
                            
                    if self.vel.y < 0:
                        if hit.rect.bottom > self.rect.top:
                            self.vel.y = 0
                            self.rect.y = hit.rect.bottom

            if dire == "x":
                for hit in hits:
                    if self.vel.x > 0:
                        if hit.rect.left < self.rect.right:
                            self.vel.x = 0
                            self.walking=False
                            self.rect.x = hit.rect.left - self.rect.width
                    if self.vel.x < 0:
                        if hit.rect.right > self.rect.left:
                            self.vel.x = 0
                            self.walking=False
                            self.rect.x = hit.rect.right
        
        #check collisions with a crafting tile
        def tileCollide(self):
            hits = pygame.sprite.spritecollide(self, self.game.tileSprites, False, collided=pygame.sprite.collide_rect)
            
            if len(hits) == 0:
                self.touching=None
                
            else:
                self.touching=hits[0].name
        
        #check to pick up items
        def itemCollide(self):
            hits = pygame.sprite.spritecollide(self, self.game.itemSprites, False, collided=pygame.sprite.collide_rect)
            
            if len(hits) == 0:
                return
            
            for hit in hits:
                self.itemPick(hit)
                
    #     def itemPick(self, item):
    #         found=False
    #         for unit in self.inventory:
    #             if unit[1]==item.name and unit[2]< self.maxItemCount and unit[0] < 40:
    # 
    # 
    #                 self.inventory[unit[0]][2]+=1
    #                 
    #                 self.inventoryChange=True
    #                 found=True
    #                 item.kill()
    #                 break
    #         
    #         if not found:
    #             for unit in self.inventory:
    #                 if unit[2]==0 and unit[0] < 40:
    #                     self.inventory[unit[0]][1]=item.name
    #                     self.inventory[unit[0]][2]=1
    #                     
    #                     self.inventoryChange=True
    #                     found=True
    #                     item.kill()
    #                     break
        
        #pick the item
        def itemPick(self, item):
            item.kill()
            self.addToInv(item.name, 1)
        #allows for a change in the players inventory            
        def invChange(self, index, name, count):
            # if the count is too large for the unit then refuse the change
            if count > self.maxItemCount:
                return False
            
            else:
                #if the count of the item is lower than zero set the unit to empty
                if count<1:
                    self.inventory[index]=[index,"empty",0]
                    
                else:
                    self.inventory[index]=[index,name,count]
                    
                self.inventoryChange=True
                
                return True
        
        #scan the player inventory for a space and then add the item to that space, otherwise drop the item as an item object
        def addToInv(self, name, count):
            found=False
            for unit in self.inventory:
                if unit[1]==name and unit[2] < self.maxItemCount and unit[0] < 40:
                    
                    count=unit[2]+count
                    
                    if count > self.maxItemCount:
                        self.invChange(unit[0], name, self.maxItemCount)
                        count-=self.maxItemCount
                        self.addToInv(name,count)
                        
                    else:
                        self.invChange(unit[0], name, count)
                        count=0
                    
                    found=True
                    break
            
            if not found:
                for unit in self.inventory:
                    if unit[2]==0 and unit[0] < 40:
                        
                        if count > self.maxItemCount:
                            self.invChange(unit[0], name, self.maxItemCount)
                            count-=self.maxItemCount
                            self.addToInv(name,count)
                            
                        else:
                            self.invChange(unit[0], name, count)
                            count=0
                            

                        found=True
                        break
            
            
            if not found:
                for i in range(count):
                    Item(self.rect.x//TILESIZE,self.rect.y//TILESIZE-3,count)
                
                count=0
                
        #remove the ingridients for crafting and then add the crafting result
        def craft(self, item):
            tile=self.game.inv.tile
            ingNameList=list(self.game.inv.recipeDict[tile][item].keys())
            ingCountList=[self.game.inv.recipeDict[tile][item][ing] for ing in ingNameList]
            
            for index, ing in enumerate(ingNameList):
                for unit in self.inventory:
                    if unit[1]==ing:
                        ingCountList[index]-=unit[2]
                        self.invChange(unit[0], unit[1], 0)
                              
                            
                self.addToInv(ingNameList[index], int(ingCountList[index]*-1))
                
            self.addToInv(item,1)
            self.game.inv.updateCrafting()
        
        #use an item
        def use(self, event):
            self.vel.x=0
            if not self.using:
                self.using=True
                self.currentSprite=0
                
            self.event=event
        
        #called from animiate if the animation is finished
        def finishUse(self):
            #do an action
            if self.tool:
                if self.tool.type=="pickaxe":
                    self.game.destroyBlock(self.event, self.tool)
                elif self.tool.type=="axe":
                    self.game.destroyTree(self.event, self.tool)
                elif self.tool.type=="hammer":
                    self.game.destroyWall(self.event, self.tool)
                elif self.tool.type=="hamaxe":
                    self.game.destroyTree(self.event, self.tool)
                    self.game.destroyWall(self.event, self.tool)
            
            else:
                
                self.game.place(self.event)
                
            self.event=None
        #if the player is killed then he simply respawns
        def kill(self):
            self.rect.x==20*TILESIZE
            self.rect.y=0*TILESIZE
            
            self.health=self.maxHealth//2
            
            for sprite in self.game.enemySprites:
                sprite.kill()
            
    #enemy slime 
    class Slime(pygame.sprite.Sprite):
        def __init__(self, game, x, y): # this x,y coord is a world coord (not pixels)
            self.game = game
            self.groups = (self.game.personSprites, self.game.enemySprites)
            pygame.sprite.Sprite.__init__(self, self.groups)

            self.vel = pygame.math.Vector2()
            
            #set constants similar to the player 
            self.speed=50
            self.jumpSpeed=800
            self.grav = 2500   #effected by gravity
            self.grounded = True  #make it so it cannot double jump
            self.lookingLeft=True 
            self.bouncing=False  #unique jumping animation effect
            
            self.jumpTimer=50  #cooldown for random jumps
            self.attackTimer=0 #cooldown for attacks
            self.stunTimer=0  #stun after getting hit
            
            self.maxHealth=40
            self.health=self.maxHealth
            
            #init the animation
            slimeSheet=Spritesheet("slimesheet.png",1, (0,0,0), 50, 25)
            self.bouncingList=[slimeSheet.getImage(i, 0) for i in range(17)]
            
            #init image and position
            self.x,self.y = x,y
            self.currentSprite=0
            self.image=self.bouncingList[self.currentSprite]
            self.mask=pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y=x*TILESIZE, y*TILESIZE

        
        #call update for the slime
        def update(self):
            self.AI()
            self.updateHealth()
            self.updateMotion()
            self.animate()
            self.playercollide()

        #define the AI for the slime
        def AI(self):
            #if the player enters within 250 pixels the slime will attack
            if self.game.calcDistanceSP(self, self.game.player) < 250:
                self.attack=True
            else:
                self.attack=False
            
            #if distance between slime and player exceed 100 pixels then kill the sprite (optimisation purposes)
            if self.game.calcDistanceSP(self, self.game.player) > 1000:
                self.kill()
                
            #decrement stunTimer
            if self.stunTimer > 0:
                self.stunTimer-=1
            
            #if not stunned then do everything
            if self.stunTimer==0:
                #if the slime is in attack mode then make the space faster and jumps more frequent
                if self.attack:
                    self.speed=100
                    self.jumpTimer-=1
                    
                    #slime should face player while in attack mode
                    if self.rect.x < self.game.player.rect.x:
                        self.lookingLeft=False
                    
                    else:
                        self.lookingLeft=True
                    
                else:
                    #normal speed/jump freq
                    self.speed=50
                    self.jumpTimer-=0.5
                    
                #update the input fore the slime
                if self.lookingLeft:
                    self.vel.x=-self.speed
                else:
                    self.vel.x=self.speed
                
                #do small jumps every interval    
                if self.jumpTimer==0:
                    self.jump("small")
                    self.jumpTimer=50
                
                #decrement attack timer
                if self.attackTimer!=0:
                    self.attackTimer-=1
            
        #jump fuction: takes size as an input and will decide what velocity jump to do based on this size and whether the slime is enraged        
        def jump(self, size):
            if self.grounded:
                if size=="large":
                    if self.attack:
                        vel=1000
                    else:
                        vel=500
                
                elif size=="small":
                    if self.attack:
                        vel=750
                    else:
                        vel=500
                    
                else:
                    vel=0
                    
                self.vel.y=-vel
                self.bouncing=True
            
        #set a transparency for the slime the lower the health goes        
        def updateHealth(self):
            
            self.image.set_alpha((self.health/self.maxHealth)*255)
            
            if self.health<=0:
                #kill slime if its health is zero or lower
                self.kill()        
        
        #make changes to the position of the slime and do collision in the x and y direction like the player
        def updateMotion(self):
            self.fallVelocity=self.vel.y
            self.vel.y += (self.grav * self.game.dt)
            self.rect.y += round(self.vel.y * self.game.dt)
            self.grounded=False
            self.collision("y") 
            self.rect.x += round(self.vel.x * self.game.dt)
            self.collision("x")

        #animate the slime based on what mode it is in
        def animate(self):
            #if jumping do the full animation
            if self.bouncing:
                self.currentSprite+=0.25*(60//self.game.FPS)
                
                if self.currentSprite >= len(self.bouncingList):
                    self.currentSprite=0
                    self.bouncing=False
                    
            #otherwise play the first few frames        
            else:
                self.currentSprite+=0.1*(60//self.game.FPS)
                if self.currentSprite >= 4:
                    self.currentSprite=0
            
            #update the image and mask
            self.image = self.bouncingList[int(self.currentSprite)]
            self.mask=pygame.mask.from_surface(self.image)
        
        #make the slime take damage and take knockback depending on the positional arugment from the player tool
        def takeDamage(self,damage, pos=None):
            
            if pos:
                self.stunTimer=30
                
                self.jump("small")
                if pos == "right":
                    self.vel.x+=(damage/self.health)*1000
                elif pos == "left":
                    self.vel.x-=(damage/self.health)*1000
                
            self.health-=damage
            self.updateHealth()  #call to update the health

        
            
        
        #checks for itersections betweem solid blocks and then places the sprite just before the intersection and sets the velocity to zero. This gives the impression of hitting a solid object.
        #enemies do not take fall damage
        def collision(self,dire):
            hits = pygame.sprite.spritecollide(self, self.game.colSprites, False, collided=pygame.sprite.collide_rect)
            if len(hits) == 0:
                return

            if dire == "y":
                for hit in hits:
                    if self.vel.y > 0:
                        if hit.rect.top < self.rect.bottom:
                        
                               
                            self.vel.y = 0
                            self.rect.y = hit.rect.top - self.rect.height 
                            self.grounded = True
                            
                            
                    if self.vel.y < 0:
                        if hit.rect.bottom > self.rect.top:
                            self.vel.y = 0
                            self.rect.y = hit.rect.bottom

            if dire == "x":
                for hit in hits:
                    if self.vel.x > 0:
                        if hit.rect.left < self.rect.right:
                            self.vel.x = 0
                            self.rect.x = hit.rect.left - self.rect.width
                            
                            
                    if self.vel.x < 0:
                        if hit.rect.right > self.rect.left:
                            self.vel.x = 0
                            self.rect.x = hit.rect.right
                            
                if not self.attack:
                    self.lookingLeft = not(self.lookingLeft)
                else:
                    self.jump("large")
                                 # perform a large jump if the slime collides with a fall
                            
                                
        #if the slime hits the player then do damage if the attack timer is zero, if the damage is dealt then the attack timer is reset            
        def playercollide(self):
            if self.attackTimer==0 and self.rect.colliderect(self.game.player.rect):
                self.game.player.takeDamage(10)
                self.attackTimer=80
                
                
    #zombie enemy          
    class Zombie(pygame.sprite.Sprite):
        def __init__(self, game, x, y): # this x,y coord is a world coord (not pixels)
            self.game = game
            #initialise groups and the pygame.sprite inheritance
            self.groups = (self.game.personSprites, self.game.enemySprites)
            pygame.sprite.Sprite.__init__(self, self.groups)
            
            #set constants- effect from graviy, speed, health, animation sheet, current image 
            self.vel = pygame.math.Vector2()
            
            self.speed=50
            self.grav = 2500
            self.grounded = True  
            self.lookingLeft=True
            
            self.attackTimer=0
            self.stunTimer=0
            
            self.maxHealth=100
            self.health=self.maxHealth
            
            zombieSheet=Spritesheet("zombiesheet.png",1, (0,0,0), 50, 68)
            self.walkingRightList=[zombieSheet.getImage(i, 1) for i in range(3)] #need a seperate list for left and right as the right is in the flipped direction to the spritesheet
            self.walkingLeftList=[zombieSheet.getImage(i, 0) for i in range(3)]
            
    
            self.x,self.y = x,y
            self.currentSprite=0
            self.image=self.walkingRightList[self.currentSprite]
            self.mask=pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y=x*TILESIZE, y*TILESIZE

        #call update
        def update(self):
            self.AI()
            self.updateHealth()
            self.updateMotion()
            self.animate()
            self.playercollide()

       #define AU 
        def AI(self):
            #if distance 300 pixels within player then attack
            if self.game.calcDistanceSP(self, self.game.player) < 300:
                self.attack=True
            else:
                self.attack=False
                
                
            if self.game.calcDistanceSP(self, self.game.player) > 1000:
                self.kill()
                
                
            if self.stunTimer > 0:
                self.stunTimer-=1
            
            #if attacking then face the player and run faster
            if self.stunTimer==0:
                if self.attack:
                    self.speed=100

                    if self.rect.x < self.game.player.rect.x:
                        self.lookingLeft=False
                    
                    else:
                        self.lookingLeft=True
                    
                else:
                    self.speed=50
                    
                    
                if self.lookingLeft:
                    self.vel.x=-self.speed
                else:
                    self.vel.x=self.speed
                    
                    
                if self.attackTimer!=0:
                    self.attackTimer-=1
            
        #jump fuction same as slime     
        def jump(self, size):
            if self.grounded:
                if size=="large":
                    if self.attack:
                        vel=750
                    else:
                        vel=500
                
                elif size=="small":
                    if self.attack:
                        vel=500
                    else:
                        vel=500
                    
                else:
                    vel=0
                
                self.vel.y=-vel
                self.bouncing=True
            
        #update health is the same but on kill the zombie has a chance to drop rare ores       
        def updateHealth(self):
            
            self.image.set_alpha((self.health/self.maxHealth)*255)
            
            if self.health<=0:
                self.kill()
                if random.uniform<=0.03:
                    Item(self.rect.x,self.rect.y,"uru")
                elif random.uniform<=0.05:
                    Item(self.rect.x,self.rect.y,"adamantite")
        
        #updates positon of zombie and calls for collisions to be dealt with 
        def updateMotion(self):
            self.fallVelocity=self.vel.y
            self.vel.y += (self.grav * self.game.dt)
            self.rect.y += round(self.vel.y * self.game.dt)
            self.grounded=False
            self.collision("y")
            self.rect.x += round(self.vel.x * self.game.dt)
            self.collision("x")

        #animate the zombie
        def animate(self):
            self.currentSprite+=0.1*(60//self.game.FPS)
            
            if self.currentSprite >= len(self.walkingRightList):
                self.currentSprite=0
            
            if self.lookingLeft:
                self.image = self.walkingLeftList[int(self.currentSprite)]     
            else:
                self.image = self.walkingRightList[int(self.currentSprite)]


            self.mask=pygame.mask.from_surface(self.image)
                    
         # take damage and be knockbacked           
        def takeDamage(self,damage, pos=None):
            
            if pos:
                self.stunTimer=30
                
                self.jump("small")
                if pos == "right":
                    self.vel.x+=(damage/self.health)*1000
                elif pos == "left":
                    self.vel.x-=(damage/self.health)*1000
                
            self.health-=damage
            self.updateHealth()

        
            
        #collision is the same as player 
            
        def collision(self,dire):
            hits = pygame.sprite.spritecollide(self, self.game.colSprites, False, collided=pygame.sprite.collide_rect)
            if len(hits) == 0:
                return

            if dire == "y":
                for hit in hits:
                    if self.vel.y > 0:
                        if hit.rect.top < self.rect.bottom:
                            
    #                         if self.fallVelocity>1500:
    #                            self.takeDamage(50)
                               
                            self.vel.y = 0
                            self.rect.y = hit.rect.top - self.rect.height 
                            self.grounded = True
                            
                            
                    if self.vel.y < 0:
                        if hit.rect.bottom > self.rect.top:
                            self.vel.y = 0
                            self.rect.y = hit.rect.bottom
                            
                            self.lookingLeft = not(self.lookingLeft)

            if dire == "x":
                for hit in hits:
                    if self.vel.x > 0:
                        if hit.rect.left < self.rect.right:
                            self.vel.x = 0
                            self.rect.x = hit.rect.left - self.rect.width
                                
                    if self.vel.x < 0:
                        if hit.rect.right > self.rect.left:
                            self.vel.x = 0
                            self.rect.x = hit.rect.right
                        
                        
                    if not self.attack:
                        self.jump("small")  #zombie will do a jump on wall collide
                    else:
                        self.jump("large")
         
         #damage works the same as slime
        def playercollide(self):
            if self.attackTimer==0 and self.rect.colliderect(self.game.player.rect):
                self.game.player.takeDamage(30)
                self.attackTimer=120            


    #everything works the same as zombie just a fiew changes 
    class Skeleton(pygame.sprite.Sprite):
        def __init__(self, game, x, y): # this x,y coord is a world coord (not pixels)
            self.game = game
            self.groups = (self.game.personSprites, self.game.enemySprites)
            pygame.sprite.Sprite.__init__(self, self.groups)

            self.vel = pygame.math.Vector2()
            
            self.speed=50
            self.jumpSpeed=800
            self.grav = 2500
            self.grounded = True
            self.lookingLeft=True
            self.using=False
            
            self.attackTimer=0
            self.stunTimer=0
            
            self.maxHealth=200  #higher health than zombie 
            self.health=self.maxHealth
            
            skeletonSheet=Spritesheet("skeletonsheet.png",3, (0,0,0), 16, 25)
            self.walkingRight=[skeletonSheet.getImage(i, 1) for i in range(10)]
            self.walkingLeft=[skeletonSheet.getImage(i, 0) for i in range(10)]
            self.usingRight=[skeletonSheet.getImage(i, 1) for i in range(10,16)]
            self.usingLeft=[skeletonSheet.getImage(i, 0) for i in range(10,16)]
        
            self.x,self.y = x,y
            self.currentSprite=0
            self.image=self.walkingRight[self.currentSprite]
            self.mask=pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y=x*TILESIZE, y*TILESIZE


        def update(self):
            self.AI()
            self.updateHealth()
            self.updateMotion()
            self.playercollide()
            self.animate()
        
        
        def AI(self):
            if self.game.calcDistanceSP(self, self.game.player) < 300:
                self.attack=True
            else:
                self.attack=False
                
            if self.game.calcDistanceSP(self, self.game.player) > 1000:
                self.kill()
                
            if self.stunTimer > 0:
                self.stunTimer-=1
                
            if self.stunTimer==0:
                if self.attack:
                    self.speed=100

                    if self.rect.x < self.game.player.rect.x:
                        self.lookingLeft=False
                        
                    
                    else:
                        self.lookingLeft=True
                    
                    if self.attackTimer==0:
                        self.use()   #has the ability to shoot projectile
                       
                else:
                    self.speed=50
                
                
                if not self.using:      
                    if self.lookingLeft:
                        self.vel.x=-self.speed
                    else:
                        self.vel.x=self.speed
                        
                        
                    if self.attackTimer!=0:
                        self.attackTimer-=1
            
                
        def jump(self, size):
            if size=="large":
                if self.attack:
                    vel=750
                else:
                    vel=500
            
            elif size=="small":
                if self.attack:
                    vel=500
                else:
                    vel=500
                
            else:
                vel=0
                
            self.vel.y=-vel
            
            
        def updateHealth(self):
            
            self.image.set_alpha((self.health/self.maxHealth)*255)
            
            if self.health<=0:
                self.kill()
                if random.uniform<=0.06:
                    Item(self.rect.x,self.rect.y,"uru")
                elif random.uniform<=0.10:
                    Item(self.rect.x,self.rect.y,"adamantite")
            
        def updateMotion(self):
            self.fallVelocity=self.vel.y
            self.vel.y += (self.grav * self.game.dt)
            self.rect.y += round(self.vel.y * self.game.dt)
            self.grounded=False
            self.collision("y")
            self.rect.x += round(self.vel.x * self.game.dt)
            self.collision("x")
            
            
        def animate(self):
                
            if self.using:
                
                self.currentSprite+=0.25*(60//self.game.FPS)
                if self.currentSprite >= len(self.usingRight):
                    self.using=False
                    self.finishUse()
                    self.currentSprite=0
                    
                if self.lookingLeft:
                    self.image = self.usingLeft[int(self.currentSprite)]

                        
                else:
                    self.image = self.usingRight[int(self.currentSprite)]

                 
            else:
                self.currentSprite+=0.1*(60//self.game.FPS)
                
                if self.currentSprite >= len(self.walkingRight):
                    self.currentSprite=0
                
                if self.lookingLeft:
                    self.image = self.walkingLeft[int(self.currentSprite)]
                    
                else:
                    self.image = self.walkingRight[int(self.currentSprite)]
                    
                    
            self.mask=pygame.mask.from_surface(self.image)
                    
                    
        def takeDamage(self,damage, pos=None):
            
            if pos:
                self.stunTimer=30
                
                self.jump("small")
                if pos == "right":
                    self.vel.x+=(damage/self.health)*1000
                elif pos == "left":
                    self.vel.x-=(damage/self.health)*1000
                
            self.health-=damage
            self.updateHealth()
        
            

            
        def collision(self,dire):
            hits = pygame.sprite.spritecollide(self, self.game.colSprites, False, collided=pygame.sprite.collide_rect)
            if len(hits) == 0:
                return

            if dire == "y":
                for hit in hits:
                    if self.vel.y > 0:
                        if hit.rect.top < self.rect.bottom:
                            
    #                         if self.fallVelocity>1500:
    #                            self.takeDamage(50)
                               
                            self.vel.y = 0
                            self.rect.y = hit.rect.top - self.rect.height 
                            self.grounded = True
                            
                            
                    if self.vel.y < 0:
                        if hit.rect.bottom > self.rect.top:
                            self.vel.y = 0
                            self.rect.y = hit.rect.bottom
                            
                            self.lookingLeft = not(self.lookingLeft)

            if dire == "x":
                for hit in hits:
                    if self.vel.x > 0:
                        if hit.rect.left < self.rect.right:
                            self.vel.x = 0
                            self.rect.x = hit.rect.left - self.rect.width
                                
                    if self.vel.x < 0:
                        if hit.rect.right > self.rect.left:
                            self.vel.x = 0
                            self.rect.x = hit.rect.right
                        
                        
                    if not self.attack:
                        self.jump("small")
                    else:
                        self.jump("large")
                                

                            
        def playercollide(self):
            if self.attackTimer==0 and self.rect.colliderect(self.game.player.rect):
                self.game.player.takeDamage(70)
                self.attackTimer=120
            
        
        #skeleton can use fireball
        def use(self):
            self.vel.x=0
            if not self.using and not self.rect.colliderect(self.game.player.rect):
                self.using=True
                self.currentSprite=0
                self.attackTimer=120
            
        #calculates the angle using pygame.math.vector
        def finishUse(self):
            playerPos = pygame.math.Vector2()
            playerPos[0] = self.game.player.rect.x
            playerPos[1] = self.game.player.rect.y
            skeletonPos= pygame.math.Vector2()
            skeletonPos[0] = self.rect.x
            skeletonPos[1] = self.rect.y
            angle=skeletonPos.angle_to(playerPos)
            self.shoot(angle)   

        #shoots fireball at this angle by seperating the velocity into components    
        def shoot(self, angle):
            vel=500
            velX=-1*vel*cos(angle*(pi/180)) if self.lookingLeft else vel*cos(angle*(pi/180))
            velY=vel*sin(angle*(pi/180))
            Fireball(self.game, self.rect.x, self.rect.y, velX, velY, False, 30)
            
            
    #projectile class
    class Fireball(pygame.sprite.Sprite):
        def __init__(self,game,x,y, velX, velY, friendly, damage):
            self.game = game
            
            self.vel = pygame.math.Vector2()
            
            self.groups = (self.game.camSprites, self.game.enemySprites)
            pygame.sprite.Sprite.__init__(self,self.groups)
            
            sheet=Spritesheet("pinkfireball.png",2, (0,0,0), 9,9)
            self.animationList=[sheet.getImage(i, 0) for i in range(12)]

            self.damage=damage
            self.time=100
            self.friendly= friendly
            
            self.currentSprite=0
            self.image=self.animationList[self.currentSprite]
            self.size=self.image.get_size()
            self.rect = self.image.get_rect()
            self.rect.x,self.rect.y = x,y
            
            self.vel.x=velX
            self.vel.y=velY
            
        #will kill after a certain time
        def update(self):
            self.time-=1
            if self.time==0:
                self.kill()
                
            self.updateMotion()
            self.collide()
            self.animate()
        
        #goes stright along a single line
        def updateMotion(self):
            self.collision()
            self.rect.y += round(self.vel.y * self.game.dt)
            self.rect.x += round(self.vel.x * self.game.dt)
            
        
        #will look as if sparkle through the animation
        def animate(self):
            self.currentSprite+=0.1*(60//self.game.FPS)
            
            if self.currentSprite >= len(self.animationList):
                self.currentSprite=0

            self.image = self.animationList[int(self.currentSprite)]
            self.mask=pygame.mask.from_surface(self.image)
                
        #dissipates if it hits something that didn't cast it 
        def takeDamage(self,damage, pos=None):
            if not self.friendly:
                self.kill()
        
        #on colllision with solid block it dissipates
        def collision(self):
            hits = pygame.sprite.spritecollide(self, self.game.colSprites, False, collided=pygame.sprite.collide_rect)
            
            if len(hits)>0:
                self.kill()
         
        #if it collides with personSprite that didn't fire it then it will do damage
        def collide(self):
            hits = pygame.sprite.spritecollide(self, self.game.personSprites, False)
            if len(hits)==0:
                return
            
            else:
                hit=hits[0]
                if hit.__class__.__name__=="Player":
                    if not self.friendly:
                        hit.takeDamage(self.damage)
                        self.kill()
                    
                elif hit.__class__.__name__=="Fireball":
                    self.kill()
                    
                else:
                    if self.friendly:
                        hit.takeDamage(self.damage)
                        self.kill()
                        
           
            
            

    #class for a solid block 
    class Block(pygame.sprite.Sprite):
        def __init__(self,game,x,y, name):
            self.game = game
            self.name=name
            #init groups
            self.groups = (self.game.camSprites, self.game.colSprites)
            pygame.sprite.Sprite.__init__(self,self.groups)
            #add to the dictionary for block/tile objects --> follow darkness rules
            self.x,self.y = x,y
            self.game.gridDict[str((self.x,self.y))]=self
            self.darkness=0
            
            #pulls the health from the stat dictionary
            self.maxHealth = self.game.blockStatDict[self.name]["health"]
            self.health=self.maxHealth
            
            self.image = pygame.Surface((TILESIZE,TILESIZE)).convert_alpha()
            self.image.blit(self.game.blockImageDict[self.name], (0,0))
            self.size=self.image.get_size()
            self.rect = self.image.get_rect()
            self.rect.x,self.rect.y = self.x*TILESIZE,self.y*TILESIZE
        
        #deal damage to the block to increase transparency, damage can only be dealt if the block can be destroyed in less than 5 hits, otherwise no damage dealt.
        #once health is zero the block is killed and an item is dropped
            #destroyed with pickaxe 

        def damage(self, power):
            if self.maxHealth//power <=5 and self.darkness==0:
                self.health-=power
                self.image.set_alpha(int((self.health/self.maxHealth)*255))
            
            if self.health <=0:
                del self.game.gridDict[str((self.x,self.y))]
                self.game.updateDarknessAR(self)
                
                if str((self.x,self.y)) in self.game.wallDict:
                    self.game.wallDict[str((self.x,self.y))].add(self.game.backSprites,self.game.wallSprites)
                elif str((self.x,self.y)) in self.game.backDict:
                    self.game.backDict[str((self.x,self.y))].add(self.game.backSprites,self.game.backgroundSprites)
                    
                if self.name=="grass":
                    Item(self.game,self.rect.x,self.rect.y,"dirt")
                            
                else:
                    Item(self.game,self.rect.x,self.rect.y,self.name)
                
                self.kill()
                
        #update the darkness level of the block
        def updateDarkness(self,level):
            self.darkness=level
            self.image = pygame.Surface((TILESIZE,TILESIZE)).convert_alpha()
            
            if self.darkness < 3:
                self.image.blit(self.game.blockImageDict[self.name], (0,0))
                self.dark=pygame.Surface((TILESIZE,TILESIZE)).convert_alpha()
                self.dark.set_alpha(int((255/3)*self.darkness))
                self.image.blit(self.dark, (0,0))
        
        def __str__(self):
            return("self.x,self.y,self.name")
                
                
    #wall, same as a block but you can walk through it and doesn't have a darkness value to it           
    class Wall(pygame.sprite.Sprite):
        def __init__(self,game,x,y, name):
            self.game = game
            self.name=name
            
            self.groups = (self.game.backSprites, self.game.wallSprites)
            pygame.sprite.Sprite.__init__(self,self.groups)
            
            self.x,self.y = x,y
            self.game.wallDict[str((self.x,self.y))]=self
            
            self.maxHealth = 30
            self.health=self.maxHealth
            
            self.image = pygame.Surface((TILESIZE,TILESIZE)).convert_alpha()
            self.image.blit(self.game.wallImageDict[self.name], (0,0))
            self.size=self.image.get_size()
            self.rect = self.image.get_rect()
            self.rect.x,self.rect.y = self.x*TILESIZE,self.y*TILESIZE
        
        #destroyed with hamemr 
        def damage(self, power):
            self.health-=power
            self.image.set_alpha(int((self.health/self.maxHealth)*255))
            
            if self.health <=0:
                if str((self.x,self.y)) in self.game.backDict:
                    self.game.backDict[str((self.x,self.y))].add(self.game.camSprites,self.game.backSprites)
                    
                self.kill()
                
        def __str__(self):
            return("self.x,self.y,self.name")
            

    #same as block but is not collideable
    class Tile(pygame.sprite.Sprite):
        def __init__(self,game,x,y, name):
            self.game = game
            self.name=name
            
            self.groups = (self.game.camSprites, self.game.tileSprites, self.game.wallSprites)
            pygame.sprite.Sprite.__init__(self,self.groups)
        
            
            self.x,self.y = x,y
            self.game.gridDict[str((self.x,self.y))]=self
            self.darkness=0
            
            self.maxHealth = 30
            self.health=self.maxHealth
            
            self.image = pygame.Surface((TILESIZE*2,TILESIZE*2)).convert_alpha()
            self.image.blit(self.game.tileImageDict[self.name], (0,0))
            self.image.set_colorkey((0,0,0))
            self.size=self.image.get_size()
            self.rect = self.image.get_rect()
            self.rect.x,self.rect.y = self.x*TILESIZE,self.y*TILESIZE
            
            if pygame.sprite.spritecollideany(self, self.game.colSprites):
                self.damage(30)
        
        #destroy with hammer
        def damage(self, power):
            self.health-=power
            self.image.set_alpha(int((self.health/self.maxHealth)*255))
            
            if self.health <=0:
                
                Item(self.game,self.rect.x,self.rect.y,self.name)
                
                self.kill()
        
        def updateDarkness(self,level):
            self.image = pygame.Surface((TILESIZE*2,TILESIZE*2)).convert_alpha()
            self.image.set_colorkey((0,0,0))
            self.image.blit(self.game.tileImageDict[self.name], (0,0))
            self.darkness=level
            self.dark=pygame.Surface((TILESIZE,TILESIZE)).convert_alpha()
            self.dark.set_alpha(int((255/3.1)*self.darkness))
            self.image.blit(self.dark, (0,0))
            
        def __str__(self):
            return("self.x,self.y,self.name")
    
    #destroy with axe to get wood 
    class Tree(pygame.sprite.Sprite):
        def __init__(self,game,x,y):
            self.game = game
            
            self.groups = (self.game.camSprites, self.game.treeSprites)
            pygame.sprite.Sprite.__init__(self,self.groups)

            self.maxHealth = 100
            self.health=self.maxHealth
            
            self.x=x
            self.y=y
            
            self.image = pygame.image.load(os.path.expanduser(filepathG + "tree.png")).convert_alpha()
            self.size=self.image.get_size()
            self.rect = self.image.get_rect()
            
            self.rect.x=x
            self.rect.bottom=y
            self.mask=pygame.mask.from_surface(self.image)
        
        def damage(self, power):
            
            self.health-=power
            self.image.set_alpha(int((self.health/self.maxHealth)*255))
            
            if self.health <=0:
                
                for i in range(10):
                    Item(self.game,self.rect.x+35,self.rect.y+160,"wood")
                
                
                self.kill()


        def __str__(self):
            return("self.x,self.y")
        
    #pick up to get the item        
    class Item(pygame.sprite.Sprite):
            def __init__(self,game,x,y, name):
                self.game = game
                self.name = name
                self.scale=0.5
                
                self.groups = (self.game.camSprites, self.game.itemSprites)
                pygame.sprite.Sprite.__init__(self,self.groups)

                self.image = (self.game.itemImageDict[self.name]).convert_alpha()
                self.size=self.image.get_size()
                self.image = pygame.transform.scale(self.image, (int(self.size[0] * self.scale), int(self.size[1] * self.scale))).convert_alpha()
                self.rect = self.image.get_rect()
                self.rect.x,self.rect.y = x+10,y+10


            def __str__(self):
                return f"{self.name} item at ({self.x},{self.y}) at "
     
    #acts as a wall but is unbreakable
    class Background(pygame.sprite.Sprite):
        def __init__(self,game,x,y, name):
            self.game = game
            self.name = name
            

            self.groups = (self.game.backSprites)
            pygame.sprite.Sprite.__init__(self,self.groups)

            self.x,self.y = x,y
            self.game.backDict[str((self.x,self.y))]=self
            
            self.image = pygame.Surface((TILESIZE,TILESIZE)).convert_alpha()
            self.image.blit(self.game.backImageDict[self.name], (0,0))
            self.size=self.image.get_size()
            self.rect = self.image.get_rect()
            self.rect.x,self.rect.y = self.x*TILESIZE,self.y*TILESIZE
        
        def __str__(self):
            return("self.x,self.y,self.name")
            
    #group for sprites that stay in the same place (relative)     
    class CameraGroup(pygame.sprite.Group):

        def __init__(self,game):
            pygame.sprite.Group.__init__(self)
            self.game = game
            self.halfWidth = self.game.screen.get_size()[0]//2  # so player always in middle
            self.halfHeight = self.game.screen.get_size()[1] // 2
            self.offset = pygame.math.Vector2() # vector currPos to middle


        def customDraw(self):
            self.offset.x = self.halfWidth - self.game.player.rect.centerx
            self.offset.y = self.halfHeight - self.game.player.rect.centery
            self.game.off = self.offset
            for sprite in self.sprites(): # overlapping should depend on if under or top
                newPos = sprite.rect.topleft + self.offset
                if -125<newPos[0]<1100 and -200<newPos[1]<800:
                    self.game.screen.blit(sprite.image,newPos)
            
    #group for sprites that move with the player   (relative)       
    class HudGroup(pygame.sprite.Group):
        
        def __init__(self,game):
            pygame.sprite.Group.__init__(self)
            self.game = game
            
        def customDraw(self):
            for sprite in self.sprites():
                self.game.screen.blit(sprite.image,(sprite.rect.x,sprite.rect.y))


    g = Game(screen, worldName, difficulty, prevTime)
    g.main()

#menu fuction
def menu(screen):
    #menu option templates
    class Entry(pygame.sprite.Sprite):
        def __init__(self):
            self.BaseColour=((58,73,135))
            self.SelectedColour=((235,235,85))
            self.chosen=False
            self.chosenColour=((255,0,0))
            
            self.image=pygame.Surface((600,75))
            self.image.set_alpha(200)
            self.image.fill(self.BaseColour)
            
            self.rect = self.image.get_rect()
            self.rect.x = 50
            self.rect.y = 175
            
    class Button(pygame.sprite.Sprite):
        def __init__(self, image, x, y):
            self.imageBase=pygame.image.load(os.path.expanduser(filepathM + f"{image}.png"))
            self.imageSelected=pygame.image.load(os.path.expanduser(filepathM + f"{image}Selected.png"))
            self.image=self.imageBase
            
            self.rect = self.image.get_rect()
            self.rect.x=x
            self.rect.y=y
            
    class Image(pygame.sprite.Sprite):
        def __init__(self, image, x, y):
            self.image=pygame.image.load(os.path.expanduser(filepathM + f"{image}.png"))
            
            self.rect = self.image.get_rect()
            self.rect.x=x
            self.rect.y=y
            
    class Box(pygame.sprite.Sprite):  
        def __init__(self, surface, fill, alpha, x, y):
            self.image=pygame.Surface(surface)
            self.image.fill(fill)
            self.image.set_alpha(alpha)
            
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            
    class Text(pygame.sprite.Sprite):
        def __init__(self, text, size, colour, timer, x, y):
            self.text=text
            self.fontSize=size
            self.font="AndyBold"
            self.colour=colour
            self.timer=timer
            self.x=x
            self.y=y

    #menu subroutines
    def checkSelected(obj):
        pos = pygame.mouse.get_pos()
        
        if obj.rect.collidepoint(pos):
            
            if obj.__class__.__base__.__name__ == "Entry":
                
                if obj.chosen:
                    obj.image.fill(obj.chosenColour)
                    textToReturn=obj.text
                else:
                    obj.image.fill(obj.SelectedColour)
                
            else:
                obj.image=obj.imageSelected
                
            return True
        
        else:
            if obj.__class__.__base__.__name__ == "Entry":
            
                if obj.chosen:
                    obj.image.fill(obj.chosenColour)
                    textToReturn=obj.text
                else:
                    obj.image.fill(obj.BaseColour)
                
            else:
                obj.image=obj.imageBase
            
            return False
        
        
    def drawList(objList, screen):
        for obj in objList:
            if obj.__class__.__name__ == "Text":
                font=pygame.font.SysFont(obj.font, obj.fontSize)
                text=font.render(obj.text, 1, self.colour)
                screen.blit(text, (obj.x, obj.y))
                
            else:
                screen.blit(obj.image, (obj.rect.x,obj.rect.y))
                
                if obj.__class__.__base__.__name__ == "Entry" or obj.__class__.__name__ == "Button":
                    checkSelected(obj)
                    
                    if obj.__class__.__base__.__name__ == "Entry":
                        
                        if type(obj).__name__ == "NameEntry":
                            obj.text=f"Name: [{str(obj.name)}] Difficulty: [{str(obj.difficulty)}]"
                            
                        font=pygame.font.SysFont("AndyBold", 28) 
                        text=font.render(obj.text, 1, (255,255,255))
                        screen.blit(text, (obj.rect.x+5, obj.rect.y+10))
                        
    def displayText(obj):
        font=pygame.font.SysFont(obj.font, obj.fontSize)
        text=font.render(obj.text, 1, obj.colour)
        screen.blit(text, (obj.x, obj.y))
    
    
    def update(B1,B2):
        B1.rect.x-=1
        B2.rect.x-=1
        if B1.rect.x==-1000:
            B1.rect.x=1000
        elif B2.rect.x==-1000:
            B2.rect.x=1000
            
        pygame.display.update()
        fpsClock.tick(FPS)
    
    def homeMenu(screen):
        running=True
        BG1=Image("background", 0, 0)
        BG2=Image("background", 1000, 0)
        title=Image("title", 100, 0)
        
        play=Button("play", 300, 150)
        Quit=Button("quit", 300, 250)

        while running:
            spriteList=[BG1, BG2, title, play, Quit]
            drawList(spriteList, screen)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if event.button == 1:
                        if checkSelected(play):
                            worldMenu(screen)
                        if checkSelected(Quit):
                            pygame.quit()
                            sys.exit()
                            
                            
            update(BG1,BG2)
            
            
            
            
    def worldMenu(screen):
        
        class World(Entry):
            def __init__(self, name, difficulty, time):
                super().__init__()
        
                self.name=name
                self.difficulty=difficulty
                self.time=time
                
                self.path=f"{filepathW}{self.name}.json"
                self.text=f"Name: {str(self.name)} | Difficulty: {str(self.difficulty)} | Time played: {str(datetime.timedelta(seconds=round(self.time)))}"
                
        def worldSelect(screen):
            
            def getWorldPaths():
                worldPathList=[]
                for file in os.listdir(filepathW):
                    if file.endswith(".json"):
                        worldpath=os.path.join(filepathW, file)
                        worldPathList.append(worldpath)
                        
                return(worldPathList)
        
            def getWorldList():
                worldPaths=getWorldPaths()
                worldList=[]
                for worldPath in worldPaths:
                    with open(os.path.expanduser(worldPath)) as file:
                        save = json.load(file)
                        
                        worldName=save["Name"]
                        time=save["TimePlayed"]
                        difficulty=save["Difficulty"]

                        world=World(worldName, difficulty, time)
                        worldList.append(world)
                    
                for index, world in enumerate(worldList):
                    yOffset=(75*index)
                    world.rect.y+=yOffset
                    
                return worldList
            
            running=True
            BG1=Image("background", 0, 0)
            BG2=Image("background", 1000, 0)
            title=Image("title", 100, 0)
            back=Button("back", 700, 400)
            play=Button("play", 725, 125)
            delete=Button("delete", 700, 225)
            
            newWorld=Button("newworld", 675, 300)
            selectWorld=Image("selectworld", 200, 100)
            transBox=Box((600,375), (58,73,135), 128, 50, 100)
            subtitleBox=Box((600,75), (58,73,135), 256, 50, 100)
            worldsFull=Text("Unable to create world, max four worlds allowed", 20, (255,0,0), 0, 675, 375)
            
            worldList=getWorldList()
            worldList
            while running:
                
                spriteList=[BG1, BG2, title, newWorld, back, transBox, subtitleBox, selectWorld]+worldList
                drawList(spriteList, screen)
                
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        if event.button == 1:
                            
                            for world in worldList:
                                if checkSelected(world):
                                    
                                    for item in worldList:
                                        item.chosen=False
                                    
                                    world.chosen=True
                                
                                if world.chosen:
                                    if checkSelected(play):
                                        game(screen, world.name, world.difficulty, world.time)
                                    if checkSelected(delete):
                                        os.remove(world.path)
                                        worldMenu(screen)
                            
                            if checkSelected(newWorld):
                                if len(worldList) < 4:
                                    createWorld(screen)
                                else:
                                    worldsFull.timer=100
                                    
                            if checkSelected(back):
                                menu(screen)
                                
                for world in worldList: 
                    if world.chosen:
                        drawList([play, delete], screen)
                
                
                if worldsFull.timer > 0:
                    worldsFull.timer -= 1
                    displayText(worldsFull)
                    
                update(BG1,BG2)

            
            
        def createWorld(screen):

            class NameEntry(Entry):
                def __init__(self):
                    super().__init__()
                        
                    self.name=""
                    self.difficulty=""
                    self.text=f"Name: {str(self.name)}, Difficulty: {str(self.difficulty)}"
            
            class Diff(Entry):
                def __init__(self, text, y):
                    super().__init__()
                    self.text=text
                    self.rect.y = y

            running=True
            BG1=Image("background", 0, 0)
            BG2=Image("background", 1000, 0)
            title=Image("title", 100, 0)
            back=Button("back", 700, 350)
            
            create=Button("create", 700, 250)
            createWorld=Image("createworld", 200, 100)
            transBox=Box((600,375), (58,73,135), 128, 50, 100)
            subtitleBox=Box((600,75), (58,73,135), 256, 50, 100)
            
            nameEntry=NameEntry()
            diffArray=[Diff("Normal", 250), Diff("Casual", 325), Diff("Creative", 400),]
            
            while running:
                
                spriteList=[BG1, BG2, title, create, back, transBox, subtitleBox, createWorld, nameEntry]+diffArray
                drawList(spriteList, screen)
                
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                        
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        
                        if event.button == 1:
                            
                            for diff in diffArray:
                                if checkSelected(diff):
                                    
                                    for item in diffArray:
                                        item.chosen=False
                                    
                                    diff.chosen=True
                                    nameEntry.difficulty=diff.text
                                    
                            if checkSelected(nameEntry):
                                nameEntry.chosen=True
                            else:
                                nameEntry.chosen=False
                                    
                            if checkSelected(create):
                                game(screen, nameEntry.name, nameEntry.difficulty)
                                
                            if checkSelected(back):
                                worldSelect(screen)
                                
                    if event.type == KEYDOWN:
                        if nameEntry.chosen:
                            if event.key == K_BACKSPACE:
                                if len(nameEntry.name)>0:
                                    nameEntry.name = nameEntry.name[:-1]
                                    
                            else:
                                nameEntry.name += event.unicode
                
                update(BG1,BG2)

                
        worldSelect(screen)
    homeMenu(screen)
menu(screen)


