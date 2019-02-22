import inspect
import sqlite3

SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"
CREATE_TABLE_SQL = "CREATE TABLE {name} ({fields});"
INSERT_SQL = 'INSERT INTO {name} ({fields}) VALUES ({placeholders});'
SELECT_ALL_SQL = 'SELECT {fields} FROM {name};'
SELECT_WHERE_SQL = 'SELECT {fields} FROM {name} WHERE {query};'

SQLITE_TYPE_MAP = {
    int: "INTEGER",
    float: "REAL",
    str: "TEXT",
    bytes: "BLOB",
    bool: "INTEGER",  # 0 or 1
}


class Database:

    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def _execute(self, sql, params=None):
        # print(sql)
        if params:
            return self.conn.execute(sql, params)
        return self.conn.execute(sql)

    @property
    def tables(self):
        return [x[0] for x in self._execute(SELECT_TABLES_SQL).fetchall()]

    def create(self, table):
        self._execute(table._get_create_sql())

    def save(self, instance):
        sql, values = instance._get_insert_sql()
        cursor = self._execute(sql, values)
        instance._data['id'] = cursor.lastrowid
        self.conn.commit()

    def all(self, table):
        sql, fields = table._get_select_all_sql()
        result = []
        for row in self._execute(sql).fetchall():
            new_fields, row = self._dereference(table, fields, row)
            data = dict(zip(new_fields, row))
            result.append(table(**data))
        return result

    def get(self, table, id):
        sql, fields, params = table._get_select_where_sql(id=id)
        row = self._execute(sql, params).fetchone()
        fields, row = self._dereference(table, fields, row)
        data = dict(zip(fields, row))
        return table(**data)

    def _dereference(self, table, fields, row):
        new_fields = []
        new_values = []
        for field, value in zip(fields, row):
            if field.endswith('_id'):
                # strip off "_id" to find field name
                field = field[:-3]
                fk = getattr(table, field)
                # fetch object with the given ID
                value = self.get(fk.table, value)
            new_fields.append(field)
            new_values.append(value)
        return new_fields, new_values


class Table:

    def __init__(self, **kwargs):
        self._data = {
            'id': None
        }
        for key, value in kwargs.items():
            self._data[key] = value

    def __getattribute__(self, key):
        _data = object.__getattribute__(self, '_data')
        if key in _data:
            return _data[key]
        return object.__getattribute__(self, key)

    @classmethod
    def _get_name(cls):
        return cls.__name__.lower()

    @classmethod
    def _get_create_sql(cls):
        fields = [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT")
        ]

        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append((name, field.sql_type))
            elif isinstance(field, ForeignKey):
                fields.append((name + "_id", "INTEGER"))

        fields = [" ".join(x) for x in fields]
        return CREATE_TABLE_SQL.format(name=cls._get_name(),
                                       fields=", ".join(fields))

    def _get_insert_sql(self):
        cls = self.__class__
        fields = []
        placeholders = []
        values = []

        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
                values.append(getattr(self, name))
                placeholders.append('?')
            elif isinstance(field, ForeignKey):
                fields.append(name + "_id")
                values.append(getattr(self, name).id)
                placeholders.append('?')

        sql = INSERT_SQL.format(name=cls._get_name(),
                                fields=", ".join(fields),
                                placeholders=", ".join(placeholders))

        return sql, values

    @classmethod
    def _get_select_all_sql(cls):
        fields = ['id']
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
            if isinstance(field, ForeignKey):
                fields.append(name + "_id")

        sql = SELECT_ALL_SQL.format(name=cls._get_name(),
                                    fields=", ".join(fields))

        return sql, fields

    @classmethod
    def _get_select_where_sql(cls, **kwargs):
        fields = ['id']
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
            if isinstance(field, ForeignKey):
                fields.append(name + "_id")

        filters = []
        params = []
        for key, value in kwargs.items():
            filters.append(key + " = ?")
            params.append(value)

        sql = SELECT_WHERE_SQL.format(name=cls._get_name(),
                                      fields=", ".join(fields),
                                      query=" AND ".join(filters))
        return sql, fields, params


class Column:

    def __init__(self, type):
        self.type = type

    @property
    def sql_type(self):
        return SQLITE_TYPE_MAP[self.type]


class ForeignKey:

    def __init__(self, table):
        self.table = table
