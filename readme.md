# AutoPy

`AutoPy` is a tool that uses OpenAI's language model to generate, execute, and refine Python scripts based on user prompts. It runs the generated code securely inside a Docker container.

## Features
- Generate Python code based on text prompts.
- Execute code in a Docker container for isolation.
- Automatically refine code based on errors.

## Requirements
- Python 3.7+
- Docker installed and running
- OpenAI API key
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

## Usage
Run the script:
```bash
python autopy.py
