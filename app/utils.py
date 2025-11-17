# pylint: disable=no-name-in-module
"""
Module utilitaire de l'application.
Contient des fonctions d'assistance (gestion des logs, boîtes de dialogue personnalisées,
gestion des dates/heures) et des classes de widgets PyQt personnalisés.
"""

import os
import logging
import sqlite3
from datetime import datetime
from typing import Optional, Any, Literal
from PyQt6.QtWidgets import QMessageBox, QWidget, QListWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from .data_models import DBSchema

logger = logging.getLogger(__name__)

LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

ICON_BASE_PATH = ":/status_icons/"
ICON_SIZE_PX = 32

ICON_MAP = {
    'ERROR': ICON_BASE_PATH + "error.png",
    'INFO': ICON_BASE_PATH + "information.png",
    'QUESTION': ICON_BASE_PATH + "question.png",
    'SUCCESS': ICON_BASE_PATH + "success.png",
    'WARNING': ICON_BASE_PATH + "warning.png",
}

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

CLOUD_KEYWORDS = ["OneDrive", "Google Drive","Mon Google Drive","Dropbox", "iCloud"]

def get_datetime() -> str:
    """
    Retourne la date et l'heure actuelles formatées pour la BDD (YYYY-MM-DD HH:MM:SS).
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_event(db_manager: Any, level: str, source: str, message: str, exception: Optional[Exception] = None):
    """
    Enregistre un événement (erreur, succès, info) dans la table logs de la BDD.
    :param db_manager: L'instance de DBManager.
    :param level: Niveau de l'événement ('SUCCESS', 'INFO', 'ERROR', 'CRITICAL', etc.).
    :param source: Nom du module/méthode.
    :param message: Le message à enregistrer.
    :param exception: L'objet exception capturé, si c'est une erreur.
    """
    logger.info("Génération log - En cours")
    source_method="utils.log_event"
    if not db_manager.connexion:
        log_error_connection_database(None, source_method)
        return

    error_type = type(exception).__name__ if exception else None
    user_id = db_manager.current_user_id
    now = get_datetime()

    log_message = f"{message} | Exception: {exception}" if exception else message

    sql = f"""
    INSERT INTO {DBSchema.TABLE_LOGS}
        (timestamp, level, source_module, error_type, message, user_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    try:
        db_manager.cursor.execute(sql, (now, level, source, error_type, log_message, user_id))
        db_manager.connexion.commit()
        logger.info("Génération log - Succès")
    except sqlite3.Error as log_e:
        logger.info("Génération log - Echec")
        logger.critical("%s - Erreur: %s",source_method,str(log_e),exc_info=True)
        log_error_connection_database(None,source_method)

def log_error_connection_database(parent_widget, source_method: str):
    """
    Loggue une erreur critique de connexion BDD et affiche une boîte de dialogue.
    :param parent_widget: Le widget parent pour la boîte de dialogue.
    :param source_method: Le nom de la méthode ou du module source.
    """
    logger.critical("%s - Connexion BDD - Statut: Echec", source_method, exc_info=True)
    show_custom_message_box(
        parent_widget,
        'CRITICAL',
        "Erreur Critique BDD",
        "Impossible de se connecter à la base de données.",
        f"(Source: {source_method})"
    )

def is_cloud_path(path: str) -> bool:
    """
    Détecte si le chemin fourni correspond à un dossier synchronisé par un service cloud.
    Retourne True si le chemin contient des mots-clés connus (OneDrive, Google Drive, Dropbox, iCloud).
    """
    abs_path = os.path.abspath(path).lower()
    cloud_keywords = ["onedrive", "google drive", "googledrive", "dropbox", "icloud"]
    return any(keyword in abs_path for keyword in cloud_keywords)

def get_storage_root(path: str) -> str:
    """
    Retourne la racine cloud si trouvée, sinon le dossier parent du fichier .db.
    """
    logger.info("Récupération racine générale bibliothèque - En cours")
    parts = path.split(os.sep)
    for i, p in enumerate(parts):
        for keyword in CLOUD_KEYWORDS:
            if keyword.lower() in p.lower():
                logger.info("Récupération racine générale bibliothèque - Terminé")
                logger.info("Racine générale bibliothèque - %s",os.sep.join(parts[:i+1]))
                return os.sep.join(parts[:i+1])
    return os.path.dirname(path)

def make_relative_cover_path(path: str) -> str:
    """
    Retourne le chemin relatif après la racine cloud si trouvée,
    sinon après le dossier parent du .db.
    """
    logger.info("Création chemin relatif bibliothèque - En cours")
    if not path:
        logger.info("Création chemin relatif bibliothèque - Terminé")
        logger.info("Création chemin relatif bibliothèque - Aucun Chemin")
        return ""
    for keyword in CLOUD_KEYWORDS:
        if keyword.lower() in path.lower():
            parts = path.split(keyword, 1)
            logger.info("Création chemin relatif bibliothèque - Terminé")
            logger.info("Création chemin relatif bibliothèque - %s",os.path.join(keyword, parts[1].lstrip("\\/")))
            return os.path.join(keyword, parts[1].lstrip("\\/"))
    logger.info("Création chemin relatif bibliothèque - Terminé")
    logger.info("Création chemin relatif bibliothèque - %s",os.path.basename(path))
    return os.path.basename(path)

def normalize_cover_path(config_manager, stored_path: str) -> str:
    """
    Reconstruit un chemin valide pour l'utilisateur courant.
    - Si chemin relatif → on le rattache à la racine cloud ou au dossier parent du .db.
    - Si chemin absolu avec cloud → on le convertit.
    - Sinon → on garde tel quel (cas local pur).
    """
    logger.info("Reconstruction chemin couverture valide - En cours")
    db_path = config_manager.get_db_path()
    user_root = get_storage_root(db_path)
    logger.info("Reconstruction chemin couverture valide - db_path: %s",db_path)
    logger.info("Reconstruction chemin couverture valide - user_root: %s",user_root)

    if not stored_path:
        return ""

    if not os.path.isabs(stored_path):
        logger.info("Reconstruction chemin couverture valide - Terminé")
        logger.info("Reconstruction chemin couverture valide - Relatif: %s",os.path.join(user_root, stored_path))
        return os.path.join(user_root, stored_path)

    for keyword in CLOUD_KEYWORDS:
        if keyword.lower() in stored_path.lower():
            parts = stored_path.split(keyword, 1)
            relative = parts[1].lstrip("\\/")
            logger.info("Reconstruction chemin couverture valide - Terminé")
            logger.info("Reconstruction chemin couverture valide - Cloud: %s",os.path.join(user_root, keyword, relative))
            return os.path.join(user_root, keyword, relative)
    logger.info("Reconstruction chemin couverture valide - Terminé")
    logger.info("Reconstruction chemin couverture valide - stored_path: %s",stored_path)
    return stored_path

def show_custom_message_box(
    parent: QWidget,
    level: Literal['ERROR', 'INFO', 'QUESTION', 'SUCCESS', 'WARNING'],
    title: str,
    text: str,
    informative_text: Optional[str] = None,
    buttons: Any = QMessageBox.StandardButton.Ok,
    min_width: int = 300,
    base_height: int = 120,
    line_height: int = 20
) -> QMessageBox.StandardButton:
    """
    Affiche une QMessageBox personnalisée avec une icône et un style harmonisés.

    :param parent: Le widget parent (obligatoire pour le style QSS).
    :param level: Le niveau de l'événement ('ERROR', 'INFO', 'QUESTION', 'SUCCESS', 'WARNING').
    :param title: Le titre de la fenêtre.
    :param text: Le message principal (affiché en gras).
    :param informative_text: Le texte secondaire/détail technique.
    :param buttons: Les boutons standard (par défaut: OK). Peut être un flag
                    (QMessageBox.StandardButton) ou une liste de chaînes de caractères
                    ('Yes', 'No').
    :return: Le bouton cliqué par l'utilisateur (ex: QMessageBox.StandardButton.Ok).
    """
    logger.info("Génération de message custom - En cours")
    # 1. Conversion de la liste de chaînes en StandardButtons
    final_buttons = buttons
    if isinstance(buttons, list):
        if not buttons:
            final_buttons = QMessageBox.StandardButton.Ok
        else:
            button_flags = QMessageBox.StandardButton.NoButton
            for btn_name in buttons:
                button_flag = BUTTON_MAP.get(btn_name)
                if button_flag:
                    button_flags |= button_flag
            final_buttons = button_flags

    # 2. Création et configuration de la MessageBox
    custom_message_box = QMessageBox(parent)
    custom_message_box.setWindowTitle(title)
    icon_path = ICON_MAP.get(level.upper(), ICON_MAP['INFO'])
    custom_message_box.setIcon(QMessageBox.Icon.NoIcon)
    custom_pixmap = QIcon(icon_path).pixmap(QSize(ICON_SIZE_PX, ICON_SIZE_PX))
    custom_message_box.setIconPixmap(custom_pixmap)
    custom_message_box.setText(f"{text}")
    if informative_text:
        custom_message_box.setInformativeText(informative_text)
    custom_message_box.setStandardButtons(final_buttons)
    custom_message_box.adjustSize()
    custom_message_box.setMinimumWidth(min_width)
    custom_message_box.setWindowModality(Qt.WindowModality.ApplicationModal)
    custom_message_box.setWindowFlags(custom_message_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    custom_message_box.raise_()
    custom_message_box.activateWindow()
    if informative_text:
        lines = informative_text.count("\n") + 1
        min_height = base_height + (lines * line_height)
        custom_message_box.setMinimumHeight(min_height)
    logger.info("Génération de message custom - Succès")
    return custom_message_box.exec()

class FocusListWidget(QListWidget):
    """
    QListWidget personnalisé qui annule la sélection lorsque le widget perd le focus,
    SAUF si l'actionneur (bouton Editer/Supprimer) a été pressé (is_acting_on_selection).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Nouveau flag pour empêcher la désélection lors de l'exécution d'une action
        self.is_acting_on_selection = False

    def focusOutEvent(self, event): # pylint: disable=invalid-name
        """Redéfinit l'événement de perte de focus."""
        # Désélectionne tous les éléments
        self.clearSelection()
        # Appelle le gestionnaire de focus du parent
        super().focusOutEvent(event)
