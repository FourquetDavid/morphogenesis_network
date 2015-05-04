import networkx as nx
import os
import gexf
from datetime import date
#import igraph as ig
def write(net,f):
    name = f.split('.')[-2]
    net.name = name
    if not os.path.exists("files/"+name): os.makedirs("files/"+name)
    nx.write_gexf(net, "files/"+name+"/"+name+".gexf")
    """
    nx.write_gml(net, "files/"+name+"/"+name+".gml")
    #igraphnet = ig.Graph.Read_GML("files/"+name+"/"+name+".gml")
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
    """
    print "original :"+name,
    print net.number_of_nodes(),
    print net.number_of_edges()

def verif(f):
    name = f.split('.')[-2]
    net = nx.read_gexf("files/"+name+"/"+name+".gexf")
    
        
    #test(net)
    #gexf.write_gexf(net, "files/"+name+"/"+name+"2.gexf")
    print "copied :",
    print net.number_of_nodes(),
    print net.number_of_edges()

def suivi(net,f):
    write(net,f)
    verif(f)
    #os.rename(f,"used/"+f)

    
def network_description():
    def is_dynamic(net): 
        return False
    def is_bipartite(net):
        is_bipartite = True
        node_types = set()
        
        for node,data in net.nodes(data = True) :
            if not data[type] :
                is_bipartite = False
                break
            else :
                node_types.append(data[type])
        return is_bipartite
    
    def try_multi(net):
        edge_types = set()
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
        
    for f in os.listdir('/files') :
        try :
            if os.path.isdir(f) :
                idnetwork,namenetwork = f.split("-",1) 
                net = nx.read_gexf("/files/"+f+"/"+namenetwork+".gexf")
                is_dynamic = is_dynamic(net)
                is_bipartite = is_bipartite(net)
                is_directed,net = try_undirected(net)
                is_weighted,net = try_unweighted(net)
                is_signed = is_signed(net)
                is_multi,net = try_multi(net)
                nbnodes = net.number_of_nodes()
                nbedges = net.number_of_edges()
                nx.write_gexf("/files/changed/"+f+"/"+namenetwork+".gexf")
                output = open("network_description.csv",'a')
                output.write(idnetwork+";"+namenetwork+";"+nbnodes+";"+nbedges+";"+is_directed +";" + is_weighted +";"+is_signed+";"+is_multi+";"+is_dynamic)
                
                os.rename("/files/"+f, "/files/computed/"+f)
                
                
        

                
        except  :
            print "PROBLEM WITH ",f
             
                       
    
def zoo(name):
    
    graph = nx.read_edgelist(name+"/out."+name,create_using=nx.DiGraph(),comments ="%", data=(('sign',int),))
    graph.name = name
    write(graph,name+".gexf")

def livemocha(name,network):
    net = network
    net.name = name
    print name
    
    def nodes() :
        for line in open(name+"-dataset/data/nodes.csv").read().splitlines() :
            net.add_node(int(line))
    def edges() :
        number_line =0
        for line in open(name+"-dataset/data/edges.csv").read().splitlines() :
            number_line +=1
            if (number_line % 500000 ==0) : print number_line, " ", net.number_of_edges()
            try :
                source,target = line.split(",")
            except :
                print number_line, line
            net.add_edge(int(source),int(target)) 
    def groups() :
        try :
            for line in open(name+"-dataset/data/group-edges.csv").read().splitlines() :
                node,group = line.split(",")
                net.node[int(node)]['group'] = int(group)  
        except IOError :
            print "no groups"
    nodes()
    edges()
    groups()
    #print net.node
    #print net.edges()
    print net.number_of_nodes()
    print net.number_of_edges()
    suivi(net,name+".gexf")
        
def add_following_slice(net,netslice,end,currenttime):
    
    for node in netslice.nodes() :
        try :
                debut,fin = net.node[node]['spells'][-1]
                if fin == end :
                    net.node[node]['spells'][-1] = (debut,currenttime)
                else : 
                    net.node[node]['spells'][-1].append((currenttime,currenttime))
                
        except :
            #print "node not found : "+str(node) +" time: "+str(currenttime)
            net.add_node(node,spells =[(currenttime,currenttime)])
    
    for source,target,data in netslice.edges(data= True) :
        
        try :
            debut,fin = net[source][target]['spells'][-1]
            if fin == end :
                net[source][target]['spells'][-1] = (debut,currenttime)
            else : 
                net[source][target]['spells'].append((currenttime,currenttime))
        except :
            #print "edge not found : "+str(source) +" "+str(target)+" time: "+str(currenttime)
            net.add_edge(source,target,spells=[(currenttime,currenttime)])
            
        
        for data_type, value in data.iteritems() :
            try :
                valeur,debut,fin = net[source][target][data_type][-1]
                if fin == end and value == valeur:
                    net[source][target][data_type][-1] = (valeur,debut,currenttime)
                else : 
                    net[source][target][data_type].append((value,currenttime,currenttime))
                
            except :
                print "data not found : "+data_type +" edge : "+str(source) +" "+str(target)+" time: "+str(currenttime)
                net[source][target][data_type] =[(value,currenttime,currenttime)]
    return net

def create_first_slice(net,start):
    for node in net.nodes() :
        net.node[node]['spells'] = [(start,start)]
    for source,target in net.edges() :
        net[source][target]['spells'] = [(start,start)]
    
    return net




def VRND():
    graph = nx.DiGraph()
    graph.name = "VanDeBunt_students"
    graph.dynamic = True
    graph.timeformat = "double"
    def attribute() :
        i=0
        for line in open("VRND/VARS.DAT").read().splitlines() :
            gender = {1: "F", 2:"M"}
            program = {2:"2-year",3:"3-year",4:"4-year"}
            smoking = {1:"yes",2 :"no"}
            gender_N,program_N,smoking_N = [int(number) for number in line.split(" ") if number != '']
            
            graph.add_node(i, dict(gender = gender[gender_N], program = program[program_N], smoking = smoking[smoking_N] ))
            i=i+1
    attribute()
                    
    def subgraph(number_time):
        subgraph = nx.DiGraph()
        subgraph.add_nodes_from(graph.nodes(data=True))
        def type_rel(number) : 
            d =  {0 : "unknown", 1 : "best_friend", 2 : "friend", 3 : "friendly_relation", 4 :"neutral",5:"troubled"}         
            return d[number]
        source=0
        for line in open("VRND/VRND32T"+ str(number_time)+".DAT").read().splitlines() :
            target = 0
            for number_of_messages in [int(number) for number in line.split(" ") if number != ''] :
                if  number_of_messages != 6 and number_of_messages != 9 : 
                    keyhere = type_rel(number_of_messages)
                    subgraph.add_edge(source,target, type_relationship = keyhere)
                    
                target = target+1
            source = source+1
        return subgraph
    
    net = create_first_slice(graph,0)
    #test(net)
    #test(subgraph(0))
    net = add_following_slice(net, subgraph(0), 0, 0, 0)
    
    net = add_following_slice(net, subgraph(1), 0, 0, 1)
    #test(net)
    net = add_following_slice(net, subgraph(2), 0, 1, 2)
    net = add_following_slice(net, subgraph(3), 0, 2, 3)
    net = add_following_slice(net, subgraph(4), 0, 3, 4)
    net = add_following_slice(net, subgraph(5), 0, 4, 5) 
    net = add_following_slice(net, subgraph(5), 0, 5, 6) 
    test(net)
    suivi(net,"VanDeBunt_students.gexf",dynamic = True)   
    
