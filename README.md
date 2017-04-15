CenterOut
=========

This is an experimental task for movement learning experiments. Use a mouse to reach to different targets. Implemented in Python and PyGame.

## Dependencies

This code requires Python3 (tested using Anaconda3 4.3.1) and Pygame.
Anaconda is the preferred method of installation, and should contain most packages:

[Install Anaconda from Continuum's site](https://www.continuum.io)

The exception is Pygame, which can be installed using pip:

`pip install pygame`

## Running

Running the Python script `AdaptationExperiment.py` should give you a simple dialog to enter the subject's name.
The task will then proceed block by block, with the experimenter/subject prompted to proceed.
Each trial is started and ended by returning the cursor to the central cross-hair.

The number of trials, the targets, and the block order can be specified by setting the right values within `AdaptationExperiment.py` itself.

## Output

Data will be saved in the `Data` subfolder as text files. There are two types of files:

* .ANA files
* .MVT files

The .ana files contain a summary of the entire experimental session for the subject, by block and trial.

The .mvt files each contain the trials for a single block, as a timeseries of trajectories.
