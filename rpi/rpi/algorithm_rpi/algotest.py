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

    GOALLIST = []
    GOALLIST.append([2, 2, 'E', 0])
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

    goalincrement = 3

    for i in range(len(obstacles)):
        Direction = obstacles[i][2]
        Xcoords = obstacles[i][0]
        Ycoords = obstacles[i][1]
        obstacleid = obstacles[i][3]

        maze[Xcoords][Ycoords] = 1
        maze[Xcoords - 1][Ycoords + 1] = 0.7  # topleft
        maze[Xcoords][Ycoords + 1] = 0.7  # top
        maze[Xcoords + 1][Ycoords + 1] = 0.7  # top right
        maze[Xcoords + 1][Ycoords] = 0.7  # right
        maze[Xcoords + 1][Ycoords - 1] = 0.7  # bottom right
        maze[Xcoords][Ycoords - 1] = 0.7  # bottom
        maze[Xcoords - 1][Ycoords - 1] = 0.7  # bottomleft
        maze[Xcoords - 1][Ycoords] = 0.7  # left

        if (Direction == "N"):
            maze[Xcoords - goalincrement][Ycoords] = 0.5
            GOALLIST.append([Xcoords - goalincrement, Ycoords, "S", obstacleid])
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "N"))

        elif (Direction == "S"):
            maze[Xcoords + goalincrement][Ycoords] = 0.5

            GOALLIST.append([Xcoords + goalincrement, Ycoords, "N", obstacleid])
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "S"))

        elif (Direction == "E"):
            maze[Xcoords][Ycoords + goalincrement] = 0.5
            GOALLIST.append([Xcoords, Ycoords + goalincrement, "W", obstacleid])
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "E"))

        elif (Direction == "W"):
            maze[Xcoords][Ycoords - goalincrement] = 0.5
            GOALLIST.append([Xcoords, Ycoords - goalincrement, "E", obstacleid])
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "W"))

        else:
            ObstacleList.append([Xcoords - 1, Ycoords - 1, "NIL", obstacleid])

    print("Obstaclelist=", ObstacleList)
    print("Goallist=", GOALLIST)

    for i in range(22):
        maze[0][i] = 1
        maze[21][i] = 1
        maze[i][0] = 1
        maze[i][21] = 1

    maze = np.array(maze)

    return maze, ObstacleList, GOALLIST


