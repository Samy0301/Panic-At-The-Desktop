import customtkinter as ctk
import tkinter as tk
from config import *


class EditorPanel(ctk.CTkFrame):
    def __init__(self, parent, on_save, on_cancel, settings=None):
        super().__init__(parent, fg_color=purple_bg)
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.settings = settings

        self.title_history = []
        self.title_history_index = -1
        self._title_undoing = False

        self.title_font_size = self.settings.get("title_font_size", 17) if self.settings else 17
        self.text_font_size = self.settings.get("editor_font_size", 15) if self.settings else 15

        self._original_date_text = ""
        self._feedback_after_id = None

        self.title_entry = ctk.CTkEntry(self, 
            placeholder_text="Note title...", font=ctk.CTkFont(size=self.title_font_size, weight="bold"), height=38, fg_color=purple_editor, 
            text_color="white", border_color=purple_bright)
        self.title_entry.pack(fill="x", padx=10, pady=(10, 5))

        self.title_entry.bind("<Control-z>", lambda e: self._title_undo())
        self.title_entry.bind("<Control-y>", lambda e: self._title_redo())
        self.title_entry.bind("<Control-s>", lambda e: self._trigger_save())
        self.title_entry.bind("<Return>", lambda e: self._focus_textbox())
        self.title_entry.bind("<Control-minus>", lambda e: self._decrease_font())
        self.title_entry.bind("<Control-plus>", lambda e: self._increase_font())
        self.title_entry.bind("<Control-equal>", lambda e: self._increase_font())

        self.date_label = ctk.CTkLabel(self, 
            text="", font=ctk.CTkFont(size=11), text_color="#a688c5")
        self.date_label.pack(anchor="w", padx=10)

        self.textbox = ctk.CTkTextbox(self,
            wrap = "word", font=ctk.CTkFont(family="Consolas", size=self.text_font_size), fg_color=purple_editor, text_color="#e0d5f0",
            corner_radius=8, border_color=purple_bright, border_width=1)
        self.textbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.textbox._textbox.configure(undo=True, maxundo=-1)
        self.textbox.bind("<Control-z>", lambda e: self._text_undo())
        self.textbox.bind("<Control-y>", lambda e: self._text_redo())
        self.textbox.bind("<Control-Shift-z>", lambda e: self._text_redo())
        self.textbox.bind("<Control-s>", lambda e: self._trigger_save())
        self.textbox.bind("<Control-minus>", lambda e: self._decrease_font())
        self.textbox.bind("<Control-plus>", lambda e: self._increase_font())
        self.textbox.bind("<Control-equal>", lambda e: self._increase_font())

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.info_label = ctk.CTkLabel(btn_frame, 
            text="0 words", font=ctk.CTkFont(size=11), text_color="#a688c5")
        self.info_label.pack(side="left")

        zoom_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        zoom_frame.pack(side="left", padx=(12, 0))

        ctk.CTkButton(zoom_frame, text="-", width=28, height=26,
            fg_color="transparent", border_width=1, border_color=purple_bright,
            text_color="white", hover_color=purple_hov_sel,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._decrease_font).pack(side="left", padx=2)

        ctk.CTkButton(zoom_frame, text="+", width=28, height=26,
            fg_color="transparent", border_width=1, border_color=purple_bright,
            text_color="white", hover_color=purple_hov_sel,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._increase_font).pack(side="left", padx=2)

        ctk.CTkButton(btn_frame, 
            text="Cancel", width=100, fg_color="transparent", border_width=2, border_color=purple_bright, text_color="white",
            hover_color=purple_hov_sel, command=self.on_cancel).pack(side="right", padx=5)

        ctk.CTkButton(btn_frame, 
            text="Save", width=120, fg_color=purple_accent, hover_color=purple_hov_sel, 
            command=self.on_save).pack(side="right", padx=5)

        self.textbox.bind("<KeyRelease>", lambda e: self._count())
        self.title_entry.bind("<KeyRelease>", lambda e: self._on_title_keyrelease())


    def _increase_font(self):
        if self.text_font_size < 32:
            self.text_font_size += 1
            self.title_font_size += 1
            self._apply_font()
        return "break"

    def _decrease_font(self):
        if self.text_font_size > 8:
            self.text_font_size -= 1
            self.title_font_size -= 1
            self._apply_font()
        return "break"

    def _apply_font(self):
        self.textbox.configure(font=ctk.CTkFont(family="Consolas", size=self.text_font_size))
        self.title_entry.configure(font=ctk.CTkFont(size=self.title_font_size, weight="bold"))
        if self.settings:
            self.settings.set("editor_font_size", self.text_font_size)
            self.settings.set("title_font_size", self.title_font_size)


    def set_date(self, date_str):
        self._original_date_text = f"Editing • {date_str}"
        self.date_label.configure(text=self._original_date_text, text_color=purple_text)

    def show_saved_feedback(self):
        if self._feedback_after_id is not None:
            self.after_cancel(self._feedback_after_id)
        self.date_label.configure(text="Saved successfully", text_color=purple_text)
        self._feedback_after_id = self.after(1500, self._restore_date_label)

    def _restore_date_label(self):
        self.date_label.configure(text=self._original_date_text, text_color=purple_text)
        self._feedback_after_id = None


    def _focus_textbox(self):
        self.textbox.focus()
        return "break"


    def _trigger_save(self):
        self.on_save()
        return "break"


    def _on_title_keyrelease(self):
        if self._title_undoing:
            return
        self._save_title_state()
        self._count()

    def _save_title_state(self):
        current = self.title_entry.get()
        if self.title_history_index < len(self.title_history) - 1:
            self.title_history = self.title_history[:self.title_history_index + 1]
        if not self.title_history or self.title_history[-1] != current:
            self.title_history.append(current)
            self.title_history_index += 1

    def _title_undo(self):
        if self.title_history_index > 0:
            self.title_history_index -= 1
            self._title_undoing = True
            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, self.title_history[self.title_history_index])
            self.title_entry._entry.icursor("end")
            self._title_undoing = False
        return "break"

    def _title_redo(self):
        if self.title_history_index < len(self.title_history) - 1:
            self.title_history_index += 1
            self._title_undoing = True
            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, self.title_history[self.title_history_index])
            self.title_entry._entry.icursor("end")
            self._title_undoing = False
        return "break"


    def _text_undo(self):
        try:
            self.textbox._textbox.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def _text_redo(self):
        try:
            self.textbox._textbox.edit_redo()
        except tk.TclError:
            pass
        return "break"


    def load_note(self, note):
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note.get("title", ""))
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", note.get("content", ""))
        self._original_date_text = f"Editing • {note.get('date', '')}"
        self.date_label.configure(text=self._original_date_text, text_color=purple_text)
        self.title_history = [note.get("title", "")]
        self.title_history_index = 0
        self._count()
        self.title_entry.focus()

    def clear(self):
        self.title_entry.delete(0, "end")
        self.textbox.delete("0.0", "end")
        self._original_date_text = "New note"
        self.date_label.configure(text=self._original_date_text, text_color=purple_text)
        self.title_history = [""]
        self.title_history_index = 0
        self._count()
        self.title_entry.focus()

    def get_data(self):
        title = self.title_entry.get().strip()
        if not title:
            title = "Untitled"
        return title, self.textbox.get("0.0", "end")

    def _count(self):
        text = self.textbox.get("0.0", "end-1c")
        words = len(text.split()) if text.strip() else 0
        self.info_label.configure(text=f"{words} words")