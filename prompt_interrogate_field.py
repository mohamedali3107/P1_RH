
from langchain.prompts import PromptTemplate

template_extract_field = """* Situation : A recruiter is asking a question about a candidate
for a job.
* Your task : Based on the recruiter's question, identify what topic this question is about
among a list of possible topics, in between triple backsticks. 
You should output only the identified topic, do not make a sentence.

<EXAMPLE>
Mock possible topics : < age, first name, name, skills, languages, most recent diploma, hobbies >

Question of the recruiter : How old is he ?
Your output : age

Question of the recruiter : Does she know Python ?
Your output : skills

Question of the recruiter : Do they speak Spanish ?
Your output : languages

Question of the recruiter : What does he or she like to do ?
Your output : hobbies

Question of the recruiter : What is her name ?
Your output : name
</EXAMPLE>

Forget about the above possible topics. Following is the actual list of possible topics.

Possible topics : < ```{topics}``` >

Question of the recruiter : {question}
Your output : """

prompt_extract_field = PromptTemplate(template=template_extract_field, input_variables=["topics", "question"])