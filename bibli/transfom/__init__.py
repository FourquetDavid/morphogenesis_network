import networkx as nx
import os
import igraph as ig

def write(net,f):
    name = f.split('.')[-2]
    net.name = name
    if not os.path.exists("files/"+name): os.makedirs("files/"+name)
    nx.write_gexf(net, "files/"+name+"/"+name+".gexf")
    nx.write_gml(net, "files/"+name+"/"+name+".gml")
    igraphnet = ig.Graph.Read_GML("files/"+name+"/"+name+".gml")
    write_pajek(net,"files/"+name+"/"+name+".net")
    igraphnet.save("files/"+name+"/"+name+".graphml",format="graphml")
    #nx.write_pajek(net, "files/"+name+"/"+name+".net")
    nx.write_dot(net, "files/"+name+"/"+name+".dot")
    
    nx.write_adjlist(net,"files/"+name+"/"+name+".adjlist")
    edge = open("files/"+name+"/"+name+".adjlist",'r').readlines()[2:]
    open("files/"+name+"/"+name+".adjlist",'w').writelines(edge)
    if net.edges(data=True)[0][2]:
        nx.write_weighted_edgelist(net,"files/"+name+"/"+name+".edgelist")
    else :     
        nx.write_edgelist(net,"files/"+name+"/"+name+".edgelist",data = False)
    
    print "original :"+name,
    print net.number_of_nodes(),
    print net.number_of_edges()

def verif(f):
    name = f.split('.')[-2]
    net = nx.read_gexf("files/"+name+"/"+name+".gexf")
    print "copied :",
    print net.number_of_nodes(),
    print net.number_of_edges()

def suivi(net,f):
    write(net,f)
    verif(f)
    os.rename(f,"used/"+f)
    
def EIES(name):
    graph = nx.MultiDiGraph()
    graph.name = "EIES"
    def attribute() :
        i=0
        for line in open(name+".ATT").read().splitlines() :
    
            def prof(number) :    
                d =  {1 : "sociology", 2 : "anthropology", 3 : "mathematics/statistics", 4 : "psychology"}         
                return d[int(number)]
            citations,type_research = [number for number in line.split(" ") if number != '']
            
            graph.add_node(i, dict(number_of_citations = int(citations), discipline = prof(type_research) ))
            i=i+1
    attribute()
    
    print graph.node
    def message() :
        subgraph = nx.DiGraph()
        subgraph.name = name+"-messages"
        subgraph.add_nodes_from(graph.nodes(data=True))
        source=0
        for line in open("messages.asc").read().splitlines() :
            target = 0
            for number_of_messages in [number for number in line.split(" ") if number != ''] :
                if int(number_of_messages) != 0 :
                    graph.add_edge(source,target, key = 'number_of_messages_sent', weight = int(number_of_messages))
                    subgraph.add_edge(source, target, weight = int(number_of_messages))
                target = target+1
            source = source+1
        return subgraph
    
    def time(number_time):
        
        def type_rel(number) : 
            d =  {1 : "do_not_know_the_other", 2 : "heard_about_the_other,did_not_meet_him/her", 3 : "have_met_the_other", 4 :"friend" }         
            return d[int(number)]
        source=0
        for line in open(name +"."+ str(number_time)).read().splitlines() :
            target = 0
            for number_of_messages in [number for number in line.split(" ") if number != ''] :
                if int(number_of_messages) != 0 : 
                    keyhere = type_rel(int(number_of_messages))
                    if not graph.get_edge_data(source, target, keyhere , False) :
                        graph.add_edge(source,target, key = keyhere,start = number_time, end = number_time) 
                    else :
                        graph[source][target][keyhere]['end'] = number_time
                    
                target = target+1
            source = source+1
        
            
    def subgraph(number_time):
        subgraph = nx.DiGraph()
        subgraph.name = name+"-"+str(number_time)
        subgraph.add_nodes_from(graph.nodes(data=True))
        subgraph.add_edges_from([ (debut,fin, {"relation_type" : keyd}) for debut,fin,keyd,dico in graph.edges(data=True,keys = True) 
                                 if dico.get('start',None)<=number_time<=dico.get('end',None)])
        
        return subgraph
    
    graph_message = message()
    time(1)
    time(2)
    graph_1 = subgraph(1)
    graph_2 = subgraph(2)
    graph.mode = 'dynamic'
    write(graph_1,name+"-1.gexf")
    write(graph_2,name+"-2.gexf")
    write(graph_message,name+"-messages.gexf")
    if not os.path.exists("files/"+name): os.makedirs("files/"+name)
    nx.write_gexf(graph, "files/"+name+"/"+name+".gexf")
    print graph.node
    print graph.edge[0]
    print graph_1.edge[0]
    print graph_2.edge[0]     
