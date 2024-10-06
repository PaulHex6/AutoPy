# AutoPy

`AutoPy` short for Auto Python, is a tool that leverages OpenAI's language model to generate, execute, and refine Python scripts based on user prompts. It securely runs the generated code inside a Docker container.

**Note:** AutoPy is currently in the initial development stage, and further refinements are coming soon.

## AutoPy Workflow

Below is the workflow logic for AutoPy:

1. **Input:** Receives a natural language prompt.

2. **Code Generation:** Uses GPT to generate Python code based on the input prompt.

3. **Execution and Refinement:**
   - In order to verify the code runs it (secure Docker environment).
   - Captures and processes errors, refining the code with GPT until corrected.
   - Verifies the output against expected results, repeating the process if necessary.

4. **Output:** Returns the final code and its output.


## Requirements
- Python 3.7+
- Docker installed and running
- API key from [aimlapi.com](https://aimlapi.com)
- Python packages: `openai`, `docker`, `python-dotenv`

## Installation
1. Install the required packages:
    ```bash
    pip install openai docker python-dotenv
    ```
2. Set up Docker from [docker.com](https://www.docker.com/).
3. Create a `.env` file with your OpenAI API key:
    ```env
    OPENAI_API_KEY=your_api_key_here
    ```
    This key will be used to access OpenAI services through [aimlapi.com](https://aimlapi.com).

## Usage
Run the script:
```bash
python AutoPy.py
