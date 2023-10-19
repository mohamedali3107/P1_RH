
def list_of_names(cursor_db):
    cursor_db.execute("SELECT FirstName, FamilyName FROM candidates;")
    sql_outputs = cursor_db.fetchall()
    names = [res[0] + ' ' + res[1] for res in sql_outputs]
    return names

def list_of_fields(cursor_db):
    cursor_db.execute("SELECT FirstName, FamilyName FROM candidates;")
    sql_outputs = cursor_db.fetchall()
    names = [res[0] + ' ' + res[1] for res in sql_outputs]
    return names