def kapf(name):
    graph = nx.MultiDiGraph()
    graph.name = name
    def attribute() :
        i=0
        for line in open(name+"a_stat.dat").read().splitlines() :
    
            def prof(number) :    
                d =  {1 : "head tailor" , 2 :"cutter", 3 :"line 1 tailor", 4:"button machiner",
                      5:"line 3 tailor", 6:"ironer",7:"cotton boy",8:"line 2 tailor"}         
                return d[int(number)]
            type_research = line
            
            graph.add_node(i,  job = prof(type_research) )
            i=i+1
    attribute()
    
    print graph.node
    def message() :
        source=0
        for line in open("messages.asc").read().splitlines() :
            target = 0
            for number_of_messages in [number for number in line.split(" ") if number != ''] :
                if int(number_of_messages) != 0 :
                    graph.add_edge(source,target, key = 'number_of_messages_sent', weight = int(number_of_messages))
                target = target+1
            source = source+1
    
    
    def time(number_time,type_rel,reduced_type):
        source=0
        for line in open(name +reduced_type+ str(number_time)+".dat").read().splitlines() :
            target = 0
            for relate in [number for number in line.split(" ") if number != ''] :
                if int(relate) != 0 : 
                    keyhere = type_rel
                    if not graph.get_edge_data(source, target, keyhere , False) :
                        graph.add_edge(source,target, key = keyhere,start = number_time, end = number_time) 
                    else :
                        graph[source][target][keyhere]['end'] = number_time
                target = target+1
            source = source+1
            
    def subdigraph(number_time,key):

        subgraph = nx.DiGraph()
        subgraph.name = name+"-"+key+str(number_time)
        subgraph.add_nodes_from(graph.nodes(data=True))
        subgraph.add_edges_from([ (debut,fin) for debut,fin,keyd,dico in graph.edges(data=True,keys = True) 
                                 if (keyd == key) & (dico.get('start',None)<=number_time<=dico.get('end',None))])
        
        return subgraph
    
    def subgraph(number_time,key):

        subgraph = nx.Graph()
        subgraph.name = name+"-"+key+str(number_time)
        subgraph.add_nodes_from(graph.nodes(data=True))
        subgraph.add_edges_from([ (debut,fin ) for debut,fin,keyd,dico in graph.edges(data=True,keys = True) 
                                 if (keyd == key) & (dico.get('start',None)<=number_time<=dico.get('end',None))])
        
        return subgraph
    time(1,"instrumental interactions","ti")
    time(2,"instrumental interactions","ti")
    time(1,"sociational interactions","ts")
    time(2,"sociational interactions","ts")
    graph_1_ti = subdigraph(1,"instrumental interactions")
    graph_2_ti = subdigraph(2,"instrumental interactions")
    graph_1_tr = subdigraph(1,"sociational interactions")
    graph_2_tr = subdigraph(2,"sociational interactions")
    write(graph_1_ti,name+"-instrumental-interactions-1.gexf")
    write(graph_2_ti,name+"-instrumental-interactions-2.gexf")
    write(graph_1_tr,name+"-sociational-interactions-1.gexf")
    write(graph_2_tr,name+"-sociational-interactions-2.gexf")
    if not os.path.exists("files/"+name): os.makedirs("files/"+name)
    nx.write_gexf(graph, "files/"+name+"/"+name+".gexf")
    print graph.node
    print graph.edge[0]
    print graph_1_tr.edge[0]
    print graph_1_ti.edge[0]
    print graph_2_tr.edge[0]
    print graph_2_ti.edge[0]     
