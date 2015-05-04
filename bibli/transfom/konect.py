'''
Created on 13 mars 2014

@author: davidfourquet
'''

if __name__ == '__main__':
    from lxml import html
    from lxml import etree
    import os
    import tarfile
    import  urllib
    import networkx as nx
    import gexf
    import random
    
    def bipartite_konect(graph_init,name,type0,type1,trois=None,quatre=None):
        graph = graph_init
        graph.name = name
        for line in (open(name+"/out."+graph.name).read().splitlines()) :
            if not line.startswith("%") :
                linesplit = [element for element in line.split(" ") if element != '']
                graph.add_node(type0+"-"+linesplit[0], type = type0)
                graph.add_node(type1+"-"+linesplit[1], type = type1)
                attributes = {}
                if trois : 
                    try :
                        attributes.update({trois : int(linesplit[2])})
                    except :
                        attributes.update({trois : float(linesplit[2])})
                if quatre : 
                    try :
                        attributes.update({quatre : int(linesplit[3])})
                    except :
                        attributes.update({quatre : float(linesplit[3])})
                graph.add_edge(type0+"-"+linesplit[0], type1+"-"+linesplit[1],**attributes)
        return write(graph,graph.name+".gexf")
    
    def konect(graph_init,name,trois = None, quatre = None):
        graph = graph_init
        graph.name = name
        for line in (open(name+"/out."+graph.name).read().splitlines()) :
            if not line.startswith("%") :
                linesplit = [element for element in line.split(" ") if element != '']
                attributes = {}
                if trois : 
                    try :
                        attributes.update({trois : int(linesplit[2])})
                    except :
                        attributes.update({trois : float(linesplit[2])})
                if quatre : 
                    try :
                        attributes.update({quatre : int(linesplit[3])})
                    except :
                        attributes.update({quatre : float(linesplit[3])})
                graph.add_edge(int(linesplit[0]), int(linesplit[1]),**attributes)
        return write(graph,graph.name+".gexf")
        
    def write(net,f):
            name = f.split('.')[-2]
            net.name = name
            if not os.path.exists("files/0-"+name): os.makedirs("files/0-"+name)
            gexf.write_gexf(net, "files/0-"+name+"/"+name+".gexf")
            return net.number_of_nodes(),net.number_of_edges()
            



    
        
    ht = html.parse("http://konect.uni-koblenz.de/networks/")
    liste = list(ht.iter('tr'))
    random.shuffle(liste)
    for network in liste:
            try :
                name = network[9][1][1].get("href").replace("../downloads/","").replace(".tar.bz2","")
            except :
                print "not a network",network[1].text
                continue
            
            nodes_info = int(network[6].text.replace(",",""))
            edges_info = int(network[7].text.replace(",",""))
            directed =  network[3][1][0].get("alt").startswith("Directed")
            bipartite =  network[3][1][0].get("alt").startswith("Bipartite")
            multiple = network[4][1][0].get("alt").startswith("Multiple")
            weighted = " weighted " in network[4][1][0].get("alt") or "Signed" in network[4][1][0].get("alt") or "rating" in network[4][1][0].get("alt")
            
            try : 
                loop_info = False
                loop_info = network[5][0][1][0][0].get("title","").startswith("Loop") 
            except: pass
            try : 
                time_info = False
                time_info = network[5][0][0][0][0].get("title","").startswith("Time")
            except: pass
            
            bip1,bip2 = "",""
            if bipartite :
                w = html.parse("http://konect.uni-koblenz.de/networks/"+name)
                for tr in w.iter("tr") :
                    if tr[0].text == "Vertex type " :
                        bip1,bip2 = tr[1].text.split(",")   
            
            if  not "0-"+name in os.listdir("files") :
                print name,"| directed :",directed,"| bipartite :",bipartite,bip1,bip2,"| multiple :",multiple,"| weighted :",weighted,"| loop :",loop_info,"| time :",time_info 
                if edges_info < 50000000 :
                    
                    """"DOWNLOAD"""""
                    try :
                        if not os.path.exists(name+".tar.bz2") and not os.path.exists(name) :
                            urllib.urlretrieve ("http://konect.uni-koblenz.de/downloads/"+name+".tar.bz2", name+".tar.bz2")
                        print name,"downloaded"
                    except :
                        print name,"not found"
                        continue
                    
                    """"EXTRACT"""""
                    if not os.path.exists(name) :
                        net_file = tarfile.open(name+".tar.bz2").extractall()
                    print name,"extracted"
                    
                    """"GEXFY"""""
                    if directed and (loop_info or multiple) :
                        graph = nx.MultiDiGraph()
                    if not directed and (loop_info or multiple) :
                        graph = nx.MultiGraph()
                    if directed and (not (loop_info or multiple)) :
                        graph = nx.DiGraph()
                    if not directed and (not (loop_info or multiple) ):
                        graph = nx.Graph()
                    
                    options = {} 
                    if weighted : options.update({"trois":"weight"})
                    if time_info : options.update({"quatre":"timestamp"})  
                    if bipartite  :
                        nodes,edges = bipartite_konect(graph,name, bip1, bip2,**options)
                    else :
                        nodes,edges = konect(graph,name,**options)
                    print name,"gexfied"
                    try :
                        os.renames(name, "used/"+name)
                        os.remove(name+".tar.bz2")
                    except: pass
                    
                    if nodes != nodes_info or edges != edges_info :
                        print name,"failed : expected :",nodes_info,edges_info,"found :",nodes,edges
                    print name,"done"
                else :
                    print name,"is big",edges_info
            else :
                try :os.renames("files/"+name, "files/0-"+name)
                except: pass
                print name,"is already present"
            
        
        