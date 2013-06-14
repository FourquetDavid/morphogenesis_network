'''
Created on 4 mars 2013

@author: davidfourquet
'''


import networkx as nx
import community
import numpy as np
import itertools as it 
from lxml import etree as xml
import mdp
import matplotlib.pyplot as plt
from scipy import stats
import math

already_computed = {}


def to_undirected(f):
    def wrapper(net):
        if net.is_directed() :
            return f(net.to_undirected())
        else :
            return f(net)
    return wrapper

def to_directed(f):
    def wrapper(net):
        if not net.is_directed() :
            return f(net.to_directed())
        else :
            return f(net)
    return wrapper


def println(f):
    def wrapper(net):
            result = f(net)
            print result
            return result
    return wrapper    
   
def giant_component(net):
    if 'giant_component' in already_computed :
        return already_computed['giant_component']
    else :
        if net.is_directed() :
            already_computed['giant_component'] = nx.strongly_connected_component_subgraphs(net)[0]
        else :
            already_computed['giant_component'] = nx.connected_component_subgraphs(net)[0]
        return already_computed['giant_component']

def distances_matrix(net):
    if 'distance' in already_computed :
        return already_computed['distance']
    else :
        already_computed['distance'] = nx.shortest_path_length(giant_component(net))      
        return already_computed['distance']

def eccentricity_list(net):
    if 'eccentricity' in already_computed :
        return already_computed['eccentricity']
    else :
        already_computed['eccentricity'] = nx.eccentricity(giant_component(net),sp= distances_matrix(net))
        return already_computed['eccentricity']
    
    
def distri(values, name): 
    mean = np.mean(values)
    std = np.std(values)
    return (mean,'average_'+name),(std,'std_'+name)

def distriMax(values,name): 
    m,s = distri(values, name)
    return m,s,(np.max(values),'max_'+name)  

def distriCentra(values,values_th,name):    
    centralization = np.sum(max(values)-np.array(values))
    centralization_max = np.sum(max(values_th)-np.array(values_th))
    score = float(centralization)/centralization_max
    m,s =distri(values,name+'_centrality')
    return m,s,(score,'centralization_'+name)
 
def setSize(ensemble,number_of_nodes,name): 
    return (len(ensemble),'size_'+name),(float(len(ensemble))/number_of_nodes,'proportion_'+name)       

def dirige(network):
    return ((network.is_directed(),'directed'),)
@println           
def nodes(network):
    return ((network.number_of_nodes(),'number_of_nodes'),)

def edges(network):
    return ((network.number_of_edges(),'number_of_edges'),)

def prop_edges(network):
    if network.is_directed():
        return ((float(network.number_of_edges())/(network.number_of_nodes()*(network.number_of_nodes()-1)), 'proportion_of_edges'),)
    else :
        return ((2*float(network.number_of_edges())/(network.number_of_nodes()*(network.number_of_nodes()-1)), 'proportion_of_edges'),)

@to_undirected
def communities(net):
    parti = community.best_partition(net)
    modu = community.modularity(parti, net)
    com = parti.values()
    number_of_communities = max(com)+1
    hist = np.histogram(com,bins=range(0,number_of_communities+1),density=True)[0]
    values = np.square(hist)
    repartition = 1 / (sum(values))
    return (number_of_communities,'number_of_communities'),(repartition,'equivalent_number_of_communities'),(modu,'modularity_Louvain_partition')
@println
def degrees(network): 
    if network.is_directed() :
        d1 = distriMax(network.in_degree().values(), 'indegree')
        d2 = distriMax(network.out_degree().values(), 'outdegree')
    else :
        d1 = distriMax(network.degree().values(), 'indegree')
        d2 = distriMax(network.degree().values(), 'outdegree')
    d0 = distriMax(network.degree().values(), 'degree')
    return d0+d1+d2

