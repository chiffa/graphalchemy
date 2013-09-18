#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================

from datetime import datetime

class Base(object):
    def __init__(self, *args, **kwargs):
        for arg in args:
            for key in arg:
                setattr(self, key, arg[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


class Website(Base):
    def __init__(self, *args, **kwargs):
        self.element_type = "Website"
        self.name = None
        self.domain = None
        self.description = None
        self.content = None
        super(Website, self).__init__(*args, **kwargs)

class Page(Base):
    def __init__(self, *args, **kwargs):
        self.element_type = "Page"
        self.title = None
        self.url = None
        super(Page, self).__init__(*args, **kwargs)

class WebsiteHostsPage(Base):
    def __init__(self, *args, **kwargs):
        self.label = 'hosts'
        self.since = None
        self.accessible = None
        super(WebsiteHostsPage, self).__init__(*args, **kwargs)


from graphalchemy.blueprints.schema import MetaData
from graphalchemy.ogm.mapper import Mapper
metadata = MetaData()
mapper = Mapper()

from graphalchemy.blueprints.schema import Relationship
from graphalchemy.blueprints.schema import Node
from graphalchemy.blueprints.schema import Adjacency
from graphalchemy.blueprints.types import String
from graphalchemy.blueprints.types import Boolean
from graphalchemy.blueprints.types import Url
from graphalchemy.blueprints.types import DateTime
from graphalchemy.blueprints.schema import Property

website = Node('Website', metadata,
    Property('name', String(127), nullable=False, indexed=True),
    Property('domain', Url(2801)),
    Property('description', String(1024)),
    Property('content', String(1024))
)
page = Node('Page', metadata,
    Property('title', String(127), nullable=False),
    Property('url', Url(2801))
)

websiteHostsPageZ = Relationship('hosts', metadata,
    Property('since', DateTime, nullable=False, default=datetime.now),
    Property('accessible', Boolean())
)

websiteHostsPage_out = Adjacency(Website, WebsiteHostsPage,
    direction=Relationship.OUT,
    multi=True,
    nullable=True
)
websiteHostsPage_in = Adjacency(Page, WebsiteHostsPage,
    direction=Relationship.IN,
    multi=False,
    nullable=False
)


mapper(WebsiteHostsPage, websiteHostsPageZ)
mapper(Page, page, properties={
    'isHostedBy': websiteHostsPage_in
})
mapper(Website, website, properties={
    'hosts': websiteHostsPage_out
})


website_obj = Website()
website_obj.name = 'AllRecipes'
website_obj.domain = 'http://allrecipes.com'
website_obj.description = 'Interesting recipe website'
website_obj.content = 'A lot !'

metadata_map = {
    'Website': website
}
identity_map = {}

from bulbs.titan import TitanClient
client = TitanClient(db_name="graph")
from bulbs.rest import log
log.setLevel(1)


from graphalchemy.ogm.session import Session
ogm = Session(client=client, metadata=metadata, logger=log)
    
ogm.add(website_obj)
ogm.flush()

website_obj.name = 'AllRecipes 2'
ogm.add(website_obj)
ogm.flush()


