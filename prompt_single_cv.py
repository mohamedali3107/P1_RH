from langchain.prompts import PromptTemplate

template = """
Your task is to help a recruiter get the information they need from the provided CV of a candidate.
The CV will be delimited by triple backsticks.
All the information from the CV is about one individual who is the candidate.

If you did not find the answer, just say you don't know, do not try to make up an answer.
Keep the answer as concise as possible.
After giving a first answer, try scanning again the document to see if you can find other pieces of
relevant information that you did not include in your first answer. 
Then, only if you found additionnal relevant pieces of information, provide a more complete answer,
based on your previous one and the newly found relevant pieces of information.
Use the following format :

<CV> : ```
Universit´ e Paris-Saclay, Orsay et Versailles
Licence et Master 1 Math´ ematiques Fondamentales et Appliqu´ ees 2012-2014
Universit´ e Paris-Sud, Orsay
Classe pr´ eparatoire (CPGE) MPSI-MP 2010-2012

Doctorat Math´ ematiques-Informatique et monitorat en Informatique 2016-2019
Universit´ e de Lille, sous la direction de Nicolas M. Dupont
Th` ese soutenue le 29 novembre 2019 

Classe pr´ eparatoire (CPGE) MPSI-MP 2010-2012
Lyc´ ee la Martinière, Lyon
RECHERCHE
Mots-cl´ es : Informatique fondamentale, combinatoire, algorithmique, calcul formel,

Soins aupr` es d’animaux sauvages en diﬃcult´ e, notamment rapaces
ATER en Informatique 2019-2021
Universit´ e Paris-Sud, Orsay ```

<question of the recruiter>: Where did they study ?

<answer>: They studied in Université de Lille and Université Paris-Sud.

<complete answer>: They studied in Université de Lille, Université Paris-Sud, Université Paris-Saclay and Lycée la Martinière.


<CV> : ```{context}```

<question of the recruiter>: {question}
"""

prompt_generic = PromptTemplate(template=template, input_variables=["context", "question"])

template_concise = """
Your task is to help a recruiter get the information they need from the provided CV of a candidate.
The CV will be delimited by triple backsticks.
All the information from the CV is about one individual who is the candidate.

If you did not find the answer, just say you don't know, do not try to make up an answer.
Keep the answer as concise as possible, do not make a full sentence. If the question of the
recruiter is a yes-no question, answer just 'Yes' or 'No' or 'Unknown'.
Use the following format :

<CV> : ```
Universit´ e Paris-Saclay, Orsay et Versailles
Licence et Master 1 Math´ ematiques Fondamentales et Appliqu´ ees 2012-2014
Universit´ e Paris-Sud, Orsay
Classe pr´ eparatoire (CPGE) MPSI-MP 2010-2012

Doctorat Math´ ematiques-Informatique et monitorat en Informatique 2016-2019
Universit´ e de Lille, sous la direction de Nicolas M. Dupont
Th` ese soutenue le 29 novembre 2019 

Classe pr´ eparatoire (CPGE) MPSI-MP 2010-2012
Lyc´ ee la Martinière, Lyon
RECHERCHE
Mots-cl´ es : Informatique fondamentale, combinatoire, algorithmique, calcul formel,

Soins aupr` es d’animaux sauvages en diﬃcult´ e, notamment rapaces
ATER en Informatique 2019-2021
Universit´ e Paris-Sud, Orsay ```

<question of the recruiter> : Where did they study ?
<answer> : Université de Lille, Université Paris-Sud, Université Paris-Saclay, Lycée la Martinière


<CV> : ```{context}```

<question of the recruiter> : {question}
<answer> :"""

prompt_concise = PromptTemplate(template=template_concise, input_variables=["context", "question"])

template_from_field = """
You will be provided with :
* a topic (or it could be several topics)
* a piece of data about somebody regarding this topic (delimited by triple backsticks)
* a question about the data of this person
Your task is to answer the question using the provided data.
Keep it as concise as possible.
If you did not find the answer, do not try to make up an answer, just answer 'Unknown'.
If the query is a yes-no question, answer just 'Yes' or 'No' or 'Unknown'.

<EXAMPLES>
Topic    : Age
Data     : ```30```
Question : Is he or she more than 25 years old ?
Answer   : Yes

Topic    : First name, Family name
Data     : ```Luke Skywalker```
Question : What is her or his name ?
Answer   : Luke Skywalker

Topic    : Education
Data     : ```Normalien, mathématiques.\nErasmus de 8 mois à Cardiff University
\nAgrégation de mathématiques (39e/310)
\n2015-2019
\nLycée Charles et Adrien Dupuy, Clermont-Ferrand
\nClasses préparatoires PC*```
Question : Where did he or she study ?
Answer   : Lycée Charles et Adrien Dupuy in Clermont-Ferrand and Cardiff University
</EXAMPLES>

Topic    : {topic}
Data     : ```{data}```
Question : {question}
Answer   :"""

prompt_from_field = PromptTemplate(template=template_from_field, input_variables=["topic", "data", "question"])