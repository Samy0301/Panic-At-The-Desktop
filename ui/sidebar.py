import customtkinter as ctk
from config import *


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, storage, on_new, on_edit, on_delete):
        super().__init__(parent, width=340, fg_color=purple_frame)
        self.storage = storage
        self.on_new = on_new
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.active_note = None
        self.note_widgets = []   # referencias a los widgets de cada nota

        self.grid_propagate(False)

        ctk.CTkLabel(self, 
            text="Main Character Notes", font=ctk.CTkFont(size=22, weight="bold"),
            text_color=purple_text).pack(pady=(15, 10))

        ctk.CTkButton(self, 
            text="+ New note", font=ctk.CTkFont(size=15), height=38, fg_color=purple_accent, hover_color=purple_hov_sel,
            command=self.on_new).pack(fill="x", padx=12, pady=(0, 10))

        self.list_container = ctk.CTkScrollableFrame(self, fg_color=purple_frame, width=300)
        self.list_container.pack(fill="both", expand=True, padx=0, pady=5)

        self.render()

    # --- Render completo (solo al inicio o cuando no hay otra opción) ---

    def render(self):
        for w in self.list_container.winfo_children():
            w.destroy()
        self.note_widgets.clear()

        notes = self.storage.notes
        if not notes:
            self.empty_label = ctk.CTkLabel(self.list_container,
                text="No saved notes.\n Click 'New note' to create one.",
                text_color="#a688c5", font=ctk.CTkFont(size=14))
            self.empty_label.pack(pady=40)
            return

        for i, note in enumerate(notes):
            self._create_note_frame(i, note)

        self._apply_highlight()

    def _create_note_frame(self, index, note, before_widget=None):
        frame = ctk.CTkFrame(self.list_container, fg_color=purple_frame)
        frame.note_index = index   # índice "vivo" que podemos actualizar

        if before_widget:
            frame.pack(fill="x", pady=15, padx=12, before=before_widget)
        else:
            frame.pack(fill="x", pady=15, padx=12)

        widgets = {"frame": frame, "title": None, "preview": None, "date": None}

        frame.bind("<Button-1>", lambda e, f=frame: self._select_frame(f))

        title = note["title"].strip() or "Untitled"
        lbl_title = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=15, weight="bold"), anchor="w", text_color="white")
        lbl_title.pack(fill="x", padx=10, pady=(10, 3))
        lbl_title.bind("<Button-1>", lambda e, f=frame: self._select_frame(f))
        widgets["title"] = lbl_title

        preview = note["content"].replace("\n", " ")[:45]
        if len(note["content"]) > 45:
            preview += "..."
        lbl_preview = ctk.CTkLabel(frame, text=preview or " ", font=ctk.CTkFont(size=13), text_color="#a688c5", anchor="w")
        lbl_preview.pack(fill="x", padx=10, pady=(0, 3))
        lbl_preview.bind("<Button-1>", lambda e, f=frame: self._select_frame(f))
        widgets["preview"] = lbl_preview

        bottom = ctk.CTkFrame(frame, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=(0, 8))

        lbl_date = ctk.CTkLabel(bottom, 
            text=note.get("date", ""), font=ctk.CTkFont(size=11), 
            text_color="#7a5c94")
        lbl_date.pack(side="left")
        widgets["date"] = lbl_date

        ctk.CTkButton(bottom, 
            text="🗑", width=32, height=26, fg_color="transparent", hover_color="#8B0000",
            font=ctk.CTkFont(size=14), command=lambda f=frame: self._delete_frame(f)).pack(side="right")

        if before_widget:
            self.note_widgets.insert(0, widgets)
        else:
            self.note_widgets.append(widgets)
        return widgets

    # --- Acciones por frame (usando el índice "vivo") ---

    def _select_frame(self, frame):
        self._select(frame.note_index)

    def _delete_frame(self, frame):
        self.on_delete(frame.note_index)

    def _apply_highlight(self):
        for i, widgets in enumerate(self.note_widgets):
            frame = widgets["frame"]
            if i == self.active_note:
                frame.configure(fg_color=purple_hov_sel, border_width=2, border_color=purple_bright)
            else:
                frame.configure(fg_color=purple_frame, border_width=0, border_color=purple_frame)

    def _select(self, index):
        self.active_note = index
        self._apply_highlight()
        self.on_edit(index)

    def set_active(self, index):
        self.active_note = index
        self._apply_highlight()

    def clear_active(self):
        self.active_note = None
        self._apply_highlight()

    # --- Actualizaciones parciales (sin reconstruir) ---

    def update_note(self, index):
        """Cambia título, preview y fecha de una nota existente."""
        if 0 <= index < len(self.note_widgets):
            note = self.storage.get(index)
            if note:
                w = self.note_widgets[index]
                w["title"].configure(text=note["title"].strip() or "Untitled")
                preview = note["content"].replace("\n", " ")[:45]
                if len(note["content"]) > 45:
                    preview += "..."
                w["preview"].configure(text=preview or " ")
                w["date"].configure(text=note.get("date", ""))

    def insert_note_at_top(self):
        """Inserta una nota nueva arriba de todo sin tocar las demás."""
        if hasattr(self, 'empty_label') and self.empty_label.winfo_exists():
            self.empty_label.destroy()
            delattr(self, 'empty_label')

        # Los índices de las notas existentes suben 1
        for widgets in self.note_widgets:
            widgets["frame"].note_index += 1

        note = self.storage.get(0)
        if note:
            before = self.note_widgets[0]["frame"] if self.note_widgets else None
            self._create_note_frame(0, note, before_widget=before)

            if self.active_note is not None:
                self.active_note += 1
            self._apply_highlight()

    def remove_note(self, index):
        """Elimina una nota y reindexa las que quedan."""
        if 0 <= index < len(self.note_widgets):
            widgets = self.note_widgets.pop(index)
            widgets["frame"].destroy()

            # Reindexar las siguientes
            for i, w in enumerate(self.note_widgets[index:], start=index):
                w["frame"].note_index = i

            if self.active_note == index:
                self.active_note = None
            elif self.active_note is not None and self.active_note > index:
                self.active_note -= 1

            self._apply_highlight()

            if not self.note_widgets:
                self.render()