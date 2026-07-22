import os
import re
from time import sleep
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client = Groq(api_key=my_api_key)
model = "llama-3.3-70b-versatile"


# ---------- TOOL 1: Old hardcoded price lookup (kept as fallback/example) ----------
def get_product_price(product):
    if product == 'iPhone 17':
        return 1000
    elif product == "iPhone 15":
        return 500
    else:
        return 0


# ---------- TOOL 2: Web search based price lookup ----------
def search_product_price(product):
    """Searches the web and tries to extract a price."""
    query = f"{product} price in India"
    try:
        results = DDGS().text(query, max_results=5)
    except Exception as e:
        return f"search error: {e}"

    price_pattern = r"₹\s?[\d,]+|Rs\.?\s?[\d,]+|INR\s?[\d,]+"
    for r in results:
        text = r.get("body", "") + " " + r.get("title", "")
        match = re.search(price_pattern, text)
        if match:
            return f"Found: {match.group()} (source: {r.get('href')})"
    return "No clear price found in search results."


# ---------- Helper: extract clean number from messy price text ----------
def clean_price(text):
    match = re.search(r"[\d,]+", text.replace("₹", "").replace("Rs.", ""))
    if match:
        return match.group().replace(",", "")
    return None


# ---------- TOOL 3:  calculator  ----------
def calculator(expression):
    try:
        return eval(expression)
    except:
        return "calc error!"


tools = {
    "get_product_price": get_product_price,
    "search_product_price": search_product_price,
    "calculator": calculator
}

system_prompt = """
You are a shopping assistant.
You have these tools:
search_product_price(product)   -> searches the web for current price
calculator(expression)           -> does math (only +, -, *, /)

IMPORTANT:
Call tools exactly like these examples:
Action: search_product_price("iPhone 17")
Action: calculator("5000 - 1000")

Never write:
search_product_price(product="iPhone 17")
Never write:
calculator(expression="5000 - 1000")

Follow these rules:
1. Decide what you need to do next.
2. Call ONLY ONE tool at a time.
3. After writing an Action, STOP immediately.
4. Never guess or invent a tool result.
5. Wait until you receive an Observation.
6. If the Observation contains "Extracted numeric price: X", use X (the plain
   number) in calculator, not the raw currency text.
7. When the task is complete, give the Final Answer.

Format:
Thought: what you need to do
Action: tool_name(argument)
When finished:
Final Answer: your answer
"""


def run_agent(question):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    for step in range(5):
        print("\n------------------")
        print("STEP", step + 1)
        print("------------------")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        answer = response.choices[0].message.content
        print(answer)

        # Agent has finished
        if "Final Answer:" in answer:
            break

        # Find the Action
        match = re.search(r"Action:\s*(\w+)\((.*?)\)", answer)
        if match:
            tool_name = match.group(1)
            tool_input = match.group(2).strip().strip('"')

            # Run the tool
            if tool_name in tools:
                observation = tools[tool_name](tool_input)
            else:
                observation = "Tool not found"

            # If we just did a price search, extract the clean number too
            if tool_name == "search_product_price":
                price_num = clean_price(str(observation))
                if price_num:
                    observation = f"{observation} | Extracted numeric price: {price_num}"

            print("Observation:", observation)

            # Add LLM response to memory
            messages.append({"role": "assistant", "content": answer})

            # Give tool result back to LLM
            messages.append({
                "role": "user",
                "content": "Observation: " + str(observation)
            })

            sleep(5)


prompt = """
I have 5000 rupees. What is the price of an average fighter plane?
and how much money will I have left?
"""

run_agent(prompt)