def stu98():
    name = "stu98"
    graph = nx.DiGraph()
    graph.name = name
    
    
    def attribute() :
        i=0
        for line in open("stu98/stud98.txt").read().splitlines() :
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
            
    def subgraph(number_time):
        graph = nx.DiGraph()
        def type_rel(number) : 
            d =  {1 : "Best friendship", 2 : "Friendship", 3 : "Friendly relationship", 4 :"Neutral relationship",5:"Troubled relationship" }         
            return d[int(number)]
        source=0
        for line in open("stu98/"+name +"t"+ str(number_time)+".txt").read().splitlines() :
            target = 0
            for number_of_messages in [number for number in line.split("\t") if number != ''] :
                if int(number_of_messages) not in [0,6,8,9] : 
                    keyhere = type_rel(int(number_of_messages))
                    graph.add_edge(source,target, relationship = keyhere) 
                target = target+1
            source = source+1
        return graph
    
    attribute()
    net = create_first_slice(graph,0)
    #test(net)
    #test(subgraph(0))
    net = add_following_slice(net, subgraph(0), 0, 0, 0)
    #test(net)
    net = add_following_slice(net, subgraph(2), 0, 0, 2)
    net = add_following_slice(net, subgraph(3), 0, 2, 3)
    net = add_following_slice(net, subgraph(5), 0, 3, 5)
    net = add_following_slice(net, subgraph(6), 0, 4, 6) 
    #test(net)
    suivi(net,"stud98.gexf",dynamic = True)   
        
            
def EIES(name):
    graph = nx.DiGraph()
    graph.name = "EIES"
    graph.dynamic = True
    graph.timeformat = "double"
    def attribute() :
        i=0
        for line in open("EIES/EIES.ATT").read().splitlines() :
            field =  {1 : "sociology", 2 : "anthropology", 3 : "mathematics/statistics", 4 : "psychology"}
            citations,type_research = [int(number) for number in line.split(" ") if number != '']
            
            graph.add_node(i, dict(number_of_citations = citations, discipline = field[type_research] ))
            i=i+1
    attribute()
    
    def message() :
        source=0
        for line in open("EIES/messages.asc").read().splitlines() :
            target = 0
            for number_of_messages in [number for number in line.split(" ") if number != ''] :
                if int(number_of_messages) != 0 :
                    graph.add_edge(source,target, number_of_messages_sent = int(number_of_messages))
                target = target+1
            source = source+1
    
                    
    def subgraph(number_time):
        subgraph = nx.DiGraph()
        subgraph.add_nodes_from(graph.nodes(data=True))
        def type_rel(number) : 
            d =  {1 : "do_not_know_the_other", 2 : "heard_about_the_other,did_not_meet_him/her", 3 : "have_met_the_other", 4 :"friend" }         
            return d[number]
        source=0
        for line in open("EIES/EIES."+ str(number_time)).read().splitlines() :
            target = 0
            for number_of_messages in [int(number) for number in line.split(" ") if number != ''] :
                if  number_of_messages != 0  : 
                    keyhere = type_rel(number_of_messages)
                    subgraph.add_edge(source,target, relationship = keyhere)
                    
                target = target+1
            source = source+1
        return subgraph
    
    net = create_first_slice(graph,1)
    #test(net)
    #test(subgraph(0))
    net = add_following_slice(net, subgraph(1), 1, 1,1)
    net = add_following_slice(net, subgraph(2), 1, 1,2)
    message()
    #test(net)
    suivi(net,"EIES.gexf",dynamic = True)   
     
    
      
def kapf():
    graph = nx.MultiDiGraph()
    graph.name = "kapf"
    def attribute() :
        i=0
        for line in open("kapf/kapfa_stat.dat").read().splitlines() :
    
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
        for line in open("kapf/messages.asc").read().splitlines() :
            target = 0
            for number_of_messages in [number for number in line.split(" ") if number != ''] :
                if int(number_of_messages) != 0 :
                    graph.add_edge(source,target, key = 'number_of_messages_sent', weight = int(number_of_messages))
                target = target+1
            source = source+1
    
    
    def time(number_time):
        subgraph = nx.DiGraph()
        subgraph.add_nodes_from(graph.nodes(data=True))
        source=0
        for line in open("kapf/kapfti"+ str(number_time)+".dat").read().splitlines() :
            target = 0
            for relate in [number for number in line.split(" ") if number != ''] :
                if int(relate) != 0 : 
                        subgraph.add_edge(source,target, type = "instrumental_interactions") 

                target = target+1
            source = source+1
        for line in open("kapf/kapfts"+ str(number_time)+".dat").read().splitlines() :
            target = 0
            for relate in [number for number in line.split(" ") if number != ''] :
                if int(relate) != 0 : 
                        subgraph.add_edge(source,target, type = "sociational_interactions") 

                target = target+1
            source = source+1
        return subgraph
    
    
    net = create_first_slice(graph,1)
    #test(net)
    #test(subgraph(0))
    net = add_following_slice(net, time(1), 1, 1,1)
    net = add_following_slice(net, time(2), 1, 1,2)
    message()
    test(net)
    suivi(net,"kapf.gexf",dynamic = True)     
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
            graph.add_edge(debut,fin,type = typedg, weight = float(size))
    
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
    
    
    #graph_follows = subgraph("follows")
    #graph_retweets = subgraph("retweets")
    #graph_mentions = subgraph("mentions")
    #print graph_follows.edge
    #write(graph_follows,realname+"-follows.gexf")
    #write(graph_retweets,realname+"-retweets.gexf")
    #write(graph_mentions,realname+"-mentions.gexf") 
    suivi(graph, realname+".gexf")   

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
                    graph.add_edge(source,target, type = exp_type)
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
    #adv=subdigraph("advice")
    #fr=subdigraph("friend")
    #wo=subdigraph("work")
    #print graph.node
    #print graph.edge
    #write(adv,name+"-advice.gexf")
    #write(fr,name+"-friend.gexf")
    #write(wo,name+"-work.gexf") 
    if not os.path.exists("files/"+name): os.makedirs("files/"+name)
    suivi(graph, name+".gexf")



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
    
def cities(filename ):
    net = nx.Graph()
    lines = iter(open(filename).read().splitlines())
    while lines :
        try:
            l=next(lines)
        except: #EOF
            break
        if l.startswith("*net"):
            _,name=l.split()
            net.name = "Global cities"
        if l.startswith("*vertices"):
            _,totalnumber,numberofrows=l.split()
            for _ in range(int(numberofrows)) :
                l = next(lines).replace(" ","")
                numero,city,_ = l.split('"')
                net.add_node(int(numero))
                net.node[int(numero)]['label'] = city
                net.node[int(numero)]['type'] = 'city'
            while lines:
                l =next(lines)
                if l.startswith("*matrix"): break
                if l.startswith("%") :
                    _,sector_company = l.split(" ",1)
                else :
                    l.replace(" ","")
                    numero,company,_ = l.split('"')
                    net.add_node(int(numero))
                    net.node[int(numero)]['label'] = company
                    net.node[int(numero)]['type'] = 'company'
                    net.node[int(numero)]['sector'] = sector_company         
        if l.startswith("*matrix"): 
            for source in range(1,int(numberofrows)+1):
                edges=next(lines).split()
                for target in range(int(totalnumber)-int(numberofrows)) :
                    if int(edges[target]) != 0 :
                        net.add_edge(source,target+int(numberofrows)+1,weight=int(edges[target]))
                    
    suivi(net,"globalCities.net")