@println
def ball(net):
    netsize = float(net.number_of_nodes())
    #here we take the full network to find neighbors, not only the giant component part.
    dist = nx.shortest_path_length(net).values()
    def prop(entier):
        return [ len([distance for distance in x1.values() if distance<=entier])/netsize for x1 in dist]
    def size(entier):
        return [ len([distance for distance in x1.values() if distance<=entier]) for x1 in dist]
    
    return distri(size(1), 'size_1_neighborhood')+distri(size(2), 'size_2_neighborhood')+distri(size(3), 'size_3_neighborhood')+distri(prop(1), 
                            'proportion_1_neighborhood')+distri(prop(2), 'proportion_2_neighborhood')+distri(prop(3), 'proportion_3_neighborhood')
'''@to_undirected                            
def motif(net):
    triangle =0
    fourche =0
    clique=0
    for node1,degree in net.degree_iter :
        for node2 in net.neighbors_iter(node1) :
            for node3 in  net.neighbors_iter(node1) :
                if net.has_edge(node2,node3) :
                    triangle+=1
                else :
                    fourche+=1
                for node4 in net.neighbors_iter(node1) :
                    count = [net.has_edge(node2,node3),net.has_edge(node2,node4),net.has_edge(node3,node4)].count(True)
                    if count == 0 : tri_fourche+=1
                    if count == 0 : tri_fourche+=1
                    if count == 0 : tri_fourche+=1
                    if count == 3 : clique+=1    
                for node4 in net.neighbors_iter(node2) :
                    pass
        fourche-= degree           
 '''               
                    
                    
        

    
def distances(network):
    dist = distances_matrix(network).values()
    list_dist = list(it.chain.from_iterable([dict_of_length.values() for dict_of_length in dist]))
    return distriMax(list_dist,'distance')


def bala(net):
    netsize = giant_component(net).number_of_nodes()
    edgenum = giant_component(net).number_of_edges()
    dist = distances_matrix(network).values()
    list_dist = [1.0/math.sqrt(sum(distances.values())) for distances in dist]
    bala = (edgenum*sum(list_dist)**2)/(edgenum-netsize+2)
    return ((bala,'balaban_index'),)


def harary(net):
    dist = distances_matrix(net)
    list_dist = [1.0/distance for dict_of_length in dist.values() for distance in dict_of_length.values() if distance!=0]
    hara = sum(list_dist)/2
    return ((hara,'harary_index'),)


def wiener(net):
    dist = distances_matrix(net)
    list_dist = [distance for dict_of_length in dist.values() for distance in dict_of_length.values() if distance!=0]
    wien = sum(list_dist)/2
    return ((wien,'wiener_index'),)

         
def effi(net):
    dist = distances_matrix(net)
    list_dist = np.asarray([1.0/distance for dict_of_length in dist.values() for distance in dict_of_length.values() if distance!=0])
    effi = np.mean(list_dist)
    return ((effi,'efficiency'),)


def radiality(net):
    dist = distances_matrix(net)
    N = giant_component(net).number_of_nodes()
    d = nx.diameter(net,e=eccentricity_list(net))
    radiality = map(lambda distances :d-float(sum(distances.values()))/(N-1),dist.values())
    return distri(radiality,'radiality')

def core(net):
    cori = nx.core_number(net)
    main_core = nx.k_core(net,  core_number=cori)
    return distri(cori.values(), 'core_number')+setSize(main_core, net.number_of_nodes(), 'main_core')
    
@to_undirected
def clustering(network):
    return distri(nx.clustering(network).values(),'clustering')

def neighdeg(network):
    return distri(nx.average_neighbor_degree(network).values(),'neighbor_degree')

def star(net):
    return nx.star_graph(net.number_of_nodes()-1)

def pagerank(net):
    return distri(nx.pagerank(net).values(),
                        'pagerank')
def eigen(net):
    return distriCentra(nx.eigenvector_centrality_numpy(net).values(),
                        nx.eigenvector_centrality_numpy(star(net)).values(),
                        'eigenvector')
      
def close_center(net):
    return distriCentra(nx.closeness_centrality(net).values(),
                        nx.closeness_centrality(star(net)).values(),
                        'closeness')


def between_center(net):
    return distriCentra(nx.betweenness_centrality(net,normalized= True).values(),
                        nx.betweenness_centrality(star(net),normalized= True).values(),
                        'betweenness')
    

