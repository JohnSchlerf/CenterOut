import math

# Import the appropriate "MotionHardware" class
from UseMouse import MotionHardware
# Could be expanded for additional plugins.

class Cursor:
    """
    2D Cursor class.
    """

    # Handle some simple world-to-graphics values. These can be perturbed to
    # require adaptation (learning).
    CurrentRotation = 0
    CurrentRotationRad = 0
    HorizontalMapping = 1
    VerticalMapping = 1

    def __init__(self,CenterPos=(1024/2,768/2),HomePos=None):
        # Create the cursor, start everything at the middle value.

        self.CenterX = CenterPos[0]
        self.CenterY = CenterPos[1]

        # Using a mouse (which can be picked up and moved), this is 
        # redundant. Using something with a one-to-one mapping 
        # between physical position and reported position (IE, 
        # motion capture device, tablets), this is important as it 
        # specifies the "hardware" location of the center.
        if not (HomePos):
            self.homeX = CenterPos[0]
            self.homeY = CenterPos[1]
        else:
            self.homeX = HomePos[0]
            self.homeY = HomePos[1]

        self.CurrentX = self.CenterX
        self.CurrentY = self.CenterY

        self.DisplayX = self.CenterX
        self.DisplayY = self.CenterY

        # Initialize motion hardware (mouse, motion tracker, etc)
        self.hardware = MotionHardware(self.homeX,self.homeY)
	
    def invertY(self):
        # Allows y-axis to be inverted (up moves down):
        self.VerticalMapping *= -1
    
    def invertX(self):
        # Allows x-axis to be inverted (left moves right):
        self.HorizontalMapping *= -1

    def setGain(newXgain,newYgain=None):
        # Allows for cursor gain manipulations and affords calibration
        # from mm to pixels on certain displays.

        # default is isotropic:
        if not(newYgain): newYgain = newXgain

        # Preserve flipping for convenience
        self.HorizontalMapping = math.copysign(newXgain, self.HorizontalMapping)
        self.VerticalMapping = math.copysign(newYgain, self.VerticalMapping)

    def update(self):

    	# Hardware update
        self.hardware.Update()

        # In a perfect world, this would be the horizontal and vertical 
        # distance in mm from home:
        self.CurrentX = self.hardware.getRelX()
        self.CurrentY = self.hardware.getRelY()

        # Compute where the visual cursor should be:
        dX_Vis = self.CurrentX*self.HorizontalMapping
        dY_Vis = self.CurrentY*self.VerticalMapping

        # Implement rotation:
        self.DisplayX = int(round(self.CenterX + \
            dX_Vis*math.cos(self.CurrentRotationRad) - \
            dY_Vis*math.sin(self.CurrentRotationRad)))
        self.DisplayY = int(round(self.CenterY + \
            dX_Vis*math.sin(self.CurrentRotationRad) + \
            dY_Vis*math.cos(self.CurrentRotationRad)))
        
        # Distance is very handy in these experiments, so compute it:
        self.VisualDisplacement = math.sqrt(dX_Vis**2 + dY_Vis**2)

    def setRotationDeg(self,newRotation):
        # set the cursor rotation in degrees
        self.CurrentRotation = newRotation
        self.CurrentRotationRad = newRotation * math.pi / 180

    def setRotationRad(self,newRotationRad):
        # set the cursor rotation in radians
        self.CurrentRotationRad = newRotationRad
        self.CurrentRotation = newRotationRad * 180 / math.pi

    def setRotation(self,newRotation):
        # legacy behavior; assume degrees
        self.setRotationDeg(newRotation)

    def setCenter(self,newCenterX,newCenterY=None):
        # change the position of the graphical center
        if len(newCenterX) == 2:
            newCenterY = newCenterX[1]
            newCenterX = newCenterX[0]
        self.CenterX = newCenterX
        self.CenterY = newCenterY

    def setHome(self,newHomeX,newHomeY=None):
        # change the position of the hardware center
        if len(newHomeX) == 2:
            newHomeY = newHomeX[1]
            newHomeX = newHomeX[0]
        self.homeX = newHomeX
        self.homeY = newHomeY
        self.hardware.setHome(self.homeX,self.homeY)

    def reCenter(self):
        # recenter the cursor on the current location
        self.DisplayX = self.CenterX
        self.DisplayY = self.CenterY
        # Use current hardware position as home:
        [self.homeX, self.homeY] = self.hardware.reHome()

    def getHomePosition(self):
    	return (self.homeX,self.homeY)
