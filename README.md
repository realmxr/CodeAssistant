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


Where to get official binaries
-----------------------------
When you publish release artifacts on GitHub, add them to the Releases page for the repository. Example URL pattern (replace <your-username> and repo name):

https://github.com/<your-username>/CodeAssistant/releases

Add a release and upload the Windows `.exe` and any other platform artifacts. Include SHA256 checksums and short usage instructions in the release notes.

Environment variables and secrets
---------------------------------
This project reads API keys from a `.env` file in the project root. For safety the repository includes a committed `.env.template` (no secrets) — copy that to `.env` and fill in real values.

Quick steps (Windows cmd.exe):

- Create your local `.env` from the template and edit it:

```cmd
copy .env.template .env
notepad .env
```

- Make sure `.env` is ignored by git (the repository's `.gitignore` already contains `.env`). If you accidentally committed `.env` and need to remove it from the repo history, untrack it (this removes it from the index but keeps your local file):

```cmd
git rm --cached .env
git commit -m "Remove .env from repository (should be ignored)"
git push
```

- If you already pushed a secret to a remote, rotate the exposed key immediately (create a new key and revoke the compromised one). To remove the secret from repository history you will need to rewrite Git history (tools such as the BFG Repo-Cleaner or `git filter-repo` can help). Rewriting history is disruptive to collaborators — consult Git docs before proceeding.

Keep `.env` local and do not commit it. Use `.env.template` in the repo to show what environment variables are required.
