
import pandas as pd

template_path = "data_template_concise.csv"
template_df = pd.read_csv(template_path)
fields = list(template_df)

# # Prompt asking to fill directly a template
# prompt_global = """ The texts provided to you are the resumes of the candidates.
# Your task is to answer the user question in a structured way as in the following format.

# <Desired format>

# Please extract the first name in the resume
# First name:
# Please extract the last name in the resume
# Last name:
# Please extract the phone number in the resume
# Phone number:
# Please extract the email contact in the resume
# Email adress:
# Please extract the language skills mentioned in the resume
# Languages :
# Please extract the technical skills mentioned in the resume
# Technical skills:
# Please extract the last experience of the candidate
# Last experience:

# </Desired format>

# Take your time to read carrefuly the pieces in the context to answer the question.
# Do not provide answer out of the context pieces.
# If you don't know the answer, just say that you don't know, don't try to make up an answer.

# Keep the answer as concise as possible. 

# Always say "thanks for asking!" at the end of the answer.
# {context}
# """

# ## Prompt for retrieving the last position of the candidate
# prompt_last_position = """ You are an AI assistant who loves to help people!

# The texts provided to you are the resumes of the candidates.

# Your task is to provide the details about the most recent position of the candidate in the given context

# Your answer maybe the job title of the candidate, company/organization name, dates of employment

# Take your time to read carefully the pieces in the context to provide the request field.

# Do not provide answer out of the context pieces.

# If you don't know the answer, just say that you don't know, don't try to make up an answer.

# Always say "thanks for asking!" at the end of the answer.

# {context}

# Question: {query}

# Answer the question in the language of the question

# Helpful Answer:
# """

prompts_concise_v0 = [[""] +              # Avoiding the first field (=filename)
[f"""You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find and provide the {field} of the person in this CV.
Your output should be only the {field}, do not make a sentence.
Do not provide answer out of the context pieces. If you did not find it, you should output "Unknown".

Curriculum Vitae : ```{{context}}```
{field} of the person :
"""
for field in fields[1:] # Avoiding the first field (=filename)
]]

prompts_df_concise = pd.DataFrame(data=prompts_concise_v0, columns=fields)
prompts_df_concise.to_csv("prompt_templates_concise.csv", index=False)