def stud_gov(filename ):
    net = nx.DiGraph()
    lines = iter(open(filename).read().splitlines())
    while lines :
        l=next(lines)
        net.name = filename
        if l.startswith("*Vertices"):
            _,totalnumber=l.replace(" ","").split("s")
            for _ in range(int(totalnumber)) :
                l = next(lines)
                numero,name = [info for info in l.split(" ") if info != ''][0:2]
                net.add_node(int(numero))
                net.node[int(numero)]['label'] = name    
            break
    
    while lines :
        try :
            l=next(lines)  
        except :
            break
        if l.startswith("*Arcs"): 
            while lines :
                l=next(lines)
                if l.startswith("*") : break
                splitline = [value for value in l.split() if value != '']
                source,target,_ = splitline
                net.add_edge(int(source),int(target))
                
        if l.startswith("*Partition s"):
            _,numbersteps=next(lines).replace(" ","").split("s")
            type_dict = {1:"advisor",2:"minister",3:"prime minister"}
            for numero in range(1,int(numbersteps)+1) :
                l = next(lines)
                print l
                type_node = int(l)
                net.node[int(numero)]['position'] = type_dict[type_node]
                
        
    #test(net)                
    suivi(net,filename)  

def centrality(filename ="centrality_literature.paj" ):
    net = nx.DiGraph()
    lines = iter(open(filename).read().splitlines())
    while lines :
        l=next(lines)
        net.name = filename.split(".")[0]
        if l.startswith("*Vertices"):
            _,totalnumber=l.replace(" ","").split("s")
            for _ in range(int(totalnumber)) :
                l = next(lines)
                numero,name = [info for info in l.split('"') if info !=''][0:2]
                net.add_node(int(numero))
                net.node[int(numero)]['label'] = name    
            break
    
    while lines :
        try :
            l=next(lines)  
        except :
            break
        if l.startswith("*Arcs"): 
            while lines :
                l=next(lines)
                if l.startswith("*Edges") : break
                splitline = [value for value in l.split() if value != '']
                if splitline ==[] : break
                source,target = splitline[:2]
                net.add_edge(int(source),int(target))

                
                 
                
    #test(net)                
    suivi(net,filename)
def Dining_partner(filename ="Dining-table_partners.net" ):
    net = nx.DiGraph()
    lines = iter(open(filename).read().splitlines())
    while lines :
        l=next(lines)
        net.name = filename.split(".")[0]
        if l.startswith("*Vertices"):
            _,totalnumber=l.replace(" ","").split("s")
            for _ in range(int(totalnumber)) :
                l = next(lines)
                numero,name = [info for info in l.split('"') if info !=''][0:2]
                net.add_node(int(numero))
                net.node[int(numero)]['label'] = name    
            break
    
    while lines :
        try :
            l=next(lines)  
        except :
            break
        if l.startswith("*Arcs"): 
            while lines :
                l=next(lines)
                if l.startswith("*Edges") : break
                splitline = [value for value in l.split() if value != '']
                if splitline ==[] : break
                source,target,rank = splitline[:3]
                net.add_edge(int(source),int(target),rank = int(rank))

                
                 
                
    #test(net)                
    suivi(net,filename)
def sanjuan(filename ):
    net = nx.DiGraph()
    lines = iter(open(filename).read().splitlines())
    while lines :
        l=next(lines)
        net.name = filename.split(".")[0]
        if l.startswith("*Vertices"):
            _,totalnumber=l.replace(" ","").split("s")
            for _ in range(int(totalnumber)) :
                l = next(lines)
                numero,name = [info for info in l.split('"') if info !=''][0:2]
                net.add_node(int(numero))
                net.node[int(numero)]['label'] = name    
            break
    
    while lines :
        try :
            l=next(lines)  
        except :
            break
        if l.startswith("*Arcs"): 
            while lines :
                dict_type ={1 :"ordinary visits", 2 :" visits among kin", 3 :"visits among ritual kin"}
                l=next(lines)
                if l.startswith("*Edges") : break
                splitline = [value for value in l.split() if value != '']
                if splitline ==[] : break
                source,target,type_relation = splitline[:3]
                net.add_edge(int(source),int(target))
                net[int(source)][int(target)]['type'] = dict_type[int(type_relation)]
                
                 
                
        if l.startswith("*Partition SanJuanSur_status.clu"):
            _,numbersteps=next(lines).replace(" ","").split("s")
            for numero in range(1,int(numbersteps)+1) :
                l = next(lines)
                type_node = int(l)
                net.node[int(numero)]['status'] = type_node
                
        if l.startswith("*Partition SanJuanSur_leaders.clu"):
            _,numbersteps=next(lines).replace(" ","").split("s")
            for numero in range(1,int(numbersteps)+1) :
                l = next(lines)
                type_node = int(l)
                net.node[int(numero)]['prestige_leader'] = type_node
                
    #test(net)                
    suivi(net,filename)      
def scotland(filename ):
    net = nx.Graph()
    lines = iter(open(filename).read().splitlines())
    while lines :
        l=next(lines)
        net.name = filename
        if l.startswith("*Vertices"):
            _,totalnumber=l.replace(" ","").split("s")
            for _ in range(int(totalnumber)) :
                l = next(lines)
                numero,name = [info for info in l.split('"') if info !=''][0:2]
                net.add_node(int(numero))
                net.node[int(numero)]['label'] = name    
            break
    
    while lines :
        try :
            l=next(lines)  
        except :
            break
        if l.startswith("*Edges"): 
            while lines :
                l=next(lines)
                
                splitline = [value for value in l.split() if value != '']
                if splitline ==[] : break
                source,target,_ = splitline
                net.add_edge(int(source),int(target))
                
        if l.startswith("*Partition A"):
            _,numbersteps=next(lines).replace(" ","").split("s")
            type_dict = {1:"company",2:"director"}
            for numero in range(1,int(numbersteps)+1) :
                l = next(lines)
                type_node = int(l)
                net.node[int(numero)]['type'] = type_dict[type_node]
                
        if l.startswith("*Partition I"):
            _,numbersteps=next(lines).replace(" ","").split("s")
            type_dict = {1:"oil and mining",2:"railway",3:"engineering and steel",
                         4:"electricity and chemicals",5:"domestic products",6:"banks",
                         7:"insurance",8:"investment"}
            for numero in range(1,int(numbersteps)+1) :
                l = next(lines)
                type_node = int(l)
                net.node[int(numero)]['industry_type'] = type_dict[type_node]
                
        if l.startswith("*Vector"):
            _,numbersteps=next(lines).replace(" ","").split("s")
            for numero in range(1,int(numbersteps)+1) :
                l = next(lines)
                capital = int(l)
                net.node[int(numero)]['capital'] = capital*1000
    test(net)                
    suivi(net,filename)

def test(net):
    for node in net.nodes(data= True) :
        print node
    for edge in net.edges(data= True) :
        print edge
