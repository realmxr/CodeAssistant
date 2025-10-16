import customtkinter as ctk
from theme import Theme


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, callbacks: dict):
        super().__init__(parent, width=200, corner_radius=0, fg_color=Theme.FRAME_BG)
        self.callbacks = callbacks
        self.grid_rowconfigure(10, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        self.logo_label = ctk.CTkLabel(self, text="Actions", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.import_file_button = ctk.CTkButton(self, text="Import File",
                                                 command=self.callbacks.get("import_file"),
                                                 fg_color=Theme.YELLOW, hover_color=Theme.YELLOW_HOVER)
        self.import_file_button.grid(row=1, column=0, padx=20, pady=10)

        self.add_comments_button = ctk.CTkButton(self, text="Add Comments",
                                                 command=lambda: self.callbacks.get("process_code")("add detailed comments"),
                                                 fg_color=Theme.BLUE, hover_color=Theme.BLUE_HOVER)
        self.add_comments_button.grid(row=2, column=0, padx=20, pady=10)

        self.refactor_button = ctk.CTkButton(self, text="Refactor Code",
                                             command=lambda: self.callbacks.get("process_code")(
                                                 "refactor this code for readability and efficiency"),
                                             fg_color=Theme.GREEN, hover_color=Theme.GREEN_HOVER)
        self.refactor_button.grid(row=3, column=0, padx=20, pady=10)

        self.generate_docs_button = ctk.CTkButton(self, text="Generate Docs",
                                                  command=lambda: self.callbacks.get("process_code")(
                                                      "generate professional-level documentation"),
                                                  fg_color=Theme.YELLOW, hover_color=Theme.YELLOW_HOVER)
        self.generate_docs_button.grid(row=4, column=0, padx=20, pady=10)

        self.refine_label = ctk.CTkLabel(self, text="Iterative Refinement",
                                         font=ctk.CTkFont(size=14, weight="bold"))
        self.refine_label.grid(row=5, column=0, padx=20, pady=(20, 5))

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
            self,
            values=preset_instructions,
            command=self.callbacks.get("preset_selected"),
            fg_color=Theme.TEXT_INPUT_BG,
            button_color=Theme.BLUE,
            button_hover_color=Theme.BLUE_HOVER,
            dropdown_fg_color=Theme.FRAME_BG
        )
        self.refinement_dropdown.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        self.refinement_dropdown.set("Select preset...")

        self.refinement_entry = ctk.CTkEntry(self,
                                            placeholder_text="e.g., Make comments concise",
                                            fg_color=Theme.TEXT_INPUT_BG,
                                            text_color=Theme.TEXT)
        self.refinement_entry.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        self.refinement_entry.insert(0, "Make the comments more concise")

        self.refine_button = ctk.CTkButton(self, text="Refine Last Output",
                                           command=self.callbacks.get("refine_last_output"),
                                           fg_color=Theme.BLUE, hover_color=Theme.BLUE_HOVER)
        self.refine_button.grid(row=8, column=0, padx=20, pady=10)

        self.export_button = ctk.CTkButton(self, text="Export Output",
                                          command=self.callbacks.get("export_output"),
                                          fg_color=Theme.GREEN, hover_color=Theme.GREEN_HOVER)
        self.export_button.grid(row=9, column=0, padx=20, pady=10)

    def get_refinement_instruction(self) -> str:
        instruction = self.refinement_entry.get().strip()
        if not instruction:
            instruction = "Make the comments more concise"
            self.refinement_entry.delete(0, "end")
            self.refinement_entry.insert(0, instruction)
        return instruction

    def set_buttons_state(self, state: str):
        try:
            self.add_comments_button.configure(state=state)
            self.refactor_button.configure(state=state)
            self.generate_docs_button.configure(state=state)
            self.refine_button.configure(state=state)
        except Exception:
            pass

