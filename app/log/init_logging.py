# Fichier : app/log/init_logging.py

import os
import sys
import logging
import traceback
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox
from app.config_manager import ConfigManager
from app.utils import show_custom_message_box

try:
    configManager = ConfigManager()
    LOG_DIR_BASE = configManager._get_app_config_dir()
    LOG_DIR = os.path.join(LOG_DIR_BASE, "Logs")
except Exception:
    LOG_DIR = os.path.join(os.path.expanduser("~"), ".MonGestionnaireOuvrages_logs_crash")

os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_NAME = os.path.join(LOG_DIR, f'MonGestionnaireOuvrages_Log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

try:
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
    )

    file_handler = logging.FileHandler(
        LOG_FILE_NAME,
        mode='a',
        encoding='utf-8',
        delay=False
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logging.root.addHandler(file_handler)
    logging.root.setLevel(logging.INFO)

except Exception as e:
    show_custom_message_box(
        None,
        'ERROR',
        "Erreur Gestion Log Applicatif",
        "Erreur fatale lors de la configuration du logging",
        f"Erreur: {str(e)}",
        buttons=['Ok']
    )

def custom_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Fonction appelée par Python pour toute exception non gérée.
    """
    # Ignorer les arrêts normaux
    if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error(
        "Erreur fatale non gérée.",
        exc_info=(exc_type, exc_value, exc_traceback)
    )

    for handler in logging.root.handlers:
        handler.flush()

    title = "Erreur Critique de l'Application"
    text = "Une erreur critique et inattendue est survenue."
    informative_text = (
        "Le programme doit s'arrêter.\n"
        "Pour résoudre ce problème, merci de communiquer le fichier concerné au concepteur :\n\n"
        f"Dossier de Log: {LOG_DIR}\n\n"
        f"Fichier concerné: {os.path.basename(LOG_FILE_NAME)}"
    )

    show_custom_message_box(
        None,
        'ERROR',
        title,
        text,
        informative_text,
        QMessageBox.StandardButton.Ok
    )

    logging.shutdown()

# --- 3. Activation du Hook (Encapsulé) ---
def setup_exception_hook():
    """Configure le gestionnaire d'exception global de Python."""
    sys.excepthook = custom_exception_handler