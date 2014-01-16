
import numpy as np
import collections
import mdp
import matplotlib.pyplot as plt
import networkx as nx
import community
import scipy.cluster.vq as clust 
from lxml import etree
import os
import random
from networkx.convert import from_numpy_matrix
from pylab import pcolor, show, colorbar, xticks, yticks

net_2 = {'prop_2' : 14,'prop_3' :  23, 'prop_1' : 12, 'prop_4' : 26}
net_1 = {'prop_1' : 3, 'prop_2' : 65, 'prop_4' : 1,'prop_3' :  32}
net_3 = {'prop_1' : 47, 'prop_2' : 3.5, 'prop_4' : 107/3,'prop_3' :  32}

dico = {'name_1' : net_1, 'name_2' : net_2,'name_3' : net_3}




def fromDicoToVectors (dico):
    names_vect = np.asarray(dico.keys())
    
    props_vect = np.asarray(random.choice(dico.values()).keys())
    
    #check if all networks have same properties
    #delete when there are too many
    print len(props_vect)
    print len(names_vect)
    import math
    
    
    values_vect = None
    for name in names_vect :
        values = [dico[name][prop] for prop in props_vect]
        for prop in props_vect :
            if math.isnan(dico[name][prop]) : print name, prop
        if values_vect is None :
            values_vect = values
        else :
            values_vect = np.vstack((values_vect, values))
            
    
    return names_vect, props_vect, values_vect

def correlationMatrix(array):  
    correlation = np.corrcoef(np.transpose(array)) 
    print np.sum(correlation) /(118*118)
    return correlation



    
      
    
def correlation(props, array,ratio):
    #import math
    
    print correlationMatrix(array)[111]
    for (i,j),value in np.ndenumerate(correlationMatrix(array)) :
        if i>j and abs(value) > ratio :
            print str(props[i])+" and "+str(props[j])+" are correlated : "+str(value)
        #if math.isnan(value) : print str(props[i])+" and "+str(props[j]), j
       
def communityDetection(props,array):
    
    graph = nx.Graph()
    for (i,j),value in np.ndenumerate(correlationMatrix(array)) :
        if i>j :
            graph.add_edge(props[i], props[j], {'weight' : abs(value)})
    
    
    
    #print graph.edges(data = True)
    partition = community.best_partition(graph)
    
    communities = {}
    for key, item in partition.iteritems() :
        graph.node[key]['community']= item
        if item not in communities :
            communities[item] = []
        communities[item].append(key)
    for key, value in communities.iteritems() :
        for element in value : 
            print element
            '''
            sum =0
            for element2 in value :
                if element2 != element : 
                    sum+=graph[element][element2]['weight']
            print element,sum
            '''
        print '###########'
        print len(communities[key])
    print graph.nodes(data=True)
    for (i,j),value in np.ndenumerate(correlationMatrix(array)) :
        if i>j :
            graph[props[i]][props[j]]['weight'] = 1000*( abs(value)**5)
    nx.write_gexf(graph, "../../correlation.gexf") 
    return communities

def correlationMatrixReloaded(correlation,props,communities): 
    correlationReloaded = correlation.copy()
    new_props =[prop  for community in [3,1,2,0,4] for prop in communities[community]]
    print new_props
    
    props = list(props)
    
    for i,prop_i in enumerate(new_props) :
        old_index_i = props.index(prop_i)
        for j,prop_j in enumerate(new_props) :
            old_index_j = props.index(prop_j)
            correlationReloaded[i,j] = correlation[old_index_i,old_index_j]
    
    pcolor(np.abs(correlationReloaded), cmap=plt.cm.gray)
    colorbar()
    '''
    fig, ax = plt.subplots()
    ax.imshow(np.abs(correlationReloaded), cmap=plt.cm.gray, interpolation='nearest')
    

    # Move left and bottom spines outward by 10 points
    ax.spines['left'].set_position(('outward', 10))
    ax.spines['bottom'].set_position(('outward', 10))
    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

'''    
    plt.show()        
    return new_props,correlationReloaded

    
def Kmeans(names,data,nb_clusters):  
    # computing K-Means with K = 2 (2 clusters)
    centroids,note = clust.kmeans(data,nb_clusters)
    print note 
    # assign each sample to a cluster
    idx,_ = clust.vq(data,centroids)
    communities = {}
    for numero, item in enumerate(idx) :
        if item not in communities :
            communities[item] = []
        communities[item].append(names[numero])
    for key, value in communities.iteritems() :
        print value          
        
