#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

class Mapper(object):
    """
    """

    _new_mappers = False

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return self.register(*args, **kwargs)

    def register(self, class_, model, adjacencies={}):

        # Instrument class attributes
        # Instrument class adjacencies

        # Update the metadata to register the class
        model.register_class(class_)

        # Update the metadata to register the adjacencies
        if len(adjacencies) and not model.is_node():
            raise Exception('Adjacencies can only be registered on nodes.')
        for name, adjacency in adjacencies.iteritems():
            node = model
            node.add_adjacency(adjacency, name)
            relationship = adjacency.relationship
            relationship.add_adjacency(adjacency, name)