def twitter (name):
    realname = name+"-twitter"
    graph = nx.MultiDiGraph()
    graph.name = realname
    
    
    
    graph.add_nodes_from(open(name+"/"+name+".ids").read().splitlines())
    for line in open(name+"/"+name+".communities").read().splitlines() :
        community = line.split(": ")
        community_name = community[0]
        names = community[1].split(",")
        for named in names :
            graph.node[named]['community'] = community_name
            graph.node[named]['listmerged500'] = {}
            graph.node[named]['lists500'] = {}
            graph.node[named]['tweets500'] = {}
    def add_typed_edge(typedg):
        for line in open(name+"/"+name+"-"+typedg+".mtx").read().splitlines()[1:] :
            debut,fin,size = line.split(" ")
            graph.add_edge(debut,fin,key = typedg, weight = float(size))
    
    add_typed_edge("followedby")
    add_typed_edge("follows")
    add_typed_edge("retweetedby")
    add_typed_edge("retweets")
    add_typed_edge("mentionedby")
    add_typed_edge("mentions")
    
    def feature(namefeature):
        dictfeatures ={}
        i=0
        for line in open(name+"/"+name+"-"+namefeature+".features").read().splitlines():
            #print line
            dictfeatures[i] = line#.decode("utf-8","mixed")
            #print line.decode("utf-8")
            i=i+1   
        for line in open(name+"/"+name+"-"+namefeature+".mtx").read().splitlines()[1:] :
            feat,node,weight = line.split(" ")
            graph.node[node][namefeature][dictfeatures[int(feat)]] = float(weight)
    
    feature("listmerged500")
    feature("lists500")
    feature("tweets500")
       
    graph = nx.convert_node_labels_to_integers(graph)
    #print graph.nodes(data= True)
    def subgraph(complement):
        subgraph = nx.DiGraph()
        subgraph.name = realname+complement
        subgraph.add_nodes_from(graph.nodes(data=True))
        subgraph.add_edges_from([ (debut,fin,dico) for debut,fin,keyd,dico in graph.edges(data=True,keys = True) if keyd==complement])
        return subgraph
    
    graph_follows = subgraph("follows")
    graph_retweets = subgraph("retweets")
    graph_mentions = subgraph("mentions")
    print graph_follows.edge
    write(graph_follows,realname+"-follows.gexf")
    write(graph_retweets,realname+"-retweets.gexf")
    write(graph_mentions,realname+"-mentions.gexf") 
    if not os.path.exists("files/"+realname): os.makedirs("files/"+realname)
    nx.write_gexf(graph, "files/"+realname+"/"+realname+".gexf")   

def lazega():
    name = "LazegaLawyers"
    graph = nx.MultiDiGraph()
    graph.name = name
    def attribute() :
        i=0
        for line in open(name+"/"+"ELattr.dat").read().splitlines() :      
            def stat(number) :    
                d =  {1 : "partner" , 2 :"associate"}         
                return d[int(number)]
            def gen(number) :    
                d =  {1 : "male" , 2 :"woman"}         
                return d[int(number)]
            def off(number) :    
                d =  {1 : "Boston" , 2 :"Hartford",3:"Providence"}         
                return d[int(number)]
            def prac(number) :    
                d =  {1 : "litigation" , 2 :"corporate"}         
                return d[int(number)]
            def sch(number) :    
                d =  {1 : "harvard, yale" , 2 :"ucon",3:"other"}         
                return d[int(number)]
            seniority,status,gender,office,years,age,practice,school = [number for number in line.split(" ") if number != '']
            
            graph.add_node(i,  seniority = int(seniority), status = stat(status),gender =gen(gender),
                           office = off(office), years_within_the_firm = int(years),age = int(age), 
                           practice =prac(practice),law_scool = sch(school) )
            i=i+1
    attribute()
    
    def message(typed,exp_type) :
        source=0
        for line in open(name+"/"+"EL"+typed+".dat").read().splitlines() :
            target = 0
            for number_of_messages in [number for number in line.split(" ") if number != ''] :
                if int(number_of_messages) != 0 :
                    graph.add_edge(source,target, key = exp_type)
                target = target+1
            source = source+1
    def subdigraph(key):

        subgraph = nx.DiGraph()
        subgraph.name = name+"-"+key
        subgraph.add_nodes_from(graph.nodes(data=True))
        subgraph.add_edges_from([ (debut,fin) for debut,fin,keyd,_ in graph.edges(data=True,keys = True) 
                                 if keyd == key])
        
        return subgraph
    
    message("adv","advice")
    message("friend","friend")
    message("work","work")
    adv=subdigraph("advice")
    fr=subdigraph("friend")
    wo=subdigraph("work")
    print graph.node
    print graph.edge
    write(adv,name+"-advice.gexf")
    write(fr,name+"-friend.gexf")
    write(wo,name+"-work.gexf") 
    if not os.path.exists("files/"+name): os.makedirs("files/"+name)
    nx.write_gexf(graph, "files/"+name+"/"+name+".gexf")
