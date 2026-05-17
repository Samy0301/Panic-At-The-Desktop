import customtkinter as ctk
import tkinter as tk
from config import *


class EditorPanel(ctk.CTkFrame):
    def __init__(self, parent, on_save, on_cancel):
        super().__init__(parent, fg_color=purple_bg)
        self.on_save = on_save
        self.on_cancel = on_cancel

        # --- Historial manual para el título ---
        self.title_history = []
        self.title_history_index = -1
        self._title_undoing = False

        self.title_entry = ctk.CTkEntry(self, 
            placeholder_text="Note title...", font=ctk.CTkFont(size=17, weight="bold"), height=38, fg_color=purple_editor, 
            text_color="white", border_color=purple_bright)
        self.title_entry.pack(fill="x", padx=10, pady=(10, 5))

        # Binds del título
        self.title_entry.bind("<Control-z>", lambda e: self._title_undo())
        self.title_entry.bind("<Control-y>", lambda e: self._title_redo())
        self.title_entry.bind("<Control-s>", lambda e: self._trigger_save())
        # Enter para ir al cuerpo de la nota
        self.title_entry.bind("<Return>", lambda e: self._focus_textbox())

        self.date_label = ctk.CTkLabel(self, 
            text="", font=ctk.CTkFont(size=11), text_color="#a688c5")
        self.date_label.pack(anchor="w", padx=10)

        self.textbox = ctk.CTkTextbox(self,
            wrap = "word", font=ctk.CTkFont(family="Consolas", size=15), fg_color=purple_editor, text_color="#e0d5f0",
            corner_radius=8, border_color=purple_bright, border_width=1)
        self.textbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Binds del contenido
        self.textbox._textbox.configure(undo=True, maxundo=-1)
        self.textbox.bind("<Control-z>", lambda e: self._text_undo())
        self.textbox.bind("<Control-y>", lambda e: self._text_redo())
        self.textbox.bind("<Control-Shift-z>", lambda e: self._text_redo())
        self.textbox.bind("<Control-s>", lambda e: self._trigger_save())

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.info_label = ctk.CTkLabel(btn_frame, 
            text="0 words", font=ctk.CTkFont(size=11), text_color="#a688c5")
        self.info_label.pack(side="left")

        ctk.CTkButton(btn_frame, 
            text="Cancel", width=100, fg_color="transparent", border_width=2, border_color=purple_bright, text_color="white",
            hover_color=purple_hov_sel, command=self.on_cancel).pack(side="right", padx=5)

        ctk.CTkButton(btn_frame, 
            text="Save", width=120, fg_color=purple_accent, hover_color=purple_hov_sel, 
            command=self.on_save).pack(side="right", padx=5)

        self.textbox.bind("<KeyRelease>", lambda e: self._count())
        self.title_entry.bind("<KeyRelease>", lambda e: self._on_title_keyrelease())

    # --- Enter desde el título al contenido ---

    def _focus_textbox(self):
        self.textbox.focus()
        return "break"

    # --- Guardar con Ctrl+S ---

    def _trigger_save(self):
        self.on_save()
        return "break"

    # --- Undo/redo del TÍTULO ---

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

    # --- Undo/redo del CONTENIDO ---

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

    # --- Resto del panel ---

    def load_note(self, note):
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note.get("title", ""))
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", note.get("content", ""))
        self.date_label.configure(text=f"Editing • {note.get('date', '')}", text_color=purple_text)
        self.title_history = [note.get("title", "")]
        self.title_history_index = 0
        self._count()
        self.title_entry.focus()

    def clear(self):
        self.title_entry.delete(0, "end")
        self.textbox.delete("0.0", "end")
        self.date_label.configure(text="New note", text_color=purple_text)
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