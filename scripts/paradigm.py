from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB']
from psychopy import visual, core, sound, event, gui, logging #, parallel
import numpy as np
import random as rnd
import os
from triggers import setParallelData
setParallelData(0)

###### set project driectory automatically relative to script dir ##############
my_path = os.path.abspath(os.path.dirname(__file__))
os.chdir(my_path)
os.chdir('..')
log_dir = 'logs/'

################## Stimulus list and randomization #############################
ntrials = 200 # number of trials per block 
bnames = ['con1','con2', 'inc1', 'inc2'] # congruent and incongruent block names
stdev = [[1,2],[2,1],[1,2],[2,1]] # define local standard [0] and deviant [1]
gprobs = [0.75,0.75,0.25,0.25] # global probability of local standard

blocks = {}
for bidx, bname in enumerate(bnames):
    blocks[bname] = {} # initialize current block
    cur_stdev = stdev[bidx] # get current mapping of standard and deviant
    prime = [cur_stdev[0]]*4 # first four sounds of the sequence
    tlist, triggers = [], [] # initialize trial list

    # set number of patterns for standard or deviant:
    for sdidx, sd in enumerate(cur_stdev):
        cur_n = np.round(np.abs(sdidx - gprobs[bidx]) * ntrials).astype(int) #How many?
        tlist = tlist + [prime + [sd]] * cur_n # add to trial list
        triggers = triggers + [(bidx + 1) * 10 + sdidx + 1] * cur_n # add to trigger list
        
    tlist = tlist + [prime + [3]] * 10 # add target tones to block
    triggers = triggers + [100] * 10 # add target triggers to block
    
    # Let's randomize and make sure no two target sounds are played consecutively
    trial_idx = np.arange(len(triggers)).astype('int64') # trial index
    
    # While consecutive targets, randomize again:
    probe = None
    while probe == None:
        rnd.shuffle(trial_idx)
        if 1 in np.diff(np.where(np.array(triggers)[trial_idx] == 100)):
           probe = None
        else:
           probe = True
    #print(trial_idx)

    #update and store trial and trigger list:
    blocks[bname]['tlist'] = [tlist[t] for t in trial_idx]
    blocks[bname]['triggers'] = [triggers[t] for t in trial_idx]

practice_seq = [[1,1,1,1,2],[1,1,1,1,2],[1,1,1,1,1],[1,1,1,1,1],
                [1,1,1,1,2],[1,1,1,1,1],[1,1,1,1,2]]

######################## Create sound stimuli ##################################

fs = 48000 # sampling frequency
heights = np.array([-4,0,10]) # tone steps
steps = 2**(heights*(1/12)) # well tempered scaled
freqs = steps*440; # center around 440
print('current stimulus F0: {}'.format(np.round(freqs,2)))
dur = 0.08 # duration of the tone
t = np.linspace(0, dur, int(dur * fs), False) # create times for sound wave
attenuation = np.flip(np.arange(0,1,1/1600))# create decay attenuation
# create complex tones with 5 harmonics and decreasing power:
tones = [np.sin(f * t * 2 * np.pi)*0.3 + 
         np.sin(f * t * 2 * np.pi*2)*0.25 +
         np.sin(f * t * 2 * np.pi*3)*0.2 +
         np.sin(f * t * 2 * np.pi*4)*0.15 +
         np.sin(f * t * 2 * np.pi*5)*0.1 for f in freqs] 

# add decay:
for nidx,n in enumerate(tones):
    n[(len(n)-1600):] = n[(len(n)-1600):]*attenuation
    tones[nidx] = n

sounds = [sound.Sound(value = tone,sampleRate = fs,hamming = True) for tone in tones]

########################## Setup Psychopy task #################################
# define quit function:
def quit_exp():
    win.close()
    logging.flush()
    core.quit()

# create quit key:
event.globalKeys.add(key='escape', func = quit_exp, name='shutdown')
keyNext = 'space' # set key to advance

# define and counterbalance conditions:
conds = list(blocks.keys())
rnd.shuffle(conds) # randomize condition order

blocks_msg = ('current block order is ' + conds[0] + ', ' + conds[1] + ', ' + conds[2] + 
             ', ' + conds[3] + '.\nLeave blank if you agree.\nElse, type the blocks ' +
             'to include in the desired order,\n' + 
             'separated by commas:')

# get subject info:
ID_box = gui.Dlg(title = 'Subject identity')
ID_box.addField('ID: ')
ID_box.addField(blocks_msg)
ID_box.addField('practice? (YES: 1 or blank; NO: 0): ')

sub_id = ID_box.show()
if len(sub_id[1])>2:
   conds = sub_id[1].split(',')

practice_switch = 1
if len(sub_id[2])>0:
    if int(sub_id[2]) < 1:
        practice_switch = 0

#create a window
color = 'white'
win = visual.Window(fullscr=True, color='black')

#set screen refresh rate
frate = np.round(win.getActualFrameRate())
prd = 1000 / frate
print('screen fps = {} / cycle duration = {} ms'.format(frate, np.round(prd,2)))

fixationCross = visual.TextStim(win, text='+', color=color, height=0.2)
############### Set instructions and other relevant texts  #####################
Instructions = visual.TextStim(win, text='In the following, you will hear a sequence '
                                        'of short sound patterns.\n'
                                        'At certain points in the sequence, '
                                        'a high-pitched sound outlier will be played.\n'
                                        'Your task is to listen attentively to the '
                                        'sequence and press the button as soon as you '
                                        'hear the high-pitched outlier.\n\n'
                                        'Please answer as fast as you can!\n\n'
                                        'Press any button to start the experiment',
                                        color=color, wrapWidth=1.8)

