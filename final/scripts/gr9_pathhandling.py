#PATH SAFERIZATION
def makePathSafe(maplist, nodes):
    newPath = []
    
    for node in nodes:
        
        right = (maplist[node[0]][node[1] + 1] == "x")
        left = (maplist[node[0]][node[1] - 1] == "x")
        above = (maplist[node[0] - 1][node[1]] == "x")
        under = (maplist[node[0] + 1][node[1]] == "x")

        aboveAndUnder = (above and under)
        leftAndRight = (left and right)

        downRight = (maplist[node[0] + 1][node[1] + 1] == "x")
        upLeft = (maplist[node[0] - 1][node[1] - 1] == "x")
        upRight = (maplist[node[0] - 1][node[1] + 1] == "x")
        downLeft = (maplist[node[0] + 1][node[1] - 1] == "x")

        upRightAndDownLeft = (upRight and downLeft)
        upLeftAndDownRight = (upLeft and downRight)

        '''
        
        UNSAFE PATHS
              | x   x |     x
        x x x | x   x |   x       x
          o   | x o x | x   o   x  
        x x x | x   x |       x
        
        '''

        if aboveAndUnder or leftAndRight or upRightAndDownLeft or upLeftAndDownRight:
            #stay or take new path
            newPath.append((node[0], node[1]))
        elif above:
            #move down
            newPath.append((node[0] + 1, node[1]))
        elif under:
            #move up
            newPath.append((node[0] - 1, node[1]))
        elif left:
            #move righ
            newPath.append((node[0], node[1] + 1))
        elif right:
            #move left
            newPath.append((node[0], node[1] - 1))
        elif upRight:
            #move down left
            newPath.append((node[0] + 1, node[1] - 1))
        elif upLeft:
            #move down right
            newPath.append((node[0] + 1, node[1] + 1))
        elif downLeft:
            #move up right
            newPath.append((node[0] - 1, node[1] + 1))
        elif downRight:
            #move up left
            newPath.append((node[0] - 1, node[1] - 1))
        else:
            newPath.append((node[0], node[1]))
            
    return newPath

#NODE OPTIMIZATION
def drawMap(worldMap):
    for y in worldMap:
        for x in y:
            print(x, end=" ")
        print()

def removeNodesFromMap(worldMap, nodes):
    for node in nodes:
        print("Node 1: {0}, Node 0: {1}".format(node[1], node[0]))
        worldMap[node[1]][node[0]] = " "
    return worldMap

def printNodes(nodes, keyword="NODES"):
    for node in nodes:
        print(keyword, node)

def checkNeighbour(index, path, x, y):
    nodeX = (path[index][0] + x == path[index + 1][0])
    nodeY = (path[index][1] + y == path[index + 1][1])
    nextNodeX = (path[index + 1][0] + x == path[index + 2][0])
    nextNodeY = (path[index + 1][1] + y == path[index + 2][1])
    if nodeX and nodeY:
        if nextNodeX and nextNodeY:
            return path[index + 1]
    return None

def removeNullLists(nodes):
    finalList = []
    for node in nodes:
        if not (node == None):
            finalList.append(node)
    return finalList

def main(worldMap, path):
    nodesToRemove = []
    for i in range(len(path)):
        if (i+2) < len(path):
            nodesToRemove.append(checkNeighbour(i, path, 1, 1))
            nodesToRemove.append(checkNeighbour(i, path, -1, 1))
            nodesToRemove.append(checkNeighbour(i, path, 1, -1))
            nodesToRemove.append(checkNeighbour(i, path, -1, -1))
            nodesToRemove.append(checkNeighbour(i, path, 0, 1))
            nodesToRemove.append(checkNeighbour(i, path, 1, 0))
            nodesToRemove.append(checkNeighbour(i, path, 0, -1))
            nodesToRemove.append(checkNeighbour(i, path, -1, 0))
        nodesToRemove = removeNullLists(nodesToRemove)
    
    finalPath = [x for x in path if x not in nodesToRemove]

    return finalPath

#ASTAR PATHFINDING
class Node():
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.currentCost = 0
        self.estimatedDistance = 0
        self.totalCost = 0

    def __eq__(self, other):
        return self.position == other.position

def astar(maplist, playerposition, goalposition):
    """Returns a list of tuples wich represents the shortest route"""

    #START NODE
    startNode = Node(None, playerposition)
    startNode.currentCost = 0
    startNode.estimatedDistance = 0
    startNode.totalCost = 0

    #GOAL NODE
    goalNode = Node(None, goalposition)
    goalNode.currentCost = 0
    goalNode.estimatedDistance = 0
    goalNode.totalCost = 0

    #INIT
    openList = []
    closedList = []

    openList.append(startNode)

    while len(openList) > 0:

        currentNode = openList[0]
        currentIndex = 0
        for index, item in enumerate(openList):
            if item.totalCost < currentNode.totalCost:
                currentNode = item
                currentIndex = index

        openList.pop(currentIndex)
        closedList.append(currentNode)

        #FOUND GOAL
        if currentNode == goalNode:
            path = []
            current = currentNode
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        children = []
        for neighbourPositions in [(0, -1),(0, 1),(-1, 0),(1, 0),(-1, -1),(-1, 1),(1, -1),(1, 1)]:

            nodePosition = (currentNode.position[0] + neighbourPositions[0], currentNode.position[1] + neighbourPositions[1])

            inRange = nodePosition[0] > (len(maplist) - 1) or nodePosition[0] < 0 or nodePosition[1] > (len(maplist[len(maplist)-1]) -1) or nodePosition[1] < 0
            nonWalkable = maplist[nodePosition[0]][nodePosition[1]] != ' '
            
            if inRange or nonWalkable:
                continue

            children.append(Node(currentNode, nodePosition))

        for child in children:
            child.currentCost = currentNode.currentCost + 1
            child.estimatedDistance = ((child.position[0] - goalNode.position[0]) ** 2) + ((child.position[1] - goalNode.position[1]) ** 2)
            child.totalCost = child.currentCost + child.estimatedDistance
            openList.append(child)
