import customtkinter as ctk
from theme import Theme


class RefinementHistoryPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color=Theme.FRAME_BG)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.refinement_history = []
        self.refinement_count = 0
        self.history_step_frames = []

        self._create_widgets()

    def _create_widgets(self):
        title = ctk.CTkLabel(self, text="Refinement History", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.history_scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=Theme.BACKGROUND,
            scrollbar_button_color=Theme.BLUE,
            scrollbar_button_hover_color=Theme.BLUE_HOVER
        )
        self.history_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.history_scroll_frame.grid_columnconfigure(0, weight=1)

        self.history_placeholder = ctk.CTkLabel(
            self.history_scroll_frame,
            text="No refinements yet.\n\nClick 'Refine Last Output'\nto begin iterative refinement.",
            font=("Consolas", 10),
            text_color="#6c7a89"
        )
        self.history_placeholder.grid(row=0, column=0, pady=20)

        self.clear_btn = ctk.CTkButton(
            self, text="Clear History",
            command=self.clear_history,
            fg_color=Theme.YELLOW, hover_color=Theme.YELLOW_HOVER,
            height=28
        )
        self.clear_btn.grid(row=2, column=0, padx=10, pady=(0, 10))

    def add_refinement(self, text: str):
        self.refinement_history.append(text)
        self.refinement_count += 1
        self._update_display()

    def clear_history(self):
        self.refinement_history.clear()
        self.refinement_count = 0
        for frame in self.history_step_frames:
            frame.destroy()
        self.history_step_frames.clear()

        self.history_placeholder = ctk.CTkLabel(
            self.history_scroll_frame,
            text="No refinements yet.\n\nClick 'Refine Last Output'\nto begin iterative refinement.",
            font=("Consolas", 10),
            text_color="#6c7a89"
        )
        self.history_placeholder.grid(row=0, column=0, pady=20)

    def _update_display(self):
        for frame in self.history_step_frames:
            frame.destroy()
        self.history_step_frames.clear()

        if not self.refinement_history:
            self.history_placeholder = ctk.CTkLabel(
                self.history_scroll_frame,
                text="No refinements yet.\n\nClick 'Refine Last Output'\nto begin iterative refinement.",
                font=("Consolas", 10),
                text_color="#6c7a89"
            )
            self.history_placeholder.grid(row=0, column=0, pady=20)
            return

        for i, step in enumerate(self.refinement_history, start=1):
            step_frame = ctk.CTkFrame(self.history_scroll_frame, fg_color=Theme.STEP_BG)
            step_frame.grid(row=i-1, column=0, sticky="ew", padx=5, pady=5)
            self.history_step_frames.append(step_frame)

            step_label = ctk.CTkLabel(
                step_frame, text=f"Refinement {i}:",
                font=("Consolas", 12, "bold"),
                text_color=Theme.TEXT
            )
            step_label.pack(anchor="nw", padx=10, pady=(10, 0))

            step_content = ctk.CTkTextbox(
                step_frame, font=("Consolas", 10),
                fg_color=Theme.TEXT_INPUT_BG, text_color=Theme.TEXT,
                wrap="word", border_width=2
            )
            step_content.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            step_content.insert("1.0", step)

        # Ensure the scrollable frame updates its layout; avoid calling internal yview API
        try:
            self.history_scroll_frame.update_idletasks()
        except Exception:
            pass
