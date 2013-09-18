#! /usr/bin/env python
#-*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from unittest import TestCase

# Services to test
from graphalchemy.blueprints.types import Type
from graphalchemy.blueprints.types import Integer
from graphalchemy.blueprints.types import String
from graphalchemy.blueprints.types import Const
from graphalchemy.blueprints.types import Float
from graphalchemy.blueprints.types import Boolean
from graphalchemy.blueprints.types import Url
from graphalchemy.blueprints.types import DateTime
from graphalchemy.blueprints.types import Date

# System
import datetime


# ==============================================================================
#                                     TESTING
# ==============================================================================

class TypeTestCase(TestCase):

    def test_validate(self):

        ok, errors = Type().validate(None)
        self.assertTrue(ok)
        self.assertEquals([], errors)


class IntegerTestCase(TestCase):

	def test_validate(self):

		# Type
		ok, errors = Integer().validate(1)
		self.assertTrue(ok)
		self.assertEquals([], errors)

		ok, errors = Integer().validate(1.0)
		self.assertFalse(ok)
		self.assertEquals([u"Wrong type : expected int, got <type 'float'>"], errors)

		# Max
		ok, errors = Integer(max_value=1).validate(1)
		self.assertTrue(ok)
		self.assertEquals([], errors)

		ok, errors = Integer(max_value=1).validate(2)
		self.assertFalse(ok)
		self.assertEquals([u'Too big : 2 > 1'], errors)

		# Min
		ok, errors = Integer(min_value=1).validate(1)
		self.assertTrue(ok)
		self.assertEquals([], errors)

		ok, errors = Integer(min_value=2).validate(1)
		self.assertFalse(ok)
		self.assertEquals([u'Too small : 1 < 2'], errors)


class FloatTestCase(TestCase):

    def test_validate(self):

		# Type
		ok, errors = Float().validate(1.0)
		self.assertTrue(ok)
		self.assertEquals([], errors)

		ok, errors = Float().validate(1)
		self.assertFalse(ok)
		self.assertEquals([u"Wrong type : expected float, got <type 'int'>"], errors)

		# Max
		ok, errors = Float(max_value=1).validate(1.0)
		self.assertTrue(ok)
		self.assertEquals([], errors)

		ok, errors = Float(max_value=1).validate(2.0)
		self.assertFalse(ok)
		self.assertEquals([u'Too big : 2.0 > 1'], errors)

		# Min
		ok, errors = Float(min_value=1).validate(1.0)
		self.assertTrue(ok)
		self.assertEquals([], errors)

		ok, errors = Float(min_value=2).validate(1.0)
		self.assertFalse(ok)
		self.assertEquals([u'Too small : 1.0 < 2'], errors)


class BooleanTestCase(TestCase):

    def test_validate(self):

        ok, errors = Boolean().validate(True)
        self.assertTrue(ok)
        self.assertEquals([], errors)

        ok, errors = Boolean().validate(1.0)
        self.assertFalse(ok)
        self.assertEquals([u"Wrong type : expected bool, got <type 'float'>"], errors)


class ConstTestCase(TestCase):

    def test_validate(self):

		ok, errors = Const([1]).validate(1)
		self.assertTrue(ok)
		self.assertEquals([], errors)

		ok, errors = Const([]).validate(1.0)
		self.assertFalse(ok)
		self.assertEquals([u'Value 1.0 is not in ()'], errors)

		ok, errors = Const([1, 3]).validate(2)
		self.assertFalse(ok)
		self.assertEquals([u'Value 2 is not in (1, 3)'], errors)

		ok, errors = Const([1]).validate(1.0)
		self.assertTrue(ok)
		self.assertEquals([], errors)


class StringTestCase(TestCase):

    def test_validate(self):

        ok, errors = String().validate("Foo")
        self.assertTrue(ok)
        self.assertEquals([], errors)

        ok, errors = String().validate(1.0)
        self.assertFalse(ok)
        self.assertEquals([u"Wrong type : expected basestring, got <type 'float'>"], errors)


class DateTestCase(TestCase):

    def test_validate(self):

        ok, errors = Date().validate(datetime.date.today())
        self.assertTrue(ok)
        self.assertEquals([], errors)

        ok, errors = DateTime().validate(datetime.datetime.now())
        self.assertTrue(ok)
        self.assertEquals([], errors)

        ok, errors = Date().validate(1.0)
        self.assertFalse(ok)
        self.assertEquals([u"Wrong type : expected date, got <type 'float'>"], errors)


class DateTimeTestCase(TestCase):

    def test_validate(self):

        ok, errors = DateTime().validate(datetime.datetime.now())
        self.assertTrue(ok)
        self.assertEquals([], errors)

        ok, errors = Date().validate(datetime.date.today())
        self.assertTrue(ok)
        self.assertEquals([], errors)

        ok, errors = DateTime().validate(1.0)
        self.assertFalse(ok)
        self.assertEquals([u"Wrong type : expected datetime, got <type 'float'>"], errors)


