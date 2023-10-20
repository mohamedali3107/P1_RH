
def list_of_names(cursordb):
    cursordb.execute("SELECT FirstName, FamilyName FROM candidates;")
    sql_outputs = cursordb.fetchall()
    names = [res[0] + ' ' + res[1] for res in sql_outputs]
    return names

def list_of_fields(entity):  # as of now, entity corresponds to candidates
    # entity could be a class, including entity table name, relation table name,
    # their respective "fields" (columns) would be retrieved from the prompt
    # used to (previously used to) create the entity table
    # or saved as an attribute
    # todo : implement
    # Temporary implementation :
    fields = [  "FileName"
                "FirstName",
                "FamilyName",
                "Gender",
                "Email",
                "PhoneNumber",
                "LinkedIn",
                "Webpage",
                "Country",
                "City"
                ]
    return fields

def entities(cursordb) :
    # todo : implement
    return ["candidates"]

def all_fields(cursordb) :
    entities = entities(cursordb)
    fields = []
    for entity in entities :
        fields.extend(list_of_fields(entity))