def flow_center(net):
    return distriCentra(nx.current_flow_closeness_centrality(net,normalized= True).values(),
                        nx.current_flow_closeness_centrality(star(net),normalized= True).values(),
                        'information')


def flow_between(net):
    return distriCentra(nx.current_flow_betweenness_centrality(net,normalized= True).values(),
                        nx.current_flow_betweenness_centrality(star(net),normalized= True).values(),
                        'current_flow_betweenness')
    

def load_center(net):
    return distriCentra(nx.load_centrality(net,normalized= True).values(),
                        nx.load_centrality(star(net),normalized= True).values(),
                        'load')
    

def com_center(net):
    return distriCentra(nx.communicability_centrality(net).values(),
                        nx.communicability_centrality(star(net)).values(),
                        'communicability')

def com_bet(net):
    return distriCentra(nx.communicability_betweenness_centrality(net,normalized= True).values(),
                        nx.communicability_betweenness_centrality(star(net),normalized= True).values(),
                        'communicability_betweenness')
@to_directed
def edge_reciprocity(net):
    N = net.number_of_nodes()
    L = net.number_of_edges()
    density = float(L)/(N*(N-1))
    number_of_reciprocal_links = sum([1 for node in net.nodes_iter() for node2 in net.successors_iter(node) if net.has_edge(node2,node) ])
    return (((float(number_of_reciprocal_links)/L - density)/(1-density),'reciprocity'),)

@to_directed
def hits(net):
    hubs,authorities = nx.hits_numpy(net)
    return distri(hubs.values(), 'hubs')+distri(authorities.values(),'authorities')
    
def trans(net): 
    return ((nx.transitivity(net),'transitivity'),)
def vit(net):
    return((nx.closeness_vitality(net),'closeness'),)
def comp(net):
    return setSize(giant_component(net),net.number_of_nodes(),'main_strongly_connected_component')
def center(net):
    return setSize(nx.center(net,e=eccentricity_list(net)), net.number_of_nodes(),'center')
def peri(net):
    return setSize(nx.periphery(net,e=eccentricity_list(net)), net.number_of_nodes(),'periphery')
def rad(net):
    return ((nx.radius(net,e=eccentricity_list(net)),'radius'),)
def eccc(net):
    return distri(eccentricity_list(net).values(),'eccentricity')
def diam(net):
    return ((nx.diameter(net,e=eccentricity_list(net)),'diameter'),)

def spectrum(spectre,name):
    maxi = max(spectre)
    mean = np.mean(spectre)
    std = np.std(spectre)
    mini = min(spectre)
    return (mini.real,'minimum_'+name+'_eigenvalue'),(maxi.real,'maximum_'+name+'_eigenvalue'), (mean.real,'average_'+name+'_eigenvalue'),(std.real,'std_'+name+'_eigenvalue')

def lapl_spect(net):
    spec = nx.laplacian_spectrum(net)
    connec = sorted(spec)[1]
    _,b,c,d = spectrum(spec,'laplacian')
    return b,c,d,(connec,'algebraic_connectivity')

def adja_spect(net):
    return spectrum(nx.adjacency_spectrum(net),'adjacency')

@to_undirected
def ramsey(net):
    def ramsey_R2(graph):
        if not graph:
            return (set([]), set([]))
    
        node = next(graph.nodes_iter())
        nbrs = nx.all_neighbors(graph, node)
        nnbrs = nx.non_neighbors(graph, node)
        c_1, i_1 = ramsey_R2(graph.subgraph(nbrs))
        c_2, i_2 = ramsey_R2(graph.subgraph(nnbrs))
    
        c_1.add(node)
        i_2.add(node)
        return (max([c_1, c_2]), max([i_1, i_2]))
    clique,inde = ramsey_R2(net)
    return setSize(inde,net.number_of_nodes(),'maximum_independant_set')+setSize(clique,net.number_of_nodes(),'maximum_clique')


