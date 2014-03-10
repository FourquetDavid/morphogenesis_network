'''
Created on 17 janv. 2014

@author: davidfourquet
'''

import network_development as nd 
import graph_types.Undirected_UnweightedGWU as uugwu
import networkx as nx
import matplotlib.pyplot as plt

    
def grow_network_with_constants(constant,variable,number_of_nodes, number_of_steps,graph= None):
    if graph is None :
        graph = uugwu.Undirected_UnweightedGWU(graph)
        
    number_of_nodes_init = graph.number_of_nodes()
    for i in range(number_of_nodes) :
        graph.add_node(i+number_of_nodes_init)
    #adds one edge according to its probability
    for _ in xrange(number_of_steps) :
        #each edge has a probability that is the result of the tree
        probas = constant*(getattr(graph,variable)())
        #we remove unnecessary edges : self loops, negative proba
        #we choose one among remaining ones
        
        edge,_ = nd.choose_edge(probas, graph)
        
        if edge is None : #this can happen if every edge has a -infinity probability thanks to log or / or - exp...
            break
        
        graph.add_edge(*edge)
            
    return graph   


if __name__ == '__main__':
     
    net = grow_network_with_constants(3.,"TargDegree",10,10 )
    nx.write_gexf(net, "../../data/Dyn/Dyn0.gexf")
    nx.draw(net)
    plt.savefig("../../data/Dyn/Dyn0.png")
    plt.close()
    
    net = grow_network_with_constants(3.,"TargDegree",2,4,net)
    nx.write_gexf(net, "../../data/Dyn/Dyn1.gexf")
    nx.draw(net)
    plt.savefig("../../data/Dyn/Dyn1.png")
    plt.close()
    
    net = grow_network_with_constants(3.,"TargDegree",3,8,net)
    nx.write_gexf(net, "../../data/Dyn/Dyn2.gexf")
    nx.draw(net)
    plt.savefig("../../data/Dyn/Dyn2.png")
    plt.close()
    
    net = grow_network_with_constants(3.,"TargDegree",2,12,net)
    nx.write_gexf(net, "../../data/Dyn/Dyn3.gexf")
    nx.draw(net)
    plt.savefig("../../data/Dyn/Dyn3.png")
    plt.close()
    
    net = grow_network_with_constants(3.,"TargDegree",3,16,net)
    nx.write_gexf(net, "../../data/Dyn/Dyn4.gexf")
    nx.draw(net)
    plt.savefig("../../data/Dyn/Dyn4.png")
    plt.close()
    
       
    