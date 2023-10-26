from copy import deepcopy

class DBTable():

    def __init__(self, database, sql_query: str, is_entity: bool):
        self.name = sql_query.split(" ")[5]  # follows 'create table if not exists'
        self.database = database
        self.is_entity = is_entity
        self.database.execute(sql_query)
        self.database.execute("DESC " + self.name)
        self.cols = self.database.cursor.fetchall()

    def columns(self, full_desc: bool = False, include_primary: bool =True):
        cols = self.cols
        if full_desc:
            return deepcopy(cols)
        else:
            if include_primary:
                return [col[0] for col in cols]
            # else exclude artificial primary key of type int
            return [col[0] for col in cols if col[3] != 'PRI' or col[1] != 'int']
        
    def insert(self, columns, values):
        '''Inputs columns and values may be lists of strings or just one string'''
        if not isinstance(columns, list):
            columns = [columns]
        if not isinstance(values, list):
            values = [values]
        columns = ", ".join(columns)
        values = "'" + "', '".join(values) + "'"
        self.database.execute(f"""INSERT INTO {self.name} ({columns}) 
                                    VALUES ({values});""")
        self.database.db.commit()
        
    # todo : fill, update, interrogate