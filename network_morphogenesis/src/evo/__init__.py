
'''
Created on 12 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
'''

import network_evaluation as ne
import genetic_algorithm as ga

'''
This is the main file of the program :
it stores datas from the real network necessary to the chosen evaluation method 
define the genetic algorithm and its grammar
and call it
'''



#possible arguments : 
#*evaluation_method : the method used to evaluate teh proximity between real network and generated network
#                        possible values : "degree_distribution"
ne.get_datas_from_real_network('../../data/karate.gml',
                               '../../results/karate.txt',
                               evaluation_method="degree_distribution")

#optional arguments for genome : 
#*max_depth : maximal depth of the decision tree that defines a genome 
#             possible values : int > 0
#*building_tree_method : method to build a decision tree
#                        possible values : "grow"
genome = ga.new_genome(
                       [["+","-","*"],
                        ["OrigId","TargId","OrigInDegree","TargInDegree","OrigOutDegree","OrigInDegree"]],
                       '../../results/karate.txt',
                       max_depth=3,
                       building_tree_method="grow",
                       )

#optional arguments for evolve :
#*nb_generations : number of generatiosn of teh evolution 
#                   possible values : int > 0
#*evaluation_method : the method used to evaluate teh proximity between real network and generated network
#                        possible values : "degree_distribution"
#*genetic_algorithm : the genetic algorithm used for the evolution process
results = ga.evolve(genome, evaluation_method = "degree_distribution", nb_generations =1)
print results

