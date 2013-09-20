#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from graphalchemy.blueprints.types import List
from graphalchemy.blueprints.types import Dict


# ==============================================================================
#                                      MODEL
# ==============================================================================

class Model(object):
    """ Holds all the schema characteristics that we want to enforce on an
    Element (a Vertex or an Edge).

    This is an abstract class that is extended by specializations for Nodes
    and Relationships.
    """

    # The key under which the Model name will be saved
    model_name_storage_key = None
    model_type = None

    def __init__(self, model_name, metadata, *args, **kwargs):
        self.model_name = model_name
        self.metadata = metadata
        self._properties = {}
        self._adjacencies = {}
        self.indices = {}
        self.logger = kwargs.get('logger', None)


    def register_class(self, class_):
        """ Binds this model to a Python class in the current metadata map, in
        order to be able to perform mapping operations.

        :param class_: The python class to tie to this model.
        :type class_: object
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.Model
        """
        raise NotImplementedError()


    def is_node(self):
        """ :returns: True if this model is applicable to a node.
        :rtype: bool
        """
        raise NotImplementedError()


    def is_relationship(self):
        """ :returns: True if this model is applicable to a relationship.
        :rtype: bool
        """
        raise NotImplementedError()


    def add_property(self, prop):
        """ Registers a property on the current model, and register its index
        if it exists.

        :param prop: The property to register.
        :type prop: graphalchemy.blueprints.schema.Property
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.Model
        """
        if prop.name_py in self._properties:
            raise Exception('Cannot override previously set property.')
        self._properties[prop.name_py] = prop
        if prop.index:
            self.indices[prop.name_py] = prop
        if prop.prefix == True:
            prop.name_db = self.model_name + '_' + prop.name_db
        prop.model = self
        return self


    def add_adjacency(self, adjacency, name):
        raise NotImplementedError()


    def __repr__(self):
        """ :returns: a readable representation of this model.
        :rtype: str
        """
        return self.model_name


    def _useful_indices_among(self, amongs):
        return [among for among in amongs if (among in self.indices)]



class Node(Model):
    """ Defines a model over a vertex, by specifying its properties.

    Example use :
    >>> website = Node('Website', metadata,
    ...     Property('name', String(127), nullable=False, indexed='search'),
    ...     Property('domain', Url(2801))
    ... )
    """

    # The key under which the Model name will be saved
    model_name_storage_key = 'element_type'
    model_type = 'vertex'

    def __init__(self, model_name, metadata, *args, **kwargs):
        """ Creates a vertex model. It will enforce a domain model on every
        vertex that has the corresponding model_name. It is similar to a table
        for a relational database.
        By itself, it does not contain any relationship. Relationships are
        declared as adjacencies in the mapper step, because adjacencies are
        constraints enforced between different objects (a node and a relation).

        :param model_name: The name of the model in the database. Will be saved
        as a property with key model_name_storage_key.
        :type model_name: str
        :param metadata: The metadata object that will hold the metadata.
        :type metadata: graphalchemy.blueprints.schema.Metadata
        :param properties: The list of properties that this model supports. Only
        them will be persisted in the graph.
        :type properties: list<graphalchemy.blueprints.model.Property>
        """
        super(Node, self).__init__(model_name, metadata, *args, **kwargs)
        for prop in args:
            if prop.primaryKey == True:
                raise Exception('Only edge properties can be primaryKeys.')
            self.add_property(prop)


    def register_class(self, class_):
        """ Binds this model to a Python class in the current metadata map, in
        order to be able to perform mapping operations.

        :param class_: The python class to tie to this model.
        :type class_: object
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.Node
        """
        self.metadata.bind_node(class_, self)
        return self


    def is_node(self):
        """ :returns: True if this model is applicable to a node.
        :rtype: bool
        """
        return True


    def is_relationship(self):
        """ :returns: True if this model is applicable to a relationship.
        :rtype: bool
        """
        return False


    def add_adjacency(self, adjacency, name):
        """ Registers an adjacency in the current model.

        :param adjacency: The adjacency to register.
        :type adjacency: str
        :param name: The name of the property to connect the node to.
        :type name: str
        """

        # Save in related models
        self._adjacencies[name] = adjacency
        if adjacency.node is None:
            adjacency.node = self

        # Register property
        # @todo

        return self


