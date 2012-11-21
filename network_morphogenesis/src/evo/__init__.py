
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
#*evaluation_method : the method used to evaluate the proximity between real network and generated network
#                        possible values : "degree_distribution"
ne.get_datas_from_real_network('../../data/karate.gml',
                               '../../results/karate.txt',
                               evaluation_method="degree_distribution")

#optional arguments for genome : 
#*max_depth : maximal depth of the decision tree that defines a genome 
#             possible values : int > 0
#*init_method : method to build a decision tree
#                        possible values : "grow"
genome = ga.new_genome(
                       [["+","-","*"],
                        ["OrigId","TargId","OrigInDegree","TargInDegree","OrigOutDegree","OrigInDegree"]],
                       '../../results/karate.txt',
                       max_depth=3,
                       init_method ="grow",
                       evaluation_method="degree_distribution"
                       )

#optional arguments for evolve :
#*nb_generations : number of generations of the evolution 
#                   possible values : int > 0
#*evaluation_method : the method used to evaluate the proximity between real network and generated network
#                        possible values : "degree_distribution"
#*goal : "minimize" if the goal is to minimize the evaluation function
#        "maximize" if the goal is to maximize the evaluation function

results = ga.evolve(genome, nb_generations =2, goal="minimize")
print results

