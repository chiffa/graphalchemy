#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from graphalchemy.tests.abstract import GraphAlchemyTestCase

from graphalchemy.metadata import BulbsMetadata
from graphalchemy.model import Node
from bulbs.property import String

from graphalchemy.fixture.model import Page
from graphalchemy.fixture.model import WebsiteHostsPage


# ==============================================================================
#                                     LOCAL FIXTURES
# ==============================================================================

class User(Node):
    element_type = 'User'
    firstname = String(indexed=True)
    lastname = String()
    

# ==============================================================================
#                                     BASE CLASS
# ==============================================================================

class BulbsMetadataTestCase(GraphAlchemyTestCase):
    
    def test___init__(self):
        
        metadata = BulbsMetadata(User)
        self.assertEquals(metadata.indices, ['firstname'])


class DictTestCase(GraphAlchemyTestCase):
    
    def test_dict(self):
        """ Series of tests to verify that we can use standard dictionaries as 
        holders for (relation, node) pairs in relationships."""
        
        # Create fixtures
        rel1 = WebsiteHostsPage()
        rel2 = WebsiteHostsPage()
        rel3 = WebsiteHostsPage()
        rels = [rel1, rel2, rel3]
        node1 = Page(name='Foo')
        node2 = Page(name='Bar')
        node3 = Page(name='Baz')
        nodes = [node1, node2, node3]
        
        # Define from concatenation
        dic = dict(zip(rels, nodes))
        self.assertIs(node1, dic[rel1])
        self.assertIs(node2, dic[rel2])
        self.assertIs(node3, dic[rel3])
        
        # Define as standard dict
        dic = dict()
        dic[rel1] = node1
        dic[rel2] = node2
        dic[rel3] = node3
        self.assertIs(node1, dic[rel1])
        self.assertIs(node2, dic[rel2])
        self.assertIs(node3, dic[rel3])
        
        # Verify iteration on values
        iterator = dic.itervalues()
        self.assertIs(node1, next(iterator))
        self.assertIs(node2, next(iterator))
        self.assertIs(node3, next(iterator))
        
        # Verify iteration on keys
        iterator = dic.iterkeys()
        self.assertIs(rel1, next(iterator))
        self.assertIs(rel2, next(iterator))
        self.assertIs(rel3, next(iterator))
        
        # Verify iteration on items
        iterator = dic.iteritems()
        tuple_ = next(iterator)
        self.assertIs(tuple_[0], rel1)
        self.assertIs(tuple_[1], node1)
        tuple_ = next(iterator)
        self.assertIs(tuple_[0], rel2)
        self.assertIs(tuple_[1], node2)
        tuple_ = next(iterator)
        self.assertIs(tuple_[0], rel3)
        self.assertIs(tuple_[1], node3)
        
        