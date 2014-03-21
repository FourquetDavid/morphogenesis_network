'''
Created on 17 mars 2014

@author: davidfourquet
'''
import networkx as nx
import gexf
import csv
from lxml import html
import os

 


def getDataFromSnas() :
    
    f = open("snas.csv")
    dictionaries =csv.DictReader(f)
    for dictionary_name_data in dictionaries :
        dict_datas = {"name" : dictionary_name_data["data_name"],
                      "bipartite" :dictionary_name_data["is_bipartite"],
                      "nodetypes" :dictionary_name_data["list_nodetype"],
                      "nbnodes":dictionary_name_data["count_nodetotal"],
                      "nodedatas" :dictionary_name_data["list_nodeattribute"],
                      "multiple" :dictionary_name_data["is_multiplex"],
                      "directed" : dictionary_name_data["is_directed"],
                      "undirected" : dictionary_name_data["is_undirected"],
                      "weighted" : dictionary_name_data["is_edgeweighted"],
                      "signed" : dictionary_name_data["is_edgesigned"],
                      "edgedata" : dictionary_name_data["count_edgetype"],
                      "static" : dictionary_name_data["is_static"],
                      "dynamic" : dictionary_name_data["is_dynamic"]}
        dict_id_datas[int(dictionary_name_data["id"])] = dict_datas

def getDataFromKonect() :
    ht = html.parse("http://konect.uni-koblenz.de/networks/")
    for network in ht.iter('tr'):
            try :
                name = network[9][1][1].get("href").replace("../downloads/","").replace(".tar.bz2","")
            except :
                continue
            
            nodes_info = int(network[6].text.replace(",",""))
            edges_info = int(network[7].text.replace(",",""))
            directed =  network[3][1].get("alt").startswith("Directed")
            bipartite =  network[3][1].get("alt").startswith("Bipartite")
            multiple = network[4][1].get("alt").startswith("Multiple")
            weighted = " weighted " in network[4][1].get("alt")  or "atings" in network[4][1].get("alt")
            signed = "Signed" in network[4][1].get("alt")
            
            try : 
                loop_info = False
                loop_info = network[5][0][1][0].get("title","").startswith("Loop") 
            except: pass
            try : 
                time_info = False
                time_info = network[5][0][0][0].get("title","").startswith("Time")
            except: pass
            
            edge_types =0
            if time_info : edge_types+=1
            if weighted or signed : edge_types+=1
            
            dict_datas = {"name" : name,
                      "bipartite" :bipartite,
                      "nbnodes":nodes_info,
                      "nbedges" : edges_info,
                      "multiple" :multiple or loop_info,
                      "directed" : directed,
                      "weighted" : weighted,
                      "signed" : signed,
                      "edgedata" : edge_types,
                      "dynamic" : False}
            dict_id_datas[name] = dict_datas

def getNetworksDone():
    networks =[]
    networkfile = open("done.csv")
    for line in networkfile.read().splitlines() :
        name = line.split(";",1)[0]
        networks.append(name)
    return networks

def getNetworksProblems():
    networks =[]
    networkfile = open("problems.csv")
    for line in networkfile.read().splitlines() :
        name = line.split(";",1)[0]
        networks.append(name)
    return networks     

def compareDataswithFiles():
    def study(carac) :
        perfect = True
        
        """ si les datas sont absentes"""
        if not expected_datas[carac] :
            print carac,"expected:", expected_datas[carac],"found:"
            expected_datas['csv'] = expected_datas['csv']+str(expected_datas[carac])+",;"
            del expected_datas[carac]
            perfect = False
            return perfect
        
        """ si les datas sont presentes mais incorrectes """
        if expected_datas[carac] == 'false' : expected_datas[carac] = False
        if expected_datas[carac] == 'true' : expected_datas[carac] = True
        
        if expected_datas[carac] != found_datas[carac] :
            print carac,"expected:", expected_datas[carac],"found:", found_datas[carac]
            expected_datas['csv'] = expected_datas['csv']+str(expected_datas[carac])+","+str(found_datas[carac])+";"
            perfect = False
        else :
            """ si les datas sont presentes et correctes """
            expected_datas['csv'] = expected_datas['csv']+str(expected_datas[carac])+";"
        del expected_datas[carac]
        del found_datas[carac]
        return perfect
        
        
        
    networks = getNetworksDone()
    net2 = getNetworksProblems()
    for directory in os.listdir("files") :
        print 'STUDY', directory
        name = directory.split("-",1)[1]
        if os.path.isdir("files/"+directory) and (name not in networks) and (name not in net2) :
            
            try :
                expected_datas = find_expected_datas(directory)
                found_datas = network_description(directory)
                perfect = True
                perfect = study('nbnodes') and perfect
                perfect = study('nbedges') and perfect
                perfect = study("directed") and perfect
                perfect = study("multiple") and perfect
                perfect = study("bipartite") and perfect
                perfect = study("weighted") and perfect
                perfect = study("signed") and perfect
                perfect = study("dynamic") and perfect
                perfect = study("edgedata") and perfect
                print "expected",expected_datas
                print "found",found_datas
                if perfect : 
                    open("done.csv",'a').write(expected_datas['csv']+"\n")
                else :
                    open("problems.csv",'a').write(expected_datas['csv']+"\n")
            except :
                open("problems.csv",'a').write(name+"\n")
            
            
            #cas ou pas de datas
            #cas de datas manquantes
            #cas ou datas differentes
            #cas parfait
            
