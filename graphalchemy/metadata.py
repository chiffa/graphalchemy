#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                   IMPORTS
# ==============================================================================


# ==============================================================================
#                               IMPLEMENTATION
# ==============================================================================

class BulbsMetadata(object):
    """ Holds metadata for a given Bulbs model. Notably, saves which properties
    are indexed for faster retrieval.

    For now, the models can be built following the bulbs specification, extending
    another class :

    >>> from graphalchemy.model import Node
    >>> from bulbs.property import String
    >>> from graphalchemy.property import Url
    >>>
    >>> class Website(Node):
    ...     name = String()
    ...     domain = Url(indexed=True)
    >>>
    >>> class Page(Node):
    ...     title = String()
    ...     url = Url(indexed=True)
    >>>
    >>> website = Website(domain="http://www.allrecipes.com")
    >>> ogm.add(website)
    >>> ogm.flush()

    Ultimately, the object-to-graph mapping will be performed through a metadata
    builder, which will not require the model object to extend a specific class :

    >>> from my.models.nodes import Website, Page
    >>> from my.models.relations import WebsiteHasPage
    >>> from ogm.metadata import Metadata, Property, Relationship
    >>>
    >>> metadata = Metadata()
    >>>
    >>> website = Node('Website', metadata,
    ...     Property('name', String(127), nullable=False),
    ...     Property('domain', Url(2801))
    ... )
    >>> mapper(Website, website, adjacencies={
    ...     'pages': relationship(WebsiteHasPage, multi=True, nullable=True, direction=OUT)
    ... })
    >>>
    >>> page = Node('Page', metadata,
    ...     Property('title', String(127), nullable=False),
    ...     Property('url', Url(2801))
    ... )
    >>> mapper(Page, page, adjacencies={
    ...     'website': Relationship(WebsiteHasPage, multi=False, nullable=False, direction=IN)
    ... })
    >>>
    >>> websiteHasPage = Relationship('WebsiteHasPage', metadata,
    ...     Property('created', DateTime, nullable=False, default=datetime.now)
    ... )
    >>> mapper(WebsiteHasPage, websiteHasPage,
    ...     out_node=Website,
    ...     in_node=Page
    ... )

    @todo : implement the following specification :

    Properties of a node :
    - on deletion, cascade deletion of relations

    Properties of a relation :
    - on deletion, delete orphan nodes
    - allow multiple of same type between same pairs of node ?
    - allow multiple of same type from node ?
    - allow multiple of same type to node ?
    - allow node from type ?
    - allow node to type ?
    - vertex-centrix index ?
    """

    def __init__(self, model):
        """ Analyses a model object to infer which properties are indexed.

        :param model_name: The name of the model which metadata is being extracted.
        :type model_name: str
        :param model: The model itself.
        :type model: bulbs.model.Node, bulbs.model.Relationship
        """
        self.indices = []
        for property_name, property in model._properties.iteritems():
            # property_type = property.__class__.__name__.replace('Field', '')
            if property.indexed:
                self.indices.append(property_name)
