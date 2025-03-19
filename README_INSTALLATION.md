# OWL Framework Installation

This repository contains an installation of the [OWL (Optimized Workforce Learning) Framework](https://github.com/camel-ai/owl) - a cutting-edge framework for multi-agent collaboration built on top of the CAMEL-AI Framework.

## Setup Instructions

1. Create and activate a virtual environment:
   ```bash
   # Using uv (recommended)
   pip install uv
   uv venv .venv --python=3.10
   source .venv/bin/activate  # On macOS/Linux
   # OR .venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
   # Install with uv
   uv pip install -e .
   # OR using pip
   pip install -r requirements.txt --use-pep517
   ```

3. Set up environment variables:
   ```bash
   # Edit the .env file with your API keys
   # At minimum, you need an OpenAI API key:
   # OPENAI_API_KEY='your-key-here'
   ```

## Running Examples

To run the minimal example:

```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # On macOS/Linux
# OR .venv\Scripts\activate  # On Windows

# Run the minimal example
python examples/run_mini.py
```

## Available Toolkits

OWL includes various toolkits for different tasks:
- SearchToolkit: For web search across multiple engines
- BrowserToolkit: For browser automation
- CodeExecutionToolkit: To write and execute Python code
- And many more...

## License

This package includes code from the CAMEL-AI Framework and the OWL Framework, which are licensed under the Apache License 2.0. 