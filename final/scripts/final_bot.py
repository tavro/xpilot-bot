# ========================================================
# BOTNAME.pdf a bot for completing various tasks in XPILOT
#
# Written by: isaho220, trugr925, andfr210
# Updated: DEC 16, 20:05
#
# Features: BASIC NAVIGATION, ITEM-COLLECTION AND HANDLING,
# PATH-FINDING FOLLOWING DRAWING AND OPTIMIZATION,
# REFUELLING, SEARCH AND DESTROY, MULTITHREADING
#
# BASIC NAVIGATION:
# Moves to specified (x, y) coord
# Use by writing following in chat:
#
# move-to-stop x y :[botname] (this will stop at specified coord)
# move-to-pass x y :[botname] (this will pass by specified coord)
# move-to-pos  x y :[botname] (this will do the same as pass)
#
# ITEM-COLLECTION:
# Collects specified item
# Use by writing following in chat:
#
# collect-item item :[botname]
#
# ITEM-HANDLING:
# Uses specified item at (x, y) coord
# Use by writing following in chat:
#
# use-item item x y :[botname]
# use-item tank x y (next/prev/detach/fuel) :[botname]
#
# PATH-HANDLING:
# Returns safe and optimized a* path from
# startPos (y, x) to endPos (y, x)
#
# Draws finished path as well as map in console when done
# EXAMPLE:
#          x x x x x x x x x x
#          x P               x
#          x                 x
#          x                 x
#          x     o     o     x
#          x                 x
#          x                 x
#          x               o x
#          x           o     x
#          x x x x x x x x x x
#
# REFUELLING:
# Moves to specified fuelstation and refuels ship
# Use by writing following in chat:
#
# refuel stationId :[botname]
#
# SEARCH AND DESTROY:
# More like 'flee'
#
# MULTITHREADING:
# Runs a* code on other thread
#
# FOR TESTING:
# REFUELLING,       MAP : fuel.xp
# BASIC NAVIGATION, MAP : astar.xp
# PATH HANDLING,    MAP : astar.xp
# ITEM COLLECTION,  MAP : item.xp
# ITEM HANDLING,    MAP : item.xp
# MULTITHREADING,   MAP : random
# ========================================================

import threading
import queue
import random
import sys
import traceback
import math
import random
import libpyAI as ai
from optparse import OptionParser

#OUR OWN LIBRARY CONTAINING PATH- FINDING, OPT AND MAKING SAFER
import gr9_pathhandling as ph

#
#GLOBAL VARIABLES (PERSISTS BETWEEN TICKS)
#

#XPILOT-SPEC
tickCount = 0
mode = "ready"
selfX, selfY = 0, 0
selfVelX, selfVelY = 0, 0
selfSpeed = 0
selfTracking = 0

#ITEMS
item = 0
itemId = 0
lastItemCount = 0

#COMMUNICATION
tsk = []
latestTask = ""

#A*
maplist = []
mapWidth, mapHeight = 0, 0
finalPath = []
finalPosition = []

#REFUELING
stationId = 0
fuelIndex = 0

#MULTITHREADING
maplistQueue = queue.Queue()
searchQueue = queue.Queue()
pathQueue = queue.Queue()

#MULTITHREADING
def calculatePath(srchQueue, finalPath):
    search = False
    while True:
        try:
            search = srchQueue.get(timeout=1)
        except queue.Empty:
            print("QUEUE IS EMPTY")
        if searchForPath:
            print("SEARCHING FOR PATH!")
            maplist, finalPath = getPath(pixelsToBlockSize(mapWidth, mapHeight), tuple(finalPosition), mapWidth, mapHeight)
            maplistQueue.put(maplist)
            pathQueue.put(finalPath)
            print("FINAL PATH:", finalPath)

searchForPath = False
pathThread = threading.Thread(target=calculatePath, args=(searchQueue, finalPath))
#print("THREAD IS ALIVE:", pathThread.isAlive())
pathThread.start()