practiceStart = visual.TextStim(win, text='First, let us do some practice trials\n\n'
                                          'Be careful! sometimes the last tone may '
                                          'sound like an outlier but it is not different '
                                          'enough. Make sure your chosen outlier '
                                          'has a clearly different very high pitch.\n\n'
                                          'Press any button to begin',
                                          color=color, wrapWidth=1.8)

practiceEnd = visual.TextStim(win, text='That was the end of the practice.\n'
                                        'We will continue in a moment with the real task.\n '
                                        'During the experiment, please always look at the '
                                        'white cross (+) in the middle.',
                                         color=color, wrapWidth=1.8)

nextText = visual.TextStim(win, text='(press any button to continue)',
                           color=color, pos=(0, -0.8))
continueTxt =['This is the end of the block {}!\n Now take a little break '
             'press a button to continue when ready.']
endTxt = ['This is the end of the block {} and the experiment!\n Thank you for participating!']

############### Define other relevant variables ################################

#create a silent sound for buffer issues:
silentDur = .5
silent = sound.Sound('C', secs=silentDur, volume=0)

# set relevant clocks:
RT = core.Clock()
block_time = core.Clock()
practice_time = core.Clock()

# setup logging file
logging.setDefaultClock(block_time)
filename = log_dir + sub_id[0] +  '.log'
lastLog = logging.LogFile(filename, level=logging.INFO, filemode='a')

############ Create functions to present stimuli ##############################

def practice(practice_seq):
    
    practiceStart.draw()
    nextText.draw()
    win.flip()
    event.waitKeys()
    
    fixationCross.draw()
    win.flip()
    
    dev_patterns = np.array([5,11,17]) # index of the patterns with outliers
    silent.play()  # to prevent omission/cut of the first stimulus
    core.wait(silentDur)
    
    ## we will run practice trials until participants identify the outliers properly:
    block_time.reset()
    pdone = None
    while pdone == None:
        dev_times = [] # list to store time of outlier presentation
        event.clearEvents(eventType='keyboard') # initialize keypress record
        practice_time.reset() # reset time for this chunk of trials
        for a in range(20): # we will allow 20 trials per practice chunk
            
            cur_pattern = practice_seq[a % len(practice_seq)].copy() # copy practice pattern
            #if the patten must have an outlier, change the last tone for target:
            if np.isin(a,dev_patterns):
               cur_pattern[4] = 3
            
            #loop over sounds in pattern and play:
            for midx, ts in enumerate(cur_pattern): 
                sounds[ts-1].name = 'practice' + '_' + str(ts)
                sounds[ts-1].play()
                #if there is a deviant in 5th position, record onset time:
                if (midx == 4) & (cur_pattern[4] == 3):
                   dev_times.append(practice_time.getTime())                
                core.wait(0.0999)# wait until next onset
            core.wait(0.4999) #wait until next pattern
        
        # compare key presses with outlier onset times:
        pkeys = np.array(event.getKeys(timeStamped=practice_time)).astype(np.float)
        dev_times = np.array(dev_times)
        if len(pkeys) > 0: # if there was a key press
            dmat = (pkeys[:,1].reshape(1,len(pkeys[:,1])) - 
                    dev_times.reshape(len(dev_times),1)) # differences matrix
            # we will stop practice trials if there were three key presses in a chunk,
            # each one within 2 seconds after an outlier:
            if (sum(sum((dmat > 0) & (dmat < 2)))==3) & (dmat.shape[1] == 3):
               pdone = 1
    
    practiceEnd.draw()
    win.flip()
    event.waitKeys(keyList=[keyNext])
    logging.flush() 

def block_run(cond, ftxt):
    block = blocks[cond]
    finalTxt = visual.TextStim(win, text=ftxt, color=color,wrapWidth=1.8)
    block_time.reset() # restart block time count
    fixationCross.draw() # draw fixation:
    win.flip()
    silent.play()  # to prevent omission/cut of the first stimulus
    core.wait(silentDur)
    fixationCross.draw()
    win.flip()
    nextFlip = win.getFutureFlipTime(clock='ptb')
    for tidx, t in enumerate(block['tlist']):     # loop over trials:
        ttime = block_time.getTime() ## track trial onset
        mel = block['tlist'][tidx] #current pattern
        trigger = block['triggers'][tidx]  # trigger to send

        # present pattern (loop over sounds):
        for midx, ts in enumerate(mel):
            sounds[ts-1].name = str(trigger) + '_' + str(midx+1)
            if midx == 0:
                win.callOnFlip(setParallelData, trigger)
            sounds[ts-1].play(when = nextFlip)
            for frs in range(int(np.round(50/prd))): # 6 frames = 50 ms
                fixationCross.draw()
                win.flip()
            win.callOnFlip(setParallelData, 0)
            for frs in range(int(np.round(50/prd))): # 6 frames = 50 ms
                fixationCross.draw()
                win.flip()
            nextFlip = win.getFutureFlipTime(clock='ptb')
        for frs in range(int(np.round(500/prd))): # 30 frames = 400 ms
            fixationCross.draw()
            win.flip()
        nextFlip = win.getFutureFlipTime(clock='ptb')
    logging.flush()
    finalTxt.draw()
    win.flip()
    event.waitKeys()

########################### Run the experiment #################################
Instructions.draw()
nextText.draw()
win.flip()
event.waitKeys()

if practice_switch:
    practice(practice_seq)

for cidx, c in enumerate(conds):
    # switch between continuation and end of experiment messages:
    if cidx == (len(conds) - 1):
        ftxt = endTxt[0].format(c)
    else:
        ftxt = continueTxt[0].format(c)
    block_run(c,ftxt)

win.close()
core.quit()