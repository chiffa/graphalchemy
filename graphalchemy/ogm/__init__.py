#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                   IMPORTS
# ==============================================================================

from graphalchemy.repository import BulbsNodeRepository
from graphalchemy.repository import BulbsRelationshipRepository

# Bulbs
from bulbs.model import Node
from bulbs.model import Relationship

# System
import importlib


# ==============================================================================
#                               IMPLEMENTATION
# ==============================================================================

class BulbsObjectManager(object):
    """ This is a wrapper around the Titan APIs designed to provide a clean an 
    uniformized interface for model persistence in graphs.
    
    Loading the OGM :
    >>> ogm = BulbsObjectManager("http://localhost:8182/graphs", "graph")
    
    Querying with simple filters :
    >>> websites = ogm.repository('Website').filter(url='http://www.cuisineaz.com')
    
    Deleting entities :
    >>> website_del = websites[0]
    >>> ogm.delete(website_old)
    >>> ogm.commit()
    >>> ogm.flush()
    
    Updating entities :
    >>> website_upd = websites[1]
    >>> website_upd.name = 'CuisineAZ - Forum'
    >>> ogm.add(website_upd)
    >>> ogm.commit()
    >>> ogm.flush()
    
    Creating entities :
    >>> website_add = Website(name="Marmiton", url="http://www.marmiton.org")
    >>> ogm.add(website_new)
    >>> ogm.commit()
    >>> ogm.flush()
    
    Performing lazy-loaded traversals :
    >>> website_upd.pages()
    """
    
    def __init__(self, uri, database, logger=None, model_paths=[]):
        """ Connects to the database instance through a Rexster client, and 
        initializes a session and identity map.
        
        :param uri: The URI to the database.
        :type uri: str
        :param database: The database name.
        :type database: str
        :param logger: A logger instance.
        :type logger: logging
        :param model_paths: The fully qualified path to your models.
        :type model_paths: list
        """
        self.logger = logger
        
        # Init connection
        from bulbs.config import Config
        # config = Config(uri)
        from bulbs.titan import TitanClient
        self.client = TitanClient(db_name=database)
        from bulbs.titan import Graph
        self.graph = Graph(self.client.config)
        
        # Init identity map
        self.session_delete = []
        self.session_add = []
        self._repositorys = {}
        self.model_paths = model_paths

    
    def repository(self, repository_name):
        """ Returns the repository corresponding to a given model.
        
        :param repository_name: The name of the repository to load.
        :type repository_name: str
        :returns: graphalchemy.repository.BulbsNodeRepository -- the requested 
        repository, loaded with the model metadata.
        """
        
        if repository_name in self._repositorys:
            return self._repositorys[repository_name]
        
        found = False
        for module_name in self.model_paths:
            module = importlib.import_module(module_name)
            if repository_name not in module.__dict__:
                continue
            found = True
            break
        
        if not found:
            raise Exception('Repository not found.')
        
        # Register proxy and metdata
        model = module.__dict__[repository_name]
        
        # Build repository
        if issubclass(model, Node):
            repository = BulbsNodeRepository(
                model, 
                self.client, 
                graph=self.graph, 
                logger=self.logger
            )
        elif issubclass(model, Relationship):
            self.graph.add_proxy(repository_name, model)
            repository = BulbsRelationshipRepository(
                model, 
                self.client, 
                graph=self.graph, 
                logger=self.logger
            )
        else:
            raise Exception('Element class seems not to be Node nor Relationship.')

        self._repositorys[repository_name] = repository
        return repository


    def add(self, entity):
        """ Adds an entity to the current session for bulk save / update.
        
        :param entity: The entity to add to the session.
        :type entity: bulbs.model.Node, bulbs.model.Relationship
        :returns: graphalchemy.ogm.BulbsObjectManager -- this object itself.
        """
        found = False
        for entity_add in self.session_add:
            if entity_add is entity:
                found = True
                break
        if not found:
            self.session_add.append(entity)
        
        for entity_delete in self.session_delete:
            if entity_delete is entity:
                self.session_delete.remove(entity)
                break
        return self


    def delete(self, entity):
        """ Schedules an entity for removal in the database.
        
        :param entity: The entity to add to the session.
        :type entity: bulbs.model.Node, bulbs.model.Relationship
        :returns: graphalchemy.ogm.BulbsObjectManager -- this object itself.
        """
        found = False
        for entity_delete in self.session_delete:
            if entity is entity_delete:
                found = True
                break
        if not found:
            self.session_add.append(entity)
        for entity_add in self.session_add:
            if entity is entity_add:
                self.session_add.remove(entity)
        return self


    def commit(self):
        """ Prepares the gremlin queries, start a transaction.
        
        :returns: graphalchemy.ogm.BulbsObjectManager -- this object itself.
        """
        self.query('g.commit()', {})
        return self


    def flush(self):
        """ Commits the transaction, flushes the result to the database.
        
        :returns: graphalchemy.ogm.BulbsObjectManager -- this object itself.
        """
        
        # We need to save nodes first
        for entity in self.session_add:
            if isinstance(entity, Node):
                self._log("Flushed "+str(entity))
                self._flush_one_node(entity)
        for entity in self.session_add:
            if isinstance(entity, Relationship):
                self._log("Flushed "+str(entity))
                self._flush_one_relation(entity)
        # Do not reset the session, we keep them tracked            
        # self.session_add = []
        
        # We need to delete nodes first
        for entity in self.session_delete:
            if entity._client is None:
                continue
            if isinstance(entity, Relationship):
                self._log("Deleted "+str(entity))
                entity._edges.delete(entity.eid)
        for entity in self.session_delete:
            if entity._client is None:
                continue
            if isinstance(entity, Node):
                self._log("Deleted "+str(entity))
                entity._vertices.delete(entity.eid)
        # All deleted entities are detached
        self.session_delete = []
        
        return self
    
    
    def _flush_one_node(self, entity):
        # Regular case, the entity is either loaded or created via repository
        if entity._client is not None:
            entity.save()
            return self
            
        # Case where the entity was created from scratch (our hack)
        entity._client = self.graph.client
        entity._create(entity._get_property_data(), {})
        
        return self
    
            
    def _flush_one_relation(self, entity):
        # Regular case, the entity is either loaded or created via repository
        if entity._client is not None:
            entity.save()
            return self
            
        # Case where the entity was created from scratch (our hack)
        entity._client = self.graph.client
        
        # At this point, all Nodes are supposed to have been persisted, so we 
        # can retrieve their eid.
        if entity._outV_vertex is None:
            raise Exception('Outbound Vertex not set')

        if entity._inV_vertex is None:
            raise Exception('Inbound Vertex not set')

        entity._create(
            entity._outV_vertex,
            entity._inV_vertex,
            entity._get_property_data(), 
            {}
        )
        
        entity._outV_vertex = None
        entity._inV_vertex = None
        
        return self
    
            
    def query(self, gremlin, params):
        """ Performs a gremlin query against the database.
        
        :param gremlin: The gremlin query.
        :type gremlin: str
        :param params: The set of parameter values.
        :type params: dict
        :returns: The result of the query.
        """
        self._log(gremlin+u" "+unicode(params))
        return self.graph.gremlin.query(gremlin, params)
            
            
    def refresh(self, entity):
        """ Fetches information from the database to update the current entity.
        
        @todo
        
        :param entity: The entity to add to the session.
        :type entity: bulbs.model.Node, bulbs.model.Relationship
        :returns: graphalchemy.ogm.BulbsObjectManager -- this object itself.
        """
        
        caches = [key for key in entity.__dict__ if '_cache' in key]
        for cache in caches:
            delattr(entity, cache)
                
        # Reload all other properties from DB.
        
        return self
            
            
    def close_all(self):
        """ Fetches information from the database to update the current entity.
        
        @todo we should also free all _clients properties of all loaded entities.
        
        :param entity: The entity to add to the session.
        :type entity: bulbs.model.Node, bulbs.model.Relationship
        :returns: graphalchemy.ogm.BulbsObjectManager -- this object itself.
        """
        self.session_add = []
        self.session_delete = []
        return self
        
            
    def merge(self, entity):
        """ Merges an entity with its current version in the database.
        
        @todo
        
        :param entity: The entity to add to the session.
        :type entity: bulbs.model.Node, bulbs.model.Relationship
        :returns: graphalchemy.ogm.BulbsObjectManager -- this object itself.
        """
        raise NotImplementedException('Method not implemented.')

        
    def _log(self, message, level=10):
        """ Thin wrapper for logging purposes.
        
        :param message: The message to log.
        :type message: str
        :param level: The level of the log.
        :type level: int
        :returns: graphalchemy.ogm.BulbsObjectManager -- this object itself.
        """
        if self.logger:
            self.logger.log(level, message)
        return self
