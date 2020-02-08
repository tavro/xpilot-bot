import sys
import traceback
import math
import libpyAI as ai
from optparse import OptionParser

tickCount = 0
mode = "ready"

def tick():

    try:

        global tickCount
        global mode

        if not ai.selfAlive():
            tickCount = 0
            mode = "ready"
            return

        tickCount += 1

        selfX = ai.selfX()
        selfY = ai.selfY()
        selfVelX = ai.selfVelX()
        selfVelY = ai.selfVelY()
        selfSpeed = ai.selfSpeed()
        tracking = ai.selfTrackingRad()
        selfHeading = ai.selfHeadingRad()
        message = ai.scanTalkMsg(0)
        mass = ai.selfMass()
        friction = ai.getOption("friction")
        thrustPower = ai.getPower()



        def scalar_product(lis, n):
            return [x * n for x in lis]

        def vector_sum(list1, list2):
            return [sum(x) for x in zip(list1, list2)]

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

        def stopping_distance(mass, friction, thrustPower, selfSpeed):
            fForce = friction * mass
            tForce = thrustPower
            accTot = ((fForce/mass) + (tForce/(mass+5)))
            return ((selfSpeed * selfSpeed) / (2 * accTot))

        stopping_distance = stopping_distance(mass, friction, thrustPower, selfSpeed)

        print ("tick count:", tickCount, "mode", mode)

        if mode == "ready":
            print(friction, mass, selfSpeed, thrustPower)
            print(selfX, selfY)
            if "move-to" in message:
                splitmessage = message.split()
                action = splitmessage[0]

                if "move-to-stop" in action:
                    mode = "move-to-stop"
                if "move-to-pass" in action:
                    mode = "move-to-pass"

        if mode == "move-to-pass":
            splitmessage = message.split()
            coordX = float(splitmessage[1])
            coordY = float(splitmessage[2])
            print(coordX, coordY)
            distance = math.sqrt(abs(coordX-selfX)**2 + abs(coordY-selfY)**2)
            time = time_of_impact((coordX-selfX), (coordY-selfY), 0, 0, 10)
            targetDirection = (math.atan2(coordY-selfY, coordX-selfX))
            print(targetDirection)
            if tracking == targetDirection:
                ai.thrust()
            else:
                ai.turnToRad(targetDirection)
                ai.thrust()
                if distance < 10:
                    mode == "klar"

        if mode == "move-to-stop":
            splitmessage = message.split()
            coordX = int(splitmessage[1])
            coordY = int(splitmessage[2])
            print(coordX, coordY)
            distance = math.sqrt(abs(coordX-selfX)**2 + abs(coordY-selfY)**2)
            time = time_of_impact((coordX-selfX), (coordY-selfY), 0, 0, selfSpeed+0.000001)
            target_position = vector_sum((coordX-selfX, coordY-selfY), scalar_product((0-selfVelX, 0-selfVelY), time))
            targetDirection = (math.atan2(target_position[1], target_position[0]))
            print(target_position)
            print(targetDirection)
            if tickCount % 2 == 0:
                if abs(tracking-targetDirection) > 0.01:
                    ai.turnToRad(targetDirection)
            print("vinkel", (tracking-targetDirection), "tid", time)
            #if abs(targetDirection-tracking) > 0.03:
            #    ai.thrust()
            #ai.thrust()
        #    if tickCount % 2 == 0:
            #if selfSpeed < 30:
            ai.thrust()
            #if targetDirection-tracking < -0.1:
            #    ai.turnRad(-(tracking-targetDirection))
            #    ai.thrust()
            #if targetDirection-tracking < 0.1:
            #    ai.turnRad(-(tracking-targetDirection))
            #    ai.thrust()
            #if not tracking == targetDirection:
            #    ai.turnToRad(targetDirection)
            #    ai.thrust()
            #    if distance < 10:
            #        mode == "klar"
        #    print("V", selfSpeed, "tP", thrustPower, "fr", friction, "M", mass)
            print(stopping_distance, distance)
            if stopping_distance > distance:
                mode = "brake"

        if mode == "brake":
            ai.turnToRad(tracking+math.pi)
            ai.thrust()
            print(selfX, selfY)
            splitmessage = message.split()
            coordX = int(splitmessage[1])
            coordY = int(splitmessage[2])
            distance = math.sqrt(abs(coordX-selfX)**2 + abs(coordY-selfY)**2)
            print (distance)
            if selfSpeed < 2:
                mode = "xD"

        if mode == "xD":
            print(selfX,selfY)
            splitmessage = message.split()
            coordX = int(splitmessage[1])
            coordY = int(splitmessage[2])
            distance = math.sqrt(abs(coordX-selfX)**2 + abs(coordY-selfY)**2)
            print (distance)

    except:
        print(traceback.print_exc())



parser = OptionParser()
parser.add_option ("-p", "--port", action="store", type="int",
                   dest="port", default=15345,
                   help="The port number. Used to avoid port collisions when"
                   " connecting to the server.")

(options, args) = parser.parse_args()

name = "Stub"

ai.start(tick,["-name", name,
               "-join",
               "-turnSpeed", "64",
               "-turnResistance", "0",
               "-port", str(options.port)])
