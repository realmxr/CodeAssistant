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
