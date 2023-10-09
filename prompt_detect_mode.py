from langchain.prompts import PromptTemplate

template = """L'input que tu reçois est une question d'un recruteur RH portant sur un ensemble de CVs de candidats dans le domaine de la Tech. 
    
    Ta tâche est de déterminer si, pour répondre avec exactitude à la question, le recruteur doit parcourir un seul CV, tous les CVs, ou ni l'un ni l'autre. Tu dois choisir parmi les trois réponses suivantes, qui sont les seules possibles.

    <REPONSES POSSIBLES>
    - single (si le recruteur doit parcourir un seul CV pour répondre à la question) ;
    - transverse (si le recruteur doit parcourir plusieurs CVs pour répondre à la question) ;
    - unknown (si tu n'arrives pas à répondre à la question ou si l'information ne se trouve pas dans les CVs).
    </REPONSES POSSIBLES>
    
    <EXEMPLES>
    Question : "Quel est l'email de Julie Delon ?"
    single

    Question : "Donner la liste des emails des candidats."
    transverse

    Question : "Quel(s) candidat(s) travaillent chez Illuin Technology ?"
    transverse

    Question : "Quel est la personne avec le plus d'expérience ?"
    transverse

    Question : "Quel est le poste actuel de Jean Durand ?"
    single

    Question : "Quelles sont les expériences de Jacques Lafitte ?"
    single

    Question : "Lister les expériences du premier candidat ?"
    single

    Question : "Quel est le candidat le plus adapté pour le poste de Data Scientist ?"
    transverse
    </EXEMPLES>

    Question : {question}"""

prompt = PromptTemplate(template=template, input_variables=["question"])