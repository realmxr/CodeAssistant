CodeAssistant
===============

Overview
--------
CodeAssistant is a small GUI application (built with CustomTkinter) that helps you iteratively refine and annotate source code using an LLM backend. The app supports:

- Sending code to the model with pre-built transformations (e.g. add comments).
- Iterative refinement: send last output back to the model with a new instruction.
- A UI text field to enter custom refinement instructions.
- Importing a code file directly into the input box.
- Background processing (threads) so the UI stays responsive.

Requirements
------------
- Python 3.8+ (3.13 was used during development)
- Git (optional, for cloning)
- A virtual environment is recommended
- The project's Python dependencies are in `requirements.txt`

Environment variables and secrets
---------------------------------
This project reads API keys from a `.env` file in the project root. For safety the repository includes a committed `.env.template` (no secrets) — copy that to `.env` and fill in real values.

Quick steps (Windows cmd.exe):

- Create your local `.env` from the template and edit it:

```cmd
copy .env.template .env
notepad .env
```