def domi(net):
    def min_weighted_dominating_set(graph, weight=None):
    
        # min cover = min dominating set
        dom_set = set([])
        cost_func = dict((node, nd.get(weight, 1)) \
                         for node, nd in graph.nodes_iter(data=True))
    
        vertices = set(graph)
        sets = dict((node, set([node]) | set(graph[node])) for node in graph)
    
        def _cost(subset):
            """ Our cost effectiveness function for sets given its weight
            """
            cost = sum(cost_func[node] for node in subset)
            return cost / float(len(subset - dom_set))
    
        while vertices:
            # find the most cost effective set, and the vertex that for that set
            dom_node, min_set = min(sets.items(),
                                    key=lambda x: (x[0], _cost(x[1])))
            alpha = _cost(min_set)
    
            # reduce the cost for the rest
            for node in min_set - dom_set:
                cost_func[node] = alpha
    
            # add the node to the dominating set and reduce what we must cover
            dom_set.add(dom_node)
            del sets[dom_node]
            vertices = vertices - min_set
        return dom_set
    return setSize(min_weighted_dominating_set(net),net.number_of_nodes(),'dominating_set')

@to_undirected
def circuit(net):
    return ((net.number_of_edges()-net.number_of_nodes()+nx.number_connected_components(net),'circuit_rank'),)

@to_directed
def circ(net):
    cycles = nx.simple_cycles(net) 
    circ = max(map(lambda c : len(c),cycles))
    print ((circ,'circumference'),)
    return ((circ,'circumference'),)
       
def matching(net):
    return setSize(nx.maximal_matching(net),net.number_of_edges(),'maximal_matching')   

@to_undirected
def vertex_cov(net):
    def min_weighted_vertex_cover(graph, weight=None):
        weight_func = lambda nd: nd.get(weight, 1)
        cost = dict((n, weight_func(nd)) for n, nd in graph.nodes(data=True))
    
        # while there are edges uncovered, continue
        for u,v in graph.edges_iter():
            # select some uncovered edge
            min_cost = min([cost[u], cost[v]])
            cost[u] -= min_cost
            cost[v] -= min_cost
    
        return set(u for u in cost if cost[u] == 0) 
    return setSize(min_weighted_vertex_cover(net),net.number_of_nodes(),'vertex_cover')


def edgebet(net):
    return distri(nx.edge_betweenness(net, normalized = True).values(),'betweenness')

def edgeflow(net):
    return distri(nx.edge_current_flow_betweenness_centrality(net, normalized = True).values(),'edge_information_centrality')

def edgeload(net):
    return distri(nx.edge_load(net).values(),'edgeload')
     

def assort(net):
    return ((nx.degree_assortativity_coefficient(net),'assortativity'),)

@to_undirected
def commun(net):
    dist = nx.communicability_exp(net).values()
    communicability = list(it.chain.from_iterable([dict_of_length.values() for dict_of_length in dist]))
    return distri(communicability,'communicability')

@to_undirected
def bipart(net):
        import scipy.linalg
        nodelist = net.nodes() # ordering of nodes in matrix
        A = nx.to_numpy_matrix(net,nodelist)
        # convert to 0-1 matrix
        A[A!=0.0] = 1
        expA = scipy.linalg.expm(A)
        chA = scipy.linalg.coshm(A)
        return ((np.trace(chA)/np.trace(expA),'bipartitivity'),)
    
    
def overwriteXML(path, nameglobal,net):
    writeXML(path, nameglobal,net,True)

