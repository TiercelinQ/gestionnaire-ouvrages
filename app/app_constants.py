import logging
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QSize

# --- Logging ---
LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

# --- App Config ---
DEFAULT_DB_FILE_NAME = "MonGestionnaireOuvrages.db"
CONFIG_FILE = "config_user.json"
APP_NAME = "MonGestionnaireOuvrages"
SETTINGS_FILE = "MonGestionnaireOuvrages"

# --- Search Table ---
COLUMNS = [
    ("ID", 0),
    ("Auteur", 200),
    ("Titre", 300),
    ("Édition", 150),
    ("Catégorie", 150),
    ("Actions", 160)
]
ACTION_COL_INDEX = 5

# --- Icons ---
ICON_BASE_PATH = ":/status_icons/"
ICON_SIZE_PX = 32
ICON_BASE_PATH_THEME = ":/theme_icons/"
ICON_SIZE = QSize(30, 30)

ICON_MAP = {
    'ERROR': ICON_BASE_PATH + "error.png",
    'INFO': ICON_BASE_PATH + "information.png",
    'QUESTION': ICON_BASE_PATH + "question.png",
    'SUCCESS': ICON_BASE_PATH + "success.png",
    'WARNING': ICON_BASE_PATH + "warning.png",
}

# --- UI Buttons ---
BUTTON_MAP = {
    'Ok': QMessageBox.StandardButton.Ok,
    'Yes': QMessageBox.StandardButton.Yes,
    'No': QMessageBox.StandardButton.No,
    'Cancel': QMessageBox.StandardButton.Cancel,
    'Save': QMessageBox.StandardButton.Save,
    'Discard': QMessageBox.StandardButton.Discard,
    'Restart': QMessageBox.StandardButton.Yes,
    'Later': QMessageBox.StandardButton.No,
    'Ouvrir': QMessageBox.StandardButton.Open,
    'Créer': QMessageBox.StandardButton.Save,
}

# --- Storage ---
CLOUD_KEYWORDS = [
    "OneDrive",
    "Google Drive",
    "Mon Google Drive",
    "Dropbox",
    "iCloud",
]

# --- Cover ---
PREVIEW_MAX_SIZE = QSize(150, 250)
INITIAL_MIN_WIDTH = 150
INITIAL_MIN_HEIGHT = 200