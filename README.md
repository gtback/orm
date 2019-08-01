# orm
A toy Object Relational Mapper

This is the code used for the talk I gave on building an ORM. 

## Usage

```python
from orm import Database, Table, Column, ForeignKey

# Create reference to SQLite database file
db = Database("./test.db")

# Define tables
class Author(Table):
    name = Column(str)
    lucky_number = Column(int)

class Post(Table):
    title = Column(str)
    published = Column(bool)
    author = ForeignKey(Author)

# Create tables
db.create(Author)
db.create(Post)

# Create and save an Author in the database
greg = Author(name="Greg Back", 
              lucky_number=13)
db.save(greg)

# Fetch all Authors from the database
authors = db.all(Author)

# Fetch a specific Author from the database by ID
bob = db.get(Author, 47)

# Create object with reference to another object
post = Post(title="Building an ORM",
            published=True,
            author=greg)

# Save object with foreign key reference
db.save(post)

# Fetching an object with a foreign key
# will dereference that key
print(Post.get(55).author.name)
``` 

## Testing

This talk was developed using a technique I'm calling "Test-Driven Live Coding".
The tests in `test_orm.py` are designed to be run one at a time, and guide the
presenter (me!) to the next step that needs to be completed. They build on each
other (so are not proper "unit tests"), and can be run one-at-a-time using
`pytest -k 01` (and so on for each of the tests).


## Talk Information

PyOhio 2019
July 27-28, 2019
Columbus OH
Sunday 3:15PM, Hays Cape

---

PyTennessee 2019  
February 9-10, 2019  
Nashville TN  
Sunday 2PM, Auditorium  

### Abstract

Applications rely on data, and relational databases are a convenient way to
organize structured information. Object-relational mappers like SQLAlchemy and
Django's ORM are complex libraries, but they aren't black magic. De-mystify some
of the magic as we build a (basic) ORM in under an hour.

### Talk Description

We’ll start with some background on relational database terminology, including
CRUD, ACID, normalization, and the Active Record pattern. Next, we’ll build a
basic ORM that allows creating simple tables and inserting, querying, and
deleting records. Finally, we’ll talk about some of the challenges of building a
production-grade ORM, including caching, transactions, supporting multiple
dialects, and we’ll briefly discuss security implications of ORMs, including SQL
injection. You will leave with a greater appreciation for the inner workings of
the ORMs you use on a daily basis, while understanding the challenges that go
into building one.
