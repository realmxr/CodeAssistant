import os
import threading
#import tkinter as tk
from tkinter import filedialog
#from datetime import datetime
# Optional .env support: if python-dotenv is installed, load environment variables from a .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv not installed or failed to load; environment variables will still be read from the OS
    pass
import customtkinter as ctk
import google.generativeai as genai
from theme import Theme  # Import the custom theme colors


class CodeAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Code Refactor & Documentation Assistant")
        self.geometry("1400x750")
        ctk.set_appearance_mode("dark")

        # --- Configure Grid Layout ---
        # 3-column grid: sidebar (col 0), main content (col 1), history panel (col 2)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar Frame ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=Theme.FRAME_BG)
        self.sidebar_frame.grid(row=0, column=0, rowspan=1, sticky="nsew")
        # Reserve row 9 as the expanding spacer so rows 0-8 hold the UI elements
        self.sidebar_frame.grid_rowconfigure(9, weight=1)  # Push widgets to the top

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Actions", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- Import File Button ---
        self.import_file_button = ctk.CTkButton(self.sidebar_frame, text="Import File",
                                                 command=self.import_file,
                                                 fg_color=Theme.YELLOW, hover_color=Theme.YELLOW_HOVER)
        self.import_file_button.grid(row=1, column=0, padx=20, pady=10)

        # --- Sidebar Buttons ---
        self.add_comments_button = ctk.CTkButton(self.sidebar_frame, text="Add Comments",
                                                 command=lambda: self.process_code("add detailed comments"),
                                                 fg_color=Theme.BLUE, hover_color=Theme.BLUE_HOVER)
        self.add_comments_button.grid(row=2, column=0, padx=20, pady=10)

        self.refactor_button = ctk.CTkButton(self.sidebar_frame, text="Refactor Code",
                                             command=lambda: self.process_code(
                                                 "refactor this code for readability and efficiency"),
                                             fg_color=Theme.GREEN, hover_color=Theme.GREEN_HOVER)
        self.refactor_button.grid(row=3, column=0, padx=20, pady=10)

        self.generate_docs_button = ctk.CTkButton(self.sidebar_frame, text="Generate Docs",
                                                  command=lambda: self.process_code(
                                                      "generate professional-level documentation"),
                                                  fg_color=Theme.YELLOW, hover_color=Theme.YELLOW_HOVER)
        self.generate_docs_button.grid(row=4, column=0, padx=20, pady=10)

        # --- Refinement Section Label ---
        self.refine_label = ctk.CTkLabel(self.sidebar_frame, text="Iterative Refinement",
                                         font=ctk.CTkFont(size=14, weight="bold"))
        self.refine_label.grid(row=5, column=0, padx=20, pady=(20, 5))

        # --- Preset Refinement Instructions Dropdown ---
        preset_instructions = [
            "Make the comments more concise",
            "Add detailed docstrings",
            "Add type hints to all functions",
            "Improve variable naming",
            "Add error handling",
            "Optimize for performance",
            "Simplify complex logic",
            "Add logging statements"
        ]
        self.refinement_dropdown = ctk.CTkComboBox(
            self.sidebar_frame,
            values=preset_instructions,
            command=self._on_preset_selected,
            fg_color=Theme.TEXT_INPUT_BG,
            button_color=Theme.BLUE,
            button_hover_color=Theme.BLUE_HOVER,
            dropdown_fg_color=Theme.FRAME_BG
        )
        self.refinement_dropdown.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        self.refinement_dropdown.set("Select preset...")

        # --- Custom Refinement Instruction Entry ---
        self.refinement_entry = ctk.CTkEntry(self.sidebar_frame,
                                            placeholder_text="e.g., Make comments concise",
                                            fg_color=Theme.TEXT_INPUT_BG,
                                            text_color=Theme.TEXT)
        self.refinement_entry.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        # Set default instruction
        self.refinement_entry.insert(0, "Make the comments more concise")

        # --- Refine Button (Iterative Refinement demo) ---
        self.refine_button = ctk.CTkButton(self.sidebar_frame, text="Refine Last Output",
                                           command=self.refine_last_output_from_entry,
                                           fg_color=Theme.BLUE, hover_color=Theme.BLUE_HOVER)
        self.refine_button.grid(row=8, column=0, padx=20, pady=10)

        # --- Export Button ---
        self.export_button = ctk.CTkButton(self.sidebar_frame, text="Export Output",
                                          command=self.export_output,
                                          fg_color=Theme.GREEN, hover_color=Theme.GREEN_HOVER)
        self.export_button.grid(row=9, column=0, padx=20, pady=10)

        # Update spacer row
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # --- Main Content Area (Text Boxes) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=Theme.BACKGROUND)
        self.main_frame.grid(row=0, column=1, rowspan=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Input Textbox
        self.input_textbox = ctk.CTkTextbox(self.main_frame, font=("Consolas", 12), border_width=2,
                                            fg_color=Theme.TEXT_INPUT_BG, text_color=Theme.TEXT)
        self.input_textbox.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Placeholder text management for input textbox
        self.input_placeholder = "# Paste or type your code here...\n# Or click 'Import File' to load a Python file"
        self.input_has_placeholder = True
        self.input_textbox.insert("1.0", self.input_placeholder)
        # Make placeholder text gray by configuring text color on the widget
        self.input_textbox.configure(text_color="#6c7a89")  # Gray color for placeholder

        # Bind events for placeholder behavior
        self.input_textbox.bind("<FocusIn>", self._on_input_focus_in)
        self.input_textbox.bind("<FocusOut>", self._on_input_focus_out)
        # Also bind to any key press to clear placeholder
        self.input_textbox.bind("<Key>", self._on_input_key_press)

        # Output Textbox
        self.output_textbox = ctk.CTkTextbox(self.main_frame, font=("Consolas", 12), border_width=2,
                                             fg_color=Theme.TEXT_INPUT_BG, text_color=Theme.TEXT)
        self.output_textbox.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        # Use the valid Tk text index '1.0' for the start of the widget
        self.output_textbox.insert("1.0", "# AI-generated code will appear here...")

        # --- Refinement History Panel ---
        self.history_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=Theme.FRAME_BG)
        self.history_frame.grid(row=0, column=2, sticky="nsew", padx=(0, 10), pady=10)
        self.history_frame.grid_rowconfigure(1, weight=1)
        self.history_frame.grid_columnconfigure(0, weight=1)

        self.history_label = ctk.CTkLabel(self.history_frame, text="Refinement History",
                                         font=ctk.CTkFont(size=16, weight="bold"))
        self.history_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Scrollable frame container for history step windows
        self.history_scroll_frame = ctk.CTkScrollableFrame(self.history_frame,
                                                           fg_color=Theme.BACKGROUND,
                                                           scrollbar_button_color=Theme.BLUE,
                                                           scrollbar_button_hover_color=Theme.BLUE_HOVER)
        self.history_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.history_scroll_frame.grid_columnconfigure(0, weight=1)

        # Placeholder label when no history exists
        self.history_placeholder = ctk.CTkLabel(self.history_scroll_frame,
                                               text="No refinements yet.\n\nClick 'Refine Last Output'\nto begin iterative refinement.",
                                               font=("Consolas", 10),
                                               text_color="#6c7a89")
        self.history_placeholder.grid(row=0, column=0, pady=20)

        # Clear history button
        self.clear_history_button = ctk.CTkButton(self.history_frame, text="Clear History",
                                                  command=self.clear_history,
                                                  fg_color=Theme.YELLOW, hover_color=Theme.YELLOW_HOVER,
                                                  height=28)
        self.clear_history_button.grid(row=2, column=0, padx=10, pady=(0, 10))

        # Initialize refinement history tracking
        self.refinement_history = []
        self.refinement_count = 0
        self.history_step_frames = []  # Track individual step frames for cleanup

        # --- Gemini API Configuration ---
        # Read API key from environment variable GENAI_API_KEY
        # To set on Windows (cmd.exe): setx GENAI_API_KEY "your_key_here"
        self.api_key = os.environ.get("GENAI_API_KEY")
        # Allow model override via MODEL_NAME env var, fallback to gemini-1.5-flash
        model_name = os.environ.get("MODEL_NAME", "gemini-1.5-flash")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            try:
                self.model = genai.GenerativeModel(model_name)
            except Exception:
                # If model creation fails, leave model as None; runtime will show an error
                self.model = None
        else:
            # Leave model as None; we'll display a helpful message when attempting to use it
            self.model = None

    def process_code(self, action: str):
        """Collect input and spawn a background thread to call the API.

        This keeps the GUI responsive and disables action buttons while a request is running.
        """
        # Use a valid end index. 'end-1c' returns the text without the trailing newline
        input_code = self.input_textbox.get("1.0", "end-1c")
        if not input_code.strip() or input_code.strip() == "# Paste your code here...":
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.insert("1.0", "Error: Input code is empty.")
            return

        # Disable buttons to prevent concurrent requests
        self._set_buttons_state("disabled")

        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", "Processing...")
        self.update_idletasks()  # Force UI update

        # Prepare prompt (kept identical semantics to previous implementation)
        prompt = f"""
        **Persona:** You are an expert senior software architect specializing in writing clean,
        efficient, and well-documented Python code following all standard best practices (PEP 8).

        **Task:** Your task is to {action} for the following code snippet.

        **Constraint:** Return ONLY the updated, raw code block. Do not include explanations,
        greetings, or the markdown formatting for the code block (```python).

        **Code Snippet:**
        {input_code}
        """

        # Run the API call on a background thread
        thread = threading.Thread(target=self._api_worker, args=(prompt,), daemon=True)
        thread.start()

    def refine_last_output(self, refinement_instruction: str):
        """Take the current text from the output textbox and send it back to the model
        with an iterative refinement instruction (runs on the same background worker).
        """
        output_code = self.output_textbox.get("1.0", "end-1c")
        if not output_code.strip() or output_code.strip().startswith("# AI-generated code will appear here"):
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.insert("1.0", "Error: No existing output to refine.")
            return

        # Disable buttons while refining
        self._set_buttons_state("disabled")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", "Processing refinement...")
        self.update_idletasks()

        # Build a refinement prompt using the same persona and constraints
        prompt = f"""
        **Persona:** You are an expert senior software architect specializing in writing clean,
        efficient, and well-documented Python code following all standard best practices (PEP 8).

        **Task:** Refine the following code according to this instruction: {refinement_instruction}

        **Constraint:** Return ONLY the updated, raw code block. Do not include explanations,
        greetings, or the markdown formatting for the code block (```python).

        **Code Snippet:**
        {output_code}
        """

        # Start the background worker to perform the refinement
        thread = threading.Thread(target=self._api_worker, args=(prompt,), daemon=True)
        thread.start()

    def refine_last_output_from_entry(self):
        """Refine the last output using the custom instruction from the entry field."""
        refinement_instruction = self.refinement_entry.get().strip()
        if not refinement_instruction:
            # If the entry is empty, fallback to a default instruction
            refinement_instruction = "Make the comments more concise"
            self.refinement_entry.delete(0, "end")  # Clear the entry
            self.refinement_entry.insert(0, refinement_instruction)  # Re-insert default text

        self.refine_last_output(refinement_instruction)

    def import_file(self):
        """Open a file dialog to import a Python file and load its content into the input textbox."""
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read()
                # Clear the existing content and insert the file content
                self.input_textbox.delete("1.0", "end")
                self.input_textbox.insert("1.0", file_content)
                # Mark that we no longer have placeholder text and restore normal color
                self.input_has_placeholder = False
                self.input_textbox.configure(text_color=Theme.TEXT)

    def export_output(self):
        """Save the content of the output textbox to a file."""
        output_code = self.output_textbox.get("1.0", "end-1c")
        if not output_code.strip() or output_code.strip().startswith("# AI-generated code will appear here"):
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.insert("1.0", "Error: No output to export.")
            return

        # Ask for file save location
        file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                   filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(output_code)
                # Show success message briefly
                self.output_textbox.delete("1.0", "end")
                self.output_textbox.insert("1.0", f"Output saved to {os.path.basename(file_path)}")
                self.after(3000, lambda: self.output_textbox.delete("1.0", "end"))  # Clear after 3 seconds
            except Exception as e:
                self.output_textbox.delete("1.0", "end")
                self.output_textbox.insert("1.0", f"Error saving file: {e}")

    def clear_history(self):
        """Clear the refinement history."""
        self.refinement_history.clear()
        self.refinement_count = 0
        for frame in self.history_step_frames:
            frame.destroy()  # Clean up each step frame
        self.history_step_frames.clear()  # Clear the tracking list

        # Re-insert the placeholder label
        self.history_placeholder = ctk.CTkLabel(self.history_scroll_frame,
                                               text="No refinements yet.\n\nClick 'Refine Last Output'\nto begin iterative refinement.",
                                               font=("Consolas", 10),
                                               text_color="#6c7a89")
        self.history_placeholder.grid(row=0, column=0, pady=20)

    def _api_worker(self, prompt: str):
        """Worker that runs in a background thread and performs the API call.

        Results are marshaled back to the GUI thread using `self.after`.
        """
        if not self.model:
            result_text = (
                "API key not configured. Please set the GENAI_API_KEY environment variable "
                "and restart the app."
            )
            # Schedule UI update on main thread
            self.after(0, self._on_result, result_text)
            return

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
        except Exception as e:
            result_text = f"An error occurred:\n{e}"

        # Schedule UI update on main thread (pass result_text as an arg)
        self.after(0, self._on_result, result_text)

    def _on_result(self, text: str):
        """Update UI with result text and re-enable buttons (called on main thread)."""
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", text)
        self._set_buttons_state("normal")

        # Add to refinement history
        self.refinement_history.append(text)
        self.refinement_count += 1
        # Update history display
        self._update_history_display()

    def _update_history_display(self):
        """Update the history textbox with the current refinement history."""
        # Clear existing step frames
        for frame in self.history_step_frames:
            frame.destroy()
        self.history_step_frames.clear()

        if not self.refinement_history:
            # Re-insert the placeholder label if no history
            self.history_placeholder = ctk.CTkLabel(self.history_scroll_frame,
                                                   text="No refinements yet.\n\nClick 'Refine Last Output'\nto begin iterative refinement.",
                                                   font=("Consolas", 10),
                                                   text_color="#6c7a89")
            self.history_placeholder.grid(row=0, column=0, pady=20)
            return

        # Insert each refinement step as a new frame with step number
        for i, step in enumerate(self.refinement_history, start=1):
            step_frame = ctk.CTkFrame(self.history_scroll_frame, fg_color=Theme.STEP_BG)
            step_frame.grid(row=i-1, column=0, sticky="ew", padx=5, pady=5)
            self.history_step_frames.append(step_frame)  # Track the frame for cleanup

            step_label = ctk.CTkLabel(step_frame, text=f"Refinement {i}:", font=("Consolas", 12, "bold"),
                                      text_color=Theme.TEXT)
            step_label.pack(anchor="nw", padx=10, pady=(10, 0))

            step_content = ctk.CTkTextbox(step_frame, font=("Consolas", 10),
                                           fg_color=Theme.TEXT_INPUT_BG, text_color=Theme.TEXT,
                                           wrap="word", border_width=2)
            step_content.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            step_content.insert("1.0", step)

        # Auto-scroll to the end
        self.history_scroll_frame.yview("end")

    def _on_preset_selected(self, preset: str):
        """Load a preset refinement instruction into the entry field when a preset is selected."""
        if preset and preset != "Select preset...":
            self.refinement_entry.delete(0, "end")
            self.refinement_entry.insert(0, preset)

    def _set_buttons_state(self, state: str):
        """Enable or disable the action buttons. State should be 'normal' or 'disabled'."""
        try:
            self.add_comments_button.configure(state=state)
            self.refactor_button.configure(state=state)
            self.generate_docs_button.configure(state=state)
        except Exception:
            # Some CTk versions may not support state; attempt to configure via 'fg_color' as fallback
            pass

    def _on_input_focus_in(self, event):
        """Event handler for focus in: clear placeholder text if present."""
        if self.input_has_placeholder:
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.configure(text_color=Theme.TEXT)  # Reset to normal text color
            self.input_has_placeholder = False

    def _on_input_focus_out(self, event):
        """Event handler for focus out: restore placeholder text if input is empty."""
        if not self.input_textbox.get("1.0", "end-1c").strip():
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.insert("1.0", self.input_placeholder)
            # Make placeholder text gray
            self.input_textbox.configure(text_color="#6c7a89")
            self.input_has_placeholder = True

    def _on_input_key_press(self, event):
        """Event handler for key press: clear placeholder text on any key input."""
        if self.input_has_placeholder:
            self.input_textbox.delete("1.0", "end")
            self.input_textbox.configure(text_color=Theme.TEXT)  # Reset to normal text color
            self.input_has_placeholder = False


if __name__ == "__main__":
    app = CodeAssistantApp()
    app.mainloop()