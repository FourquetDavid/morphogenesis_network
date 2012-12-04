'''
Created on 15 nov. 2012 

@author: David
inspired by Telmo Menezes's work : telmomenezes.com
''' 

""" 
contains one main function :

*deal_with_stats : takes a genetic algorithm engine and print or write in a file the relevant statistics
        
    

"""
import pyevolve as py
import logging

class StatisticsInTxt(py.DBAdapters.DBBaseAdapter) :
    ''' This class inherits from DBAdpater in pyevolve, it will be called at each generation of the genetic algorithm
    and print stats in a txt file and print it on screen
    '''
       
    def __init__(self, filename=None, identify=None,
                frequency=py.Consts.CDefCSVFileStatsGenFreq, reset=True):
        """ The creator of StatisticsInTxt Class """

        py.DBAdapters.DBBaseAdapter.__init__(self, frequency, identify)
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
        self.file.write("selector = %s \n"%ga_engine.selector)
        self.file.write("multiprocessing = %s \n"%ga_engine.getPopulation().multiProcessing[0])
        
        print "number of generations = %s"%ga_engine.getGenerations()
        print "evaluation_method = %s"%ga_engine.getPopulation().oneSelfGenome.getParam("evaluation_method")
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
            self.file.write(str(tree.getFitnessScore()))
            print tree.getFitnessScore()
            self.file.write(tree.getTraversalString())
            print tree.getTraversalString()
        
 
 
 
 
 
 
 
 
 
 
 
######### Useless for instance #########    
   
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


