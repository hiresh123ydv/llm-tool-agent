# LLM Tool Agent (ReAct)

A simple ReAct-style AI agent built with Groq's LLM API. The agent can reason step by step, call tools, and use their results to answer questions — instead of just guessing an answer directly.

## What it does

Given a question like:

> "I have 5000 rupees. What is the price of an iPhone 17? and how much money will I have left?"

The agent will:
1. **Think** about what it needs to do next.
2. **Call a tool** (like searching the web for a price, or doing math).
3. **Wait for the real result** (never guesses or invents one).
4. Repeat until it has enough information.
5. Give a **Final Answer**.

## Tools available

- **`search_product_price(product)`** — searches the web (via DuckDuckGo) for a product's price in India and extracts it from the results.
- **`calculator(expression)`** — evaluates basic math expressions (+, -, *, /).

## Tech stack

- [Groq](https://groq.com/) — LLM inference (`llama-3.3-70b-versatile`)
- [ddgs](https://pypi.org/project/ddgs/) — free web search (no API key required)
- Python 3.12
- [uv](https://github.com/astral-sh/uv) — dependency management

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/hiresh123ydv/llm-tool-agent.git
   cd llm-tool-agent
   ```

2. Install dependencies with `uv`:
   ```bash
   uv sync
   ```

3. Create a `.env` file in the project root with your Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   ```
   Get a free key at [console.groq.com](https://console.groq.com/keys).

## Running

```bash
uv run Re_act.py
```

You'll see the agent's step-by-step reasoning printed to the console (Thought → Action → Observation), ending in a Final Answer.

## Example output

```
STEP 1
Thought: I need to find the price of iPhone 17
Action: search_product_price("iPhone 17")

Observation: Found: ₹79,900 (source: ...) | Extracted numeric price: 79900

STEP 2
Thought: Now I need to calculate the remaining money
Action: calculator("5000 - 79900")

Observation: -74900

Final Answer: The iPhone 17 costs ₹79,900. You don't have enough money — you'd be short by ₹74,900.
```

## Notes

- This is a learning project built as part of an AI agents course. The web search relies on free DuckDuckGo results, so price extraction isn't always 100% accurate — it depends on what shows up in the top search snippets.
- The `calculator` tool currently uses Python's `eval()` for simplicity. Fine for local/learning use, but not recommended for production without sandboxing.
