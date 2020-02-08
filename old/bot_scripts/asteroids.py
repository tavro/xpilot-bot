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
        shotSpeed = ai.getOption("shotSpeed")

        selfHeading = ai.selfHeadingRad()
        # 0-2pi, 0 in x direction, positive toward y

        # Add more sensors readings here

        print ("tick count:", tickCount, "mode", mode)

        def scalar_product(lis, n):
            return [x * n for x in lis]

        def vector_sum(list1, list2):
            return [sum(x) for x in zip(list1, list2)]

        # [a, b, c] [d, e, f]
        # [a,d] [b, e] [c, f]

        def time_of_impact(px, py, vx, vy, s):
            a = s * s - (vx * vx + vy * vy)
            b = px * vx + py * vy
            c = px * px + py * py

            d = b*b + a*c

            t = 0 # Time
            if d >= 0:
                t = (b + math.sqrt(d)) / a
                if (t < 0):
                    t = 0
            return t


        closest_asteroid_id = 0

        if mode == "ready":
            #print("self vel Y: ", selfVelY)
            if ai.selfSpeed() > 7: # We're going too fast!!!
                mode = "brake"

            # Find closest asteroid
            if tickCount % 1 == 0:
                for i in range(ai.asteroidCountScreen()):
                    #if not 130 <= ai.radarType(i) <= 133: # We're only looking for asteroids.
                    #    continue
                    radar_dist = ai.asteroidDist(i)
                    if radar_dist < ai.asteroidDist(closest_asteroid_id):
                        closest_asteroid_id = i

                if ai.asteroidCountScreen() > 0:
                    mode = "aim"

        if mode == "aim":
            asteroidX = ai.asteroidX(closest_asteroid_id)
            asteroidY = ai.asteroidY(closest_asteroid_id)
            asteroidVelX = ai.asteroidVelX(closest_asteroid_id)
            asteroidVelY = ai.asteroidVelY(closest_asteroid_id)

            if asteroidX - selfX > ai.mapWidthPixels()/1.2:
                print("Target is to the right. Seen to the left")
                dx = ai.mapWidthPixels() - asteroidX
                asteroidX = -dx
                #targetPosition[0] -= ai.mapWidthPixels()
            if selfX - asteroidX > ai.mapWidthPixels()/1.2:
                print("Target is to the left. Seen to the right")
                dx = asteroidX
                asteroidX = ai.mapWidthPixels() + dx

                #targetPosition[0] += ai.mapWidthPixels()

            if asteroidY - selfY > ai.mapHeightPixels()/1.2:
                print("Target is above. Seen below")
                dx = ai.mapHeightPixels() - asteroidY
                asteroidY = -dx
                #targetPosition[1] -= ai.mapHeightPixels()
            if selfY - asteroidY > ai.mapHeightPixels()/1.2:
                print("Target is below. Seen above.")
                dx = asteroidY
                asteroidY = ai.mapHeightPixels() + dy
                #targetPosition[1] += ai.mapHeightPixels()

            time = time_of_impact(asteroidX - selfX, asteroidY - selfY,
                                    asteroidVelX, asteroidVelY, shotSpeed)

            targetPosition = vector_sum((asteroidX - selfX, asteroidY - selfY),
                                scalar_product((asteroidVelX, asteroidVelY), time*1.1))

            print("Map size x: ", ai.mapWidthPixels())

            targetAngle = math.atan2(targetPosition[1], targetPosition[0])
            ai.turnToRad(targetAngle)
            if abs(selfHeading - targetAngle) % 2*math.pi < 0.8:
                print("Firing at", targetPosition[0], ",", targetPosition[1])
                ai.fireShot()
            mode = "ready"

        if mode == "brake":
            velocityVector = (selfVelX, selfVelY)
            targetAngle = math.pi + (math.atan2(velocityVector[1], velocityVector[0])) # Negative velocity vector
            ai.turnToRad(targetAngle)
            ai.thrust()
            selfVel = velocityVector[0] * velocityVector[0] + velocityVector[1] * velocityVector[1]
            if selfVel < 3: # The bot has come to a stop.
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