def read_ucinet_bimatrix(name,namerow,namecolumn):
    net = nx.Graph()
    net.name = name
    lines = iter(open(name+".dat").read().splitlines())
    while lines :
        try:
            l=next(lines)
        except: #EOF
            break
        if l.startswith("NR"):
            type1,type2=l.split(", ")
            nb_nodes_type1 = int(type1.replace("NR=",""))
            nb_nodes_type2 = int(type2.replace("NC=",""))
            for numero in range(1,nb_nodes_type1+1) :
                net.add_node(numero)
                net.node[numero]['type'] = namerow
            for numero in range(nb_nodes_type1+1,nb_nodes_type2+nb_nodes_type1+1) :
                net.add_node(numero)
                net.node[numero]['type'] = namecolumn
                
        if l.startswith("DATA:"): 
            for source in range(1,nb_nodes_type1+1):
                edges=next(lines).split()
                for target in range(nb_nodes_type2) :
                    if int(edges[target]) == 1 :
                        net.add_edge(source,target+nb_nodes_type1+1)
                    
    return net
def galas():
    net = read_ucinet_bimatrix("galas", "CEO", "club")
    suivi(net,"galas.dat")
        

def read_ucinet(name):
    
    net = nx.Graph()
    realname = name.replace("_2.0","").replace("-agent","").replace("-organization","").replace("-Agent","").replace("-location","").replace('.dl',"")
    net.name = realname
    
    lines = iter(open(name).read().splitlines())
    while lines :
        try:
            l=next(lines)
        except: #EOF
            break
        if l.startswith("N "):
            _,_,nbnodes=l.split()
            print "N",nbnodes
        if l.startswith("NM"):
            _,_,nb_of_networks=l.split()
            print "NM",nb_of_networks
            if int(nb_of_networks) > 1 :
                net = nx.MultiDiGraph(net)
            else :
                net = nx.DiGraph(net)
            print net.name
        
        if l.startswith("LABELS:"):
            nodelabels ={}
            for id in range(1,int(nbnodes)+1):
                splitline=next(lines).split()
                label=splitline[0]
                net.add_node(label)
                nodelabels[id]=label
        
        if l.startswith("MATRIX LABELS:"):
            networks_names =[]
            for i in range(int(nb_of_networks)):
                splitline=next(lines).split()
                label_network=splitline[0]
                networks_names.append(label_network)
        if l.startswith("DATA:"): 
             
            current_network = networks_names.pop(0) 
            print current_network
            while lines :    
                try:
                    l=next(lines)
                except: #EOF
                    break
                if l.startswith("#"):
                    current_network = networks_names.pop(0)
                    print current_network
                    l=next(lines)
                sourceindex,targetindex,value=l.split()
                source = nodelabels[int(sourceindex)]
                target = nodelabels[int(targetindex)]
                if int(nb_of_networks) > 1 :
                    net.add_edge(source,target,type=current_network,weight = int(value))
                else :
                    net.add_edge(source,target,weight = int(value))
    return net

def csphd():
    net = read_ucinet("csphd_2.0-agent-agent.dl")
    suivi(net,"csphd.gexf")

def dining():
    
    net = read_ucinet("dining_2.0-agent-agent.dl")
    suivi(net,"dining.gexf")
    
def drug_net():  
    net = read_ucinet("drug_net-agent-agent.dl")
    suivi(net,"drug_net.gexf") 

def Flying_teams():  
    net = read_ucinet("Flying_teams-agent-agent.dl")
    suivi(net,"Flying_teams.gexf") 

def FauxMesaHigh():  
    net = read_ucinet("FauxMesaHigh-Agent-Agent.dl")
    suivi(net,"FauxMesaHigh.gexf") 

def Galesburg():  
    net = read_ucinet("Galesburg_2.0-agent-agent.dl")
    suivi(net,"Galesburg.gexf") 

def gama():  
    net = read_ucinet("gama_2.0-agent-agent.dl")
    suivi(net,"gama.gexf") 

def knokbur():  
    net = read_ucinet("knokbur_2.0-organization-organization.dl")
    suivi(net,"knokbur.gexf") 
    
def literature_1976():  
    net = read_ucinet("literature_1976-agent-agent.dl")
    suivi(net,"literature_1976.gexf") 
    

def mexican_power():  
    net = read_ucinet("mexican_power-agent-agent.dl")
    suivi(net,"mexican_power.gexf") 
    
def ModMath():  
    net = read_ucinet("ModMath-agent-agent.dl")
    suivi(net,"ModMath.gexf") 

def NewcombFraternity():  
    net = read_ucinet("NewcombFraternity-agent-agent.dl")
    suivi(net,"NewcombFraternity.gexf") 

def SanJuanSur():  
    net = read_ucinet("SanJuanSur-agent-agent.dl")
    suivi(net,"SanJuanSur.gexf") 
    

def Sampson():  
    net = read_ucinet("Sampson-agent-agent.dl")
    suivi(net,"Sampson.gexf") 

def Scotland():  
    net = read_ucinet("Scotland-agent-agent.dl")
    suivi(net,"Scotland.gexf") 

def Stranke94():  
    net = read_ucinet("Stranke94-agent-agent.dl")
    suivi(net,"Stranke94.gexf") 

def strike():  
    net = read_ucinet("strike-agent-agent.dl")
    suivi(net,"strike.gexf") 

def szcid():  
    net = read_ucinet("szcid-agent-agent.dl")
    suivi(net,"szcid.gexf") 

def taro():  
    net = read_ucinet("taro-agent-agent.dl")
    suivi(net,"taro.gexf") 
    
def thuroff():  
    net = read_ucinet("thuroff-agent-agent.dl")
    suivi(net,"thuroff.gexf") 
    
    
def trade():  
    net = read_ucinet("trade-location-location.dl")
    suivi(net,"trade.gexf") 


def bkfrat():
    net = read_ucinet("bkfrat.dl")
    suivi(net,"bkfrat.dl")
def bkham():
    net = read_ucinet("bkham.dl")
    suivi(net,"bkham.dl")
def bktec():
    net = read_ucinet("bktec.dl")
    suivi(net,"bktec.dl")

def PGP() :
    graph = nx.Graph()
    graph.name = "PGP-giantcompo"
    net = read_pajek("PGPgiantcompo.net")
    print net.number_of_nodes()
    mapy = {oldkey:int(oldkey.replace('v','')) for oldkey in net}
    net = nx.relabel_nodes(net,mapy)
    net1 = nx.Graph()
    net1.add_nodes_from(net.nodes(data = False))
    net1.add_edges_from(net.edges(data = False))
    net1.name = "PGP-giantcompo"
    suivi(net1,"PGP-giantcompo.net")

def mathscinet() :
    graph = nx.Graph()
    graph.name = "MathSciNet"
    for line in (open("alr20--wCoAuNw--MathSciNet.txt").read().splitlines()) :
        if  not line.startswith('#') :
            source,target,weight = line.split("\t")
            graph.add_edge(source, target, weight = weight)
    suivi(graph,"MathSciNet.gexf")

def pin():
    for network in os.listdir("pin") :
        graph = nx.Graph()
        name = network.replace(".txt","")
        graph.name = name
        for line in (open("pin/"+name+".txt").read().splitlines()) :
            if  not line.startswith('#') :
                source,target = line.split("\t")[0:2]
                graph.add_edge(source, target)
        suivi(graph,name+".gexf")

def Www():
        graph = nx.DiGraph()
        name = "World-Wide-Web"
        graph.name = name
        for line in (open(name+".txt").read().splitlines()) :
            if  not line.startswith('#') :
                source,target = line.split(" ")[0:2]
                graph.add_edge(source, target)
        suivi(graph,name+".gexf") 
               
