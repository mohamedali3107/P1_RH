
from langchain.prompts import PromptTemplate

template_extract_fields = """* Situation : A recruiter is asking a question about a candidate
for a job.
* Your task : Based on the recruiter's question, identify what topic or topics this question is about
among a list of possible topics, in between triple backsticks. 
You should output only the identified topic or topics (comma separated), do not make a sentence.
If you don't know or are really not sure, your output should be 'unknown'

<EXAMPLE>
Mock possible topics : < age, first name, family name, skills, language 1, most recent diploma, language 2, hobbies >

Question of the recruiter : How old is he ?
Your output : age

Question of the recruiter : Does she know Python ?
Your output : skills

Question of the recruiter : Do they speak Spanish ?
Your output : language 1, language 2

Question of the recruiter : What does he or she like to do ?
Your output : hobbies

Question of the recruiter : What is her name ?
Your output : first name, family name

Question of the recruiter : What is the color of their shirt ?
Your output : unknown
</EXAMPLE>

Forget about the above possible topics. Following is the actual list of possible topics.

Possible topics : < ```{topics}``` >

Question of the recruiter : {question}
Your output : """

prompt_extract_fields = PromptTemplate(template=template_extract_fields, input_variables=["topics", "question"])