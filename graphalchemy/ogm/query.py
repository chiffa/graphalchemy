#! /usr/bin/env python
#-*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from urllib import quote, quote_plus, urlencode


# ==============================================================================
#                                      EXCEPTIONS
# ==============================================================================

class NoResultFound(Exception):
    pass

class MultipleResultsFound(Exception):
    pass


# ==============================================================================
#                                      SERVICE
# ==============================================================================

class Query(object):

    def __init__(self, session, *args, **kwargs):
        self.session = session
        self._filters = {}
        self._indices = {}
        self._offset = None
        self._limit = None
        self._results = None
        self.logger = kwargs.get('logger', None)


    def __iter__(self):
        if self._results is None:
            self.execute()
        for result in self._results:
            yield result


    def execute(self):
        path = self.build_path(**self._filters)
        response = self.session.client.request.get(path, params=None)
        print response
        self._results = response.results
        return self


    def indexed_filter(self, index_name, key, value):
        self._indices[index_name] = {"key": key, "value":value}
        return self


    def filter(self, **kwargs):
        """ Performs a filtering operation on the given repository. Automaticaly
        decides which index to use :
        - the eid index if provided
        - the first property key index that is matched
        Will add extra filtering as simple as queries.

        Example :
        >>> iterator = repository.filter(domain='http://www.foo.com', name='Foo')
        >>> iterator = repository.filter(eid=123)
        >>> iterator = repository.filter(indexed_property='Foo')

        @todo : it should return an iterator and wait for extra filtering.
        @todo : only limited to filtering on one entity for now.

        :returns: generator -- The list of models that match the query.
        """
        self._filters.update(kwargs)
        return self


    def build_path(self, **kwargs):
        """ Builds a gremlin query string from a set of filtering arguments.
        @todo : no escaping is implemented yet.

        :returns: string, dict -- The gremlin query.
        """
        def clean(value):
            return quote(unicode(value), safe='')

        path = ''

        # If the id is in the parameters :
        if 'id' in kwargs:
            path = '/vertices/'+clean(kwargs['id'])
            return path

        # If one of the parameters is indexed :
        if self._indices:
            for key, value in self._indices:
                path += '/indices/'+clean(index)+u'?key='+clean(key)+u'&value='+clean(val)
                # For now, we can only query on one index
                break
            # For now, we can only handle one index
            return path

        # If no parameter is indexed :
        if self.model.is_node():
            path += '/vertices'
        else:
            path += '/edges'

        # Fillup with remaining filters
        for key, val in kwargs.iteritems():
            path += u'?key='+clean(key)+u'&value='+clean(val)
            # For now, Rexster seems to support only one key/value query
            break

        return path


    def all(self):
        """Return the results represented by this Query as a list.
        This results in an execution of the underlying query.
        """
        return list(self)


    def one(self):
        """Return exactly one result or raise an exception.

        Raises ``sqlalchemy.orm.exc.NoResultFound`` if the query selects
        no rows.  Raises ``sqlalchemy.orm.exc.MultipleResultsFound``
        if multiple object identities are returned, or if multiple
        rows are returned for a query that does not return object
        identities.

        Calling one() results in an execution of the underlying query.
        """
        ret = list(self)

        l = len(ret)
        if l == 1:
            return ret[0]
        elif l == 0:
            raise NoResultFound("No row was found for one()")
        else:
            raise MultipleResultsFound("Multiple rows were found for one()")


    def first(self):
        """Return the first result of this Query or None if the result doesn't
        contain any row.

        Calling ``first()`` results in an execution of the underlying query.
        """
        ret = list(self)[0:1]
        if len(ret) > 0:
            return ret[0]
        else:
            return None


    def slice(self, start, stop):
        """apply LIMIT/OFFSET to the ``Query`` based on a "
        "range and return the newly resulting ``Query``."""

        if start is not None and stop is not None:
            self._offset = (self._offset or 0) + start
            self._limit = stop - start
        elif start is None and stop is not None:
            self._limit = stop
        elif start is not None and stop is None:
            self._offset = (self._offset or 0) + start

        if self._offset == 0:
            self._offset = None


    def limit(self, limit):
        """Apply a ``LIMIT`` to the query and return the newly resulting
        ``Query``.
        """
        self._limit = limit

    def offset(self, offset):
        """Apply an ``OFFSET`` to the query and return the newly resulting
        ``Query``.
        """
        self._offset = offset


    def _log(self, message, level=10):
        """ Thin wrapper for logging purposes.

        :param message: The message to log.
        :type message: str
        :param level: The level of the log.
        :type level: int
        :returns: This object itself.
        :rtype: graphalchemy.ogm.query.Query
        """
        if self.logger is not None:
            self.logger.log(level, message)
        return self