def autonomous():
    graphe_dynamique = None
    lasttime = None
    for network in os.listdir("as-733") :
        graph = nx.DiGraph()
        name = network.replace(".txt","")
        graph.name = name
        for line in (open("as-733/"+name+".txt").read().splitlines()) :
            if  not line.startswith('#') :
                source,target = line.split("\t")
                graph.add_edge(source, target)
        suivi(graph,name+".gexf")
        
        if graphe_dynamique is None :
            graphe_dynamique = graph.copy()
            date = name.replace("as","")
            date = date[0:4]+"-"+date[4:6]+"-"+date[6:8]
            graphe_dynamique = create_first_slice(graphe_dynamique, date)
            lasttime= date
            print lasttime
            
        else :
            date = name.replace("as","")
            date = date[0:4]+"-"+date[4:6]+"-"+date[6:8]
            add_following_slice(graphe_dynamique, graph,  lasttime, date)
            lasttime= date
            print lasttime
    suivi(graphe_dynamique,"as733.gexf")

def blogcatalog3():
    graph = nx.Graph()
    graph.name = "BlogCatalog3"
    
    for line in (open("BlogCatalog-dataset/data/group-edges.csv").read().splitlines()) :
        node,group = line.split(",")
        graph.add_node(int(node), group = int(group))
    for line in (open("BlogCatalog-dataset/data/edges.csv").read().splitlines()) :
        source,target = line.split(",")
        graph.add_edge(int(source), int(target))   
    suivi(graph,graph.name+".gexf") 

def douban():
    graph = nx.Graph()
    graph.name = "Douban"
    for line in (open("Douban-dataset/data/edges.csv").read().splitlines()) :
        source,target = line.split(",")
        graph.add_edge(int(source), int(target))   
    suivi(graph,graph.name+".gexf")
    
        
def epinions():
    graph = nx.DiGraph()
    graph.name = "epinions"
    for line in (open("soc-sign-epinions.txt").read().splitlines())[4:] :
        linesplit = line.split("\t")
        graph.add_edge(int(linesplit[0]), int(linesplit[1]), weight = int(linesplit[2]))
    write(graph,graph.name+".gexf")

def email():
    graph = nx.Graph()
    graph.name = "email"
    for line in (open("email.txt").read().splitlines()) :
        linesplit = [int(element) for element in line.split(" ") if element != '']
        graph.add_edge(int(linesplit[0]), int(linesplit[1]))
        if linesplit[2] != 1 : print str(linesplit)+"poids different de 1 : "+str(linesplit[2])
    suivi(graph,graph.name+".gexf")

def eu():
    graph = nx.DiGraph()
    graph.name = "email-EuAll"
    for line in (open(graph.name+"/out."+graph.name).read().splitlines()[2:]) :
        linesplit = [int(element) for element in line.split(" ") if element != '']
        graph.add_edge(int(linesplit[0]), int(linesplit[1]))
    suivi(graph,graph.name+".gexf")



def tribe(): 
    graph = nx.Graph()
    graph.name = "ucidata-gama"
    for line in (open(graph.name+"/out."+graph.name).read().splitlines()[2:]) :
        linesplit = [int(element) for element in line.split("\t") if element != '']
        graph.add_edge(int(linesplit[0]), int(linesplit[1]),weight = int(linesplit[2]))
    suivi(graph,graph.name+".gexf")

def hamster(): 
    graph = nx.Graph()
    graph.name = "petster-friendships-hamster"
    
    attributes = []
    lines = open(graph.name+"/ent."+graph.name).read().splitlines()
    
    for element in lines[2].replace("% ent ","").split() :
        attributes.append(element.replace("dat.",""))
    print attributes   
    for line in lines[3:] :
        prettyline = line[1:-1].replace("&nbsp","")
        linesplit = prettyline.split("\" \"") 
        graph.add_node(int(linesplit[0]),
                       **dict([(attributes[i],linesplit[i+1]) for i in range(len(attributes))]))
        
    for line in (open(graph.name+"/out."+graph.name).read().splitlines()[2:]) :
        linesplit = [int(element) for element in line.split() if element != '']
        graph.add_edge(linesplit[0], linesplit[1])
    for node in graph.nodes(data=True) :
        print node
    suivi(graph,graph.name+".gexf")
def cat():
    graph = nx.Graph()
    graph.name = "petster-friendships-cat"
    
    attributes = []
    lines = open(graph.name+"/ent."+graph.name).read().splitlines()
    
    for element in lines[2].replace("% ent ","").split() :
        attributes.append(element.replace("dat.",""))
    print attributes   
    for line in lines[3:] :
        prettyline = line.replace("&nbsp","")
        linesplit = prettyline.split(" \"") 
        graph.add_node(int(linesplit[0]),
                       **dict([(attributes[i],linesplit[i+1].replace("\"","")) for i in range(len(attributes))]))
        
    for line in (open(graph.name+"/out."+graph.name).read().splitlines()[1:]) :
        linesplit = [int(element) for element in line.split() if element != '']
        graph.add_edge(linesplit[0], linesplit[1])
    suivi(graph,graph.name+".gexf")
    
def munmun():
    graph = nx.DiGraph()
    name ="munmun_digg_reply"
    graph.name = name 
    def add_edge(source,target,timestamp) :
        
        if not graph.has_edge(source, target) :
            graph.add_edge(source,target,weight = 1,timestamps = [timestamp])
        else :
            edge = graph.get_edge_data(source, target)
            edge["timestamps"].append(timestamp)
            edge["weight"]+=1
            
    for line in open(name+"/out."+name).read().splitlines()[1:] :
        linesplit = line.split()
        add_edge(int(linesplit[0]),int(linesplit[1]),linesplit[3])
    for _,_,data in graph.edges(data=True):
        data["timestamps"] = " ".join(data["timestamps"])
    print graph.edge[1]
    suivi(graph,graph.name+".gexf")

def wiksigned(): 
    graph = nx.DiGraph()
    name ="wikisigned-k2"
    graph.name = name 
            
    for line in open(name+"/out."+name).read().splitlines()[1:] :
        linesplit = line.split()
        graph.add_edge(int(linesplit[0]),int(linesplit[1]),weight = int(linesplit[2]))
    
    print graph.edge[1]
    suivi(graph,graph.name+".gexf")


    
       
def slash(): 
    graph = nx.DiGraph()
    name ="slashdot-threads"
    graph.name = name 
    def add_edge(source,target,timestamp) :
        
        if not graph.has_edge(source, target) :
            graph.add_edge(source,target,weight = 1,timestamps = [timestamp])
        else :
            edge = graph.get_edge_data(source, target)
            edge["timestamps"].append(timestamp)
            edge["weight"]+=1
            
    for line in open(name+"/out."+name).read().splitlines()[2:] :
        linesplit = line.split()
        add_edge(int(linesplit[0]),int(linesplit[1]),linesplit[3])
    for _,_,data in graph.edges(data=True):
        data["timestamps"] = " ".join(data["timestamps"])
    print graph.edge[1]
    suivi(graph,graph.name+".gexf")
    