#@profile   
def writeXML(path, nameglobal,net,override = False):
    filename = path.replace(path.split(".")[-1],"xml")
    
    try :
        parser = xml.XMLParser(remove_blank_text=True)
        netfile = xml.parse(filename, parser).getroot()

    except: 
        netfile = xml.Element(nameglobal)
    if override :
        netfile = xml.Element(nameglobal)
        
    def add_sub(datas):
        for value,name in datas(net) :
            if netfile.find(name) is None :
                sub = xml.SubElement(netfile,name)
                sub.attrib['value'] = str(value)


        
    add_sub(nodes)
    add_sub(edges)
    add_sub(dirige)
    add_sub(edge_reciprocity)
    add_sub(prop_edges)
    add_sub(comp)
    add_sub(circuit)
    #add_sub(circ)
    add_sub(communities)
    add_sub(ball)
    add_sub(degrees)
    add_sub(distances)
    add_sub(bala)
    add_sub(harary)
    add_sub(wiener)
    add_sub(effi)
    add_sub(radiality)
    add_sub(core)
    add_sub(clustering)
    add_sub(neighdeg)
    add_sub(hits)
    add_sub(eigen)
    add_sub(pagerank)
    add_sub(close_center)
    add_sub(between_center)
    #add_sub(flow_center)
    #add_sub(flow_between)
    #add_sub(load_center)
    #add_sub(com_center)
    #add_sub(com_bet)
    add_sub(trans)
    add_sub(center)
    add_sub(peri)
    add_sub(eccc)
    add_sub(rad)
    #add_sub(vit)
    add_sub(diam)
    add_sub(lapl_spect)
    add_sub(adja_spect)
    add_sub(ramsey)
    add_sub(domi)
    add_sub(matching)
    add_sub(vertex_cov)
    add_sub(assort)
    add_sub(edgebet)
    #add_sub(edgeflow)
    #add_sub(edgeload)
    add_sub(commun)
    add_sub(bipart)
    
    file1 = open(filename, 'w')
    xml.ElementTree(netfile).write(file1, pretty_print=True)
    file1.close()

    
def parseXML(file1,values):
    parser = xml.XMLParser(remove_blank_text=True)
    rootElement = xml.parse(file1.replace(".gml",".xml"), parser).getroot()
    for node in rootElement.iter():
        if node.tag not in values :
            values[node.tag] = [float(node.attrib.get('value','1'))]
        else :
            values[node.tag].append(float(node.attrib.get('value')))

def corr(xt,yt,file3) :
        x= np.array(xt)
        y =yt
        m2, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        #print m2,
        print r_value, 
        print "####",
        file3.write(str(r_value)+";")

def centrality(net):
    values ={}
    close = nx.closeness_centrality(net, normalized= True)
    eigen = nx.eigenvector_centrality_numpy(net)
    page = nx.pagerank(net)
    bet = nx.betweenness_centrality(net,normalized= True)
    flow_c = nx.current_flow_closeness_centrality(net,normalized= True)
    flow_b = nx.current_flow_betweenness_centrality(net,normalized= True)
    load = nx.load_centrality(net, normalized = True)
    com_c = nx.communicability_centrality(net)
    com_b = nx.communicability_betweenness_centrality(net, normalized= True)
    degree = net.degree()
    
    file3 = open("bl.csv",'w')
    for xt in [bet,load,degree,page,flow_b,com_c,com_b,eigen,close,flow_c]:#[impo,bet,flow_b,load,com_c,com_b] :
        for yt in [bet,load,degree,page,flow_b,com_c,com_b,eigen,close,flow_c]:#[impo,bet,flow_b,load,com_c,com_b] :
            corr(xt.values(),yt.values(),file3)
        print
        file3.write("\n")
    file3.close()
    #plt.plot(x,y, 'o')
    #plt.plot(x, m*x + c, 'r', label='Fitted line')
    #plt.show()
    #for key,item in close.iteritems() :
        #values[key] = [impo.get(key),bet.get(key),flow_b.get(key), load.get(key),com_c.get(key),com_b.get(key)]
        
    return values

def edge_centrality(net):
    values ={}
    
    bet = nx.edge_betweenness(net,normalized= True)
    flow = nx.edge_current_flow_betweenness_centrality(net,normalized= True)
    load = nx.edge_load(net)
    com = nx.communicability(net)
    bet_list =[]
    flow_list = []
    load_list = []
    com_list = []
    for edge,value in bet.iteritems() :
        origin,end = edge
        value_flow = max(flow.get(edge),flow.get((end,origin)))
        values[edge] = [value,value_flow,load.get(edge),com.get(origin).get(end)]
        bet_list.append(value)
        flow_list.append(value_flow)
        load_list.append(load.get(edge))
        com_list.append(com.get(origin).get(end))
    file3 = open("bl.csv",'w')
    for xt in [bet_list,load_list,flow_list,com_list] :
        for yt in [bet_list,load_list,flow_list,com_list] :
            corr(xt,yt,file3)
        print
        file3.write("\n")
    file3.close()
    return values
    
