'''
Created on 27 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
''' 

""" 
contains two main function :

*get-goal() : takes an evaluation method and returns the goal that is associated : minimize if we have to minimize the evaluation_funcion
        
     

"""
def get_goal (evaluation_method) :
    if evaluation_method =="degree_distribution" :
        return "minimize"
    if evaluation_method == "2distributions" :
        return "minimize"
    raise Exception("no evaluation_method")
    
    
def get_alleles (evaluation_method,network_type):
    if evaluation_method =="degree_distribution" :
        return [["+","-","*","min","max"],
                        ["OrigId","TargId","OrigInDegree","TargInDegree","OrigOutDegree","OrigInDegree"]]
    if evaluation_method == "autre" :
        if network_type == "directed_weighted" or network_type == "undirected_weighted" :
            return [["+","-","*","/","min","max","exp","log","abs","inv","opp"],
                        ["NormalizedTargId","TargId","OrigId","NormalizedOrigId","OrigInStrength","TargInStrength","OrigOutStrength","TargOutStrength","DirectDistance","ReversedDistance",
                         "NormalizedOrigInStrength","NormalizedTargInStrength","NormalizedOrigOutStrength","NormalizedTargOutStrength","NormalizedDirectDistance","NormalizedReversedDistance",
                         "AverageInStrength","AverageOutStrength","AverageWeight" ,"AverageDistance" ,"NumberOfNodes" ,"NumberOfEdges","MaxInStrength","MaxOutStrength","MaxWeight","MaxDistance",
                       "TotalDistance","TotalWeight","Constant","Random"
                        ]]
        if network_type == "directed_unweighted" or network_type == "undirected_unweighted" :
            return [["+","-","*","/","min","max","exp","log","abs","inv","opp"],
                        ["NormalizedTargId","TargId","OrigId","NormalizedOrigId","OrigStrength","TargStrength","Distance",
                         "NormalizedOrigStrength","NormalizedTargStrength","NormalizedDistance",
                         "AverageStrength","AverageWeight" ,"AverageDistance" ,"NumberOfNodes" ,"NumberOfEdges","MaxStrength","MaxWeight","MaxDistance",
                       "TotalDistance","TotalWeight","Constant","Random"
                        ]]
            
    if evaluation_method == "2distributions" :
        if network_type == "directed_weighted" or network_type == "undirected_weighted" :
            return [["+","-","*","/","min","max","exp","log","abs","inv","opp"],
                        ["TargId","OrigId","OrigInDegree","TargInDegree","OrigOutDegree","TargOutDehree","DirectDistance","ReversedDistance",
                         "NumberOfEdges","Constant"
                        ]]
        if network_type == "directed_unweighted" or network_type == "undirected_unweighted" :
            return [["+","-","*","/","min","max","exp","log","abs","inv","opp"],
                        ["TargId","OrigId","OrigDegree","TargDegree","Distance",
                         "NumberOfEdges","Constant"
                        ]]
            
    raise Exception("no evaluation_method or network_type given")
    #if evaluation_method == "weighted" :
    #    return [["+","-","*","/","min","max","exp","log","abs","inv"],
    #                   ["NormalizedTargId","NormalizedOrigId","OrigInStrength","TargInStrength","TargOutStrength","OrigInStrength","DirectDistance","ReversedDistance"]]