def stu98():
    name = "stu98"
    graph = nx.MultiDiGraph()
    graph.name = name
    
    
    def attribute() :
        i=0
        for line in open(name+"/stud98.txt").read().splitlines() :
            def gen(number) :    
                d =  {1 : "male" , 2 :"female"}         
                return d[int(number)]
            def prog(number) :    
                d =  {1 : "regular 4-year program" , 2 :"2-year program"}         
                return d[int(number)]
            def smo(number) :    
                d =  {1 : "no" , 2 :"yes, at parties (social)",3:"1-3 cigarettes per day",4:"4-10 cigarettes per day"
                      ,5:"more than 10 p.d.", 99 : "missing"}         
                return d[int(number)]
            _,gender,years,program,smoking = [number for number in line.split("\t") if number != '']
            
            graph.add_node(i,  gender = gen(gender),age = int(years), program = prog(program),somking = smo(smoking) )
            i=i+1
    attribute()
    
    print graph.node
    def message() :
        source=0
        for line in open("messages.asc").read().splitlines() :
            target = 0
            for number_of_messages in [number for number in line.split(" ") if number != ''] :
                if int(number_of_messages) != 0 :
                    graph.add_edge(source,target, key = 'number_of_messages_sent', weight = int(number_of_messages))
                target = target+1
            source = source+1
    

    def time(number_time):
        def type_rel(number) : 
            d =  {1 : "Best friendship", 2 : "Friendship", 3 : "Friendly relationship", 4 :"Neutral relationship",5:"Troubled relationship" }         
            return d[int(number)]
        source=0
        for line in open(name+"/"+name +"t"+ str(number_time)+".txt").read().splitlines() :
            target = 0
            for number_of_messages in [number for number in line.split("\t") if number != ''] :
                if int(number_of_messages) not in [0,6,8,9] : 
                    keyhere = type_rel(int(number_of_messages))
                    if not graph.get_edge_data(source, target, keyhere , False) :
                        graph.add_edge(source,target, key = keyhere,start = number_time, end = number_time) 
                    else :
                        graph[source][target][keyhere]['end'] = number_time
                target = target+1
            source = source+1
    
    def subgraph(number_time):
        subgraph = nx.DiGraph()
        subgraph.name = name+"-"+str(number_time)
        subgraph.add_nodes_from(graph.nodes(data=True))
        subgraph.add_edges_from([ (debut,fin, {keyd : 1}) for debut,fin,keyd,dico in graph.edges(data=True,keys = True) 
                                 if dico.get('start',float("-inf"))<=number_time<=dico.get('end',float("+inf"))])
        
        return subgraph

    time(0);t0 = subgraph(0)
    time(2);t2 = subgraph(2)
    time(3);t3 = subgraph(3)
    time(5);t5 = subgraph(5)
    time(6);t6 = subgraph(6)
    print graph.node
    print graph.edge[0]


