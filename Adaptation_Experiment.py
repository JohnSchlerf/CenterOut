# This implements a simple center-out reaching experiment.

# My code:
from devices.Clock import Clock
from devices.Cursor import Cursor
from devices.Monitor import Monitor

# Pygame:
import pygame
from pygame.locals import *

# These packages are fairly standard:
import os
import sys
import math
import random
import copy

#States:
STARTING = 0
WAITING = 1
WAIT_FOR_RT = 3
MOVING_EARLY = 4
MOVING_MIDPOINT = 5
MOVING = 10
FEEDBACK = 20
FINISHED = 99

# Figure out what subject name to use for data saving:
try:
    subname = sys.argv[1]
except IndexError:
    from dialog import MyDialog
    default = 'Subject'
    subname = MyDialog('Subject name (for data saving):',default)

def distance(tuple1,tuple2):
    # computes vector length from 2D tuple1 to tuple2
    return math.sqrt((tuple1[0]-tuple2[0])**2 +
                     (tuple1[1]-tuple2[1])**2)

def angle(tuple1,tuple2):
    # computes vecot angle from 2D tuple1 to tuple2
    return math.atan2((tuple1[1]-tuple2[1]),
                      (tuple1[0]-tuple2[0])) * 180 / math.pi

class Adaptation_Experiment:

    # target parameters:
    numTargets = 12
    targetDistance = 200 # pixels
    targetRadius = 10 # pixels
    targetColor = (128,128,0) # yellow
    holdTime = 0.2 # time in seconds before target appears
    
    # screen parameters
    width = 1024
    height = 768
    fullscreen = True

    # file locations
    dataDir = "Data"

    # onscreen cursor (a circle)
    cursorColor = (128,128,128) # ie, white
    cursorRad = 5 # radius in pixels

    # starting location
    fixRad = 15 # pixels
    fixWidth = 2 # pixels

    # feedback
    feedbackColor = (255,0,0) #red
    feedbackTime = 1 # seconds

    sampleRate = 100 # in Hz
    graphicsRate = 120 # in Hz; this is an "upper limit" across a trial

    # I'm going to store data into a Python dictionary to make this code readable.
    # Python dictionaries are not sorted in any particular order. Since I'd like
    # control over how values show up in the datafile, I need to enforce the order
    # with a list:
    datFileKeyOrder = ['blockNumber',
                       'trialNumber',
                       'startTime',
                       'rotation',
                       'cursorVisible',
                       'earlyAngle',
                       'midpointAngle',
                       'reactionTime',
                       'movementTime',
                       'targetX',
                       'targetY',
                       'targetAngle',
                       'targetDistance',
                       'startX',
                       'startY',
                       'earlyX',
                       'earlyY',
                       'earlyAngle',
                       'midpointX',
                       'midpointY',
                       'midpointAngle',
                       'finalX',
                       'finalY',
                       'finalAngle',
                       'feedbackX',
                       'feedbackY',
                       'feedbackAngle',
                       ]
    # Anything that is added outside this list will be appended at the end 
    # using whatever order Python chooses.

    # initial control flags:
    quitBlock = False
    quitExperiment = False
    blockRunning = False
    

    def __init__(self,subname):

        # Initialize data dictionary:
        self.defaultTrialDict = {}
        for key in self.datFileKeyOrder:
            self.defaultTrialDict[key] = -1

        self.screen = Monitor(self.width,self.height,self.fullscreen)

        self.centerX = self.width/2
        self.centerY = self.height/2

        self.cursor = Cursor((self.centerX,self.centerY))

        self.timer = Clock(5)
    
        self.subName = subname
        self.curBlock = 0

        # graphics flags:
        self.cursorOn = False
        self.cueOn = False
        self.targetOn = False
        self.fixOn = False
        self.feedbackOn = False

    def update(self):
        # check the clock and cursor:
        self.timer.update()
        self.cursor.update()

        # check keyboard events for quit signal:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.quitBlock = True
                elif event.key == K_END:
                    self.quitExperiment = True    

    def pol2rect(self,R,thetaDeg):
        # polar to rectangular conversion, assuming origin
        # of the polar axis is at centerX,centerY:
        X = self.centerX+R*math.cos(thetaDeg*math.pi/180)
        Y = self.centerY+R*math.sin(thetaDeg*math.pi/180)
        return (X,Y)

    def drawGraphics(self):
        self.screen.blankRects()
        
        # draw the "fixation" spot in the center:
        if self.fixOn:
            if (distance((self.cursor.DisplayX,self.cursor.DisplayY),
                        (self.centerX,self.centerY)) < self.fixRad) and not(self.targetOn):
                fixColor = (0,0,255)
            else: fixColor = (255,255,0)
            self.screen.drawFix(fixColor,(self.centerX,self.centerY),
                                self.fixRad,self.fixWidth)

        # The cursor can be invisible
        if self.cursorOn:
            self.screen.drawCircle(self.cursorColor,
                                   (self.cursor.DisplayX,
                                    self.cursor.DisplayY),
                                   self.cursorRad,0)

        # Sometimes I'll write some text near the center:
        if self.cueOn:
            self.screen.drawText(self.textColor,(self.centerX,self.centerY+50),self.cueText)
        
        # target
        if self.targetOn:
            self.screen.drawCircle(self.targetColor,
                                   (self.thisTrial['targetX']+self.thisTrial['startX'],
                                    self.thisTrial['targetY']+self.thisTrial['startY']),
                                   self.targetRadius,0)

        # feedback of final position
        if (self.feedbackOn):
            self.screen.drawCircle(self.feedbackColor,
                                   (self.thisTrial['feedbackX']+self.thisTrial['startX'],
                                    self.thisTrial['feedbackY']+self.thisTrial['startY']),
                                   self.cursorRad,0)

        self.screen.update()

    def writeAna(self,dataDict):
        # write the trial-by-trial summary datafile:
        datFileName = os.path.join(self.dataDir,self.subName+'.ana')
        if not(os.path.exists(datFileName)):
            datFileObj = open(datFileName,'w')
            # Write a header first

            # First thing, write all the data that I've coded above:
            keyList = list(dataDict.keys())
            for key in self.datFileKeyOrder:
                if key in keyList:
                    print(key)
                    datFileObj.write(str(key)+'\t')
                    keyList.remove(key)
            # Now write any data that I haven't explicitly ordered:
            for key in keyList:
                datFileObj.write(str(key)+'\t')
            # Write a newline:
            datFileObj.write('\n')
        else:
            datFileObj = open(datFileName,'a')
        
        # Now save the data, stepping through explicitly ordered keys first:
        for key in self.datFileKeyOrder:
            if key in dataDict.keys():
                datFileObj.write(str(dataDict[key])+'\t')
                del dataDict[key]
        # Now write any data that I haven't explicitly ordered:
        for key in dataDict.keys():
            datFileObj.write(str(dataDict[key])+'\t')
        
        # write a newline and close the file
        datFileObj.write('\n')
        datFileObj.close()

    def writeTrajectory(self,dataList,header = 'Trial:\n'):
        # Writes one trial at a time; trials could be rather long
        dataFile = open(os.path.join(self.dataDir,self.subName + '_' + str(self.curBlock).zfill(2) + '.mvt'),'a')
        if not('\n' in header):
            header = header + '\n'
        dataFile.write(header)
        for datum in dataList:
            try:
                for column in datum:
                    dataFile.write(str(column)+'\t')
            except:
                dataFile.write(str(datum))
            dataFile.write('\n')
        dataFile.write('\n')
        dataFile.close()

    def randomTarget(self,targetDistance = None):

        if not(targetDistance):
            # This allows for some flexibility later; not really necessary right now, though
            targetDistance = self.targetDistance 
        
        # Pick the target at random, and set all necessary positions:
        self.thisTrial['targetAngle'] = random.choice(range(self.numTargets))*(360.0/self.numTargets)
        self.thisTrial['targetDistance'] = targetDistance
        (self.thisTrial['targetX'], self.thisTrial['targetY']) = self.pol2rect(self.thisTrial['targetDistance'],
                                                                               self.thisTrial['targetAngle'])

    def runTrial(self,trial_number,rotation):

        # Coded as a functional example of a "slicing" movement
        self.thisTrial = copy.deepcopy(self.defaultTrialDict)
        self.thisTrial['rotation'] = rotation
        self.thisTrial['trialNumber'] = trial_number+1 # count from 1 to make data more human-readable
        self.thisTrial['blockNumber'] = self.curBlock
        self.thisTrial['startTime'] = self.timer[0]

        # May want to remove this later if trials are to be scripted:
        self.randomTarget()

        trialOver = False
        traj = []
        state = STARTING
        
        # Initialize graphics flags:
        self.cursorOn = True
        self.fixOn = True
        self.targetOn = False
        self.feedbackOn = False
        self.cueOn = False
        self.cursor.setRotation(self.thisTrial['rotation'])

        self.timer.reset(1)
        while not(trialOver) and not(self.quitBlock) and not(self.quitExperiment):
            self.update()

            # Save data at a fixed rate (keeps datafile sane)
            if self.timer[4] >= 1.0/self.sampleRate:
                traj.append([self.timer[1], state, 
                             self.cursor.CurrentX, self.cursor.CurrentY, 
                             self.cursor.DisplayX, self.cursor.DisplayY])
                # Rather than resetting timer 4, I want to allow for some jitter:
                self.timer[4] = self.timer[4] - 1.0/self.sampleRate
            
            # Update graphics at a fixed rate (avoids overhead)
            if self.timer[3] >= 1.0/self.graphicsRate:
                self.drawGraphics()
                # Rather than resetting timer 3, I want to allow for some jitter:
                self.timer[3] = self.timer[3] - 1.0/self.graphicsRate
            
            #######################################################################
            # Trial state machine:
            if state == STARTING:
                # wait for the cursor to be in the fixation spot:
                if self.cursor.VisualDisplacement < self.fixRad:
                    self.timer.reset(2)
                    state = WAITING
            elif state == WAITING:
                # wait an appropriate amount of time in the fixation spot
                if self.timer[2] >= self.holdTime:
                    self.timer.reset(2)
                    self.targetOn = True
                    state = WAIT_FOR_RT
            elif state == WAIT_FOR_RT:
                # wait for subject to start moving
                if self.cursor.VisualDisplacement < self.fixRad:
                    self.thisTrial['reactionTime'] = self.timer[2]
                    self.timer.reset(2)
                    state = MOVING_EARLY
            elif state == MOVING_EARLY:
                # wait for the cursor to cross 1/4 of target distance, save position
                if self.cursor.VisualDisplacement >= self.targetDistance / 4.0:
                    self.thisTrial['earlyTime'] = self.timer[2]
                    self.thisTrial['earlyX'] = self.cursor.CurrentX
                    self.thisTrial['earlyY'] = self.cursor.CurrentY
                    self.thisTrial['earlyAngle'] = math.atan2(self.cursor.CurrentY,self.cursor.CurrentX)
                    state = MOVING_MIDPOINT
            elif state == MOVING_MIDPOINT:
                # wait for the cursor to cross 1/2 of target distance, save position
                if self.cursor.VisualDisplacement >= self.targetDistance / 2.0:
                    self.thisTrial['midpointTime'] = self.timer[2]
                    self.thisTrial['midpointX'] = self.cursor.CurrentX
                    self.thisTrial['midpointY'] = self.cursor.CurrentY
                    self.thisTrial['midpointAngle'] = math.atan2(self.cursor.CurrentY,self.cursor.CurrentX)
                    state = MOVING
            elif state == MOVING:
                # wait for the cursor to cross target distance, save position
                if self.cursor.VisualDisplacement >= self.targetDistance:
                    self.thisTrial['movementTime'] = self.timer[2]
                    self.thisTrial['finalX'] = self.cursor.CurrentX
                    self.thisTrial['finalY'] = self.cursor.CurrentY
                    self.thisTrial['finalAngle'] = math.atan2(self.cursor.CurrentY,self.cursor.CurrentX)
                    self.thisTrial['feedbackX'] = self.cursor.DisplayX
                    self.thisTrial['feedbackY'] = self.cursor.DisplayY
                    state = FEEDBACK
                    self.timer.reset(2)
                    self.feedbackOn = True
            elif state == FEEDBACK:
                if self.timer[2] >= self.feedbackTime:
                    state = FINISHED
                    trialOver = True

        return [self.thisTrial, traj]

    def runBlock(self, numTrials):
        # This is a bit simplistic; should be enhanced to use script files for a proper experiment.
        if self.curBlock%2==0:
            if random.random() > 0.5: rotation = 45
            else: rotation = -45
        else:
            rotation = 0

        for trial_number in range(numTrials):
            [trialData,traj] = self.runTrial(trial_number,rotation)
            # write the trajectory information after every trial to keep memory cost low
            self.writeAna(trialData)
            self.writeTrajectory(traj,'Trial '+str(trial_number)+':')
            if self.quitExperiment or self.quitBlock: break

        self.screen.blank()
 
    def run(self):
        # This is basically a "demo mode" for running blocks of trials, as things are not super controlled.
        # It will run blocks of 24 trials each. Every odd block will have no perturbation; even blocks will
        # have a 45 degree clockwise or counterclockwise rotation imposed (selected at random).

        # Run blocks until the end button is pressed:
        while not(self.quitExperiment):
            self.screen.drawText((255,255,255),(self.centerX,self.centerY-50),
                                 'Welcome, ' + self.subName)
            self.screen.drawText((255,255,255),(self.centerX,self.centerY),
                                 'Press <SPACE> to begin, <END> to quit')
            self.screen.drawText((255,255,255),(self.centerX,self.centerY+50),
                                 'You have run ' + str(self.curBlock) + ' blocks.')
            self.screen.update()
            
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.quitExperiment = True
                    elif event.key == K_END:
                        self.quitExperiment = True
                    elif event.key == K_SPACE:
                        self.curBlock += 1
                        self.runBlock(24)

        self.screen.close()

Adaptation_Experiment(subname).run()