def southern():
    graph = nx.Graph()
    graph.name = "Davis_southern_club_women"
    
    women ={}
    i = 1
    for line in (open(graph.name+"-name.txt").read().splitlines()) :
        women[i] = line.replace("\"","")
        i+=1
        
    for line in (open(graph.name+"-two_mode.txt").read().splitlines()) :
        linesplit = [element for element in line.split(" ") if element != '']
        graph.add_node(women[int(linesplit[0])], type = "woman")
        graph.add_node("event-"+linesplit[1], type = "event")
        graph.add_edge(women[int(linesplit[0])], "event-"+linesplit[1])
    suivi(graph,graph.name+".gexf")



def bipart(name,type1,type2,nb_type1):
    nb_users = nb_type1
    graph = nx.Graph()
    graph.name = name 
    def add_bipartite_edge(user,group) :
        if not graph.has_node(user) :
            graph.add_node(user, bipartite = type1, name = str(user))
        if not graph.has_node(group+nb_users) :
            graph.add_node(group, bipartite = type2, name = str(group))
        graph.add_edge(user, group+nb_users)
            
    for line in open(name+"/out."+name).read().splitlines()[1:] :
        linesplit = line.split(" ")
        add_bipartite_edge(int(linesplit[0]),int(linesplit[1]))
    print graph.edge[1]
    suivi(graph,graph.name+".gexf")
def YG() : 
    bipart("youtube-groupmemberships","youtube-user","youtube-group",94238)
    

def db() :
    bipart("dbpedia-team","athlete","team",138652)

def record():
    bipart("dbpedia-recordlabel","artist","record",151640)

def flickr():
    bipart("flickr-groupmemberships", "flickr-user", "flickr-group", 395979)

def wall():
    graph = nx.DiGraph()
    name ="facebook-wosn-wall"
    graph.name = name 
    def add_edge(source,target,timestamp) :
        
        if not graph.has_edge(source, target) :
            graph.add_edge(source,target,weight = 1,timestamps = [timestamp])
        else :
            edge = graph.get_edge_data(source, target)
            edge["timestamps"].append(timestamp)
            edge["weight"]+=1
            
    for line in open(name+"/out."+name).read().splitlines()[1:] :
        linesplit = line.split("\t")
        add_edge(int(linesplit[0]),int(linesplit[1]),linesplit[2].split()[1])
    for _,_,data in graph.edges(data=True):
        data["timestamps"] = " ".join(data["timestamps"])
    print graph.edge[1]
    print graph[1015][1017]
    suivi(graph,graph.name+".gexf")

def oclinks():
    graph = nx.DiGraph()
    graph.name = "OClinks"
    for line in (open("OClinks_w.dl").read().splitlines())[4:] :
        linesplit = line.split(" ")
        graph.add_edge(int(linesplit[0]), int(linesplit[1]), weight = int(linesplit[2]))
    write(graph,graph.name+".gexf")

def slashdot(numero):
    graph = nx.DiGraph()
    graph.name = "Slashdot"+numero
    for line in (open("Slashdot"+numero+".txt").read().splitlines())[4:] :
        linesplit = line.split("\t")
        graph.add_edge(int(linesplit[0]), int(linesplit[1]))
    write(graph,graph.name+".gexf")
    
def facebook(number):
    graph = nx.Graph()
    graph.name = "ego-Facebook-"+str(number)
    
    def attributes() : 
        list_features =[] 
        for line in open("facebook/"+str(number)+".featnames").read().splitlines() :
            linesplit = line.replace(";","_").split(" ")
            feature = linesplit[1].replace("id","").replace("anonymized","")
            feat_num = int(linesplit[0])
            list_features.append((feature,feat_num))
        return list_features  
    features = attributes()
    print features
    
    def myattributes() :
        for line in open("facebook/"+str(number)+".egofeat").read().splitlines() :
            graph.add_node(0)
            splitline =[int(numero) for numero in line.split(" ") if numero != ''][1:]
            together = zip(splitline,features)
            for numero,feat in together :
                if numero==1 :
                    feature,feat_num = feat
                    graph.node[0][feature] = feat_num
    def otherattributes():
        for line in open("facebook/"+str(number)+".feat").read().splitlines() :
            splitline =[int(numero) for numero in line.split(" ") if numero != '']
            i= splitline[0]
            graph.add_node(i)
            graph.add_edge(0, i)
            splitline =[int(numero) for numero in line.split(" ") if numero != '']
            together = zip(splitline[1:],features)
            for numero,feat in together :
                if numero==1 :
                    feature,feat_num = feat
                    graph.node[i][feature] = feat_num
            i=i+1
    myattributes()
    otherattributes()
    #print graph.node[0]
    #import random
    #node =random.choice(graph.nodes())
    #print node
    #print graph.edge[0]
    def edges() :
        for line in open("facebook/"+str(number)+".edges").read().splitlines() :
            l =[int(numero) for numero in line.split(" ") if numero != '']
            graph.add_edge(l[0],l[1])
    def circles() :
        for line in open("facebook/"+str(number)+".circles").read().splitlines() :
            splitline =[numero for numero in line.split("\t") if numero != '']
            numero_circle = int(splitline[0].replace("circle",""))
            #print numero_circle
            for numero in splitline[1:] :
                graph.node[int(numero)]['circle']=numero_circle
    edges()
    circles()
    #print graph.edge[node]
    #print graph.node[node]['circle']
    suivi(graph,graph.name+".gexf")
    

def consulting():
    graph = nx.MultiDiGraph()
    realname = "Cross_Parker-Consulting"
    name = "Cross_Parker/Cross_Parker-Consulting"
    graph.name = realname
    def edge(nameE,nameExt,dico): 
        for line in open(name+"_"+nameE+".txt").read().splitlines() :
            source, target,weight = [int(entier) for entier in line.split(" ") if entier != '']
            graph.add_edge(source, target, type = nameExt,**{nameExt : dico[weight]})
    edge("info","ask_for_advice",{0: "I Do Not Know This Person", 1: "Never", 2: "Seldom", 3: "Sometimes", 4: "Often", 5:"Very Often"})
    edge("value","has_expertise",{0: "I Do Not Know This Person", 1: "Strongly Disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly Agree" })     
   
    def attribute(nameA,dico,realnameA=None) :
        if realnameA == None : realnameA = nameA
        for line in open(name+"-"+nameA+".txt").read().splitlines() :
            linesplit = line.split(" ")
            i=1
            for prop in [int(entier) for entier in linesplit if entier !=''] :
                graph.node[i][nameA] = dico[prop]
                i+=1
    attribute("gender",{1: "male", 2: 'female'})
    attribute("orglevel",{1 : "Research Assistant", 2: "Junior Consultant", 3: "Senior Consultant", 4: "Managing Consultant", 5: "Partner"}, "organisational_level")
    attribute("region",{1: "Europe", 2: "USA"})
    attribute("location",{1: "Boston", 2: "London", 3: "Paris", 4: "Rome", 5: "Madrid", 6: "Oslo", 7: "Copenhagen"})
    
    #import random
    #print random.choice(graph.nodes(data=True))   
    #print random.choice(graph.edges(keys=True,data = True))
    suivi(graph,realname+".gexf")

