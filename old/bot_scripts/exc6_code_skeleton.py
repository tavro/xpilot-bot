#
# This file can be used as a starting point for the bots.
#

import sys
import traceback
import math
import random
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


        if mode == "ready":

            greetings = ["Hey. ", "Hello. ", "Yooo. ", "Excuse me, sir? ",
                         "It's yo boy in da house. ", "Goddaaaaag, NOLLA! ",
                         "'Sup. Come here often? "]
            
            questions = ["What are your coords?",
                         "What is your heading?",
                         "How many items have you seen?",
                         "What ships have you seen?",
                         "What is your tracking?"]

            if tickCount % 50 == 0:
                unansweredQuestions = []
                for i in range(ai.getMaxMsgs()):
                    if ":[Pelle]" in ai.scanTalkMsg(i):
                        unansweredQuestions.append(ai.scanTalkMsg(i))
                        ai.removeTalkMsg(i)

                if name == "Stub":
                    rand = random.SystemRandom()
                    ai.talk("Pelle:" + rand.choice(greetings) + rand.choice(questions))

                for s in unansweredQuestions:
                    if ":[Pelle]" in s:
                        msg = "Stub:Hey"
                        if "coords" in s:
                            msg = "Stub:My coords are (" + str(ai.selfX()) + ", " + str(ai.selfY()) + ")."
                        elif "heading" in s:
                            msg = "Stub:My heading is " + str(ai.selfHeadingRad()) + " radians."
                        elif "tracking" in s:
                            msg = "Stub:My tracking is " + str(ai.selfTrackingRad()) + " radians."
                        elif "items" in s:
                            msg = "Stub:I have seen " + str(ai.itemCountScreen()) + " items."
                        elif "ships" in s:
                            ships = []

                            if (ai.shipCountScreen() - 1) > 0:
                                for player_id in range(ai.playerCountServer()):
                                    if ai.playerName(player_id) != ai.selfName():
                                        ships.append(ai.playerName(player_id))
                                    
                            msg = "I see " + str(ai.shipCountScreen() - 1) + " ship(s). " + str(ships)
                        ai.talk(msg)

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
parser.add_option ("-n", "--name", type="string", default="Stub",
                   dest="name", help="Name of bot.")

(options, args) = parser.parse_args()

name = options.name

#
# Start the AI
#

ai.start(tick,["-name", name, 
               "-join",
               "-turnSpeed", "64",
               "-turnResistance", "0",
               "-port", str(options.port)])
