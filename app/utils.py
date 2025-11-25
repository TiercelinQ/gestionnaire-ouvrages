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
from app.app_constants import LOG_LEVEL_MAP, ICON_MAP, ICON_SIZE_PX, BUTTON_MAP, CLOUD_KEYWORDS

logger = logging.getLogger(__name__)

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
    return any(keyword.lower() in abs_path for keyword in CLOUD_KEYWORDS)

def get_storage_root(path: str) -> str:
    """
    Retourne la racine cloud si trouvée, sinon le dossier parent du fichier .db.
    - Si path est un fichier .db → retourne son dossier parent.
    - Si path contient un mot-clé cloud → retourne la racine cloud jusqu'au dossier.
    - Sinon → retourne dirname(path).
    """
    logger.info("Récupération racine générale bibliothèque - En cours")

    # Cas 1 : si c'est un fichier .db → on prend son dossier parent
    if path.lower().endswith(".db"):
        root = os.path.dirname(path)
        logger.info("Racine générale bibliothèque - Fichier .db détecté → %s", root)
        return root

    # Cas 2 : recherche d'un mot-clé cloud dans le chemin
    parts = path.split(os.sep)
    for i, p in enumerate(parts):
        for keyword in CLOUD_KEYWORDS:
            if keyword.lower() in p.lower():
                root = os.sep.join(parts[:i+1])
                logger.info("Racine générale bibliothèque - Cloud détecté → %s", root)
                return root

    # Cas 3 : fallback → dossier parent
    root = os.path.dirname(path)
    logger.info("Racine générale bibliothèque - Local → %s", root)
    return root

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

class CoverPathManager:
    """
    Gestionnaire centralisé pour les chemins de couvertures.
    """

    @staticmethod
    def make_relative(path: str, db_path: str) -> str:
        """
        Convertit un chemin absolu en chemin relatif par rapport à la racine de stockage
        associée à la base de données.

        Cette méthode est utilisée pour uniformiser les chemins des couvertures afin
        qu'ils soient indépendants de l'emplacement local de OneDrive ou du disque
        dur de l'utilisateur. Elle calcule un chemin relatif à partir du répertoire
        racine de la base (`get_storage_root(db_path)`).

        Args:
            path (str): Chemin absolu ou relatif vers une image de couverture.
            db_path (str): Chemin absolu vers le fichier de base de données, utilisé
                        pour déterminer la racine de stockage.

        Returns:
            str: Chemin relatif par rapport à la racine de stockage. Si le calcul
                échoue (ex. chemin hors racine), retourne le chemin original.
        """
        if not path:
            return ""
        root = get_storage_root(db_path)
        try:
            return os.path.relpath(path, start=root)
        except ValueError:
            return path

    @staticmethod
    def normalize(stored_path: str, db_path: str) -> str:
        """
        Reconstruit un chemin absolu local à partir d'un chemin stocké en base.

        Cette méthode garantit que les chemins relatifs ou cloud sont correctement
        rattachés à la racine locale de l'utilisateur. Elle gère trois cas :
        - Si le chemin est relatif : rattache directement à la racine.
        - Si le chemin est absolu et contient un mot-clé cloud (ex. 'OneDrive') :
            recalcule un chemin relatif puis le rattache à la racine.
        - Sinon : retourne le chemin tel quel (cas local hors cloud).

        Args:
            stored_path (str): Chemin stocké en base (relatif ou absolu).
            db_path (str): Chemin absolu vers le fichier de base de données, utilisé
                        pour déterminer la racine de stockage.

        Returns:
            str: Chemin absolu reconstruit pour l'environnement local de l'utilisateur.
        """
        if not stored_path:
            return ""
        root = get_storage_root(db_path)
        if not os.path.isabs(stored_path):
            return os.path.join(root, stored_path)
        for keyword in CLOUD_KEYWORDS:
            if keyword.lower() in stored_path.lower():
                try:
                    relative = os.path.relpath(stored_path, start=root)
                    return os.path.join(root, relative)
                except ValueError:
                    return stored_path
        return stored_path

    @staticmethod
    def detect_location(path: str, db_path: str) -> str | None:
        """
        Détermine l'emplacement d'une image de couverture (Cloud ou Local).

        La logique repose sur la nature du chemin :
        - Si le chemin est relatif : considéré comme 'Cloud'.
        - Si le chemin absolu contient un mot-clé cloud (ex. 'OneDrive') :
            considéré comme 'Cloud'.
        - Sinon : considéré comme 'Local'.

        Args:
            path (str): Chemin absolu ou relatif vers une image de couverture.
            db_path (str): Chemin de la base de données (non utilisé directement
                        ici mais conservé pour cohérence d'API).

        Returns:
            str | None: 'Cloud' si le chemin est relatif ou lié à OneDrive,
                        'Local' sinon. Retourne None si le chemin est vide.
        """
        if not path:
            return None
        if not os.path.isabs(path):
            return "Cloud"
        for keyword in CLOUD_KEYWORDS:
            if keyword.lower() in path.lower():
                return "Cloud"
        return "Local"

class FocusListWidget(QListWidget):
    """
    QListWidget personnalisé qui annule la sélection lorsque le widget perd le focus,
    SAUF si l'actionneur (bouton Editer/Supprimer) a été pressé (is_acting_on_selection).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_acting_on_selection = False

    def focusOutEvent(self, event): # pylint: disable=invalid-name
        """Redéfinit l'événement de perte de focus."""
        self.clearSelection()
        super().focusOutEvent(event)
