
from langchain.prompts import PromptTemplate

template_identify_name = """
You will be provided with the name of a person, as typed by someone online.
The provided name might be ill-formatted, for instance it might miss capital initials or
accentuated letters or a dash, or it may have additional accents...
Your task is to identify the correct name among a list of possible names, and output it.
Your output should be only the name, do not make a sentence.
If you did not find it, you should output "Unknown".

<example 1>
Possible names : [ Martine Laurent, Philippe Poutou, Bruce Bayne, Léa Sandman ]
Provided name : lea Sandman
Identified name : Léa Sandman
</example 1>

<example 2>
Possible names : [ Leo Laurent, Philippe Poutou, Peter J. Cameron, Léa Sandman ]
Provided name : Léo laurent
Identified name : Leo Laurent
</example 2>

<example 3>
Possible names : [ Maria Laurent, Bruce Bayne, Peter J. Cameron, Léa Sandman ]
Provided name : maria m. laurent
Identified name : Maria Laurent
</example 3>

<example 4>
Possible names : [ Bruce Bayne, Peter J. Cameron, Léa Hackman ]
Provided name : peter cameron
Identified name : Peter J. Cameron
</example 4>

<example 5>
Possible names : [ Jean-Edouard Beauf, Bastien Allegre, Lily Potter ]
Provided name : jean edouard beauf
Identified name : Jean-Edouard Beauf
</example 5>

Possible names : [ {context} ]
Provided name : {name}
Identified name :"""

prompt_identify_name = PromptTemplate(template=template_identify_name, input_variables=["context", "name"])