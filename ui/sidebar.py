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
        self.note_widgets = []

        self.grid_propagate(False)

        ctk.CTkLabel(self, 
            text="Main Character Notes", font=ctk.CTkFont(size=22, weight="bold"),
            text_color=purple_text).pack(pady=(15, 10))

        ctk.CTkButton(self, 
            text="+ New note", font=ctk.CTkFont(size=15), height=38, fg_color=purple_accent, hover_color=purple_hov_sel,
            command=self.on_new).pack(fill="x", padx=12, pady=(0, 10))

        # --- Búsqueda en vivo ---
        self.search_var = ctk.StringVar()
        
        search_frame = ctk.CTkFrame(self, fg_color=purple_editor, height=32, corner_radius=6, border_width=1, border_color=purple_bright)
        search_frame.pack(fill="x", padx=12, pady=(0, 10))
        search_frame.grid_propagate(False)
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_rowconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(search_frame,
            font=ctk.CTkFont(size=13), fg_color="transparent",
            text_color="white", border_width=0, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=0, sticky="nsew", padx=8)
        
        self.search_placeholder = ctk.CTkLabel(search_frame, text="Search",
            font=ctk.CTkFont(size=13), text_color="#a688c5", fg_color="transparent")
        self.search_placeholder.place(rely=0.5, anchor="w", x=8)
        
        self.search_var.trace_add("write", lambda *args: self._on_search_change())
        self.search_entry.bind("<FocusIn>", lambda e: self._update_placeholder())
        self.search_entry.bind("<FocusOut>", lambda e: self._update_placeholder())
        self.search_entry.bind("<Escape>", lambda e: self.search_var.set(""))

        self.list_container = ctk.CTkScrollableFrame(self, fg_color=purple_frame, width=300)
        self.list_container.pack(fill="both", expand=True, padx=0, pady=5)
        self.list_container.grid_columnconfigure(0, weight=1)

        self.no_results_label = None
        self.empty_label = None

        self.render()

    def _on_search_change(self):
        self._update_placeholder()
        self._apply_filter()

    def _update_placeholder(self):
        if self.search_var.get() == "":
            try:
                focused = self.focus_get()
            except Exception:
                focused = None
            
            if focused == self.search_entry._entry:
                self.search_placeholder.place_forget()
            else:
                self.search_placeholder.place(rely=0.5, anchor="w", x=8)
        else:
            self.search_placeholder.place_forget()

    # --- Orden visual (pinned primero) ---

    def _get_visual_order(self):
        order = []
        for i, note in enumerate(self.storage.notes):
            if note.get("pinned", False):
                order.append(i)
        for i, note in enumerate(self.storage.notes):
            if not note.get("pinned", False):
                order.append(i)
        return order

    def _reposition_all(self):
        order = self._get_visual_order()
        for visual_pos, storage_idx in enumerate(order):
            if 0 <= storage_idx < len(self.note_widgets):
                w = self.note_widgets[storage_idx]
                w["frame"].grid_row = visual_pos
                w["frame"].grid_configure(row=visual_pos)

    # --- Filtro en vivo ---

    def _apply_filter(self):
        query = self.search_var.get().lower().strip()
        visible_count = 0

        for i, widgets in enumerate(self.note_widgets):
            note = self.storage.get(i)
            if not note:
                continue

            if query == "":
                match = True
            else:
                title = note.get("title", "").lower()
                content = note.get("content", "").lower()
                match = query in title or query in content

            frame = widgets["frame"]
            if match:
                frame.grid(row=frame.grid_row, column=0, sticky="ew", pady=15, padx=12)
                visible_count += 1
            else:
                frame.grid_remove()

        if not self.storage.notes:
            pass
        elif visible_count == 0:
            if self.no_results_label is None or not self.no_results_label.winfo_exists():
                self.no_results_label = ctk.CTkLabel(self.list_container,
                    text="No matching notes.", text_color="#a688c5",
                    font=ctk.CTkFont(size=14))
            self.no_results_label.grid(row=0, column=0, pady=40)
        else:
            if self.no_results_label is not None and self.no_results_label.winfo_exists():
                self.no_results_label.grid_remove()

    # --- Render completo ---

    def render(self):
        for w in self.list_container.winfo_children():
            w.destroy()
        self.note_widgets.clear()
        self.no_results_label = None
        self.empty_label = None

        notes = self.storage.notes
        if not notes:
            self.empty_label = ctk.CTkLabel(self.list_container,
                text="No saved notes.\n Click 'New note' to create one.",
                text_color="#a688c5", font=ctk.CTkFont(size=14))
            self.empty_label.grid(row=0, column=0, pady=40)
            return

        for i, note in enumerate(notes):
            self._create_note_frame(i, note, list_index=i)

        self._reposition_all()
        self._apply_highlight()

    def _create_note_frame(self, index, note, list_index=None):
        if list_index is None:
            list_index = len(self.note_widgets)

        frame = ctk.CTkFrame(self.list_container, fg_color=purple_frame)
        frame.note_index = index
        frame.grid_row = list_index
        frame.grid(row=list_index, column=0, sticky="ew", pady=15, padx=12)

        widgets = {"frame": frame, "title": None, "preview": None, "date": None, "pin_btn": None}

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

        # Botón pin/unpin con emoji
        is_pinned = note.get("pinned", False)
        pin_btn = ctk.CTkButton(bottom, 
            text="❎" if is_pinned else "📌", width=32, height=26,
            fg_color=purple_bright if is_pinned else "transparent",
            hover_color=purple_hov_sel, text_color="white",
            font=ctk.CTkFont(size=14), command=lambda f=frame: self._toggle_pin_frame(f))
        pin_btn.pack(side="right", padx=(0, 5))
        widgets["pin_btn"] = pin_btn

        ctk.CTkButton(bottom, 
            text="🗑", width=32, height=26, fg_color="transparent", hover_color="#8B0000",
            font=ctk.CTkFont(size=14), command=lambda f=frame: self._delete_frame(f)).pack(side="right")

        self.note_widgets.insert(list_index, widgets)
        return widgets

    # --- Acciones por frame ---

    def _select_frame(self, frame):
        self._select(frame.note_index)

    def _delete_frame(self, frame):
        self.on_delete(frame.note_index)

    def _toggle_pin_frame(self, frame):
        new_state = self.storage.toggle_pin(frame.note_index)
        for w in self.note_widgets:
            if w["frame"] == frame:
                w["pin_btn"].configure(
                    text="❎" if new_state else "📌",
                    fg_color=purple_bright if new_state else "transparent"
                )
                break
        self._reposition_all()
        self._apply_filter()
        self._apply_highlight()

    def _apply_highlight(self):
        for widgets in self.note_widgets:
            frame = widgets["frame"]
            note = self.storage.get(frame.note_index)
            is_pinned = note.get("pinned", False) if note else False
            
            if frame.note_index == self.active_note:
                frame.configure(fg_color=purple_hov_sel, border_width=2, border_color=purple_bright)
            elif is_pinned:
                frame.configure(fg_color=purple_frame, border_width=1, border_color=purple_bright)
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

    def update_note(self, index):
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
                self._apply_filter()

    def insert_note_at_top(self):
        if self.empty_label is not None and self.empty_label.winfo_exists():
            self.empty_label.destroy()
            self.empty_label = None

        for widgets in self.note_widgets:
            widgets["frame"].note_index += 1

        note = self.storage.get(0)
        if note:
            self._create_note_frame(0, note, list_index=0)

            if self.active_note is not None:
                self.active_note += 1

            self._reposition_all()
            self._apply_filter()
            self._apply_highlight()

    def remove_note(self, index):
        if 0 <= index < len(self.note_widgets):
            widgets = self.note_widgets.pop(index)
            widgets["frame"].destroy()

            for i, w in enumerate(self.note_widgets):
                w["frame"].note_index = i

            if self.active_note == index:
                self.active_note = None
            elif self.active_note is not None and self.active_note > index:
                self.active_note -= 1

            self._reposition_all()
            self._apply_filter()
            self._apply_highlight()

            if not self.note_widgets:
                self.render()