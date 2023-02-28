import numpy as np
import queue
from itertools import groupby
import ast
import json


def ReadWriteConvert():
    file = r"C:\Users\siddh\Desktop\mdp-g20\rpi\rpi\algorithm_rpi\AcquirefromAndroid.json"
    maze = []
    for i in range(22):
        inner = []
        for j in range(22):
            if (i == 0 or i == 21):
                inner.append(1)
                continue
            if (j == 0 or j == 21):
                inner.append(1)
                continue
            inner.append(0)
        maze.append(inner)

    with open(file) as json_file:
        obstacles = json.load(json_file)

    print('obstacles before:\n', obstacles)
    print('obstacles type before:\n', type(obstacles))
    obstacles = ast.literal_eval(obstacles)
    print('obstacles after:\n', obstacles)
    print('obstacles type after:\n', type(obstacles))

    GOALLIST = []
    GOALLIST.append([2, 2, 'E',0])
    ObstacleList = []
    # Convert the list of obstacles to fit the tree
    for i in range(len(obstacles)):
        obstacles[i][0] += 1
        obstacles[i][1] += 1

        if (obstacles[i][2] == "E"):
            obstacles[i][2] = "S"

        elif (obstacles[i][2] == "N"):
            obstacles[i][2] = "E"

        elif (obstacles[i][2] == "S"):
            obstacles[i][2] = "W"

        elif (obstacles[i][2] == "W"):
            obstacles[i][2] = "N"

    print(obstacles)

    for i in range(len(obstacles)):
        Direction = obstacles[i][2]
        Xcoords = obstacles[i][0]
        Ycoords = obstacles[i][1]
        obstacleid = obstacles[i][3]
        maze[Xcoords][Ycoords] = 1

        if (Direction == "N"):
            maze[Xcoords - 2][Ycoords] = 0.5
            GOALLIST.append([Xcoords - 2, Ycoords, "S", obstacleid])
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "N"))

        elif (Direction == "S"):
            maze[Xcoords + 2][Ycoords] = 0.5
            GOALLIST.append([Xcoords + 2, Ycoords, "N",obstacleid])
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "S"))

        elif (Direction == "E"):
            maze[Xcoords][Ycoords + 2] = 0.5
            GOALLIST.append([Xcoords, Ycoords + 2, "W", obstacleid])
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "E"))

        elif (Direction == "W"):
            maze[Xcoords][Ycoords - 2] = 0.5
            GOALLIST.append([Xcoords, Ycoords - 2, "E",obstacleid])
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "W"))

        else:
            ObstacleList.append([Xcoords - 1, Ycoords - 1, "NIL"])

    print(ObstacleList)
    print("Goallist=", GOALLIST)

    maze = np.array(maze)

    return maze, ObstacleList, GOALLIST



def greedy_sort(coordinates):
    path = []
    current_point = coordinates[0]
    while coordinates:
        closest_point = min(coordinates, key=lambda x: ((x[0]-current_point[0])**2 + (x[1]-current_point[1])**2)**0.5)
        path.append(closest_point)
        current_point = closest_point
        coordinates.remove(closest_point)
    return path


class MazeGraph(object):
    ''' Class to represent a Graph
        Construction : Using Edges
    '''
    def __init__(self):
        self.edges = {}  # why are edges dictionary?

    def all_edges(self):
        return self.edges

    def neighbors(self, node):
        return self.edges[node]


