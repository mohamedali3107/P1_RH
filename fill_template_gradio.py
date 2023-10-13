from dotenv import load_dotenv, find_dotenv
import pandas as pd
import gradio as gr
import fill_template

demo = gr.Interface(
    fn = lambda file: fill_template.fill_one_row(fill_template.template_path, file, verbose=True),
    inputs =
    [
        gr.Dropdown(
            fill_template.complete_paths, label="File", info="Select the file you want to analyze"
        )
    ],
    outputs=
    [
        gr.Textbox(label = field) for field in list(pd.read_csv(fill_template.template_path))
    ],
    description = "Analyzes a file according to the given template"
)

demo.launch(inbrowser=True)