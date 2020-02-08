#import concurrent.futures
#import multiprocessing
import threading
#import time
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

#GLOBAL VARIABLES (PERSISTS BETWEEN TICKS)
tickCount = 0
mode = "ready"
item = 0
itemId = 0
lastItemCount = 0
tsk = []
maplist = []
mapWidth, mapHeight = 0, 0
finalPath = []
searchQueue = queue.Queue()
pathQueue = queue.Queue()
selfVelX, selfVelY = 0, 0
selfSpeed = 0
selfTracking = 0
finalPosition = []
latestTask = ""

#startQueue = queue.Queue()
#endQueue = queue.Queue()

def calculatePath(srchQueue, finalPath):
    search = False
    while True:
        try:
            search = srchQueue.get(timeout=1)
        except queue.Empty:
            print("Queue is empty")
        if searchForPath:
            print("SEARCHING FOR PATH!")
            finalPath = getPath(pixelsToBlockSize(mapWidth, mapHeight), tuple(finalPosition), mapWidth, mapHeight)
            pathQueue.put(finalPath)
            print(finalPath)


searchForPath = False
pathThread = threading.Thread(target=calculatePath, args=(searchQueue, finalPath))#, args=(startQueue, endQueue))
print(pathThread.isAlive())
pathThread.start()


def tick():
    #NO EXCEPTION HANDLING
    try:
        #GLOBAL VARIABLES
        global tickCount
        global mode
        global item
        global itemId
        global lastItemCount
        global latestTask
        global mapWidth
        global mapHeight
        global maplist
        global finalPath
        global pathThread # Does not need to be global at the moment
        global searchForPath, searchQueue
        global selfVelX, selfVelY
        global selfSpeed
        global selfTracking
        global finalPosition

        #RESET IF DEAD
        if not ai.selfAlive():
            tickCount = 0

            #Create a clear function
            targetPos = []
            finalPath = []

            mode = "idle"
            return

        tickCount += 1

        #SENSORS READINGS
        selfX = ai.selfX()
        selfY = (mapHeight * ai.blockSize()) - ai.selfY()
        selfVelX = ai.selfVelX()
        selfVelY = ai.selfVelY()
        selfSpeed = ai.selfSpeed()
        selfTracking = ai.selfTrackingRad()
        selfHeading = ai.selfHeadingRad()
        mass = ai.selfMass()
        friction = ai.getOption("friction")
        thrustPower = ai.getPower()

        mapWidth = ai.getOption("mapwidth")
        mapHeight = ai.getOption("mapheight")

        print ("tick count:", tickCount, "mode", mode)

        #IN THIS MODE WE ARE WAITING FOR THE PLAYER TO GIVE THE BOT INSTRUCTIONS
        if mode == "idle":
            mode, value = getMessage()

            if mode == "move":
                finalPosition = value
            elif mode == "collect":
                item = value
        #IN THIS MODE WE ARE CALUCLATING PATH USING ASTAR
        elif mode == "move":
            #GET PATH
            searchForPath = True
            searchQueue.put(searchForPath)
            try:
                finalPath = pathQueue.get(timeout=1)
            except queue.Empty:
                pass
                
            #if not finalPath:
                #print("CALCULATING PATH")
                #finalPath = getPath(pixelsToBlockSize(mapWidth, mapHeight), tuple(finalPosition), mapWidth, mapHeight)
            # else:
            #SEARCH
            print("final path", finalPath)
            
            if finalPath:
                print("I HAVE A FINAL PATH!")
                print("FINAL PATH: ", finalPath)
                searchForPath = False # We have now found a path
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
                        finalPosition = []
                        finalPath = []
                        mode = "idle"
                    

            #MOVES
            if finalPath and finalPosition:
                print("I HAVE A FINAL POSITION!")
                stoppingDist = stopping_distance(mass, friction, thrustPower, selfSpeed)
                moveToPos(selfX, selfY, [targetPosition[1]*ai.blockSize(), targetPosition[0]*ai.blockSize()], stoppingDist)
            else:
                print("NO FINAL POSITION")

        #TODO: Search and destroy
        elif mode == "destroy":
            pass
        #TODO: Astar safe path
        elif mode == "refuel":
            fuelIndex = random.randint(0, ai.fuelstationCount())
            refueling = False

            #GET FEULSTATION X AND Y POS
            finalxPosition = ai.fuelstationBlockX(fuelIndex)
            finalyPosition = mapHeight - ai.fuelstationBlockY(fuelIndex)

            finalxAndyPosition = [finalyPosition - 1, finalxPosition]

            targetPos = finalxAndyPosition

            mode = "move"
            #TODO: USE WITH ASTAR

            if refueling:
                '''Amount of fuel in station'''
                if ai.fuelstationFuel(fuelIndex) > 0:
                    '''Keep calling to refuel'''
                    ai.refuel()
                else:
                    mode = "idle"

            '''Number of fueltanks on server'''
            #ai.tankCountServer()
            '''Number of fuelstations on server'''
            #ai.fuelstationCount()
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

                itemX = ai.itemX(itemId)
                itemY = ai.itemY(itemId)
                itemVelX = ai.itemVelX(itemId)
                itemVelY = ai.itemVelY(itemId)

                deltaPosX = itemX - selfX
                deltaPosY = itemY - ai.selfY()

                deltaVelX = itemVelX - selfVelX
                deltaVelY = itemVelY - selfVelY

                time = time_of_impact(deltaPosX, deltaPosY, itemVelX, itemVelY, 10)
                targetPosition = vector_sum((deltaPosX, deltaPosY), scalar_product((deltaVelX, deltaVelY), time))

                ai.turnToRad(math.atan2(targetPosition[1], targetPosition[0]))

                if selfSpeed < 10:
                    thrust(10)
                else:
                    brake(2)

    except:
        print(traceback.print_exc())


