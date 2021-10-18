#54121 -+sycu 6y 
from psychopy import parallel

# Set port address to match your local machine
paddress = '/dev/parport0' # '0xDFF8' in Windows
try:
    port = parallel.setPortAddress(address=paddress) 
except NotImplementedError:
    port = []
# NB problems getting parallel port working under conda env
# from psychopy.parallel._inpout32 import PParallelInpOut32
# port = PParallelInpOut32(address=0xDFF8)  # on MEG stim PC
# parallel.setPortAddress(address='0xDFF8')
# port = parallel

# Figure out whether to flip pins or fake it
if port:
    def setParallelData(code=1):
        port.setData(code)
        print('trigger sent {}'.format(code))
else:
    def setParallelData(code=1):
        print('trigger not sent {}'.format(code))