def greedy_sort(coordinates):
    path = []
    current_point = coordinates[0]
    while coordinates:
        closest_point = min(coordinates,
                            key=lambda x: ((x[0] - current_point[0]) ** 2 + (x[1] - current_point[1]) ** 2) ** 0.5)
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

    fwleftarr = ["FL090", "FW016"]
    fwrightarr = ["FR090", "FW016"]
    bkrightarr = ["BW014", "BR090"]
    bkleftarr = ["BW014", "BL090"]

    ObstBoundary = 0.7

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
                            if mazeGrid[i - 2, j] == ObstBoundary or mazeGrid[i - 2, j + 1] == ObstBoundary or mazeGrid[
                                i - 2, j - 1] == ObstBoundary:
                                neighbors.append(((i - 1, j, d), 500, ["FW010"]))
                            else:
                                neighbors.append(((i - 1, j, d), 1, ["FW010"]))

                        # move backwards
                        if (i < height - 2) and mazeGrid[i + 2, j] != 1 and mazeGrid[i + 2, j + 1] != 1 and mazeGrid[
                            i + 2, j - 1] != 1:
                            if mazeGrid[i + 2, j] == 0.7 or mazeGrid[i + 2, j + 1] == 0.7 or mazeGrid[
                                i + 2, j - 1] == 0.7:
                                neighbors.append(((i + 1, j, d), 500, ["BW010"]))
                            else:
                                neighbors.append(((i + 1, j, d), 1, ["BW010"]))

                        # forward left turn
                        exit = False
                        if (j > 4 and i > 4):  # ensure that it is within the border
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i - row, j - col] == 0.7):
                                        neighbors.append(((i - 3, j - 3, "W"), 1000, fwleftarr))
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i - 3, j - 3, "W"), 100, fwleftarr))  # increase weights to reduce turning

                        # forward right turning
                        exit = False
                        if (i > 4 and j < width - 5):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i - row, j + col] == 0.7):
                                        neighbors.append(((i - 3, j + 3, "E"), 1000, fwrightarr))
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i - 3, j + 3, "E"), 100, fwrightarr))  # increase weights to reduce turning

                        # Backward left Turning
                        exit = False
                        if (i < height - 5 and j > 4):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i + row, j - col] == 0.7):
                                        neighbors.append(((i + 3, j - 3, "E"), 1000,
                                                          bkleftarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(((i + 3, j - 3, "E"), 100,
                                                  bkleftarr))  # increase weights to reduce turning

                        # Backwards Right Turning
                        exit = False
                        if (i < height - 5 and j < width - 5):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i + row, j + col] == 0.7):
                                        neighbors.append(((i + 3, j + 3, "W"), 1000,
                                                          bkrightarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i + 3, j + 3, "W"), 100, bkrightarr))  # increase weights to reduce turning

                        # Insert edges in the graph
                        if len(neighbors) > 0:  # if there exist neighbors
                            mazeGraph.edges[(i, j, d)] = neighbors

                    if (d == "S"):  # Vehicle is currently facing south
                        # move forwards
                        if (i < height - 2) and mazeGrid[i + 2, j] != 1 and mazeGrid[i + 2, j + 1] != 1 and mazeGrid[
                            i + 2, j - 1] != 1:
                            if mazeGrid[i + 2, j] == 0.7 or mazeGrid[i + 2, j + 1] == 0.7 or mazeGrid[
                                i + 2, j - 1] == 0.7:
                                neighbors.append(((i + 1, j, d), 500, ["FW010"]))
                            else:
                                neighbors.append(((i + 1, j, d), 1, ["FW010"]))

                        # move backwards
                        if (i > 1) and mazeGrid[i - 2, j] != 1 and mazeGrid[i - 2, j + 1] != 1 and mazeGrid[
                            i - 2, j - 1] != 1:
                            if mazeGrid[i - 2, j] == 0.7 or mazeGrid[i - 2, j + 1] == 0.7 or mazeGrid[
                                i - 2, j - 1] == 0.7:
                                neighbors.append(((i - 1, j, d), 500, ["BW010"]))
                            else:
                                neighbors.append(((i - 1, j, d), 1, ["BW010"]))

                        # move forward left turning
                        exit = False
                        if (i < height - 5 and j < width - 5):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i + row, j + col] == 0.7):
                                        neighbors.append(((i + 3, j + 3, "E"), 1000,
                                                          fwleftarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i + 3, j + 3, "E"), 100, fwleftarr))  # increase weights to reduce turning

                        # move forward right turning
                        exit = False
                        if (i < height - 5 and j > 4):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i + row, j - col] == 0.7):
                                        neighbors.append(((i + 3, j - 3, "W"), 1000,
                                                          fwrightarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i + 3, j - 3, "W"), 100, fwrightarr))  # increase weights to reduce turning

                        # move backwards left turning
                        exit = False
                        if (i > 4 and j < width - 5):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i - row, j + col] == 0.7):
                                        neighbors.append(((i - 3, j + 3, "W"), 1000,
                                                          bkleftarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i - 3, j + 3, "W"), 100, bkleftarr))  # increase weights to reduce turning

                        # move backwards right turning
                        exit = False
                        if (j > 4 and i > 4):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i - row, j - col] == 0.7):
                                        neighbors.append(((i - 3, j - 3, "E"), 1000,
                                                          bkrightarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i - 3, j - 3, "E"), 100, bkrightarr))  # increase weights to reduce turning

                        # Insert edges in the graph
                        if len(neighbors) > 0:  # if there exist neighbors
                            mazeGraph.edges[(i, j, d)] = neighbors

                    if (d == "W"):  # facing the west direction
                        # move forwards
                        if (j > 1) and mazeGrid[i, j - 2] != 1 and mazeGrid[i - 1, j - 2] != 1 and mazeGrid[
                            i + 1, j - 2] != 1:
                            if (mazeGrid[i, j - 2] == 0.7 or mazeGrid[i - 1, j - 2] == 0.7 or mazeGrid[
                                i + 1, j - 2] == 0.7):
                                neighbors.append(((i, j - 1, d), 500, ["FW010"]))
                            else:
                                neighbors.append(((i, j - 1, d), 1, ["FW010"]))

                        # move backwards
                        if (j < width - 2) and mazeGrid[i, j + 2] != 1 and mazeGrid[i - 1, j + 2] != 1 and mazeGrid[
                            i + 1, j + 2] != 1:
                            if mazeGrid[i, j + 2] == 0.7 or mazeGrid[i - 1, j + 2] == 0.7 or mazeGrid[
                                i + 1, j + 2] == 0.7:
                                neighbors.append(((i, j + 1, d), 500, ["BW010"]))
                            else:
                                neighbors.append(((i, j + 1, d), 1, ["BW010"]))

                        # move forward left turn
                        exit = False
                        if (i < height - 5 and j > 4):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i + row, j - col] == 0.7):
                                        neighbors.append(((i + 3, j - 3, "S"), 1000,
                                                          fwleftarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i + 3, j - 3, "S"), 100, fwleftarr))  # increase weights to reduce turning

                        # move forward right turn
                        exit = False
                        if (j > 4 and i > 4):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i - row, j - col] == 0.7):
                                        neighbors.append(((i - 3, j - 3, "N"), 1000,
                                                          fwrightarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i - 3, j - 3, "N"), 100, fwrightarr))  # increase weights to reduce turning

                        # move backwards left turn
                        exit = False
                        if (i < height - 5 and j < width - 5):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i + row, j + col] == 0.7):
                                        neighbors.append(((i + 3, j + 3, "N"), 1000,
                                                          bkleftarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i + 3, j + 3, "N"), 100, bkleftarr))  # increase weights to reduce turning

                        # move backwards right turn
                        exit = False
                        if (i > 4 and j < width - 5):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i - row, j + col] == 0.7):
                                        neighbors.append(((i - 3, j + 3, "S"), 1000,
                                                          bkrightarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i - 3, j + 3, "S"), 100, bkrightarr))  # increase weights to reduce turning

                        # Insert edges in the graph
                        if len(neighbors) > 0:  # if there exist neighbors
                            mazeGraph.edges[(i, j, d)] = neighbors

                    if (d == "E"):
                        # move forward
                        if (j < width - 2) and mazeGrid[i, j + 2] != 1 and mazeGrid[i - 1, j + 2] != 1 and mazeGrid[
                            i + 1, j + 2] != 1:
                            if mazeGrid[i, j + 2] == 0.7 or mazeGrid[i - 1, j + 2] == 0.7 or mazeGrid[
                                i + 1, j + 2] == 0.7:
                                neighbors.append(((i, j + 1, d), 500, ["FW010"]))
                            else:
                                neighbors.append(((i, j + 1, d), 1, ["FW010"]))

                        # move backwards
                        if (j > 1) and mazeGrid[i, j - 2] != 1 and mazeGrid[i - 1, j - 2] != 1 and mazeGrid[
                            i + 1, j - 2] != 1:
                            if mazeGrid[i, j - 2] == 0.7 or mazeGrid[i - 1, j - 2] == 0.7 or mazeGrid[
                                i + 1, j - 2] == 0.7:
                                neighbors.append(((i, j - 1, d), 500, ["BW010"]))
                            else:
                                neighbors.append(((i, j - 1, d), 1, ["BW010"]))

                        # move forward right turn
                        exit = False
                        if (i < height - 5 and j < width - 5):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i + row, j + col] == 0.7):
                                        neighbors.append(((i + 3, j + 3, "S"), 1000,
                                                          fwrightarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i + 3, j + 3, "S"), 100, fwrightarr))  # increase weights to reduce turning

                        # move forward left turn
                        exit = False
                        if (i > 4 and j < width - 5):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i - row, j + col] == 0.7):
                                        neighbors.append(((i - 3, j + 3, "N"), 1000,
                                                          fwleftarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i - 3, j + 3, "N"), 100, fwleftarr))  # increase weights to reduce turning

                        # move backwards left turn
                        exit = False
                        if (j > 4 and i > 4):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i - row, j - col] == 0.7):
                                        neighbors.append(((i - 3, j - 3, "S"), 1000,
                                                          bkleftarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i - 3, j - 3, "S"), 100, bkleftarr))  # increase weights to reduce turning

                        # move backwards right turn
                        exit = False
                        if (i < height - 5 and j > 4):
                            for row in range(2, 5):
                                if exit == True:
                                    break
                                for col in range(2, 5):
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
                            denote = False
                            for row in range(2, 5):
                                if denote == True:
                                    break
                                for col in range(2, 5):
                                    if (mazeGrid[i + row, j - col] == 0.7):
                                        neighbors.append(((i + 3, j - 3, "N"), 1000,
                                                          bkrightarr))  # increase weights to reduce turning
                                        denote = True
                                        break
                            if denote == False:
                                neighbors.append(
                                    ((i + 3, j - 3, "N"), 100, bkrightarr))  # increase weights to reduce turning

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
    GOALLIST = greedy_sort(GOALLIST)
    Obstaclevisit = []
    print(GOALLIST)
    for i in range(len(GOALLIST)):
        if (i == 0):
            GOALLIST[i].pop()
            GOALLIST[i] = tuple(GOALLIST[i])
        else:
            Obstaclevisit.append("AND|OBS-" + str(GOALLIST[i].pop()))
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
        path, cantreachgoal, actions = reconstruct_path(nodesExplored, start=GOALLIST[i], goal=currentNode)
        lol.append(path)
        FinalActions += actions
        ActionsWCamera += actions
        ActionsWCamera.append('Camera')

    i = 0
    while (True):
        if "FW" in ActionsWCamera[i] and "FW" in ActionsWCamera[i + 1]:
            Total = int(ActionsWCamera[i][2:]) + int(ActionsWCamera[i + 1][2:])
            ActionsWCamera[i + 1] = "FW" + str(Total)
            del (ActionsWCamera[i])
            continue
        if "BW" in ActionsWCamera[i] and "BW" in ActionsWCamera[i + 1]:
            Total = int(ActionsWCamera[i][2:]) + int(ActionsWCamera[i + 1][2:])
            ActionsWCamera[i + 1] = "BW" + str(Total)
            del (ActionsWCamera[i])
            continue

        if (i == len(ActionsWCamera) - 1):
            break
        i += 1

    print("Concat Actions:", ActionsWCamera)
    data = ActionsWCamera
    write_json(data, filename="testing234.json")
    return data, Obstaclevisit


