#!/usr/bin/env python3
# use the agent.py file to run the agent
import argparse
import re
import pandas as pd
from tqdm import tqdm       # Import tqdm for progress bar
from agent import AgentAI   # Import the agentAI class, this is for the designer
from agentC import AgentAIC   # Import the AgentC class, this is for the programmer
from agentH import AgentH   # Import the AgentH class, this is for the human


## File name to save
strFileNameToSave = "results/conversation_hackathon.xlsx"

def extract_python_code(markdown: str) -> str:
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

def main():
    MAX_ITERATIONS = 3  # Set the maximum number of iterations

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the AgentAI with a prompt.")
    parser.add_argument("--prompt", type=str, required=True, help="The prompt to send to the agent.")
    args = parser.parse_args()

    # Create an instance of the Agent class
    agentDesigner = AgentAI(server_address="http://lazythought.cse.chalmers.se", 
                              model_name="llama3.2:3b",
                              my_role="You are a Python designer. You will be given a task and you will respond with design suggestions to solve or the task.")
    
    agentProgrammer = AgentAI(server_address="http://lazythought.cse.chalmers.se", 
                            model_name="llama3.2:3b",
                            my_role=(
                                "You are a Python programmer."
                                " Return ONLY Python code wrapped in a markdown code block."
                                " No comments or explanations."
                            ))
    # Conversation log: list of dicts with iteration, role, prompt and response
    conversation_log = []

    # Get the response from the programmer for the initial prompt
    responseProgrammer = agentProgrammer.get_response(args.prompt)
    # Log programmer initial response (iteration 0)
    conversation_log.append({
        'iteration': 0,
        'role': 'programmer',
        'prompt': args.prompt,
        'response': responseProgrammer
    })

    # Get the response from the designer based on the programmer's response
    prompt_to_designer = f'Here is my solution to this problem {args.prompt}, how can I improve it: {responseProgrammer}?'
    responseDesigner = agentDesigner.get_response(prompt_to_designer)
    # Log designer initial response (iteration 0)
    conversation_log.append({
        'iteration': 0,
        'role': 'designer',
        'prompt': prompt_to_designer,
        'response': responseDesigner
    })

    # now get the response from the human
    agentHuman = AgentH(server_address=None, 
                        model_name=None, 
                        my_role=None)
    
    prompt_to_human = f'Iteration {0}: Here is the latest suggestion from the programmer: {responseProgrammer}. Please provide your feedback or improvements.'
    
    responseHuman = agentHuman.get_response(prompt_to_human)

    # Log human response for this iteration
    conversation_log.append({
        'iteration': 0,
        'role': 'human',
        'prompt': prompt_to_human,
        'response': responseHuman
    })

    for i in tqdm(range(MAX_ITERATIONS), desc="Processing iterations"):
        iteration = i + 1

        # Prompt programmer with latest designer message
        prompt_to_programmer = f'For your program, the designer suggested: {responseDesigner}. \n The human provided feedback: {responseHuman}. Address these points in your next solution.'

        responseProgrammer = agentProgrammer.get_response(prompt_to_programmer)
        # Log programmer response for this iteration
        conversation_log.append({
            'iteration': iteration,
            'role': 'programmer',
            'prompt': prompt_to_programmer,
            'response': responseProgrammer
        })

        # Prompt designer with latest programmer response
        prompt_to_designer = f'Here is my solution, how can I improve it {responseProgrammer}?'

        responseDesigner = agentDesigner.get_response(prompt_to_designer)

        # Log designer response for this iteration
        conversation_log.append({
            'iteration': iteration,
            'role': 'designer',
            'prompt': prompt_to_designer,
            'response': responseDesigner
        })

        # Ask the human only every 5th iteration; otherwise reuse last feedback
        if iteration % 5 == 0:
            prompt_to_human = f'Iteration {iteration}: Here is the latest suggestion from the programmer: {responseProgrammer}. Please provide your feedback or improvements.'
            responseHuman = agentHuman.get_response(prompt_to_human)

            # Log human response for this iteration
            conversation_log.append({
                'iteration': iteration,
                'role': 'human',
                'prompt': prompt_to_human,
                'response': responseHuman
            })

        # Periodically save the agent's messages and the conversation log
        agentProgrammer.save_to_excel(strFileNameToSave)
        # also save the conversation log to an excel file
        try:
            pd.DataFrame(conversation_log).to_excel(strFileNameToSave.replace('.xlsx', '_log.xlsx'), index=False)
        except Exception:
            # ignore failures to save log while iterating
            pass
    
    # After loop finishes, save final conversation log
    try:
        pd.DataFrame(conversation_log).to_excel(strFileNameToSave.replace('.xlsx', '_log.xlsx'), index=False)
        print(f"Conversation log saved to {strFileNameToSave.replace('.xlsx', '_log.xlsx')}")
    except Exception as e:
        print(f"Failed to save conversation log: {e}")


if __name__ == "__main__":
    main()
