#
# This file can be used as a starting point for the bots.
#

import sys
import traceback
import math
import libpyAI as ai
from optparse import OptionParser

#
# Global variables that persist between ticks
#
tickCount = 0
mode = "ready"
targetId = 0
lis = [0, 1, 2, 3]
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
        global targetId
        global lis

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
        selfTracking = ai.selfTrackingRad()
        # 0-2pi, 0 in x direction, positive toward y

        # Add more sensors readings here

        print ("tick count:", tickCount, "mode", mode)
        
        if mode == "ready":
            for i in range(4):
                if ai.targetAlive(i):
                    targetId = i
                    break
            xDiff = ai.targetX(targetId) - ai.selfX()
            yDiff = ai.targetY(targetId) - ai.selfY()
            targetDirection = math.atan2(yDiff, xDiff)
            ai.turnToRad(targetDirection)
            ai.setPower(20)
            if selfSpeed < 20:
                ai.thrust()
                
            if xDiff < 400 and yDiff < 400:
                mode = "brake"

            if abs(selfHeading - selfTracking) > 0.1 and selfSpeed > 20:
                mode = "stab"
                
        elif mode == "stab":
            if selfSpeed < 2:
                mode = "ready"
            else:
                ai.setPower(50)
                ai.turnToRad(math.pi + ai.selfTrackingRad())
                ai.thrust()
        elif mode == "brake":
            if selfSpeed < 2:
                mode = "aim"
            else:
                ai.setPower(50)
                ai.turnToRad(math.pi + ai.selfTrackingRad())
                ai.thrust()
        elif mode == "aim":
            xDiff = ai.targetX(targetId) - ai.selfX()
            yDiff = ai.targetY(targetId) - ai.selfY()
            targetDirection = math.atan2(yDiff, xDiff)
            ai.turnToRad(targetDirection)
            angleDiff = abs(targetDirection - selfHeading)
            if angleDiff < 0.25 or angleDiff > 2*math.pi - 0.25:
                mode = "shoot"
        elif mode == "shoot":
            ai.fireShot()
            xDiff = ai.targetX(targetId) - ai.selfX()
            yDiff = ai.targetY(targetId) - ai.selfY()
            targetDirection = math.atan2(yDiff, xDiff)
            ai.turnToRad(targetDirection)
            if not ai.targetAlive(targetId):
                mode = "ready"

    except:
        print(traceback.print_exc())

#
# Parse the command line arguments
#
parser = OptionParser()

parser.add_option ("-p", "--port", action="store", type="int", 
                   dest="port", default=15345, 
                   help="The port number. Used to avoid port collisions when" 
                   " connecting to the server.")

(options, args) = parser.parse_args()

name = "Stub"

#
# Start the AI
#

ai.start(tick,["-name", name, 
               "-join",
               "-turnSpeed", "64",
               "-turnResistance", "0",
               "-port", str(options.port)])
