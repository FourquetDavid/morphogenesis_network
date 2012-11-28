'''
Created on 27 nov. 2012

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
''' 

""" 
contains two main function :

*get-goal() : takes an evaluation method and returns teh goal that is associated : minimize if we have to minimize the evaluation_funcion
        
    

"""
def get_goal (evaluation_method) :
    if evaluation_method =="degree_distribution" :
        return "minimize"
    elif evaluation_method == "weighted" :
        return "minimize"
    else :
        return "minimize"
    
def get_alleles (evaluation_method):
    if evaluation_method =="degree_distribution" :
        return [["+","-","*","min","max"],
                        ["OrigId","TargId","OrigInDegree","TargInDegree","OrigOutDegree","OrigInDegree"]]
    if evaluation_method == "weighted" :
        return [["+","-","*","/","min","max","exp","log","abs"],
                        ["RelativeTargId","RelativeOrigId","OrigInStrength","TargInStrength","OrigOutStrength","OrigInStrength","DirectDistance","ReversedDistance"]]