# Function to convert a maze to a graph
def maze_to_graph(mazeGrid):
    ''' Converts a 2D binary maze to corresponding graph
        Input : 2D NumPy array with 0 and 1 as elements
        Output : MazeGraph corresponding to input maze
    '''

    directions = ["N", "S", "E", "W"]
    mazeGraph = MazeGraph()  # this initialize the class to mazeGraph
    (height, width) = mazeGrid.shape  # numpy array dimensions into a tuple?

    for i in range(height):
        for j in range(width):

            # Only consider blank cells as nodes
            # Instead of consdiering blank cells as nodes, try to allow obstacles to be nodes.
            if mazeGrid[i, j] != 1:

                # Adjacent cell : Top

                for d in directions:
                    neighbors = []
                    if (d == "N"):
                        # move forward
                        if (i > 1) and mazeGrid[i - 2, j] != 1 and mazeGrid[i - 2, j + 1] != 1 and mazeGrid[
                            i - 2, j - 1] != 1:
                            neighbors.append(((i - 1, j, d), 1, ["FW010"]))

                        # move backwards
                        if (i < height - 2) and mazeGrid[i + 2, j] != 1 and mazeGrid[i + 2, j + 1] != 1 and mazeGrid[
                            i + 2, j - 1] != 1:
                            neighbors.append(((i + 1, j, d), 1, ["BW010"]))

                        # forward left turn
                        exit = False
                        if (j > 3 and i > 3):  # ensure that it is within the border
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i - row, j - col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i - row, j - 1] == 1 or mazeGrid[i - row, j] == 1 or mazeGrid[
                                        i - row, j + 1] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if (exit == False):
                            neighbors.append(
                                ((i - 2, j - 2, "W"), 100, ["FL090"]))  # increase weights to reduce turning

                        # forward right turning
                        exit = False
                        if (i > 3 and j < width - 4):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i - row, j + col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i - row, j - 1] == 1 or mazeGrid[i - row, j] == 1 or mazeGrid[
                                        i - row, j + 1] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i - 2, j + 2, "E"), 100, ["FR090"]))  # increase weights to reduce turning

                        # Backward left Turning
                        exit = False
                        if (i < height - 4 and j > 3):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i + row, j - col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i + row, j - 1] == 1 or mazeGrid[i + row, j] == 1 or mazeGrid[
                                        i + row, j + 1] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i + 2, j - 2, "E"), 100, ["BL090"]))  # increase weights to reduce turning

                        # Backwards Right Turning
                        exit = False
                        if (i < height - 4 and j < width - 4):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i + row, j + col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i + row, j - 1] == 1 or mazeGrid[i + row, j] == 1 or mazeGrid[
                                        i + row, j + 1] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i + 2, j + 2, "W"), 100, ["BR090"]))  # increase weights to reduce turning

                        # Insert edges in the graph
                        if len(neighbors) > 0:  # if there exist neighbors
                            mazeGraph.edges[(i, j, d)] = neighbors

                    if (d == "S"):  # Vehicle is currently facing south
                        # move forwards
                        if (i < height - 2) and mazeGrid[i + 2, j] != 1 and mazeGrid[i + 2, j + 1] != 1 and mazeGrid[
                            i + 2, j - 1] != 1:
                            neighbors.append(((i + 1, j, d), 1, ["FW010"]))

                        # move backwards
                        if (i > 1) and mazeGrid[i - 2, j] != 1 and mazeGrid[i - 2, j + 1] != 1 and mazeGrid[
                            i - 2, j - 1] != 1:
                            neighbors.append(((i - 1, j, d), 1, ["BW010"]))

                        # move forward left turning
                        exit = False
                        if (i < height - 4 and j < width - 4):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i + row, j + col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i + row, j - 1] == 1 or mazeGrid[i + row, j] == 1 or mazeGrid[
                                        i + row, j + 1] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i + 2, j + 2, "E"), 100, ["FL090"]))  # increase weights to reduce turning

                        # move forward right turning
                        exit = False
                        if (i < height - 4 and j > 3):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i + row, j - col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i + row, j - 1] == 1 or mazeGrid[i + row, j] == 1 or mazeGrid[
                                        i + row, j + 1] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i + 2, j - 2, "W"), 100, ["FR090"]))  # increase weights to reduce turning

                        # move backwards left turning
                        exit = False
                        if (i > 3 and j < width - 4):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i - row, j + col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i - row, j - 1] == 1 or mazeGrid[i - row, j] == 1 or mazeGrid[
                                        i - row, j + 1] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i - 2, j + 2, "W"), 100, ["BL090"]))  # increase weights to reduce turning

                        # move backwards right turning
                        exit = False
                        if (j > 3 and i > 3):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i - row, j - col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i - row, j - 1] == 1 or mazeGrid[i - row, j] == 1 or mazeGrid[
                                        i - row, j + 1] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i - 2, j - 2, "E"), 100, ["BR090"]))  # increase weights to reduce turning

                        # Insert edges in the graph
                        if len(neighbors) > 0:  # if there exist neighbors
                            mazeGraph.edges[(i, j, d)] = neighbors

                    if (d == "W"):  # facing the west direction
                        # move forwards
                        if (j > 1) and mazeGrid[i, j - 2] != 1 and mazeGrid[i - 1, j - 2] != 1 and mazeGrid[
                            i + 1, j - 2] != 1:
                            neighbors.append(((i, j - 1, d), 1, ["FW010"]))

                        # move backwards
                        if (j < width - 2) and mazeGrid[i, j + 2] != 1 and mazeGrid[i - 1, j + 2] != 1 and mazeGrid[
                            i + 1, j + 2] != 1:
                            neighbors.append(((i, j + 1, d), 1, ["BW010"]))

                        # move forward left turn
                        exit = False
                        if (i < height - 4 and j > 3):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i + row, j - col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i, j - col] == 1 or mazeGrid[i + 1, j - col] == 1 or mazeGrid[
                                        i - 1, j - col] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i + 2, j - 2, "S"), 100, ["FL090"]))  # increase weights to reduce turning

                        # move forward right turn
                        exit = False
                        if (j > 3 and i > 3):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i - row, j - col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i, j - col] == 1 or mazeGrid[i - 1, j - col] == 1 or mazeGrid[
                                        i + 1, j - col] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i - 2, j - 2, "N"), 100, ["FR090"]))  # increase weights to reduce turning

                        # move backwards left turn
                        exit = False
                        if (i < height - 4 and j < width - 4):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i + row, j + col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i, j + col] == 1 or mazeGrid[i + 1, j + col] == 1 or mazeGrid[
                                        i - 1, j + col] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i + 2, j + 2, "N"), 100, ["BL090"]))  # increase weights to reduce turning

                        # move backwards right turn
                        exit = False
                        if (i > 3 and j < width - 4):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i - row, j + col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i, j + col] == 1 or mazeGrid[i - 1, j + col] == 1 or mazeGrid[
                                        i - 1, j + col] == 1):
                                        exit = True
                                        break

                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i - 2, j + 2, "S"), 100, ["BR090"]))  # increase weights to reduce turning

                        # Insert edges in the graph
                        if len(neighbors) > 0:  # if there exist neighbors
                            mazeGraph.edges[(i, j, d)] = neighbors

                    if (d == "E"):
                        # move forward
                        if (j < width - 2) and mazeGrid[i, j + 2] != 1 and mazeGrid[i - 1, j + 2] != 1 and mazeGrid[
                            i + 1, j + 2] != 1:
                            neighbors.append(((i, j + 1, d), 1, ["FW010"]))

                        # move backwards
                        if (j > 1) and mazeGrid[i, j - 2] != 1 and mazeGrid[i - 1, j - 2] != 1 and mazeGrid[
                            i + 1, j - 2] != 1:
                            neighbors.append(((i, j - 1, d), 1, ["BW010"]))

                        # move forward right turn
                        exit = False
                        if (i < height - 4 and j < width - 4):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i + row, j + col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i, j + col] == 1 or mazeGrid[i - 1, j + col] == 1 or mazeGrid[
                                        i + 1, j + col] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True
                        if exit == False:
                            neighbors.append(
                                ((i + 2, j + 2, "S"), 100, ["FR090"]))  # increase weights to reduce turning

                        # move forward left turn
                        exit = False
                        if (i > 3 and j < width - 4):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i - row, j + col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i, j + col] == 1 or mazeGrid[i + 1, j + col] == 1 or mazeGrid[
                                        i - 1, j + col] == 1):
                                        exit = True
                                        break

                        else:
                            exit = True
                        if exit == False:
                            neighbors.append(
                                ((i - 2, j + 2, "N"), 100, ["FL090"]))  # increase weights to reduce turning

                        # move backwards left turn
                        exit = False
                        if (j > 3 and i > 3):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i - row, j - col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i, j - col] == 1 or mazeGrid[i - 1, j - col] == 1 or mazeGrid[
                                        i + 1, j - col] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i - 2, j - 2, "S"), 100, ["BL090"]))  # increase weights to reduce turning

                        # move backwards right turn
                        exit = False
                        if (i < height - 4 and j > 3):
                            for row in range(1, 4):
                                if exit == True:
                                    break
                                for col in range(1, 4):
                                    if (mazeGrid[i + row, j - col] == 1):
                                        exit = True
                                        break
                                    if (mazeGrid[i, j - col] == 1 or mazeGrid[i + 1, j - col] == 1 or mazeGrid[
                                        i - 1, j - col] == 1):
                                        exit = True
                                        break
                        else:
                            exit = True

                        if exit == False:
                            neighbors.append(
                                ((i + 2, j - 2, "N"), 100, ["BR090"]))  # increase weights to reduce turning

                        if len(neighbors) > 0:  # if there exist neighbors
                            mazeGraph.edges[(i, j, d)] = neighbors

    return mazeGraph