def find_expected_datas(directory) :
                splitname =directory.split("-")
                try : 
                    number = int(splitname[0])
                    if number == 0:
                        name = '-'.join(splitname[1:])
                        return dict_id_datas[name]
                    else :
                        return  dict_id_datas[number]
                except : return None        
        
    
    
def network_description(directory):
    name = directory.split("-",1)[1]
    net = gexf.read_gexf("files/"+directory+"/"+name+".gexf")
    
    network_datas ={}
    
    def is_dynamic(): 
        dynamic = False
        for _,data in net.nodes(data = True) :
            for _,v in data.iteritems() :
                if isinstance(v, list) :
                    dynamic = True
                    break
            if dynamic : break
        for _,_,data in net.edges(data = True) :
            for _,v in data.iteritems() :
                if isinstance(v, list) :
                    dynamic = True
                    break
            if dynamic : break
        network_datas['dynamic'] = dynamic
    
    def node_types():
        from sets import Set
        types = Set()
        for _,data in net.nodes(data = True) :
            for type_node in data :
                types.add(type_node)
        network_datas['node_types'] = list(types)
        
    def edge_types():
        from sets import Set
        types = Set()
        keys = Set()
        if isinstance(net, nx.MultiGraph) or isinstance(net, nx.MultiDiGraph)  :
            for source,target,key,data in net.edges(data = True,keys = True) :
                keys.add(key)
                for type_edge in data :
                    types.add(type_edge)
        else :
            for source,target,data in net.edges(data = True) :
                for type_edge in data :
                    types.add(type_edge)
        types.remove("id")
        network_datas['edge_types'] = list(types)
        network_datas['edgedata'] = types.__len__()
        if 3 in list(keys) :
            network_datas['edge_keys'] = len(keys)
        else :
            network_datas['edge_keys'] = list(keys)
                
            
            
    def is_bipartite():
        from sets import Set
        is_bipartite = True
        node_types = Set()
        
        for _,data in net.nodes(data = True) :
            if not data.get("type",False) :
                is_bipartite = False
                break
            else :
                node_types.append(data[type])
        network_datas['bipartite'] = is_bipartite
    
    def is_directed():
        network_datas["directed"] = isinstance(net, nx.DiGraph) or isinstance(net, nx.MultiDiGraph)
    
    def is_multiple():
        network_datas["multiple"] = isinstance(net, nx.MultiGraph) or isinstance(net, nx.MultiDiGraph)
    
    def is_weighted():
        weighted = True
        signed = False
        for e in net.edges( data = True) :
            _,_,data =e
            if  not data.get('weight',None) :
                weighted = False
                break
            if data['weight'] < 0 :
                signed = True
                break
        network_datas["signed"] = signed
        network_datas["weighted"] = weighted
        
    def size():
        network_datas["nbnodes"] = len(net)
        network_datas["nbedges"] = net.size()
    
    is_bipartite()
    is_directed()
    is_dynamic()
    is_multiple()
    is_weighted()
    edge_types()
    node_types()
    size()
    return network_datas
    
dict_id_datas ={}   
getDataFromSnas() 
getDataFromKonect()
compareDataswithFiles() 


def try_multi(net):
        from sets import Set
        edge_types = Set()
        if net.is_instance(nx.Graph) or net.is_instance(nx.DiGraph) :
            return False,net
        
        else :
            for source,target,key in net.edges(keys= True) :
                edge_types.add(key)
        if len(edge_types) == 1 :
            if net.is_instance(nx.MultiGraph) :
                net = nx.Graph(net)
            if net.is_instance(nx.MultiDiGraph) :
                net = nx.DiGraph(net)  
            return False,net
        return True,net 
def try_unweighted(net): 
        weighted = False
        for e in net.edges( data = True) :
            _,_,data =e
            if  not data['weight'] :
                break
            if data['weight'] != 1.0 :
                print 'weighted'
                print e
                weighted = True
                break
        if not weighted :
            print "unweighted"
            if isinstance(net, nx.MultiDiGraph) or isinstance(net, nx.MultiGraph) :
                for source,target,key in net.edges(keys=True) :
                    del net.edge[source][target][key]['weight']
            else :
                for source,target in net.edges() :
                    del net.edge[source][target]['weight']
        return weighted,net             
def try_undirected(net): 
        net2 = net
        if isinstance(net, nx.MultiDiGraph) :
            undirected = True
            for source,target,key,data in net.edges(data = True,keys = True) :
                if not net.has_edge(target,source,key =key) or data['weight'] != net[target][source][key]['weight']:
                    print "multidirected"
                    undirected = False
                    break
            if undirected :
                print "multiundirected"
                net2 = nx.MultiGraph(net)
            
        else :
            undirected = True
            for source, target, data in net.edges(data = True) :
                if not net.has_edge(target,source) or data['weight'] != net[target][source]['weight']:
                    print "directed"
                    print source,target
                    undirected = False
                    break
            if undirected :
                print "undirected"
                net2 = nx.MultiGraph(net)
        return net2    
def is_signed(net):
        signed = True
        for e in net.edges( data = True) :
            _,_,data =e
            if  not data['weight'] :
                signed = False
                break
            if data['weight'] != 1.0 and data['weight'] != -1.0 :
                signed = False
                break
        
        return signed    