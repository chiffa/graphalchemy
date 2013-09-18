#! /usr/bin/env python
#-*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from graphalchemy.tests.abstract import GraphAlchemyTestCase

# Models
from graphalchemy.model import Node
from bulbs.property import String
from graphalchemy.property import Url
from graphalchemy.property import Boolean
from graphalchemy.fixture.model import Recipe
from graphalchemy.fixture.model import WebsiteHostsPage

# Fixtures
from graphalchemy.fixture.instance import PageFixture


# ==============================================================================
#                                 SERVICE TEST
# ==============================================================================

class NodeTest(GraphAlchemyTestCase):
    
    def test___init__(self):
        
        # Ability to create an entity directly from its model :
        recipe = Recipe(timeTotal=30)
        str(recipe)
        self.assertEquals('Recipe', recipe.element_type)
        self.assertEquals(30, recipe.timeTotal)
        self.assertEquals(None, recipe._client)
        self.assertIsInstance(recipe, Recipe)
        self.assertIn('timeTotal', recipe._properties)
        self.assertEquals({}, recipe._data)
        self.assertTrue(recipe._initialized)
        
        # Ability to set a property as a simple setter
        recipe.title = 'Hello'
        self.assertEquals('Hello', recipe.title)
        self.assertIn('title', recipe._properties)
        self.assertEquals({}, recipe._data)
        self.assertTrue(recipe._initialized)
        
        # Ability to load a client
        recipe = Recipe('bla')
        self.assertEquals('bla', recipe._client)
        
        # Ability to create and read non-persisted properties
        recipe.foo = 'Foo'
        self.assertEquals('Foo', recipe.foo)
        
        
    def test_create(self):
        
        # Ability to create an entity from the repository :
        recipe = self.ogm.repository('Recipe')(timeTotal=30)
        self.assertEquals(30, recipe.timeTotal)
        self.assertIsInstance(recipe, Recipe)
        
        # Ability to create an entity from the repository create method :
        recipe = self.ogm.repository('Recipe').create(timeTotal=30)
        self.assertEquals(30, recipe.timeTotal)
        self.assertIsInstance(recipe, Recipe)
        
        
    # ======================================================================
    # For future reference, the Node creation process in bulbs : 
    # ======================================================================
    # NodeProxy.create
    #   Element.__init__
    #       self._client = client
    #       self._data = {}
    #       self._result = None
    #       self._vertices = None
    #       self._edges = None
    #       self._initialized = True
    #   Node._create(_data, kwds)
    #       data, index_name, keys = self.get_bundle(_data, **kwds)
    #       resp = self._client.create_indexed_vertex(data, index_name, keys)
    #       result = resp.one()
    #       self._initialize(result)
    #           Element._initialize(self,result)
    #               self._result = result
    #               self._data = result.get_data().copy() 
    #               self._set_pretty_id(self._client)
    #               self._vertices = VertexProxy(Vertex,self._client)
    #               self._edges = EdgeProxy(Edge,self._client)
    #           self._initialized = False
    #           self._set_property_data()
    #               Transfers the stuff in _data to the attributes
    #           self._initialized = True

    def test___init__(self):
        
        # Ability to create an entity directly from its model :
        hosts = WebsiteHostsPage(since=123)
        str(hosts)
        self.assertEquals('hosts', hosts.label)
        self.assertEquals(123, hosts.since)
        self.assertEquals(None, hosts._client)
        self.assertIsInstance(hosts, WebsiteHostsPage)
        self.assertIn('since', hosts._properties)
        self.assertEquals({}, hosts._data)
        self.assertTrue(hosts._initialized)
        
        # Ability to set a property as a simple setter
        hosts.accessible = True
        self.assertEquals(True, hosts.accessible)
        self.assertIn('since', hosts._properties)
        self.assertIn('accessible', hosts._properties)
        self.assertEquals({}, hosts._data)
        self.assertTrue(hosts._initialized)
        
        # Ability to load a client
        hosts = WebsiteHostsPage('bla')
        self.assertEquals('bla', hosts._client)
        

    def test_create(self):
        
        page_fixture = PageFixture(self.ogm)
        page_fixture.clean()
        page_fixture.load()
        inV = page_fixture._parent['Website'].get('Website1')
        outV = page_fixture.get('Website1Page1')
        
        # Ability to create an entity from the repository :
        hosts = self.ogm.repository('WebsiteHostsPage')(outV, inV, since=123)
        self.assertEquals(inV.eid, hosts._inV)
        self.assertEquals(outV.eid, hosts._outV)
        self.assertEquals(123, hosts.since)
        self.assertIsInstance(hosts, WebsiteHostsPage)
        
        # Ability to create an entity from the repository create method :
        hosts = self.ogm.repository('WebsiteHostsPage').create(outV, inV, since=30)
        self.assertEquals(inV.eid, hosts._inV)
        self.assertEquals(outV.eid, hosts._outV)
        self.assertEquals(30, hosts.since)
        self.assertIsInstance(hosts, WebsiteHostsPage)
        
        
    # ======================================================================
    # For future reference, the Relationship creation process in bulbs : 
    # ======================================================================
    # RelationshipProxy.create
    #   Element.__init__
    #       self._client = client
    #       self._data = {}
    #       self._result = None
    #       self._vertices = None
    #       self._edges = None
    #       self._initialized = True
    #   Relationship._create(_data, kwds)
    #       label = self.get_label(self._client.config)
    #       outV, inV = coerce_vertices(outV, inV)  # Returns the ids of the vertixes
    #       data, index_name, keys = self.get_bundle(_data, **kwds)
    #       resp = self._client.create_indexed_edge(outV, label, inV, data, index_name, keys)
    #       result = resp.one()
    #       self._initialize(result)
    #           Element._initialize(self,result)
    #               self._result = result
    #               self._data = result.get_data().copy() 
    #               self._set_pretty_id(self._client)
    #               self._vertices = VertexProxy(Vertex,self._client)
    #               self._edges = EdgeProxy(Edge,self._client)
    #           self._initialized = False
    #           self._set_property_data()
    #               Transfers the stuff in _data to the attributes
    #           self._initialized = True

    def test_get(self):
        
        class Website(Node):
            element_type = 'Website'
            pass
        class Page(Node):
            element_type = 'Page'
            title = String()
            url = Url()
            
            def isHostedBy(self):
                return self._relation('hosts', 'in', unique=True)
            def isHostedBy_add(self, relation, node):
                return self._relation_add('hosts', 'in', relation, node)
            def isHostedBy_del(self, relation):
                return self._relation_del('hosts', 'in', relation)
            
            def describes(self):
                return self._relation('describes', 'out', unique=False)
            def describes_add(self, relation, node):
                return self._relation_add('describes', 'out', relation, node)
            def describes_del(self, relation):
                return self._relation_del('describes', 'out', relation)
        class Content(Node):
            element_type = 'Content'
            pass
        
        class PageDescribesContent(Node):
            label = 'describes'
            accessible = Boolean()
        class WebsiteHostsPage(Node):
            label = 'hosts'
        
        # No relation for now
        page = Page(title='Foo', url='Bar')
        self.assertEquals({}, page.describes())
        self.assertEquals({}, page.isHostedBy())
        
        # Add a relation
        describe1 = PageDescribesContent(accessible=True)
        describe2 = PageDescribesContent(accessible=False)
        content1 = Content()
        content2 = Content()
        page.describes_add(describe1, content1)
        page.describes_add(describe2, content2)
        describes = page.describes()
        self.assertIn(describe1, describes)
        self.assertIn(describe2, describes)
        self.assertIs(describes[describe1], content1)
        self.assertIs(describes[describe2], content2)
        
        host1 = WebsiteHostsPage()
        website1 = Website()
        page.isHostedBy_add(host1, website1)
        hosts = page.isHostedBy()
        self.assertIn(host1, hosts)
        self.assertIs(hosts[host1], website1)
        
        # Add a duplicate
        page.describes_add(describe1, content1)
        describes = page.describes()
        self.assertEquals(2, len(describes))
        
        page.isHostedBy_add(host1, website1)
        hosts = page.isHostedBy()
        self.assertEquals(1, len(hosts))
        
        # Delete a relation
        page.describes_del(describe2)
        describes = page.describes()
        self.assertIn(describe1, describes)
        self.assertNotIn(describe2, describes)
        self.assertIs(describes[describe1], content1)
        self.assertEquals(len(describes), 1)
        
        page.isHostedBy_del(host1)
        hosts = page.isHostedBy()
        self.assertEquals({}, hosts)
        
        # Delete a non-existing relation
        page.describes_del(host1)
        describes = page.describes()
        self.assertIn(describe1, describes)
        self.assertNotIn(describe2, describes)
        self.assertIs(describes[describe1], content1)
        self.assertEquals(len(describes), 1)
        
        page.isHostedBy_del(describe1)
        hosts = page.isHostedBy()
        self.assertEquals({}, hosts)
        