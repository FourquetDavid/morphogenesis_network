'''
Created on 15 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
'''
import numpy as np 
import networkx as nx
import itertools as it
""" 
contains two main function :

*get_datas_from_real_network : takes a relative path to network-type file and store relevant infos for future studies
*eval_network : takes a network and returns a number that cracterizes 
                the proximity between the network and the real network already registered
                
                methods of evaluation implemented : degree_distribution
"""

        
def get_datas_from_real_network (data_path,results_path,**kwargs):
    '''takes a relative path to network-type file and store relevant infos for future studies
    '''
    
    #the function used to read the network is dependant on the type of network used
    graph = read_typed_file(data_path)
    
    f = open(results_path, 'w')
    
    #First relevant infos are number of nodes and number of edges, 
    #should be dependant on the method used to develop the network, 
    #but until now they are necessary and always stored
    f.write(str(nx.number_of_nodes(graph)))
    f.write("\n")
    f.write(str(nx.number_of_edges(graph)))
    f.write("\n")
    #Other infos depend on the evaluation method used
    result = get_evaluation_datas(graph,evaluation_method=kwargs.get("evaluation_method"),network_type = kwargs["network_type"])

    f.write(result)
    
    f.close()

def eval_network(network,results_path,**kwargs):
    '''takes a network and returns a number that caracterizes 
    the proximity between the network and the real network already registered in results_path'''
    # default evaluation method is node distribution
    eval_method = kwargs.get("evaluation_method")
    network_type = kwargs["network_type"]
    if eval_method == "degree_distribution" :
        if network_type == "wundirected_weighted"  or network_type == "undirected_unweighted" :
            return eval_degree_distribution(network,results_path)
    
    
    if eval_method == "2distributions" :
        if network_type == "directed_weighted"  or network_type == "directed_unweighted" :
            return eval_2distributions_directed(network,results_path)
        if network_type == "undirected_weighted"  or network_type == "undirected_unweighted" :
            return eval_2distributions_undirected(network,results_path)
    raise Exception("no evaluation_method or network_type given")
  
    """ 
    Function that help evaluating network
    """ 
         


def eval_degree_distribution(network,results_path):
    '''  the bigger the result is, the worse the network is '''
    #build the alist describing the distribution of degrees of the evaluated network
    hist_test = nx.degree_histogram(network)
    
    #build the list describing the distribution of degrees of the real network
    #item k is the number of nodes of degree k
    f = open(results_path, 'r')
    lines = f.readlines()
    hist_goal = eval(lines[2])
    #this function compares list and return the difference in 
    result = compare(hist_test,hist_goal )
    f.close() 
    return result

def eval_2distributions_directed(network,results_path):
    '''  the bigger the result is, the worse the network is '''
    #build the alist describing the distribution of degrees of the evaluated network
    hist_test_indegree = get_histogram(network.in_degree().values())
    hist_test_outdegree = get_histogram(network.out_degree().values())
    #this line converts dict of dict of lengths to list of lists, chain them, then get an histogram 
    hist_test_distances = get_histogram(list(it.chain.from_iterable([ dict_of_length.values() for dict_of_length in nx.shortest_path_length(network).values()])))
    
    #build the list describing the distribution of indegrees, outdegrees and distances of the real network
    #item k is the number of nodes of degree k
    f = open(results_path, 'r')
    lines = f.readlines()
    hist_goal_indegree = eval(lines[2])
    hist_goal_outdegree = eval(lines[3])
    hist_goal_distances = eval(lines[4])
    
    #this function compares list and return the difference in 
    result = compare(hist_test_indegree,hist_goal_indegree ) + compare(hist_test_outdegree,hist_goal_outdegree ) + compare(hist_test_distances,hist_goal_distances ) 
    f.close() 
    return result

