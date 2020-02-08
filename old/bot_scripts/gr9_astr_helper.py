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
            walkable = maplist[nodePosition[0]][nodePosition[1]] != ' '
            
            if inRange or walkable:
                continue

            children.append(Node(currentNode, nodePosition))

        for child in children:
            child.currentCost = currentNode.currentCost + 1
            child.estimatedDistance = ((child.position[0] - goalNode.position[0]) ** 2) + ((child.position[1] - goalNode.position[1]) ** 2)
            child.totalCost = child.currentCost + child.estimatedDistance
            openList.append(child)
