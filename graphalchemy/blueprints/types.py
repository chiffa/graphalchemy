#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from datetime import datetime
from datetime import date


# ==============================================================================
#                                    EXTENSIONS
# ==============================================================================

class Type(object):
    """ Types can be used in the schema definition of Nodes and Relationships.

    They are especially usefull in :
    - validation (checking that the entity properties have the righ format)
    - coercion (before the entity is saved in the database)
    """

    # https://github.com/thinkaurelius/titan/wiki/Datatype-and-Attribute-Serializer-Configuration
    # https://code.google.com/p/kryo/#Default_serializers
    name_db = None

    def to_py(self, value):
        """ Coerces the value to the appropriate python type.

        :param value: The value to coerce.
        :returns: The coerced value.
        """
        return value


    def to_db(self, value):
        """ Coerces the value to the appropriate database type.

        :param value: The value to coerce.
        :returns: The coerced value.
        """
        return value

    def validate(self, value):
        """ Validates the value against the specifications of the Type.

        :param value: The value to validate.
        :returns: A boolean stating if the validation was successfull, and the
        eventual list of errors.
        :rtype: boolean, list<string>
        """
        return True, []

    def __repr__(self):
        """ Returns a readable representation of the Type.
        """
        return self.__class__.__name__


class Numeric(Type):

    def __init__(self, min_value=None, max_value=None):
        """ Defines the specifications of the Type.

        :param min_value: The minimal value that can be taken.
        :type min_value: comparable
        :param max_value: The minimal value that can be taken.
        :type max_value: comparable
        """
        self.min_value = min_value
        self.max_value = max_value

    def to_py(self, value):
        raise NotImplementedError()

    def validate(self, value):
        if self.max_value is not None \
        and value > self.max_value:
            return False, [u'Too big : '+str(value)+u' > '+str(self.max_value)]
        if self.min_value is not None \
        and value < self.min_value:
            return False, [u'Too small : '+str(value)+u' < '+str(self.min_value)]
        return super(Numeric, self).validate(value)


class Integer(Numeric):

    name_db = "Integer.class"

    def to_py(self, value):
        return int(value)

    def validate(self, value):
        if not isinstance(value, int):
            return False, [u'Wrong type : expected int, got '+str(type(value))]
        return super(Integer, self).validate(value)


class Float(Numeric):

    def to_py(self, value):
        return float(value)

    def validate(self, value):
        if not isinstance(value, float):
            return False, [u'Wrong type : expected float, got '+str(type(value))]
        return super(Float, self).validate(value)


class Boolean(Integer):

    def to_py(self, value):
        return bool(value)

    def validate(self, value):
        if not isinstance(value, bool):
            return False, [u'Wrong type : expected bool, got '+str(type(value))]
        return super(Boolean, self).validate(value)


class Const(Type):

    def __init__(self, choices):
        """ Defines the specifications of the Type.

        :param choices: The list of values that can be taken.
        :type choices: iterable
        """
        self.choices = choices

    def validate(self, value):
        if value not in self.choices:
            return False, [u'Value '+str(value)+u' is not in ('+u", ".join([str(choice) for choice in self.choices])+u')']
        return super(Const, self).validate(value)


class String(Type):

    name_db = "String.class"

    def __init__(self, size=None):
        """ Defines the specifications of the Type.

        :param size: The maximum length that the value can have.
        :type size: int
        """
        self.size = size

    def to_py(self, value):
        return unicode(value)

    def validate(self, value):
        if not isinstance(value, basestring):
            return False, [u'Wrong type : expected basestring, got '+str(type(value))]
        if self.size is not None \
        and len(value) > self.size:
            return False, [u'Value is too long : '+str(len(value))+u' > '+str(self.size)]
        return super(String, self).validate(value)


class Url(String):

    def validate(self, value):
        from urlparse import urlparse
        try:
            parse = urlparse(value)
            if parse.scheme == '':
                return False, [u'Unable to parse URL']
            return super(Url, self).validate(value)
        except:
            return False, [u'Unable to parse URL']


class DateTime(Type):

    name_db = "Integer.class"

    def validate(self, value):
        if not isinstance(value, datetime):
            return False, [u'Wrong type : expected datetime, got '+str(type(value))]
        return super(DateTime, self).validate(value)


class Date(Type):

    def validate(self, value):
        if not isinstance(value, date):
            return False, [u'Wrong type : expected date, got '+str(type(value))]
        return super(Date, self).validate(value)


class List(Type):

    name_db = 'Collection.class'



class Dict(Type):

    name_db = 'Map.class'