def normalizedVectors(array): 
    def normalize(a):
        return (a - np.mean(a))/np.std(a)
    return np.apply_along_axis(normalize, 0, array)

def pcaScikit(digits,names,props):
    from time import time
    import pylab as pl
    
    from sklearn import metrics
    from sklearn.cluster import KMeans
    from sklearn.datasets import load_digits
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import scale
    
    np.random.seed(36)
    
    data = scale(digits)
    
    n_samples, n_features = data.shape
    n_digits = 5
    labels = names
    
    sample_size = 300
    
    print("n_digits: %d, \t n_samples %d, \t n_features %d"
          % (n_digits, n_samples, n_features))
    
    
    print(79 * '_')
    print('% 9s' % 'init'
          '    time  inertia    homo   compl  v-meas     ARI AMI  silhouette')
    
    
    def bench_k_means(estimator, name, data):
        t0 = time()
        estimator.fit(data)
        print('% 9s   %.2fs    %i   %.3f   %.3f   %.3f   %.3f   %.3f    %.3f'
              % (name, (time() - t0), estimator.inertia_,
                 metrics.homogeneity_score(labels, estimator.labels_),
                 metrics.completeness_score(labels, estimator.labels_),
                 metrics.v_measure_score(labels, estimator.labels_),
                 metrics.adjusted_rand_score(labels, estimator.labels_),
                 metrics.adjusted_mutual_info_score(labels,  estimator.labels_),
                 metrics.silhouette_score(data, estimator.labels_,
                                          metric='euclidean',
                                          sample_size=sample_size)))
    
    
    
    # in this case the seeding of the centers is deterministic, hence we run the
    # kmeans algorithm only once with n_init=1
    pca = PCA(n_components=n_digits,whiten = True).fit(data)
    
    bench_k_means(KMeans(init=pca.components_, n_clusters=n_digits, n_init=1),
                  name="PCA-based",
                  data=data)
    print(79 * '_')
    
    ###############################################################################
    # Visualize the results on PCA-reduced data
    
    reduced_data = PCA(n_components=2).fit_transform(data)
    '''
    for vectors in pca.components_ :
        for index,value in enumerate(vectors) :
            if abs(value) > 0.03 :
                print props[index], value
        print "#################"
        '''
    kmeans = KMeans(init='k-means++', n_clusters=n_digits, n_init=10)
    kmeans.fit(reduced_data)
    
    # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = .02     # point in the mesh [x_min, m_max]x[y_min, y_max].
    
    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() + 1, reduced_data[:, 0].max() - 1
    y_min, y_max = reduced_data[:, 1].min() + 1, reduced_data[:, 1].max() - 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    
    # Obtain labels for each point in mesh. Use last trained model.
    Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])
    
    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    fig,ax =pl.subplots()#pl.figure(1)
    for i in np.arange(len(names)) :
        ax.annotate(names[i],xy=(reduced_data[i,0],reduced_data[i,1]),xytext =(reduced_data[i,0],reduced_data[i,1]))
    ax.set_ylabel('Centralization')
    ax.set_xlabel('Density')
    pl.imshow(Z, interpolation='nearest',
              extent=(xx.min(), xx.max(), yy.min(), yy.max()),
              cmap=pl.cm.Blues_r,
              aspect='auto', origin='lower')
    
    pl.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # Plot the centroids as a white X
    centroids = kmeans.cluster_centers_
    pl.scatter(centroids[:, 0], centroids[:, 1],
               marker='x', s=60, linewidths=3,
               color='w', zorder=10)
    pl.title('K-means clustering on the networks (PCA-reduced data)\n'
             'Centroids are marked with white cross')
    pl.xlim(x_min, x_max)
    pl.ylim(y_min, y_max)
    pl.xticks(())
    pl.yticks(())
    pl.show()
    
