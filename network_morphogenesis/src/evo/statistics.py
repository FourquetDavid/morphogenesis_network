'''
Created on 15 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
''' 

""" 
contains one main function :

*deal_with_stats : takes a genetic algorithm engine and print or write in a file the relevant statistics
        
    

"""


def deal_with_stats(engine,stat_path) :
    
    """ writes population statistics and the 5 best elements"""
    
    f = open(stat_path, 'a')
    f.write( "#####      Generation  {numero}   ###########".format(numero=engine.getCurrentGeneration()))
    print "#####      Generation  {numero}   ###########".format(numero=engine.getCurrentGeneration())
    print engine.getStatistics()
    f.write(engine.getStatistics().__repr__())
    
    pop = engine.getPopulation()
    for i in xrange(5) :
        f.write( "######### Arbre num {numero} ###########".format(numero=i) )
        print "######### Arbre num {numero} ###########".format(numero=i)
        tree = pop.bestFitness(i)
        f.write( str(tree.getFitnessScore()))
        print tree.getFitnessScore()
        f.write( tree.getTraversalString())
        print tree.getTraversalString()
    f.close()