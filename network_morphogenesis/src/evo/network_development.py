'''
Created on 15 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
'''


import random
import numpy  as np
import operator as op
import math
import graph_types.Directed_WeightedGWU as dwgwu
import graph_types.Undirected_WeightedGWU as uwgwu
import graph_types.Directed_UnweightedGWU as dugwu
import graph_types.Undirected_UnweightedGWU as uugwu 

""" 
contains one main function :

*grow_network : takes a tree of decision and returns the graph that grows according to those rules
    Tree : consider an edge, returns a real number
        max depth : 3. 
        each leaf can be one of :
        "OrigId"  "TargId" "OrigInDegree" "OrigOutDegree"  "TargInDegree"  "TargOutDegree" 
        "OrigInStrength" "OrigOutStrength"  "TargInStrength"  "TargOutStrength" 
        "DirectDistance" "ReversedDistance"
        each node can be one of : + - * / exp log abs min max opp inv
    
    Growth algorithm :
        begins with an empty graph with the number of nodes  of the real network
        at each step the tree gives a probability to every possible edge
        one edge is chosen randomly
        until the number of edges equals the number of edges of the real network
        
    

"""

def grow_network(decision_tree):
    '''takes a tree of decision and returns the graph that grows according to those rules'''
    ''' graph has directed edges'''
    '''depending on the method used, this graph can have weighted or unweighted edges'''
    
    tree_type = decision_tree.getParam("tree_type")
    number_of_nodes = int(decision_tree.getParam("nb_nodes"))
    number_of_edges = int(decision_tree.getParam("nb_edges"))
    network_type = decision_tree.getParam("network_type")
    
    graph = createGraph(network_type)
    if tree_type == "simple" :
        return grow_simple_network(graph,decision_tree,number_of_nodes, number_of_edges)
    if tree_type == "with_constants" :
        return grow_network_with_constants(graph,decision_tree,number_of_nodes, number_of_edges)
            
    raise Exception("no tree_type given")    

 
'''
Functions that grow a network according to the method of evaluation used
'''       
def createGraph(network_type) :
    if network_type =="directed_weighted" :
        return dwgwu.Directed_WeightedGWU()
    if network_type == "undirected_weighted" :
        return uwgwu.Undirected_WeightedGWU()
    if network_type =="directed_unweighted" :
        return dugwu.Directed_UnweightedGWU()
    if network_type == "undirected_unweighted" :
        return uugwu.Undirected_UnweightedGWU()
    raise Exception("network_type not given")
    
def grow_simple_network(graph,decision_tree,number_of_nodes, number_of_edges):
    '''takes a tree of decision and returns the graph that grows according to those rules'''
    '''graph can be (un)directed/(un)weighted'''

    #begins with an empty graph with the number of nodes  of the real network
    for i in xrange(number_of_nodes) :
        graph.add_node(i)
    #adds one edge according to its probability
    for i in xrange(number_of_edges) :
        #each edge has a probability that is the result of the tree
        probas = calc(decision_tree.getRoot(),graph)
        #we remove unnecessary edges : self loops, negative proba
        #we choose one among remaining ones
        edge,_ = choose_edge(probas, graph)
        if edge is None : #this can happen if every edge has a -infinity probability thanks to log or / or - exp...
            break
        graph.add_edge(*edge)
        
    return graph
    
#@profile
def grow_network_with_constants(graph,decision_tree,number_of_nodes, number_of_edges):
    '''takes a tree of decision and returns the graph that grows according to those rules'''
    '''graph can be (un)directed/(un)weighted'''
    #begins with an empty graph with the number of nodes  of the real network
    for i in xrange(number_of_nodes) :
        graph.add_node(i)
    #adds one edge according to its probability
    for i in xrange(number_of_edges) :
        #each edge has a probability that is the result of the tree
        probas = calc_with_constants(decision_tree.getRoot(),graph)
        #we remove unnecessary edges : self loops, negative proba
        #we choose one among remaining ones
        
        edge,weight_value = choose_edge(probas, graph)
        
        if edge is None : #this can happen if every edge has a -infinity probability thanks to log or / or - exp...
            break
        if graph.isWeighted() :
            graph.add_edge(*edge,weight=weight_value)
        else :
            graph.add_edge(*edge)
            
    return graph