def fix_Commands(commands):
    print("Commands before fixing:\n", commands)
    cmds = []
    for i in commands:
        if i == 'Camera':
            cmds.append("RPI|TOCAM")
        elif 'AND|' in i:
            cmds.append(i)
        else:
            cmds.append("STM|" + i)

    # cmds.append("RPI_END|0")  # add stop word
    return cmds
    # print("Commands after fix 1:\n", cmds)
    # grouped_L = [(k, sum(1 for i in g)) for k, g in groupby(cmds)]
    # print("Counted:\n", grouped_L)
    # new_cmds = []
    # for i in grouped_L:
    #     cmd = i[0].split("|", 1)[1]
    #     cnt = i[1]
    #     if cnt < 10:
    #         if cmd == "FW010":
    #             newCmd = "STM|FW0" + str(i[1]) + "0"
    #             new_cmds.append(newCmd)
    #         elif cmd == "BW010":
    #             newCmd = "STM|BW0" + str(i[1]) + "0"
    #             new_cmds.append(newCmd)
    #         else:
    #             for j in range(cnt):
    #                 new_cmds.append(i[0])
    #     elif cnt >= 10:
    #         if cmd == "FW010":
    #             newCmd = "STM|FW" + str(i[1]) + "0"
    #             new_cmds.append(newCmd)
    #         elif cmd == "BW010":
    #             newCmd = "STM|BW" + str(i[1]) + "0"
    #             new_cmds.append(newCmd)
    #         else:
    #             for j in range(cnt):
    #                 new_cmds.append(i[0])
    # # print(new_cmds)
    # return new_cmds
    # print("commands after fix 2:\n", new_cmds)


def RunMain():
    data1 = finalmain()
    data = fix_Commands(data1)
    print("\n\n\n\n", data)
    return data