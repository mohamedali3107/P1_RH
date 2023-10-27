from config_database_mysql import config_candidates as candidates

prompt_languages = """You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find the languages spoken with the corresponding proficiency level by the person in this Curriculum Vitae and provide the comprehensive list of these. If a language name is not given in English, translate it to English. If you find, in this Curriculum Vitae, a language name without a specified proficiency level, you should output 'Unknown' instead of the proficiency level.
Do not provide answer out of the Curriculum Vitae.
Your final output should be a list of tuples of strings given in title case and in English, in the following format:

[(Language 1, Proficiency level 1), (Language 2, Proficiency level 2), (Language 3, Proficiency level 3)]

Here are some examples of final outputs:

<EXAMPLE 1>
[('French', 'Native'), ('English', 'Fluent'), ('Italian', 'Basic'), ('Chinese', 'Notions')]
</EXAMPLE 1>

<EXAMPLE 2>
[('English', 'Native'), ('French', 'Fluent')]
</EXAMPLE 2>

<EXAMPLE 3>
[('Spanish', 'Fluent'), ('Swedish', 'Unknown')]
</EXAMPLE 3>

Curriculum Vitae : ```{context}```
"""

entity_name = 'languages'
entity_primary_key = 'NameLanguage'
type_language = 'varchar(30)'

relation_name = 'speaks'
relation_col = 'Level'
type_relation = 'varchar(30)'

sql_create_languages = f"""CREATE TABLE IF NOT EXISTS {entity_name} (
                        {entity_primary_key} {type_language} PRIMARY KEY
                        );"""

sql_create_speaks = f"""CREATE TABLE IF NOT EXISTS {relation_name} (
                     id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                     {entity_primary_key} {type_language},
                     {candidates.primary_key} {candidates.primary_type},
                     {relation_col} {type_relation},
                     FOREIGN KEY ({candidates.primary_key}) REFERENCES
                     {candidates.table_name}({candidates.primary_key}),
                     FOREIGN KEY ({entity_primary_key}) REFERENCES
                     {entity_name}({entity_primary_key})
                     );"""


