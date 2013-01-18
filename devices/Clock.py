import os
# Use the most accurate clock.
# Tested on Windows XP and Linux.
if os.name == 'nt':
    from time import clock as CurrentTime
    import time
    ADJUST_FOR_EPOCH = time.time()
else:
    from time import time as CurrentTime
    ADJUST_FOR_EPOCH = 0

class Clock:
    # Multiple calls to time has a slowing effect. A better solution is
    # to use one master timer, with multiple synchronized "stopwatches".
    # This is a concept I learned from Joern Diedrichsen; the Python
    # implementation is my own.

    def __init__(self,numTimers):
        # Must initialize with a few stopwatches
        self.timers = []
        for i in range(numTimers):
            self.timers.append(0.0)
        self.resetAll()

    def __getitem__(self,key):
        # Allow stopwatches to be called directly for convenience
        return self.timers[key]

    def __setitem__(self,key,value):
        # Allow stopwatches to be set directly for convenience
        self.timers[key] = value

    def update(self):
        # This is the master updater, makes sure that I only query
        # time once.
        self.dt = CurrentTime()+ADJUST_FOR_EPOCH - self.lastTime
        self.lastTime += self.dt
        for i in range(len(self.timers)):
            self.timers[i] += self.dt
        
    def reset(self,whichTimer):
        # Reset individual stopwatches
        self.timers[whichTimer] = 0.0

    def resetAll(self):
        # Reset all stopwatches and the master clock.
        self.initialTime = CurrentTime()+ADJUST_FOR_EPOCH
        self.lastTime = self.initialTime
        self.dt = 0
        for i in range(len(self.timers)):
            self.timers[i] = 0.0