#process = multiprocessing.Process(target=getPath, args=(maplist, start, end))
#process.start() # ONCE!

# MULTITHREADING
def calc_path():#startQueue, endQueue):
    #startPos = ()
    #endPos = ()

    while True:
        '''
        try:
            startPos = startQueue.get(timeout=1)
            endPos = endQueue.get(timeout=1)
        except queue.Empty:
            print("Queue is empty")
        '''
        if searchForPath:
            finalPath = getPath(pixelsToBlockSize(mapWidth, mapHeight), tuple(finalPosition), mapWidth, mapHeight)

#MAIN FUNCTIONS

'''aim at a specified target'''
def aim(targetId):
    if targetId == 0:
        pass
    else:
        if not (angleDiff < 0.25 or angleDiff > 2*math.pi - 0.25):
            xDiff = ai.targetX(targetId) - ai.selfX()
            yDiff = ai.targetY(targetId) - ai.selfY()
            targetDirection = math.atan2(yDiff, xDiff)
            ai.turnToRad(targetDirection)
            angleDiff = abs(targetDirection - selfHeading)

def moveToPos(selfX, selfY, targetPositionPixels, stoppingDistance):
    deltaX = targetPositionPixels[0] - selfX
    deltaY = selfY - targetPositionPixels[1]
    targetDirection = (math.atan2(deltaY, deltaX))
    distanceToTarget = math.sqrt((targetPositionPixels[0] - selfX)**2 + (targetPositionPixels[1] - selfY)**2)
    isBraking = distanceToTarget < stoppingDistance

    if not isBraking:
        ai.turnToRad(targetDirection)
        ai.setPower(40)
        ai.thrust()
    else:
        brake(2)

def brake(targetSpeed=2):
    if selfSpeed > targetSpeed:
        ai.turnToRad(selfTracking + math.pi)
        ai.thrust()

def getPath(start, end, mapWidth, mapHeight, drawPlayers=False, drawItems=False, printWholeMap=False):
    maplist = [['x' if ai.mapData(x,y) == 1 else ' ' for x in range(mapWidth)] for y in range(mapHeight-1, -1, -1)]

    if drawPlayers:
        maplist = placeTargets(players, 'p', maplist)
    if drawItems:
        maplist = placeTargets(items, 'i', maplist)

    #START/END ARE TUPLES OF FORM (Y, X)
    path = ph.astar(maplist, start, end)


    #with concurrent.futures.ThreadPoolExecutor() as executor:
    #    print("CALCULATING 1!")
    #    future = executor.submit(ph.astar, maplist, start, end)
    #    print("CALCULATING 2!")
    #    path = future.result()
    #    print("FOUND PATH!!!")

    #pthThread = threading.Thread(target=ph.astar, args=(maplist, start, end))
    #pthThread.start()
    #pthThread.join()
    #path = ph.astar(maplist, start, end)

    #DRAW PATH IN CONSOLE
    for i in range(len(path)):
        maplist[path[i][0]][path[i][1]] = 'o'
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

    #OPTIMIZING PATH
    fPath = ph.main(maplist, path)
    fPath = fPath[1:]

    #MAKING PATH SAFER
    fPath = ph.makePathSafe(maplist, fPath)

    return fPath

def thrust(power):
    ai.setPower(power)
    ai.thrust()

def shoot():
    ai.fireShot()

'''Use Item Functions'''
def useMine(x, y):
    ai.dropMine()

def useMissile(x, y):
    ai.fireTorpedo()

def useLaser(x, y):
    ai.fireLaser()

def useFuel(x, y):
    ai.refuel()