def manufacturing():
    graph = nx.MultiDiGraph()
    realname = "Cross_Parker-Manufacturing"
    name = "Cross_Parker/Cross_Parker-Manufacturing"
    graph.name = realname
    def edge(nameE,nameExt,dico): 
        for line in open(name+"_"+nameE+".txt").read().splitlines() :
                source, target,weight = [int(entier) for entier in line.split(" ") if entier != '']
                graph.add_edge(source, target, type = nameExt,**{nameExt : dico[weight]})
    edge("info","provides_information",{0: "I Do Not Know This Person", 1: "Very Infrequently", 2: "Infrequently", 3: "Somewhat Infrequently", 4: "Somewhat Frequently", 5:"Frequently",6:"Very Frequently"})
    edge("aware","aware_of_skill",{0: "I Do Not Know This Person", 1: "Strongly Disagree", 2: "Disagree", 3: "Somewhat Disagree", 4: "Somewhat Agree", 5: "Agree", 6: "Strongly Agree" })     
   
    def attribute(nameA,dico,realnameA=None) :
        if realnameA == None : realnameA = nameA
        for line in open(name+"-"+nameA+".txt").read().splitlines() :
            linesplit = line.split(" ")
            i=1
            for prop in [int(entier) for entier in linesplit if entier !=''] :
                graph.node[i][nameA] = dico[prop]
                i+=1
    attribute("tenure",{1: "1-12 months", 2: '13-36 months',3:"37-60 months",4:"61+ months"})
    attribute("orglevel",{1 : "Global Dept Manager", 2: "Local Dept Manager", 3: "Project Leader", 4: "Researcher"}, "organisational_level")
    attribute("location",{1: "Paris", 2: "Frankfurt", 3: "Warsaw", 4: "Geneva"})
    
    #import random
    #print random.choice(graph.nodes(data=True))   
    #print random.choice(graph.edges(keys=True,data=True))
    suivi(graph,realname+".gexf")
def terrorAttack():
    graph = nx.MultiDiGraph()
    name = "terrorist_attack"
    graph.name = name
    def attribute() :
        for line in open("TerrorAttack/"+name+".nodes").read().splitlines() :
            linesplit = line.split("\t")
            graph.add_node(linesplit[0])
            i= 0
            for prop in linesplit[1:-1] :
                graph.node[linesplit[0]]["attribute"+str(i)] = "present" if int(prop)==1 else "absent"
                i+=1
            graph.node[linesplit[0]]['label_type'] = linesplit[-1]
    attribute()
    
    import random
    print random.choice(graph.nodes(data=True))   
    
    def edges():
        for line in open("TerrorAttack/"+name+"_loc.edges").read().splitlines() :
                source, target = line.split(" ")
                graph.add_edge(source, target, key = "colocated_TA")
        for line in open("TerrorAttack/"+name+"_loc_org.edges").read().splitlines() :
                source, target = line.split(" ")
                graph.add_edge(source, target, key = "colocated_same_organization_TA")
    edges() 
    print random.choice(graph.edges(keys=True))
    suivi(graph,"TerrorAttack.gexf")
               
    

def vand():
    name = "vanDuijn_students"
    
    gend_prog = {}
    
    def attribute(graph,number) :
        i=0
        for line in open("cov"+str(number)+".dat").read().splitlines() :
               
            gen =  {1 : "male" , 2 :"female"}         
            prog =  {1 : "regular 4-year program" , 2 :"2-year program"}         
            smo =  {99 : "unknown",9 : "unknown",0 : "no" ,1:"no", 2 :"yes, at parties (social)",3:"1-3 cigarettes per day",4:"4-10 cigarettes per day", 5: "more than 10 p.d."}
            drug = {99 : "unknown",1:"no", 2: "yes, less than once a month", 3:"yes, 1-3 times p.m.", 4:"yes, 1-3 times per week", 5:"yes, more than 3 times p.w." }
            satisfaction = {99 : "unknown",1:"very dissatisfied", 2:"rather dissatisfied", 3:"not satisfied/not dissatisfied",4: "rather satisfied", 5: "very satisfied"}
            numberf = {99 : "unknown",1:"far too few", 2:"too few", 3:"exactly right number", 4:"too many", 5:"far too many"}
            part = {99 : "unknown",1:"none", 2:"approx. 25%", 3:"approx 50%", 4:"approx. 75%", 5:"100%"}
            
            
            linesplit = [int(numero) for numero in line.split(" ") if numero != '']
            print linesplit
            if number == 1 :
                gender,program,smoking,using = linesplit[1:5]
                out,movie,dinner,exerc,watch,coffee,relig,listening,politics,personal,fun,assoc,classes = linesplit[5:18]
                satis,numfriends,city = linesplit[18:21]
                gend_prog[i]=(gender,program)
            if number == 4 :
                gender,program = gend_prog[i]
                smoking,using = linesplit[1:3]
                out,movie,dinner,exerc,watch,coffee,relig,listening,politics,personal,fun,assoc,classes = linesplit[3:16]
                satis,numfriends,city = linesplit[16:19]
            
            graph.add_node(i,  gender = gen[gender], program = prog[program],
                           smoking = smo[smoking], soft_drugs= drug[using],going_out=out,
                           going_to_a_concert_or_movie = movie,having_dinner_at_home = dinner,
                           exercising_doing_sports = exerc,watching_sports = watch,
                           having_coffee_in_the_university_cafeteria = coffee,
                           religious_involvement_church_activities = relig,listening_to_pusic = listening,
                           discussing_politics = politics,discussing_personal_feelings = personal,
                           making_jokes_having_fun = fun,student_association_involvement_organizing_activities =assoc,
                           discussing_the_classes_or_study_program = classes,
                           satisfaction_with_number_of_real_friends_or_friends = satisfaction[satis],
                           too_few_many_friends = numberf[numfriends],
                            which_part_of_current_friends_live_in_the_city_of_groningen = part[city])        
            i=i+1
    def subgraph(number_time):
        subgraph = nx.DiGraph()
        subgraph.name = name+"-"+str(number_time)
        attribute_number = 1 if number_time <4 else 4
        attribute(subgraph,attribute_number)
        def type_rel(number) : 
            d =  {0: "unknown",1 : "Best friendship", 2 : "Friendship", 3 : "Friendly relationship", 4 :"Neutral relationship",5:"Troubled relationship" }         
            return d[number]
        source=0
        for line in open("t"+ str(number_time)+".dat").read().splitlines() :
            target = 0
            for number_of_messages in [int(number) for number in line.split(" ") if number != ''] :
                if  number_of_messages != 6 and number_of_messages != 9 and number_of_messages != 8 : 
                    keyhere = type_rel(number_of_messages)
                    subgraph.add_edge(source,target, type_relationship = keyhere)
                    
                target = target+1
            source = source+1
        return subgraph
    print subgraph(1).node
    print subgraph(1).edge[0]
    write(subgraph(1),name+"-1.gexf")
    write(subgraph(2),name+"-2.gexf")
    write(subgraph(3),name+"-3.gexf")
    write(subgraph(4),name+"-4.gexf")
    write(subgraph(5),name+"-5.gexf")
    net = create_first_slice(graphe,1)
    #test(net)
    #test(subgraph(0))
    net = add_following_slice(net, time(1), 1, 1,1)
    net = add_following_slice(net, time(2), 1, 1,2)
    test(net)
    suivi(net,"kapf.gexf",dynamic = True)
    

def infect():
    for f in os.listdir('30-infectious') :
        if os.path.isfile('30-infectious/'+f) :
            print f
            net =nx.read_gml('30-infectious/'+f)
            nx.write_gexf(net,'30-infectious/'+f.replace("gml","gexf")) 
 
def try_unweighted(net): 
    weighted = False
    for e in net.edges( data = True) :
        _,_,data =e
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
    return net
        
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


