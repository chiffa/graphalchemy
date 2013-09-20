# Vocabulary

- **Object** : a plain Python object.

- **Vertex** (Vertices) : -
- **Edge** (Edges) : -
- **Element** (Elements) : a Vertex or an Edge.

- **Node** (Nodes) : a Vertex with a specific domain Model.
- **Relationship** (Relationships) : an Edge with a specific domain Model.
- **Model** (Models) : a Node or a Relationship.


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

