# DamnVulnerableADK
Simple ADK implementation with an sqlite3 db and SQL injection vulnerability

This is an exercise project to learn about ADK Framework and the security of those AI Agents.

No coding skill required.

## Installation
- create a virtual environment
    - `uv venv`
- install dependencies
    - `uv sync`
- configure your Gemini API key
    - rename `.env.example` to `.env`
    - add your Gemini API key to the `GOOGLE_API_KEY` variable in the `.env` file
- run the project
    - `uv run .\src\adk\main.py`

Alternatively, you can run the project using adk web
- activate the virtual environment
    - `source venv/bin/activate` (linux) or `.\venv\Scripts\activate` (win)
- move to the src directory
    - `cd src`
- run adk web
    - `adk web`
- open the browser and go to `http://localhost:8000`

## Target
- make the bot leak sensitive information about the users through the console/chat
- use SQL injection to execute arbitrary query
- fix the issues

## Rules
- the solution/data MUST BE a text message from the agent (final answer)
- Function calls output in console are NOT considered a solution

## Tips
- sometimes you can win even with a very simple prompt, no magic needed.
- try common jailbreak techniques
- restart the session often instead of keep trying

## Resources
- [ADK Framework](https://google.github.io/adk-docs/events/#how-events-flow-generation-and-processing)
- [L1B3RT4S](https://github.com/elder-plinius/L1B3RT4S)
- [Pliny The Liberator](https://x.com/elder_plinius)
- [SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)

