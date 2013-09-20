# OGM

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





# Model definition


Your domain-specific objects remains untouched, they can be raw object definitions. Notably, they do not require to extend a specific class :


    # Raw object definition
    # models.py

    class Website(object):
        def __init__(self)
            self.name = None
            self.domain = None

    class Page(object):
        def __init__(self)
            self.title = None
            self.url = None


Then, you have to explain the database which models you want to persist in the database. The metadata object stores all this data. Note that this is completely independant from your objects. It's somewhat like the declaration of your tables in a relationnal database.


    # Mapping definition
    # mapping.py

    from graphalchemy.blueprints.types import String
    from graphalchemy.blueprints.types import Url
    from graphalchemy.blueprints.types import DateTime
    from graphalchemy.blueprints.schema import Property
    from graphalchemy.blueprints.schema import Relationship
    from graphalchemy.blueprints.schema import Metadata

    metadata = Metadata()

    websiteHasPage = Relationship('WebsiteHasPage', metadata,
        Property('created', DateTime(), nullable=False)
    )
    website = Node('Website', metadata,
        Property('name', String(127), nullable=False, indexed='search'),
        Property('domain', Url(2801))
    )
    page = Node('Page', metadata,
        Property('title', String(127), nullable=False, indexed=True),
        Property('url', Url(2801), unique=True)
    )



Eventually, you need to bind each of these declarations to existing objects. It's at this point that the objects are instrumented. Some custom accessors are added.


    # Mapping binding
    # still in mapping.py

    mapper(WebsiteHasPage, websiteHasPage)
    mapper(Website, website, adjacencies={
        'pages': Adjacency(
            website,
            websiteHasPage,
            unique=True,
            nullable=True,
            direction=Relationship.OUT
        )
    })
    mapper(Page, page, adjacencies={
        'website': Adjacency(
            page,
            websiteHasPage,
            unique=True,
            nullable=False,
            direction=Relationship.IN
        )
    })



# Model-specific repositories :

Repositories can be loaded directly from the OGM :

    repository = ogm.repository('Website')


Easy entity creation and pre-persistence :

    website = repository(domain="http://www.foodnetwork.com")
    website = repository.create(domain="http://www.allrecipes.com")


SQL-alchemy like API for querying, with automatic index selection :

    repository = ogm.repository('User')
    users = repository.filter(firstname="Joe")
    users = repository.filter(firstname="Joe", lastname="Miller")


