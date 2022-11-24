import mysql.connector


class ElibDBConnector:
    def __init__(self, host, user, password, database):
        self._elib_db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        self._elib_db.autocommit = True
        self._cursor = self._elib_db.cursor(buffered=True)

    def add_book(self, author, title, year_of_publishing, num_of_copies):
        exists = "SELECT EXISTS (SELECT 1 FROM books)"
        self._cursor.execute(exists)
        if self._cursor.fetchone()[0] == 1:
            id = "SELECT MAX(book_id) + 1 FROM (SELECT * FROM books) as `b*`"
            self._cursor.execute(id)
            id = self._cursor.fetchone()[0]
        else:
            id = 1

        add_book = ("INSERT INTO books "
                    "VALUES (%(id)s, %(author)s, %(title)s, %(year_of_publishing)s, %(num_of_copies)s)")
        self._cursor.execute(add_book,
                             {'id': id,
                              'author': author,
                              'title': title,
                              'year_of_publishing': str(year_of_publishing),
                              'num_of_copies': str(num_of_copies)})

    def add_reader(self, surname, name, patronymic, address):
        exists = "SELECT EXISTS (SELECT 1 FROM readers)"
        self._cursor.execute(exists)
        if self._cursor.fetchone()[0] == 1:
            library_card = "SELECT MAX(library_card) + 1 FROM (SELECT * FROM readers) as `rt*`"
            self._cursor.execute(library_card)
            library_card = self._cursor.fetchone()[0]
        else:
            library_card = 1

        add_reader = ("INSERT INTO readers "
                      "VALUES (%(library_card)s, %(surname)s, %(name)s, %(patronymic)s, %(address)s)")
        self._cursor.execute(add_reader,
                             {'library_card': library_card,
                              'surname': surname,
                              'name': name,
                              'patronymic': patronymic,
                              'address': address})

    def delete_book_or_reader(self, table, id):
        if table == 'books':
            col = 'book_id'
        elif table == 'readers':
            col = 'library_card'
        else:
            raise ValueError

        delete_rows = ("DELETE FROM {table} "
                       "WHERE {col} = {id}").format(table=table,
                                                    col=col,
                                                    id=id)
        self._cursor.execute(delete_rows)

        delete_rows = ("DELETE FROM checked_out_books "
                       "WHERE {col} = {id}").format(col=col,
                                                    id=id)
        self._cursor.execute(delete_rows)

    def delete_checked_book(self, book_id, library_card):
        delete_row = ("DELETE FROM checked_out_books "
                      "WHERE book_id = {book_id} "
                      "AND library_card = {library_card}").format(book_id=book_id,
                                                                  library_card=library_card)

    def search_book_by_id(self, id):
        search = ("SELECT * FROM books "
                  "WHERE book_id = %s")
        self._cursor.execute(search, (str(id),))
        return self._cursor.fetchall()

    def flexible_books_search(self,
                              author="",
                              title="",
                              year_of_publishing="",
                              author_accurate=False,
                              title_accurate=False,
                              year_sign="="):
        drop = ("DROP TABLE "
                "IF EXISTS flexible_search")
        self._cursor.execute(drop)

        tab = ("CREATE TABLE flexible_search AS "
               "SELECT * from books")
        self._cursor.execute(tab)

        if author != "":
            tab = ("DELETE FROM flexible_search "
                   "WHERE NOT author ")
            if author_accurate:
                tab += "= %s"
                self._cursor.execute(tab, (author,))
            else:
                tab += "LIKE %s"
                self._cursor.execute(tab, ('%' + author + '%',))

        if title != "":
            tab = ("DELETE FROM flexible_search "
                   "WHERE NOT title ")
            if title_accurate:
                tab += "= %s"
                self._cursor.execute(tab, (title,))
            else:
                tab += "LIKE %s"
                self._cursor.execute(tab, ('%' + title + '%',))

        if year_of_publishing != "":
            tab = ("DELETE FROM flexible_search "
                   "WHERE NOT year_of_publishing " + year_sign + "%s")
            self._cursor.execute(tab, (year_of_publishing,))

        tab = "SELECT * FROM flexible_search"
        self._cursor.execute(tab)

        res = self._cursor.fetchall()

        drop = ("DROP TABLE "
                "IF EXISTS flexible_search")
        self._cursor.execute(drop)

        return res

    def get_table_data(self, table_name):
        table = "SELECT * FROM {table_name}".format(table_name=table_name)
        self._cursor.execute(table)
        return self._cursor.fetchall()
