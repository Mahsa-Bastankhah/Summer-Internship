#@author Mahsa Bastankhah
'''
This code propagates the transacion identifier in the lightning network and stops when a path is found
the goal is to find the average number of involved nodes in the route discovery process
'''
import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

iteration = 100
# uploading the LN graph
G = nx.read_gpickle("LNData.gpickle")

# calculate the sum of the degree of all the neighbours of one node
def calculateSumOfDegreeOfAllNbrs(node, G , suffNum):
    sumOfDegree = 0
    if suffNum == 1:
        for nbr in list(G.predecessors(node)):
            sumOfDegree = sumOfDegree + len(list(G.predecessors(nbr)))
    else:
        for nbr in list(G.successors(node)):
            sumOfDegree = sumOfDegree + len(list(G.successors(nbr)))

    return sumOfDegree

# this function instantiate a random pair of sender and receiver that are connected in the graph
def instanceSenderAndReceiver():
    goodPair = False
    while goodPair == False:
        sender = random.choice(list(G.nodes))
        receiver = random.choice(list(G.nodes))
        try:
            path = nx.shortest_path(G, sender, receiver)
            if receiver != sender:
                goodPair = True
        except:
            goodPair = False
    return sender , receiver , len(path)



# this function propagates the message to the neighbours of already touched nodes
def propagateMessage(queue, suffNum , distance):
    ## suffixes. S stands for the sender and R stands for the receiver
    suffs = ['S', 'R']
    pathFound = False
    for node in queue:
        if not G.nodes[node]['met_' + suffs[suffNum]]:
            G.nodes[node]['met_' + suffs[suffNum]] = True
            G.nodes[node]['Num_' + suffs[suffNum]] = distance

        sumOfAllDegree = calculateSumOfDegreeOfAllNbrs(node, G , suffNum)
        # choosing one of the neighbours randomly based on a degree proportional distribution
        whichSpread = np.random.rand()
        p = 0.0

        # gating the neighbours of the node
        if suffNum == 1:
            nbrList = list(G.predecessors(node))
        else :
            nbrList = list(G.successors(node))
        # forward the message to the chosen neighbour
        for nbr in nbrList:
            p += G.degree[nbr] / sumOfAllDegree
            if whichSpread <= p:
                if G.nodes[nbr]['met_' + suffs[1 - suffNum]]:
                    pathFound = True
                G.nodes[nbr]['met_' + suffs[suffNum]] = True
                return [nbr], pathFound



def findPath(sender, receiver):

    # at the beginning no node is touched from any side
    # met_S is true if the node has received the packet that was initiated from the sender
    # met_R is true if the node has received the packet that was initiated from the receiver
    # Num_S shows that what is the distance of this node in the path from the sender
    # Num_R shows that what is the distance of this node in the path from the receiver
    for node in G.nodes:
        G.nodes[node]['met_S'] = False
        G.nodes[node]['met_R'] = False
        G.nodes[node]['Num_S'] = -1
        G.nodes[node]['Num_R'] = -1
    #this queue contains the nodes that has received the packet  from the sender and
    #should forward this packet to their neighbours at this round
    queue_S = [sender]
    # this queue contains the nodes that has received the packet from the receiver and
    # should forward this packet to their neighbours at this round
    queue_R = [receiver]
    G.nodes[sender]['met_S'] = True
    G.nodes[receiver]['met_R'] = True
    G.nodes[sender]['Num_S'] = 0
    G.nodes[receiver]['Num_R'] = 0
    # the distance of the current propagating nodes from the sender or the receiver
    distanceSender = 0
    distanceReceiver = 0
    pathLength = 0

    # the totatl number of nodes that have receive the packet from at least one of the sender and the receiver
    touchedNodes = 0

    # this flag becomes true if an intermediary node receives the packet from both the sender and the receiver
    pathFound = False
    pathFoundReceiver = False
    pathFoundSender = False

    while not pathFound:
        #propagating the message from the sender
        try:
            queue_S, pathFoundSender = propagateMessage(queue_S, 0, distanceSender)
            touchedNodes += 1
            distanceSender = distanceSender + 1
        except:
            # in some rare cases the packet might get stuck
            return -1, -1
        try:
            queue_R, pathFoundReceiver = propagateMessage(queue_R, 1 , distanceReceiver)
            touchedNodes += 1
            distanceReceiver = distanceReceiver + 1
        except:
            # in some rare cases the packet might get stuck
            return -1 , -1
        pathFound = pathFoundSender or pathFoundReceiver or pathFound

    return touchedNodes , pathLength




plotIterationList = [i for i in range(iteration)]
touchedNodesNum = []
touchedNodesNumMeans = []
unsuccessfulAttempts = 0
# iterate the process to find the average
for i in range(iteration):
    sender, receiver , shortestPath = instanceSenderAndReceiver()
    touchedNodes, pathLength = findPath(sender, receiver)
    if touchedNodes == -1:
        unsuccessfulAttempts = unsuccessfulAttempts + 1
    else:
        touchedNodesNum.append(touchedNodes)
        touchedNodesNumMeans.append(np.average(touchedNodesNum))



## plotting the figures
print(" We had " + str(unsuccessfulAttempts) + " unsuccessful try out of " + str(iteration) + " attempts")
plt.plot( touchedNodesNum, 'g')
plt.plot( touchedNodesNumMeans, 'r')
plt.legend(['number of touched nodes' , 'mean of number of touched nodes '], loc='upper left')
plt.title("Lightning Network " )
plt.xlabel("iteration")
plt.ylabel("the average of number of touched nodes")
plt.show()

