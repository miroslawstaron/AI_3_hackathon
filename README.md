# AI-Assisted Software Engineering 3.0 Hackathon
Modern software engineering uses generative AI when developing, testing, and even specifying software. We can use tools like Github Copilot or ChatGPT to get help in specific tasks, e.g., completing the body of a function and implementing a specific algorithm. However, there are a few show-stoppers before generative AI can be used in software development companies – one is the ability to use custom models trained on the code from the company. Another is the ability to develop tools that use multiple models to achieve more advanced tasks, e.g., specify software, develop code, test the code, fix defects, etc. 

This Hackathon’s goal is to develop a tool that uses multiple models to develop, test, and optimize software for a specific task. The figure below illustrates the architecture of this tool.

![architecture](architecture.png)

The coordinator prompts LLM1 to solve a task and then prompts LLM2 to test the program developed by LLM1. If there are errors, the coordinator prompts one of the LLMs to provide the solution. 

## Tests before the hackathon

In this hackathon we use two servers at Chalmers / Göteborgs Universitet that run LLaMA 3.2 models through the Ollama framework . We communicate with them using REST API. 

_Test 1:_ to check that you can connect to the server, please go to this address in your browser: deeperthought.cse.chalmers.se:80/api/tags. This should result in output like this:

![JSON output](json.png)

If it does not work, please check the proxy settings and let me know beforehand. 

_Test 2:_ To check that you can connect to these servers from a Python script, please run the following Python program: 

```
import requests
import json
url = 'http://deeperthought.cse.chalmers.se:80/api/generate'
data = {
    "model": "llama3.2",
    "prompt": "Write a program to calculate Fibonacci numbers in Python.",
    "stream": False
    }
headers = {'Content-Type': 'application/json'}
response = requests.post(url, data=json.dumps(data), headers=headers)

json_data = json.loads(response.text)
print(json_data['response'])
```

The output should be a Fibonacci program in Python; the response should come within less than 20 seconds. If the program does not respond, please change the last line to print(json_data) and check the results. 