def eval_2distributions_undirected(network,results_path):
    '''  the bigger the result is, the worse the network is '''
    #build the alist describing the distribution of degrees of the evaluated network
    hist_test_degree = get_histogram(network.degree().values())
    #this line converts dict of dict of lengths to list of lists, chain them, then get an histogram 
    hist_test_distances = get_histogram(list(it.chain.from_iterable([ dict_of_length.values() for dict_of_length in nx.shortest_path_length(network).values()])))
    
    #build the list describing the distribution of indegrees, outdegrees and distances of the real network
    #item k is the number of nodes of degree k
    f = open(results_path, 'r')
    lines = f.readlines()
    hist_goal_degree = eval(lines[2])
    hist_goal_distances = eval(lines[3])
    
    #this function compares list and return the difference in 
    result = compare(hist_test_degree,hist_goal_degree ) + compare(hist_test_distances,hist_goal_distances ) 
    f.close() 
    return result
                  
def compare(list1, list2):
    '''compares 2 arrays by appending with zeros the little one
    gives the sum of absolute differences between corresponding items of both arrays'''
   
    list1.extend(it.repeat(0,len(list2)-len(list1)))
    list2.extend(it.repeat(0,len(list1)-len(list2)))
    
    array1 = np.array(list1)
    array2 = np.array(list2)
    return sum(abs(array1-array2))
    
    
    
    """ 
    Function that help reading file and storing datas
    """ 
    
def read_typed_file(path) :
    #3 types of network can be read
    if path.find(".gml") :
        return nx.read_gml(path)
    if path.find(".gexf") :
        return nx.read_gexf(path)
    if path.find(".net") :
        return nx.read_pajek(path)
    raise Exception("network_format not recognized")

def get_evaluation_datas(graph, **kwargs) :
    #cast to string relevant infos for the evaluation of networks
    # default_method is node_distribution
    evaluation_method = kwargs.get("evaluation_method") 
    network_type = kwargs.get("network_type")
    if evaluation_method == "degree_distribution" :
        if network_type == "undirected_weighted"  or network_type == "undirected_unweighted" :
            return datas_degree_distribution(graph)
        
    if evaluation_method == "2distributions" :
        if network_type == "directed_weighted"  or network_type == "directed_unweighted" :
            return datas_2distributions_directed(graph)
        if network_type == "undirected_weighted"  or network_type == "undirected_unweighted" :
            return datas_2distributions_undirected(graph)
    raise Exception("no evaluation_method or network_type given")

def datas_degree_distribution(graph) :
    result = str(get_histogram(graph.degree().values())) 
   
    return result

def datas_2distributions_directed(graph) :
    #results are not weight-dependant because we have no weight on real edges
    indegree = get_histogram(graph.in_degree().values())
    outdegree = get_histogram(graph.out_degree().values())
    #this line converts dict of dict of lengths to list of lists, chain them, then get an histogram 
    shortest_path = get_histogram(list(it.chain.from_iterable([ dict_of_length.values() for dict_of_length in nx.shortest_path_length(graph).values()])))
    return '\n'.join([str(indegree),str(outdegree),str(shortest_path)])

def datas_2distributions_undirected(graph) :
    #results are not weight-dependant because we have no weight on real edges
    indegree = get_histogram(graph.degree().values())
    #this line converts dict of dict of lengths to list of lists, chain them, then get an histogram 
    shortest_path = get_histogram(list(it.chain.from_iterable([ dict_of_length.values() for dict_of_length in nx.shortest_path_length(graph).values()])))
    return '\n'.join([str(indegree),str(shortest_path)])
    
def get_number_of_nodes(results_path):    
    f = open(results_path, 'r')
    lines = f.readlines()
    nb_nodes = int(lines[0])
    f.close()
    return nb_nodes

def get_number_of_edges(results_path):
    f = open(results_path, 'r')
    lines = f.readlines()
    nb_edges = int(lines[1])
    f.close()
    return nb_edges

def get_histogram(degseq):
    '''takes a sequence of integer values and returns the distribution of values'''    
    dmax=max(degseq)+1
    freq= [ 0 for d in range(dmax) ]
    for d in degseq:
        freq[d] += 1
    return freq
