'''
Created on 15 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
''' 
import networkx as nx
import random
import numpy  as np
import itertools as it

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


def choose_edge3(probas,network):
    '''deprecated because choose_edge is more efficienta at doing the same job
    takes a matrix of probabilities and a network, 
    returns an edge (no self loop, not already present in the network) according to probabilities '''
    
    #gives -infinity as probability to self loops
    np.fill_diagonal(probas, float('-inf'))
    #gives -infinity as probability to already existing edges
    for edge in network.edges_iter() :
        probas[edge] =float('-inf')
    
    # we count the sum of strict positive probabilities  in case where we have some positive proba
    weights_sum = 0 
    #we count the number of possible edges in case every probability is negative or 0
    count_numbers  = 0
    #use a loop to count
    for weight in  probas.flat :
        if weight > float('-inf') : 
            count_numbers+=1
            if weight > 0 : 
                weights_sum += weight
            
    #if every probability is negative, we choose one edge among the possible (impossible have been marked by -inifinity)    
    if weights_sum == 0 :
        #we assume that there is at least one possible edge
        #count_numbers is excluded    
        rand = np.random.randint(0,count_numbers)
        for edge,weight in np.ndenumerate(probas) :
            if weight > float('-inf') :
                if  rand == 0 :
                    return edge
                rand-=1
    #idf there is one positive probability, we choose one edge between those with positive probability
    else :
        rand = random.random() * weights_sum
        for edge,weight in np.ndenumerate(probas) :
            if weight > 0 :
                rand-=weight
                if  rand <= 0 :
                    return edge
      

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
    

  


    
    
          






