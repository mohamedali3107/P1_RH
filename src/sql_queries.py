
create_candidates = """
CREATE TABLE IF NOT EXISTS candidates (
FileName varchar(30) primary key,
FirstName varchar(30),
FamilyName varchar(40),
Email varchar(30),
PhoneNumber varchar(15),
LinkedIn varchar(30),
Webpage varchar(40),
Country varchar(30)
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
