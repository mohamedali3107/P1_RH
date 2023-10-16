
from langchain.prompts import PromptTemplate

template_file_name = """Your task is to detect if there is a full human name in a provided file name.
Be aware that a full name is at least two words long and do not contain the word "CV" or "cv".
For instance,
"John Smith" is a valid human name composed by the first name "John" and the family name "Smith",
but "John" is only one word so it can never be a full name.
For your answer, you should use the following output format :
[ True or False, "<full name of at least two words>" or None ]

Before answering, see if "CV" or "cv" is part of the name you guessed,
and if yes, just answer [ False, None ] instead.
For instance, if you guessed "Marie CV" as a name, you should actually answer [ False, None ] as "Marie CV" contains the word "CV".

Following are a few examples of what you are expected to do :
<EXAMPLES>
file name : allegre_drevon_CV.pdf
output : [ False, None ]

file name : CurriculumVitae-Dupont.pdf
output : [ False, None ]

file name : CV-tom.pdf
output : [ False, None ]

file name : julie_cv.pdf
output : [ False, None ]

file name : robin_cv_version4.pdf
output : [ False, None ]

file name : CV_Paul_V2.pdf
output : [ False, None ]

file name : anna_white_CV.pdf
output : [ True, "Anna White" ]

file name : cv-JessicaJones.pdf
output : [ True, "Jessica Jones" ]

file name : cv_hackman-marina.pdf
output : [ True, "Marina Hackman" ]

file name : CV_taylor-joy.pdf
output : [ False, None ]

file name : CV_michael_JACKSON.pdf
output : [ True, "Michael Jackson" ]
</EXAMPLES>

file name : {file}
output :
"""

#2. the first name (first word) looks like a common human first name
#3. the full name consists of at least two words.

prompt_file_name = PromptTemplate(template=template_file_name, input_variables=["file"])

template_name_in_text = """
You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the full name of the person in this CV.
Your output should be only the name, do not make a sentence.
If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{context}```
Name of the person :"""

prompt_name_in_text = PromptTemplate(template=template_name_in_text, input_variables=["context"])

template_name_in_query = """
You will be provided with a query about a person that will be delimited by triple backsticks.
Your task is to find and provide the full name of the person from this query.
Your output should be only the name, do not make a sentence.
If you did not find it, you should output "Unknown".

Query : ```{context}```
Name of the person :"""

prompt_name_in_query = PromptTemplate(template=template_name_in_query, input_variables=["context"])