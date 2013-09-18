#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================


# ==============================================================================
#                                  FIXTURE GENERATION
# ==============================================================================

class AbstractFixture(object):
    """ Base class for fixtures. Fixtures are designed to set the database in a 
    known state. This is usefull to perform tests that hit the database.
    
    Example use : 
    >>> fixture = PageFixture(ogm)
    >>> fixture.load()
    >>> element = fixture.get('Element1')
    >>> # Do your tests here
    >>> fixture.clean()
    """

    def __init__(self, em, logger=None):
        """ Creates a fixture object, injects dependencies.
        
        :param em: A graph Object Manager instance.
        :type em: graphalchemy.ogm.BulbsObjectManager 
        :param logger: a logger instance.
        :type logger: logging.Logger
        """
        self.em = em
        self._parent = {}
        self._fixtures = {}
        self._unpersisted_fixtures = {}
        self.verbose = False
        self.logger = logger


    def get(self, which, persisted=True):
        """ Returns a fixture element specified by its key.
        
        :returns: The requested element.
        :rtype: graphalchemy.model.Node, graphalchemy.model.Relationship 
        """
        if persisted:
            return self._fixtures[which]
        return self._unpersisted_fixtures[which]


    def get_parent(self, which):
        """ Returns a parent fixture specified by its key.
        
        :returns: The requested fixture.
        :rtype: graphalchemy.fixture.abstract.AbstractFixture 
        """
        return self._parent[which]


    def load(self):
        """ Wrapper around _load_all for logging purposes.
        
        :returns: This object itself.
        :rtype: graphalchemy.fixture.abstract.AbstractFixture
        """
        self._log('Loading fixtures : start')
        self._load_all()
        self.em.commit()
        self._log('Loading fixtures : stop')
        return self
    
        
    def _load_all(self):
        """ Loads this fixture, including its parents..
        
        :returns: This object itself.
        :rtype: graphalchemy.fixture.abstract.AbstractFixture
        """
        for parent in self._parent.itervalues():
            parent._load_all()
        
        self.build()
        
        self._load_self()
        self._log('  Fixture loaded : '+str(self))
        
        return self
    
    
    def _load_self(self):
        """ Loads the elements of this particular fixture.
        
        :returns: This object itself.
        :rtype: graphalchemy.fixture.abstract.AbstractFixture
        """
        for fixture in self._fixtures.itervalues():
            fixture.save()
            self._log(u"    Inserted "+unicode(fixture))
        return self
    
    
    def build(self):
        """ Builds every fixture element one by one, stores them in the _fixture 
        attribute, waiting to be persisted.
        
        :returns: This object itself.
        :rtype: graphalchemy.fixture.abstract.AbstractFixture
        """
        raise NotImplementedError("Abstract class : you need to implement this method yourself.")
        
    
    def clean(self):
        """ Cleans the fixture after use. Only public method to use.
        
        :returns: This object itself.
        :rtype: graphalchemy.fixture.abstract.AbstractFixture
        """
        self._log('Cleaning fixtures : start')
        self._clean_all()
        self.em.commit()
        self._log('Cleaning fixtures : stop')
        return self
    
    
    def _clean_all(self):
        """ Cleans the fixture after use.
        
        :returns: This object itself.
        :rtype: graphalchemy.fixture.abstract.AbstractFixture
        """
        
        self.clean_self()
        self._log('  Fixture cleaned : '+str(self))
    
        for parent in self._parent.itervalues():
            parent._clean_all()
                
        self._fixtures = {}
        self._unpersisted_fixtures = {}
                
        return self
        
    
    def clean_self(self):
        """ Removes the elements loaded in the database by this fixture.
        
        :returns: graphalchemy.fixture.abstract.AbstractFixture -- this object 
        itself.
        """
        raise NotImplementedError("Abstract class : you need to implement this method yourself.")
        
        
    def set_logger(self, logger):    
        """ Recursively sets the logger to all fixtures (including parents). 
        
        :param logger: a logger instance.
        :type logger: logging.Logger
        :returns: graphalchemy.fixture.abstract.AbstractFixture -- this object 
        itself.
        """
        self.logger = logger
        for parent in self._parent.itervalues():
            parent.set_logger(logger)
        return self
    
        
    def _log(self, message, level=10):
        """ Thin wrapper for logging purposes.
        
        :param message: The message to log.
        :type message: str
        :param level: The level of the log.
        :type level: int
        :returns: graphalchemy.fixture.abstract.AbstractFixture -- this object 
        itself.
        """
        if self.logger:
            self.logger.log(level, message)
        return self
