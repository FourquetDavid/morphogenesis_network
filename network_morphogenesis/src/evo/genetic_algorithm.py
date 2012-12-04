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
import statistics as st
import evaluation_method_options as emo


""" 
contains two main function :

*new_genome : takes a set of alleles and options that define initializator, mutator, crossover, evaluator 
                and returns a genome with those options
                
*evolve : takes a genome and options that define the genetic algorithm
                apply it to the genome
                returns infos about the best individual
                
"""

def new_genome(results_path,**kwargs):
    '''
    *new_genome : takes a set of alleles [function_alleles, leaves_alleles] 
                and options that define initializator, mutator, crossover, evaluator 
                and returns a genome with those options
                
                possible initializator : "grow" : "grow" algorithm of network = recursive and possibly incomplete
                possible mutator : "simple" : change genomic alleles with possible alleles with probability pmut
                possible crossover :
                possible evaluator : "degree_distribution"
     '''  
    evaluation_method = kwargs.get("evaluation_method")      
    choices = emo.get_alleles(evaluation_method)
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
    genome.setParams(evaluation_method = evaluation_method)
    genome.evaluator.set(eval_func)
    
    #define the crossover function - default now
    
    #define the function that mutates trees
    genome.setParams(mutation_method = kwargs.get("mutation_method","default_mutation"))
    genome.mutator.set(mutate_tree)
    
    tree_init(genome)
    return genome

def evolve(genome,**kwargs):  
    '''
     takes a genome and options that define the genetic algorithm
                apply it to the genome
                returns infos about the best individual
    '''
    #depending on the evaluation_method, we will have different goals
    goal = emo.get_goal( kwargs.get("evaluation_method"))         
    multiprocessing = kwargs.get("multiprocessing",False)   
    #genetic_algorithm = kwargs.get("genetic_algorithm","default_algorithm")
    
    algo = py.GSimpleGA.GSimpleGA(genome)
    algo.setMultiProcessing(multiprocessing)

    
    
    #the selector is used to choose which ones will be parents of the next generation
    algo.selector.set(Selectors.GRouletteWheel)
    
    #elitism will keep the top individuals with their score in the next generation : 
    #it can help us to keep track of some of the best graph generations
    #algo.setElitism(True)
    #algo.setElitismReplacement(10)
    
    
    algo.setMinimax(py.Consts.minimaxType[goal])
    
    
    
    
    #now we do evolve with algorithm and every freq stats, we compute statistics
    freq_stats = int(kwargs.get("freq_stats","1"))
    filename_stats = kwargs.get("stats_path")
    stats_adapter = st.StatisticsInTxt(filename=filename_stats,frequency = freq_stats)
    algo.setDBAdapter(stats_adapter)
    
    
    number_of_generations = int(kwargs.get("nb_generations","100"))
    algo.setGenerations(number_of_generations)
    algo.evolve()
   
        
       
            
            
            
        

'''
Functions that build trees
'''
  
def tree_init(genome,**args):
    max_depth = genome.getParam("max_depth")
    max_siblings = genome.getParam("max_siblings")
    allele = genome.getParam("allele")
    
    init_method = genome.getParam("init_method")
    if init_method == "grow" :
        root = buildGTreeGrow(0, allele[0][0],allele[0][1], max_siblings, max_depth)
    else :
        #default method
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
def simple_mutate_tree(genome, **args):
    mutations = 0
    allele = genome.getParam("allele")
    for node in genome.getAllNodes() :
        if py.Util.randomFlipCoin(args["pmut"]):
            mutations += 1
            if node.isLeaf() : 
                node.setData(random.choice(allele[0][1]))
            else : 
                node.setData(random.choice(allele[0][0]))
    return mutations

def mutate_tree(genome, **args):
    mutation_method = genome.getParam("mutation_method")
    if mutation_method == "simple_mutation" :
        return simple_mutate_tree(genome, **args)
    #default method
    return simple_mutate_tree(genome, **args)
    
'''
Functions that evaluate trees
'''

def eval_func(chromosome):
    net = nd.grow_network(chromosome,int(chromosome.getParam("nb_nodes")),int(chromosome.getParam("nb_edges")),
                          evaluation_method=chromosome.getParam("evaluation_method"))
    score = ne.eval_network(net,chromosome.getParam("results_path"),evaluation_method=chromosome.getParam("evaluation_method"))                          
    return score  
