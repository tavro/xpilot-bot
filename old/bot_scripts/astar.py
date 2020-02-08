#
# This file can be used as a starting point for the bots.
#

import sys
import traceback
import math
import random
import gr9_astr_helper as astr
import libpyAI as ai
from optparse import OptionParser

#
# Global variables that persist between ticks
#
tickCount = 0
mode = "ready"
# add more if needed

def tick():
    #
    # The API won't print out exceptions, so we have to catch and print them ourselves.
    #
    try:

        #
        # Declare global variables so we have access to them in the function
        #
        global tickCount
        global mode

        #
        # Reset the state machine if we die.
        #
        if not ai.selfAlive():
            tickCount = 0
            mode = "ready"
            return

        tickCount += 1

        #
        # Read some "sensors" into local variables, to avoid excessive calls to the API
        # and improve readability.
        #

        selfX = ai.selfX()
        selfY = ai.selfY()
        selfVelX = ai.selfVelX()
        selfVelY = ai.selfVelY()
        selfSpeed = ai.selfSpeed()

        selfHeading = ai.selfHeadingRad() 
        # 0-2pi, 0 in x direction, positive toward y

        # Add more sensors readings here

        print ("tick count:", tickCount, "mode", mode)

        maplist = [['x' if ai.mapData(x,y) == 1 else ' ' for x in range(32)] for y in range(31, -1, -1)]
        
        lisOfOne = [(6,4), (9,7), (20,11), (28,16)]
        lisOfTwo = [(3,7), (5,23), (20,20), (20,27), (25,6)]
        lisOfThree = [(3,17), (12,18), (14,9), (18,5), (26,11)]
        lisOfFour = [(5,12), (9,27), (14,25), (18,6), (25,26)]

        '''
        xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        x                              x
        x                              x
        x      2         3             x
        x        x                     x
        x        x  4  x       2       x
        x   1    x     x               x
        x        x     x               x
        x        x     x               x
        x      1       x     xxxx  4   x
        x              x               x
        x                              x
        x   xxxxxx        3            x
        x                              x
        x        3               4     x
        x              _  xxxx         x
        x                              x
        x       xxxxx          xxxx    x
        x    34                        x
        x                              x
        x          1        2      2   x
        x  x           xxx             x
        x  x    xxxx                   x
        x  x                           x
        x  x                           x
        x     2                   4    x
        x          3        xxxxx      x
        x                              x
        x     xxxxx     1              x
        x                              x
        x                              x
        xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        '''
        
        if mode == "ready":
            playerX = int(ai.selfX() / 32)-1
            playerY = 31 - int((ai.selfY() / 32)-1)

            maplist = placeTargets(lisOfOne, '2', maplist)
            maplist = placeTargets(lisOfTwo, '2', maplist)
            maplist = placeTargets(lisOfThree, '2', maplist)
            maplist = placeTargets(lisOfFour, '2', maplist)
            
            maplist[playerY][playerX] = '3'

            path = astr.astar(maplist, (playerY,playerX), (30, 30))

            for i in range(len(path)):
                maplist[path[i][0]][path[i][1]] = '5'

            for y in maplist:
                for x in y:
                    print(x, end=" ")
                print()

    except:
        print(traceback.print_exc())

def placeTargets(lis, char, maplis):
    for pos in lis:
        maplis[pos[0]][pos[1]] = char
    return maplis
        
#
# Parse the command line arguments
#
parser = OptionParser()

parser.add_option ("-p", "--port", action="store", type="int", 
                   dest="port", default=15345, 
                   help="The port number. Used to avoid port collisions when" 
                   " connecting to the server.")

(options, args) = parser.parse_args()

#
# Start the AI
#

ai.start(tick,["-join",
               "-turnSpeed", "64",
               "-turnResistance", "0",
               "-port", str(options.port)])