'''
Functions that let us choose a random element in the matrix of probabilities
'''


    
def choose_edge(probas,network):
    ''' takes a matrix of probabilities and a network, 
    returns an edge (no self loop, not already present in the network) according to probabilities and its weight for the network'''
    '''the returned weight is (1+erf(proba)) /2 : because this function takes a number in R and return a number between 0 and 1'''
    #we mark impossible edge, because it faster to remove them this way instead of filtering the matrix enumerated
    # finding edges in matrices is in constant time 
    #finding edges in sequences is in linear time
    
    #gives -infinity as probability to self loops
    np.fill_diagonal(probas, float('-inf'))
    #gives -infinity as probability to already existing edges
    if network.isDirected() :
        for edge in network.edges_iter() :
            probas[edge] = float('-inf')
    else :
        'because edges are only stored once : begin-end and not end-begin'
        for target,origin in network.edges_iter() :
            probas[origin,target] = float('-inf')
            probas[target,origin] = float('-inf')
    
    #probas can contain a number + infinity, -inifinity, nan
    liste_probas = np.ndenumerate(probas)
    
    #we list possible edge : no self loops, no existing edges, no negative probabilities
    possible_edges = filter(lambda x : x[1] > float('-inf'), liste_probas)    
    #if there is no possible edge, we stop the building of the network 
    if len(possible_edges) == 0 :
        return (None,0)
    
    
    #we list edges with strictly positive probabilities
    positive_edges = filter(lambda x : x[1] > 0, possible_edges)    
    #if every probability is negative, we choose one edge among the possible 
    if len(positive_edges) == 0 :
        edge,weight = random.choice(possible_edges)
        return (edge, normalize(weight))
    
    
    #we list edges with infinite probabilities
    infinite_edges = filter(lambda x : x[1] == float('+inf'), positive_edges)  
    #if some probability are infinite, we choose one edge among the inifinite probabilities
    if len(infinite_edges) != 0 :
        weighted_edge = random.choice(infinite_edges)
        return (weighted_edge[0],1)
       
    
    #if there is one positive probability, we choose one edge between those with positive probability
    weights_sum = sum(weighted_edge[1] for weighted_edge in positive_edges)
    rand = random.random() * weights_sum
    for edge,weight in positive_edges :
            rand-=weight
            if  rand <= 0 :
                return (edge,normalize(weight))
    #if weights_sum = +infty but probabilities are different from + infinity,
    #we can have this possibility
    return random.choice(possible_edges) 
            
      
   


'''
Functions that compute the tree for each node
'''

def calc(node, graph): 
    ''' takes a node of the decision tree and a graph
    computes recursively a value for each edge of the graph at the same time
    a node can be a leaf with a variable or a function
    returns a 2D array containing the value for each edge
    '''
    
    data = node.getData()
    
    #recursive computation on function nodes : we always have 2 children if not a leaf, by construction
    if node.isLeaf() :
        return compute_leaf(graph,data)
        
    else :  
        #values returned are arrays of dimension 2
        value0 = calc(node.getChild(0), graph)
        value1 = calc(node.getChild(1), graph)
        return compute_function(data,value0,value1)
        
def calc_with_constants(node, graph): 
    ''' takes a node of the decision tree and a graph
    computes recursively a value for each edge of the graph at the same time
    returns a 2D array containing the value for each edge
    difference is that leaves of the tree contain a constant and a variable
    '''
    
    data = node.getData()
    #recursive computation on function nodes : we always have 2 children if not a leaf, by construction
    if node.isLeaf() :
        constant, variable = data
        return constant*(compute_leaf(graph,variable))
        
    else :
        
        #values returned are arrays of dimension 2
        value0 = calc_with_constants(node.getChild(0), graph)
        value1 = calc_with_constants(node.getChild(1), graph)
        return compute_function(data,value0,value1)

def compute_function(data,value0,value1) :
    '''returns the computation of value0 data value1 
    data is an operation between two numbers
    '''
    return  {
                       "+" : op.add,
                       "-" : op.sub,
                       "*" : op.mul,
                       "min" : np.minimum,
                       "max" : np.maximum,
                       "exp" : exp,
                       "log" : log,
                       "abs" : np.absolute,
                         "/" : div,
                         "inv" : inv,
                         "opp" : opp
                       }[data](value0,value1)  
                             
