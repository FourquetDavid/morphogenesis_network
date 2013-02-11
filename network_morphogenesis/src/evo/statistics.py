'''
Created on 15 nov. 2012 

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
''' 

""" 
this class inherits from pyevovle.DBAdapters.DBBaseAdaoter. It computes and stores statistics during genetic algorithm processing.
       

"""
import pyevolve as py
import pyevolve.DBAdapters as db
import logging
from collections import defaultdict
import operator 


class StatisticsInTxt(db.DBBaseAdapter) :
    ''' This class inherits from DBAdpater in pyevolve, it will be called at each generation of the genetic algorithm
    and print stats in a txt file and print it on screen
    '''
       
    def __init__(self, filename=None, identify=None,
                frequency=py.Consts.CDefCSVFileStatsGenFreq, reset=True):
        """ The creator of StatisticsInTxt Class """

        db.DBBaseAdapter.__init__(self, frequency, identify)
        self.filename = filename
        self.file = None
        self.reset = reset

    def __repr__(self):
        """ The string representation of adapter """
        ret = "StatisticsInTxt DB Adapter [File='%s', identify='%s']" % (self.filename, self.getIdentify())
        return ret

    def open(self, ga_engine):
        """ Open the Txt file or creates a new file
        """

        logging.debug("Opening the txt file to dump statistics [%s]", self.filename)
        if self.reset: open_mode = "w"
        else: open_mode = "a"
        self.fHandle = open(self.filename, open_mode)
        self.file = open(self.filename,open_mode)
        
        
        self.file.write("number of generations = %s \n"%ga_engine.getGenerations())
        self.file.write("evaluation_method = %s \n"%ga_engine.getPopulation().oneSelfGenome.getParam("evaluation_method"))
        self.file.write("network_type = %s \n"%ga_engine.getPopulation().oneSelfGenome.getParam("network_type"))
        self.file.write("tree_type = %s \n"%ga_engine.getPopulation().oneSelfGenome.getParam("tree_type"))
        self.file.write("selector = %s \n"%ga_engine.selector)
        self.file.write("multiprocessing = %s \n"%ga_engine.getPopulation().multiProcessing[0])
        
        print "number of generations = %s"%ga_engine.getGenerations()
        print "evaluation_method = %s"%ga_engine.getPopulation().oneSelfGenome.getParam("evaluation_method")
        print "network_type = %s"%ga_engine.getPopulation().oneSelfGenome.getParam("network_type")
        print "tree_type = %s"%ga_engine.getPopulation().oneSelfGenome.getParam("tree_type")
        print "selector = %s"%ga_engine.selector
        print "multiprocessing = %s"%ga_engine.getPopulation().multiProcessing[0]
        
    def close(self):
        """ Closes the Txt file  """
        logging.debug("Closing the txt file [%s]", self.filename)
        self.file.close()

    def commitAndClose(self):
        """ Commits and closes """
        self.close()

    def insert(self, ga_engine):
    
        """ writes population statistics and the 5 best elements"""
        self.file.write("#####      Generation  {numero}   ###########\n".format(numero=ga_engine.getCurrentGeneration()))
        print "#####      Generation  {numero}   ###########".format(numero=ga_engine.getCurrentGeneration())
        print ga_engine.getStatistics()
        self.file.write(ga_engine.getStatistics().__repr__())
    
        pop = ga_engine.getPopulation()
        for i in xrange(5) :
            self.file.write("######### Arbre num {numero} ###########\n".format(numero=i))
            print "######### Arbre num {numero} ###########".format(numero=i)
            tree = pop.bestFitness(i)
            self.file.write(str(tree.getRawScore()))
            print tree.getRawScore()
            self.file.write(tree.getTraversalString())
            print tree.getTraversalString()
        
 
 
 
 
 
 
 
 
list_of_functions_number = defaultdict(int)
list_of_functions_sum = defaultdict(int) 
count = 0

