#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from bulbs.model import Node
from graphalchemy.repository import BulbsNodeRepository
from bulbs.model import Relationship
from graphalchemy.repository import BulbsRelationshipRepository

from bulbs.model import STRICT


# ==============================================================================
#                                    RELATIONS
# ==============================================================================

class Relationship(Relationship):
    """ Thin wrapper around the base bulbs.model.Relationship class. It is essentially
    designed to provide more flexibility in the coding.
    
    >>> from my.models.nodes import WebsiteHostsPage
    >>> hosts = WebsiteHostsPage(since=2013)
    >>> hosts.accessible = True
    >>> hosts.set_inV(website)
    >>> hosts.set_outV(page)
    >>> ogm.add(hosts)
    >>> ogm.flush()
    """
    
    def __init__(self, *args, **kwargs):
        """ Overwrites the bulbs.element.Element __init__ method in order to 
        be able to create an Element without passing the client.
        """
        self._outV_vertex = None
        self._inV_vertex = None
        
        # Load keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Replace the "client" argument if not provided
        if args is ():
            args = (None, )
                
        # Init the Element with the regular method
        super(Relationship, self).__init__(*args)
    
    
    def set_outV(self, vertex):
        self._outV_vertex = vertex
        return self
    
    
    def set_inV(self, vertex):
        self._inV_vertex = vertex
        return self
    
    
    @classmethod 
    def get_proxy_class(cls):
        return BulbsRelationshipRepository
    
    
    def __unicode__(self):
        """ Overwrites the bulbs.element.Element __unicode__ method in order to 
        prevent it to crash when the client is not initialized.
        
        :returns: str -- A human-readable representation of the Node.
        """
        if self._result is None:
            return '<%s: %s>' % (self.__class__.__name__, 'Not persisted')
        return super(Relationship, self).__unicode__()
    
    

# ==============================================================================
#                                      NODES
# ==============================================================================

