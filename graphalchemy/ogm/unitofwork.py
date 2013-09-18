from graphalchemy.ogm.state import InstanceState


class UnitOfWork(object):

    def __init__(self, client, identity_map, metadata_map, logger=None):
        self.client = client
        self.identity_map = identity_map
        self.metadata_map = metadata_map
        self.logger = logger


    def register_object(self, obj, state):

        if state == 'new':

            class_meta = self.metadata_map.for_object(obj)

            if obj in self.identity_map:
                identity = self.identity_map[obj]

                self._log("Found in identity map : updating "+str(identity.id))
                # Get data to update
                data = {}
                for property in class_meta.properties:
                    python_value = getattr(obj, property.name_py)
                    property.validate(python_value)
                    if identity.attribute_has_changed(property.name_py, python_value):
                        data[property.name_db] = property.to_db(python_value)
                        self._log('  Property '+str(property)+' changed to '+str(python_value)+', updating.')
                    else:
                        self._log('  Property '+str(property)+' has not changed.')

                # Update
                if len(data):
                    response = self.client.update_vertex(identity.id, data)
                    self._log("Updated "+str(identity.id))
                else:
                    self._log("Nothing to update in "+str(identity.id))

            else:
                self._log("Not found in identity map : inserting.")

                # Get data to update
                data = {}
                for property in class_meta.properties:
                    self._log('  Property '+str(property)+' is new.')
                    python_value = getattr(obj, property.name_py)
                    property.validate(python_value)
                    data[property.name_db] = property.to_db(python_value)
                data[class_meta.model_name_storage_key] = class_meta.model_name

                # Insert
                response = self.client.create_vertex(data)

                # Update identity map
                id = response.content['results']['_id']
                self._log('  Property '+str('id')+' updated to '+str(id))
                obj.id = id
                self.identity_map[obj] = InstanceState(obj)
                self.identity_map[obj].update_id(id)
                self.identity_map[obj].update_attributes(data)



    def _log(self, message, level=10):
        if self.logger is None:
            return self
        self.logger.log(level, message)