'''
Created on 15 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
''' 
import networkx as nx
import random
import numpy  as np
import operator as op
""" 
contains one main function :

*grow_network : takes a tree of decision and returns the graph that grows according to those rules
    Tree : consider an edge, returns a real number
        max depth : 3. 
        each leaf can be one of :
        "OrigId"  "TargId" "OrigInDegree" "OrigOutDegree"  "TargInDegree"  "TargOutDegree" 
        "OrigInStrength" "OrigOutStrength"  "TargInStrength"  "TargOutStrength" 
        "DirectDistance" "ReversedDistance"
        each node can be one of : + - * / exp log abs min max
    
    Growth algorithm :
        begins with an empty graph with the number of nodes  of the real network
        at each step the tree gives a probability to every possible edge
        one edge is chosen randomly
        until the number of edges equals the number of edges of the real network
        
    

"""
def grow_network(decision_tree,number_of_nodes, number_of_edges,**kwargs):
    '''takes a tree of decision and returns the graph that grows according to those rules'''
    ''' graph has directed edges'''
    '''depending on teh method use, this graph can have weighted or unweighted edges'''
    
    evaluation_method = kwargs.get("evaluation_method")
    if evaluation_method == "degree_distribution" :
        return grow_simple_network(decision_tree,number_of_nodes, number_of_edges)
    if evaluation_method == "weighted" :
        return grow_weighted_network(decision_tree,number_of_nodes, number_of_edges)
 
'''
Functions that grow a network according to the method of evaluation used
''' 
    
def grow_weighted_network(decision_tree,number_of_nodes, number_of_edges):
    '''takes a tree of decision and returns the graph that grows according to those rules'''
    ''' graph has weighted and directed edges'''
    graph = nx.DiGraph()
    #begins with an empty graph with the number of nodes  of the real network
    for i in xrange(number_of_nodes) :
        graph.add_node(i)
    #adds one edge according to its probability
    for i in xrange(number_of_edges) :
        #each edge has a probability that is the result of the tree
        probas = calc(decision_tree.getRoot(),graph)
        #we remove unnecessary edges : self loops, negative proba
        #we choose one among remaining ones
        edge,weight = choose_edge_with_weight(probas, graph)
        if edge is None : #this can happen if every edge has a -infinity probability thanks to log or / or - exp...
            break
        graph.add_edge(*edge,weight=weight)
        
    return graph 
    
def grow_simple_network(decision_tree,number_of_nodes, number_of_edges):
    '''takes a tree of decision and returns the graph that grows according to those rules'''
    '''graph is directed but unweighted'''
    #directed graph
    graph = nx.DiGraph() 
    #begins with an empty graph with the number of nodes  of the real network
    for i in xrange(number_of_nodes) :
        graph.add_node(i)
    #adds one edge according to its probability
    for i in xrange(number_of_edges) :
        #each edge has a probability that is the result of the tree
        probas = calc(decision_tree.getRoot(),graph)
        #we remove unnecessary edges : self loops, negative proba
        #we choose one among remaining ones
        edge = choose_edge(probas, graph)
        
        graph.add_edge(*edge)
        
    return graph


'''
Functions that let us choose a random element in the matrix of probabilities
'''

def choose_edge(probas,network):
    ''' takes a matrix of probabilities and a network, 
    returns an edge (no self loop, not already present in the network) according to probabilities '''
    #we mark impossible edge, because it faster to remove them this way instead of filtering the matrix enumerated
    # finding edges in matrices is in constant time 
    #finding edges in sequences is in linear time
    
    #gives -infinity as probability to self loops
    np.fill_diagonal(probas, float('-inf'))
    #gives -infinity as probability to already existing edges
    for edge in network.edges_iter() :
        probas[edge] = float('-inf')
    
    
    liste_probas = np.ndenumerate(probas)
    #we list possible edge : no self loops, no existing edges
    possible_edges = filter(lambda x : x[1] > float('-inf'), liste_probas)
    #we list edges with strictly positive probabilities
    positive_edges = filter(lambda x : x[1] > 0, possible_edges)
    
    

    weights_sum = sum(weighted_edge[1] for weighted_edge in positive_edges)
   
            
    #if every probability is negative, we choose one edge among the possible     
    if weights_sum == 0 :
        return random.choice([weighted_edge[0] for weighted_edge in possible_edges])
    #if there is one positive probability, we choose one edge between those with positive probability
    else :
        rand = random.random() * weights_sum
        for edge,weight in positive_edges :
                rand-=weight
                if  rand <= 0 :
                    return edge

