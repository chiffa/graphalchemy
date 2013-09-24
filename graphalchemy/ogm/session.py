
from graphalchemy.ogm.identity import IdentityMap
from graphalchemy.ogm.unitofwork import UnitOfWork
from graphalchemy.ogm.state import InstanceState

class Session(object):

    def __init__(self, client, metadata, logger=None):
        '''
        @param client: client to which the session will bind
        @type client:
        @param metadata: metadataobject that defines the data model that will be enforced by the session
        @type metadata: graphalchemy.blueprints.schema.MetaData
        @param logger: logger for the session
        @type logger: python.logging.logger     
        '''
        self.identity_map = IdentityMap()
        self.metadata_map = metadata
        self.client = client
        self.logger = logger

        # three types of modifications pythonic objects can undergo.
        self._update = []
        self._delete = []
        self._new = []


    def add(self, instance):
        # Once again, those are strong references; is this necessary?
        if instance in self.identity_map:
            self._update.append(instance)
        else:
            self._new.append(instance)
        return self


    def get_vertex(self, id):
        # What exactly is the object? id? The number of node within Titan's natural index?
        obj = self.identity_map.get_by_id(id)
        if obj:
            return obj, False
        return self.client.get_vertex(id), True


    def add_to_identity_map(self, obj):
        # Add to the identity_map
        self.identity_map[obj] = InstanceState(obj)
        self.identity_map[obj].update_id(id)
        # self.identity_map[obj].update_attributes(data)
        return self


    def clear(self):
        self.identity_map.clear()
        self._update = []
        self._delete = []
        self._new = []
        return self


    def flush(self):

        uow = UnitOfWork(self.client, self.identity_map, self.metadata_map, logger=self.logger)

        # We need to save nodes first
        for obj in self._new:
            if self.metadata_map.is_node(obj):
                uow.register_object(obj, 'new')
                self._log("Inserted "+str(obj))
        for obj in self._new:
            if self.metadata_map.is_relationship(obj):
                uow.register_object(obj, 'new')
                self._log("Inserted "+str(obj))

        # Update all other nodes
        for obj in self._update:
            if self.metadata_map.is_node(obj):
                uow.register_object(obj, 'update')
                self._log("Updated "+str(obj))
        for obj in self._update:
            if self.metadata_map.is_relationship(obj):
                uow.register_object(obj, 'update')
                self._log("Updated "+str(obj))

        # We need to delete relations first
        for obj in self._delete:
            if self.metadata_map.is_relationship(obj):
                uow.register_object(obj, 'delete')
                self._log("Deleted "+str(obj))
        for obj in self._delete:
            if self.metadata_map.is_node(obj):
                uow.register_object(obj, 'delete')
                self._log("Deleted "+str(obj))

        return self


    def _log(self, message, level=10):
        if self.logger is None:
            return self
        self.logger.log(level, message)