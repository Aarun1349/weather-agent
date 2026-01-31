from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
from pydentic import BaseModel,Field
from typing import Optional
import os

load_dotenv()

client = OpenAI()


class MyOutputFormat(BaseModel):
    step :str = Field(..., description="The current step of the agent's reasoning process. Possible values are: START, PLAN, ACTION, OBSERVE, OUTPUT.")
    content:Optional[str] =Field(None, description="The content of the current step, if applicable.")
    tool:Optional[str] =Field(None, description="The name of the tool to be used, if the step is ACTION.")
    input:Optional[str] =Field(None, description="The input for the tool, if the step is ACTION.")

def run_commang(command: str):
   result = os.system(command)
   return result


def get_weather(location: str) -> str:
    url = f"http://wttr.in/{location.lower()}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f" The weather in {location} is {response.text}"
    else:
        return " Sorry, I couldn't fetch the weather information right now."

available_tool ={
    "get_weather": get_weather
}
    
SYSTEM_PROMPT = """

                """
                
message_history = [{"role": "system", "content": SYSTEM_PROMPT}]
while True:
    user_query = input("👉 ")
    message_history.append({"role": "user", "content": user_query})

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format=MyOutputFormat,
            messages=message_history)
        
        raw_result = response.choices[0].message.parsed
        message_history.append({"role": "assistant", "content": raw_result})
        parsed_result = response.choices[0].message.parsed
        print("parsed result",parsed_result)
        
        if parsed_result.step == "START":
            print(f"🔆 : {parsed_result.content}")
            continue
        if parsed_result.step == "PLAN":
            print(f"🔆 : {parsed_result.content}")
            continue
        if parsed_result.step == "ACTION":
            tool_to_call = parsed_result.tool
            tool_input = parsed_result.input
            tool_response=available_tool[tool_to_call](tool_input)
            message_history.append({"role": "developer", "content": json.dumps({
                "step":"OBSERVE","tool":tool_to_call,"input":tool_input, "tool_response":tool_response
            })})
            continue
        if parsed_result.step == "OUTPUT":
            print(f"🔆 : {parsed_result.content}")
            break
    
print("/n/n/n")