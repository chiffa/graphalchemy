import weakref

class InstanceState(object):
    
    ADD = 'add'
    DELETE = 'delete'
    
    def __init__(self, obj):
        self.obj = weakref.ref(obj)
        self.class_ = obj.__class__
        self.state = self.ADD
        self.id = None
        self._attributes = {}
        
    def update_id(self, _id):
        if self.id is not None and _id != self.id:
            raise Exception('Identifier of the entity seems to have changed.')
        self.id = _id
        return self
    
    def update_attributes(self, _attributes):
        ''' Updates self.attributes avec les attributes fournis par l'argument. Only the attributes
                that have been explicitely passed to the update_attributes parameter will be cast into TitanDB
            @param _attributes: user-defined dictionary of attributes that is inserted into the attirbutes of the python
            @type _attributes: dictionnaire python String:String 
        '''
        self._attributes.update(_attributes)
        
    def attribute_has_changed(self, attribute, value):
        if attribute not in self._attributes:
            return True
        return (self._attributes[attribute] != value)