def compute_leaf(graph,variable) :
    '''returns the computation of value0 data value1 
    data is an operation between two numbers
    '''
    return {
                       #local variables
                       "OrigId" : graph.OrigId,
                       "TargId" : graph.TargId,
                       "OrigInDegree" : graph.OrigInDegree,
                       "OrigOutDegree" : graph.OrigOutDegree,
                       "TargInDegree" : graph.TargInDegree,
                       "TargOutDegree" : graph.TargOutDegree,
                       "OrigInStrength" : graph.OrigInStrength,
                       "OrigOutStrength" : graph.OrigOutStrength,
                       "TargInStrength" : graph.TargInStrength,
                       "TargOutStrength" : graph.TargOutStrength,
                       "DirectDistance" : graph.DirectDistance,
                       "ReversedDistance" : graph.ReversedDistance,
                       
                       #undirected local variables
                       "OrigDegree" : graph.OrigDegree,
                       "TargDegree" : graph.TargDegree,
                       "OrigStrength" : graph.OrigStrength,
                       "TargStrength" : graph.TargStrength,
                       "Distance" : graph.Distance,
                       
                       #global variables
                       "NumberOfNodes" : graph.NumberOfNodes,
                       "NumberOfEdges" : graph.NumberOfEdges,
                       "MaxInDegree" : graph.MaxInDegree,
                       "MaxOutDegree" : graph.MaxOutDegree,
                       "MaxInStrength" : graph.MaxInStrength,
                       "MaxOutStrength" : graph.MaxOutStrength,
                       "MaxWeight" : graph.MaxWeight,
                       "MaxDistance" : graph.MaxDistance,
                       "TotalDistance" : graph.TotalDistance,
                       "TotalWeight" : graph.TotalWeight,
                       "Constant" : graph.Constant,
                       "Random" : graph.Random,
                       
                       #undirected global variables
                       "MaxDegree" : graph.MaxDegree,
                       "MaxStrength" : graph.MaxStrength,
                       
                       #normalized local variables
                       "NormalizedOrigId" : graph.NormalizedOrigId,
                       "NormalizedTargId" : graph.NormalizedTargId,
                       "NormalizedOrigInDegree" : graph.NormalizedOrigInDegree,
                       "NormalizedOrigOutDegree" : graph.NormalizedOrigOutDegree,
                       "NormalizedTargInDegree" : graph.NormalizedTargInDegree,
                       "NormalizedTargOutDegree" : graph.NormalizedTargOutDegree,
                       "NormalizedOrigInStrength" : graph.NormalizedOrigInStrength,
                       "NormalizedOrigOutStrength" : graph.NormalizedOrigOutStrength,
                       "NormalizedTargInStrength" : graph.NormalizedTargInStrength,
                       "NormalizedTargOutStrength" : graph.NormalizedTargOutStrength,
                       "NormalizedDirectDistance" : graph.NormalizedDirectDistance,
                       "NormalizedReversedDistance" : graph.NormalizedReversedDistance,
                       
                       #undirected normalized local variables
                       "NormalizedOrigDegree" : graph.NormalizedOrigDegree,
                       "NormalizedTargDegree" : graph.NormalizedTargDegree,
                       "NormalizedOrigStrength" : graph.NormalizedOrigStrength,
                       "NormalizedTargStrength" : graph.NormalizedTargStrength,
                       "NormalizedDistance" : graph.NormalizedDistance,
                       
                       #averaged global variables
                       "AverageInDegree" : graph.AverageInDegree,
                       "AverageOutDegree" : graph.AverageOutDegree,
                       "AverageInStrength" : graph.AverageInStrength,
                       "AverageOutStrength" : graph.AverageOutStrength,
                       "AverageWeight" : graph.AverageWeight,
                       "AverageDistance" : graph.AverageDistance,
                       
                       #undirected averaged global variables
                       "AverageDegree" : graph.AverageDegree,
                       "AverageStrength" : graph.AverageStrength,
                       
                       
                       }[variable]()
                          
def div(a,b):
    'divides by 1+b to avoid dividing by 0 in most cases'
    return a/(1+b)  
      
def exp(a,b) :
    return np.exp(a)

def log(a,b) :
    'computes log(1+a) to avoid most cases where a = 0'
    return np.log(1+a)

def inv(a,b):
    return np.power(a,-1)

def opp(a,b):
    return -a

def normalize(x) :
    return (math.tanh(x)+1)/2

    
    



