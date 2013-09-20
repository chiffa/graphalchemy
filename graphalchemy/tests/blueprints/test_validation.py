#! /usr/bin/env python
#-*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from unittest import TestCase

# Services to test
from graphalchemy.blueprints.validation import Validator

# Model
from graphalchemy.blueprints.schema import Node
from graphalchemy.blueprints.schema import Relationship
from graphalchemy.blueprints.schema import MetaData
from graphalchemy.blueprints.schema import Property
from graphalchemy.blueprints.schema import Adjacency

# Types
from graphalchemy.blueprints.types import List
from graphalchemy.blueprints.types import String
from graphalchemy.blueprints.types import Boolean
from graphalchemy.blueprints.types import Url
from graphalchemy.blueprints.types import DateTime

# Auxiliary
from graphalchemy.ogm.mapper import Mapper

from datetime import datetime


# ==============================================================================
#                                     TESTING
# ==============================================================================

class ValidatorTestCase(TestCase):

    def setUp(self):
        self.mapper = Mapper()
        self.metadata = MetaData()
        self.validator = Validator(self.metadata)

    def test_run(self):

        class Website(object):
            def __init__(self):
                self.name = None
                self.url = None
        website = Node('Website', self.metadata,
            Property('name', String(127), nullable=False, index=True),
            Property('url', Url(), nullable=False, index=True),
        )
        self.mapper(Website, website)
        obj = Website()

        # Null value
        obj.name = None
        obj.url = None
        ok, errors = self.validator.run(obj)
        self.assertFalse(ok)
        self.assertEquals({
            "name":[u'Property is not nullable.'],
            'url': [u'Property is not nullable.']
        }, errors)

        # Ability to reach to the second level
        obj.name = "*"*128
        obj.url = "http://www.url.com/"
        ok, errors = self.validator.run(obj)
        self.assertFalse(ok)
        self.assertEquals({"name":[u'Value is too long : 128 > 127']}, errors)

        # Ability to check various properties
        obj.name = "*"*127
        obj.url = "bla"
        ok, errors = self.validator.run(obj)
        self.assertFalse(ok)
        self.assertEquals({'url': [u'Unable to parse URL']}, errors)

        # Ability to accumulate errors on various properties
        obj.name = "*"*128
        obj.url = "bla"
        ok, errors = self.validator.run(obj)
        self.assertFalse(ok)
        self.assertEquals({"name":[u'Value is too long : 128 > 127'], 'url': [u'Unable to parse URL']}, errors)

        # Return value if success
        obj.name = "*"*127
        obj.url = "http://www.url.com/"
        ok, errors = self.validator.run(obj)
        self.assertTrue(ok)
        self.assertEquals({}, errors)