def useCloak(x, y):
    ai.cloak()

def useTransporter(x, y):
    '''steal an opponents item'''
    ai.transporter()

def useTank(x, y):
    '''currently selected tank'''
    #ai.selfFuelCurrent
    '''detaches fuel tank from ship'''
    #ai.tankDetach()
    '''switch to ships next fuel tank'''
    #ai.nextTank()
    '''switch to ships previous fuel tank'''
    #ai.prevTank()
    pass

def useEcm(x, y):
    '''Temporarily blind opponents'''
    ai.ecm()

def useEmergencyThrust(x, y):
    ai.emergencyThrust()

def useTractorBeam(x, y):
    '''Pull enemy ships towards the ship'''
    ai.tractorBeam()

def useAutoPilot(x, y):
    '''Stop the ships movement'''
    ai.toggleAutopilot()

def useEmergencyShield(x, y):
    ai.emergencyShield()

def useItemDeflector(x, y):
    '''Pushes everything away from the ship'''
    ai.deflector()

def useHyperJump(x, y):
    '''Puts the player on a random location at the map'''
    ai.hyperjump()

def usePhasing(x, y):
    '''Allows passing through walls'''
    ai.phasing()

def getMessage():
    msg = ai.scanTalkMsg(0)
    if ":[" + name + "]" in msg:
        tsk = msg.split()
        ai.removeTalkMsg(0)
        print(tsk)
        latestTask = tsk[0]
        if tsk[0] == "move-to-stop" or tsk[0] == "move-to-pass" or tsk[0] == "move-to-pos":
            x = tsk[1]
            y = tsk[2]
            print("MOVING TO POS")
            finalPosition = [int(y),int(x)]
            return "move", finalPosition
        elif tsk[0] == "collect-item":
            itemDict = {0: "fuel", 1: "wideangle", 2: "rearshot", 3: "afterburner", 4: "cloak", 5: "sensor",
            6: "transporter", 7: "tank", 8: "mine", 9: "missile", 10: "ecm",
            11: "laser", 12: "emergencythrust", 13: "tractorbeam", 14: "autopilot", 15: "emergencyshield",
            16: "itemdeflector", 17: "hyperjump", 18:"phasing", 19:"mirror", 20:"armor"}

            for key in itemDict:
                if tsk[1] == itemDict[key]:
                    return "collect", key
        elif tsk[0] == "use-item":
            useItemDict = {"mine": useMine, "missile": useMissile, "laser": useLaser, "fuel": useFuel, "cloak": useCloak,
                           "transporter": useTransporter, "tank": useTank, "ecm": useEcm, "emergencythrust":useEmergencyThrust,
                           "tractorbeam": useTractorBeam, "autopilot": useAutoPilot, "emergencyshield": useEmergencyShield,
                           "itemdeflector": useItemDeflector, "hyperjump": useHyperJump, "phasing": usePhasing}

            for key in useItemDict:
                if tsk[1] == key:
                    if len(tsk) >= 5:
                        useItemDict[key](tsk[2], tsk[3])
                    else:
                        useItemDict[key](0, 0)
        elif tsk[0] == "refuel":
            return "refuel", []

    return "idle", []

def sendMessage(receiver):
    ai.talk(receiver + ":" + latestTask + " completed")

#HELP FUNCTIONS

#ASTAR FUNCTIONS
def placeTargets(lis, char, maplis):
    for pos in lis:
        maplis[pos[0]][pos[1]] = char
    return maplis

def pixelsToBlockSize(mapWidth, mapHeight):
    playerX = int(ai.selfX() // ai.blockSize())-0
    playerY = mapHeight-1 - int((ai.selfY() // ai.blockSize())-1)
    return (playerY, playerX)

#BASIC NAVIGATION FUNCTIONS
def stopping_distance(mass, friction, thrustPower, selfSpeed):
            fForce = friction * mass
            tForce = thrustPower
            accTot = ((fForce/mass) + (tForce/(mass+5)))
            return ((selfSpeed * selfSpeed) / (2 * accTot))

def distance(posA, posB):
    return math.sqrt((posA[0] - posB[0])**2 + (posA[1] - posB[1])**2)

#ASTEROIDS FUNCTIONS
def scalar_product(lis, n):
    return [x * n for x in lis]

def vector_sum(list1, list2):
    return [sum(x) for x in zip(list1, list2)]

def time_of_impact(px, py, vx, vy, s):
    a = s * s - (vx * vx + vy * vy)
    b = px * vx + py * vy
    c = px * px + py * py

    d = b*b + a*c

    time = 0
    if d >= 0:
        time = (b + math.sqrt(d)) / a
        if (time < 0):
            time = 0
    return time

# Parse the command line arguments
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
