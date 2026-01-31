from dotenv import load_dotenv
from openai import OpenAI
import json
import requests

load_dotenv()

client = OpenAI()


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

user_query = input("👉 ")
message_history.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type":"json_object"},
        messages=message_history)
    
    raw_result = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": raw_result})
    parsed_result = json.loads(raw_result)
    
    if parsed_result.get("step") == "START":
        print(f"🔆 : {parsed_result.get('content')}")
        continue
    if parsed_result.get("step") == "PLAN":
        print(f"🔆 : {parsed_result.get('content')}")
        continue
    if parsed_result.get("step") == "ACTION":
        tool_to_call = parsed_result.get("action")
        tool_input = parsed_result.get("action_input")
        tool_response=available_tool[tool_to_call](tool_input)
        message_history.append({"role": "developer", "content": json.dumps({
            "step":"OBSERVE","tool":tool_to_call,"input":tool_input, "tool_response":tool_response
        })})
        continue
    if parsed_result.get("step") == "OUTPUT":
        print(f"🔆 : {parsed_result.get('content')}")
        break
    
print("/n/n/n")