def heuristic(nodeA, nodeB):
    (xA, yA, AD) = nodeA  # gets the coodinates of X and Y of current node
    (xB, yB, BD) = nodeB  # gets the coordinates of X and Y of Destination node
    return abs(xA - xB) + abs(yA - yB)


# A*-Search (A*S) with Priority Queue

def astar_search(mazeGraph, start, goal):
    ''' Function to perform A*S to find path in a graph
        Input  : Graph with the start and goal vertices
        Output : Dict of explored vertices in the graph
    '''
    frontier = queue.PriorityQueue()  # Priority Queue for Frontier

    # initialization
    frontier.put((0, start))  # Add the start node to frontier with priority 0
    explored = {}  # Dict of explored nodes {node : parentNode}
    explored[start] = None  # start node has no parent node
    pathcost = {}  # Dict of cost from start to node
    pathcost[start] = 0  # start to start cost should be 0
    processed = 0  # Count of total nodes processed

    while not frontier.empty():
        currentNode = frontier.get()[1]
        processed += 1

        # stop when goal is reached
        if currentNode in goal:
            if (processed != 1):
                break

        # explore every single neighbor of current node
        for nextNode, weight, action in mazeGraph.neighbors(currentNode):

            # compute the new cost for the node based on the current node/ Calculating g(n)
            newcost = pathcost[currentNode] + weight

            if (nextNode not in explored) or (
                    newcost < pathcost[nextNode]):  # if the newcost is smaller then the nextNode
                # priority= #f(n) = h(n) + g(n);
                priority = heuristic(nextNode, goal[0]) + newcost
                # put new node in frontier with priority
                frontier.put((priority, nextNode))

                # Stores the parent node of the nextnode into explored
                explored[nextNode] = currentNode, action

                # updates g(n) for the nextNode
                pathcost[nextNode] = newcost

    return explored, pathcost, processed, currentNode