def pca(array,outputdim):
    pcanode1= mdp.nodes.PCANode(output_dim=outputdim,reduce = True, var_abs =1)
    pcar = pcanode1.execute(normalizedVectors(array))
    #print pcar
    #Graph the results
    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    #ax.plot([pcar[:,i] for i in range(len(pcar[0]))])

    #Show variance accounted for
    #ax.set_xlabel((pcanode1.d[0]))
    #ax.set_ylabel((pcanode1.d[1]))
    print pcanode1.explained_variance
    print pcanode1.get_recmatrix()
    print pcanode1.d[0]
    print pcanode1.d[1]
    print pcanode1.d[2]
    print pcanode1.d[3]
    print pcanode1.d[4]
    
    fig, ax = plt.subplots()
    plt.bar(np.arange(len(pcanode1.d)), pcanode1.d, color = 'black')
    plt.xticks( [0,1,2,3] ,  ('Size', 'Density','Centralization', 'Spectrum') )
    
    ax.set_ylabel('Explained Variance (%)')
    ax.set_xlabel('Components')
    ax.set_title('Scree Plot')
    plt.setp(plt.gca().get_xticklabels(), rotation=45)
    plt.show()
    
    
    for vectors in pcanode1.get_recmatrix() :
        for index,value in enumerate(vectors) :
            if abs(value) > 0.15 :
                print props[index], value
        print "#################"
    
    #plt.show()

def KmeansNewDimensions(names,array,outputdim,nb_clusters):
    #compute new dimensions with pca
    pcanode= mdp.nodes.PCANode(output_dim=outputdim)
    pcanode.execute(normalizedVectors(array))
    
    #compute new coordinates in those dimensions
    data = clust.whiten(np.dot(array,pcanode.get_projmatrix()))
    #data = np.dot(array,pcanode.get_projmatrix())
    
    # computing K-Means with K = 2 (2 clusters)
    centroids,score = clust.kmeans(data,4)
    # assign each sample to a cluster
    idx,_ = clust.vq(data,centroids)
    
    communities = {}
    for numero, item in enumerate(idx) :
        if item not in communities :
            communities[item] = []
        communities[item].append(names[numero])
    print score
    for item, value in communities.iteritems() :
        print value
    plt.scatter(data[:,4], data[:,1], c=idx)
    plt.show()
    
    '''
    # some plotting using numpy's logical indexing
    plt.plot(data[idx==0,0],data[idx==0,1],'ob',
         data[idx==1,0],data[idx==1,1],'or')
    plt.plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
    plt.show() 
    '''
    return communities
    
   

def subcorrelations(names,array, communities): 
    
    def sub_matrix(nets):
        names_list = list(names)
        submatrix = np.ndarray((len(nets),array.shape[1]))
        for i,name_i in enumerate(nets) :
            old_index_i = names_list.index(name_i)
            submatrix[i] = array[old_index_i]
        return submatrix
      
    for _, nets in communities.iteritems() :
        print  np.sum(np.abs(correlationMatrix(sub_matrix(nets))) )/(118*118)
        pcolor(np.abs(correlationMatrix(sub_matrix(nets))), cmap=plt.cm.gray)
        colorbar()
        show()
        #print "in "+str(nets)+" :"
        #correlation( props,sub_matrix(nets),0.9)

def etree_to_dict(t):
    d={}
    for child in t.iterchildren() :
        if child.tag not in ['algebraic_connectivity'] :
            d[child.tag] = float(child.attrib['value'])
    return t.tag,d        
        
def etrees_to_dict(path):
    dictionnary ={}
    for f in os.listdir(path) :
        name = "-".join(f.split("-")[1:])
        directory = path +f+"/"
        name,infos = etree_to_dict(etree.parse(directory+name+".xml").getroot())
        dictionnary[name] = infos
    return dictionnary

def xmls_to_dict(path):
    dictionnary = {}
    for f in os.listdir(path) :
        name,infos = etree_to_dict(etree.parse(path+f).getroot())
        dictionnary[name] = infos
    return dictionnary

if __name__ == '__main__':
    #current_path = "../../xml/" 
    #dictionnary =etrees_to_dict(current_path)  
    dictionnary = xmls_to_dict("../../aml2/")
    
    names, props , values = fromDicoToVectors(dictionnary) 
    #print  names, props, values
    #print values
    
    #correlation(props,values,0.9)
    #fromMatrixToNetwork(props, values)
    #communities = communityDetection(props,values)
    #correlationMatrixReloaded(correlationMatrix(values), props, communities)
    #Kmeans(names,values,10)
    #communities = KmeansNewDimensions(names,values, 5,5)
    #subcorrelations(names, values, communities)
    #groupes(names, props,values, [1./2,1./2])
    pca(values,0.9)
    #pcaScikit(values,names,props)
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