import threading
import time

'''
Create an instance of AStarThread.
To retrieve a path, do the following:
    - Set the A* arguments every frame by calling the setArgs method.
    - Start the thread ONCE (i.e check if it's running). Note that
      using the isAlive() function may not work.
    - While the thread is running, you can retrieve the path by
      accessing it through the attribute "path" (i.e pathThread.path,
      assuming the instance is called pathThread).

      # E.g:
      [before the tick function]:
      # pathThread = astr_threading.AStarThread(1) [this should be global]
      # threadAlive = False [this should be global]
      # ...
      [in the tick function]:
      # pathThread.setArgs(...)
      # if not threadAlive:
            pathThread.start()
            threadAlive = True
      # ...
      # ...
      # finalPath = nodeHandler.main(maplist, pathThread.path)
'''


class AStarThread(threading.Thread):
    def __init__(self, threadId):
        threading.Thread.__init__(self)
        self.threadId = 0#threaart()dId
        self.startPos = ()#start
        self.endPos = ()#end
        self.mapWidth = 0#mapWidth
        self.mapHeight = (0)#mapHeight
        self.intervalInSeconds = 0#intervalInSeconds

        self.drawPlayers = False
        self.drawItems = False
        self.printWholeMap = False

        self.path = []

    # Test. Tastes like spaghetti
    def setArgs(self, startPos, endPos, mapWidth, mapHeight, intervalInSeconds):
        self.startPos = startPos
        self.endPos = endPos
        self.mapWidth = mapWidth
        self.mapHeight = mapHeight
        self.intervalInSeconds = intervalInSeconds

        print("Self.path = ", self.path) # It exists here???

    def run(self):
        '''Calculate path and synchronize threads (if this is even required)'''
        threadLock = threading.Lock() # Probably not needed
        threadLock.acquire() # Synchronize threads (probably not needed)

        print("Calculating A-Star path. Thread ID: {0}. Interval: {1}".format(self.threadId, self.intervalInSeconds))
        self.path = getPath(self.startPos, self.endPos, self.mapWidth, self.mapHeight)
        time.sleep(self.intervalInSeconds)

        threadLock.release() # Free lock to release next thread (probably not needed)

    def getPath(start, end, mapWidth, mapHeight):
        maplist = [['x' if ai.mapData(x,y) == 1 else ' ' for x in range(mapWidth)] for y in range(mapHeight-1, -1, -1)]

        if self.drawPlayers:
            maplist = placeTargets(players, 'p', maplist)
        if self.drawItems:
            maplist = placeTargets(items, 'i', maplist)

        # start, end, tuples: (y, x)
        pth = astr.astar(maplist, start, end)

        #drawing path in console
        for i in range(len(path)):
            maplist[pth[i][0]][pth[i][1]] = 'o'
        playerPos = pixelsToBlockSize(mapWidth-1, mapHeight-1)


        print("pPos:", playerPos)
        maplist[playerPos[0]][playerPos[1]] = "P"
        viewDist = 20

        notOutXRight = not (playerPos[1] + viewDist//2 > mapWidth-1)
        notOutXLeft = not (playerPos[1] - viewDist//2 < 0)
        notOutYUp = not (playerPos[0] + viewDist//2 > mapHeight-1)
        notOutYDown = not (playerPos[0] - viewDist//2 < 0)
        inRange = notOutXRight and notOutXLeft and notOutYUp and notOutYDown

        if self.printWholeMap:
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

        return pth
