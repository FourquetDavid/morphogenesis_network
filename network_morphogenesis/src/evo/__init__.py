'''

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
'''

import network_evaluation as ne  
import genetic_algorithm as ga  
import numpy as np


 
'''
This is the main file of the program :
it stores datas from the real network necessary to the chosen evaluation method 
define the genetic algorithm and its grammar
and call it
'''
#@profile
def main() :

    evaluation_method ="communities_degrees_distances_clustering_importance"
    tree_type = "with_constants"
    network_type = "undirected_unweighted"
    network = "karate"
    multiprocessing = False
    dynamic = False
    data_path = '../../data/{}/'.format(network)
    results_path ='../../results/{}/{}.xml'.format(network,evaluation_method)
    stats_path = '../../results/{}/{}_stats.txt'.format(network,evaluation_method)
    nb_generations =11 
    freq_stats =5
    #do not display numpy warnings     
    np.seterr('ignore') 
 
    
#arguments : path to the real network, path to print datas
    #possible arguments : 
#*evaluation_method : the method used to evaluate the proximity between real network and generated network
#                        possible values : "(nodes)_(vertices)_(clustering)_(importance)_(communities)_(distances)_(degrees)"
    ne.get_datas_from_real_network(data_path,
                               results_path,
                               name= network,
                               evaluation_method= evaluation_method,
                               network_type = network_type,
                               dynamic = dynamic,
                               extension = ".gexf")
    
    
#arguments : path to datas about the real network
#optional arguments for genome : 
#*max_depth : maximal depth of the decision tree that defines a genome 
#             possible values : int > 0
#evaluation_method : the method used to evaluate the proximity between real network and generated network
#                        possible values : "(nodes)_(vertices)_(clustering)_(importance)_(communities)_(distances)_(degrees)"
#tree_type : the type of the trees used to stores genomes : with or without constants in leaves
#                        possible values : "with_constants" "simple"
#network_type : the type of the networks studied and generated : directed or not
#                possible values : "(un)weighted_(un)directed"
#dynamic : if the network is dynamic or not
    
    genome = ga.new_genome(
                       results_path,
                       name= network,
                       data_path = data_path,
                       evaluation_method= evaluation_method,
                       dynamic = dynamic,
                       tree_type = tree_type,
                       network_type = network_type,
                       extension = ".gexf"
                       )
    
#optional arguments for evolve :
#*nb_generations : number of generations of the evolution 
#                   possible values : int > 0 : default : 100
#*freq_stats : number of generations between two prints of statistics 
#                   possible values : int > 0 : default : 5
#*stats_path : path to the file where the stats will be printed 
#*multiprocessing : will use or not multiprocessing 
#                possible values : True False
    

    ga.evolve(genome,stats_path = stats_path , nb_generations =nb_generations,freq_stats = freq_stats, multiprocessing = multiprocessing)

if __name__ == "__main__":
    main()

