template = """You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find the languages spoken with the corresponding proficiency level by the person in this Curriculum Vitae and provide the comprehensive list of these. 
Your output should be a list of tuples, in the following format:

[(Language 1, Proficiency level 1), (Language 2, Proficiency level 2), (Language 3, Proficiency level 3)]

Here are some examples of outputs:

<EXAMPLE 1>
[(French, Native), (English, Fluent), (Italian, basic), (Chinese, notions)]
</EXAMPLE 1>

<EXAMPLE 2>
[(English, Native), (French, Fluent)]
</EXAMPLE 2>

Curriculum Vitae : ```{context}```
"""

