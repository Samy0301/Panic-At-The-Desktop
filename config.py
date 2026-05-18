import os
import sys

_base = os.environ.get("APPDATA", os.path.expanduser("~")) if sys.platform == "win32" else os.path.expanduser("~/.local/share")
app_folder = os.path.join(_base, "NotasApp")
os.makedirs(app_folder, exist_ok=True)
notes_file = os.path.join(app_folder, "mis_notas.json")
settings_file = os.path.join(app_folder, "settings.json")

purple_bg      = "#1a0a2e"
purple_frame   = "#240b3a"
purple_editor  = "#1e0b33"
purple_accent  = "#7b2cbf"
purple_hov_sel = "#5a189a"
purple_bright  = "#9d4edd"
purple_text    = "#e0aaff"