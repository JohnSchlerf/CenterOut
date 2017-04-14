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
    """Class for timers

    In general, calls to the built-in time class can stop the iteration
    of your program and slow things down. Maintaining multiple timers is
    something that you often want, so this simplifies that while minimizing
    calls to the built-in time functions.

    Original inspiration for this concept came from Joern Diedrichsen.
    """
    def __init__(self, num_timers=10):
        """Initialize a set of synchronized timers, all set at 0

        Parameters
        ----------
        num_timers : int (optional)
            The number of timers to maintain. Default is 10.
        """
        self.timers = []
        for _ in range(num_timers):
            self.timers.append(0.0)
        self.resetAll()


    def __getitem__(self, which_timer):
        """Return the value of the appropriate timer

        Note that Python counts from 0.

        Example:
        --------
        >>> myTimers = Clock(10)
        >>> print(myTimers[0], myTimers[1], myTimers[2])
        0.0, 0.0, 0.0
        """
        return self.timers[which_timer]


    def __setitem__(self, which_timer, value):
        """Allows stopwatches to be set directly for convenience

        Example:
        --------
        >>> myTimers = Clock(10)
        >>> myTimers[0] = 0.0
        >>> myTimers[1] = 1.0
        >>> myTimers[2] = 2.0
        >>> print(myTimers[0], myTimers[1], myTimers[2])
        0.0, 1.0, 2.0
        """
        self.timers[which_timer] = value


    def update(self):
        """Updates all timers with a single call to time

        Example:
        --------
        >>> myTimers = Clock(10)
        >>> orig_0 = myTimers[0]
        >>> orig_1 = myTimers[1]
        >>> myTimers.update()
        >>> print((myTimers[0] - orig_0) == (myTimers[1] - orig_1))
        True
        >>> myTimers.update()
        >>> print((myTimers[0] - orig_0) == (myTimers[1] - orig_1))
        True
        >>> myTimers[1] = 0.0
        >>> myTimers.update()
        >>> print((myTimers[0] - orig_0) == (myTimers[1] - orig_1))
        False
        """
        # First make a call to time and compute the update (dt):
        self.dt = CurrentTime() + ADJUST_FOR_EPOCH - self.lastTime
        # Now update the last time to keep the next dt accurate:
        self.lastTime += self.dt
        # Finally, update all the timers we're keeping track of:
        for i in range(len(self.timers)):
            self.timers[i] += self.dt
        
        
    def reset(self, which_timer):
        # Reset individual stopwatches
        self.timers[which_timer] = 0.0

    
    def resetAll(self):
        # Reset all stopwatches and the master clock.
        self.initialTime = CurrentTime()+ADJUST_FOR_EPOCH
        self.lastTime = self.initialTime
        self.dt = 0
        for i in range(len(self.timers)):
            self.timers[i] = 0.0
