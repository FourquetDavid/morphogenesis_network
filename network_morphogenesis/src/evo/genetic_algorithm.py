'''
Created on 15 nov. 2012
@author: David
inspired by Telmo Menezes's work : telmomenezes.com
'''
import random
import network_development as nd
import network_evaluation as ne
import pyevolve as py
from pyevolve import *

""" 
contains two main function :

*new_genome : takes a set of alleles and options that define initializator, mutator, crossover, evaluator 
                and returns a genome with those options
                
*evolve : takes a genome and options that define the genetic algorithm
                apply it to the genome
                returns infos about the best individual
                
"""

def new_genome(choices,results_path,**kwargs):
    '''
    *new_genome : takes a set of alleles [function_alleles, leaves_alleles] 
                and options that define initializator, mutator, crossover, evaluator 
                and returns a genome with those options
                
                possible initializator : "grow" : "grow" algorithm of network = recursive and possibly incomplete
                possible mutator : "simple" : change genomic alleles with possible alleles with probability pmut
                possible crossover :
                possible evaluator : "degree_distribution"
     '''           
    genome = py.GTree.GTree()
    genome.setParams(nb_nodes=ne.get_number_of_nodes(results_path))
    genome.setParams(nb_edges=ne.get_number_of_edges(results_path))
    genome.setParams(results_path=results_path)
    

    #define alleles : one array containing possible leaves and one containing possible functions
    alleles = py.GAllele.GAlleles()
    lst = py.GAllele.GAlleleList(choices)
    alleles.add(lst)
    genome.setParams(allele=alleles)
    
    #define the way to construct a random tree
    genome.setParams(max_depth=int(kwargs.get("max_depth","3"))) 
    genome.setParams(max_siblings=int(kwargs.get("max_siblings","2")))
    
    genome.setParams(init_method = kwargs.get("init_method","default_init"))
    genome.initializator.set(tree_init)
    
    #define the how to evaluate a genome
    genome.setParams(evaluation_method = kwargs.get("evaluation_method","default_evaluation"))
    genome.evaluator.set(eval_func)
    
    #define the crossover function - default now
    
    #define the function that mutates trees
    genome.setParams(mutation_method = kwargs.get("mutation_method","default_mutation"))
    genome.mutator.set(mutate_tree)
    
    return genome

def evolve(genome,**kwargs): 
    '''
     takes a genome and options that define the genetic algorithm
                apply it to the genome
                returns infos about the best individual
    '''
    
    genetic_algorithm = kwargs.get("genetic_algorithm","default")
    if genetic_algorithm == "default" :
        ga = py.GSimpleGA.GSimpleGA(genome)
    ga.setGenerations(int(kwargs.get("nb_generations","100")))
    ga.evolve()
    return ga.bestIndividual()

'''
Functions that build trees
'''
    
def tree_init(genome):
    max_depth = genome.getParam("max_depth")
    max_siblings = genome.getParam("max_siblings")
    allele = genome.getParam("allele")
    
    init_method = genome.getParam("init_method")
    if init_method == "grow" :
        root = buildGTreeGrow(0, allele[0][0],allele[0][1], max_siblings, max_depth)
    if init_method == "default_init" :
        root = buildGTreeGrow(0, allele[0][0],allele[0][1], max_siblings, max_depth)
            
    genome.setRoot(root)
    genome.processNodes()
    assert genome.getHeight() <= max_depth

def buildGTreeGrow(depth, value_callback, value_leaf, max_siblings, max_depth):
    random_value = random.choice(value_callback)
    random_value_leaf =  random.choice(value_leaf)
    n = py.GTree.GTreeNode(0)

    if depth == max_depth: 
        n.setData(random_value_leaf)
        return n

    if py.Util.randomFlipCoin(0.5) :
        child = buildGTreeGrow(depth + 1, value_callback, value_leaf, max_siblings, max_depth)
        child.setParent(n)
        n.addChild(child)
        
        child = buildGTreeGrow(depth + 1, value_callback, value_leaf, max_siblings, max_depth)
        child.setParent(n)
        n.addChild(child)
    
    if n.isLeaf() : 
        n.setData(random_value_leaf)
    else :
        n.setData(random_value)
    return n




'''
Functions that mutate trees
'''
def mutate_tree(genome, **args):
    mutations = 0
    for node in genome.getAllNodes() :
        if py.Util.randomFlipCoin(args["pmut"]):
            mutations += 1
            if node.isLeaf() : 
                node.setData(random.choice(["OrigId","TargId","OrigInDegree","TargInDegree","OrigOutDegree","TargOutDegree"]))
            else : 
                node.setData(random.choice(["+","-","*"]))
    return mutations
    
'''
Functions that evaluate trees
'''

def eval_func(chromosome):
    net = nd.grow_network(chromosome,int(chromosome.getParam("nb_nodes")),int(chromosome.getParam("nb_edges")))
    score = ne.eval_network(net,chromosome.getParam("results_path"),evaluation_method=chromosome.getParam("evaluation_method"))                          
    return score  