def choose_edge_with_weight(probas,network):
    ''' takes a matrix of probabilities and a network, 
    returns an edge (no self loop, not already present in the network) according to probabilities and its weight for the network'''
    '''the returned weight is (1+tanh(proba)) /2 : because this function takes a number in R and return a number between 0 and 1'''
    #we mark impossible edge, because it faster to remove them this way instead of filtering the matrix enumerated
    # finding edges in matrices is in constant time 
    #finding edges in sequences is in linear time
    
    #gives -infinity as probability to self loops
    np.fill_diagonal(probas, float('-inf'))
    #gives -infinity as probability to already existing edges
    for edge in network.edges_iter() :
        probas[edge] = float('-inf')
    
    #probas can contain a number + infinity, -inifinity, nan
    liste_probas = np.ndenumerate(probas)
    #we list possible edge : no self loops, no existing edges, no negative probabilities
    possible_edges = filter(lambda x : x[1] > float('-inf'), liste_probas)
    #we list edges with strictly positive probabilities
    positive_edges = filter(lambda x : x[1] > 0, possible_edges)
    #we list edges with infinite probabilities
    infinite_edges = filter(lambda x : x[1] == float('+inf'), positive_edges)
    
    weights_sum = sum(weighted_edge[1] for weighted_edge in positive_edges)
    
    #if there is no possible edge, we stop the building of the network 
    if len(possible_edges) == 0 :
        return (None,0)
    
    #if some probability are infinite, we choose one edge among the inifinite probabilities
    if len(infinite_edges) != 0 :
        edge = random.choice([weighted_edge[0] for weighted_edge in infinite_edges])
        return (edge,1)
    
    #if every probability is negative, we choose one edge among the possible 
    if len(positive_edges) == 0 :
        edge = random.choice([weighted_edge[0] for weighted_edge in possible_edges])
        return (edge, 0.5)
    
    #if there is one positive probability, we choose one edge between those with positive probability
    rand = random.random() * weights_sum
    for edge,weight in positive_edges :
            rand-=weight
            if  rand <= 0 :
                return (edge,1+np.tanh(weight)/2)

'''
Functions that compute the tree for each node
'''

def calc(node, graph): 
    ''' takes a node of the decision tree and a graph
    computes recursively a value for each edge of the graph at the same time
    returns a 2D array containing the value for each edge
    '''
    
    data = node.getData()
    #we have 12 posible leaves
    possible_leaves = {
                       "OrigId" : OrigId,
                       "TargId" : TargId,
                       "RelativeOrigId" : RelativeOrigId,
                       "RelativeTargId" : RelativeTargId,
                       "OrigInDegree" : OrigInDegree,
                       "OrigOutDegree" : OrigOutDegree,
                       "TargInDegree" : TargInDegree,
                       "TargOutDegree" : TargOutDegree,
                       "OrigInStrength" : OrigInStrength,
                       "OrigOutStrength" : OrigOutStrength,
                       "TargInStrength" : TargInStrength,
                       "TargOutStrength" : TargOutStrength,
                       "DirectDistance" : DirectDistance,
                       "ReversedDistance" : ReversedDistance
                       }
    
    possible_functions = {
                       "+" : op.add,
                       "-" : op.sub,
                       "*" : op.mul,
                       "min" : np.minimum,
                       "max" : np.maximum,
                       "exp" : exp,
                       "log" : log,
                       "abs" : np.absolute,
                       "/" : op.div
                       }
    
    if node.isLeaf() :
        return possible_leaves[data](graph)
        
    else :
        #recursive computation on function nodes : 3 possibilities, we always have 2 children, by construction
        value0 = calc(node.getChild(0), graph)
        value1 = calc(node.getChild(1), graph)
        return possible_functions[data](value0,value1)
        
