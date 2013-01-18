# Mouse module for Cursor class.
# Uses pygame.
# Could be re-implemented for other hardware.
import pygame

class MotionHardware:

    def __init__(self, homeX, homeY):
        # Since this is just a mouse, this is trivial. Other hardware
        # may need hardware initialization code here (query serial
        # port, etc.)     
        self.homeX = homeX
        self.homeY = homeY
        self.currentX = homeX
        self.currentY = homeY

    def Update(self):
        # Since this is just a mouse, update it with the change since
        # the last update. Doing it this way is important, because I
        # expect that the actual mouse cursor will not be visible in
        # most use-cases:
        [dX,dY] = pygame.mouse.get_rel()

        # In a perfect world, I would make sure that currentX and
        # currentY were always in mm. But I'm ignoring that since 
        # we're using a mouse.
        self.currentX += dX
        self.currentY += dY

    def getRelX(self):
        # return distance along X to home position
        return self.currentX - self.homeX

    def getRelY(self):
        # return distance along Y to home position
        return self.currentY - self.homeY

    def setHome(self,newHomeX,newHomeY):
        # adjust "hardware center"
        self.homeX = newHomeX
        self.homeY = newHomeY

    def reHome(self):
        # adjust "hardware center" to current
        self.homeX = self.currentX
        self.homeY = self.currentY
        # Return the home position for bookkeeping
        return [self.homeX, self.homeY]
