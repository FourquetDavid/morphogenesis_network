'''
Created on 15 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
'''
import networkx as nx
import random
import numpy  as np

""" 
contains one main function :

*grow_network : takes a tree of decision and returns the graph that grows according to those rules
    Tree : consider an edge, returns a real number
        max depth : 3. 
        each leaf can be one of :
        "OrigId"  "TargId" "OrigInDegree" "OrigOutDegree"  "TargInDegree"  "TargOutDegree" 
        each node can be one of : + - *
    
    Growth algorithm :
        begins with an empty graph with the number of nodes  of the real network
        at each step the tree gives a probability to every possible edge
        one edge is chosen randomly
        until the number of edges equals teh number of edges of the real network
        
    

"""
def grow_network(decision_tree,number_of_nodes, number_of_edges):
    '''takes a tree of decision and returns the graph that grows according to those rules'''
    #directed graph
    graph = nx.DiGraph() 
    #begins with an empty graph with the number of nodes  of the real network
    for i in range(number_of_nodes) :
        graph.add_node(i)
    
    #adds one edge according to its probability
    for i in range(number_of_edges) :
        #each edge has a probability that is the result of the tree
        probas = calc(decision_tree.getRoot(),graph)
        for j in range(probas.shape[0]) :
            probas[j][j] = 0
        #we remove unnecessary edges    
        possible_edges = find_possible_edges(probas,graph)
        #we choose on among them
        edge = weighted_choice(possible_edges)
        graph.add_edge(*edge)
        
    return graph


'''
Functions that let us choose a random element in teh matrix of probabilities
'''
            
def find_possible_edges(matrice,network):
    ''' takes a matrix of probabilities and a network, 
    returns [edges,weight] of edges that can be selected for next step '''
    choices = []
    adjacency_matrix = nx.to_numpy_matrix(network)
    for i in range(matrice.shape[0]) :
        for j in range(matrice.shape[0]) :
            #we remove self-loops and already existing adges
            if i!=j and  adjacency_matrix[i,j] == 0:
                #negative probabiliies are considered as 0
                choices.append([[i,j],max(matrice[i][j],0)])
    return choices
      
def weighted_choice(choices): 
    ''' takes an array of [edge, weight], return one edge chosen randomly according to its weight
    '''
    #choices is never empty by construction
    total = sum(w for [c,w] in choices)
    #if all probabilities are 0, we choose one randomly
    if total == 0 :
        edge = random.choice([c for [c,w] in choices])
        return edge
    #else we compute the cumulative distribution of weights and choose one randomly
    r = random.uniform(0, total)
    upto = 0
    for [c,w] in choices:
        if upto+w > r:
            return c
        upto += w
    
'''
Functions that compute the tree for each node
'''

def calc(node, graph): 
    ''' takes a node of the decision tree and a graph
    computes recursively a value for each edge of the graph at the same time
    returns a 2D array containing the value for each edge
    '''
    data = node.getData()
    #we have 6 posible leaves
    if node.isLeaf() :
        if data == "OrigId" : return OrigId(graph)
        if data == "TargId" : return TargId(graph)
        if data == "OrigInDegree" : return OrigInDegree(graph)
        if data == "OrigOutDegree" : return OrigOutDegree(graph)
        if data == "TargInDegree" : return TargInDegree(graph)
        if data == "TargOutDegree" : return TargOutDegree(graph)
    else :
        #recursive computation on function nodes : 3 possibilities, we always have 2 children, by construction
        value0 = calc(node.getChild(0), graph)
        value1 = calc(node.getChild(1), graph)
        if data == "+" : return value0 + value1
        if data == "-" : return value0 - value1
        if data == "*" : return value0 * value1
        
def OrigInDegree(graph) : 
    ''' returns a 2d array containing the in degree of the origin node for all edges
    '''
    probas = np.dot( 
                  np.transpose(np.array(list(graph.in_degree().values()))[np.newaxis,:]),
                  np.ones((1,graph.number_of_nodes())))
    return probas

def OrigOutDegree(graph) :
    ''' returns a 2d array containing the out degree of the origin node for all edges
    '''
    probas = np.dot( 
                  np.transpose(np.array(list(graph.out_degree().values()))[np.newaxis,:]),
                  np.ones((1,graph.number_of_nodes())))
    return probas

def OrigId(graph) :
    ''' returns a 2d array containing the identity number (0 to n=number of nodes) of the origin node for all edges
    ''' 
    probas = np.dot( 
                  np.transpose(np.array(range(graph.number_of_nodes()))[np.newaxis,:]),
                  np.ones((1,graph.number_of_nodes())))
    return probas

def TargInDegree(graph) : 
    ''' returns a 2d array containing the in degree of the target node for all edges
    ''' 
    probas =  np.dot( 
                  np.ones((graph.number_of_nodes(),1)),
                  np.array(list(graph.in_degree().values()), ndmin=2,dtype=float)
                  )        
    return probas



def TargOutDegree(graph) :
    ''' returns a 2d array containing the out degree of the target node for all edges
    ''' 
    probas =  np.dot( 
                  np.ones((graph.number_of_nodes(),1)),
                  np.array(list(graph.out_degree().values()), ndmin=2,dtype=float)
                  )        
    return probas
   
def TargId(graph) : 
    ''' returns a 2d array containing the identity number of the target node for all edges
    ''' 
    probas =  np.dot( 
                  np.ones((graph.number_of_nodes(),1)),
                  np.array(range(graph.number_of_nodes()), ndmin=2,dtype=float)
                  )        
    return probas
    


  


    
    
          






