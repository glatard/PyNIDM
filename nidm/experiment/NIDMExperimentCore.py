import os,sys
import uuid
from rdflib.namespace import XSD
from types import *
#import rdflib as rdf
from prov.model import ProvDocument

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Common import Constants

from prov.model import *

class NIDMExperimentCore(object):
    """Base-class for NIDM-Experimenent

    Typically this class is not instantiated directly.  Instantiate one of the child classes such as
    NIDMExperimentInvestigation, NIDMExperimentImaging, NIDMExperimentAssessments, etec.

    @author: David Keator <dbkeator@uci.edu>
    @copyright: University of California, Irvine 2017

    """
    language = 'en'
    def __init__(self):
        """
        Default constructor, loads empty graph and namespaces from NIDM/Scripts/Constants.py
        """
        #make a local copy p_graph PROV document with namespaces already bound
        self.graph = Constants.p_graph
        #make a local copy of the namespaces
        self.namespaces = Constants.namespaces

    #class constructor with user-supplied PROV document/graph, namespaces from Constants.py
    @classmethod
    def withGraph(self,graph):
        """
        Alternate constructor, loads user-supplied graph and default namespaces from NIDM/Scripts/Constants.py

        Keyword arguments:
            graph -- an rdflib.Graph object
        """
        self.graph = graph
        self.namespaces = {}
        #bind namespaces to self.graph
        for name, namespace in self.namespaces.items():
            self.graph.add_namespace(name, namespace)

    #class constructor with user-supplied graph and namespaces
    @classmethod
    def withGraphAndNamespaces(self,graph,namespaces):
        """
        Alternate constructor, loads user-supplied graph and binds user-supplied namespaces

        :param graph: an rdflib.Graph object
        :param namespaces: python dictionary {namespace_identifier, URL}
        :return: none
        """


        self.graph = graph
        self.namespaces = namespaces
        #bind namespaces to self.graph
        for name, namespace in self.namespaces.items():
            self.graph.add_namespace(name, namespace)

    def getGraph(self):
        """
        Returns rdflib.Graph object
        """
        return self.graph

    def getNamespace(self):
        """
        Returns namespace dictionary {namespace_id, URL}
        """
        return self.namespaces

    def addNamespace(self, prefix, namespace):
        """
        Adds namespace to self.graph
        :param prefix: namespace identifier
        :param namespace: namespace URL
        :return: none
        """
        self.graph.add_namespace(prefix, namespace)

    def safe_string(self, string):
        return string.strip().replace(" ","_").replace("-", "_").replace(",", "_").replace("(", "_").replace(")","_")\
            .replace("'","_").replace("/", "_")

    def getUUID (self):
        return str(uuid.uuid1())

    def getDataType(self,var):
        if type(var) is IntType:
            return XSD_INTEGER
        elif type(var) is LongType:
            return XSD_LONG
        elif type(var) is FloatType:
            return XSD_FLOAT
        elif (type(var) is StringType):
            return XSD_STRING
        elif (type(var) is UnicodeType):
            return XSD_STRING
        elif (type(var) is list):
            return list
        else:
            print "datatype not found..."
            return None
    def addLiteralAttribute(self, id, pred_namespace, pred_term, object):
        """
        Adds generic literal and inserts into the graph
        :param id: subject identifier/URI
        :param pred_namespace: predicate namespace URL
        :param pred_term: predidate term to associate with tuple
        :param object: literal to add as object of tuple
        :return: none
        """
        #figure out datatype of literal
        datatype = self.getDataType(object)
        #print "datatype = " + datatype
        #figure out if predicate namespace is defined, if not, return predicate namespace error
        try:
            if (datatype != None):
                id.add_attributes({self.namespaces[pred_namespace][pred_term]: Literal(object, datatype=datatype)})
            else:
                id.add_attributes({self.namespaces[pred_namespace][pred_term]: Literal(object)})
        except (KeyError,),e:
            print "\nPredicate namespace identifier \"" + str(e).split("'")[1] + "\" not found!"
            print "Use addNamespace method to add namespace before adding literal attribute"
            print "No attribute has been added \n"
    def addListAttribute(self,id,pred_namespace,pred_term, object):
        """
        Adds generic literal to subject [id] and inserts into the graph
        :param id: subject identifier/URI
        :param pred_namespace: predicate namespace URL
        :param pred_term: predidate term to associate with tuple
        :param object: literal to add as object of tuple
        :return: none
        """
        #convert list to string
        str1 = ''.join(object)
        datatype = XSD.string
        #self.graph.add((id, self.namespaces[pred_namespace][pred_term], rdf.Literal(str1, datatype=datatype)))
        id.add_attributes({self.namespaces[pred_namespace][pred_term]: Literal(str1)})
    def addURIRef(self,id,pred_namespace,pred_term, object):
        """
        Adds URIRef attribute and inserts into the graph
        :param id: subject identifier/URI
        :param pred_namespace: predicate namespace URL
        :param pred_term: predidate term to associate with tuple
        :param object: URIRef to add as object of tuple
        :return: none
        """
        id.add_attributes({self.namespaces[pred_namespace][pred_term]: Literal(object, XSD_ANYURI)})
    def addPerson(self):
        """
        Generic add prov:Person, use addLiteralAttribute to add more descriptive attributes
        :return: URI identifier of this subject
        """
        #Get unique ID
        uuid = self.getUUID()
        #add to graph
        p1=self.graph.agent(self.namespaces["nidm"][uuid])
        return p1
    def wasAssociatedWith(self, subject, object):
        """
        Generic prov:wasAssociatedWith function to associate the subject and objects together in graph
        :param subject: URI of subject (e.g. person)
        :param object: URI of object (e.g. investigation)
        :return: URI identifier of this subject
        """
        self.graph.add((subject, self.namespaces["prov"]["wasAssociatedWith"], object))
    def serializeTurtle(self):
        """
        Serializes graph to Turtle format
        :return: text of serialized graph in Turtle format
        """
        return self.graph.serialize(None, format='rdf', rdf_format='ttl')
    def serializeJSONLD(self):
        """
        Serializes graph to JSON-LD format
        :return: text of serialized graph in JSON-LD format
        """
        return self.graph.serialize(format='json-ld', indent=4)
    def __str__(self):
        return "NIDM-Experiment Base Class"