def normalize(array):
    return (array - np.mean(array))/np.std(array)
def pca_ici(glist):
    pcanode1= mdp.nodes.PCANode(output_dim=4)
    values ={}
    current_path = "../../data" 
    for name in glist :
        print name 
        parseXML(current_path + "/" + name+"/"+name+".xml",values)    
        
    print values
    matrixvalues =[]
    for key, item in values.iteritems() :
        if len(item) == len(glist) :
            print key
            matrixvalues.append(normalize(np.array(item)))
    matrixvalues = np.array(matrixvalues).transpose()
    
    #pcanode1.train(matrixvalues)          
    #pcanode1.stop_training()
    #print(pcanode1.explained_variance)        
    #v = pcanode1.get_projmatrix() 
    #print(v)
    
    pcar = pcanode1.execute(matrixvalues)
    #Graph the results
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(pcar[:10,0], pcar[:10,1], 'bo')
    ax.plot(pcar[10:,0], pcar[10:,1], 'ro')

#Show variance accounted for
    ax.set_xlabel((pcanode1.d[0]))
    ax.set_ylabel((pcanode1.d[1]))
    print pcanode1.explained_variance
    print pcanode1.get_projmatrix()
    plt.show()
    
    
    file4 = open("bla.csv",'w')
    for i in pcar :
        for j in i :
            file4.write(str(j))
            file4.write(";")
        file4.write("\n") 
    

def correlation_edge_centrality(name):
        current_path = "../../data" 
        network = nx.read_gml(current_path + "/" + name+"/"+name+".gml")
        edge_centrality(network)
          
