# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========

import sys
import os
import pathlib
import gradio as gr
import time
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from examples.scientific_essay_generator import construct_scientific_essay_society
from owl.utils import run_society

# Load environment variables
base_dir = pathlib.Path(__file__).parent.parent
env_path = base_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

# Ensure the essays directory exists
essays_dir = base_dir / "essays"
essays_dir.mkdir(exist_ok=True)

def generate_essay(api_key, topic, pages, instructions, progress=None):
    """Generate a scientific essay using the OWL framework.
    
    Args:
        api_key (str): OpenAI API key to use
        topic (str): Topic for the scientific essay
        pages (int): Number of pages to generate
        instructions (str): Additional instructions for the essay
        progress (gr.Progress, optional): Progress component
        
    Returns:
        tuple: (essay content, output filename, token count)
    """
    # Set the API key in environment
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Progress stages
    if progress:
        progress(0.1, desc="Setting up agent society...")
    
    # Construct the society
    society = construct_scientific_essay_society(
        topic=topic,
        pages=pages,
        instructions=instructions
    )
    
    if progress:
        progress(0.2, desc="Researching and generating essay...")
    
    # Generate the essay
    answer, chat_history, token_count = run_society(society)
    
    if progress:
        progress(0.9, desc="Finalizing essay...")
    
    # Generate output filename
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_filename = f"scientific_essay_{safe_topic}_{timestamp}.md"
    full_path = essays_dir / output_filename
    
    # Save the essay
    with open(full_path, "w") as f:
        f.write(answer)
    
    if progress:
        progress(1.0, desc="Essay completed!")
    
    return answer, str(full_path), token_count

# Gradio interface
def create_interface():
    with gr.Blocks(title="Scientific Essay Generator", theme=gr.themes.Soft()) as interface:
        gr.Markdown(
            """
            # 🦉 OWL Scientific Essay Generator
            
            This application uses the OWL framework to generate comprehensive scientific essays on any topic.
            
            Enter your OpenAI API key, specify the topic, number of pages, and any additional instructions.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=3):
                api_key = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="sk-...",
                    type="password",
                    value=os.environ.get("OPENAI_API_KEY", "")
                )
            
            with gr.Column(scale=1):
                pages = gr.Slider(
                    label="Pages",
                    minimum=1,
                    maximum=20,
                    value=5,
                    step=1,
                    interactive=True
                )
                
        topic = gr.Textbox(
            label="Essay Topic",
            placeholder="e.g., Recent advances in quantum computing",
            lines=1
        )
        
        instructions = gr.Textbox(
            label="Additional Instructions",
            placeholder="e.g., Focus on practical applications, include diagrams, compare with classical computing",
            lines=3,
            value="Include at least 10 scientific references and add visual representations where appropriate."
        )
        
        with gr.Row():
            generate_button = gr.Button("Generate Essay", variant="primary")
            cancel_button = gr.Button("Cancel", variant="stop")
        
        status_text = gr.Markdown("Ready to generate essay")
        
        with gr.Tabs():
            with gr.TabItem("Essay Preview"):
                essay_output = gr.Markdown("Your essay will appear here")
            with gr.TabItem("Details"):
                file_path = gr.Textbox(label="Saved to", interactive=False)
                token_count = gr.Number(label="Tokens Used", interactive=False)
        
        def on_generate(api_key, topic, pages, instructions, progress=gr.Progress()):
            if not api_key:
                return "Please enter your OpenAI API key", "", 0
            if not topic:
                return "Please enter a topic for your essay", "", 0
            
            status_text.update("Generating essay...")
            
            try:
                essay, path, tokens = generate_essay(api_key, topic, pages, instructions, progress)
                status_text.update("Essay generation completed!")
                return essay, path, tokens
            except Exception as e:
                status_text.update(f"Error: {str(e)}")
                return f"Error: {str(e)}", "", 0
        
        generate_button.click(
            fn=on_generate,
            inputs=[api_key, topic, pages, instructions],
            outputs=[essay_output, file_path, token_count]
        )
        
        def on_cancel():
            status_text.update("Generation canceled")
            return "Generation canceled", "", 0
            
        cancel_button.click(
            fn=on_cancel,
            inputs=[],
            outputs=[essay_output, file_path, token_count]
        )
        
        gr.Markdown(
            """
            ## How It Works
            
            This tool uses OWL's multi-agent framework to:
            1. Research the topic using ArXiv, Google Scholar, and other sources
            2. Generate a well-structured academic essay
            3. Include appropriate citations and references
            4. Save the result as a Markdown file in the `essays` directory
            
            All essays are saved locally and can be accessed in the essays folder.
            """
        )
    
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()
    # Enable queue (required for progress tracking)
    interface.queue()
    interface.launch(share=False, inbrowser=True) 