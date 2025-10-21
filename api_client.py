import os
import google.generativeai as genai


class GeminiAPIClient:  # Interacts with Gemini API
    def __init__(self):
        self.api_key = os.environ.get("GENAI_API_KEY")
        self.model_name = os.environ.get("MODEL_NAME")
        self.model = None
        if genai and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
            except Exception:
                self.model = None

    def is_configured(self) -> bool:
        return self.model is not None

    def generate_content(self, prompt: str) -> str:
        """Generate content using the configured Gemini model.

        Returns an error message string when model isn't configured or if the API call fails.
        """
        if not self.model:
            return (
                "API key not configured. Please set the GENAI_API_KEY environment variable "
                "and restart the app."
            )
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred:\n{e}"

    @staticmethod
    def build_persona_prompt(action: str, code: str) -> str:
        return f"""
        Persona: You are an expert senior software architect specializing in writing clean, efficient, and well-documented code following all standard best practices for the language provided.

        Task: Your task is to {action} for the following code snippet.

        Constraint: Return ONLY the updated, raw code block. Do not include explanations, greetings, or any markdown formatting for the code block.

        Code Snippet:
        {code}
        """

    @staticmethod
    def build_refinement_prompt(refinement_instruction: str, previous_code: str) -> str:
        return f"""
        Iterative Refinement: You are an expert code assistant. Refine the following code according to this new instruction: "{refinement_instruction}".

        Constraint: Return ONLY the updated, raw code block. Do not include explanations, greetings, or any markdown formatting for the code block.

        Previous Output:
        {previous_code}
        """
