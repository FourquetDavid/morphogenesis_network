
import numpy as np
import collections
import mdp
import matplotlib.pyplot as plt
import networkx as nx
import community
#import scipy.cluster.vq as clust
from lxml import etree
import os

net_2 = {'prop_2' : 14,'prop_3' :  23, 'prop_1' : 12, 'prop_4' : 26}
net_1 = {'prop_1' : 3, 'prop_2' : 65, 'prop_4' : 1,'prop_3' :  32}
net_3 = {'prop_1' : 47, 'prop_2' : 3.5, 'prop_4' : 107/3,'prop_3' :  32}

dico = {'name_1' : net_1, 'name_2' : net_2,'name_3' : net_3}




def fromDicoToVectors (dico):
    
    names_vect = np.asarray(dico.keys())
    
    props_vect = None
    for props in dico.values() :
        if props_vect is not None :
            if collections.Counter(props_vect) != collections.Counter(props.keys()) :
                print props_vect
                print props.keys()
                raise TypeError()
        else :
            props_vect = props.keys()
    props_vect = np.asarray(props_vect)
    
    values_vect = None
    for props in dico.values() : 
        values = np.asarray(props.values())
        if values_vect is None :
            values_vect = values
        else :
            values_vect = np.vstack((values_vect, values))
            
    
    return names_vect, props_vect, values_vect

def correlationMatrix(array):  
    return np.corrcoef(np.transpose(array)) 

def correlation(props, array,ratio):
    print correlationMatrix(array)
    for (i,j),value in np.ndenumerate(correlationMatrix(array)) :
        if i>j and abs(value) > ratio :
            print str(props[i])+" and "+str(props[j])+" are correlated : "+str(value)
def communityDetection(props,array):
    graph = nx.Graph()
    for (i,j),value in np.ndenumerate(correlationMatrix(array)) :
        if i>j :
            graph.add_edge(props[i], props[j], weight=abs(value))
    print graph.edges(data = True)
    partition = community.best_partition(graph)
    communities = {}
    for key, item in partition.iteritems() :
        if item not in communities :
            communities[item] = []
        communities[item].append(key)
    print communities

         
def Kmeans(names,data,nb_clusters):  
    # computing K-Means with K = 2 (2 clusters)
    centroids,_ = clust.kmeans(data,nb_clusters)
    # assign each sample to a cluster
    idx,_ = clust.vq(data,centroids)
    communities = {}
    for numero, item in enumerate(idx) :
        if item not in communities :
            communities[item] = []
        communities[item].append(names[numero])
    print communities          
        
def normalizedVectors(array): 
    def normalize(a):
        return (a - np.mean(a))/np.std(a)
    return np.apply_along_axis(normalize, 0, array)

def pca(array,outputdim):
    pcanode1= mdp.nodes.PCANode(output_dim=outputdim)
    pcar = pcanode1.execute(normalizedVectors(array))
    #print pcar
    #Graph the results
    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    #ax.plot([pcar[:,i] for i in range(len(pcar[0]))])

    #Show variance accounted for
    #ax.set_xlabel((pcanode1.d[0]))
    #ax.set_ylabel((pcanode1.d[1]))
    #print pcanode1.explained_variance
    print pcanode1.get_recmatrix()
    #plt.show()

def KmeansNewDimensions(names,array,outputdim,nb_clusters):
    #compute new dimensions with pca
    pcanode= mdp.nodes.PCANode(output_dim=outputdim)
    pcanode.execute(normalizedVectors(array))
    
    #compute new coordinates in those dimensions
    data = clust.whiten(np.dot(array,pcanode.get_projmatrix()))

    # computing K-Means with K = 2 (2 clusters)
    centroids,_ = clust.kmeans(data,nb_clusters)
    # assign each sample to a cluster
    idx,_ = clust.vq(data,centroids)
    communities = {}
    for numero, item in enumerate(idx) :
        if item not in communities :
            communities[item] = []
        communities[item].append(names[numero])
    print communities
    # some plotting using numpy's logical indexing
    plt.plot(data[idx==0,0],data[idx==0,1],'ob',
         data[idx==1,0],data[idx==1,1],'or')
    plt.plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
    plt.show() 

    return communities
    
   

def subcorrelations(names,array, communities): 
    def sub_matrix(nets):
        def f(x):
            return x in nets
        elements = np.vectorize(f)(names)
        return array[elements ,:]  
    for _, nets in communities.iteritems() :
        print "in "+str(nets)+" :"
        correlation( props,sub_matrix(nets),0.9)

def etree_to_dict(t):
    d={}
    for child in t.iterchildren() :
        d[child.tag] = child.attrib['value']
    return t.tag,d        
        
def etrees_to_dict(path):
    dictionnary ={}
    for f in os.listdir(current_path) :
        name = "-".join(f.split("-")[1:])
        directory = current_path +f+"/"
        name,infos = etree_to_dict(etree.parse(directory+name+".xml").getroot())
        dictionnary[name] = infos
    return dictionnary
    
if __name__ == '__main__':
    current_path = "../../xml/" 
    dictionnary =etrees_to_dict(current_path)  
    names, props , values = fromDicoToVectors(dictionnary)
    #print  names, props
    #print values
    
    correlation(props,values,0.9)
    #communityDetection(props,values)
    #Kmeans(names,values,2)
    #communities = KmeansNewDimensions(names,values, 2,2)
    #subcorrelations(names, values, communities)
    #groupes(names, props,values, [1./2,1./2])
    #pca(values,2)
    #print correlationMatrix(values)
    #print normalizedVectors(values)
    
'''   
def groupes(names,props,values,repartition):
    
    number_of_networks = len(names)
    number_of_vraiables = len(props)
    #for each metric :
    #each measure is reduced to its ranked value : max if its value is high, 0 if its value is low compared to the others 
    cumulated_rep = np.cumsum(repartition)
    def digitize_axe(a):
        b = np.sort(a)
        bins = [b[i*len(b)-1] for i in cumulated_rep]
        c = np.digitize(a,bins,right = True)
        return c
    digitized = np.apply_along_axis(digitize_axe,0, values)
    print values
    print digitized
    
    #we compare networks and their ranks
    
    def compare_networks(i,j):
        return [digitized[i,k] == digitized[j,k] for k in range(len(values[i]))]
    
    def compare_variables(i,j):
        return [digitized[k,i] == digitized[k,j] for k in range(len(values))]
    
    
    comparedN = []
    comparedV = []
    for i in range(number_of_vraiables) :
        for j in range(number_of_vraiables) :
            if i <j :
                comparedV.append((props[i],props[j],compare_variables(i, j)))
                
    for i in range(number_of_networks) :
        for j in range(number_of_networks) :
            if i <j :
                print names[i] +" and "+ names[j]+" : ",
                print [props[k] for k,boolean in enumerate(compare_networks(i, j)) if boolean]
                comparedN.append((names[i],names[j],compare_networks(i, j)))

    print comparedN
    print comparedV
    
    #we regroup variables that are correlated on same networks
    def regroupVariables():
        for (propA,propB,nets) in regroupVariables() :
            for (propA2,propB2,nets2) in regroupVariables() :
                nets3 = np.logical_xor(nets,nets2)
                if np.all(nets3) or not np.any(nets3) :
                    print 
        
                
 '''   