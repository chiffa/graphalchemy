#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

class Mapper(object):
    """Define the correlation of class attributes to database table
    columns.

    The :class:`.Mapper` object is instantiated using the
    :func:`~sqlalchemy.orm.mapper` function.    For information
    about instantiating new :class:`.Mapper` objects, see
    that function's documentation.


    When :func:`.mapper` is used
    explicitly to link a user defined class with table
    metadata, this is referred to as *classical mapping*.
    Modern SQLAlchemy usage tends to favor the
    :mod:`sqlalchemy.ext.declarative` extension for class
    configuration, which
    makes usage of :func:`.mapper` behind the scenes.

    Given a particular class known to be mapped by the ORM,
    the :class:`.Mapper` which maintains it can be acquired
    using the :func:`.inspect` function::

        from sqlalchemy import inspect

        mapper = inspect(MyClass)

    A class which was mapped by the :mod:`sqlalchemy.ext.declarative`
    extension will also have its mapper available via the ``__mapper__``
    attribute.


    """

    _new_mappers = False

    def __init__(self):
        pass

    def __call__(self,
                 class_,
                 model=None,
                 properties=None
                 ):

        # Instrument class attributes
        # Instrument class adjacencies
        
        # Update the metadata to register the class
        model.register_class(class_)
        
        