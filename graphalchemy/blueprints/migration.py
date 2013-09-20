#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from graphalchemy.blueprints.schema import Relationship


# ==============================================================================
#                                      SERVICE
# ==============================================================================

class MigrationGenerator(object):
    """ Generates the groovy schema declaration from the current metadata.

    Example use :
    >>> migration_generator = MigrationGenerator(metadata)
    >>> migration_generator.run()
    """

    def __init__(self, metadata_map, logger=None):
        """ Initializes the migration generator from :

        :param metadata_map: The metadata holder.
        :type metadata_map: graphalchemy.blueprints.schema.MetaData
        :param logger: An optionnal logger.
        :type logger: logging.Logger
        """
        self.metadata_map = metadata_map
        self.logger = logger

        self._queries = []
        self._properties = {}
        self._labels = {}
        self._groups = {}


    def run(self):
        """ Generates all queries.

        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.MigrationGenerator
        """
        for node in self.metadata_map._nodes.values():
            self._queries.append('// Node '+node.model_name)
            self.run_node(node)
        for relationship in self.metadata_map._relationships.values():
            self._queries.append('// Relationship '+relationship.model_name)
            self.run_relationship(relationship)
        self._queries.append('// Groups')
        for i, name in enumerate(self._groups.keys()):
            self.make_group(name, i + 2) # Indexing starts at 2
        return self


    def run_node(self, node):
        """ Generates all queries for a given node model.

        :param node: The node to generate the label from.
        :type node: graphalchemy.blueprints.schema.Node
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.MigrationGenerator
        """
        for prop in node._properties.values():
            self.make_property_key(node, prop)
        return self


    def run_relationship(self, relationship):
        """ Generates all queries for a given relationship model.

        :param relationship: The relationship to generate the label from.
        :type relationship: graphalchemy.blueprints.schema.Relationship
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.MigrationGenerator
        """
        for prop in relationship._properties.values():
            self.make_property_key(relationship, prop)
        self.make_edge_label(relationship)
        return self


    def make_edge_label(self, relationship):
        """ Creates the query for an edge label.

        :param relationship: The relationship to generate the label from.
        :type relationship: graphalchemy.blueprints.schema.Relationship
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.MigrationGenerator
        """
        query = 'graph.makeType()'
        query += '.name("'+relationship.model_name+'")'
        # query += '.indexed('+'Edge.class'+')'
        # query += '.unique(Direction.BOTH).makePropertyKey()'

        # primaryKey
        pks = [prop for prop in relationship._properties.values() if prop.primaryKey]
        if len(pks) > 1:
            raise Exception('More than one private key was defined.')
        if len(pks) == 1:
            query += '.primaryKey('+pks[0].name_db+')'

        # Signature
        # @todo

        # Direction
        if relationship.directed:
            query += '.directed()'
        else:
            query += '.undirected()'

        # Uniqueness
        uniques_in = [
            adjacency
            for adjacency in relationship._adjacencies.values()
            if adjacency.unique == True and adjacency.direction == Relationship.IN
        ]
        all_in = [
            adjacency
            for adjacency in relationship._adjacencies.values()
            if adjacency.direction == Relationship.IN
        ]
        if len(uniques_in) == len(all_in):
            query += '.unique(IN)'
        uniques_out = [
            adjacency
            for adjacency in relationship._adjacencies.values()
            if adjacency.unique == True and adjacency.direction == Relationship.OUT
        ]
        all_out = [
            adjacency
            for adjacency in relationship._adjacencies.values()
            if adjacency.direction == Relationship.OUT
        ]
        if len(uniques_out) == len(all_out):
            query += '.unique(OUT)'

        # Type
        query += '.makeEdgeLabel()'
        query += ';'
        self._push_label(relationship.model_name, query)
        return self


    def make_property_key(self, model, property):
        """ Creates the query for a property key.

        :param model: The model to generate the property from.
        :type model: graphalchemy.blueprints.schema.Model
        :param property: The property to create.
        :type property: graphalchemy.blueprints.schema.Property
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.MigrationGenerator
        """
        query = 'graph.makeType()'

        # Groups
        if property.group is not None:
            query += '.group("'+property.group+'")'
            self._push_group(property.group, None)

        # Name
        query += '.name("'+property.name_db+'")'

        # Type
        query += '.dataType('+property.type.name_db+')'

        # Indexing
        if property.index is not None:
            query += '.indexed("' + property.index + '", ' + ('Vertex.class' if model.is_node() else 'Edge.class')+')'

        # Uniqueness
        if property.unique_graph and not property.unique_node:
            query += '.unique(Direction.BOTH)'
        else:
            if property.unique_graph:
                query += '.unique(Direction.IN)'
            if not property.unique_node:
                query += '.unique(Direction.OUT)'

        # Type
        query += '.makePropertyKey()'
        query += ';'
        self._push_property(property.name_db, query)
        return self


    def make_group(self, name, id):
        """ Creates the query for a group.

        :param name_db: The name of the property in the database.
        :type name_db: str
        :param query: The corresponding query.
        :type query: str
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.MigrationGenerator
        """
        query = 'TypeGroup ' + name + ' = TypeGroup.of(' + str(id) + ', "' + name + '");'
        self._queries.append(query)
        return self


    def _push_property(self, name_db, query):
        """ Adds a property to the creation list. This is usefull to detect and
        resolve conflicts at model definition runtime.

        :param name_db: The name of the property in the database.
        :type name_db: str
        :param query: The corresponding query.
        :type query: str
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.MigrationGenerator
        """
        if name_db in self._properties:
            raise Exception('This property is already used : '+str(name_db))
        self._properties[name_db] = query
        self._queries.append(query)
        return self


    def _push_label(self, name_db, query):
        """ Adds a label to the creation list. This is usefull to detect and
        resolve conflicts at model definition runtime.

        :param name_db: The name of the label in the database.
        :type name_db: str
        :param query: The corresponding query.
        :type query: str
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.MigrationGenerator
        """
        if name_db in self._labels:
            raise Exception('This label is already used : '+str(name_db))
        self._labels[name_db] = query
        self._queries.append(query)
        return self


    def _push_group(self, name_db, query):
        """ Adds a group to the creation list. This is usefull to detect and
        resolve conflicts at model definition runtime.

        :param name_db: The name of the property in the database.
        :type name_db: str
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.MigrationGenerator
        """
        self._groups[name_db] = query
        return self


    def __str__(self):
        """ Returns a readable version of the required queries.

        :rtype: str
        """
        return "\n".join(self._queries)