def tick():
    #NO EXCEPTION HANDLING
    try:
        #
        #GLOBAL VARIABLES
        #

        #XPILOT-SPEC
        global tickCount
        global mode
        global selfVelX, selfVelY
        global selfX, selfY
        global selfSpeed
        global selfTracking

        #ITEMS
        global item
        global itemId
        global lastItemCount

        #COMMUNICATION
        global latestTask

        #A*
        global mapWidth
        global mapHeight
        global maplist
        global finalPath
        global finalPosition

        #REFUELING
        global fuelIndex
        global stationId

        #MULTITHREADING
        global maplistQueue
        global searchForPath
        global searchQueue
        global pathQueue

        #RESET IF DEAD
        if not ai.selfAlive():
            tickCount = 0

            #CLEAR A*
            finalPosition = []
            finalPath = []

            mode = "idle"
            return

        tickCount += 1

        #
        #SENSORS READINGS
        #

        #XPILOT-SPEC
        selfX = ai.selfX()
        selfY = (mapHeight * ai.blockSize()) - ai.selfY()
        selfVelX = ai.selfVelX()
        selfVelY = ai.selfVelY()
        selfSpeed = ai.selfSpeed()
        selfTracking = ai.selfTrackingRad()
        selfHeading = ai.selfHeadingRad()

        #DOES NOT EXIST FIRST TICKS
        if tickCount > 6:
            mass = ai.selfMass()

        thrustPower = ai.getPower()
        friction = ai.getOption("friction")
        mapWidth = ai.getOption("mapwidth")
        mapHeight = ai.getOption("mapheight")

        print ("tick count:", tickCount, "mode", mode)

        #IN THIS MODE WE ARE WAITING FOR THE PLAYER TO GIVE THE BOT INSTRUCTIONS
        if mode == "idle":
            mode, value, latestTask = getMessage()

            if mode == "move":
                finalPosition = value
            elif mode == "collect":
                item = value
            elif mode == "refuel":
                fuelIndex = value

        #IN THIS MODE WE ARE CALUCLATING PATH USING ASTAR
        elif mode == "move":

            #MULTITHREADING
            searchForPath = True
            searchQueue.put(searchForPath)
            try:
                finalPath = pathQueue.get(timeout=1)
                maplist = maplistQueue.get(timeout=1)
            except queue.Empty:
                pass

            #SEARCH-PATH-PART
            if not finalPath:
                print("CALCULATING PATH")
                maplist, finalPath = getPath(pixelsToBlockSize(mapWidth, mapHeight), tuple(finalPosition), mapWidth, mapHeight)
                print("CALCULATED MAPLIST LENGTH:", len(maplist))
                print("CALCULATED FINAL PATH:", len(finalPath))
            else:
                if maplist:
                    printMap(finalPath, True)

                #MULTITHREADING
                searchForPath = False
                searchQueue.put(searchForPath)

                print("Final Path:", finalPath)
                print("Player Pos:","(",selfY // ai.blockSize(), selfX // ai.blockSize(),")")
                targetPosition = finalPath[0]

                if finalPath[0][1] == selfX // ai.blockSize() and finalPath[0][0] == selfY // ai.blockSize():
                    if len(finalPath) > 1:
                        finalPath = finalPath[1:]
                    else:
                        print("REACHED TARGETPOS")
                        sendMessage("teacherbot")

                        finalX = finalPosition[1]
                        finalY = finalPosition[0]
                        finalPosition = []
                        finalPath = []

                        print(latestTask)
                        if "refuel" in latestTask:
                            mode = "refueling"
                        elif latestTask == "use-item mine":
                            mode = useMine(finalX, finalY)
                        elif latestTask == "use-item missile":
                            mode = useMissile(finalX, finalY)
                        elif latestTask == "use-item laser":
                            mode = useLaser(finalX, finalY)
                        else:
                            mode = "idle"

            #MOVE-PART
            if finalPosition:
                stoppingDist = stopping_distance(mass, friction, thrustPower, selfSpeed)
                moveToPos(selfX, selfY, [targetPosition[1]*ai.blockSize(), targetPosition[0]*ai.blockSize()], stoppingDist)

        #IF OTHER PLAYER IS SHOOTING TOWARDS YOU FLEE
        elif mode == "flee":
            if ai.selfItem(18):
                usePhasing(0, 0)
            elif ai.selfItem(17):
                useHyperJump(0, 0)
            elif ai.selfItem(10):
                useEcm(0,0)
            elif ai.selfItem(15):
                useEmergencyShield(0, 0)
            else:
                ai.shield()

        #IN THIS MODE WE ARE REFUELING
        elif mode == "refuel":

            mode, finalPath, finalPosition = moveToFuelStation()
        elif mode == "refueling":
            '''Amount of fuel in station'''
            if ai.fuelstationFuel(fuelIndex) > 0:
                '''Keep calling to refuel'''
                ai.refuel()
            else:
                mode = "idle"

        #IN THIS MODE WE ARE COLLECTING ITEMS
        elif mode == "collect":
            if ai.itemCountScreen() > 0:
                itemOnScreen = False
                for i in range(ai.itemCountScreen()):
                    if ai.itemType(i) == item:
                        itemId = i
                        itemOnScreen = True
                        break

                if not itemOnScreen:
                    print("No item of type " + str(item) + " on screen")
                    mode = "idle"

                collectAim(itemId)

                if selfSpeed < 10:
                    thrust(10)
                else:
                    brake(2)

    except:
        print(traceback.print_exc())

#
#MAIN FUNCTIONS
#

'''Aim at a specified target'''
def aim(targetId):
    xDiff = ai.targetX(targetId) - ai.selfX()
    yDiff = ai.targetY(targetId) - ai.selfY()
    targetDirection = math.atan2(yDiff, xDiff)
    ai.turnToRad(targetDirection)

'''Aim at a specified object'''
def collectAim(targetId):
    itemX = ai.itemX(targetId)
    itemY = ai.itemY(targetId)
    itemVelX = ai.itemVelX(targetId)
    itemVelY = ai.itemVelY(targetId)

    deltaPosX = itemX - selfX
    deltaPosY = itemY - ai.selfY()

    deltaVelX = itemVelX - selfVelX
    deltaVelY = itemVelY - selfVelY

    time = time_of_impact(deltaPosX, deltaPosY, itemVelX, itemVelY, 10)

    targetPosition = vector_sum((deltaPosX, deltaPosY), scalar_product((deltaVelX, deltaVelY), time))
    targetDirection = math.atan2(targetPosition[1], targetPosition[0])

    ai.turnToRad(targetDirection)

'''Moves to specified targetPosition'''
def moveToPos(selfX, selfY, targetPositionPixels, stoppingDistance):
    deltaX = targetPositionPixels[0] - selfX
    deltaY = selfY - targetPositionPixels[1]
    targetDirection = (math.atan2(deltaY, deltaX))
    distanceToTarget = math.sqrt((targetPositionPixels[0] - selfX)**2 + (targetPositionPixels[1] - selfY)**2)
    isBraking = distanceToTarget < stoppingDistance

    if not isBraking:
        ai.turnToRad(targetDirection)
        thrust(40)
    else:
        brake(2)

'''Brakes if moving faster than targetSpeed'''
def brake(targetSpeed=2):
    if selfSpeed > targetSpeed:
        ai.turnToRad(selfTracking + math.pi)
        ai.thrust()

'''Draws map (with path) in console'''
def printMap(pathList, printWholeMap=False):

    for i in range(len(pathList)):
        print("i: ", i)
        print("Pathlist i:", pathList[i])
        print("Maplist len:", len(maplist))

        maplist[pathList[i][0]][pathList[i][1]] = 'o'

    for x in range(mapWidth):
        for y in range(mapHeight):
            if maplist[y][x] == "P":
                maplist[y][x] = " "

    playerPos = pixelsToBlockSize(mapWidth-1, mapHeight-1)
    maplist[playerPos[0]][playerPos[1]] = "P"

    viewDist = 20

    notOutXRight = not (playerPos[1] + viewDist//2 > mapWidth-1)
    notOutXLeft = not (playerPos[1] - viewDist//2 < 0)
    notOutYUp = not (playerPos[0] + viewDist//2 > mapHeight-1)
    notOutYDown = not (playerPos[0] - viewDist//2 < 0)
    inRange = notOutXRight and notOutXLeft and notOutYUp and notOutYDown

    if printWholeMap:
        '''Print the whole map in console'''
        for y in maplist:
            for x in y:
                print(x, end=" ")
            print()
    else:
        '''Print the area around player in console'''
        if inRange:
            for y in range(playerPos[0] - viewDist//2, playerPos[0] + viewDist//2):
                for x in range(playerPos[1] - viewDist//2, playerPos[1] + viewDist//2):
                    print(maplist[y][x], end=" ")
                print()

'''Returns a optimized and safed a* path'''
def getPath(start, end, mapWidth, mapHeight):
    maplist = [['x' if ai.mapData(x,y) == 1 else ' ' for x in range(mapWidth)] for y in range(mapHeight-1, -1, -1)]

    if ai.getOption("mapname") == "fuel":
        #FUELSTATIONS
        maplist[29][3] = "x"
        maplist[29][9] = "x"
        maplist[29][15] = "x"
        maplist[29][16] = "x"
        maplist[29][22] = "x"
        maplist[29][28] = "x"

    #START/END IS TUPLES OF FORM (Y, X)
    path = ph.astar(maplist, start, end)
    print("PATH:", path)

    #OPTIMIZING PATH
    oPath = ph.main(maplist, path)
    oPath = oPath[1:]
    print("OPT. PATH:", oPath)

    #MAKING PATH SAFER
    sPath = ph.makePathSafe(maplist, oPath)
    print("SAFE PATH:", sPath)
    fPath = ph.makePathSafe(maplist, sPath)
    print("FINAL PATH:", fPath)

    return maplist, fPath

'''Thrusts with specified power'''
def thrust(power):
    ai.setPower(power)
    ai.thrust()

def shoot():
    ai.fireShot()

'''Use Item Functions'''
def useMine(x, y):
    if distance((selfX//ai.blockSize(), selfY//ai.blockSize()), (x, y)) < 1:
        ai.dropMine()
        sendMessage("teacherbot")
        return "idle"
    else:
        return [y,x]


def useMissile(x, y):
    if checkDistance(x, y, 5):
        useAtPosition(x, y, ai.fireTorpedo)
        return "idle"
    else:
        return [y, x]

def useLaser(x, y):
    if checkDistance(x, y, 5):
        useAtPosition(x, y, ai.fireLaser)
        return "idle"
    else:
        return [y,x]

def checkDistance(x, y, dist):
    if distance((selfX//ai.blockSize(), selfY//ai.blockSize()), (x, y)) < dist:
        return True
    return False

def setFinalPosition(x, y):
    finalPosition = [y, x]
    return finalPosition

def useAtPosition(x, y, func):
    xDiff = selfX//ai.blockSize() - x
    yDiff = selfY//ai.blockSize() - y
    targetDirection = math.atan2(yDiff, xDiff)
    ai.turnToRad(targetDirection)
    func()
    sendMessage("teacherbot")

def useFuel(x, y):
    ai.refuel()

def useCloak(x, y):
    ai.cloak()

'''Steal an opponents item'''
def useTransporter(x, y):
    ai.transporter()

def useTank(x, y, task):
    #DETACHES FUELTANK
    if task == "detach":
        ai.tankDetach()
    #NEXT FUELTANK
    elif task == "next":
        ai.nextTank()
    #PREVIOUS FUELTANK
    elif task == "prev":
        ai.prevTank()
    else:
        ai.selfFuelCurrent()

'''Temporarily blind opponents'''
def useEcm(x, y):
    ai.ecm()

def useEmergencyThrust(x, y):
    ai.emergencyThrust()

'''Pull enemy ships towards the ship'''
def useTractorBeam(x, y):
    ai.tractorBeam()

'''Stop the ships movement'''
def useAutoPilot(x, y):
    ai.toggleAutopilot()

def useEmergencyShield(x, y):
    ai.emergencyShield()

'''Pushes everything away from the ship'''
def useItemDeflector(x, y):
    ai.deflector()

'''Puts the player on a random location at the map'''
def useHyperJump(x, y):
    ai.hyperjump()

'''Allows passing through walls'''
def usePhasing(x, y):
    ai.phasing()

def getMessage():
    msg = ai.scanTalkMsg(0)
    if ":[" + name + "]" in msg:
        tsk = msg.split()
        ai.removeTalkMsg(0)
        print(tsk)
        latestTask = tsk[0] + " " + tsk[1]
        if tsk[0] == "move-to-stop" or tsk[0] == "move-to-pass" or tsk[0] == "move-to-pos":
            x = tsk[1]
            y = tsk[2]
            print("MOVING TO POS")
            finalPosition = [int(y),int(x)]
            return "move", finalPosition, latestTask
        elif tsk[0] == "collect-item":
            itemDict = {0: "fuel", 1: "wideangle", 2: "rearshot", 3: "afterburner", 4: "cloak", 5: "sensor",
            6: "transporter", 7: "tank", 8: "mine", 9: "missile", 10: "ecm",
            11: "laser", 12: "emergencythrust", 13: "tractorbeam", 14: "autopilot", 15: "emergencyshield",
            16: "itemdeflector", 17: "hyperjump", 18:"phasing", 19:"mirror", 20:"armor"}

            for key in itemDict:
                if tsk[1] == itemDict[key]:
                    return "collect", key, latestTask
        elif tsk[0] == "use-item":
            useItemDict = {"mine": useMine, "missile": useMissile, "laser": useLaser, "fuel": useFuel, "cloak": useCloak,
                           "transporter": useTransporter, "ecm": useEcm, "emergencythrust":useEmergencyThrust,
                           "tractorbeam": useTractorBeam, "autopilot": useAutoPilot, "emergencyshield": useEmergencyShield,
                           "itemdeflector": useItemDeflector, "hyperjump": useHyperJump, "phasing": usePhasing}

            for key in useItemDict:
                if tsk[1] == key:
                    if len(tsk) >= 5:
                        return "move", useItemDict[key](int(tsk[2]), int(tsk[3])), latestTask
                    else:
                        useItemDict[key](0, 0)

            if tsk[1] == "tank":
                useTank(int(tsk[2]), int(tsk[3]), tsk[4])
        elif tsk[0] == "refuel":
            fuelStationId = int(tsk[1])
            return "refuel", fuelStationId, latestTask

    return "idle", [], ""

def sendMessage(receiver):
    ai.talk(receiver + ":" + "completed " + latestTask)

#
#HELP FUNCTIONS
#

def moveToFuelStation():
    #GET FEULSTATION X AND Y POS
    finalxPosition = ai.fuelstationBlockX(fuelIndex)
    finalyPosition = mapHeight - ai.fuelstationBlockY(fuelIndex)

    finalxAndyPosition = [finalyPosition - 2, finalxPosition]

    finalPath = []
    finalPosition = finalxAndyPosition

    return "move", finalPath, finalPosition

'''Finds the closest ship and return its id'''
def closestShipId():
    closestId = 0
    for i in range(ai.shipCountScreen()):
        closestShipDist =  distance((selfX, selfY), (ai.shipX(closestId), ai.shipY(closestId)))
        if distance((selfX, selfY), (ai.shipX(i), ai.shipY(i))) < closestShipDist:
            closestId = i
    return closestId

#ASTAR FUNCTIONS
def placeTargets(positionLis, char, maplis):
    for pos in positionLis:
        maplis[pos[0]][pos[1]] = char
    return maplis

def pixelsToBlockSize(mapWidth, mapHeight):
    playerX = int(ai.selfX() // ai.blockSize())-0
    playerY = mapHeight-1 - int((ai.selfY() // ai.blockSize())-1)
    return (playerY, playerX)

#BASIC NAVIGATION FUNCTIONS
def stopping_distance(mass, friction, thrustPower, selfSpeed):
    selfSpeedSquared = selfSpeed * selfSpeed
    accTot = ((friction) + (thrustPower/(mass+5)))
    return (selfSpeedSquared / (2 * accTot))

def distance(posA, posB):
    deltaX = (posA[0] - posB[0])**2
    deltaY = (posA[1] - posB[1])**2
    return math.sqrt(deltaX + deltaY)

#ASTEROIDS FUNCTIONS
def scalar_product(lis, scalar):
    return [x * scalar for x in lis]

def vector_sum(list1, list2):
    return [sum(x) for x in zip(list1, list2)]

def time_of_impact(playerX, playerY, targetVelocityX, targetVelocityY, speed):
    speedSquared = speed * speed
    targetVXSquared = targetVelocityX * targetVelocityX
    targetVYSquared = targetVelocityY * targetVelocityY
    playerXSquared = playerX * playerX
    playerYSquared = playerY * playerY

    a = speedSquared - (targetVXSquared + targetVYSquared)
    b = playerX * targetVelocityX + playerY * targetVelocityY
    c = playerXSquared + playerYSquared

    d = b*b + a*c

    time = 0
    if d >= 0:
        time = (b + math.sqrt(d)) / a
        if (time < 0):
            time = 0
    return time

#PARSE THE COMMAND LINE ARGUMENTS
parser = OptionParser()

parser.add_option ("-p", "--port", action="store", type="int",
                   dest="port", default=15345,
                   help="The port number. Used to avoid port collisions when"
                   " connecting to the server.")

(options, args) = parser.parse_args()

name = "Stub"

#START AI
ai.start(tick,["-name", name,
               "-join",
               "-turnSpeed", "64",
               "-turnResistance", "0",
               "-port", str(options.port)])