# Reconstruct the path from the Dict of explored nodes {node : parentNode}
# Intuition : Backtrack from the goal node by checking successive parents
def reconstruct_path(explored, start, goal):
    currentNode = goal  # start at the goal node
    path = []  # initiate the blank path
    actions = []
    cantreachgoal = False
    # stop when backtrack reaches start node
    try:
        actions += explored[currentNode][1]
    except TypeError:
        return
    while currentNode != start:
        # grow the path backwards and backtrack
        flag = 0
        path.append(currentNode)
        currentNode = explored[currentNode][0]
        try:
            actions += explored[currentNode][1]
        except TypeError:
            continue

            # Try Changing to left or right
        # currentNode = explored[currentNode]
    path.append(start)  # append start node for completeness
    path.reverse()  # reverse the path from start to goal

    actions.append
    actions.reverse()
    return path, cantreachgoal, actions


def write_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def finalmain():
    maze, ObstacleList, GOALLIST = ReadWriteConvert()
    GOALLIST  = greedy_sort(GOALLIST)
    Obstaclevisit = []
    print(GOALLIST)
    for i in range(len(GOALLIST)):
        if(i==0):
            GOALLIST[i].pop()
            GOALLIST[i] = tuple(GOALLIST[i])
        else:
            Obstaclevisit.append("AND|OBS-"+ str(GOALLIST[i].pop()))
            GOALLIST[i] = tuple(GOALLIST[i])
    write_json(Obstaclevisit, filename="ObjectIDsequence.json")

    for i in range(1, len(GOALLIST)):
        temp = []
        current = GOALLIST[i]

        temp.append(current)
        if current[2] == "E" or current[2] == "W":
            if (current[0] > 2):
                tempSideGoal = list(current)
                tempSideGoal[0] = tempSideGoal[0] - 1
                temp.append(tuple(tempSideGoal))
                maze[tempSideGoal[0], tempSideGoal[1]] = 0.5

            if (current[0] < 19):
                tempSideGoal = list(current)
                tempSideGoal[0] = tempSideGoal[0] + 1
                temp.append(tuple(tempSideGoal))
                maze[tempSideGoal[0], tempSideGoal[1]] = 0.5


        elif current[2] == "N" or current[2] == "S":
            if (current[1] > 2):
                tempSideGoal = list(current)
                tempSideGoal[1] = tempSideGoal[1] - 1
                temp.append(tuple(tempSideGoal))
                maze[tempSideGoal[0], tempSideGoal[1]] = 0.5

            if (current[1] < 19):
                tempSideGoal = list(GOALLIST[i])
                tempSideGoal[1] = tempSideGoal[1] + 1
                temp.append(tuple(tempSideGoal))
                maze[tempSideGoal[0], tempSideGoal[1]] = 0.5
        GOALLIST[i] = temp

    print(GOALLIST)
        ### Convert the maze to a graph
    mazegraph = maze_to_graph(maze)

    # Print the edges with weights
    mazegraph.all_edges()

    ActionsWCamera = []
    cantreachgoal = False
    # Run the A*S algorithm for path finding
    lol = []
    FinalActions = []
    for i in range(len(GOALLIST) - 1):
        nodesExplored, pathsExplored, nodesProcessed, currentNode = astar_search(mazegraph, start=GOALLIST[i],
                                                                                 goal=GOALLIST[i + 1])
        GOALLIST[i + 1] = currentNode
        # print(nodesExplored[(2, 6, 'E')])
        path, cantreachgoal, actions = reconstruct_path(nodesExplored, start=GOALLIST[i], goal=currentNode)
        lol.append(path)
        FinalActions += actions
        #     print(lol)
        #print("path", i, "=", path)
        ActionsWCamera += actions
        ActionsWCamera.append('Camera')

    print("Actions sent with Camera", ActionsWCamera)
    data = ActionsWCamera
    write_json(data, filename = "testing234.json")
    return data


