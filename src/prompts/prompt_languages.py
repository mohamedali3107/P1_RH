template = """You will be provided with a Curriculum Vitae delimited by triple backsticks.
Your task is to find the languages spoken with the corresponding proficiency level by the person in this Curriculum Vitae and provide the comprehensive list of these. Once you obtained such a list, translate that list into English to give your final output. If you do not find the proficiency level, you should output 'Unkown' instead.
Your final output should be a list of tuples of strings, each string in English language and in title case, in the following format:

[(Language 1, Proficiency level 1), (Language 2, Proficiency level 2), (Language 3, Proficiency level 3)]

Here are some examples of final outputs:

<EXAMPLE 1>
[('French', 'Native'), ('English', 'Fluent'), ('Italian', 'Basic'), ('Chinese', 'Notions')]
</EXAMPLE 1>

<EXAMPLE 2>
[('English', 'Native'), ('French', 'Fluent')]
</EXAMPLE 2>

<EXAMPLE 3>
[('Spanish', 'Fluent'), ('Swedish', 'Unknown')]
</EXAMPLE 3>

Curriculum Vitae : ```{context}```
"""

