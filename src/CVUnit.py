import DBTable

class CVUnit():

    def __init__(self, database, entity_name: str, relation_name: str = ''):
        self.database = database
        self.name = entity_name
        self.entity = DBTable(self.name)   # todo : complete
        self.relation = relation_name
        tables = self.database.list_tables()
        if entity_name not in tables:
            database.execute(f"""CREATE TABLE IF NOT EXISTS {entity_name};""")
        if self.relation and self.relation not in tables:
            database.execute(f"""CREATE TABLE IF NOT EXISTS {self.relation};""")

    def fill(self, cv_doc, prompt_dict: dict):
        pass

    def attributes(self):
        pass