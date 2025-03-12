# This file checks if the files generated by the models execute
# Author: Miroslaw Staron
# Date: February 14, 2025

# go through the file in ./rosetta_programs directory
# execute each file 
import os
import subprocess
import re
import pandas as pd
from tqdm import tqdm

def extract_python_code(text):
    '''Extract the python code from the text.
    The text is assumed to be in markdown format.
    The python code is assumed to be in a code block with the language specified as python.'''
    pattern = r'```python(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def execute_files():
    '''Go through the files in the rosetta_programs directory
    Execute each file and store the result in a csv file'''

    # list to store the results, which we need for converting to 
    # a pandas dataframe and then to a csv file
    list_results = []

    # go through the files in the rosetta_programs directory
    for file in tqdm(os.listdir('./rosetta_programs')):
        
        # since the phi3 model is not good at all, we remove these files
        if file.endswith('.py') and 'phi3' not in file: # and 'gemma' in file:
            
            # read the string from the file
            with open(os.path.join('./rosetta_programs', file), 'r') as f:
                text = f.read()
            
            # extract the python code
            python_code = extract_python_code(text)
            if python_code is None:
                continue
            else:
                # write the python code to a new file
                with open('temp.py', 'w') as f:
                    f.write(python_code)
            
            # here we execute the file and capture the output
            # which is OK, Error or timed out
            try:
                strResult = f'{file}'
                oneFileRes = [strResult]
                strR = ""
                result = subprocess.run(['python3', './temp.py'], 
                                        capture_output=True, 
                                        text=True, 
                                        check=True, 
                                        timeout=10)
                strR += "Error" if "Error" in result.stderr else "OK"
            except subprocess.CalledProcessError as e:
                strR = "Error"
            except subprocess.TimeoutExpired:
                strR = "timed out"
            
            # store the result of this execution in a list 
            oneFileRes.append(strR)
            
            # append the result of this file to the list of results
            list_results.append(oneFileRes)

            # convert the list of results to a pandas dataframe
            # and save to a csv file
            df = pd.DataFrame(list_results, columns=['File', 'Result'])
            df.to_csv('results.csv', index=False)
    return list_results

# main function that calls the execute_files function
# and saves the results to a csv file
if __name__ == '__main__':
    lstResults = execute_files()
    df = pd.DataFrame(lstResults, columns=['File', 'Result'])
    df.to_csv('results.csv', index=False)