class VirtualNode(object):
    """ A VirtualNode is the image of the node that is supposed to exist in the
    database, but has not been loaded. It will be merged or retrieved at query
    time.
    """
    
    def __init__(self, *args, **kwargs):
        self.eid = None
        for arg in args:
            for key in arg:
                setattr(self, key, arg[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
    


class Node(Node):
    """ Thin wrapper around the base bulbs.model.Node class. It is essentially
    designed to provide more flexibility in the coding.
    
    Model declaration (properties and relations)
    >>> class Page(Node):
    ...     element_type = 'Page'
    ...     title = String()
    ...     url = Url()
    ...     def isHostedBy(self):
    ...         return self._relation('hosts', 'in', unique=True)
    ...     def isHostedBy_add(self, relation, node):
    ...         return self._relation_add('hosts', 'in', relation, node)
    ...     def isHostedBy_del(self, relation):
    ...         return self._relation_del('hosts', 'in', relation)
    
    Model instanciation and persistence
    >>> page = Page(title="AllRecipes")
    >>> page.url = 'http://www.allrecipes.com/page/2'
    >>> ogm.add(page)
    >>> ogm.flush()
    
    Relation interaction (lazy-load + caching, addition, deletion)
    >>> page.isHostedBy()
    >>> page.isHostedBy_add(hosted_relation, website_node)
    >>> page.isHostedBy_del(hosted_relation)
    >>> ogm.add(page)
    >>> ogm.flush()
    """
    
    """ Use strict mode in order to limit the items persisted in the database.
    """
    __mode__ = STRICT
    
    
    def __init__(self, *args, **kwargs):
        """ Overwrites the bulbs.element.Element __init__ method in order to 
        be able to create an Element without passing the client.
        """
        
        # Load keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Replace the "client" argument if not provided
        if args is ():
            args = (None, )
                
        # Init the Element with the regular method
        super(Node, self).__init__(*args)
    
    
    @classmethod 
    def get_proxy_class(cls):
        return BulbsNodeRepository
    
    
    def __unicode__(self):
        """ Overwrites the bulbs.element.Element __unicode__ method in order to 
        prevent it to crash when the client is not initialized.
        
        :returns: str -- A human-readable representation of the Node.
        """
        if self._result is None:
            return '<%s: %s>' % (self.__class__.__name__, 'Not persisted')
        return super(Node, self).__unicode__()
    
    
    def _relation(self, name, direction, unique=False):
        """ Temporary method for relations management. It allows to quickly wrap
        the calls on the different relations for lazy-loading and caching.
        
        It uses a cache field _cache_{in|out}_{name} to store the relationship
        data.
        
        With the above example :
        >>> class Page(Node)
        ...     # ...
        ...     def isHostedBy(self):
        ...         return self._relation('hosts', 'in', unique=True)
        
        :param name: The name of the relation.
        :type name: str
        :param direction: Whether the relation is inbound, outbound or both.
        :type direction: str (in|out|both)
        :returns: A dictionnary which keys are the relations and values are the
                  related nodes.
        :rtype: dict<graphalchemy.model.Relationship, graphalchemy.model.Node> 
        """
        cache_name = '_cache'+'_'+direction+'_'+name
        
        # If the entity has not been loaded
        if self._client is None:
            # If there is no cache, create it
            if not hasattr(self, cache_name):
                setattr(self, cache_name, {})
            # If there is cache, use it
            return getattr(self, cache_name)
                
        # If the entity has been loaded
        else:
            # If there is no cache
            if not hasattr(self, cache_name):
                # Retrieve edges and vertices from the database
                if direction == 'out':
                    edges = self.outE(name),
                    vertices = self.outV(name)
                elif direction == 'in':
                    edges = self.outE(name),
                    vertices = self.outV(name)
                elif direction == 'both':
                    edges = self.bothE(name),
                    vertices = self.bothV(name)
                else:
                    raise Exception('Unknown direction : '+direction)
                    
                # Fill up cache
                if len(edges) != len(vertices):
                    raise Exception('Vertices and edges mismatch')
                if len(edges):
                    dic = dict(zip(edges, vertices))
                else:
                    dic = {}
                setattr(self, cache_name, dic)
            
            # If there is cache, return it
            return getattr(self, cache_name)


    def _relation_add(self, name, direction, relation, node):
        """ Temporary method for relations addition. It allows to quickly wrap
        the calls on the different relations for relation addition.
        
        With the above example :
        >>> class Page(Node)
        ...     # ...
        ...     def isHostedBy_add(self, relation, node):
        ...         return self._relation_add('hosts', 'in', relation, node)
        
        Note that this does not persist the relation nor the node unless explicitely
        specified by the user.
        
        :param name: The name of the relation.
        :type name: str
        :param direction: Whether the relation is inbound, outbound or both.
        :type direction: str
        :param relation: The relation to add.
        :type relation: graphalchemy.model.Relationship
        :param node: The node to add.
        :type node: graphalchemy.model.Node
        :returns: This node itself.
        :rtype: graphalchemy.model.Node
        """
        cache_name = '_cache'+'_'+direction+'_'+name
        relations = self._relation(name, direction)
        if relation in relations:
            return self
        relations[relation] = node
        setattr(self, cache_name, relations)
        return self
            
        
    def _relation_del(self, name, direction, relation):
        """ Temporary method for relations deletion. It allows to quickly wrap
        the calls on the different relations for relation deletion.
        
        With the above example :
        >>> class Page(Node)
        ...     # ...
        ...     def isHostedBy_del(self, relation):
        ...         return self._relation_del('hosts', 'in', relation)
        
        Note that this does not remove the relation nor the node unless explicitely
        specified by the user.
        
        :param name: The name of the relation.
        :type name: str
        :param direction: Whether the relation is inbound, outbound or both.
        :type direction: str
        :param relation: The relation to delete.
        :type relation: graphalchemy.model.Relationship
        :returns: This node itself.
        :rtype: graphalchemy.model.Node
        """
        cache_name = '_cache'+'_'+direction+'_'+name
        relations = self._relation(name, direction)
        if relation not in relations:
            return self
        del relations[relation]
        setattr(self, cache_name, relations)
        return self
        