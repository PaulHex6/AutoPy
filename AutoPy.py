import os
import logging
from dotenv import load_dotenv
import docker
from openai import OpenAI
import time
import re
from datetime import datetime
import platform

# Load environment variables
load_dotenv()

# Generate a unique log file name for each run
log_filename = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the default logging level to ERROR (other DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename

    # Use StreamHandler to output logs to console:
    #handlers=[logging.StreamHandler()]

    #Use NullHandler to discard all logging messages:
    #handlers=[logging.NullHandler()] 
)

# Set up the client for LLM interaction
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.aimlapi.com",
)

class AutoPy:
    def __init__(self, max_iterations=3, model='gpt-4o'):
        try:
            # Initialize Docker client based on the platform
            if platform.system() == "Windows":
                self.docker_client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
            else:
                self.docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        except docker.errors.DockerException as e:
            logging.error(f"Docker initialization error: {str(e)}")
            self.docker_client = None
        self.max_iterations = max_iterations
        self.model = model

    def code_generator(self, user_input):
        try:
            logging.info("Generating code from input...")
            # Use the OpenAI client to generate Python code based on user input
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": 
                            "You are a professional Python developer. Your output should be fully functional Python code, "
                            "provided without comments, introductions, summaries, or explanations – just plain Python code."
                            },
                    {"role": "user", "content": user_input},
                ],
            )
            logging.info(f"Raw API response: {response.choices[0].message.content}")
            
            # Extract the Python code block using regex
            code_match = re.search(r"```python(.*?)```", response.choices[0].message.content, re.DOTALL)
            if code_match:
                code = code_match.group(1).strip()
                logging.info(f"Extracted Code: {code}")
                return code
            else:
                logging.warning("No valid Python code block found in the response.")
                return None
        except Exception as e:
            logging.error(f"Error generating code: {str(e)}")
            return None

    def execute_code(self, code):
        if not self.docker_client:
            logging.error("Docker client is not initialized. Cannot execute code.")
            return None, "Docker client is not initialized. Cannot execute code."
        
        try:
            # Use inline command to run Python code inside Docker
            logging.info("Running code in Docker container...")
            try:
                output = self.docker_client.containers.run(
                    image="python:3.9",
                    command=["python", "-c", code],  # Execute the code inline
                    detach=False,
                    mem_limit="128m",
                    network_disabled=True,
                    stderr=True,
                    remove=True,
                )

                # Decode the output and return
                logs = output.decode('utf-8')
                logging.info(f"Container execution successful: {logs}")
                return logs, None

            except docker.errors.ContainerError as e:
                logging.error(f"Container error: {e.stderr.decode('utf-8')}")
                return None, "Container error during execution"
            except docker.errors.DockerException as e:
                logging.error(f"Docker error during container run: {str(e)}")
                return None, "Docker error during container run"
            except Exception as e:
                logging.error(f"Unexpected error during container execution: {str(e)}")
                return None, "Unexpected error during container execution"

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return None, "Unexpected error"

    def run_code_generation(self, description):
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            logging.info(f"Starting iteration {iteration} for code generation")

            # Generate code based on the description
            code = self.code_generator(description)
            if code is None:
                logging.warning("Failed to generate valid Python code from input.")
                break

            logging.info(f"Generated Code (Iteration {iteration}):\n{code}")

            # Execute the generated code
            output, error = self.execute_code(code)

            if error:
                # Stop refining if the error is Docker-related
                if "Docker" in error or "Container error" in error:
                    logging.error(f"Docker Error: {error}. Stopping further refinement.")
                    break

                logging.info(f"Error encountered: {error}. Refining the code...")
                description += f"\nPlease correct the following error:\n{error}"
            else:
                logging.info(f"Successful execution:\n{output}")
                return code, output

            time.sleep(1)

        logging.error("Exceeded maximum number of iterations. Unable to generate a working code.")
        return None, None

if __name__ == "__main__":
    task_description = input("Enter the task description (Press Enter for default): ")
    if not task_description:
        task_description = "Write a script that prints the Fibonacci series up to 100."

    # Initialize AutoPy
    autopy = AutoPy(max_iterations=5, model='gpt-4o-mini')

    # Generate and execute Python code
    final_code, result = autopy.run_code_generation(task_description)

    if final_code and result:
        logging.info("Final code generated and executed successfully.")
        print("===== Final Code: =====\n", final_code)
        print("===== Execution Result: =====\n", result)
    elif final_code and not result:
        logging.error("Code generated, but execution failed.")
        print("===== Final Code: =====\n", final_code)
        print("Error during code execution. Check the logs for more details.")
    else:
        logging.warning("Failed to generate a working script.")
        print("Failed to generate a working script.")
