from copy import deepcopy

class DBTable():

    def __init__(self, database, sql_query: str, is_entity: bool):
        self.name = sql_query.split(" ")[5]  # follows 'create table if not exist'
        self.database = database
        self.is_entity = is_entity
        database.execute(sql_query)
        self.database.execute("DESC " + self.name)
        self.cols = self.database.cursor.fetchall()

    def columns(self, full_desc: bool = False):
        cols = self.cols
        if full_desc:
            return deepcopy(cols)
        else:
            return [col[0] for col in cols]
        
    def insert(self, columns, values):
        columns = ", ".join(columns)
        values = "'" + "', '".join(values) + "'"
        self.database.execute(f"""INSERT INTO candidates ({columns}) 
                                    VALUES ({values});""")
        self.database.db.commit()
        
    # todo : fill, update, interrogate