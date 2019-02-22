import os
import unittest

DB_PATH = "./test.db"


class Test01_CreateTestDatabase(unittest.TestCase):

    def test_it(self):
        global Database, db
        from orm import Database

        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

        db = Database(DB_PATH)

        assert db.tables == []


class Test02_DefineTables(Test01_CreateTestDatabase):

    def test_it(self):
        super().test_it()
        global Table, Column, ForeignKey
        global Author, Post

        from orm import Table, Column, ForeignKey

        class Author(Table):
            name = Column(str)
            lucky_number = Column(int)

        class Post(Table):
            title = Column(str)
            published = Column(bool)
            author = ForeignKey(Author)

        assert Author.name.type == str
        assert Post.author.table == Author

        
class Test03_CreateTables(Test02_DefineTables):

    def test_it(self):
        super().test_it()

        db.create(Author)
        db.create(Post)

        assert Author._get_create_sql() == "CREATE TABLE author (id INTEGER PRIMARY KEY AUTOINCREMENT, lucky_number INTEGER, name TEXT);"
        assert Post._get_create_sql() == "CREATE TABLE post (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"

        for table in ('author', 'post'):
            assert table in db.tables
        

class Test04_CreateAuthorInstance(Test03_CreateTables):

    def test_it(self):
        super().test_it()
        global greg

        greg = Author(name="Greg Back", lucky_number=13)

        assert greg.name == "Greg Back"
        assert greg.lucky_number == 13
        assert greg.id is None


class Test05_SaveAuthorInstance(Test04_CreateAuthorInstance):

    def test_it(self):
        super().test_it()

        db.save(greg)

        assert greg._get_insert_sql() == (
            "INSERT INTO author (lucky_number, name) VALUES (?, ?);",
            [13, "Greg Back"]
        )

        assert greg.id == 1

class Test06_MoreAuthors(Test05_SaveAuthorInstance):

    def test_it(self):
        super().test_it()
        global roman

        arvie = Author(name="Viktor Arvidsson", lucky_number=33)
        db.save(arvie)
        assert arvie.id == 2

        filip = Author(name="Filip Forsberg", lucky_number=9)
        db.save(filip)
        assert filip.id == 3

        roman = Author(name="Roman Josi", lucky_number=59)
        db.save(roman)
        assert roman.id == 4


class Test07_QueryAuthors(Test06_MoreAuthors):

    def test_it(self):
        super().test_it()

        authors = db.all(Author)

        assert len(authors) == 4

        assert Author._get_select_all_sql() == (
            "SELECT id, lucky_number, name FROM author;",
            ['id', 'lucky_number', 'name'],
        )
        assert type(authors[0]) == Author
        assert {x.lucky_number for x in authors} == {9, 13, 33, 59}


class Test08_GetAuthor(Test07_QueryAuthors):

    def test_it(self):
        super().test_it()

        roman = db.get(Author, 4)
        assert type(roman) == Author
        assert Author._get_select_where_sql(id=4) == (
            "SELECT id, lucky_number, name FROM author WHERE id = ?;",
            ['id', 'lucky_number', 'name'], 
            [4],
        )
        assert roman.name == "Roman Josi"
        assert roman.lucky_number == 59


class Test09_SavePosts(Test08_GetAuthor):

    def test_it(self):
        super().test_it()

        post = Post(title="Building an ORM", published=False, author=greg)
        db.save(post)

        post2 = Post(title="Scoring Goals", published=True, author=roman)
        db.save(post2)

        assert post._get_insert_sql() == (
            "INSERT INTO post (author_id, published, title) VALUES (?, ?, ?);",
            [1, False, "Building an ORM"],
        )

class Test10_GetPost(Test09_SavePosts):

    def test_it(self):
        super().test_it()

        post = db.get(Post, 2)
        assert post.title == "Scoring Goals"

        print(post._data)
        assert post.author.id == 4
        assert post.author.name == "Roman Josi"


class Test11_AllPosts(Test10_GetPost):

    def test_it(self):
        super().test_it()

        posts = db.all(Post)

        assert posts[1].author.name == "Roman Josi"
        