#! /usr/bin/env python
#-*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from graphalchemy.ogm.query import Query


# ==============================================================================
#                                     SERVICE
# ==============================================================================

class Repository(object):
    """ Repositories are shortcuts that allow simple querying of entities.

    Repositories can be loaded directly from the OGM :
    >>> repository = ogm.repository('Website')

    Easy entity creation and pre-persistence :
    >>> website = repository(domain="http://www.foodnetwork.com")
    >>> website = repository.create(domain="http://www.allrecipes.com")

    SQL-alchemy like API for querying, with automatic index selection :
    >>> repository = ogm.repository('User')
    >>> users = repository.filter(firstname="Joe")
    >>> users = repository.filter(firstname="Joe", lastname="Miller")
    """

    def __init__(self, session, model, class_, logger=None):
        """ Loads a repository.

        :param session: The session to perform requests against.
        :type session: graphalchemy.ogm.session.Session
        :param model: The model instance of the current class.
        :type model: graphalchemy.blueprints.schema.Model
        :param class_: The class that is actually mapped.
        :type class_: object
        :param logger: An optionnal logger.
        :type logger: logging.Logger
        """
        self.session = session
        self.model = model
        self.class_ = class_
        self.logger = logger


    def __call__(self, *args, **kwargs):
        """ Creates an instance of the mapped class, initialized with the
        given parameters.

        Example use:
        >>> website = repository(domain="http://www.foodnetwork.com")

        :param class_: The class that is actually mapped.
        :type class_: object
        """
        return self.create(*args, **kwargs)


    def create(self, *args, **kwargs):
        """ Creates an instance of the mapped class, initialized with the
        given parameters.

        Example use :
        >>> website = repository.create(domain="http://www.allrecipes.com")

        :param class_: The class that is actually mapped.
        :type class_: object
        """
        return self.class_(*args, **kwargs)


    def get(self, id):
        """ Retrieves an element from its id.

        Example use :
        >>> website = repository.get(123)

        :param id: The element id.
        :type id: int
        :returns: The object with the given id in the database.
        :rtype: object
        """

        # Retrieve from DB or identity map
        response, loaded = self.session.get_vertex(id)
        if not loaded:
            self._log('Object found in entity map')
            return response
        self._log('Object not found in entity map')
        results = response.content['results']

        # Verify type
        _type = results.pop('_type')
        self._check_type(_type)

        # Verify model_name
        model_name = results.pop(self.model.model_name_storage_key)
        self._check_model_name(model_name)

        # Verify id
        _id = results.pop('_id')
        self._check_id(_id, id)

        # Build object
        obj = self._build_object(results)
        obj.id = id

        self.session.add_to_identity_map(obj)
        return obj

    def filter(self, **kwargs):
        """ We have to pre-process the query here to use the right index.
        """
        query = Query(self.session)
        # If one of the arguments is indexed, we use it first.
        indices = self.model._useful_indices_among(kwargs)
        if len(indices):
            index_name = indices[0]
            key = index_name
            value = kwargs[index_name]
            query.filter_on_index(index_name, key, value)
            kwargs.pop(index_name)
        # Else, we simply use the index on the model name.
        else:
            index_name = self.model.model_name_storage_key
            key = index_name
            value = self.model.model_name
            query.filter_on_index()

        query.filter(**kwargs)
        return query


    def _build_object(self, results):
        obj = self.class_(results)
        self._update_object(obj, results)
        return obj


    def _update_object(self, obj, results):
        for property_db, value_db in results.iteritems():
            found = False
            for property in self.model._properties:
                if property.name_db != property_db:
                    continue
                found = True
                break
            if not found:
                raise Exception('Property retrieved but not found : '+property_db)
            value_py = property.to_py(value_db)
            setattr(obj, property.name_py, value_py)
        return obj


    def _check_model_name(self, model_name):
        if model_name != self.model.model_name:
            raise Exception('Expected vertex, got '+str(model_name))
        return True


    def _check_id(self, _id, id):
        if _id != id:
            raise Exception('Expected '+str(id)+', got '+str(_id))
        return True


    def _check_type(self, _type):
        if _type == 'vertex' and self.model.is_node():
            return True
        elif _type == 'edge' and self.model.is_relationship():
            return True
        raise Exception('Received '+_type+' for '+self.model.model_type)


    def _log(self, message, level=10):
        """ Thin wrapper for logging purposes.

        :param message: The message to log.
        :type message: str
        :param level: The level of the log.
        :type level: int
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.Validator
        """
        if self.logger is not None:
            self.logger.log(level, message)
        return self