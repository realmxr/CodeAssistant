"""
Entry point for CodeAssistant - minimal wrapper that loads .env and runs the app
"""

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from app import CodeAssistantApp


if __name__ == "__main__":
    app = CodeAssistantApp()
    app.mainloop()