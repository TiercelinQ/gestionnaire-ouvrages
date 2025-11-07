# pylint: disable=no-name-in-module
"""
Module utilitaire de l'application.
Contient des fonctions d'assistance (gestion des logs, boîtes de dialogue personnalisées,
gestion des dates/heures) et des classes de widgets PyQt personnalisés.
"""

import logging
import sqlite3
from datetime import datetime
from typing import Optional, Any, Literal
from PyQt6.QtWidgets import QMessageBox, QWidget, QListWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
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
    logger.info("Génération d'un log - En cours")
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
        logger.info("Génération d'un log - Succès")
    except sqlite3.Error as log_e:
        logger.info("Génération d'un log - Echec")
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
