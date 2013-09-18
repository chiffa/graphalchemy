GraphAlchemy
============

GraphAlchemy - No more magic.

GraphAlchemy is a Object-Graph Mapper (OGM) for Python. It aims to be compatible
with all Blueprints-enabled graph implementations, as well as Neo4J.

Disclaimer : this module is under active development. It's dirty, full of bugs,
only partially tested, and its APIs will change a lot in the incoming months. Use
at your own risk. Contributions welcome.


# Overview

## Standard OGM functionnalities :

Loading the OGM :

    from graphalchemy.ogm import BulbsObjectManager
    ogm = BulbsObjectManager("http://localhost:8182/graphs", "graph", model_paths=['my.models.nodes'])

Querying with simple filters :

    websites = ogm.repository('Website').filter(domain='http://www.foodnetwork.com')

Deleting entities :

    website_del = websites[0]
    ogm.delete(website_del)
    ogm.flush()

Updating entities :

    website_upd = websites[1]
    website_upd.name = 'FoodNetwork'
    ogm.add(website_upd)
    ogm.flush()

Creating entities :

    website_new = Website(name="AllRecipes", domain="http://www.allrecipes.com")
    ogm.add(website_new)
    ogm.flush()

Performing lazy-loaded traversals :

    website_upd.pages()


## Model definition :

For now, the models can be built following the bulbs specification, extending
another class :

    from graphalchemy.model import Node
    from bulbs.property import String
    from graphalchemy.property import Url

    class Website(Node):
        name = String()
        domain = Url(indexed=True)

    class Page(Node):
        title = String()
        url = Url(indexed=True)

    website = Website(domain="http://www.allrecipes.com")
    ogm.add(website)
    ogm.flush()


Ultimately, the object-to-graph mapping will be performed through a metadata builder,
which will not require the model object to extend a specific class :


    class Website(object):
        def __init__(self)
            self.name = None
            self.domain = None

    class Page(object):
        def __init__(self)
            self.title = None
            self.url = None

    from graphalchemy.property import String
    from graphalchemy.property import Url
    from graphalchemy.property import DateTime
    from graphalchemy.metadata import Property
    from graphalchemy.metadata import Relationship
    from graphalchemy.metadata import Metadata

    metadata = Metadata()

    website = Node('Website', metadata,
        Property('name', String(127), nullable=False),
        Property('domain', Url(2801))
    )
    mapper(Website, website, properties={
        'pages': relationship(WebsiteHasPage, multi=True, nullable=True, direction=OUT)
    })

    page = Node('Page', metadata,
        Property('title', String(127), nullable=False),
        Property('url', Url(2801))
    )
    mapper(Page, page, properties={
        'website': Relationship(WebsiteHasPage, multi=False, nullable=False, direction=IN)
    })

    websiteHasPage = Relationship('WebsiteHasPage', metadata,
        Property('created', DateTime, nullable=False, default=datetime.now)
    )
    mapper(WebsiteHasPage, websiteHasPage,
        out_node=Website,
        in_node=Page
    )



## Model-specific repositories :

Repositories can be loaded directly from the OGM :

    repository = ogm.repository('Website')

Easy entity creation and pre-persistence :

    website = repository(domain="http://www.foodnetwork.com")
    website = repository.create(domain="http://www.allrecipes.com")

SQL-alchemy like API for querying, with automatic index selection :

    repository = ogm.repository('User')
    users = repository.filter(firstname="Joe")
    users = repository.filter(firstname="Joe", lastname="Miller")


# Installation

As of today, GraphAlchemy is built on top of bulbs, and, as such, requires bulbs
0.3.14 as a dependency (managed by pip).

To install GraphAlchemy :

```
pip install git+https://github.com/chefjerome/graphalchemy.git
```


# Design defense

GraphAlachemy is built with the following ideas in mind :

## No magic

GraphAlchemy does not make use of fancy Pythonic tricks. You stay in control of
what happens :
- you control when flushes happen
- you can create objects without pre-persisting them
- you can merge pre-hydrated objects with their image in the database
_ ...

## No globals

GraphAlchemy does not use global variables, connections or configurations. Each
Object-Graph-Mapper lives on its own.

For now, it helps you be sure that you are always using the very same connection
to the database, and the same session.

Ultimately, this will allow to deal with several databases or transactions at once.

## Domain objects are domain objects

They should not be polluted with database-specific methods or properties. The
persistence of these objects in a database is a separate concern, and, as such,
must be handled by a separate service.

Thus, a model shall not have a `save()` method. The OGM is precisely here to
perform such an operation.

Ultimately, this will allow you to decouple the object-to-database mapping from
the object, through a Metadata class. The idea behind that is to enable you
persist objects in several databases. For instance, persist the same object
in MySQL with SQLAlchemy, and in Titan with GraphAlchemy.

## SQLAlchemy-inspired interface

We try to use an interface similar to SQLAlchemy, so developers that have this
background find a friendly interface.

# LICENSE and AUTHOR:

Author:: Antoine Durieux <adurieux@chefjerome.com>

Copyright:: 2013, Jerome, SAS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