def read_pajek(path,encoding='UTF-8'):
    path2 = open(path,mode='rb').read().splitlines()   
    lines = (line.decode(encoding) for line in path2)
    
    import shlex
    from networkx.utils import is_string_like
    # multigraph=False
    if is_string_like(lines): lines=iter(lines.split('\n'))
    lines = iter([line.rstrip('\n') for line in lines])
    G=nx.Graph() 
    while lines:
        try:
            l=next(lines)
        except: #EOF
            break
        if l.lower().startswith("*network"):
            label,name=l.split()
            G.name=name
        if l.lower().startswith("*vertices"):
            nodelabels={}
            l,nnodes=l.split()
            for i in range(int(nnodes)):
                    currentline = next(lines)
                    if currentline.lower().startswith("*edges") or currentline.lower().startswith("*arcs") :
                        l = currentline
                        for i in range(int(nnodes)):
                            G.add_node(i)
                            nodelabels[i]=i
                        break
                    splitline=shlex.split(str(currentline))
                    ida,label=splitline[0:2]
                    G.add_node(label)
                    nodelabels[ida]=label
                    G.node[label]={'id':ida}
                    try: 
                        x,y,shape=splitline[2:5]
                        G.node[label].update({'x':float(x),
                                              'y':float(y),
                                              'shape':shape})
                    except:
                        pass
                    extra_attr=zip(splitline[5::2],splitline[6::2])
                    G.node[label].update(extra_attr)
                
                    
        if l.lower().startswith("*edges") or l.lower().startswith("*arcs"):
            for l in lines:
                splitline=shlex.split(str(l))
                if len(splitline)<2:
                    continue
                ui,vi=splitline[0:2]
                u=nodelabels.get(ui,ui)
                v=nodelabels.get(vi,vi)
                # parse the data attached to this edge and put in a dictionary 
                edge_data={}
                try:
                    # there should always be a single value on the edge?
                    w=splitline[2:3]
                    edge_data.update({'weight':float(w[0])})
                except:
                    pass
                    # if there isn't, just assign a 1
#                    edge_data.update({'value':1})
                extra_attr=zip(splitline[3::2],splitline[4::2])
                edge_data.update(extra_attr)
                # if G.has_edge(u,v):
                #     multigraph=True
                G.add_edge(u,v,**edge_data)
    return G

def write_pajek(G, path, encoding='UTF-8'):
    from networkx.utils import is_string_like
    def make_qstr(t):
        
        if not is_string_like(t): 
            t = str(t)
        if " " in t: 
            t=r'"%s"'%t
        return t

    def generate_pajek(G):
        if G.name=='': 
            name='NetworkX'
        else:
            name=G.name
        yield '*network %s'%name
    
        # write nodes with attributes
        yield '*vertices %s'%(G.order())
        nodes = G.nodes()
        # make dictionary mapping nodes to integers
        nodenumber=dict(zip(nodes,range(1,len(nodes)+1))) 
        for n in nodes:
            na=G.node.get(n,{})
            id=int(na.get('id',nodenumber[n]))
            nodenumber[n]=id
            s=' '.join(map(make_qstr,(id,n)))
            for k,v in na.items():
                s+=' %s %s'%(make_qstr(k),make_qstr(v))
            yield s
    
        # write edges with attributes         
        if G.is_directed():
            yield '*arcs'
        else:
            yield '*edges'
        for u,v,edgedata in G.edges(data=True):
            d=edgedata.copy()
            if 'weight' in d :
                value=d.pop('weight',1.0) # use 1 as default edge value
                s=' '.join(map(make_qstr,(nodenumber[u],nodenumber[v],value)))
            else :
                s=' '.join(map(make_qstr,(nodenumber[u],nodenumber[v])))
            for k,v in d.items():
                s+=' %s %s'%(make_qstr(k),make_qstr(v))
            yield s
    path2 = open(path,mode='wb')     
    for line in generate_pajek(G):
        line+='\n'
        path2.write(line.encode(encoding))
    path2.close()
              
for f in os.listdir('.') :
    if os.path.isfile(f) :
        net = None
        if ".gexf" in f :
            net = nx.read_gexf(f)
            suivi(net,f)
        if ".net" in f :
            net = read_pajek(f)
            mapy = {oldkey:int(oldkey) for oldkey in net}
            net = nx.relabel_nodes(net,mapy)
            suivi(net,f)    
        if ".txt" in f :
            print f
            net = nx.read_edgelist(f,create_using=nx.DiGraph(),nodetype=int)
            suivi(net,f)
        if ".gml" in f :
            print f
            net = nx.read_gml(f)
            suivi(net,f)
EIES("EIES")
#stu98()
#lazega()
#siena("EIES")
#siena2("kapf")