def OrigInDegree(graph) : 
    ''' returns a 2d array containing the in degree of the origin node for all edges
    '''
    probas = np.dot( 
                  np.transpose(np.array(list(graph.in_degree().values()))[np.newaxis,:]),
                  np.ones((1,graph.number_of_nodes())))
    return probas

def OrigInStrength(graph) : 
    ''' returns a 2d array containing the in degree of the origin node for all edges
    '''
    probas = np.dot( 
                  np.transpose(np.array(list(graph.in_degree(weight="weight").values()))[np.newaxis,:]),
                  np.ones((1,graph.number_of_nodes())))
    return probas

def OrigOutDegree(graph) :
    ''' returns a 2d array containing the out degree of the origin node for all edges
    '''
    probas = np.dot( 
                  np.transpose(np.array(list(graph.out_degree().values()))[np.newaxis,:]),
                  np.ones((1,graph.number_of_nodes())))
    return probas

def OrigOutStrength(graph) :
    ''' returns a 2d array containing the out degree of the origin node for all edges
    '''
    probas = np.dot( 
                  np.transpose(np.array(list(graph.out_degree(weight="weight").values()))[np.newaxis,:]),
                  np.ones((1,graph.number_of_nodes())))
    return probas

def OrigId(graph) :
    ''' returns a 2d array containing the identity number (0 to n=number of nodes) of the origin node for all edges
    ''' 
    probas = np.dot( 
                  np.transpose(np.array(range(graph.number_of_nodes()))[np.newaxis,:]),
                  np.ones((1,graph.number_of_nodes())))
    return probas

def RelativeOrigId(graph) :
    ''' returns a 2d array containing the identity number (0 to n=number of nodes) of the origin node divided by the number of nodes for all edges
    ''' 
    
    probas = np.dot( 
                  np.transpose(np.linspace(0.0, 1.0, num=graph.number_of_nodes())[np.newaxis,:]),
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

def TargInStrength(graph) : 
    ''' returns a 2d array containing the in degree of the target node for all edges
    ''' 
    probas =  np.dot( 
                  np.ones((graph.number_of_nodes(),1)),
                  np.array(list(graph.in_degree(weight="weight").values()), ndmin=2,dtype=float)
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

def TargOutStrength(graph) :
    ''' returns a 2d array containing the out degree of the target node for all edges
    ''' 
    probas =  np.dot( 
                  np.ones((graph.number_of_nodes(),1)),
                  np.array(list(graph.out_degree(weight="weight").values()), ndmin=2,dtype=float)
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

def RelativeTargId(graph) : 
    ''' returns a 2d array containing the identity number of the target node / number of nodes for all edges
    ''' 
    
    probas =  np.dot( 
                  np.ones((graph.number_of_nodes(),1)),
                  np.linspace(0.0, 1.0, num=graph.number_of_nodes())[np.newaxis,:]
                  )  
          
    return probas
 
def DirectDistance(graph) :
    ''' returns a 2d array containing the direct distance = shortest path length, takes weights into account, takes direction of edges into account'''
    ''' gives +infinity if no path'''
    
    shortest_path_dict = nx.shortest_path_length(graph,weight="weight")
    probas = np.empty((graph.number_of_nodes(), graph.number_of_nodes()))
    #every path that does not exist has distance +infinity
    probas.fill(float('+inf'))
    
    for node1, row in shortest_path_dict.iteritems():
        for node2, length in row.iteritems():
            probas[node1, node2] = length 
    return probas

def ReversedDistance(graph) :
    ''' returns a 2d array containing the reversed distance = reversed shortest path length, takes weights into account, takes direction of edges into account'''
    ''' gives +infinity if no path'''
    
    shortest_path_dict = nx.shortest_path_length(graph,weight="weight")
    #every path that does not exist has distance +infinity
    probas = np.empty((graph.number_of_nodes(), graph.number_of_nodes()))
    probas.fill(float('+inf'))
    
    for node1, row in shortest_path_dict.iteritems():
        for node2, length in row.iteritems():
    #This line is the difference with direct distance function:  direct shortest path length from key1 to key2 = reversed sortest path length from key2 to key1        
            probas[node2, node1] = length 
    return probas
    
def exp(a,b) :
    return np.exp(a)

def log(a,b) :
    return np.log(a)



    
    



