#!/bin/python3
import argparse
from tqdm import tqdm  # Import tqdm for progress bar
from agent import AgentAI

NUMBER_OF_ITERATIONS = 10

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the AgentAI with a prompt.")
    parser.add_argument("--prompt", type=str, required=True, help="The prompt to send to the agent.")
    args = parser.parse_args()

    # Create an instance of the Agent class
    agentDesigner = AgentAI(server_address="http://deeperthought.cse.chalmers.se", 
                              model_name="llama3.2:1b",
                              my_role="You are a C designer. You will be given a task and you will respond with design suggestions to solve or the task.")
    
    agentProgrammer = AgentAI(server_address="http://deepthought.cse.chalmers.se", 
                            model_name="llama3.2",
                            my_role="You are a C Programmer. You respond with the code in C to solve the task. No comments or explanations")
    
    # Get the response from the agent
    responseProgrammer = agentProgrammer.get_response(args.prompt)
    print("Programmer Response:", responseProgrammer)
    
    responseDesigner = agentDesigner.get_response(f'Here is my program, which solves this problem {args.prompt}. How can I improve it {responseProgrammer}')
    print("\n\nDesigner Response:", responseDesigner)

    for i in tqdm(range(NUMBER_OF_ITERATIONS), desc="Processing iterations"):
        responseProgrammer = agentProgrammer.get_response(responseDesigner)
        #print("\n\n:::::::::::::::::::Programmer Response::::::::::::::::::")
        #print(responseProgrammer[:100])
        
        responseDesigner = agentDesigner.get_response(responseProgrammer)
        #print("\n\n:::::::::::::::::::Designer Response::::::::::::::::::")
        #print(responseDesigner[:100])

        # once every 10 times save to excel
        if i % 5 == 0:
            agentProgrammer.save_to_excel("programmer_conversation_llama33gemma3.xlsx")

    
if __name__ == "__main__":
    main()
