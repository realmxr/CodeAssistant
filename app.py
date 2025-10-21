import os
import threading
from tkinter import filedialog

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import customtkinter as ctk
from theme import Theme
from api_client import GeminiAPIClient
from sidebar import Sidebar
from history import RefinementHistoryPanel


class CodeAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Code Refactor & Documentation Assistant")
        self.geometry("1400x750")
        ctk.set_appearance_mode("dark")

        # --- Configure Grid Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # API client
        self.api_client = GeminiAPIClient()

        # Sidebar (pass callbacks)
        callbacks = {
            "import_file": self.import_file,
            "process_code": self.process_code,
            "preset_selected": self._on_preset_selected,
            "refine_last_output": self.refine_last_output,
            "export_output": self.export_output,
        }
        self.sidebar = Sidebar(self, callbacks)
        self.sidebar.grid(row=0, column=0, rowspan=1, sticky="nsew")

        # Main content and history panel
        self._create_main_content()

        self.history_panel = RefinementHistoryPanel(self)
        self.history_panel.grid(row=0, column=2, sticky="nsew", padx=(0, 10), pady=10)

    def _create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=Theme.BACKGROUND)
        self.main_frame.grid(row=0, column=1, rowspan=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Input Textbox
        self.input_textbox = ctk.CTkTextbox(self.main_frame, font=("Consolas", 12), border_width=2,
                                            fg_color=Theme.TEXT_INPUT_BG, text_color=Theme.TEXT)
        self.input_textbox.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Placeholder management
        self.input_placeholder = "# Paste or type your code here...\n# Or click 'Import File' to load a file"
        self.input_has_placeholder = True
        self.input_textbox.insert("1.0", self.input_placeholder)
        self.input_textbox.configure(text_color="#6c7a89")

        self.input_textbox.bind("<FocusIn>", self._on_input_focus_in)
        self.input_textbox.bind("<FocusOut>", self._on_input_focus_out)
        self.input_textbox.bind("<Key>", self._on_input_key_press)

        # Output Textbox
        self.output_textbox = ctk.CTkTextbox(self.main_frame, font=("Consolas", 12), border_width=2,
                                             fg_color=Theme.TEXT_INPUT_BG, text_color=Theme.TEXT)
        self.output_textbox.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.output_textbox.insert("1.0", "# AI-generated code will appear here...")

    def process_code(self, action: str):
        input_code = self.input_textbox.get("1.0", "end-1c")
        if not input_code.strip() or input_code.strip() == self.input_placeholder:
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.insert("1.0", "Error: Input code is empty.")
            return

        self.sidebar.set_buttons_state("disabled")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", "Processing...")
        self.update_idletasks()

        prompt = self.api_client.build_persona_prompt(action, input_code)
        thread = threading.Thread(target=self._api_worker, args=(prompt,), daemon=True)
        thread.start()

    def refine_last_output(self, refinement_instruction: str = None):
        # If called as a callback from Sidebar without args, read entry
        if refinement_instruction is None:
            refinement_instruction = self.sidebar.get_refinement_instruction()

        output_code = self.output_textbox.get("1.0", "end-1c")
        if not output_code.strip() or output_code.strip().startswith("# AI-generated code will appear here"):
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.insert("1.0", "Error: No existing output to refine.")
            return

        self.sidebar.set_buttons_state("disabled")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", "Processing refinement...")
        self.update_idletasks()

        prompt = self.api_client.build_refinement_prompt(refinement_instruction, output_code)
        thread = threading.Thread(target=self._api_worker, args=(prompt,), daemon=True)
        thread.start()

    def refine_last_output_from_entry(self):
        instruction = self.sidebar.get_refinement_instruction()
        self.refine_last_output(instruction)

    def import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read()
                self.input_textbox.delete("1.0", "end")
                self.input_textbox.insert("1.0", file_content)
                self.input_has_placeholder = False
                self.input_textbox.configure(text_color=Theme.TEXT)

    def export_output(self):
        output_code = self.output_textbox.get("1.0", "end-1c")
        if not output_code.strip() or output_code.strip().startswith("# AI-generated code will appear here"):
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.insert("1.0", "Error: No output to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                 filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(output_code)
                self.output_textbox.delete("1.0", "end")
                self.output_textbox.insert("1.0", f"Output saved to {os.path.basename(file_path)}")
                # Clear the message after 3 seconds using a named method
                self.after(3000, self._clear_output_message)
            except Exception as e:
                self.output_textbox.delete("1.0", "end")
                self.output_textbox.insert("1.0", f"Error saving file: {e}")

    def clear_history(self):
        # Delegate to history panel
        self.history_panel.clear_history()

    def _api_worker(self, prompt: str):
        if not self.api_client.is_configured():
            result_text = (
                "API key not configured. Please set the GENAI_API_KEY environment variable "
                "and restart the app."
            )
            self.after(0, self._on_result, result_text)
            return

        result_text = self.api_client.generate_content(prompt)
        self.after(0, self._on_result, result_text)

    def _on_result(self, text: str):
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", text)
        self.sidebar.set_buttons_state("normal")
        # Add to history panel
        self.history_panel.add_refinement(text)

    def _on_preset_selected(self, preset: str):
        if preset and preset != "Select preset...":
            self.sidebar.refinement_entry.delete(0, "end")
            self.sidebar.refinement_entry.insert(0, preset)

    def _set_buttons_state(self, state: str):
        self.sidebar.set_buttons_state(state)

    def _on_input_focus_in(self, event):
        if self.input_has_placeholder:
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.configure(text_color=Theme.TEXT)
            self.input_has_placeholder = False

    def _on_input_focus_out(self, event):
        if not self.input_textbox.get("1.0", "end-1c").strip():
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.insert("1.0", self.input_placeholder)
            self.input_textbox.configure(text_color="#6c7a89")
            self.input_has_placeholder = True

    def _on_input_key_press(self, event):
        if self.input_has_placeholder:
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.configure(text_color=Theme.TEXT)
            self.input_has_placeholder = False

    def _clear_output_message(self):
        """Clear transient messages in the output textbox."""
        try:
            self.output_textbox.delete("1.0", "end")
        except Exception:
            pass
