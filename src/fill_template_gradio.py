from dotenv import load_dotenv, find_dotenv
import pandas as pd
import gradio as gr
import fill_csv

demo_fill_template = gr.Interface(
    fn = lambda file: fill_csv.fill_one_row(fill_csv.template_path, file, force_refill=True, verbose=True),
    inputs =
    [
        gr.Dropdown(
            fill_csv.complete_paths, label="File", info="Select the file you want to analyze"
        )
    ],
    outputs=
    [
        gr.Textbox(label = field) for field in list(pd.read_csv(fill_csv.template_path))
    ],
    description = "Analyzes a file according to the given template"
)

demo_fill_template.launch(inbrowser=True)