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

prompt_french = PromptTemplate(template=template, input_variables=["question"])

template = """You will be provided with a question delimited by triple backsticks.
The question is asked by a recruiter about some candidates for a job and their CV.
Your task is to determine what kind of question that is.

    < Possible outputs>
    - single (if the question asked involves only one candidate) ;
    - transverse (if the question involves several candidates/CV) ;
    - unknown (if you cannot predict for sure).
    </Possible outputs>
    
    <EXEMPLES>
    Question : "What is the e-mail of Julie Delon ?"
    single

    Question : "List the e-mail addresses of candidates"
    transverse

    Question : "What candidates work at Illuin Technology ?"
    transverse

    Question : "Who is the most skilled ?"
    transverse

    Question : "What position did Jean Durand last occupy ?"
    single

    Question : "What are the experiences of Jacques Lafitte ?"
    single

    Question : "List the experiences of the first candidate"
    single

    Question : "Who is the most fitted candidate for the a Data Scientist job ?"
    transverse
    </EXEMPLES>

    Question : ```{question}```
    """

prompt_english = PromptTemplate(template=template, input_variables=["question"])

template_predict_operation = """You will be provided with a query about some candidates delimited by triple backsticks.
Your task is to determine what kind of operation the query involves, among a list of possible operations.
Your output should be only one word that is one of the possible operations :
    <possible operations> =     [
                                "Sort",
                                "Comparison",
                                "MinMax",
                                "Condition",
                                "All,
                                "Unknown"
                                ]

Following are some guidelines to make up your mind, ordered by priority.

* If you detect a sorting request (with words such as 'sort', 'sorted'), you should predict "Sort"
* Otherwise, if you receive a comparative query involving words such as 'than', 'at least', 'at most', 'more than', 'less than',
or adjectives with the comparative suffixe '-er' (examples : 'lower', 'better'...), you should predict "Comparison".
* Otherwise, if you find superlatives such as 'most', 'least', 'the more', 'the less', 
or adjectives with the superlative suffixe '-est' (examples : 'lowest', 'best'...), you should predict "MinMax".
* Otherwise, if you find the expression of a condition, involving words such as 'such that', 'what are the [...] that', 'the [...] who', 'select',
you should predict "Condition".
Examples of conditions : 'what candidates studied in Lyon ?' or 'give me the names of the candidates who know C++'
* Otherwise, if the query asks for a list of a piece of information about all candidates without condition,
you should predict "All". For instance : 'what are the names of the candidates ?' or
'give me the phone numbers of all candidates' are such queries.
* Otherwise, output "Unknown".

Question : ```{question}````
Your prediction :"""

prompt_predict_operation = PromptTemplate(template=template_predict_operation, input_variables=["question"])