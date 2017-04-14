import pygame
from pygame.locals import *

# I'm defining this to handle basic pygame initialization stuff and deal
# with the screen object in an easy-to-use way. Does a lot of the standard
# things that I need for experiments; somewhat limited in terms of more
# advanced graphics.

def loadImage(filename, colorkey=(0,0,0)):
    """Load an image by filename."""
    if filename:
        image = pygame.image.load(filename)
        image = image.convert()
        if colorkey:
            image.set_colorkey(colorkey)
        return image

class Monitor:

    def __init__(self,width=1024,height=768,fullscreen=False,grabValue=1,textSize=40):
        
        pygame.init()
        pygame.font.init()
        pygame.mouse.set_visible(0)
        pygame.event.set_grab(grabValue)
        self.horizSize = width
        self.vertSize = height

        if fullscreen:
            self.myScreen = pygame.display.set_mode((width,height),FULLSCREEN)
        else:
            self.myScreen = pygame.display.set_mode((width,height))

        self.font = pygame.font.Font(None,textSize)

        # Using these speeds things up enormously
        self.rectlist = []
        self.blankrectlist = []
        
        # This slightly speeds up drawText
        self.textDict = {}

        # Defaults (allows for back-projection, mirrors, rotation...)
        self.horizFlipped = False
        self.vertFlipped = False

    def blank(self,color=(0,0,0)):
        self.myScreen.fill(color)
        pygame.display.flip()

    def flipHorizontal(self):
        self.horizFlipped = not(self.horizFlipped)

    def flipVertical(self):
        self.vertFlipped = not(self.vertFlipped)

    def update(self):
        pygame.display.update(self.blankrectlist)
        pygame.display.update(self.rectlist)
        self.blankrectlist = self.rectlist
        self.rectlist = []

    def drawObject(self,imageObject,position):
        # draw an object centered on a position

        # handle screen flipping
        if self.horizFlipped:
            position = [self.horizSize-position[0],position[1]]
        if self.vertFlipped:
            position = [position[0],self.vertSize-position[1]]

        # Get around deprecation warnings:
        position = [int(round(position[0])),int(round(position[1]))]
       
        width,height = imageObject.get_size()
        posAdj = [round(position[0]+width/2),round(position[1]+height/2)]
        self.rectlist.append(self.myScreen.blit(pygame.transform.flip(imageObject,self.horizFlipped,self.vertFlipped),posAdj))

    def blankRects(self,color=(0,0,0)):
        for rect in self.blankrectlist:
            self.myScreen.fill(color,rect)

    def drawFix(self,color,position,radius,width=2):
        # draws a circle with a cross in the center
        self.drawCircle(color,position,radius,width)
        self.drawLine(color,[position[0]-radius,position[1]],
                 [position[0]+radius,position[1]],width)
        self.drawLine(color,[position[0],position[1]-radius],
                 [position[0],position[1]+radius],width)

    def drawCircle(self,color,position,radius,width=0):
        # draw a circle.  Filled by default; set width nonzero to leave empty

        # handle screen flipping
        if self.horizFlipped:
            position = [self.horizSize-position[0],position[1]]
        if self.vertFlipped:
            position = [position[0],self.vertSize-position[1]]
        
        # Get around deprecation warnings:
        position = [int(round(position[0])),int(round(position[1]))]
        radius = int(round(radius))
        width = int(round(width))
        
        self.rectlist.append(pygame.draw.circle(self.myScreen,color,\
                                                    position,radius,width))

    def drawLine(self,color,start_pos,end_pos,width=1):
        # draw a line.
                
        # handle screen flipping
        if self.horizFlipped:
            start_pos = [self.horizSize-start_pos[0],start_pos[1]]
            end_pos = [self.horizSize-end_pos[0],end_pos[1]]
        if self.vertFlipped:
            start_pos = [start_pos[0],self.vertSize-start_pos[1]]
            end_pos = [end_pos[0],self.vertSize-end_pos[1]]
        
        # Get around deprecation warnings:
        start_pos = [int(round(start_pos[0])),int(round(start_pos[1]))]
        end_pos = [int(round(end_pos[0])),int(round(end_pos[1]))]

        self.rectlist.append(pygame.draw.line(self.myScreen,color,\
                                                  start_pos,end_pos,width))

    def drawText(self,color,pos,text,defaultVertIsFlipped = True):
        """Draw (blit) text on the screen (self.screen). If cache is True, the
        text bitmap will be stored into textDict for reuse.
        """
        if not text in self.textDict:
            self.textDict[text] = self.font.render(text, 1, color)
        
        width,height = self.textDict[text].get_size()
        
        # handle screen flipping
        if self.horizFlipped:
            pos = [self.horizSize-pos[0],pos[1]]
        if self.vertFlipped:
            pos = [pos[0],self.vertSize-pos[1]]
        
        pos = [int(round(pos[0]))-width/2,int(round(pos[1]))-height/2]
        
        self.rectlist.append(self.myScreen.blit(pygame.transform.flip(self.textDict[text],
                                                                      self.horizFlipped,
                                                                      self.vertFlipped),
                                                pos))
        
    def close(self):
        # Cleanup
        pygame.display.quit()
