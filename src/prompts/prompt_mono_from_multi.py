
from langchain.prompts import PromptTemplate

template_mono_from_multi = """* Situation : A recruiter is asking a question about a pool of candidates
for a job.
* Your task : Based on the recruiter's query that concerns the pool of
candidates, identify and extract the question that should be asked about each candidate
in order to get the piece of information needed.

<EXAMPLE>
Query of the recruiter : What are the candidates that have a master degree in computer science ?
Your output : Does he or she have a degree in computer science ?

Query of the recruiter : Tell me who knows Python ?
Your output : Does he or she know Python ?

Query of the recruiter : Give me the names of the candidates that have at least three years of experience
Your output : Does he or she have at least three years of experience ?

Query of the recruiter : What candidates studied in ENS or Polytechnique ?
Your output : Did he or she study in ENS or Polytechnique ?

Query of the recruiter : What are the skills of the candidates ?
Your output : What are her or his skills ?

Query of the recruiter : List the phone numbers the candidates
Your output : What is her or his phone number ?
</EXAMPLE>

Query of the recruiter : {question}
Your output : """

prompt_template = PromptTemplate(template=template_mono_from_multi, input_variables=["question"])