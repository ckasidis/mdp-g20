from mazegraph import MazeGraph
import numpy as np
import queue
import json

# Main driver function
def main(map_dir, cmd_dir):
    ''' Main driver/wrapper function to execute all all sub functions'''
    try:
        filename1=map_dir
        filename2=cmd_dir
        maze, ObstacleList, GOALLIST = ReadWriteConvert(filename1)

        GOALLIST  = greedy_sort(GOALLIST)
        # print(ObstacleList)
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
            if cantreachgoal == True:
                BT = lol[i - 1][-2]
                nodesExplored, pathsExplored, nodesProcessed = astar_search(mazegraph, start=BT, goal=GOALLIST[i + 1])
                path, cantreachgoal, actions = reconstruct_path(nodesExplored, start=BT, goal=GOALLIST[i + 1])
            else:
                nodesExplored, pathsExplored, nodesProcessed = astar_search(mazegraph, start=GOALLIST[i], goal=GOALLIST[i + 1])
                path, cantreachgoal, actions = reconstruct_path(nodesExplored, start=GOALLIST[i], goal=GOALLIST[i + 1])

            lol.append(path)
            FinalActions += actions
            # print(lol)
            # print("path", i, "=", path)
            ActionsWCamera += actions
            ActionsWCamera.append('Camera')

        # print("Actions sent with Camera", ActionsWCamera)
        data = ActionsWCamera
        write_json(data, filename=filename2)
        return data
    except Exception as e:
        print('[PATH MAIN FUNC ERROR]', str(e))

def fixCommands(commands):
    cmds=[]
    for i in commands:
        if i=='Camera':
            cmds.append("RPI|TOCAM")
        else:
            cmds.append("STM|"+i)


    cmds.append("RPI_END")
    return cmds

def write_json(data, filename="testing.json"):
    cmds = fixCommands(data)
    with open(filename, "w") as f:
        json.dump(cmds, f, indent=4)

def ReadWriteConvert(filename = "AcquireFromAndriod.json"):
    # file = "AcquireFromAndriod.json"
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
    obstacles=[]
    with open(filename) as json_file:
        data = json.load(json_file)
        # obs = data.replace("ALGO|", "")
        obs = data[1:len(obstacles)-1]
        obs = obs.split(', ')
        # print(obs)

        for ob in obs:
            obj = ob[1:-1]
            obj = obj.split(',')
            obj[0] = int(obj[0])
            obj[1] = int(obj[1])
            # print(obj)
            obj[2] = obj[2][0]
            # print(obj[2][0])
            obstacles.append(obj)

    # print(obstacles)
    GOALLIST = []
    GOALLIST.append((2, 2, 'E'))
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

    # print(obstacles)

    for i in range(len(obstacles)):
        Direction = obstacles[i][2]
        Xcoords = obstacles[i][0]
        Ycoords = obstacles[i][1]
        maze[Xcoords][Ycoords] = 1
        if (Direction == "N"):
            maze[Xcoords - 2][Ycoords] = 0.5
            GOALLIST.append((Xcoords - 2, Ycoords, "S"))
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "N"))

        elif (Direction == "S"):
            maze[Xcoords + 2][Ycoords] = 0.5
            GOALLIST.append((Xcoords + 2, Ycoords, "N"))
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "S"))

        elif (Direction == "E"):
            maze[Xcoords][Ycoords + 2] = 0.5
            GOALLIST.append((Xcoords, Ycoords + 2, "W"))
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "E"))

        elif (Direction == "W"):
            maze[Xcoords][Ycoords - 2] = 0.5
            GOALLIST.append((Xcoords, Ycoords - 2, "E"))
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "W"))

        else:
            ObstacleList.append((Xcoords - 1, Ycoords - 1, "NIL"))

    # print(ObstacleList)
    # print("Goallist=", GOALLIST)

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
    try:
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
            if currentNode == goal:
                break

            # explore every single neighbor of current node
            for nextNode, weight, action in mazeGraph.neighbors(currentNode):

                # compute the new cost for the node based on the current node/ Calculating g(n)
                newcost = pathcost[currentNode] + weight

                if (nextNode not in explored) or (
                        newcost < pathcost[nextNode]):  # if the newcost is smaller then the nextNode
                    # priority= #f(n) = h(n) + g(n);
                    priority = heuristic(nextNode, goal) + newcost
                    # put new node in frontier with priority
                    frontier.put((priority, nextNode))

                    # Stores the parent node of the nextnode into explored
                    explored[nextNode] = currentNode, action

                    # updates g(n) for the nextNode
                    pathcost[nextNode] = newcost

        return explored, pathcost, processed
    except Exception as e:
        print('[ASTAR SEARCH ERROR]',str(e))

# Reconstruct the path from the Dict of explored nodes {node : parentNode}
# Intuition : Backtrack from the goal node by checking successive parents
def reconstruct_path(explored, start, goal):
    try:
        currentNode = goal  # start at the goal node
        path = []  # initiate the blank path
        actions = []
        direction = ['N', 'S', 'E', 'W']
        cantreachgoal = False
        # stop when backtrack reaches start node
        actions += explored[currentNode][1] 
        while currentNode != start:
            # grow the path backwards and backtrack
            flag = 0
            path.append(currentNode)
            try:
                currentNode = explored[currentNode][0]
            except KeyError:
                num = direction.index(currentNode[2])
                if num == 3:
                    num = -1
                currentNode = (currentNode[0], currentNode[1], direction[num + 1])
                cantreachgoal = True
                flag = 0

            if (flag == 0):
                try:
                    actions += explored[currentNode][1]
                except TypeError:
                    continue
            else:
                continue

                # Try Changing to left or right
            # currentNode = explored[currentNode]
        
        path.append(start)  # append start node for completeness
        path.reverse()  # reverse the path from start to goal

        actions.append
        actions.reverse()

        return path, cantreachgoal, actions

    except Exception as e:
        print("[RECONSTRUCTPATH ERROR]",str(e))
        # raise e

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