if __name__ == '__main__':
    #["dolphins","Consulting", "Freemans","karate","lesmis","Manufacturing","polbooks","southern_club"]
    
    #correlation_edge_centrality("karate")
    
    current_path = "../../data/gexf/" 
    #name ="politicsuk-twitter-follows"
    #name ="karate"
    #network = nx.read_gml(current_path + "/" + name+"/"+name+".gml")
    #overwriteXML(current_path + "/" + name+"/"+name+".gml",name, network)
    #network = nx.read_gexf(current_path + "/" + name+"/"+name+".gexf")
    #centrality(network)
    #writeXML(current_path + "/" + name+"/"+name+".gexf",name, network)

    
    import os
    for f in os.listdir(current_path) :
        import StringIO
        l = StringIO.StringIO('''<xs:schema elementFormDefault="qualified" targetNamespace="http://www.gexf.net/1.1draft"><xs:include schemaLocation="data.xsd"/><xs:include schemaLocation="dynamics.xsd"/><xs:include schemaLocation="hierarchy.xsd"/><xs:include schemaLocation="phylogenics.xsd"/><xs:import schemaLocation="viz.xsd"/><xs:element name="gexf" type="ns1:gexf-content"/><xs:complexType name="gexf-content"><xs:annotation><xs:documentation>Tree</xs:documentation></xs:annotation><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element ref="ns1:meta"/><xs:element ref="ns1:graph"/></xs:choice><xs:attribute name="version" use="required"><xs:simpleType><xs:restriction base="xs:string"><xs:enumeration value="1.1"/></xs:restriction></xs:simpleType></xs:attribute><xs:attribute name="variant" type="xs:string"/></xs:complexType><xs:element name="meta" type="ns1:meta-content"/><xs:element name="graph" type="ns1:graph-content"/><xs:complexType name="meta-content"><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element ref="ns1:creator"/><xs:element ref="ns1:keywords"/><xs:element ref="ns1:description"/></xs:choice><xs:attribute name="lastmodifieddate" type="xs:date"/></xs:complexType><xs:element name="creator" type="xs:string"/><xs:element name="keywords" type="xs:string"/><xs:element name="description" type="xs:string"/><xs:complexType name="nodes-content"><xs:sequence><xs:element minOccurs="0" maxOccurs="unbounded" ref="ns1:node"/></xs:sequence><xs:attribute name="count" type="xs:nonNegativeInteger"/></xs:complexType><xs:element name="node" type="ns1:node-content"/><xs:complexType name="edges-content"><xs:sequence><xs:element minOccurs="0" maxOccurs="unbounded" ref="ns1:edge"/></xs:sequence><xs:attribute name="count" type="xs:nonNegativeInteger"/></xs:complexType><xs:element name="edge" type="ns1:edge-content"/><xs:simpleType name="defaultedgetype-type"><xs:annotation><xs:documentation>Datatypes</xs:documentation></xs:annotation><xs:restriction base="xs:string"><xs:enumeration value="directed"/><xs:enumeration value="undirected"/><xs:enumeration value="mutual"/></xs:restriction></xs:simpleType><xs:simpleType name="edgetype-type"><xs:restriction base="xs:string"><xs:enumeration value="directed"/><xs:enumeration value="undirected"/><xs:enumeration value="mutual"/></xs:restriction></xs:simpleType><xs:simpleType name="id-type"><xs:union memberTypes="xs:string xs:integer"/></xs:simpleType><xs:simpleType name="idtype-type"><xs:restriction base="xs:string"><xs:enumeration value="integer"/><xs:enumeration value="string"/></xs:restriction></xs:simpleType><xs:simpleType name="mode-type"><xs:restriction base="xs:string"><xs:enumeration value="static"/><xs:enumeration value="dynamic"/></xs:restriction></xs:simpleType><xs:simpleType name="weight-type"><xs:restriction base="xs:float"/></xs:simpleType></xs:schema>
        ''')
        xmlschema_doc = xml.parse(l)
        xmlschema = xml.XMLSchema(xmlschema_doc)
        doc = xml.parse(current_path + f)
        xmlschema.assertValid(doc)
        
        network = nx.read_gexf(current_path + f)
        name = f.split("-")[2:5]
        writeXML(current_path +f,name, network)
    '''    
            n=0
            network=None
           # if ".gml" in name :  
                #network = nx.read_gml(current_path+"/"+name) 
                #n=1
            if "jazz.net" in name or ".NET" in name or "PGPgiantcompo.net" in name :
                print name
                network = nx.read_pajek(current_path+"/"+name)
                print network.number_of_nodes()
                print network.is_directed()
                nx.write_gml(network, current_path+"/"+name.replace(".net",".gml")) 
            
            if "sp_data_school_day_2.gexf" in name :
                network = nx.read_gexf(current_path+"/"+name)
                #nx.write_gml(network,current_path+"/"+name.replace("sp_data_school_day_2.gexf","school_1.gml"))
                nx.read_gml(current_path+"/"+name.replace("sp_data_school_day_2.gexf","school_1.gml"))
                             
            if ".txt" in name: 
                print name
                network = nx.read_edgelist(current_path+"/"+name, data=(('weight',float),))
                print network.number_of_nodes()
                print network.is_directed()
                nx.write_gml(network, current_path+"/verif/"+name.replace(".txt",".gml")) 
                #n=1
            #if list_of_networks.has_key(network.number_of_nodes()) :
             #       print "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
             #       print name
             #       print list_of_networks[network.number_of_nodes()]
             #       print network.number_of_nodes()
            if n==1 :
                pass
                #print name+" "+str(len(network))+" DIRECTED "+ str(network.is_directed())  
                
               #if not network.is_directed() :    
                    #os.rename(current_path+"/"+name,current_path+"/verif/"+name)
                #else :
                    #os.rename(current_path+"/"+name,current_path+"/directed/"+name)
            
        

            print name  
            if True :
                network = nx.read_gml(current_path + "/" + name+"/"+name+".gml") 
                if network.number_of_nodes() < 250 :
                    writeXML(current_path + "/" + name+"/"+name+".gml",name, network) 
                    #os.rename(current_path + "/" + name, current_path + "/gml/" + name)
                else :
                    #os.rename(current_path + "/" + name, current_path + "/gros/" + name) 
                    pass
'''
    


            
           

