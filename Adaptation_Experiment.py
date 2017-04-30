# This implements a simple center-out reaching experiment.

# My code:
from devices.Clock import Clock
from devices.Cursor import Cursor
from devices.Monitor import Monitor
from dialog import get_name, get_target_files

# Pygame:
import pygame
from pygame.locals import *

# These packages are fairly standard:
import os
import sys
import math
import random
import copy
import pandas as pd

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
    participant_name = sys.argv[1]
except IndexError:
    default = 'Volunteer'
    participant_name = get_name('Participant name (for data saving):', default)


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

    # I'm going to store data into a Python dictionary to make this code 
    # readable. The keys in Python dictionaries are not sorted in any 
    # particular order. Since I'd like control over how values show up in
    # the datafile, I need to enforce the order with a list:
    datFileKeyOrder = [
        'blockNumber',
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


    def __init__(self, subname):

        # Figure out the blocks to run:
        self.block_list = get_target_files()

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


    def pol2rect(self, r, theta_deg):
        """Convert from polar to rectangular coordinates

        Assumes the origin of the polar axis should be at centerX,
        centerY in Cartesian space.

        Parameters
        ----------
        r : float
            The radius, in pixels, from the center of the screen

        theta_deg : float
            The angle, in degrees, from horizontal

        Returns
        -------
        (x, y) : float
            Returns cartesian coordinates in screen space, where a
            radius of 0 is always at the center of the screen
        """
        x = self.centerX + r * math.cos(theta_deg * math.pi / 180.0)
        y = self.centerY + r * math.sin(theta_deg * math.pi / 180.0)
        return (x, y)


    def rect2pol(self, x, y):
        """Convert from rectangular coordinates to polar

        Parameters
        ----------
        (x, y) : numeric
            Cartesian coordinates, relative to the center of the screen.

        Returns
        r : float
            The radius, in pixels, from the center of the screen

        theta_deg : float
            The angle, in degrees, from horizontal
        """
        r = (x**2 + y**2)**0.5
        theta_deg = math.atan2(y, x) * 180.0 / math.pi
        return (r, theta_deg)


    def drawGraphics(self):
        """Routine to update graphics
        """
        self.screen.blankRects()
        # draw the "fixation" spot in the center:
        if self.fixOn:
            current_dist = distance(
                (self.cursor.DisplayX, self.cursor.DisplayY),
                (self.centerX, self.centerY)
            )
            if current_dist < self.fixRad and not(self.targetOn):
                fixColor = (0,0,255)
            else: 
                fixColor = (255,255,0)
            self.screen.drawFix(
                fixColor,
                (self.centerX, self.centerY),
                self.fixRad,
                self.fixWidth
            )
        # The cursor can be invisible
        if self.cursorOn:
            self.screen.drawCircle(
                self.cursorColor,
                (self.cursor.DisplayX, self.cursor.DisplayY),
                self.cursorRad,
                0
            )
        # Sometimes I'll write some text near the center:
        if self.cueOn:
            self.screen.drawText(
                self.textColor,
                (self.centerX, self.centerY + 50),
                self.cueText
            )
        # target
        if self.targetOn:
            self.screen.drawCircle(
                self.targetColor,
                (
                    self.thisTrial['targetX'] + self.thisTrial['startX'],
                    self.thisTrial['targetY'] + self.thisTrial['startY']
                ),
                self.targetRadius,
                0
            )
        # feedback of final position
        if (self.feedbackOn):
            self.screen.drawCircle(
                self.feedbackColor,
                (
                    self.thisTrial['feedbackX'] + self.thisTrial['startX'],
                    self.thisTrial['feedbackY'] + self.thisTrial['startY']
                ),
                self.cursorRad,
                0
            )
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
        dataFile = open(
            os.path.join(
                self.dataDir,
                self.subName + '_' + str(self.curBlock).zfill(2) + '.mvt'
                ),
            'a'
            )
        if not('\n' in header):
            header = header + '\n'
        dataFile.write(header)
        for datum in dataList:
            try:
                for column in datum:
                    dataFile.write(str(column) + '\t')
            except:
                dataFile.write(str(datum))
            dataFile.write('\n')
        dataFile.write('\n')
        dataFile.close()


    def randomTarget(self, target_distance = None):

        if not(target_distance):
            # This allows for some flexibility later;
            # not really necessary right now, though
            target_distance = self.targetDistance 

        # Pick the target at random, and set all necessary positions:
        self.thisTrial['targetAngle'] = \
            random.choice(range(self.numTargets)) * (360.0/self.numTargets)
        self.thisTrial['targetDistance'] = target_distance
        (self.thisTrial['targetX'], self.thisTrial['targetY']) = \
            self.pol2rect(
                self.thisTrial['targetDistance'],
                self.thisTrial['targetAngle']
            )


    def runTrial(self, trial_number, trial_data):
        """Run a single trial

        Parameters
        ----------
        trial_number : int
            The trial number. More for bookkeeping than anything else.

        trial_data : dict
            A dictionary of parameters for this trial. Parameters supported:
                rotation - numeric (optional)
                    A rotation perturbation to apply to the cursor. If not supplied, we'll use 0.
                target_angle - numeric (optional)
                    The angle of the target, in degrees. Has precedence over supplying X/Y coordinates.
                target_distance - numeric (optional)
                    The distance of the target, in pixels. If not supplied, defaults to the set distance.
                target_x, target_y - numeric (optional)
                    The x- and y-coordinates of the target. Ignored if target_angle is set.

            NOTE: If no target information is supplied, a target will be selected at random.

        Returns
        -------
        ana_dict : dict
            A dictionary summary of the events in the trial.

        trajectory : list
            A list of values that make up the full trajectory. Each row is a single sample.
        """
        # Coded as a functional example of a "slicing" movement
        self.thisTrial = copy.deepcopy(self.defaultTrialDict)
        if 'rotation' in trial_data:
            self.thisTrial['rotation'] = trial_data['rotation']
        else:
            self.thisTrial['rotation'] = 0
        # count from 1 to make data more human-readable
        self.thisTrial['trialNumber'] = trial_number + 1
        self.thisTrial['blockNumber'] = self.curBlock
        self.thisTrial['startTime'] = self.timer[0]

        # May want to remove this later if trials are to be scripted:
        #self.randomTarget()
        if 'target_angle' in trial_data:
            self.thisTrial['targetAngle'] = trial_data['target_angle']
            if 'target_distance' in trial_data:
                self.thisTrial['targetDistance'] = trial_data['target_distance']
            else:
                self.thisTrial['targetDistance'] = self.targetDistance
            self.thisTrial['targetX'], self.thisTrial['targetY'] = \
                self.pol2rect(
                    self.thisTrial['targetDistance'],
                    self.thisTrial['targetAngle']
                )
        elif 'target_x' in trial_data:
            self.thisTrial['targetX'] = trial_data['target_x']
            self.thisTrial['targetY'] = trial_data['target_y']
            self.thisTrial['targetAngle'], self.thisTrial['targetDistance'] = \
                self.rect2pol(
                    self.thisTrial['targetX'], self.thisTrial['targetY']
                    )
        else:
            # If no target is defined, then pick one at random:
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
        while not(trialOver) \
            and not(self.quitBlock) \
            and not(self.quitExperiment):
            self.update()

            # Save data at a fixed rate (keeps datafile sane)
            if self.timer[4] >= 1.0/self.sampleRate:
                traj.append([self.timer[1], state, 
                             self.cursor.CurrentX, self.cursor.CurrentY, 
                             self.cursor.DisplayX, self.cursor.DisplayY])
                # Rather than resetting timer 4, I want to allow jitter:
                self.timer[4] = self.timer[4] - 1.0/self.sampleRate

            # Update graphics at a fixed rate (avoids overhead)
            if self.timer[3] >= 1.0/self.graphicsRate:
                self.drawGraphics()
                # Rather than resetting timer 3, I want to allow jitter:
                self.timer[3] = self.timer[3] - 1.0/self.graphicsRate
            ################################################################
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
                # wait for the cursor to cross 1/4 of target distance,
                # save position
                if self.cursor.VisualDisplacement >= self.targetDistance / 4.0:
                    self.thisTrial['earlyTime'] = self.timer[2]
                    self.thisTrial['earlyX'] = self.cursor.CurrentX
                    self.thisTrial['earlyY'] = self.cursor.CurrentY
                    self.thisTrial['earlyAngle'] = \
                        math.atan2(self.cursor.CurrentY, self.cursor.CurrentX)
                    state = MOVING_MIDPOINT
            elif state == MOVING_MIDPOINT:
                # wait for the cursor to cross 1/2 of target distance,
                # save position
                if self.cursor.VisualDisplacement >= self.targetDistance / 2.0:
                    self.thisTrial['midpointTime'] = self.timer[2]
                    self.thisTrial['midpointX'] = self.cursor.CurrentX
                    self.thisTrial['midpointY'] = self.cursor.CurrentY
                    self.thisTrial['midpointAngle'] = \
                        math.atan2(self.cursor.CurrentY, self.cursor.CurrentX)
                    state = MOVING
            elif state == MOVING:
                # wait for the cursor to cross target distance, save position
                if self.cursor.VisualDisplacement >= self.targetDistance:
                    self.thisTrial['movementTime'] = self.timer[2]
                    self.thisTrial['finalX'] = self.cursor.CurrentX
                    self.thisTrial['finalY'] = self.cursor.CurrentY
                    self.thisTrial['finalAngle'] = \
                        math.atan2(self.cursor.CurrentY, self.cursor.CurrentX)
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


    def runBlock(self, target_file):
        """Run a block

        Parameters
        ----------
        target_file : string
            The path to a target file. This is expected to be a comma separated file with one line for each trial.
            When all trials have been run, the block will be considered done.
        """
        try:
            all_trials = pd.read_csv(target_file)
        except:
            # Something seems to have gone wrong with the target file. COULD run a demo block if you like.
            print("Something is wrong with the input target file...")
            # Uncomment this next line to run a demo block:
            #self.runBlockDemo()
            return

        for trial_number in range(all_trials.shape[0]):
            [ana_data, trajectory_data] = self.runTrial(
                trial_number, dict(all_trials.iloc[trial_number, :])
                )
            # Write out data after every trial to avoid losing data.
            self.writeAna(ana_data)
            self.writeTrajectory(trajectory_data, 'Trial %i:' % (trial_number))
            if self.quitExperiment or self.quitBlock:
                break

        self.screen.blank()


    def runBlockDemo(self, num_trials=24):
        # Old version; just runs 24-trial blocks, with random +/- 45 degree rotation each time.
        if self.curBlock%2==0:
            if random.random() > 0.5: rotation = 45
            else: rotation = -45
        else:
            rotation = 0

        for trial_number in range(num_trials):
            [trial_data, traj] = self.runTrial(trial_number, {'rotation':rotation})
            # write the trajectory information after every trial to
            # keep memory cost low
            self.writeAna(trial_data)
            self.writeTrajectory(traj, 'Trial ' + str(trial_number) + ':')
            if self.quitExperiment or self.quitBlock:
                break

        self.screen.blank()

    def run(self):

        # Run the selected blocks. Allow an abort if the END button is pressed:
        while not(self.quitExperiment):
            self.screen.drawText(
                (255, 255, 255),
                (self.centerX, self.centerY - 50),
                'Welcome, ' + self.subName
                )
            self.screen.drawText(
                (255, 255, 255),
                (self.centerX, self.centerY),
                'Press <SPACE> to begin, <END> or <ESC> to quit'
                )
            self.screen.drawText(
                (255, 255, 255),
                (self.centerX, self.centerY + 50),
                'You have run ' + str(self.curBlock) + ' blocks.'
                )
            self.screen.update()

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.quitExperiment = True
                    elif event.key == K_END:
                        self.quitExperiment = True
                    elif event.key == K_SPACE:
                        target_file = self.block_list[self.curBlock]
                        self.curBlock += 1
                        self.runBlock(target_file)


            if self.curBlock >= len(self.block_list):
                self.screen.drawText(
                    (255, 255, 255),
                    (self.centerX, self.centerY - 50),
                    "Thank you, " + self.subName + "!"
                    )
                self.screen.drawText(
                    (255, 255, 255),
                    (self.centerX, self.centerY),
                    "You are now done."
                    )
                self.screen.update()
                # The above "thank you" message will disappear quickly unless you introduce a pause:
                self.timer.reset(1)
                while self.timer[1] < 1:
                    self.timer.update()
                self.quitExperiment = True

        self.screen.close()


if __name__ == "__main__":
    Adaptation_Experiment(participant_name).run()