class Relationship(Model):
    """ Defines a model over an edge, by specifying its properties.

    Example use :
    >>> websiteHasPage = Relationship('WebsiteHasPage', metadata,
    ...     Property('created', DateTime(), nullable=False)
    ... )
    """

    # The key under which the Model name will be saved
    model_name_storage_key = 'label'
    model_type = 'edge'

    IN = 'in'
    OUT = 'out'
    BOTH = 'both'

    def __init__(self, model_name, metadata, *args, **kwargs):
        """ Creates an edge model. It will enforce a domain model on every
        edge that has the corresponding model_name. It is similar to a join
        table for a relational database.
        By itself, it does not contain any relationship. Relationships are
        declared as adjacencies in the mapper step, because adjacencies are
        constraints enforced between different objects (a node and a relation).

        :param model_name: The name of the model in the database. Will be saved
        as a property with key model_name_storage_key.
        :type model_name: str
        :param metadata: The metadata object that will hold the metadata.
        :type metadata: graphalchemy.blueprints.schema.Metadata
        :param properties: The list of properties that this model supports. Only
        them will be persisted in the graph.
        :type properties: list<graphalchemy.blueprints.model.Property>
        """
        super(Relationship, self).__init__(model_name, metadata, *args, **kwargs)
        self.directed = kwargs.get('directed', True)
        self.signature = kwargs.get('signature', True)
        for prop in args:
            self.add_property(prop)

    def register_class(self, class_):
        """ Binds this model to a Python class in the current metadata map, in
        order to be able to perform mapping operations.

        :param class_: The python class to tie to this model.
        :type class_: object
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.Model
        """
        self.metadata.bind_relationship(class_, self)


    def add_adjacency(self, adjacency, name):
        """ Registers an adjacency in the current model.

        :param adjacency: The adjacency to register.
        :type adjacency: str
        :param name: The name of the property to connect the relationship to.
        :type name: str
        """

        # Save in related models
        self._adjacencies[name] = adjacency
        if adjacency.relationship is None:
            adjacency.relationship = self

        # Register property
        # @todo

        return self


    def is_node(self):
        """ :returns: True if this model is applicable to a node.
        :rtype: bool
        """
        return False

    def is_relationship(self):
        """ :returns: True if this model is applicable to a relationship.
        :rtype: bool
        """
        return True



# ==============================================================================
#                                    STRUCTURE
# ==============================================================================

class Adjacency(object):
    """ An adjacency defines a constraint that we impose between a relation and
    a node. It imposes :
    - at the database level, unique-IN and unique-OUT constraints
    - at the application level, specifications on the type of node that a given
    relationship connects.
    """

    def __init__(self, relationship, nullable=None, unique=True, direction=None, node=None):
        """ Defines the constraints to apply on an adjacency.

        :param node: The node model that is connected.
        :type node: graphalchemy.blueprints.schema.Node
        :param relationship: The relationship model that connects.
        :type relationship: graphalchemy.blueprints.schema.Relationship
        :param unique: Whether the given node can be connected to multiple
        instances of the relationship.
        :type unique: bool
        :param nullable: Whether the given node can be connected to no instance
        of the relationship.
        :type nullable: bool
        :param direction: Whether the relation is IN-bound, or OUT-bound.
        :type direction: const
        """
        self.node = node
        self.relationship = relationship
        self.direction = direction
        self.unique = unique
        self.nullable = nullable



