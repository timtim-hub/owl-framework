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

import argparse
import pathlib
from dotenv import load_dotenv

from camel.models import ModelFactory
from camel.toolkits import (
    SearchToolkit,
    ArxivToolkit,
    GoogleScholarToolkit,
    SemanticScholarToolkit,
    CodeExecutionToolkit,
    FileWriteToolkit,
)
from camel.types import ModelPlatformType, ModelType
from camel.logger import set_log_level

from owl.utils import run_society
from camel.societies import RolePlaying

# Load environment variables
base_dir = pathlib.Path(__file__).parent.parent
env_path = base_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

# Set logging level for debugging
set_log_level(level="INFO")


def construct_scientific_essay_society(topic, pages, instructions):
    """Construct a society of agents for generating scientific essays.
    
    Args:
        topic (str): The scientific topic for the essay
        pages (int): Approximate number of pages for the essay
        instructions (str): Additional instructions for essay generation
        
    Returns:
        RolePlaying: A configured society of agents ready to generate the essay
    """
    
    # Calculate approximate word count based on pages (500 words per page is a common estimate)
    word_count = pages * 500
    
    # Create models for different components
    models = {
        "user": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict={"temperature": 0.1},
        ),
        "assistant": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict={"temperature": 0.1},
        ),
        "researcher": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict={"temperature": 0.1},
        ),
    }

    # Configure specialized research toolkits for scientific content
    tools = [
        # Academic research tools
        *ArxivToolkit().get_tools(),
        *SemanticScholarToolkit().get_tools(),
        *GoogleScholarToolkit().get_tools(),
        
        # General search capabilities
        SearchToolkit().search_duckduckgo,
        SearchToolkit().search_wiki,
        
        # For creating visualizations or analyzing data
        *CodeExecutionToolkit(sandbox="subprocess").get_tools(),
        
        # For saving the generated essay
        *FileWriteToolkit(output_dir="./essays/").get_tools(),
    ]

    # Configure agent roles and parameters
    user_agent_kwargs = {"model": models["user"]}
    assistant_agent_kwargs = {
        "model": models["assistant"], 
        "tools": tools,
    }

    # Construct the task prompt with all parameters
    task_prompt = (
        f"I need a comprehensive scientific essay on the topic: '{topic}'. "
        f"The essay should be approximately {word_count} words (about {pages} pages). "
        f"Additional requirements: {instructions}. "
        f"The essay should follow proper academic structure with an abstract, introduction, "
        f"methodology/literature review, discussion, conclusion, and references. "
        f"Use recent scientific research and cite sources properly in a standard academic format. "
        f"When complete, save the essay as a Markdown file."
    )

    # Create and return the society
    society = RolePlaying(
        task_prompt=task_prompt,
        with_task_specify=True,  # This enables more detailed task planning
        user_role_name="scientific advisor",
        user_agent_kwargs=user_agent_kwargs,
        assistant_role_name="research assistant",
        assistant_agent_kwargs=assistant_agent_kwargs,
    )

    return society


def main():
    """Main function to run the scientific essay generator."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate scientific essays with OWL")
    parser.add_argument("--topic", type=str, required=True, help="Scientific topic for the essay")
    parser.add_argument("--pages", type=int, default=5, help="Approximate number of pages (default: 5)")
    parser.add_argument(
        "--instructions", 
        type=str, 
        default="Include at least 10 scientific references and add visual representations where appropriate.",
        help="Additional instructions for the essay"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default=None, 
        help="Output filename (default: auto-generated based on topic)"
    )
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    pathlib.Path("./essays").mkdir(exist_ok=True)
    
    # Construct and run the society
    society = construct_scientific_essay_society(
        topic=args.topic,
        pages=args.pages,
        instructions=args.instructions
    )
    
    print(f"Generating a {args.pages}-page scientific essay on: {args.topic}")
    print(f"With instructions: {args.instructions}")
    print("\nThis may take some time depending on the length and complexity...\n")
    
    answer, chat_history, token_count = run_society(society)
    
    # Generate output filename if not provided
    if args.output is None:
        # Create safe filename from topic
        safe_topic = "".join(c if c.isalnum() else "_" for c in args.topic)
        output_filename = f"./essays/scientific_essay_{safe_topic}.md"
    else:
        output_filename = f"./essays/{args.output}"
        if not output_filename.endswith(".md"):
            output_filename += ".md"
    
    # Save the essay to a file
    with open(output_filename, "w") as f:
        f.write(answer)
    
    print(f"\n\033[92mEssay successfully generated and saved to: {output_filename}\033[0m")
    print(f"Total tokens used: {token_count}")
    

if __name__ == "__main__":
    main() 