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
    f.write(str(nx.number_of_nodes(graph))+"\n")
    f.write(str(nx.number_of_edges(graph))+"\n")
    
    #Other infos depend on the evaluation method used
    result = get_evaluation_datas(graph,method=kwargs.get("evaluation_method","default"))

    f.write(result.__repr__())
    
    f.close()

def eval_network(network,results_path,**kwargs):
    '''takes a network and returns a number that caracterizes 
    the proximity between the network and the real network already registered in results_path'''
    # default evaluation method is node distribution
    eval_method = kwargs.get("evaluation_method","default_eval")
    if eval_method == eval_degree_distribution :
        return eval_degree_distribution(network,results_path)
    return default_eval(network,results_path)
    
  
  
    """ 
    Function that help evaluating network
    """ 
         
def default_eval(network,results_path): 
    return eval_degree_distribution(network,results_path)

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
                  
def compare(list1, list2):
    #compare 2 arrays by appending with zeros the little one
    #gives the sum of absolute differences between corresponding items of both arrays
   
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
    method = kwargs.get("method","default_method") 
    if method == "degree_distribution" :
        return degree_distribution(graph)
    return default_method(graph)

def degree_distribution(graph) :
    result = nx.degree_histogram(graph)
    return result

def default_method(graph) :
    print "default evaluation (degree distribution) method has been used"
    return degree_distribution(graph)
    
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