class Property(object):
    """ A property specifies how a property is constrained, and how it is mapped
    to the database. A property can apply to a node as well as a relationship.

    It imposes :
    - a validation on the application side (notably type validation and nullable
    verification)
    - a conversion to the appropriate datatype for database persistence

    It enables :
    - a flexible property mapping (prefixing, property name conversion)
    - indexing on a per-property and per-model basis
    - primaryKey definition for edges
    """

    def __init__(self, name_py, type_, nullable=None, unique=False, index=None, primaryKey=False, group=None, prefix=False, name_db=None):
        """ Defines the constraints to apply on a property.

        :param name_py: The name of the property in the Python objects
        :type name_py: str
        :param type_: The python type, that will be automatically converted to
        a corresponding datatype in the database.
        :type type_: graphalchemy.blueprints.types.Type
        :param nullable: Whether the property can be None.
        :type nullable: bool
        :param unique: Whether the property value is unique in the entire graph.
        This is enforced as a unique-IN constraint in the graph type definition.
        :type unique: bool
        :param index: Which index to use to index the property. If True is
        provided, the default index will be used. Not that this is enforced at
        the database-level, not at the model level, so if this property is used
        in multiple models, it will be indexed on the same index. The Migration
        tool detects such conflicts, and you can use the prefix property to add
        the model name to the node.
        :type index: bool
        :param primaryKey: Whether the property must be used as a primary key
        to index relations.
        :type primaryKey: bool
        :param group: The name of the group to save this relation in.
        :type group: str
        :param prefix: Whether this property must be prefixed by the model name.
        This is typically usefull for indexing purposes, when the property name
        conflicts with other models.
        :type prefix: bool
        :param name_db: The name of the property in the database. Defaults to
        the name of the property in Python.
        """

        self.model = None

        self.name_py = name_py
        self.prefix = prefix
        if name_db is None:
            name_db = name_py
        self.name_db = name_db

        self.type = type_
        self.nullable = nullable

        self.unique_graph = unique
        if index is True:
            index = 'standard'
        if isinstance(self.type, List) \
        or isinstance(self.type, Dict):
            self.unique_node = True
        else:
            self.unique_node = False

        self.index = index

        self.group = group
        self.primaryKey = primaryKey


    def to_py(self, value):
        """ Casts a database value to its correct type in Python, after being
        retrieved from the database for instance.

        :param value: The value to cast.
        :type value: mixed
        :returns: The casted value.
        :type: mixed
        """
        return self.type.to_py(value)


    def to_db(self, value):
        """ Casts a python value to its correct type in the database, before
        being persisted in the database for instance.

        :param value: The value to cast.
        :type value: mixed
        :returns: The casted value.
        :type: mixed
        """
        return self.type.to_db(value)


    def validate(self, value):
        """ Validates a value given the property specifications. Returns False
        and a list of errors if it fails.

        :param value: The value to validate.
        :type value: mixed
        :returns: A boolean and a list of potential errors.
        :rtype: bool, list
        """
        if self.nullable == False \
        and value is None:
            return False, [u'Property is not nullable.']
        return self.type.validate(value)


    def __repr__(self):
        """ :returns: A readable representation of the property.
        :rtype: str
        """
        return '<'+str(self.model)+'.'+self.name_py+'('+str(self.type)+')>'



# ==============================================================================
#                                    SERVICES
# ==============================================================================

class MetaData(object):
    """ Holds a map of all available metadata of all mapped models.
    """

    def __init__(self, bind=None, schema=None):
        self._nodes = {}
        self._relationships = {}
        self.schema = schema
        self.bind = bind

    def __repr__(self):
        return 'MetaData(bind=%r)' % self.bind


    def __contains__(self, table_or_key):
        if not isinstance(table_or_key, util.string_types):
            table_or_key = table_or_key.key
        return table_or_key in self.tables

    def for_object(self, obj):
        class_ = obj.__class__
        return self.for_class(class_)

    def for_class(self, class_):
        if class_ in self._nodes:
            return self._nodes[class_]
        if class_ in self._relationships:
            return self._relationships[class_]
        raise Exception('Unmapped class.')

    def for_model(self, model):
        for class_, node_model in self._nodes:
            if model is node_model:
                return class_
        for class_, relationship_model in self._relationships:
            if model is relationship_model:
                return class_
        raise Exception('Unmapped model.')

    def bind_node(self, class_, model):
        if not model.is_node():
            raise Exception('Bound model is not a node !')
        self._nodes[class_] = model
        return self

    def bind_relationship(self, class_, model):
        if not model.is_relationship():
            raise Exception('Bound model is not a relationship !')
        self._relationships[class_] = model
        return self

    def is_node(self, obj):
        return obj.__class__ in self._nodes

    def is_relationship(self, obj):
        return obj.__class__ in self._relationships

    def is_bind(self, obj):
        return self.is_node(obj) or self.is_relationship(obj)


