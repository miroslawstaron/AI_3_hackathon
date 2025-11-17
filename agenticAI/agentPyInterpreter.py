import agent
import subprocess
import re
import requests
import json
import os

class AgentInterpreter(agent.AgentAI):
    '''This class uses the LLM model together with a gcc compiler to compile
        and to fix potential compilation errors.'''

    def __init__(self, server_address, model_name, trials: int = 3, timeout_seconds: int = 10):
        self.server_address = server_address        # address of the server
        self.model_name = model_name                # name of the model 
        self.url = f'{self.server_address}/v1/chat/completions'    # chat API endpoint
        self.__response = ""                    # response from the model
        self.__mdCode = ""                      # markdown code block, which is part of the response
        self.__code = ""                        # just the code from the markdown code block   
        self.__interpret_result = ""              # result of the interpretation using python 
        self.__trials = trials                   # number of trials to fix the interpretation errors
        self.__timeout_seconds = timeout_seconds  # max seconds to wait for code execution

        # initial interpret messages queue
        self.__initial_interpret_messages = [
            {"role": "system",
             "content": "You are a Python Programmer. You solve problems with Python programs, no comments or explanations. "
            }
        ]

        # the conversation between the model and the user
        # that is aimed to solve compilation errors
        self.__interpret_messages = self.__initial_interpret_messages

    def get_response(self, code: str) -> str:
        '''This method compiles the code using gcc and tries to fix the compilation errors. 
        It returns the result of the compilation.'''

        # check if the code is in the markdown code block
        # if it is, we extract the code from the markdown code block
        # if it is not, we just use the code as it is
        if ("```python" in code.lower()) or ("```markdown" in code.lower()):
            self.__mdCode = code
            self.__code = self.__get_code(code)
        else:
            self.__code = code

        # compile the code using gcc
        self.__interpret_result = self.__interpret_code(code)

        # if the compilation was successful, we return the result
        if self.__interpret_result == "Interpretation successful" or self.__interpret_result == "Timeout":
            return self.__code, self.__interpret_result
        else:
            # if the compilation was not successful, we try to fix it
            attempts = 0
            while attempts < self.__trials and self.__interpret_result != "Interpretation successful":
                print(f'Attempt {attempts + 1} to fix the compilation error...')
                self.__solve_problem()
                attempts += 1
            return self.__code, self.__interpret_result

    def __solve_problem(self) -> str:
        '''This method solves the compilation problems using the model.
        It sends the prompt to the model and returns the response.'''

        # get the response from the model
        strPrompt = f'For this program {self.__code}, I got the following interpretation error: {self.__interpret_result}. Please fix the code and return the fixed code in a markdown code block.'
        
        # please note that we use the __interpret_messages list to store the conversation
        # between the model and the user
        self.__interpret_messages.append({"role": "user", "content": strPrompt})
        
        # get the response from the model
        strResult = self.__get_response_interpretation(strPrompt)
        return strResult

    def __get_response_interpretation(self, prompt: str) -> str:
        '''This method gets the response from the model. 
        It sends the prompt to the model and returns the response.'''
        
        data = {
            "model": self.model_name,
            "messages": self.__interpret_messages,
            "stream": False,
            "temperature": 0.0,
        }
        headers = {'Content-Type': 'application/json'}
        api_key = os.getenv('OPENAI_API_KEY', '')
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        # we use three retries just in case the server is busy
        # or there is a timeout
        retries = 3     


        for attempt in range(retries):
            try:
                # communicate with the server
                response = requests.post(self.url,
                                        headers=headers,
                                        json=data,
                                        timeout=300)

                if response.status_code == 200:
                    # get the response from the server
                    response_dict = json.loads(response.text)

                    # since the response contains a lot of other things, we need to extract the content
                    response_raw = response_dict['choices'][0]['message']['content']

                    return response_raw
                else:
                    # on error, we print the error message
                    print(f"Error: {response.status_code} - {response.text}")
                    return None
            except requests.exceptions.Timeout:
                print(f"Timeout occurred. Retrying {attempt + 1}/{retries}...")
                if attempt == retries - 1:
                    print("Max retries reached. Exiting.")
            return None

    def __extract_python_code(self, markdown: str) -> str:
        '''This function extracts the Python code from a markdown string.'''
        try:
            patterns = [r"```python(.*?)```", r"```markdown(.*?)```"]
            for pattern in patterns:
                match = re.search(pattern, markdown, re.DOTALL | re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        except:
            pass
        return ""
    
    def __get_code(self, code: str) -> str:
        '''This method gets the program code generated by the prompt. 
        The generation often results in a markdown code block. 
        This method extracts the code from the markdown block and returns it as a string.
        Line by line, with line breaks.'''
        
        # extract only the block that is between the ```python and ``` lines
        self.code = self.__extract_python_code(code)
        
        if code != "":
            # remove the first and the last line
            self.code = self.code.split('\n')
            #mdCode = mdCode[1:-1]
            self.code = '\n'.join(self.code)
        
        return self.code
    
    # interpret the code using python
    def __interpret_code(self, code: str) -> str:
        '''This method interprets the code using python.
        It returns the result of the interpretation.'''

        if self.__code != "":
            with open(f'./temp/code_temp.py', 'w+') as f:
                f.write(self.__code)
            # interpret the code using python
            try:
                result = subprocess.run(
                    ['python3', f'./temp/code_temp.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=self.__timeout_seconds
                )
            except subprocess.TimeoutExpired:
                self.__interpret_result = "Timeout"
                return self.__interpret_result

            # print the output of the interpretation
            # print(result.stdout.decode())
            # print(result.stderr.decode())

            # check if the output of the interpretation contains the word "error"
            if b'error' in result.stderr:
                self.__interpret_result = f"Interpretation error: {result.stderr.decode()}"
            else:
                self.__interpret_result = "Interpretation successful"
        else:
            self.__interpret_result = "No code found"   
        return self.__interpret_result