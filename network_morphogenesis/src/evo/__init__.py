
'''
Created on 12 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
'''

import network_evaluation as ne  
import genetic_algorithm as ga  
import numpy as np
import os, sys
import warnings
 
'''
This is the main file of the program :
it stores datas from the real network necessary to the chosen evaluation method 
define the genetic algorithm and its grammar
and call it
'''

def main() :
    
    #possible arguments : 
#*evaluation_method : the method used to evaluate the proximity between real network and generated network
#                        possible values : "degree_distribution""weighted"
    evaluation_method ="degree_distribution"
    multiprocessing = True
    
    #do not display numpy warnings     
    np.seterr('ignore') 
    
#arguments : path to the real network, path to print datas
    ne.get_datas_from_real_network('../../data/karate.gml',
                               '../../results/karate_weighted.txt',
                               evaluation_method= evaluation_method)
    
    
#arguments : path to datas about the real network
#optional arguments for genome : 
#*max_depth : maximal depth of the decision tree that defines a genome 
#             possible values : int > 0
#*init_method : method to build a decision tree
#                        possible values : "grow"
    genome = ga.new_genome(
                       '../../results/karate_weighted.txt',
                       evaluation_method= evaluation_method
                       )
    
    
#optional arguments for evolve :
#*nb_generations : number of generations of the evolution 
#                   possible values : int > 0 : default : 100
#*freq_stats : number of generations between two prints of statistics 
#                   possible values : int > 0 : default : 5
#*stats_path : path to the file where the stats will be printed 
#                   
    if len(sys.argv) > 1 : numero= sys.argv[1]
    else : numero = 0

    ga.evolve(genome,stats_path = '../../results/karate_weighted_stats{}.txt'.format(numero), nb_generations =100,freq_stats = 5, multiprocessing = multiprocessing)

if __name__ == "__main__":
    main()

