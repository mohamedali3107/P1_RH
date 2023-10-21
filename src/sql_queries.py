import prompts.prompt_candidates as pr_candidates

dict_candidates = pr_candidates.dict_candidates


create_candidates = """
CREATE TABLE IF NOT EXISTS candidates (
FileName varchar(50) primary key,
FirstName varchar(40),
FamilyName varchar(40),
Gender varchar(20),
Email varchar(30),
PhoneNumber varchar(25),
LinkedIn varchar(40),
Webpage varchar(40),
Country varchar(30),
City varchar(30)
);
"""

create_languages = """
CREATE TABLE IF NOT EXISTS languages (
NameLanguage varchar(30) primary key
);
"""

create_speaks = """
CREATE TABLE IF NOT EXISTS speaks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    NameLanguage varchar(30),
    Candidate varchar(30),
    FOREIGN KEY (NameLanguage) REFERENCES languages (Name),
    FOREIGN KEY (Candidate) REFERENCES candidates (FileName)
);
"""
