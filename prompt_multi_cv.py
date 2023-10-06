template = """You will be provided with chunks from several Curriculum Vitae of candidates in
    between triple backsticks.
    Your task is to help a recruiter get the information they need from the provided CVs,
    so you should answer the question at the end regarding the candidates.
    Look for the relevant pieces of information in the provided chunks of CVs, and then try to answer based on this relevant information.
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Provide a complete answer but keep it as concise as possible.
    Following is an example of what you are expected to do (do not consider these mock chunks as
    data for your actual final answer) :
    
<EXAMPLE>
** <mock chunks>: [ [from cv_Dupont.pdf] ]   Martin Dupont
37 Villa du château
92270 Bois-Colombes
France
06 84 17 31 18
m.dupont@hotmail.fr
Formation

[ [from cv_Dupont.pdf] ]   - MP*, Lycée Stanislas, Paris
Expériences profesionnelles
2019 +
Software & AI Engineer - ILLUIN Technology
- Paris, France 

[ [from CV-JDoe.pdf] ]   Jane Doe
Docteure en mathématiques appliquées
A propos
Expérience Docteure en mathématiques appliquées et ancienne élève de l’ENS Lyon.</mock chunks>

** <question of the recruiter>: What is the e-mail address of Martin Dupont ?
** <answer>: m.dupont@hotmail.fr
</EXAMPLE>

Forget about the chunks of CV's provided above.
The actual chunks of CV you should be exclusively considering for information are provided below, delimited by triple backsticks.

** <chunks of CV's>: ```{context}```

** <question of the recruiter>: {question}
** <answer>:"""