class StatisticsQualityInTxt(py.DBAdapters.DBBaseAdapter) :
    ''' This class inherits from DBAdpater in pyevolve, it will be called at each generation of the genetic algorithm
    and print stats in a txt file and print it on screen
    '''
     
     
    def __init__(self,current_variable, filename=None, identify=None,
                frequency=py.Consts.CDefCSVFileStatsGenFreq, reset=True):
        """ The creator of StatisticsInTxt Class """
        global count
        
        py.DBAdapters.DBBaseAdapter.__init__(self, frequency, identify)
        self.filename = filename
        self.file = None
        self.reset = reset

    def __repr__(self):
        """ The string representation of adapter """
        ret = "StatisticsQualityInTxt DB Adapter [File='%s', identify='%s']" % (self.filename, self.getIdentify())
        return ret

    def open(self, ga_engine):
        """ Open the Txt file or creates a new file
        """

        logging.debug("Opening the txt file to dump statistics [%s]", self.filename)
        if self.reset: open_mode = "w"
        else: open_mode = "a"
        self.fHandle = open(self.filename, open_mode)
        self.file = open(self.filename,open_mode)
        
    def close(self):
        """ Closes the Txt file  """
        logging.debug("Closing the txt file [%s]", self.filename)
        global list_of_functions_number
        global list_of_functions_sum
        global count
        
        count+=1
        if count == 10 :
            count = 0
            list_of_functions_quality ={}
            list_of_functions_product ={}
            list_of_functions_rapport ={}
            
            for key in list_of_functions_number : 
                list_of_functions_quality[key] = list_of_functions_sum[key] / list_of_functions_number[key]
            
            maximum = max(list_of_functions_quality.values())
            for key in list_of_functions_quality :
                list_of_functions_quality[key] = maximum - list_of_functions_quality[key]
                list_of_functions_product[key] = list_of_functions_quality[key]*list_of_functions_number[key]
                list_of_functions_rapport[key] = list_of_functions_number[key]*list_of_functions_number[key]/list_of_functions_sum[key]
             
            sorted_quality = sorted(list_of_functions_quality.iteritems(), key=operator.itemgetter(1))[-8:]
            sorted_product = sorted(list_of_functions_product.iteritems(), key=operator.itemgetter(1))[-8:]
            sorted_rapport = sorted(list_of_functions_rapport.iteritems(), key=operator.itemgetter(1))[-8:]
            
            print "\n### Sorted by Quality ####"
            for (key, _) in sorted_quality :
                print " ".join(["variable :",key,"number of apparitions =",str(list_of_functions_number[key]),"quality =", str(list_of_functions_quality[key])]) 
            print "\n#####Sorted by Quantity*Quality#########"
            for (key, _) in sorted_product :
                print " ".join(["variable :",key,"number of apparitions =",str(list_of_functions_number[key]),"quality =", str(list_of_functions_quality[key])]) 
            print "\n######Sorted by Rate######"
            for (key, _) in sorted_rapport :
                print " ".join(["variable :",key,"number of apparitions =",str(list_of_functions_number[key]),"quality =", str(list_of_functions_quality[key])]) 
            
            
            self.file.write( "\n### Sorted by Quality ####\n")
            for (key, _) in sorted_quality :
                self.file.write(" ".join(["variable :",key,"number of apparitions =",str(list_of_functions_number[key]),"quality =", str(list_of_functions_quality[key]),"\n"]))
            self.file.write("\n#####Sorted by Quantity*Quality#########\n")
            for (key, _) in sorted_product :
                self.file.write(" ".join(["variable :",key,"number of apparitions =",str(list_of_functions_number[key]),"quality =", str(list_of_functions_quality[key]),"\n"]))
            self.file.write( "\n######Sorted by Rate######\n")
            for (key, _) in sorted_rapport :
                self.file.write( " ".join(["variable :",key,"number of apparitions =",str(list_of_functions_number[key]),"quality =", str(list_of_functions_quality[key]),"\n"])) 
            
            list_of_functions_number.clear()
            list_of_functions_sum.clear()    
        self.file.close()
        
        
    def commitAndClose(self):
        """ Commits and closes """
        self.close()

    def insert(self, ga_engine):
        global list_of_functions_number
        global list_of_functions_sum
       
    
        pop = ga_engine.getPopulation()
        for element in pop :
            score = element.getRawScore()
            for node in element.getAllNodes() :
                if node.isLeaf() :
                    variable = node.getData()[1]
                    list_of_functions_number[variable]+=1
                    list_of_functions_sum[variable]+=score
                #else : 
                    #variable = node.getData()
                    #list_of_functions_number[variable]+=1 
                    #list_of_functions_sum[variable]+=score
 
 
 
 
 
 
 
 
 
 
 
 
######### Useless now #########    
   
class StatisticsInCSV(py.DBAdapters.DBBaseAdapter) :
    ''' DBFileCSV Class - Adapter to dump statistics in CSV format
            
            Inheritance diagram for :class:`DBAdapters.DBFileCSV`:
            
            .. inheritance-diagram:: DBAdapters.DBFileCSV
            
            Example:
               >>> adapter = DBFileCSV(filename="file.csv", identify="run_01",
                                       frequency = 1, reset = True)
            
               :param filename: the CSV filename
               :param identify: the identify of the run
               :param frequency: the generational dump frequency
               :param reset: if is True, the file old data will be overwrite with the new
            
            .. versionadded:: 0.6
               Removed the stub methods and subclassed the :class:`DBBaseAdapter` class.
        
    '''         
    def __init__(self, filename=py.Consts.CDefCSVFileName, identify=None,
                frequency=py.Consts.CDefCSVFileStatsGenFreq, reset=True):
        """ The creator of DBFileCSV Class """

        py.DBAdapters.DBBaseAdapter.__init__(self, frequency, identify)
      
        self.csvmod = None
        self.filename = filename
        self.csvWriter = None
        self.fHandle = None
        self.reset = reset

    def __repr__(self):
        """ The string representation of adapter """
        ret = "DBFileCSV DB Adapter [File='%s', identify='%s']" % (self.filename, self.getIdentify())
        return ret

    def open(self, ga_engine):
        """ Open the CSV file or creates a new file
        :param ga_engine: the GA Engine
        .. versionchanged:: 0.6
        The method now receives the *ga_engine* parameter.
        """
        if self.csvmod is None:
            logging.debug("Loading the csv module...")
            self.csvmod = py.Util.importSpecial("csv")

        logging.debug("Opening the CSV file to dump statistics [%s]", self.filename)
        if self.reset: open_mode = "w"
        else: open_mode = "a"
        self.fHandle = open(self.filename, open_mode)
        self.csvWriter = self.csvmod.writer(self.fHandle, delimiter=';')

    def close(self):
        """ Closes the CSV file handle """
        logging.debug("Closing the CSV file [%s]", self.filename)
        if self.fHandle:
            self.fHandle.close()

    def commitAndClose(self):
        """ Commits and closes """
        self.close()

    def insert(self, ga_engine):
        """ Inserts the stats into the CSV file
        """
        stats = ga_engine.getStatistics()
        generation = ga_engine.getCurrentGeneration()
        line = [self.getIdentify(), generation]
        line.extend(stats.asTuple())
        self.csvWriter.writerow(line)


