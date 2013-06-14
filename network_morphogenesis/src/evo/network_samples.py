'''
Created on 13 dec. 2012

@author: davidfourquet
'''
# some_file.py

import network_evaluation as ne  
import network_development as nd
import genetic_algorithm as ga  
import pyevolve as py
import numpy as np
import networkx as nx
import evaluation_method_options as emo
import statistics as st
import matplotlib.pyplot as plt

'''
This module tests the stability of our algorithm
We produce networks thanks to knwown algorithms and our rules and we try to find the rules with our algorithm.
'''
#allele_gen ="MaxDistance"
data_path = '../../results/temp/working_network.gml'
evaluation_method ="communities_degrees_distances_clustering_importance"
tree_type = "with_constants"
network_type = "undirected_unweighted"
number_of_tries = 1
number_of_nodes = 50
number_of_edges = 150
nb_generations =11
freq_stats =5



    
def main() :
    global number_of_tries
    global number_of_nodes
    global number_of_edges
    global allele_gen
    
    #list_of_rules = createListOfRules()
    #[py.GTree.GTreeNode([5,allele_gen])]
    #createListofRules()
    list_of_rules = [py.GTree.GTreeNode([5,'OrigDegree'])]
    
    for rule in list_of_rules :
        
        print "##########new rule############"
        print rule
        rule_name = rule.getData()[1]
        rule_found_list = []
        for number in range(number_of_tries) :
            develop_network(rule,number)
            rule_found = get_rule(rule_name)
            rule_found_list.append(rule_found)
        printResults(rule, rule_found_list)


def createListOfRules():
    choices = emo.get_alleles(evaluation_method,network_type)[1]
    list_of_rules = []
    for allele in choices :
        list_of_rules.append(py.GTree.GTreeNode([5,allele]))
    return list_of_rules
    

def develop_network(rule,number):
    graph = nd.createGraph(network_type)
    variable = rule.getData()[1]
    global data_path
    network = nd.grow_network_with_constants(graph,py.GTree.GTree(rule),number_of_nodes, number_of_edges)  
    nx.write_gml(network, data_path)
    nx.draw(network)
    plt.savefig("../../results/temp/drawings/{}_{}.png".format(variable,number))
    plt.close()
    
def printResults(rule, rule_found_list) : 
    global_stats_path = '../../results/temp/stats_{}.txt'.format(rule.getData()[1])
    print "################rule studied###############"
    print rule
    print "####################rules found#####################"
    for rule_found in rule_found_list :
        print rule_found.getTraversalString()
        print rule_found.getRawScore()
    
    file_stats = open(global_stats_path,'a')
    file_stats.write("################rule studied###############\n")
    file_stats.write(str(rule))
    file_stats.write("####################rules found#####################\n")
    for rule_found in rule_found_list :
        file_stats.write(rule_found.getTraversalString())
        file_stats.write(str(rule_found.getRawScore())+"\n")
    file_stats.close()
'''   
def grow_undirected_weighted_network_with_constants(graph,node,number_of_nodes, number_of_edges):
    takes a tree of decision and returns the graph that grows according to those rules
     graph has weighted and directed edges
    #begins with an empty graph with the number of nodes  of the real network
    for i in xrange(number_of_nodes) :
        graph.add_node(i)
    #adds one edge according to its probability
    for i in xrange(number_of_edges) :
        #each edge has a probability that is the result of the tree
        probas = nd.calc_with_constants(node,graph)
        #we remove unnecessary edges : self loops, negative proba
        #we choose one among remaining ones
        
        edge,weight_value = nd.choose_undirected_edge_with_weight(probas, graph)
        
        if edge is None : #this can happen if every edge has a -infinity probability thanks to log or / or - exp...
            break
        graph.add_edge(*edge,weight=weight_value)
        
    return graph

def grow_directed_weighted_network_with_constants(graph,node,number_of_nodes, number_of_edges):
    takes a tree of decision and returns the graph that grows according to those rules
     graph has weighted and directed edges
    #begins with an empty graph with the number of nodes  of the real network
    for i in xrange(number_of_nodes) :
        graph.add_node(i)
    #adds one edge according to its probability
    for i in xrange(number_of_edges) :
        #each edge has a probability that is the result of the tree
        probas = nd.calc_with_constants(node,graph)
        #we remove unnecessary edges : self loops, negative proba
        #we choose one among remaining ones
        
        edge,weight_value = nd.choose_directed_edge_with_weight(probas, graph)
        
        if edge is None : #this can happen if every edge has a -infinity probability thanks to log or / or - exp...
            break
        graph.add_edge(*edge,weight=weight_value)
        
    return graph
 ''' 
    
def get_rule(rule_name):
    global evaluation_method
    global tree_type
    global network_type
    global data_path
    global nb_generations
    
    
    multiprocessing = False
    
    results_path ='../../results/temp/working_results.txt'
    
    #do not display numpy warnings     
    np.seterr('ignore') 

    ne.get_datas_from_real_network(data_path,
                               results_path,
                               evaluation_method= evaluation_method,
                               network_type = network_type)

    genome = ga.new_genome(
                       results_path,
                       evaluation_method= evaluation_method,
                       tree_type = tree_type,
                       network_type = network_type
                       )


    return evolve(genome ,rule_name, nb_generations =nb_generations, multiprocessing = multiprocessing)
    
def evolve(genome,rule_name,**kwargs):  
    '''
     takes a genome and options that define the genetic algorithm
                apply it to the genome
                returns infos about the best individual
    '''
   
    filename_stats = '../../results/temp/stats_quality_{}.txt'.format(rule_name)
    goal = emo.get_goal(genome.getParam("evaluation_method"))         
    multiprocessing = kwargs.get("multiprocessing",False)   
    algo = py.GSimpleGA.GSimpleGA(genome)
    algo.setMultiProcessing(multiprocessing)
    algo.selector.set(py.Selectors.GRouletteWheel)
    algo.setMinimax(py.Consts.minimaxType[goal]) 
    stats_adapter = st.StatisticsInTxt(rule_name,frequency = freq_stats)
    #stats_adapter = st.StatisticsQualityInTxt(rule_name,filename=filename_stats,frequency = freq_stats)
    algo.setDBAdapter(stats_adapter)
    number_of_generations = int(kwargs.get("nb_generations","100"))
    algo.setGenerations(number_of_generations)
    algo.evolve()
    return algo.bestIndividual()

if __name__ == "__main__":
    main()