def fix_Commands(commands):
    print("Commands before fixing:\n",commands)
    cmds = []
    for i in commands:
        if i == 'Camera':
            cmds.append("RPI|TOCAM")  # keyword for camera
        elif 'AND|' in i:
            cmds.append(i)
        else:
            cmds.append("STM|" + i)

    cmds.append("RPI_END|0")  # add stop word
    # return cmds
    print("Commands after fix 1:\n", cmds)
    grouped_L = [(k, sum(1 for i in g)) for k, g in groupby(cmds)]
    print("Counted:\n",grouped_L)
    new_cmds = []
    for i in grouped_L:
        cmd = i[0].split("|", 1)[1]
        cnt=i[1]
        if cnt<10: 
            if cmd == "FW010":
                newCmd = "STM|FW0" + str(i[1]) + "0"
                new_cmds.append(newCmd)
            elif cmd == "BW010":
                newCmd = "STM|BW0" + str(i[1]) + "0"
                new_cmds.append(newCmd)
            else:
                for j in range(cnt):
                    new_cmds.append(i[0])
        elif cnt>=10: 
            if cmd == "FW010":
                newCmd = "STM|FW" + str(i[1]) + "0"
                new_cmds.append(newCmd)
            elif cmd == "BW010":
                newCmd = "STM|BW" + str(i[1]) + "0"
                new_cmds.append(newCmd)
            else:
                for j in range(cnt):
                    new_cmds.append(i[0])
    # print(new_cmds)
    return new_cmds
    print("commands after fix 2:\n", new_cmds)


def RunMain():
    data1 = finalmain()
    data = fix_Commands(data1)
# data = fix_Commands(data)
    print("\n\n\n\n",data)
    # print("\n\n\n\n",data1)
    return data

