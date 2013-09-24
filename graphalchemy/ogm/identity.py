from graphalchemy.ogm.state import InstanceState


class IdentityMap(dict):
    ''' The container for the InstanceStates, InstanceStates are being meant to represent at the same time the python objects and the Titan DB nodes
    '''
    
    def __init__(self):
        # Super?
        pass


    def add(self, obj):
        ''' Defines the instance state for a python object and adds it and it's InstanceState to the Itself.
            WHAT EXACTLY is the 'obj' parameter? 
        '''
        if obj in self:
            return self
        state = InstanceState(obj)
        dict.__setitem__(self, obj, state)  # Add to the dictionary the obj:state reference ATTENTION! WE SHOULD use WEAKREFERENCES 
                                            # to the objects, rather then the bold references, to avoid keeping them alive for too long


    def get_by_id(self, id):
    	for obj, state in self.iteritems():     # This is not very efficient if you are performing searches on the dicts: instead of having
                                                # log(n) efficiency, it is going to be an efficiency i time n. It might be better to define a second dictionary, specifically on the IDs
    		print obj
    		if obj.id == id:
    			return obj
		return None