def bipartite_konect(graph_init,name,type0,type1,trois=None,quatre=None):
    graph = graph_init
    graph.name = name
    for line in (open("out."+graph.name).read().splitlines()) :
        if not line.startswith("%") :
            linesplit = [element for element in line.split(" ") if element != '']
            graph.add_node(type0+"-"+linesplit[0], type = type0)
            graph.add_node(type1+"-"+linesplit[1], type = type1)
            attributes = {}
            if trois : attributes.update({trois : linesplit[2]})
            if quatre : attributes.update({quatre : linesplit[3]})
            graph.add_edge(type0+"-"+linesplit[0], type1+"-"+linesplit[1],**attributes)
    suivi(graph,graph.name+".gexf")



def konect(graph_init,name,trois = None, quatre = None):
    graph = graph_init
    graph.name = name
    for line in (open("out."+graph.name).read().splitlines()) :
        if not line.startswith("%") :
            linesplit = [element for element in line.split(" ") if element != '']
            attributes = {}
            if trois : attributes.update({trois : linesplit[2]})
            if quatre : attributes.update({quatre : linesplit[3]})
            graph.add_edge(int(linesplit[0]), int(linesplit[1]),**attributes)    
    suivi(graph,graph.name+".gexf")

def netscience():
    net = nx.read_gml("netscience.gml")
    net.name = "netscience"
    for source,target in net.edges() :
        net[source][target]['weight'] = net[source][target]['value']
        del net[source][target]['value']
    suivi(net,"netscience.gml")

def condmat():
    net = nx.read_gml("cond-mat-2005.gml")
    net.name = "cond-mat-2005"
    for source,target in net.edges() :
        net[source][target]['weight'] = net[source][target]['value']
        del net[source][target]['value']
    suivi(net,"cond-mat-2005.gml")

def polblogs():
    net = nx.read_gml("polblogs.gml")
    net.name = "polblogs"
    suivi(net,"polblogs.gml")

def jazz():
    net = read_pajek("jazz.net")
    net.name = "jazz"
    mapy = {oldkey:int(oldkey) for oldkey in net}
    net = nx.relabel_nodes(net,mapy)
    suivi(net,"jazz.net") 
       

                 
for f in os.listdir('.') :
    if os.path.isfile(f) :
        net = None
        if "e.paj" in f :
            #net = read_pajek(f)
            #mapy = {oldkey:int(oldkey) for oldkey in net}
            #net = nx.relabel_nodes(net,mapy)
            # for node in net.node :
                #print node
                pass
        if ".dat" in f :
            #net = read_ucinet_bimatrix("galas", "CEO", "club")
            #for node in net.nodes(data = True) :
                #print node
            #for edge in net.edges() :
                #print edge
            #suivi(net,f)
            pass
        
       
        if ".txt" in f :
            #print f
            #net = nx.read_edgelist(f,create_using=nx.DiGraph(),nodetype=int)
            #suivi(net,f)
            pass
       

#netscience()
#jazz()
#polblogs()
#condmat()
#email()
#PGP()
#mathscinet()
#dl_advogato()
#bipartite_konect(nx.MultiGraph(),"dbpedia-country", "entity", "country")
#bipartite_konect(nx.Graph(),"amazon-ratings", "user", "product",trois ="weight",quatre ="timestamp")
#bipartite_konect(nx.Graph(),"opsahl-collaboration", "author", "paper")
#konect(nx.MultiDiGraph(),"advogato-konect",trois="weight")
#konect(nx.DiGraph(),"amazon0601")
#konect(nx.Graph(),"ca-AstroPh")
#konect(nx.MultiGraph(),"ca-cit-HepPh",quatre = "timestamp")
#konect(nx.MultiGraph(),"ca-cit-HepTh",quatre = "timestamp")
#konect(nx.MultiDiGraph(),"cit-HepTh")
#konect(nx.MultiDiGraph(),"hep-th-citations")
#konect(nx.DiGraph(),"web-BerkStan")
#konect(nx.MultiDiGraph(),"zhishi-baidu-internallink")
#konect(nx.MultiDiGraph(),"zhishi-baidu-relatedpages")
#konect(nx.MultiGraph(),"arenas-meta")
#konect(nx.Graph(),"as-caida20071105")
#konect(nx.Graph(),"loc-brightkite_edges")
#konect(nx.MultiDiGraph(),"citeseer")
#konect(nx.MultiDiGraph(),"zhishi-zhwiki-internallink")
#konect(nx.Graph(),"roadNet-CA")
#bipartite_konect(nx.MultiGraph(),"bibsonomy-2ti", "tag", "publication",quatre ="timestamp")
#bipartite_konect(nx.MultiGraph(),"bibsonomy-2ui", "user", "publication",quatre ="timestamp")
#bipartite_konect(nx.MultiGraph(),"bibsonomy-2ut", "user", "tag",quatre ="timestamp")
#bipartite_konect(nx.Graph(),"bookcrossing_full-rating", "user", "book")
#bipartite_konect(nx.Graph(),"bookcrossing_rating", "user", "book",trois = "rating")
#bkfrat()
#bkham()
#bktec()
#galas()
#EIES("EIES")
#stu98()
#lazega()
#siena("EIES")
#siena2("kapf")
#VRND()
facebook(0)
facebook(107)
facebook(348)
facebook(414)
facebook(686)
facebook(698)
facebook(1684)
facebook(1912)
facebook(3437)
facebook(3980)
#twitter("olympics")
#twitter("football")
#twitter("rugby")
#twitter("politicsuk")
#kapf()
#vand()
#infect()
#oclinks()
#kapf()
"""
csphd()
dining()
drug_net()
Flying_teams()
FauxMesaHigh()
Galesburg()
gama()
knokbur()
literature_1976()
mexican_power()
ModMath()
NewcombFraternity()
SanJuanSur()
Sampson()
Scotland()
Stranke94()
strike()
szcid()
taro()
thuroff()
trade()
"""
Www()
#pin()
#autonomous()
#
#terrorAttack()
#mathscinet()
#consulting()
#manufacturing()
#southern()
#YG()
#db()
#record()
#flickr()
#wall()
#eu()
##slash()
#munmun()
#wikiconflict()
#tribe()
#hamster()
#wiksigned()
#mun_twitt()
#cat()
#blogcatalog3()
#douban() 
#Dining_partner()
#centrality() 
#sanjuan("SanJuanSur2.paj")
#stud_gov("Student_government.paj")           
#scotland("Scotland.paj")            
#cities("da6+.net")            
#EIES("EIES")
#stu98()
#lazega()
#siena("EIES")
##siena2("kapf")
#zoo("slashdot-zoo")
#VRND("VRND.txt")
#livemocha("BlogCatalog",nx.Graph())
#livemocha("BuzzNet",nx.DiGraph())
#livemocha("Delicious",nx.DiGraph())
#livemocha("Digg",nx.DiGraph())
#livemocha("Douban",nx.DiGraph())
#livemocha("Flickr",nx.Graph())
#livemocha("Flixster",nx.DiGraph())
#livemocha("Foursquare",nx.DiGraph())
#livemocha("Friendster",nx.Graph())
#livemocha("Hyves",nx.Graph())
#livemocha("Last.fm",nx.DiGraph())
#livemocha("LiveJournal",nx.DiGraph())
#livemocha("Livemocha",nx.Graph())