#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Responsible for communication with the Rexter Server that manages the remote
access to the TitanDB
'''

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

import requests

# ==============================================================================
#                                    Base Classes
# ==============================================================================


class Client(object):
    '''
    Establishes and maintains a connection with a Rexter Server servent the 
    TitanDB
    '''
    
    def __init__(self,*args,**kwargs):
        self.request=''
        
    
    def add_to_request(self,string):
        

class Requests=