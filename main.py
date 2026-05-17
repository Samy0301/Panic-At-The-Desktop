import customtkinter as ctk
from tkinter import messagebox

from config import *
from core.storage import NotesStorage
from ui.sidebar import Sidebar
from ui.editor import EditorPanel
from ui.welcome import WelcomePanel

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class NotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("What Was I Saying???")
        self.geometry("900x600")
        self.minsize(700, 450)
        self.configure(fg_color = purple_bg)

        self.storage = NotesStorage()
        self.editing_index = None

        self._build_ui()
        self.show_welcome()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self.storage, 
            on_new=self.action_new, on_edit=self.action_edit, on_delete=self.action_delete)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        self.right_panel = ctk.CTkFrame(self, fg_color=purple_bg)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(0, weight=1)

        self.welcome = WelcomePanel(self.right_panel)
        self.editor = EditorPanel(self.right_panel, 
            on_save = self.action_save, on_cancel = self.action_cancel)

    def show_welcome(self):
        self.editor.grid_remove()
        self.welcome.grid(row=0, column=0, sticky="nsew")
        self.editing_index = None
        self.sidebar.clear_active()

    def show_editor(self):
        self.welcome.grid_remove()
        self.editor.grid(row=0, column=0, sticky="nsew")

    def action_new(self):
        self.editing_index = None
        self.editor.clear()
        self.show_editor()

    def action_edit(self, index):
        self.editing_index = index
        note = self.storage.get(index)
        if note:
            self.editor.load_note(note)
            self.show_editor()

    def action_save(self):
        title, content = self.editor.get_data()

        if self.editing_index is not None:
            self.storage.update(self.editing_index, title, content)
        else:
            self.editing_index = self.storage.create(title, content)

        # Actualizar sidebar y mantener la nota seleccionada
        self.sidebar.set_active(self.editing_index)

        # Mostrar feedback y actualizar la fecha en el editor
        note = self.storage.get(self.editing_index)
        self.editor.set_date(note.get("date", ""))
        self.editor.show_saved_feedback()

    def action_cancel(self):
        self.show_welcome()

    def action_delete(self, index):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this note?"):
            self.storage.delete(index)
            if self.editing_index == index:
                self.show_welcome()
            self.sidebar.render()


if __name__ == "__main__":
    app = NotesApp()
    app.mainloop()